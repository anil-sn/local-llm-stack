"""
Test hardware detection module.

Tests GPU, CPU, RAM, and disk detection without mocking.
"""

import pytest
import sys
from pathlib import Path

from local_llm.hardware.detector import (
    HardwareDetector,
    GPUInfo,
    CPUInfo,
    MemoryInfo,
    DiskInfo,
    HardwareInfo,
    detect_hardware,
    get_optimal_config,
)


class TestHardwareDetector:
    """Test hardware detector class."""

    @pytest.fixture
    def detector(self):
        """Create hardware detector instance."""
        return HardwareDetector()

    def test_detector_init(self, detector):
        """Test detector initialization."""
        assert detector is not None
        assert detector.info is None

    def test_detect_returns_hardware_info(self, detector):
        """Test detect method returns HardwareInfo."""
        hw_info = detector.detect()
        
        assert isinstance(hw_info, HardwareInfo)
        assert hasattr(hw_info, 'gpu')
        assert hasattr(hw_info, 'cpu')
        assert hasattr(hw_info, 'memory')
        assert hasattr(hw_info, 'disk')
        assert hasattr(hw_info, 'platform')

    def test_detect_platform(self, detector):
        """Test platform detection."""
        hw_info = detector.detect()
        
        assert hw_info.platform in ['linux', 'darwin', 'windows']
        
        # Verify matches actual platform
        if sys.platform == 'darwin':
            assert hw_info.platform == 'darwin'
        elif sys.platform.startswith('linux'):
            assert hw_info.platform == 'linux'

    def test_detect_gpu(self, detector):
        """Test GPU detection."""
        hw_info = detector.detect()
        gpu = hw_info.gpu
        
        assert isinstance(gpu, GPUInfo)
        assert hasattr(gpu, 'has_gpu')
        assert hasattr(gpu, 'gpu_type')
        assert hasattr(gpu, 'gpu_name')
        assert hasattr(gpu, 'vram_total_gb')
        assert hasattr(gpu, 'recommended_layers')
        
        # GPU type should be valid
        assert gpu.gpu_type in ['cuda', 'rocm', 'metal', 'none']
        
        # If GPU exists, should have name
        if gpu.has_gpu:
            assert gpu.gpu_name is not None
            assert len(gpu.gpu_name) > 0
            assert gpu.recommended_layers > 0

    def test_detect_cpu(self, detector):
        """Test CPU detection."""
        hw_info = detector.detect()
        cpu = hw_info.cpu
        
        assert isinstance(cpu, CPUInfo)
        assert hasattr(cpu, 'model')
        assert hasattr(cpu, 'cores')
        assert hasattr(cpu, 'threads')
        
        # Should have at least 1 core
        assert cpu.cores >= 1
        assert cpu.threads >= 1
        
        # Model should be a string
        assert isinstance(cpu.model, str)

    def test_detect_memory(self, detector):
        """Test memory detection."""
        hw_info = detector.detect()
        mem = hw_info.memory
        
        assert isinstance(mem, MemoryInfo)
        assert hasattr(mem, 'total_gb')
        assert hasattr(mem, 'available_gb')
        assert hasattr(mem, 'used_gb')
        
        # Should have reasonable memory values
        assert mem.total_gb > 0
        assert mem.available_gb > 0
        assert mem.used_gb >= 0
        assert mem.total_gb >= mem.available_gb

    def test_detect_disk(self, detector):
        """Test disk detection."""
        hw_info = detector.detect()
        disk = hw_info.disk
        
        assert isinstance(disk, DiskInfo)
        assert hasattr(disk, 'total_gb')
        assert hasattr(disk, 'free_gb')
        assert hasattr(disk, 'used_gb')
        
        # Should have reasonable disk values
        assert disk.total_gb > 0
        assert disk.free_gb > 0
        assert disk.used_gb >= 0

    def test_hardware_info_to_dict(self, detector):
        """Test HardwareInfo to_dict method."""
        hw_info = detector.detect()
        hw_dict = hw_info.to_dict()
        
        assert isinstance(hw_dict, dict)
        assert 'platform' in hw_dict
        assert 'gpu' in hw_dict
        assert 'cpu' in hw_dict
        assert 'memory' in hw_dict
        assert 'disk' in hw_dict

    def test_hardware_info_summary(self, detector):
        """Test HardwareInfo summary method."""
        hw_info = detector.detect()
        summary = hw_info.summary()
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        # Summary should contain key hardware info
        assert 'CPU' in summary or 'RAM' in summary or 'GPU' in summary


class TestGPUInfo:
    """Test GPUInfo dataclass."""

    def test_gpu_info_defaults(self):
        """Test GPUInfo default values."""
        gpu = GPUInfo()
        
        assert gpu.has_gpu == False
        assert gpu.gpu_type == "none"
        assert gpu.gpu_name == "Unknown"
        assert gpu.vram_total_gb == 0.0
        assert gpu.recommended_layers == 0

    def test_gpu_info_custom_values(self):
        """Test GPUInfo with custom values."""
        gpu = GPUInfo(
            has_gpu=True,
            gpu_type="cuda",
            gpu_name="NVIDIA GeForce RTX 4090",
            vram_total_gb=24.0,
            recommended_layers=999,
        )
        
        assert gpu.has_gpu == True
        assert gpu.gpu_type == "cuda"
        assert "RTX 4090" in gpu.gpu_name
        assert gpu.vram_total_gb == 24.0
        assert gpu.recommended_layers == 999


