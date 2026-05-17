# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-05-17

### Added

- Initial release of the VecTrade Python SDK
- Sync (`VecTrade`) and async (`AsyncVecTrade`) clients
- Resources: quotes, fundamentals, technicals, news, earnings, insider, analyst, options, screener, developer, webhooks
- AI streaming analysis with generator-based interface
- Automatic retries with exponential backoff and jitter
- Typed exception hierarchy with structured error parsing
- Pydantic v2 response models with full type safety
- Middleware support for request/response interceptors
- LangChain integration (`vectrade.integrations.langchain`)
- OpenTelemetry observability (optional `[telemetry]` extra)
- Pandas DataFrame conversion (optional `[pandas]` extra)
- Comprehensive test suite (206 tests, 70%+ coverage)
- CI: GitHub Actions with Python 3.9–3.13 matrix
- PyPI trusted publishing workflow

[Unreleased]: https://github.com/VecTrade-io/vectrade-python/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/VecTrade-io/vectrade-python/releases/tag/v0.1.0
