"""
Test model resolution module.

Tests model identifier resolution without mocking.
"""

import pytest
from pathlib import Path

from local_llm.models.resolver import (
    ModelResolver,
    ModelReference,
    resolve_model,
)


class TestModelReference:
    """Test ModelReference dataclass."""

    def test_model_reference_defaults(self):
        """Test ModelReference default values."""
        ref = ModelReference(original="test", ref_type="unknown")
        
        assert ref.original == "test"
        assert ref.ref_type == "unknown"
        assert ref.hf_repo is None
        assert ref.hf_file is None
        assert ref.config_key is None

    def test_model_reference_with_values(self):
        """Test ModelReference with custom values."""
        ref = ModelReference(
            original="unsloth/Qwen3.5-9B-GGUF:Q4_K_M",
            ref_type="hf_repo",
            hf_repo="unsloth/Qwen3.5-9B-GGUF",
            hf_file="Qwen3.5-9B-UD-Q4_K_M.gguf",
            quantization="Q4_K_M",
        )
        
        assert ref.original == "unsloth/Qwen3.5-9B-GGUF:Q4_K_M"
        assert ref.ref_type == "hf_repo"
        assert ref.hf_repo == "unsloth/Qwen3.5-9B-GGUF"
        assert ref.quantization == "Q4_K_M"

    def test_model_reference_is_downloadable(self):
        """Test ModelReference is_downloadable method."""
        # Downloadable reference
        ref1 = ModelReference(
            original="test",
            ref_type="hf_repo",
            hf_repo="user/repo",
        )
        assert ref1.is_downloadable() == True
        
        # Non-downloadable reference
        ref2 = ModelReference(
            original="test",
            ref_type="config_key",
            config_key="llama-3-8b",
        )
        assert ref2.is_downloadable() == False
        
        # Unknown reference
        ref3 = ModelReference(
            original="test",
            ref_type="unknown",
        )
        assert ref3.is_downloadable() == False

    def test_model_reference_to_dict(self):
        """Test ModelReference to_dict method."""
        ref = ModelReference(
            original="test",
            ref_type="hf_repo",
            hf_repo="user/repo",
            hf_file="model.gguf",
        )
        
        ref_dict = ref.to_dict()
        
        assert isinstance(ref_dict, dict)
        assert ref_dict['original'] == "test"
        assert ref_dict['ref_type'] == "hf_repo"
        assert ref_dict['hf_repo'] == "user/repo"
        assert ref_dict['hf_file'] == "model.gguf"


class TestModelResolver:
    """Test ModelResolver class."""

    @pytest.fixture
    def resolver(self, project_root):
        """Create model resolver with config."""
        from local_llm.config import get_config
        config = get_config(str(project_root / "config.yaml"))
        return ModelResolver(config=config)

    def test_resolver_init(self, project_root):
        """Test resolver initialization."""
        from local_llm.config import get_config
        config = get_config(str(project_root / "config.yaml"))
        resolver = ModelResolver(config=config)
        
        assert resolver is not None
        assert resolver.config is not None

    def test_resolve_config_key(self, resolver):
        """Test resolving config model key."""
        ref = resolver.resolve("llama-3-8b")
        
        assert ref is not None
        assert ref.ref_type == "config_key"
        assert ref.config_key == "llama-3-8b"
        assert ref.hf_repo is not None
        assert ref.hf_file is not None

    def test_resolve_hf_repo_simple(self, resolver):
        """Test resolving HuggingFace repo reference."""
        ref = resolver.resolve("unsloth/Qwen3.5-9B-GGUF")
        
        assert ref is not None
        assert ref.ref_type == "hf_repo"
        assert ref.hf_repo == "unsloth/Qwen3.5-9B-GGUF"

    def test_resolve_hf_repo_with_quant(self, resolver):
        """Test resolving HF repo with quantization."""
        ref = resolver.resolve("unsloth/Qwen3.5-9B-GGUF:Q4_K_M")
        
        assert ref is not None
        assert ref.ref_type == "hf_repo"
        assert ref.hf_repo == "unsloth/Qwen3.5-9B-GGUF"
        assert ref.quantization is not None
        assert "Q4" in ref.quantization

    def test_resolve_hf_repo_with_file(self, resolver):
        """Test resolving HF repo with specific file."""
        ref = resolver.resolve("unsloth/Qwen3.5-9B-GGUF:Qwen3.5-9B-UD-Q4_K_M.gguf")
        
        assert ref is not None
        assert ref.ref_type == "hf_repo"
        assert ref.hf_repo == "unsloth/Qwen3.5-9B-GGUF"
        assert ref.hf_file is not None
        assert ref.hf_file.endswith(".gguf")

    def test_resolve_partial_match(self, resolver):
        """Test resolving partial model name."""
        ref = resolver.resolve("llama-3")
        
        assert ref is not None
        # Should match llama-3-8b or llama-3-70b
        assert ref.config_key is not None
        assert "llama" in ref.config_key.lower()

    def test_resolve_unknown(self, resolver):
        """Test resolving unknown model."""
        ref = resolver.resolve("nonexistent-model-xyz123")
        
        assert ref is not None
        assert ref.ref_type == "unknown"

    def test_resolve_url_pattern(self, resolver):
        """Test resolving HuggingFace URL pattern."""
        url = "https://huggingface.co/unsloth/Qwen3.5-9B-GGUF"
        ref = resolver.resolve(url)
        
        assert ref is not None
        assert ref.ref_type in ["url", "hf_repo"]
        assert ref.hf_repo is not None

    def test_resolve_mistral(self, resolver):
        """Test resolving mistral model."""
        ref = resolver.resolve("mistral-7b")
        
        assert ref is not None
        assert ref.config_key is not None
        assert "mistral" in ref.config_key.lower()

    def test_resolve_qwen(self, resolver):
        """Test resolving qwen model."""
        ref = resolver.resolve("qwen")
        
        assert ref is not None
        # Should match one of the qwen models
        assert "qwen" in ref.config_key.lower() or ref.ref_type == "unknown"


