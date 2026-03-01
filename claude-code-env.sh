# ═══════════════════════════════════════════════════════════
# Claude Code CLI Integration
# ═══════════════════════════════════════════════════════════
# Use this local LLM stack as a custom backend for Claude Code CLI
# This allows you to use Qwen, Llama, Mistral, etc. with Claude Code
# ═══════════════════════════════════════════════════════════

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
# Point Claude Code to local server
export ANTHROPIC_BASE_URL=http://localhost:8080

# Model name (must match what's running on the server)
# This will be auto-set from config.yaml
export ANTHROPIC_MODEL="Qwen3.5-35B-A3B-UD-Q4_K_XL.gguf"

# ═══════════════════════════════════════════════════════════
# Optional: Additional Settings
# ═══════════════════════════════════════════════════════════
# Timeout settings (in seconds)
export CLAUDE_CODE_TIMEOUT=300

# Max tokens for responses
export CLAUDE_CODE_MAX_TOKENS=8192

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
