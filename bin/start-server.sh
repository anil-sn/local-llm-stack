#!/usr/bin/env bash
#
# Start Qwen3.5-35B-A3B inference server with llama.cpp
# Optimized for performance and stability on Apple Silicon
#

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     Qwen3.5-35B-A3B Inference Server                     ║"
echo "║     Optimized for Apple Silicon (M1/M2/M3/M4)            ║"
echo "╚══════════════════════════════════════════════════════════╝"

# Default configuration - optimized for M4 Pro
PORT=8080
CONTEXT=131072
GPU_LAYERS=999
HOST="0.0.0.0"
THREADS=$(sysctl -n hw.ncpu)
BATCH_SIZE=512
UBATCH_SIZE=256
REASONING="off"  # on|off

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --port) PORT="$2"; shift 2 ;;
        --context) CONTEXT="$2"; shift 2 ;;
        --gpu-layers) GPU_LAYERS="$2"; shift 2 ;;
        --host) HOST="$2"; shift 2 ;;
        --threads) THREADS="$2"; shift 2 ;;
        --batch-size) BATCH_SIZE="$2"; shift 2 ;;
        --ubatch-size) UBATCH_SIZE="$2"; shift 2 ;;
        --reasoning) REASONING="$2"; shift 2 ;;
        --reasoning-on) REASONING="on"; shift ;;
        --reasoning-off) REASONING="off"; shift ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --port PORT        Server port (default: 8080)"
            echo "  --context SIZE     Context size (default: 131072)"
            echo "  --gpu-layers N     GPU layers to offload (default: 999)"
            echo "  --host HOST        Bind host (default: 0.0.0.0)"
            echo "  --threads N        CPU threads (default: hw.ncpu)"
            echo "  --batch-size N     Logical batch size (default: 512)"
            echo "  --ubatch-size N    Physical batch size (default: 256)"
            echo "  --reasoning on|off Enable/disable reasoning (default: off)"
            echo "  --reasoning-on     Enable reasoning mode"
            echo "  --reasoning-off    Disable reasoning mode"
            echo "  --help             Show this help"
            exit 0
            ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# Configure reasoning mode
if [[ "$REASONING" == "on" ]] || [[ "$REASONING" == "true" ]] || [[ "$REASONING" == "1" ]]; then
    REASONING_FORMAT="deepseek"
    REASONING_BUDGET="-1"
    REASONING_STATUS="Enabled (unlimited)"
else
    REASONING_FORMAT="none"
    REASONING_BUDGET="0"
    REASONING_STATUS="Disabled"
fi

# Find model
MODEL_DIR="$HOME/models"
MODEL_FILE="Qwen3.5-35B-A3B-UD-Q4_K_XL.gguf"
MODEL_PATH="$MODEL_DIR/$MODEL_FILE"

# Search for model in common locations
if [ ! -f "$MODEL_PATH" ]; then
    for pattern in "$HOME/models/*.gguf" "/Volumes/*/models/*.gguf"; do
        for f in $pattern; do
            if [[ -f "$f" && "$f" == *"Qwen3.5"* ]]; then
                MODEL_PATH="$f"
                break
            fi
        done
    done
fi

if [ ! -f "$MODEL_PATH" ]; then
    echo "❌ Model not found: $MODEL_PATH"
    echo ""
    echo "Download the model first:"
    echo "  ./bin/download-model.sh"
    exit 1
fi

echo "✅ Model found: $MODEL_PATH"
echo ""

# Check if llama-server is installed
if ! command -v llama-server &> /dev/null; then
    echo "❌ llama-server not found"
    echo ""
    echo "Install llama.cpp first:"
    echo "  ./bin/install.sh"
    exit 1
fi

# Kill existing server
pkill -f "llama-server.*$PORT" 2>/dev/null || true
sleep 1

# Start llama-server with optimized settings
echo "📦 Starting llama.cpp server with optimized settings..."
echo "   Port: $PORT"
echo "   Context: $CONTEXT"
echo "   GPU Layers: $GPU_LAYERS (full offload)"
echo "   Threads: $THREADS"
echo "   Batch Size: $BATCH_SIZE"
echo "   Micro Batch: $UBATCH_SIZE"
echo "   Reasoning: $REASONING_STATUS"
echo ""
echo "🌐 Web UI will be available at: http://localhost:$PORT"
echo ""

llama-server \
    -m "$MODEL_PATH" \
    --port "$PORT" \
    --host "$HOST" \
    --ctx-size "$CONTEXT" \
    --n-gpu-layers "$GPU_LAYERS" \
    --threads "$THREADS" \
    --threads-batch "$THREADS" \
    --batch-size "$BATCH_SIZE" \
    --ubatch-size "$UBATCH_SIZE" \
    --flash-attn auto \
    --reasoning-format "$REASONING_FORMAT" \
    --reasoning-budget "$REASONING_BUDGET" \
    --chat-template-kwargs '{"enable_thinking":false}'
