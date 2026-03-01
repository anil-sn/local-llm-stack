#!/usr/bin/env bash
#
# Stop llama.cpp inference server
#

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║          Stopping llama.cpp Server                       ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check for PID file
if [ -f /tmp/llama-server.pid ]; then
    PID=$(cat /tmp/llama-server.pid)
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "🛑 Stopping server (PID: $PID)..."
        kill "$PID"
        rm -f /tmp/llama-server.pid
        echo "✅ Server stopped"
    else
        echo "⚠️  Server not running (stale PID file)"
        rm -f /tmp/llama-server.pid
    fi
else
    echo "🔍 No PID file found, searching for llama-server processes..."
    PIDS=$(pgrep -f "llama-server" || true)
    if [ -n "$PIDS" ]; then
        echo "🛑 Stopping llama-server processes: $PIDS"
        pkill -f "llama-server"
        echo "✅ Server stopped"
    else
        echo "ℹ️  No llama-server processes found"
    fi
fi
