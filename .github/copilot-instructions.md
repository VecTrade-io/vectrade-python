# VecTrade Python SDK — Copilot Instructions

## Workflow

All agents follow the standard workflow defined in `instructions/agent-workflow.instructions.md`:
**Implement → Verify → Changelog → Commit**

## Agents

| Agent | When to Use |
|-------|------------|
| `@vt-sdk-dev` | Implementing/fixing SDK methods |
| `@vt-sdk-tester` | Writing/fixing tests |

## Conventions

- Python 3.9+ compatible
- httpx for HTTP (sync + async)
- Pydantic v2 for models (strict mode)
- Full type annotations (mypy strict)
- Google-style docstrings
- Resource-based client: `client.quotes.get("AAPL")`

## Build & Test

```bash
pip install -e ".[dev]"    # Install with dev deps
pytest                     # Run tests
pytest --cov               # With coverage
ruff check .               # Lint
mypy src/                  # Type check
```

## Release

Version managed in `pyproject.toml`. Published to PyPI on tag push.
