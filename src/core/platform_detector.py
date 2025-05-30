"""
Author: Thomas Fischer
Version: 0.1.1
Filename: platform_detector.py
Pathname: src/core/platform_detector.py

This module implements the platform detection functionality for canCANary CAN-Bus Simulator.
It detects the operating system, hardware details, and available CAN interfaces.

Classes:
    OSType: Enum for supported operating systems
        - LINUX, WINDOWS, MACOS, RASPBERRY_PI, UNKNOWN
    HardwareType: Enum for supported hardware architectures
        - X86_64, ARM, ARM64, UNKNOWN
    PlatformDetector: Singleton class for platform detection
        - OS and hardware detection
        - CAN interface discovery
        - Platform-specific capabilities
"""

import platform
import os
import sys
import re
import subprocess
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
import json

# Local imports
try:
    from .logging_system import get_logger
except ImportError:
    # Fallback for standalone usage or when logging_system is not available
    import logging
    def get_logger(name):
        logger = logging.getLogger(name)
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger


class OSType(Enum):
    """Enumeration of supported operating systems."""
    LINUX = "Linux"
    WINDOWS = "Windows"
    MACOS = "Darwin"
    RASPBERRY_PI = "RaspberryPi"  # Special case of Linux
    UNKNOWN = "Unknown"


class HardwareType(Enum):
    """Enumeration of supported hardware platforms."""
    X86_64 = "x86_64"
    ARM = "arm"
    ARM64 = "aarch64"
    UNKNOWN = "unknown"


