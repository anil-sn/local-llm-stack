#!/usr/bin/env bash
#
# Install Local LLM Stack CLI
# Sets up the Python package and makes the CLI available system-wide
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_ROOT/.venv"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     Installing Local LLM Stack CLI                       ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
PYTHON_CMD="python3"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    echo "📊 Python version: $PYTHON_VERSION"
    
    # Check minimum version
    if [ "$(echo "$PYTHON_VERSION < 3.10" | bc -l)" = "1" ]; then
        echo "❌ Python 3.10+ required (found $PYTHON_VERSION)"
        exit 1
    fi
else
    echo "❌ Python 3 not found"
    exit 1
fi

echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment..."
    $PYTHON_CMD -m venv "$VENV_DIR"
    echo "✅ Virtual environment created: $VENV_DIR"
    echo ""
else
    echo "✅ Virtual environment exists: $VENV_DIR"
    echo ""
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source "$VENV_DIR/bin/activate"
echo "✅ Activated"
echo ""

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip --quiet
echo "✅ Done"
echo ""

# Install the package in development mode
echo "📦 Installing Local LLM Stack CLI..."
cd "$PROJECT_ROOT"
pip install -e ".[all]" --quiet
echo "✅ Installed"
echo ""

# Verify installation
echo "🔍 Verifying installation..."
if python -c "import local_llm" 2>/dev/null; then
    echo "✅ Package imported successfully"
else
    echo "❌ Failed to import package"
    exit 1
fi

# Check if CLI is available
if command -v llm-stack &> /dev/null; then
    CLI_PATH=$(which llm-stack)
    echo "✅ CLI available: $CLI_PATH"
else
    echo "⚠️  CLI not in PATH, but can be run with: $VENV_DIR/bin/llm-stack"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Installation complete!"
echo ""
echo "Usage:"
echo ""
echo "  # Activate virtual environment"
echo "  source $VENV_DIR/bin/activate"
echo ""
echo "  # Or use the wrapper script"
echo "  $PROJECT_ROOT/bin/llm-stack --help"
echo ""
echo "  # Quick start"
echo "  llm-stack status"
echo "  llm-stack server start"
echo "  llm-stack chat interactive"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
