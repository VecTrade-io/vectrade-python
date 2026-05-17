# Contributing to VecTrade Python SDK

Thank you for your interest in contributing! Here's how to get started.

## Development Setup

```bash
git clone https://github.com/VecTrade-io/vectrade-python.git
cd vectrade-python
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

## Running Tests

```bash
pytest tests/ -v
```

## Code Quality

We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting, and [mypy](https://mypy-lang.org/) for type checking:

```bash
ruff check src/ tests/
ruff format src/ tests/
mypy src/
```

## Pull Request Process

1. Fork the repository and create a feature branch from `main`.
2. Write tests for any new functionality.
3. Ensure all tests pass and linting is clean.
4. Update `CHANGELOG.md` under an `[Unreleased]` section.
5. Submit a PR with a clear description of the change.

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat: add new resource`
- `fix: correct field mapping`
- `docs: update README examples`
- `test: add coverage for edge case`

## Code Style

- Target Python 3.9+ compatibility
- Use type annotations everywhere
- Follow existing patterns in `src/vectrade/resources/`
- Keep dependencies minimal (httpx + pydantic only for core)

## Reporting Issues

Use [GitHub Issues](https://github.com/VecTrade-io/vectrade-python/issues) with:
- SDK version (`pip show vectrade`)
- Python version
- Minimal reproduction code
- Expected vs actual behavior

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
