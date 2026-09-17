# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Retained JSON/UTF-8 encoding and service header-value formatting."""

from __future__ import annotations
import json
from typing import Any, Union

# Compact separators (no spaces) match the byte sequence the existing
# core-python pipeline produces today.
_COMPACT_SEPARATORS = (",", ":")


def normalize_utf16_surrogates(value: str) -> str:
    """Combine UTF-16 pairs while retaining unpaired code units unchanged."""
    return value.encode("utf-16-le", "surrogatepass").decode(
        "utf-16-le", "surrogatepass"
    )


def encode_json_to_utf8(json_body: str) -> bytes:
    """Encode JSON, combining UTF-16 pairs and escaping unpaired surrogates."""
    try:
        return json_body.encode("utf-8")
    except UnicodeEncodeError:
        normalized = normalize_utf16_surrogates(json_body)
        return normalized.encode("utf-8", "backslashreplace")


def serialize_body_to_bytes(
    body: Any, *, ensure_ascii: bool = True, allow_nan: bool = True
) -> bytes:
    """Return the exact bytes to put in the request body.

    :param body: The request body in any of the accepted Python shapes.
    :type body: Any
    :keyword bool ensure_ascii: Escape non-ASCII characters unless compact UTF-8 writes are enabled.
    :keyword bool allow_nan: Whether non-finite numbers are permitted during serialization.
    :returns: UTF-8 encoded bytes. Empty bytes (``b""``) when ``body``
        is ``None``.
    :rtype: bytes
    :raises TypeError: when ``body`` is not one of the accepted shapes.
    """
    if body is None:
        return b""
    if isinstance(body, (bytes, bytearray)):
        return bytes(body)
    if isinstance(body, str):
        return body.encode("utf-8")
    if isinstance(body, (dict, list, tuple)):
        return encode_json_to_utf8(
            json.dumps(
                body,
                separators=_COMPACT_SEPARATORS,
                ensure_ascii=ensure_ascii,
                allow_nan=allow_nan,
            )
        )
    raise TypeError(
        "Cannot serialize request body of type "
        f"{type(body).__name__!r}; expected dict, list, tuple, str, "
        f"bytes, bytearray, or None."
    )


SerializableBody = Union[None, bytes, bytearray, str, dict, list, tuple]


def format_ru_charge(charge: float) -> str:
    """Render a request charge as the wire-string shape (``str(float)``).

    :param charge: The RU charge as a float (typically from the Rust
        backend's typed response struct).
    :type charge: float
    :returns: The wire-string representation, e.g. ``"1.0"``, ``"1.43"``.
    :rtype: str
    """
    return str(float(charge))
