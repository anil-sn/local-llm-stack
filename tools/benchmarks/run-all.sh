#!/usr/bin/env bash
#
# Complete Benchmark Suite for Qwen3.5-35B-A3B
# Integrates all llama.cpp benchmarking tools
#

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║    Qwen3.5-35B-A3B Complete Benchmark Suite              ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Configuration
MODEL="${1:-$HOME/models/Qwen3.5-35B-A3B-UD-Q4_K_XL.gguf}"
OUTPUT_DIR="${2:-benchmarks/$(date +%Y%m%d_%H%M%S)}"

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

# Check for required tools
echo "🔧 Checking required tools..."
TOOLS_OK=true

for tool in llama-bench llama-perplexity jq; do
    if command -v $tool &> /dev/null; then
        echo "   ✅ $tool"
    else
        echo "   ❌ $tool (not found)"
        TOOLS_OK=false
    fi
done

# Optional tools
echo ""
echo "Optional tools:"
for tool in llama-batched-bench llama-gguf-hash llama-cli; do
    if command -v $tool &> /dev/null; then
        echo "   ✅ $tool"
    else
        echo "   ⚪ $tool (optional)"
    fi
done

if [ "$TOOLS_OK" = false ]; then
    echo ""
    echo "❌ Some required tools are missing"
    echo "   Install: brew install llama.cpp"
    exit 1
fi

echo ""

# Run model validation
run_validation() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔹 Step 1: Model Validation"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    ./bin/validate-model.sh "$MODEL" 2>&1 | tee "$OUTPUT_DIR/validation.txt"
    echo ""
}

# Run llama-bench (native performance)
run_llama_bench() {
    local output_file="$OUTPUT_DIR/llama-bench.md"
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔹 Step 2: Native Performance (llama-bench)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    llama-bench \
        -m "$MODEL" \
        -p 512 \
        -n 128 \
        -r 3 \
        -t $(sysctl -n hw.ncpu) \
        -ngl 999 \
        -b 512 \
        -ub 256 \
        --flash-attn 1 \
        -o md \
        2>&1 | tee "$output_file"
    
    echo ""
    echo "✅ Results saved to: $output_file"
    echo ""
}

# Run perplexity test
run_perplexity() {
    local output_file="$OUTPUT_DIR/perplexity.txt"
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔹 Step 3: Perplexity Test (llama-perplexity)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    local test_text="$OUTPUT_DIR/test_text.txt"
    cat > "$test_text" << 'EOF'
The quick brown fox jumps over the lazy dog. This sentence contains every letter of the alphabet.
Artificial intelligence is transforming how we interact with technology and process information.
Machine learning models learn patterns from data to make predictions and decisions.
The development of large language models has revolutionized natural language processing.
Deep learning neural networks consist of multiple layers that process information hierarchically.
EOF
    
    llama-perplexity \
        -m "$MODEL" \
        -f "$test_text" \
        -t $(sysctl -n hw.ncpu) \
        -ngl 999 \
        --ctx-size 4096 \
        --flash-attn 1 \
        2>&1 | tee "$output_file"
    
    echo ""
    echo "✅ Results saved to: $output_file"
    echo ""
}

# Run batched benchmark
run_batched_bench() {
    local output_file="$OUTPUT_DIR/batched-bench.md"
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔹 Step 4: Batched Throughput (llama-batched-bench)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    if command -v llama-batched-bench &> /dev/null; then
        llama-batched-bench \
            -m "$MODEL" \
            -t $(sysctl -n hw.ncpu) \
            -ngl 999 \
            -b 256 \
            -ub 256 \
            -c 256 \
            --flash-attn 1 \
            -n 256 \
            --batch-count 10 \
            -o md \
            2>&1 | tee "$output_file"
        
        echo ""
        echo "✅ Results saved to: $output_file"
    else
        echo "⚪ Skipped: llama-batched-bench not installed"
    fi
    echo ""
}

