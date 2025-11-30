# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.1] - 2025-11-30

### Added for version 0.2.1

- `get_route_elevation_gain` tool to calculate elevation stats and profiles for routes (useful for cycling/hiking).
- Optional `traffic_model` parameter to `get_traffic_conditions` and `calculate_route_safety_factors` tools (supports `best_guess`, `optimistic`, `pessimistic`).

## [0.2.0] - 2025-11-29

### Added for version 0.2.0

- `get_place_details` tool to retrieve comprehensive place information (opening hours, contact details, websites) using the new Places API.
- `get_traffic_conditions` tool for real-time congestion analysis and delay estimates between locations.
- `calculate_route_safety_factors` tool for assessing route safety based on traffic density, road types, speed limits, and time of day.
- Granular unit tests for all new tools (`TrafficConditionsTool`, `RouteSafetyTool`, `PlaceDetailsTool`).
- Integration tests covering the full suite of 10 tools.

### Changed

- Migrated Places API usage to the new Google Maps Places API (v1) for improved data access and field masking.
- Enhanced error handling across all tools with clearer user-facing messages.
- Optimised CI pipeline by separating Codecov uploads into a dedicated workflow for better security with protected branches.

## [0.1.0] - 2025-01-23

### Added for version 0.1.0

- Initial release of Google Maps MCP Server
- Support for Places API (nearby search)
- Support for Directions API (with real-time traffic)
- Support for Geocoding API (forward and reverse)
- Support for Distance Matrix API
- Support for Roads API (snap to roads, speed limits)
- Production-ready error handling and retry logic
- Comprehensive test suite
- Docker support
- Full documentation and examples

### Features

- 7 MCP tools covering all major Google Maps APIs
- Type-safe implementation with Pydantic
- Structured logging with structlog
- Automatic retries with exponential backoff
- Claude Desktop integration
- Google ADK integration examples

[Unreleased]: https://github.com/ettysekhon/google-maps-mcp-server/compare/v0.2.1...HEAD
[0.2.1]: https://github.com/ettysekhon/google-maps-mcp-server/releases/tag/v0.2.1
[0.2.0]: https://github.com/ettysekhon/google-maps-mcp-server/releases/tag/v0.2.0
[0.1.0]: https://github.com/ettysekhon/google-maps-mcp-server/releases/tag/v0.1.0
