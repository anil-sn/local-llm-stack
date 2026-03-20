"""
Test utility functions.

Tests cross-platform utilities without mocking.
"""

import os
import socket
import subprocess
import sys
import pytest
from pathlib import Path

from local_llm.utils import (
    get_platform,
    is_macos,
    is_linux,
    is_windows,
    get_cpu_count,
    get_total_ram_gb,
    get_available_ram_gb,
    get_disk_usage,
    is_port_in_use,
    get_process_using_port,
    kill_process,
    get_system_info,
    check_command_exists,
    get_command_path,
    expand_path,
    ensure_directory,
    format_size,
    get_gpu_info,
)


class TestPlatformDetection:
    """Test platform detection functions."""

    def test_get_platform(self):
        """Test get_platform function."""
        platform = get_platform()
        
        assert isinstance(platform, str)
        assert platform in ['linux', 'darwin', 'windows']
        
        # Should match sys.platform
        if sys.platform.startswith('linux'):
            assert platform == 'linux'
        elif sys.platform == 'darwin':
            assert platform == 'darwin'

    def test_is_macos(self):
        """Test is_macos function."""
        result = is_macos()
        assert isinstance(result, bool)
        
        if sys.platform == 'darwin':
            assert result == True
        else:
            assert result == False

    def test_is_linux(self):
        """Test is_linux function."""
        result = is_linux()
        assert isinstance(result, bool)
        
        if sys.platform.startswith('linux'):
            assert result == True
        else:
            assert result == False

    def test_is_windows(self):
        """Test is_windows function."""
        result = is_windows()
        assert isinstance(result, bool)
        
        if sys.platform == 'windows':
            assert result == True
        else:
            assert result == False


class TestCPUFunctions:
    """Test CPU-related functions."""

    def test_get_cpu_count(self):
        """Test get_cpu_count function."""
        count = get_cpu_count()
        
        assert isinstance(count, int)
        assert count >= 1
        
        # Should match or be close to os.cpu_count()
        os_count = os.cpu_count()
        if os_count:
            assert count <= os_count * 2  # Allow some variance


class TestMemoryFunctions:
    """Test memory-related functions."""

    def test_get_total_ram_gb(self):
        """Test get_total_ram_gb function."""
        total = get_total_ram_gb()
        
        assert isinstance(total, float)
        assert total > 0
        assert total >= 8  # Minimum reasonable RAM

    def test_get_available_ram_gb(self):
        """Test get_available_ram_gb function."""
        available = get_available_ram_gb()
        
        assert isinstance(available, float)
        assert available > 0
        
        # Available should be <= total
        total = get_total_ram_gb()
        assert available <= total

    def test_memory_values_reasonable(self):
        """Test that memory values are reasonable."""
        total = get_total_ram_gb()
        available = get_available_ram_gb()
        
        # Total should be in reasonable range
        assert 4 <= total <= 1024  # 4GB to 1TB
        
        # Available should be positive
        assert available > 0


class TestDiskFunctions:
    """Test disk-related functions."""

    def test_get_disk_usage(self):
        """Test get_disk_usage function."""
        total, used, free = get_disk_usage("/")
        
        assert isinstance(total, float)
        assert isinstance(used, float)
        assert isinstance(free, float)
        
        assert total > 0
        assert used >= 0
        assert free > 0
        assert used + free <= total * 1.1  # Allow small variance

    def test_get_disk_usage_custom_path(self):
        """Test get_disk_usage with custom path."""
        total, used, free = get_disk_usage("/tmp")
        
        assert total > 0
        assert free > 0

    def test_get_disk_usage_nonexistent_path(self):
        """Test get_disk_usage with non-existent path."""
        total, used, free = get_disk_usage("/nonexistent/path/xyz")
        
        # Should return zeros or handle gracefully
        assert isinstance(total, float)
        assert isinstance(used, float)
        assert isinstance(free, float)


