# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Ensure a Cosmos document carries an ``id`` field before it goes on the wire.

Every Cosmos item needs a top-level ``id`` string. When the caller passes
``enable_automatic_id_generation=True`` and omits ``id``, the SDK mints a
UUID4 in its place. The current branch can run either the Rust backend or the
core-Python backend, and a Rust-selected client can still fall back for
unmigrated request shapes. This helper centralises the id logic so both paths
mint ids consistently during migration. The intended final architecture keeps
only the Rust path.
"""
from __future__ import annotations

import uuid
from typing import Any, Dict, Optional


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
