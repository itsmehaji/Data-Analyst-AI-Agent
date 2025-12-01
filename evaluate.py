"""
Evaluation framework for testing agent accuracy
"""
from agent import DataAnalystAgent
from typing import List, Dict, Tuple
import time
import json
from pathlib import Path


class AgentEvaluator:
    """
    Evaluation framework to test agent performance
    Tests SQL generation accuracy against expected queries
    """
    
    def __init__(self, agent: DataAnalystAgent):
        self.agent = agent
        self.test_results = []
        
    def run_test_suite(self, test_cases: List[Dict]) -> Dict:
        """
        Run a suite of test cases
        
        Args:
            test_cases: List of test case dictionaries with:
                - natural_query: The NL question
                - expected_sql: Expected SQL (optional)
                - should_succeed: Whether query should succeed
                - description: Test description
                
        Returns:
            Dictionary with evaluation metrics
        """
        print("🧪 Running Agent Evaluation Suite\n")
        print("=" * 60)
        
        passed = 0
        failed = 0
        total_time = 0
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest {i}/{len(test_cases)}: {test_case['description']}")
            print(f"Query: {test_case['natural_query']}")
            
            start_time = time.time()
            result = self.agent.query(test_case['natural_query'])
            elapsed = time.time() - start_time
            total_time += elapsed
            
            # Evaluate result
            success = result['success']
            expected_success = test_case.get('should_succeed', True)
            
            test_passed = (success == expected_success)
            
            if test_passed:
                passed += 1
                status = "✅ PASS"
            else:
                failed += 1
                status = "❌ FAIL"
                
            # Store result
            test_result = {
                "test_id": i,
                "description": test_case['description'],
                "natural_query": test_case['natural_query'],
                "generated_sql": result.get('sql_query', ''),
                "expected_sql": test_case.get('expected_sql', ''),
                "success": success,
                "expected_success": expected_success,
                "passed": test_passed,
                "response_time": elapsed,
                "error": result.get('error', None),
                "rows_returned": len(result.get('results', [])) if result.get('results') is not None else 0
            }
            self.test_results.append(test_result)
            
            print(f"Status: {status}")
            print(f"Response time: {elapsed:.2f}s")
            if result.get('sql_query'):
                print(f"Generated SQL: {result['sql_query'][:100]}...")
            if not test_passed and result.get('error'):
                print(f"Error: {result['error']}")
            print("-" * 60)
        
        # Calculate metrics
        accuracy = passed / len(test_cases) if test_cases else 0
        avg_time = total_time / len(test_cases) if test_cases else 0
        
        summary = {
            "total_tests": len(test_cases),
            "passed": passed,
            "failed": failed,
            "accuracy": accuracy * 100,
            "average_response_time": avg_time,
            "total_time": total_time
        }
        
        print("\n" + "=" * 60)
        print("📊 EVALUATION SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']} ✅")
        print(f"Failed: {summary['failed']} ❌")
        print(f"Accuracy: {summary['accuracy']:.1f}%")
        print(f"Average Response Time: {summary['average_response_time']:.2f}s")
        print("=" * 60)
        
        return summary
        
    def save_results(self, filepath: str = "logs/evaluation_results.json"):
        """Save test results to file"""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump({
                "test_results": self.test_results,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }, f, indent=2)
        
        print(f"\n💾 Results saved to {filepath}")


def get_sample_test_cases() -> List[Dict]:
    """Define sample test cases for evaluation"""
    return [
        {
            "description": "Basic aggregation - total sales",
            "natural_query": "What is the total revenue from all sales?",
            "should_succeed": True
        },
        {
            "description": "Top N query with sorting",
            "natural_query": "Show me the top 5 products by revenue",
            "should_succeed": True
        },
        {
            "description": "Grouping by category",
            "natural_query": "What are the total sales by product category?",
            "should_succeed": True
        },
        {
            "description": "Join query across tables",
            "natural_query": "Show me customer names and their total order amounts",
            "should_succeed": True
        },
        {
            "description": "Date filtering",
            "natural_query": "How many orders were placed in the last 30 days?",
            "should_succeed": True
        },
        {
            "description": "Count query",
            "natural_query": "How many customers do we have in each region?",
            "should_succeed": True
        },
        {
            "description": "Average calculation",
            "natural_query": "What is the average order value?",
            "should_succeed": True
        },
        {
            "description": "Multiple conditions",
            "natural_query": "Show me all electronics products priced above $100",
            "should_succeed": True
        },
        {
            "description": "Regional analysis",
            "natural_query": "Which region has the highest total sales?",
            "should_succeed": True
        },
        {
            "description": "Complex join with aggregation",
            "natural_query": "What is the total revenue per customer region?",
            "should_succeed": True
        }
    ]


def run_evaluation():
    """Main evaluation function"""
    print("Initializing agent for evaluation...\n")
    
    try:
        agent = DataAnalystAgent()
        evaluator = AgentEvaluator(agent)
        
        # Get test cases
        test_cases = get_sample_test_cases()
        
        # Run evaluation
        summary = evaluator.run_test_suite(test_cases)
        
        # Save results
        evaluator.save_results()
        
        # Save metrics
        agent.save_state()
        
        agent.close()
        
        return summary
        
    except Exception as e:
        print(f"❌ Evaluation failed: {str(e)}")
        raise


if __name__ == "__main__":
    run_evaluation()
