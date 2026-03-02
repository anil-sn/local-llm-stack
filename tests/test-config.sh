#!/usr/bin/env bash
#
# Configuration Test
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS=0
FAIL=0

test_config() {
    local cmd="$1"
    local desc="$2"
    local expected="$3"
    
    echo -n "Testing: $desc... "
    
    OUTPUT=$(eval "$cmd" 2>&1)
    
    if echo "$OUTPUT" | grep -q "$expected"; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((PASS++))
    else
        echo -e "${RED}❌ FAIL${NC} (expected: $expected)"
        ((FAIL++))
    fi
}

echo "╔══════════════════════════════════════════════════╗"
echo "║     Configuration Test                           ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# Activate venv
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Test config loading
echo "Testing configuration loading..."
echo ""

test_config "llm-stack config show" "Config summary" "Configuration Summary"
test_config "llm-stack config show server" "Server section" "port"
test_config "llm-stack config show api" "API section" "base_url"
test_config "llm-stack config show advanced" "Advanced section" "temperature"
test_config "llm-stack config validate" "Config validation" "Configuration is valid"
test_config "llm-stack config models" "Model list" "Configured Models"

# Test specific values
echo ""
echo "Testing configuration values..."

# Check port
PORT=$(llm-stack config show server 2>&1 | grep "port" | awk '{print $2}')
if [ "$PORT" = "8081" ]; then
    echo -e "${GREEN}✅ Port: $PORT${NC}"
    ((PASS++))
else
    echo -e "${RED}❌ Port: $PORT (expected 8081)${NC}"
    ((FAIL++))
fi

# Check active model
MODEL=$(llm-stack config show 2>&1 | grep "active_model" | awk '{print $2}')
if [ -n "$MODEL" ]; then
    echo -e "${GREEN}✅ Active model: $MODEL${NC}"
    ((PASS++))
else
    echo -e "${RED}❌ Active model not found${NC}"
    ((FAIL++))
fi

# Test model info
echo ""
echo "Testing model information..."
test_config "llm-stack model info" "Active model info" "Model:"
test_config "llm-stack model list" "Model list" "Available Models"

# Test path resolution
echo ""
echo "Testing path resolution..."
MODEL_PATH=$(llm-stack config show 2>&1 | grep "model_path" | awk '{print $2}')
if [ -n "$MODEL_PATH" ]; then
    echo -e "${GREEN}✅ Model path resolved: $MODEL_PATH${NC}"
    ((PASS++))
else
    echo -e "${RED}❌ Model path not resolved${NC}"
    ((FAIL++))
fi

echo ""
echo "══════════════════════════════════════════════════"
echo "Results: ${GREEN}$PASS passed${NC}, ${RED}$FAIL failed${NC}"
echo "══════════════════════════════════════════════════"

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✅ All configuration tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some configuration tests failed${NC}"
    exit 1
fi