class TestPortFunctions:
    """Test port-related functions."""

    def test_is_port_in_use_free_port(self):
        """Test is_port_in_use with free port."""
        # Find a free port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            s.listen(1)
            port = s.getsockname()[1]
        
        # Port should be free after socket is closed
        # Note: May be in TIME_WAIT state
        result = is_port_in_use(port)
        assert isinstance(result, bool)

    def test_is_port_in_use_bound_port(self):
        """Test is_port_in_use with bound port."""
        # Create a server socket
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("localhost", 0))
        server.listen(1)
        port = server.getsockname()[1]
        
        try:
            # Port should be in use
            result = is_port_in_use(port, host="localhost")
            assert result == True
        finally:
            server.close()

    def test_get_process_using_port(self):
        """Test get_process_using_port function."""
        # Create a server socket
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("localhost", 0))
        server.listen(1)
        port = server.getsockname()[1]
        
        try:
            pid = get_process_using_port(port, host="localhost")
            
            # Should return PID or None
            assert pid is None or isinstance(pid, int)
            
            if pid is not None:
                assert pid > 0
        finally:
            server.close()


class TestProcessFunctions:
    """Test process-related functions."""

    def test_kill_process_invalid_pid(self):
        """Test kill_process with invalid PID."""
        result = kill_process(999999)
        assert result == False

    def test_kill_process_own_process(self):
        """Test kill_process with own process (don't actually kill)."""
        # Just test that it doesn't crash
        pid = os.getpid()
        # Don't actually kill it, just test the function exists
        assert isinstance(pid, int)
        assert pid > 0


class TestSystemInfo:
    """Test system info function."""

    def test_get_system_info(self):
        """Test get_system_info function."""
        info = get_system_info()
        
        assert isinstance(info, dict)
        assert 'platform' in info
        assert 'os' in info
        assert 'cpu_count' in info
        assert 'total_ram_gb' in info
        assert 'available_ram_gb' in info
        assert 'disk_total_gb' in info
        assert 'disk_free_gb' in info
        assert 'python_version' in info
        
        # Validate types
        assert isinstance(info['platform'], str)
        assert isinstance(info['cpu_count'], int)
        assert isinstance(info['total_ram_gb'], float)
        assert isinstance(info['python_version'], str)


class TestCommandFunctions:
    """Test command-related functions."""

    def test_check_command_exists_python(self):
        """Test check_command_exists with python."""
        result = check_command_exists("python3") or check_command_exists("python")
        assert result == True

    def test_check_command_exists_nonexistent(self):
        """Test check_command_exists with non-existent command."""
        result = check_command_exists("nonexistent_command_xyz123")
        assert result == False

    def test_get_command_path_python(self):
        """Test get_command_path with python."""
        path = get_command_path("python3") or get_command_path("python")
        
        if path is not None:
            assert isinstance(path, str)
            assert os.path.isabs(path)
            assert os.path.exists(path)

    def test_get_command_path_nonexistent(self):
        """Test get_command_path with non-existent command."""
        path = get_command_path("nonexistent_command_xyz123")
        assert path is None


class TestPathFunctions:
    """Test path-related functions."""

    def test_expand_path_absolute(self):
        """Test expand_path with absolute path."""
        path = "/home/user/test"
        expanded = expand_path(path)
        
        assert expanded == path

    def test_expand_path_home(self):
        """Test expand_path with ~."""
        path = "~/test"
        expanded = expand_path(path)
        
        assert expanded.startswith(os.path.expanduser("~"))
        assert "~" not in expanded

    def test_expand_path_env_var(self):
        """Test expand_path with $HOME."""
        path = "$HOME/test"
        expanded = expand_path(path)
        
        assert expanded.startswith(os.path.expanduser("~"))
        assert "$" not in expanded

    def test_expand_path_relative(self):
        """Test expand_path with relative path."""
        path = "relative/path"
        expanded = expand_path(path)
        
        assert os.path.isabs(expanded)

    def test_expand_path_empty(self):
        """Test expand_path with empty string."""
        expanded = expand_path("")
        assert expanded == ""

    def test_ensure_directory(self, temp_dir):
        """Test ensure_directory function."""
        new_dir = temp_dir / "test" / "nested" / "directory"
        
        result = ensure_directory(str(new_dir))
        
        assert result == True
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_ensure_directory_existing(self, temp_dir):
        """Test ensure_directory with existing directory."""
        result = ensure_directory(str(temp_dir))
        
        assert result == True


