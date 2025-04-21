"""
Author: Thomas Fischer
Version: 0.1.1
Filename: test_runner.py
Pathname: src/testing/test_runner.py

This module implements the test runner for the canCANary CAN-Bus Simulator.
It provides functionality to discover, configure, and run pytest-based tests,
with support for filtering, reporting, and integration with the logging system.

Classes:
    TestScope: Enum defining test scopes (UNIT, INTEGRATION, SYSTEM, etc.)
    TestResult: Enum defining test outcomes (PASSED, FAILED, SKIPPED, ERROR)
    TestSummary: Data class for test execution results and statistics
    TestRunner: Main test execution framework
        - Test discovery and filtering
        - Test execution with pytest
        - Result collection and reporting
        - Coverage report generation
"""
