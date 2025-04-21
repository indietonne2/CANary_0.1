"""
Author: TF-Canary Team
Version: 0.1.0
Filename: test_venv_setup.py
Pathname: tests/test_env/test_venv_setup.py

Tests for the VenvSetup class in the TF-Canary CAN-Bus Simulator.
"""

import os
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the module to test
from canary.env.venv_setup import VenvSetup


@pytest.mark.unit
class TestVenvSetup:
    """Tests for the VenvSetup class."""
    
    def test_init(self, temp_dir, disable_logging):
        """Test initialization of VenvSetup."""
        # Test with default path
        venv_setup = VenvSetup()
        assert venv_setup.venv_path == Path(".venv")
        
        # Test with custom path
        test_path = temp_dir / "test_venv"
        venv_setup = VenvSetup(test_path)
        assert venv_setup.venv_path == test_path
    
    def test_get_python_path(self, temp_dir, disable_logging):
        """Test get_python_path method."""
        venv_setup = VenvSetup(temp_dir / "test_venv")
        
        # Test on Windows
        with patch('os.name', 'nt'):
            python_path = venv_setup.get_python_path()
            assert python_path == temp_dir / "test_venv" / "Scripts" / "python.exe"
        
        # Test on Unix
        with patch('os.name', 'posix'):
            python_path = venv_setup.get_python_path()
            assert python_path == temp_dir / "test_venv" / "bin" / "python"
    
    def test_get_pip_path(self, temp_dir, disable_logging):
        """Test get_pip_path method."""
        venv_setup = VenvSetup(temp_dir / "test_venv")
        
        # Test on Windows
        with patch('os.name', 'nt'):
            pip_path = venv_setup.get_pip_path()
            assert pip_path == temp_dir / "test_venv" / "Scripts" / "pip.exe"
        
        # Test on Unix
        with patch('os.name', 'posix'):
            pip_path = venv_setup.get_pip_path()
            assert pip_path == temp_dir / "test_venv" / "bin" / "pip"
    
    def test_is_venv_activated(self, disable_logging):
        """Test is_venv_activated method."""
        venv_setup = VenvSetup()
        
        # Test not activated
        with patch.object(sys, 'prefix', 'prefix'), \
             patch.object(sys, 'base_prefix', 'prefix'):
            assert not venv_setup.is_venv_activated()
        
        # Test activated with base_prefix
        with patch.object(sys, 'prefix', 'prefix'), \
             patch.object(sys, 'base_prefix', 'different_prefix'):
            assert venv_setup.is_venv_activated()
        
        # Test activated with real_prefix (older Python versions)
        with patch.object(sys, 'real_prefix', 'real_prefix', create=True):
            assert venv_setup.is_venv_activated()
    
    def test_create_venv(self, temp_dir, disable_logging, mock_error_manager):
        """Test create_venv method."""
        venv_path = temp_dir / "test_venv"
        venv_setup = VenvSetup(venv_path)
        
        # Test successful creation
        with patch('venv.create') as mock_create:
            assert venv_setup.create_venv()
            mock_create.assert_called_once_with(
                env_dir=venv_path,
                system_site_packages=False,
                clear=False,
                with_pip=True,
                prompt="canary"
            )
        
        # Test with existing venv
        with patch.object(Path, 'exists', return_value=True), \
             patch('venv.create') as mock_create:
            assert venv_setup.create_venv()
            mock_create.assert_not_called()
        
        # Test with existing venv and clear=True
        with patch.object(Path, 'exists', return_value=True), \
             patch('shutil.rmtree') as mock_rmtree, \
             patch('venv.create') as mock_create:
            assert venv_setup.create_venv(clear=True)
            mock_rmtree.assert_called_once_with(venv_path)
            mock_create.assert_called_once()
        
        # Test with exception
        with patch('venv.create', side_effect=Exception("Test error")), \
             patch('shutil.rmtree'):
            assert not venv_setup.create_venv()
            assert len(mock_error_manager.error_log) == 1
    
    def test_validate_venv(self, temp_dir, disable_logging):
        """Test validate_venv method."""
        venv_path = temp_dir / "test_venv"
        venv_setup = VenvSetup(venv_path)
        
        # Test with non-existent venv
        with patch.object(Path, 'exists', return_value=False):
            assert not venv_setup.validate_venv()
        
        # Test with existent venv but missing Python
        with patch.object(Path, 'exists', side_effect=[True, False]):
            assert not venv_setup.validate_venv()
        
        # Test with existent venv, Python but missing pip
        with patch.object(Path, 'exists', side_effect=[True, True, False]):
            assert not venv_setup.validate_venv()
        
        # Test successful validation
        with patch.object(Path, 'exists', return_value=True), \
             patch('subprocess.run') as mock_run:
            mock_process = MagicMock()
            mock_process.stdout = "Python 3.10.0"
            mock_run.return_value = mock_process
            assert venv_setup.validate_venv()
        
        # Test with subprocess error
        with patch.object(Path, 'exists', return_value=True), \
             patch('subprocess.run', side_effect=Exception("Test error")):
            assert not venv_setup.validate_venv()
    
    def test_install_requirements(self, temp_dir, disable_logging, mock_error_manager):
        """Test install_requirements method."""
        venv_path = temp_dir / "test_venv"
        venv_setup = VenvSetup(venv_path)
        
        # Create a test requirements file
        req_path = temp_dir / "requirements.txt"
        req_path.write_text("pytest==7.0.0\ntyper==0.9.0\n")
        
        # Test with non-existent requirements file
        non_existent_path = temp_dir / "non_existent.txt"
        assert not venv_setup.install_requirements(non_existent_path)
        assert len(mock_error_manager.error_log) == 1
        mock_error_manager.error_log.clear()
        
        # Test with missing pip
        with patch.object(Path, 'exists', side_effect=[True, False]):
            assert not venv_setup.install_requirements(req_path)
            assert len(mock_error_manager.error_log) == 1
        mock_error_manager.error_log.clear()
        
        # Test successful installation
        with patch.object(Path, 'exists', return_value=True), \
             patch('subprocess.run') as mock_run:
            mock_process = MagicMock()
            mock_process.stdout = "Successfully installed pytest-7.0.0 typer-0.9.0"
            mock_process.stderr = ""
            mock_run.return_value = mock_process
            assert venv_setup.install_requirements(req_path)
        
        # Test with subprocess error
        with patch.object(Path, 'exists', return_value=True), \
             patch('subprocess.run', side_effect=Exception("Test error")):
            assert not venv_setup.install_requirements(req_path)
            assert len(mock_error_manager.error_log) == 1
    
    def test_get_activation_command(self, temp_dir, disable_logging):
        """Test get_activation_command method."""
        venv_path = temp_dir / "test_venv"
        venv_setup = VenvSetup(venv_path)
        
        # Test on Windows
        with patch('os.name', 'nt'):
            cmd = venv_setup.get_activation_command()
            assert cmd == f"{venv_path}\\Scripts\\activate.bat"
        
        # Test on Unix
        with patch('os.name', 'posix'):
            cmd = venv_setup.get_activation_command()
            assert cmd == f"source {venv_path}/bin/activate"
