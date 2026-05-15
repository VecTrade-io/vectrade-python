"""SDK configuration constants and environment variable handling."""

from __future__ import annotations

import logging
import os

logger = logging.getLogger("vectrade")

# Environment variable names
ENV_API_KEY = "VECTRADE_API_KEY"
ENV_BASE_URL = "VECTRADE_BASE_URL"
ENV_SANDBOX = "VECTRADE_SANDBOX"
ENV_TIMEOUT = "VECTRADE_TIMEOUT"
ENV_MAX_RETRIES = "VECTRADE_MAX_RETRIES"

# Default configuration values
DEFAULT_BASE_URL = "https://api.vectrade.io/v1"
# Sandbox uses the same domain — mode is determined by API key prefix (vq_test_ vs vq_live_).
SANDBOX_BASE_URL = DEFAULT_BASE_URL
DEFAULT_TIMEOUT = 60.0
DEFAULT_MAX_RETRIES = 3

# API key format validation
API_KEY_PREFIX_LIVE = "vq_live_"
API_KEY_PREFIX_TEST = "vq_test_"
API_KEY_MIN_LENGTH = 20

# Allowed URL schemes for base URL
_ALLOWED_SCHEMES = ("https://",)


def resolve_base_url(*, base_url: str | None = None, sandbox: bool = False) -> str:
    """Resolve the base URL from explicit value, env, or defaults.

    Priority:
        1. Explicit `base_url` parameter
        2. `VECTRADE_BASE_URL` environment variable
        3. `VECTRADE_SANDBOX` env var (if "true"/"1")
        4. `sandbox` parameter
        5. Default production URL
    """
    resolved: str | None = None

    if base_url:
        resolved = base_url.rstrip("/")
    elif env_base := os.environ.get(ENV_BASE_URL):
        resolved = env_base.rstrip("/")
    elif os.environ.get(ENV_SANDBOX, "").lower() in ("true", "1", "yes"):
        resolved = SANDBOX_BASE_URL
    elif sandbox:
        resolved = SANDBOX_BASE_URL
    else:
        resolved = DEFAULT_BASE_URL

    # Warn if using insecure scheme (allows override for local dev but warns)
    if not any(resolved.startswith(scheme) for scheme in _ALLOWED_SCHEMES):
        logger.warning(
            "VecTrade SDK: base_url uses non-HTTPS scheme (%s). "
            "This is insecure and should only be used for local development.",
            resolved,
        )

    return resolved


def resolve_api_key(api_key: str | None = None) -> str | None:
    """Resolve API key from explicit value or environment."""
    return api_key or os.environ.get(ENV_API_KEY)


def resolve_timeout(timeout: float | None = None) -> float:
    """Resolve timeout from explicit value or environment."""
    if timeout is not None:
        return timeout

    env_timeout = os.environ.get(ENV_TIMEOUT)
    if env_timeout:
        try:
            return float(env_timeout)
        except ValueError:
            pass

    return DEFAULT_TIMEOUT


def resolve_max_retries(max_retries: int | None = None) -> int:
    """Resolve max retries from explicit value or environment."""
    if max_retries is not None:
        return max_retries

    env_retries = os.environ.get(ENV_MAX_RETRIES)
    if env_retries:
        try:
            return int(env_retries)
        except ValueError:
            pass

    return DEFAULT_MAX_RETRIES
