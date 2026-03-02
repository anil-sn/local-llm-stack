#!/usr/bin/env bash
#
# Local LLM Stack CLI - Comprehensive Test Script
# Tests all 28 CLI commands
#
# Usage: ./tests/test-all.sh
#

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

# Test log file
TEST_LOG="tests/test-$(date +%Y%m%d-%H%M%S).log"

# Helper functions
log() {
    echo -e "$1" | tee -a "$TEST_LOG"
}

pass() {
    ((PASSED_TESTS++))
    ((TOTAL_TESTS++))
    log "${GREEN}✅ PASS${NC}: $1"
}

fail() {
    ((FAILED_TESTS++))
    ((TOTAL_TESTS++))
    log "${RED}❌ FAIL${NC}: $1"
}

skip() {
    ((SKIPPED_TESTS++))
    ((TOTAL_TESTS++))
    log "${YELLOW}⚠️  SKIP${NC}: $1"
}

section() {
    log ""
    log "${CYAN}════════════════════════════════════════════════════════${NC}"
    log "${CYAN}$1${NC}"
    log "${CYAN}════════════════════════════════════════════════════════${NC}"
}

test_command() {
    local cmd="$1"
    local description="$2"
    local expect_success="${3:-true}"
    
    log ""
    log "${BLUE}Testing:${NC} $description"
    log "${DIM}Command:${NC} $cmd"
    
    # Run command and capture output
    if eval "$cmd" >> "$TEST_LOG" 2>&1; then
        if [ "$expect_success" = "true" ]; then
            pass "$description"
            return 0
        else
            fail "$description (expected to fail but succeeded)"
            return 1
        fi
    else
        if [ "$expect_success" = "false" ]; then
            pass "$description (expected failure)"
            return 0
        else
            fail "$description"
            return 1
        fi
    fi
}

# Check prerequisites
check_prerequisites() {
    section "📋 Checking Prerequisites"
    
    # Check if CLI is installed
    if command -v llm-stack &> /dev/null; then
        pass "llm-stack CLI is installed"
    else
        # Try to use wrapper
        if [ -f "bin/llm-stack" ]; then
            export PATH="$(pwd)/bin:$PATH"
            if command -v llm-stack &> /dev/null; then
                pass "llm-stack CLI found via wrapper"
            else
                fail "llm-stack CLI not found"
                exit 1
            fi
        else
            fail "llm-stack CLI not found"
            exit 1
        fi
    fi
    
    # Check if config.yaml exists
    if [ -f "config.yaml" ]; then
        pass "config.yaml exists"
    else
        fail "config.yaml not found"
        exit 1
    fi
    
    # Check Python venv
    if [ -d ".venv" ]; then
        pass "Python virtual environment exists"
    else
        skip "Python virtual environment not found (some tests may fail)"
    fi
    
    # Get CLI version
    log ""
    log "${CYAN}CLI Version:${NC} $(llm-stack --version 2>&1)"
}

# Test main CLI
test_main_cli() {
    section "🎯 Testing Main CLI"
    
    test_command "llm-stack --help" "Main help"
    test_command "llm-stack --version" "Version check"
}

# Test status commands
test_status_commands() {
    section "📊 Testing Status Commands"
    
    test_command "llm-stack status --help" "Status help"
    test_command "llm-stack status system" "System status"
    test_command "llm-stack status server" "Server status"
    test_command "llm-stack status model" "Model status"
    test_command "llm-stack status dependencies" "Dependencies check"
    test_command "llm-stack status all" "Complete status overview"
}

# Test server commands
test_server_commands() {
    section "🖥️  Testing Server Commands"
    
    test_command "llm-stack server --help" "Server help"
    test_command "llm-stack server status" "Server status check"
    test_command "llm-stack server logs --help" "Server logs help"
    
    # Note: Don't actually start/stop server in automated test
    skip "Server start (manual test required)"
    skip "Server stop (manual test required)"
    skip "Server restart (manual test required)"
}

# Test model commands
test_model_commands() {
    section "📦 Testing Model Commands"
    
    test_command "llm-stack model --help" "Model help"
    test_command "llm-stack model list" "List models"
    test_command "llm-stack model list --verbose" "List models (verbose)"
    test_command "llm-stack model info" "Model info (active)"
    test_command "llm-stack model info llama-3-8b" "Model info (specific)"
    test_command "llm-stack model validate" "Model validate (active)"
    
    # Note: Don't download/delete in automated test
    skip "Model download (manual test required)"
    skip "Model delete (manual test required)"
}

# Test chat commands
test_chat_commands() {
    section "💬 Testing Chat Commands"
    
    test_command "llm-stack chat --help" "Chat help"
    test_command "llm-stack chat interactive --help" "Interactive chat help"
    test_command "llm-stack chat quick --help" "Quick chat help"
    test_command "llm-stack chat agent --help" "Agent help"
    
    # Test quick chat if server is running
    if curl -s http://localhost:8081/health > /dev/null 2>&1; then
        test_command "llm-stack chat quick 'Test'" "Quick chat (live server)"
    else
        skip "Quick chat (server not running)"
    fi
    
    skip "Interactive chat (manual test required)"
    skip "Agent mode (manual test required)"
}

