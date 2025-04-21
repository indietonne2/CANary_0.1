"""
Author: Thomas Fischer
Version: 0.1.0
Filename: error_manager.py
Pathname: src/core/error_manager.py

This module implements the error management system for the canCANary CAN-Bus Simulator.
It handles application-wide error capture, reporting, and recovery strategies.

Classes:
    ErrorSeverity: Enum defining error severity levels (DEBUG to FATAL)
    ErrorCategory: Enum categorizing errors (CONFIGURATION, CAN_BUS, etc.)
    CanaryError: Base exception class for all application errors
    ConfigurationError: Configuration-specific errors
    CANBusError: CAN bus communication errors
    HardwareError: Hardware-related errors
    ErrorManager: Singleton class for centralized error handling
        - Error tracking and reporting
        - Recovery strategies
        - Category-based error handling
"""

import sys
import traceback
from enum import Enum, auto
from typing import Dict, Any, List, Optional, Callable, Type
import logging
from datetime import datetime

# Local imports
from .logging_system import get_logger


class ErrorSeverity(Enum):
    """Enumeration of error severity levels."""
    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()
    FATAL = auto()


class ErrorCategory(Enum):
    """Categorization of error types for better handling."""
    CONFIGURATION = auto()
    DATABASE = auto()
    NETWORK = auto()
    CAN_BUS = auto()
    HARDWARE = auto()
    USER_INPUT = auto()
    SYSTEM = auto()
    PLUGIN = auto()
    UNKNOWN = auto()


class CanaryError(Exception):
    """Base exception class for all canCANary application errors."""
    
    def __init__(
        self, 
        message: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.severity = severity
        self.category = category
        self.details = details or {}
        self.timestamp = datetime.now()
        
        # Initialize the base class
        super().__init__(message)


class ConfigurationError(CanaryError):
    """Error raised for configuration-related issues."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message,
            severity=ErrorSeverity.ERROR,
            category=ErrorCategory.CONFIGURATION,
            details=details
        )


class CANBusError(CanaryError):
    """Error raised for CAN bus communication issues."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message,
            severity=ErrorSeverity.ERROR,
            category=ErrorCategory.CAN_BUS,
            details=details
        )


