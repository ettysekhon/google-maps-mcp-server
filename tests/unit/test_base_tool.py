"""Unit tests for BaseTool."""

from typing import Any

import pytest

from google_maps_mcp_server.config import Settings
from google_maps_mcp_server.tools.base import BaseTool


class _TestTool(BaseTool):
    """Test implementation of BaseTool."""

    @property
    def name(self) -> str:
        return "test_tool"

    @property
    def description(self) -> str:
        return "A test tool"

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {"test_param": {"type": "string"}},
            "required": ["test_param"],
        }

    async def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return self._format_response({"result": "test"})


def test_base_tool_initialization() -> None:
    """Test BaseTool can be initialized."""
    settings = Settings(google_maps_api_key="AIzaSyDEMO_KEY_12345678901234567890123")
    tool = _TestTool(settings)

    assert tool.settings == settings
    assert tool.gmaps is not None


def test_base_tool_to_mcp_tool() -> None:
    """Test BaseTool can convert to MCP Tool type."""
    settings = Settings(google_maps_api_key="AIzaSyDEMO_KEY_12345678901234567890123")
    tool = _TestTool(settings)
    mcp_tool = tool.to_mcp_tool()

    assert mcp_tool.name == "test_tool"
    assert mcp_tool.description == "A test tool"
    assert mcp_tool.inputSchema == tool.input_schema


@pytest.mark.asyncio
async def test_base_tool_execute() -> None:
    """Test BaseTool execute method."""
    settings = Settings(google_maps_api_key="AIzaSyDEMO_KEY_12345678901234567890123")
    tool = _TestTool(settings)

    result = await tool.execute({"test_param": "value"})

    assert result["status"] == "success"
    assert result["tool"] == "test_tool"
    assert "data" in result


def test_base_tool_format_response_success() -> None:
    """Test BaseTool _format_response for success."""
    settings = Settings(google_maps_api_key="AIzaSyDEMO_KEY_12345678901234567890123")
    tool = _TestTool(settings)

    response = tool._format_response({"key": "value"})

    assert response["status"] == "success"
    assert response["tool"] == "test_tool"
    assert response["data"] == {"key": "value"}


def test_base_tool_format_response_error() -> None:
    """Test BaseTool _format_response for error."""
    settings = Settings(google_maps_api_key="AIzaSyDEMO_KEY_12345678901234567890123")
    tool = _TestTool(settings)

    response = tool._format_response(None, status="error", error="Test error")

    assert response["status"] == "error"
    assert response["tool"] == "test_tool"
    assert response["error"] == "Test error"
    assert "data" not in response
