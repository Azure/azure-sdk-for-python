# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Utilities for parsing and decoding ``data:`` URLs (RFC 2397).

Usage::

    from azure.ai.agentserver.responses import data_url

    if data_url.is_data_url(value):
        raw_bytes = data_url.decode_bytes(value)
        media_type = data_url.get_media_type(value)
"""

from __future__ import annotations

import base64

_DATA_PREFIX = "data:"
_BASE64_MARKER = ";base64"


def is_data_url(value: str | None) -> bool:
    """Check whether *value* is a ``data:`` URL.

    :param value: The string to test.
    :type value: str | None
    :returns: ``True`` if *value* starts with ``data:``, ``False`` otherwise.
    :rtype: bool
    """
    return value is not None and value.lower().startswith(_DATA_PREFIX)


def decode_bytes(data_url_str: str) -> bytes:
    """Decode the base-64 payload of a ``data:`` URL.

    :param data_url_str: A ``data:`` URL string.
    :type data_url_str: str
    :returns: The decoded bytes.
    :rtype: bytes
    :raises ValueError: If *data_url_str* is not a valid ``data:`` URL or
        its base-64 payload cannot be decoded.
    """
    if data_url_str is None:
        raise ValueError("data_url_str must not be None")
    comma = data_url_str.find(",")
    if comma < 0 or not data_url_str.lower().startswith(_DATA_PREFIX):
        raise ValueError("Invalid data URL: expected format 'data:[<mediatype>][;base64],<data>'.")
    payload = data_url_str[comma + 1 :]
    try:
        return base64.b64decode(payload)
    except Exception as exc:
        raise ValueError(f"Failed to decode base-64 payload: {exc}") from exc


def try_decode_bytes(data_url_str: str | None) -> bytes | None:
    """Attempt to decode a ``data:`` URL, returning ``None`` on failure.

    :param data_url_str: A ``data:`` URL string, or ``None``.
    :type data_url_str: str | None
    :returns: The decoded bytes, or ``None`` if *data_url_str* is not a
        valid ``data:`` URL.
    :rtype: bytes | None
    """
    if data_url_str is None:
        return None
    try:
        return decode_bytes(data_url_str)
    except (ValueError, TypeError):
        return None


def get_media_type(data_url_str: str | None) -> str | None:
    """Extract the media type from a ``data:`` URL.

    :param data_url_str: A ``data:`` URL string, or ``None``.
    :type data_url_str: str | None
    :returns: The media type (e.g. ``"image/png"``), or ``None`` if absent
        or if *data_url_str* is not a valid ``data:`` URL.
    :rtype: str | None
    """
    if data_url_str is None:
        return None
    lower = data_url_str.lower()
    if not lower.startswith(_DATA_PREFIX):
        return None
    after_scheme = len(_DATA_PREFIX)
    comma = data_url_str.find(",", after_scheme)
    if comma < 0:
        return None
    header = data_url_str[after_scheme:comma]
    base64_pos = header.lower().find(_BASE64_MARKER)
    media_type = header[:base64_pos] if base64_pos >= 0 else header
    return media_type if media_type else None
