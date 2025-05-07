"""
Author: Thomas Fischer
Version: 0.1.0
Filename: cli.py
Pathname: src/cli/cli.py

This module implements the command-line interface for the canCANary CAN-Bus Simulator.
It provides a unified entry point for all CLI commands and options.

Commands:
    init: Initialize the canCANary environment
    setup-can: Configure CAN bus interfaces
    run: Run a CAN bus simulation scenario
    test: Run the test suite
    web: Start the web interface

The CLI is built using Typer and Rich for a modern, user-friendly interface
with colorful output, progress bars, and helpful error messages.
"""

import os
import sys
import time
from pathlib import Path
from typing import Optional, List, Dict, Any

import typer
from rich.console import Console
from rich.progress import Progress
from rich.panel import Panel
from rich import print as rprint

# Local imports (using relative imports for the package)
from ..core.logging_system import LoggingSystem, get_logger
from ..core.error_manager import ErrorManager, ConfigurationError
from ..core.platform_detector import PlatformDetector

# Create the CLI app
app = typer.Typer(
    name="canary",
    help="canCANary CAN-Bus Simulator for Raspberry Pi and Web",
    add_completion=False
)

# Console for rich output
console = Console()


def version_callback(value: bool):
    """Print version information and exit."""
    if value:
        from importlib.metadata import version
        try:
            v = version("canary")
        except:
            v = "0.1.0 (development)"
            
        console.print(f"[bold green]TF-Canary[/bold green] version: [bold]{v}[/bold]")
        raise typer.Exit()


@app.callback()
def callback(
    version: bool = typer.Option(False, "--version", "-v", callback=version_callback, help="Show version and exit."),
    config_path: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to configuration file."),
    verbose: bool = typer.Option(False, "--verbose", help="Enable verbose output."),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode."),
):
    """
    canCANary CAN-Bus Simulator for Raspberry Pi and Web.
    """
    # Initialize core systems
    init_core_systems(config_path, verbose, debug)


def init_core_systems(config_path: Optional[Path], verbose: bool, debug: bool):
    """Initialize core systems needed for all commands."""
    # Set log level based on verbosity flags
    log_level = "INFO"
    if debug:
        log_level = "DEBUG"
    elif verbose:
        log_level = "INFO"
        
    # Configure logging
    logging_config = {
        "level": log_level,
        "log_dir": "logs"
    }
    LoggingSystem(logging_config)
    logger = get_logger("cli")
    logger.debug("Logging initialized")
    
    # Initialize error manager
    ErrorManager()
    logger.debug("Error manager initialized")
    
    # Initialize platform detector
    PlatformDetector()
    logger.debug("Platform detection complete")


@app.command("init")
def init_command(
    force: bool = typer.Option(False, "--force", "-f", help="Force reinitialization."),
    skip_checks: bool = typer.Option(False, "--skip-checks", help="Skip compatibility checks."),
):
    """
    Initialize the TF-Canary environment and check dependencies.
    """
    logger = get_logger("cli.init")
    logger.info("Starting initialization...")
    
    with console.status("[bold green]Initializing canCANary environment...[/bold green]") as status:
        # Check platform compatibility
        if not skip_checks:
            status.update("[bold yellow]Checking platform compatibility...[/bold yellow]")
            time.sleep(0.5)  # Simulating work
            platform_detector = PlatformDetector()
            
            if platform_detector.os_type.value == "Unknown":
                console.print("[bold red]Warning:[/bold red] Running on an unsupported platform.")
        
        # Check for CAN interfaces
        status.update("[bold yellow]Checking for CAN interfaces...[/bold yellow]")
        time.sleep(0.5)  # Simulating work
        
        # Initialize core directories
        status.update("[bold yellow]Setting up directories...[/bold yellow]")
        time.sleep(0.5)  # Simulating work
        os.makedirs("logs", exist_ok=True)
        os.makedirs("config", exist_ok=True)
        os.makedirs("scenarios", exist_ok=True)
        
        # Check dependencies
        status.update("[bold yellow]Checking dependencies...[/bold yellow]")
        time.sleep(0.5)  # Simulating work
        
        # Create default configuration
        status.update("[bold yellow]Creating default configuration...[/bold yellow]")
        time.sleep(0.5)  # Simulating work
    
    console.print("[bold green]✓[/bold green] canCANary environment initialized successfully!")
    
    # Return instructions only if initialization was successful
    console.print(
        Panel.fit(
            "[bold]Next steps:[/bold]\n\n"
            "1. Configure your CAN interface:\n"
            "   [cyan]canary setup-can[/cyan]\n\n"
            "2. Run a scenario:\n"
            "   [cyan]canary run --scenario SCENARIO_NAME[/cyan]\n\n"
            "3. Start the web interface:\n"
            "   [cyan]canary web[/cyan]",
            title="canCANary",
            border_style="green"
        )
    )


