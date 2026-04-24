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
# Token schema version so decoders can reject unknown envelope shapes.
_FIELD_VERSION = "v"
# Resource ID for the container that originally produced this token.
_FIELD_COLLECTION_RID = "cr"
# Fingerprint of query text + parameter values to prevent wrong-query resume.
_FIELD_QUERY_HASH = "qh"
# Fingerprint of the caller's input feed_range to prevent wrong-scope resume.
_FIELD_FEEDRANGE_HASH = "frh"
# The feedrange currently being read when this token was emitted.
_FIELD_CURRENT_FEEDRANGE = "cf"
# Feedranges that still remain after current feedrange is drained.
_FIELD_REMAINING_FEEDRANGES = "rf"
# Backend continuation for the current feedrange only (may be null).
_FIELD_BACKEND_CONTINUATION = "bc"
# Safety guard for repeated empty pages with no continuation/feedrange movement.
_MAX_CONSECUTIVE_NO_PROGRESS_PAGES = 1000


# ----- Hash helpers ------------------------------------------------------
def _stable_hash_128(payload: bytes) -> str:
    """Stable 128-bit hex digest.

    SHA-256 truncated to 32 hex characters. Switch to a vendored
    MurmurHash3-128 if cross-SDK token portability is ever required
    (it currently is not).

    :param payload: Bytes to hash.
    :returns: A 32-character hexadecimal digest.
    :rtype: str
    """
    return hashlib.sha256(payload).hexdigest()[:32]


def _hash_query_spec(query: Any) -> str:
    """Hash query text + (parameter name, JSON-canonical value) pairs.

    Resume requires the exact same query shape, not a semantically
    equivalent one. ``query`` may be either a string or the dict form
    produced by ``__CheckAndUnifyQueryFormat``.

    :param query: Query text or query spec dictionary.
    :returns: Stable hash for query text and parameters.
    :rtype: str
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

    :param feed_range: Input feed range.
    :returns: Stable feed range fingerprint.
    :rtype: str
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
    """JSON-serialize ``payload`` then base64-encode to a single ASCII blob.

    :param payload: Token envelope to serialize.
    :returns: Base64-encoded token string.
    :rtype: str
    """
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

    :param serialized: Encoded continuation token from the caller.
    :returns: Decoded token payload when valid; otherwise ``None``.
    :rtype: Optional[dict]
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
    them without checking for ``KeyError``.

    :param decoded: Decoded token payload to validate.
    """
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
    """Each persisted feedrange is a {'min': str, 'max': str} dict.

    :param range_dict: Serialized feed range dictionary.
    :param field_name: Field label used in validation messages.
    """
    if not isinstance(range_dict.get("min"), str) or not isinstance(range_dict.get("max"), str):
        raise ValueError(
            "Malformed feed_range continuation token: '{}' and '{}' are required.".format(
                f"{field_name}.min", f"{field_name}.max"
            )
        )


# ----- Feedrange / routing helpers ---------------------------------------
def _dict_to_range(range_dict: dict) -> routing_range.Range:
    """Convert a persisted ``{'min': ..., 'max': ...}`` dict back into a ``Range``.

    :param range_dict: Persisted feed range dictionary.
    :returns: Routing range instance.
    :rtype: ~azure.cosmos._routing.routing_range.Range
    """
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
    request.

    :param inbound: Decoded inbound token payload.
    :param resource_id: Current collection resource ID.
    :param query: Current query spec.
    :param feed_range_epk: Current feed range scope.
    """
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
    backend continuation out of a v1 token.

    :param inbound: Decoded inbound token payload.
    :returns: Current feedrange, remaining feedranges, and backend continuation.
    :rtype: tuple[~azure.cosmos._routing.routing_range.Range, list[~azure.cosmos._routing.routing_range.Range], Optional[str]]
    """
    current_feedrange = _dict_to_range(inbound[_FIELD_CURRENT_FEEDRANGE])
    remaining_feedranges = [_dict_to_range(r) for r in inbound[_FIELD_REMAINING_FEEDRANGES]]
    return current_feedrange, remaining_feedranges, inbound.get(_FIELD_BACKEND_CONTINUATION)


