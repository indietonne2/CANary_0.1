#!/usr/bin/env python3
"""
Author: CANary Development Team
Version: 0.1.0
Filename: canary_startup.py
Pathname: ./canary_startup.py

This script initializes and runs the CANary CAN-Bus Simulator.
It handles environment setup, dependency installation via Pixi,
CAN interface configuration, and application startup.
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


class CANaryStarter:
    """
    Main class for initializing and running the CANary CAN-Bus Simulator.
    Handles environment setup, dependency management, and application startup.
    """
    
    def __init__(self):
        """Initialize the starter with default settings."""
        self.project_root = Path(__file__).resolve().parent
        self.pixi_available = self._check_pixi_installed()
        
        # Default configuration
        self.config = {
            "interface": "vcan0",
            "bitrate": 500000,
            "virtual": True,
            "headless": False,
            "scenario": "default",
            "log_level": "INFO"
        }
        
        # Load config if exists
        config_path = self.project_root / "config" / "starter_config.json"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
            except Exception as e:
                print(f"Warning: Failed to load config: {e}")

    def _check_pixi_installed(self):
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

    def run_pixi_command(self, command, args=None):
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

    def setup_environment(self):
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
            
        print("Environment setup complete!")
        return True

    def setup_can_interface(self):
        """Set up the CAN interface based on configuration."""
        if platform.system() != "Linux":
            print("CAN interface setup is only supported on Linux.")
            return False
            
        print(f"\n=== Setting up CAN interface: {self.config['interface']} ===")
        
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
                    result = subprocess.run(cmd, check=False)
                    if result.returncode != 0 and "File exists" not in str(result.stderr):
                        print(f"Warning: Command returned non-zero exit code: {result.returncode}")
                except Exception as e:
                    print(f"Error setting up virtual CAN: {e}")
                    return False
                    
            print(f"Virtual CAN interface {self.config['interface']} set up successfully!")
        else:
            # Set up physical CAN interface
            commands = [
                ["sudo", "ip", "link", "set", "down", self.config['interface']],
                ["sudo", "ip", "link", "set", self.config['interface'], "type", "can", "bitrate", str(self.config['bitrate'])],
                ["sudo", "ip", "link", "set", "up", self.config['interface']]
            ]
            
            for cmd in commands:
                print(f"Running: {' '.join(cmd)}")
                try:
                    result = subprocess.run(cmd, check=False)
                    if result.returncode != 0:
                        print(f"Warning: Command returned non-zero exit code: {result.returncode}")
                except Exception as e:
                    print(f"Error setting up physical CAN: {e}")
                    return False
                    
            print(f"Physical CAN interface {self.config['interface']} set up with bitrate {self.config['bitrate']}!")
            
        return True

    def run_application(self, command=None, args=None):
        """Run the CANary application with the specified command and arguments."""
        print("\n=== Running CANary ===")
        
        if not command:
            command = "run"
            
        cli_args = ["python", "-m", "canary.cli", command]
        
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
        
        # Run the command using Pixi to ensure the environment is activated
        pixi_args = ["run", "--"] + cli_args
        
        return self.run_pixi_command("run", pixi_args)

    def interactive_menu(self):
        """Show an interactive menu for the user."""
        while True:
            print("\n=== CANary CAN-Bus Simulator ===")
            print("1. Setup environment")
            print("2. Setup CAN interface")
            print("3. Run simulation")
            print("4. Run web interface")
            print("5. Run tests")
            print("6. Configure settings")
            print("7. Exit")
            
            choice = input("\nEnter your choice (1-7): ")
            
            if choice == "1":
                self.setup_environment()
            elif choice == "2":
                self.setup_can_interface()
            elif choice == "3":
                self.run_application("run")
            elif choice == "4":
                self.run_application("web")
            elif choice == "5":
                self.run_application("test")
            elif choice == "6":
                self.configure_settings()
            elif choice == "7":
                print("Exiting CANary starter.")
                break
            else:
                print("Invalid choice. Please try again.")
            
            input("\nPress Enter to continue...")

    def configure_settings(self):
        """Configure the application settings interactively."""
        print("\n=== Configure CANary Settings ===")
        
        # Ask for CAN interface settings
        print("\nCAN Interface Settings:")
        self.config["virtual"] = input(f"Use virtual CAN interface? (y/n) [{self.config['virtual'] and 'y' or 'n'}]: ").lower() == 'y'
        self.config["interface"] = input(f"CAN interface name [{self.config['interface']}]: ") or self.config["interface"]
        
        if not self.config["virtual"]:
            bitrate_input = input(f"CAN bitrate [{self.config['bitrate']}]: ") or str(self.config["bitrate"])
            try:
                self.config["bitrate"] = int(bitrate_input)
            except ValueError:
                print(f"Invalid bitrate. Using default: {self.config['bitrate']}")
        
        # Ask for simulation settings
        print("\nSimulation Settings:")
        self.config["scenario"] = input(f"Default scenario [{self.config['scenario']}]: ") or self.config["scenario"]
        self.config["headless"] = input(f"Run in headless mode? (y/n) [{self.config['headless'] and 'y' or 'n'}]: ").lower() == 'y'
        
        # Save the configuration
        config_dir = self.project_root / "config"
        config_dir.mkdir(exist_ok=True)
        
        try:
            with open(config_dir / "starter_config.json", 'w') as f:
                json.dump(self.config, f, indent=2)
            print("Configuration saved successfully!")
        except Exception as e:
            print(f"Error saving configuration: {e}")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="CANary CAN-Bus Simulator Starter")
    
    parser.add_argument("--init", action="store_true", help="Initialize the environment")
    parser.add_argument("--setup-can", action="store_true", help="Set up CAN interface")
    parser.add_argument("--run", action="store_true", help="Run the simulation")
    parser.add_argument("--web", action="store_true", help="Start the web interface")
    parser.add_argument("--test", action="store_true", help="Run tests")
    parser.add_argument("--virtual", action="store_true", help="Use virtual CAN interface")
    parser.add_argument("--interface", type=str, help="CAN interface name")
    parser.add_argument("--bitrate", type=int, help="CAN bitrate (bps)")
    parser.add_argument("--scenario", type=str, help="Scenario to run")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    
    return parser.parse_args()


def main():
    """Main function to run the CANary starter."""
    # Parse command line arguments
    args = parse_arguments()
    
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
    
    # Process commands based on arguments
    if args.init:
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
        starter.run_application("test")
    else:
        # No specific command provided, show interactive menu
        starter.interactive_menu()


if __name__ == "__main__":
    main()
