"""
Author: TF-Canary Team
Version: 0.1.0
Filename: conftest.py
Pathname: tests/conftest.py

Common test fixtures for TF-Canary CAN-Bus Simulator tests.
"""

import os
import sys
import tempfile
import pytest
from pathlib import Path

# Add the src directory to sys.path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test artifacts."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def disable_logging(monkeypatch):
    """Disable logging for tests."""
    def mock_get_logger(*args, **kwargs):
        mock_logger = type('MockLogger', (), {
            'debug': lambda *a, **kw: None,
            'info': lambda *a, **kw: None,
            'warning': lambda *a, **kw: None,
            'error': lambda *a, **kw: None,
            'critical': lambda *a, **kw: None,
        })()
        return mock_logger
    
    # Patch the get_logger function
    monkeypatch.setattr('canary.core.logging_system.get_logger', mock_get_logger)


@pytest.fixture
def mock_error_manager(monkeypatch):
    """Mock the error manager for tests."""
    class MockErrorManager:
        def __init__(self):
            self.error_log = []
        
        def handle_error(self, error):
            self.error_log.append(error)
            return True
    
    mock_instance = MockErrorManager()
    
    def mock_get_error_manager():
        return mock_instance
    
    monkeypatch.setattr('canary.core.error_manager.get_error_manager', mock_get_error_manager)
    
    return mock_instance


@pytest.fixture
def mock_platform_detector(monkeypatch):
    """Mock the platform detector for tests."""
    class MockPlatformDetector:
        def __init__(self):
            from canary.core.platform_detector import OSType, HardwareType
            self.os_type = OSType.LINUX
            self.hardware_type = HardwareType.X86_64
            self.can_interfaces = ["vcan0", "can0"]
            self.platform_info = {
                "os": {
                    "type": "Linux",
                    "version": "Test"
                },
                "hardware": {
                    "type": "x86_64",
                    "machine": "Test"
                }
            }
        
        def is_can_supported(self):
            return True
        
        def get_recommended_can_interface(self):
            return "can0"
    
    mock_instance = MockPlatformDetector()
    
    def mock_get_platform_detector():
        return mock_instance
    
    monkeypatch.setattr('canary.core.platform_detector.get_platform_detector', 
                       mock_get_platform_detector)
    
    return mock_instance
