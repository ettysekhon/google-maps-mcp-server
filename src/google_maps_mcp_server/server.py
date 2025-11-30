"""
Google Maps MCP Server - Production-grade implementation
"""

import asyncio
import logging
import sys
from collections.abc import Sequence
from typing import Any

import mcp.server.stdio
import structlog
from mcp import types as mcp_types
from mcp.server.lowlevel import Server

from .config import Settings
from .tools import (
    DirectionsTool,
    DistanceMatrixTool,
    ElevationTool,
    GeocodingTool,
    PlaceDetailsTool,
    PlacesTool,
    ReverseGeocodingTool,
    RouteSafetyTool,
    SnapToRoadsTool,
    SpeedLimitsTool,
    TrafficConditionsTool,
)

logger = structlog.get_logger()


class GoogleMapsMCPServer:
    """
    Production-ready MCP server for Google Maps Platform APIs.

    Supports:
    - Places API (nearby search, text search, place details)
    - Directions API (routing with traffic, alternatives)
    - Geocoding API (address to coordinates)
    - Distance Matrix API (multi-origin/destination distances)
    - Roads API (snap to roads, speed limits)
    - Elevation API (route elevation profiles)
    """

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings()
        self.app = Server("google-maps-mcp-server")

        # Initialize tools
        self.tools = [
            PlacesTool(self.settings),
            PlaceDetailsTool(self.settings),
            DirectionsTool(self.settings),
            GeocodingTool(self.settings),
            ReverseGeocodingTool(self.settings),
            DistanceMatrixTool(self.settings),
            SnapToRoadsTool(self.settings),
            SpeedLimitsTool(self.settings),
            TrafficConditionsTool(self.settings),
            RouteSafetyTool(self.settings),
            ElevationTool(self.settings),
        ]

        self._register_handlers()
        logger.info(
            "server_initialized",
            num_tools=len(self.tools),
            version=self.settings.version,
        )

    def _register_handlers(self) -> None:
        """Register MCP protocol handlers."""

        @self.app.list_tools()
        async def list_tools() -> list[mcp_types.Tool]:
            """List all available Google Maps tools."""
            return [tool.to_mcp_tool() for tool in self.tools]

        @self.app.call_tool()
        async def call_tool(
            name: str,
            arguments: dict[str, Any],
        ) -> Sequence[mcp_types.TextContent | mcp_types.ImageContent]:
            """Execute the requested tool."""
            logger.info("tool_called", tool_name=name, arguments=arguments)

            tool = next((t for t in self.tools if t.name == name), None)
            if not tool:
                error_msg = f"Unknown tool: {name}"
                logger.error("tool_not_found", tool_name=name)
                return [mcp_types.TextContent(type="text", text=error_msg)]

            try:
                result = await tool.execute(arguments)
                logger.info("tool_executed", tool_name=name, success=True)

                # Convert result to JSON string
                import json

                result_str = json.dumps(result, indent=2, ensure_ascii=False)

                return [mcp_types.TextContent(type="text", text=result_str)]

            except Exception as e:
                logger.exception("tool_execution_failed", tool_name=name, error=str(e))
                error_result = {
                    "status": "error",
                    "tool": name,
                    "error": str(e),
                }
                import json

                return [mcp_types.TextContent(type="text", text=json.dumps(error_result, indent=2))]

    async def run(self) -> None:
        """Run the MCP server with stdio transport."""
        logger.info("server_starting")

        try:
            async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                await self.app.run(
                    read_stream,
                    write_stream,
                    self.app.create_initialization_options(),
                )
        except Exception as e:
            logger.exception("server_error", error=str(e))
            raise
        finally:
            logger.info("server_stopped")


def configure_logging(log_level: str = "INFO") -> None:
    """Configure structured logging."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            (
                structlog.dev.ConsoleRenderer()
                if sys.stderr.isatty()
                else structlog.processors.JSONRenderer()
            ),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, log_level.upper())),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
        cache_logger_on_first_use=True,
    )


def main() -> None:
    """Entry point for the Google Maps MCP server."""
    try:
        settings = Settings()
        configure_logging(settings.log_level)

        logger.info(
            "starting_google_maps_mcp_server",
            version=settings.version,
            log_level=settings.log_level,
        )

        server = GoogleMapsMCPServer(settings)
        asyncio.run(server.run())

    except KeyboardInterrupt:
        logger.info("server_stopped", reason="keyboard_interrupt")
        sys.exit(0)
    except Exception as e:
        logger.exception("server_failed", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
