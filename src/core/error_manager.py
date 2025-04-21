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