def _explode_feedrange_on_multi_overlap(
    current_feedrange: routing_range.Range,
    overlapping: List[dict],
    remaining_feedranges: List[routing_range.Range],
) -> Tuple[routing_range.Range, List[routing_range.Range], bool]:
    """If a saved feedrange now spans more than one physical partition
    (Cosmos split it), slice it into one sub-feedrange per child.

    :param current_feedrange: Feed range currently being resumed.
    :param overlapping: Partition ranges overlapping ``current_feedrange``.
    :param remaining_feedranges: Not-yet-visited feed ranges.
    :returns: New current feedrange, updated remaining feedranges, and split indicator.
    :rtype: tuple[~azure.cosmos._routing.routing_range.Range, list[~azure.cosmos._routing.routing_range.Range], bool]
    """
    if len(overlapping) <= 1:
        return current_feedrange, remaining_feedranges, False
    sub_feedranges = _derive_initial_feedranges(current_feedrange, overlapping)
    if not sub_feedranges:
        return current_feedrange, remaining_feedranges, False
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

    :param overlapping: Overlapping partition-range dictionaries.
    :param feedrange: Feed range used for error context.
    :returns: Original overlaps and their union scope.
    :rtype: tuple[list[dict], ~azure.cosmos._routing.routing_range.Range]
    """
    if not overlapping:
        raise RuntimeError(
            "Routing map returned no overlapping ranges for feedrange "
            "[{}, {}).".format(feedrange.min, feedrange.max)
        )
    min_inclusive = overlapping[0]["minInclusive"]
    max_exclusive = overlapping[0]["maxExclusive"]
    for overlap_range in overlapping[1:]:
        if overlap_range["minInclusive"] < min_inclusive:
            min_inclusive = overlap_range["minInclusive"]
        if overlap_range["maxExclusive"] > max_exclusive:
            max_exclusive = overlap_range["maxExclusive"]
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
    ordered by EPK ``min``.

    :param feed_range_epk: Requested feed range.
    :param overlapping: Overlapping partition-range dictionaries.
    :returns: Derived feed ranges ordered by ``min``.
    :rtype: list[~azure.cosmos._routing.routing_range.Range]
    """
    feedranges: List[routing_range.Range] = []
    for overlap_range in overlapping:
        partition_range = routing_range.Range.PartitionKeyRangeToRange(overlap_range)
        feedranges.append(
            routing_range.Range(
                range_min=max(partition_range.min, feed_range_epk.min),
                range_max=min(partition_range.max, feed_range_epk.max),
                isMinInclusive=True,
                isMaxInclusive=False,
            )
        )
    feedranges.sort(key=lambda feedrange_range: feedrange_range.min)
    return feedranges