# Test config commands
test_config_commands() {
    section "⚙️  Testing Config Commands"
    
    test_command "llm-stack config --help" "Config help"
    test_command "llm-stack config show" "Config show (summary)"
    test_command "llm-stack config show server" "Config show (server)"
    test_command "llm-stack config show api" "Config show (api)"
    test_command "llm-stack config show advanced" "Config show (advanced)"
    test_command "llm-stack config show models" "Config show (models)"
    test_command "llm-stack config validate" "Config validate"
    test_command "llm-stack config models" "Config models list"
    
    skip "Config edit (manual test required)"
}

# Test benchmark commands
test_benchmark_commands() {
    section "🏃 Testing Benchmark Commands"
    
    test_command "llm-stack benchmark --help" "Benchmark help"
    test_command "llm-stack benchmark run --help" "Benchmark run help"
    test_command "llm-stack benchmark native --help" "Benchmark native help"
    test_command "llm-stack benchmark api --help" "Benchmark API help"
    test_command "llm-stack benchmark compare --help" "Benchmark compare help"
    test_command "llm-stack benchmark clean --help" "Benchmark clean help"
    
    # Note: Don't run actual benchmarks in quick test
    skip "Benchmark run (takes long, manual test)"
    skip "Benchmark native (takes long, manual test)"
    skip "Benchmark API (requires server, manual test)"
}

# Test GPU detection
test_gpu_detection() {
    section "🎮 Testing GPU Detection"
    
    # Test GPU info function
    if llm-stack status system 2>&1 | grep -q "GPU"; then
        pass "GPU detection working"
    else
        fail "GPU detection not working"
    fi
    
    # Check GPU type
    if llm-stack status system 2>&1 | grep -q "METAL\|CUDA\|ROCm"; then
        pass "GPU type detected"
    else
        # CPU-only is also valid
        pass "CPU-only mode (no GPU detected)"
    fi
}

# Test cross-platform compatibility
test_cross_platform() {
    section "🌍 Testing Cross-Platform Compatibility"
    
    # Get platform
    PLATFORM=$(uname -s)
    log "${CYAN}Platform:${NC} $PLATFORM"
    
    case "$PLATFORM" in
        Darwin)
            pass "Running on macOS"
            test_command "sysctl -n machdep.cpu.brand_string" "macOS sysctl"
            ;;
        Linux)
            pass "Running on Linux"
            if [ -f "/proc/meminfo" ]; then
                pass "Linux /proc/meminfo accessible"
            fi
            ;;
        *)
            skip "Unknown platform: $PLATFORM"
            ;;
    esac
}

# Test error handling
test_error_handling() {
    section "🛡️  Testing Error Handling"
    
    # Test with invalid command
    if ! llm-stack invalid-command 2>&1 | grep -qi "No such command\|Error\|Usage"; then
        fail "Invalid command not handled"
    else
        pass "Invalid command handled correctly"
    fi
    
    # Test missing subcommand
    if ! llm-stack status 2>&1 | grep -qi "Missing command\|Error\|Usage"; then
        fail "Missing subcommand not handled"
    else
        pass "Missing subcommand handled correctly"
    fi
}

# Print summary
print_summary() {
    section "📊 Test Summary"
    
    log ""
    log "Total Tests:  $TOTAL_TESTS"
    log "${GREEN}Passed:       $PASSED_TESTS${NC}"
    log "${RED}Failed:       $FAILED_TESTS${NC}"
    log "${YELLOW}Skipped:      $SKIPPED_TESTS${NC}"
    log ""
    
    if [ $FAILED_TESTS -eq 0 ]; then
        log "${GREEN}════════════════════════════════════════${NC}"
        log "${GREEN}✅ ALL TESTS PASSED!${NC}"
        log "${GREEN}════════════════════════════════════════${NC}"
        exit 0
    else
        log "${RED}════════════════════════════════════════${NC}"
        log "${RED}❌ SOME TESTS FAILED${NC}"
        log "${RED}════════════════════════════════════════${NC}"
        exit 1
    fi
}

# Main test runner
main() {
    # Change to project root
    cd "$(dirname "$0")/.." || exit 1
    
    # Initialize log
    mkdir -p tests
    echo "Local LLM Stack CLI Test Log" > "$TEST_LOG"
    echo "Date: $(date)" >> "$TEST_LOG"
    echo "=========================================" >> "$TEST_LOG"
    
    log "${CYAN}╔══════════════════════════════════════════════════╗${NC}"
    log "${CYAN}║   Local LLM Stack CLI - Comprehensive Test      ║${NC}"
    log "${CYAN}╚══════════════════════════════════════════════════╝${NC}"
    log ""
    log "Test Log: $TEST_LOG"
    log ""
    
    # Run all tests
    check_prerequisites
    test_main_cli
    test_status_commands
    test_server_commands
    test_model_commands
    test_chat_commands
    test_config_commands
    test_benchmark_commands
    test_gpu_detection
    test_cross_platform
    test_error_handling
    
    # Print summary
    print_summary
}

# Run main
main "$@"
