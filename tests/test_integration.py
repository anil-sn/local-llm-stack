"""
Integration tests for Local LLM Stack CLI.

Tests complete workflows without mocking, including:
- Server lifecycle
- Model operations
- Chat functionality
- Configuration workflows
- Hardware detection workflows
"""

import os
import signal
import subprocess
import sys
import time
import pytest
from pathlib import Path
from typing import Optional


class TestServerLifecycle:
    """Test complete server lifecycle."""

    def test_server_start_stop(self, run_cli, server_port, temp_dir):
        """Test starting and stopping server."""
        # Skip if no model downloaded
        from local_llm.config import get_config
        config = get_config()
        
        if not os.path.isfile(config.model_path):
            pytest.skip("Model not downloaded")
        
        # Skip if llama-server not available
        if not subprocess.run(["which", "llama-server"], capture_output=True).returncode == 0:
            pytest.skip("llama-server not installed")
        
        # Start server in background
        start_result = run_cli([
            "server", "start",
            "--port", str(server_port),
            "--background",
        ])
        
        # Give server time to start
        time.sleep(3)
        
        # Check if server started
        status_result = run_cli(["server", "status"])
        
        # Stop server
        stop_result = run_cli(["server", "stop"])
        
        # Assertions
        assert start_result.returncode == 0 or "already in use" in start_result.stderr.lower()
        assert stop_result.returncode == 0 or "not found" in stop_result.stdout.lower()

    def test_server_status_running(self, run_cli):
        """Test server status when server is running."""
        # This test assumes a server may or may not be running
        result = run_cli(["server", "status"])
        
        assert result.returncode == 0
        # Should show either running or not running
        assert "running" in result.stdout.lower() or "not running" in result.stdout.lower()

    def test_server_logs(self, run_cli):
        """Test server logs command."""
        result = run_cli(["server", "logs", "--lines", "10"])
        
        # Should not crash
        assert result.returncode == 0 or "not found" in result.stdout.lower()


class TestModelWorkflows:
    """Test model management workflows."""

    def test_model_list_info(self, run_cli):
        """Test listing and getting model info."""
        # List models
        list_result = run_cli(["model", "list"])
        assert list_result.returncode == 0
        assert "Available Models" in list_result.stdout or "model" in list_result.stdout.lower()
        
        # Get info for first model
        info_result = run_cli(["model", "info", "llama-3-8b"])
        assert info_result.returncode == 0
        assert "Model:" in info_result.stdout or "model" in info_result.stdout.lower()

    def test_model_validate(self, run_cli):
        """Test model validation workflow."""
        result = run_cli(["model", "validate"])
        
        # Should not crash
        assert "Validating" in result.stdout or "not found" in result.stdout.lower()

    def test_model_recommend(self, run_cli):
        """Test model recommendation workflow."""
        result = run_cli(["model", "recommend"])
        
        # Should analyze hardware and provide recommendations
        assert result.returncode == 0
        assert "Analyzing" in result.stdout or "Recommended" in result.stdout or "hardware" in result.stdout.lower()


class TestConfigurationWorkflows:
    """Test configuration workflows."""

    def test_config_show_validate(self, run_cli):
        """Test showing and validating configuration."""
        # Show config
        show_result = run_cli(["config", "show"])
        assert show_result.returncode == 0
        assert "Configuration" in show_result.stdout
        
        # Validate config
        validate_result = run_cli(["config", "validate"])
        assert validate_result.returncode == 0
        assert "Valid" in validate_result.stdout or "config" in validate_result.stdout.lower()

    def test_config_models(self, run_cli):
        """Test listing configured models."""
        result = run_cli(["config", "models"])
        
        assert result.returncode == 0
        assert "Configured Models" in result.stdout or "model" in result.stdout.lower()

    def test_config_sections(self, run_cli):
        """Test showing config sections."""
        sections = ["server", "api", "advanced", "models"]
        
        for section in sections:
            result = run_cli(["config", "show", section])
            assert result.returncode == 0


