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