class HardwareError(CanaryError):
    """Error raised for hardware-related issues."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message,
            severity=ErrorSeverity.ERROR,
            category=ErrorCategory.HARDWARE,
            details=details
        )


class ErrorManager:
    """
    Central error handling system for the canCANary application.
    
    Provides:
    - Centralized error tracking and reporting
    - Custom exception hierarchy
    - Error categorization and severity levels
    - Error event subscription for UI updates
    - Recovery strategies for known error patterns
    """
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ErrorManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the error manager."""
        if self._initialized:
            return
            
        self.logger = get_logger("error_manager")
        self.error_log: List[CanaryError] = []
        self.error_handlers: Dict[ErrorCategory, List[Callable]] = {
            category: [] for category in ErrorCategory
        }
        self.recovery_strategies: Dict[Type[Exception], Callable] = {}
        
        # Set up as global exception handler
        sys.excepthook = self.global_exception_handler
        
        self._initialized = True
        self.logger.info("Error Manager initialized")
    
    def register_error_handler(self, category: ErrorCategory, handler: Callable) -> None:
        """
        Register a handler function for a specific error category.
        
        Args:
            category: The category of errors to handle
            handler: Callback function(error: CanaryError) -> None
        """
        self.error_handlers[category].append(handler)
        self.logger.debug(f"Registered error handler for {category.name}")
    
    def register_recovery_strategy(self, exception_type: Type[Exception], strategy: Callable) -> None:
        """
        Register a recovery strategy for a specific exception type.
        
        Args:
            exception_type: The exception class to handle
            strategy: Function(exception) that attempts recovery and returns success bool
        """
        self.recovery_strategies[exception_type] = strategy
        self.logger.debug(f"Registered recovery strategy for {exception_type.__name__}")
    
    def handle_error(self, error: CanaryError) -> bool:
        """
        Process an error through the error management system.
        
        Args:
            error: The CanaryError to handle
            
        Returns:
            True if error was handled, False if no handler was found
        """
        # Log the error
        log_method = self._get_log_method(error.severity)
        log_method(f"{error.category.name} ERROR: {error.message}")
        
        if error.details:
            self.logger.debug(f"Error details: {error.details}")
        
        # Add to error log
        self.error_log.append(error)
        
        # Notify handlers
        handlers = self.error_handlers[error.category]
        if handlers:
            for handler in handlers:
                try:
                    handler(error)
                except Exception as e:
                    self.logger.error(f"Error in error handler: {e}")
            return True
        return False
    
    def _get_log_method(self, severity: ErrorSeverity):
        """Map ErrorSeverity to the appropriate logging method."""
        severity_map = {
            ErrorSeverity.DEBUG: self.logger.debug,
            ErrorSeverity.INFO: self.logger.info,
            ErrorSeverity.WARNING: self.logger.warning,
            ErrorSeverity.ERROR: self.logger.error,
            ErrorSeverity.CRITICAL: self.logger.critical,
            ErrorSeverity.FATAL: self.logger.critical
        }
        return severity_map.get(severity, self.logger.error)
    
    def global_exception_handler(self, exc_type, exc_value, exc_traceback):
        """Global exception handler for uncaught exceptions."""
        if issubclass(exc_type, KeyboardInterrupt):
            # Call the original excepthook for KeyboardInterrupt
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        # Get traceback as a string
        tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        
        # Log the exception
        self.logger.error(f"Uncaught {exc_type.__name__}: {exc_value}")
        self.logger.debug(f"Traceback:\n{tb_str}")
        
        # Check if we have a recovery strategy
        for exception_class, strategy in self.recovery_strategies.items():
            if issubclass(exc_type, exception_class):
                try:
                    if strategy(exc_value):
                        self.logger.info(f"Recovery strategy for {exc_type.__name__} succeeded")
                        return
                    else:
                        self.logger.warning(f"Recovery strategy for {exc_type.__name__} failed")
                except Exception as e:
                    self.logger.error(f"Error in recovery strategy: {e}")
        
        # If we're here, recovery failed or no strategy exists
        if issubclass(exc_type, CanaryError):
            # This is one of our custom errors, handle it directly
            self.handle_error(exc_value)
        else:
            # This is a standard exception, convert to our format
            canary_error = CanaryError(
                message=str(exc_value),
                severity=ErrorSeverity.ERROR,
                category=ErrorCategory.SYSTEM,
                details={"traceback": tb_str, "type": exc_type.__name__}
            )
            self.handle_error(canary_error)
    
    def get_last_error(self) -> Optional[CanaryError]:
        """Get the most recent error if any."""
        if self.error_log:
            return self.error_log[-1]
        return None
    
    def get_errors_by_category(self, category: ErrorCategory) -> List[CanaryError]:
        """Get all errors of a specific category."""
        return [e for e in self.error_log if e.category == category]
    
    def clear_log(self) -> None:
        """Clear the error log."""
        self.error_log.clear()
        self.logger.debug("Error log cleared")


# Get the global error manager instance
def get_error_manager() -> ErrorManager:
    """
    Get the global ErrorManager instance.
    
    Returns:
        The singleton ErrorManager instance
    """
    return ErrorManager()


# Test the module directly
if __name__ == "__main__":
    # Initialize error manager
    error_manager = get_error_manager()
    
    # Define a test handler
    def test_handler(error: CanaryError):
        print(f"Test handler received: {error.message}")
    
    # Register the handler
    error_manager.register_error_handler(ErrorCategory.CONFIGURATION, test_handler)
    
    # Generate a test error
    try:
        raise ConfigurationError("Test configuration error", {"config_file": "test.conf"})
    except CanaryError as e:
        error_manager.handle_error(e)
    
    # Generate an uncaught error to test global handler
    try:
        # This will be caught by the global handler
        1 / 0
    except:
        # Let the global handler catch it
        pass
    
    print("Error manager test complete.")
