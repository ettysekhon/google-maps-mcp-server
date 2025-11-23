# Google Maps MCP Server - Examples

This directory contains example scripts demonstrating various use cases for the Google Maps MCP Server.

## Examples Overview

| Script | Description | Complexity |
|--------|-------------|------------|
| `simple_query.py` | Basic usage of all tools | Beginner |
| `flask_routing.py` | Fleet route optimization | Intermediate |
| `adk_agent.py` | Integration with Google ADK | Intermediate |
| `gps_trace_analyzer.py` | GPS trace analysis for safety | Advanced |
| `mcp_client_test.py` | MCP protocol testing | Beginner |

## Setup

    1. Install the package:

    ```bash
    uv pip install google-maps-mcp-server
    ```

    2. Set your API key:

    ```bash
    export GOOGLE_MAPS_API_KEY="your_key_here"
    ```

    3. Run an example:

    ```bash
    python examples/simple_query.py
    ```

## Example Descriptions

### simple_query.py

Demonstrates basic usage of each tool:

- Search for nearby places
- Get directions with traffic
- Geocode addresses
- Reverse geocode coordinates
- Calculate distance matrices
- Snap GPS points to roads
- Get speed limits

**Run:**

    ```bash
    python examples/simple_query.py
    ```

### flask_routing.py

Fleet delivery route optimization:

- Multi-vehicle route planning
- Distance matrix calculation
- Nearest neighbor optimization
- Turn-by-turn directions

**Run:**

    ```bash
    python examples/flask_routing.py
    ```

### adk_agent.py

Google ADK integration example:

- Create intelligent location agent
- Natural language queries
- Multi-tool orchestration
- Interactive mode

**Requirements:**

    ```bash
    pip install google-adk
    ```

**Run:**

    ```bash
    python examples/adk_agent.py
    ```

### gps_trace_analyzer.py

Fleet safety monitoring:

- GPS trace cleaning
- Speed limit detection
- Violation identification
- Safety report generation

**Run:**

    ```bash
    python examples/gps_trace_analyzer.py
    ```

### mcp_client_test.py

MCP protocol testing:

- Server connection test
- Tool discovery
- Tool execution test
- Error handling verification

**Run:**

    ```bash
    python examples/mcp_client_test.py
    ```

## Customization

Each example can be customized by:

1. Modifying the input data
2. Changing API parameters
3. Adjusting output formatting
4. Adding additional logic

## Common Issues

**Import Error:**

    ```python
    ModuleNotFoundError: No module named 'google_maps_mcp_server'
    ```

Solution: Install the package with `uv pip install google-maps-mcp-server`

**API Key Error:**

    ```bash
    ValidationError: google_maps_api_key cannot be empty
    ```

Solution: Set `GOOGLE_MAPS_API_KEY` environment variable

**Rate Limit Error:**

    ```python
    OVER_QUERY_LIMIT
    ```

Solution: Check your API quota in Google Cloud Console

## Further Reading

- [API Documentation](../docs/API.md)
- [Google Maps Platform Docs](https://developers.google.com/maps)
- [MCP Protocol Spec](https://modelcontextprotocol.io)
