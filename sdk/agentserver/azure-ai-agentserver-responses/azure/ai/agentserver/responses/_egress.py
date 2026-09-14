# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Strip framework-internal metadata from client-facing payloads.

``internal_metadata`` (on items) and the reserved ``_internal_metadata`` key
(inside a response's public ``metadata`` map) are framework-internal — they
round-trip through storage but MUST NOT reach a client. :func:`strip_internal_metadata`
is the single egress chokepoint: every site that serialises a response, an item
collection, or an SSE event for the wire routes its payload through it first.

The helper only ever removes the two documented keys, so it is safe to walk the
whole payload tree. It mutates the passed mapping **in place**; callers pass a
payload that is safe to mutate (e.g. the fresh dict from ``model.as_dict()``).
"""

from __future__ import annotations

from typing import Any

_ITEM_KEY = "internal_metadata"
_RESERVED_KEY = "_internal_metadata"


def strip_internal_metadata(payload: Any) -> Any:
    """Remove all framework-internal metadata from *payload*, in place.

    - Removes the ``internal_metadata`` key from every dict in the tree (the
      item-level bag — no public field shares this name).
    - Removes the reserved ``_internal_metadata`` key from any ``metadata``
      sub-map (the response-level backing). If that leaves the ``metadata`` map
      empty, it is normalised to ``None`` so the egressed shape matches a
      response with no public metadata.

    Fail-closed: non-mapping / unexpected input is returned unchanged.

    :param payload: A response-, item-, or event-shaped mapping (or a list /
        scalar, which is walked / returned as-is).
    :type payload: ~typing.Any
    :returns: The same object, mutated in place.
    :rtype: ~typing.Any
    """
    if isinstance(payload, dict):
        # Item-level bag (safe on any dict — the key is framework-reserved).
        payload.pop(_ITEM_KEY, None)
        # Response-level reserved key inside the public ``metadata`` map.
        metadata = payload.get("metadata")
        if isinstance(metadata, dict) and _RESERVED_KEY in metadata:
            del metadata[_RESERVED_KEY]
            if not metadata:
                payload["metadata"] = None
        for value in payload.values():
            strip_internal_metadata(value)
    elif isinstance(payload, list):
        for value in payload:
            strip_internal_metadata(value)
    return payload
