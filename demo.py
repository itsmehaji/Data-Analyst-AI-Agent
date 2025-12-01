"""
Demo script showcasing agent capabilities
"""
from agent import DataAnalystAgent
import time


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def run_demo():
    """Run demonstration of agent capabilities"""
    
    print_section("🚀 Data Analyst AI Agent Demo")
    
    # Initialize agent
    print("Initializing agent...")
    agent = DataAnalystAgent()
    print("✅ Agent initialized!\n")
    
    # Show schema
    print_section("📊 Database Schema")
    schema = agent.get_schema_info()
    for table_name, columns in schema.items():
        print(f"\n{table_name}:")
        for col in columns[:5]:  # Show first 5 columns
            print(f"  - {col['name']} ({col['type']})")
    
    # Example queries
    demo_queries = [
        "What are the top 5 products by revenue?",
        "Show me total sales by region",
        "How many customers do we have in each region?",
        "What is the average order value?",
        "Which product category generates the most revenue?"
    ]
    
    print_section("💬 Example Queries")
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n{'─' * 60}")
        print(f"Query {i}: {query}")
        print(f"{'─' * 60}")
        
        result = agent.query(query)
        
        if result['success']:
            print(f"\n✅ SQL Generated:")
            print(f"   {result['sql_query']}")
            
            print(f"\n📊 Results ({result['response_time']:.2f}s):")
            df = result['results']
            if df is not None and not df.empty:
                print(df.head(10).to_string(index=False))
                if len(df) > 10:
                    print(f"   ... and {len(df) - 10} more rows")
            else:
                print("   No results")
            
            print(f"\n💡 Interpretation:")
            print(f"   {result['interpretation']}")
        else:
            print(f"\n❌ Error: {result['error']}")
        
        time.sleep(1)  # Small delay between queries
    
    # Show metrics
    print_section("📈 Performance Metrics")
    metrics = agent.get_metrics()
    print(f"Total Queries: {metrics['queries_processed']}")
    print(f"Successful: {metrics['successful_queries']}")
    print(f"Failed: {metrics['failed_queries']}")
    print(f"Average Response Time: {metrics['average_response_time']:.2f}s")
    
    # Show conversation history
    print_section("💬 Conversation History")
    history = agent.get_conversation_history()
    print(f"Total messages: {len(history)}")
    for msg in history[-3:]:  # Show last 3 messages
        role = msg['role'].upper()
        content = msg['content'][:80] + "..." if len(msg['content']) > 80 else msg['content']
        print(f"{role}: {content}")
    
    # Clean up
    print_section("🏁 Demo Complete")
    agent.save_state()
    agent.close()
    print("Agent state saved. Goodbye! 👋")


if __name__ == "__main__":
    run_demo()
