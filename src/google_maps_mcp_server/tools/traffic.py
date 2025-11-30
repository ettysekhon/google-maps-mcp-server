"""Traffic analysis tool implementation."""

from datetime import datetime
from typing import Any

import googlemaps
import structlog

from .base import BaseTool

logger = structlog.get_logger()


class TrafficConditionsTool(BaseTool):
    """Analyze traffic conditions between two locations."""

    @property
    def name(self) -> str:
        return "get_traffic_conditions"

    @property
    def description(self) -> str:
        return (
            "Analyze real-time traffic conditions between origin and destination. "
            "Returns duration in traffic, delay estimates, and congestion level."
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
                "departure_time": {
                    "type": "string",
                    "description": "ISO 8601 timestamp for departure (defaults to now)",
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
        """Execute traffic analysis."""
        try:
            origin = arguments["origin"]
            destination = arguments["destination"]
            traffic_model = arguments.get("traffic_model", "best_guess")

            # Default to now if not provided
            departure_time = datetime.now()
            if "departure_time" in arguments:
                departure_time = datetime.fromisoformat(
                    arguments["departure_time"].replace("Z", "+00:00")
                )

            logger.info(
                "analyzing_traffic",
                origin=origin,
                destination=destination,
                departure_time=departure_time,
                traffic_model=traffic_model,
            )

            # Call Directions API
            # We need two calls ideally to get accurate "free flow" vs "traffic" baseline,
            # but Directions API returns standard "duration" (usually average/free flow)
            # and "duration_in_traffic" (real-time) in the same response if departure_time is set.
            result = await self._execute_with_retry(
                self.gmaps.directions,
                origin=origin,
                destination=destination,
                mode="driving",
                departure_time=departure_time,
                traffic_model=traffic_model,
            )

            if not result:
                return self._format_response(None, status="error", error="No route found")

            route = result[0]
            leg = route["legs"][0]

            duration_seconds = leg["duration"]["value"]
            duration_text = leg["duration"]["text"]

            # duration_in_traffic might be missing if not available
            in_traffic_seconds = leg.get("duration_in_traffic", {}).get("value", duration_seconds)
            in_traffic_text = leg.get("duration_in_traffic", {}).get("text", duration_text)

            delay_seconds = max(0, in_traffic_seconds - duration_seconds)
            delay_minutes = delay_seconds / 60.0

            # Calculate congestion estimation
            # < 10% delay = Low
            # 10-30% delay = Moderate
            # > 30% delay = Heavy
            congestion_level = "Low"
            if duration_seconds > 0:
                ratio = in_traffic_seconds / duration_seconds
                if ratio > 1.3:
                    congestion_level = "Heavy"
                elif ratio > 1.1:
                    congestion_level = "Moderate"

            analysis = {
                "route_summary": route.get("summary"),
                "normal_duration": duration_text,
                "traffic_duration": in_traffic_text,
                "delay_minutes": round(delay_minutes, 1),
                "congestion_level": congestion_level,
                "distance": leg["distance"]["text"],
                "start_address": leg["start_address"],
                "end_address": leg["end_address"],
                "traffic_model_used": traffic_model,
            }

            logger.info(
                "traffic_analyzed",
                congestion=congestion_level,
                delay=delay_minutes,
            )

            return self._format_response(analysis)

        except googlemaps.exceptions.ApiError as e:
            error_msg = str(e)
            logger.error("traffic_analysis_failed", error=error_msg)
            return self._format_response(None, status="error", error=error_msg)
        except Exception as e:
            logger.error("traffic_analysis_failed", error=str(e))
            return self._format_response(None, status="error", error=str(e))
