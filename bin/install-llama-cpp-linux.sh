#!/usr/bin/env bash
#
# Install llama.cpp with CUDA Support on Linux
# 
# This script will:
# 1. Install required build dependencies
# 2. Clone llama.cpp from GitHub
# 3. Build with CUDA GPU acceleration
# 4. Install binaries to /usr/local/bin
#
# Usage: ./install-llama-cpp-linux.sh
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Install llama.cpp with CUDA Support (Linux)          ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running on Linux
if [ "$(uname)" != "Linux" ]; then
    echo -e "${RED}❌ This script is for Linux only${NC}"
    echo "For macOS, use: brew install llama.cpp"
    exit 1
fi

# Check for NVIDIA GPU
echo -e "${YELLOW}📊 Checking for NVIDIA GPU...${NC}"
if command -v nvidia-smi &> /dev/null; then
    NVIDIA_GPU=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)
    echo -e "${GREEN}✅ NVIDIA GPU detected: $NVIDIA_GPU${NC}"
else
    echo -e "${RED}❌ No NVIDIA GPU detected${NC}"
    echo "This script requires CUDA support. Please check your NVIDIA installation."
    exit 1
fi

# Check for CUDA
echo -e "${YELLOW}📊 Checking for CUDA...${NC}"
if command -v nvcc &> /dev/null; then
    CUDA_VERSION=$(nvcc --version | grep "release" | awk '{print $6}' | tr -d ',')
    echo -e "${GREEN}✅ CUDA detected: $CUDA_VERSION${NC}"
else
    echo -e "${YELLOW}⚠️  CUDA not found in PATH${NC}"
    echo "CUDA will be built into llama.cpp if available"
fi

# Install build dependencies
echo ""
echo -e "${YELLOW}📦 Installing build dependencies...${NC}"

# Detect package manager
if command -v apt-get &> /dev/null; then
    echo "Using apt (Debian/Ubuntu)"
    sudo apt-get update
    sudo apt-get install -y \
        build-essential \
        cmake \
        git \
        libopenblas-dev \
        libatlas-base-dev \
        libblas-dev \
        liblapack-dev
elif command -v dnf &> /dev/null; then
    echo "Using dnf (Fedora/RHEL)"
    sudo dnf install -y \
        gcc \
        gcc-c++ \
        make \
        cmake \
        git \
        openblas-devel
elif command -v yum &> /dev/null; then
    echo "Using yum (CentOS/RHEL)"
    sudo yum install -y \
        gcc \
        gcc-c++ \
        make \
        cmake \
        git \
        openblas-devel
elif command -v pacman &> /dev/null; then
    echo "Using pacman (Arch Linux)"
    sudo pacman -S --noconfirm \
        base-devel \
        cmake \
        git \
        openblas
else
    echo -e "${RED}❌ Unsupported package manager${NC}"
    echo "Please install: build-essential, cmake, git"
    exit 1
fi

echo -e "${GREEN}✅ Dependencies installed${NC}"

# Clone llama.cpp
LLAMA_DIR="$HOME/llama.cpp"
if [ -d "$LLAMA_DIR" ]; then
    echo ""
    echo -e "${YELLOW}📁 llama.cpp directory already exists${NC}"
    echo -n "Do you want to update it? (y/n): "
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "Updating llama.cpp..."
        cd "$LLAMA_DIR"
        git pull
    else
        echo "Using existing llama.cpp installation"
    fi
else
    echo ""
    echo -e "${YELLOW}📥 Cloning llama.cpp from GitHub...${NC}"
    cd ~
    git clone https://github.com/ggml-org/llama.cpp
    cd llama.cpp
fi

# Build with CUDA
echo ""
echo -e "${YELLOW}🔨 Building llama.cpp with CUDA support...${NC}"
echo "This may take 5-10 minutes depending on your system..."

# Create build directory
rm -rf build
mkdir -p build
cd build

# Configure with CMake
echo -e "${BLUE}Configuring build with CMake...${NC}"
cmake .. \
    -DGGML_CUDA=ON \
    -DGGML_CUDA_F16=ON \
    -DCMAKE_BUILD_TYPE=Release \
    -DGGML_NATIVE=OFF

# Build
echo -e "${BLUE}Building llama.cpp...${NC}"
cmake --build . --config Release -j$(nproc)

echo -e "${GREEN}✅ Build complete${NC}"

# Install binaries
echo ""
echo -e "${YELLOW}📦 Installing binaries to /usr/local/bin...${NC}"

# Copy all llama-* binaries
sudo cp bin/llama-* /usr/local/bin/

# Verify installation
echo ""
echo -e "${YELLOW}🔍 Verifying installation...${NC}"

INSTALLED_TOOLS=0
MISSING_TOOLS=0

check_tool() {
    local tool=$1
    if command -v "$tool" &> /dev/null; then
        echo -e "${GREEN}✅ $tool${NC}"
        ((INSTALLED_TOOLS++))
    else
        echo -e "${RED}❌ $tool${NC}"
        ((MISSING_TOOLS++))
    fi
}

echo "Installed tools:"
check_tool llama-server
check_tool llama-cli
check_tool llama-bench
check_tool llama-perplexity
check_tool llama-gguf
check_tool llama-quantize
check_tool llama-imatrix

echo ""
echo "══════════════════════════════════════════════════"
echo "Installation Summary"
echo "══════════════════════════════════════════════════"
echo -e "Installed: ${GREEN}$INSTALLED_TOOLS${NC}"
echo -e "Missing:   ${RED}$MISSING_TOOLS${NC}"
echo ""

if [ $MISSING_TOOLS -eq 0 ]; then
    echo -e "${GREEN}✅ llama.cpp installation complete!${NC}"
    echo ""
    echo "You can now use:"
    echo "  llama-server --help"
    echo "  llama-cli --help"
    echo "  llama-bench --help"
    echo ""
    echo "Or use the Local LLM Stack CLI:"
    echo "  llm-stack status dependencies"
    echo "  llm-stack server start"
    echo "  llm-stack chat interactive"
else
    echo -e "${YELLOW}⚠️  Some tools are missing${NC}"
    echo "Check build logs for errors"
fi

echo ""
echo "Build directory: $HOME/llama.cpp/build"
echo "Binaries installed to: /usr/local/bin"
echo ""
