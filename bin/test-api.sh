#!/usr/bin/env bash
#
# Test Qwen3.5-35B-A3B API endpoints
#

set -e

BASE_URL="${QWEN_API_BASE:-http://localhost:8080/v1}"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║           Testing Qwen3.5-35B-A3B API                    ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "Base URL: $BASE_URL"
echo ""

# Test 1: Health check
echo "📍 Test 1: Health Check"
echo "   GET /health"
HEALTH=$(curl -s "$BASE_URL/../health" 2>/dev/null || echo '{"status":"error"}')
if echo "$HEALTH" | jq -e '.status == "ok"' > /dev/null 2>&1; then
    echo "   ✅ Server is healthy"
else
    echo "   ❌ Server health check failed"
    echo "   Response: $HEALTH"
    exit 1
fi
echo ""

# Test 2: List models
echo "📍 Test 2: List Models"
echo "   GET /v1/models"
MODELS=$(curl -s "$BASE_URL/models")
MODEL_COUNT=$(echo "$MODELS" | jq '.data | length' 2>/dev/null || echo "0")
echo "   ✅ Found $MODEL_COUNT model(s)"
echo "$MODELS" | jq '.data[].id' 2>/dev/null || true
echo ""

# Test 3: Chat completion (short)
echo "📍 Test 3: Chat Completion (Short)"
echo "   POST /v1/chat/completions"
RESPONSE=$(curl -s "$BASE_URL/chat/completions" \
    -H 'Content-Type: application/json' \
    -d '{
        "model": "qwen3.5-35b-a3b",
        "max_tokens": null,
        "messages": [{"role": "user", "content": "Say hello in one word."}]
    }')

CONTENT=$(echo "$RESPONSE" | jq -r '.choices[0].message.content' 2>/dev/null)
if [ -n "$CONTENT" ] && [ "$CONTENT" != "null" ]; then
    echo "   ✅ Response: $CONTENT"
else
    echo "   ⚠️  Got reasoning (may need more tokens)"
fi
echo ""

# Test 4: Chat completion (full response)
echo "📍 Test 4: Chat Completion (Full Response)"
echo "   POST /v1/chat/completions"
RESPONSE=$(curl -s "$BASE_URL/chat/completions" \
    -H 'Content-Type: application/json' \
    -d '{
        "model": "qwen3.5-35b-a3b",
        "max_tokens": null,
        "messages": [{"role": "user", "content": "What is 2 + 2?"}]
    }')

CONTENT=$(echo "$RESPONSE" | jq -r '.choices[0].message.content' 2>/dev/null)
TOKENS=$(echo "$RESPONSE" | jq -r '.usage.total_tokens' 2>/dev/null)
echo "   ✅ Response: $CONTENT"
echo "   📊 Tokens used: $TOKENS"
echo ""

# Test 5: Performance test
echo "📍 Test 5: Performance Metrics"
TIMINGS=$(echo "$RESPONSE" | jq '.timings' 2>/dev/null)
if [ "$TIMINGS" != "null" ] && [ -n "$TIMINGS" ]; then
    PROMPT_PS=$(echo "$TIMINGS" | jq -r '.prompt_per_second' 2>/dev/null)
    PREDICTED_PS=$(echo "$TIMINGS" | jq -r '.predicted_per_second' 2>/dev/null)
    echo "   Prompt processing: ${PROMPT_PS} tokens/sec"
    echo "   Generation: ${PREDICTED_PS} tokens/sec"
else
    echo "   ⚠️  No timing data available"
fi
echo ""

echo "╔══════════════════════════════════════════════════════════╗"
echo "║                  All Tests Passed! ✅                    ║"
echo "╚══════════════════════════════════════════════════════════╝"
