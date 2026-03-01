#!/usr/bin/env bash
#
# Claude Code CLI Integration Script
# Automatically configures environment to use local LLM with Claude Code
#
# Usage:
#   source scripts/claude-code.sh
#   claude
#

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Load configuration
source "$SCRIPT_DIR/config.sh"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║        Claude Code CLI - Local LLM Integration          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check if server is running
echo "🔍 Checking server status..."
if curl -s "http://localhost:$SERVER_PORT/health" | jq -e '.status' > /dev/null 2>&1; then
    echo "✅ Server is running on port $SERVER_PORT"
else
    echo "❌ Server is not running"
    echo ""
    read -p "Start server now? [Y/n] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]] || [ -z "$REPLY" ]; then
        echo ""
        "$PROJECT_ROOT/bin/start-webui.sh"
    else
        echo "⚠️  Claude Code won't work without a running server"
        return 1
    fi
fi

echo ""
echo "📊 Configuration:"
echo "   Active Model: $ACTIVE_MODEL"
echo "   Model Name: $MODEL_NAME"
echo "   Server URL: http://localhost:$SERVER_PORT"
echo "   Model Size: ${MODEL_SIZE_GB}GB"
echo "   RAM Required: ${MODEL_RAM_GB}GB"
echo ""

# Set Claude Code environment variables
export CLAUDE_CODE_DISABLE_TELEMETRY=1
unset ANTHROPIC_API_KEY
export ANTHROPIC_AUTH_TOKEN=dummy
export ANTHROPIC_BASE_URL="http://localhost:$SERVER_PORT"
export ANTHROPIC_MODEL="$MODEL_NAME"

# Optional settings
export CLAUDE_CODE_TIMEOUT=300
export CLAUDE_CODE_MAX_TOKENS=8192

echo "✅ Environment configured for Claude Code"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 Next Steps:"
echo ""
echo "   1. Start Claude Code:"
echo "      claude"
echo ""
echo "   2. Or with a specific command:"
echo "      claude 'Explain quantum computing'"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 Tips:"
echo "   • To switch models: edit config.yaml and change 'active_model'"
echo "   • To stop server: ./bin/stop-server.sh"
echo "   • To view logs: cat $LOG_FILE"
echo ""

# Function to restore original environment
restore_env() {
    unset CLAUDE_CODE_DISABLE_TELEMETRY
    unset ANTHROPIC_AUTH_TOKEN
    unset ANTHROPIC_BASE_URL
    unset ANTHROPIC_MODEL
    unset CLAUDE_CODE_TIMEOUT
    unset CLAUDE_CODE_MAX_TOKENS
    echo "✅ Environment restored"
}

# Set trap to restore on shell exit (optional)
# trap restore_env EXIT

echo "ℹ️  To restore environment: run 'restore_env'"
echo ""