class _FeedRangePaginationState:
    """Mutable state machine shared by sync and async feed-range loops."""

    def __init__(
        self,
        current_feedrange: Optional[routing_range.Range],
        remaining_feedranges: List[routing_range.Range],
        backend_continuation: Optional[str],
        remaining_page_item_count: Optional[int],
    ) -> None:
        self.current_feedrange = current_feedrange
        self.remaining_feedranges = remaining_feedranges
        self.backend_continuation = backend_continuation
        self.remaining_page_item_count = remaining_page_item_count

    @classmethod
    def from_inbound(
        cls,
        inbound: dict,
        remaining_page_item_count: Optional[int],
    ) -> "_FeedRangePaginationState":
        """Build state from a decoded inbound token.

        :param inbound: Decoded inbound token payload.
        :param remaining_page_item_count: Remaining items allowed in this logical page.
        :returns: Pagination state initialized for resume.
        :rtype: _FeedRangePaginationState
        """
        current_feedrange, remaining_feedranges, backend_continuation = _extract_resume_state(inbound)
        return cls(
            current_feedrange,
            remaining_feedranges,
            backend_continuation,
            remaining_page_item_count,
        )

    @classmethod
    def from_derived_feedranges(
        cls,
        feedranges: List[routing_range.Range],
        remaining_page_item_count: Optional[int],
    ) -> "_FeedRangePaginationState":
        """Build state from the first/remaining feedranges computed at startup.

        :param feedranges: Derived feedranges ordered by ``min``.
        :param remaining_page_item_count: Remaining items allowed in this logical page.
        :returns: Pagination state initialized for first request.
        :rtype: _FeedRangePaginationState
        """
        if not feedranges:
            return cls(None, [], None, remaining_page_item_count)
        return cls(feedranges[0], feedranges[1:], None, remaining_page_item_count)

    def can_issue_request(self) -> bool:
        """Whether another backend POST can be issued for this page.

        :returns: ``True`` when there is a current feedrange and remaining page items.
        :rtype: bool
        """
        if self.current_feedrange is None:
            return False
        if self.remaining_page_item_count is not None and self.remaining_page_item_count <= 0:
            return False
        return True

    def explode_on_multi_overlap(self, overlapping: List[dict]) -> bool:
        """Split current feedrange when routing now overlaps multiple partitions.

        :param overlapping: Routing overlaps for ``current_feedrange``.
        :returns: ``True`` when current feedrange was exploded.
        :rtype: bool
        """
        if self.current_feedrange is None:
            return False
        self.current_feedrange, self.remaining_feedranges, did_explode = _explode_feedrange_on_multi_overlap(
            self.current_feedrange,
            overlapping,
            self.remaining_feedranges,
        )
        if did_explode:
            self.backend_continuation = None
        return did_explode

    def apply_post_result(self, items_returned: int, backend_continuation: Optional[str]) -> None:
        """Apply one backend response to pagination state.

        :param items_returned: Number of documents returned by this POST.
        :param backend_continuation: Continuation for current feedrange.
        """
        if self.remaining_page_item_count is not None:
            self.remaining_page_item_count -= items_returned

        self.backend_continuation = backend_continuation
        if backend_continuation:
            return
        if not self.remaining_feedranges:
            self.current_feedrange = None
            return
        self.current_feedrange = self.remaining_feedranges.pop(0)

    def write_outbound_continuation(
        self,
        last_response_headers: MutableMapping[str, Any],
        resource_id: str,
        query: Any,
        feed_range_epk: routing_range.Range,
    ) -> None:
        """Set/clear outbound continuation header from current state.

        :param last_response_headers: Response headers to mutate.
        :param resource_id: Collection resource ID.
        :param query: Query spec used for hashing.
        :param feed_range_epk: Original request feed range.
        """
        _set_outbound_continuation(
            last_response_headers,
            resource_id,
            query,
            feed_range_epk,
            self.current_feedrange,
            self.remaining_feedranges,
            self.backend_continuation,
        )


def _build_outbound_token(
    resource_id: str,
    query: Any,
    feed_range_epk: routing_range.Range,
    current_feedrange: routing_range.Range,
    remaining_feedranges: List[routing_range.Range],
    backend_continuation: Optional[str],
) -> str:
    """Build and base64-encode the outbound continuation token.

    :param resource_id: Collection resource ID.
    :param query: Query spec used for hashing.
    :param feed_range_epk: Original feed range for the request.
    :param current_feedrange: Feed range currently in progress.
    :param remaining_feedranges: Feed ranges still pending.
    :param backend_continuation: Service continuation for current range.
    :returns: Encoded continuation token.
    :rtype: str
    """
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

    :param raw_max_item_count: Raw ``maxItemCount`` value from options.
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


def _extract_query_text(query: Any) -> Optional[str]:
    """Return SQL text from either a string query or query-spec dict.

    :param query: Query text or query spec dictionary.
    :returns: Query text when present.
    :rtype: Optional[str]
    """
    if isinstance(query, str):
        return query
    if isinstance(query, dict):
        query_text = query.get("query")
        if isinstance(query_text, str):
            return query_text
    return None


def _is_select_value_aggregate_query(query: Any) -> bool:
    """Detect SELECT VALUE aggregate shapes that return scalar merge fragments.

    :param query: Query text or query spec dictionary.
    :returns: ``True`` when query is SELECT VALUE with COUNT/SUM/MIN/MAX/AVG.
    :rtype: bool
    """
    query_text = _extract_query_text(query)
    if not query_text:
        return False
    normalized = " ".join(query_text.upper().split())
    if "SELECT VALUE" not in normalized:
        return False
    return any(token in normalized for token in ("COUNT(", "SUM(", "MIN(", "MAX(", "AVG("))


