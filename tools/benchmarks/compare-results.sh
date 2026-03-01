#!/usr/bin/env bash
#
# Compare benchmark results from different runs
#

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║           Benchmark Comparison Tool                      ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

BENCHMARKS_DIR="benchmarks"

# Find latest API benchmark results
find_latest_api() {
    ls -td "$BENCHMARKS_DIR"/20*/api-*.json 2>/dev/null | head -1
}

# Get average speed from JSON file
get_avg_speed() {
    local file="$1"
    if [ -f "$file" ]; then
        jq '[.[].tokens_per_sec] | add / length' "$file" 2>/dev/null || echo "N/A"
    else
        echo "N/A"
    fi
}

# Get test details
get_test_speed() {
    local file="$1"
    local test="$2"
    if [ -f "$file" ]; then
        jq -r ".[] | select(.test==\"$test\") | .tokens_per_sec" "$file" 2>/dev/null || echo "N/A"
    else
        echo "N/A"
    fi
}

# Get mode from filename
get_mode_from_file() {
    local file="$1"
    local basename=$(basename "$file")
    if [[ "$basename" == *"no-reasoning"* ]]; then
        echo "Non-Reasoning"
    elif [[ "$basename" == *"reasoning"* ]]; then
        echo "Reasoning"
    else
        echo "Current (auto)"
    fi
}

echo "Looking for benchmark results..."
echo ""

# Find all API benchmark files
API_FILES=$(ls -t "$BENCHMARKS_DIR"/20*/api-*.json 2>/dev/null || true)

if [ -z "$API_FILES" ]; then
    echo "⚠️  No API benchmark results found."
    echo ""
    echo "Run benchmarks first:"
    echo "  ./tools/benchmarks/run-api-benchmark.sh 8080"
else
    echo "📊 Found API Benchmark Results:"
    
    for file in $API_FILES; do
        if [ -f "$file" ]; then
            dir=$(dirname "$file")
            mode=$(get_mode_from_file "$file")
            avg=$(get_avg_speed "$file")
            timestamp=$(basename "$dir")
            echo "   [$timestamp] $mode: ${avg} tok/s avg"
        fi
    done
    echo ""
fi

# Show details for latest result
LATEST_FILE=$(find_latest_api)
if [ -n "$LATEST_FILE" ] && [ -f "$LATEST_FILE" ]; then
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║         Latest Run Details                               ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""
    
    mode=$(get_mode_from_file "$LATEST_FILE")
    avg=$(get_avg_speed "$LATEST_FILE")
    
    echo "  Mode: $mode"
    echo "  Average Speed: ${avg} tokens/sec"
    echo ""
    
    echo "  By Test:"
    for test in greeting math explanation reasoning creative; do
        speed=$(get_test_speed "$LATEST_FILE" "$test")
        if [ "$speed" != "N/A" ] && [ -n "$speed" ]; then
            printf "    %-12s %s tok/s\n" "$test:" "$speed"
        fi
    done
    echo ""
fi

# Show llama-bench results if available
LLAMA_BENCH_FILE="$BENCHMARKS_DIR/llama-bench.md"
if [ -f "$LLAMA_BENCH_FILE" ]; then
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║         Native Performance (llama-bench)                 ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""
    
    grep -E "^\|" "$LLAMA_BENCH_FILE" | tail -5
    echo ""
fi

# Show perplexity results if available
PERPLEXITY_FILE=$(ls -t "$BENCHMARKS_DIR"/20*/perplexity*.txt 2>/dev/null | head -1)
if [ -f "$PERPLEXITY_FILE" ]; then
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║         Perplexity Results                               ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""
    
    grep -i "perplexity" "$PERPLEXITY_FILE" | tail -5
    echo ""
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "To run new benchmarks:"
echo "  ./tools/benchmarks/run-all.sh              (full suite)"
echo "  ./tools/benchmarks/run-native-benchmark.sh (llama-bench)"
echo "  ./tools/benchmarks/run-api-benchmark.sh 8080 (API tests)"
echo "  ./tools/benchmarks/run-perplexity.sh       (perplexity)"
echo ""
