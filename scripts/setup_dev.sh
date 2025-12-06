#!/bin/bash

set -e

echo "======================================"
echo "Google Maps MCP Server - Dev Setup"
echo "======================================"
echo ""

echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.10 or higher required. Found: $python_version"
    exit 1
fi
echo "✓ Python $python_version"
echo ""

echo "Checking for uv package manager..."
if ! command -v uv &> /dev/null; then
    echo "uv not found. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
    echo "✓ uv installed"
else
    echo "✓ uv found: $(uv --version)"
fi
echo ""

echo "Installing dependencies..."
uv sync --extra dev --extra docs
echo "✓ Dependencies installed"
echo ""

echo "Setting up pre-commit hooks..."
uv run pre-commit install
echo "✓ Pre-commit hooks installed"
echo ""

if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your GOOGLE_MAPS_API_KEY"
    echo ""
else
    echo "✓ .env file already exists"
    echo ""
fi

if grep -q "your_api_key_here" .env 2>/dev/null || ! grep -q "GOOGLE_MAPS_API_KEY" .env 2>/dev/null; then
    echo "⚠️  WARNING: GOOGLE_MAPS_API_KEY not configured in .env"
    echo "   Get your API key from: https://console.cloud.google.com/apis/credentials"
    echo ""
fi

echo "Running initial code quality checks..."
echo ""

echo "Formatting code with black..."
uv run black src tests examples || echo "⚠️  Black formatting had issues"
echo ""

echo "Checking with ruff..."
uv run ruff check src tests examples --fix || echo "⚠️  Ruff found some issues"
echo ""

echo "Type checking with mypy..."
uv run mypy src || echo "⚠️  Type checking found some issues"
echo ""

echo "Running unit tests..."
if uv run pytest -m "not integration" --tb=short; then
    echo "✓ All unit tests passed"
else
    echo "⚠️  Some unit tests failed"
fi
echo ""

echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your GOOGLE_MAPS_API_KEY"
echo "2. Run tests: ./scripts/run_tests.sh"
echo "3. Start the server: uv run google-maps-mcp-server"
echo "4. Run examples: python examples/simple_query.py"
echo ""
echo "Useful commands:"
echo "  uv run pytest              # Run all tests"
echo "  uv run black src tests     # Format code"
echo "  uv run ruff check src      # Lint code"
echo "  uv run mypy src            # Type check"
echo ""
