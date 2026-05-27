"""Profile resource — company profile information."""

from __future__ import annotations

from typing import TYPE_CHECKING

from vectrade._utils.encoding import encode_path_param
from vectrade.types.profile import ProfileResponse

if TYPE_CHECKING:
    from vectrade._http_wrapper import AsyncHTTP, SyncHTTP


class Profile:
    """Synchronous profile resource."""

    def __init__(self, http: SyncHTTP) -> None:
        self._http = http

    def get(self, symbol: str) -> ProfileResponse:
        """Get company profile (sector, industry, description, location).

        Args:
            symbol: Stock ticker symbol (e.g., "AAPL").

        Returns:
            ProfileResponse with company information.
        """
        response = self._http.get(f"/vq/profile/{encode_path_param(symbol)}")
        return ProfileResponse.model_validate(response.json())


class AsyncProfile:
    """Asynchronous profile resource."""

    def __init__(self, http: AsyncHTTP) -> None:
        self._http = http

    async def get(self, symbol: str) -> ProfileResponse:
        """Get company profile (sector, industry, description, location)."""
        response = await self._http.get(f"/vq/profile/{encode_path_param(symbol)}")
        return ProfileResponse.model_validate(response.json())
