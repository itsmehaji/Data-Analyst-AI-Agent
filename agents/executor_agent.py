"""
Query Executor Agent
Executes validated SQL queries against the database
"""
import pandas as pd
from typing import Tuple, Optional
from utils.logger import log_agent_action, log_error
from tools.database_tool import DatabaseTool


class QueryExecutorAgent:
    """
    Agent responsible for:
    1. Executing validated SQL queries
    2. Handling execution errors
    3. Returning query results
    """
    
    def __init__(self, db_tool: DatabaseTool):
        self.db_tool = db_tool
        log_agent_action("QueryExecutorAgent", "initialized", {})
        
    def execute(self, sql_query: str) -> Tuple[bool, Optional[pd.DataFrame], Optional[str]]:
        """
        Execute SQL query and return results
        
        Args:
            sql_query: Validated SQL query to execute
            
        Returns:
            Tuple of (success, results_dataframe, error_message)
        """
        try:
            log_agent_action("QueryExecutorAgent", "executing_query", {
                "sql": sql_query[:200]
            })
            
            success, df, error = self.db_tool.execute_query(sql_query)
            
            if success:
                if df is not None:
                    log_agent_action("QueryExecutorAgent", "execution_success", {
                        "rows": len(df),
                        "columns": list(df.columns) if not df.empty else []
                    })
                else:
                    log_agent_action("QueryExecutorAgent", "execution_success", {
                        "message": "Query executed successfully (no results returned)"
                    })
                return True, df, None
            else:
                log_agent_action("QueryExecutorAgent", "execution_failed", {
                    "error": error
                })
                return False, None, error
                
        except Exception as e:
            log_error("QueryExecutorAgent", e, {"query": sql_query[:200]})
            return False, None, str(e)
            
    def get_result_summary(self, df: pd.DataFrame) -> str:
        """
        Generate a summary of query results
        
        Args:
            df: Results dataframe
            
        Returns:
            Text summary of results
        """
        if df is None or df.empty:
            return "No results found."
            
        summary_parts = [
            f"Found {len(df)} row(s)",
            f"Columns: {', '.join(df.columns)}",
        ]
        
        # Add data type info
        dtypes = [f"{col}: {dtype}" for col, dtype in df.dtypes.items()]
        summary_parts.append(f"Data types: {', '.join(dtypes)}")
        
        log_agent_action("QueryExecutorAgent", "summary_generated", {
            "rows": len(df),
            "columns": len(df.columns)
        })
        
        return "\n".join(summary_parts)
