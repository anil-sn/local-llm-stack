#!/usr/bin/env bash
#
# Qwen3.5-35B-A3B Performance Benchmark
# Tests generation speed, throughput, and latency
# Configuration loaded from config.yaml
#

set -e

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../../scripts/config.sh"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║      Qwen3.5-35B-A3B Performance Benchmark               ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

BASE_URL="http://localhost:$SERVER_PORT/v1"
RESULTS_DIR="${BENCHMARK_DIR:-benchmarks}"
mkdir -p "$RESULTS_DIR"

# Test prompts of varying complexity
PROMPTS=(
    "Hello!"
    "What is the capital of France?"
    "Explain quantum entanglement in simple terms."
    "Write a Python function to sort a list using merge sort."
    "Analyze the themes in Shakespeare's Hamlet."
)

TOKEN_TARGETS=(null)

echo "📍 Server: $BASE_URL"
echo "📍 Results: $RESULTS_DIR/"
echo ""

# Check server health
echo "Checking server health..."
HEALTH=$(curl -s "$BASE_URL/../health" 2>/dev/null || echo '{}')
if ! echo "$HEALTH" | jq -e '.status' > /dev/null 2>&1; then
    echo "❌ Server not responding. Start with: ./start-qwen.sh"
    exit 1
fi
echo "✅ Server is healthy"
echo ""

# Benchmark function
run_benchmark() {
    local prompt="$1"
    local max_tokens="$2"
    local test_name="$3"
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Test: $test_name"
    echo "Prompt: ${prompt:0:50}..."
    echo "Max tokens: unlimited"
    echo ""
    
    # Time the request
    START_TIME=$(date +%s.%N)
    
    RESPONSE=$(curl -s "$BASE_URL/chat/completions" \
        -H 'Content-Type: application/json' \
        -d "{
            \"model\": \"$ACTIVE_MODEL\",
            \"max_tokens\": null,
            \"messages\": [{\"role\": \"user\", \"content\": \"$prompt\"}]
        }")
    
    END_TIME=$(date +%s.%N)
    
    # Parse results
    TOTAL_TIME=$(echo "$END_TIME - $START_TIME" | bc)
    PROMPT_TOKENS=$(echo "$RESPONSE" | jq -r '.usage.prompt_tokens' 2>/dev/null || echo "0")
    COMP_TOKENS=$(echo "$RESPONSE" | jq -r '.usage.completion_tokens' 2>/dev/null || echo "0")
    TOTAL_TOKENS=$(echo "$RESPONSE" | jq -r '.usage.total_tokens' 2>/dev/null || echo "0")
    
    # Get timing details from llama.cpp
    PROMPT_MS=$(echo "$RESPONSE" | jq -r '.timings.prompt_ms' 2>/dev/null || echo "0")
    PREDICTED_MS=$(echo "$RESPONSE" | jq -r '.timings.predicted_ms' 2>/dev/null || echo "0")
    PROMPT_PS=$(echo "$RESPONSE" | jq -r '.timings.prompt_per_second' 2>/dev/null || echo "0")
    PREDICTED_PS=$(echo "$RESPONSE" | jq -r '.timings.predicted_per_second' 2>/dev/null || echo "0")
    
    # Get response content
    CONTENT=$(echo "$RESPONSE" | jq -r '.choices[0].message.content' 2>/dev/null || echo "")
    REASONING=$(echo "$RESPONSE" | jq -r '.choices[0].message.reasoning_content' 2>/dev/null || echo "")
    
    # Calculate metrics
    if [ "$PREDICTED_MS" != "0" ] && [ "$PREDICTED_MS" != "null" ]; then
        GEN_SPEED=$(echo "scale=2; $COMP_TOKENS / ($PREDICTED_MS / 1000)" | bc 2>/dev/null || echo "N/A")
    else
        GEN_SPEED="N/A"
    fi
    
    echo "📊 Results:"
    echo "   Total time: ${TOTAL_TIME}s"
    echo "   Tokens: $PROMPT_TOKENS (prompt) + $COMP_TOKENS (completion) = $TOTAL_TOKENS"
    echo "   Prompt processing: ${PROMPT_PS} tokens/sec"
    echo "   Generation speed: ${GEN_SPEED} tokens/sec"
    echo ""
    
    # Print response
    echo "📝 Response:"
    echo ""
    if [ -n "$REASONING" ] && [ "$REASONING" != "null" ]; then
        echo "💭 Reasoning:"
        echo "$REASONING"
        echo ""
    fi
    if [ -n "$CONTENT" ] && [ "$CONTENT" != "null" ]; then
        echo "📤 Output:"
        # Try to render with glow if available, otherwise plain text
        if command -v glow &> /dev/null; then
            echo "$CONTENT" | glow -s dark
        else
            echo "$CONTENT"
        fi
    else
        echo "(Response may continue beyond token limit)"
    fi
    echo ""
    
    # Save detailed results
    echo "$RESPONSE" | jq ". + {\"test_name\": \"$test_name\", \"total_time_sec\": $TOTAL_TIME}" > "$RESULTS_DIR/${test_name}.json"
}

# Run benchmarks
echo "🚀 Running benchmarks..."
echo ""

# Test 1: Simple greeting
run_benchmark "Hello!" null "01_greeting"

# Test 2: Factual question
run_benchmark "What is the capital of France? Answer in one sentence." null "02_factual"

# Test 3: Explanation
run_benchmark "Explain what a neural network is in 2-3 sentences." null "03_explanation"

# Test 4: Code generation
run_benchmark "Write a Python function to calculate fibonacci numbers." null "04_code"

# Test 5: Creative writing
run_benchmark "Write a short haiku about artificial intelligence." null "05_creative"

# Test 6: Long form
run_benchmark "Explain the theory of relativity in detail." null "06_longform"

# Test 7: Reasoning
run_benchmark "If all Bloops are Razzies and all Razzies are Lazzies, are all Bloops definitely Lazzies? Explain your reasoning." null "07_reasoning"

# Test 8: Math
run_benchmark "Solve: A train travels at 60 mph for 2 hours, then at 80 mph for 1.5 hours. How far did it travel total?" null "08_math"

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║              Benchmark Complete! ✅                      ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "📁 Results saved to: $RESULTS_DIR/"
echo ""

# Summary
echo "📊 Summary:"
echo ""
printf "%-20s %10s %12s %15s\n" "Test" "Tokens" "Time (s)" "Tokens/sec"
echo "──────────────────────────────────────────────────────────"

for file in "$RESULTS_DIR"/*.json; do
    if [ -f "$file" ]; then
        NAME=$(jq -r '.test_name' "$file")
        TOKENS=$(jq -r '.usage.completion_tokens' "$file")
        TIME=$(jq -r '.total_time_sec' "$file")
        if [ "$TIME" != "null" ] && [ "$TIME" != "0" ]; then
            PS=$(echo "scale=1; $TOKENS / $TIME" | bc 2>/dev/null || echo "N/A")
        else
            PS="N/A"
        fi
        printf "%-20s %10s %12s %15s\n" "$NAME" "$TOKENS" "$TIME" "$PS"
    fi
done

echo ""
echo "To view detailed results:"
echo "  cat $RESULTS_DIR/01_greeting.json | jq ."
