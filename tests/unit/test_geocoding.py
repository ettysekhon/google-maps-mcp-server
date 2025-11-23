"""Unit tests for Geocoding tools."""

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
