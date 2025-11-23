"""Places API tool implementations."""

import asyncio
from typing import Any

import googlemaps
import structlog
from google.api_core import client_options
from google.maps import places_v1
from google.type import latlng_pb2
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
        """Execute nearby places search using the new Places API."""
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

            # Parse location (lat,lng)
            lat_str, lng_str = location.split(",")
            lat = float(lat_str.strip())
            lng = float(lng_str.strip())

            # Execute API call using new Places API
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self._search_nearby_new_api(lat, lng, radius, keyword, place_type),
            )

            # Format response
            places = result[: self.settings.max_results]

            logger.info("places_found", count=len(places))
            return self._format_response({"places": places, "count": len(places)})

        except googlemaps.exceptions.ApiError as e:
            # Handle API errors gracefully (e.g., PERMISSION_DENIED, REQUEST_DENIED)
            error_msg = str(e)
            logger.error("places_search_failed", error=error_msg)
            return self._format_response(None, status="error", error=error_msg)
        except Exception as e:
            logger.error("places_search_failed", error=str(e))
            return self._format_response(None, status="error", error=str(e))

    def _search_nearby_new_api(
        self,
        lat: float,
        lng: float,
        radius: float,
        keyword: str,
        place_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search nearby places using the new Places API."""
        # Create client with API key authentication
        opts = client_options.ClientOptions(api_key=self.settings.google_maps_api_key)
        client = places_v1.PlacesClient(client_options=opts)

        # Build the request
        request = places_v1.SearchNearbyRequest(
            location_restriction=places_v1.SearchNearbyRequest.LocationRestriction(
                circle=places_v1.Circle(
                    center=latlng_pb2.LatLng(latitude=lat, longitude=lng),
                    radius=radius,
                )
            ),
            included_types=[place_type] if place_type else [],
            max_result_count=min(20, self.settings.max_results),
            rank_preference=places_v1.SearchNearbyRequest.RankPreference.DISTANCE,
        )

        # Add field mask to specify which fields to return
        # This is required by the new API
        field_mask = "places.displayName,places.formattedAddress,places.location,places.rating,places.types,places.id"

        # Execute the search
        response = client.search_nearby(
            request=request, metadata=[("x-goog-fieldmask", field_mask)]
        )

        # Format results
        places = []
        for place in response.places:
            # Filter by keyword if provided (new API doesn't have keyword parameter)
            if keyword:
                keyword_lower = keyword.lower()
                display_name = place.display_name.text.lower() if place.display_name else ""
                types_str = " ".join(place.types).lower() if place.types else ""
                if keyword_lower not in display_name and keyword_lower not in types_str:
                    continue

            places.append(
                {
                    "name": place.display_name.text if place.display_name else None,
                    "address": place.formatted_address if place.formatted_address else None,
                    "location": {
                        "lat": place.location.latitude if place.location else None,
                        "lng": place.location.longitude if place.location else None,
                    },
                    "rating": place.rating if hasattr(place, "rating") else None,
                    "types": list(place.types) if place.types else [],
                    "place_id": place.id if place.id else None,
                }
            )

        return places


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
