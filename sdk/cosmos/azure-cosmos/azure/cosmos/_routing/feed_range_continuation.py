# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Shared helpers for the structured ``feed_range`` continuation token.

Both the sync (``azure.cosmos._cosmos_client_connection``) and async
(``azure.cosmos.aio._cosmos_client_connection_async``) ``__QueryFeed``
implementations import from this module so that there is exactly one
source of truth for token wire-format, hash fingerprinting, and
routing-scope resolution. Only the pagination loop differs between the
two paths (sync vs. ``await``); the token logic does not.

Terminology: the saved continuation tracks progress through the
caller's input ``feed_range``. We need to remember (a) the piece of
that range we are currently reading and (b) any pieces we have not
started yet. We call each piece a ``feedrange`` because it is exactly
that - a sub-range of the caller's ``feed_range``, represented as the
same ``routing_range.Range`` type the rest of the routing code uses.
The two-letter wire codes ``cf`` (current feedrange) and ``rf``
(remaining feedranges) deliberately diverge from the codes Java uses
in ``ReadManyByPartitionKeyContinuationToken`` (``cb``/``rb``); the
divergence is intentional, like ``ph`` -> ``frh`` already in this
file, and makes accidental cross-SDK token reuse fail at the shape
check rather than producing wrong rows.
"""

import base64
import binascii
import hashlib
import json
from typing import Any, List, MutableMapping, Optional, Tuple

from .. import http_constants
from . import routing_range


# ----- Token wire-format constants ---------------------------------------
# Field codes for the v=1 envelope.
_TOKEN_VERSION = 1
_FIELD_VERSION = "v"
_FIELD_COLLECTION_RID = "cr"
_FIELD_QUERY_HASH = "qh"
_FIELD_FEEDRANGE_HASH = "frh"
_FIELD_CURRENT_FEEDRANGE = "cf"
_FIELD_REMAINING_FEEDRANGES = "rf"
_FIELD_BACKEND_CONTINUATION = "bc"


# ----- Hash helpers ------------------------------------------------------
def _stable_hash_128(payload: bytes) -> str:
    """Stable 128-bit hex digest.

    SHA-256 truncated to 32 hex characters. Switch to a vendored
    MurmurHash3-128 if cross-SDK token portability is ever required
    (it currently is not).
    """
    return hashlib.sha256(payload).hexdigest()[:32]


def _hash_query_spec(query: Any) -> str:
    """Hash query text + (parameter name, JSON-canonical value) pairs.

    Resume requires the exact same query shape, not a semantically
    equivalent one. ``query`` may be either a string or the dict form
    produced by ``__CheckAndUnifyQueryFormat``.
    """
    parameters: list = []
    parts: List[bytes] = []
    if isinstance(query, dict):
        parts.append((query.get("query") or "").encode("utf-8"))
        parameters = query.get("parameters") or []
    else:
        parts.append((query or "").encode("utf-8"))
    parts.append(b"\0")
    for p in parameters:
        parts.append((p.get("name", "") or "").encode("utf-8"))
        parts.append(b"\0")
        parts.append(
            json.dumps(p.get("value"), sort_keys=True, separators=(",", ":")).encode("utf-8")
        )
        parts.append(b"\0")
    return _stable_hash_128(b"".join(parts))


def _hash_feed_range(feed_range: routing_range.Range) -> str:
    """Stable 128-bit fingerprint of the INPUT feed_range.

    Detects a token that was created against a different feed_range on
    the same container being replayed against the wrong scope.
    """
    canonical = json.dumps(
        {
            "min": feed_range.min,
            "max": feed_range.max,
            "isMinInclusive": True,
            "isMaxInclusive": False,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return _stable_hash_128(canonical.encode("utf-8"))


# ----- Token codec -------------------------------------------------------
def _encode_token(payload: dict) -> str:
    """JSON-serialize ``payload`` then base64-encode to a single ASCII blob."""
    return base64.b64encode(
        json.dumps(payload, separators=(",", ":")).encode("utf-8")
    ).decode("ascii")


def _decode_token(serialized: Optional[str]) -> Optional[dict]:
    """Decode a continuation string into our token dict, or ``None``.

    Returns ``None`` when ``serialized`` is empty or not in our shape.
    A pre-fix opaque continuation falls into that bucket and the caller
    treats it as ``continuation_token=None`` (start fresh).

    Raises ``ValueError`` only when the input parses as our shape but
    is structurally invalid - an unknown ``v`` value or a missing
    required field. We fail loudly there so a token from a future SDK
    or a corrupted blob is not silently coerced into "start fresh".
    """
    if not serialized:
        return None
    try:
        decoded_bytes = base64.b64decode(serialized, validate=True)
        decoded = json.loads(decoded_bytes.decode("utf-8"))
    except (ValueError, TypeError, UnicodeDecodeError, binascii.Error):
        return None  # not our shape -> start fresh
    if not isinstance(decoded, dict) or _FIELD_VERSION not in decoded:
        return None
    version = decoded.get(_FIELD_VERSION)
    if version != _TOKEN_VERSION:
        raise ValueError(
            "Unsupported feed_range continuation token version: {}. "
            "This SDK supports version {}.".format(version, _TOKEN_VERSION)
        )
    _validate_v1_token_structure(decoded)
    return decoded


def _validate_v1_token_structure(decoded: dict) -> None:
    """Validate required v1 token fields so downstream code can index
    them without checking for ``KeyError``."""
    if not isinstance(decoded.get(_FIELD_COLLECTION_RID), str):
        raise ValueError("Malformed feed_range continuation token: 'cr' is required.")
    if not isinstance(decoded.get(_FIELD_QUERY_HASH), str):
        raise ValueError("Malformed feed_range continuation token: 'qh' is required.")
    if not isinstance(decoded.get(_FIELD_FEEDRANGE_HASH), str):
        raise ValueError("Malformed feed_range continuation token: 'frh' is required.")

    current = decoded.get(_FIELD_CURRENT_FEEDRANGE)
    if not isinstance(current, dict):
        raise ValueError("Malformed feed_range continuation token: 'cf' is required.")
    _validate_range_dict(current, "cf")

    remaining = decoded.get(_FIELD_REMAINING_FEEDRANGES)
    if not isinstance(remaining, list):
        raise ValueError("Malformed feed_range continuation token: 'rf' is required.")
    for idx, entry in enumerate(remaining):
        if not isinstance(entry, dict):
            raise ValueError(
                "Malformed feed_range continuation token: 'rf[{}]' must be an object.".format(idx)
            )
        _validate_range_dict(entry, "rf[{}]".format(idx))

    backend_continuation = decoded.get(_FIELD_BACKEND_CONTINUATION)
    if backend_continuation is not None and not isinstance(backend_continuation, str):
        raise ValueError("Malformed feed_range continuation token: 'bc' must be a string or null.")


def _validate_range_dict(range_dict: dict, field_name: str) -> None:
    """Each persisted feedrange is a {'min': str, 'max': str} dict."""
    if not isinstance(range_dict.get("min"), str) or not isinstance(range_dict.get("max"), str):
        raise ValueError(
            "Malformed feed_range continuation token: '{}.min' and '{}.max' are required.".format(
                field_name, field_name
            )
        )


# ----- Feedrange / routing helpers ---------------------------------------
def _dict_to_range(range_dict: dict) -> routing_range.Range:
    """Convert a persisted ``{'min': ..., 'max': ...}`` dict back into a ``Range``."""
    return routing_range.Range(
        range_min=range_dict["min"],
        range_max=range_dict["max"],
        isMinInclusive=True,
        isMaxInclusive=False,
    )


def _validate_token_identity(
    inbound: dict,
    resource_id: str,
    query: Any,
    feed_range_epk: routing_range.Range,
) -> None:
    """Confirm the inbound token was created for the same collection,
    query, and feed_range the current call is using. If any of the
    three fingerprints disagrees, raise ``ValueError`` so the caller
    finds out instead of silently getting rows from a different
    request."""
    expected_qh = _hash_query_spec(query)
    expected_frh = _hash_feed_range(feed_range_epk)
    if inbound[_FIELD_COLLECTION_RID] != resource_id:
        raise ValueError(
            "Continuation token was created for a different collection "
            "(collection rid mismatch)."
        )
    if inbound[_FIELD_QUERY_HASH] != expected_qh:
        raise ValueError(
            "Continuation token was created with a different query "
            "(query hash mismatch). Resume requires the exact same query shape."
        )
    if inbound[_FIELD_FEEDRANGE_HASH] != expected_frh:
        raise ValueError(
            "Continuation token was created for a different feed_range "
            "(feed_range hash mismatch)."
        )


def _extract_resume_state(
    inbound: dict,
) -> Tuple[routing_range.Range, List[routing_range.Range], Optional[str]]:
    """Pull the current feedrange, the remaining feedranges, and the
    backend continuation out of a v1 token."""
    current_feedrange = _dict_to_range(inbound[_FIELD_CURRENT_FEEDRANGE])
    remaining_feedranges = [_dict_to_range(r) for r in inbound[_FIELD_REMAINING_FEEDRANGES]]
    return current_feedrange, remaining_feedranges, inbound.get(_FIELD_BACKEND_CONTINUATION)


def _explode_feedrange_on_multi_overlap(
    current_feedrange: routing_range.Range,
    overlapping: List[dict],
    remaining_feedranges: List[routing_range.Range],
) -> Tuple[routing_range.Range, List[routing_range.Range], bool]:
    """If a saved feedrange now spans more than one physical partition
    (Cosmos split it), slice it into one sub-feedrange per child."""
    if len(overlapping) <= 1:
        return current_feedrange, remaining_feedranges, False
    sub_feedranges = _derive_initial_feedranges(current_feedrange, overlapping)
    return sub_feedranges[0], sub_feedranges[1:] + remaining_feedranges, True


def _build_scope_from_overlaps(
    overlapping: List[dict], feedrange: routing_range.Range
) -> Tuple[List[dict], routing_range.Range]:
    """Compute the union EPK scope over a set of overlapping physical
    partitions, returning the overlaps and the union as a ``Range``.

    Both the sync and async pagination paths call this directly after
    awaiting / invoking ``routing_map_provider.get_overlapping_ranges``
    themselves, so the live lookup stays at the call site (sync vs.
    async) and the pure union logic is shared here.
    """
    if not overlapping:
        raise RuntimeError(
            "Routing map returned no overlapping ranges for feedrange "
            "[{}, {}).".format(feedrange.min, feedrange.max)
        )
    min_inclusive = overlapping[0]["minInclusive"]
    max_exclusive = overlapping[0]["maxExclusive"]
    for r in overlapping[1:]:
        if r["minInclusive"] < min_inclusive:
            min_inclusive = r["minInclusive"]
        if r["maxExclusive"] > max_exclusive:
            max_exclusive = r["maxExclusive"]
    scope = routing_range.Range(
        range_min=min_inclusive,
        range_max=max_exclusive,
        isMinInclusive=True,
        isMaxInclusive=False,
    )
    return overlapping, scope


def _derive_initial_feedranges(
    feed_range_epk: routing_range.Range, overlapping: List[dict]
) -> List[routing_range.Range]:
    """Given the caller's input feed_range and the partitions it
    currently overlaps, return one sub-feedrange per partition (the
    intersection of the partition's range and the input feed_range),
    ordered by EPK ``min``."""
    feedranges: List[routing_range.Range] = []
    for olr in overlapping:
        single = routing_range.Range.PartitionKeyRangeToRange(olr)
        feedranges.append(
            routing_range.Range(
                range_min=max(single.min, feed_range_epk.min),
                range_max=min(single.max, feed_range_epk.max),
                isMinInclusive=True,
                isMaxInclusive=False,
            )
        )
    feedranges.sort(key=lambda r: r.min)
    return feedranges


def _build_outbound_token(
    resource_id: str,
    query: Any,
    feed_range_epk: routing_range.Range,
    current_feedrange: routing_range.Range,
    remaining_feedranges: List[routing_range.Range],
    backend_continuation: Optional[str],
) -> str:
    """Build and base64-encode the outbound continuation token."""
    payload = {
        _FIELD_VERSION: _TOKEN_VERSION,
        _FIELD_COLLECTION_RID: resource_id,
        _FIELD_QUERY_HASH: _hash_query_spec(query),
        _FIELD_FEEDRANGE_HASH: _hash_feed_range(feed_range_epk),
        _FIELD_CURRENT_FEEDRANGE: {"min": current_feedrange.min, "max": current_feedrange.max},
        _FIELD_REMAINING_FEEDRANGES: [
            {"min": r.min, "max": r.max} for r in remaining_feedranges
        ],
        _FIELD_BACKEND_CONTINUATION: backend_continuation,
    }
    return _encode_token(payload)


# ----- Pagination-loop helpers shared by sync and async ------------------
def _normalize_max_item_count(raw_max_item_count: Any) -> Optional[int]:
    """Normalize the caller's ``maxItemCount`` to a positive page-size cap or
    ``None`` (unbounded).

    Three rules, applied in order:
      * ``None`` (caller did not set one) -> ``None`` (unbounded - the
        backend decides page size; preserves pre-fix behavior).
      * Non-numeric values (e.g. a malformed string) -> ``None``. Raising
        here would change the error surface for callers that previously
        worked by accident; ``None`` keeps them working.
      * Any value ``<= 0`` -> ``None``. A zero or negative cap would make
        the pagination loop emit a continuation token without issuing any
        backend POST, which can produce an empty-page-with-continuation
        cycle on the caller side.
    """
    if raw_max_item_count is None:
        return None
    try:
        normalized = int(raw_max_item_count)
    except (TypeError, ValueError):
        return None
    if normalized <= 0:
        return None
    return normalized


def _apply_feedrange_request_headers(
    req_headers: MutableMapping[str, Any],
    overlapping: List[dict],
    partition_scope: routing_range.Range,
    current_feedrange: routing_range.Range,
    remaining_budget: Optional[int],
    inbound_continuation: Optional[str],
) -> None:
    """Populate ``req_headers`` for one backend POST against
    ``current_feed range`` and the partition currently serving it.

    Routes by ``PartitionKeyRangeID`` and only adds the EPK filter
    headers when the current feed range is a strict sub-range of the
    partition. Page size and continuation are explicitly set or
    cleared so leftover state from the previous iteration cannot leak.
    """
    pkr_id = overlapping[0]["id"]
    req_headers[http_constants.HttpHeaders.PartitionKeyRangeID] = pkr_id

    is_full_partition = (
        len(overlapping) == 1
        and current_feedrange.min == partition_scope.min
        and current_feedrange.max == partition_scope.max
    )
    if is_full_partition:
        req_headers.pop(http_constants.HttpHeaders.StartEpkString, None)
        req_headers.pop(http_constants.HttpHeaders.EndEpkString, None)
    else:
        req_headers[http_constants.HttpHeaders.StartEpkString] = current_feedrange.min
        req_headers[http_constants.HttpHeaders.EndEpkString] = current_feedrange.max
    req_headers[http_constants.HttpHeaders.ReadFeedKeyType] = "EffectivePartitionKeyRange"

    if remaining_budget is not None:
        req_headers[http_constants.HttpHeaders.PageSize] = str(remaining_budget)

    if inbound_continuation is not None:
        req_headers[http_constants.HttpHeaders.Continuation] = inbound_continuation
    else:
        req_headers.pop(http_constants.HttpHeaders.Continuation, None)


def _set_outbound_continuation(
    last_response_headers: MutableMapping[str, Any],
    resource_id: str,
    query: Any,
    feed_range_epk: routing_range.Range,
    current_feedrange: Optional[routing_range.Range],
    remaining_feedranges: List[routing_range.Range],
    backend_continuation: Optional[str],
) -> None:
    """Either clear the outbound continuation header (when the whole
    feed_range is drained) or stamp a fresh v=1 envelope onto it.

    ``current_feedrange = None`` is the call site's signal that the
    pagination loop ran out of feedranges; in that case the caller's
    ``by_page`` loop will see no continuation and terminate.
    """
    if current_feedrange is None:
        last_response_headers.pop(http_constants.HttpHeaders.Continuation, None)
        return
    last_response_headers[http_constants.HttpHeaders.Continuation] = (
        _build_outbound_token(
            resource_id,
            query,
            feed_range_epk,
            current_feedrange,
            remaining_feedranges,
            backend_continuation,
        )
    )

