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

## 🚀 Setup Instructions

### Prerequisites
- Python 3.10+
- SQLite (included) or PostgreSQL/MySQL
- Google AI API key (for Gemini)

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd Google-AI-Agent-Capstone
```

2. Create virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Create .env file
GOOGLE_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///sample_data.db
```

5. Initialize sample database:
```bash
python setup_database.py
```

## 📖 Usage

### Basic Query
```python
from agent import DataAnalystAgent

agent = DataAnalystAgent()
response = agent.query("Show me total sales by region for last quarter")
print(response)
```

### Interactive Mode
```bash
python main.py
```

## 🧪 Running Tests
```bash
python -m pytest tests/
```

## 📊 Demo

The system includes a sample e-commerce database with:
- Customers table
- Orders table
- Products table
- Sales transactions

Example queries:
- "What were the top 5 products by revenue last month?"
- "Show me customer retention rate by region"
- "Compare sales trends year over year"

## 🎬 Video Demo
[Link to YouTube video - under 3 minutes]

## 🏆 Capstone Track
**Enterprise Agents** - Automating data analysis workflows

## 🛠️ Technologies Used
- Google ADK-Python
- Gemini 2.0 (via Google AI Studio)
- SQLite/PostgreSQL
- Pandas for data processing
- Plotly for visualizations
- Python logging & OpenTelemetry

## 📝 Project Journey
[Document your development process, challenges faced, and solutions]

## 👥 Team
[Your team member names and Kaggle usernames]

## 📄 License
MIT License
