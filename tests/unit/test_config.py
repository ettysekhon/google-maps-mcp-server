"""Unit tests for configuration."""

import pytest
from pydantic import ValidationError

from google_maps_mcp_server.config import Settings


def test_settings_requires_api_key() -> None:
    """Test that API key is required."""
    with pytest.raises(ValidationError):
        Settings(google_maps_api_key="", google_api_key="")


def test_settings_validates_log_level() -> None:
    """Test log level validation."""
    with pytest.raises(ValidationError):
        Settings(google_maps_api_key="test", log_level="INVALID")


def test_settings_defaults() -> None:
    """Test default values."""
    settings = Settings(google_maps_api_key="test_key")

    assert settings.log_level == "INFO"
    assert settings.max_results == 20
    assert settings.default_radius_meters == 5000
    assert settings.max_radius_meters == 50000


def test_settings_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test loading from environment variables."""
    monkeypatch.setenv("GOOGLE_MAPS_API_KEY", "env_key")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("MAX_RESULTS", "30")

    settings = Settings()

    assert settings.google_maps_api_key == "env_key"
    assert settings.log_level == "DEBUG"
    assert settings.max_results == 30
