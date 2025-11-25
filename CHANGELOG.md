# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-01-XX

### Added

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

[Unreleased]: https://github.com/ettysekhon/google-maps-mcp-server/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ettysekhon/google-maps-mcp-server/releases/tag/v0.1.0
