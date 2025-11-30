"""Route safety scoring tool implementation."""

from datetime import datetime
from typing import Any

import googlemaps
import structlog

from .base import BaseTool

logger = structlog.get_logger()


class RouteSafetyTool(BaseTool):
    """Calculate safety scores for a route based on traffic, road conditions, and speed limits."""

    @property
    def name(self) -> str:
        return "calculate_route_safety_factors"

    @property
    def description(self) -> str:
        return (
            "Calculate safety assessment for a route. "
            "Analyzes traffic congestion, road types, and speed limits to identify risk factors."
        )

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "origin": {
                    "type": "string",
                    "description": "Starting location",
                },
                "destination": {
                    "type": "string",
                    "description": "Ending location",
                },
                "departure_time": {
                    "type": "string",
                    "description": "ISO 8601 timestamp for departure (defaults to now)",
                },
                "traffic_model": {
                    "type": "string",
                    "enum": ["best_guess", "optimistic", "pessimistic"],
                    "default": "pessimistic",
                    "description": "Traffic prediction model (defaults to pessimistic for safety analysis)",
                },
            },
            "required": ["origin", "destination"],
        }

    async def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute safety analysis."""
        try:
            origin = arguments["origin"]
            destination = arguments["destination"]
            traffic_model = arguments.get("traffic_model", "pessimistic")

            departure_time = datetime.now()
            if "departure_time" in arguments:
                departure_time = datetime.fromisoformat(
                    arguments["departure_time"].replace("Z", "+00:00")
                )

            logger.info(
                "calculating_route_safety",
                origin=origin,
                destination=destination,
                traffic_model=traffic_model,
            )

            # 1. Get Route & Traffic
            directions_result = await self._execute_with_retry(
                self.gmaps.directions,
                origin=origin,
                destination=destination,
                mode="driving",
                departure_time=departure_time,
                traffic_model=traffic_model,
            )

            if not directions_result:
                return self._format_response(None, status="error", error="No route found")

            route = directions_result[0]
            leg = route["legs"][0]

            # Traffic Analysis
            duration_seconds = leg["duration"]["value"]
            in_traffic_seconds = leg.get("duration_in_traffic", {}).get("value", duration_seconds)

            traffic_risk = "Low"
            traffic_score = 10.0
            if duration_seconds > 0:
                traffic_ratio = in_traffic_seconds / duration_seconds
                if traffic_ratio > 1.4:
                    traffic_risk = "High"
                    traffic_score = 4.0
                elif traffic_ratio > 1.1:
                    traffic_risk = "Moderate"
                    traffic_score = 7.0

            # 2. Road Type & Speed Limit Analysis
            # Sample points from steps for speed limit check
            path_points = []
            for step in leg["steps"]:
                loc = step["start_location"]
                path_points.append(f"{loc['lat']},{loc['lng']}")

            # Limit to max 50 points for API quotas
            sample_points = path_points[:50]

            speed_risk = "Unknown"
            speed_score = 5.0  # Neutral default
            max_speed_limit = 0

            try:
                # Snap to roads to get place IDs (more accurate for speed limits)
                snapped = await self._execute_with_retry(
                    self.gmaps.snap_to_roads, path="|".join(sample_points), interpolate=True
                )

                if snapped:
                    place_ids = [p["placeId"] for p in snapped[:50]]  # Limit again just in case

                    # Get speed limits
                    limits = await self._execute_with_retry(
                        self.gmaps.speed_limits, place_ids=place_ids
                    )

                    speeds = []
                    for limit in limits:
                        if "speedLimit" in limit:
                            speeds.append(limit["speedLimit"])

                    if speeds:
                        max_speed_limit = max(speeds)

                        # Higher speed roads are generally riskier for severity,
                        # but highways are safer per mile than city streets.
                        # This logic is subjective for the example.
                        if max_speed_limit > 100:
                            speed_risk = "High Speed"
                            speed_score = 6.0
                        elif max_speed_limit > 60:
                            speed_risk = "Moderate Speed"
                            speed_score = 8.0
                        else:
                            speed_risk = "Low Speed"
                            speed_score = 9.0
            except Exception:
                # Roads API might fail or not be enabled, gracefully downgrade
                logger.warning("speed_limit_check_failed_continuing")

            # 3. Calculate Overall Safety Score (0-100)
            # Weighted average: Traffic (40%) + Speed/Road (40%) + Weather/Time (20% - placeholder)

            # Time of day risk (Night is riskier)
            hour = departure_time.hour
            time_risk = "Day"
            time_score = 10.0
            if hour < 6 or hour > 20:
                time_risk = "Night"
                time_score = 6.0

            overall_score = traffic_score * 4 + speed_score * 4 + time_score * 2

            risk_factors = []
            if traffic_risk != "Low":
                risk_factors.append(f"Traffic: {traffic_risk} congestion")
            if speed_risk == "High Speed":
                risk_factors.append(f"Road: High speed limit ({max_speed_limit} km/h)")
            if time_risk == "Night":
                risk_factors.append("Conditions: Night driving")

            assessment = {
                "safety_score": round(overall_score, 1),
                "risk_level": (
                    "High" if overall_score < 60 else "Moderate" if overall_score < 80 else "Low"
                ),
                "details": {
                    "traffic_risk": traffic_risk,
                    "road_risk": speed_risk,
                    "time_risk": time_risk,
                    "max_speed_limit_kmh": max_speed_limit if max_speed_limit > 0 else None,
                },
                "risk_factors": risk_factors,
                "route_summary": route.get("summary"),
                "traffic_model_used": traffic_model,
            }

            logger.info("route_safety_calculated", score=overall_score)
            return self._format_response(assessment)

        except googlemaps.exceptions.ApiError as e:
            error_msg = str(e)
            logger.error("safety_analysis_failed", error=error_msg)
            return self._format_response(None, status="error", error=error_msg)
        except Exception as e:
            logger.error("safety_analysis_failed", error=str(e))
            return self._format_response(None, status="error", error=str(e))
