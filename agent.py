"""
Main Data Analyst AI Agent
Orchestrates the multi-agent workflow
"""
import time
from typing import Dict, Optional, Tuple
import pandas as pd
from agents.validator_agent import QueryValidatorAgent
from agents.executor_agent import QueryExecutorAgent
from agents.interpreter_agent import ResultInterpreterAgent
from tools.database_tool import DatabaseTool
from utils.memory import InMemorySessionService, MemoryBank
from utils.logger import log_agent_action, log_error, metrics
from config import MAX_CONVERSATION_HISTORY
import uuid


class DataAnalystAgent:
    """
    Main orchestrator for the Data Analyst AI Assistant
    Coordinates validator, executor, and interpreter agents in a sequential workflow
    """
    
    def __init__(self, database_url: str = None):
        """Initialize the multi-agent system"""
        log_agent_action("DataAnalystAgent", "initializing", {})
        
        # Initialize database tool
        self.db_tool = DatabaseTool(database_url) if database_url else DatabaseTool()
        
        # Initialize agents
        self.validator = QueryValidatorAgent(self.db_tool)
        self.executor = QueryExecutorAgent(self.db_tool)
        self.interpreter = ResultInterpreterAgent()
        
        # Initialize memory systems
        self.session_service = InMemorySessionService(max_history=MAX_CONVERSATION_HISTORY)
        self.memory_bank = MemoryBank()
        
        # Load and cache schema
        schema = self.db_tool.get_schema_info()
        self.memory_bank.store_schema(schema)
        
        # Create default session
        self.current_session = str(uuid.uuid4())
        self.session_service.create_session(self.current_session)
        
        log_agent_action("DataAnalystAgent", "initialized", {
            "session_id": self.current_session,
            "tables": list(schema.keys())
        })
        
    def query(self, natural_language_query: str, 
             session_id: Optional[str] = None,
             return_visualization: bool = False) -> Dict:
        """
        Process a natural language query through the multi-agent pipeline
        
        Args:
            natural_language_query: User's question in natural language
            session_id: Session ID for conversation context (optional)
            return_visualization: Whether to include visualization (optional)
            
        Returns:
            Dictionary containing results, interpretation, and metadata
        """
        start_time = time.time()
        session_id = session_id or self.current_session
        
        log_agent_action("DataAnalystAgent", "query_received", {
            "query": natural_language_query[:100],
            "session_id": session_id
        })
        
        # Add user message to session
        self.session_service.add_message(session_id, "user", natural_language_query)
        
        # Get conversation context
        context = self.session_service.get_context(session_id)
        
        # Get cached schema
        schema = self.memory_bank.get_schema()
        
        # Step 1: Validate and generate SQL (Validator Agent)
        log_agent_action("DataAnalystAgent", "step_1_validation", {})
        success, sql_query, error = self.validator.process(
            natural_language_query, 
            schema,
            context
        )
        
        if not success:
            response_time = time.time() - start_time
            metrics.record_query(False, response_time, "validation")
            log_agent_action("DataAnalystAgent", "query_failed", {
                "stage": "validation",
                "error": error
            })
            return {
                "success": False,
                "error": error,
                "stage": "validation",
                "response_time": response_time
            }
            
        # Step 2: Execute SQL (Executor Agent)
        log_agent_action("DataAnalystAgent", "step_2_execution", {"sql": sql_query[:200]})
        success, results_df, error = self.executor.execute(sql_query)
        
        if not success:
            response_time = time.time() - start_time
            metrics.record_query(False, response_time, "execution")
            self.memory_bank.add_query_pattern(natural_language_query, sql_query, False)
            log_agent_action("DataAnalystAgent", "query_failed", {
                "stage": "execution",
                "error": error
            })
            return {
                "success": False,
                "error": error,
                "stage": "execution",
                "sql_query": sql_query,
                "response_time": response_time
            }
            
        # Step 3: Interpret results (Interpreter Agent)
        log_agent_action("DataAnalystAgent", "step_3_interpretation", {})
        success, interpretation, error = self.interpreter.interpret_results(
            natural_language_query,
            sql_query,
            results_df
        )
        
        if not success:
            interpretation = "Results retrieved but interpretation failed."
            
        # Create visualization if requested and appropriate
        visualization = None
        if return_visualization and results_df is not None and not results_df.empty:
            visualization = self.interpreter.create_visualization(results_df)
            
        # Record success
        response_time = time.time() - start_time
        metrics.record_query(True, response_time)
        self.memory_bank.add_query_pattern(natural_language_query, sql_query, True)
        
        # Add assistant response to session
        self.session_service.add_message(
            session_id, 
            "assistant", 
            interpretation,
            {"sql": sql_query, "rows": len(results_df) if results_df is not None else 0}
        )
        
        log_agent_action("DataAnalystAgent", "query_completed", {
            "response_time": response_time,
            "rows": len(results_df) if results_df is not None else 0
        })
        
        return {
            "success": True,
            "query": natural_language_query,
            "sql_query": sql_query,
            "results": results_df,
            "interpretation": interpretation,
            "visualization": visualization,
            "response_time": response_time,
            "session_id": session_id
        }
        
    def get_schema_info(self) -> Dict:
        """Get database schema information"""
        return self.memory_bank.get_schema()
        
    def get_conversation_history(self, session_id: Optional[str] = None) -> list:
        """Get conversation history for a session"""
        session_id = session_id or self.current_session
        history = self.session_service.get_history(session_id)
        return [{"role": msg.role, "content": msg.content} for msg in history]
        
    def clear_history(self, session_id: Optional[str] = None):
        """Clear conversation history"""
        session_id = session_id or self.current_session
        self.session_service.clear_session(session_id)
        log_agent_action("DataAnalystAgent", "history_cleared", {"session_id": session_id})
        
    def get_metrics(self) -> Dict:
        """Get agent performance metrics"""
        return metrics.get_metrics()
        
    def save_state(self):
        """Save session and memory state to disk"""
        self.session_service.save_session(
            self.current_session, 
            "logs/session_state.json"
        )
        self.memory_bank.save_to_file("logs/memory_bank.json")
        metrics.save_metrics("logs/metrics.json")
        log_agent_action("DataAnalystAgent", "state_saved", {})
        
    def close(self):
        """Clean up resources"""
        self.save_state()
        self.db_tool.close()
        log_agent_action("DataAnalystAgent", "closed", {})
