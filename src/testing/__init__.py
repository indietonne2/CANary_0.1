"""
Testing tools for the canCANary CAN-Bus Simulator.

This package provides test runners, fixtures, and utilities for
unit, integration, and system testing.
"""

# Import key modules to make them available at package level
try:
    from .test_runner import TestRunner, TestScope, TestResult, TestSummary
except ImportError:
    # Handle situation where implementation files might not exist yet
    pass
