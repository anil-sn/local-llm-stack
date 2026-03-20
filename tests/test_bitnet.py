"""
Test BitNet support.

Tests for BitNet b1.58 model recognition, configuration, and optimization.
"""

import pytest
from pathlib import Path

from local_llm.models.resolver import ModelResolver, ModelReference
from local_llm.hardware.detector import get_optimal_config, HardwareDetector
from local_llm.config import get_config


class TestBitNetModelResolution:
    """Test BitNet model resolution."""

    @pytest.fixture
    def resolver(self, project_root):
        """Create model resolver with config."""
        config = get_config(str(project_root / "config.yaml"))
        return ModelResolver(config=config)

    def test_resolve_bitnet_2b_4t(self, resolver):
        """Test resolving bitnet-2b-4t model key."""
        ref = resolver.resolve("bitnet-2b-4t")
        
        assert ref is not None
        assert ref.config_key == "bitnet-2b-4t"
        assert ref.model_type == "bitnet"
        assert ref.is_bitnet() == True
        assert "microsoft" in ref.hf_repo.lower()

    def test_resolve_bitnet_large(self, resolver):
        """Test resolving bitnet-large model key."""
        ref = resolver.resolve("bitnet-large")
        
        assert ref is not None
        assert ref.config_key == "bitnet-large"
        assert ref.model_type == "bitnet"
        assert ref.is_bitnet() == True

    def test_resolve_bitnet_3b(self, resolver):
        """Test resolving bitnet-3b model key."""
        ref = resolver.resolve("bitnet-3b")
        
        assert ref is not None
        assert ref.config_key == "bitnet-3b"
        assert ref.model_type == "bitnet"
        assert ref.is_bitnet() == True

    def test_resolve_bitnet_partial(self, resolver):
        """Test resolving partial BitNet model name."""
        ref = resolver.resolve("bitnet")
        
        assert ref is not None
        # Should match first BitNet model
        assert ref.model_type == "bitnet"

    def test_resolve_bitnet_hf_repo(self, resolver):
        """Test resolving BitNet HuggingFace repo."""
        ref = resolver.resolve("microsoft/bitnet-b1.58-2B-4T-gguf")
        
        assert ref is not None
        assert ref.ref_type == "hf_repo"
        assert "microsoft" in ref.hf_repo.lower()
        assert "bitnet" in ref.hf_repo.lower()

    def test_bitnet_reference_is_bitnet(self):
        """Test ModelReference is_bitnet method."""
        ref = ModelReference(
            original="test",
            ref_type="config_key",
            config_key="bitnet-2b-4t",
            model_type="bitnet",
        )
        
        assert ref.is_bitnet() == True
        
        # Test standard model
        ref_standard = ModelReference(
            original="test",
            ref_type="config_key",
            config_key="llama-3-8b",
            model_type="standard",
        )
        
        assert ref_standard.is_bitnet() == False

    def test_bitnet_quantization_detection(self, resolver):
        """Test BitNet quantization type detection."""
        ref = resolver.resolve("bitnet-2b-4t")
        
        assert ref is not None
        assert ref.quantization is not None
        assert ref.quantization.lower() in ["i2_s", "tl1", "tl2"]

    def test_bitnet_to_dict(self, resolver):
        """Test BitNet model reference to_dict method."""
        ref = resolver.resolve("bitnet-2b-4t")
        
        ref_dict = ref.to_dict()
        
        assert isinstance(ref_dict, dict)
        assert ref_dict["model_type"] == "bitnet"
        assert ref_dict["config_key"] == "bitnet-2b-4t"
        assert "microsoft" in ref_dict["hf_repo"].lower()


class TestBitNetHardwareOptimization:
    """Test BitNet hardware optimization."""

    @pytest.fixture
    def detector(self):
        """Create hardware detector."""
        return HardwareDetector()

    def test_get_bitnet_config(self, detector):
        """Test getting BitNet-optimized configuration."""
        detector.detect()
        config = detector.get_optimal_config(model_type="bitnet")
        
        assert isinstance(config, dict)
        assert "use_bitnet_kernels" in config
        assert config["use_bitnet_kernels"] == True
        assert "bitnet_parallel_factor" in config

    def test_bitnet_vs_standard_config(self, detector):
        """Test BitNet config differs from standard."""
        detector.detect()
        
        bitnet_config = detector.get_optimal_config(model_type="bitnet")
        standard_config = detector.get_optimal_config(model_type="standard")
        
        # BitNet should use different settings
        assert bitnet_config["use_bitnet_kernels"] == True
        assert standard_config["use_bitnet_kernels"] == False
        
        # BitNet can handle larger batches
        assert bitnet_config["batch_size"] >= standard_config["batch_size"]

    def test_bitnet_cpu_optimization(self, detector):
        """Test BitNet CPU optimization."""
        detector.detect()
        config = detector.get_optimal_config(model_type="bitnet")
        
        # BitNet scales well with CPU threads
        assert config["threads"] >= 1
        
        # BitNet can use larger context
        assert config["context_size"] >= 16384

    def test_bitnet_gpu_layers(self, detector):
        """Test BitNet GPU layers setting."""
        detector.detect()
        config = detector.get_optimal_config(model_type="bitnet")
        
        # BitNet works great on CPU, so GPU layers may be reduced
        assert config["gpu_layers"] >= 0

    def test_get_optimal_config_function(self):
        """Test get_optimal_config convenience function."""
        config = get_optimal_config(model_type="bitnet")
        
        assert isinstance(config, dict)
        assert config["use_bitnet_kernels"] == True