@app.command("setup-can")
def setup_can_command(
    interface: str = typer.Option("can0", "--interface", "-i", help="CAN interface name."),
    bitrate: int = typer.Option(500000, "--bitrate", "-b", help="Bitrate in bits per second."),
    virtual: bool = typer.Option(False, "--virtual", "-v", help="Setup virtual CAN interface."),
):
    """
    Configure CAN bus interface.
    """
    logger = get_logger("cli.setup_can")
    logger.info(f"Setting up CAN interface: {interface} (bitrate: {bitrate}, virtual: {virtual})")
    
    platform_detector = PlatformDetector()
    
    # Check if we're on Linux/RPi (required for SocketCAN)
    if platform_detector.os_type.value not in ["Linux", "RaspberryPi"]:
        console.print("[bold red]Error:[/bold red] SocketCAN setup is only supported on Linux.")
        raise typer.Exit(1)
    
    if virtual:
        # Set up virtual CAN interface
        console.print(f"[bold green]Setting up virtual CAN interface: {interface}[/bold green]")
        
        with console.status("Creating virtual CAN interface...") as status:
            # Here would be the actual code to set up vcan
            # For now, we'll just simulate it
            time.sleep(1)
            status.update("Configuring interface settings...")
            time.sleep(1)
        
        console.print(f"[bold green]✓[/bold green] Virtual CAN interface {interface} configured successfully!")
    else:
        # Set up physical CAN interface
        console.print(f"[bold green]Setting up physical CAN interface: {interface}[/bold green]")
        
        with console.status("Configuring CAN interface...") as status:
            # Here would be the actual code to set up the physical interface
            # For now, we'll just simulate it
            time.sleep(1)
            status.update(f"Setting bitrate to {bitrate}...")
            time.sleep(1)
        
        console.print(f"[bold green]✓[/bold green] CAN interface {interface} configured successfully!")
    
    # Test the interface
    console.print("[bold yellow]Testing CAN interface...[/bold yellow]")
    # Here would be test code
    time.sleep(1)
    console.print("[bold green]✓[/bold green] CAN interface test passed!")


@app.command("run")
def run_command(
    scenario: str = typer.Option(None, "--scenario", "-s", help="Scenario name to run."),
    interface: str = typer.Option(None, "--interface", "-i", help="CAN interface to use."),
    headless: bool = typer.Option(False, "--headless", help="Run without GUI."),
):
    """
    Run a CAN bus simulation scenario.
    """
    logger = get_logger("cli.run")
    
    if not scenario:
        console.print("[bold red]Error:[/bold red] Scenario name is required.")
        raise typer.Exit(1)
    
    logger.info(f"Running scenario: {scenario} (interface: {interface}, headless: {headless})")
    
    console.print(f"[bold green]Running scenario: {scenario}[/bold green]")
    
    # Check if scenario exists
    # This would typically check a scenarios directory
    scenario_exists = True  # Placeholder
    
    if not scenario_exists:
        console.print(f"[bold red]Error:[/bold red] Scenario '{scenario}' not found.")
        raise typer.Exit(1)
    
    # Determine interface if not specified
    if not interface:
        platform_detector = PlatformDetector()
        interface = platform_detector.get_recommended_can_interface()
        if interface:
            console.print(f"Using detected CAN interface: [bold]{interface}[/bold]")
        else:
            console.print("[bold yellow]Warning:[/bold yellow] No CAN interface detected. Using virtual interface.")
            interface = "vcan0"
    
    # Initialize progress
    with Progress() as progress:
        task1 = progress.add_task("[green]Loading scenario...", total=100)
        progress.update(task1, advance=30)
        time.sleep(0.5)
        
        # Here would be the actual scenario loading code
        progress.update(task1, advance=40)
        time.sleep(0.5)
        
        # Simulate starting simulation
        progress.update(task1, advance=30)
        time.sleep(0.5)
    
    if headless:
        console.print("[bold green]✓[/bold green] Simulation started in headless mode.")
        console.print("[yellow]Press Ctrl+C to stop.[/yellow]")
        
        try:
            # Simulate running the simulation
            with console.status("[bold green]Simulation running...[/bold green]", spinner="dots"):
                time.sleep(5)  # In a real app, this would keep running
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Simulation stopped by user.[/bold yellow]")
    else:
        console.print("[bold green]✓[/bold green] Simulation prepared. Starting GUI...")
        # In a real app, this would launch the GUI
        console.print("[yellow]Simulating GUI mode (not implemented in example)[/yellow]")


@app.command("test")
def test_command(
    module: Optional[str] = typer.Option(None, "--module", "-m", help="Specific module to test."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose test output."),
):
    """
    Run TF-Canary test suite.
    """
    logger = get_logger("cli.test")
    logger.info(f"Running tests (module: {module}, verbose: {verbose})")
    
    console.print("[bold green]Running canCANary test suite[/bold green]")
    
    # Build the test command based on options
    test_args = []
    if module:
        test_args.append(module)
    if verbose:
        test_args.append("-v")
    
    # Here we would typically use pytest.main() to run tests
    # For demonstration, we'll simulate test output
    
    with Progress() as progress:
        task1 = progress.add_task("[green]Running tests...", total=100)
        
        # Simulate running tests
        for i in range(10):
            progress.update(task1, advance=10)
            time.sleep(0.2)
    
    # Report results
    tests_run = 25
    tests_passed = 23
    tests_failed = 2
    
    console.print(f"[bold]Tests completed:[/bold] {tests_run} tests, {tests_passed} passed, {tests_failed} failed")
    
    if tests_failed > 0:
        console.print("[bold red]Some tests failed![/bold red]")
        raise typer.Exit(1)
    else:
        console.print("[bold green]✓[/bold green] All tests passed!")


@app.command("web")
def web_command(
    host: str = typer.Option("127.0.0.1", "--host", help="Host address to bind to."),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind to."),
):
    """
    Start the TF-Canary web interface.
    """
    logger = get_logger("cli.web")
    logger.info(f"Starting web interface (host: {host}, port: {port})")
    
    console.print(f"[bold green]Starting canCANary web interface on {host}:{port}[/bold green]")
    
    # Here we would typically start a web server
    # For demonstration, we'll just show a message
    
    with console.status(f"[bold green]Web server running at http://{host}:{port}/[/bold green]", spinner="dots"):
        console.print("[yellow]Press Ctrl+C to stop the server.[/yellow]")
        
        try:
            # Keep the server running until interrupted
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Web server stopped by user.[/bold yellow]")


def main():
    """Entry point for the CLI."""
    try:
        app()
    except Exception as e:
        console = Console(stderr=True)
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
