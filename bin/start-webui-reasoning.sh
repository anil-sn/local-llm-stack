#!/usr/bin/env bash
#
# Start llama.cpp with Web UI - Reasoning Mode Enabled
# This is a convenience wrapper that starts the server with reasoning on
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     Starting llama.cpp Web UI - Reasoning Mode ON        ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Pass all arguments to start-webui.sh with reasoning enabled
exec "$SCRIPT_DIR/start-webui.sh" "${1:-$HOME/models/Qwen3.5-35B-A3B-UD-Q4_K_XL.gguf}" "${2:-8080}" "${3:-131072}" "${4:-$(sysctl -n hw.ncpu)}" on