def _count_page_items_from_partial_result(
    partial_result: Optional[dict[str, Any]],
    query: Any,
) -> int:
    """Return how many logical items should consume the remaining page-item count.

    Aggregate partial rows are merge-input fragments, not final logical
    rows, so they should not consume page items and force an early break.

    :param partial_result: One backend POST result.
    :param query: Query text or query spec dictionary.
    :returns: Number of items to subtract from the remaining page-item count.
    :rtype: int
    """
    if not partial_result:
        return 0
    docs = partial_result.get("Documents")
    if not isinstance(docs, list):
        return 0
    if len(docs) != 1:
        return len(docs)

    row = docs[0]
    # Object/scalar aggregate partials must be merged across overlaps first.
    if isinstance(row, dict) and row.get("_aggregate") is not None:
        return 0
    # SELECT VALUE aggregates (COUNT/SUM/MIN/MAX/AVG) can surface a scalar
    # merge fragment per partition. Do not charge page items for those.
    if isinstance(row, (int, float, bool)) and _is_select_value_aggregate_query(query):
        return 0
    return 1


def _update_no_progress_page_count(
    current_no_progress_count: int,
    page_items_returned: int,
    previous_feedrange: Optional[routing_range.Range],
    previous_backend_continuation: Optional[str],
    current_feedrange: Optional[routing_range.Range],
    current_backend_continuation: Optional[str],
) -> int:
    """Track consecutive empty pages that still carry continuation.

    :param current_no_progress_count: Current consecutive no-progress page count.
    :param page_items_returned: Number of logical page items returned this iteration.
    :param previous_feedrange: Feedrange before processing this response.
    :param previous_backend_continuation: Backend continuation before response.
    :param current_feedrange: Feedrange after processing this response.
    :param current_backend_continuation: Backend continuation after response.
    :returns: Updated consecutive no-progress page count.
    :rtype: int
    """
    if page_items_returned > 0:
        return 0
    if current_backend_continuation is None:
        return 0
    if current_feedrange != previous_feedrange:
        return 0
    if current_backend_continuation != previous_backend_continuation:
        return 0

    # No logical rows and no cursor/feedrange movement: caller made no progress.
    if current_backend_continuation is not None:
        return current_no_progress_count + 1
    return 0


def _apply_feedrange_request_headers(
    req_headers: MutableMapping[str, Any],
    overlapping: List[dict],
    partition_scope: routing_range.Range,
    current_feedrange: routing_range.Range,
    remaining_page_item_count: Optional[int],
    inbound_continuation: Optional[str],
) -> None:
    """Populate ``req_headers`` for one backend POST against
    ``current_feedrange`` and the partition currently serving it.

    Routes by ``PartitionKeyRangeID`` and only adds the EPK filter
    headers when the current feed range is a strict sub-range of the
    partition. Page size and continuation are explicitly set or
    cleared so leftover state from the previous iteration cannot leak.

    :param req_headers: Mutable request headers to populate.
    :param overlapping: Overlapping partition-range dictionaries.
    :param partition_scope: Union scope for overlapping partitions.
    :param current_feedrange: Feed range for the current backend request.
    :param remaining_page_item_count: Remaining items allowed in this logical page.
    :param inbound_continuation: Continuation token for backend request.
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

    if remaining_page_item_count is not None:
        req_headers[http_constants.HttpHeaders.PageSize] = str(remaining_page_item_count)
    else:
        req_headers.pop(http_constants.HttpHeaders.PageSize, None)

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

    :param last_response_headers: Mutable response headers to update.
    :param resource_id: Collection resource ID.
    :param query: Query spec used for hashing.
    :param feed_range_epk: Original feed range for this query.
    :param current_feedrange: Current feed range or ``None`` when complete.
    :param remaining_feedranges: Feed ranges that remain after current.
    :param backend_continuation: Service continuation for current feed range.
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
