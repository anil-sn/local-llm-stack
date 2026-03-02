#!/usr/bin/env python3
"""
Configuration loader for Qwen3.5-35B-A3B and other models
Loads settings from config.yaml and provides access to all configuration values
Supports multiple models - automatically loads the active_model configuration
"""

import os
import yaml
from pathlib import Path
from typing import Any, Optional, Dict

class Config:
    """Configuration manager that loads and provides access to config.yaml"""
    
    _instance: Optional['Config'] = None
    _config: dict = {}
    _active_model: dict = {}
    _loaded: bool = False
    
    def __new__(cls) -> 'Config':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._loaded:
            self.load()
    
    @classmethod
    def get_project_root(cls) -> Path:
        """Get the project root directory"""
        # Go up two levels from src/python/
        return Path(__file__).parent.parent.parent
    
    @classmethod
    def get_config_path(cls) -> Path:
        """Get the path to config.yaml"""
        return cls.get_project_root() / 'config.yaml'
    
    def load(self) -> None:
        """Load configuration from config.yaml"""
        config_path = self.get_config_path()
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            self._config = yaml.safe_load(f)
        
        # Load active model configuration
        self._load_active_model()
        
        # Resolve paths
        self._resolve_paths()
        self._loaded = True
    
    def _load_active_model(self) -> None:
        """Load the active model configuration"""
        active_key = self._config.get('active_model', 'qwen-35b-a3b')
        models = self._config.get('models', {})
        
        if active_key not in models:
            raise ValueError(f"Active model '{active_key}' not found in models list")
        
        self._active_model = models[active_key]
        self._active_model['key'] = active_key
    
    def _resolve_paths(self) -> None:
        """Resolve environment variables in paths"""
        home = str(Path.home())
        project_root = str(self.get_project_root())
        
        # Resolve model path
        if 'path' in self._active_model:
            path = self._active_model['path']
            path = path.replace('$HOME', home)
            if path.startswith('./'):
                path = str(Path(project_root) / path[2:])
            self._active_model['path'] = path
        
        # Resolve model dir
        if 'dir' in self._active_model:
            path = self._active_model['dir']
            path = path.replace('$HOME', home)
            if path.startswith('./'):
                path = str(Path(project_root) / path[2:])
            self._active_model['dir'] = path
        
        # Resolve other paths
        if 'paths' in self._config:
            paths = self._config['paths']
            for key in ['build_dir', 'venv_dir', 'benchmark_dir']:
                if key in paths:
                    path = paths[key]
                    path = path.replace('$HOME', home)
                    if path.startswith('./'):
                        path = str(Path(project_root) / path[2:])
                    paths[key] = path
    
    def get(self, *keys, default: Any = None) -> Any:
        """
        Get a configuration value by nested keys
        
        Example:
            config.get('server', 'port')
            config.get('paths', 'log_file', default='/tmp/log.txt')
        """
        value = self._config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def get_model(self, key: str, default: Any = None) -> Any:
        """Get active model configuration"""
        return self._active_model.get(key, default)
    
    def get_server(self, key: str, default: Any = None) -> Any:
        """Get server configuration"""
        return self.get('server', key, default=default)
    
    def get_reasoning(self, key: str, default: Any = None) -> Any:
        """Get reasoning configuration"""
        return self.get('reasoning', key, default=default)
    
    def get_paths(self, key: str, default: Any = None) -> Any:
        """Get path configuration"""
        return self.get('paths', key, default=default)
    
    def get_benchmarks(self, key: str, default: Any = None) -> Any:
        """Get benchmark configuration"""
        return self.get('benchmarks', key, default=default)
    
    def get_features(self, key: str, default: Any = None) -> Any:
        """Get feature configuration"""
        return self.get('features', key, default=default)
    
    def get_advanced(self, key: str, default: Any = None) -> Any:
        """Get advanced configuration"""
        return self.get('advanced', key, default=default)
    
    def get_model_path(self) -> str:
        """Get full model path"""
        return self.get_model('path', '')
    
    def get_model_dir(self) -> str:
        """Get model directory"""
        return self.get_model('dir', str(Path.home() / 'models'))
    
    def get_model_name(self) -> str:
        """Get model filename"""
        return self.get_model('name', '')
    
    def get_model_key(self) -> str:
        """Get active model key"""
        return self._active_model.get('key', 'unknown')
    
    def get_model_size_gb(self) -> int:
        """Get model size in GB"""
        return self.get_model('size_gb', 0)
    
    def get_model_ram_gb(self) -> int:
        """Get required RAM in GB"""
        return self.get_model('ram_required_gb', 0)
    
    def get_model_description(self) -> str:
        """Get model description"""
        return self.get_model('description', '')
    
    def get_server_url(self) -> str:
        """Get server base URL"""
        port = self.get_server('port', 8080)
        return f"http://localhost:{port}"
    
    def get_api_url(self) -> str:
        """Get API base URL"""
        return self.get('api', 'base_url', default=f"{self.get_server_url()}/v1")
    
    def get_hf_repo(self) -> str:
        """Get HuggingFace repository"""
        return self.get_model('hf_repo', '')
    
    def get_hf_file(self) -> str:
        """Get HuggingFace filename"""
        return self.get_model('hf_file', '')
    
    def list_models(self) -> Dict[str, dict]:
        """Get list of all available models"""
        return self._config.get('models', {})
    
    def get_active_model_key(self) -> str:
        """Get the active model key"""
        return self._config.get('active_model', 'qwen-35b-a3b')
    
    def set_active_model(self, model_key: str) -> bool:
        """
        Set active model by key
        
        Example:
            config.set_active_model('llama-3-70b')
        """
        models = self._config.get('models', {})
        if model_key not in models:
            return False
        
        self._config['active_model'] = model_key
        self._active_model = models[model_key]
        self._active_model['key'] = model_key
        self._resolve_paths()
        return True
    
    def to_dict(self) -> dict:
        """Get entire configuration as dictionary"""
        return self._config.copy()
    
    def reload(self) -> None:
        """Reload configuration from file"""
        self._loaded = False
        self.load()

    def validate(self) -> list:
        """
        Validate configuration and return list of errors/warnings
        
        Returns:
            list: List of error/warning messages
        """
        issues = []
        
        # Check model path exists
        model_path = self.get_model_path()
        if model_path and not os.path.exists(model_path):
            issues.append(f"⚠️  Model file not found: {model_path}")
        
        # Check server port is valid
        port = self.get_server('port')
        if port:
            if not isinstance(port, int) or port < 1 or port > 65535:
                issues.append(f"❌ Invalid server port: {port} (must be 1-65535)")
            elif port < 1024:
                issues.append(f"⚠️  Port {port} requires root privileges (consider using port > 1024)")
        
        # Check context size
        context_size = self.get_server('context_size')
        if context_size:
            if not isinstance(context_size, int) or context_size < 512:
                issues.append(f"❌ Invalid context size: {context_size} (minimum: 512)")
            elif context_size > 262144:
                issues.append(f"⚠️  Large context size {context_size} may cause memory issues")
        
        # Check GPU layers
        gpu_layers = self.get_server('gpu_layers')
        if gpu_layers is not None:
            if not isinstance(gpu_layers, int) or gpu_layers < 0:
                issues.append(f"❌ Invalid GPU layers: {gpu_layers} (must be >= 0)")
        
        # Check batch sizes
        batch_size = self.get_server('batch_size')
        ubatch_size = self.get_server('ubatch_size')
        if batch_size and ubatch_size:
            if ubatch_size > batch_size:
                issues.append(f"⚠️  ubatch_size ({ubatch_size}) > batch_size ({batch_size}) may cause issues")
        
        # Check temperature
        temperature = self.get('advanced', 'temperature')
        if temperature is not None:
            if not isinstance(temperature, (int, float)) or temperature < 0 or temperature > 2:
                issues.append(f"❌ Invalid temperature: {temperature} (must be 0-2)")
        
        # Check reasoning configuration
        reasoning_format = self.get('reasoning', 'format')
        if reasoning_format and reasoning_format not in ['none', 'deepseek']:
            issues.append(f"⚠️  Unknown reasoning format: {reasoning_format} (use 'none' or 'deepseek')")
        
        # Check API base URL matches server port
        api_url = self.get('api', 'base_url')
        server_url = self.get_server_url()
        if api_url and server_url:
            expected_api_url = f"{server_url}/v1"
            if api_url != expected_api_url:
                issues.append(f"⚠️  API base_url ({api_url}) doesn't match server port ({server_url})")
        
        return issues


