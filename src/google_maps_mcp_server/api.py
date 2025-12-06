"""
Google Maps MCP Server - HTTP/SSE API

This module provides an HTTP server with SSE transport for the MCP server,
following the standard MCP SSE implementation pattern.

Usage:
    uvicorn google_maps_mcp_server.api:app --host 0.0.0.0 --port 8080

Or via the module:
    python -m google_maps_mcp_server.api
"""

import logging
import os

import uvicorn
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route
from starlette.types import ASGIApp, Receive, Scope, Send

from .config import Settings
from .server import GoogleMapsMCPServer

# Only configure logging if not in test mode
if not os.environ.get("PYTEST_CURRENT_TEST"):
    logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app() -> ASGIApp:
    """
    Create and configure the Starlette ASGI application.

    This follows the standard MCP SSE server pattern:
    - /sse endpoint for SSE connections (GET)
    - /messages endpoint for client messages (POST)
    - /health endpoint for health checks (GET)
    """
    settings = Settings()
    mcp_server = GoogleMapsMCPServer(settings)
    sse = SseServerTransport("/messages")

    logger.info(
        f"MCP Server initialised with {len(mcp_server.tools)} tools, version {settings.version}"
    )

    async def handle_sse(request: Request) -> None:
        """Handle SSE connection requests."""
        logger.info(f"SSE connection request from {request.client}")
        async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
            await mcp_server.app.run(
                streams[0],
                streams[1],
                mcp_server.app.create_initialization_options(),
            )

    async def handle_messages(request: Request) -> None:
        """Handle POST messages from MCP clients."""
        await sse.handle_post_message(request.scope, request.receive, request._send)

    async def health_check(request: Request) -> Response:
        """Health check endpoint for load balancers and monitoring."""
        return JSONResponse(
            {"status": "healthy", "version": settings.version, "service": "google-maps-mcp-server"}
        )

    routes = [
        Route("/health", endpoint=health_check),
    ]

    app = Starlette(
        debug=settings.log_level.upper() == "DEBUG",
        routes=routes,
    )

    inner_app = app

    async def sse_middleware(scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            path = scope.get("path", "")
            if path == "/sse":
                logger.info(f"SSE connection from {scope.get('client')}")
                async with sse.connect_sse(scope, receive, send) as streams:
                    await mcp_server.app.run(
                        streams[0],
                        streams[1],
                        mcp_server.app.create_initialization_options(),
                    )
                return
            elif path == "/messages" and scope.get("method") == "POST":
                await sse.handle_post_message(scope, receive, send)
                return
        await inner_app(scope, receive, send)

    return sse_middleware


app = create_app()


def main() -> None:
    """Run the server using uvicorn."""
    uvicorn.run(
        "google_maps_mcp_server.api:app",
        host="0.0.0.0",
        port=8080,
        log_level="info",
    )


if __name__ == "__main__":
    main()
