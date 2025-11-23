"""Directions API tool implementation."""

from datetime import datetime
from typing import Any

import structlog

from .base import BaseTool

logger = structlog.get_logger()


class DirectionsTool(BaseTool):
    """Get route directions between two locations with traffic data."""

    @property
    def name(self) -> str:
        return "get_directions"

    @property
    def description(self) -> str:
        return (
            "Get route directions between origin and destination with real-time traffic data. "
            "Returns routes with distance, duration, steps, and traffic information."
        )

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "origin": {
                    "type": "string",
                    "description": "Starting location (address or 'lat,lng')",
                },
                "destination": {
                    "type": "string",
                    "description": "Ending location (address or 'lat,lng')",
                },
                "mode": {
                    "type": "string",
                    "enum": ["driving", "walking", "bicycling", "transit"],
                    "default": "driving",
                    "description": "Travel mode",
                },
                "departure_time": {
                    "type": "string",
                    "description": "ISO 8601 timestamp for departure (for traffic estimation)",
                },
                "alternatives": {
                    "type": "boolean",
                    "default": True,
                    "description": "Return alternative routes",
                },
                "avoid": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["tolls", "highways", "ferries", "indoor"]},
                    "description": "Features to avoid",
                },
                "traffic_model": {
                    "type": "string",
                    "enum": ["best_guess", "optimistic", "pessimistic"],
                    "default": "best_guess",
                    "description": "Traffic prediction model",
                },
            },
            "required": ["origin", "destination"],
        }

    async def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute directions request."""
        try:
            origin = arguments["origin"]
            destination = arguments["destination"]
            mode = arguments.get("mode", "driving")
            alternatives = arguments.get("alternatives", True)
            avoid = arguments.get("avoid")
            traffic_model = arguments.get("traffic_model", "best_guess")

            # Parse departure time if provided
            departure_time = None
            if "departure_time" in arguments:
                departure_time = datetime.fromisoformat(
                    arguments["departure_time"].replace("Z", "+00:00")
                )
            elif mode == "driving":
                departure_time = datetime.now()  # Use current time for traffic

            logger.info(
                "getting_directions",
                origin=origin,
                destination=destination,
                mode=mode,
                departure_time=departure_time,
            )

            # Execute API call
            result = await self._execute_with_retry(
                self.gmaps.directions,
                origin=origin,
                destination=destination,
                mode=mode,
                departure_time=departure_time,
                alternatives=alternatives,
                avoid=avoid,
                traffic_model=traffic_model if mode == "driving" else None,
            )

            # Format results
            routes = []
            for route in result:
                leg = route["legs"][0]  # First leg
                routes.append(
                    {
                        "summary": route.get("summary"),
                        "distance": leg["distance"]["text"],
                        "distance_meters": leg["distance"]["value"],
                        "duration": leg["duration"]["text"],
                        "duration_seconds": leg["duration"]["value"],
                        "duration_in_traffic": (
                            leg.get("duration_in_traffic", {}).get("text")
                            if "duration_in_traffic" in leg
                            else None
                        ),
                        "start_address": leg["start_address"],
                        "end_address": leg["end_address"],
                        "start_location": leg["start_location"],
                        "end_location": leg["end_location"],
                        "steps": [
                            {
                                "instruction": step.get("html_instructions", "")
                                .replace("<b>", "")
                                .replace("</b>", "")
                                .replace("<div", "\n<div"),
                                "distance": step["distance"]["text"],
                                "duration": step["duration"]["text"],
                            }
                            for step in leg["steps"]
                        ],
                        "warnings": route.get("warnings", []),
                    }
                )

            logger.info("directions_found", num_routes=len(routes))
            return self._format_response({"routes": routes, "count": len(routes)})

        except Exception as e:
            logger.exception("directions_failed", error=str(e))
            return self._format_response(None, status="error", error=str(e))
