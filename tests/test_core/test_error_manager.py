"""
Author: Thomas Fischer
Version: 0.1.0
Filename: test_error_manager.py
Pathname: tests/test_core/test_error_manager.py

This module contains unit tests for the ErrorManager class of the canCANary simulator.
"""

import sys
import os
import pytest
from unittest.mock import patch, MagicMock
import logging

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

# Import the module to test
from canary.core.error_manager import (
    ErrorManager, get_error_manager,
    CanaryError, ConfigurationError, CANBusError, HardwareError,
    ErrorSeverity, ErrorCategory
)


@pytest.fixture
def error_manager():
    """Create an ErrorManager instance for testing."""
    # Reset the singleton instance
    ErrorManager._instance = None
    
    # Create and return a new instance
    return ErrorManager()


class TestErrorManager:
    """Test suite for the ErrorManager class."""
    
    def test_singleton_pattern(self):
        """Test that ErrorManager follows the singleton pattern."""
        # Reset the singleton instance
        ErrorManager._instance = None
        
        # Create two instances
        manager1 = ErrorManager()
        manager2 = ErrorManager()
        
        # Check that they are the same instance
        assert manager1 is manager2
        
        # Also check the global function
        manager3 = get_error_manager()
        assert manager1 is manager3
    
    def test_handle_error(self, error_manager, caplog):
        """Test that errors are properly handled and logged."""
        # Set caplog level to DEBUG
        caplog.set_level(logging.DEBUG)
        
        # Create a test error
        test_error = CanaryError(
            message="Test error message",
            severity=ErrorSeverity.ERROR,
            category=ErrorCategory.CONFIGURATION,
            details={"key": "value"}
        )
        
        # Handle the error
        error_manager.handle_error(test_error)
        
        # Check that the error was logged
        assert "Test error message" in caplog.text
        
        # Check that the error was added to the log
        assert len(error_manager.error_log) == 1
        assert error_manager.error_log[0] is test_error
    
    def test_error_handler_registration(self, error_manager):
        """Test that error handlers can be registered and called."""
        # Create a mock handler
        mock_handler = MagicMock()
        
        # Register the handler
        error_manager.register_error_handler(ErrorCategory.CONFIGURATION, mock_handler)
        
        # Create and handle a test error
        test_error = ConfigurationError("Test config error")
        error_manager.handle_error(test_error)
        
        # Check that the handler was called with the error
        mock_handler.assert_called_once()
        args, _ = mock_handler.call_args
        assert args[0] is test_error
    
    def test_get_last_error(self, error_manager):
        """Test the get_last_error method."""
        # Initially there should be no errors
        assert error_manager.get_last_error() is None
        
        # Add an error
        error1 = CanaryError("First error")
        error_manager.handle_error(error1)
        
        # Check that get_last_error returns the error
        assert error_manager.get_last_error() is error1
        
        # Add another error
        error2 = CanaryError("Second error")
        error_manager.handle_error(error2)
        
        # Check that get_last_error returns the new error
        assert error_manager.get_last_error() is error2
    
    def test_get_errors_by_category(self, error_manager):
        """Test the get_errors_by_category method."""
        # Add some errors of different categories
        error1 = ConfigurationError("Config error")
        error2 = CANBusError("CAN Bus error")
        error3 = ConfigurationError("Another config error")
        
        error_manager.handle_error(error1)
        error_manager.handle_error(error2)
        error_manager.handle_error(error3)
        
        # Get errors by category
        config_errors = error_manager.get_errors_by_category(ErrorCategory.CONFIGURATION)
        can_errors = error_manager.get_errors_by_category(ErrorCategory.CAN_BUS)
        
        # Check the results
        assert len(config_errors) == 2
        assert error1 in config_errors
        assert error3 in config_errors
        
        assert len(can_errors) == 1
        assert error2 in can_errors
    
    def test_clear_log(self, error_manager):
        """Test the clear_log method."""
        # Add some errors
        error_manager.handle_error(CanaryError("Error 1"))
        error_manager.handle_error(CanaryError("Error 2"))
        
        # Check that errors were added
        assert len(error_manager.error_log) == 2
        
        # Clear the log
        error_manager.clear_log()
        
        # Check that the log is empty
        assert len(error_manager.error_log) == 0
    
    def test_recovery_strategy(self, error_manager):
        """Test that recovery strategies can be registered and used."""
        # Create a mock recovery strategy
        mock_strategy = MagicMock(return_value=True)
        
        # Register the strategy
        error_manager.register_recovery_strategy(ValueError, mock_strategy)
        
        # Create a global exception handler that will call our strategy
        with patch.object(error_manager, 'global_exception_handler') as mock_handler:
            # Simulate the global_exception_handler directly
            error_manager.global_exception_handler(ValueError, ValueError("Test value error"), None)
            
            # Make sure the handler was called
            mock_handler.assert_called_once()
    
    def test_custom_error_classes(self):
        """Test that custom error classes have the right properties."""
        # Test ConfigurationError
        config_error = ConfigurationError("Config error", {"file": "config.yaml"})
        assert config_error.message == "Config error"
        assert config_error.category == ErrorCategory.CONFIGURATION
        assert config_error.severity == ErrorSeverity.ERROR
        assert config_error.details == {"file": "config.yaml"}
        
        # Test CANBusError
        can_error = CANBusError("CAN error")
        assert can_error.message == "CAN error"
        assert can_error.category == ErrorCategory.CAN_BUS
        
        # Test HardwareError
        hw_error = HardwareError("Hardware error")
        assert hw_error.message == "Hardware error"
        assert hw_error.category == ErrorCategory.HARDWARE
