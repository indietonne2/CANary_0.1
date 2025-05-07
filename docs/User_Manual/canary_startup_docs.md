# CANary CAN-Bus Simulator - Startup Guide

**Author**: Thomas Fischer  
**Version**: 0.1.0  
**Last Updated**: May 7, 2025

## Overview

This guide explains how to use the `canary_startup.py` script to initialize, configure, and run the CANary CAN-Bus Simulator. The startup script provides a simple interface for managing the simulator environment, handling dependencies via Pixi, configuring CAN interfaces, and launching different components of the application.

## Prerequisites

Before using the startup script, ensure you have:

1. **Python 3.10+** installed on your system
2. **Git** for cloning the repository (if you haven't already)
3. **sudo privileges** (for Linux users who need to configure physical CAN interfaces)

## Getting Started

### Step 1: Obtain the Startup Script

The `canary_startup.py` script should be located in the root directory of the CANary project. If you don't have it:

```bash
# Clone the repository if you haven't already
git clone https://github.com/indietonne2/CANary_0.1.git
cd CANary_0.1

# Make the startup script executable (Linux/macOS)
chmod +x canary_startup.py
```

### Step 2: Running the Script

You can run the script in two ways:

#### Interactive Mode

For an easy-to-use menu interface:

```bash
./canary_startup.py
# or
python canary_startup.py
```

This will display a menu with the following options:
1. Setup environment
2. Setup CAN interface
3. Run simulation
4. Run web interface
5. Run tests
6. Configure settings
7. Exit

#### Command Line Mode

For direct execution or automation:

```bash
# Initialize the environment
python canary_startup.py --init

# Set up CAN interface
python canary_startup.py --setup-can

# Run the simulation
python canary_startup.py --run

# Start the web interface
python canary_startup.py --web

# Run tests
python canary_startup.py --test
```

## Configuration Options

The startup script supports the following command-line options:

| Option | Description |
|--------|-------------|
| `--init` | Initialize the environment |
| `--setup-can` | Set up CAN interface |
| `--run` | Run the simulation |
| `--web` | Start the web interface |
| `--test` | Run tests |
| `--virtual` | Use virtual CAN interface |
| `--interface [NAME]` | Specify CAN interface name (default: vcan0) |
| `--bitrate [BPS]` | Set CAN bitrate in bits per second (default: 500000) |
| `--scenario [NAME]` | Specify scenario to run (default: default) |
| `--headless` | Run in headless mode without GUI |

### Examples

```bash
# Run with a specific scenario
python canary_startup.py --run --scenario automotive_diagnostics

# Setup a physical CAN interface with custom bitrate
python canary_startup.py --setup-can --interface can0 --bitrate 250000

# Run in headless mode
python canary_startup.py --run --headless
```

## Environment Setup

When you run the environment setup (via the interactive menu or `--init` flag), the script will:

1. Check if Pixi is installed (and provide instructions if it's not)
2. Create necessary directories (logs, config, scenarios)
3. Install dependencies using Pixi
4. Configure the application for first use

## CAN Interface Setup

### Virtual CAN Interfaces

For development and testing, you can use virtual CAN interfaces:

```bash
python canary_startup.py --setup-can --virtual --interface vcan0
```

This will:
1. Load the vcan kernel module
2. Create a virtual CAN interface named vcan0
3. Bring the interface up

### Physical CAN Interfaces

For hardware testing with real CAN devices:

```bash
python canary_startup.py --setup-can --interface can0 --bitrate 500000
```

This will:
1. Configure the physical CAN interface (can0)
2. Set the specified bitrate
3. Bring the interface up

**Note**: Setting up physical CAN interfaces requires sudo privileges on Linux.

## Saving Configuration

The script saves your configuration settings in `config/starter_config.json`. When you run the script next time, it will use these saved settings as defaults.

You can update these settings through the interactive menu (Option 6: Configure settings).

## Troubleshooting

### Pixi Not Found

If the script cannot find Pixi, it will provide installation instructions. Follow these instructions to install Pixi, then run the script again.

### CAN Interface Issues

On Linux, if you encounter issues with CAN interfaces:

1. Ensure you have the necessary kernel modules:
   ```bash
   sudo modprobe can
   sudo modprobe can_raw
   sudo modprobe vcan  # For virtual CAN
   ```

2. Check if the interface exists:
   ```bash
   ip link show
   ```

3. For physical interfaces, ensure your CAN hardware is properly connected and supported.

### Dependency Issues

If you encounter issues with dependencies:

1. Try running the environment setup again:
   ```bash
   python canary_startup.py --init
   ```

2. Check the Pixi logs for more detailed information.

## Advanced Usage

### Integrating with Other Scripts

You can integrate the startup script with other automation tools:

```bash
# Example: Set up environment, then run tests
python canary_startup.py --init && python canary_startup.py --test

# Example: Daily test automation script
#!/bin/bash
cd /path/to/canary
./canary_startup.py --setup-can --virtual
./canary_startup.py --run --scenario regression_tests --headless
```

## Next Steps

After setting up and starting CANary, you can:

1. Explore the built-in scenarios in the scenarios directory
2. Create your own CAN bus simulation scenarios
3. Use the web interface to monitor and interact with the CAN bus
4. Extend the functionality with custom plugins

For more detailed information, refer to the main CANary documentation.
