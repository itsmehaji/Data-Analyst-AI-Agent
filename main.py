"""
Interactive command-line interface for the Data Analyst AI Agent
"""
from agent import DataAnalystAgent
from utils.logger import logger
import sys
from pathlib import Path


def print_banner():
    """Print welcome banner"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║         Data Analyst AI Assistant                         ║
║         Natural Language to SQL Query System              ║
╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_help():
    """Print help message"""
    help_text = """
Available commands:
  - Type your question in natural language
  - 'schema' - Show database schema
  - 'history' - Show conversation history
  - 'metrics' - Show performance metrics
  - 'clear' - Clear conversation history
  - 'help' - Show this help message
  - 'exit' or 'quit' - Exit the application

Example queries:
  - "What are the top 5 products by revenue?"
  - "Show me total sales by region"
  - "How many customers signed up last month?"
  - "What's the average order value?"
    """
    print(help_text)


def format_dataframe(df):
    """Format dataframe for display"""
    if df is None or df.empty:
        return "No results"
    
    # Show first 10 rows
    if len(df) > 10:
        display_df = df.head(10)
        footer = f"\n... and {len(df) - 10} more rows"
    else:
        display_df = df
        footer = ""
    
    return display_df.to_string() + footer


def main():
    """Main interactive loop"""
    print_banner()
    
    # Check if .env file exists
    if not Path(".env").exists():
        print("⚠️  Warning: .env file not found!")
        print("Please create a .env file with your GOOGLE_API_KEY")
        print("You can copy .env.example and fill in your API key")
        return
    
    try:
        # Initialize agent
        print("Initializing Data Analyst AI Agent...")
        agent = DataAnalystAgent()
        print("✅ Agent initialized successfully!\n")
        
        # Show schema info
        schema = agent.get_schema_info()
        print(f"Connected to database with {len(schema)} tables: {', '.join(schema.keys())}\n")
        
        print("Type 'help' for available commands or start asking questions!\n")
        
        # Main loop
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                    
                user_input_lower = user_input.lower()
                
                # Handle commands
                if user_input_lower in ['exit', 'quit']:
                    print("\nSaving state and exiting...")
                    agent.save_state()
                    print("Goodbye! 👋")
                    break
                    
                elif user_input_lower == 'help':
                    print_help()
                    continue
                    
                elif user_input_lower == 'schema':
                    schema = agent.get_schema_info()
                    print("\n📊 Database Schema:")
                    for table_name, columns in schema.items():
                        print(f"\n  Table: {table_name}")
                        for col in columns:
                            print(f"    - {col['name']} ({col['type']})")
                    print()
                    continue
                    
                elif user_input_lower == 'history':
                    history = agent.get_conversation_history()
                    print("\n💬 Conversation History:")
                    for msg in history:
                        role = msg['role'].upper()
                        content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
                        print(f"  {role}: {content}")
                    print()
                    continue
                    
                elif user_input_lower == 'metrics':
                    metrics = agent.get_metrics()
                    print("\n📈 Performance Metrics:")
                    for key, value in metrics.items():
                        if isinstance(value, float):
                            print(f"  {key}: {value:.2f}")
                        else:
                            print(f"  {key}: {value}")
                    print()
                    continue
                    
                elif user_input_lower == 'clear':
                    agent.clear_history()
                    print("✅ Conversation history cleared.\n")
                    continue
                
                # Process natural language query
                print("\n🤔 Processing your query...\n")
                result = agent.query(user_input, return_visualization=False)
                
                if result['success']:
                    print(f"🔍 Generated SQL:")
                    print(f"   {result['sql_query']}\n")
                    
                    print(f"📊 Results ({result['response_time']:.2f}s):")
                    print(format_dataframe(result['results']))
                    print()
                    
                    print(f"💡 Interpretation:")
                    print(f"   {result['interpretation']}\n")
                else:
                    print(f"❌ Error at {result['stage']} stage:")
                    print(f"   {result['error']}\n")
                    
            except KeyboardInterrupt:
                print("\n\nInterrupted. Type 'exit' to quit properly.\n")
                continue
            except Exception as e:
                print(f"\n❌ Error: {str(e)}\n")
                logger.error("main_loop_error", error=str(e))
                continue
                
    except Exception as e:
        print(f"\n❌ Failed to initialize agent: {str(e)}")
        print("Make sure your .env file has a valid GOOGLE_API_KEY")
        return
    finally:
        try:
            agent.close()
        except:
            pass


if __name__ == "__main__":
    main()
