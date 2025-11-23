"""Unit tests for Places tool."""

from unittest.mock import MagicMock, patch

import pytest

from google_maps_mcp_server.config import Settings
from google_maps_mcp_server.tools.places import PlacesTool


@pytest.mark.asyncio
async def test_places_tool_name() -> None:
    """Test places tool name."""
    settings = Settings(google_maps_api_key="AIzaSyDEMO_KEY_12345678901234567890123")
    tool = PlacesTool(settings)
    assert tool.name == "search_places"


@pytest.mark.asyncio
async def test_places_tool_schema() -> None:
    """Test places tool has valid schema."""
    settings = Settings(google_maps_api_key="AIzaSyDEMO_KEY_12345678901234567890123")
    tool = PlacesTool(settings)
    schema = tool.input_schema

    assert schema["type"] == "object"
    assert "location" in schema["properties"]
    assert "keyword" in schema["properties"]
    assert schema["required"] == ["location", "keyword"]


@pytest.mark.asyncio
async def test_places_tool_mcp_conversion() -> None:
    """Test places tool converts to MCP Tool type."""
    settings = Settings(google_maps_api_key="AIzaSyDEMO_KEY_12345678901234567890123")
    tool = PlacesTool(settings)
    mcp_tool = tool.to_mcp_tool()

    assert mcp_tool.name == "search_places"
    assert mcp_tool.description is not None
    assert mcp_tool.inputSchema is not None


@pytest.mark.asyncio
async def test_places_execute_mock(mock_settings: Settings, mock_gmaps_client: MagicMock) -> None:
    """Test places execution with mocked new Places API client."""
    tool = PlacesTool(mock_settings)

    # Mock the new Places API client and response
    mock_place = MagicMock()
    mock_place.display_name.text = "Test Restaurant"
    mock_place.formatted_address = "123 Main St"
    mock_place.location.latitude = 40.7128
    mock_place.location.longitude = -74.0060
    mock_place.rating = 4.5
    mock_place.types = ["restaurant"]
    mock_place.id = "test_place_id"

    mock_response = MagicMock()
    mock_response.places = [mock_place]

    with patch("google_maps_mcp_server.tools.places.places_v1.PlacesClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client.search_nearby.return_value = mock_response
        mock_client_class.return_value = mock_client

        result = await tool.execute(
            {
                "location": "40.7128,-74.0060",
                "keyword": "restaurant",
            }
        )

    assert result["status"] == "success"
    assert "data" in result
    assert "places" in result["data"]
    assert len(result["data"]["places"]) == 1
    assert result["data"]["places"][0]["name"] == "Test Restaurant"