# Run API benchmark (optional, requires server)
run_api_benchmark() {
    local port="${1:-8080}"
    local output_file="$OUTPUT_DIR/api-benchmark.json"
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔹 Step 5: API Benchmark (optional)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    read -p "Run API benchmark? (requires server on port $PORT) [y/N] " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ./tools/benchmarks/run-api-benchmark.sh "$port" 2>&1 | tee -a "$output_file"
    else
        echo "⚪ Skipped"
    fi
    echo ""
}

# Generate summary report
generate_summary() {
    local summary_file="$OUTPUT_DIR/SUMMARY.md"
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔹 Generating Summary Report"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    cat > "$summary_file" << EOF
# Qwen3.5-35B-A3B Benchmark Summary

**Date:** $(date -Iseconds)
**Model:** $MODEL
**System:** $(sysctl -n machdep.cpu.brand_string 2>/dev/null || echo 'Unknown')
**Cores:** $(sysctl -n hw.ncpu)
**Memory:** $(( $(sysctl -n hw.memsize) / 1024 / 1024 / 1024 ))GB

---

## Results

### Native Performance (llama-bench)
EOF
    
    if [ -f "$OUTPUT_DIR/llama-bench.md" ]; then
        grep -E "^\|" "$OUTPUT_DIR/llama-bench.md" >> "$summary_file" 2>/dev/null || echo "No data" >> "$summary_file"
    else
        echo "Not run" >> "$summary_file"
    fi
    
    cat >> "$summary_file" << EOF

### Perplexity
EOF
    
    if [ -f "$OUTPUT_DIR/perplexity.txt" ]; then
        grep -i "perplexity" "$OUTPUT_DIR/perplexity.txt" | tail -3 >> "$summary_file" 2>/dev/null || echo "No data" >> "$summary_file"
    else
        echo "Not run" >> "$summary_file"
    fi
    
    cat >> "$summary_file" << EOF

### Batched Throughput
EOF
    
    if [ -f "$OUTPUT_DIR/batched-bench.md" ]; then
        grep -E "^\|" "$OUTPUT_DIR/batched-bench.md" >> "$summary_file" 2>/dev/null || echo "No data" >> "$summary_file"
    else
        echo "Not run" >> "$summary_file"
    fi
    
    echo ""
    echo "✅ Summary saved to: $summary_file"
    echo ""
}

# Main execution
echo "Select benchmark mode:"
echo "  1) Quick (llama-bench only)"
echo "  2) Standard (llama-bench + perplexity)"
echo "  3) Full (all benchmarks)"
echo "  4) Custom (select individual tests)"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        run_llama_bench
        generate_summary
        ;;
    2)
        run_llama_bench
        run_perplexity
        generate_summary
        ;;
    3)
        run_validation
        run_llama_bench
        run_perplexity
        run_batched_bench
        generate_summary
        ;;
    4)
        echo ""
        echo "Select tests to run:"
        read -p "  Run validation? [y/N] " run_val; [[ "$run_val" =~ ^[Yy]$ ]] && run_validation
        read -p "  Run llama-bench? [y/N] " run_lb; [[ "$run_lb" =~ ^[Yy]$ ]] && run_llama_bench
        read -p "  Run perplexity? [y/N] " run_ppl; [[ "$run_ppl" =~ ^[Yy]$ ]] && run_perplexity
        read -p "  Run batched-bench? [y/N] " run_bb; [[ "$run_bb" =~ ^[Yy]$ ]] && run_batched_bench
        generate_summary
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

# Final summary
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║              Benchmark Complete! ✅                      ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "📁 Results saved to: $OUTPUT_DIR"
echo ""
echo "Files generated:"
ls -la "$OUTPUT_DIR"
echo ""

# Show quick summary
if [ -f "$OUTPUT_DIR/SUMMARY.md" ]; then
    echo "📊 Quick Summary:"
    echo ""
    cat "$OUTPUT_DIR/SUMMARY.md"
fi

echo ""
echo "To view detailed results:"
echo "  cat $OUTPUT_DIR/*.md"
echo "  cat $OUTPUT_DIR/*.txt"
echo "  cat $OUTPUT_DIR/*.json | jq ."