class TestModelResolverWithoutConfig:
    """Test ModelResolver without config."""

    @pytest.fixture
    def resolver_no_config(self):
        """Create model resolver without config."""
        return ModelResolver(config=None)

    def test_resolver_no_config(self, resolver_no_config):
        """Test resolver without config."""
        assert resolver_no_config.config is None

    def test_resolve_hf_repo_no_config(self, resolver_no_config):
        """Test resolving HF repo without config."""
        ref = resolver_no_config.resolve("unsloth/Qwen3.5-9B-GGUF:Q4_K_M")
        
        assert ref is not None
        assert ref.ref_type == "hf_repo"
        assert ref.hf_repo == "unsloth/Qwen3.5-9B-GGUF"

    def test_resolve_config_key_no_config(self, resolver_no_config):
        """Test resolving config key without config (should fail gracefully)."""
        ref = resolver_no_config.resolve("llama-3-8b")
        
        # Without config, should try to parse as HF repo or return unknown
        assert ref is not None
        assert ref.ref_type in ["unknown", "hf_repo"]

    def test_resolve_partial_no_config(self, resolver_no_config):
        """Test resolving partial match without config."""
        ref = resolver_no_config.resolve("llama")
        
        # Without config, should return unknown
        assert ref is not None
        assert ref.ref_type == "unknown"


class TestQuantizationExtraction:
    """Test quantization extraction."""

    @pytest.fixture
    def resolver(self, project_root):
        """Create model resolver with config."""
        from local_llm.config import get_config
        config = get_config(str(project_root / "config.yaml"))
        return ModelResolver(config=config)

    def test_extract_q4_k_m(self, resolver):
        """Test extracting Q4_K_M quantization."""
        ref = resolver.resolve("test:Q4_K_M")
        
        if ref.ref_type == "hf_repo":
            assert ref.quantization is not None
            assert "Q4" in ref.quantization

    def test_extract_q5_k_m(self, resolver):
        """Test extracting Q5_K_M quantization."""
        ref = resolver.resolve("test:Q5_K_M")
        
        if ref.ref_type == "hf_repo":
            assert ref.quantization is not None
            assert "Q5" in ref.quantization

    def test_extract_q6_k(self, resolver):
        """Test extracting Q6_K quantization."""
        ref = resolver.resolve("test:Q6_K")
        
        if ref.ref_type == "hf_repo":
            assert ref.quantization is not None
            assert "Q6" in ref.quantization

    def test_extract_q8(self, resolver):
        """Test extracting Q8 quantization."""
        ref = resolver.resolve("test:Q8_0")
        
        if ref.ref_type == "hf_repo":
            assert ref.quantization is not None
            assert "Q8" in ref.quantization

    def test_extract_from_filename(self, resolver):
        """Test extracting quantization from filename."""
        ref = resolver.resolve("test:Model-Q4_K_M.gguf")
        
        if ref.ref_type == "hf_repo":
            assert ref.hf_file is not None
            assert ref.hf_file.endswith(".gguf")
            assert ref.quantization is not None


