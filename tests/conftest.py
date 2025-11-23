"""Pytest configuration and fixtures."""

from collections.abc import Iterator
from unittest.mock import MagicMock, patch

import pytest

from google_maps_mcp_server.config import Settings
from google_maps_mcp_server.server import GoogleMapsMCPServer


@pytest.fixture
def mock_settings() -> Settings:
    """Create mock settings for testing."""
    return Settings(
        google_maps_api_key="AIzaSyDEMO_KEY_12345678901234567890123",
        log_level="DEBUG",
        max_results=10,
        default_radius_meters=5000,
        max_radius_meters=50000,
    )


@pytest.fixture
def mock_gmaps_client() -> Iterator[MagicMock]:
    """Mock Google Maps client."""
    with patch("google_maps_mcp_server.tools.base.googlemaps.Client") as mock_client_class:
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def server(mock_settings: Settings) -> GoogleMapsMCPServer:
    """Create server instance for testing."""
    return GoogleMapsMCPServer(mock_settings)
