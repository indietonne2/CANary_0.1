"""
Author: Thomas Fischer
Version: 0.1.1
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

from __future__ import annotations

import logging
import sys
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Type

from .logging_system import get_logger


class ErrorSeverity(Enum):
    """Enumeration of error severities."""

    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()


class ErrorCategory(Enum):
    """Enumeration of error categories."""

    GENERAL = auto()
    CONFIGURATION = auto()
    CAN_BUS = auto()
    HARDWARE = auto()


class CanaryError(Exception):
    """Base exception class for all application errors."""

    def __init__(
        self,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        category: ErrorCategory = ErrorCategory.GENERAL,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.severity = severity
        self.category = category
        self.details = details or {}


class ConfigurationError(CanaryError):
    """Configuration-specific errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, ErrorSeverity.ERROR, ErrorCategory.CONFIGURATION, details)


class CANBusError(CanaryError):
    """CAN bus communication errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, ErrorSeverity.ERROR, ErrorCategory.CAN_BUS, details)


class HardwareError(CanaryError):
    """Hardware-related errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, ErrorSeverity.ERROR, ErrorCategory.HARDWARE, details)


class ErrorManager:
    """Singleton class for centralized error handling."""

    _instance: Optional["ErrorManager"] = None

    def __new__(cls, *args, **kwargs) -> "ErrorManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return

        self.logger = get_logger("error_manager")
        self.error_log: List[CanaryError] = []
        self.error_handlers: Dict[ErrorCategory, List[Callable[[CanaryError], None]]] = {}
        self.recovery_strategies: Dict[Type[BaseException], Callable[[BaseException], Any]] = {}

        # Install global exception hook to capture unhandled exceptions
        sys.excepthook = self.global_exception_handler

        self._initialized = True

    # ------------------------------------------------------------------
    # Error logging and retrieval
    # ------------------------------------------------------------------
    def handle_error(self, error: CanaryError) -> None:
        """Handle an error by logging and calling registered handlers."""
        self.logger.error(error.message)
        self.error_log.append(error)
        for handler in self.error_handlers.get(error.category, []):
            try:
                handler(error)
            except Exception as exc:  # pragma: no cover - handler failures are logged
                self.logger.error(f"Error handler failed: {exc}")

    def register_error_handler(self, category: ErrorCategory, handler: Callable[[CanaryError], None]) -> None:
        """Register a handler for a specific error category."""
        self.error_handlers.setdefault(category, []).append(handler)

    def get_last_error(self) -> Optional[CanaryError]:
        """Return the most recently handled error."""
        return self.error_log[-1] if self.error_log else None

    def get_errors_by_category(self, category: ErrorCategory) -> List[CanaryError]:
        """Return a list of errors for the given category."""
        return [e for e in self.error_log if e.category == category]

    def clear_log(self) -> None:
        """Clear the stored error log."""
        self.error_log.clear()

    # ------------------------------------------------------------------
    # Recovery strategies and exception handling
    # ------------------------------------------------------------------
    def register_recovery_strategy(
        self, exc_type: Type[BaseException], strategy: Callable[[BaseException], Any]
    ) -> None:
        """Register a recovery strategy for a specific exception type."""
        self.recovery_strategies[exc_type] = strategy

    def global_exception_handler(
        self, exc_type: Type[BaseException], exc: BaseException, tb: Optional[Any]
    ) -> None:
        """Global exception hook that applies recovery strategies."""
        strategy = None
        for etype, strat in self.recovery_strategies.items():
            if issubclass(exc_type, etype):
                strategy = strat
                break

        if strategy is not None:
            try:
                strategy(exc)
            except Exception as e:  # pragma: no cover - edge case
                self.logger.error(f"Recovery strategy failed: {e}")
        else:
            self.logger.error("Unhandled exception", exc_info=(exc_type, exc, tb))


# Convenience function to get the singleton

def get_error_manager() -> ErrorManager:
    """Return the global ErrorManager instance."""
    return ErrorManager()
