# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Document ID preparation and immutable encoded snapshots before dispatch."""

from __future__ import annotations
import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Dict, Optional
from ._resource_validation import validate_resource
from ._wire_encoding import normalize_utf16_surrogates, serialize_body_to_bytes


def ensure_item_id(body: Dict[str, Any], *, generate: bool = True) -> Optional[str]:
    """Return the document id, minting a UUID4 in-place if needed.

    - Truthy existing id: returned unchanged, ``body`` is not mutated.
    - Missing/falsy id with ``generate=True``: mint a UUID4, write it
      into ``body["id"]``, return the same value.
    - Missing/falsy id with ``generate=False``: return ``None``,
      ``body`` is not mutated.

    :param body: The Cosmos document. Mutated in place only when an id
        is minted. The caller is responsible for copying first if the
        original dict must be preserved.
    :type body: Dict[str, Any]
    :param generate: When ``True`` (default), mint a UUID4 for a missing
        id. When ``False``, leave ``body`` alone and return ``None``.
    :type generate: bool
    :returns: The id the body now carries, or ``None`` if id was missing
        and ``generate=False``.
    :rtype: Optional[str]
    """
    existing = body.get("id")
    if existing:
        return existing

    if not generate:
        return None

    new_id = str(uuid.uuid4())
    body["id"] = new_id
    return new_id


@dataclass(frozen=True)
class SerializedDocument:
    """Encoded document and its body ID, not a replacement's target ID."""

    body_id: Optional[str]
    body_bytes: bytes


def build_create_document(body: Any, *, generate_id: bool) -> dict[str, Any]:
    """Resolve the ID in a shallow top-level copy without changing caller data."""
    if not isinstance(body, Mapping):
        raise TypeError("create_item body must be a mapping.")
    prepared = dict(body)
    validate_resource(prepared)
    item_id = ensure_item_id(prepared, generate=generate_id)
    if not isinstance(item_id, str):
        if prepared.get("id") is not None and not isinstance(prepared["id"], str):
            raise TypeError("Item id must be a string.")
        raise ValueError(
            "Item body requires a non-empty 'id' or enable_automatic_id_generation=True."
        )
    if not item_id:
        raise ValueError("Item id must not be empty.")
    return prepared


def serialize_document(
    body: Any, *, operation: str, compact_utf8: bool = False
) -> SerializedDocument:
    """Encode a normalized document without generating an ID or changing input."""
    if operation not in ("create_item", "upsert_item", "replace_item"):
        raise ValueError(f"Cannot serialize a document for {operation!r}.")
    encoded = serialize_body_to_bytes(
        body, ensure_ascii=not compact_utf8, allow_nan=operation != "create_item"
    )
    # Replacement also accepts pre-encoded bodies; its target ID is separate.
    if isinstance(body, dict):
        body_id = dict.get(body, "id")
    elif operation != "replace_item" or isinstance(body, Mapping):
        body_id = body.get("id")
    else:
        body_id = None
    if isinstance(body_id, str) and body_id:
        body_id = str.__str__(body_id)
        if not body_id.isascii():
            # JSON readers combine escaped pairs in either encoding mode.
            body_id = normalize_utf16_surrogates(body_id)
    else:
        body_id = None
    return SerializedDocument(body_id=body_id, body_bytes=encoded)
