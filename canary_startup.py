#!/usr/bin/env python3
"""
Author: CANary Development Team
Version: 0.1.5
Filename: canary_startup.py
Pathname: ./canary_startup.py
Description:
canCANary CAN-Bus Simulator

This package provides a comprehensive CAN-Bus simulation platform
with support for GUI and CLI interfaces, virtual and hardware CAN
interfaces, and scenario-based testing.
"""

import os
import sys
import subprocess
import platform
import argparse
import shutil
from pathlib import Path
import json
import time
import logging
from typing import Dict, Any, List, Optional, Union

# Import the test runner
try:
    from src.testing.test_runner import TestRunner, TestScope
except ImportError:
    print("Warning: Could not import TestRunner. Self-testing will be unavailable.")
    TestRunner = None
    TestScope = None

# Import platform detector
try:
    from src.core.platform_detector import get_platform_detector, OSType, HardwareType

    PLATFORM_DETECTOR_AVAILABLE = True
except ImportError:
    print("Warning: Could not import platform_detector. Platform-specific features will be limited.")
    PLATFORM_DETECTOR_AVAILABLE = False


    # Create fallback enum classes for compatibility
    class OSType:
        LINUX = "Linux"
        WINDOWS = "Windows"
        MACOS = "Darwin"
        RASPBERRY_PI = "RaspberryPi"
        UNKNOWN = "Unknown"


    class HardwareType:
        X86_64 = "x86_64"
        ARM = "arm"
        ARM64 = "aarch64"
        UNKNOWN = "unknown"

# Define version
__version__ = "0.1.3"  # Incremented last digit

# Configure logging for the canary startup process
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
canary_logger = logging.getLogger("canary_startup")

# Additional logger for self-test results
self_test_logger = logging.getLogger("canary_startup_self_test")
self_test_handler = logging.StreamHandler(sys.stdout)
self_test_formatter = logging.Formatter('CANARY_SELF_TEST - %(asctime)s - %(levelname)s - %(message)s')
self_test_handler.setFormatter(self_test_formatter)
self_test_logger.addHandler(self_test_handler)
self_test_logger.setLevel(logging.INFO)
self_test_logger.propagate = False


