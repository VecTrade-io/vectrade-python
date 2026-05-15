"""Tests for streaming SSE parsing."""

import pytest

from vectrade._streaming import StreamChunk, StreamDone, parse_sse_data


class TestParseSSEData:
    """Test SSE data line parsing."""

    def test_text_chunk(self) -> None:
        """JSON with content is parsed as StreamChunk."""
        result = parse_sse_data('{"content": "Hello", "type": "text"}')
        assert isinstance(result, StreamChunk)
        assert result.text == "Hello"
        assert result.type == "text"

    def test_done_signal(self) -> None:
        """[DONE] sentinel returns StreamDone."""
        result = parse_sse_data("[DONE]")
        assert isinstance(result, StreamDone)

    def test_done_type_in_json(self) -> None:
        """JSON with type=done returns StreamDone."""
        result = parse_sse_data('{"type": "done", "usage": {"tokens": 42}}')
        assert isinstance(result, StreamDone)
        assert result.usage == {"tokens": 42}

    def test_non_json_returns_raw_text(self) -> None:
        """Non-JSON data is returned as raw text chunk."""
        result = parse_sse_data("plain text data")
        assert isinstance(result, StreamChunk)
        assert result.text == "plain text data"

    def test_metadata_field(self) -> None:
        """Metadata field is passed through."""
        result = parse_sse_data('{"content": "x", "metadata": {"source": "test"}}')
        assert isinstance(result, StreamChunk)
        assert result.metadata == {"source": "test"}

    def test_missing_content_defaults_empty(self) -> None:
        """Missing content field defaults to empty string."""
        result = parse_sse_data('{"type": "citation"}')
        assert isinstance(result, StreamChunk)
        assert result.text == ""
        assert result.type == "citation"
