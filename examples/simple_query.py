"""
Simple example of using Google Maps MCP Server tools directly.

This example demonstrates basic usage of each tool without MCP protocol overhead.
"""

import asyncio

from dotenv import load_dotenv

from google_maps_mcp_server.config import Settings
from google_maps_mcp_server.tools import (
    DirectionsTool,
    DistanceMatrixTool,
    GeocodingTool,
    PlacesTool,
    ReverseGeocodingTool,
    SnapToRoadsTool,
    SpeedLimitsTool,
)


async def main() -> None:
    """Run simple examples for each tool."""
    # Load environment variables
    load_dotenv()

    # Initialize settings
    settings = Settings()

    print("=" * 80)
    print("Google Maps MCP Server - Simple Usage Examples")
    print("=" * 80)
    print()

    # Example 1: Search for nearby places
    print("1. Searching for coffee shops near Times Square...")
    print("-" * 80)
    places_tool = PlacesTool(settings)
    places_result = await places_tool.execute(
        {
            "location": "40.7580,-73.9855",  # Times Square coordinates
            "keyword": "coffee",
            "radius": 500,
        }
    )

    if places_result["status"] == "success":
        print(f"Found {places_result['data']['count']} coffee shops:")
        for place in places_result["data"]["places"][:3]:  # Show first 3
            print(f"  - {place['name']}")
            print(f"    Address: {place['address']}")
            print(f"    Rating: {place.get('rating', 'N/A')}⭐")
            print()
    print()

    # Example 2: Get directions
    print("2. Getting directions from NYC to Boston...")
    print("-" * 80)
    directions_tool = DirectionsTool(settings)
    directions_result = await directions_tool.execute(
        {
            "origin": "New York, NY",
            "destination": "Boston, MA",
            "mode": "driving",
            "alternatives": False,
        }
    )

    if directions_result["status"] == "success":
        route = directions_result["data"]["routes"][0]
        print(f"Distance: {route['distance']}")
        print(f"Duration: {route['duration']}")
        if route.get("duration_in_traffic"):
            print(f"Duration in traffic: {route['duration_in_traffic']}")
        print(f"Route: {route['summary']}")
        print()
    print()

    # Example 3: Geocode an address
    print("3. Geocoding Google headquarters address...")
    print("-" * 80)
    geocoding_tool = GeocodingTool(settings)
    geocode_result = await geocoding_tool.execute(
        {"address": "1600 Amphitheatre Parkway, Mountain View, CA"}
    )

    if geocode_result["status"] == "success":
        data = geocode_result["data"]
        print(f"Address: {data['formatted_address']}")
        print(f"Coordinates: {data['location']['lat']}, {data['location']['lng']}")
        print(f"Place ID: {data['place_id']}")
        print()
    print()

    # Example 4: Reverse geocode coordinates
    print("4. Reverse geocoding coordinates (Eiffel Tower)...")
    print("-" * 80)
    reverse_geocoding_tool = ReverseGeocodingTool(settings)
    reverse_result = await reverse_geocoding_tool.execute(
        {
            "lat": 48.8584,
            "lng": 2.2945,
        }
    )

    if reverse_result["status"] == "success":
        print(f"Address: {reverse_result['data']['formatted_address']}")
        print()
    print()

    # Example 5: Calculate distance matrix
    print("5. Calculating distances between major US cities...")
    print("-" * 80)
    distance_tool = DistanceMatrixTool(settings)
    distance_result = await distance_tool.execute(
        {
            "origins": ["New York, NY", "Los Angeles, CA"],
            "destinations": ["Chicago, IL", "Miami, FL"],
            "mode": "driving",
        }
    )

    if distance_result["status"] == "success":
        print("Distance Matrix:")
        for origin_routes in distance_result["data"]["matrix"]:
            for route in origin_routes:
                if route["status"] == "OK":
                    print(f"  {route['origin']} → {route['destination']}")
                    print(f"    Distance: {route['distance']}")
                    print(f"    Duration: {route['duration']}")
                    print()
    print()

    # Example 6: Snap to roads (GPS trace cleaning)
    print("6. Snapping GPS coordinates to roads...")
    print("-" * 80)
    snap_tool = SnapToRoadsTool(settings)

    # Example GPS trace (slightly off the road)
    gps_trace = [
        {"lat": 40.714224, "lng": -73.961452},
        {"lat": 40.714624, "lng": -73.961852},
        {"lat": 40.715024, "lng": -73.962252},
    ]

    snap_result = await snap_tool.execute(
        {
            "path": gps_trace,
            "interpolate": True,
        }
    )

    if snap_result["status"] == "success":
        print(f"Snapped {snap_result['data']['count']} points to roads")
        print("Original points → Snapped points:")
        for i, point in enumerate(snap_result["data"]["snapped_points"][:3]):
            original = gps_trace[point.get("original_index", i)]
            snapped = point["location"]
            print(
                f"  ({original['lat']:.6f}, {original['lng']:.6f}) → "
                f"({snapped['lat']:.6f}, {snapped['lng']:.6f})"
            )
        print()
    print()

    # Example 7: Get speed limits
    if snap_result["status"] == "success" and snap_result["data"]["snapped_points"]:
        print("7. Getting speed limits for road segments...")
        print("-" * 80)
        speed_tool = SpeedLimitsTool(settings)

        # Get place IDs from snapped points
        place_ids = [p["place_id"] for p in snap_result["data"]["snapped_points"][:2]]

        speed_result = await speed_tool.execute(
            {
                "place_ids": place_ids,
                "units": "MPH",
            }
        )

        if speed_result["status"] == "success":
            print(f"Found speed limits for {speed_result['data']['count']} segments:")
            for limit in speed_result["data"]["speed_limits"]:
                print(f"  Speed limit: {limit['speed_limit']} {limit['units']}")
            print()

    print("=" * 80)
    print("All examples completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
