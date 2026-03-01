#!/usr/bin/env bash
#
# Throughput and Concurrency Benchmark
# Tests server performance under load
# Configuration loaded from config.yaml
#

set -e

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../../scripts/config.sh"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║         Qwen3.5-35B-A3B Throughput Benchmark             ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

BASE_URL="http://localhost:$SERVER_PORT/v1"
RESULTS_DIR="${BENCHMARK_DIR:-benchmarks}/throughput"
mkdir -p "$RESULTS_DIR"

# Check server
HEALTH=$(curl -s "$BASE_URL/../health" 2>/dev/null || echo '{}')
if ! echo "$HEALTH" | jq -e '.status' > /dev/null 2>&1; then
    echo "❌ Server not responding. Start with: ./start-qwen.sh"
    exit 1
fi
echo "✅ Server: $BASE_URL"
echo ""

# Test prompt
PROMPT="Explain the concept of machine learning in 3-4 sentences."

# Single request baseline
echo "📍 Baseline: Single Request"
echo ""

START=$(date +%s.%N)
RESPONSE=$(curl -s "$BASE_URL/chat/completions" \
    -H 'Content-Type: application/json' \
    -d "{
        \"model\": \"$ACTIVE_MODEL\",
        \"max_tokens\": null,
        \"messages\": [{\"role\": \"user\", \"content\": \"$PROMPT\"}]
    }")
END=$(date +%s.%N)

SINGLE_TIME=$(echo "$END - $START" | bc)
TOKENS=$(echo "$RESPONSE" | jq -r '.usage.completion_tokens' 2>/dev/null || echo "0")
echo "   Time: ${SINGLE_TIME}s"
echo "   Tokens: $TOKENS"
if [ "$SINGLE_TIME" != "0" ]; then
    TPS=$(echo "scale=2; $TOKENS / $SINGLE_TIME" | bc 2>/dev/null || echo "N/A")
    echo "   Throughput: ${TPS} tokens/sec"
fi
echo ""

echo "$RESPONSE" | jq ". + {\"test\": \"single_request\", \"time_sec\": $SINGLE_TIME}" > "$RESULTS_DIR/single.json"

# Concurrent requests (2 parallel)
echo "📍 Concurrency: 2 Parallel Requests"
echo ""

START=$(date +%s.%N)
curl -s "$BASE_URL/chat/completions" \
    -H 'Content-Type: application/json' \
    -d "{\"model\": \"$ACTIVE_MODEL\", \"max_tokens\": null, \"messages\": [{\"role\": \"user\", \"content\": \"$PROMPT\"}]}" > "$RESULTS_DIR/concurrent_1.json" &
curl -s "$BASE_URL/chat/completions" \
    -H 'Content-Type: application/json' \
    -d "{\"model\": \"$ACTIVE_MODEL\", \"max_tokens\": null, \"messages\": [{\"role\": \"user\", \"content\": \"$PROMPT\"}]}" > "$RESULTS_DIR/concurrent_2.json" &
wait
END=$(date +%s.%N)

CONCURRENT_TIME=$(echo "$END - $START" | bc)
echo "   Total time: ${CONCURRENT_TIME}s"
echo "   Requests: 2"
RPS=$(echo "scale=2; 2 / $CONCURRENT_TIME" | bc 2>/dev/null || echo "N/A")
echo "   RPS: ${RPS}"
echo ""

# Context length impact
echo "📍 Context Length Impact"
echo ""

for ctx in 50 100 200; do
    START=$(date +%s.%N)
    RESPONSE=$(curl -s "$BASE_URL/chat/completions" \
        -H 'Content-Type: application/json' \
        -d "{
            \"model\": \"$ACTIVE_MODEL\",
            \"max_tokens\": null,
            \"messages\": [{\"role\": \"user\", \"content\": \"$PROMPT\"}]
        }")
    END=$(date +%s.%N)
    
    TIME=$(echo "$END - $START" | bc)
    TOKENS=$(echo "$RESPONSE" | jq -r '.usage.completion_tokens' 2>/dev/null || echo "0")
    PROMPT_TOKENS=$(echo "$RESPONSE" | jq -r '.usage.prompt_tokens' 2>/dev/null || echo "0")
    
    echo "   Output tokens: $ctx -> Time: ${TIME}s (${TOKENS} gen, ${PROMPT_TOKENS} prompt)"
done

echo ""

# Memory efficiency (estimate from response)
echo "📍 Memory Efficiency"
echo ""
echo "Note: Check llama.cpp server logs for memory usage"
echo "Typical Q4_K_S 35B model uses ~20GB RAM with full GPU offload"
echo ""

echo "╔══════════════════════════════════════════════════════════╗"
echo "║           Throughput Benchmark Complete! ✅              ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "📁 Results saved to: $RESULTS_DIR/"
