"""Integration tests for the HTTP/SSE API layer."""

import logging
import os

import pytest
from starlette.testclient import TestClient

logging.getLogger("googlemaps").setLevel(logging.WARNING)
logging.getLogger("google_maps_mcp_server").setLevel(logging.WARNING)
logging.getLogger("structlog").setLevel(logging.WARNING)

os.environ["GOOGLE_MAPS_API_KEY"] = "AIzaSyDEMO_KEY_12345678901234567890123"


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the API."""
    from google_maps_mcp_server.api import create_app

    app = create_app()
    return TestClient(app)


@pytest.mark.integration
def test_health_endpoint(client: TestClient) -> None:
    """Test the health check endpoint returns correct status."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "google-maps-mcp-server"
    assert "version" in data


@pytest.mark.integration
def test_health_endpoint_version(client: TestClient) -> None:
    """Test the health endpoint returns the correct version."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    # Version should match what's in config
    assert data["version"] == "0.2.1"


@pytest.mark.integration
@pytest.mark.skip(
    reason="SSE streaming endpoint cannot be reliably tested with TestClient without hanging"
)
def test_sse_endpoint_returns_event_stream(client: TestClient) -> None:
    """Placeholder test for SSE endpoint (verified via external script)."""
    # The SSE endpoint is exercised by scripts/verify_deployment.py against a running server.
    # Keeping this test as a placeholder so future maintainers know SSE exists.
    assert True


@pytest.mark.integration
def test_messages_endpoint_requires_post(client: TestClient) -> None:
    """Test the messages endpoint does not handle GET requests."""
    # For non-POST methods we expect a 404 because the path is only handled
    # by the raw ASGI middleware for POST requests.
    response = client.get("/messages")
    assert response.status_code == 404


@pytest.mark.integration
def test_unknown_endpoint_returns_404(client: TestClient) -> None:
    """Test unknown endpoints return 404."""
    response = client.get("/unknown")
    assert response.status_code == 404


@pytest.mark.integration
def test_api_creates_successfully() -> None:
    """Test that create_app() returns a valid ASGI app."""
    from google_maps_mcp_server.api import create_app

    app = create_app()

    # The app should be a callable (ASGI app)
    assert callable(app)
