"""
Core modules for the canCANary CAN-Bus Simulator.

This package contains the fundamental components like error handling,
logging, configuration management, and platform detection.
"""

# Import key modules to make them available at package level
try:
    from .logging_system import LoggingSystem, get_logger
    from .error_manager import ErrorManager, get_error_manager, CanaryError
    from .platform_detector import PlatformDetector, get_platform_detector
except ImportError:
    # Handle situation where implementation files might not exist yet
    pass
