# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Serialize a request body into the exact bytes that go on the wire.

The Cosmos service receives every item create/replace/upsert as a
JSON document. The exact bytes matter: anything downstream that hashes
or string-compares the document (audit logs, dedup checks, content-
addressed storage, customer test fixtures) breaks silently if the SDK
reformats keys, reorders dict entries, or rewrites numeric literals.

This module produces those bytes once, in one place, so both the
core-python and rust backends ship the identical request body. Doing
it in one helper is what guarantees byte-for-byte parity between the
two paths regardless of which one ran the call.

The behaviour mirrors the legacy serializer in
``azure/cosmos/_synchronized_request.py::_data_to_unicode_string`` for
inputs the SDK actually accepts:

* ``None`` -> empty bytes (used for operations with no body, e.g. delete).
* ``str`` -> UTF-8 bytes of the string, unchanged. Caller is responsible
  for the string already being valid JSON.
* ``bytes`` / ``bytearray`` -> passthrough (already encoded by caller).
* ``dict`` / ``list`` / ``tuple`` -> ``json.dumps(...).encode("utf-8")``
  with compact separators ``(",", ":")``. Compact separators preserve
  the byte equality the rest of the SDK has always produced.

Anything else raises ``TypeError`` instead of being silently dropped.
The legacy path returns ``None`` for unknown types, which produced a
quiet "request had no body" bug downstream; we surface it here at the
helper boundary so the caller learns about it during development.
"""
from __future__ import annotations

import json
from typing import Any, Union

# json.dumps with these separators emits no spaces between elements or
# after the colon in dicts. The byte sequence matches what the existing
# core-python pipeline produces today for the same input.
_COMPACT_SEPARATORS = (",", ":")


def serialize_body_to_bytes(body: Any) -> bytes:
    """Return the exact bytes to put in the request body.

    Accepts every input shape the SDK historically accepted for a body
    (see the module docstring for the full table). The return value is
    always ``bytes`` so the backend layer can treat the body uniformly:
    the rust driver wants raw bytes, and the core-python pipeline
    accepts bytes the same way it accepts a string.

    :param body: The request body in any of the accepted Python shapes.
    :type body: Any
    :returns: UTF-8 encoded bytes ready to assign as the request
        payload. Returns empty bytes (``b""``) when ``body`` is
        ``None``, which the caller should interpret as "no body" and
        is the correct behaviour for delete-style operations.
    :rtype: bytes
    :raises TypeError: when ``body`` is not one of the accepted shapes.
        Surfaces here loudly rather than silently producing an empty
        request, which is what the legacy code path did.
    """
    # No body. The caller will skip writing a request payload.
    if body is None:
        return b""

    # Bytes-like inputs are assumed to already be UTF-8 JSON encoded
    # by the caller. This branch is the one the eventual rust path
    # will take once a later refactor removes the dict/list intermediate
    # representation; the helper supports it today so unit tests can
    # round-trip pre-encoded bodies without extra serialization.
    if isinstance(body, (bytes, bytearray)):
        return bytes(body)

    # Strings are assumed to already be JSON text. We just encode them
    # to UTF-8 bytes. The legacy path returned the string unchanged
    # and let the transport encode it; doing the encode here keeps the
    # backend interface uniform on bytes.
    if isinstance(body, str):
        return body.encode("utf-8")

    # The common case: a Python dict, list, or tuple that we serialise
    # to JSON. Compact separators (no space after comma or colon) match
    # the legacy core-python behaviour byte-for-byte. ``ensure_ascii``
    # is left at its default of True so non-ASCII characters become
    # ``\uXXXX`` escapes, which is what the existing pipeline does and
    # what every Cosmos parity test fixture in the repo expects.
    if isinstance(body, (dict, list, tuple)):
        return json.dumps(body, separators=_COMPACT_SEPARATORS).encode("utf-8")

    # Anything else is a programming error in the caller. Raise rather
    # than swallow â—” see the module docstring for the rationale.
    raise TypeError(
        "Cannot serialize request body of type "
        f"{type(body).__name__!r}; expected dict, list, tuple, str, "
        f"bytes, bytearray, or None."
    )


# Type alias kept here so the helper module advertises which inputs it
# accepts without forcing callers to import the union from elsewhere.
SerializableBody = Union[None, bytes, bytearray, str, dict, list, tuple]
