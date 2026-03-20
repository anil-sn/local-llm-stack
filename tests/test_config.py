"""
Test configuration management.

Tests config loading, validation, and access without mocking.
"""

import os
import pytest
import yaml
from pathlib import Path

from local_llm.config import Config, ConfigError, get_config


class TestConfigLoading:
    """Test configuration loading."""

    def test_load_default_config(self, project_root):
        """Test loading the default config.yaml."""
        config_path = project_root / "config.yaml"
        config = Config(str(config_path))
        
        assert config is not None
        assert config.active_model_key is not None
        assert len(config.available_models) > 0

    def test_load_invalid_path(self):
        """Test loading non-existent config file."""
        with pytest.raises(ConfigError) as exc_info:
            Config("/nonexistent/path/config.yaml")
        assert "not found" in str(exc_info.value).lower()

    def test_reload_config(self, project_root):
        """Test reloading configuration."""
        config_path = project_root / "config.yaml"
        config = Config(str(config_path))
        
        # Reload should work without errors
        config.reload()
        assert config.active_model_key is not None


class TestConfigAccess:
    """Test configuration value access."""

    @pytest.fixture
    def config(self, project_root):
        """Load config for testing."""
        config_path = project_root / "config.yaml"
        return Config(str(config_path))

    def test_get_nested_value(self, config):
        """Test getting nested configuration values."""
        port = config.get("server", "port")
        assert port is not None
        assert isinstance(port, int)

    def test_get_with_default(self, config):
        """Test getting value with default."""
        value = config.get("nonexistent", "key", default="default_value")
        assert value == "default_value"

    def test_active_model_key(self, config):
        """Test active model key property."""
        key = config.active_model_key
        assert key is not None
        assert key in config.available_models

    def test_active_model_name(self, config):
        """Test active model name property."""
        name = config.active_model_name
        assert name is not None
        assert len(name) > 0

    def test_model_path(self, config):
        """Test model path property."""
        path = config.model_path
        assert path is not None
        # Path should be expanded (no ~ or $HOME)
        assert "~" not in path
        assert "$" not in path

    def test_server_port(self, config):
        """Test server port property."""
        port = config.server_port
        assert port is not None
        assert isinstance(port, int)
        assert 1024 <= port <= 65535

    def test_server_host(self, config):
        """Test server host property."""
        host = config.server_host
        assert host is not None
        assert len(host) > 0

    def test_context_size(self, config):
        """Test context size property."""
        context = config.context_size
        assert context is not None
        assert isinstance(context, int)
        assert context > 0

    def test_gpu_layers(self, config):
        """Test GPU layers property."""
        layers = config.gpu_layers
        assert layers is not None
        assert isinstance(layers, int)
        assert layers >= 0

    def test_api_base_url(self, config):
        """Test API base URL property."""
        url = config.api_base_url
        assert url is not None
        assert url.startswith("http")
        assert "/v1" in url

    def test_api_key(self, config):
        """Test API key property."""
        key = config.api_key
        assert key is not None

    def test_temperature(self, config):
        """Test temperature property."""
        temp = config.temperature
        assert temp is not None
        assert isinstance(temp, float)
        assert 0.0 <= temp <= 2.0

    def test_top_p(self, config):
        """Test top_p property."""
        top_p = config.top_p
        assert top_p is not None
        assert isinstance(top_p, float)
        assert 0.0 <= top_p <= 1.0

    def test_repeat_penalty(self, config):
        """Test repeat penalty property."""
        penalty = config.repeat_penalty
        assert penalty is not None
        assert isinstance(penalty, float)
        assert penalty >= 0.0

    def test_available_models(self, config):
        """Test available models list."""
        models = config.available_models
        assert isinstance(models, list)
        assert len(models) > 0
        assert config.active_model_key in models

    def test_get_model(self, config):
        """Test getting specific model config."""
        model = config.get_model()
        assert model is not None
        assert isinstance(model, dict)
        assert "name" in model
        assert "path" in model

    def test_get_model_by_key(self, config):
        """Test getting model by key."""
        model_key = config.available_models[0]
        model = config.get_model(model_key)
        assert model is not None
        assert isinstance(model, dict)

    def test_get_model_invalid_key(self, config):
        """Test getting model with invalid key."""
        with pytest.raises(ConfigError):
            config.get_model("nonexistent_model_key")

    def test_get_model_info(self, config):
        """Test getting model info."""
        model_key = config.active_model_key
        info = config.get_model_info(model_key)
        
        assert info is not None
        assert isinstance(info, dict)
        assert "key" in info
        assert "name" in info
        assert "path" in info
        assert "hf_repo" in info
        assert "hf_file" in info
        assert "size_gb" in info
        assert "ram_required_gb" in info
        assert "description" in info


