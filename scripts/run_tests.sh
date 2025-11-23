#!/bin/bash

set -e

echo "======================================"
echo "Google Maps MCP Server - Test Suite"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists and has API key
if [ ! -f .env ]; then
    echo -e "${RED}❌ Error: .env file not found${NC}"
    echo "Run: cp .env.example .env"
    echo "Then edit .env and add your GOOGLE_MAPS_API_KEY"
    exit 1
fi

if ! grep -q "GOOGLE_MAPS_API_KEY" .env || grep -q "your_api_key_here" .env; then
    echo -e "${YELLOW}⚠️  Warning: GOOGLE_MAPS_API_KEY not properly configured${NC}"
    echo "Integration tests will be skipped"
    echo ""
fi

# Parse command line arguments
RUN_INTEGRATION=false
VERBOSE=false
COVERAGE=true
FAIL_FAST=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --integration)
            RUN_INTEGRATION=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --no-cov)
            COVERAGE=false
            shift
            ;;
        --fail-fast|-x)
            FAIL_FAST=true
            shift
            ;;
        --help|-h)
            echo "Usage: ./scripts/run_tests.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --integration     Run integration tests (requires API key)"
            echo "  --verbose, -v     Verbose output"
            echo "  --no-cov          Skip coverage reporting"
            echo "  --fail-fast, -x   Stop on first failure"
            echo "  --help, -h        Show this help message"
            echo ""
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Build pytest command
PYTEST_CMD="uv run pytest"

if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -v"
fi

if [ "$FAIL_FAST" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -x"
fi

if [ "$COVERAGE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=src/google_maps_mcp_server --cov-report=term-missing --cov-report=html --cov-report=xml"
fi

# Add markers based on integration flag
if [ "$RUN_INTEGRATION" = false ]; then
    PYTEST_CMD="$PYTEST_CMD -m 'not integration'"
    echo "Running unit tests only (use --integration to run all tests)"
else
    echo "Running all tests (including integration tests)"
fi

echo ""
echo "Step 1: Code Formatting Check"
echo "------------------------------"
if uv run black --check src tests examples; then
    echo -e "${GREEN}✓ Code formatting check passed${NC}"
else
    echo -e "${RED}✗ Code formatting issues found${NC}"
    echo "Run: uv run black src tests examples"
    exit 1
fi
echo ""

echo "Step 2: Linting"
echo "---------------"
if uv run ruff check src tests examples; then
    echo -e "${GREEN}✓ Linting passed${NC}"
else
    echo -e "${RED}✗ Linting issues found${NC}"
    echo "Run: uv run ruff check src tests examples --fix"
    exit 1
fi
echo ""

echo "Step 3: Type Checking"
echo "---------------------"
if uv run mypy src; then
    echo -e "${GREEN}✓ Type checking passed${NC}"
else
    echo -e "${YELLOW}⚠️  Type checking found issues${NC}"
    # Don't fail on type errors, just warn
fi
echo ""

echo "Step 4: Running Tests"
echo "---------------------"
echo "Command: $PYTEST_CMD"
echo ""

if eval $PYTEST_CMD; then
    echo ""
    echo -e "${GREEN}======================================"
    echo "✓ All Tests Passed!"
    echo "======================================${NC}"

    if [ "$COVERAGE" = true ]; then
        echo ""
        echo "Coverage report generated:"
        echo "  HTML: htmlcov/index.html"
        echo "  XML:  coverage.xml"
        echo ""
        echo "Open HTML report: open htmlcov/index.html (macOS) or xdg-open htmlcov/index.html (Linux)"
    fi

    echo ""
    exit 0
else
    echo ""
    echo -e "${RED}======================================"
    echo "✗ Tests Failed"
    echo "======================================${NC}"
    echo ""
    exit 1
fi
