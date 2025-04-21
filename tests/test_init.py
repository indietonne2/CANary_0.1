"""
Author: Thomas Fischer
Version: 0.1.0
Filename: test_init.py
Pathname: tests/test_init.py

Tests for the canCANary package initialization and structure.
"""

import pytest
import importlib.util
from pathlib import Path


@pytest.mark.unit
class TestPackageStructure:
    """Tests for the package structure."""
    
    def test_package_init(self):
        """Test that the package can be imported and has a version."""
        import canary
        assert hasattr(canary, '__version__')
        assert isinstance(canary.__version__, str)
    
    def test_core_modules_importable(self):
        """Test that core modules can be imported."""
        modules = [
            'canary.core.logging_system',
            'canary.core.error_manager',
            'canary.core.platform_detector'
        ]
        
        for module_name in modules:
            assert importlib.util.find_spec(module_name) is not None
            module = importlib.import_module(module_name)
            assert module is not None
    
    def test_cli_importable(self):
        """Test that CLI module can be imported."""
        modules = [
            'canary.cli',
            'canary.cli.cli'
        ]
        
        for module_name in modules:
            assert importlib.util.find_spec(module_name) is not None
            module = importlib.import_module(module_name)
            assert module is not None
    
    def test_env_modules_importable(self):
        """Test that environment modules can be imported."""
        modules = [
            'canary.env.venv_setup',
            'canary.env.pixi_environment'
        ]
        
        for module_name in modules:
            assert importlib.util.find_spec(module_name) is not None
            module = importlib.import_module(module_name)
            assert module is not None
    
    def test_testing_modules_importable(self):
        """Test that testing modules can be imported."""
        modules = [
            'canary.testing.test_runner'
        ]
        
        for module_name in modules:
            assert importlib.util.find_spec(module_name) is not None
            module = importlib.import_module(module_name)
            assert module is not None
