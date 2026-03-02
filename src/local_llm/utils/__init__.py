"""
Cross-platform system utilities for Local LLM Stack.

Provides OS-agnostic functions for:
- System information (CPU, RAM, disk)
- Process management
- Port checking
- Resource monitoring
"""

import os
import platform
import shutil
import socket
import subprocess
from pathlib import Path
from typing import Optional, Tuple


def get_platform() -> str:
    """Get the current platform (darwin, linux, windows)."""
    return platform.system().lower()


def is_macos() -> bool:
    """Check if running on macOS."""
    return get_platform() == "darwin"


def is_linux() -> bool:
    """Check if running on Linux."""
    return get_platform() == "linux"


def is_windows() -> bool:
    """Check if running on Windows."""
    return get_platform() == "windows"


def get_cpu_count() -> int:
    """Get the number of CPU cores (cross-platform)."""
    try:
        if is_macos():
            # Use sysctl on macOS
            result = subprocess.run(
                ["sysctl", "-n", "hw.ncpu"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                return int(result.stdout.strip())
        
        # Fallback to os.cpu_count() (works on all platforms)
        count = os.cpu_count()
        if count:
            return count
    except (ValueError, subprocess.SubprocessError):
        pass
    
    return 4  # Safe default


def get_total_ram_gb() -> float:
    """Get total system RAM in GB (cross-platform)."""
    try:
        if is_macos():
            # Use sysctl on macOS
            result = subprocess.run(
                ["sysctl", "-n", "hw.memsize"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                mem_bytes = int(result.stdout.strip())
                return mem_bytes / (1024 ** 3)
        
        elif is_linux():
            # Read from /proc/meminfo on Linux
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        mem_kb = int(line.split()[1])
                        return mem_kb / (1024 * 1024)
        
        # Fallback: use psutil if available
        try:
            import psutil
            return psutil.virtual_memory().total / (1024 ** 3)
        except ImportError:
            pass
            
    except (ValueError, subprocess.SubprocessError, IOError):
        pass
    
    return 16.0  # Safe default


def get_available_ram_gb() -> float:
    """Get available RAM in GB (cross-platform)."""
    try:
        if is_macos():
            # Use vm_stat on macOS
            result = subprocess.run(
                ["vm_stat"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                # Parse vm_stat output
                page_size = 4096  # Default macOS page size
                for line in result.stdout.split("\n"):
                    if "free" in line.lower():
                        parts = line.split(":")
                        if len(parts) >= 2:
                            free_pages = int(parts[1].strip().rstrip("."))
                            return (free_pages * page_size) / (1024 ** 3)
        
        elif is_linux():
            # Read from /proc/meminfo on Linux
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if line.startswith("MemAvailable:"):
                        mem_kb = int(line.split()[1])
                        return mem_kb / (1024 * 1024)
        
        # Fallback: use psutil if available
        try:
            import psutil
            return psutil.virtual_memory().available / (1024 ** 3)
        except ImportError:
            pass
            
    except (ValueError, subprocess.SubprocessError, IOError):
        pass
    
    return 8.0  # Safe default


def get_disk_usage(path: str = "/") -> Tuple[float, float, float]:
    """
    Get disk usage statistics for a given path.
    
    Returns:
        Tuple of (total_gb, used_gb, free_gb)
    """
    try:
        total, used, free = shutil.disk_usage(path)
        return (
            total / (1024 ** 3),
            used / (1024 ** 3),
            free / (1024 ** 3)
        )
    except OSError:
        return (0.0, 0.0, 0.0)


def is_port_in_use(port: int, host: str = "localhost") -> bool:
    """Check if a port is in use (cross-platform)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        try:
            result = s.connect_ex((host, port))
            return result == 0
        except socket.error:
            return False


def get_process_using_port(port: int, host: str = "localhost") -> Optional[int]:
    """
    Get the PID of the process using a port (cross-platform).
    
    Returns:
        PID if found, None otherwise
    """
    try:
        if is_macos() or is_linux():
            # Use lsof on macOS/Linux
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0 and result.stdout.strip():
                return int(result.stdout.strip().split("\n")[0])
        
        # Fallback: try netstat on Linux
        if is_linux():
            result = subprocess.run(
                ["ss", "-tlnp"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if f":{port}" in line:
                        # Parse PID from netstat output
                        parts = line.split()
                        if parts:
                            pid_part = parts[-1]
                            if "pid=" in pid_part:
                                pid = pid_part.split("pid=")[1].split(",")[0]
                                return int(pid)
    except (ValueError, subprocess.SubprocessError):
        pass
    
    return None


def kill_process(pid: int, signal: int = 15) -> bool:
    """
    Kill a process by PID.
    
    Args:
        pid: Process ID to kill
        signal: Signal to send (15=SIGTERM, 9=SIGKILL)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        os.kill(pid, signal)
        return True
    except (OSError, ProcessLookupError):
        return False


def get_system_info() -> dict:
    """
    Get comprehensive system information.
    
    Returns:
        Dictionary with system information
    """
    cpu_count = get_cpu_count()
    total_ram = get_total_ram_gb()
    avail_ram = get_available_ram_gb()
    disk_total, disk_used, disk_free = get_disk_usage("/")
    
    return {
        "platform": get_platform(),
        "os": platform.system(),
        "os_version": platform.version(),
        "machine": platform.machine(),
        "cpu_count": cpu_count,
        "total_ram_gb": round(total_ram, 2),
        "available_ram_gb": round(avail_ram, 2),
        "disk_total_gb": round(disk_total, 2),
        "disk_used_gb": round(disk_used, 2),
        "disk_free_gb": round(disk_free, 2),
        "python_version": platform.python_version(),
    }


def check_command_exists(command: str) -> bool:
    """Check if a command exists in PATH (cross-platform)."""
    return shutil.which(command) is not None


def get_command_path(command: str) -> Optional[str]:
    """Get the full path of a command (cross-platform)."""
    return shutil.which(command)


def expand_path(path: str, base_dir: Optional[str] = None) -> str:
    """
    Expand a path, handling ~, $HOME, and relative paths.
    
    Args:
        path: Path to expand
        base_dir: Base directory for relative paths
    
    Returns:
        Expanded absolute path
    """
    if not path:
        return ""
    
    # Expand $HOME
    path = path.replace("$HOME", os.path.expanduser("~"))
    
    # Expand ~
    path = os.path.expanduser(path)
    
    # Handle relative paths
    if not os.path.isabs(path):
        if base_dir:
            path = os.path.join(base_dir, path)
        else:
            path = os.path.abspath(path)
    
    return str(Path(path).resolve())


def ensure_directory(path: str) -> bool:
    """
    Ensure a directory exists, creating it if necessary.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except OSError:
        return False


def format_size(size_bytes: int) -> str:
    """Format a size in bytes to human-readable string."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def get_gpu_info() -> dict:
    """
    Get GPU information (cross-platform).
    
    Returns:
        Dictionary with GPU information:
        - has_gpu: bool - Whether a GPU is available
        - gpu_type: str - 'metal' (macOS), 'cuda' (NVIDIA), 'rocm' (AMD), or 'none'
        - gpu_name: str - GPU name if available
        - recommended_layers: int - Recommended GPU layers for offloading
    """
    result = {
        "has_gpu": False,
        "gpu_type": "none",
        "gpu_name": "Unknown",
        "recommended_layers": 0,
    }
    
    try:
        if is_macos():
            # macOS - Check for Metal GPU support
            result = _get_macOS_gpu_info()
        
        elif is_linux():
            # Linux - Check for NVIDIA/AMD GPU
            result = _get_linux_gpu_info()
    
    except Exception:
        # If detection fails, assume no GPU
        pass
    
    return result


def _get_macOS_gpu_info() -> dict:
    """Get GPU info on macOS (Metal)."""
    result = {
        "has_gpu": True,  # All Apple Silicon has GPU
        "gpu_type": "metal",
        "gpu_name": "Apple Silicon GPU",
        "recommended_layers": 999,  # Offload all layers on Apple Silicon
    }
    
    try:
        # Get chip type
        chip_result = subprocess.run(
            ["sysctl", "-n", "machdep.cpu.brand_string"],
            capture_output=True,
            text=True,
            check=False,
        )
        
        if chip_result.returncode == 0:
            chip = chip_result.stdout.strip()
            result["gpu_name"] = chip
            
            # M5/A19 and newer have better tensor support
            if "M5" in chip or "M6" in chip or "A19" in chip:
                result["gpu_name"] = f"{chip} (Full Metal support)"
            else:
                # Older chips may have issues with some Metal features
                result["gpu_name"] = f"{chip} (Metal)"
        
        # Get unified memory info
        mem_result = subprocess.run(
            ["sysctl", "-n", "hw.memsize"],
            capture_output=True,
            text=True,
            check=False,
        )
        
        if mem_result.returncode == 0:
            mem_gb = int(mem_result.stdout.strip()) / (1024 ** 3)
            # Adjust layers based on available memory
            if mem_gb < 16:
                result["recommended_layers"] = 35  # Conservative for 8GB
            elif mem_gb < 32:
                result["recommended_layers"] = 999  # Full offload for 16GB+
    
    except Exception:
        pass
    
    return result


def _get_linux_gpu_info() -> dict:
    """Get GPU info on Linux."""
    result = {
        "has_gpu": False,
        "gpu_type": "none",
        "gpu_name": "Unknown",
        "recommended_layers": 0,
    }
    
    # Check for NVIDIA GPU
    if check_command_exists("nvidia-smi"):
        try:
            nvidia_result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                check=False,
            )
            
            if nvidia_result.returncode == 0 and nvidia_result.stdout.strip():
                gpu_name = nvidia_result.stdout.strip().split("\n")[0]
                result["has_gpu"] = True
                result["gpu_type"] = "cuda"
                result["gpu_name"] = gpu_name
                result["recommended_layers"] = 999  # Full offload for CUDA
                return result
        
        except Exception:
            pass
    
    # Check for AMD GPU
    if check_command_exists("rocm-smi"):
        try:
            amd_result = subprocess.run(
                ["rocm-smi", "--showproductname"],
                capture_output=True,
                text=True,
                check=False,
            )
            
            if amd_result.returncode == 0 and amd_result.stdout.strip():
                result["has_gpu"] = True
                result["gpu_type"] = "rocm"
                result["gpu_name"] = "AMD ROCm GPU"
                result["recommended_layers"] = 999  # Full offload for ROCm
                return result
        
        except Exception:
            pass
    
    # Check /sys/class/drm for any GPU
    try:
        drm_path = Path("/sys/class/drm")
        if drm_path.exists():
            for item in drm_path.iterdir():
                if item.is_dir() and not item.name.startswith("card"):
                    continue
                
                # Try to read vendor
                vendor_file = item / "device" / "vendor"
                if vendor_file.exists():
                    vendor = vendor_file.read_text().strip().lower()
                    if "0x10de" in vendor:  # NVIDIA
                        result["has_gpu"] = True
                        result["gpu_type"] = "cuda"
                        result["gpu_name"] = "NVIDIA GPU (detected)"
                        result["recommended_layers"] = 999
                    elif "0x1002" in vendor:  # AMD
                        result["has_gpu"] = True
                        result["gpu_type"] = "rocm"
                        result["gpu_name"] = "AMD GPU (detected)"
                        result["recommended_layers"] = 999
    except Exception:
        pass
    
    # No GPU detected - will use CPU
    result["gpu_name"] = "CPU only"
    return result
