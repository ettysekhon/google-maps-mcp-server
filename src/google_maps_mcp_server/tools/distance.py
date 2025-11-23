"""Distance Matrix API tool implementation."""

from typing import Any

import googlemaps
import structlog

from .base import BaseTool

logger = structlog.get_logger()


class DistanceMatrixTool(BaseTool):
    """Calculate travel distances and times between multiple origins and destinations."""

    @property
    def name(self) -> str:
        return "calculate_distance_matrix"

    @property
    def description(self) -> str:
        return (
            "Calculate travel distances and times between multiple origins and destinations. "
            "Useful for route optimization and fleet management."
        )

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "origins": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of origin locations (addresses or 'lat,lng')",
                    "minItems": 1,
                },
                "destinations": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of destination locations (addresses or 'lat,lng')",
                    "minItems": 1,
                },
                "mode": {
                    "type": "string",
                    "enum": ["driving", "walking", "bicycling", "transit"],
                    "default": "driving",
                    "description": "Travel mode",
                },
                "avoid": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["tolls", "highways", "ferries", "indoor"]},
                    "description": "Features to avoid",
                },
                "units": {
                    "type": "string",
                    "enum": ["metric", "imperial"],
                    "default": "metric",
                    "description": "Unit system for distances",
                },
            },
            "required": ["origins", "destinations"],
        }

    async def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute distance matrix calculation."""
        try:
            origins = arguments["origins"]
            destinations = arguments["destinations"]
            mode = arguments.get("mode", "driving")
            avoid = arguments.get("avoid")
            units = arguments.get("units", "metric")

            logger.info(
                "calculating_distance_matrix",
                num_origins=len(origins),
                num_destinations=len(destinations),
                mode=mode,
            )

            result = await self._execute_with_retry(
                self.gmaps.distance_matrix,
                origins=origins,
                destinations=destinations,
                mode=mode,
                avoid=avoid,
                units=units,
            )

            # Format results
            matrix = []
            for i, row in enumerate(result["rows"]):
                origin_results = []
                for j, element in enumerate(row["elements"]):
                    if element["status"] == "OK":
                        origin_results.append(
                            {
                                "origin": result["origin_addresses"][i],
                                "destination": result["destination_addresses"][j],
                                "distance": element["distance"]["text"],
                                "distance_meters": element["distance"]["value"],
                                "duration": element["duration"]["text"],
                                "duration_seconds": element["duration"]["value"],
                                "status": "OK",
                            }
                        )
                    else:
                        origin_results.append(
                            {
                                "origin": result["origin_addresses"][i],
                                "destination": result["destination_addresses"][j],
                                "status": element["status"],
                                "error": f"Could not calculate route: {element['status']}",
                            }
                        )
                matrix.append(origin_results)

            logger.info("distance_matrix_calculated", total_routes=len(origins) * len(destinations))
            return self._format_response(
                {"matrix": matrix, "origins": len(origins), "destinations": len(destinations)}
            )

        except googlemaps.exceptions.ApiError as e:
            # Handle API errors gracefully
            error_msg = str(e)
            logger.error("distance_matrix_failed", error=error_msg)
            return self._format_response(None, status="error", error=error_msg)
        except Exception as e:
            logger.error("distance_matrix_failed", error=str(e))
            return self._format_response(None, status="error", error=str(e))
