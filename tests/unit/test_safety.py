"""Unit tests for RouteSafetyTool."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from google_maps_mcp_server.config import Settings
from google_maps_mcp_server.tools.safety import RouteSafetyTool


@pytest.mark.asyncio
async def test_safety_tool_name(mock_settings: Settings) -> None:
    """Test safety tool name and properties."""
    tool = RouteSafetyTool(mock_settings)
    assert tool.name == "calculate_route_safety_factors"
    assert tool.description is not None
    assert tool.input_schema is not None


@pytest.mark.asyncio
async def test_safety_calculation_low_risk(mock_settings: Settings) -> None:
    """Test safety calculation for a safe route."""
    tool = RouteSafetyTool(mock_settings)

    # Mock directions (low traffic)
    mock_directions = [
        {
            "legs": [
                {
                    "duration": {"value": 1000},
                    "duration_in_traffic": {"value": 1050},  # Low traffic
                    "steps": [{"start_location": {"lat": 1.0, "lng": 1.0}}],
                    "summary": "Safe St",
                }
            ],
            "summary": "Safe St",
        }
    ]

    # Mock snap to roads
    mock_snapped = [{"placeId": "pid1"}]

    # Mock speed limits (low speed)
    mock_limits = [{"speedLimit": 50}]

    mock_gmaps = MagicMock()
    mock_gmaps.directions.return_value = mock_directions
    mock_gmaps.snap_to_roads.return_value = mock_snapped
    mock_gmaps.speed_limits.return_value = mock_limits
    tool.gmaps = mock_gmaps

    # Set fixed time to day (12:00) to avoid night penalty
    with patch("google_maps_mcp_server.tools.safety.datetime") as mock_datetime:
        mock_datetime.now.return_value.hour = 12
        mock_datetime.fromisoformat.side_effect = lambda x: datetime.fromisoformat(x)

        result = await tool.execute({"origin": "A", "destination": "B"})

    assert result["status"] == "success"
    data = result["data"]
    assert data["risk_level"] == "Low"
    assert data["safety_score"] > 80
    assert data["details"]["traffic_risk"] == "Low"
    assert data["details"]["road_risk"] == "Low Speed"
    assert data["details"]["time_risk"] == "Day"


@pytest.mark.asyncio
async def test_safety_calculation_high_risk(mock_settings: Settings) -> None:
    """Test safety calculation for a risky route."""
    tool = RouteSafetyTool(mock_settings)

    # Mock directions (high traffic)
    mock_directions = [
        {
            "legs": [
                {
                    "duration": {"value": 1000},
                    "duration_in_traffic": {"value": 1500},  # 50% delay -> High traffic
                    "steps": [{"start_location": {"lat": 1.0, "lng": 1.0}}],
                    "summary": "Danger Hwy",
                }
            ],
            "summary": "Danger Hwy",
        }
    ]

    # Mock snap to roads
    mock_snapped = [{"placeId": "pid1"}]

    # Mock speed limits (high speed)
    mock_limits = [{"speedLimit": 120}]

    mock_gmaps = MagicMock()
    mock_gmaps.directions.return_value = mock_directions
    mock_gmaps.snap_to_roads.return_value = mock_snapped
    mock_gmaps.speed_limits.return_value = mock_limits
    tool.gmaps = mock_gmaps

    # Set fixed time to night (02:00)
    with patch("google_maps_mcp_server.tools.safety.datetime") as mock_datetime:
        mock_datetime.now.return_value.hour = 2

        result = await tool.execute({"origin": "A", "destination": "B"})

    assert result["status"] == "success"
    data = result["data"]
    # Traffic Score (4) * 4 + Speed Score (6) * 4 + Time Score (6) * 2 = 16 + 24 + 12 = 52
    assert data["safety_score"] == 52.0
    assert data["risk_level"] == "High"
    assert data["details"]["traffic_risk"] == "High"
    assert data["details"]["road_risk"] == "High Speed"
    assert data["details"]["time_risk"] == "Night"


@pytest.mark.asyncio
async def test_safety_tool_handles_partial_api_failures(mock_settings: Settings) -> None:
    """Test safety tool handles partial API failures (e.g. Roads API fails)."""
    tool = RouteSafetyTool(mock_settings)

    # Mock directions success
    mock_directions = [
        {
            "legs": [
                {
                    "duration": {"value": 1000},
                    "duration_in_traffic": {"value": 1000},
                    "steps": [{"start_location": {"lat": 1.0, "lng": 1.0}}],
                    "summary": "Main St",
                }
            ],
            "summary": "Main St",
        }
    ]

    mock_gmaps = MagicMock()
    mock_gmaps.directions.return_value = mock_directions
    # Roads API fails
    mock_gmaps.snap_to_roads.side_effect = Exception("Roads API error")
    tool.gmaps = mock_gmaps

    result = await tool.execute({"origin": "A", "destination": "B"})

    assert result["status"] == "success"
    # Should still calculate score based on defaults
    assert result["data"]["details"]["road_risk"] == "Unknown"
    assert result["data"]["details"]["max_speed_limit_kmh"] is None
