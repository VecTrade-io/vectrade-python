"""Tests for pagination utilities."""

from vectrade._pagination import SyncPaginator, SyncPage, PageInfo
from vectrade.types.screener import ScreenerResult


class TestSyncPaginator:
    """Test synchronous auto-pagination."""

    def test_single_page(self) -> None:
        """Single page with no next returns all items."""
        def fetch_page(cursor=None):
            return {
                "data": [
                    {"symbol": "AAPL", "company_name": "Apple", "price": 198.0, "change_pct": 1.0},
                    {"symbol": "MSFT", "company_name": "Microsoft", "price": 445.0, "change_pct": 0.5},
                ],
                "page_info": {"has_next": False, "cursor": None},
            }

        paginator = SyncPaginator(fetch_page=fetch_page, model=ScreenerResult)
        results = list(paginator)
        assert len(results) == 2
        assert results[0].symbol == "AAPL"
        assert results[1].symbol == "MSFT"

    def test_multiple_pages(self) -> None:
        """Paginator follows cursors across multiple pages."""
        call_count = 0

        def fetch_page(cursor=None):
            nonlocal call_count
            call_count += 1
            if cursor is None:
                return {
                    "data": [{"symbol": "AAPL", "company_name": "Apple", "price": 198.0, "change_pct": 1.0}],
                    "page_info": {"has_next": True, "cursor": "page2"},
                }
            elif cursor == "page2":
                return {
                    "data": [{"symbol": "MSFT", "company_name": "Microsoft", "price": 445.0, "change_pct": 0.5}],
                    "page_info": {"has_next": True, "cursor": "page3"},
                }
            else:
                return {
                    "data": [{"symbol": "GOOGL", "company_name": "Alphabet", "price": 178.0, "change_pct": -0.2}],
                    "page_info": {"has_next": False},
                }

        paginator = SyncPaginator(fetch_page=fetch_page, model=ScreenerResult)
        results = list(paginator)
        assert len(results) == 3
        assert call_count == 3
        assert results[2].symbol == "GOOGL"

    def test_empty_page(self) -> None:
        """Empty first page returns nothing."""
        def fetch_page(cursor=None):
            return {"data": [], "page_info": {"has_next": False}}

        paginator = SyncPaginator(fetch_page=fetch_page, model=ScreenerResult)
        results = list(paginator)
        assert results == []

    def test_pages_iterator(self) -> None:
        """Pages iterator yields SyncPage objects."""
        def fetch_page(cursor=None):
            return {
                "data": [{"symbol": "AAPL", "company_name": "Apple", "price": 198.0, "change_pct": 1.0}],
                "page_info": {"has_next": False},
            }

        paginator = SyncPaginator(fetch_page=fetch_page, model=ScreenerResult)
        pages = list(paginator.pages())
        assert len(pages) == 1
        assert isinstance(pages[0], SyncPage)
        assert len(pages[0]) == 1
