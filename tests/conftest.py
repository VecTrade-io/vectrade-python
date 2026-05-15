"""Shared test fixtures for VecTrade SDK tests."""

import pytest
import respx

from vectrade import VecTrade

BASE_URL = "https://api.vectrade.io/v1"


@pytest.fixture
def api_key() -> str:
    """Standard test API key."""
    return "vq_test_abcdefghijklmnop1234"


@pytest.fixture
def sandbox_url() -> str:
    return "https://sandbox.vectrade.io/api/v1"


@pytest.fixture
def production_url() -> str:
    return BASE_URL


@pytest.fixture
def mock_api():
    """Respx router with base_url pre-configured for the VecTrade API."""
    with respx.mock(base_url=BASE_URL) as respx_mock:
        yield respx_mock


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch, api_key: str) -> VecTrade:
    """Pre-configured VecTrade client for resource tests."""
    monkeypatch.setenv("VECTRADE_API_KEY", api_key)
    c = VecTrade()
    yield c
    c.close()


@pytest.fixture(autouse=True)
def _clear_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure no env vars leak between tests."""
    monkeypatch.delenv("VECTRADE_API_KEY", raising=False)
    monkeypatch.delenv("VECTRADE_BASE_URL", raising=False)
    monkeypatch.delenv("VECTRADE_SANDBOX", raising=False)
    monkeypatch.delenv("VECTRADE_TIMEOUT", raising=False)
    monkeypatch.delenv("VECTRADE_MAX_RETRIES", raising=False)
