"""
Session and Memory Management for conversation context
"""
from typing import List, Dict, Optional
from datetime import datetime
import json
from pathlib import Path


class Message:
    """Represents a conversation message"""
    
    def __init__(self, role: str, content: str, metadata: Dict = None):
        self.role = role  # 'user' or 'assistant'
        self.content = content
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow().isoformat()
        
    def to_dict(self) -> Dict:
        return {
            "role": self.role,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }
        
    @classmethod
    def from_dict(cls, data: Dict):
        msg = cls(data["role"], data["content"], data.get("metadata", {}))
        msg.timestamp = data.get("timestamp", msg.timestamp)
        return msg


class InMemorySessionService:
    """
    In-memory session management service
    Maintains conversation history and context
    """
    
    def __init__(self, max_history: int = 10):
        self.sessions: Dict[str, List[Message]] = {}
        self.max_history = max_history
        self.current_session_id: Optional[str] = None
        
    def create_session(self, session_id: str) -> str:
        """Create a new session"""
        self.sessions[session_id] = []
        self.current_session_id = session_id
        return session_id
        
    def add_message(self, session_id: str, role: str, content: str, metadata: Dict = None):
        """Add a message to session history"""
        if session_id not in self.sessions:
            self.create_session(session_id)
            
        message = Message(role, content, metadata)
        self.sessions[session_id].append(message)
        
        # Keep only last N messages
        if len(self.sessions[session_id]) > self.max_history:
            self.sessions[session_id] = self.sessions[session_id][-self.max_history:]
            
    def get_history(self, session_id: str) -> List[Message]:
        """Get conversation history for a session"""
        return self.sessions.get(session_id, [])
        
    def get_context(self, session_id: str) -> str:
        """Get formatted conversation context"""
        history = self.get_history(session_id)
        context_parts = []
        
        for msg in history[-5:]:  # Last 5 messages for context
            context_parts.append(f"{msg.role.upper()}: {msg.content}")
            
        return "\n".join(context_parts)
        
    def clear_session(self, session_id: str):
        """Clear a session's history"""
        if session_id in self.sessions:
            self.sessions[session_id] = []
            
    def save_session(self, session_id: str, filepath: str):
        """Save session to file"""
        if session_id in self.sessions:
            data = [msg.to_dict() for msg in self.sessions[session_id]]
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
                
    def load_session(self, session_id: str, filepath: str):
        """Load session from file"""
        if Path(filepath).exists():
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.sessions[session_id] = [Message.from_dict(msg) for msg in data]


class MemoryBank:
    """
    Long-term memory storage for learned information
    Stores database schemas, common queries, and user preferences
    """
    
    def __init__(self):
        self.schema_cache: Optional[Dict] = None
        self.query_patterns: List[Dict] = []
        self.user_preferences: Dict = {}
        
    def store_schema(self, schema: Dict):
        """Cache database schema"""
        self.schema_cache = schema
        
    def get_schema(self) -> Optional[Dict]:
        """Retrieve cached schema"""
        return self.schema_cache
        
    def add_query_pattern(self, natural_language: str, sql_query: str, success: bool):
        """Store a query pattern for learning"""
        pattern = {
            "nl": natural_language,
            "sql": sql_query,
            "success": success,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.query_patterns.append(pattern)
        
        # Keep only last 100 patterns
        if len(self.query_patterns) > 100:
            self.query_patterns = self.query_patterns[-100:]
            
    def get_similar_patterns(self, query: str, limit: int = 3) -> List[Dict]:
        """Find similar query patterns (simple keyword matching)"""
        query_lower = query.lower()
        scored_patterns = []
        
        for pattern in self.query_patterns:
            if pattern["success"]:
                # Simple keyword matching score
                nl_lower = pattern["nl"].lower()
                common_words = set(query_lower.split()) & set(nl_lower.split())
                score = len(common_words)
                
                if score > 0:
                    scored_patterns.append((score, pattern))
                    
        # Sort by score and return top matches
        scored_patterns.sort(reverse=True, key=lambda x: x[0])
        return [p[1] for p in scored_patterns[:limit]]
        
    def set_preference(self, key: str, value: any):
        """Store user preference"""
        self.user_preferences[key] = value
        
    def get_preference(self, key: str, default: any = None) -> any:
        """Get user preference"""
        return self.user_preferences.get(key, default)
        
    def save_to_file(self, filepath: str = "logs/memory_bank.json"):
        """Save memory bank to file"""
        data = {
            "schema_cache": self.schema_cache,
            "query_patterns": self.query_patterns,
            "user_preferences": self.user_preferences
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
            
    def load_from_file(self, filepath: str = "logs/memory_bank.json"):
        """Load memory bank from file"""
        if Path(filepath).exists():
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.schema_cache = data.get("schema_cache")
                self.query_patterns = data.get("query_patterns", [])
                self.user_preferences = data.get("user_preferences", {})
