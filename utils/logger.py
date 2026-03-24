"""
Logging module for structured logging with timestamps.
"""

from typing import Optional, Dict, Any
from enum import Enum
from datetime import datetime
import json


class LogLevel(Enum):
    """Log level enumeration."""
    DEBUG = "debug"
    INFO = "info"
    ERROR = "error"
    SUCCESS = "success"


class Logger:
    """Logger class for structured logging with timestamps."""
    
    def _format_message(self, level: LogLevel, message: str, 
                       context: Optional[Dict[str, Any]] = None,
                       error: Optional[Exception] = None) -> str:
        """
        Format log message with timestamp and optional context.
        
        Args:
            level: Log level
            message: Log message
            context: Optional context dictionary for structured logging
            error: Optional exception object
            
        Returns:
            Formatted log message string
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        level_str = level.value.upper()
        
        # Build base message
        formatted = f"[{timestamp}] [{level_str}] {message}"
        
        # Add context if provided
        if context:
            context_str = json.dumps(context, indent=2)
            formatted += f"\n  Context: {context_str}"
        
        # Add error details if provided
        if error:
            formatted += f"\n  Error: {type(error).__name__}: {str(error)}"
        
        return formatted
    
    def info(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log info message with timestamp and optional context.
        
        Args:
            message: Info message to log
            context: Optional context dictionary for structured logging
        """
        formatted = self._format_message(LogLevel.INFO, message, context)
        print(formatted)
    
    def error(self, message: str, error: Optional[Exception] = None, 
              context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log error message with timestamp, optional exception, and context.
        
        Args:
            message: Error message to log
            error: Optional exception object
            context: Optional context dictionary for structured logging
        """
        formatted = self._format_message(LogLevel.ERROR, message, context, error)
        print(formatted)
    
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log debug message with timestamp and optional context.
        
        Args:
            message: Debug message to log
            context: Optional context dictionary for structured logging
        """
        formatted = self._format_message(LogLevel.DEBUG, message, context)
        print(formatted)
    
    def success(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log success message with timestamp and optional context.
        
        Args:
            message: Success message to log
            context: Optional context dictionary for structured logging
        """
        formatted = self._format_message(LogLevel.SUCCESS, message, context)
        print(formatted)
