"""URL path encoding utility to prevent path traversal attacks."""

from __future__ import annotations

from urllib.parse import quote


def encode_path_param(value: str) -> str:
    """Safely encode a value for use in a URL path segment.

    Prevents path traversal by encoding all special characters including
    forward slashes, dots, and percent signs.

    Args:
        value: Raw value to embed in a URL path.

    Returns:
        URL-encoded string safe for path interpolation.
    """
    encoded = quote(value, safe="")
    # Percent-encode standalone dot sequences that could enable path traversal.
    # After quote(), slashes are already encoded, so ".." can only appear as
    # a literal dot-dot from the original input.
    encoded = encoded.replace("..", "%2E%2E")
    return encoded
