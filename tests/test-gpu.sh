#!/usr/bin/env bash
#
# GPU Detection Test
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "╔══════════════════════════════════════════════════╗"
echo "║     GPU Detection Test                           ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# Activate venv
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Get system info
echo "Getting system information..."
OUTPUT=$(llm-stack status system 2>&1)

echo "$OUTPUT" | grep -A 20 "System Information"

# Check GPU detection
echo ""
echo "Checking GPU detection..."

if echo "$OUTPUT" | grep -q "GPU"; then
    echo -e "${GREEN}✅ GPU detected${NC}"
    
    # Check GPU type
    if echo "$OUTPUT" | grep -q "METAL"; then
        echo -e "${GREEN}✅ Metal GPU (macOS)${NC}"
    elif echo "$OUTPUT" | grep -q "CUDA"; then
        echo -e "${GREEN}✅ NVIDIA CUDA GPU${NC}"
    elif echo "$OUTPUT" | grep -q "ROCm"; then
        echo -e "${GREEN}✅ AMD ROCm GPU${NC}"
    else
        echo -e "${YELLOW}⚠️  GPU type unknown${NC}"
    fi
    
    # Check recommended layers
    if echo "$OUTPUT" | grep -q "Recommended Layers"; then
        LAYERS=$(echo "$OUTPUT" | grep "Recommended Layers" | awk '{print $NF}')
        echo -e "${GREEN}✅ Recommended layers: $LAYERS${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No GPU detected (CPU-only mode)${NC}"
fi

# Test Python API
echo ""
echo "Testing Python GPU API..."
python3 -c "
from local_llm.utils import get_gpu_info
info = get_gpu_info()
print(f'GPU Info: {info}')
if info['has_gpu']:
    print(f'✅ GPU: {info[\"gpu_name\"]}')
    print(f'   Type: {info[\"gpu_type\"]}')
    print(f'   Layers: {info[\"recommended_layers\"]}')
else:
    print('⚠️  No GPU detected')
"

echo ""
echo -e "${GREEN}✅ GPU detection test complete!${NC}"
