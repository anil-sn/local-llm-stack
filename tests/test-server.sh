#!/usr/bin/env bash
#
# Server Test (Non-destructive)
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS=0
FAIL=0

test_server() {
    local cmd="$1"
    local desc="$2"
    local expected="$3"
    
    echo -n "Testing: $desc... "
    
    OUTPUT=$(eval "$cmd" 2>&1)
    
    if echo "$OUTPUT" | grep -q "$expected"; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((PASS++))
    else
        echo -e "${RED}❌ FAIL${NC}"
        ((FAIL++))
    fi
}

echo "╔══════════════════════════════════════════════════╗"
echo "║     Server Test (Non-destructive)               ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# Activate venv
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Check if server is running
echo "Checking server status..."
echo ""

if curl -s http://localhost:8081/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Server is running${NC}"
    SERVER_RUNNING=true
else
    echo -e "${YELLOW}⚠️  Server is not running${NC}"
    SERVER_RUNNING=false
fi

echo ""

# Test server commands (non-destructive)
test_server "llm-stack server --help" "Server help" "Commands"
test_server "llm-stack server status" "Server status" "Server Status"
test_server "llm-stack server logs --help" "Server logs help" "Options"

# Test API if server is running
if [ "$SERVER_RUNNING" = true ]; then
    echo ""
    echo "Testing API endpoints..."
    
    # Health check
    if curl -s http://localhost:8081/health | grep -q "ok"; then
        echo -e "${GREEN}✅ Health endpoint working${NC}"
        ((PASS++))
    else
        echo -e "${RED}❌ Health endpoint failed${NC}"
        ((FAIL++))
    fi
    
    # Models endpoint
    if curl -s http://localhost:8081/v1/models | grep -q "models"; then
        echo -e "${GREEN}✅ Models endpoint working${NC}"
        ((PASS++))
    else
        echo -e "${RED}❌ Models endpoint failed${NC}"
        ((FAIL++))
    fi
    
    # Quick chat test
    echo ""
    echo "Testing quick chat..."
    RESPONSE=$(llm-stack chat quick 'Say "test"' 2>&1)
    if echo "$RESPONSE" | grep -qi "test"; then
        echo -e "${GREEN}✅ Quick chat working${NC}"
        ((PASS++))
    else
        echo -e "${RED}❌ Quick chat failed${NC}"
        ((FAIL++))
    fi
else
    echo ""
    echo -e "${YELLOW}Skipping API tests (server not running)${NC}"
    echo "To start server: llm-stack server start"
fi

# Test server configuration
echo ""
echo "Testing server configuration..."
test_server "llm-stack config show server" "Server config" "port"

echo ""
echo "══════════════════════════════════════════════════"
echo "Results: ${GREEN}$PASS passed${NC}, ${RED}$FAIL failed${NC}"
echo "══════════════════════════════════════════════════"

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✅ All server tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some server tests failed${NC}"
    exit 1
fi
