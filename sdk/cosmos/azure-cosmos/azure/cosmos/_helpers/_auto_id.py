# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Make sure the document going to the wire has an ``id`` field.

Every Cosmos item must carry an ``id`` string at the top level. The
SDK historically lets a customer omit it and quietly mints a UUID:
that's the
``Container.create_item(..., enable_automatic_id_generation=True)``
contract. The legacy implementation lives inline in
``_cosmos_client_connection._GetContainerIdWithPathForItem``:

    document = dict(document)
    if not document.get("id") and not options.get("disableAutomaticIdGeneration"):
        document["id"] = base.GenerateGuidId()

This module extracts the *same* logic into a pure helper so both
backends can mint identical ids and so the future rust path can pin
the id it gives to its ``ItemReference`` constructor against the id
the body actually carries. If those two ids ever drift, a retried
write would store the document under one id while the SDK logged
another â—” a debugging nightmare. The fix is to mint once, in one
place, and return the value to the caller.

The helper is intentionally minimal:

* It does not copy the body. The caller decides whether to copy first
  (the legacy path copies; new callers may already be holding a copy).
* It does not validate the type of an existing id. Cosmos rejects
  non-string ids with a 400 anyway, and the legacy path does not
  validate either; matching that behaviour preserves byte-equality
  with existing fixtures.
"""
from __future__ import annotations

import uuid
from typing import Any, Dict, Optional


def ensure_item_id(body: Dict[str, Any], *, generate: bool = True) -> Optional[str]:
    """Return the document id, minting a UUID if needed and allowed.

    The function checks ``body.get("id")`` and follows three branches:

    * Truthy existing id (the common case for caller-supplied ids):
      returned unchanged. ``body`` is not mutated.
    * Missing or falsy id with ``generate=True``: mint a fresh UUID4
      string, write it into ``body["id"]`` (in-place mutation), return
      the same value so the caller can assert it matches whatever the
      backend stamps onto a parallel ``ItemReference``.
    * Missing or falsy id with ``generate=False``: leave ``body``
      untouched and return ``None`` â—” the caller's contract is "I
      told you not to mint, so the request will fail server-side."

    "Falsy" here mirrors the legacy ``not document.get("id")`` check:
    empty string, ``None``, ``0``, ``False``, missing key. All trigger
    minting when ``generate=True``.

    :param body: The Cosmos document. Mutated in place when an id is
        minted; otherwise left alone. The caller is responsible for
        copying first if they need to preserve the original dict.
    :type body: Dict[str, Any]
    :param generate: When ``True`` (the default), a missing id will be
        minted as a fresh UUID4 string. When ``False``, the helper
        does not mutate ``body`` and returns ``None`` for a missing id.
    :type generate: bool
    :returns: The id string the body now carries, or ``None`` if id
        was missing and ``generate=False``.
    :rtype: Optional[str]
    """
    existing = body.get("id")
    if existing:  # Any truthy value: non-empty string is the only legitimate case.
        return existing

    if not generate:
        return None

    # ``str(uuid.uuid4())`` matches what legacy ``_base.GenerateGuidId``
    # produces (lowercase 36-char UUID with hyphens). Pinning the
    # representation here avoids drift if either side moves.
    new_id = str(uuid.uuid4())
    body["id"] = new_id
    return new_id
