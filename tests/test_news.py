"""Tests for the news resource."""

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


class TestNews:
    @respx.mock
    def test_list_news(self, client: VecTrade) -> None:
        respx.get(f"{BASE_URL}/vq/news/AAPL").respond(
            200,
            json={
                "articles": [
                    {
                        "uuid": "abc-123",
                        "headline": "Apple hits record",
                        "summary": "AAPL surges.",
                        "url": "https://example.com/1",
                        "source": "Reuters",
                        "datetime": "2026-05-17T10:00:00Z",
                        "related": ["AAPL"],
                        "type": "technology",
                        "image": "https://example.com/img.jpg",
                    },
                    {
                        "uuid": "def-456",
                        "headline": "Tech rally continues",
                        "url": "https://example.com/2",
                        "source": "Bloomberg",
                        "datetime": "2026-05-17T09:00:00Z",
                    },
                ]
            },
        )
        articles = client.news.list("AAPL")
        assert len(articles) == 2
        assert articles[0].id == "abc-123"
        assert articles[0].title == "Apple hits record"
        assert articles[0].symbols == ["AAPL"]
        assert articles[0].category == "technology"
        assert articles[0].image_url == "https://example.com/img.jpg"

    @respx.mock
    def test_list_with_limit(self, client: VecTrade) -> None:
        respx.get(f"{BASE_URL}/vq/news/AAPL").respond(
            200,
            json={
                "articles": [
                    {
                        "uuid": f"id-{i}",
                        "headline": f"Article {i}",
                        "url": f"https://example.com/{i}",
                        "source": "Reuters",
                        "datetime": "2026-05-17T10:00:00Z",
                    }
                    for i in range(10)
                ]
            },
        )
        articles = client.news.list("AAPL", limit=3)
        assert len(articles) == 3

    @respx.mock
    def test_get_delegates_to_list(self, client: VecTrade) -> None:
        respx.get(f"{BASE_URL}/vq/news/TSLA").respond(
            200,
            json={"articles": []},
        )
        articles = client.news.get("TSLA")
        assert articles == []