class PlatformDetector:
    """
    Detects the platform details needed for canCANary's operation.

    This includes OS type, hardware architecture, available CAN interfaces,
    and platform-specific capabilities.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(PlatformDetector, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the platform detector."""
        if self._initialized:
            return

        self.logger = get_logger("platform_detector")

        # Detect and store platform details
        self.os_type = self._detect_os()
        self.hardware_type = self._detect_hardware()
        self.can_interfaces = self._detect_can_interfaces()
        self.platform_info = self._collect_platform_info()

        self._initialized = True

        # Log platform information
        self.logger.info(f"Detected platform: {self.os_type.value} on {self.hardware_type.value}")
        self.logger.debug(f"Platform details: {json.dumps(self.platform_info, indent=2)}")
        if self.can_interfaces:
            self.logger.info(f"Detected CAN interfaces: {', '.join(self.can_interfaces)}")
        else:
            self.logger.warning("No CAN interfaces detected")

    def _detect_os(self) -> OSType:
        """
        Detect the operating system.

        Returns:
            OSType enum value
        """
        system = platform.system()

        if system == "Linux":
            # Check if we're on a Raspberry Pi
            if self._is_raspberry_pi():
                return OSType.RASPBERRY_PI
            return OSType.LINUX
        elif system == "Windows":
            return OSType.WINDOWS
        elif system == "Darwin":
            return OSType.MACOS
        else:
            self.logger.warning(f"Unknown operating system: {system}")
            return OSType.UNKNOWN

    def _is_raspberry_pi(self) -> bool:
        """
        Check if we're running on a Raspberry Pi.

        Returns:
            True if the system is a Raspberry Pi
        """
        # Method 1: Check for Raspberry Pi model file
        model_path = "/proc/device-tree/model"
        if os.path.exists(model_path):
            try:
                with open(model_path, 'r') as f:
                    model = f.read()
                    if "Raspberry Pi" in model:
                        return True
            except Exception as e:
                self.logger.debug(f"Error reading {model_path}: {e}")

        # Method 2: Check CPU info
        try:
            with open("/proc/cpuinfo", 'r') as f:
                cpuinfo = f.read()
                if "BCM" in cpuinfo or "Raspberry Pi" in cpuinfo:
                    return True
        except Exception:
            pass

        # Method 3: Check for Raspberry Pi-specific directories
        pi_specific_dirs = [
            "/opt/vc",
            "/sys/firmware/devicetree/base/model"
        ]
        for directory in pi_specific_dirs:
            if os.path.exists(directory):
                return True

        return False

    def _detect_hardware(self) -> HardwareType:
        """
        Detect the hardware architecture.

        Returns:
            HardwareType enum value
        """
        machine = platform.machine().lower()

        if machine in ["x86_64", "amd64"]:
            return HardwareType.X86_64
        elif machine in ["arm64", "aarch64"]:
            return HardwareType.ARM64
        elif machine.startswith("arm"):
            return HardwareType.ARM
        else:
            self.logger.warning(f"Unknown hardware architecture: {machine}")
            return HardwareType.UNKNOWN

    def _detect_can_interfaces(self) -> List[str]:
        """
        Detect available CAN interfaces on the system.

        Returns:
            List of CAN interface names
        """
        interfaces = []

        # Check for SocketCAN interfaces on Linux
        if self.os_type in [OSType.LINUX, OSType.RASPBERRY_PI]:
            try:
                # Run ip link show to list network interfaces
                result = subprocess.run(
                    ["ip", "-d", "link", "show"],
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0:
                    for line in result.stdout.splitlines():
                        if "can" in line.lower():
                            # Extract interface name
                            match = re.search(r"^\d+:\s+([^:@]+)", line)
                            if match:
                                interfaces.append(match.group(1).strip())
            except FileNotFoundError:
                # 'ip' command not found, try different approach
                self.logger.debug("'ip' command not found, trying alternative methods")
                try:
                    # Check /proc/net/dev for network interfaces
                    with open("/proc/net/dev", "r") as f:
                        for line in f:
                            if "can" in line.lower():
                                # Extract interface name
                                parts = line.strip().split(":")
                                if len(parts) >= 2:
                                    interfaces.append(parts[0].strip())
                except Exception as e:
                    self.logger.warning(f"Error checking /proc/net/dev for CAN interfaces: {e}")
            except Exception as e:
                self.logger.warning(f"Error detecting CAN interfaces: {e}")

        # Check for CAN adapters on macOS
        elif self.os_type == OSType.MACOS:
            try:
                # Check for known USB CAN adapters
                result = subprocess.run(
                    ["system_profiler", "SPUSBDataType"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    can_adapters = []
                    for line in result.stdout.splitlines():
                        # Look for common CAN adapter manufacturers
                        if any(vendor in line for vendor in ["PEAK-System", "Kvaser", "PCAN", "Vector", "National Instruments"]):
                            can_adapters.append(line.strip())

                    if can_adapters:
                        self.logger.info(f"Found potential CAN adapters: {can_adapters}")
                        # For macOS, we don't have real interface names like Linux
                        # So we'll just use generic names
                        interfaces = [f"can{i}" for i in range(len(can_adapters))]
            except Exception as e:
                self.logger.warning(f"Error detecting CAN adapters on macOS: {e}")

        # Check for CAN adapters on Windows
        elif self.os_type == OSType.WINDOWS:
            # For Windows, we'll check in the device manager
            try:
                result = subprocess.run(
                    ["wmic", "path", "Win32_PnPEntity", "get", "Name"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    can_adapters = []
                    for line in result.stdout.splitlines():
                        # Look for common CAN adapter names
                        if any(adapter in line for adapter in ["CAN", "PCAN", "Kvaser", "Vector"]):
                            can_adapters.append(line.strip())

                    if can_adapters:
                        self.logger.info(f"Found potential CAN adapters: {can_adapters}")
                        # For Windows, we'll use generic names
                        interfaces = [f"can{i}" for i in range(len(can_adapters))]
            except Exception as e:
                self.logger.warning(f"Error detecting CAN adapters on Windows: {e}")

        return interfaces

    def _collect_platform_info(self) -> Dict[str, Any]:
        """
        Collect detailed platform information.

        Returns:
            Dictionary with platform details
        """
        info = {
            "os": {
                "type": self.os_type.value,
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version()
            },
            "hardware": {
                "type": self.hardware_type.value,
                "machine": platform.machine(),
                "processor": platform.processor()
            },
            "python": {
                "version": platform.python_version(),
                "implementation": platform.python_implementation(),
                "compiler": platform.python_compiler()
            }
        }

        # Add Raspberry Pi specific information
        if self.os_type == OSType.RASPBERRY_PI:
            rpi_info = self._get_raspberry_pi_info()
            if rpi_info:
                info["raspberry_pi"] = rpi_info

        # Add macOS specific information
        if self.os_type == OSType.MACOS:
            mac_info = self._get_macos_info()
            if mac_info:
                info["macos"] = mac_info

        return info

    def _get_raspberry_pi_info(self) -> Optional[Dict[str, Any]]:
        """
        Get Raspberry Pi specific information.

        Returns:
            Dictionary with Raspberry Pi details or None if not a Pi
        """
        if not self._is_raspberry_pi():
            return None

        info = {}

        # Try to get the model
        try:
            with open("/proc/device-tree/model", 'r') as f:
                info["model"] = f.read().strip('\0')
        except Exception:
            info["model"] = "Unknown Raspberry Pi"

        # Try to get the SoC temperature
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", 'r') as f:
                temp = int(f.read().strip()) / 1000.0
                info["temperature"] = temp
        except Exception:
            pass

        # Try to get GPIO information
        gpio_present = os.path.exists("/sys/class/gpio")
        info["gpio_present"] = gpio_present

        # Check for SPI
        spi_present = os.path.exists("/dev/spidev0.0") or os.path.exists("/dev/spidev0.1")
        info["spi_present"] = spi_present

        # Check for I2C
        i2c_present = os.path.exists("/dev/i2c-1")
        info["i2c_present"] = i2c_present

        return info

    def _get_macos_info(self) -> Dict[str, Any]:
        """
        Get macOS specific information.

        Returns:
            Dictionary with macOS details
        """
        info = {}

        # Try to get macOS version details
        try:
            result = subprocess.run(
                ["sw_vers"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if ":" in line:
                        key, value = line.split(":", 1)
                        key = key.strip().lower().replace(" ", "_")
                        value = value.strip()
                        info[key] = value
        except Exception as e:
            self.logger.debug(f"Error getting macOS system details: {e}")

        # Check for Homebrew (common on macOS)
        try:
            result = subprocess.run(
                ["which", "brew"],
                capture_output=True,
                text=True
            )
            info["homebrew_present"] = result.returncode == 0
        except Exception:
            info["homebrew_present"] = False

        # Check if this is an Apple Silicon Mac
        info["is_apple_silicon"] = self.hardware_type == HardwareType.ARM64

        return info

    def is_can_supported(self) -> bool:
        """
        Check if CAN bus is supported on this platform.

        Returns:
            True if CAN is supported
        """
        # CAN is supported if interfaces are detected or if we're on Linux/RPi
        if self.can_interfaces:
            return True

        # On Linux, SocketCAN might be available but not configured
        if self.os_type in [OSType.LINUX, OSType.RASPBERRY_PI]:
            return True

        # On Windows, check for Peak CAN drivers
        if self.os_type == OSType.WINDOWS:
            try:
                # Check for Peak CAN driver files
                peak_paths = [
                    os.path.exists("C:\\Windows\\System32\\PCANBasic.dll"),
                    os.path.exists("C:\\Program Files\\PEAK-System\\PCAN-Basic API\\"),
                    os.path.exists("C:\\Program Files (x86)\\PEAK-System\\PCAN-Basic API\\")
                ]
                if any(peak_paths):
                    return True
            except Exception:
                pass

        # On macOS, check for common CAN tools
        if self.os_type == OSType.MACOS:
            try:
                # Check for common CAN tools that might be installed
                tools = ["candump", "cansend", "slcand"]
                for tool in tools:
                    result = subprocess.run(["which", tool], capture_output=True, text=True)
                    if result.returncode == 0:
                        return True
            except Exception:
                pass

        return False

    def get_recommended_can_interface(self) -> Optional[str]:
        """
        Get the recommended CAN interface for this platform.

        Returns:
            Interface name or None if no recommendation
        """
        if not self.can_interfaces:
            # No interfaces detected, suggest default based on OS
            if self.os_type in [OSType.LINUX, OSType.RASPBERRY_PI]:
                return "vcan0"  # Suggest virtual CAN as fallback
            else:
                return None

        # Prefer physical interfaces (can0, can1) over virtual (vcan0)
        physical_interfaces = [i for i in self.can_interfaces if not i.startswith('v')]
        if physical_interfaces:
            return physical_interfaces[0]

        # Fall back to any interface
        return self.can_interfaces[0]

    def get_platform_summary(self) -> str:
        """
        Get a human-readable summary of the platform.

        Returns:
            String with platform summary
        """
        summary = [
            f"OS: {self.os_type.value}",
            f"Hardware: {self.hardware_type.value}"
        ]

        if self.os_type == OSType.RASPBERRY_PI and "raspberry_pi" in self.platform_info:
            rpi_info = self.platform_info["raspberry_pi"]
            if "model" in rpi_info:
                summary.append(f"Model: {rpi_info['model']}")
            if "temperature" in rpi_info:
                summary.append(f"Temperature: {rpi_info['temperature']}°C")

        if self.os_type == OSType.MACOS and "macos" in self.platform_info:
            mac_info = self.platform_info["macos"]
            if "product_version" in mac_info:
                summary.append(f"Version: {mac_info['product_version']}")
            if "is_apple_silicon" in mac_info and mac_info["is_apple_silicon"]:
                summary.append("Processor: Apple Silicon")

        summary.append(f"CAN Supported: {self.is_can_supported()}")
        if self.can_interfaces:
            summary.append(f"CAN Interfaces: {', '.join(self.can_interfaces)}")

        return "\n".join(summary)


# Get the global detector instance
def get_platform_detector() -> PlatformDetector:
    """
    Get the global PlatformDetector instance.

    Returns:
        The singleton PlatformDetector instance
    """
    return PlatformDetector()


# Test the module directly
if __name__ == "__main__":
    detector = get_platform_detector()

    print("\n=== Platform Detection Results ===")
    print(detector.get_platform_summary())

    print("\nDetailed platform information:")
    print(json.dumps(detector.platform_info, indent=2))

    print("\nCAN Interface Information:")
    print(f"CAN supported: {detector.is_can_supported()}")
    print(f"Detected interfaces: {detector.can_interfaces}")
    print(f"Recommended interface: {detector.get_recommended_can_interface()}")