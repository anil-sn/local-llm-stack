#!/usr/bin/env bash
#
# Load environment variables from .env file
# Usage: source scripts/load-env.sh
#

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Path to .env file
ENV_FILE="$PROJECT_ROOT/.env"

# Load .env file if it exists
if [ -f "$ENV_FILE" ]; then
    # Export all variables from .env
    set -a
    source "$ENV_FILE"
    set +a
    
    # Resolve paths
    if [[ "$MODEL_DIR" == \$HOME* ]]; then
        MODEL_DIR="${MODEL_DIR/\$HOME/$HOME}"
    fi
    
    if [[ "$MODEL_PATH" == \$HOME* ]]; then
        MODEL_PATH="${MODEL_PATH/\$HOME/$HOME}"
    fi
    
    if [[ "$VENV_DIR" != /* ]]; then
        VENV_DIR="$PROJECT_ROOT/$VENV_DIR"
    fi
    
    if [[ "$BENCHMARK_DIR" != /* ]]; then
        BENCHMARK_DIR="$PROJECT_ROOT/$BENCHMARK_DIR"
    fi
else
    # Set defaults if .env doesn't exist
    export MODEL_NAME="Qwen3.5-35B-A3B-UD-Q4_K_XL.gguf"
    export MODEL_DIR="$HOME/models"
    export MODEL_PATH="$MODEL_DIR/$MODEL_NAME"
    export HF_REPO="unsloth/Qwen3.5-35B-A3B-GGUF"
    export HF_FILE="Qwen3.5-35B-A3B-UD-Q4_K_XL.gguf"
    export SERVER_PORT="8080"
    export SERVER_HOST="0.0.0.0"
    export CONTEXT_SIZE="131072"
    export GPU_LAYERS="999"
    export BATCH_SIZE="512"
    export UBATCH_SIZE="256"
    export FLASH_ATTN="auto"
    export REASONING_FORMAT="none"
    export REASONING_BUDGET="0"
    export ENABLE_THINKING="false"
    export API_BASE_URL="http://localhost:$SERVER_PORT/v1"
    export API_KEY="not-needed"
    export INSTALL_DIR="/usr/local/bin"
    export BUILD_DIR="$HOME/llama.cpp"
    export LOG_FILE="/tmp/llama-server.log"
    export PID_FILE="/tmp/llama-server.pid"
    export VENV_DIR="$PROJECT_ROOT/.venv"
    export BENCHMARK_DIR="$PROJECT_ROOT/benchmarks"
    export BENCH_REPETITIONS="3"
    export MIN_RAM_GB="16"
    export RECOMMENDED_RAM_GB="32"
    export MIN_DISK_GB="25"
    export ENABLE_WEBUI="true"
    export ENABLE_CHAT_CLI="true"
    export ENABLE_AGENT="true"
    export ENABLE_BENCHMARKS="true"
    export TEMPERATURE="0.7"
    export TOP_P="0.9"
    export REPEAT_PENALTY="1.1"
    export MAX_TOKENS="-1"
fi

# Export resolved paths
export MODEL_DIR
export MODEL_PATH
export VENV_DIR
export BENCHMARK_DIR
