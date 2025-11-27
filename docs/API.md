# API Reference

Complete reference for all Google Maps MCP Server tools.

## Table of Contents

- [Tools Overview](#tools-overview)
- [Places API](#places-api)
- [Directions API](#directions-api)
- [Geocoding API](#geocoding-api)
- [Distance Matrix API](#distance-matrix-api)
- [Roads API](#roads-api)
- [Error Handling](#error-handling)
- [Response Formats](#response-formats)

## Tools Overview

The Google Maps MCP Server provides 10 tools across 5 Google Maps Platform APIs:

| Tool Name | API | Purpose |
|-----------|-----|---------|
| `search_places` | Places API | Find POIs near a location |
| `get_place_details` | Places API | Get comprehensive details for a place |
| `get_directions` | Directions API | Get routes with traffic |
| `get_traffic_conditions` | Directions API | Analyse real-time traffic congestion |
| `geocode_address` | Geocoding API | Address → Coordinates |
| `reverse_geocode` | Geocoding API | Coordinates → Address |
| `calculate_distance_matrix` | Distance Matrix API | Multi-point distances |
| `snap_to_roads` | Roads API | Clean GPS data |
| `get_speed_limits` | Roads API | Speed limit retrieval |
| `calculate_route_safety_factors` | Compound | Assess route safety risks |

---

## Places API

### search_places

Search for places near a specific location.

#### Parameters (search_places)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `location` | string | Yes | Location as "lat,lng" or address |
| `keyword` | string | Yes | Search keyword (e.g., "restaurant") |
| `radius` | integer | No | Search radius in meters (default: 5000, max: 50000) |
| `type` | string | No | Place type filter |

#### Place Types

Common place types:

- `restaurant`, `cafe`, `bar`
- `gas_station`, `parking`
- `hospital`, `pharmacy`, `doctor`
- `hotel`, `lodging`
- `bank`, `atm`
- `store`, `shopping_mall`
- `park`, `gym`

[Full list of place types](https://developers.google.com/maps/documentation/places/web-service/supported_types)

#### Request Example (search_places)

```json
{
  "location": "51.5118,-0.1175",
  "keyword": "pizza",
  "radius": 1000,
  "type": "restaurant"
}
```

#### Response Example (search_places)

```json
{
  "status": "success",
  "tool": "search_places",
  "data": {
    "places": [
      {
        "name": "Pizza Express",
        "address": "The Strand, London",
        "location": {
          "lat": 51.5120,
          "lng": -0.1180
        },
        "rating": 4.3,
        "user_ratings_total": 1234,
        "types": ["restaurant", "food", "point_of_interest"],
        "place_id": "ChIJN1t_tDeuEmsRUsoyG83frY4",
        "business_status": "OPERATIONAL"
      }
    ],
    "count": 1,
    "radius_meters": 1000
  }
}
```

### get_place_details

Get comprehensive details for a place.

#### Parameters (get_place_details)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `place_id` | string | Yes | The unique Place ID |
| `fields` | array | No | Specific fields to retrieve (e.g., ["name", "phone", "hours"]) |

#### Request Example (get_place_details)

```json
{
  "place_id": "ChIJN1t_tDeuEmsRUsoyG83frY4",
  "fields": ["name", "website", "hours"]
}
```

#### Response Example (get_place_details)

```json
{
  "status": "success",
  "tool": "get_place_details",
  "data": {
    "name": "The Ritz London",
    "website": "https://www.theritzlondon.com",
    "opening_hours": {
      "open_now": true,
      "periods": [...],
      "weekday_text": ["Monday: Open 24 hours", ...]
    }
  }
}
```

---

## Directions API

### get_directions

Get route directions between two locations with real-time traffic.

#### Parameters (get_directions)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `origin` | string | Yes | Start location |
| `destination` | string | Yes | End location |
| `mode` | string | No | Travel mode (default: "driving") |
| `departure_time` | string | No | ISO 8601 timestamp |
| `alternatives` | boolean | No | Return alternative routes (default: true) |
| `avoid` | array | No | Features to avoid |
| `traffic_model` | string | No | Traffic prediction model |

#### Travel Modes

- `driving` - Car directions (default)
- `walking` - Pedestrian directions
- `bicycling` - Bicycle directions
- `transit` - Public transportation

#### Avoidance Options

- `tolls` - Avoid toll roads
- `highways` - Avoid highways
- `ferries` - Avoid ferries
- `indoor` - Avoid indoor steps

#### Traffic Models

- `best_guess` - Default traffic model
- `optimistic` - Optimistic traffic assumptions
- `pessimistic` - Pessimistic traffic assumptions

#### Request Example (get_directions)

```json
{
  "origin": "London, UK",
  "destination": "Manchester, UK",
  "mode": "driving",
  "departure_time": "2025-01-15T09:00:00Z",
  "alternatives": true,
  "avoid": ["tolls"],
  "traffic_model": "best_guess"
}
```

#### Response Example (get_directions)

```json
{
  "status": "success",
  "tool": "get_directions",
  "data": {
    "routes": [
      {
        "summary": "M4",
        "distance": "320 km",
        "distance_meters": 320000,
        "duration": "3 hours 48 mins",
        "duration_seconds": 13680,
        "duration_in_traffic": "4 hours 15 mins",
        "start_address": "London, UK",
        "end_address": "Manchester, UK",
        "start_location": {"lat": 51.5074, "lng": -0.1278},
        "end_location": {"lat": 53.4808, "lng": -2.2426},
        "steps": [
          {
            "instruction": "Head north on M1",
            "distance": "0.2 km",
            "duration": "1 min"
          }
        ],
        "warnings": []
      }
    ],
    "count": 1
  }
}
```

### get_traffic_conditions

Analyze real-time traffic conditions between two locations.

#### Parameters (get_traffic_conditions)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `origin` | string | Yes | Starting location |
| `destination` | string | Yes | Ending location |
| `departure_time` | string | No | ISO 8601 timestamp (defaults to now) |

#### Request Example (get_traffic_conditions)

```json
{
  "origin": "London, UK",
  "destination": "Oxford, UK"
}
```

#### Response Example (get_traffic_conditions)

```json
{
  "status": "success",
  "tool": "get_traffic_conditions",
  "data": {
    "route_summary": "M40",
    "normal_duration": "1 hour 10 mins",
    "traffic_duration": "1 hour 35 mins",
    "delay_minutes": 25.0,
    "congestion_level": "Moderate",
    "distance": "90 km",
    "start_address": "London, UK",
    "end_address": "Oxford, UK"
  }
}
```

---

## Geocoding API

### geocode_address

Convert a street address to geographic coordinates.

#### Parameters (geocode_address)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `address` | string | Yes | Street address to geocode |
| `components` | object | No | Component filters |
| `region` | string | No | Region bias (country code) |

#### Component Filters

Filter results by:

```json
{
  "country": "GB",
  "postal_code": "SW1A 2AA",
  "locality": "London"
}
```

#### Request Example (geocode_address)

```json
{
  "address": "10 Downing Street, London, UK",
  "region": "GB"
}
```

#### Response Example (geocode_address)

```json
{
  "status": "success",
  "tool": "geocode_address",
  "data": {
    "formatted_address": "10 Downing St, London SW1A 2AA, UK",
    "location": {
      "lat": 51.5034,
      "lng": -0.1276
    },
    "place_id": "ChIJ2eUgeAK6j4ARbn5u_wAGqWA",
    "types": ["street_address"],
    "address_components": [
      {
        "long_name": "10",
        "short_name": "10",
        "types": ["street_number"]
      },
      {
        "long_name": "Downing Street",
        "short_name": "Downing St",
        "types": ["route"]
      }
    ]
  }
}
```

### reverse_geocode

Convert geographic coordinates to a street address.

#### Parameters (reverse_geocode)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `lat` | number | Yes | Latitude (-90 to 90) |
| `lng` | number | Yes | Longitude (-180 to 180) |
| `result_type` | array | No | Filter by result types |

#### Result Types

Filter by types such as:

- `street_address` - Precise street address
- `route` - Named route
- `locality` - City/town
- `postal_code` - Postal code
- `country` - Country

#### Request Example (reverse_geocode)

```json
{
  "lat": 51.5034,
  "lng": -0.1276,
  "result_type": ["street_address"]
}
```

#### Response Example (reverse_geocode)

```json
{
  "status": "success",
  "tool": "reverse_geocode",
  "data": {
    "formatted_address": "10 Downing St, London SW1A 2AA, UK",
    "place_id": "ChIJd8BlQ2BZwokRAFUEcm_qrcA",
    "types": ["street_address"],
    "address_components": [...]
  }
}
```

---

## Distance Matrix API

### calculate_distance_matrix

Calculate travel distances and times between multiple origins and destinations.

#### Parameters (calculate_distance_matrix)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `origins` | array | Yes | Array of origin locations |
| `destinations` | array | Yes | Array of destination locations |
| `mode` | string | No | Travel mode (default: "driving") |
| `avoid` | array | No | Features to avoid |
| `units` | string | No | "metric" or "imperial" |

#### Request Example (calculate_distance_matrix)

```json
{
  "origins": ["London, UK", "Manchester, UK"],
  "destinations": ["Birmingham, UK", "Leeds, UK"],
  "mode": "driving",
  "units": "metric"
}
```

#### Response Example (calculate_distance_matrix)

```json
{
  "status": "success",
  "tool": "calculate_distance_matrix",
  "data": {
    "matrix": [
      [
        {
          "origin": "London, UK",
          "destination": "Birmingham, UK",
          "distance": "190 km",
          "distance_meters": 190000,
          "duration": "2 hours 15 mins",
          "duration_seconds": 8100,
          "status": "OK"
        },
        {
          "origin": "London, UK",
          "destination": "Leeds, UK",
          "distance": "310 km",
          "distance_meters": 310000,
          "duration": "3 hours 30 mins",
          "duration_seconds": 12600,
          "status": "OK"
        }
      ]
    ],
    "origins": 2,
    "destinations": 2
  }
}
```

---

## Roads API

### snap_to_roads

Snap GPS coordinates to the nearest road on the road network.

#### Parameters (snap_to_roads)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | array | Yes | Array of GPS points (2-100 points) |
| `interpolate` | boolean | No | Fill gaps between points (default: true) |

#### Path Format

Each point in the path must have:

```json
{
  "lat": 51.5034,
  "lng": -0.1276
}
```

#### Request Example (snap_to_roads)

```json
{
  "path": [
    {"lat": 51.5034, "lng": -0.1276},
    {"lat": 51.5035, "lng": -0.1275},
    {"lat": 51.5036, "lng": -0.1274}
  ],
  "interpolate": true
}
```

#### Response Example (snap_to_roads)

```json
{
  "status": "success",
  "tool": "snap_to_roads",
  "data": {
    "snapped_points": [
      {
        "location": {"lat": 51.5034, "lng": -0.1276},
        "original_index": 0,
        "place_id": "ChIJNwVFswe2woARUXfAcXJHxwU"
      },
      {
        "location": {"lat": 51.5035, "lng": -0.1275},
        "original_index": 1,
        "place_id": "ChIJNwVFswe2woARUXfAcXJHxwU"
      }
    ],
    "count": 2
  }
}
```

### get_speed_limits

Get speed limit information for road segments.

#### Parameters (get_speed_limits)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `place_ids` | array | Yes | Place IDs from snap_to_roads |

#### Request Example (get_speed_limits)

```json
{
  "place_ids": [
    "ChIJNwVFswe2woARUXfAcXJHxwU",
    "ChIJQVrGwwm2woARU_VBoPPVnKM"
  ]
}
```

#### Response Example (get_speed_limits)

```json
{
  "status": "success",
  "tool": "get_speed_limits",
  "data": {
    "speed_limits": [
      {
        "place_id": "ChIJNwVFswe2woARUXfAcXJHxwU",
        "speed_limit": 30,
        "units": "MPH"
      },
      {
        "place_id": "ChIJQVrGwwm2woARU_VBoPPVnKM",
        "speed_limit": 40,
        "units": "MPH"
      }
    ],
    "count": 2
  }
}
```

### calculate_route_safety_factors

Assess route safety risks.

#### Parameters (calculate_route_safety_factors)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `origin` | string | Yes | Starting location |
| `destination` | string | Yes | Ending location |
| `departure_time` | string | No | ISO 8601 timestamp (defaults to now) |

#### Request Example (calculate_route_safety_factors)

```json
{
  "origin": "London, UK",
  "destination": "Oxford, UK",
  "departure_time": "2023-10-27T23:00:00Z"
}
```

#### Response Example (calculate_route_safety_factors)

```json
{
  "status": "success",
  "tool": "calculate_route_safety_factors",
  "data": {
    "safety_score": 78.5,
    "risk_level": "Moderate",
    "details": {
      "traffic_risk": "Moderate",
      "road_risk": "Low Speed",
      "time_risk": "Night",
      "max_speed_limit_kmh": 112
    },
    "risk_factors": [
      "Traffic: Moderate congestion",
      "Conditions: Night driving"
    ],
    "route_summary": "M40"
  }
}
```

---

## Error Handling

All tools return errors in a consistent format:

```json
{
  "status": "error",
  "tool": "tool_name",
  "error": "Error message describing what went wrong"
}
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `REQUEST_DENIED` | API not enabled or key restricted | Enable API in Google Cloud Console |
| `INVALID_REQUEST` | Missing or invalid parameters | Check parameter format |
| `OVER_QUERY_LIMIT` | Exceeded API quota | Check quota in Google Cloud Console |
| `ZERO_RESULTS` | No results found | Try broader search parameters |
| `UNKNOWN_ERROR` | Server error | Retry request |

### Retry Logic

The server automatically retries failed requests:

- Maximum retries: 3 (configurable)
- Exponential backoff: 1s, 2s, 4s
- Only retries on 5xx errors

---

## Response Formats

### Success Response

```json
{
  "status": "success",
  "tool": "tool_name",
  "data": {
    // Tool-specific data
  }
}
```

### Error Response

```json
{
  "status": "error",
  "tool": "tool_name",
  "error": "Error message"
}
```

### Data Types

- **Coordinates**: `{"lat": number, "lng": number}`
- **Distance**: Text (e.g., "5.2 km") and meters
- **Duration**: Text (e.g., "15 mins") and seconds
- **Place ID**: String identifier for a place
- **Address**: Formatted string

---

## Rate Limits

Default Google Maps API quotas:

| API | Requests per Day | Requests per Second |
|-----|------------------|---------------------|
| Geocoding | 40,000 | 50 |
| Directions | 40,000 | 50 |
| Distance Matrix | 100 elements per query | |
| Places | 40,000 | 50 |
| Roads | 40,000 | 50 |

Quotas can be increased in Google Cloud Console.

---

## Best Practices

1. **Caching**: Cache results when possible to reduce API calls
2. **Batch Requests**: Use Distance Matrix for multiple origin/destination pairs
3. **Error Handling**: Always check response status
4. **Rate Limiting**: Implement client-side rate limiting if making many requests
5. **API Key Security**: Never expose API keys in client-side code

---

For more information, see the [Google Maps Platform Documentation](https://developers.google.com/maps/documentation).
