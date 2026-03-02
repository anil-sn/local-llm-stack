#!/usr/bin/env bash
#
# Stop LLM Server
#
# DEPRECATED: Use 'llm-stack server stop' instead
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PID_FILE="/tmp/llama-server.pid"

# Show deprecation notice
echo "⚠️  This script is deprecated. Use the new CLI instead:"
echo "   llm-stack server stop"
echo ""

# Try to get PID from file
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    
    if kill -0 "$PID" 2>/dev/null; then
        echo "Stopping server (PID: $PID)..."
        kill "$PID"
        
        # Wait for process to stop
        for i in {1..10}; do
            if ! kill -0 "$PID" 2>/dev/null; then
                echo "✅ Server stopped"
                rm -f "$PID_FILE"
                exit 0
            fi
            sleep 0.5
        done
        
        # Force kill if still running
        echo "Graceful shutdown timed out, forcing..."
        kill -9 "$PID"
        echo "✅ Server stopped (forced)"
        rm -f "$PID_FILE"
    else
        echo "⚠️  Server process not found (may have already stopped)"
        rm -f "$PID_FILE"
    fi
else
    # Try to find by port
    source "$SCRIPT_DIR/../scripts/config.sh"
    PORT="${1:-$SERVER_PORT}"
    
    if command -v lsof &> /dev/null; then
        PID=$(lsof -ti :$PORT 2>/dev/null | head -1)
        if [ -n "$PID" ]; then
            echo "Stopping server on port $PORT (PID: $PID)..."
            kill "$PID"
            sleep 1
            if kill -0 "$PID" 2>/dev/null; then
                kill -9 "$PID"
            fi
            echo "✅ Server stopped"
        else
            echo "⚠️  No server found on port $PORT"
        fi
    else
        echo "⚠️  PID file not found and lsof not available"
        echo "   Manually find process: lsof -i :$PORT"
    fi
fi
