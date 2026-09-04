# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Serialize a request body into the exact bytes that go on the wire.

Produces the bytes once, in one place, so the current core-Python and Rust
backends ship the identical request body during migration. The intended final
architecture keeps only the Rust path. Accepted inputs:

- ``None`` -> empty bytes (no-body operations).
- ``str`` -> UTF-8 bytes (caller must already have valid JSON).
- ``bytes`` / ``bytearray`` -> passthrough.
- ``dict`` / ``list`` / ``tuple`` -> ``json.dumps`` with compact
  separators ``(",", ":")`` then UTF-8 encode.

Any other type raises ``TypeError``; the legacy path silently dropped
unknown types, which masked caller bugs.
"""
from __future__ import annotations

import json
from typing import Any, Union

# Compact separators (no spaces) match the byte sequence the existing
# core-python pipeline produces today.
_COMPACT_SEPARATORS = (",", ":")


def serialize_body_to_bytes(body: Any) -> bytes:
    """Return the exact bytes to put in the request body.

    :param body: The request body in any of the accepted Python shapes.
    :type body: Any
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
        return json.dumps(body, separators=_COMPACT_SEPARATORS).encode("utf-8")
    raise TypeError(
        "Cannot serialize request body of type "
        f"{type(body).__name__!r}; expected dict, list, tuple, str, "
        f"bytes, bytearray, or None."
    )


SerializableBody = Union[None, bytes, bytearray, str, dict, list, tuple]
