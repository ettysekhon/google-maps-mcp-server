"""Unit tests for TrafficConditionsTool."""

from datetime import datetime
from unittest.mock import MagicMock

import googlemaps
import pytest

from google_maps_mcp_server.config import Settings
from google_maps_mcp_server.tools.traffic import TrafficConditionsTool


@pytest.mark.asyncio
async def test_traffic_tool_name(mock_settings: Settings) -> None:
    """Test traffic tool name and properties."""
    tool = TrafficConditionsTool(mock_settings)
    assert tool.name == "get_traffic_conditions"
    assert tool.description is not None
    assert tool.input_schema is not None


@pytest.mark.asyncio
async def test_traffic_tool_schema(mock_settings: Settings) -> None:
    """Test traffic tool schema."""
    tool = TrafficConditionsTool(mock_settings)
    schema = tool.input_schema

    assert schema["type"] == "object"
    assert "origin" in schema["properties"]
    assert "destination" in schema["properties"]
    assert "departure_time" in schema["properties"]
    assert schema["required"] == ["origin", "destination"]


@pytest.mark.asyncio
async def test_traffic_analysis_low_congestion(mock_settings: Settings) -> None:
    """Test traffic analysis with low congestion."""
    tool = TrafficConditionsTool(mock_settings)

    # Mock directions response
    mock_result = [
        {
            "legs": [
                {
                    "duration": {"value": 1000, "text": "16 mins"},
                    "duration_in_traffic": {"value": 1050, "text": "17 mins"},
                    "distance": {"text": "10 km"},
                    "start_address": "A",
                    "end_address": "B",
                    "start_location": {"lat": 1.0, "lng": 1.0},
                    "end_location": {"lat": 2.0, "lng": 2.0},
                    "steps": [],
                }
            ],
            "summary": "Main St",
        }
    ]

    # Easier to patch _execute_with_retry or the underlying gmaps client
    # Since gmaps client methods are synchronous, we should mock them as synchronous functions

    mock_gmaps = MagicMock()
    mock_gmaps.directions.return_value = mock_result
    tool.gmaps = mock_gmaps

    result = await tool.execute({"origin": "A", "destination": "B"})

    assert result["status"] == "success"
    data = result["data"]
    assert data["congestion_level"] == "Low"
    assert (
        data["delay_minutes"] == 0.8
    )  # (1050 - 1000) / 60 rounded to 1 decimal place? 50/60 = 0.833 -> 0.8
    assert data["normal_duration"] == "16 mins"
    assert data["traffic_duration"] == "17 mins"


@pytest.mark.asyncio
async def test_traffic_analysis_heavy_congestion(mock_settings: Settings) -> None:
    """Test traffic analysis with heavy congestion."""
    tool = TrafficConditionsTool(mock_settings)

    # Mock directions response with heavy traffic (> 30% delay)
    mock_result = [
        {
            "legs": [
                {
                    "duration": {"value": 1000, "text": "16 mins"},
                    "duration_in_traffic": {"value": 1400, "text": "23 mins"},  # 40% increase
                    "distance": {"text": "10 km"},
                    "start_address": "A",
                    "end_address": "B",
                    "start_location": {"lat": 1.0, "lng": 1.0},
                    "end_location": {"lat": 2.0, "lng": 2.0},
                    "steps": [],
                }
            ],
            "summary": "Main St",
        }
    ]

    mock_gmaps = MagicMock()
    mock_gmaps.directions.return_value = mock_result
    tool.gmaps = mock_gmaps

    result = await tool.execute({"origin": "A", "destination": "B"})

    assert result["status"] == "success"
    data = result["data"]
    assert data["congestion_level"] == "Heavy"
    assert data["delay_minutes"] == 6.7  # (1400 - 1000) / 60 = 6.666 -> 6.7


@pytest.mark.asyncio
async def test_traffic_tool_custom_time(mock_settings: Settings) -> None:
    """Test traffic tool with custom departure time."""
    tool = TrafficConditionsTool(mock_settings)

    mock_gmaps = MagicMock()
    mock_gmaps.directions.return_value = (
        []
    )  # Return empty to trigger "No route found" check or just check call args
    tool.gmaps = mock_gmaps

    custom_time = "2023-10-27T10:00:00Z"

    await tool.execute({"origin": "A", "destination": "B", "departure_time": custom_time})

    call_args = mock_gmaps.directions.call_args
    assert call_args.kwargs["departure_time"] == datetime.fromisoformat(
        custom_time.replace("Z", "+00:00")
    )
    assert call_args.kwargs["traffic_model"] == "best_guess"


@pytest.mark.asyncio
async def test_traffic_tool_api_error(mock_settings: Settings) -> None:
    """Test traffic tool handles API errors."""
    tool = TrafficConditionsTool(mock_settings)

    mock_gmaps = MagicMock()
    mock_gmaps.directions.side_effect = googlemaps.exceptions.ApiError("REQUEST_DENIED")
    tool.gmaps = mock_gmaps

    result = await tool.execute({"origin": "A", "destination": "B"})

    assert result["status"] == "error"
    assert "REQUEST_DENIED" in result["error"]
