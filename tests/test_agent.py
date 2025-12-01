"""
Unit tests for the Data Analyst AI Agent
"""
import pytest
from agent import DataAnalystAgent
from tools.database_tool import DatabaseTool
from utils.memory import InMemorySessionService, MemoryBank
import os
from pathlib import Path


# Skip tests if no API key is available
skip_if_no_api_key = pytest.mark.skipif(
    not os.getenv("GOOGLE_API_KEY"),
    reason="GOOGLE_API_KEY not set"
)


class TestDatabaseTool:
    """Tests for DatabaseTool"""
    
    def test_connection(self):
        """Test database connection"""
        db = DatabaseTool()
        schema = db.get_schema_info()
        assert isinstance(schema, dict)
        assert len(schema) > 0
        db.close()
        
    def test_query_validation_safe(self):
        """Test query validation for safe queries"""
        db = DatabaseTool()
        is_safe, error = db.validate_query_safety("SELECT * FROM products")
        assert is_safe
        assert error is None
        db.close()
        
    def test_query_validation_unsafe(self):
        """Test query validation for unsafe queries"""
        db = DatabaseTool()
        is_safe, error = db.validate_query_safety("DROP TABLE products")
        assert not is_safe
        assert error is not None
        db.close()
        
    def test_execute_query(self):
        """Test query execution"""
        db = DatabaseTool()
        success, df, error = db.execute_query("SELECT * FROM products LIMIT 5")
        assert success
        assert df is not None
        assert len(df) > 0
        db.close()


class TestMemorySystem:
    """Tests for memory management"""
    
    def test_session_creation(self):
        """Test session creation"""
        session = InMemorySessionService()
        session_id = session.create_session("test-session")
        assert session_id == "test-session"
        assert "test-session" in session.sessions
        
    def test_message_storage(self):
        """Test message storage and retrieval"""
        session = InMemorySessionService(max_history=5)
        session_id = "test-session"
        session.create_session(session_id)
        
        session.add_message(session_id, "user", "Hello")
        session.add_message(session_id, "assistant", "Hi there")
        
        history = session.get_history(session_id)
        assert len(history) == 2
        assert history[0].role == "user"
        assert history[1].role == "assistant"
        
    def test_memory_bank_schema_cache(self):
        """Test schema caching in memory bank"""
        memory = MemoryBank()
        schema = {"products": [{"name": "id", "type": "INTEGER"}]}
        
        memory.store_schema(schema)
        cached = memory.get_schema()
        
        assert cached == schema
        
    def test_memory_bank_query_patterns(self):
        """Test query pattern storage"""
        memory = MemoryBank()
        
        memory.add_query_pattern("total sales", "SELECT SUM(total) FROM sales", True)
        patterns = memory.get_similar_patterns("total sales")
        
        assert len(patterns) > 0


@skip_if_no_api_key
class TestDataAnalystAgent:
    """Tests for main agent (requires API key)"""
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        agent = DataAnalystAgent()
        assert agent.validator is not None
        assert agent.executor is not None
        assert agent.interpreter is not None
        assert agent.memory_bank.get_schema() is not None
        agent.close()
        
    def test_simple_query(self):
        """Test a simple query execution"""
        agent = DataAnalystAgent()
        result = agent.query("Show me all products")
        
        assert result['success'] == True
        assert 'sql_query' in result
        assert 'results' in result
        assert result['results'] is not None
        
        agent.close()
        
    def test_query_with_context(self):
        """Test query with conversation context"""
        agent = DataAnalystAgent()
        
        # First query
        result1 = agent.query("What products do we have?")
        assert result1['success']
        
        # Second query with context
        result2 = agent.query("Show me the top 3 by price")
        assert result2['success']
        
        agent.close()
        
    def test_get_metrics(self):
        """Test metrics retrieval"""
        agent = DataAnalystAgent()
        agent.query("SELECT * FROM products LIMIT 1")
        
        metrics = agent.get_metrics()
        assert 'queries_processed' in metrics
        assert metrics['queries_processed'] > 0
        
        agent.close()


def test_sample_database_exists():
    """Test that sample database file exists"""
    db_path = Path("sample_data.db")
    assert db_path.exists(), "Run 'python setup_database.py' first"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