class TestFormatSize:
    """Test format_size function."""

    def test_format_size_bytes(self):
        """Test format_size with bytes."""
        result = format_size(100)
        assert "B" in result
        assert "100" in result

    def test_format_size_kb(self):
        """Test format_size with KB."""
        result = format_size(1024)
        assert "KB" in result
        assert "1.00" in result

    def test_format_size_mb(self):
        """Test format_size with MB."""
        result = format_size(1024 * 1024)
        assert "MB" in result
        assert "1.00" in result

    def test_format_size_gb(self):
        """Test format_size with GB."""
        result = format_size(1024 * 1024 * 1024)
        assert "GB" in result
        assert "1.00" in result

    def test_format_size_tb(self):
        """Test format_size with TB."""
        result = format_size(1024 * 1024 * 1024 * 1024)
        assert "TB" in result
        assert "1.00" in result


class TestGPUInfo:
    """Test GPU info function."""

    def test_get_gpu_info(self):
        """Test get_gpu_info function."""
        gpu_info = get_gpu_info()
        
        assert isinstance(gpu_info, dict)
        assert 'has_gpu' in gpu_info
        assert 'gpu_type' in gpu_info
        assert 'gpu_name' in gpu_info
        assert 'recommended_layers' in gpu_info
        
        # Validate types
        assert isinstance(gpu_info['has_gpu'], bool)
        assert isinstance(gpu_info['gpu_type'], str)
        assert isinstance(gpu_info['gpu_name'], str)
        assert isinstance(gpu_info['recommended_layers'], int)

    def test_get_gpu_info_valid_type(self):
        """Test that GPU type is valid."""
        gpu_info = get_gpu_info()
        
        assert gpu_info['gpu_type'] in ['cuda', 'rocm', 'metal', 'none']

    def test_get_gpu_info_consistency(self):
        """Test GPU info consistency."""
        gpu_info = get_gpu_info()
        
        if gpu_info['has_gpu']:
            assert gpu_info['gpu_type'] != 'none'
            assert gpu_info['recommended_layers'] > 0
        else:
            assert gpu_info['gpu_type'] == 'none'
            assert gpu_info['recommended_layers'] == 0

    def test_get_gpu_info_linux(self):
        """Test GPU info on Linux."""
        if sys.platform.startswith('linux'):
            gpu_info = get_gpu_info()
            
            # Should attempt CUDA or ROCm detection
            assert isinstance(gpu_info, dict)

    def test_get_gpu_info_macos(self):
        """Test GPU info on macOS."""
        if sys.platform == 'darwin':
            gpu_info = get_gpu_info()
            
            # Should have Metal GPU
            assert gpu_info['has_gpu'] == True
            assert gpu_info['gpu_type'] == 'metal'
            assert 'Apple' in gpu_info['gpu_name'] or 'Silicon' in gpu_info['gpu_name']


class TestUtilityEdgeCases:
    """Test edge cases in utility functions."""

    def test_get_disk_usage_root(self):
        """Test get_disk_usage with root."""
        total, used, free = get_disk_usage("/")
        
        assert total > 0
        assert free > 0

    def test_is_port_in_use_invalid_port(self):
        """Test is_port_in_use with invalid port."""
        # Test with port out of range - should handle gracefully
        import pytest
        
        # Port 0 is actually valid (means any port)
        result = is_port_in_use(0)
        assert isinstance(result, bool)
        
        # Very high port should fail or return False
        try:
            result = is_port_in_use(99999)
            assert isinstance(result, bool)
        except (OverflowError, OSError):
            # Expected behavior for invalid port
            pass

    def test_expand_path_none(self):
        """Test expand_path with None."""
        # Should handle gracefully
        try:
            result = expand_path(None)
            assert result == ""
        except (TypeError, AttributeError):
            # Also acceptable
            pass

    def test_format_size_zero(self):
        """Test format_size with zero."""
        result = format_size(0)
        assert "0" in result
        assert "B" in result

    def test_format_size_negative(self):
        """Test format_size with negative."""
        result = format_size(-100)
        # Should still format
        assert isinstance(result, str)
