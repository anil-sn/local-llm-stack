"""
Hardware detection module.

Detects GPU, CPU, RAM, and provides optimal configuration for LLM inference.
"""

import os
import re
import subprocess
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict, Any


@dataclass
class GPUInfo:
    """GPU information."""
    has_gpu: bool = False
    gpu_type: str = "none"  # cuda, rocm, metal, none
    gpu_name: str = "Unknown"
    vram_total_gb: float = 0.0
    vram_available_gb: float = 0.0
    compute_capability: str = ""
    driver_version: str = ""
    recommended_layers: int = 0
    tensor_parallel: int = 1


@dataclass
class CPUInfo:
    """CPU information."""
    model: str = "Unknown"
    cores: int = 0
    threads: int = 0
    architecture: str = "x86_64"


@dataclass
class MemoryInfo:
    """System memory information."""
    total_gb: float = 0.0
    available_gb: float = 0.0
    used_gb: float = 0.0


@dataclass
class DiskInfo:
    """Disk information."""
    total_gb: float = 0.0
    free_gb: float = 0.0
    used_gb: float = 0.0


@dataclass
class HardwareInfo:
    """Complete hardware information."""
    gpu: GPUInfo = field(default_factory=GPUInfo)
    cpu: CPUInfo = field(default_factory=CPUInfo)
    memory: MemoryInfo = field(default_factory=MemoryInfo)
    disk: DiskInfo = field(default_factory=DiskInfo)
    platform: str = "unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "platform": self.platform,
            "gpu": {
                "has_gpu": self.gpu.has_gpu,
                "gpu_type": self.gpu.gpu_type,
                "gpu_name": self.gpu.gpu_name,
                "vram_total_gb": self.gpu.vram_total_gb,
                "vram_available_gb": self.gpu.vram_available_gb,
                "recommended_layers": self.gpu.recommended_layers,
            },
            "cpu": {
                "model": self.cpu.model,
                "cores": self.cpu.cores,
                "threads": self.cpu.threads,
            },
            "memory": {
                "total_gb": self.memory.total_gb,
                "available_gb": self.memory.available_gb,
            },
            "disk": {
                "free_gb": self.disk.free_gb,
            },
        }
    
    def summary(self) -> str:
        """Get human-readable summary."""
        parts = []
        
        if self.gpu.has_gpu:
            parts.append(f"GPU: {self.gpu.gpu_name} ({self.gpu.vram_total_gb:.1f}GB VRAM)")
        else:
            parts.append("CPU only (no GPU)")
        
        parts.append(f"CPU: {self.cpu.model} ({self.cpu.cores} cores)")
        parts.append(f"RAM: {self.memory.total_gb:.1f}GB total, {self.memory.available_gb:.1f}GB available")
        parts.append(f"Disk: {self.disk.free_gb:.1f}GB free")
        
        return " | ".join(parts)


