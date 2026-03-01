# ═══════════════════════════════════════════════════════════
# Claude Code CLI Integration
# ═══════════════════════════════════════════════════════════
# Use this local LLM stack as a custom backend for Claude Code CLI
# This allows you to use Qwen, Llama, Mistral, etc. with Claude Code
#
# Configuration is loaded from config.yaml
# Edit config.yaml to change port, model, etc.
# ═══════════════════════════════════════════════════════════

# Load configuration from config.yaml
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/scripts/config.sh"

# ═══════════════════════════════════════════════════════════
# Disable Telemetry
# ═══════════════════════════════════════════════════════════
# Prevents CLI from attempting remote telemetry validation
export CLAUDE_CODE_DISABLE_TELEMETRY=1

# ═══════════════════════════════════════════════════════════
# Dummy Authentication
# ═══════════════════════════════════════════════════════════
# Required because Claude CLI expects non-empty key
# Local server ignores authentication
unset ANTHROPIC_API_KEY
export ANTHROPIC_AUTH_TOKEN=dummy

# ═══════════════════════════════════════════════════════════
# API Configuration
# ═══════════════════════════════════════════════════════════
# Point Claude Code to local server (uses SERVER_PORT from config.yaml)
export ANTHROPIC_BASE_URL="http://localhost:$SERVER_PORT"

# Model name (uses MODEL_NAME from config.yaml - matches active_model)
export ANTHROPIC_MODEL="$MODEL_NAME"

# ═══════════════════════════════════════════════════════════
# Optional: Additional Settings
# ═══════════════════════════════════════════════════════════
# Timeout settings (in seconds) - from config.yaml
export CLAUDE_CODE_TIMEOUT="${CLAUDE_CODE_TIMEOUT:-300}"

# Max tokens for responses - from config.yaml
export CLAUDE_CODE_MAX_TOKENS="${CLAUDE_CODE_MAX_TOKENS:-8192}"

# Enable verbose logging (optional)
# export CLAUDE_CODE_VERBOSE=1

# ═══════════════════════════════════════════════════════════
# Usage Instructions
# ═══════════════════════════════════════════════════════════
#
# 1. Start the local server:
#    ./bin/start-webui.sh
#
# 2. Source this file:
#    source claude-code-env.sh
#
# 3. Run Claude Code:
#    claude
#
# ═══════════════════════════════════════════════════════════
