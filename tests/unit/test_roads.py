"""Unit tests for Roads API tools."""

import googlemaps
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


@pytest.mark.asyncio
async def test_speed_limits_execution_does_not_send_units(
    mock_settings: Settings, mock_gmaps_client: googlemaps.Client
) -> None:
    """SpeedLimitsTool execution no longer includes the 'units' parameter."""
    tool = SpeedLimitsTool(mock_settings)

    # Mock response
    mock_gmaps_client.speed_limits.return_value = {
        "speedLimits": [
            {"placeId": "p1", "speedLimit": 65, "units": "KPH"},
        ]
    }

    result = await tool.execute({"place_ids": ["p1"]})

    # Ensure units was not passed to the client
    kwargs = mock_gmaps_client.speed_limits.call_args.kwargs
    assert "place_ids" in kwargs
    assert kwargs.get("units") is None

    assert result["status"] == "success"
    assert result["data"]["count"] == 1


@pytest.mark.asyncio
async def test_snap_to_roads_handles_api_error(
    mock_settings: Settings, mock_gmaps_client: googlemaps.Client
) -> None:
    """SnapToRoadsTool handles googlemaps.exceptions.ApiError gracefully."""
    tool = SnapToRoadsTool(mock_settings)

    mock_gmaps_client.snap_to_roads.side_effect = googlemaps.exceptions.ApiError("API_ERROR")

    result = await tool.execute(
        {
            "path": [{"lat": 1.0, "lng": 2.0}, {"lat": 1.1, "lng": 2.1}],
            "interpolate": True,
        }
    )

    assert result["status"] == "error"
    assert "API_ERROR" in result.get("error", "")


@pytest.mark.asyncio
async def test_speed_limits_handles_api_error(
    mock_settings: Settings, mock_gmaps_client: googlemaps.Client
) -> None:
    """SpeedLimitsTool handles googlemaps.exceptions.ApiError gracefully."""
    tool = SpeedLimitsTool(mock_settings)

    mock_gmaps_client.speed_limits.side_effect = googlemaps.exceptions.ApiError("PERMISSION_DENIED")

    result = await tool.execute({"place_ids": ["p1", "p2"]})

    assert result["status"] == "error"
    assert "PERMISSION_DENIED" in result.get("error", "")
