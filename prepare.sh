#!/usr/bin/env bash
#
# Qwen3.5-35B-A3B Setup Script
# Auto-detects OS and prepares the environment for macOS and Linux
#

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     Qwen3.5-35B-A3B Local Inference Setup                ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        OS_VERSION=$(sw_vers -productVersion)
        ARCH=$(uname -m)
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            OS_VERSION="$NAME $VERSION_ID"
        else
            OS_VERSION=$(uname -r)
        fi
        ARCH=$(uname -m)
    else
        log_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
    
    echo "📊 System Information:"
    echo "   OS: $OS"
    echo "   Version: $OS_VERSION"
    echo "   Architecture: $ARCH"
    echo ""
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    echo ""
    
    local missing=()
    
    # Check RAM
    if [[ "$OS" == "macos" ]]; then
        RAM_GB=$(( $(sysctl -n hw.memsize) / 1024 / 1024 / 1024 ))
    else
        RAM_GB=$(( $(grep MemTotal /proc/meminfo | awk '{print $2}') / 1024 / 1024 ))
    fi
    
    if [ $RAM_GB -lt 16 ]; then
        log_warning "Low RAM detected: ${RAM_GB}GB (32GB recommended)"
    else
        log_success "RAM: ${RAM_GB}GB"
    fi
    
    # Check disk space
    if [[ "$OS" == "macos" ]]; then
        DISK_GB=$(df -g / | tail -1 | awk '{print $4}')
    else
        DISK_GB=$(df -BG / | tail -1 | awk '{print $4}' | sed 's/G//')
    fi
    
    if [ $DISK_GB -lt 25 ]; then
        log_warning "Low disk space: ${DISK_GB}GB (25GB recommended)"
    else
        log_success "Disk Space: ${DISK_GB}GB available"
    fi
    
    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1)
        log_success "Python: $PYTHON_VERSION"
    else
        log_error "Python 3 not found"
        missing+=("python3")
    fi
    
    # Check pip
    if command -v pip3 &> /dev/null || command -v pip &> /dev/null; then
        log_success "pip: installed"
    else
        log_warning "pip not found (will be installed if needed)"
    fi
    
    echo ""
    
    if [ ${#missing[@]} -ne 0 ]; then
        log_error "Missing prerequisites: ${missing[*]}"
        echo ""
        echo "Please install the missing dependencies and run this script again."
        exit 1
    fi
}

# Install macOS dependencies
install_macos_deps() {
    log_info "Installing macOS dependencies..."
    echo ""
    
    # Check for Homebrew
    if ! command -v brew &> /dev/null; then
        log_warning "Homebrew not found. Installing..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Add Homebrew to PATH
        if [[ "$ARCH" == "arm64" ]]; then
            echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
            eval "$(/opt/homebrew/bin/brew shellenv)"
        else
            echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
            eval "$(/usr/local/bin/brew shellenv)"
        fi
        
        log_success "Homebrew installed"
    else
        log_success "Homebrew: $(brew --version | head -1)"
    fi
    
    echo ""
    
    # Install Xcode Command Line Tools
    if ! xcode-select -p &> /dev/null; then
        log_info "Installing Xcode Command Line Tools..."
        xcode-select --install
        log_success "Xcode Command Line Tools installed"
    else
        log_success "Xcode Command Line Tools: installed"
    fi
    
    echo ""
    
    # Install required packages
    log_info "Installing required packages..."
    brew update
    brew install cmake git jq bc wget
    
    log_success "All macOS dependencies installed"
    echo ""
}

# Install Linux dependencies
install_linux_deps() {
    log_info "Installing Linux dependencies..."
    echo ""
    
    # Detect package manager
    if command -v apt-get &> /dev/null; then
        PKG_MANAGER="apt"
        log_info "Detected Debian/Ubuntu package manager (apt)"
        sudo apt-get update
        sudo apt-get install -y build-essential cmake git jq bc wget curl
    elif command -v dnf &> /dev/null; then
        PKG_MANAGER="dnf"
        log_info "Detected Fedora/RHEL package manager (dnf)"
        sudo dnf install -y gcc gcc-c++ cmake git jq bc wget curl
    elif command -v yum &> /dev/null; then
        PKG_MANAGER="yum"
        log_info "Detected RHEL/CentOS package manager (yum)"
        sudo yum install -y gcc gcc-c++ cmake git jq bc wget curl
    elif command -v pacman &> /dev/null; then
        PKG_MANAGER="pacman"
        log_info "Detected Arch Linux package manager (pacman)"
        sudo pacman -Syu --noconfirm base-devel cmake git jq bc wget curl
    elif command -v zypper &> /dev/null; then
        PKG_MANAGER="zypper"
        log_info "Detected openSUSE package manager (zypper)"
        sudo zypper install -y gcc gcc-c++ cmake git jq bc wget curl
    else
        log_error "Unsupported package manager. Please install dependencies manually."
        exit 1
    fi
    
    echo ""
    log_success "All Linux dependencies installed (via $PKG_MANAGER)"
    echo ""
}

# Install llama.cpp
install_llama_cpp() {
    log_info "Installing llama.cpp..."
    echo ""
    
    if command -v llama-server &> /dev/null; then
        LLAMA_VERSION=$(llama-server --version 2>&1 | head -1)
        log_success "llama.cpp already installed: $LLAMA_VERSION"
        echo ""
        read -p "Reinstall llama.cpp? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return
        fi
    fi
    
    if [[ "$OS" == "macos" ]]; then
        # macOS: Use Homebrew
        log_info "Installing llama.cpp via Homebrew..."
        brew install llama.cpp
    else
        # Linux: Build from source with CUDA/Metal support if available
        log_info "Building llama.cpp from source..."
        
        # Check for NVIDIA GPU
        if command -v nvidia-smi &> /dev/null; then
            log_info "NVIDIA GPU detected. Building with CUDA support..."
            BUILD_CUDA=1
        else
            log_info "No NVIDIA GPU detected. Building with CPU-only support..."
            BUILD_CUDA=0
        fi
        
        # Clone and build
        cd /tmp
        
        # Clean up any existing llama.cpp directory
        if [ -d "llama.cpp" ]; then
            log_info "Cleaning up existing llama.cpp directory..."
            rm -rf llama.cpp
        fi
        
        git clone --depth 1 https://github.com/ggml-org/llama.cpp
        cd llama.cpp

        if [ $BUILD_CUDA -eq 1 ]; then
            # Use GGML_CUDA instead of deprecated LLAMA_CUBLAS
            cmake -B build -DGGML_CUDA=ON -DCMAKE_BUILD_TYPE=Release
        else
            cmake -B build -DCMAKE_BUILD_TYPE=Release
        fi

        cmake --build build --config Release -j"$(nproc)" --target llama-server

        # Install
        sudo cp build/bin/llama-server /usr/local/bin/
        sudo chmod +x /usr/local/bin/llama-server

        cd ..
        rm -rf llama.cpp

        log_success "llama.cpp installed to /usr/local/bin/llama-server"
    fi
    
    echo ""
    if command -v llama-server &> /dev/null; then
        log_success "llama.cpp: $(llama-server --version 2>&1 | head -1)"
    fi
    echo ""
}

# Setup Python virtual environment
setup_python_venv() {
    log_info "Setting up Python virtual environment..."
    echo ""
    
    local VENV_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.venv"
    
    if [ -d "$VENV_DIR" ]; then
        log_success "Virtual environment already exists at: $VENV_DIR"
        echo ""
        read -p "Recreate virtual environment? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return
        fi
        rm -rf "$VENV_DIR"
    fi
    
    python3 -m venv "$VENV_DIR"
    log_success "Virtual environment created at: $VENV_DIR"
    
    # Activate and install dependencies
    source "$VENV_DIR/bin/activate"
    
    if [ -f "src/python/requirements.txt" ]; then
        log_info "Installing Python dependencies..."
        pip install --upgrade pip
        pip install -r src/python/requirements.txt
        log_success "Python dependencies installed"
    fi
    
    deactivate
    echo ""
}

# Download model
download_model() {
    log_info "Model download setup..."
    echo ""
    
    local MODEL_DIR="$HOME/models"
    local MODEL_FILE="Qwen3.5-35B-A3B-UD-Q4_K_XL.gguf"
    local MODEL_PATH="$MODEL_DIR/$MODEL_FILE"
    
    if [ -f "$MODEL_PATH" ]; then
        local SIZE=$(du -h "$MODEL_PATH" | cut -f1)
        log_success "Model already exists: $MODEL_PATH ($SIZE)"
        echo ""
        read -p "Download anyway? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return
        fi
    fi
    
    # Check for huggingface-cli
    if ! command -v huggingface-cli &> /dev/null; then
        log_info "Installing huggingface_hub..."
        if [ -f ".venv/bin/activate" ]; then
            source ".venv/bin/activate"
        fi
        pip3 install -U huggingface_hub
        if [ -f ".venv/bin/activate" ]; then
            deactivate
        fi
    fi
    
    # Create models directory
    mkdir -p "$MODEL_DIR"
    
    echo ""
    log_info "Downloading model (~19GB)..."
    echo "   Source: unsloth/Qwen3.5-35B-A3B-GGUF"
    echo "   Destination: $MODEL_PATH"
    echo ""
    
    huggingface-cli download \
        unsloth/Qwen3.5-35B-A3B-GGUF \
        Qwen3.5-35B-A3B-UD-Q4_K_XL.gguf \
        --local-dir "$MODEL_DIR" \
        --local-dir-use-symlinks false \
        --resume-download
    
    if [ -f "$MODEL_PATH" ]; then
        local SIZE=$(du -h "$MODEL_PATH" | cut -f1)
        log_success "Model downloaded: $MODEL_PATH ($SIZE)"
    else
        log_error "Model download failed"
        exit 1
    fi
    echo ""
}

# Validate installation
validate_installation() {
    log_info "Validating installation..."
    echo ""
    
    local errors=0
    
    # Check llama-server
    if command -v llama-server &> /dev/null; then
        log_success "llama-server: $(which llama-server)"
    else
        log_error "llama-server not found"
        ((errors++))
    fi
    
    # Check model
    local MODEL_PATH="$HOME/models/Qwen3.5-35B-A3B-UD-Q4_K_XL.gguf"
    if [ -f "$MODEL_PATH" ]; then
        log_success "Model: $MODEL_PATH"
    else
        log_warning "Model not found (run: ./bin/download-model.sh)"
    fi
    
    # Check scripts
    if [ -x "bin/start-webui.sh" ]; then
        log_success "Scripts: executable"
    else
        log_error "Scripts not executable"
        ((errors++))
    fi
    
    echo ""
    
    if [ $errors -eq 0 ]; then
        log_success "All validations passed!"
    else
        log_error "$errors validation(s) failed"
    fi
    echo ""
}

# Print summary
print_summary() {
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║              Setup Complete! ✅                          ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""
    echo "📊 System:"
    echo "   OS: $OS $OS_VERSION"
    echo "   Architecture: $ARCH"
    echo ""
    echo "🚀 Next Steps:"
    echo ""
    echo "   1. Start the server:"
    echo "      ./bin/start-webui.sh"
    echo ""
    echo "   2. Or use terminal chat:"
    echo "      ./bin/chat-cli"
    echo ""
    echo "   3. Run benchmarks:"
    echo "      ./tools/benchmarks/run-all.sh"
    echo ""
    echo "   4. View documentation:"
    echo "      cat README.md"
    echo ""
    echo "📚 Documentation:"
    echo "   - Quick Start: docs/QUICKSTART.md"
    echo "   - API Reference: docs/API.md"
    echo "   - Benchmarks: tools/benchmarks/README.md"
    echo ""
}

# Main execution
main() {
    echo ""
    detect_os
    check_prerequisites
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    if [[ "$OS" == "macos" ]]; then
        install_macos_deps
    else
        install_linux_deps
    fi
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    install_llama_cpp
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    setup_python_venv
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Ask about model download
    read -p "Download the model now? (~19GB) [Y/n] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]] || [ -z "$REPLY" ]; then
        download_model
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
    fi
    
    validate_installation
    print_summary
}

# Parse command line arguments
if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --help, -h          Show this help message"
    echo "  --skip-model        Skip model download"
    echo "  --only-deps         Install dependencies only"
    echo "  --only-llama        Install llama.cpp only"
    echo "  --only-model        Download model only"
    echo ""
    echo "Examples:"
    echo "  $0                  # Full setup"
    echo "  $0 --skip-model     # Setup without model download"
    echo "  $0 --only-deps      # Install dependencies only"
    echo ""
    exit 0
fi

if [[ "$1" == "--skip-model" ]]; then
    SKIP_MODEL=1
elif [[ "$1" == "--only-deps" ]]; then
    ONLY_DEPS=1
elif [[ "$1" == "--only-llama" ]]; then
    ONLY_LLAMA=1
elif [[ "$1" == "--only-model" ]]; then
    ONLY_MODEL=1
fi

# Run main
main

# Handle special modes
if [[ "$ONLY_DEPS" == "1" ]]; then
    if [[ "$OS" == "macos" ]]; then
        install_macos_deps
    else
        install_linux_deps
    fi
    exit 0
fi

if [[ "$ONLY_LLAMA" == "1" ]]; then
    install_llama_cpp
    exit 0
fi

if [[ "$ONLY_MODEL" == "1" ]]; then
    download_model
    exit 0
fi

if [[ "$SKIP_MODEL" == "1" ]]; then
    echo ""
    log_info "Skipping model download"
    echo ""
    echo "To download the model later:"
    echo "  ./bin/download-model.sh"
    echo ""
fi
