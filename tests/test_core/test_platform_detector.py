"""
Author: TF-Canary Team
Version: 0.1.0
Filename: test_platform_detector.py
Pathname: tests/test_core/test_platform_detector.py

This module contains unit tests for the PlatformDetector class.
"""

import sys
import os
import pytest
from unittest.mock import patch, MagicMock, mock_open
import platform
import subprocess

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

# Import the module to test
from canary.core.platform_detector import (
    PlatformDetector, get_platform_detector,
    OSType, HardwareType
)


@pytest.fixture
def reset_platform_detector():
    """Reset the PlatformDetector singleton between tests."""
    PlatformDetector._instance = None
    yield


class TestPlatformDetector:
    """Test suite for the PlatformDetector class."""
    
    def test_singleton_pattern(self, reset_platform_detector):
        """Test that PlatformDetector follows the singleton pattern."""
        # Create two instances
        detector1 = PlatformDetector()
        detector2 = PlatformDetector()
        
        # Check that they are the same instance
        assert detector1 is detector2
        
        # Also check the global function
        detector3 = get_platform_detector()
        assert detector1 is detector3
    
    @patch('platform.system')
    def test_detect_os_linux(self, mock_system, reset_platform_detector):
        """Test OS detection for Linux."""
        # Mock platform.system to return Linux
        mock_system.return_value = "Linux"
        
        # Also mock _is_raspberry_pi to return False
        with patch.object(PlatformDetector, '_is_raspberry_pi', return_value=False):
            detector = PlatformDetector()
            
            # Check that the OS was detected correctly
            assert detector.os_type == OSType.LINUX
    
    @patch('platform.system')
    def test_detect_os_windows(self, mock_system, reset_platform_detector):
        """Test OS detection for Windows."""
        # Mock platform.system to return Windows
        mock_system.return_value = "Windows"
        
        detector = PlatformDetector()
        
        # Check that the OS was detected correctly
        assert detector.os_type == OSType.WINDOWS
    
    @patch('platform.system')
    def test_detect_os_macos(self, mock_system, reset_platform_detector):
        """Test OS detection for macOS."""
        # Mock platform.system to return Darwin
        mock_system.return_value = "Darwin"
        
        detector = PlatformDetector()
        
        # Check that the OS was detected correctly
        assert detector.os_type == OSType.MACOS
    
    @patch('platform.system')
    def test_detect_os_unknown(self, mock_system, reset_platform_detector):
        """Test OS detection for unknown OS."""
        # Mock platform.system to return something unknown
        mock_system.return_value = "Solaris"
        
        detector = PlatformDetector()
        
        # Check that the OS was detected as unknown
        assert detector.os_type == OSType.UNKNOWN
    
    @patch('platform.system')
    @patch('os.path.exists')
    @patch('builtins.open')
    def test_detect_os_raspberry_pi(self, mock_open_func, mock_exists, mock_system, reset_platform_detector):
        """Test OS detection for Raspberry Pi."""
        # Mock platform.system to return Linux
        mock_system.return_value = "Linux"
        
        # Mock os.path.exists to return True for the model file
        mock_exists.return_value = True
        
        # Mock open to return a file containing "Raspberry Pi"
        mock_open_func.return_value.__enter__.return_value.read.return_value = "Raspberry Pi 4 Model B"
        
        detector = PlatformDetector()
        
        # Check that the OS was detected as Raspberry Pi
        assert detector.os_type == OSType.RASPBERRY_PI
    
    @patch('platform.machine')
    def test_detect_hardware_x86_64(self, mock_machine, reset_platform_detector):
        """Test hardware detection for x86_64."""
        # Mock platform.machine to return x86_64
        mock_machine.return_value = "x86_64"
        
        # Need to mock the OS detection as well
        with patch.object(PlatformDetector, '_detect_os'):
            with patch.object(PlatformDetector, '_detect_can_interfaces'):
                detector = PlatformDetector()
                detector.os_type = OSType.LINUX  # Set manually for test
                
                # Check that the hardware was detected correctly
                assert detector.hardware_type == HardwareType.X86_64
    
    @patch('platform.machine')
    def test_detect_hardware_arm64(self, mock_machine, reset_platform_detector):
        """Test hardware detection for arm64."""
        # Mock platform.machine to return aarch64
        mock_machine.return_value = "aarch64"
        
        # Need to mock the OS detection as well
        with patch.object(PlatformDetector, '_detect_os'):
            with patch.object(PlatformDetector, '_detect_can_interfaces'):
                detector = PlatformDetector()
                detector.os_type = OSType.RASPBERRY_PI  # Set manually for test
                
                # Check that the hardware was detected correctly
                assert detector.hardware_type == HardwareType.ARM64
    
    @patch('platform.machine')
    def test_detect_hardware_arm(self, mock_machine, reset_platform_detector):
        """Test hardware detection for arm."""
        # Mock platform.machine to return armv7l
        mock_machine.return_value = "armv7l"
        
        # Need to mock the OS detection as well
        with patch.object(PlatformDetector, '_detect_os'):
            with patch.object(PlatformDetector, '_detect_can_interfaces'):
                detector = PlatformDetector()
                detector.os_type = OSType.RASPBERRY_PI  # Set manually for test
                
                # Check that the hardware was detected correctly
                assert detector.hardware_type == HardwareType.ARM
    
    @patch('platform.machine')
    def test_detect_hardware_unknown(self, mock_machine, reset_platform_detector):
        """Test hardware detection for unknown architecture."""
        # Mock platform.machine to return something unknown
        mock_machine.return_value = "mips"
        
        # Need to mock the OS detection as well
        with patch.object(PlatformDetector, '_detect_os'):
            with patch.object(PlatformDetector, '_detect_can_interfaces'):
                detector = PlatformDetector()
                detector.os_type = OSType.LINUX  # Set manually for test
                
                # Check that the hardware was detected as unknown
                assert detector.hardware_type == HardwareType.UNKNOWN
    
    @patch('subprocess.run')
    def test_detect_can_interfaces(self, mock_run, reset_platform_detector):
        """Test detection of CAN interfaces."""
        # Mock subprocess.run to return a successful result with sample output
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "1: can0: <NOARP,UP,LOWER_UP> mtu 16 qdisc pfifo_fast state UP \n" + \
                            "2: vcan0: <NOARP,UP,LOWER_UP> mtu 16 qdisc pfifo_fast state UP \n"
        mock_run.return_value = mock_result
        
        # Need to mock the OS and hardware detection
        with patch.object(PlatformDetector, '_detect_os'):
            with patch.object(PlatformDetector, '_detect_hardware'):
                detector = PlatformDetector()
                detector.os_type = OSType.LINUX  # Set manually for test
                
                # Manually call _detect_can_interfaces
                interfaces = detector._detect_can_interfaces()
                
                # Check that the interfaces were detected correctly
                assert len(interfaces) == 2
                assert "can0" in interfaces
                assert "vcan0" in interfaces
    
    def test_is_can_supported(self, reset_platform_detector):
        """Test the is_can_supported method."""
        # Create a detector with mocked parameters
        with patch.object(PlatformDetector, '_detect_os'):
            with patch.object(PlatformDetector, '_detect_hardware'):
                with patch.object(PlatformDetector, '_detect_can_interfaces'):
                    detector = PlatformDetector()
                    
                    # Set up test conditions
                    detector.os_type = OSType.LINUX
                    detector.can_interfaces = ["can0"]
                    
                    # Check that CAN is reported as supported
                    assert detector.is_can_supported() is True
                    
                    # Test with no interfaces but Linux OS
                    detector.can_interfaces = []
                    assert detector.is_can_supported() is True
                    
                    # Test with unsupported OS and no interfaces
                    detector.os_type = OSType.UNKNOWN
                    assert detector.is_can_supported() is False
    
    def test_get_recommended_can_interface(self, reset_platform_detector):
        """Test the get_recommended_can_interface method."""
        # Create a detector with mocked parameters
        with patch.object(PlatformDetector, '_detect_os'):
            with patch.object(PlatformDetector, '_detect_hardware'):
                with patch.object(PlatformDetector, '_detect_can_interfaces'):
                    detector = PlatformDetector()
                    
                    # Test with no interfaces
                    detector.can_interfaces = []
                    assert detector.get_recommended_can_interface() is None
                    
                    # Test with only virtual interfaces
                    detector.can_interfaces = ["vcan0", "vcan1"]
                    assert detector.get_recommended_can_interface() == "vcan0"
                    
                    # Test with both physical and virtual interfaces
                    detector.can_interfaces = ["vcan0", "can0", "can1"]
                    assert detector.get_recommended_can_interface() == "can0"
    
    def test_collect_platform_info(self, reset_platform_detector):
        """Test the _collect_platform_info method."""
        # Create a detector with mocked parameters
        with patch.object(PlatformDetector, '_detect_os'):
            with patch.object(PlatformDetector, '_detect_hardware'):
                with patch.object(PlatformDetector, '_detect_can_interfaces'):
                    detector = PlatformDetector()
                    
                    # Set up test conditions
                    detector.os_type = OSType.LINUX
                    detector.hardware_type = HardwareType.X86_64
                    
                    # Call the method
                    info = detector._collect_platform_info()
                    
                    # Check the returned info
                    assert "os" in info
                    assert "hardware" in info
                    assert "python" in info
                    assert info["os"]["type"] == OSType.LINUX.value
                    assert info["hardware"]["type"] == HardwareType.X86_64.value
