#!/usr/bin/env bash
#
# Quick API Benchmark - Reasoning vs Non-Reasoning Comparison
# Requires a running server
# Configuration loaded from config.yaml
#

set -e

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../../scripts/config.sh"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║         API Benchmark: Reasoning vs Non-Reasoning        ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Configuration from config.yaml
PORT="${1:-$SERVER_PORT}"
BASE_URL="http://localhost:$PORT/v1"
OUTPUT_DIR="${BENCHMARK_DIR:-benchmarks}/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

# Test prompts with expected complexity
declare -a PROMPTS=(
    "Say hello in one word."
    "What is 2 + 2?"
    "Explain what a neural network is in 2 sentences."
    "If all Bloops are Razzies and all Razzies are Lazzies, are all Bloops definitely Lazzies?"
    "Write a haiku about artificial intelligence."
)

declare -a NAMES=(
    "greeting"
    "math"
    "explanation"
    "reasoning"
    "creative"
)

echo "📍 Server: $BASE_URL"
echo "📁 Output: $OUTPUT_DIR"
echo ""

# Check server health
echo "Checking server health..."
HEALTH=$(curl -s "$BASE_URL/../health" 2>/dev/null || echo '{}')
if ! echo "$HEALTH" | jq -e '.status' > /dev/null 2>&1; then
    echo "❌ Server not responding at port $PORT"
    echo ""
    echo "Start server with:"
    echo "  ./bin/start-webui.sh           (no reasoning)"
    echo "  ./bin/start-webui-reasoning.sh (with reasoning)"
    exit 1
fi
echo "✅ Server is healthy"
echo ""

# Benchmark function
run_test() {
    local prompt="$1"
    local name="$2"
    local output_file="$3"
    
    local start_time=$(date +%s.%N)
    
    local response=$(curl -s "$BASE_URL/chat/completions" \
        -H 'Content-Type: application/json' \
        -d "{
            \"model\": \"$ACTIVE_MODEL\",
            \"max_tokens\": null,
            \"messages\": [{\"role\": \"user\", \"content\": \"$prompt\"}]
        }")
    
    local end_time=$(date +%s.%N)
    local total_time=$(echo "$end_time - $start_time" | bc)
    
    local prompt_tokens=$(echo "$response" | jq -r '.usage.prompt_tokens // 0')
    local comp_tokens=$(echo "$response" | jq -r '.usage.completion_tokens // 0')
    local total_tokens=$(echo "$response" | jq -r '.usage.total_tokens // 0')
    local pred_ps=$(echo "$response" | jq -r '.timings.predicted_per_second // 0')
    
    echo "  $name:"
    echo "    Tokens: $prompt_tokens + $comp_tokens = $total_tokens"
    echo "    Time: ${total_time}s"
    echo "    Speed: ${pred_ps} tok/s"
    echo ""
    
    # Save numeric data only (avoid JSON escaping issues with response text)
    echo "{\"test\":\"$name\",\"prompt_tokens\":$prompt_tokens,\"completion_tokens\":$comp_tokens,\"total_tokens\":$total_tokens,\"time_sec\":$total_time,\"tokens_per_sec\":$pred_ps}" >> "$output_file"
}

# Run benchmarks for current mode
run_benchmarks() {
    local mode="$1"
    local output_file="$OUTPUT_DIR/api-${mode}.jsonl"
    local json_file="$OUTPUT_DIR/api-${mode}.json"

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔹 Testing: $mode mode"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    > "$output_file"  # Clear file

    for i in "${!PROMPTS[@]}"; do
        run_test "${PROMPTS[$i]}" "${NAMES[$i]}" "$output_file"
    done

    # Convert JSONL to JSON array properly
    if [ -s "$output_file" ]; then
        jq -s '.' "$output_file" > "$json_file"
        rm "$output_file"
        echo ""
        echo "✅ Results saved to: $json_file"
    else
        echo "⚠️  No results generated"
    fi
    echo ""
}

# Get current server mode from logs or assume
echo "Starting benchmark..."
echo ""

run_benchmarks "current"

# Generate summary
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║              Benchmark Complete! ✅                      ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Calculate averages
echo "📊 Summary:"
echo ""

if [ -f "$OUTPUT_DIR/api-current.json" ]; then
    avg_speed=$(jq '[.[].tokens_per_sec] | add / length' "$OUTPUT_DIR/api-current.json" 2>/dev/null || echo "N/A")
    avg_tokens=$(jq '[.[].total_tokens] | add / length' "$OUTPUT_DIR/api-current.json" 2>/dev/null || echo "N/A")
    total_time=$(jq '[.[].time_sec] | add' "$OUTPUT_DIR/api-current.json" 2>/dev/null || echo "N/A")
    
    echo "  Average Speed: ${avg_speed} tokens/sec"
    echo "  Average Tokens: ${avg_tokens}"
    echo "  Total Time: ${total_time}s"
fi

echo ""
echo "📁 Results saved to: $OUTPUT_DIR"
echo ""
echo "To compare modes, run this script twice:"
echo "  1. Start server: ./bin/start-webui.sh"
echo "     Run benchmark: ./tools/benchmarks/run-api-benchmark.sh"
echo ""
echo "  2. Start server: ./bin/start-webui-reasoning.sh"
echo "     Run benchmark: ./tools/benchmarks/run-api-benchmark.sh"