class TestBitNetConfiguration:
    """Test BitNet configuration in config.yaml."""

    @pytest.fixture
    def config(self, project_root):
        """Load config."""
        return get_config(str(project_root / "config.yaml"))

    def test_bitnet_models_in_config(self, config):
        """Test BitNet models are in config."""
        bitnet_models = [
            key for key in config.available_models
            if config.get_model(key).get("model_type") == "bitnet"
        ]
        
        assert len(bitnet_models) >= 1
        assert "bitnet-2b-4t" in bitnet_models

    def test_bitnet_model_info(self, config):
        """Test BitNet model information."""
        model = config.get_model("bitnet-2b-4t")
        
        assert model is not None
        assert model.get("model_type") == "bitnet"
        assert model.get("quantization") == "i2_s"
        assert "microsoft" in model.get("hf_repo", "").lower()

    def test_bitnet_model_size(self, config):
        """Test BitNet model size is reasonable."""
        model = config.get_model("bitnet-2b-4t")
        
        # BitNet models should be small
        assert model.get("size_gb", 0) <= 3
        assert model.get("ram_required_gb", 0) <= 12

    def test_bitnet_model_path(self, config):
        """Test BitNet model path."""
        model_info = config.get_model_info("bitnet-2b-4t")
        
        assert "bitnet" in model_info["path"].lower()
        assert model_info["hf_repo"] == "microsoft/bitnet-b1.58-2B-4T-gguf"


class TestBitNetCLI:
    """Test BitNet CLI commands."""

    def test_bitnet_help(self, run_cli):
        """Test BitNet command help."""
        result = run_cli(["bitnet", "--help"])
        
        assert result.returncode == 0
        assert "BitNet" in result.stdout or "bitnet" in result.stdout.lower()

    def test_bitnet_list(self, run_cli):
        """Test BitNet list command."""
        result = run_cli(["bitnet", "list"])
        
        assert result.returncode == 0
        assert "BitNet" in result.stdout or "bitnet" in result.stdout.lower()

    def test_bitnet_info(self, run_cli):
        """Test BitNet info command."""
        result = run_cli(["bitnet", "info", "bitnet-2b-4t"])
        
        assert result.returncode == 0
        assert "BitNet" in result.stdout or "bitnet" in result.stdout.lower()

    def test_bitnet_recommend(self, run_cli):
        """Test BitNet recommend command."""
        result = run_cli(["bitnet", "recommend"])
        
        assert result.returncode == 0
        assert "BitNet" in result.stdout or "bitnet" in result.stdout.lower()

    def test_bitnet_download_help(self, run_cli):
        """Test BitNet download help."""
        result = run_cli(["bitnet", "download", "--help"])
        
        assert result.returncode == 0
        assert "download" in result.stdout.lower()


class TestBitNetIntegration:
    """Test BitNet integration."""

    def test_bitnet_end_to_end_resolution(self, project_root):
        """Test complete BitNet model resolution workflow."""
        config = get_config(str(project_root / "config.yaml"))
        resolver = ModelResolver(config=config)
        
        # Resolve model
        ref = resolver.resolve("bitnet-2b-4t")
        
        assert ref is not None
        assert ref.model_type == "bitnet"
        assert ref.hf_repo is not None
        assert ref.hf_file is not None
        
        # Get hardware config
        hw_config = get_optimal_config(model_type="bitnet")
        
        assert hw_config["use_bitnet_kernels"] == True
        assert hw_config["batch_size"] >= 512

    def test_bitnet_all_models_resolvable(self, project_root):
        """Test all configured BitNet models are resolvable."""
        config = get_config(str(project_root / "config.yaml"))
        resolver = ModelResolver(config=config)
        
        bitnet_models = [
            key for key in config.available_models
            if config.get_model(key).get("model_type") == "bitnet"
        ]
        
        for model_key in bitnet_models:
            ref = resolver.resolve(model_key)
            
            assert ref is not None, f"Failed to resolve {model_key}"
            assert ref.model_type == "bitnet", f"Wrong model type for {model_key}"

    def test_bitnet_config_validation(self, project_root):
        """Test BitNet configuration is valid."""
        config = get_config(str(project_root / "config.yaml"))
        
        bitnet_models = [
            key for key in config.available_models
            if config.get_model(key).get("model_type") == "bitnet"
        ]
        
        for model_key in bitnet_models:
            model = config.get_model(model_key)
            
            # Validate required fields
            assert "hf_repo" in model, f"Missing hf_repo for {model_key}"
            assert "hf_file" in model, f"Missing hf_file for {model_key}"
            assert "path" in model, f"Missing path for {model_key}"
            assert "size_gb" in model, f"Missing size_gb for {model_key}"
            assert "ram_required_gb" in model, f"Missing ram_required_gb for {model_key}"
            
            # Validate BitNet-specific fields
            assert model.get("model_type") == "bitnet", f"Wrong model_type for {model_key}"
            assert "quantization" in model, f"Missing quantization for {model_key}"
