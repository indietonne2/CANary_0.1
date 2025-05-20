"""
Author: Thomas Fischer
Version: 0.1.3
Filename: test_runner.py
Pathname: src/testing/test_runner.py

This module implements the test runner for the canCANary CAN-Bus Simulator.
It provides functionality to discover, configure, and run pytest-based tests,
with support for filtering, reporting, and integration with the logging system.

Classes:
    TestScope: Enum defining test scopes (UNIT, INTEGRATION, SYSTEM, etc.)
    TestResultStatus: Enum defining test outcomes (PASSED, FAILED, SKIPPED, ERROR)
    TestSummary: Data class for test execution results and statistics
    TestRunner: Main test execution framework
        - Test discovery and filtering
        - Test execution with pytest
        - Result collection and reporting
        - Coverage report generation
"""

import enum
import dataclasses
import subprocess
import sys
import logging
import os
import tempfile
import pytest  # For type hinting and potentially direct calls
from pathlib import Path

# Configure basic logging for the module
logger = logging.getLogger(__name__)


class TestScope(enum.Enum):
    """Defines the scope of tests."""
    UNIT = "unit"
    INTEGRATION = "integration"
    SYSTEM = "system"
    ACCEPTANCE = "acceptance"
    SMOKE = "smoke"
    ALL = "all"


class TestResultStatus(enum.Enum):
    """Defines the possible outcomes of a test execution."""
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    ERROR = "ERROR"  # Indicates an error during test setup or execution, not a test failure itself


@dataclasses.dataclass
class TestSummary:
    """Holds the summary of a test execution."""
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: int = 0
    duration: float = 0.0  # in seconds
    # Optional: detailed results per test case
    # results: list[dict] = dataclasses.field(default_factory=list)