class TestConfigProperties:
    """Test various configuration properties."""

    @pytest.fixture
    def config(self, project_root):
        """Load config for testing."""
        config_path = project_root / "config.yaml"
        return Config(str(config_path))

    def test_batch_size(self, config):
        """Test batch size property."""
        batch_size = config.batch_size
        assert isinstance(batch_size, int)
        assert batch_size > 0

    def test_ubatch_size(self, config):
        """Test micro-batch size property."""
        ubatch_size = config.ubatch_size
        assert isinstance(ubatch_size, int)
        assert ubatch_size > 0

    def test_flash_attn(self, config):
        """Test flash attention property."""
        flash_attn = config.flash_attn
        assert flash_attn in ["auto", "on", "off"]

    def test_threads(self, config):
        """Test threads property."""
        threads = config.threads
        # Can be None (auto-detect) or positive int
        assert threads is None or (isinstance(threads, int) and threads > 0)

    def test_reasoning_format(self, config):
        """Test reasoning format property."""
        fmt = config.reasoning_format
        assert isinstance(fmt, str)

    def test_reasoning_budget(self, config):
        """Test reasoning budget property."""
        budget = config.reasoning_budget
        assert isinstance(budget, int)
        assert budget >= -1  # -1 = unlimited

    def test_enable_thinking(self, config):
        """Test enable thinking property."""
        thinking = config.enable_thinking
        assert isinstance(thinking, bool)

    def test_enable_webui(self, config):
        """Test enable WebUI property."""
        webui = config.enable_webui
        assert isinstance(webui, bool)

    def test_enable_chat_cli(self, config):
        """Test enable chat CLI property."""
        chat_cli = config.enable_chat_cli
        assert isinstance(chat_cli, bool)

    def test_enable_agent(self, config):
        """Test enable agent property."""
        agent = config.enable_agent
        assert isinstance(agent, bool)

    def test_enable_benchmarks(self, config):
        """Test enable benchmarks property."""
        benchmarks = config.enable_benchmarks
        assert isinstance(benchmarks, bool)

    def test_log_file(self, config):
        """Test log file path property."""
        log_file = config.log_file
        assert isinstance(log_file, str)
        assert os.path.isabs(log_file)

    def test_pid_file(self, config):
        """Test PID file path property."""
        pid_file = config.pid_file
        assert isinstance(pid_file, str)
        assert os.path.isabs(pid_file)

    def test_venv_dir(self, config):
        """Test virtual environment directory property."""
        venv_dir = config.venv_dir
        assert isinstance(venv_dir, str)

    def test_benchmark_dir(self, config):
        """Test benchmark directory property."""
        benchmark_dir = config.benchmark_dir
        assert isinstance(benchmark_dir, str)


class TestConfigValidation:
    """Test configuration validation."""

    @pytest.fixture
    def config(self, project_root):
        """Load config for testing."""
        config_path = project_root / "config.yaml"
        return Config(str(config_path))

    def test_yaml_syntax_valid(self, config):
        """Test that config.yaml has valid YAML syntax."""
        # If config loaded, YAML is valid
        assert config._config is not None

    def test_required_fields_present(self, config):
        """Test that required fields are present."""
        required = ["active_model", "models", "server", "api"]
        for field in required:
            assert field in config._config, f"Missing required field: {field}"

    def test_models_section_valid(self, config):
        """Test models section structure."""
        models = config.get("models")
        assert isinstance(models, dict)
        assert len(models) > 0

        for key, model_config in models.items():
            assert "name" in model_config, f"Model {key} missing 'name'"
            assert "path" in model_config, f"Model {key} missing 'path'"
            assert "hf_repo" in model_config, f"Model {key} missing 'hf_repo'"
            assert "hf_file" in model_config, f"Model {key} missing 'hf_file'"

    def test_server_section_valid(self, config):
        """Test server section structure."""
        server = config.get("server")
        assert isinstance(server, dict)
        assert "port" in server
        assert "host" in server
        assert "context_size" in server
        assert "gpu_layers" in server

    def test_api_section_valid(self, config):
        """Test API section structure."""
        api = config.get("api")
        assert isinstance(api, dict)
        assert "base_url" in api
        assert "key" in api


class TestGlobalConfig:
    """Test global config instance."""

    def test_get_config_singleton(self, project_root):
        """Test that get_config returns same instance."""
        config1 = get_config()
        config2 = get_config()
        assert config1 is config2

    def test_get_config_custom_path(self, project_root):
        """Test get_config with custom path."""
        config_path = project_root / "config.yaml"
        config = get_config(str(config_path))
        assert config is not None
        assert config.active_model_key is not None


class TestConfigEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_config_file(self, temp_dir):
        """Test loading empty config file."""
        empty_config = temp_dir / "empty.yaml"
        empty_config.write_text("")
        
        with pytest.raises(ConfigError) as exc_info:
            Config(str(empty_config))
        assert "not found" in str(exc_info.value).lower() or "Active model" in str(exc_info.value)

    def test_invalid_yaml_syntax(self, temp_dir):
        """Test loading config with invalid YAML."""
        invalid_config = temp_dir / "invalid.yaml"
        invalid_config.write_text("invalid: yaml: syntax: [")
        
        with pytest.raises(ConfigError) as exc_info:
            Config(str(invalid_config))
        assert "YAML" in str(exc_info.value) or "Invalid" in str(exc_info.value)

    def test_missing_active_model(self, temp_dir, project_root):
        """Test config with missing active model definition."""
        # Load original config
        with open(project_root / "config.yaml", "r") as f:
            config_data = yaml.safe_load(f)
        
        # Change active model to non-existent one
        config_data["active_model"] = "nonexistent_model"
        
        # Write modified config
        test_config = temp_dir / "test.yaml"
        with open(test_config, "w") as f:
            yaml.dump(config_data, f)
        
        with pytest.raises(ConfigError) as exc_info:
            Config(str(test_config))
        assert "not found" in str(exc_info.value).lower() or "Active model" in str(exc_info.value)
