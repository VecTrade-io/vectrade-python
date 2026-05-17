"""Developer self-service resource — key management, usage, and quota."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import httpx


class Developer:
    """Developer self-service endpoints.

    These endpoints manage API keys, view usage, and check quota.

    Note: These endpoints require JWT authentication (session token),
    not API key authentication. Use ``base_url`` pointing to your
    VecTrade instance and ensure the client is authenticated via
    a session token or API key with developer scope.
    """

    def __init__(self, http: httpx.Client) -> None:
        self._http = http

    def list_keys(self) -> list[dict[str, Any]]:
        """List all API keys for the authenticated user.

        Returns:
            List of API key metadata (prefix, label, scopes, created_at).
            The raw key value is never returned.
        """
        response = self._http.get("/vq/developer/keys")
        response.raise_for_status()
        return response.json()

    def create_key(self, *, label: str, scopes: list[str] | None = None) -> dict[str, Any]:
        """Create a new API key.

        The raw key (``vq_...``) is returned **only once** in the response.
        Store it securely — it cannot be retrieved again.

        Args:
            label: Human-readable label for the key.
            scopes: Optional list of permission scopes.

        Returns:
            Dict with ``id``, ``key_prefix``, ``label``, ``scopes``,
            ``raw_key``, and ``created_at``.
        """
        body: dict[str, Any] = {"label": label}
        if scopes is not None:
            body["scopes"] = scopes
        response = self._http.post("/vq/developer/keys", json=body)
        response.raise_for_status()
        return response.json()

    def revoke_key(self, key_id: str) -> None:
        """Permanently revoke an API key.

        The key is deactivated immediately. This action cannot be undone.

        Args:
            key_id: UUID of the key to revoke.
        """
        response = self._http.delete(f"/vq/developer/keys/{key_id}")
        response.raise_for_status()

    def get_usage(self) -> dict[str, Any]:
        """Get aggregated API usage for the current billing period.

        Returns:
            Dict with ``period``, ``total_requests``, ``ai_requests``,
            ``error_count``, ``tokens_used``, ``quota_limit``, ``quota_remaining``.
        """
        response = self._http.get("/vq/developer/usage")
        response.raise_for_status()
        return response.json()

    def get_daily_usage(self, *, days: int = 30) -> list[dict[str, Any]]:
        """Get per-day, per-endpoint usage breakdown.

        Args:
            days: Number of days to look back (max 90).

        Returns:
            List of daily usage records.
        """
        response = self._http.get("/vq/developer/usage/daily", params={"days": str(min(days, 90))})
        response.raise_for_status()
        return response.json()

    def get_plan(self) -> dict[str, Any]:
        """Get the user's active subscription details.

        Returns:
            Dict with ``plan_id``, ``plan_name``, ``status``,
            ``current_period_start``, ``current_period_end``.
        """
        response = self._http.get("/vq/developer/plan")
        response.raise_for_status()
        return response.json()

    def get_quota(self) -> dict[str, Any]:
        """Check remaining API and token quota for the current billing period.

        Returns:
            Dict with ``plan_id``, ``monthly_quota``, ``used``, ``remaining``,
            ``overage_policy``, ``reset_at``.
        """
        response = self._http.get("/vq/developer/quota")
        response.raise_for_status()
        return response.json()


class AsyncDeveloper:
    """Asynchronous developer self-service endpoints."""

    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def list_keys(self) -> list[dict[str, Any]]:
        response = await self._http.get("/vq/developer/keys")
        response.raise_for_status()
        return response.json()

    async def create_key(self, *, label: str, scopes: list[str] | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {"label": label}
        if scopes is not None:
            body["scopes"] = scopes
        response = await self._http.post("/vq/developer/keys", json=body)
        response.raise_for_status()
        return response.json()

    async def revoke_key(self, key_id: str) -> None:
        response = await self._http.delete(f"/vq/developer/keys/{key_id}")
        response.raise_for_status()

    async def get_usage(self) -> dict[str, Any]:
        response = await self._http.get("/vq/developer/usage")
        response.raise_for_status()
        return response.json()

    async def get_daily_usage(self, *, days: int = 30) -> list[dict[str, Any]]:
        response = await self._http.get(
            "/vq/developer/usage/daily", params={"days": str(min(days, 90))}
        )
        response.raise_for_status()
        return response.json()

    async def get_plan(self) -> dict[str, Any]:
        response = await self._http.get("/vq/developer/plan")
        response.raise_for_status()
        return response.json()

    async def get_quota(self) -> dict[str, Any]:
        response = await self._http.get("/vq/developer/quota")
        response.raise_for_status()
        return response.json()
