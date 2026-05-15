"""Cursor-based auto-pagination iterators."""

from __future__ import annotations

from collections.abc import Iterator, AsyncIterator, Callable, Awaitable
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

# Type alias for the page-fetch callback return shape
PageDict = dict[str, Any]
FetchPageFn = Callable[..., PageDict]
AsyncFetchPageFn = Callable[..., Awaitable[PageDict]]


class PageInfo(BaseModel):
    """Pagination metadata from API responses."""

    has_next: bool
    cursor: str | None = None
    total: int | None = None


class SyncPage(Generic[T]):
    """A single page of results with pagination metadata."""

    def __init__(self, data: list[T], page_info: PageInfo) -> None:
        self.data = data
        self.page_info = page_info

    def __iter__(self) -> Iterator[T]:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)


class SyncPaginator(Generic[T]):
    """Auto-paginating synchronous iterator.

    Usage:
        for item in client.screener.run(filters):
            print(item.symbol)
    """

    def __init__(self, fetch_page: FetchPageFn, model: type[T]) -> None:
        self._fetch_page = fetch_page
        self._model = model
        self._cursor: str | None = None
        self._exhausted = False

    def __iter__(self) -> Iterator[T]:
        while not self._exhausted:
            page = self._fetch_page(cursor=self._cursor)
            data = page.get("data", [])
            page_info_raw = page.get("page_info", {})

            for item in data:
                yield self._model.model_validate(item)

            if page_info_raw.get("has_next") and page_info_raw.get("cursor"):
                self._cursor = page_info_raw["cursor"]
            else:
                self._exhausted = True

    def pages(self) -> Iterator[SyncPage[T]]:
        """Iterate page by page instead of item by item."""
        while not self._exhausted:
            page = self._fetch_page(cursor=self._cursor)
            data = [self._model.model_validate(item) for item in page.get("data", [])]
            page_info = PageInfo.model_validate(page.get("page_info", {"has_next": False}))

            yield SyncPage(data=data, page_info=page_info)

            if page_info.has_next and page_info.cursor:
                self._cursor = page_info.cursor
            else:
                self._exhausted = True


class AsyncPaginator(Generic[T]):
    """Auto-paginating asynchronous iterator.

    Usage:
        async for item in client.screener.run(filters):
            print(item.symbol)
    """

    def __init__(self, fetch_page: AsyncFetchPageFn, model: type[T]) -> None:
        self._fetch_page = fetch_page
        self._model = model
        self._cursor: str | None = None
        self._exhausted = False

    async def __aiter__(self) -> AsyncIterator[T]:
        while not self._exhausted:
            page = await self._fetch_page(cursor=self._cursor)
            data = page.get("data", [])
            page_info_raw = page.get("page_info", {})

            for item in data:
                yield self._model.model_validate(item)

            if page_info_raw.get("has_next") and page_info_raw.get("cursor"):
                self._cursor = page_info_raw["cursor"]
            else:
                self._exhausted = True
