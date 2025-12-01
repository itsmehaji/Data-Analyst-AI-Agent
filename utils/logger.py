"""
Logging and observability utilities
"""
import logging
import structlog
from datetime import datetime
import json
from pathlib import Path
from config import LOG_LEVEL, LOG_FILE

# Create logs directory if it doesn't exist
Path("logs").mkdir(exist_ok=True)

# Configure standard logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# Configure structlog for structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()


class AgentMetrics:
    """Track agent performance metrics"""
    
    def __init__(self):
        self.metrics = {
            "queries_processed": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "validation_errors": 0,
            "execution_errors": 0,
            "average_response_time": 0.0,
            "total_response_time": 0.0
        }
        
    def record_query(self, success: bool, response_time: float, error_type: str = None):
        """Record a query execution"""
        self.metrics["queries_processed"] += 1
        self.metrics["total_response_time"] += response_time
        self.metrics["average_response_time"] = (
            self.metrics["total_response_time"] / self.metrics["queries_processed"]
        )
        
        if success:
            self.metrics["successful_queries"] += 1
        else:
            self.metrics["failed_queries"] += 1
            if error_type == "validation":
                self.metrics["validation_errors"] += 1
            elif error_type == "execution":
                self.metrics["execution_errors"] += 1
                
        logger.info(
            "query_recorded",
            success=success,
            response_time=response_time,
            error_type=error_type,
            total_queries=self.metrics["queries_processed"]
        )
        
    def get_metrics(self) -> dict:
        """Get current metrics"""
        return self.metrics.copy()
    
    def save_metrics(self, filepath: str = "logs/metrics.json"):
        """Save metrics to file"""
        with open(filepath, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        logger.info("metrics_saved", filepath=filepath)


# Global metrics instance
metrics = AgentMetrics()


def log_agent_action(agent_name: str, action: str, details: dict = None):
    """Log an agent action with structured data"""
    logger.info(
        "agent_action",
        agent=agent_name,
        action=action,
        details=details or {},
        timestamp=datetime.utcnow().isoformat()
    )


def log_error(agent_name: str, error: Exception, context: dict = None):
    """Log an error with context"""
    logger.error(
        "agent_error",
        agent=agent_name,
        error_type=type(error).__name__,
        error_message=str(error),
        context=context or {},
        timestamp=datetime.utcnow().isoformat()
    )
