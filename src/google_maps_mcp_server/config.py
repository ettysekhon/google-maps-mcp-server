"""Configuration management with validation."""

from __future__ import annotations

from typing import Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Google Maps MCP Server configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Google Maps API
    google_maps_api_key: str = ""
    # Google API key
    google_api_key: str = ""

    # Server configuration
    version: str = "0.2.1"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # API limits
    max_results: int = 20
    default_radius_meters: int = 5000
    max_radius_meters: int = 50000

    # Retry configuration
    max_retries: int = 3
    retry_min_wait: float = 1.0
    retry_max_wait: float = 10.0

    @field_validator("google_maps_api_key")
    @classmethod
    def validate_api_key(cls, v: str, info: object) -> str:
        """Validate that at least one API key is provided."""
        # If google_maps_api_key is set, verify it's not empty
        if v and v.strip():
            return v

        # Check if google_api_key was provided (it would be in the validation context if we could access it easily,
        # but Pydantic's validator execution order can be tricky.
        # Instead, we'll define a root validator or use a model_validator to check if EITHER is set.)
        return v

    @model_validator(mode="after")
    def check_api_keys(self) -> Settings:
        """Ensure at least one API key is set and sync them."""
        if not self.google_maps_api_key and not self.google_api_key:
            raise ValueError("Either GOOGLE_MAPS_API_KEY or GOOGLE_API_KEY is required")

        # If only GOOGLE_API_KEY is set, copy it to GOOGLE_MAPS_API_KEY
        if not self.google_maps_api_key:
            self.google_maps_api_key = self.google_api_key

        # If only GOOGLE_MAPS_API_KEY is set, copy it to GOOGLE_API_KEY
        if not self.google_api_key:
            self.google_api_key = self.google_maps_api_key

        return self
