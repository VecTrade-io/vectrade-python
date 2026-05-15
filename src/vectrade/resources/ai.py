"""AI resource — streaming agentic analysis."""

from __future__ import annotations

from collections.abc import Generator, AsyncGenerator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import httpx


class AIChunk:
    """A single chunk from a streaming AI analysis response."""

    def __init__(self, text: str, type: str = "text") -> None:
        self.text = text
        self.type = type


class AI:
    """Synchronous AI analysis resource."""

    def __init__(self, http: httpx.Client) -> None:
        self._http = http

    def stream(self, prompt: str) -> Generator[AIChunk, None, None]:
        """Stream an AI analysis response.

        Args:
            prompt: Analysis prompt (e.g., "Analyze AAPL for long-term hold").

        Yields:
            AIChunk objects with streamed text content.
        """
        with self._http.stream(
            "POST",
            "/vq/ai/analyze",
            json={"prompt": prompt, "stream": True},
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line.startswith("data: "):
                    import json

                    data = json.loads(line[6:])
                    if data.get("type") == "done":
                        break
                    yield AIChunk(text=data.get("content", ""), type=data.get("type", "text"))


class AsyncAI:
    """Asynchronous AI analysis resource."""

    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def stream(self, prompt: str) -> AsyncGenerator[AIChunk, None]:
        """Stream an AI analysis response."""
        async with self._http.stream(
            "POST",
            "/vq/ai/analyze",
            json={"prompt": prompt, "stream": True},
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    import json

                    data = json.loads(line[6:])
                    if data.get("type") == "done":
                        break
                    yield AIChunk(text=data.get("content", ""), type=data.get("type", "text"))
