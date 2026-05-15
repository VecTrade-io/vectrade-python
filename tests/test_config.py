"""Tests for configuration resolution logic."""

import pytest

from vectrade._utils.config import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
    SANDBOX_BASE_URL,
    resolve_api_key,
    resolve_base_url,
    resolve_max_retries,
    resolve_timeout,
)


class TestResolveApiKey:
    """Test API key resolution priority."""

    def test_explicit_key(self) -> None:
        """Explicit key is returned directly."""
        assert resolve_api_key("vq_test_explicit") == "vq_test_explicit"

    def test_from_environment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Falls back to environment variable."""
        monkeypatch.setenv("VECTRADE_API_KEY", "vq_test_from_env")
        assert resolve_api_key() == "vq_test_from_env"

    def test_explicit_overrides_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Explicit value takes precedence over env."""
        monkeypatch.setenv("VECTRADE_API_KEY", "vq_test_env")
        assert resolve_api_key("vq_test_explicit") == "vq_test_explicit"

    def test_returns_none_when_missing(self) -> None:
        """Returns None when no key is available."""
        assert resolve_api_key() is None


class TestResolveBaseUrl:
    """Test base URL resolution priority."""

    def test_default_is_production(self) -> None:
        """Default URL is production."""
        assert resolve_base_url() == DEFAULT_BASE_URL

    def test_explicit_url(self) -> None:
        """Explicit URL is used directly."""
        assert resolve_base_url(base_url="https://custom.io/v1") == "https://custom.io/v1"

    def test_strips_trailing_slash(self) -> None:
        """Trailing slash is stripped."""
        assert resolve_base_url(base_url="https://custom.io/v1/") == "https://custom.io/v1"

    def test_sandbox_flag(self) -> None:
        """Sandbox flag sets sandbox URL."""
        assert resolve_base_url(sandbox=True) == SANDBOX_BASE_URL

    def test_env_base_url(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """VECTRADE_BASE_URL env var takes precedence over sandbox."""
        monkeypatch.setenv("VECTRADE_BASE_URL", "https://env-custom.io/v1")
        assert resolve_base_url(sandbox=True) == "https://env-custom.io/v1"

    def test_env_sandbox(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """VECTRADE_SANDBOX env var activates sandbox."""
        monkeypatch.setenv("VECTRADE_SANDBOX", "true")
        assert resolve_base_url() == SANDBOX_BASE_URL

    def test_env_sandbox_values(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """VECTRADE_SANDBOX accepts various truthy values."""
        for val in ("true", "1", "yes", "True", "YES"):
            monkeypatch.setenv("VECTRADE_SANDBOX", val)
            assert resolve_base_url() == SANDBOX_BASE_URL

    def test_explicit_overrides_all(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Explicit base_url overrides everything."""
        monkeypatch.setenv("VECTRADE_BASE_URL", "https://env.io/v1")
        monkeypatch.setenv("VECTRADE_SANDBOX", "true")
        assert resolve_base_url(base_url="https://explicit.io/v1") == "https://explicit.io/v1"


class TestResolveTimeout:
    """Test timeout resolution."""

    def test_default(self) -> None:
        assert resolve_timeout() == DEFAULT_TIMEOUT

    def test_explicit(self) -> None:
        assert resolve_timeout(120.0) == 120.0

    def test_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("VECTRADE_TIMEOUT", "45")
        assert resolve_timeout() == 45.0

    def test_invalid_env_uses_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("VECTRADE_TIMEOUT", "invalid")
        assert resolve_timeout() == DEFAULT_TIMEOUT


class TestResolveMaxRetries:
    """Test max retries resolution."""

    def test_default(self) -> None:
        assert resolve_max_retries() == DEFAULT_MAX_RETRIES

    def test_explicit(self) -> None:
        assert resolve_max_retries(5) == 5

    def test_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("VECTRADE_MAX_RETRIES", "10")
        assert resolve_max_retries() == 10

    def test_explicit_zero(self) -> None:
        """Zero retries disables retry."""
        assert resolve_max_retries(0) == 0
