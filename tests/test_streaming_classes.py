"""Tests for streaming classes — Stream, AsyncStream, iter_sse_lines, aiter_sse_lines, parse_sse_data."""

import asyncio
from unittest.mock import MagicMock

import pytest

from vectrade._streaming import (
    AsyncStream,
    Stream,
    StreamChunk,
    StreamDone,
    aiter_sse_lines,
    iter_sse_lines,
    parse_sse_data,
)


class TestParseSSEData:
    def test_done_signal(self) -> None:
        result = parse_sse_data("[DONE]")
        assert isinstance(result, StreamDone)
        assert result.usage is None

    def test_done_type(self) -> None:
        result = parse_sse_data('{"type": "done", "usage": {"tokens": 100}}')
        assert isinstance(result, StreamDone)
        assert result.usage == {"tokens": 100}

    def test_text_chunk(self) -> None:
        result = parse_sse_data('{"content": "hello", "type": "text"}')
        assert isinstance(result, StreamChunk)
        assert result.text == "hello"
        assert result.type == "text"

    def test_chunk_with_metadata(self) -> None:
        result = parse_sse_data('{"content": "hi", "type": "text", "metadata": {"key": "val"}}')
        assert isinstance(result, StreamChunk)
        assert result.metadata == {"key": "val"}

    def test_invalid_json_returns_raw_chunk(self) -> None:
        result = parse_sse_data("not json")
        assert isinstance(result, StreamChunk)
        assert result.text == "not json"


class TestIterSSELines:
    def test_yields_data_lines(self) -> None:
        mock_response = MagicMock()
        mock_response.iter_lines.return_value = iter(
            [
                "data: hello",
                "data: world",
            ]
        )
        lines = list(iter_sse_lines(mock_response))
        assert lines == ["hello", "world"]

    def test_skips_comments(self) -> None:
        mock_response = MagicMock()
        mock_response.iter_lines.return_value = iter(
            [
                ": keepalive",
                "data: actual",
                ": another comment",
            ]
        )
        lines = list(iter_sse_lines(mock_response))
        assert lines == ["actual"]

    def test_skips_non_data_lines(self) -> None:
        mock_response = MagicMock()
        mock_response.iter_lines.return_value = iter(
            [
                "event: update",
                "data: payload",
                "id: 123",
            ]
        )
        lines = list(iter_sse_lines(mock_response))
        assert lines == ["payload"]

    def test_empty_stream(self) -> None:
        mock_response = MagicMock()
        mock_response.iter_lines.return_value = iter([])
        lines = list(iter_sse_lines(mock_response))
        assert lines == []


class TestAiterSSELines:
    @pytest.mark.asyncio
    async def test_yields_data_lines(self) -> None:
        mock_response = MagicMock()

        async def _aiter():
            for line in ["data: hello", "data: world"]:
                yield line

        mock_response.aiter_lines.return_value = _aiter()
        lines = [line async for line in aiter_sse_lines(mock_response)]
        assert lines == ["hello", "world"]

    @pytest.mark.asyncio
    async def test_skips_comments(self) -> None:
        mock_response = MagicMock()

        async def _aiter():
            for line in [": ping", "data: real"]:
                yield line

        mock_response.aiter_lines.return_value = _aiter()
        lines = [line async for line in aiter_sse_lines(mock_response)]
        assert lines == ["real"]

    @pytest.mark.asyncio
    async def test_empty_stream(self) -> None:
        mock_response = MagicMock()

        async def _aiter():
            return
            yield  # noqa: make it an async generator

        mock_response.aiter_lines.return_value = _aiter()
        lines = [line async for line in aiter_sse_lines(mock_response)]
        assert lines == []


class TestStream:
    def test_iterates_chunks(self) -> None:
        mock_response = MagicMock()
        mock_response.iter_lines.return_value = iter(
            [
                'data: {"content": "Hello", "type": "text"}',
                'data: {"content": " world", "type": "text"}',
                "data: [DONE]",
            ]
        )
        stream = Stream(mock_response)
        chunks = list(stream)
        assert len(chunks) == 2
        assert chunks[0].text == "Hello"
        assert chunks[1].text == " world"

    def test_stops_on_done(self) -> None:
        mock_response = MagicMock()
        mock_response.iter_lines.return_value = iter(
            [
                'data: {"content": "first"}',
                "data: [DONE]",
                'data: {"content": "should not appear"}',
            ]
        )
        stream = Stream(mock_response)
        chunks = list(stream)
        assert len(chunks) == 1
        assert chunks[0].text == "first"

    def test_context_manager(self) -> None:
        mock_response = MagicMock()
        mock_response.iter_lines.return_value = iter([])
        with Stream(mock_response) as stream:
            list(stream)
        mock_response.close.assert_called_once()

    def test_close(self) -> None:
        mock_response = MagicMock()
        stream = Stream(mock_response)
        stream.close()
        mock_response.close.assert_called_once()


class TestAsyncStream:
    @pytest.mark.asyncio
    async def test_iterates_chunks(self) -> None:
        mock_response = MagicMock()

        async def _aiter():
            for line in [
                'data: {"content": "Hello", "type": "text"}',
                'data: {"content": " world", "type": "text"}',
                "data: [DONE]",
            ]:
                yield line

        mock_response.aiter_lines.return_value = _aiter()
        stream = AsyncStream(mock_response)
        chunks = [chunk async for chunk in stream]
        assert len(chunks) == 2
        assert chunks[0].text == "Hello"
        assert chunks[1].text == " world"

    @pytest.mark.asyncio
    async def test_stops_on_done(self) -> None:
        mock_response = MagicMock()

        async def _aiter():
            for line in [
                'data: {"content": "only this"}',
                "data: [DONE]",
                'data: {"content": "ignored"}',
            ]:
                yield line

        mock_response.aiter_lines.return_value = _aiter()
        stream = AsyncStream(mock_response)
        chunks = [chunk async for chunk in stream]
        assert len(chunks) == 1
        assert chunks[0].text == "only this"

    @pytest.mark.asyncio
    async def test_context_manager(self) -> None:
        mock_response = MagicMock()

        async def _aiter():
            return
            yield  # noqa: make it an async generator

        mock_response.aiter_lines.return_value = _aiter()

        async def mock_aclose():
            pass

        mock_response.aclose = MagicMock(side_effect=mock_aclose)

        async with AsyncStream(mock_response) as stream:
            _ = [chunk async for chunk in stream]
        mock_response.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_close(self) -> None:
        mock_response = MagicMock()

        async def mock_aclose():
            pass

        mock_response.aclose = MagicMock(side_effect=mock_aclose)
        stream = AsyncStream(mock_response)
        await stream.close()
        mock_response.aclose.assert_called_once()
