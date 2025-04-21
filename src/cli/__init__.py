"""
Command Line Interface for the canCANary CAN-Bus Simulator.

This package provides the CLI entry points and commands for interacting
with the simulator from the terminal.
"""

# Import key modules to make them available at package level
try:
    from .cli import app, main
except ImportError:
    # Handle situation where implementation files might not exist yet
    pass
