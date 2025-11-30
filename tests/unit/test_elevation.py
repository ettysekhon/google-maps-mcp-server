"""Unit tests for ElevationTool."""

from unittest.mock import MagicMock

import googlemaps
import pytest

from google_maps_mcp_server.config import Settings
from google_maps_mcp_server.tools.elevation import ElevationTool


@pytest.mark.asyncio
async def test_elevation_tool_name(mock_settings: Settings) -> None:
    """Test elevation tool name and properties."""
    tool = ElevationTool(mock_settings)
    assert tool.name == "get_route_elevation_gain"
    assert tool.description is not None
    assert tool.input_schema is not None


@pytest.mark.asyncio
async def test_elevation_analysis_success(mock_settings: Settings) -> None:
    """Test elevation analysis with successful API responses."""
    tool = ElevationTool(mock_settings)

    # Mock route response
    mock_directions = [
        {
            "legs": [{"distance": {"text": "10 km"}}],
            "overview_polyline": {"points": "encoded_polyline"},
            "summary": "Scenic Route",
        }
    ]

    # Mock elevation response
    mock_elevation = [
        {"elevation": 10.0},
        {"elevation": 20.0},
        {"elevation": 15.0},
        {"elevation": 25.0},
    ]

    mock_gmaps = MagicMock()
    mock_gmaps.directions.return_value = mock_directions
    mock_gmaps.elevation_along_path.return_value = mock_elevation
    tool.gmaps = mock_gmaps

    result = await tool.execute({"origin": "A", "destination": "B", "mode": "bicycling"})

    assert result["status"] == "success"
    data = result["data"]
    assert data["route_summary"] == "Scenic Route"
    assert data["total_distance"] == "10 km"

    stats = data["elevation_stats"]
    # 10->20 (+10), 20->15 (-5), 15->25 (+10) = +20 gain, 5 loss
    assert stats["total_gain_meters"] == 20.0
    assert stats["total_loss_meters"] == 5.0
    assert stats["max_elevation_meters"] == 25.0
    assert stats["min_elevation_meters"] == 10.0

    profile = data["elevation_profile"]
    assert len(profile) == 4
    assert profile[0]["elevation_meters"] == 10.0
    assert profile[-1]["distance_percentage"] == 100


@pytest.mark.asyncio
async def test_elevation_tool_no_route(mock_settings: Settings) -> None:
    """Test elevation tool when no route is found."""
    tool = ElevationTool(mock_settings)

    mock_gmaps = MagicMock()
    mock_gmaps.directions.return_value = []
    tool.gmaps = mock_gmaps

    result = await tool.execute({"origin": "A", "destination": "B"})

    assert result["status"] == "error"
    assert "No route found" in result["error"]


@pytest.mark.asyncio
async def test_elevation_tool_api_error(mock_settings: Settings) -> None:
    """Test elevation tool handles API errors."""
    tool = ElevationTool(mock_settings)

    mock_gmaps = MagicMock()
    mock_gmaps.directions.side_effect = googlemaps.exceptions.ApiError("REQUEST_DENIED")
    tool.gmaps = mock_gmaps

    result = await tool.execute({"origin": "A", "destination": "B"})

    assert result["status"] == "error"
    assert "REQUEST_DENIED" in result["error"]
