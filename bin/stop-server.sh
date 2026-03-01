#!/usr/bin/env bash
#
# Stop llama.cpp inference server
# Configuration loaded from config.yaml
#

set -e

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../scripts/config.sh"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║          Stopping llama.cpp Server                       ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check for PID file - use config value
PID_FILE="${PID_FILE:-/tmp/llama-server.pid}"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "🛑 Stopping server (PID: $PID)..."
        kill "$PID"
        rm -f "$PID_FILE"
        echo "✅ Server stopped"
    else
        echo "⚠️  Server not running (stale PID file)"
        rm -f "$PID_FILE"
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
