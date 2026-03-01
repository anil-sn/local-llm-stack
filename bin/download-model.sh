#!/usr/bin/env bash
#
# Download Qwen3.5-35B-A3B model from HuggingFace
# Uses configuration from config.yaml
#

set -e

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../scripts/config.sh"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║        Downloading Qwen3.5-35B-A3B Model                 ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check for huggingface-cli
if ! command -v huggingface-cli &> /dev/null; then
    echo "📦 Installing huggingface_hub..."
    if [ -d "$VENV_DIR" ]; then
        source "$VENV_DIR/bin/activate"
    fi
    pip3 install -U huggingface_hub
    if [ -d "$VENV_DIR" ]; then
        deactivate
    fi
fi

# Create models directory
mkdir -p "$MODEL_DIR"

# Check if model already exists
if [ -f "$MODEL_PATH" ]; then
    SIZE=$(du -h "$MODEL_PATH" | cut -f1)
    echo "✅ Model already exists at: $MODEL_PATH"
    echo "   Size: $SIZE"
    echo ""
    read -p "Download anyway? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

# Download using huggingface-cli (faster, supports resume)
echo "📥 Downloading $MODEL_NAME (~19GB)..."
echo "   Source: $HF_REPO"
echo "   Destination: $MODEL_PATH"
echo ""

huggingface-cli download \
    "$HF_REPO" \
    "$HF_FILE" \
    --local-dir "$MODEL_DIR" \
    --local-dir-use-symlinks false \
    --resume-download

# Verify download
if [ -f "$MODEL_PATH" ]; then
    SIZE=$(du -h "$MODEL_PATH" | cut -f1)
    echo ""
    echo "✅ Download complete!"
    echo "   Location: $MODEL_PATH"
    echo "   Size: $SIZE"
    echo ""
else
    echo "❌ Download failed!"
    exit 1
fi

# Alternative: Direct download with curl (if huggingface-cli fails)
echo "Alternative download method (if above fails):"
echo "  curl -L -o \"$MODEL_PATH\" \"https://huggingface.co/$HF_REPO/resolve/main/$HF_FILE\""
echo ""
