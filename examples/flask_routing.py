"""
Fleet routing example using Google Maps MCP Server.

This example demonstrates how to optimize routes for a fleet of delivery vehicles
using the Distance Matrix and Directions APIs.
"""

import asyncio
from typing import Any

from dotenv import load_dotenv

from google_maps_mcp_server.config import Settings
from google_maps_mcp_server.tools import (
    DirectionsTool,
    DistanceMatrixTool,
    GeocodingTool,
)


class FleetRouter:
    """Simple fleet routing optimizer."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.distance_tool = DistanceMatrixTool(settings)
        self.directions_tool = DirectionsTool(settings)
        self.geocoding_tool = GeocodingTool(settings)

    async def optimize_route(
        self, depot: str, destinations: list[str], vehicle_count: int = 1
    ) -> dict[str, Any]:
        """
        Optimize delivery routes for multiple vehicles.

        Args:
            depot: Starting location (warehouse/depot)
            destinations: List of delivery addresses
            vehicle_count: Number of available vehicles

        Returns:
            Optimized route assignments
        """
        print(
            f"Optimizing routes for {len(destinations)} deliveries with {vehicle_count} vehicle(s)"
        )
        print(f"Depot: {depot}")
        print()

        # Step 1: Geocode all locations to get coordinates
        print("Step 1: Geocoding locations...")
        locations = {}

        # Geocode depot
        depot_result = await self.geocoding_tool.execute({"address": depot})
        if depot_result["status"] == "success":
            locations[depot] = depot_result["data"]["location"]
            print(f"  ✓ Depot: {depot}")

        # Geocode destinations
        for dest in destinations:
            dest_result = await self.geocoding_tool.execute({"address": dest})
            if dest_result["status"] == "success":
                locations[dest] = dest_result["data"]["location"]
                print(f"  ✓ {dest}")

        print()

        # Step 2: Calculate distance matrix
        print("Step 2: Calculating distance matrix...")
        all_locations = [depot] + destinations

        matrix_result = await self.distance_tool.execute(
            {
                "origins": all_locations,
                "destinations": all_locations,
                "mode": "driving",
            }
        )

        if matrix_result["status"] != "success":
            return {"error": "Failed to calculate distance matrix"}

        # Build distance matrix
        distances: dict[str, dict[str, float]] = {}
        durations: dict[str, dict[str, float]] = {}

        for i, origin in enumerate(all_locations):
            distances[origin] = {}
            durations[origin] = {}
            for j, destination in enumerate(all_locations):
                route = matrix_result["data"]["matrix"][i][j]
                if route["status"] == "OK":
                    distances[origin][destination] = route["distance_meters"]
                    durations[origin][destination] = route["duration_seconds"]

        print(f"  ✓ Calculated {len(all_locations)}x{len(all_locations)} matrix")
        print()

        # Step 3: Simple route optimization (nearest neighbor heuristic)
        print("Step 3: Optimizing routes using nearest neighbor algorithm...")
        routes = []
        remaining_destinations = destinations.copy()

        for vehicle_num in range(vehicle_count):
            if not remaining_destinations:
                break

            route = {
                "vehicle": vehicle_num + 1,
                "stops": [depot],
                "total_distance_km": 0,
                "total_duration_min": 0,
            }

            current_location = depot

            # Build route using nearest neighbor
            while remaining_destinations:
                # Find nearest unvisited destination
                nearest = min(
                    remaining_destinations, key=lambda dest: distances[current_location][dest]
                )

                route["stops"].append(nearest)
                route["total_distance_km"] += distances[current_location][nearest] / 1000
                route["total_duration_min"] += durations[current_location][nearest] / 60

                remaining_destinations.remove(nearest)
                current_location = nearest

                # Limit stops per vehicle
                if len(route["stops"]) - 1 >= len(destinations) // vehicle_count + 1:
                    break

            # Return to depot
            route["stops"].append(depot)
            route["total_distance_km"] += distances[current_location][depot] / 1000
            route["total_duration_min"] += durations[current_location][depot] / 60

            routes.append(route)
            print(f"  ✓ Vehicle {vehicle_num + 1}: {len(route['stops']) - 2} stops")

        print()

        # Step 4: Get detailed directions for each route
        print("Step 4: Getting detailed turn-by-turn directions...")
        for route in routes:
            # Get directions for the full route
            waypoints = route["stops"][1:-1]  # Exclude start and end depot

            if waypoints:
                # For simplicity, get directions from depot to first stop
                # In production, you'd get directions for the entire route with waypoints
                directions_result = await self.directions_tool.execute(
                    {
                        "origin": route["stops"][0],
                        "destination": route["stops"][1],
                        "mode": "driving",
                        "alternatives": False,
                    }
                )

                if directions_result["status"] == "success":
                    route["directions"] = directions_result["data"]["routes"][0]
                    print(f"  ✓ Vehicle {route['vehicle']}: Got turn-by-turn directions")

        print()

        return {
            "depot": depot,
            "routes": routes,
            "total_destinations": len(destinations),
            "vehicles_used": len(routes),
        }

    def print_route_summary(self, result: dict[str, Any]) -> None:
        """Print a summary of optimized routes."""
        print("=" * 80)
        print("ROUTE OPTIMIZATION SUMMARY")
        print("=" * 80)
        print()
        print(f"Depot: {result['depot']}")
        print(f"Total Destinations: {result['total_destinations']}")
        print(f"Vehicles Used: {result['vehicles_used']}")
        print()

        for route in result["routes"]:
            print(f"Vehicle {route['vehicle']}:")
            print(f"  Stops: {len(route['stops']) - 2} deliveries")
            print(f"  Total Distance: {route['total_distance_km']:.1f} km")
            print(f"  Total Duration: {route['total_duration_min']:.0f} minutes")
            print(f"  Route: {' → '.join(route['stops'])}")
            print()


async def main() -> None:
    """Run fleet routing example."""
    load_dotenv()
    settings = Settings()

    # Example: Delivery company in New York
    depot = "350 5th Ave, New York, NY 10118"  # Empire State Building

    destinations = [
        "Times Square, New York, NY",
        "Central Park, New York, NY",
        "Brooklyn Bridge, New York, NY",
        "Statue of Liberty, New York, NY",
        "Grand Central Terminal, New York, NY",
        "One World Trade Center, New York, NY",
    ]

    router = FleetRouter(settings)

    # Optimize routes with 2 vehicles
    result = await router.optimize_route(depot=depot, destinations=destinations, vehicle_count=2)

    # Print summary
    router.print_route_summary(result)


if __name__ == "__main__":
    asyncio.run(main())
