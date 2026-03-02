"""
Configuration management for Local LLM Stack.

Handles loading, validating, and accessing configuration from config.yaml.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from local_llm.utils import expand_path, get_platform


class ConfigError(Exception):
    """Configuration error exception."""
    pass


class Config:
    """
    Configuration manager for Local LLM Stack.
    
    Provides type-safe access to configuration values with
    proper defaults and validation.
    """
    
    DEFAULT_CONFIG_PATH = "config.yaml"
    
    def __init__(self, config_path: Optional[str] = None, base_dir: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to config.yaml (uses default if None)
            base_dir: Base directory for resolving relative paths
        """
        # Determine base directory (project root)
        if base_dir is None:
            # Try to find project root by looking for config.yaml
            possible_roots = [
                Path(__file__).parent.parent.parent.parent,  # src/local_llm -> project root
                Path.cwd(),
            ]
            for root in possible_roots:
                if (root / "config.yaml").exists():
                    base_dir = str(root)
                    break
            if base_dir is None:
                base_dir = str(Path.cwd())
        
        self._base_dir = base_dir
        self._config_path = config_path or self.DEFAULT_CONFIG_PATH
        self._config_path = expand_path(self._config_path, self._base_dir)
        self._config: Dict[str, Any] = {}
        self._active_model_config: Dict[str, Any] = {}
        self._load()
    
    def _load(self) -> None:
        """Load configuration from YAML file."""
        if not os.path.exists(self._config_path):
            raise ConfigError(f"Configuration file not found: {self._config_path}")
        
        try:
            with open(self._config_path, "r") as f:
                self._config = yaml.safe_load(f) or {}
            
            # Load active model configuration
            self._load_active_model()
            
        except yaml.YAMLError as e:
            raise ConfigError(f"Invalid YAML in config file: {e}")
        except IOError as e:
            raise ConfigError(f"Error reading config file: {e}")
    
    def _load_active_model(self) -> None:
        """Load the active model configuration."""
        active_model_key = self.get("active_model", default="qwen-35b-a3b")
        models = self.get("models", default={})

        if active_model_key not in models:
            available = list(models.keys())
            raise ConfigError(
                f"Active model '{active_model_key}' not found in config. "
                f"Available models: {available}"
            )

        self._active_model_config = models[active_model_key]
    
    def get(self, *keys: str, default: Any = None) -> Any:
        """
        Get a configuration value by nested keys.
        
        Args:
            *keys: Nested keys to traverse (e.g., "server", "port")
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        value = self._config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def get_model(self, model_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Get configuration for a specific model.
        
        Args:
            model_key: Model key (uses active model if None)
        
        Returns:
            Model configuration dictionary
        """
        if model_key is None:
            return self._active_model_config
        
        models = self.get("models", default={})
        if model_key not in models:
            raise ConfigError(f"Model '{model_key}' not found in config")
        
        return models[model_key]
    
    @property
    def active_model_key(self) -> str:
        """Get the active model key."""
        return self.get("active_model", default="qwen-35b-a3b")

    @property
    def active_model_name(self) -> str:
        """Get the active model name."""
        return self._active_model_config.get("name", "Unknown")
    
    @property
    def model_path(self) -> str:
        """Get the expanded path to the active model."""
        path = self._active_model_config.get("path", "")
        return expand_path(path, os.path.dirname(self._config_path))
    
    @property
    def model_exists(self) -> bool:
        """Check if the active model file exists."""
        return os.path.isfile(self.model_path)
    
    # Server configuration
    @property
    def server_port(self) -> int:
        """Get server port."""
        return int(self.get("server", "port", default=8081))
    
    @property
    def server_host(self) -> str:
        """Get server host."""
        return self.get("server", "host", default="0.0.0.0")
    
    @property
    def context_size(self) -> int:
        """Get context size."""
        return int(self.get("server", "context_size", default=131072))
    
    @property
    def gpu_layers(self) -> int:
        """Get GPU layers for offloading."""
        return int(self.get("server", "gpu_layers", default=999))
    
    @property
    def batch_size(self) -> int:
        """Get batch size."""
        return int(self.get("server", "batch_size", default=512))
    
    @property
    def ubatch_size(self) -> int:
        """Get micro-batch size."""
        return int(self.get("server", "ubatch_size", default=256))
    
    @property
    def flash_attn(self) -> str:
        """Get flash attention setting."""
        return self.get("server", "flash_attn", default="auto")
    
    @property
    def threads(self) -> Optional[int]:
        """Get thread count (None = auto-detect)."""
        return self.get("server", "threads", default=None)
    
    # API configuration
    @property
    def api_base_url(self) -> str:
        """Get API base URL."""
        return self.get("api", "base_url", default=f"http://localhost:{self.server_port}/v1")
    
    @property
    def api_key(self) -> str:
        """Get API key."""
        return self.get("api", "key", default="not-needed")
    
    # Advanced settings
    @property
    def temperature(self) -> float:
        """Get temperature setting."""
        return float(self.get("advanced", "temperature", default=0.7))
    
    @property
    def top_p(self) -> float:
        """Get top_p setting."""
        return float(self.get("advanced", "top_p", default=0.9))
    
    @property
    def repeat_penalty(self) -> float:
        """Get repeat penalty setting."""
        return float(self.get("advanced", "repeat_penalty", default=1.1))
    
    # Paths
    @property
    def log_file(self) -> str:
        """Get log file path."""
        path = self.get("paths", "log_file", default="/tmp/llama-server.log")
        return expand_path(path)
    
    @property
    def pid_file(self) -> str:
        """Get PID file path."""
        path = self.get("paths", "pid_file", default="/tmp/llama-server.pid")
        return expand_path(path)
    
    @property
    def venv_dir(self) -> str:
        """Get virtual environment directory."""
        path = self.get("paths", "venv_dir", default="./.venv")
        return expand_path(path, os.path.dirname(self._config_path))
    
    @property
    def benchmark_dir(self) -> str:
        """Get benchmark directory."""
        path = self.get("paths", "benchmark_dir", default="./benchmarks")
        return expand_path(path, os.path.dirname(self._config_path))
    
    # Reasoning configuration
    @property
    def reasoning_format(self) -> str:
        """Get reasoning format."""
        return self.get("reasoning", "format", default="none")
    
    @property
    def reasoning_budget(self) -> int:
        """Get reasoning token budget."""
        return int(self.get("reasoning", "budget", default=0))
    
    @property
    def enable_thinking(self) -> bool:
        """Check if thinking is enabled."""
        return self.get("reasoning", "enable_thinking", default=False)
    
    # Features
    @property
    def enable_webui(self) -> bool:
        """Check if WebUI is enabled."""
        return self.get("features", "enable_webui", default=True)
    
    @property
    def enable_chat_cli(self) -> bool:
        """Check if chat CLI is enabled."""
        return self.get("features", "enable_chat_cli", default=True)
    
    @property
    def enable_agent(self) -> bool:
        """Check if agent mode is enabled."""
        return self.get("features", "enable_agent", default=True)
    
    @property
    def enable_benchmarks(self) -> bool:
        """Check if benchmarks are enabled."""
        return self.get("features", "enable_benchmarks", default=True)
    
    # Claude Code integration
    @property
    def claude_code_enabled(self) -> bool:
        """Check if Claude Code integration is enabled."""
        return self.get("claude_code", "enabled", default=True)
    
    @property
    def claude_code_disable_telemetry(self) -> bool:
        """Check if Claude Code telemetry is disabled."""
        return self.get("claude_code", "disable_telemetry", default=True)
    
    @property
    def claude_code_auth_token(self) -> str:
        """Get Claude Code auth token."""
        return self.get("claude_code", "auth_token", default="dummy")
    
    @property
    def claude_code_timeout(self) -> int:
        """Get Claude Code timeout in seconds."""
        return int(self.get("claude_code", "timeout", default=300))
    
    @property
    def claude_code_max_tokens(self) -> int:
        """Get Claude Code max tokens."""
        return int(self.get("claude_code", "max_tokens", default=8192))
    
    @property
    def claude_code_alias(self) -> str:
        """Get Claude Code model alias."""
        return self.get("claude_code", "alias", default="")
    
    # Model list
    @property
    def available_models(self) -> List[str]:
        """Get list of available model keys."""
        return list(self.get("models", default={}).keys())
    
    def get_model_info(self, model_key: str) -> Dict[str, Any]:
        """
        Get detailed information about a model.
        
        Args:
            model_key: Model key
        
        Returns:
            Dictionary with model information
        """
        model = self.get_model(model_key)
        return {
            "key": model_key,
            "name": model.get("name", "Unknown"),
            "path": expand_path(model.get("path", ""), os.path.dirname(self._config_path)),
            "hf_repo": model.get("hf_repo", ""),
            "hf_file": model.get("hf_file", ""),
            "size_gb": model.get("size_gb", 0),
            "ram_required_gb": model.get("ram_required_gb", 0),
            "description": model.get("description", ""),
        }
    
    def reload(self) -> None:
        """Reload configuration from disk."""
        self._load()
    
    def __repr__(self) -> str:
        return f"Config(path={self._config_path!r}, model={self.active_model_key!r})"


# Global config instance (lazy-loaded)
_config: Optional[Config] = None


def get_config(config_path: Optional[str] = None) -> Config:
    """
    Get the global configuration instance.
    
    Args:
        config_path: Optional custom config path
    
    Returns:
        Config instance
    """
    global _config
    if _config is None or config_path is not None:
        _config = Config(config_path)
    return _config