class CANaryStarter:
    """
    Main class for initializing and running the CANary CAN-Bus Simulator.
    Handles environment setup, dependency management, and application startup.
    """

    def __init__(self):
        """Initialize the starter with default settings."""
        self.project_root = Path(__file__).resolve().parent
        self.pixi_available = self._check_pixi_installed()

        # Initialize platform detection if available
        self.platform_detector = None
        if PLATFORM_DETECTOR_AVAILABLE:
            try:
                self.platform_detector = get_platform_detector()
                canary_logger.info(
                    f"Platform detection initialized: {self.platform_detector.os_type.value} on {self.platform_detector.hardware_type.value}")
            except Exception as e:
                canary_logger.error(f"Error initializing platform detector: {e}")

        # Default configuration based on detected platform
        self.config = self._get_default_config()

        # Load config if exists
        config_path = self.project_root / "config" / "starter_config.json"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
            except Exception as e:
                print(f"Warning: Failed to load config: {e}")

        # Display version and configuration
        self._display_header()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration based on detected platform."""
        config = {
            "interface": "vcan0",
            "bitrate": 500000,
            "virtual": True,
            "headless": False,
            "scenario": "default",
            "log_level": "INFO"
        }

        # Adjust configuration based on detected platform if platform detector is available
        if self.platform_detector:
            # Get recommended CAN interface if available
            recommended_interface = self.platform_detector.get_recommended_can_interface()
            if recommended_interface:
                config["interface"] = recommended_interface

            # Set virtual CAN based on platform
            if self.platform_detector.os_type == OSType.RASPBERRY_PI:
                # On Raspberry Pi, default to physical CAN if interfaces detected
                if self.platform_detector.can_interfaces:
                    physical_interfaces = [i for i in self.platform_detector.can_interfaces if not i.startswith('v')]
                    if physical_interfaces:
                        config["virtual"] = False

            # On macOS, adjust for platform limitations
            if self.platform_detector.os_type == OSType.MACOS:
                config["virtual"] = True  # macOS requires virtual interfaces or adapters

            # On Windows, adjust for platform limitations
            if self.platform_detector.os_type == OSType.WINDOWS:
                config["virtual"] = True  # Windows typically requires adapters

        return config

    def _display_header(self):
        """Display the CANary header with version and configuration information."""
        print("\n" + "=" * 80)
        print(f"CANary CAN-Bus Simulator v{__version__}")
        print("=" * 80)
        print(f"Project Root: {self.project_root}")

        # Display platform information if available
        if self.platform_detector:
            print("\nPlatform Information:")
            print(f"  - OS: {self.platform_detector.os_type.value}")
            print(f"  - Hardware: {self.platform_detector.hardware_type.value}")
            if self.platform_detector.os_type == OSType.RASPBERRY_PI:
                rpi_info = self.platform_detector.platform_info.get("raspberry_pi", {})
                if "model" in rpi_info:
                    print(f"  - Model: {rpi_info['model']}")
            elif self.platform_detector.os_type == OSType.MACOS:
                mac_info = self.platform_detector.platform_info.get("macos", {})
                if "product_version" in mac_info:
                    print(f"  - macOS Version: {mac_info['product_version']}")

            print(f"  - CAN Support: {'Yes' if self.platform_detector.is_can_supported() else 'No'}")
            if self.platform_detector.can_interfaces:
                print(f"  - Detected Interfaces: {', '.join(self.platform_detector.can_interfaces)}")

        print("\nConfiguration:")
        print(f"  - Interface: {self.config['interface']}")
        print(f"  - Bitrate: {self.config['bitrate']} bps")
        print(f"  - Virtual: {'Yes' if self.config['virtual'] else 'No'}")
        print(f"  - Headless: {'Yes' if self.config['headless'] else 'No'}")
        print(f"  - Scenario: {self.config['scenario']}")
        print(f"  - Log Level: {self.config['log_level']}")
        print(f"  - Pixi Available: {'Yes' if self.pixi_available else 'No'}")
        print("=" * 80 + "\n")

    def _check_pixi_installed(self) -> bool:
        """Check if Pixi is installed and available in PATH."""
        try:
            result = subprocess.run(
                ["pixi", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def _install_pixi(self):
        """Provide instructions for installing Pixi."""
        print("\n=== Pixi Installation Instructions ===")
        print("Pixi is required but not found on your system.")

        if platform.system() == "Windows":
            print("\nTo install Pixi on Windows:")
            print("1. Open PowerShell as administrator")
            print("2. Run the following command:")
            print("   curl -fsSL https://pixi.sh/install.ps1 | powershell")
        elif platform.system() in ["Linux", "Darwin"]:
            print("\nTo install Pixi on Linux/macOS:")
            print("1. Open a terminal")
            print("2. Run the following command:")
            print("   curl -fsSL https://pixi.sh/install.sh | bash")

        print("\nAfter installation, restart this script.")
        sys.exit(1)

    def run_pixi_command(self, command: str, args: List[str] = None) -> bool:
        """Run a Pixi command with given arguments."""
        if not self.pixi_available:
            self._install_pixi()

        full_command = ["pixi", command]
        if args:
            full_command.extend(args)

        print(f"Running: {' '.join(full_command)}")

        result = subprocess.run(
            full_command,
            cwd=self.project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            print(f"Error running Pixi command: {result.stderr}")
            return False

        return True

    def setup_environment(self) -> bool:
        """Set up the Pixi environment for CANary."""
        print("\n=== Setting up CANary environment ===")

        # Create necessary directories
        os.makedirs(self.project_root / "logs", exist_ok=True)
        os.makedirs(self.project_root / "config", exist_ok=True)
        os.makedirs(self.project_root / "scenarios", exist_ok=True)

        # Run pixi install
        print("Installing dependencies with Pixi...")
        if not self.run_pixi_command("install"):
            print("Failed to install dependencies.")
            return False

        # Platform-specific setup if needed
        if self.platform_detector:
            if self.platform_detector.os_type == OSType.RASPBERRY_PI:
                self._setup_raspberry_pi_environment()
            elif self.platform_detector.os_type == OSType.MACOS:
                self._setup_macos_environment()

        print("Environment setup complete!")
        return True

    def _setup_raspberry_pi_environment(self):
        """Set up Raspberry Pi specific environment."""
        print("\n=== Setting up Raspberry Pi environment ===")

        # Check for and enable SPI/I2C if needed
        rpi_info = self.platform_detector.platform_info.get("raspberry_pi", {})
        if not rpi_info.get("spi_present", False):
            print("SPI not detected. You may need to enable it using raspi-config.")
            print("Run 'sudo raspi-config' and enable SPI under Interfacing Options.")

        if not rpi_info.get("i2c_present", False):
            print("I2C not detected. You may need to enable it using raspi-config.")
            print("Run 'sudo raspi-config' and enable I2C under Interfacing Options.")

        # Check for CAN interfaces
        if not self.platform_detector.can_interfaces:
            print("No CAN interfaces detected. Setting up virtual CAN interface.")
            self.setup_can_interface()

    def _setup_macos_environment(self):
        """Set up macOS specific environment."""
        print("\n=== Setting up macOS environment ===")

        # Check for Homebrew
        mac_info = self.platform_detector.platform_info.get("macos", {})
        if not mac_info.get("homebrew_present", False):
            print("Homebrew not detected. It's recommended for installing dependencies.")
            print("Visit https://brew.sh for installation instructions.")

        # Check for CAN tools
        print("Note: On macOS, hardware CAN interfaces require specific drivers.")
        print("Virtual CAN simulation will be used by default.")

        # Set virtual mode to ensure compatibility
        self.config["virtual"] = True

    def setup_can_interface(self) -> bool:
        """Set up the CAN interface based on configuration."""
        print(f"\n=== Setting up CAN interface: {self.config['interface']} ===")

        # Platform-specific CAN setup
        if self.platform_detector:
            if self.platform_detector.os_type in [OSType.LINUX, OSType.RASPBERRY_PI]:
                return self._setup_linux_can_interface()
            elif self.platform_detector.os_type == OSType.MACOS:
                return self._setup_macos_can_interface()
            elif self.platform_detector.os_type == OSType.WINDOWS:
                return self._setup_windows_can_interface()
        else:
            # Fallback to basic Linux detection if platform detector is not available
            if platform.system() == "Linux":
                return self._setup_linux_can_interface()
            else:
                print(f"CAN interface setup is currently not supported on {platform.system()}")
                return False

    def _setup_linux_can_interface(self) -> bool:
        """Set up CAN interface on Linux/Raspberry Pi."""
        if self.config['virtual']:
            # Set up virtual CAN interface
            commands = [
                ["sudo", "modprobe", "vcan"],
                ["sudo", "ip", "link", "add", "dev", self.config['interface'], "type", "vcan"],
                ["sudo", "ip", "link", "set", "up", self.config['interface']]
            ]

            for cmd in commands:
                print(f"Running: {' '.join(cmd)}")
                try:
                    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
                    if result.returncode != 0 and "File exists" not in str(result.stderr):
                        print(f"Warning: Command returned non-zero exit code: {result.returncode}")
                        print(f"Error: {result.stderr}")
                except Exception as e:
                    print(f"Error setting up virtual CAN: {e}")
                    return False

            print(f"Virtual CAN interface {self.config['interface']} set up successfully!")
        else:
            # Set up physical CAN interface
            commands = [
                ["sudo", "ip", "link", "set", "down", self.config['interface']],
                ["sudo", "ip", "link", "set", self.config['interface'], "type", "can", "bitrate",
                 str(self.config['bitrate'])],
                ["sudo", "ip", "link", "set", "up", self.config['interface']]
            ]

            for cmd in commands:
                print(f"Running: {' '.join(cmd)}")
                try:
                    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
                    if result.returncode != 0:
                        print(f"Warning: Command returned non-zero exit code: {result.returncode}")
                        print(f"Error: {result.stderr}")
                except Exception as e:
                    print(f"Error setting up physical CAN: {e}")
                    return False

            print(f"Physical CAN interface {self.config['interface']} set up with bitrate {self.config['bitrate']}!")

        return True

    def _setup_macos_can_interface(self) -> bool:
        """Set up CAN interface on macOS (mostly virtual/simulated)."""
        print("Setting up CAN interface on macOS...")
        print("Note: macOS requires virtual CAN simulation or hardware adapters with specific drivers.")

        # For macOS, we'll use a virtual interface
        print(f"Using virtual CAN interface: {self.config['interface']}")
        print("This will be simulated in software, no actual hardware configuration is performed.")

        # Update config to ensure virtual mode
        self.config['virtual'] = True

        # Save the config to indicate we've set up the interface
        self._save_config()

        return True

    def _setup_windows_can_interface(self) -> bool:
        """Set up CAN interface on Windows (requires hardware adapters)."""
        print("Setting up CAN interface on Windows...")
        print("Note: Windows requires hardware CAN adapters with specific drivers.")

        # For Windows, we need to check for adapters
        if self.platform_detector and self.platform_detector.can_interfaces:
            print(f"Detected CAN interfaces: {', '.join(self.platform_detector.can_interfaces)}")
            print(f"Using interface: {self.config['interface']}")
        else:
            print("No CAN interfaces detected. Please install appropriate drivers for your CAN hardware.")
            print("Using virtual simulation mode.")
            self.config['virtual'] = True

        # Save the config
        self._save_config()

        return True

    def _save_config(self):
        """Save the current configuration to a file."""
        config_dir = self.project_root / "config"
        config_dir.mkdir(exist_ok=True)

        try:
            with open(config_dir / "starter_config.json", 'w') as f:
                json.dump(self.config, f, indent=2)
            print("Configuration saved successfully!")
        except Exception as e:
            print(f"Error saving configuration: {e}")

    def run_application(self, command: str = None, args: List[str] = None) -> bool:
        """Run the CANary application with the specified command and arguments."""
        print("\n=== Running CANary ===")

        if not command:
            command = "run"

        cli_args = ["python", str(self.project_root / "canary_startup.py"), f"--{command}"]

        if command == "run":
            # Add scenario parameter
            cli_args.extend(["--scenario", self.config["scenario"]])

            # Add interface parameter if provided
            if self.config["interface"]:
                cli_args.extend(["--interface", self.config["interface"]])

            # Add headless flag if enabled
            if self.config["headless"]:
                cli_args.append("--headless")

        elif command == "setup-can":
            cli_args.extend(["--interface", self.config["interface"]])
            cli_args.extend(["--bitrate", str(self.config["bitrate"])])
            if self.config["virtual"]:
                cli_args.append("--virtual")

        # Add any additional arguments
        if args:
            cli_args.extend(args)

        print(f"Running: {' '.join(cli_args)}")

        # Display the parameters in a more structured way
        print("\nCommand-line Parameters:")
        for i, arg in enumerate(cli_args):
            if arg.startswith("--") and i + 1 < len(cli_args) and not cli_args[i + 1].startswith("--"):
                print(f"  {arg}: {cli_args[i + 1]}")
            elif arg.startswith("--") and (i + 1 >= len(cli_args) or cli_args[i + 1].startswith("--")):
                print(f"  {arg}: <flag>")

        # Run the command using Pixi to ensure the environment is activated
        pixi_args = ["--"] + cli_args

        return self.run_pixi_command("run", pixi_args)

    def interactive_menu(self):
        """Show an interactive menu for the user."""
        while True:
            print("\n=== CANary CAN-Bus Simulator ===")
            # Display platform info in the menu header
            if self.platform_detector:
                print(
                    f"Platform: {self.platform_detector.os_type.value} on {self.platform_detector.hardware_type.value}")
                print(
                    f"CAN Interfaces: {', '.join(self.platform_detector.can_interfaces) if self.platform_detector.can_interfaces else 'None detected'}")

            print("\nOptions:")
            print("1. Setup environment")
            print("2. Setup CAN interface")
            print("3. Run simulation")
            print("4. Run web interface")
            print("5. Run tests")
            print("6. Configure settings")
            print("7. Platform information")
            print("8. Exit")

            choice = input("\nEnter your choice (1-8): ")

            if choice == "1":
                self.setup_environment()
            elif choice == "2":
                self.setup_can_interface()
            elif choice == "3":
                self.run_application("run")
            elif choice == "4":
                self.run_application("web")
            elif choice == "5":
                self.run_tests_menu()
            elif choice == "6":
                self.configure_settings()
            elif choice == "7":
                self.display_platform_info()
            elif choice == "8":
                print("Exiting CANary starter.")
                break
            else:
                print("Invalid choice. Please try again.")

            input("\nPress Enter to continue...")

    def display_platform_info(self):
        """Display detailed platform information."""
        print("\n=== Platform Information ===")

        if self.platform_detector:
            # Display the platform summary
            print(self.platform_detector.get_platform_summary())

            # Display detected CAN interfaces
            print("\nCAN Interface Information:")
            print(f"CAN Supported: {'Yes' if self.platform_detector.is_can_supported() else 'No'}")
            print(
                f"Detected Interfaces: {', '.join(self.platform_detector.can_interfaces) if self.platform_detector.can_interfaces else 'None'}")
            print(f"Recommended Interface: {self.platform_detector.get_recommended_can_interface() or 'None'}")

            # Display platform-specific details
            if self.platform_detector.os_type == OSType.RASPBERRY_PI:
                rpi_info = self.platform_detector.platform_info.get("raspberry_pi", {})
                print("\nRaspberry Pi Details:")
                for key, value in rpi_info.items():
                    print(f"  - {key}: {value}")

            elif self.platform_detector.os_type == OSType.MACOS:
                mac_info = self.platform_detector.platform_info.get("macos", {})
                print("\nmacOS Details:")
                for key, value in mac_info.items():
                    print(f"  - {key}: {value}")
        else:
            print("Platform detector is not available.")
            print(f"OS: {platform.system()}")
            print(f"Release: {platform.release()}")
            print(f"Version: {platform.version()}")
            print(f"Machine: {platform.machine()}")
            print(f"Processor: {platform.processor()}")

    def run_tests_menu(self):
        """Show a submenu for running tests."""
        while True:
            print("\n=== Test Runner Options ===")
            print("1. Run all tests")
            print("2. Run unit tests")
            print("3. Run integration tests")
            print("4. Run system tests")
            print("5. Run smoke tests")
            print("6. Run self-test")
            print("7. Back to main menu")

            choice = input("\nEnter your choice (1-7): ")

            if choice == "1":
                self.run_application("test", ["--scope", "all"])
            elif choice == "2":
                self.run_application("test", ["--scope", "unit"])
            elif choice == "3":
                self.run_application("test", ["--scope", "integration"])
            elif choice == "4":
                self.run_application("test", ["--scope", "system"])
            elif choice == "5":
                self.run_application("test", ["--scope", "smoke"])
            elif choice == "6":
                self.run_application("test", ["--self-test"])
            elif choice == "7":
                break
            else:
                print("Invalid choice. Please try again.")

            input("\nPress Enter to continue...")

    def configure_settings(self):
        """Configure the application settings interactively."""
        print("\n=== Configure CANary Settings ===")

        # Ask for CAN interface settings
        print("\nCAN Interface Settings:")

        # Use platform detector to help with configuration
        if self.platform_detector and self.platform_detector.os_type in [OSType.MACOS, OSType.WINDOWS]:
            print(f"Note: On {self.platform_detector.os_type.value}, virtual CAN is recommended.")

        virtual_default = 'y' if self.config['virtual'] else 'n'
        virtual_input = input(f"Use virtual CAN interface? (y/n) [{virtual_default}]: ").lower()
        self.config["virtual"] = virtual_input == 'y' if virtual_input else self.config["virtual"]

        # Suggest detected interfaces if available
        if self.platform_detector and self.platform_detector.can_interfaces:
            print(f"Detected interfaces: {', '.join(self.platform_detector.can_interfaces)}")
            recommended = self.platform_detector.get_recommended_can_interface()
            if recommended:
                print(f"Recommended interface: {recommended}")

        self.config["interface"] = input(f"CAN interface name [{self.config['interface']}]: ") or self.config[
            "interface"]

        if not self.config["virtual"]:
            bitrate_input = input(f"CAN bitrate [{self.config['bitrate']}]: ") or str(self.config['bitrate'])
            try:
                self.config["bitrate"] = int(bitrate_input)
            except ValueError:
                print(f"Invalid bitrate. Using default: {self.config['bitrate']}")

        # Ask for simulation settings
        print("\nSimulation Settings:")
        self.config["scenario"] = input(f"Default scenario [{self.config['scenario']}]: ") or self.config["scenario"]

        # Headless mode makes more sense on RaspberryPi
        headless_prompt = "Run in headless mode (no GUI)?"
        if self.platform_detector and self.platform_detector.os_type == OSType.RASPBERRY_PI:
            headless_prompt += " (Recommended for Raspberry Pi)"

        headless_default = 'y' if self.config['headless'] else 'n'
        self.config["headless"] = input(f"{headless_prompt} (y/n) [{headless_default}]: ").lower() == 'y'

        # Ask for logging settings
        print("\nLogging Settings:")
        log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        print("Available log levels: " + ", ".join(log_levels))
        log_level = input(f"Log level [{self.config['log_level']}]: ") or self.config["log_level"]
        if log_level in log_levels:
            self.config["log_level"] = log_level
        else:
            print(f"Invalid log level. Using default: {self.config['log_level']}")

        # Save the configuration
        self._save_config()

        # Update the display header with new config
        self._display_header()


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="CANary CAN-Bus Simulator Starter")

    # Main commands
    command_group = parser.add_argument_group("Commands")
    command_group.add_argument("--init", action="store_true", help="Initialize the environment")
    command_group.add_argument("--setup-can", action="store_true", help="Set up CAN interface")
    command_group.add_argument("--run", action="store_true", help="Run the simulation")
    command_group.add_argument("--web", action="store_true", help="Start the web interface")
    command_group.add_argument("--test", action="store_true", help="Run tests")
    command_group.add_argument("--platform-info", action="store_true", help="Display platform information")

    # Test-specific options
    test_group = parser.add_argument_group("Test Options")
    test_group.add_argument("--scope", choices=["unit", "integration", "system", "acceptance", "smoke", "all"],
                            default="all", help="Scope of tests to run")
    test_group.add_argument("--marker", help="Pytest marker to filter tests")
    test_group.add_argument("--keyword", help="Pytest keyword expression to filter tests")
    test_group.add_argument("--report", action="store_true", help="Generate HTML test report")
    test_group.add_argument("--report-path", default="test_report.html", help="Path for HTML test report")
    test_group.add_argument("--self-test", action="store_true", help="Run self-test only")

    # CAN interface options
    can_group = parser.add_argument_group("CAN Interface Options")
    can_group.add_argument("--virtual", action="store_true", help="Use virtual CAN interface")
    can_group.add_argument("--interface", type=str, help="CAN interface name")
    can_group.add_argument("--bitrate", type=int, help="CAN bitrate (bps)")

    # Simulation options
    sim_group = parser.add_argument_group("Simulation Options")
    sim_group.add_argument("--scenario", type=str, help="Scenario to run")
    sim_group.add_argument("--headless", action="store_true", help="Run in headless mode")
    sim_group.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                           default="INFO", help="Logging level")

    # Version
    parser.add_argument("--version", action="store_true", help="Show version information and exit")

    return parser.parse_args()


def run_test_with_args(args, starter):
    """Run tests based on command line arguments."""
    if TestRunner is None:
        print("Error: TestRunner module not available. Cannot run tests.")
        return False

    # Determine the test scope enum
    scope_str = args.scope.upper() if args.scope else "ALL"
    scope_enum = None

    if TestScope:
        for scope in TestScope:
            if scope.name == scope_str:
                scope_enum = scope
                break

    if scope_enum is None:
        print(f"Error: Invalid test scope '{args.scope}'")
        return False

    # Create a TestRunner instance
    test_dir = starter.project_root / "tests"
    runner = TestRunner(test_directory=str(test_dir))

    # Handle self-test
    if args.self_test:
        print("Running TestRunner self-test...")
        return runner.run_self_test(invoked_by_canary_startup=True)

    # Discover and run tests
    test_paths = runner.discover_tests(scope=scope_enum, marker=args.marker)

    summary = runner.run_tests(
        test_paths=test_paths,
        marker=args.marker,
        keyword=args.keyword,
        generate_report=args.report,
        report_path=args.report_path
    )

    print("\nTest Execution Summary:")
    print(f"Total Tests: {summary.total_tests}")
    print(f"Passed: {summary.passed}")
    print(f"Failed: {summary.failed}")
    print(f"Skipped: {summary.skipped}")
    print(f"Errors: {summary.errors}")
    print(f"Duration: {summary.duration:.2f} seconds")

    return summary.failed == 0 and summary.errors == 0


def main():
    """Main function to run the CANary starter."""
    # Parse command line arguments
    args = parse_arguments()

    # Handle version display
    if args.version:
        print(f"CANary CAN-Bus Simulator v{__version__}")

        # Display platform information with version if available
        if PLATFORM_DETECTOR_AVAILABLE:
            try:
                detector = get_platform_detector()
                print(f"Running on: {detector.os_type.value} {detector.hardware_type.value}")
            except Exception:
                pass

        return

    # Create the starter instance
    starter = CANaryStarter()

    # Update config from command line arguments
    if args.interface:
        starter.config["interface"] = args.interface
    if args.bitrate:
        starter.config["bitrate"] = args.bitrate
    if args.scenario:
        starter.config["scenario"] = args.scenario
    if args.virtual:
        starter.config["virtual"] = True
    if args.headless:
        starter.config["headless"] = True
    if args.log_level:
        starter.config["log_level"] = args.log_level

    # Process commands based on arguments
    if args.platform_info:
        starter.display_platform_info()
    elif args.init:
        starter.setup_environment()
    elif args.setup_can:
        starter.setup_can_interface()
    elif args.run:
        starter.setup_environment()
        starter.run_application("run")
    elif args.web:
        starter.setup_environment()
        starter.run_application("web")
    elif args.test:
        starter.setup_environment()
        run_test_with_args(args, starter)
    else:
        # No specific command provided, show interactive menu
        starter.interactive_menu()


def main_startup_procedure():
    """Run the main CANary startup procedure with self-testing."""
    canary_logger.info("Canary startup sequence initiated.")

    # Log platform information if available
    if PLATFORM_DETECTOR_AVAILABLE:
        try:
            detector = get_platform_detector()
            canary_logger.info(f"Platform: {detector.os_type.value} on {detector.hardware_type.value}")
            if detector.can_interfaces:
                canary_logger.info(f"Detected CAN interfaces: {', '.join(detector.can_interfaces)}")
            else:
                canary_logger.warning("No CAN interfaces detected.")
        except Exception as e:
            canary_logger.error(f"Error detecting platform: {e}")

    # Check if TestRunner is available
    if TestRunner is None:
        canary_logger.error("TestRunner module not available. Self-testing is disabled.")
        return False

    # Initialize the TestRunner
    test_dir = Path(__file__).resolve().parent / "tests"
    runner = TestRunner(test_directory=str(test_dir))

    canary_logger.info("Performing TestRunner self-test...")
    # Run self-test with canary startup flag
    self_test_ok = runner.run_self_test(invoked_by_canary_startup=True)

    if self_test_ok:
        canary_logger.info("TestRunner self-test PASSED. Proceeding with startup.")
        # Run smoke tests if self-test passed
        canary_logger.info("Running smoke tests...")
        try:
            smoke_test_paths = runner.discover_tests(scope=TestScope.SMOKE)
            smoke_test_summary = runner.run_tests(test_paths=smoke_test_paths)

            if smoke_test_summary.failed == 0 and smoke_test_summary.errors == 0:
                canary_logger.info("Smoke tests PASSED.")
            else:
                canary_logger.error("Smoke tests FAILED. Proceeding with caution.")
                # Continuing despite smoke test failures - this could be configurable
        except Exception as e:
            canary_logger.error(f"Error running smoke tests: {e}")
    else:
        canary_logger.error(
            "TestRunner self-test FAILED. This may indicate issues with the testing environment or pytest setup.")
        canary_logger.error(
            "Aborting startup sequence. Check 'canary_startup_self_test' logs or console output for details from test_runner.")
        return False

    canary_logger.info("Canary startup sequence completed successfully.")
    return True


if __name__ == "__main__":
    # Default behavior is to run main() which processes command line args
    # However, if a specific environment variable is set, we would run the startup procedure instead
    if os.environ.get("CANARY_RUN_STARTUP_PROCEDURE") == "1":
        success = main_startup_procedure()
        if not success:
            sys.exit(1)
    else:
        main()