class HardwareDetector:
    """Detect and analyze hardware for LLM inference."""
    
    def __init__(self):
        self.info: Optional[HardwareInfo] = None
    
    def detect(self) -> HardwareInfo:
        """Detect all hardware components."""
        self.info = HardwareInfo()
        
        self.info.platform = self._detect_platform()
        self.info.gpu = self._detect_gpu()
        self.info.cpu = self._detect_cpu()
        self.info.memory = self._detect_memory()
        self.info.disk = self._detect_disk()
        
        return self.info
    
    def _detect_platform(self) -> str:
        """Detect platform."""
        import platform
        return platform.system().lower()
    
    def _detect_gpu(self) -> GPUInfo:
        """Detect GPU information."""
        gpu = GPUInfo()
        
        # Try NVIDIA first
        nvidia_info = self._detect_nvidia()
        if nvidia_info.has_gpu:
            return nvidia_info
        
        # Try AMD ROCm
        amd_info = self._detect_amd()
        if amd_info.has_gpu:
            return amd_info
        
        # Try Apple Metal
        if self._detect_platform() == "darwin":
            metal_info = self._detect_apple_metal()
            if metal_info.has_gpu:
                return metal_info
        
        return gpu
    
    def _detect_nvidia(self) -> GPUInfo:
        """Detect NVIDIA GPU."""
        gpu = GPUInfo()

        if not shutil.which("nvidia-smi"):
            return gpu

        try:
            # Get GPU info
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                check=True,
            )

            lines = result.stdout.strip().split("\n")
            if lines:
                parts = lines[0].split(", ")
                if len(parts) >= 3:
                    gpu.has_gpu = True
                    gpu.gpu_type = "cuda"
                    gpu.gpu_name = parts[0].strip()
                    # Parse VRAM - remove "MiB" suffix
                    vram_str = parts[1].strip().replace(" MiB", "").replace("GiB", "")
                    gpu.vram_total_gb = float(vram_str) / 1024
                    gpu.driver_version = parts[2].strip()

                    # Get compute capability
                    cc = self._get_nvidia_compute_capability()
                    if cc:
                        gpu.compute_capability = cc

                    # Calculate recommended layers
                    # For most models, 1GB VRAM ≈ 1B parameters at Q4
                    # Reserve 2GB for context and overhead
                    usable_vram = max(0, gpu.vram_total_gb - 2)
                    gpu.recommended_layers = 999 if usable_vram >= 16 else int(usable_vram * 50)

                    # Multi-GPU support
                    if len(lines) > 1:
                        gpu.tensor_parallel = len(lines)

            # Try to get available VRAM (requires nvidia-ml-py)
            try:
                import pynvml
                pynvml.nvmlInit()
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpu.vram_available_gb = info.free / (1024 ** 3)
                pynvml.nvmlShutdown()
            except ImportError:
                # Estimate available as 90% of total
                gpu.vram_available_gb = gpu.vram_total_gb * 0.9

        except (subprocess.CalledProcessError, Exception) as e:
            import sys
            print(f"Debug: NVIDIA detection failed: {e}", file=sys.stderr)
            pass
        
        return gpu
    
    def _get_nvidia_compute_capability(self) -> Optional[str]:
        """Get NVIDIA compute capability."""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=compute_cap", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                check=True,
            )
            if result.stdout.strip():
                cap = result.stdout.strip().split("\n")[0]
                return f"{cap[0]}.{cap[1:]}"
        except Exception:
            pass
        return None
    
    def _detect_amd(self) -> GPUInfo:
        """Detect AMD GPU."""
        gpu = GPUInfo()
        
        if not shutil.which("rocm-smi"):
            return gpu
        
        try:
            result = subprocess.run(
                ["rocm-smi", "--showproductname"],
                capture_output=True,
                text=True,
                check=True,
            )
            
            if result.stdout.strip():
                gpu.has_gpu = True
                gpu.gpu_type = "rocm"
                gpu.gpu_name = "AMD ROCm GPU"
                gpu.recommended_layers = 999
        except Exception:
            pass
        
        return gpu
    
    def _detect_apple_metal(self) -> GPUInfo:
        """Detect Apple Silicon GPU."""
        gpu = GPUInfo()
        gpu.has_gpu = True
        gpu.gpu_type = "metal"
        gpu.gpu_name = "Apple Silicon GPU"
        gpu.recommended_layers = 999
        
        try:
            result = subprocess.run(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                gpu.gpu_name = result.stdout.strip()
            
            # Get unified memory
            result = subprocess.run(
                ["sysctl", "-n", "hw.memsize"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                mem_gb = int(result.stdout.strip()) / (1024 ** 3)
                gpu.vram_total_gb = mem_gb
                gpu.vram_available_gb = mem_gb * 0.75
                
                # Adjust for memory size
                if mem_gb < 16:
                    gpu.recommended_layers = 35
        except Exception:
            pass
        
        return gpu
    
    def _detect_cpu(self) -> CPUInfo:
        """Detect CPU information."""
        cpu = CPUInfo()
        platform = self._detect_platform()
        
        try:
            if platform == "linux":
                # Read /proc/cpuinfo
                with open("/proc/cpuinfo", "r") as f:
                    content = f.read()
                
                # Get model name
                for line in content.split("\n"):
                    if line.startswith("model name"):
                        cpu.model = line.split(":")[1].strip()
                        break
                
                # Count cores
                cpu.cores = content.count("processor")
                cpu.threads = cpu.cores  # Simplified
                
                # Detect architecture
                if "aarch64" in content or "arm" in content.lower():
                    cpu.architecture = "arm64"
                elif "x86_64" in content or "amd64" in content:
                    cpu.architecture = "x86_64"
            
            elif platform == "darwin":
                # macOS
                result = subprocess.run(
                    ["sysctl", "-n", "machdep.cpu.brand_string"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode == 0:
                    cpu.model = result.stdout.strip()
                
                result = subprocess.run(
                    ["sysctl", "-n", "hw.ncpu"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode == 0:
                    cpu.threads = int(result.stdout.strip())
                    cpu.cores = cpu.threads // 2  # Assume hyperthreading
                
                # Detect Apple Silicon
                if "apple" in cpu.model.lower() or "m1" in cpu.model.lower() or "m2" in cpu.model.lower() or "m3" in cpu.model.lower():
                    cpu.architecture = "arm64"
            
            # Fallback
            if cpu.cores == 0:
                cpu.cores = os.cpu_count() or 4
                cpu.threads = cpu.cores
                
        except Exception:
            cpu.cores = 4
            cpu.threads = 4
        
        return cpu
    
    def _detect_memory(self) -> MemoryInfo:
        """Detect system memory."""
        mem = MemoryInfo()
        platform = self._detect_platform()
        
        try:
            if platform == "linux":
                with open("/proc/meminfo", "r") as f:
                    for line in f:
                        if line.startswith("MemTotal:"):
                            mem.total_gb = int(line.split()[1]) / (1024 * 1024)
                        elif line.startswith("MemAvailable:"):
                            mem.available_gb = int(line.split()[1]) / (1024 * 1024)
                        elif line.startswith("MemFree:"):
                            mem.used_gb = mem.total_gb - (int(line.split()[1]) / (1024 * 1024))
            
            elif platform == "darwin":
                result = subprocess.run(
                    ["sysctl", "-n", "hw.memsize"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode == 0:
                    mem.total_gb = int(result.stdout.strip()) / (1024 ** 3)
                
                # Get available via vm_stat
                result = subprocess.run(["vm_stat"], capture_output=True, text=True, check=False)
                if result.returncode == 0:
                    page_size = 4096
                    for line in result.stdout.split("\n"):
                        if "free" in line.lower():
                            parts = line.split(":")
                            if len(parts) >= 2:
                                free_pages = int(parts[1].strip().rstrip("."))
                                mem.available_gb = (free_pages * page_size) / (1024 ** 3)
                                mem.used_gb = mem.total_gb - mem.available_gb
            
            # Fallback using psutil
            if mem.total_gb == 0:
                try:
                    import psutil
                    vmem = psutil.virtual_memory()
                    mem.total_gb = vmem.total / (1024 ** 3)
                    mem.available_gb = vmem.available / (1024 ** 3)
                    mem.used_gb = vmem.used / (1024 ** 3)
                except ImportError:
                    mem.total_gb = 16.0
                    mem.available_gb = 8.0
                    mem.used_gb = 8.0
        
        except Exception:
            mem.total_gb = 16.0
            mem.available_gb = 8.0
            mem.used_gb = 8.0
        
        return mem
    
    def _detect_disk(self) -> DiskInfo:
        """Detect disk space."""
        disk = DiskInfo()
        
        try:
            import shutil
            usage = shutil.disk_usage("/")
            disk.total_gb = usage.total / (1024 ** 3)
            disk.free_gb = usage.free / (1024 ** 3)
            disk.used_gb = usage.used / (1024 ** 3)
        except Exception:
            disk.total_gb = 500.0
            disk.free_gb = 100.0
            disk.used_gb = 400.0
        
        return disk
    
    def get_optimal_config(self, model_type: str = "standard") -> Dict[str, Any]:
        """
        Get optimal configuration for detected hardware.

        Args:
            model_type: Type of model ('standard' or 'bitnet')

        Returns dict with:
        - gpu_layers: Number of layers to offload
        - threads: CPU threads to use
        - batch_size: Batch size
        - context_size: Maximum context size
        - flash_attn: Whether to use flash attention
        - use_bitnet_kernels: Whether to use BitNet-optimized kernels
        """
        if self.info is None:
            self.detect()

        gpu = self.info.gpu
        cpu = self.info.cpu
        mem = self.info.memory

        # BitNet-specific optimizations
        if model_type == "bitnet":
            return self._get_bitnet_config(gpu, cpu, mem)

        # Standard model configuration
        config = {
            "gpu_layers": 0,
            "threads": cpu.threads,
            "batch_size": 512,
            "ubatch_size": 256,
            "context_size": 131072,
            "flash_attn": "auto",
            "tensor_parallel": 1,
            "use_bitnet_kernels": False,
        }

        if gpu.has_gpu:
            # GPU offloading
            config["gpu_layers"] = gpu.recommended_layers

            # Adjust batch size based on VRAM
            if gpu.vram_total_gb >= 24:
                config["batch_size"] = 1024
                config["ubatch_size"] = 512
            elif gpu.vram_total_gb >= 16:
                config["batch_size"] = 512
                config["ubatch_size"] = 256
            elif gpu.vram_total_gb >= 8:
                config["batch_size"] = 256
                config["ubatch_size"] = 128
            else:
                config["batch_size"] = 128
                config["ubatch_size"] = 64

            # Flash attention for modern GPUs
            if gpu.gpu_type == "cuda" and gpu.vram_total_gb >= 16:
                config["flash_attn"] = "on"

            # Multi-GPU
            if gpu.tensor_parallel > 1:
                config["tensor_parallel"] = gpu.tensor_parallel

        # Adjust context size based on RAM
        available_for_context = max(0, mem.available_gb - 4)  # Reserve 4GB
        # Rough estimate: 1GB ≈ 16K context for Q4 models
        max_context = int(available_for_context * 16 * 1024)
        config["context_size"] = min(262144, max(16384, max_context))

        # Thread optimization
        if gpu.has_gpu:
            # Fewer threads needed with GPU
            config["threads"] = max(4, cpu.cores // 2)

        return config

    def _get_bitnet_config(self, gpu, cpu, mem) -> Dict[str, Any]:
        """
        Get optimized configuration for BitNet models.

        BitNet models are highly optimized for CPU inference,
        so we adjust settings accordingly.
        """
        config = {
            "gpu_layers": 0,
            "threads": cpu.threads,
            "batch_size": 1024,  # BitNet can handle larger batches
            "ubatch_size": 512,
            "context_size": 131072,
            "flash_attn": "auto",
            "tensor_parallel": 1,
            "use_bitnet_kernels": True,
            "bitnet_parallel_factor": 4,  # BitNet-specific parallel factor
        }

        # BitNet works great on CPU, but GPU can still help
        if gpu.has_gpu:
            # BitNet benefits less from GPU offloading
            # Use GPU for remaining computation only
            config["gpu_layers"] = max(0, gpu.recommended_layers // 2)
            config["batch_size"] = max(config["batch_size"], 512)

            # Flash attention still useful
            if gpu.gpu_type == "cuda" and gpu.vram_total_gb >= 16:
                config["flash_attn"] = "on"

            # Multi-GPU
            if gpu.tensor_parallel > 1:
                config["tensor_parallel"] = gpu.tensor_parallel

        # BitNet uses less memory, so we can afford larger context
        available_for_context = max(0, mem.available_gb - 2)  # Reserve only 2GB
        # BitNet is more efficient: 1GB ≈ 32K context
        max_context = int(available_for_context * 32 * 1024)
        config["context_size"] = min(262144, max(16384, max_context))

        # CPU threads - BitNet scales well with more threads
        config["threads"] = cpu.threads

        return config


# Global detector instance
_detector: Optional[HardwareDetector] = None


def get_detector() -> HardwareDetector:
    """Get or create hardware detector."""
    global _detector
    if _detector is None:
        _detector = HardwareDetector()
    return _detector


def detect_hardware() -> HardwareInfo:
    """Detect hardware and return info."""
    return get_detector().detect()


def get_optimal_config(model_type: str = "standard") -> Dict[str, Any]:
    """Get optimal configuration for current hardware.
    
    Args:
        model_type: Type of model ('standard' or 'bitnet')
    """
    return get_detector().get_optimal_config(model_type)
