"""Tests for the developer resource."""

import pytest
import respx

from vectrade import VecTrade

BASE_URL = "https://api.vectrade.io/v1"


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> VecTrade:
    monkeypatch.setenv("VECTRADE_API_KEY", "vq_test_abcdefghijklmnop1234")
    c = VecTrade(max_retries=0)
    yield c
    c.close()


class TestDeveloper:
    @respx.mock
    def test_list_keys(self, client: VecTrade) -> None:
        respx.get(f"{BASE_URL}/vq/developer/keys").respond(
            200, json=[{"id": "key-1", "label": "prod", "scopes": ["read"]}]
        )
        keys = client.developer.list_keys()
        assert len(keys) == 1
        assert keys[0]["label"] == "prod"

    @respx.mock
    def test_create_key(self, client: VecTrade) -> None:
        respx.post(f"{BASE_URL}/vq/developer/keys").respond(
            201,
            json={
                "id": "key-new",
                "label": "ci",
                "scopes": ["read"],
                "raw_key": "vq_test_newkey12345678901234",
            },
        )
        key = client.developer.create_key(label="ci", scopes=["read"])
        assert key["id"] == "key-new"

    @respx.mock
    def test_revoke_key(self, client: VecTrade) -> None:
        route = respx.delete(f"{BASE_URL}/vq/developer/keys/key-1").respond(204)
        client.developer.revoke_key("key-1")
        assert route.called

    @respx.mock
    def test_get_usage(self, client: VecTrade) -> None:
        respx.get(f"{BASE_URL}/vq/developer/usage").respond(
            200,
            json={"total_requests": 1500, "quota_remaining": 8500},
        )
        usage = client.developer.get_usage()
        assert usage["total_requests"] == 1500

    @respx.mock
    def test_get_daily_usage(self, client: VecTrade) -> None:
        respx.get(f"{BASE_URL}/vq/developer/usage/daily").respond(
            200,
            json=[{"date": "2026-05-17", "requests": 100}],
        )
        daily = client.developer.get_daily_usage(days=7)
        assert len(daily) == 1

    @respx.mock
    def test_get_plan(self, client: VecTrade) -> None:
        respx.get(f"{BASE_URL}/vq/developer/plan").respond(
            200,
            json={"plan_id": "pro", "plan_name": "Pro", "status": "active"},
        )
        plan = client.developer.get_plan()
        assert plan["plan_name"] == "Pro"

    @respx.mock
    def test_get_quota(self, client: VecTrade) -> None:
        respx.get(f"{BASE_URL}/vq/developer/quota").respond(
            200,
            json={"monthly_quota": 10000, "used": 1500, "remaining": 8500},
        )
        quota = client.developer.get_quota()
        assert quota["remaining"] == 8500
