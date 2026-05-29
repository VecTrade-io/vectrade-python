# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-05-29

### Changed

- **Stable release** — all public APIs finalized, semver enforced from this point

## [0.2.0] - 2026-05-29

### Fixed

- Options resource: corrected endpoint path to `/vq/options/{symbol}/chain` and response parsing for calls/puts arrays
- Analyst resource: fixed paths to `/vq/analyst-consensus/`, `/vq/analyst-targets/`, `/vq/upgrades-downgrades/`
- Fundamentals resource: aligned with nested `income_statement.earnings` and `balance_sheet.earnings` response structure
- Screener resource: changed to POST `/vq/screener/filter` with JSON body
- Options types: added camelCase aliases, nullable volume/openInterest fields
- Analyst types: corrected `ticker` alias, `ratings` dict, `targets` dict structure
- Fundamental types: updated to capitalized field names ("Total Revenue", "Total Assets"), added `extra="allow"`

### Added

- Developer self-service endpoints: `get_plan()`, `get_usage()`, `get_daily_usage()`, `get_quota()`, `list_keys()`, `create_key()`, `revoke_key()`
- Full plan-level quota enforcement and consumption tracking

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

[Unreleased]: https://github.com/VecTrade-io/vectrade-python/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/VecTrade-io/vectrade-python/compare/v0.2.0...v1.0.0
[0.2.0]: https://github.com/VecTrade-io/vectrade-python/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/VecTrade-io/vectrade-python/releases/tag/v0.1.0
