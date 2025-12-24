"""
Structured logging configuration for the Book Management System.
Provides consistent logging across all modules with proper formatting and levels.
"""
import logging
import sys
from typing import Any
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging in production.
    Outputs logs in JSON format for easy parsing by log aggregation tools.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
            
        return json.dumps(log_data)


def setup_logging(log_level: str = "INFO", use_json: bool = False) -> None:
    """
    Configure application-wide logging.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_json: If True, use JSON formatter for structured logs (recommended for production)
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    
    # Set formatter
    if use_json:
        formatter = JSONFormatter()
    else:
        # Human-readable format for development
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.addHandler(handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Name of the logger (typically __name__)
    
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
