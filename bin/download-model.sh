#!/usr/bin/env bash
#
# Download LLM models from HuggingFace
# Uses configuration from config.yaml (via .env)
#
# Usage:
#   ./bin/models download qwen-3-9b   # Download specific model
#   ./bin/download-model.sh           # Download active model
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║         Model Download Utility                           ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Activate venv if it exists
if [ -d "$PROJECT_ROOT/.venv" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

# Check if model key is provided
if [ -n "$1" ]; then
    MODEL_KEY="$1"
    echo "📥 Downloading model: $MODEL_KEY"
    echo ""
    cd "$PROJECT_ROOT/src/python"
    python3 manage_models.py download "$MODEL_KEY"
else
    # Download active model
    echo "📥 Downloading active model from config.yaml"
    echo ""
    cd "$PROJECT_ROOT/src/python"
    python3 manage_models.py status
    echo ""
    read -p "Download the active model? [Y/n] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]] || [ -z "$REPLY" ]; then
        python3 manage_models.py download
    fi
fi
