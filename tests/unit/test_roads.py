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


@pytest.mark.asyncio
async def test_snap_to_roads_handles_various_api_errors(
    mock_settings: Settings, mock_gmaps_client: googlemaps.Client
) -> None:
    """SnapToRoadsTool handles various types of googlemaps.exceptions.ApiError gracefully."""
    tool = SnapToRoadsTool(mock_settings)

    error_messages = [
        "REQUEST_DENIED",
        "OVER_QUERY_LIMIT",
        "INVALID_REQUEST",
        "UNKNOWN_ERROR",
    ]

    test_path = [{"lat": 40.7128, "lng": -74.0060}, {"lat": 40.7129, "lng": -74.0061}]

    for error_msg in error_messages:
        mock_gmaps_client.snap_to_roads.side_effect = googlemaps.exceptions.ApiError(error_msg)

        result = await tool.execute({"path": test_path, "interpolate": True})

        assert result["status"] == "error"
        assert error_msg in result.get("error", "")
        assert result["tool"] == "snap_to_roads"


@pytest.mark.asyncio
async def test_speed_limits_handles_various_api_errors(
    mock_settings: Settings, mock_gmaps_client: googlemaps.Client
) -> None:
    """SpeedLimitsTool handles various types of googlemaps.exceptions.ApiError gracefully."""
    tool = SpeedLimitsTool(mock_settings)

    error_messages = [
        "PERMISSION_DENIED",
        "REQUEST_DENIED",
        "OVER_QUERY_LIMIT",
        "INVALID_REQUEST",
    ]

    for error_msg in error_messages:
        mock_gmaps_client.speed_limits.side_effect = googlemaps.exceptions.ApiError(error_msg)

        result = await tool.execute({"place_ids": ["place1", "place2"]})

        assert result["status"] == "error"
        assert error_msg in result.get("error", "")
        assert result["tool"] == "get_speed_limits"


@pytest.mark.asyncio
async def test_speed_limits_does_not_pass_units_parameter(
    mock_settings: Settings, mock_gmaps_client: googlemaps.Client
) -> None:
    """SpeedLimitsTool does not send 'units' parameter when calling the Google Maps API."""
    tool = SpeedLimitsTool(mock_settings)

    # Mock successful response
    mock_gmaps_client.speed_limits.return_value = {
        "speedLimits": [
            {"placeId": "place1", "speedLimit": 100, "units": "KPH"},
            {"placeId": "place2", "speedLimit": 80, "units": "KPH"},
        ]
    }

    result = await tool.execute({"place_ids": ["place1", "place2"]})

    # Verify the method was called
    assert mock_gmaps_client.speed_limits.called

    # Get the call arguments
    call_kwargs = mock_gmaps_client.speed_limits.call_args.kwargs

    # Verify 'units' parameter is NOT in the call
    assert "units" not in call_kwargs
    # Verify 'place_ids' IS in the call
    assert "place_ids" in call_kwargs
    assert call_kwargs["place_ids"] == ["place1", "place2"]

    # Verify successful result
    assert result["status"] == "success"
    assert result["data"]["count"] == 2
    assert result["data"]["speed_limits"][0]["units"] == "KPH"


@pytest.mark.asyncio
async def test_speed_limits_returns_units_from_api_response(
    mock_settings: Settings, mock_gmaps_client: googlemaps.Client
) -> None:
    """SpeedLimitsTool correctly returns units from API response, not from request."""
    tool = SpeedLimitsTool(mock_settings)

    # Mock response with various units
    mock_gmaps_client.speed_limits.return_value = {
        "speedLimits": [
            {"placeId": "place1", "speedLimit": 65, "units": "MPH"},
            {"placeId": "place2", "speedLimit": 100, "units": "KPH"},
        ]
    }

    result = await tool.execute({"place_ids": ["place1", "place2"]})

    assert result["status"] == "success"
    assert result["data"]["count"] == 2

    # Verify units are returned from API response
    speed_limits = result["data"]["speed_limits"]
    assert speed_limits[0]["units"] == "MPH"
    assert speed_limits[0]["speed_limit"] == 65
    assert speed_limits[1]["units"] == "KPH"
    assert speed_limits[1]["speed_limit"] == 100
