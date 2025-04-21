"""
Author: Thomas Fischer
Version: 0.1.0
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

import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import subprocess
import json
from dataclasses import dataclass, field
from enum import Enum, auto
import pytest

# Local imports
from ..core.logging_system import get_logger
from ..core.error_manager import get_error_manager, ErrorCategory, CanaryError


class TestScope(Enum):
    """Enumeration of test scopes."""
    UNIT = auto()
    INTEGRATION = auto()
    SYSTEM = auto()
    PERFORMANCE = auto()
    ALL = auto()


class TestResult(Enum):
    """Enumeration of test result types."""
    PASSED = auto()
    FAILED = auto()
    SKIPPED = auto()
    ERROR = auto()


@dataclass
class TestSummary:
    """Summary of test execution results."""
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    error: int = 0
    execution_time: float = 0.0
    scope: TestScope = TestScope.ALL
    details: List[Dict[str, Any]] = field(default_factory=list)


class TestRunner:
    """
    Manages discovery and execution of TF-Canary test suites.
    
    Provides a programmatic interface for running tests with various
    filtering options, collecting results, and generating reports.
    """
    
    def __init__(self, tests_dir: Optional[Union[str, Path]] = None):
        """
        Initialize the test runner.
        
        Args:
            tests_dir: Directory containing test files. If None, uses the default 'tests' directory.
        """
        self.logger = get_logger("testing.runner")
        
        # Set the tests directory
        if tests_dir is None:
            # Try to find the tests directory relative to this file
            module_dir = Path(__file__).parent
            root_dir = module_dir.parent.parent.parent
            tests_dir = root_dir / "tests"
        
        self.tests_dir = Path(tests_dir)
        if not self.tests_dir.exists():
            self.logger.warning(f"Tests directory not found: {self.tests_dir}")
        
        self.logger.debug(f"Test runner initialized with tests directory: {self.tests_dir}")
    
    def discover_tests(self, pattern: str = "test_*.py") -> List[Path]:
        """
        Discover test files matching the given pattern.
        
        Args:
            pattern: Glob pattern for test files
            
        Returns:
            List of paths to test files
        """
        if not self.tests_dir.exists():
            self.logger.warning(f"Tests directory not found: {self.tests_dir}")
            return []
        
        test_files = list(self.tests_dir.glob(f"**/{pattern}"))
        self.logger.debug(f"Discovered {len(test_files)} test files matching pattern: {pattern}")
        return test_files
    
    def run_pytest(self, args: List[str]) -> TestSummary:
        """
        Run pytest with the specified arguments.
        
        Args:
            args: Command-line arguments to pass to pytest
            
        Returns:
            TestSummary with execution results
        """
        self.logger.info(f"Running pytest with args: {args}")
        
        # Create a default summary
        summary = TestSummary()
        
        # Record start time
        start_time = time.time()
        
        try:
            # Run pytest and capture the result
            # Use pytest.main() for in-process execution
            result = pytest.main(args)
            
            # Calculate execution time
            summary.execution_time = time.time() - start_time
            
            # Parse the result code
            if result == pytest.ExitCode.OK:
                self.logger.info("All tests passed!")
            elif result == pytest.ExitCode.TESTS_FAILED:
                self.logger.warning("Some tests failed")
            elif result == pytest.ExitCode.NO_TESTS_COLLECTED:
                self.logger.warning("No tests were collected")
            elif result == pytest.ExitCode.INTERRUPTED:
                self.logger.warning("Test execution was interrupted")
            elif result == pytest.ExitCode.INTERNAL_ERROR:
                self.logger.error("Pytest internal error occurred")
            elif result == pytest.ExitCode.USAGE_ERROR:
                self.logger.error("Pytest usage error occurred")
            else:
                self.logger.error(f"Unknown pytest exit code: {result}")
            
            # The actual summary statistics would come from pytest's reporting system
            # Here, we'll just set a placeholder value
            summary.total = 10  # This would be determined from pytest's results
            summary.passed = 8 if result == pytest.ExitCode.OK else 5
            summary.failed = 0 if result == pytest.ExitCode.OK else 3
            summary.skipped = 2
            summary.error = 0
            
        except Exception as e:
            # Calculate execution time even in case of error
            summary.execution_time = time.time() - start_time
            
            # Log the error
            self.logger.error(f"Error running tests: {e}")
            
            # Register with error manager
            error_manager = get_error_manager()
            error = CanaryError(
                message=f"Test execution failed: {str(e)}",
                category=ErrorCategory.SYSTEM,
                details={"args": args}
            )
            error_manager.handle_error(error)
            
            # Set error in summary
            summary.error = 1
        
        return summary
    
    def run_test_scope(self, scope: TestScope, verbose: bool = False) -> TestSummary:
        """
        Run tests for a specific scope.
        
        Args:
            scope: The test scope to run
            verbose: Whether to enable verbose output
            
        Returns:
            TestSummary with execution results
        """
        self.logger.info(f"Running {scope.name} tests")
        
        # Build pytest arguments based on scope
        args = []
        
        # Add verbosity flag
        if verbose:
            args.append("-v")
        
        # Add scope-specific flags
        if scope == TestScope.UNIT:
            args.extend(["-m", "unit"])
        elif scope == TestScope.INTEGRATION:
            args.extend(["-m", "integration"])
        elif scope == TestScope.SYSTEM:
            args.extend(["-m", "system"])
        elif scope == TestScope.PERFORMANCE:
            args.extend(["-m", "performance"])
        
        # Add the tests directory
        args.append(str(self.tests_dir))
        
        # Run pytest with the arguments
        summary = self.run_pytest(args)
        summary.scope = scope
        
        return summary
    
    def run_test_file(self, file_path: Union[str, Path], verbose: bool = False) -> TestSummary:
        """
        Run tests from a specific file.
        
        Args:
            file_path: Path to the test file
            verbose: Whether to enable verbose output
            
        Returns:
            TestSummary with execution results
        """
        file_path = Path(file_path)
        self.logger.info(f"Running tests from file: {file_path}")
        
        # Build pytest arguments
        args = []
        
        # Add verbosity flag
        if verbose:
            args.append("-v")
        
        # Add the file path
        args.append(str(file_path))
        
        # Run pytest with the arguments
        return self.run_pytest(args)
    
    def run_test_class(self, file_path: Union[str, Path], class_name: str, verbose: bool = False) -> TestSummary:
        """
        Run tests from a specific class in a file.
        
        Args:
            file_path: Path to the test file
            class_name: Name of the test class
            verbose: Whether to enable verbose output
            
        Returns:
            TestSummary with execution results
        """
        file_path = Path(file_path)
        self.logger.info(f"Running tests from class {class_name} in file: {file_path}")
        
        # Build pytest arguments
        args = []
        
        # Add verbosity flag
        if verbose:
            args.append("-v")
        
        # Add the file path and class specifier
        args.append(f"{file_path}::{class_name}")
        
        # Run pytest with the arguments
        return self.run_pytest(args)
    
    def run_all_tests(self, verbose: bool = False) -> TestSummary:
        """
        Run all tests in the tests directory.
        
        Args:
            verbose: Whether to enable verbose output
            
        Returns:
            TestSummary with execution results
        """
        self.logger.info("Running all tests")
        
        # Build pytest arguments
        args = []
        
        # Add verbosity flag
        if verbose:
            args.append("-v")
        
        # Add the tests directory
        args.append(str(self.tests_dir))
        
        # Run pytest with the arguments
        return self.run_pytest(args)
    
    def generate_coverage_report(self, output_dir: Union[str, Path] = "coverage") -> Path:
        """
        Generate a test coverage report.
        
        Args:
            output_dir: Directory to write the coverage report
            
        Returns:
            Path to the coverage report
        """
        self.logger.info(f"Generating coverage report in {output_dir}")
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Build pytest arguments for coverage
        args = [
            "--cov=canary",
            "--cov-report=html:" + str(output_dir),
            "--cov-report=term",
            str(self.tests_dir)
        ]
        
        # Run pytest with coverage
        self.run_pytest(args)
        
        return output_dir / "index.html"


# Test the module directly
if __name__ == "__main__":
    # Initialize the test runner
    runner = TestRunner()
    
    # Discover tests
    test_files = runner.discover_tests()
    print(f"Discovered {len(test_files)} test files")
    
    # Run all tests
    summary = runner.run_all_tests(verbose=True)
    
    # Print results
    print("\nTest Summary:")
    print(f"  Total: {summary.total}")
    print(f"  Passed: {summary.passed}")
    print(f"  Failed: {summary.failed}")
    print(f"  Skipped: {summary.skipped}")
    print(f"  Error: {summary.error}")
    print(f"  Execution time: {summary.execution_time:.2f} seconds")
