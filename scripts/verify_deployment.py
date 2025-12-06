#!/usr/bin/env python3
"""
Verification script for Google Maps MCP Server deployment.

Tests:
1. Health check endpoint
2. SSE endpoint accessibility
3. Full MCP client connection and tool listing

Usage:
    python scripts/verify_deployment.py [URL]

    URL defaults to http://localhost:8080/sse
"""

import asyncio
import sys

import httpx
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client


async def test_mcp_server(base_url: str) -> bool:
    """Test the MCP server deployment."""
    # Normalise the URL
    if base_url.endswith("/sse"):
        sse_url = base_url
        base_url = base_url.rsplit("/sse", 1)[0]
    else:
        base_url = base_url.rstrip("/")
        sse_url = f"{base_url}/sse"

    health_url = f"{base_url}/health"

    print("Testing MCP Server")
    print(f"  Base URL: {base_url}")
    print(f"  SSE URL:  {sse_url}")
    print(f"  Health:   {health_url}")
    print()

    # 1. Health Check
    print("Step 1: Health Check")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(health_url)
            if resp.status_code == 200:
                data = resp.json()
                print("  [PASS] Health Check Passed")
                print(f"     Status:  {data.get('status', 'unknown')}")
                print(f"     Version: {data.get('version', 'unknown')}")
            else:
                print(f"  [FAIL] Health Check Failed: HTTP {resp.status_code}")
                print(f"     Response: {resp.text[:200]}")
                return False
    except Exception as e:
        print(f"  [FAIL] Health Check Failed: {type(e).__name__}: {e}")
        return False

    print()

    # 2. SSE Endpoint Accessibility
    print("Step 2: SSE Endpoint Accessibility")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Use stream to test SSE endpoint
            async with client.stream("GET", sse_url) as response:
                if response.status_code == 200:
                    # Check content type
                    content_type = response.headers.get("content-type", "")
                    if "text/event-stream" in content_type:
                        print("  [PASS] SSE Endpoint Accessible")
                        print(f"     Content-Type: {content_type}")
                    else:
                        print("  [WARN] SSE Endpoint returned unexpected content type")
                        print(f"     Content-Type: {content_type}")
                        # Still continue as it might work
                else:
                    print(f"  [FAIL] SSE Endpoint returned HTTP {response.status_code}")
                    return False
    except httpx.ReadTimeout:
        # This is actually expected for SSE - the connection stays open
        print("  [WARN] SSE connection timed out (this may be normal for SSE)")
    except Exception as e:
        print(f"  [FAIL] SSE Endpoint Failed: {type(e).__name__}: {e}")
        return False

    print()

    # 3. Full MCP Client Test
    print("Step 3: MCP Client Connection & Tool Listing")
    try:
        async with sse_client(sse_url) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                print("  Initialising MCP session...")
                await session.initialize()

                print("  Listing available tools...")
                tools_result = await session.list_tools()
                tools = tools_result.tools

                print(f"  [PASS] Connected! Found {len(tools)} tools:")

                # List all tools
                for tool in tools:
                    print(f"     - {tool.name}")

                # Check for expected tools
                expected_tools = [
                    "search_places",
                    "get_directions",
                    "geocode_address",
                    "reverse_geocode",
                ]
                found_tools = {t.name for t in tools}

                print()
                print("  Expected tools check:")
                all_found = True
                for tool_name in expected_tools:
                    if tool_name in found_tools:
                        print(f"     [PASS] {tool_name}")
                    else:
                        print(f"     [FAIL] {tool_name} (missing)")
                        all_found = False

                if not all_found:
                    print()
                    print("  [WARN] Some expected tools are missing")

    except Exception as e:
        print(f"  [FAIL] MCP Client Connection Failed: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        return False

    print()
    print("=" * 50)
    print("[PASS] Verification Complete - Server is working!")
    print("=" * 50)
    return True


def main() -> None:
    """Main entry point."""
    # Default to localhost
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080/sse"

    print("=" * 50)
    print("Google Maps MCP Server - Deployment Verification")
    print("=" * 50)
    print()

    success = asyncio.run(test_mcp_server(url))
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