class TestCPUInfo:
    """Test CPUInfo dataclass."""

    def test_cpu_info_defaults(self):
        """Test CPUInfo default values."""
        cpu = CPUInfo()
        
        assert cpu.model == "Unknown"
        assert cpu.cores == 0
        assert cpu.threads == 0

    def test_cpu_info_custom_values(self):
        """Test CPUInfo with custom values."""
        cpu = CPUInfo(
            model="AMD Ryzen 9 7950X3D",
            cores=16,
            threads=32,
        )
        
        assert cpu.model == "AMD Ryzen 9 7950X3D"
        assert cpu.cores == 16
        assert cpu.threads == 32


class TestMemoryInfo:
    """Test MemoryInfo dataclass."""

    def test_memory_info_defaults(self):
        """Test MemoryInfo default values."""
        mem = MemoryInfo()
        
        assert mem.total_gb == 0.0
        assert mem.available_gb == 0.0
        assert mem.used_gb == 0.0


class TestDiskInfo:
    """Test DiskInfo dataclass."""

    def test_disk_info_defaults(self):
        """Test DiskInfo default values."""
        disk = DiskInfo()
        
        assert disk.total_gb == 0.0
        assert disk.free_gb == 0.0
        assert disk.used_gb == 0.0


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_detect_hardware_function(self):
        """Test detect_hardware convenience function."""
        hw_info = detect_hardware()
        
        assert isinstance(hw_info, HardwareInfo)
        assert hw_info.gpu is not None
        assert hw_info.cpu is not None
        assert hw_info.memory is not None
        assert hw_info.disk is not None

    def test_get_optimal_config_function(self):
        """Test get_optimal_config convenience function."""
        config = get_optimal_config()
        
        assert isinstance(config, dict)
        assert 'gpu_layers' in config
        assert 'threads' in config
        assert 'batch_size' in config
        assert 'context_size' in config
        
        # Values should be reasonable
        assert config['gpu_layers'] >= 0
        assert config['threads'] >= 1
        assert config['batch_size'] > 0
        assert config['context_size'] > 0

    def test_get_optimal_config_has_flash_attn(self):
        """Test that optimal config includes flash attention."""
        config = get_optimal_config()
        
        assert 'flash_attn' in config
        assert config['flash_attn'] in ['auto', 'on', 'off']


class TestPlatformSpecificDetection:
    """Test platform-specific detection."""

    def test_linux_detection(self, detector):
        """Test detection on Linux."""
        if sys.platform.startswith('linux'):
            hw_info = detector.detect()
            
            # Should detect Linux platform
            assert hw_info.platform == 'linux'
            
            # Should read from /proc files
            assert hw_info.cpu.cores >= 1
            assert hw_info.memory.total_gb > 0

    def test_macos_detection(self, detector):
        """Test detection on macOS."""
        if sys.platform == 'darwin':
            hw_info = detector.detect()
            
            # Should detect macOS platform
            assert hw_info.platform == 'darwin'
            
            # Should use sysctl commands
            assert hw_info.cpu.model is not None
            assert hw_info.memory.total_gb > 0


class TestGPUTypeValidation:
    """Test GPU type detection."""

    def test_cuda_detection(self, detector):
        """Test CUDA GPU detection."""
        hw_info = detector.detect()
        gpu = hw_info.gpu
        
        if gpu.gpu_type == 'cuda':
            assert gpu.has_gpu == True
            assert 'NVIDIA' in gpu.gpu_name or gpu.gpu_name != "Unknown"
            assert gpu.recommended_layers > 0

    def test_metal_detection(self, detector):
        """Test Metal GPU detection."""
        hw_info = detector.detect()
        gpu = hw_info.gpu
        
        if gpu.gpu_type == 'metal':
            assert gpu.has_gpu == True
            assert gpu.recommended_layers > 0
            # On macOS, should have Metal GPU
            if sys.platform == 'darwin':
                assert 'Apple' in gpu.gpu_name or 'Silicon' in gpu.gpu_name

    def test_no_gpu(self, detector):
        """Test system without GPU."""
        hw_info = detector.detect()
        gpu = hw_info.gpu
        
        if not gpu.has_gpu:
            assert gpu.gpu_type == 'none'
            assert gpu.recommended_layers == 0


class TestOptimalConfigLogic:
    """Test optimal configuration logic."""

    def test_config_with_gpu(self, detector):
        """Test optimal config when GPU is available."""
        hw_info = detector.detect()
        
        if hw_info.gpu.has_gpu:
            config = get_optimal_config()
            
            # Should recommend GPU offloading
            assert config['gpu_layers'] > 0
            
            # Should have optimized batch size
            assert config['batch_size'] >= 128

    def test_config_without_gpu(self, detector):
        """Test optimal config when no GPU available."""
        hw_info = detector.detect()
        
        if not hw_info.gpu.has_gpu:
            config = get_optimal_config()
            
            # Should not recommend GPU offloading
            assert config['gpu_layers'] == 0

    def test_config_threads_based_on_cpu(self, detector):
        """Test thread count based on CPU cores."""
        hw_info = detector.detect()
        config = get_optimal_config()
        
        # Threads should be based on CPU cores
        assert config['threads'] >= 1
        assert config['threads'] <= hw_info.cpu.threads * 2

    def test_config_context_based_on_ram(self, detector):
        """Test context size based on available RAM."""
        hw_info = detector.detect()
        config = get_optimal_config()
        
        # Context size should be positive
        assert config['context_size'] > 0
        assert config['context_size'] <= 262144  # Max limit