class TestRunner:
    """
    Manages the discovery, configuration, and execution of pytest-based tests.
    """
    def __init__(self, test_directory: str = "tests", log_level: int = logging.INFO):
        """
        Initializes the TestRunner.

        Args:
            test_directory (str): The root directory where tests are located.
            log_level (int): The logging level for the TestRunner's logger.
        """
        # Convert to absolute path at initialization
        self.test_directory = os.path.abspath(test_directory)
        self.logger = logging.getLogger(f"{__name__}.TestRunner")
        self.logger.setLevel(log_level)
        self.logger.info(f"TestRunner initialized. Target test directory: {self.test_directory}")

        # Ensure the logger has a handler if not configured globally
        if not self.logger.hasHandlers():
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def discover_tests(self, scope: TestScope = TestScope.ALL, marker: str | None = None) -> list[str]:
        """
        Discovers tests based on scope and markers.
        This is a simplified discovery; pytest handles actual collection.
        This method can be used to list potential test files or directories.

        Args:
            scope (TestScope): The scope of tests to discover.
            marker (str | None): A specific pytest marker to filter tests.

        Returns:
            list[str]: A list of test files or directories matching the criteria.
                       (Currently returns the base test directory or a sub-directory based on scope)
        """
        self.logger.info(f"Discovering tests in '{self.test_directory}' for scope '{scope.value}' with marker '{marker}'.")

        # Basic discovery: just point to the test directory or a sub-directory.
        # Pytest will handle the actual collection.

        target_dir = self.test_directory
        if scope != TestScope.ALL and scope != TestScope.SMOKE:  # Smoke might run across all, or specific minimal set
             # Assuming scopes like UNIT, INTEGRATION map to subdirectories
            scope_dir = os.path.join(self.test_directory, scope.value)
            if os.path.isdir(scope_dir):
                target_dir = scope_dir
            else:
                self.logger.warning(f"Scope directory '{scope_dir}' not found. Using base test directory.")

        return [target_dir]

    def run_tests(
        self,
        test_paths: list[str] | None = None,
        marker: str | None = None,
        keyword: str | None = None,
        generate_report: bool = False,
        report_path: str = "test_report.html"
    ) -> TestSummary:
        """
        Runs tests using pytest.

        Args:
            test_paths (list[str] | None): Specific test files or directories to run.
                                           If None, uses self.test_directory.
            marker (str | None): Pytest marker to filter tests (e.g., "slow", "unit").
            keyword (str | None): Pytest keyword expression to filter tests (e.g., "TestClass and not test_method").
            generate_report (bool): Whether to generate an HTML report.
            report_path (str): Path to save the HTML report.

        Returns:
            TestSummary: A summary of the test results.
        """
        if test_paths is None:
            test_paths = [self.test_directory]

        self.logger.info(f"Starting test execution for paths: {test_paths}")
        pytest_args = list(test_paths)  # Start with paths to test

        if marker:
            pytest_args.extend(["-m", marker])
            self.logger.info(f"Filtering by marker: {marker}")

        if keyword:
            pytest_args.extend(["-k", keyword])
            self.logger.info(f"Filtering by keyword: {keyword}")

        # Add arguments for collecting results
        # We'll use a JSON report format for better analysis
        report_json_path = report_path.replace('.html', '.json')
        pytest_args.extend(['--json-report', f'--json-report-file={report_json_path}'])

        # Add HTML report if requested
        if generate_report:
            pytest_args.extend([f"--html={report_path}", "--self-contained-html"])
            self.logger.info(f"Generating HTML report at: {report_path}")

        pytest_command = [sys.executable, "-m", "pytest"] + pytest_args
        self.logger.debug(f"Executing pytest command: {' '.join(pytest_command)}")

        try:
            process = subprocess.run(pytest_command, capture_output=True, text=True, check=False)

            summary = TestSummary()

            # Basic parsing from exit code
            if process.returncode == 0:
                self.logger.info("Pytest execution successful (all tests passed or skipped appropriately).")
                # Try to parse output for more details
                if "collected " in process.stdout:
                    try:
                        # Look for patterns like "collected 5 items"
                        import re
                        collected_match = re.search(r"collected (\d+) items?", process.stdout)
                        passed_match = re.search(r"(\d+) passed", process.stdout)
                        skipped_match = re.search(r"(\d+) skipped", process.stdout)

                        if collected_match:
                            summary.total_tests = int(collected_match.group(1))
                        if passed_match:
                            summary.passed = int(passed_match.group(1))
                        if skipped_match:
                            summary.skipped = int(skipped_match.group(1))
                    except Exception as e:
                        self.logger.warning(f"Failed to parse pytest output: {e}")
                else:
                    summary.passed = -1  # Flag that we don't have exact counts from this simple run
            elif process.returncode == 1:
                summary.failed = -1  # Flag that we don't have exact counts
                self.logger.warning("Pytest execution completed with test failures.")
                # Try to parse failures
                try:
                    failed_match = re.search(r"(\d+) failed", process.stdout)
                    if failed_match:
                        summary.failed = int(failed_match.group(1))
                except Exception:
                    pass
            else:
                summary.errors = -1  # Flag that we don't have exact counts
                self.logger.error(f"Pytest execution failed with exit code {process.returncode}.")

            # Attempt to read JSON report if it exists for more detailed analysis
            if os.path.exists(report_json_path):
                try:
                    import json
                    with open(report_json_path, 'r') as f:
                        report_data = json.load(f)

                    if 'summary' in report_data:
                        rpt_summary = report_data['summary']
                        summary.total_tests = rpt_summary.get('total', summary.total_tests)
                        summary.passed = rpt_summary.get('passed', summary.passed)
                        summary.failed = rpt_summary.get('failed', summary.failed)
                        summary.skipped = rpt_summary.get('skipped', summary.skipped)
                        summary.errors = rpt_summary.get('error', summary.errors)
                        summary.duration = rpt_summary.get('duration', summary.duration)

                except Exception as e:
                    self.logger.warning(f"Failed to parse JSON report: {e}")

            self.logger.info("Pytest stdout:\n" + process.stdout)
            if process.stderr:
                self.logger.warning("Pytest stderr:\n" + process.stderr)

            return summary

        except FileNotFoundError:
            self.logger.error("pytest command not found. Make sure pytest is installed and in PATH.")
            return TestSummary(errors=1)  # Indicate an error in running tests
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during test execution: {e}", exc_info=True)
            return TestSummary(errors=1)

    def run_self_test(self, invoked_by_canary_startup: bool = False) -> bool:
        """
        Runs a simple self-test to ensure the TestRunner and pytest are functioning.

        Args:
            invoked_by_canary_startup (bool): If True, logs results more verbosely
                                             or to a specific canary log.

        Returns:
            bool: True if the self-test passed, False otherwise.
        """
        self.logger.info("Starting self-test...")

        # Create a temporary test file for the self-test
        # This ensures the self-test is isolated and doesn't depend on existing project tests.
        self_test_content = """
import pytest

def test_example_success():
    assert True

# def test_example_failure(): # Uncomment to test failure reporting
#    assert False
"""
        passed = False
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", prefix="selftest_", delete=False) as tmp_test_file:
                tmp_test_file.write(self_test_content)
                test_file_path = tmp_test_file.name

            self.logger.info(f"Self-test file created at: {test_file_path}")

            # Run pytest on this temporary file
            pytest_command = [sys.executable, "-m", "pytest", test_file_path, "-v"]
            process = subprocess.run(pytest_command, capture_output=True, text=True, check=False)

            if process.returncode == 0:
                self.logger.info("Self-test PASSED.")
                if "1 passed" in process.stdout:  # A simple check
                    passed = True
                else:  # Should not happen if exit code is 0 and test is simple pass
                    self.logger.warning("Self-test passed (exit code 0) but output confirmation not found.")
                    self.logger.debug(f"Self-test stdout: {process.stdout}")
                    passed = True  # Assume pass on exit code 0
            else:
                self.logger.error(f"Self-test FAILED. Exit code: {process.returncode}")
                self.logger.error(f"Self-test stdout:\n{process.stdout}")
                if process.stderr:
                    self.logger.error(f"Self-test stderr:\n{process.stderr}")

        except Exception as e:
            self.logger.error(f"Error during self-test execution: {e}", exc_info=True)
        finally:
            if 'test_file_path' in locals() and os.path.exists(test_file_path):
                os.remove(test_file_path)
                self.logger.info(f"Self-test file {test_file_path} removed.")

        if invoked_by_canary_startup:
            # Special logging for canary_startup
            canary_logger = logging.getLogger("canary_startup_self_test")
            # Ensure it has a handler if not configured by canary_startup.py
            if not canary_logger.hasHandlers():
                handler = logging.StreamHandler(sys.stdout)
                formatter = logging.Formatter('CANARY_SELF_TEST - %(asctime)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                canary_logger.addHandler(handler)
                canary_logger.propagate = False  # Avoid duplicate logging if root logger is also stdout

            if passed:
                canary_logger.info(f"TestRunner self-test result: PASSED.")
            else:
                canary_logger.error(f"TestRunner self-test result: FAILED.")

        return passed


# Example usage / main entry point for self-testing or direct execution
if __name__ == "__main__":
    # Basic configuration for standalone execution
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logger.info("Executing test_runner.py directly.")

    # Parse command line arguments for standalone execution
    import argparse
    parser = argparse.ArgumentParser(description="CANary Test Runner")
    parser.add_argument("--test-dir", default="tests", help="Directory containing test files")
    parser.add_argument("--scope", choices=[scope.value for scope in TestScope],
                        default=TestScope.ALL.value, help="Scope of tests to run")
    parser.add_argument("--marker", help="Pytest marker to filter tests")
    parser.add_argument("--keyword", help="Pytest keyword expression to filter tests")
    parser.add_argument("--report", action="store_true", help="Generate HTML test report")
    parser.add_argument("--report-path", default="test_report.html", help="Path for HTML test report")
    parser.add_argument("--self-test", action="store_true", help="Run self-test only")
    parser.add_argument("--canary-self-test", action="store_true",
                        help="Run self-test in canary startup mode")

    args = parser.parse_args()

    # Create the test runner
    runner = TestRunner(test_directory=args.test_dir)

    # Check if we should run the self-test
    if args.self_test or args.canary_self_test:
        self_test_passed = runner.run_self_test(invoked_by_canary_startup=args.canary_self_test)

        if self_test_passed:
            logger.info("TestRunner self-test completed successfully.")
            if not args.canary_self_test:  # Don't exit if invoked by canary
                sys.exit(0)
        else:
            logger.error("TestRunner self-test failed. Please check logs.")
            if not args.canary_self_test:  # Don't exit if invoked by canary
                sys.exit(1)

    # If we're not just doing a self-test and we're not invoked by canary,
    # run the tests as specified by the command line arguments
    if not args.self_test and not args.canary_self_test:
        # Convert scope string to enum
        scope_enum = next((s for s in TestScope if s.value == args.scope), TestScope.ALL)

        # Discover tests based on scope and marker
        test_paths = runner.discover_tests(scope=scope_enum, marker=args.marker)

        # Run the tests
        summary = runner.run_tests(
            test_paths=test_paths,
            marker=args.marker,
            keyword=args.keyword,
            generate_report=args.report,
            report_path=args.report_path
        )

        # Display the summary
        logger.info("Test execution completed.")
        logger.info(f"Summary: Total={summary.total_tests}, Passed={summary.passed}, "
                   f"Failed={summary.failed}, Skipped={summary.skipped}, Errors={summary.errors}")

        # Exit with appropriate code
        if summary.failed > 0 or summary.errors > 0:
            sys.exit(1)