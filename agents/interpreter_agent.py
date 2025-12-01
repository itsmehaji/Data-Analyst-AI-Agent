"""
Result Interpreter Agent
Analyzes query results and generates insights with visualizations
"""
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Optional, Tuple
from config import GOOGLE_API_KEY, MODEL_NAME
from utils.logger import log_agent_action, log_error


class ResultInterpreterAgent:
    """
    Agent responsible for:
    1. Analyzing query results
    2. Generating natural language insights
    3. Creating visualizations when appropriate
    """
    
    def __init__(self):
        genai.configure(api_key=GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(MODEL_NAME)
        log_agent_action("ResultInterpreterAgent", "initialized", {"model": MODEL_NAME})
        
    def interpret_results(self, natural_language_query: str, sql_query: str, 
                         results_df: pd.DataFrame) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Generate natural language interpretation of query results
        
        Args:
            natural_language_query: Original user query
            sql_query: SQL query that was executed
            results_df: Query results as DataFrame
            
        Returns:
            Tuple of (success, interpretation, error_message)
        """
        try:
            log_agent_action("ResultInterpreterAgent", "interpreting_results", {
                "rows": len(results_df) if results_df is not None else 0
            })
            
            if results_df is None or results_df.empty:
                return True, "No results found for your query.", None
                
            # Prepare data summary
            data_summary = self._prepare_data_summary(results_df)
            
            # Create interpretation prompt
            prompt = f"""You are a data analyst assistant. Analyze the query results and provide clear, concise insights.

User's Question: {natural_language_query}

SQL Query: {sql_query}

Results Summary:
{data_summary}

Sample Data (first 5 rows):
{results_df.head().to_string()}

Provide a clear, natural language interpretation that:
1. Answers the user's question directly
2. Highlights key findings from the data
3. Mentions any interesting patterns or outliers
4. Keeps the response concise (2-4 sentences)

Interpretation:"""

            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 512
                }
            )
            
            interpretation = response.text.strip()
            
            log_agent_action("ResultInterpreterAgent", "interpretation_generated", {
                "length": len(interpretation)
            })
            
            return True, interpretation, None
            
        except Exception as e:
            log_error("ResultInterpreterAgent", e, {
                "query": natural_language_query[:100]
            })
            return False, None, str(e)
            
    def create_visualization(self, results_df: pd.DataFrame, 
                           query_type: str = "auto") -> Optional[go.Figure]:
        """
        Create appropriate visualization for results
        
        Args:
            results_df: Query results
            query_type: Type of visualization (auto, bar, line, pie, scatter)
            
        Returns:
            Plotly figure or None
        """
        try:
            if results_df is None or results_df.empty or len(results_df) > 100:
                return None
                
            log_agent_action("ResultInterpreterAgent", "creating_visualization", {
                "rows": len(results_df),
                "columns": len(results_df.columns)
            })
            
            # Auto-detect visualization type
            if query_type == "auto":
                query_type = self._detect_viz_type(results_df)
                
            fig = None
            
            if query_type == "bar" and len(results_df.columns) >= 2:
                # Bar chart for categorical vs numerical
                x_col = results_df.columns[0]
                y_col = results_df.columns[1]
                fig = px.bar(results_df, x=x_col, y=y_col, 
                           title=f"{y_col} by {x_col}")
                
            elif query_type == "line" and len(results_df.columns) >= 2:
                # Line chart for time series or trends
                x_col = results_df.columns[0]
                y_col = results_df.columns[1]
                fig = px.line(results_df, x=x_col, y=y_col,
                            title=f"{y_col} over {x_col}")
                
            elif query_type == "pie" and len(results_df.columns) >= 2:
                # Pie chart for distributions
                fig = px.pie(results_df, names=results_df.columns[0], 
                           values=results_df.columns[1],
                           title="Distribution")
                
            elif query_type == "scatter" and len(results_df.columns) >= 2:
                # Scatter plot for correlations
                x_col = results_df.columns[0]
                y_col = results_df.columns[1]
                fig = px.scatter(results_df, x=x_col, y=y_col,
                               title=f"{y_col} vs {x_col}")
                
            if fig:
                fig.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20))
                log_agent_action("ResultInterpreterAgent", "visualization_created", {
                    "type": query_type
                })
                
            return fig
            
        except Exception as e:
            log_error("ResultInterpreterAgent", e, {"action": "create_visualization"})
            return None
            
    def _prepare_data_summary(self, df: pd.DataFrame) -> str:
        """Prepare a text summary of the dataframe"""
        summary_parts = [
            f"Total rows: {len(df)}",
            f"Columns: {', '.join(df.columns)}",
        ]
        
        # Add statistics for numerical columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            summary_parts.append("\nNumerical Summary:")
            for col in numeric_cols[:3]:  # Limit to first 3 numeric columns
                summary_parts.append(f"  {col}: min={df[col].min():.2f}, "
                                   f"max={df[col].max():.2f}, "
                                   f"avg={df[col].mean():.2f}")
                
        return "\n".join(summary_parts)
        
    def _detect_viz_type(self, df: pd.DataFrame) -> str:
        """Auto-detect appropriate visualization type"""
        if len(df.columns) < 2:
            return "none"
            
        # Check column types
        numeric_cols = df.select_dtypes(include=['number']).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        # Heuristics for chart type
        if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
            if len(df) <= 20:
                return "bar"
            else:
                return "line"
        elif len(numeric_cols) >= 2:
            return "scatter"
        else:
            return "bar"
