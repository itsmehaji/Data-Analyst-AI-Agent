# Data Analyst AI Assistant

## 🎯 Problem Statement
Non-technical users struggle to extract insights from databases due to the complexity of SQL. Data analysts spend significant time writing repetitive queries instead of focusing on analysis.

## 💡 Solution
An intelligent multi-agent system that converts natural language questions into SQL queries, executes them safely, and presents results in an understandable format with visualizations.

## 🏗️ Architecture

### Multi-Agent System
1. **Query Validator Agent**: Analyzes natural language input, generates SQL, and validates query safety
2. **Query Executor Agent**: Executes validated SQL queries against the database
3. **Result Interpreter Agent**: Analyzes results and generates insights with visualizations

### Key Features (Meeting Capstone Requirements)
✅ **Multi-agent system**: Sequential workflow with 3 specialized agents  
✅ **Tools**: Custom database tools, built-in Code Execution  
✅ **Sessions & Memory**: Conversation history and schema learning  
✅ **Observability**: Comprehensive logging, tracing, and metrics  
✅ **Agent Evaluation**: Test suite with accuracy metrics  


# Quick Start Guide

## Prerequisites
- Python 3.10 or higher
- Google AI API key (get one at https://aistudio.google.com/app/apikey)

## Installation Steps

### 1. Set up environment
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Key
```powershell
# Copy example env file
Copy-Item .env.example .env

# Edit .env and add your API key
# GOOGLE_API_KEY=your_actual_api_key_here
```

### 3. Create Sample Database
```powershell
python setup_database.py
```

This creates a sample e-commerce database with:
- 100 customers across 4 regions
- 15 products in 5 categories
- Realistic orders and sales data

## Usage Options

### Option 1: Interactive Mode (Recommended)
```powershell
python main.py
```

Then type queries like:
- "What are the top 5 products by revenue?"
- "Show me total sales by region"
- "How many customers signed up last month?"

Commands:
- `schema` - View database structure
- `history` - View conversation history
- `metrics` - View performance stats
- `clear` - Clear conversation
- `exit` - Quit

### Option 2: Demo Mode
```powershell
python demo.py
```

Runs pre-configured queries to showcase capabilities.

### Option 3: Python API
```python
from agent import DataAnalystAgent

# Initialize agent
agent = DataAnalystAgent()

# Query
result = agent.query("What are the top 5 products by revenue?")

# Access results
print(result['sql_query'])
print(result['results'])
print(result['interpretation'])

# Clean up
agent.close()
```

## Running Tests

```powershell
# Run unit tests
python -m pytest tests/ -v

# Run evaluation suite
python evaluate.py
```

## Troubleshooting

### Error: "GOOGLE_API_KEY not found"
Make sure `.env` file exists with valid API key.

### Error: "No module named 'google.generativeai'"
Install dependencies: `pip install -r requirements.txt`

### Error: Database not found
Run: `python setup_database.py`

## Project Structure
```
Google-AI-Agent-Capstone/
├── agents/              # Three specialized agents
│   ├── validator_agent.py
│   ├── executor_agent.py
│   └── interpreter_agent.py
├── tools/               # Custom database tools
│   └── database_tool.py
├── utils/               # Memory and logging
│   ├── memory.py
│   └── logger.py
├── tests/               # Unit tests
├── agent.py             # Main orchestrator
├── main.py              # Interactive CLI
├── demo.py              # Demo script
├── evaluate.py          # Evaluation framework
└── setup_database.py    # Database setup
```

## Next Steps
1. ✅ Run `setup_database.py`
2. ✅ Configure your API key in `.env`
3. ✅ Try `python main.py`
4. ✅ Experiment with queries
5. ✅ Run evaluation with `python evaluate.py`

## Support
For issues, check logs in `logs/` directory.
