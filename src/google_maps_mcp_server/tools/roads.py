"""Roads API tool implementations."""

from typing import Any

import structlog

from .base import BaseTool

logger = structlog.get_logger()


class SnapToRoadsTool(BaseTool):
    """Snap GPS coordinates to nearest roads."""

    @property
    def name(self) -> str:
        return "snap_to_roads"

    @property
    def description(self) -> str:
        return (
            "Snap GPS coordinates to the nearest road. Useful for cleaning noisy GPS data "
            "from vehicle tracking systems."
        )

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "lat": {"type": "number"},
                            "lng": {"type": "number"},
                        },
                        "required": ["lat", "lng"],
                    },
                    "description": "Array of GPS coordinates to snap to roads",
                    "minItems": 2,
                    "maxItems": 100,
                },
                "interpolate": {
                    "type": "boolean",
                    "default": True,
                    "description": "Fill gaps between GPS points",
                },
            },
            "required": ["path"],
        }

    async def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute snap to roads request."""
        try:
            path = arguments["path"]
            interpolate = arguments.get("interpolate", True)

            # Convert path to tuples format
            path_tuples = [(point["lat"], point["lng"]) for point in path]

            logger.info("snapping_to_roads", num_points=len(path_tuples))

            result = await self._execute_with_retry(
                self.gmaps.snap_to_roads, path=path_tuples, interpolate=interpolate
            )

            # Format results
            snapped_points = []
            for point in result:
                snapped_points.append(
                    {
                        "location": point["location"],
                        "original_index": point.get("originalIndex"),
                        "place_id": point["placeId"],
                    }
                )

            logger.info("roads_snapped", snapped_points=len(snapped_points))
            return self._format_response(
                {"snapped_points": snapped_points, "count": len(snapped_points)}
            )

        except Exception as e:
            logger.exception("snap_to_roads_failed", error=str(e))
            return self._format_response(None, status="error", error=str(e))


class SpeedLimitsTool(BaseTool):
    """Get speed limits for road segments."""

    @property
    def name(self) -> str:
        return "get_speed_limits"

    @property
    def description(self) -> str:
        return (
            "Get speed limit data for road segments. Requires place IDs from snap_to_roads. "
            "Critical for fleet safety and compliance monitoring."
        )

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "place_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Place IDs from snap_to_roads results",
                    "minItems": 1,
                    "maxItems": 100,
                },
                "units": {
                    "type": "string",
                    "enum": ["KPH", "MPH"],
                    "default": "KPH",
                    "description": "Speed limit units",
                },
            },
            "required": ["place_ids"],
        }

    async def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute speed limits request."""
        try:
            place_ids = arguments["place_ids"]
            units = arguments.get("units", "KPH")

            logger.info("getting_speed_limits", num_places=len(place_ids))

            result = await self._execute_with_retry(
                self.gmaps.speed_limits, place_ids=place_ids, units=units
            )

            # Format results
            speed_limits = []
            for limit in result.get("speedLimits", []):
                speed_limits.append(
                    {
                        "place_id": limit["placeId"],
                        "speed_limit": limit["speedLimit"],
                        "units": limit["units"],
                    }
                )

            logger.info("speed_limits_retrieved", count=len(speed_limits))
            return self._format_response({"speed_limits": speed_limits, "count": len(speed_limits)})

        except Exception as e:
            logger.exception("speed_limits_failed", error=str(e))
            return self._format_response(None, status="error", error=str(e))
