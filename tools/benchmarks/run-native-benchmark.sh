#!/usr/bin/env bash
#
# Native Performance Benchmark using llama-bench
# Measures raw model performance (prompt processing + generation speed)
# Configuration loaded from config.yaml
#

set -e

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../../scripts/config.sh"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║         Native Performance Benchmark (llama-bench)       ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Configuration from config.yaml (command line args override)
MODEL="${1:-$MODEL_PATH}"
OUTPUT_DIR="${2:-${BENCHMARK_DIR:-benchmarks}/$(date +%Y%m%d_%H%M%S)}"
THREADS="${3:-$(sysctl -n hw.ncpu)}"
REPETITIONS="${4:-$BENCH_REPETITIONS:-3}"

# Check model exists
if [ ! -f "$MODEL" ]; then
    echo "❌ Model not found: $MODEL"
    echo ""
    echo "Download with: ./bin/download-model.sh"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

echo "📦 Model: $MODEL"
echo "📁 Output: $OUTPUT_DIR"
echo "🧵 Threads: $THREADS"
echo "🔄 Repetitions: $REPETITIONS"
echo ""

# Get system info
echo "📊 System Information:"
echo "   CPU: $(sysctl -n machdep.cpu.brand_string 2>/dev/null || echo 'Unknown')"
echo "   Cores: $THREADS"
echo "   Memory: $(( $(sysctl -n hw.memsize) / 1024 / 1024 / 1024 ))GB"
echo ""

OUTPUT_FILE="$OUTPUT_DIR/llama-bench.md"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔹 Running llama-bench"
echo "   Prompt tokens: 512"
echo "   Generation tokens: 128"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Run llama-bench (note: reasoning flags not supported in llama-bench)
llama-bench \
    -m "$MODEL" \
    -p 512 \
    -n 128 \
    -r "$REPETITIONS" \
    -t "$THREADS" \
    -ngl 999 \
    -b 512 \
    -ub 256 \
    --flash-attn 1 \
    -o md \
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
    echo "📊 Key Metrics (from markdown table):"
    grep -E "^\|" "$OUTPUT_FILE" | tail -10
fi

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║              Benchmark Complete! ✅                      ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "📁 Results: $OUTPUT_DIR"
echo ""
echo "To view full results:"
echo "  cat $OUTPUT_FILE"
