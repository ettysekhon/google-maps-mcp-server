"""Unit tests for PlaceDetailsTool."""

from unittest.mock import MagicMock, patch

import googlemaps
import pytest

from google_maps_mcp_server.config import Settings
from google_maps_mcp_server.tools.places import PlaceDetailsTool


@pytest.mark.asyncio
async def test_place_details_tool_name(mock_settings: Settings) -> None:
    """Test place details tool name."""
    tool = PlaceDetailsTool(mock_settings)
    assert tool.name == "get_place_details"
    assert tool.description is not None
    assert tool.input_schema is not None


@pytest.mark.asyncio
async def test_place_details_execution(mock_settings: Settings) -> None:
    """Test place details execution with mocked API."""
    tool = PlaceDetailsTool(mock_settings)

    mock_place = MagicMock()
    mock_place.display_name.text = "Test Place"
    mock_place.formatted_address = "123 Test St"
    mock_place.location.latitude = 1.0
    mock_place.location.longitude = 1.0
    mock_place.id = "pid1"
    mock_place.national_phone_number = "555-1234"
    mock_place.website_uri = "http://test.com"

    with patch("google_maps_mcp_server.tools.places.places_v1.PlacesClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client.get_place.return_value = mock_place
        mock_client_class.return_value = mock_client

        result = await tool.execute({"place_id": "pid1"})

    assert result["status"] == "success"
    data = result["data"]
    assert data["name"] == "Test Place"
    assert data["phone_number"] == "555-1234"
    assert data["website"] == "http://test.com"


@pytest.mark.asyncio
async def test_place_details_custom_fields(mock_settings: Settings) -> None:
    """Test place details with custom fields."""
    tool = PlaceDetailsTool(mock_settings)

    mock_place = MagicMock()
    mock_place.display_name.text = "Test Place"

    with patch("google_maps_mcp_server.tools.places.places_v1.PlacesClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client.get_place.return_value = mock_place
        mock_client_class.return_value = mock_client

        await tool.execute({"place_id": "pid1", "fields": ["name", "phone"]})

        call_args = mock_client.get_place.call_args
        metadata = call_args.kwargs["metadata"]
        # Check if mask contains mapped fields
        mask = next(m[1] for m in metadata if m[0] == "x-goog-fieldmask")
        assert "displayName" in mask
        assert "nationalPhoneNumber" in mask


@pytest.mark.asyncio
async def test_place_details_api_error(mock_settings: Settings) -> None:
    """Test place details handles API errors."""
    tool = PlaceDetailsTool(mock_settings)

    with patch("google_maps_mcp_server.tools.places.places_v1.PlacesClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client.get_place.side_effect = googlemaps.exceptions.ApiError("NOT_FOUND")
        mock_client_class.return_value = mock_client

        result = await tool.execute({"place_id": "pid1"})

    assert result["status"] == "error"
    assert "NOT_FOUND" in result["error"]
