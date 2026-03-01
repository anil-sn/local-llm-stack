#!/usr/bin/env bash
#
# Batched Throughput Benchmark using llama-batched-bench
# Tests concurrent request handling and throughput
# Configuration loaded from config.yaml
#

set -e

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../../scripts/config.sh"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║      Batched Throughput Benchmark                        ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Configuration from config.yaml (command line args override)
MODEL="${1:-$MODEL_PATH}"
OUTPUT_DIR="${2:-${BENCHMARK_DIR:-benchmarks}/$(date +%Y%m%d_%H%M%S)}"

# Check model exists
if [ ! -f "$MODEL" ]; then
    echo "❌ Model not found: $MODEL"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

echo "📦 Model: $MODEL"
echo "📁 Output: $OUTPUT_DIR"
echo ""

# Get system info
echo "📊 System Information:"
echo "   CPU: $(sysctl -n machdep.cpu.brand_string 2>/dev/null || echo 'Unknown')"
echo "   Cores: $(sysctl -n hw.ncpu)"
echo "   Memory: $(( $(sysctl -n hw.memsize) / 1024 / 1024 / 1024 ))GB"
echo ""

# Check for llama-batched-bench
if ! command -v llama-batched-bench &> /dev/null; then
    echo "❌ llama-batched-bench not found"
    echo "   Install: brew install llama.cpp"
    exit 1
fi

echo "Select test scenario:"
echo "  1) Quick test (single batch)"
echo "  2) Standard test (multiple configurations)"
echo "  3) Full test (comprehensive)"
echo ""
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        # Quick test
        NPP="256"
        NTG="128"
        NPL="1"
        ;;
    2)
        # Standard test
        NPP="128,256,512"
        NTG="64,128"
        NPL="1,2,4"
        ;;
    3)
        # Full test
        NPP="64,128,256,512"
        NTG="32,64,128,256"
        NPL="1,2,4,8"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

OUTPUT_FILE="$OUTPUT_DIR/batched-bench.md"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔹 Running Batched Benchmark"
echo "   Prompt tokens (-npp): $NPP"
echo "   Generation tokens (-ntg): $NTG"
echo "   Parallel prompts (-npl): $NPL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

llama-batched-bench \
    -m "$MODEL" \
    -t $(sysctl -n hw.ncpu) \
    -ngl 999 \
    -b 512 \
    -ub 256 \
    -c 4096 \
    --flash-attn 1 \
    -npp "$NPP" \
    -ntg "$NTG" \
    -npl "$NPL" \
    --output-format md \
    2>&1 | tee "$OUTPUT_FILE"

echo ""
echo "✅ Results saved to: $OUTPUT_FILE"
echo ""

# Extract key metrics
echo "╔══════════════════════════════════════════════════════════╗"
echo "║              Performance Summary                         ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

if [ -f "$OUTPUT_FILE" ]; then
    grep -E "^\|" "$OUTPUT_FILE" | tail -15
fi

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║              Benchmark Complete! ✅                      ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "📁 Results: $OUTPUT_DIR"