class TestConvenienceFunction:
    """Test resolve_model convenience function."""

    def test_resolve_model_function(self, project_root):
        """Test resolve_model function."""
        from local_llm.config import get_config
        config = get_config(str(project_root / "config.yaml"))
        
        ref = resolve_model("llama-3-8b", config=config)
        
        assert ref is not None
        assert ref.config_key == "llama-3-8b"

    def test_resolve_model_without_config(self):
        """Test resolve_model function without config."""
        ref = resolve_model("unsloth/Qwen3.5-9B-GGUF")
        
        assert ref is not None
        assert ref.ref_type == "hf_repo"


class TestModelResolverEdgeCases:
    """Test edge cases in model resolution."""

    @pytest.fixture
    def resolver(self, project_root):
        """Create model resolver with config."""
        from local_llm.config import get_config
        config = get_config(str(project_root / "config.yaml"))
        return ModelResolver(config=config)

    def test_resolve_empty_string(self, resolver):
        """Test resolving empty string."""
        ref = resolver.resolve("")
        
        assert ref is not None
        # Empty string might match partial or be unknown
        assert ref.ref_type in ["unknown", "partial"]

    def test_resolve_whitespace(self, resolver):
        """Test resolving whitespace."""
        ref = resolver.resolve("   ")
        
        assert ref is not None
        # Whitespace might match partial or be unknown
        assert ref.ref_type in ["unknown", "partial"]

    def test_resolve_path_like(self, resolver):
        """Test resolving path-like string."""
        ref = resolver.resolve("/path/to/model.gguf")
        
        # Should not crash, should return unknown
        assert ref is not None
        assert ref.ref_type == "unknown"

    def test_resolve_malformed_repo(self, resolver):
        """Test resolving malformed repo reference."""
        ref = resolver.resolve("invalid/repo/format/here")
        
        # Should not crash
        assert ref is not None
        assert ref.ref_type == "unknown"

    def test_resolve_single_word(self, resolver):
        """Test resolving single word."""
        ref = resolver.resolve("qwen")
        
        # Should try partial match
        assert ref is not None

    def test_resolve_with_special_chars(self, resolver):
        """Test resolving with special characters."""
        ref = resolver.resolve("test-model_123")
        
        # Should not crash
        assert ref is not None

    def test_resolve_colon_only(self, resolver):
        """Test resolving colon only."""
        ref = resolver.resolve(":")
        
        # Should not crash
        assert ref is not None
        assert ref.ref_type == "unknown"


class TestListAvailableModels:
    """Test listing available models."""

    @pytest.fixture
    def resolver(self, project_root):
        """Create model resolver with config."""
        from local_llm.config import get_config
        config = get_config(str(project_root / "config.yaml"))
        return ModelResolver(config=config)

    def test_list_available_models(self, resolver):
        """Test listing available models."""
        models = resolver.list_available_models()
        
        assert isinstance(models, list)
        assert len(models) > 0
        
        for model in models:
            assert isinstance(model, dict)
            assert 'key' in model
            assert 'name' in model
            assert 'hf_repo' in model

    def test_list_models_without_config(self):
        """Test listing models without config."""
        resolver = ModelResolver(config=None)
        models = resolver.list_available_models()
        
        # Should return empty list
        assert isinstance(models, list)
        assert len(models) == 0


class TestSearchHuggingFace:
    """Test HuggingFace search (may be skipped if no network)."""

    @pytest.fixture
    def resolver(self, project_root):
        """Create model resolver with config."""
        from local_llm.config import get_config
        config = get_config(str(project_root / "config.yaml"))
        return ModelResolver(config=config)

    def test_search_huggingface_no_network(self, resolver):
        """Test search when huggingface_hub not installed."""
        # This should not crash even without network or package
        models = resolver.search_huggingface("llama", limit=5)
        
        # May return empty list if package not installed or no network
        assert isinstance(models, list)
