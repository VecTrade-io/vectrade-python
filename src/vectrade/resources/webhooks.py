"""Webhooks resource — manage and verify webhook subscriptions."""

from __future__ import annotations

import hashlib
import hmac
import time
from typing import TYPE_CHECKING, Any

from vectrade._exceptions import VecTradeError
from vectrade._utils.encoding import encode_path_param
from vectrade.types.webhook import WebhookEvent, WebhookSubscription

if TYPE_CHECKING:
    from vectrade._http_wrapper import AsyncHTTP, SyncHTTP

SIGNATURE_HEADER = "x-vq-signature"
TIMESTAMP_HEADER = "x-vq-timestamp"
TOLERANCE_SECONDS = 300  # 5 minutes


class Webhooks:
    """Synchronous webhooks resource."""

    def __init__(self, http: SyncHTTP) -> None:
        self._http = http

    def create(
        self, *, url: str, events: list[str], description: str | None = None
    ) -> WebhookSubscription:
        """Create a webhook subscription."""
        body: dict[str, Any] = {"url": url, "events": events}
        if description:
            body["description"] = description
        response = self._http.post("/vq/webhooks", json=body)
        return WebhookSubscription.model_validate(response.json())

    def list(self) -> list[WebhookSubscription]:
        """List all webhook subscriptions."""
        response = self._http.get("/vq/webhooks")
        return [WebhookSubscription.model_validate(item) for item in response.json()["data"]]

    def delete(self, webhook_id: str) -> None:
        """Delete a webhook subscription."""
        self._http.delete(f"/vq/webhooks/{encode_path_param(webhook_id)}")

    @staticmethod
    def verify(payload: str | bytes, headers: dict[str, str], secret: str) -> WebhookEvent:
        """Verify a webhook signature and return the parsed event.

        Args:
            payload: Raw request body.
            headers: Request headers.
            secret: Webhook signing secret.

        Returns:
            Parsed WebhookEvent.

        Raises:
            VecTradeError: If signature is invalid or timestamp is stale.
        """
        signature = headers.get(SIGNATURE_HEADER)
        timestamp = headers.get(TIMESTAMP_HEADER)

        if not signature or not timestamp:
            raise VecTradeError("Missing webhook signature headers")

        # Check timestamp tolerance
        ts = int(timestamp)
        now = int(time.time())
        if abs(now - ts) > TOLERANCE_SECONDS:
            raise VecTradeError("Webhook timestamp outside tolerance window")

        # Verify HMAC-SHA256
        if isinstance(payload, str):
            payload_bytes = payload.encode()
        else:
            payload_bytes = payload

        signed_payload = f"{timestamp}.".encode() + payload_bytes
        expected = hmac.HMAC(secret.encode(), signed_payload, hashlib.sha256).hexdigest()

        if not hmac.compare_digest(signature, expected):
            raise VecTradeError("Invalid webhook signature")

        import json

        return WebhookEvent.model_validate(json.loads(payload_bytes))


class AsyncWebhooks:
    """Asynchronous webhooks resource."""

    def __init__(self, http: AsyncHTTP) -> None:
        self._http = http

    async def create(
        self, *, url: str, events: list[str], description: str | None = None
    ) -> WebhookSubscription:
        body: dict[str, Any] = {"url": url, "events": events}
        if description:
            body["description"] = description
        response = await self._http.post("/vq/webhooks", json=body)
        return WebhookSubscription.model_validate(response.json())

    async def list(self) -> list[WebhookSubscription]:
        response = await self._http.get("/vq/webhooks")
        return [WebhookSubscription.model_validate(item) for item in response.json()["data"]]

    async def delete(self, webhook_id: str) -> None:
        await self._http.delete(f"/vq/webhooks/{encode_path_param(webhook_id)}")

    verify = Webhooks.verify  # Static method shared
