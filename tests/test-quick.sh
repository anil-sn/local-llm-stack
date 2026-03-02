#!/usr/bin/env bash
#
# Quick Test - Tests core CLI functionality (2 minutes)
#

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS=0
FAIL=0

test_cmd() {
    local cmd="$1"
    local desc="$2"
    
    echo -n "Testing: $desc... "
    
    if eval "$cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((PASS++))
    else
        echo -e "${RED}❌ FAIL${NC}"
        ((FAIL++))
    fi
}

echo "╔══════════════════════════════════════════════════╗"
echo "║     Local LLM Stack CLI - Quick Test            ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# Activate venv if exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Main CLI
test_cmd "llm-stack --help" "Main help"
test_cmd "llm-stack --version" "Version"

# Status
test_cmd "llm-stack status system" "Status system"
test_cmd "llm-stack status server" "Status server"
test_cmd "llm-stack status model" "Status model"
test_cmd "llm-stack status dependencies" "Status dependencies"

# Config
test_cmd "llm-stack config show" "Config show"
test_cmd "llm-stack config validate" "Config validate"
test_cmd "llm-stack config models" "Config models"

# Model
test_cmd "llm-stack model list" "Model list"
test_cmd "llm-stack model info" "Model info"

# Server
test_cmd "llm-stack server --help" "Server help"
test_cmd "llm-stack server status" "Server status"

# Chat
test_cmd "llm-stack chat --help" "Chat help"
test_cmd "llm-stack chat quick --help" "Chat quick help"

# Benchmark
test_cmd "llm-stack benchmark --help" "Benchmark help"

echo ""
echo "══════════════════════════════════════════════════"
echo "Results: ${GREEN}$PASS passed${NC}, ${RED}$FAIL failed${NC}"
echo "══════════════════════════════════════════════════"

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✅ All quick tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi
