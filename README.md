# VecTrade Python SDK

[![License](https://img.shields.io/github/license/VecTrade-io/vectrade-python)](LICENSE) [![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

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

## Configuration

```python
vt = VecTrade(
    api_key="vq_live_...",       # or set VECTRADE_API_KEY
    sandbox=True,                # use sandbox environment
    timeout=60.0,                # request timeout (seconds)
    max_retries=3,               # retry on 429/5xx
)
```

## License

MIT — see [LICENSE](LICENSE).
