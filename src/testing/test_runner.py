"""
Author: Thomas Fischer
Version: 0.1.2
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

import enum
import dataclasses
import subprocess
import sys
import logging
import os
import tempfile
import pytest # For type hinting and potentially direct calls

# Configure basic logging for the module
logger = logging.getLogger(__name__)
# Example: logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Proper logging configuration should be handled by the application's entry point.

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
    ERROR = "ERROR" # Indicates an error during test setup or execution, not a test failure itself

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
        self.logger.info(f"TestRunner initialized. Target test directory: {self.test_directory}") # Log the actual path
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
        # For more specific discovery, one might walk the directory or use pytest's collection hooks.
        
        target_dir = self.test_directory
        if scope != TestScope.ALL and scope != TestScope.SMOKE : # Smoke might run across all, or specific minimal set
             # Assuming scopes like UNIT, INTEGRATION map to subdirectories
            scope_dir = os.path.join(self.test_directory, scope.value)
            if os.path.isdir(scope_dir):
                target_dir = scope_dir
            else:
                self.logger.warning(f"Scope directory '{scope_dir}' not found. Using base test directory.")

        # This method is more for conceptual grouping; pytest's `-k` or `-m` will do the real filtering.
        # For now, it just returns the target directory for pytest to scan.
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
        pytest_args = list(test_paths) # Start with paths to test

        if marker:
            pytest_args.extend(["-m", marker])
            self.logger.info(f"Filtering by marker: {marker}")
        
        if keyword:
            pytest_args.extend(["-k", keyword])
            self.logger.info(f"Filtering by keyword: {keyword}")

        # Add arguments for collecting results; using a temporary JSON report is robust
        # We will parse this JSON report to create the TestSummary
        # However, for simplicity in this step, we'll rely on pytest's exit code and stdout/stderr.
        # A more advanced version would use pytest.main() and plugins or parse json output.

        # For now, let's use subprocess and capture output.
        # This is generally more isolated than `pytest.main()`.
        pytest_command = [sys.executable, "-m", "pytest"] + pytest_args
        
        if generate_report:
            pytest_command.extend([f"--html={report_path}", "--self-contained-html"])
            self.logger.info(f"Generating HTML report at: {report_path}")

        self.logger.debug(f"Executing pytest command: {' '.join(pytest_command)}")

        try:
            # Note: Capturing output can be memory intensive for large test suites.
            # Using pytest's JSON report (`--json-report`) and parsing it is more robust for data.
            # However, direct output capture is simpler for a basic implementation.
            process = subprocess.run(pytest_command, capture_output=True, text=True, check=False)
            
            # Basic parsing of pytest output - this is very fragile.
            # A real implementation should use pytest's rich terminal output, JSON report, or a custom plugin.
            # For now, we primarily rely on exit codes.
            # Exit codes: 0 = all tests passed, 1 = tests failed, 2 = interrupted, ...
            
            summary = TestSummary()
            # This is a placeholder for proper result parsing.
            # For accurate counts, you need to parse pytest's output or use a report file.
            if process.returncode == 0:
                summary.passed = -1 # Flag that we don't have exact counts from this simple run
                self.logger.info("Pytest execution successful (all tests passed or skipped appropriately).")
            elif process.returncode == 1:
                summary.failed = -1 # Flag that we don't have exact counts
                self.logger.warning("Pytest execution completed with test failures.")
            else:
                summary.errors = -1 # Flag that we don't have exact counts
                self.logger.error(f"Pytest execution failed with exit code {process.returncode}.")

            self.logger.info("Pytest stdout:\n" + process.stdout)
            if process.stderr:
                self.logger.warning("Pytest stderr:\n" + process.stderr)
            
            # A more sophisticated approach would involve pytest.main and a custom plugin
            # or parsing the output of `pytest --json-report`.
            # For now, we'll return a summary based on exit code.
            # TODO: Implement robust parsing of pytest output or use JSON report.

            return summary # This summary is very basic.

        except FileNotFoundError:
            self.logger.error("pytest command not found. Make sure pytest is installed and in PATH.")
            return TestSummary(errors=1) # Indicate an error in running tests
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
            # Using a simplified version of run_tests logic
            pytest_command = [sys.executable, "-m", "pytest", test_file_path, "-v"]
            process = subprocess.run(pytest_command, capture_output=True, text=True, check=False)

            if process.returncode == 0:
                self.logger.info("Self-test PASSED.")
                if "1 passed" in process.stdout: # A simple check
                    passed = True
                else: # Should not happen if exit code is 0 and test is simple pass
                    self.logger.warning("Self-test passed (exit code 0) but output confirmation not found.")
                    self.logger.debug(f"Self-test stdout: {process.stdout}")
                    passed = True # Assume pass on exit code 0
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
            # This could involve writing to a dedicated log file or using a specific logger
            # For now, we'll just add a distinct log message.
            canary_logger = logging.getLogger("canary_startup_self_test")
            # Ensure it has a handler if not configured by canary_startup.py
            if not canary_logger.hasHandlers():
                # Example: could log to a specific file like 'canary_self_test.log'
                # For now, log to console with a special prefix.
                handler = logging.StreamHandler(sys.stdout)
                formatter = logging.Formatter('CANARY_SELF_TEST - %(asctime)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                canary_logger.addHandler(handler)
                canary_logger.propagate = False # Avoid duplicate logging if root logger is also stdout

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
    
    runner = TestRunner(test_directory="path/to/your/project/tests") # Adjust test_directory as needed
                                                                     # For self-contained example, this might not be used unless testing run_tests
    
    # Check if this script is being run in a context that implies canary_startup.py initiated it.
    # This is a placeholder. A real check might involve:
    # - Checking sys.argv for a specific flag.
    # - Checking an environment variable set by canary_startup.py.
    # - Being called by a specific function in canary_startup.py which passes a flag.
    
    # Simulating the check:
    # For example, if canary_startup.py always calls a main function in this script like `main(from_canary=True)`
    # or sets an environment variable os.environ.get("INVOKED_BY_CANARY") == "true"
    
    # For this example, let's assume if __name__ == "__main__" AND a specific arg is passed,
    # it's a canary startup style invocation for the self-test.
    is_canary_invocation = False
    if len(sys.argv) > 1 and sys.argv[1] == "--canary-self-test":
        logger.info("Invoked with --canary-self-test flag.")
        is_canary_invocation = True

    self_test_passed = runner.run_self_test(invoked_by_canary_startup=is_canary_invocation)
    
    if self_test_passed:
        logger.info("TestRunner self-test completed successfully.")
        # As an example, you could proceed to run actual project tests
        # summary = runner.run_tests(marker="smoke")
        # logger.info(f"Test run summary: {summary}")
    else:
        logger.error("TestRunner self-test failed. Please check logs.")
        sys.exit(1) # Exit with error if self-test fails

    # Example of running actual tests (assuming a 'tests' directory exists relative to where this is run)
    # print("\nRunning example project tests (if any configured):")
    # project_tests_path = os.path.join(os.path.dirname(__file__), '..', 'tests') # Adjust path as needed
    # if not os.path.isdir(project_tests_path):
    #    project_tests_path = "tests" # Fallback for common project structures
    #
    # if os.path.isdir(project_tests_path):
    #    project_runner = TestRunner(test_directory=project_tests_path)
    #    test_summary = project_runner.run_tests()
    #    print(f"Project Test Summary: Total={test_summary.total_tests}, Passed={test_summary.passed}, Failed={test_summary.failed}")
    # else:
    #    print(f"Skipping example project tests: Directory '{project_tests_path}' not found.")