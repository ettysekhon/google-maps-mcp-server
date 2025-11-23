"""Places API tool implementations."""

import asyncio
from typing import Any

import googlemaps
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import BaseTool

logger = structlog.get_logger()


class PlacesTool(BaseTool):
    """Search for nearby places using Google Places API."""

    @property
    def name(self) -> str:
        return "search_places"

    @property
    def description(self) -> str:
        return (
            "Search for nearby places based on location and keywords. "
            "Returns place names, addresses, ratings, and other details."
        )

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "Location as 'lat,lng' (e.g., '37.7749,-122.4194')",
                },
                "keyword": {
                    "type": "string",
                    "description": "Keyword to search for (e.g., 'gas station', 'restaurant')",
                },
                "radius": {
                    "type": "integer",
                    "default": 5000,
                    "description": "Search radius in meters (default: 5000, max: 50000)",
                },
                "type": {
                    "type": "string",
                    "description": "Place type (e.g., 'restaurant', 'gas_station', 'parking')",
                },
            },
            "required": ["location", "keyword"],
        }

    async def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute nearby places search."""
        try:
            location = arguments["location"]
            keyword = arguments["keyword"]
            radius = min(
                arguments.get("radius", self.settings.default_radius_meters),
                self.settings.max_radius_meters,
            )
            place_type = arguments.get("type")

            logger.info(
                "searching_places",
                location=location,
                keyword=keyword,
                radius=radius,
                type=place_type,
            )

            # Execute API call
            result = await self._execute_with_retry(
                self.gmaps.places_nearby,
                location=location,
                keyword=keyword,
                radius=radius,
                type=place_type,
            )

            # Clean and format response
            places = []
            for place in result.get("results", [])[: self.settings.max_results]:
                places.append(
                    {
                        "name": place.get("name"),
                        "address": place.get("vicinity"),
                        "location": place.get("geometry", {}).get("location"),
                        "rating": place.get("rating"),
                        "types": place.get("types", []),
                        "place_id": place.get("place_id"),
                    }
                )

            logger.info("places_found", count=len(places))
            return self._format_response({"places": places, "count": len(places)})

        except Exception as e:
            logger.exception("places_search_failed", error=str(e))
            return self._format_response(None, status="error", error=str(e))


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def search_nearby(gmaps: googlemaps.Client, params: dict[str, Any]) -> dict[str, Any]:
    """Search for nearby places with retry logic"""

    # Run in executor since googlemaps is synchronous
    loop = asyncio.get_event_loop()

    result = await loop.run_in_executor(
        None,
        lambda: gmaps.places_nearby(
            location=params["location"],
            keyword=params["keyword"],
            radius=params.get("radius", 5000),
            type=params.get("type"),
        ),
    )

    # Clean and format response for fleet safety context
    places = []
    for place in result.get("results", [])[:10]:  # Limit results
        places.append(
            {
                "name": place.get("name"),
                "address": place.get("vicinity"),
                "location": place.get("geometry", {}).get("location"),
                "rating": place.get("rating"),
                "types": place.get("types", []),
                "place_id": place.get("place_id"),
            }
        )

    return {"status": "success", "count": len(places), "places": places}
