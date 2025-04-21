"""
Author: Thomas Fischer
Version: 0.1.0
Filename: logging_system.py
Pathname: src/core/logging_system.py

This module implements the central logging system for the canCANary CAN-Bus Simulator.
It provides a unified interface for all logging operations, supports multiple output formats,
and handles log rotation, formatting, and filtering.

Classes:
    LoggingSystem: Singleton class that manages all logging operations
        - Configures console and file handlers
        - Supports different log levels
        - Provides rotation and formatting
        - Thread-safe logging
"""

import os
import sys
import json
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Union, Any, List


class LoggingSystem:
    """
    Centralized logging system for canCANary CAN-Bus Simulator.
    
    This singleton class configures and manages all logging operations,
    providing multiple handlers (console, file) with different log levels.
    """
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(LoggingSystem, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the logging system with the provided configuration.
        
        Args:
            config: Configuration dictionary with the following optional keys:
                - level: Overall logging level (default: INFO)
                - file_level: Level for file logging (default: DEBUG)
                - console_level: Level for console logging (default: INFO)
                - format: Log format string
                - log_dir: Directory for log files
                - max_size: Maximum size per log file in bytes
                - backup_count: Number of backup files to keep
        """
        if self._initialized:
            return
            
        self.config = config or {}
        self.level = self._get_level(self.config.get('level', 'INFO'))
        self.file_level = self._get_level(self.config.get('file_level', 'DEBUG'))
        self.console_level = self._get_level(self.config.get('console_level', 'INFO'))
        
        self.format = self.config.get('format', 
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s')
        
        self.log_dir = Path(self.config.get('log_dir', 'logs'))
        self.max_size = self.config.get('max_size', 10 * 1024 * 1024)  # 10 MB
        self.backup_count = self.config.get('backup_count', 5)
        
        # Create the logger
        self.root_logger = logging.getLogger('canary')
        self.root_logger.setLevel(self.level)
        
        # Set up handlers
        self._setup_console_handler()
        self._setup_file_handler()
        
        # Mark as initialized
        self._initialized = True
        
        # Log startup
        self.root_logger.info(f"Logging system initialized (level={self.level})")
    
    def _get_level(self, level_name: str) -> int:
        """Convert a level name to a logging level."""
        return getattr(logging, level_name.upper(), logging.INFO)
    
    def _setup_console_handler(self) -> None:
        """Set up a console handler for the root logger."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.console_level)
        formatter = logging.Formatter(self.format)
        console_handler.setFormatter(formatter)
        self.root_logger.addHandler(console_handler)
    
    def _setup_file_handler(self) -> None:
        """Set up a rotating file handler for the root logger."""
        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create timestamp for log filename
        timestamp = datetime.now().strftime("%Y-%m-%d")
        log_file = self.log_dir / f"canary-{timestamp}.log"
        
        # Create the handler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=self.max_size,
            backupCount=self.backup_count
        )
        file_handler.setLevel(self.file_level)
        
        # Create formatter and add to handler
        formatter = logging.Formatter(self.format)
        file_handler.setFormatter(formatter)
        
        # Add handler to the logger
        self.root_logger.addHandler(file_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a named logger that inherits from the root logger.
        
        Args:
            name: The name of the logger, typically __name__
            
        Returns:
            A configured Logger instance
        """
        if not name.startswith('canary.'):
            name = f'canary.{name}'
        return logging.getLogger(name)
    
    def set_level(self, level: Union[str, int]) -> None:
        """
        Set the logging level for the root logger.
        
        Args:
            level: The level to set, either as a string or integer
        """
        if isinstance(level, str):
            level = self._get_level(level)
        self.root_logger.setLevel(level)
        self.root_logger.info(f"Logging level changed to {level}")
    
    def log_dict(self, level: str, message: str, data: Dict[str, Any], logger_name: str = 'canary') -> None:
        """
        Log a dictionary as a properly formatted JSON string.
        
        Args:
            level: The log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Message to log before the JSON data
            data: Dictionary to log as JSON
            logger_name: Name of the logger to use
        """
        logger = logging.getLogger(logger_name)
        log_method = getattr(logger, level.lower(), logger.info)
        
        try:
            json_str = json.dumps(data, default=str, sort_keys=True, indent=2)
            log_method(f"{message}\n{json_str}")
        except Exception as e:
            logger.error(f"Failed to log dictionary as JSON: {e}")
            logger.debug(f"Original data: {data}")


# Convenience function to get the global logger
def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger from the LoggingSystem.
    
    Args:
        name: Logger name (defaults to module name)
        
    Returns:
        Configured Logger instance
    """
    if name is None:
        # Get the caller's module name
        import inspect
        frame = inspect.currentframe().f_back
        name = frame.f_globals['__name__']
    
    # Ensure the LoggingSystem is initialized
    logging_system = LoggingSystem()
    return logging_system.get_logger(name)


# Test the module directly
if __name__ == "__main__":
    # Initialize with custom config
    config = {
        'level': 'DEBUG',
        'log_dir': 'test_logs'
    }
    logging_system = LoggingSystem(config)
    
    # Get a test logger
    logger = logging_system.get_logger('test')
    
    # Log at different levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Log a dictionary
    logging_system.log_dict('INFO', "Test configuration:", {
        'version': '0.1.0',
        'platform': 'test',
        'timestamp': datetime.now()
    })
    
    print("Logging test complete. Check test_logs directory.")