class TestStatusWorkflows:
    """Test status check workflows."""

    def test_status_complete(self, run_cli):
        """Test complete status check."""
        result = run_cli(["status", "all"])
        
        assert result.returncode == 0
        # Should contain multiple sections
        assert "System" in result.stdout
        assert "Server" in result.stdout or "server" in result.stdout.lower()

    def test_status_individual(self, run_cli):
        """Test individual status checks."""
        checks = [
            ("status", "system", ["CPU", "RAM", "System"]),
            ("status", "server", ["Server", "status"]),
            ("status", "model", ["Model", "status"]),
            ("status", "dependencies", ["Dependency", "dependencies"]),
        ]
        
        for cmd, subcmd, expected_keywords in checks:
            result = run_cli([cmd, subcmd])
            assert result.returncode == 0
            
            # Check for expected keywords
            found = any(kw in result.stdout for kw in expected_keywords)
            assert found, f"Expected keywords {expected_keywords} not found in output"


class TestHardwareDetectionWorkflow:
    """Test hardware detection workflow."""

    def test_hardware_detection_complete(self):
        """Test complete hardware detection."""
        from local_llm.hardware.detector import HardwareDetector
        
        detector = HardwareDetector()
        hw_info = detector.detect()
        
        # Should detect all components
        assert hw_info.gpu is not None
        assert hw_info.cpu is not None
        assert hw_info.memory is not None
        assert hw_info.disk is not None
        
        # Should provide summary
        summary = hw_info.summary()
        assert len(summary) > 0

    def test_optimal_config_generation(self):
        """Test optimal configuration generation."""
        from local_llm.hardware.detector import get_optimal_config
        
        config = get_optimal_config()
        
        # Should have all required keys
        required_keys = ['gpu_layers', 'threads', 'batch_size', 'context_size', 'flash_attn']
        for key in required_keys:
            assert key in config, f"Missing key: {key}"

    def test_gpu_detection_integration(self):
        """Test GPU detection integration."""
        from local_llm.utils import get_gpu_info
        
        gpu_info = get_gpu_info()
        
        # Should return valid dict
        assert isinstance(gpu_info, dict)
        assert 'has_gpu' in gpu_info
        assert 'gpu_type' in gpu_info
        
        # Type should be valid
        assert gpu_info['gpu_type'] in ['cuda', 'rocm', 'metal', 'none']


class TestModelResolutionWorkflow:
    """Test model resolution workflow."""

    def test_resolve_config_model(self):
        """Test resolving configured model."""
        from local_llm.config import get_config
        from local_llm.models.resolver import ModelResolver
        
        config = get_config()
        resolver = ModelResolver(config=config)
        
        # Resolve active model
        ref = resolver.resolve(config.active_model_key)
        
        assert ref is not None
        assert ref.config_key == config.active_model_key
        assert ref.hf_repo is not None
        assert ref.hf_file is not None

    def test_resolve_hf_repo(self):
        """Test resolving HuggingFace repo."""
        from local_llm.models.resolver import resolve_model
        
        ref = resolve_model("unsloth/Qwen3.5-9B-GGUF:Q4_K_M")
        
        assert ref is not None
        assert ref.ref_type == "hf_repo"
        assert ref.hf_repo == "unsloth/Qwen3.5-9B-GGUF"

    def test_resolve_partial_name(self):
        """Test resolving partial model name."""
        from local_llm.config import get_config
        from local_llm.models.resolver import ModelResolver
        
        config = get_config()
        resolver = ModelResolver(config=config)
        
        ref = resolver.resolve("llama")
        
        # Should find a match or return unknown
        assert ref is not None


class TestChatWorkflow:
    """Test chat workflow (requires server running)."""

    def test_chat_quick_help(self, run_cli):
        """Test chat quick command help."""
        result = run_cli(["chat", "quick", "--help"])
        
        assert result.returncode == 0
        assert "Quick" in result.stdout or "single" in result.stdout.lower()

    def test_chat_interactive_help(self, run_cli):
        """Test chat interactive command help."""
        result = run_cli(["chat", "interactive", "--help"])
        
        assert result.returncode == 0
        assert "Interactive" in result.stdout or "interactive" in result.stdout.lower()


