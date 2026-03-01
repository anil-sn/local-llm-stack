#!/usr/bin/env bash
#
# Test Claude Code Integration
# Verifies that local LLM is properly configured for Claude Code CLI
# Configuration loaded from config.yaml
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Load configuration
source "$SCRIPT_DIR/config.sh"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║        Claude Code Integration Test Suite                ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

TESTS_PASSED=0
TESTS_FAILED=0

# Test function
run_test() {
    local test_name="$1"
    local test_cmd="$2"

    echo -n "🧪 Testing: $test_name... "

    if eval "$test_cmd" > /dev/null 2>&1; then
        echo "✅ PASS"
        ((TESTS_PASSED++))
        return 0
    else
        echo "❌ FAIL"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Test 1: Server health check
run_test "Server Health Check" "curl -s http://localhost:$SERVER_PORT/health | jq -e '.status == \"ok\"'"

# Test 2: Models endpoint
run_test "Models Endpoint" "curl -s http://localhost:$SERVER_PORT/v1/models | jq -e '.data | length > 0'"

# Test 3: Chat completion API
run_test "Chat Completion API" "curl -s http://localhost:$SERVER_PORT/v1/chat/completions -H 'Content-Type: application/json' -d '{\"model\":\"test\",\"messages\":[{\"role\":\"user\",\"content\":\"hi\"}],\"max_tokens\":10}' | jq -e '.choices | length > 0'"

# Test 4: Environment variables
echo -n "🧪 Testing: Environment Variables... "
source "$SCRIPT_DIR/claude-code.sh" > /dev/null 2>&1
if [ "$CLAUDE_CODE_DISABLE_TELEMETRY" = "1" ] && \
   [ "$ANTHROPIC_AUTH_TOKEN" = "dummy" ] && \
   [ "$ANTHROPIC_BASE_URL" = "http://localhost:$SERVER_PORT" ] && \
   [ -n "$ANTHROPIC_MODEL" ]; then
    echo "✅ PASS"
    ((TESTS_PASSED++))
else
    echo "❌ FAIL"
    ((TESTS_FAILED++))
fi

# Test 5: Model name matches config
echo -n "🧪 Testing: Model Name from Config... "
source "$PROJECT_ROOT/scripts/config.sh" > /dev/null 2>&1
if [ "$ANTHROPIC_MODEL" = "$MODEL_NAME" ]; then
    echo "✅ PASS ($ANTHROPIC_MODEL)"
    ((TESTS_PASSED++))
else
    echo "❌ FAIL (Expected: $MODEL_NAME, Got: $ANTHROPIC_MODEL)"
    ((TESTS_FAILED++))
fi

# Test 6: Claude Code CLI installed
run_test "Claude Code CLI Installed" "which claude"

# Test 7: API response format
echo -n "🧪 Testing: API Response Format... "
RESPONSE=$(curl -s http://localhost:$SERVER_PORT/v1/chat/completions \
    -H 'Content-Type: application/json' \
    -d '{
        "model":"test",
        "messages":[{"role":"user","content":"Say hello"}],
        "max_tokens":10
    }')

if echo "$RESPONSE" | jq -e '.choices[0].message.content' > /dev/null 2>&1; then
    CONTENT=$(echo "$RESPONSE" | jq -r '.choices[0].message.content')
    echo "✅ PASS (Response: $CONTENT)"
    ((TESTS_PASSED++))
else
    echo "❌ FAIL"
    ((TESTS_FAILED++))
fi

# Test 8: Performance check
echo -n "🧪 Testing: API Response Time... "
START_TIME=$(date +%s%N)
curl -s http://localhost:$SERVER_PORT/v1/chat/completions \
    -H 'Content-Type: application/json' \
    -d '{
        "model":"test",
        "messages":[{"role":"user","content":"Hi"}],
        "max_tokens":20
    }' > /dev/null
END_TIME=$(date +%s%N)
DURATION=$(( (END_TIME - START_TIME) / 1000000 ))  # Convert to milliseconds

if [ $DURATION -lt 10000 ]; then
    echo "✅ PASS (${DURATION}ms)"
    ((TESTS_PASSED++))
else
    echo "❌ FAIL (${DURATION}ms - too slow)"
    ((TESTS_FAILED++))
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Test Summary:"
echo "   ✅ Passed: $TESTS_PASSED"
echo "   ❌ Failed: $TESTS_FAILED"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║          All Tests Passed! ✅                            ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""
    echo "🚀 Ready to use Claude Code with local LLM!"
    echo ""
    echo "   Run: claude"
    echo ""
    exit 0
else
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║          Some Tests Failed ❌                            ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""
    echo "Troubleshooting:"
    echo "   • Start server: ./bin/start-webui.sh"
    echo "   • Check logs: cat /tmp/llama-server.log"
    echo "   • Verify config: cat config.yaml"
    echo ""
    exit 1
fi
