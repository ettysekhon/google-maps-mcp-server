"""
GPS trace analysis example for fleet safety monitoring.

This example demonstrates how to:
1. Clean noisy GPS data by snapping to roads
2. Retrieve speed limits for road segments
3. Detect speeding violations
4. Generate safety reports
"""

import asyncio
from datetime import datetime
from typing import Any

from dotenv import load_dotenv

from google_maps_mcp_server.config import Settings
from google_maps_mcp_server.tools import SnapToRoadsTool, SpeedLimitsTool


class GPSTraceAnalyzer:
    """Analyze GPS traces for fleet safety monitoring."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.snap_tool = SnapToRoadsTool(settings)
        self.speed_tool = SpeedLimitsTool(settings)

    async def analyze_trace(
        self, gps_trace: list[dict[str, Any]], vehicle_id: str, timestamp: datetime
    ) -> dict[str, Any]:
        """
        Analyze a GPS trace for safety compliance.

        Args:
            gps_trace: List of GPS points with lat, lng, and speed
            vehicle_id: Vehicle identifier
            timestamp: Timestamp of the trace

        Returns:
            Analysis report with violations and recommendations
        """
        print(f"Analyzing GPS trace for vehicle {vehicle_id}")
        print(f"Trace timestamp: {timestamp}")
        print(f"Number of GPS points: {len(gps_trace)}")
        print()

        # Step 1: Snap GPS points to roads
        print("Step 1: Cleaning GPS data (snapping to roads)...")
        path = [{"lat": p["lat"], "lng": p["lng"]} for p in gps_trace]

        snap_result = await self.snap_tool.execute(
            {
                "path": path,
                "interpolate": True,
            }
        )

        if snap_result["status"] != "success":
            return {"error": "Failed to snap GPS points to roads"}

        snapped_points = snap_result["data"]["snapped_points"]
        print(f"  ✓ Snapped {len(snapped_points)} points to road network")
        print()

        # Step 2: Get speed limits for road segments
        print("Step 2: Retrieving speed limits for road segments...")
        place_ids = [p["place_id"] for p in snapped_points]

        # Remove duplicates while preserving order
        unique_place_ids = list(dict.fromkeys(place_ids))

        speed_result = await self.speed_tool.execute(
            {
                "place_ids": unique_place_ids,
                "units": "MPH",
            }
        )

        if speed_result["status"] != "success":
            return {"error": "Failed to retrieve speed limits"}

        speed_limits = {
            limit["place_id"]: limit["speed_limit"]
            for limit in speed_result["data"]["speed_limits"]
        }

        print(f"  ✓ Retrieved speed limits for {len(speed_limits)} unique road segments")
        print()

        # Step 3: Detect speeding violations
        print("Step 3: Analyzing for speeding violations...")
        violations = []

        for i, point in enumerate(snapped_points):
            place_id = point["place_id"]
            speed_limit = speed_limits.get(place_id)

            if speed_limit and i < len(gps_trace):
                vehicle_speed = gps_trace[i].get("speed", 0)  # MPH

                if vehicle_speed > speed_limit:
                    violation = {
                        "location": point["location"],
                        "speed_limit": speed_limit,
                        "vehicle_speed": vehicle_speed,
                        "overage": vehicle_speed - speed_limit,
                        "overage_percent": ((vehicle_speed - speed_limit) / speed_limit) * 100,
                        "severity": self._get_violation_severity(vehicle_speed, speed_limit),
                    }
                    violations.append(violation)

        print(f"  ✓ Found {len(violations)} speeding violations")
        print()

        # Step 4: Generate report
        report = {
            "vehicle_id": vehicle_id,
            "timestamp": timestamp.isoformat(),
            "trace_length": len(gps_trace),
            "snapped_points": len(snapped_points),
            "violations": violations,
            "compliance_score": self._calculate_compliance_score(gps_trace, violations),
            "recommendations": self._generate_recommendations(violations),
        }

        return report

    def _get_violation_severity(self, vehicle_speed: float, speed_limit: float) -> str:
        """Determine violation severity."""
        overage_percent = ((vehicle_speed - speed_limit) / speed_limit) * 100

        if overage_percent > 50:
            return "CRITICAL"
        elif overage_percent > 25:
            return "HIGH"
        elif overage_percent > 10:
            return "MEDIUM"
        else:
            return "LOW"

    def _calculate_compliance_score(
        self, gps_trace: list[dict[str, Any]], violations: list[dict[str, Any]]
    ) -> float:
        """Calculate compliance score (0-100)."""
        if not gps_trace:
            return 100.0

        violation_rate = len(violations) / len(gps_trace)
        compliance = (1 - violation_rate) * 100

        # Reduce score based on violation severity
        for violation in violations:
            if violation["severity"] == "CRITICAL":
                compliance -= 5
            elif violation["severity"] == "HIGH":
                compliance -= 3
            elif violation["severity"] == "MEDIUM":
                compliance -= 1

        return max(0.0, min(100.0, compliance))

    def _generate_recommendations(self, violations: list[dict[str, Any]]) -> list[str]:
        """Generate safety recommendations based on violations."""
        recommendations = []

        if not violations:
            recommendations.append("Excellent driving! No violations detected.")
            return recommendations

        # Count violations by severity
        severity_counts: dict[str, int] = {}
        for v in violations:
            severity = v["severity"]
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        if severity_counts.get("CRITICAL", 0) > 0:
            recommendations.append(
                "⚠️ CRITICAL: Excessive speeding detected. Immediate driver counseling required."
            )

        if severity_counts.get("HIGH", 0) > 2:
            recommendations.append(
                "⚠️ Multiple high-severity violations. Schedule driver safety training."
            )

        if len(violations) > 5:
            recommendations.append(
                "Consider installing in-vehicle speed limiters or warning systems."
            )

        recommendations.append(
            f"Total violations: {len(violations)}. Review route and driver behavior."
        )

        return recommendations

    def print_report(self, report: dict[str, Any]) -> None:
        """Print formatted safety report."""
        print("=" * 80)
        print("FLEET SAFETY ANALYSIS REPORT")
        print("=" * 80)
        print()
        print(f"Vehicle ID: {report['vehicle_id']}")
        print(f"Timestamp: {report['timestamp']}")
        print(f"Compliance Score: {report['compliance_score']:.1f}/100")
        print()

        print("Trace Summary:")
        print(f"  GPS Points: {report['trace_length']}")
        print(f"  Snapped Points: {report['snapped_points']}")
        print(f"  Violations: {len(report['violations'])}")
        print()

        if report["violations"]:
            print("Violations Detected:")
            print()
            for i, violation in enumerate(report["violations"][:5], 1):  # Show first 5
                print(f"  {i}. [{violation['severity']}] Location: {violation['location']}")
                print(f"     Speed Limit: {violation['speed_limit']} MPH")
                print(f"     Vehicle Speed: {violation['vehicle_speed']} MPH")
                print(
                    f"     Overage: {violation['overage']:.1f} MPH ({violation['overage_percent']:.1f}%)"
                )
                print()

            if len(report["violations"]) > 5:
                print(f"  ... and {len(report['violations']) - 5} more violations")
                print()

        print("Recommendations:")
        for rec in report["recommendations"]:
            print(f"  • {rec}")
        print()
        print("=" * 80)


async def main() -> None:
    """Run GPS trace analysis example."""
    load_dotenv()
    settings = Settings()

    # Example GPS trace with speed data (simulated fleet vehicle)
    # In production, this would come from vehicle telematics
    gps_trace = [
        {"lat": 40.714224, "lng": -73.961452, "speed": 28},  # Within limit
        {"lat": 40.714324, "lng": -73.961552, "speed": 32},  # Slightly over
        {"lat": 40.714424, "lng": -73.961652, "speed": 45},  # Significant speeding
        {"lat": 40.714524, "lng": -73.961752, "speed": 38},  # Over limit
        {"lat": 40.714624, "lng": -73.961852, "speed": 25},  # Within limit
        {"lat": 40.714724, "lng": -73.961952, "speed": 30},  # Within limit
        {"lat": 40.714824, "lng": -73.962052, "speed": 42},  # Speeding
        {"lat": 40.714924, "lng": -73.962152, "speed": 35},  # Slightly over
    ]

    # Analyze trace
    analyzer = GPSTraceAnalyzer(settings)
    report = await analyzer.analyze_trace(
        gps_trace=gps_trace, vehicle_id="FLEET-001", timestamp=datetime.now()
    )

    # Print report
    analyzer.print_report(report)


if __name__ == "__main__":
    asyncio.run(main())
