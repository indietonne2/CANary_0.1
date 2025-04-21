"""
Author: Thomas Fischer
Version: 0.1.0
Filename: test_cli.py
Pathname: tests/test_cli/test_cli.py

Tests for the CLI commands of the canCANary CAN-Bus Simulator.
"""

import sys
import pytest
from typer.testing import CliRunner
from rich.console import Console

# Import the module to test
from canary.cli.cli import app


@pytest.fixture
def runner():
    """Create a CLI runner for testing."""
    return CliRunner()


@pytest.mark.unit
class TestCLI:
    """Tests for the CLI module."""
    
    def test_cli_version(self, runner, monkeypatch):
        """Test that the CLI shows the version."""
        def mock_version(pkg_name):
            return "0.1.0.test"
        
        # Patch the version function
        monkeypatch.setattr('importlib.metadata.version', mock_version)
        
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0.test" in result.stdout
    
    def test_init_command(self, runner, disable_logging, mock_error_manager):
        """Test the init command."""
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0
        assert "TF-Canary environment initialized successfully" in result.stdout
    
    def test_setup_can_command(self, runner, monkeypatch, disable_logging, mock_platform_detector):
        """Test the setup-can command."""
        # Set os_type to Linux so the command runs
        mock_platform_detector.os_type.value = "Linux"
        
        result = runner.invoke(app, ["setup-can", "--interface", "vcan0", "--virtual"])
        assert result.exit_code == 0
        assert "Virtual CAN interface vcan0 configured successfully" in result.stdout
    
    def test_run_command_missing_scenario(self, runner, disable_logging):
        """Test the run command without a scenario."""
        result = runner.invoke(app, ["run"])
        assert result.exit_code == 1
        assert "Scenario name is required" in result.stdout
    
    def test_run_command_with_scenario(self, runner, disable_logging, mock_platform_detector):
        """Test the run command with a scenario."""
        result = runner.invoke(app, ["run", "--scenario", "test_scenario", "--headless"])
        assert result.exit_code == 0
        assert "Running scenario: test_scenario" in result.stdout
        assert "Simulation started in headless mode" in result.stdout
    
    def test_test_command(self, runner, disable_logging):
        """Test the test command."""
        result = runner.invoke(app, ["test"])
        assert result.exit_code == 0
        assert "Running TF-Canary test suite" in result.stdout
    
    def test_web_command(self, runner, disable_logging):
        """Test the web command."""
        # Mock KeyboardInterrupt to exit the web server loop
        with pytest.raises(KeyboardInterrupt):
            runner.invoke(app, ["web", "--host", "localhost", "--port", "8080"])
