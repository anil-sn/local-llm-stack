#!/usr/bin/env bash
#
# Run pytest test suite for Local LLM Stack CLI
# Comprehensive tests without mocking
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_ROOT/.venv"
TESTS_DIR="$PROJECT_ROOT/tests"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     Local LLM Stack CLI - Pytest Test Suite             ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Activate virtual environment
if [ -d "$VENV_DIR" ]; then
    echo -e "${BLUE}📦 Activating virtual environment...${NC}"
    source "$VENV_DIR/bin/activate"
    echo -e "${GREEN}✅ Activated${NC}"
else
    echo -e "${RED}❌ Virtual environment not found: $VENV_DIR${NC}"
    echo ""
    echo "Run ./prepare.sh first to set up the environment"
    exit 1
fi

echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${YELLOW}⚠️  Installing pytest...${NC}"
    pip install pytest pytest-cov --quiet
    echo -e "${GREEN}✅ Installed${NC}"
    echo ""
fi

# Parse arguments
COVERAGE=false
VERBOSE=false
SPECIFIC_TEST=""
MARKER=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --coverage|-c)
            COVERAGE=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --test)
            SPECIFIC_TEST="$2"
            shift 2
            ;;
        --marker|-m)
            MARKER="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --coverage, -c      Generate coverage report"
            echo "  --verbose, -v       Verbose output"
            echo "  --test, -t          Run specific test file"
            echo "  --marker, -m        Run tests with specific marker"
            echo "  --help, -h          Show this help"
            echo ""
            echo "Examples:"
            echo "  $0                              # Run all tests"
            echo "  $0 -c                           # Run with coverage"
            echo "  $0 -t test_config.py            # Run specific test"
            echo "  $0 -m 'not slow'                # Skip slow tests"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Build pytest command
PYTEST_CMD="pytest"

# Add verbosity
if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -v"
fi

# Add coverage
if [ "$COVERAGE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=src/local_llm --cov-report=term-missing --cov-report=html:htmlcov"
fi

# Add marker
if [ -n "$MARKER" ]; then
    PYTEST_CMD="$PYTEST_CMD -m '$MARKER'"
fi

# Add specific test
if [ -n "$SPECIFIC_TEST" ]; then
    PYTEST_CMD="$PYTEST_CMD $TESTS_DIR/$SPECIFIC_TEST"
else
    PYTEST_CMD="$PYTEST_CMD $TESTS_DIR/"
fi

# Run tests
echo -e "${BLUE}🏃 Running tests...${NC}"
echo ""
echo "Command: $PYTEST_CMD"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd "$PROJECT_ROOT"
eval "$PYTEST_CMD"
EXIT_CODE=$?

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
else
    echo -e "${RED}❌ Some tests failed${NC}"
fi

echo ""

# Show coverage report location
if [ "$COVERAGE" = true ]; then
    echo -e "${BLUE}📊 Coverage report generated:${NC}"
    echo "   HTML: $PROJECT_ROOT/htmlcov/index.html"
    echo ""
fi

exit $EXIT_CODE
