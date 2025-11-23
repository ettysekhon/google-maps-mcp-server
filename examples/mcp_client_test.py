"""
Test MCP client connection to Google Maps MCP Server.

This example demonstrates how to connect to the MCP server
and test all available tools.
"""

import asyncio
import json
import os

from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


async def test_mcp_server() -> None:
    """Test connection to Google Maps MCP Server."""
    load_dotenv()

    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        print("Error: GOOGLE_MAPS_API_KEY not set")
        return

    print("Connecting to Google Maps MCP Server...")
    print()

    # Connect to server
    server_params = StdioServerParameters(
        command="google-maps-mcp-server", env={"GOOGLE_MAPS_API_KEY": api_key}
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize session
            await session.initialize()

            print("✓ Connected to MCP server")
            print()

            # List available tools
            print("Available Tools:")
            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"  • {tool.name}: {tool.description}")
            print()

            # Test each tool
            test_cases = [
                {
                    "name": "search_places",
                    "args": {"location": "40.7580,-73.9855", "keyword": "pizza", "radius": 500},
                },
                {
                    "name": "get_directions",
                    "args": {
                        "origin": "New York, NY",
                        "destination": "Boston, MA",
                        "mode": "driving",
                    },
                },
                {
                    "name": "geocode_address",
                    "args": {"address": "1600 Amphitheatre Parkway, Mountain View, CA"},
                },
                {"name": "reverse_geocode", "args": {"lat": 40.7128, "lng": -74.0060}},
            ]

            print("Running Tool Tests:")
            print("=" * 80)
            print()

            for test in test_cases:
                print(f"Testing: {test['name']}")
                print(f"Arguments: {json.dumps(test['args'], indent=2)}")

                try:
                    result = await session.call_tool(test["name"], test["args"])
                    print("✓ Success")
                    print(f"Response preview: {str(result)[:200]}...")
                except Exception as e:
                    print(f"✗ Error: {e}")

                print()
                print("-" * 80)
                print()

            print("All tests completed!")


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
