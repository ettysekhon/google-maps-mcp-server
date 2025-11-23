"""Unit tests for Distance Matrix tool."""

import pytest

from google_maps_mcp_server.config import Settings
from google_maps_mcp_server.tools.distance import DistanceMatrixTool


@pytest.mark.asyncio
async def test_distance_matrix_tool_name() -> None:
    """Test distance matrix tool name."""
    settings = Settings(google_maps_api_key="AIzaSyDEMO_KEY_12345678901234567890123")
    tool = DistanceMatrixTool(settings)
    assert tool.name == "calculate_distance_matrix"


@pytest.mark.asyncio
async def test_distance_matrix_schema() -> None:
    """Test distance matrix tool has valid schema."""
    settings = Settings(google_maps_api_key="AIzaSyDEMO_KEY_12345678901234567890123")
    tool = DistanceMatrixTool(settings)
    schema = tool.input_schema

    assert schema["type"] == "object"
    assert "origins" in schema["properties"]
    assert "destinations" in schema["properties"]
    assert schema["properties"]["origins"]["type"] == "array"
    assert schema["properties"]["destinations"]["type"] == "array"
    assert set(schema["required"]) == {"origins", "destinations"}


@pytest.mark.asyncio
async def test_distance_matrix_units() -> None:
    """Test distance matrix supports both unit systems."""
    settings = Settings(google_maps_api_key="AIzaSyDEMO_KEY_12345678901234567890123")
    tool = DistanceMatrixTool(settings)
    schema = tool.input_schema

    units_enum = schema["properties"]["units"]["enum"]
    assert "metric" in units_enum
    assert "imperial" in units_enum
