"""Options resource — options chain data."""

from __future__ import annotations

from typing import TYPE_CHECKING

from vectrade._utils.encoding import encode_path_param
from vectrade.types.options import OptionsChain

if TYPE_CHECKING:
    import httpx


class Options:
    """Synchronous options resource."""

    def __init__(self, http: httpx.Client) -> None:
        self._http = http

    def chain(
        self,
        symbol: str,
        *,
        expiration: str | None = None,
        option_type: str | None = None,
    ) -> OptionsChain:
        """Get the options chain for a symbol.

        Args:
            symbol: Underlying stock ticker symbol.
            expiration: Filter by expiration date (YYYY-MM-DD).
            option_type: Filter by type ("call" or "put").

        Returns:
            OptionsChain with available contracts.
        """
        params: dict[str, str] = {}
        if expiration:
            params["expiration"] = expiration
        if option_type:
            params["type"] = option_type

        response = self._http.get(f"/vq/options/{encode_path_param(symbol)}", params=params)
        response.raise_for_status()
        return OptionsChain.model_validate(response.json())

    def expirations(self, symbol: str) -> list[str]:
        """Get available expiration dates for a symbol.

        Args:
            symbol: Underlying stock ticker symbol.

        Returns:
            List of expiration dates as ISO date strings.
        """
        response = self._http.get(f"/vq/options/{encode_path_param(symbol)}/expirations")
        response.raise_for_status()
        return response.json()["data"]


class AsyncOptions:
    """Asynchronous options resource."""

    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def chain(
        self,
        symbol: str,
        *,
        expiration: str | None = None,
        option_type: str | None = None,
    ) -> OptionsChain:
        """Get the options chain for a symbol."""
        params: dict[str, str] = {}
        if expiration:
            params["expiration"] = expiration
        if option_type:
            params["type"] = option_type

        response = await self._http.get(f"/vq/options/{encode_path_param(symbol)}", params=params)
        response.raise_for_status()
        return OptionsChain.model_validate(response.json())

    async def expirations(self, symbol: str) -> list[str]:
        """Get available expiration dates for a symbol."""
        response = await self._http.get(f"/vq/options/{encode_path_param(symbol)}/expirations")
        response.raise_for_status()
        return response.json()["data"]