# Global configuration instance
config = Config()


# Convenience functions
def get(*keys, default=None):
    """Get configuration value"""
    return config.get(*keys, default=default)

def get_model_path():
    """Get model path"""
    return config.get_model_path()

def get_model_name():
    """Get model name"""
    return config.get_model_name()

def get_server_port():
    """Get server port"""
    return config.get_server('port', 8080)

def get_api_url():
    """Get API URL"""
    return config.get_api_url()

def list_models():
    """List all available models"""
    return config.list_models()

def get_active_model():
    """Get active model key"""
    return config.get_active_model_key()

def set_active_model(model_key: str):
    """Set active model"""
    return config.set_active_model(model_key)

def validate_config():
    """Validate configuration and return list of issues"""
    return config.validate()


if __name__ == '__main__':
    # Test configuration loading
    print("╔══════════════════════════════════════════════════════════╗")
    print("║         Configuration Loaded Successfully! ✅            ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    print(f"Active Model: {get_active_model()}")
    print(f"Model Name: {get_model_name()}")
    print(f"Model Path: {get_model_path()}")
    print(f"Model Size: {config.get_model_size_gb()} GB")
    print(f"RAM Required: {config.get_model_ram_gb()} GB")
    print(f"Description: {config.get_model_description()}")
    print()
    print(f"Server Port: {get_server_port()}")
    print(f"API URL: {get_api_url()}")
    print()
    
    # Validate configuration
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    print("🔍 Configuration Validation:")
    issues = validate_config()
    if not issues:
        print("   ✅ No issues found")
    else:
        for issue in issues:
            print(f"   {issue}")
    print()
    
    print("Available Models:")
    for key, model in list_models().items():
        marker = "●" if key == get_active_model() else "○"
        print(f"  {marker} {key}: {model.get('description', 'N/A')}")
