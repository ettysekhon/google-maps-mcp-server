"""Elevation API tool implementation."""

from typing import Any

import googlemaps
import structlog

from .base import BaseTool

logger = structlog.get_logger()


class ElevationTool(BaseTool):
    """Get elevation gain and profile for a route."""

    @property
    def name(self) -> str:
        return "get_route_elevation_gain"

    @property
    def description(self) -> str:
        return (
            "Calculate elevation gain and retrieve elevation profile for a route. "
            "Useful for cycling, hiking, or fuel efficiency analysis."
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
                    "enum": ["driving", "walking", "bicycling"],
                    "default": "bicycling",
                    "description": "Travel mode (elevation is most relevant for bicycling/walking)",
                },
                "samples": {
                    "type": "integer",
                    "default": 50,
                    "description": "Number of elevation samples along the route (max 512)",
                },
            },
            "required": ["origin", "destination"],
        }

    async def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute elevation analysis."""
        try:
            origin = arguments["origin"]
            destination = arguments["destination"]
            mode = arguments.get("mode", "bicycling")
            samples = min(arguments.get("samples", 50), 512)

            logger.info(
                "calculating_elevation_gain",
                origin=origin,
                destination=destination,
                mode=mode,
            )

            # 1. Get the route first to get the path
            directions_result = await self._execute_with_retry(
                self.gmaps.directions,
                origin=origin,
                destination=destination,
                mode=mode,
            )

            if not directions_result:
                return self._format_response(None, status="error", error="No route found")

            route = directions_result[0]
            overview_polyline = route["overview_polyline"]["points"]

            # 2. Get elevation along the path
            # elevation_along_path automatically decodes the polyline and samples points
            elevation_data = await self._execute_with_retry(
                self.gmaps.elevation_along_path,
                path=overview_polyline,
                samples=samples,
            )

            # 3. Calculate stats
            total_gain = 0.0
            total_loss = 0.0
            max_elevation = -float("inf")
            min_elevation = float("inf")

            profile = []

            for i, point in enumerate(elevation_data):
                elev = point["elevation"]
                max_elevation = max(max_elevation, elev)
                min_elevation = min(min_elevation, elev)

                profile.append(
                    {
                        "distance_percentage": (
                            int((i / (len(elevation_data) - 1)) * 100)
                            if len(elevation_data) > 1
                            else 0
                        ),
                        "elevation_meters": round(elev, 1),
                    }
                )

                if i > 0:
                    diff = elev - elevation_data[i - 1]["elevation"]
                    if diff > 0:
                        total_gain += diff
                    else:
                        total_loss += abs(diff)

            result = {
                "route_summary": route.get("summary"),
                "total_distance": route["legs"][0]["distance"]["text"],
                "elevation_stats": {
                    "total_gain_meters": round(total_gain, 1),
                    "total_loss_meters": round(total_loss, 1),
                    "max_elevation_meters": round(max_elevation, 1),
                    "min_elevation_meters": round(min_elevation, 1),
                },
                "elevation_profile": profile,  # Sampled points
            }

            logger.info("elevation_calculated", gain=total_gain)
            return self._format_response(result)

        except googlemaps.exceptions.ApiError as e:
            error_msg = str(e)
            logger.error("elevation_failed", error=error_msg)
            return self._format_response(None, status="error", error=error_msg)
        except Exception as e:
            logger.error("elevation_failed", error=str(e))
            return self._format_response(None, status="error", error=str(e))
