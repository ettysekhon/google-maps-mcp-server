"""Unit tests for Roads API tools."""

import pytest

from google_maps_mcp_server.config import Settings
from google_maps_mcp_server.tools.roads import SnapToRoadsTool, SpeedLimitsTool


@pytest.mark.asyncio
async def test_snap_to_roads_tool_name() -> None:
    """Test snap to roads tool name."""
    settings = Settings(google_maps_api_key="AIzaSyDEMO_KEY_12345678901234567890123")
    tool = SnapToRoadsTool(settings)
    assert tool.name == "snap_to_roads"


@pytest.mark.asyncio
async def test_snap_to_roads_schema() -> None:
    """Test snap to roads tool has valid schema."""
    settings = Settings(google_maps_api_key="AIzaSyDEMO_KEY_12345678901234567890123")
    tool = SnapToRoadsTool(settings)
    schema = tool.input_schema

    assert schema["type"] == "object"
    assert "path" in schema["properties"]
    assert schema["properties"]["path"]["type"] == "array"
    assert schema["properties"]["path"]["minItems"] == 2
    assert schema["properties"]["path"]["maxItems"] == 100


@pytest.mark.asyncio
async def test_speed_limits_tool_name() -> None:
    """Test speed limits tool name."""
    settings = Settings(google_maps_api_key="AIzaSyDEMO_KEY_12345678901234567890123")
    tool = SpeedLimitsTool(settings)
    assert tool.name == "get_speed_limits"


@pytest.mark.asyncio
async def test_speed_limits_schema() -> None:
    """Test speed limits tool has valid schema."""
    settings = Settings(google_maps_api_key="AIzaSyDEMO_KEY_12345678901234567890123")
    tool = SpeedLimitsTool(settings)
    schema = tool.input_schema

    assert schema["type"] == "object"
    assert "place_ids" in schema["properties"]
    assert schema["properties"]["place_ids"]["type"] == "array"
    assert schema["required"] == ["place_ids"]


@pytest.mark.asyncio
async def test_speed_limits_units() -> None:
    """Test speed limits tool schema (units are returned by API, not specified in request)."""
    settings = Settings(google_maps_api_key="AIzaSyDEMO_KEY_12345678901234567890123")
    tool = SpeedLimitsTool(settings)
    schema = tool.input_schema

    # The new API doesn't accept units parameter - units are returned in the response
    assert "place_ids" in schema["properties"]
    assert "units" not in schema["properties"]
