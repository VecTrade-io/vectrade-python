"""Tests for webhook verification ensuring HMAC correctness."""

import hashlib
import hmac
import json
import time

import httpx
import pytest
import respx

from vectrade import VecTrade
from vectrade._exceptions import VecTradeError
from vectrade.resources.webhooks import Webhooks


WEBHOOK_SECRET = "whsec_test_secret_key_12345"

SAMPLE_EVENT = {
    "id": "evt_abc123",
    "type": "quote.updated",
    "data": {"symbol": "AAPL", "price": 198.50},
    "created_at": "2026-05-15T12:00:00Z",
}


def _generate_signature(payload: str, timestamp: str, secret: str) -> str:
    """Generate a valid HMAC-SHA256 signature for testing."""
    signed_payload = f"{timestamp}.".encode() + payload.encode()
    return hmac.HMAC(secret.encode(), signed_payload, hashlib.sha256).hexdigest()


class TestWebhookVerify:
    """Test webhook HMAC signature verification."""

    def test_valid_signature(self) -> None:
        """Verifies a correctly signed webhook payload."""
        payload = json.dumps(SAMPLE_EVENT)
        timestamp = str(int(time.time()))
        signature = _generate_signature(payload, timestamp, WEBHOOK_SECRET)

        headers = {
            "x-vq-signature": signature,
            "x-vq-timestamp": timestamp,
        }

        event = Webhooks.verify(payload, headers, WEBHOOK_SECRET)
        assert event.id == "evt_abc123"
        assert event.type == "quote.updated"

    def test_invalid_signature_rejected(self) -> None:
        """Rejects a payload with an incorrect signature."""
        payload = json.dumps(SAMPLE_EVENT)
        timestamp = str(int(time.time()))

        headers = {
            "x-vq-signature": "deadbeef" * 8,
            "x-vq-timestamp": timestamp,
        }

        with pytest.raises(VecTradeError, match="Invalid webhook signature"):
            Webhooks.verify(payload, headers, WEBHOOK_SECRET)

    def test_missing_headers_rejected(self) -> None:
        """Rejects when signature headers are missing."""
        payload = json.dumps(SAMPLE_EVENT)

        with pytest.raises(VecTradeError, match="Missing webhook signature headers"):
            Webhooks.verify(payload, {}, WEBHOOK_SECRET)

    def test_stale_timestamp_rejected(self) -> None:
        """Rejects payload with expired timestamp (replay attack)."""
        payload = json.dumps(SAMPLE_EVENT)
        # 10 minutes ago — outside 5-minute tolerance
        timestamp = str(int(time.time()) - 600)
        signature = _generate_signature(payload, timestamp, WEBHOOK_SECRET)

        headers = {
            "x-vq-signature": signature,
            "x-vq-timestamp": timestamp,
        }

        with pytest.raises(VecTradeError, match="timestamp outside tolerance"):
            Webhooks.verify(payload, headers, WEBHOOK_SECRET)

    def test_payload_bytes_accepted(self) -> None:
        """Accepts payload as bytes (not just str)."""
        payload_str = json.dumps(SAMPLE_EVENT)
        payload_bytes = payload_str.encode()
        timestamp = str(int(time.time()))
        signature = _generate_signature(payload_str, timestamp, WEBHOOK_SECRET)

        headers = {
            "x-vq-signature": signature,
            "x-vq-timestamp": timestamp,
        }

        event = Webhooks.verify(payload_bytes, headers, WEBHOOK_SECRET)
        assert event.id == "evt_abc123"

    def test_tampered_payload_rejected(self) -> None:
        """Rejects a payload that was modified after signing."""
        payload = json.dumps(SAMPLE_EVENT)
        timestamp = str(int(time.time()))
        signature = _generate_signature(payload, timestamp, WEBHOOK_SECRET)

        tampered = json.dumps({**SAMPLE_EVENT, "type": "malicious.event"})
        headers = {
            "x-vq-signature": signature,
            "x-vq-timestamp": timestamp,
        }

        with pytest.raises(VecTradeError, match="Invalid webhook signature"):
            Webhooks.verify(tampered, headers, WEBHOOK_SECRET)


class TestWebhookCRUD:
    """Test webhook subscription CRUD operations."""

    def test_create_webhook(self, client: VecTrade, mock_api: respx.Router) -> None:
        """Creates a webhook subscription."""
        mock_response = {
            "id": "wh_123",
            "url": "https://example.com/webhook",
            "events": ["quote.updated"],
            "description": "Test hook",
            "secret": "whsec_xxx",
            "active": True,
            "created_at": "2026-05-15T12:00:00Z",
        }
        route = mock_api.post("/vq/webhooks").mock(
            return_value=httpx.Response(200, json=mock_response)
        )

        result = client.webhooks.create(
            url="https://example.com/webhook",
            events=["quote.updated"],
            description="Test hook",
        )
        assert route.called
        assert result.id == "wh_123"
        assert result.url == "https://example.com/webhook"

    def test_list_webhooks(self, client: VecTrade, mock_api: respx.Router) -> None:
        """Lists all webhook subscriptions."""
        mock_response = {
            "data": [
                {
                    "id": "wh_123",
                    "url": "https://example.com/webhook",
                    "events": ["quote.updated"],
                    "secret": "whsec_xxx",
                    "active": True,
                    "created_at": "2026-05-15T12:00:00Z",
                }
            ]
        }
        route = mock_api.get("/vq/webhooks").mock(
            return_value=httpx.Response(200, json=mock_response)
        )

        results = client.webhooks.list()
        assert route.called
        assert len(results) == 1
        assert results[0].id == "wh_123"

    def test_delete_webhook(self, client: VecTrade, mock_api: respx.Router) -> None:
        """Deletes a webhook subscription."""
        route = mock_api.delete("/vq/webhooks/wh_123").mock(
            return_value=httpx.Response(204)
        )

        client.webhooks.delete("wh_123")
        assert route.called
