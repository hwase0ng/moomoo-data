# Changelog

All notable changes to `moomoo-data` will be documented in this file.

## [Unreleased]

### Added
- Initial release with full service layer
- Real-time stock quotes for HKSE/KLSE
- K-line (candlestick) data retrieval
- Capital flow and distribution analysis
- Chip distribution analysis with triangular distribution model
- Provider abstraction with Moomoo, YFinance, Akshare support
- Rate limiting with configurable limits
- Memory caching with TTL
- Configuration via environment variables and pydantic-settings
- Ticker format conversion utilities
- Market detection (HKSE, KLSE)

### Features
- Triangular distribution chip analysis with L-Curve decay
- Dynamic bin sizing based on market and price tier
- NumPy vectorization for 100x faster chip calculation
- Automatic fallback to alternative data providers
- Thread-safe rate limiting and caching

## [0.1.0] - 2026-04-23

### Added
- Initial release
