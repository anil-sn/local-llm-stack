#!/usr/bin/env python3
"""
Generate .env file from config.yaml
Run this after changing config.yaml to update shell scripts
"""

import yaml
from pathlib import Path
import os

def generate_env():
    """Generate .env file from config.yaml"""
    project_root = Path(__file__).parent.parent
    config_path = project_root / "config.yaml"
    env_path = project_root / ".env"
    
    # Load config.yaml
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Get active model
    active_model_key = config.get('active_model', 'qwen-35b-a3b')
    models = config.get('models', {})
    model = models.get(active_model_key, {})
    
    # Extract model directory from path
    model_path = model.get('path', '$HOME/models/' + model.get('name', ''))
    model_dir = str(model_path).rsplit('/', 1)[0] if '/' in str(model_path) else '$HOME/models'
    
    # Server config
    server = config.get('server', {})
    reasoning = config.get('reasoning', {})
    api = config.get('api', {})
    paths = config.get('paths', {})
    advanced = config.get('advanced', {})
    
    env_content = f"""# Auto-generated from config.yaml
# DO NOT EDIT - Run 'python scripts/generate_env.py' to regenerate

# ═══════════════════════════════════════════════════════════
# MODEL CONFIGURATION
# ═══════════════════════════════════════════════════════════
ACTIVE_MODEL="{active_model_key}"
MODEL_NAME="{model.get('name', '')}"
MODEL_DIR="{model_dir}"
MODEL_PATH="{model_path}"
HF_REPO="{model.get('hf_repo', '')}"
HF_FILE="{model.get('hf_file', '')}"
MODEL_SIZE_GB="{model.get('size_gb', 0)}"
MODEL_RAM_GB="{model.get('ram_required_gb', 0)}"

# ═══════════════════════════════════════════════════════════
# SERVER CONFIGURATION
# ═══════════════════════════════════════════════════════════
SERVER_PORT="{server.get('port', 8081)}"
SERVER_HOST="{server.get('host', '0.0.0.0')}"
CONTEXT_SIZE="{server.get('context_size', 131072)}"
GPU_LAYERS="{server.get('gpu_layers', 999)}"
BATCH_SIZE="{server.get('batch_size', 512)}"
UBATCH_SIZE="{server.get('ubatch_size', 256)}"
FLASH_ATTN="{server.get('flash_attn', 'auto')}"

# ═══════════════════════════════════════════════════════════
# REASONING CONFIGURATION
# ═══════════════════════════════════════════════════════════
REASONING_FORMAT="{reasoning.get('format', 'none')}"
REASONING_BUDGET="{reasoning.get('budget', 0)}"
ENABLE_THINKING="{str(reasoning.get('enable_thinking', False)).lower()}"

# ═══════════════════════════════════════════════════════════
# API CONFIGURATION
# ═══════════════════════════════════════════════════════════
API_BASE_URL="{api.get('base_url', f'http://localhost:{server.get('port', 8081)}/v1')}"
API_KEY="{api.get('key', 'not-needed')}"

# ═══════════════════════════════════════════════════════════
# PATHS
# ═══════════════════════════════════════════════════════════
INSTALL_DIR="{paths.get('install_dir', '/usr/local/bin')}"
BUILD_DIR="{paths.get('build_dir', '$HOME/llama.cpp')}"
LOG_FILE="{paths.get('log_file', '/tmp/llama-server.log')}"
PID_FILE="{paths.get('pid_file', '/tmp/llama-server.pid')}"
VENV_DIR="{paths.get('venv_dir', './.venv')}"
BENCHMARK_DIR="{paths.get('benchmark_dir', './benchmarks')}"

# ═══════════════════════════════════════════════════════════
# ADVANCED OPTIONS
# ═══════════════════════════════════════════════════════════
TEMPERATURE="{advanced.get('temperature', 0.7)}"
TOP_P="{advanced.get('top_p', 0.9)}"
REPEAT_PENALTY="{advanced.get('repeat_penalty', 1.1)}"
MAX_TOKENS="{advanced.get('max_tokens', -1)}"
"""
    
    # Write .env file
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print(f"✅ Generated .env file at: {env_path}")
    print(f"   Active model: {active_model_key}")
    print(f"   Model path: {model_path}")
    print(f"   Server port: {server.get('port', 8081)}")
    print()
    print("📝 Note: This file is auto-generated from config.yaml")
    print("   Edit config.yaml and run 'python scripts/generate_env.py' to update")

if __name__ == "__main__":
    generate_env()
