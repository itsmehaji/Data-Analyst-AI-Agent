"""
Database tools for executing SQL queries
"""
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
from typing import Dict, List, Tuple, Optional
from config import DATABASE_URL
from utils.logger import log_agent_action, log_error, logger


class DatabaseTool:
    """Custom tool for database operations"""
    
    def __init__(self, database_url: str = DATABASE_URL):
        """Initialize database connection"""
        self.engine = create_engine(database_url)
        log_agent_action("DatabaseTool", "initialized", {"database_url": database_url})
        
    def get_schema_info(self) -> Dict[str, List[Dict]]:
        """
        Get database schema information
        Returns table names and their columns
        """
        try:
            inspector = inspect(self.engine)
            schema = {}
            
            for table_name in inspector.get_table_names():
                columns = []
                for column in inspector.get_columns(table_name):
                    columns.append({
                        "name": column["name"],
                        "type": str(column["type"]),
                        "nullable": column["nullable"]
                    })
                schema[table_name] = columns
                
            log_agent_action("DatabaseTool", "schema_retrieved", {
                "table_count": len(schema)
            })
            return schema
            
        except Exception as e:
            log_error("DatabaseTool", e, {"action": "get_schema_info"})
            raise
            
    def execute_query(self, sql_query: str) -> Tuple[bool, Optional[pd.DataFrame], Optional[str]]:
        """
        Execute a SQL query and return results
        
        Args:
            sql_query: SQL query to execute
            
        Returns:
            Tuple of (success, dataframe, error_message)
        """
        try:
            log_agent_action("DatabaseTool", "executing_query", {
                "query": sql_query[:200]  # Log first 200 chars
            })
            
            with self.engine.connect() as connection:
                result = connection.execute(text(sql_query))
                
                # Check if query returns results
                if result.returns_rows:
                    df = pd.DataFrame(result.fetchall(), columns=result.keys())
                    log_agent_action("DatabaseTool", "query_success", {
                        "rows_returned": len(df),
                        "columns": list(df.columns)
                    })
                    return True, df, None
                else:
                    # For INSERT, UPDATE, DELETE queries
                    connection.commit()
                    log_agent_action("DatabaseTool", "query_success", {
                        "rows_affected": result.rowcount
                    })
                    return True, None, None
                    
        except SQLAlchemyError as e:
            error_msg = str(e)
            log_error("DatabaseTool", e, {"query": sql_query[:200]})
            return False, None, error_msg
            
    def validate_query_safety(self, sql_query: str) -> Tuple[bool, Optional[str]]:
        """
        Validate if a query is safe to execute
        
        Args:
            sql_query: SQL query to validate
            
        Returns:
            Tuple of (is_safe, error_message)
        """
        sql_lower = sql_query.lower().strip()
        
        # Block dangerous operations
        dangerous_keywords = [
            "drop", "truncate", "delete", "alter", "create",
            "insert", "update", "grant", "revoke"
        ]
        
        for keyword in dangerous_keywords:
            if keyword in sql_lower.split():
                error_msg = f"Query contains potentially dangerous keyword: {keyword.upper()}"
                log_agent_action("DatabaseTool", "validation_failed", {
                    "reason": error_msg,
                    "query": sql_query[:100]
                })
                return False, error_msg
                
        # Ensure query is a SELECT statement
        if not sql_lower.startswith("select"):
            error_msg = "Only SELECT queries are allowed"
            log_agent_action("DatabaseTool", "validation_failed", {
                "reason": error_msg,
                "query": sql_query[:100]
            })
            return False, error_msg
            
        log_agent_action("DatabaseTool", "validation_passed", {
            "query": sql_query[:100]
        })
        return True, None
        
    def get_sample_data(self, table_name: str, limit: int = 5) -> pd.DataFrame:
        """Get sample rows from a table"""
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        success, df, error = self.execute_query(query)
        
        if success:
            return df
        else:
            raise ValueError(f"Failed to get sample data: {error}")
            
    def close(self):
        """Close database connection"""
        self.engine.dispose()
        log_agent_action("DatabaseTool", "connection_closed", {})
