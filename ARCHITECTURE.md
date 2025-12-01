# Architecture Documentation

## Overview
The Data Analyst AI Assistant is a multi-agent system that converts natural language questions into SQL queries, executes them safely, and provides intelligent interpretations of results.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface                            │
│              (CLI / Python API / Notebook)                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                Data Analyst Agent                            │
│                  (Orchestrator)                              │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Session & Memory Management                         │  │
│  │  - InMemorySessionService (conversation history)     │  │
│  │  - MemoryBank (schema cache, query patterns)         │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼             ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Validator  │ │   Executor   │ │ Interpreter  │
│    Agent     │ │    Agent     │ │    Agent     │
│              │ │              │ │              │
│ - NL to SQL  │ │ - Execute    │ │ - Generate   │
│ - Validate   │ │   queries    │ │   insights   │
│   safety     │ │ - Return     │ │ - Create viz │
│              │ │   results    │ │              │
└──────┬───────┘ └──────┬───────┘ └──────────────┘
       │                │
       │                │
       ▼                ▼
┌──────────────────────────────────┐
│      Database Tool               │
│  - Schema inspection             │
│  - Query execution               │
│  - Safety validation             │
└────────────┬─────────────────────┘
             │
             ▼
     ┌──────────────┐
     │   Database   │
     │   (SQLite)   │
     └──────────────┘
```

## Agent Workflow (Sequential Processing)

### Stage 1: Query Validation
**Validator Agent** (`validator_agent.py`)

1. Receives natural language query
2. Retrieves database schema from MemoryBank
3. Gets conversation context from SessionService
4. Uses Gemini to generate SQL query
5. Validates query safety (blocks DROP, DELETE, etc.)
6. Returns validated SQL or error

**Technologies:**
- Google Generative AI (Gemini 2.0)
- Custom safety validation rules

### Stage 2: Query Execution
**Executor Agent** (`executor_agent.py`)

1. Receives validated SQL query
2. Executes query using DatabaseTool
3. Handles execution errors
4. Returns results as pandas DataFrame
5. Generates result summary

**Technologies:**
- SQLAlchemy for database operations
- Pandas for data manipulation

### Stage 3: Result Interpretation
**Interpreter Agent** (`interpreter_agent.py`)

1. Receives query results
2. Analyzes data patterns
3. Uses Gemini to generate natural language insights
4. Creates appropriate visualizations (optional)
5. Returns interpretation and visualization

**Technologies:**
- Google Generative AI (Gemini 2.0)
- Plotly for visualizations

## Core Components

### 1. Multi-Agent System
- **Three specialized agents** working in sequence
- Each agent has specific responsibilities
- Clear separation of concerns
- Sequential workflow ensures data validation

### 2. Tools
- **DatabaseTool**: Custom tool for safe database operations
  - Schema inspection
  - Query execution
  - Safety validation
- **Built-in tools**: Code execution via Gemini

### 3. Memory & Sessions
- **InMemorySessionService**:
  - Stores conversation history
  - Maintains context across queries
  - Supports multiple concurrent sessions
  
- **MemoryBank**:
  - Caches database schema
  - Stores successful query patterns
  - Learns user preferences
  - Persists to disk

### 4. Observability
- **Structured Logging** (structlog):
  - JSON-formatted logs
  - Action tracing for each agent
  - Error logging with context
  
- **Metrics Tracking**:
  - Query success/failure rates
  - Response times
  - Validation/execution errors
  - Average performance

- **State Persistence**:
  - Session history saved to disk
  - Memory bank serialization
  - Metrics export to JSON

### 5. Agent Evaluation
- Automated test suite
- Accuracy metrics calculation
- Response time tracking
- SQL generation quality assessment

## Data Flow

1. **User Input** → Natural language question
2. **Orchestrator** → Routes to Validator Agent
3. **Validator** → Generates & validates SQL
4. **Orchestrator** → Routes SQL to Executor Agent
5. **Executor** → Executes query, returns DataFrame
6. **Orchestrator** → Routes results to Interpreter Agent
7. **Interpreter** → Generates insights & visualization
8. **Orchestrator** → Combines all results
9. **User Output** → SQL, results, interpretation

## Memory Management

### Short-term Memory (Session)
- Last N messages in conversation
- User queries and agent responses
- Query metadata (SQL, response times)
- Session-specific context

### Long-term Memory (MemoryBank)
- Database schema (cached)
- Historical query patterns
- User preferences
- Performance statistics

### Context Engineering
- Automatic context summarization
- Relevant history injection
- Schema information formatting
- Similar query pattern matching

## Safety & Validation

### Query Safety Rules
1. Only SELECT queries allowed
2. No DROP, DELETE, UPDATE, INSERT
3. No schema modifications
4. No privilege changes (GRANT, REVOKE)

### Error Handling
- Validation errors caught before execution
- Execution errors logged and reported
- Graceful degradation
- User-friendly error messages

## Performance Considerations

### Optimization Strategies
1. **Schema Caching**: Database schema cached in memory
2. **Context Compaction**: Limited conversation history
3. **Efficient SQL Generation**: Low temperature for deterministic outputs
4. **Connection Pooling**: SQLAlchemy connection management

### Metrics
- Average response time: ~2-4 seconds
- Query validation: ~1-2 seconds
- Query execution: <1 second (depends on query)
- Interpretation: ~1-2 seconds

## Extensibility

### Adding New Agents
Implement agent interface with:
- `__init__`: Setup
- `process`: Main logic
- Logging integration
- Error handling

### Adding New Tools
Extend DatabaseTool or create new tool classes:
- Define tool methods
- Add logging
- Implement error handling
- Register with agents

### Supporting New Databases
- Update DatabaseTool with new connection string
- Ensure SQL dialect compatibility
- Test query validation rules

## Deployment Considerations

### Local Deployment
- Python environment setup
- SQLite database (included)
- No external dependencies beyond API key

### Cloud Deployment (Optional)
- Google Cloud Agent Engine
- Cloud Run for API serving
- Cloud SQL for production database
- Secret Manager for API keys

## Capstone Requirements Coverage

✅ **Multi-agent system**: 3 sequential agents  
✅ **Tools**: Custom DatabaseTool + Gemini built-ins  
✅ **Sessions & Memory**: InMemorySessionService + MemoryBank  
✅ **Observability**: Structlog + metrics tracking  
✅ **Agent evaluation**: Automated test suite with accuracy metrics  

**Bonus:**  
✅ **Gemini usage**: Powers Validator and Interpreter agents  
✅ **Documentation**: Comprehensive README and architecture docs
