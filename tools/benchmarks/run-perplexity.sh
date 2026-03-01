#!/usr/bin/env bash
#
# Perplexity Benchmark using llama-perplexity
# Measures model quality on test text
# Configuration loaded from config.yaml
#

set -e

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../../scripts/config.sh"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║              Perplexity Benchmark                        ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Configuration from config.yaml (command line args override)
MODEL="${1:-$MODEL_PATH}"
OUTPUT_DIR="${2:-${BENCHMARK_DIR:-benchmarks}/$(date +%Y%m%d_%H%M%S)}"
THREADS="${3:-$(sysctl -n hw.ncpu)}"

# Check model exists
if [ ! -f "$MODEL" ]; then
    echo "❌ Model not found: $MODEL"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

echo "📦 Model: $MODEL"
echo "📁 Output: $OUTPUT_DIR"
echo "🧵 Threads: $THREADS"
echo ""

# Create test texts
mkdir -p "$OUTPUT_DIR/texts"

# Short test text
cat > "$OUTPUT_DIR/texts/short.txt" << 'EOF'
The quick brown fox jumps over the lazy dog. This sentence contains every letter of the alphabet.
Artificial intelligence is transforming how we interact with technology and process information.
Machine learning models learn patterns from data to make predictions and decisions.
EOF

# Medium test text
cat > "$OUTPUT_DIR/texts/medium.txt" << 'EOF'
The development of large language models has revolutionized natural language processing.
These models are trained on vast amounts of text data and learn to predict the next token in a sequence.
Deep learning neural networks consist of multiple layers that process information hierarchically.
Transformers use self-attention mechanisms to capture long-range dependencies in text.
The scaling laws show that model performance improves predictably with more data and compute.
Modern language models can perform various tasks including translation, summarization, and question answering.
EOF

# Long test text (code)
cat > "$OUTPUT_DIR/texts/code.txt" << 'EOF'
def fibonacci(n):
    """Calculate the nth Fibonacci number using dynamic programming."""
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    
    dp = [0] * (n + 1)
    dp[1] = 1
    
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    
    return dp[n]

# Test the function
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
EOF

echo "Select test text:"
echo "  1) Short (general text, ~50 tokens)"
echo "  2) Medium (technical text, ~100 tokens)"
echo "  3) Code (Python code, ~80 tokens)"
echo "  4) Custom file"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        TEST_FILE="$OUTPUT_DIR/texts/short.txt"
        ;;
    2)
        TEST_FILE="$OUTPUT_DIR/texts/medium.txt"
        ;;
    3)
        TEST_FILE="$OUTPUT_DIR/texts/code.txt"
        ;;
    4)
        read -p "Enter path to test file: " TEST_FILE
        if [ ! -f "$TEST_FILE" ]; then
            echo "❌ File not found: $TEST_FILE"
            exit 1
        fi
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "📄 Test file: $TEST_FILE"
echo "📊 Tokens in file: $(wc -w < "$TEST_FILE") words"
echo ""

OUTPUT_FILE="$OUTPUT_DIR/perplexity-$(basename "$TEST_FILE" .txt).txt"

echo "Running perplexity test..."
echo ""

llama-perplexity \
    -m "$MODEL" \
    -f "$TEST_FILE" \
    -t "$THREADS" \
    -ngl 999 \
    --ctx-size 4096 \
    --flash-attn auto \
    2>&1 | tee "$OUTPUT_FILE"

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║              Benchmark Complete! ✅                      ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "📁 Results saved to: $OUTPUT_FILE"
echo ""

# Extract final perplexity if available
if grep -q "Final perplexity" "$OUTPUT_FILE"; then
    echo "📊 Final Perplexity:"
    grep "Final perplexity" "$OUTPUT_FILE"
fi
