#!/usr/bin/env bash
#
# Install llama.cpp with Auto-Detection or Manual GPU/CPU Selection
# 
# This script will:
# 1. Auto-detect hardware (NVIDIA GPU or CPU-only)
# 2. Install required build dependencies
# 3. Clone llama.cpp from GitHub
# 4. Build with optimal settings for your hardware
# 5. Install binaries to /usr/local/bin
#
# Usage: 
#   ./install-llama-cpp-linux.sh              # Auto-detect (recommended)
#   ./install-llama-cpp-linux.sh --cuda       # Force CUDA build
#   ./install-llama-cpp-linux.sh --cpu        # Force CPU-only build
#   ./install-llama-cpp-linux.sh --help       # Show help
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Build type (auto, cuda, cpu)
BUILD_TYPE="auto"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --cuda)
            BUILD_TYPE="cuda"
            shift
            ;;
        --cpu)
            BUILD_TYPE="cpu"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Install llama.cpp with optimal settings for your hardware."
            echo ""
            echo "Options:"
            echo "  --cuda      Force CUDA GPU build (requires NVIDIA GPU)"
            echo "  --cpu       Force CPU-only build (no GPU acceleration)"
            echo "  --help, -h  Show this help message"
            echo ""
            echo "Default: Auto-detect hardware and choose optimal build"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Function to print header
print_header() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║     Install llama.cpp for Linux                          ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Function to detect hardware
detect_hardware() {
    echo -e "${CYAN}🔍 Detecting Hardware...${NC}"
    echo ""
    
    local has_nvidia=false
    local has_cuda=false
    local cuda_version=""
    local gpu_name=""
    
    # Check for NVIDIA GPU
    if command -v nvidia-smi &> /dev/null; then
        has_nvidia=true
        gpu_name=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)
        echo -e "${GREEN}✅ NVIDIA GPU detected: $gpu_name${NC}"
        
        # Check for CUDA
        if command -v nvcc &> /dev/null; then
            has_cuda=true
            cuda_version=$(nvcc --version | grep "release" | awk '{print $6}' | tr -d ',')
            echo -e "${GREEN}✅ CUDA compiler found: $cuda_version${NC}"
        else
            echo -e "${YELLOW}⚠️  CUDA compiler not found in PATH${NC}"
            echo "   (CUDA runtime detected, will try to use system CUDA)"
        fi
    else
        echo -e "${YELLOW}⚠️  No NVIDIA GPU detected${NC}"
    fi
    
    # Check CPU cores
    CPU_CORES=$(nproc)
    echo -e "${GREEN}✅ CPU Cores: $CPU_CORES${NC}"
    
    # Check RAM
    TOTAL_RAM_KB=$(grep "MemTotal" /proc/meminfo | awk '{print $2}')
    TOTAL_RAM_GB=$((TOTAL_RAM_KB / 1024 / 1024))
    echo -e "${GREEN}✅ Total RAM: ${TOTAL_RAM_GB} GB${NC}"
    
    echo ""
    
    # Determine build type
    if [ "$BUILD_TYPE" = "auto" ]; then
        if [ "$has_nvidia" = true ]; then
            BUILD_TYPE="cuda"
            echo -e "${CYAN}📌 Auto-selected: ${GREEN}CUDA GPU Build${NC}"
            echo "   Your system has an NVIDIA GPU, enabling GPU acceleration"
        else
            BUILD_TYPE="cpu"
            echo -e "${CYAN}📌 Auto-selected: ${YELLOW}CPU-Only Build${NC}"
            echo "   No NVIDIA GPU detected, building CPU-only version"
        fi
    else
        if [ "$BUILD_TYPE" = "cuda" ]; then
            if [ "$has_nvidia" = false ]; then
                echo -e "${RED}❌ CUDA build requested but no NVIDIA GPU detected${NC}"
                echo "   Please use --cpu for CPU-only build"
                exit 1
            fi
            echo -e "${CYAN}📌 Selected: ${GREEN}CUDA GPU Build${NC} (forced)"
        else
            echo -e "${CYAN}📌 Selected: ${YELLOW}CPU-Only Build${NC} (forced)"
        fi
    fi
    
    echo ""
    
    # Export for later use
    export HAS_NVIDIA=$has_nvidia
    export HAS_CUDA=$has_cuda
    export CUDA_VERSION=$cuda_version
    export GPU_NAME=$gpu_name
    export CPU_CORES=$CPU_CORES
    export TOTAL_RAM_GB=$TOTAL_RAM_GB
}

# Install build dependencies
install_dependencies() {
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
}

# Clone llama.cpp
clone_llama_cpp() {
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
}

# Build llama.cpp
build_llama_cpp() {
    echo ""
    if [ "$BUILD_TYPE" = "cuda" ]; then
        echo -e "${YELLOW}🔨 Building llama.cpp with CUDA support...${NC}"
        echo "This may take 5-10 minutes depending on your system..."
        
        # CUDA build flags
        CMAKE_FLAGS=(
            "-DGGML_CUDA=ON"
            "-DGGML_CUDA_F16=ON"
            "-DCMAKE_BUILD_TYPE=Release"
            "-DGGML_NATIVE=OFF"
        )
        BUILD_DESC="CUDA GPU"
    else
        echo -e "${YELLOW}🔨 Building llama.cpp (CPU-only)...${NC}"
        echo "This may take 5-10 minutes depending on your system..."
        
        # CPU-only build flags
        CMAKE_FLAGS=(
            "-DGGML_CUDA=OFF"
            "-DGGML_OPENBLAS=ON"
            "-DCMAKE_BUILD_TYPE=Release"
            "-DGGML_NATIVE=OFF"
        )
        BUILD_DESC="CPU-Only"
    fi
    
    # Create build directory
    rm -rf build
    mkdir -p build
    cd build
    
    # Configure with CMake
    echo -e "${BLUE}Configuring build with CMake ($BUILD_DESC)...${NC}"
    echo "CMake flags: ${CMAKE_FLAGS[*]}"
    echo ""
    
    cmake .. "${CMAKE_FLAGS[@]}"
    
    # Build
    echo -e "${BLUE}Building llama.cpp (using $CPU_CORES cores)...${NC}"
    cmake --build . --config Release -j"$CPU_CORES"
    
    echo -e "${GREEN}✅ Build complete${NC}"
}

# Install binaries
install_binaries() {
    echo ""
    echo -e "${YELLOW}📦 Installing binaries to /usr/local/bin...${NC}"
    
    # Copy all llama-* binaries
    sudo cp bin/llama-* /usr/local/bin/
}

# Verify installation
verify_installation() {
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
    echo -e "Build Type:  ${CYAN}$BUILD_DESC${NC}"
    echo -e "Installed:   ${GREEN}$INSTALLED_TOOLS${NC}"
    echo -e "Missing:     ${RED}$MISSING_TOOLS${NC}"
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
}

# Main execution
main() {
    # Check if running on Linux
    if [ "$(uname)" != "Linux" ]; then
        echo -e "${RED}❌ This script is for Linux only${NC}"
        echo "For macOS, use: brew install llama.cpp"
        exit 1
    fi
    
    print_header
    detect_hardware
    install_dependencies
    clone_llama_cpp
    build_llama_cpp
    install_binaries
    verify_installation
}

# Run main
main
