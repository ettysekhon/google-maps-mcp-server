"""Unit tests for Directions tool."""

import googlemaps
import pytest

from google_maps_mcp_server.config import Settings
from google_maps_mcp_server.tools.directions import DirectionsTool


@pytest.mark.asyncio
async def test_directions_tool_name() -> None:
    """Test directions tool name."""
    settings = Settings(google_maps_api_key="AIzaSyDEMO_KEY_12345678901234567890123")
    tool = DirectionsTool(settings)
    assert tool.name == "get_directions"


@pytest.mark.asyncio
async def test_directions_tool_description() -> None:
    """Test directions tool has description."""
    settings = Settings(google_maps_api_key="AIzaSyDEMO_KEY_12345678901234567890123")
    tool = DirectionsTool(settings)
    assert tool.description is not None
    assert len(tool.description) > 0


@pytest.mark.asyncio
async def test_directions_tool_schema() -> None:
    """Test directions tool has valid schema."""
    settings = Settings(google_maps_api_key="AIzaSyDEMO_KEY_12345678901234567890123")
    tool = DirectionsTool(settings)
    schema = tool.input_schema

    assert schema["type"] == "object"
    assert "origin" in schema["properties"]
    assert "destination" in schema["properties"]
    assert set(schema["required"]) == {"origin", "destination"}


@pytest.mark.asyncio
async def test_directions_mode_options() -> None:
    """Test directions tool supports all travel modes."""
    settings = Settings(google_maps_api_key="AIzaSyDEMO_KEY_12345678901234567890123")
    tool = DirectionsTool(settings)
    schema = tool.input_schema

    mode_enum = schema["properties"]["mode"]["enum"]
    assert "driving" in mode_enum
    assert "walking" in mode_enum
    assert "bicycling" in mode_enum
    assert "transit" in mode_enum


@pytest.mark.asyncio
async def test_directions_mcp_conversion() -> None:
    """Test directions tool converts to MCP Tool type."""
    settings = Settings(google_maps_api_key="AIzaSyDEMO_KEY_12345678901234567890123")
    tool = DirectionsTool(settings)
    mcp_tool = tool.to_mcp_tool()

    assert mcp_tool.name == "get_directions"
    assert mcp_tool.description is not None
    assert mcp_tool.inputSchema is not None


@pytest.mark.asyncio
async def test_directions_handles_api_error(
    mock_settings: Settings, mock_gmaps_client: googlemaps.Client
) -> None:
    """DirectionsTool correctly handles googlemaps.exceptions.ApiError."""
    tool = DirectionsTool(mock_settings)

    mock_gmaps_client.directions.side_effect = googlemaps.exceptions.ApiError("OVER_QUERY_LIMIT")

    result = await tool.execute(
        {
            "origin": "A",
            "destination": "B",
        }
    )

    assert result["status"] == "error"
    assert "OVER_QUERY_LIMIT" in result.get("error", "")
