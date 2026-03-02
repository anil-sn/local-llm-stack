#!/usr/bin/env bash
#
# Cross-Platform Compatibility Test
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "╔══════════════════════════════════════════════════╗"
echo "║     Cross-Platform Compatibility Test            ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# Activate venv
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Detect platform
PLATFORM=$(uname -s)
echo "Platform: $PLATFORM"
echo ""

case "$PLATFORM" in
    Darwin)
        echo -e "${GREEN}✅ Running on macOS${NC}"
        echo ""
        
        # Test macOS-specific commands
        echo "Testing macOS system commands..."
        
        if sysctl -n hw.ncpu > /dev/null 2>&1; then
            CPU=$(sysctl -n hw.ncpu)
            echo -e "${GREEN}✅ CPU cores: $CPU${NC}"
        else
            echo -e "${RED}❌ sysctl failed${NC}"
        fi
        
        if sysctl -n hw.memsize > /dev/null 2>&1; then
            MEM=$(sysctl -n hw.memsize)
            MEM_GB=$((MEM / 1024 / 1024 / 1024))
            echo -e "${GREEN}✅ Memory: ${MEM_GB} GB${NC}"
        else
            echo -e "${RED}❌ Memory detection failed${NC}"
        fi
        
        # Test Metal GPU
        echo ""
        echo "Testing Metal GPU detection..."
        if llm-stack status system 2>&1 | grep -q "METAL"; then
            echo -e "${GREEN}✅ Metal GPU detected${NC}"
        else
            echo -e "${YELLOW}⚠️  Metal GPU not detected${NC}"
        fi
        ;;
        
    Linux)
        echo -e "${GREEN}✅ Running on Linux${NC}"
        echo ""
        
        # Test Linux-specific commands
        echo "Testing Linux system commands..."
        
        if [ -f /proc/cpuinfo ]; then
            CPU=$(grep -c "^processor" /proc/cpuinfo)
            echo -e "${GREEN}✅ CPU cores: $CPU${NC}"
        fi
        
        if [ -f /proc/meminfo ]; then
            MEM=$(grep "MemTotal" /proc/meminfo | awk '{print $2}')
            MEM_GB=$((MEM / 1024 / 1024))
            echo -e "${GREEN}✅ Memory: ${MEM_GB} GB${NC}"
        fi
        
        # Test GPU detection
        echo ""
        echo "Testing GPU detection..."
        
        if command -v nvidia-smi > /dev/null 2>&1; then
            echo -e "${GREEN}✅ NVIDIA GPU detected${NC}"
            nvidia-smi --query-gpu=name --format=csv,noheader
        elif command -v rocm-smi > /dev/null 2>&1; then
            echo -e "${GREEN}✅ AMD GPU detected${NC}"
        else
            echo -e "${YELLOW}⚠️  No GPU detected (CPU-only mode)${NC}"
        fi
        ;;
        
    *)
        echo -e "${YELLOW}⚠️  Unknown platform: $PLATFORM${NC}"
        ;;
esac

# Test CLI cross-platform functions
echo ""
echo "Testing CLI cross-platform functions..."

python3 << 'EOF'
from local_llm.utils import (
    get_platform,
    is_macos,
    is_linux,
    get_cpu_count,
    get_total_ram_gb,
    get_gpu_info
)

print(f"Platform: {get_platform()}")
print(f"Is macOS: {is_macos()}")
print(f"Is Linux: {is_linux()}")
print(f"CPU Count: {get_cpu_count()}")
print(f"Total RAM: {get_total_ram_gb():.1f} GB")

gpu = get_gpu_info()
print(f"GPU: {gpu['gpu_name']}")
print(f"GPU Type: {gpu['gpu_type']}")
print(f"Has GPU: {gpu['has_gpu']}")

print("\n✅ All cross-platform functions working!")
EOF

echo ""
echo -e "${GREEN}✅ Cross-platform test complete!${NC}"
