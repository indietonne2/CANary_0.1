Getting Started with CANary
CANary is a CAN-Bus Simulator for Raspberry Pi and Web platforms. This guide will help you get up and running quickly.
Prerequisites

Python 3.10 or later
Git (for cloning the repository)

Installation

Clone the repository:
bashgit clone https://github.com/indietonne2/CANary_0.1.git
cd CANary_0.1

(Optional) Create a virtual environment:
bashpython -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install dependencies (future step):
bash# Coming soon: pip install -r requirements.txt


Running CANary
CANary can be run as a Python module using the python -m syntax:
bash# Show available commands
python -m src --help

# Initialize the simulator
python -m src init --mode default

# List available scenarios
python -m src list

# Run a specific scenario
python -m src run demo_scenario_1

# Show version information
python -m src version
Operation Modes
CANary supports three modes of operation:

Default - Standard operation with default settings
User - Custom user settings that persist between sessions
Workshop - "Kiosk" mode where settings don't persist

Specify the mode during initialization:
bashpython -m src init --mode workshop
Project Structure
The CANary project follows a modular architecture:
CANary_0.1/
├── docs/                # Documentation
│   └── Architecture/    # Architecture diagrams and specifications
├── src/                 # Source code
│   ├── __init__.py      # Package initialization
│   ├── __main__.py      # Entry point when run as a module
│   ├── cli.py           # Command-line interface
│   └── ...              # Other module files
└── tests/               # Test suite
