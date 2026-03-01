#!/usr/bin/env bash
#
# Install llama.cpp with Metal GPU acceleration for macOS
#

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║         Installing llama.cpp for macOS Metal             ║"
echo "╚══════════════════════════════════════════════════════════╝"

# Check for Homebrew
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found. Please install from https://brew.sh"
    exit 1
fi

# Check for Xcode Command Line Tools
if ! xcode-select -p &> /dev/null; then
    echo "❌ Xcode Command Line Tools not found."
    echo "   Install with: xcode-select --install"
    exit 1
fi

# Install llama.cpp via Homebrew (recommended)
echo "📦 Installing llama.cpp via Homebrew..."
brew install llama.cpp

# Verify installation
echo ""
if command -v llama-server &> /dev/null; then
    echo "✅ Installation complete!"
    echo ""
    llama-server --version
    echo ""
    echo "📍 llama-server installed at: $(which llama-server)"
    echo ""
    echo "Next steps:"
    echo "  1. Download the model: ./bin/download-model.sh"
    echo "  2. Start the server:   ./bin/start-webui.sh"
else
    echo "❌ Installation failed!"
    exit 1
fi
