#!/usr/bin/env bash
#
# Load environment from .env file (auto-generated from config.yaml)
#
# Usage: source scripts/generate_env.sh
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_ROOT/.env"

# Check if .env exists, generate if not
if [ ! -f "$ENV_FILE" ]; then
    echo "⚠️  .env not found. Generating from config.yaml..."
    
    if [ -d "$PROJECT_ROOT/.venv" ]; then
        source "$PROJECT_ROOT/.venv/bin/activate"
    fi
    
    python3 "$PROJECT_ROOT/scripts/generate_env.py"
fi

# Load .env file
if [ -f "$ENV_FILE" ]; then
    set -a  # Automatically export all variables
    source "$ENV_FILE"
    set +a
else
    echo "❌ Failed to load .env file"
    return 1
fi
