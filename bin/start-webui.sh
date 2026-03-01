#!/usr/bin/env bash
#
# Start llama.cpp with Web UI in background
#

set -e

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../scripts/config.sh"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║          Starting llama.cpp Web UI                       ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Use environment variables or command line arguments
MODEL="${1:-$MODEL_PATH}"
PORT="${2:-$SERVER_PORT}"
CONTEXT="${3:-$CONTEXT_SIZE}"

# Detect threads (Linux vs macOS)
if command -v nproc &> /dev/null; then
    # Linux
    THREADS="${4:-$(nproc)}"
else
    # macOS
    THREADS="${4:-$(sysctl -n hw.ncpu)}"
fi
REASONING="${5:-off}"  # on|off

# Check model exists
if [ ! -f "$MODEL" ]; then
    echo "❌ Model not found: $MODEL"
    echo ""
    echo "Download with:"
    echo "  ./bin/download-model.sh"
    exit 1
fi

# Get system info for optimal settings
TOTAL_MEM=$(sysctl -n hw.memsize 2>/dev/null || echo "34359738368")
RECOMMENDED_MEM=$((TOTAL_MEM * 85 / 100))  # 85% of total RAM

# Configure reasoning mode
if [[ "$REASONING" == "on" ]] || [[ "$REASONING" == "true" ]] || [[ "$REASONING" == "1" ]]; then
    REASONING_FORMAT="deepseek"
    REASONING_BUDGET="-1"
    REASONING_STATUS="✅ Enabled (unlimited)"
else
    REASONING_FORMAT="none"
    REASONING_BUDGET="0"
    REASONING_STATUS="❌ Disabled"
fi

echo "📦 Model: $MODEL"
echo "📍 Port: $PORT"
echo "🧠 Context: $CONTEXT tokens"
echo "🧵 Threads: $THREADS"
echo "🤔 Reasoning: $REASONING_STATUS"
echo "💾 Memory limit: ~$((RECOMMENDED_MEM / 1024 / 1024 / 1024))GB"
echo "🌐 Web UI: http://localhost:$PORT"
echo ""

# Check if port is in use
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Port $PORT is already in use"
    PID=$(lsof -ti:$PORT)
    echo "   Running by PID: $PID"
    echo ""
    read -p "Kill existing process and continue? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        kill $PID 2>/dev/null || pkill -f "llama-server.*$PORT" || true
        sleep 2
    else
        exit 1
    fi
fi

# Kill any existing llama-server
pkill -f "llama-server" 2>/dev/null || true
sleep 1

# Start server in background
echo "🚀 Starting llama-server with optimized settings..."
echo ""

nohup llama-server \
    -m "$MODEL" \
    --port "$PORT" \
    --host "0.0.0.0" \
    --ctx-size "$CONTEXT" \
    --threads "$THREADS" \
    --threads-batch "$THREADS" \
    --batch-size "${BATCH_SIZE:-512}" \
    --ubatch-size "${UBATCH_SIZE:-256}" \
    --flash-attn "${FLASH_ATTN:-auto}" \
    --n-gpu-layers "${GPU_LAYERS:-999}" \
    --reasoning-format "$REASONING_FORMAT" \
    --reasoning-budget "$REASONING_BUDGET" \
    --chat-template-kwargs '{"enable_thinking":false}' \
    > "$LOG_FILE" 2>&1 &

SERVER_PID=$!
echo "✅ Server process started!"
echo "   PID: $SERVER_PID"
echo "   Logs: $LOG_FILE"
echo ""

# Wait for server to start
echo "⏳ Waiting for server to be ready..."
for i in {1..60}; do
    if curl -s "http://localhost:$PORT/health" | jq -e '.status' > /dev/null 2>&1; then
        echo ""
        echo "╔══════════════════════════════════════════════════════════╗"
        echo "║           Web UI is Ready! ✅                            ║"
        echo "╚══════════════════════════════════════════════════════════╝"
        echo ""
        echo "📊 Server Configuration:"
        echo "   Model: Qwen3.5-35B-A3B (19GB)"
        echo "   Context: $CONTEXT tokens"
        echo "   GPU Offload: Full (${GPU_LAYERS:-999} layers)"
        echo "   Flash Attention: ${FLASH_ATTN:-auto}"
        echo "   Reasoning: $REASONING_STATUS"
        echo ""
        echo "🌐 Web UI: http://localhost:$PORT"
        echo "📊 API Docs: http://localhost:$PORT/docs"
        echo "💚 Health: http://localhost:$PORT/health"
        echo ""
        echo "🛑 Stop server:"
        echo "   ./bin/stop-server.sh"
        echo "   # or: kill $SERVER_PID"
        echo ""

        # Save PID for later
        echo "$SERVER_PID" > "$PID_FILE"

        # Open browser automatically
        echo "🌐 Opening Web UI in your browser..."
        if command -v open &> /dev/null; then
            open "http://localhost:$PORT"
        fi

        exit 0
    fi
    sleep 1
done

echo "❌ Server failed to start within 60 seconds"
echo ""
echo "📋 Last 20 lines of logs:"
tail -20 "$LOG_FILE"
echo ""
echo "📄 Full logs: $LOG_FILE"
exit 1
