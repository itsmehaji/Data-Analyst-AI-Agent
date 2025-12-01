"""
Configuration module for the Data Analyst AI Assistant
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///sample_data.db")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = "logs/agent.log"

# Agent Configuration
MAX_CONVERSATION_HISTORY = int(os.getenv("MAX_CONVERSATION_HISTORY", "10"))
ENABLE_QUERY_VALIDATION = os.getenv("ENABLE_QUERY_VALIDATION", "true").lower() == "true"

# Model Configuration
MODEL_NAME = "models/gemini-2.5-flash"  # Stable Gemini 2.5 Flash model
TEMPERATURE = 0.1  # Low temperature for more deterministic SQL generation
MAX_OUTPUT_TOKENS = 2048
