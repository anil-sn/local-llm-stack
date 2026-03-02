#!/usr/bin/env bash
#
# Test API Endpoints
#
# DEPRECATED: Use 'llm-stack status server' and curl commands instead
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Load configuration
source "$SCRIPT_DIR/../scripts/config.sh"

PORT="${1:-$SERVER_PORT}"
BASE_URL="http://localhost:$PORT"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     Testing LLM API Endpoints                            ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "Base URL: $BASE_URL"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test health endpoint
echo "📊 Testing /health..."
if command -v curl &> /dev/null; then
    response=$(curl -s -w "\n%{http_code}" "$BASE_URL/health")
    body=$(echo "$response" | head -n -1)
    code=$(echo "$response" | tail -n 1)
    
    if [ "$code" = "200" ]; then
        echo "✅ Health check passed (HTTP $code)"
        echo "   Response: $body"
    else
        echo "❌ Health check failed (HTTP $code)"
    fi
else
    echo "⚠️  curl not found, skipping..."
fi

echo ""

# Test models endpoint
echo "📊 Testing /v1/models..."
if command -v curl &> /dev/null; then
    response=$(curl -s -w "\n%{http_code}" "$BASE_URL/v1/models")
    body=$(echo "$response" | head -n -1)
    code=$(echo "$response" | tail -n 1)
    
    if [ "$code" = "200" ]; then
        echo "✅ Models endpoint passed (HTTP $code)"
        if command -v jq &> /dev/null; then
            echo "$body" | jq '.'
        else
            echo "   Response: $body"
        fi
    else
        echo "❌ Models endpoint failed (HTTP $code)"
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "For complete API testing, use:"
echo "  curl $BASE_URL/v1/chat/completions ..."
echo ""
