"""Integration tests for MCP server."""

import pytest

from google_maps_mcp_server.config import Settings
from google_maps_mcp_server.server import GoogleMapsMCPServer


@pytest.mark.integration
def test_server_initialization() -> None:
    """Test server can be initialized."""
    settings = Settings(google_maps_api_key="AIzaSyDEMO_KEY_12345678901234567890123")
    server = GoogleMapsMCPServer(settings)

    assert server.settings == settings
    assert len(server.tools) == 10  # All 10 tools loaded


@pytest.mark.integration
def test_all_tools_registered() -> None:
    """Test all tools are properly registered."""
    settings = Settings(google_maps_api_key="AIzaSyDEMO_KEY_12345678901234567890123")
    server = GoogleMapsMCPServer(settings)

    tool_names = {tool.name for tool in server.tools}
    expected_names = {
        "search_places",
        "get_directions",
        "geocode_address",
        "reverse_geocode",
        "calculate_distance_matrix",
        "snap_to_roads",
        "get_speed_limits",
        "get_place_details",
        "get_traffic_conditions",
        "calculate_route_safety_factors",
    }

    assert tool_names == expected_names
