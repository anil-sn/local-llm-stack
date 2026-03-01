#!/usr/bin/env bash
#
# Start llama.cpp with Web UI - Reasoning Mode Enabled
# This is a convenience wrapper that starts the server with reasoning on
# Configuration loaded from config.yaml
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../scripts/config.sh"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     Starting llama.cpp Web UI - Reasoning Mode ON        ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Pass all arguments to start-webui.sh with reasoning enabled
exec "$SCRIPT_DIR/start-webui.sh" "${1:-$MODEL_PATH}" "${2:-$SERVER_PORT}" "${3:-$CONTEXT_SIZE}" "${4:-$(sysctl -n hw.ncpu)}" on