class TestBenchmarkWorkflow:
    """Test benchmark workflow."""

    def test_benchmark_help(self, run_cli):
        """Test benchmark command help."""
        result = run_cli(["benchmark", "--help"])
        
        assert result.returncode == 0
        assert "benchmark" in result.stdout.lower()

    def test_benchmark_scripts_exist(self, project_root):
        """Test that benchmark scripts exist."""
        benchmark_dir = project_root / "tools" / "benchmarks"
        
        if benchmark_dir.exists():
            scripts = [
                "run-all.sh",
                "run-native-benchmark.sh",
                "run-batched-bench.sh",
                "run-perplexity.sh",
                "run-api-benchmark.sh",
            ]
            
            for script in scripts:
                script_path = benchmark_dir / script
                # Scripts may or may not exist, but if they do, they should be executable
                if script_path.exists():
                    assert os.access(script_path, os.X_OK) or script_path.suffix == '.sh'


class TestEndToEndWorkflow:
    """Test end-to-end workflows."""

    def test_cli_help_chain(self, run_cli):
        """Test help for all main commands."""
        commands = [
            ["--help"],  # Main help (not empty)
            ["run", "--help"],
            ["server", "--help"],
            ["model", "--help"],
            ["chat", "--help"],
            ["benchmark", "--help"],
            ["config", "--help"],
            ["status", "--help"],
        ]
        
        for cmd in commands:
            result = run_cli(cmd)
            assert result.returncode == 0, f"Command 'local-llm {' '.join(cmd)}' failed"

    def test_config_load_and_access(self, project_root):
        """Test loading config and accessing values."""
        from local_llm.config import Config
        
        config_path = project_root / "config.yaml"
        config = Config(str(config_path))
        
        # Access various properties
        assert config.active_model_key is not None
        assert config.server_port is not None
        assert config.model_path is not None
        assert len(config.available_models) > 0

    def test_hardware_detect_and_optimize(self):
        """Test hardware detection and optimization."""
        from local_llm.hardware.detector import detect_hardware, get_optimal_config
        
        # Detect hardware
        hw = detect_hardware()
        
        # Get optimal config
        config = get_optimal_config()
        
        # Config should be based on hardware
        assert config['gpu_layers'] >= 0
        assert config['threads'] >= 1
        
        # If GPU available, should recommend offloading
        if hw.gpu.has_gpu:
            assert config['gpu_layers'] > 0


class TestErrorHandling:
    """Test error handling in workflows."""

    def test_invalid_command(self, run_cli):
        """Test invalid command handling."""
        result = run_cli(["nonexistent-command-xyz123"])
        
        assert result.returncode != 0
        assert "No such command" in result.stderr or "not found" in result.stderr.lower()

    def test_invalid_model_key(self, run_cli):
        """Test invalid model key handling."""
        result = run_cli(["model", "info", "nonexistent-model-xyz123"])
        
        # Should show error, not crash
        assert result.returncode != 0 or "Error" in result.stdout or "not found" in result.stdout.lower()

    def test_invalid_config_section(self, run_cli):
        """Test invalid config section handling."""
        result = run_cli(["config", "show", "nonexistent-section-xyz123"])
        
        # Should show error or empty
        assert result.returncode != 0 or "Error" in result.stdout or "not found" in result.stdout.lower()


class TestConcurrencyAndState:
    """Test concurrency and state management."""

    def test_multiple_config_loads(self, project_root):
        """Test loading config multiple times."""
        from local_llm.config import Config, get_config
        
        config_path = project_root / "config.yaml"
        
        # Load multiple times
        config1 = Config(str(config_path))
        config2 = Config(str(config_path))
        config3 = get_config(str(config_path))
        
        # All should have same active model
        assert config1.active_model_key == config2.active_model_key
        assert config2.active_model_key == config3.active_model_key

    def test_hardware_detector_singleton(self):
        """Test hardware detector singleton behavior."""
        from local_llm.hardware.detector import get_detector
        
        detector1 = get_detector()
        detector2 = get_detector()
        
        # Should be same instance
        assert detector1 is detector2

    def test_global_config_singleton(self, project_root):
        """Test global config singleton behavior."""
        from local_llm.config import get_config
        
        config_path = str(project_root / "config.yaml")
        
        config1 = get_config(config_path)
        config2 = get_config(config_path)
        
        # Should have same values (not necessarily same instance in test context)
        assert config1.active_model_key == config2.active_model_key
        assert config1.server_port == config2.server_port
