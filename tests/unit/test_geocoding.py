"""Unit tests for Geocoding tools."""

import googlemaps
import pytest

from google_maps_mcp_server.config import Settings
from google_maps_mcp_server.tools.geocoding import GeocodingTool, ReverseGeocodingTool


@pytest.mark.asyncio
async def test_geocoding_tool_name() -> None:
    """Test geocoding tool name."""
    settings = Settings(google_maps_api_key="AIzaSyDEMO_KEY_12345678901234567890123")
    tool = GeocodingTool(settings)
    assert tool.name == "geocode_address"


@pytest.mark.asyncio
async def test_reverse_geocoding_tool_name() -> None:
    """Test reverse geocoding tool name."""
    settings = Settings(google_maps_api_key="AIzaSyDEMO_KEY_12345678901234567890123")
    tool = ReverseGeocodingTool(settings)
    assert tool.name == "reverse_geocode"


@pytest.mark.asyncio
async def test_geocoding_schema_validation() -> None:
    """Test geocoding tool schema requires address."""
    settings = Settings(google_maps_api_key="AIzaSyDEMO_KEY_12345678901234567890123")
    tool = GeocodingTool(settings)
    schema = tool.input_schema

    assert "address" in schema["properties"]
    assert schema["required"] == ["address"]


@pytest.mark.asyncio
async def test_reverse_geocoding_schema_validation() -> None:
    """Test reverse geocoding requires lat/lng."""
    settings = Settings(google_maps_api_key="AIzaSyDEMO_KEY_12345678901234567890123")
    tool = ReverseGeocodingTool(settings)
    schema = tool.input_schema

    assert "lat" in schema["properties"]
    assert "lng" in schema["properties"]
    assert set(schema["required"]) == {"lat", "lng"}


@pytest.mark.asyncio
async def test_geocoding_handles_api_error(
    mock_settings: Settings, mock_gmaps_client: googlemaps.Client
) -> None:
    """GeocodingTool correctly handles googlemaps.exceptions.ApiError."""
    tool = GeocodingTool(mock_settings)

    mock_gmaps_client.geocode.side_effect = googlemaps.exceptions.ApiError("ZERO_RESULTS")

    result = await tool.execute({"address": "Some address"})

    assert result["status"] == "error"
    assert "ZERO_RESULTS" in result.get("error", "")


@pytest.mark.asyncio
async def test_reverse_geocoding_handles_api_error(
    mock_settings: Settings, mock_gmaps_client: googlemaps.Client
) -> None:
    """ReverseGeocodingTool correctly handles googlemaps.exceptions.ApiError."""
    tool = ReverseGeocodingTool(mock_settings)

    mock_gmaps_client.reverse_geocode.side_effect = googlemaps.exceptions.ApiError("REQUEST_DENIED")

    result = await tool.execute({"lat": 1.0, "lng": 2.0})

    assert result["status"] == "error"
    assert "REQUEST_DENIED" in result.get("error", "")
