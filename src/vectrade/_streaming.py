"""Server-Sent Events (SSE) streaming support."""

from __future__ import annotations

import json
from collections.abc import AsyncGenerator, Generator
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import httpx


@dataclass
class StreamChunk:
    """A single chunk from a streaming response."""

    text: str
    type: str = "text"
    metadata: dict | None = None


@dataclass
class StreamDone:
    """Sentinel indicating the stream is complete."""

    usage: dict | None = None


def iter_sse_lines(response: httpx.Response) -> Generator[str, None, None]:
    """Iterate over SSE lines from a synchronous httpx response."""
    for line in response.iter_lines():
        if line.startswith("data: "):
            yield line[6:]
        elif line.startswith(":"):
            continue  # SSE comment / keepalive


async def aiter_sse_lines(response: httpx.Response) -> AsyncGenerator[str, None]:
    """Iterate over SSE lines from an async httpx response."""
    async for line in response.aiter_lines():
        if line.startswith("data: "):
            yield line[6:]
        elif line.startswith(":"):
            continue


def parse_sse_data(data: str) -> StreamChunk | StreamDone | None:
    """Parse a single SSE data payload into a typed chunk."""
    if data == "[DONE]":
        return StreamDone()

    try:
        parsed = json.loads(data)
    except json.JSONDecodeError:
        return StreamChunk(text=data)

    if parsed.get("type") == "done":
        return StreamDone(usage=parsed.get("usage"))

    return StreamChunk(
        text=parsed.get("content", ""),
        type=parsed.get("type", "text"),
        metadata=parsed.get("metadata"),
    )


class Stream:
    """Synchronous streaming response wrapper."""

    def __init__(self, response: httpx.Response) -> None:
        self._response = response

    def __iter__(self) -> Generator[StreamChunk, None, None]:
        for data in iter_sse_lines(self._response):
            chunk = parse_sse_data(data)
            if isinstance(chunk, StreamDone):
                return
            if chunk is not None:
                yield chunk

    def close(self) -> None:
        self._response.close()

    def __enter__(self) -> Stream:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


class AsyncStream:
    """Asynchronous streaming response wrapper."""

    def __init__(self, response: httpx.Response) -> None:
        self._response = response

    async def __aiter__(self) -> AsyncGenerator[StreamChunk, None]:
        async for data in aiter_sse_lines(self._response):
            chunk = parse_sse_data(data)
            if isinstance(chunk, StreamDone):
                return
            if chunk is not None:
                yield chunk

    async def close(self) -> None:
        await self._response.aclose()

    async def __aenter__(self) -> AsyncStream:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()
