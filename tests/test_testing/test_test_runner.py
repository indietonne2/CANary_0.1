"""
Unit tests for the TestRunner class.
"""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from canary.testing.test_runner import TestRunner


@pytest.mark.unit
def test_run_tests_parses_plural_items(disable_logging):
    """Test that run_tests correctly parses plural 'items' output."""
    runner = TestRunner(test_directory="tests")

    sample_stdout = (
        "============================= test session starts ==============================\n"
        "collected 2 items\n\n"
        "============================== 2 passed in 0.01s ==============================\n"
    )
    mock_process = MagicMock(returncode=0, stdout=sample_stdout, stderr="")

    with patch.object(subprocess, "run", return_value=mock_process):
        with patch("os.path.exists", return_value=False):
            summary = runner.run_tests(test_paths=["dummy"])

    assert summary.total_tests == 2
    assert summary.passed == 2

