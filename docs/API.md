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

The Google Maps MCP Server provides 7 tools across 5 Google Maps Platform APIs:

| Tool Name | API | Purpose |
|-----------|-----|---------|
| `search_nearby_places` | Places API | Find POIs near a location |
| `get_directions` | Directions API | Get routes with traffic |
| `geocode_address` | Geocoding API | Address → Coordinates |
| `reverse_geocode` | Geocoding API | Coordinates → Address |
| `calculate_distance_matrix` | Distance Matrix API | Multi-point distances |
| `snap_to_roads` | Roads API | Clean GPS data |
| `get_speed_limits` | Roads API | Speed limit retrieval |

---

## Places API

### search_nearby_places

Search for places near a specific location.

#### Parameters

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

#### Request Example

```json
{
  "location": "40.7580,-73.9855",
  "keyword": "pizza",
  "radius": 1000,
  "type": "restaurant"
}
```

#### Response Example

```json
{
  "status": "success",
  "tool": "search_nearby_places",
  "data": {
    "places": [
      {
        "name": "Joe's Pizza",
        "address": "1435 Broadway, New York",
        "location": {
          "lat": 40.75829,
          "lng": -73.98561
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

---

## Directions API

### get_directions

Get route directions between two locations with real-time traffic.

#### Parameters

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

#### Request Example

```json
{
  "origin": "San Francisco, CA",
  "destination": "Los Angeles, CA",
  "mode": "driving",
  "departure_time": "2025-01-15T09:00:00Z",
  "alternatives": true,
  "avoid": ["tolls"],
  "traffic_model": "best_guess"
}
```

#### Response Example

```json
{
  "status": "success",
  "tool": "get_directions",
  "data": {
    "routes": [
      {
        "summary": "I-5 S",
        "distance": "616 km",
        "distance_meters": 616000,
        "duration": "5 hours 48 mins",
        "duration_seconds": 20880,
        "duration_in_traffic": "6 hours 15 mins",
        "start_address": "San Francisco, CA, USA",
        "end_address": "Los Angeles, CA, USA",
        "start_location": {"lat": 37.7749, "lng": -122.4194},
        "end_location": {"lat": 34.0522, "lng": -118.2437},
        "steps": [
          {
            "instruction": "Head south on Van Ness Ave toward Oak St",
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

---

## Geocoding API

### geocode_address

Convert a street address to geographic coordinates.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `address` | string | Yes | Street address to geocode |
| `components` | object | No | Component filters |
| `region` | string | No | Region bias (country code) |

#### Component Filters

Filter results by:

```json
{
  "country": "US",
  "postal_code": "94043",
  "locality": "Mountain View"
}
```

#### Request Example

```json
{
  "address": "1600 Amphitheatre Parkway, Mountain View, CA",
  "region": "US"
}
```

#### Response Example

```json
{
  "status": "success",
  "tool": "geocode_address",
  "data": {
    "formatted_address": "1600 Amphitheatre Pkwy, Mountain View, CA 94043, USA",
    "location": {
      "lat": 37.4224764,
      "lng": -122.0842499
    },
    "place_id": "ChIJ2eUgeAK6j4ARbn5u_wAGqWA",
    "types": ["street_address"],
    "address_components": [
      {
        "long_name": "1600",
        "short_name": "1600",
        "types": ["street_number"]
      },
      {
        "long_name": "Amphitheatre Parkway",
        "short_name": "Amphitheatre Pkwy",
        "types": ["route"]
      }
    ]
  }
}
```

### reverse_geocode

Convert geographic coordinates to a street address.

#### Parameters

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

#### Request Example

```json
{
  "lat": 40.714224,
  "lng": -73.961452,
  "result_type": ["street_address"]
}
```

#### Response Example

```json
{
  "status": "success",
  "tool": "reverse_geocode",
  "data": {
    "formatted_address": "277 Bedford Ave, Brooklyn, NY 11211, USA",
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

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `origins` | array | Yes | Array of origin locations |
| `destinations` | array | Yes | Array of destination locations |
| `mode` | string | No | Travel mode (default: "driving") |
| `avoid` | array | No | Features to avoid |
| `units` | string | No | "metric" or "imperial" |

#### Request Example

```json
{
  "origins": [
    "New York, NY",
    "Boston, MA"
  ],
  "destinations": [
    "Philadelphia, PA",
    "Washington, DC"
  ],
  "mode": "driving",
  "units": "metric"
}
```

#### Response Example

```json
{
  "status": "success",
  "tool": "calculate_distance_matrix",
  "data": {
    "matrix": [
      [
        {
          "origin": "New York, NY, USA",
          "destination": "Philadelphia, PA, USA",
          "distance": "152 km",
          "distance_meters": 152000,
          "duration": "1 hour 47 mins",
          "duration_seconds": 6420,
          "status": "OK"
        },
        {
          "origin": "New York, NY, USA",
          "destination": "Washington, DC, USA",
          "distance": "362 km",
          "distance_meters": 362000,
          "duration": "3 hours 52 mins",
          "duration_seconds": 13920,
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

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | array | Yes | Array of GPS points (2-100 points) |
| `interpolate` | boolean | No | Fill gaps between points (default: true) |

#### Path Format

Each point in the path must have:

```json
{
  "lat": 40.714224,
  "lng": -73.961452
}
```

#### Request Example

```json
{
  "path": [
    {"lat": 40.714224, "lng": -73.961452},
    {"lat": 40.714624, "lng": -73.961852},
    {"lat": 40.715024, "lng": -73.962252}
  ],
  "interpolate": true
}
```

#### Response Example

```json
{
  "status": "success",
  "tool": "snap_to_roads",
  "data": {
    "snapped_points": [
      {
        "location": {"lat": 40.714227, "lng": -73.961450},
        "original_index": 0,
        "place_id": "ChIJNwVFswe2woARUXfAcXJHxwU"
      },
      {
        "location": {"lat": 40.714623, "lng": -73.961848},
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

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `place_ids` | array | Yes | Place IDs from snap_to_roads |
| `units` | string | No | "KPH" or "MPH" (default: "KPH") |

#### Request Example

```json
{
  "place_ids": [
    "ChIJNwVFswe2woARUXfAcXJHxwU",
    "ChIJQVrGw wm2woARU_VBoPPVnKM"
  ],
  "units": "MPH"
}
```

#### Response Example

```json
{
  "status": "success",
  "tool": "get_speed_limits",
  "data": {
    "speed_limits": [
      {
        "place_id": "ChIJNwVFswe2woARUXfAcXJHxwU",
        "speed_limit": 25,
        "units": "MPH"
      },
      {
        "place_id": "ChIJQVrGwwm2woARU_VBoPPVnKM",
        "speed_limit": 35,
        "units": "MPH"
      }
    ],
    "count": 2
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
