"""
Query Validator Agent
Converts natural language to SQL and validates query safety
"""
import google.generativeai as genai
from typing import Tuple, Optional
from config import GOOGLE_API_KEY, MODEL_NAME, TEMPERATURE
from utils.logger import log_agent_action, log_error
from tools.database_tool import DatabaseTool


class QueryValidatorAgent:
    """
    Agent responsible for:
    1. Converting natural language to SQL
    2. Validating query syntax
    3. Ensuring query safety
    """
    
    def __init__(self, db_tool: DatabaseTool):
        self.db_tool = db_tool
        genai.configure(api_key=GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(MODEL_NAME)
        log_agent_action("QueryValidatorAgent", "initialized", {"model": MODEL_NAME})
        
    def generate_sql(self, natural_language_query: str, schema_info: dict, 
                     conversation_context: str = "") -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Convert natural language query to SQL
        
        Args:
            natural_language_query: User's question in natural language
            schema_info: Database schema information
            conversation_context: Previous conversation context
            
        Returns:
            Tuple of (success, sql_query, error_message)
        """
        try:
            log_agent_action("QueryValidatorAgent", "generating_sql", {
                "query": natural_language_query[:100]
            })
            
            # Build schema context
            schema_context = self._format_schema_context(schema_info)
            
            # Create prompt
            prompt = f"""You are an expert SQL query generator. Convert the natural language query to a valid SQL SELECT query.

Database Schema:
{schema_context}

Previous Context:
{conversation_context if conversation_context else "No previous context"}

User Query: {natural_language_query}

Rules:
1. Generate ONLY SELECT queries (no INSERT, UPDATE, DELETE, DROP, etc.)
2. Use proper JOIN syntax when querying multiple tables
3. Include appropriate WHERE clauses for filtering
4. Use aggregate functions (COUNT, SUM, AVG, etc.) when asked for totals or averages
5. Add ORDER BY and LIMIT clauses when appropriate
6. Return ONLY the SQL query without any explanation or markdown

SQL Query:"""

            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": TEMPERATURE,
                    "max_output_tokens": 1024
                }
            )
            
            sql_query = response.text.strip()
            
            # Clean up the response (remove markdown if present)
            if sql_query.startswith("```sql"):
                sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
            elif sql_query.startswith("```"):
                sql_query = sql_query.replace("```", "").strip()
                
            log_agent_action("QueryValidatorAgent", "sql_generated", {
                "sql": sql_query[:200]
            })
            
            return True, sql_query, None
            
        except Exception as e:
            log_error("QueryValidatorAgent", e, {
                "query": natural_language_query[:100]
            })
            return False, None, str(e)
            
    def validate_query(self, sql_query: str) -> Tuple[bool, Optional[str]]:
        """
        Validate SQL query for safety
        
        Args:
            sql_query: SQL query to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            log_agent_action("QueryValidatorAgent", "validating_query", {
                "sql": sql_query[:100]
            })
            
            # Use database tool for safety validation
            is_safe, error_msg = self.db_tool.validate_query_safety(sql_query)
            
            if not is_safe:
                log_agent_action("QueryValidatorAgent", "validation_failed", {
                    "reason": error_msg
                })
                return False, error_msg
                
            log_agent_action("QueryValidatorAgent", "validation_passed", {})
            return True, None
            
        except Exception as e:
            log_error("QueryValidatorAgent", e, {"query": sql_query[:100]})
            return False, str(e)
            
    def process(self, natural_language_query: str, schema_info: dict,
                conversation_context: str = "") -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Complete processing pipeline: generate and validate SQL
        
        Returns:
            Tuple of (success, sql_query, error_message)
        """
        # Generate SQL
        success, sql_query, error = self.generate_sql(
            natural_language_query, 
            schema_info,
            conversation_context
        )
        
        if not success:
            return False, None, f"SQL generation failed: {error}"
            
        # Validate SQL
        is_valid, validation_error = self.validate_query(sql_query)
        
        if not is_valid:
            return False, None, f"Query validation failed: {validation_error}"
            
        return True, sql_query, None
        
    def _format_schema_context(self, schema_info: dict) -> str:
        """Format schema information for prompt"""
        schema_lines = []
        
        for table_name, columns in schema_info.items():
            cols = ", ".join([f"{col['name']} ({col['type']})" for col in columns])
            schema_lines.append(f"Table: {table_name}\n  Columns: {cols}")
            
        return "\n\n".join(schema_lines)
