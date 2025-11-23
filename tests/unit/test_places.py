"""Unit tests for Places tool."""

from unittest.mock import MagicMock, patch

import googlemaps
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


@pytest.mark.asyncio
async def test_places_new_api_client_called_with_correct_params(mock_settings: Settings) -> None:
    """PlacesTool correctly calls the new Places API client with appropriate request parameters."""
    tool = PlacesTool(mock_settings)

    mock_place = MagicMock()
    mock_place.display_name.text = "Test Place"
    mock_place.formatted_address = "123 Test St"
    mock_place.location.latitude = 37.7749
    mock_place.location.longitude = -122.4194
    mock_place.rating = 4.0
    mock_place.types = ["restaurant"]
    mock_place.id = "place123"

    mock_response = MagicMock()
    mock_response.places = [mock_place]

    with (
        patch(
            "google_maps_mcp_server.tools.places.client_options.ClientOptions"
        ) as mock_opts_class,
        patch("google_maps_mcp_server.tools.places.places_v1.PlacesClient") as mock_client_class,
    ):
        mock_client = MagicMock()
        mock_client.search_nearby.return_value = mock_response
        mock_client_class.return_value = mock_client

        mock_opts = MagicMock()
        mock_opts_class.return_value = mock_opts

        await tool.execute(
            {
                "location": "37.7749,-122.4194",
                "keyword": "restaurant",
                "radius": 2000,
                "type": "restaurant",
            }
        )

        # Verify ClientOptions was called with the API key
        mock_opts_class.assert_called_once_with(api_key=mock_settings.google_maps_api_key)

        # Verify PlacesClient was created with the options
        mock_client_class.assert_called_once_with(client_options=mock_opts)

        # Verify search_nearby was called
        assert mock_client.search_nearby.called
        call_args = mock_client.search_nearby.call_args

        # Verify the request contains correct parameters
        request = call_args.kwargs["request"]
        assert request.location_restriction.circle.center.latitude == 37.7749
        assert request.location_restriction.circle.center.longitude == -122.4194
        assert request.location_restriction.circle.radius == 2000
        assert request.included_types == ["restaurant"]
        assert request.max_result_count == min(20, mock_settings.max_results)

        # Verify metadata includes field mask
        metadata = call_args.kwargs["metadata"]
        assert (
            "x-goog-fieldmask",
            "places.displayName,places.formattedAddress,places.location,places.rating,places.types,places.id",
        ) in metadata


@pytest.mark.asyncio
async def test_places_keyword_filtering(mock_settings: Settings) -> None:
    """_search_nearby_new_api correctly filters results by keyword."""
    tool = PlacesTool(mock_settings)

    # Create mock places with different names and types
    mock_place1 = MagicMock()
    mock_place1.display_name.text = "Pizza Restaurant"
    mock_place1.formatted_address = "123 Main St"
    mock_place1.location.latitude = 40.7128
    mock_place1.location.longitude = -74.0060
    mock_place1.rating = 4.5
    mock_place1.types = ["restaurant", "food"]
    mock_place1.id = "place1"

    mock_place2 = MagicMock()
    mock_place2.display_name.text = "Coffee Shop"
    mock_place2.formatted_address = "456 Main St"
    mock_place2.location.latitude = 40.7129
    mock_place2.location.longitude = -74.0061
    mock_place2.rating = 4.0
    mock_place2.types = ["cafe", "food"]
    mock_place2.id = "place2"

    mock_place3 = MagicMock()
    mock_place3.display_name.text = "Burger Restaurant"
    mock_place3.formatted_address = "789 Main St"
    mock_place3.location.latitude = 40.7130
    mock_place3.location.longitude = -74.0062
    mock_place3.rating = 4.8
    mock_place3.types = ["restaurant", "food"]
    mock_place3.id = "place3"

    mock_response = MagicMock()
    mock_response.places = [mock_place1, mock_place2, mock_place3]

    with patch("google_maps_mcp_server.tools.places.places_v1.PlacesClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client.search_nearby.return_value = mock_response
        mock_client_class.return_value = mock_client

        # Search for "restaurant" - should match place1 and place3 (by name and type)
        result = await tool.execute(
            {
                "location": "40.7128,-74.0060",
                "keyword": "restaurant",
            }
        )

        assert result["status"] == "success"
        places = result["data"]["places"]
        assert len(places) == 2
        assert places[0]["name"] == "Pizza Restaurant"
        assert places[1]["name"] == "Burger Restaurant"


@pytest.mark.asyncio
async def test_places_handles_api_error_gracefully(mock_settings: Settings) -> None:
    """PlacesTool handles googlemaps.exceptions.ApiError and returns error response."""
    tool = PlacesTool(mock_settings)

    with patch("google_maps_mcp_server.tools.places.places_v1.PlacesClient") as mock_client_class:
        mock_client = MagicMock()
        # Simulate an API error
        mock_client.search_nearby.side_effect = googlemaps.exceptions.ApiError("PERMISSION_DENIED")
        mock_client_class.return_value = mock_client

        result = await tool.execute(
            {
                "location": "40.7128,-74.0060",
                "keyword": "restaurant",
            }
        )

        assert result["status"] == "error"
        assert "PERMISSION_DENIED" in result["error"]
        assert result["tool"] == "search_places"
