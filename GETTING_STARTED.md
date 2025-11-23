# Getting Started with Google Maps MCP Server

This guide will walk you through setting up, running, and testing the Google Maps MCP Server.

## Prerequisites

- **Python 3.10+** (3.14 recommended)
- **Git**
- **Google Maps API Key** ([Get one here](https://console.cloud.google.com/apis/credentials))
- **uv** (will be installed automatically if missing)

## Step-by-Step Setup

### 1. Clone the Repository

```bash
# Clone from GitHub
git clone https://github.com/ettysekhon/google-maps-mcp-server.git
cd google-maps-mcp-server
```

### 2. Run Setup Script

```bash
# Make scripts executable
chmod +x scripts/setup_dev.sh scripts/run_tests.sh

# Run development setup
./scripts/setup_dev.sh
```

This script will:

- ✅ Check Python version
- ✅ Install uv (if needed)
- ✅ Install all dependencies
- ✅ Set up pre-commit hooks
- ✅ Create .env file
- ✅ Run initial code quality checks
- ✅ Run unit tests

### 3. Configure API Key

Edit the `.env` file and add your Google Maps API key:

```bash
# Open .env in your editor
nano .env  # or vim, code, etc.
```

Replace `your_api_key_here` with your actual API key:

```env
GOOGLE_MAPS_API_KEY=AIzaSyC...your_actual_key_here
```

**Get your API key:**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable these APIs:
   - Places API
   - Directions API
   - Geocoding API
   - Distance Matrix API
   - Roads API
4. Go to "Credentials" → "Create Credentials" → "API Key"
5. Copy your API key

### 4. Run Tests

```bash
# Run unit tests only (no API calls)
./scripts/run_tests.sh

# Run all tests including integration tests (makes real API calls)
./scripts/run_tests.sh --integration

# Run with verbose output
./scripts/run_tests.sh --verbose

# Run and stop on first failure
./scripts/run_tests.sh --fail-fast
```

### 5. Test the Server

#### Option A: Run the Server Directly

```bash
# Start the MCP server
uv run google-maps-mcp-server
```

The server will start and wait for MCP protocol messages on stdin/stdout.

#### Option B: Run Examples

```bash
# Test with simple example (all tools)
python examples/simple_query.py

# Test fleet routing optimization
python examples/flask_routing.py

# Test GPS trace analysis
python examples/gps_trace_analyzer.py

# Test MCP client connection
python examples/mcp_client_test.py
```

#### Option C: Test with Claude Desktop

1. Find your Claude Desktop config file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

2. Add the MCP server configuration:

    ```json
    {
    "mcpServers": {
        "google-maps": {
        "command": "uv",
        "args": [
            "--directory",
            "/full/path/to/google-maps-mcp-server",
            "run",
            "google-maps-mcp-server"
        ],
        "env": {
            "GOOGLE_MAPS_API_KEY": "your_api_key_here"
        }
        }
    }
    }
    ```

3. Restart Claude Desktop

4. Test with queries like:
   - "Find coffee shops near Times Square"
   - "Get directions from San Francisco to Los Angeles"
   - "What are the coordinates for the Eiffel Tower?"

## Development Workflow

### Making Changes

```bash
# Create a feature branch
git checkout -b feature/your-feature

# Make your changes
# ... edit files ...

# Format code
uv run black src tests examples

# Lint code
uv run ruff check src tests examples --fix

# Type check
uv run mypy src

# Run tests
./scripts/run_tests.sh

# Commit changes
git add .
git commit -m "feat: your feature description"
```

### Using Make Commands (Optional)

If you created the Makefile:

```bash
make help              # Show all commands
make setup             # Setup dev environment
make test              # Run unit tests
make test-integration  # Run all tests
make format            # Format code
make lint              # Lint code
make type-check        # Type check
make clean             # Clean generated files
make run               # Run server
make example           # Run simple example
```

## Common Commands Reference

```bash
# Install/Update Dependencies
uv sync                          # Install dependencies
uv sync --extra dev              # Install with dev dependencies
uv add package_name              # Add new dependency

# Code Quality
uv run black src tests           # Format code
uv run ruff check src            # Lint code
uv run ruff check src --fix      # Auto-fix linting issues
uv run mypy src                  # Type check

# Testing
uv run pytest                    # Run all tests
uv run pytest tests/unit         # Run unit tests only
uv run pytest tests/integration  # Run integration tests only
uv run pytest -v                 # Verbose output
uv run pytest -x                 # Stop on first failure
uv run pytest -k test_name       # Run specific test
uv run pytest --cov              # Run with coverage

# Running
uv run google-maps-mcp-server    # Run server
python examples/simple_query.py  # Run example
python -m google_maps_mcp_server # Run as module

# Building
uv build                         # Build package
uv publish                       # Publish to PyPI
```

## Troubleshooting

### Problem: `uv: command not found`

**Solution:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
```

### Problem: `GOOGLE_MAPS_API_KEY not set`

**Solution:**

```bash
# Make sure .env file exists
cp .env.example .env

# Edit and add your API key
nano .env
```

### Problem: `REQUEST_DENIED` from Google Maps API

**Solution:**

1. Enable required APIs in Google Cloud Console
2. Check API key restrictions
3. Verify billing is enabled

### Problem: Import errors

**Solution:**

```bash
# Reinstall dependencies
uv sync --extra dev

# Or reinstall the package
uv pip install -e .
```

### Problem: Tests failing

**Solution:**

```bash
# Check if API key is set
cat .env | grep GOOGLE_MAPS_API_KEY

# Run only unit tests (no API calls)
./scripts/run_tests.sh

# Clean and reinstall
make clean
uv sync --extra dev
```

### Problem: Permission denied on scripts

**Solution:**

```bash
chmod +x scripts/setup_dev.sh
chmod +x scripts/run_tests.sh
```

## Next Steps

1. **Read the Documentation**
   - [API Reference](docs/API.md)
   - [Contributing Guide](CONTRIBUTING.md)

2. **Try the Examples**
   - `examples/simple_query.py` - Basic usage
   - `examples/flask_routing.py` - Fleet optimization
   - `examples/gps_trace_analyzer.py` - GPS analysis

3. **Build Something**
   - Create your own examples
   - Integrate with your application
   - Contribute improvements

4. **Get Help**
   - [GitHub Issues](https://github.com/ettysekhon/google-maps-mcp-server/issues)
   - [Discussions](https://github.com/ettysekhon/google-maps-mcp-server/discussions)

## Quick Start Checklist

- [ ] Python 3.10+ installed
- [ ] Repository cloned
- [ ] Ran `./scripts/setup_dev.sh`
- [ ] Added API key to `.env`
- [ ] Ran `./scripts/run_tests.sh` successfully
- [ ] Tested with `python examples/simple_query.py`
- [ ] (Optional) Configured Claude Desktop
