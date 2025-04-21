"""
Author: TF-Canary Team
Version: 0.1.0
Filename: test_logging_system.py
Pathname: tests/test_core/test_logging_system.py

This module contains unit tests for the LoggingSystem class.
"""

import sys
import os
import logging
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

# Import the module to test
from canary.core.logging_system import LoggingSystem, get_logger


@pytest.fixture
def temp_log_dir():
    """Create a temporary directory for log files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def logging_system(temp_log_dir):
    """Create a LoggingSystem instance with a temporary log directory."""
    # Reset the singleton instance
    LoggingSystem._instance = None
    
    # Create a config with the temp directory
    config = {
        'level': 'DEBUG',
        'log_dir': str(temp_log_dir)
    }
    
    # Initialize and return the logging system
    return LoggingSystem(config)


class TestLoggingSystem:
    """Test suite for the LoggingSystem class."""
    
    def test_singleton_pattern(self):
        """Test that LoggingSystem follows the singleton pattern."""
        # Reset the singleton instance
        LoggingSystem._instance = None
        
        # Create two instances
        logger1 = LoggingSystem()
        logger2 = LoggingSystem()
        
        # Check that they are the same instance
        assert logger1 is logger2
    
    def test_get_logger(self, logging_system):
        """Test that get_logger returns a properly configured logger."""
        logger = logging_system.get_logger("test_module")
        
        # Check logger name
        assert logger.name == "canary.test_module"
        
        # Check that the logger is properly configured
        assert logger.level <= logging.DEBUG
        
        # Check that the logger has handlers
        assert len(logger.handlers) > 0 or len(logging.getLogger("canary").handlers) > 0
    
    def test_log_levels(self, logging_system, caplog):
        """Test that log messages are filtered by level."""
        # Set caplog level to DEBUG to capture all messages
        caplog.set_level(logging.DEBUG)
        
        # Get a test logger
        logger = logging_system.get_logger("test_levels")
        
        # Log at different levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        
        # Check that all messages were captured
        assert "Debug message" in caplog.text
        assert "Info message" in caplog.text
        assert "Warning message" in caplog.text
        assert "Error message" in caplog.text
        
        # Clear the log
        caplog.clear()
        
        # Set the level to WARNING
        logging_system.set_level(logging.WARNING)
        
        # Log at different levels again
        logger.debug("Debug message 2")
        logger.info("Info message 2")
        logger.warning("Warning message 2")
        logger.error("Error message 2")
        
        # Check that only WARNING and above messages were captured
        assert "Debug message 2" not in caplog.text
        assert "Info message 2" not in caplog.text
        assert "Warning message 2" in caplog.text
        assert "Error message 2" in caplog.text
    
    def test_log_file_creation(self, logging_system, temp_log_dir):
        """Test that log files are created in the specified directory."""
        # Get a test logger
        logger = logging_system.get_logger("test_files")
        
        # Log a message
        logger.info("Test log file message")
        
        # Check that a log file was created
        log_files = list(temp_log_dir.glob("*.log"))
        assert len(log_files) > 0
        
        # Check that the message was written to the file
        with open(log_files[0], 'r') as f:
            log_content = f.read()
            assert "Test log file message" in log_content
    
    def test_log_dict(self, logging_system, caplog):
        """Test the log_dict method for structured logging."""
        # Set caplog level to DEBUG
        caplog.set_level(logging.DEBUG)
        
        # Log a dictionary
        test_data = {
            'key1': 'value1',
            'key2': 123,
            'key3': ['list', 'of', 'values']
        }
        
        logging_system.log_dict('INFO', "Test dictionary:", test_data)
        
        # Check that the message and all keys were captured
        assert "Test dictionary:" in caplog.text
        assert "key1" in caplog.text
        assert "value1" in caplog.text
        assert "key2" in caplog.text
        assert "123" in caplog.text
        assert "key3" in caplog.text
        assert "list" in caplog.text
    
    def test_global_get_logger(self):
        """Test the global get_logger function."""
        # Reset the singleton
        LoggingSystem._instance = None
        
        # Use the global function
        logger = get_logger("test_global")
        
        # Check logger name
        assert logger.name == "canary.test_global"
        
        # Check that LoggingSystem was initialized
        assert LoggingSystem._instance is not None
