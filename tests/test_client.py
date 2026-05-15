"""Tests for client initialization, configuration, and error handling."""

import pytest

from vectrade import (
    VecTrade,
    AsyncVecTrade,
    ConfigurationError,
    VecTradeError,
)
from vectrade._utils.config import DEFAULT_BASE_URL, SANDBOX_BASE_URL


class TestClientInit:
    """Test client initialization behavior."""

    def test_raises_without_api_key(self) -> None:
        """Client raises ConfigurationError when no API key is provided."""
        with pytest.raises(ConfigurationError, match="api_key is required"):
            VecTrade()

    def test_reads_from_env(self, monkeypatch: pytest.MonkeyPatch, api_key: str) -> None:
        """Client reads API key from VECTRADE_API_KEY environment variable."""
        monkeypatch.setenv("VECTRADE_API_KEY", api_key)
        client = VecTrade()
        assert client.api_key == api_key
        client.close()

    def test_explicit_key_overrides_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Explicit api_key parameter takes precedence over env var."""
        monkeypatch.setenv("VECTRADE_API_KEY", "vq_test_env_key_12345")
        client = VecTrade(api_key="vq_test_explicit_key12345")
        assert client.api_key == "vq_test_explicit_key12345"
        client.close()

    def test_default_base_url(self, monkeypatch: pytest.MonkeyPatch, api_key: str) -> None:
        """Default base URL is production."""
        monkeypatch.setenv("VECTRADE_API_KEY", api_key)
        client = VecTrade()
        assert client.base_url == DEFAULT_BASE_URL
        client.close()

    def test_sandbox_mode(self, monkeypatch: pytest.MonkeyPatch, api_key: str) -> None:
        """Sandbox mode sets the correct base URL."""
        monkeypatch.setenv("VECTRADE_API_KEY", api_key)
        client = VecTrade(sandbox=True)
        assert client.base_url == SANDBOX_BASE_URL
        client.close()

    def test_sandbox_env_var(self, monkeypatch: pytest.MonkeyPatch, api_key: str) -> None:
        """VECTRADE_SANDBOX env var activates sandbox."""
        monkeypatch.setenv("VECTRADE_API_KEY", api_key)
        monkeypatch.setenv("VECTRADE_SANDBOX", "true")
        client = VecTrade()
        assert client.base_url == SANDBOX_BASE_URL
        client.close()

    def test_custom_base_url(self, monkeypatch: pytest.MonkeyPatch, api_key: str) -> None:
        """Custom base URL is respected."""
        monkeypatch.setenv("VECTRADE_API_KEY", api_key)
        client = VecTrade(base_url="https://custom.api.com/v1")
        assert client.base_url == "https://custom.api.com/v1"
        client.close()

    def test_base_url_strips_trailing_slash(self, monkeypatch: pytest.MonkeyPatch, api_key: str) -> None:
        """Trailing slashes are stripped from base URL."""
        monkeypatch.setenv("VECTRADE_API_KEY", api_key)
        client = VecTrade(base_url="https://custom.api.com/v1/")
        assert client.base_url == "https://custom.api.com/v1"
        client.close()

    def test_custom_timeout(self, monkeypatch: pytest.MonkeyPatch, api_key: str) -> None:
        """Custom timeout is respected."""
        monkeypatch.setenv("VECTRADE_API_KEY", api_key)
        client = VecTrade(timeout=120.0)
        assert client.timeout == 120.0
        client.close()

    def test_timeout_from_env(self, monkeypatch: pytest.MonkeyPatch, api_key: str) -> None:
        """Timeout from VECTRADE_TIMEOUT env var."""
        monkeypatch.setenv("VECTRADE_API_KEY", api_key)
        monkeypatch.setenv("VECTRADE_TIMEOUT", "90")
        client = VecTrade()
        assert client.timeout == 90.0
        client.close()

    def test_max_retries(self, monkeypatch: pytest.MonkeyPatch, api_key: str) -> None:
        """Custom max_retries is respected."""
        monkeypatch.setenv("VECTRADE_API_KEY", api_key)
        client = VecTrade(max_retries=5)
        assert client.max_retries == 5
        client.close()


class TestClientRepr:
    """Test client string representation."""

    def test_repr_masks_api_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Repr never exposes the full API key."""
        monkeypatch.setenv("VECTRADE_API_KEY", "vq_test_secretkey1234567890")
        client = VecTrade()
        repr_str = repr(client)
        assert "vq_test" in repr_str
        assert "secretkey1234567890" not in repr_str
        assert "..." in repr_str
        client.close()


class TestClientContextManager:
    """Test context manager behavior."""

    def test_sync_context_manager(self, monkeypatch: pytest.MonkeyPatch, api_key: str) -> None:
        """Client works as a sync context manager."""
        monkeypatch.setenv("VECTRADE_API_KEY", api_key)
        with VecTrade() as client:
            assert client.api_key == api_key

    @pytest.mark.anyio
    async def test_async_context_manager(self, monkeypatch: pytest.MonkeyPatch, api_key: str) -> None:
        """Client works as an async context manager."""
        monkeypatch.setenv("VECTRADE_API_KEY", api_key)
        async with AsyncVecTrade() as client:
            assert client.api_key == api_key


class TestClientResources:
    """Test resource namespace initialization."""

    def test_all_resources_available(self, monkeypatch: pytest.MonkeyPatch, api_key: str) -> None:
        """All API resource namespaces are available on the client."""
        monkeypatch.setenv("VECTRADE_API_KEY", api_key)
        client = VecTrade()
        assert hasattr(client, "quotes")
        assert hasattr(client, "fundamentals")
        assert hasattr(client, "technicals")
        assert hasattr(client, "news")
        assert hasattr(client, "screener")
        assert hasattr(client, "ai")
        assert hasattr(client, "webhooks")
        client.close()

    def test_async_all_resources_available(self, monkeypatch: pytest.MonkeyPatch, api_key: str) -> None:
        """All API resource namespaces are available on the async client."""
        monkeypatch.setenv("VECTRADE_API_KEY", api_key)
        client = AsyncVecTrade()
        assert hasattr(client, "quotes")
        assert hasattr(client, "fundamentals")
        assert hasattr(client, "technicals")
        assert hasattr(client, "news")
        assert hasattr(client, "screener")
        assert hasattr(client, "ai")
        assert hasattr(client, "webhooks")


class TestAsyncClientRequest:
    """Test async client request method with retry logic."""

    @pytest.mark.anyio
    async def test_async_request_has_method(self, monkeypatch: pytest.MonkeyPatch, api_key: str) -> None:
        """AsyncVecTrade exposes a request method."""
        monkeypatch.setenv("VECTRADE_API_KEY", api_key)
        async with AsyncVecTrade() as client:
            assert hasattr(client, "request")
            assert callable(client.request)

    @pytest.mark.anyio
    async def test_async_request_idempotency_key(self, monkeypatch: pytest.MonkeyPatch, api_key: str) -> None:
        """AsyncVecTrade.request() supports idempotency_key parameter."""
        import inspect

        monkeypatch.setenv("VECTRADE_API_KEY", api_key)
        async with AsyncVecTrade() as client:
            sig = inspect.signature(client.request)
            assert "idempotency_key" in sig.parameters
