#!/usr/bin/env bash
#
# Start LLM Server (Foreground)
#
# DEPRECATED: Use 'llm-stack server start --foreground' instead
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Show deprecation notice
echo "⚠️  This script is deprecated. Use the new CLI instead:"
echo "   llm-stack server start --foreground"
echo ""

# Load configuration from .env (auto-generated from config.yaml)
source "$SCRIPT_DIR/../scripts/generate_env.sh" 2>/dev/null || {
    python3 "$PROJECT_ROOT/scripts/generate_env.py"
    source "$PROJECT_ROOT/.env"
}

# Parse arguments
MODEL="${1:-$MODEL_PATH}"
PORT="${2:-$SERVER_PORT}"
CONTEXT="${3:-$CONTEXT_SIZE}"
THREADS_ARG="${4:-}"

# Detect threads (cross-platform)
if [ -z "$THREADS_ARG" ]; then
    if command -v nproc &> /dev/null; then
        THREADS_ARG="$(nproc)"
    elif command -v sysctl &> /dev/null; then
        THREADS_ARG="$(sysctl -n hw.ncpu)"
    else
        THREADS_ARG="4"
    fi
fi

# Check model exists
if [ ! -f "$MODEL" ]; then
    echo "❌ Model not found: $MODEL"
    exit 1
fi

# Check for llama-server
if ! command -v llama-server &> /dev/null; then
    echo "❌ llama-server not found"
    exit 1
fi

echo "🚀 Starting server in foreground..."
echo "📦 Model: $MODEL"
echo "🌐 Port: http://localhost:$PORT"
echo ""

# Run llama-server in foreground
exec llama-server \
    -m "$MODEL" \
    --port "$PORT" \
    --host "$SERVER_HOST" \
    --ctx-size "$CONTEXT" \
    --threads "$THREADS_ARG" \
    --threads-batch "$THREADS_ARG" \
    -ngl "$GPU_LAYERS" \
    --batch-size "$BATCH_SIZE" \
    --ubatch-size "$UBATCH_SIZE" \
    --flash-attn "$FLASH_ATTN"
