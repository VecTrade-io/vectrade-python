# VecTrade Python SDK

[![CI](https://github.com/VecTrade-io/vectrade-python/actions/workflows/ci.yml/badge.svg)](https://github.com/VecTrade-io/vectrade-python/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/vectrade)](https://pypi.org/project/vectrade/)
[![codecov](https://codecov.io/gh/VecTrade-io/vectrade-python/branch/main/graph/badge.svg)](https://codecov.io/gh/VecTrade-io/vectrade-python)
[![License](https://img.shields.io/github/license/VecTrade-io/vectrade-python)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

Official Python SDK for the [VecTrade](https://vectrade.io) financial data and AI platform.

## Features

- **Sync & Async** — both `VecTrade` and `AsyncVecTrade` clients
- **Streaming AI** — generator-based streaming analysis
- **Type-safe** — Pydantic response models, mypy strict
- **Resilient** — automatic retries with exponential backoff
- **Minimal deps** — httpx + pydantic only

## Installation

```bash
pip install vectrade
```

With optional extras:

```bash
pip install "vectrade[pandas]"       # DataFrame support
pip install "vectrade[telemetry]"    # OpenTelemetry tracing
```

## Authentication

All API requests require a valid API key passed via the `X-API-Key` header. The SDK handles this automatically.

### Getting Your API Key

1. Sign up at [vectrade.io/register](https://vectrade.io/register) (free tier includes 10,000 requests/month)
2. Navigate to [Developer Dashboard](https://vectrade.io/vtrade/developer) to view/create keys
3. Keys follow the format `vq_<random>` (e.g., `vq_xS42eF9Pa9ZOD3MRwuszYf5tTmdrEP7...`)

### Configuring the SDK

```python
import os
from vectrade import VecTrade

# Option 1: Environment variable (recommended)
os.environ["VECTRADE_API_KEY"] = "vq_live_..."
vt = VecTrade()  # auto-reads VECTRADE_API_KEY

# Option 2: Explicit parameter
vt = VecTrade(api_key="vq_live_...")
```

> **Security:** Never hardcode API keys in source code. Use environment variables or a secrets manager.

### Plan Limits & Enforcement

Each API key is bound to a subscription plan with the following enforced limits:

| Limit | Free | Standard | Professional |
|-------|------|----------|--------------|
| API calls/month | 10,000 | 100,000 | 500,000 |
| Requests/minute (RPM) | 20 | 120 | 300 |
| Requests/second (RPS) | 2 | 10 | 25 |
| Monthly tokens | — | 1,000,000 | 5,000,000 |
| AI prompts/day | 5 | Unlimited | Unlimited |
| API keys | 1 | 5 | 20 |
| Key scopes | ✓ | ✓ | ✓ |

When a limit is exceeded, the API returns a `429` status with a descriptive error body.

### Error Responses for Auth Issues

| Scenario | HTTP Status | SDK Exception |
|----------|------------|---------------|
| Missing API key | 401 | `AuthenticationError` |
| Invalid/expired/revoked key | 403 | `AuthenticationError` |
| Monthly quota exceeded | 429 | `QuotaExceededError` |
| Token quota exceeded | 429 | `QuotaExceededError` |
| RPM/RPS rate limit exceeded | 429 | `RateLimitError` |
| AI access denied (plan) | 403 | `PaymentRequiredError` |
| Scope denied (key restriction) | 403 | `AuthenticationError` |

## Quick Start

> **Prerequisite:** You need a VecTrade API key. See [Authentication](#authentication) below.

```python
from vectrade import VecTrade

vt = VecTrade()  # reads VECTRADE_API_KEY from env

# Real-time quote
quote = vt.quotes.get("AAPL")
print(f"{quote.symbol}: ${quote.price}")

# Stream AI analysis
for chunk in vt.ai.stream("Analyze AAPL for long-term hold"):
    print(chunk.text, end="")
```

## Async Usage

```python
from vectrade import AsyncVecTrade

async with AsyncVecTrade() as vt:
    quote = await vt.quotes.get("AAPL")
```

## Available Resources

| Resource | Description |
|----------|-------------|
| `client.quotes` | Real-time and historical price quotes |
| `client.fundamentals` | Financial statements, ratios, company profiles |
| `client.technicals` | Technical indicators (RSI, MACD, Bollinger, etc.) |
| `client.news` | Market news and sentiment |
| `client.earnings` | Earnings reports and estimates |
| `client.analyst` | Analyst ratings and price targets |
| `client.insider` | Insider trading activity |
| `client.options` | Options chains and Greeks |
| `client.screener` | Stock screener with pagination |
| `client.webhooks` | Webhook management for real-time alerts |
| `client.developer` | API key and usage management |
| `client.ai` | AI-powered streaming analysis |

## Configuration

```python
vt = VecTrade(
    api_key="vq_live_...",       # or set VECTRADE_API_KEY
    sandbox=True,                # use sandbox environment
    timeout=60.0,                # request timeout (seconds)
    max_retries=3,               # retry on 429/5xx
)
```

## Error Handling

The SDK raises typed exceptions for all API errors:

```python
from vectrade import (
    VecTrade,
    AuthenticationError,
    RateLimitError,
    QuotaExceededError,
    NotFoundError,
    PaymentRequiredError,
)

vt = VecTrade()

try:
    quote = vt.quotes.get("AAPL")
except AuthenticationError as e:
    # 401: missing key, 403: invalid/expired/revoked key or scope denied
    print(f"Auth failed ({e.status_code}): {e.message}")
except QuotaExceededError as e:
    # 429: monthly request or token quota exhausted
    print(f"Quota exceeded: {e.message}")
except RateLimitError as e:
    # 429: RPM or RPS burst limit hit
    print(f"Rate limited. Retry after {e.retry_after}s")
except PaymentRequiredError as e:
    # 402/403: feature not available on current plan (e.g., AI access)
    print(f"Upgrade required: {e.message}")
except NotFoundError as e:
    # 404: resource not found
    print(f"Not found: {e.message}")
```

All exceptions include `status_code`, `message`, and `request_id` for debugging.

## Developer Self-Service

Manage your API keys and monitor usage programmatically:

```python
# Check your plan and quota
plan = vt.developer.get_plan()
print(f"Plan: {plan.plan_name}, Quota: {plan.monthly_quota}")

quota = vt.developer.get_quota()
print(f"Used: {quota.used}/{quota.monthly_quota} ({quota.usage_pct}%)")

# Manage API keys
keys = vt.developer.list_keys()
new_key = vt.developer.create_key(label="production", scopes="quotes,options")
vt.developer.revoke_key(key_id=new_key.id)
```

## Pagination

Use the built-in pagination helpers for list endpoints:

```python
# Screener with pagination
results = vt.screener.filter(
    market_cap_min=1_000_000_000,
    sector="Technology",
    limit=50,
    offset=0,
)
```

## Rate Limits

The SDK automatically handles rate limiting with exponential backoff. You can also check your limits:

```python
quota = vt.developer.get_quota()
print(f"Remaining: {quota.remaining} requests this period")
```

## Documentation

Full documentation is available at [docs.vectrade.io/sdks/python](https://docs.vectrade.io/sdks/python).

- [API Reference](https://docs.vectrade.io/api-reference/overview)
- [Authentication Guide](https://docs.vectrade.io/guides/authentication)
- [Error Handling](https://docs.vectrade.io/guides/error-handling)
- [Streaming Guide](https://docs.vectrade.io/guides/streaming)
- [Examples](examples/) — runnable scripts for common use cases

## Versioning

This SDK follows [Semantic Versioning](https://semver.org/):

- **MAJOR** — breaking changes to public API
- **MINOR** — new features, backward-compatible
- **PATCH** — bug fixes, backward-compatible

Pre-1.0 releases may include breaking changes in MINOR versions. Pin your dependency accordingly:

```toml
# pyproject.toml
dependencies = ["vectrade>=0.1,<0.2"]
```

## Requirements

- Python 3.9+
- No system dependencies — pure Python

## Community

- 💬 [Discord](https://discord.gg/vectrade) — Get help, share projects, discuss features
- 📖 [Documentation](https://docs.vectrade.io) — Full API reference and guides
- 🧰 [finkit](https://github.com/VecTrade-io/finkit) — Open-source indicators & risk metrics (no API key needed)
- 🤖 [MCP Server](https://github.com/VecTrade-io/vectrade-mcp) — Use VecTrade tools in Claude, Cursor, VS Code

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release history.

## License

MIT — see [LICENSE](LICENSE).
