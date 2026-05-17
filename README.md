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

## Quick Start

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
from vectrade import VecTrade, RateLimitError, AuthenticationError, NotFoundError

try:
    quote = vt.quotes.get("INVALID")
except NotFoundError as e:
    print(f"Symbol not found: {e}")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after}s")
except AuthenticationError as e:
    print(f"Bad API key: {e}")
```

All exceptions include `request_id` and `status_code` for debugging.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release history.

## License

MIT — see [LICENSE](LICENSE).
