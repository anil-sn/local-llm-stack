#!/usr/bin/env bash
#
# YAML Configuration Loader for Shell Scripts
# Reads config.yaml and exports variables for use in shell scripts
# Supports multiple models - loads the active_model configuration
#
# Usage: source scripts/config.sh
#

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$PROJECT_ROOT/config.yaml"
VENV_DIR="$PROJECT_ROOT/.venv"

# Function to resolve paths (expand $HOME and ./)
resolve_path() {
    local path="$1"
    path="${path/\$HOME/$HOME}"
    if [[ "$path" == ./* ]]; then
        path="$PROJECT_ROOT/${path:2}"
    fi
    echo "$path"
}

# Load configuration using Python (with venv if available)
load_config() {
    if [ ! -f "$CONFIG_FILE" ]; then
        echo "⚠️  Warning: config.yaml not found at $CONFIG_FILE" >&2
        return 1
    fi
    
    # Determine which Python to use
    PYTHON_CMD="python3"
    if [ -d "$VENV_DIR" ] && [ -f "$VENV_DIR/bin/python" ]; then
        PYTHON_CMD="$VENV_DIR/bin/python"
    fi
    
    # Use Python to parse YAML and export variables
    eval "$($PYTHON_CMD << 'PYTHON_EOF'
import yaml
import os
import sys

config_file = os.environ.get('CONFIG_FILE', 'config.yaml')

try:
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    # Get active model
    active_model_key = config.get('active_model', 'qwen-35b-a3b')
    models = config.get('models', {})
    model = models.get(active_model_key, {})
    
    # Helper to escape strings for bash
    def escape(s):
        if s is None:
            return ''
        return str(s).replace("'", "'\\''")
    
    # Export active model info
    print(f"export ACTIVE_MODEL='{escape(active_model_key)}'")
    print(f"export MODEL_NAME='{escape(model.get('name', ''))}'")
    # Extract directory from path, or use default
    model_path = model.get('path', '$HOME/models/' + model.get('name', ''))
    model_dir = str(model_path).rsplit('/', 1)[0] if '/' in str(model_path) else '$HOME/models'
    print(f"export MODEL_DIR='{escape(model_dir)}'")
    print(f"export MODEL_PATH='{escape(model_path)}'")
    print(f"export HF_REPO='{escape(model.get('hf_repo', ''))}'")
    print(f"export HF_FILE='{escape(model.get('hf_file', ''))}'")
    print(f"export MODEL_SIZE_GB='{escape(model.get('size_gb', 0))}'")
    print(f"export MODEL_RAM_GB='{escape(model.get('ram_required_gb', 0))}'")
    print(f"export MODEL_DESCRIPTION='{escape(model.get('description', ''))}'")
    
    # Server config
    server = config.get('server', {})
    print(f"export SERVER_PORT='{escape(server.get('port', 8080))}'")
    print(f"export SERVER_HOST='{escape(server.get('host', '0.0.0.0'))}'")
    print(f"export CONTEXT_SIZE='{escape(server.get('context_size', 131072))}'")
    print(f"export GPU_LAYERS='{escape(server.get('gpu_layers', 999))}'")
    print(f"export BATCH_SIZE='{escape(server.get('batch_size', 512))}'")
    print(f"export UBATCH_SIZE='{escape(server.get('ubatch_size', 256))}'")
    print(f"export FLASH_ATTN='{escape(server.get('flash_attn', 'auto'))}'")
    
    # Reasoning config
    reasoning = config.get('reasoning', {})
    print(f"export REASONING_FORMAT='{escape(reasoning.get('format', 'none'))}'")
    print(f"export REASONING_BUDGET='{escape(reasoning.get('budget', 0))}'")
    print(f"export ENABLE_THINKING='{escape(reasoning.get('enable_thinking', False))}'")
    
    # API config
    api = config.get('api', {})
    print(f"export API_BASE_URL='{escape(api.get('base_url', 'http://localhost:8080/v1'))}'")
    print(f"export API_KEY='{escape(api.get('key', 'not-needed'))}'")
    
    # Paths
    paths = config.get('paths', {})
    print(f"export INSTALL_DIR='{escape(paths.get('install_dir', '/usr/local/bin'))}'")
    print(f"export BUILD_DIR='{escape(paths.get('build_dir', '$HOME/llama.cpp'))}'")
    print(f"export LOG_FILE='{escape(paths.get('log_file', '/tmp/llama-server.log'))}'")
    print(f"export PID_FILE='{escape(paths.get('pid_file', '/tmp/llama-server.pid'))}'")
    print(f"export VENV_DIR='{escape(paths.get('venv_dir', './.venv'))}'")
    print(f"export BENCHMARK_DIR='{escape(paths.get('benchmark_dir', './benchmarks'))}'")
    
    # Benchmarks
    benchmarks = config.get('benchmarks', {})
    print(f"export BENCH_REPETITIONS='{escape(benchmarks.get('repetitions', 3))}'")
    
    # System
    system = config.get('system', {})
    print(f"export MIN_RAM_GB='{escape(system.get('min_ram_gb', 16))}'")
    print(f"export RECOMMENDED_RAM_GB='{escape(system.get('recommended_ram_gb', 32))}'")
    print(f"export MIN_DISK_GB='{escape(system.get('min_disk_gb', 25))}'")
    
    # Features
    features = config.get('features', {})
    print(f"export ENABLE_WEBUI='{escape(features.get('enable_webui', True))}'")
    print(f"export ENABLE_CHAT_CLI='{escape(features.get('enable_chat_cli', True))}'")
    print(f"export ENABLE_AGENT='{escape(features.get('enable_agent', True))}'")
    print(f"export ENABLE_BENCHMARKS='{escape(features.get('enable_benchmarks', True))}'")
    
    # Advanced
    advanced = config.get('advanced', {})
    print(f"export TEMPERATURE='{escape(advanced.get('temperature', 0.7))}'")
    print(f"export TOP_P='{escape(advanced.get('top_p', 0.9))}'")
    print(f"export REPEAT_PENALTY='{escape(advanced.get('repeat_penalty', 1.1))}'")
    print(f"export MAX_TOKENS='{escape(advanced.get('max_tokens', -1))}'")

except Exception as e:
    print(f"echo 'Error loading config: {e}' >&2", file=sys.stderr)
    sys.exit(1)
PYTHON_EOF
)"
}

# Set CONFIG_FILE for Python script
export CONFIG_FILE="$CONFIG_FILE"

# Load configuration
load_config

# Resolve paths
export MODEL_DIR=$(resolve_path "$MODEL_DIR")
export MODEL_PATH=$(resolve_path "$MODEL_PATH")
export BUILD_DIR=$(resolve_path "$BUILD_DIR")
export VENV_DIR=$(resolve_path "$VENV_DIR")
export BENCHMARK_DIR=$(resolve_path "$BENCHMARK_DIR")
