#!/usr/bin/env bash
#
# Start Web UI Server
#
# DEPRECATED: Use 'llm-stack server start' instead
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Show deprecation notice
echo "⚠️  This script is deprecated. Use the new CLI instead:"
echo "   llm-stack server start"
echo ""

# Load configuration
source "$SCRIPT_DIR/../scripts/config.sh"

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
    echo ""
    echo "Download with:"
    echo "  ./bin/download-model.sh"
    exit 1
fi

# Check for llama-server
if ! command -v llama-server &> /dev/null; then
    echo "❌ llama-server not found"
    echo ""
    echo "Install llama.cpp:"
    echo "  brew install llama.cpp"
    exit 1
fi

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     Qwen3.5-35B-A3B Web UI Server                        ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "📦 Model: $MODEL"
echo "🌐 Port: http://localhost:$PORT"
echo "🧠 Context: $CONTEXT tokens"
echo "🧵 Threads: $THREADS_ARG"
echo "🎮 GPU Layers: $GPU_LAYERS"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Run llama-server
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
    --flash-attn "$FLASH_ATTN" \
    --temp "$TEMPERATURE" \
    --top-p "$TOP_P" \
    --repeat-penalty "$REPEAT_PENALTY" \
    --reasoning-format "$REASONING_FORMAT" \
    --reasoning-budget "$REASONING_BUDGET"
