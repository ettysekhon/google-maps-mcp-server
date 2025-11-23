"""Geocoding API tool implementations."""

from typing import Any

import googlemaps
import structlog

from .base import BaseTool

logger = structlog.get_logger()


class GeocodingTool(BaseTool):
    """Convert addresses to coordinates (geocoding)."""

    @property
    def name(self) -> str:
        return "geocode_address"

    @property
    def description(self) -> str:
        return "Convert a street address to geographic coordinates (latitude/longitude)."

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "address": {
                    "type": "string",
                    "description": "Street address to geocode",
                },
                "components": {
                    "type": "object",
                    "description": "Component filters (e.g., {'country': 'US'})",
                },
                "region": {
                    "type": "string",
                    "description": "Region bias (ISO 3166-1 country code)",
                },
            },
            "required": ["address"],
        }

    async def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute geocoding request."""
        try:
            address = arguments["address"]
            components = arguments.get("components")
            region = arguments.get("region")

            logger.info("geocoding_address", address=address)

            result = await self._execute_with_retry(
                self.gmaps.geocode, address=address, components=components, region=region
            )

            if not result:
                return self._format_response(
                    None, status="error", error="No results found for address"
                )

            # Format first result
            location = result[0]
            formatted_result = {
                "formatted_address": location["formatted_address"],
                "location": location["geometry"]["location"],
                "place_id": location["place_id"],
                "types": location["types"],
                "address_components": location["address_components"],
            }

            logger.info("geocoding_success", formatted_address=location["formatted_address"])
            return self._format_response(formatted_result)

        except googlemaps.exceptions.ApiError as e:
            # Handle API errors gracefully
            error_msg = str(e)
            logger.error("geocoding_failed", error=error_msg)
            return self._format_response(None, status="error", error=error_msg)
        except Exception as e:
            logger.error("geocoding_failed", error=str(e))
            return self._format_response(None, status="error", error=str(e))


class ReverseGeocodingTool(BaseTool):
    """Convert coordinates to addresses (reverse geocoding)."""

    @property
    def name(self) -> str:
        return "reverse_geocode"

    @property
    def description(self) -> str:
        return "Convert geographic coordinates (latitude/longitude) to a street address."

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "lat": {
                    "type": "number",
                    "description": "Latitude",
                    "minimum": -90,
                    "maximum": 90,
                },
                "lng": {
                    "type": "number",
                    "description": "Longitude",
                    "minimum": -180,
                    "maximum": 180,
                },
                "result_type": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Filter by result types (e.g., ['street_address', 'route'])",
                },
            },
            "required": ["lat", "lng"],
        }

    async def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute reverse geocoding request."""
        try:
            lat = arguments["lat"]
            lng = arguments["lng"]
            result_type = arguments.get("result_type")

            logger.info("reverse_geocoding", lat=lat, lng=lng)

            result = await self._execute_with_retry(
                self.gmaps.reverse_geocode, latlng=(lat, lng), result_type=result_type
            )

            if not result:
                return self._format_response(
                    None, status="error", error="No results found for coordinates"
                )

            # Format first result
            location = result[0]
            formatted_result = {
                "formatted_address": location["formatted_address"],
                "place_id": location["place_id"],
                "types": location["types"],
                "address_components": location["address_components"],
            }

            logger.info("reverse_geocoding_success", address=location["formatted_address"])
            return self._format_response(formatted_result)

        except googlemaps.exceptions.ApiError as e:
            # Handle API errors gracefully
            error_msg = str(e)
            logger.error("reverse_geocoding_failed", error=error_msg)
            return self._format_response(None, status="error", error=error_msg)
        except Exception as e:
            logger.error("reverse_geocoding_failed", error=str(e))
            return self._format_response(None, status="error", error=str(e))
