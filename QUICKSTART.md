# Quick Reference - Google Maps MCP Server

## First Time Setup

./scripts/setup_dev.sh

Edit .env and add GOOGLE_MAPS_API_KEY

## Development

./scripts/run_tests.sh              # Test your changes
uv run black src tests              # Format code
uv run ruff check src --fix         # Lint and fix
python examples/simple_query.py     # Test functionality

## Running the Server

uv run google-maps-mcp-server       # Start server

## Testing Integration

./scripts/run_tests.sh --integration --verbose

## Building for Release

uv build
