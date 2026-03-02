#!/usr/bin/env bash
#
# Server Status - Check llama.cpp server status
# Configuration loaded from config.yaml
#
# Usage:
#   ./bin/server-status.sh
#

set -e

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../scripts/config.sh"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║              Server Status Check                         ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check if PID file exists
if [ -f "$PID_FILE" ]; then
    SERVER_PID=$(cat "$PID_FILE")
    echo "📋 PID File: $PID_FILE"
    echo "   PID: $SERVER_PID"
    
    # Check if process is running
    if kill -0 "$SERVER_PID" 2>/dev/null; then
        echo "   Status: ✅ Running"
    else
        echo "   Status: ❌ Process not running (stale PID file)"
        echo ""
        echo "💡 Action: Remove stale PID file"
        echo "   rm $PID_FILE"
        SERVER_PID=""
    fi
else
    echo "📋 PID File: Not found"
    SERVER_PID=""
fi

echo ""

# Check if port is in use
echo "📍 Port Check: $SERVER_PORT"
if lsof -Pi :$SERVER_PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    PORT_PID=$(lsof -ti:$SERVER_PORT)
    echo "   Status: ✅ In use (PID: $PORT_PID)"
    
    # Check if it matches our server PID
    if [ -n "$SERVER_PID" ] && [ "$SERVER_PID" = "$PORT_PID" ]; then
        echo "   Note: Matches server PID"
    else
        echo "   ⚠️  Warning: Port in use by different process"
    fi
else
    echo "   Status: ❌ Not in use"
fi

echo ""

# Check server health
echo "🏥 Health Check: http://localhost:$SERVER_PORT/health"
if curl -s --connect-timeout 2 "http://localhost:$SERVER_PORT/health" | jq -e '.status' > /dev/null 2>&1; then
    HEALTH=$(curl -s --connect-timeout 2 "http://localhost:$SERVER_PORT/health")
    echo "   Status: ✅ Healthy"
    echo "   Response: $HEALTH"
else
    echo "   Status: ❌ Not responding"
fi

echo ""

# Check model file
echo "📦 Model Check:"
if [ -f "$MODEL_PATH" ]; then
    SIZE=$(du -h "$MODEL_PATH" | cut -f1)
    echo "   File: ✅ Exists ($SIZE)"
    echo "   Path: $MODEL_PATH"
else
    echo "   File: ❌ Not found"
    echo "   Path: $MODEL_PATH"
    echo ""
    echo "💡 Action: Download model"
    echo "   ./bin/download-model.sh"
fi

echo ""

# Check log file
echo "📝 Log File: $LOG_FILE"
if [ -f "$LOG_FILE" ]; then
    LINES=$(wc -l < "$LOG_FILE")
    SIZE=$(du -h "$LOG_FILE" | cut -f1)
    echo "   Status: ✅ Exists ($LINES lines, $SIZE)"
    echo ""
    echo "   Last 5 log entries:"
    echo "   ────────────────────────────────────────────────────────"
    tail -5 "$LOG_FILE" | sed 's/^/   /'
    echo "   ────────────────────────────────────────────────────────"
else
    echo "   Status: ℹ️  Not found (server may not have started yet)"
fi

echo ""

# Summary
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                    Summary                               ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

SERVER_RUNNING=false
if [ -n "$SERVER_PID" ] && kill -0 "$SERVER_PID" 2>/dev/null; then
    SERVER_RUNNING=true
fi

if curl -s --connect-timeout 2 "http://localhost:$SERVER_PORT/health" | jq -e '.status' > /dev/null 2>&1; then
    echo "✅ Server is RUNNING and HEALTHY"
    echo ""
    echo "🌐 Web UI: http://localhost:$SERVER_PORT"
    echo "📊 API: http://localhost:$SERVER_PORT/v1"
    echo "📖 Docs: http://localhost:$SERVER_PORT/docs"
    echo ""
    echo "🛑 Stop server:"
    echo "   ./bin/stop-server.sh"
    echo "   # or: kill $SERVER_PID"
else
    echo "❌ Server is NOT RUNNING"
    echo ""
    echo "🚀 Start server:"
    echo "   ./bin/start-webui.sh"
fi

echo ""

# Exit with appropriate code
if $SERVER_RUNNING; then
    exit 0
else
    exit 1
fi
