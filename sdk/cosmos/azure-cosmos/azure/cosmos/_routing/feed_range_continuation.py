# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Shared helpers for the structured ``feed_range`` continuation token.

Both sync and async ``__QueryFeed`` implementations use this module for
token wire format, request fingerprinting, and feed-range routing helpers.

The token stores an ordered ``c`` list of ``{min, max, bc}`` entries.
Pagination reads and updates the queue head, then advances when the head
is drained.
"""

import base64
import binascii
import json
from collections import deque
from typing import Any, Deque, Iterable, List, MutableMapping, Optional, Tuple

from .. import http_constants
from .._cosmos_integers import _UInt128
from .._cosmos_murmurhash3 import murmurhash3_128
from .._query_aggregate_utils import _AggregatePartialClassification, _classify_aggregate_partial
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
# Ordered list of {min, max, bc} entries for the requested feed range.
# Iteration state comes from the list order; there is no separate
# top-level "current" field.
_FIELD_CONTINUATIONS = "c"
# Backend continuation for ONE entry. Lives INSIDE each ``c[i]`` entry,
# never at the envelope level. ``null`` means "this sub-range has not
# been started, or has been fully drained".
_FIELD_BACKEND_CONTINUATION = "bc"
# Observability threshold for repeated empty pages with no continuation/feedrange movement.
# This is warning-only (not a hard stop); pagination continues until the queue drains.
_MAX_CONSECUTIVE_NO_PROGRESS_PAGES = 1000
# Safety guard for pathological split re-resolution loops.
_MAX_MULTI_OVERLAP_EXPLODE_ITERATIONS = 50


# ----- Hash helpers ------------------------------------------------------
def _stable_hash_128(payload: bytes) -> str:
    """Stable 128-bit hex digest of ``payload``.

    Uses ``MurmurHash3_128`` (the same helper ``partition_key.py`` uses
    for EPK routing). The fingerprint is non-cryptographic and used
    only for an equality check inside ``_decode_token``: on resume the
    SDK recomputes the same hash from the live call's inputs and
    raises if it does not match the value baked into the saved token.
    A cryptographic hash buys nothing here because the field is never
    sent to the service and is never used as proof of input.

    :param payload: Bytes to hash.
    :type payload: bytes
    :returns: A 32-character hexadecimal digest.
    :rtype: str
    """
    return murmurhash3_128(bytearray(payload), _UInt128(0, 0)).as_hex()


def _hash_query_spec(query: Any) -> str:
    """Hash query text + (parameter name, JSON-canonical value) pairs.

    Resume requires the exact same query shape, not a semantically
    equivalent one. ``query`` may be either a string or the dict form
    produced by ``__CheckAndUnifyQueryFormat``.

    :param query: Query text or query spec dictionary.
    :type query: str or dict
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

    The input is first converted to a standard ``[min, max)`` form via
    ``Range.to_normalized_range()`` (idempotent — returns ``self`` when
    already normalized). The canonical JSON intentionally carries only
    ``min`` and ``max``: under the normalized form the inclusivity
    flags are constants (``True``/``False``), so hashing them adds no
    signal and would only mask the fact that the fingerprint identifies
    the *logical EPK interval*, not the on-the-wire representation of
    the bounds. Two ``Range`` objects describing the same logical
    interval (e.g. ``[A, B)`` and the equivalent ``(A-1, B-1]``) hash
    equal.

    :param feed_range: Input feed range.
    :type feed_range: ~azure.cosmos._routing.routing_range.Range
    :returns: Stable feed range fingerprint.
    :rtype: str
    """
    normalized = feed_range.to_normalized_range()
    canonical = json.dumps(
        {"min": normalized.min, "max": normalized.max},
        sort_keys=True,
        separators=(",", ":"),
    )
    return _stable_hash_128(canonical.encode("utf-8"))


# ----- Token codec -------------------------------------------------------
def _encode_token(payload: dict) -> str:
    """JSON-serialize ``payload`` then base64-encode to a single ASCII blob.

    :param payload: Token envelope to serialize.
    :type payload: dict
    :returns: Base64-encoded token string.
    :rtype: str
    """
    return base64.b64encode(
        json.dumps(payload, separators=(",", ":")).encode("utf-8")
    ).decode("ascii")


def _decode_token(serialized: Optional[str]) -> Optional[dict]:
    """Decode a continuation string into our token dict, or ``None``.

    Returns ``None`` when ``serialized`` is empty or not in our shape.

    Raises ``ValueError`` only when the input parses as our shape but is
    structurally invalid (for example unknown ``v`` or missing fields).

    :param serialized: Encoded continuation token from the caller.
    :type serialized: Optional[str]
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
    :type decoded: dict
    """
    if not isinstance(decoded.get(_FIELD_COLLECTION_RID), str):
        raise ValueError("Malformed feed_range continuation token: 'cr' is required.")
    if not isinstance(decoded.get(_FIELD_QUERY_HASH), str):
        raise ValueError("Malformed feed_range continuation token: 'qh' is required.")
    if not isinstance(decoded.get(_FIELD_FEEDRANGE_HASH), str):
        raise ValueError("Malformed feed_range continuation token: 'frh' is required.")
    # ``bc`` must be per-entry inside ``c[i]``; top-level ``bc`` is invalid.
    if _FIELD_BACKEND_CONTINUATION in decoded:
        raise ValueError(
            "Malformed feed_range continuation token: top-level 'bc' is not "
            "supported; 'bc' must live inside each 'c' entry."
        )

    entries = decoded.get(_FIELD_CONTINUATIONS)
    if not isinstance(entries, list) or not entries:
        # Producers clear the continuation header when drained, so
        # an on-wire token must contain at least one entry.
        raise ValueError(
            "Malformed feed_range continuation token: '{}' is required and "
            "must be a non-empty list.".format(_FIELD_CONTINUATIONS)
        )
    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ValueError(
                "Malformed feed_range continuation token: '{}[{}]' must be an object.".format(
                    _FIELD_CONTINUATIONS, idx
                )
            )
        _validate_range_dict(entry, "{}[{}]".format(_FIELD_CONTINUATIONS, idx))


def _validate_range_dict(range_dict: dict, field_name: str) -> None:
    """Each persisted feedrange is a {'min': str, 'max': str, 'bc': str|null} dict.

    :param range_dict: Serialized feed range dictionary.
    :type range_dict: dict
    :param field_name: Field label used in validation messages.
    :type field_name: str
    """
    if not isinstance(range_dict.get("min"), str) or not isinstance(range_dict.get("max"), str):
        raise ValueError(
            "Malformed feed_range continuation token: '{}' and '{}' are required.".format(
                f"{field_name}.min", f"{field_name}.max"
            )
        )
    if _FIELD_BACKEND_CONTINUATION not in range_dict:
        raise ValueError(
            "Malformed feed_range continuation token: '{}.bc' is required (use null when absent).".format(
                field_name
            )
        )
    bc_value = range_dict[_FIELD_BACKEND_CONTINUATION]
    if bc_value is not None and not isinstance(bc_value, str):
        raise ValueError(
            "Malformed feed_range continuation token: '{}.bc' must be a string or null.".format(
                field_name
            )
        )


# ----- Feedrange / routing helpers ---------------------------------------
def _dict_to_range(range_dict: dict) -> routing_range.Range:
    """Convert a persisted ``{'min': ..., 'max': ...}`` dict back into a ``Range``.

    :param range_dict: Persisted feed range dictionary.
    :type range_dict: dict
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
    expected_query_hash: Optional[str] = None,
    expected_feedrange_hash: Optional[str] = None,
) -> None:
    """Confirm the inbound token was created for the same collection,
    query, and feed_range the current call is using. If any of the
    three fingerprints disagrees, raise ``ValueError`` so the caller
    finds out instead of silently getting rows from a different
    request.

    :param inbound: Decoded inbound token payload.
    :type inbound: dict
    :param resource_id: Current collection resource ID.
    :type resource_id: str
    :param query: Current query spec.
    :type query: str or dict
    :param feed_range_epk: Current feed range scope.
    :type feed_range_epk: ~azure.cosmos._routing.routing_range.Range
    :param expected_query_hash: Precomputed query hash to validate against inbound token.
    :type expected_query_hash: Optional[str]
    :param expected_feedrange_hash: Precomputed feed_range hash to validate against inbound token.
    :type expected_feedrange_hash: Optional[str]
    """
    expected_qh = expected_query_hash or _hash_query_spec(query)
    expected_frh = expected_feedrange_hash or _hash_feed_range(feed_range_epk)
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


def _should_bridge_legacy_continuation(
    inbound_serialized_continuation: Optional[str],
    inbound_token_payload: Optional[dict],
    is_full_pk_structured_scope: bool,
    is_single_partition_scope: bool,
) -> bool:
    """Whether to bridge an inbound legacy continuation into pagination state.

    We bridge only when the inbound continuation exists, did not decode as
    structured ``v=1`` (legacy/opaque token), and the current request scope can
    be represented safely by a single legacy continuation slot:

    * full-PK structured scope (always single partition), or
    * non-full-PK scope that currently maps to one physical partition.
    """
    return bool(
        inbound_serialized_continuation
        and inbound_token_payload is None
        and (is_full_pk_structured_scope or is_single_partition_scope)
    )


def _extract_resume_queue(
    inbound: dict,
) -> List[Tuple[routing_range.Range, Optional[str]]]:
    """Decode the ``c`` list into an ordered list of ``(range, bc)`` pairs.

    The wire format stores a single ordered ``c`` list of
    ``{min, max, bc}`` entries.

    :param inbound: Decoded inbound token payload.
    :type inbound: dict
    :returns: Ordered list of ``(range, backend_continuation)`` pairs.
    :rtype: list[tuple[~azure.cosmos._routing.routing_range.Range, Optional[str]]]
    """
    return [
        (_dict_to_range(entry), entry.get(_FIELD_BACKEND_CONTINUATION))
        for entry in inbound[_FIELD_CONTINUATIONS]
    ]


def _build_scope_from_overlaps(
    overlapping: List[dict], feedrange: routing_range.Range
) -> Tuple[List[dict], routing_range.Range]:
    """Compute the smallest EPK ``Range`` that covers every one of the
    overlapping physical partitions, and return both the original
    overlaps and that combined range.

    Both the sync and async pagination paths call this directly after
    awaiting / invoking ``routing_map_provider.get_overlapping_ranges``
    themselves, so the live lookup stays at the call site (sync vs.
    async) and the pure combine logic is shared here.

    :param overlapping: Overlapping partition-range dictionaries.
    :type overlapping: list[dict]
    :param feedrange: Feed range used for error context.
    :type feedrange: ~azure.cosmos._routing.routing_range.Range
    :returns: Original overlaps and the combined range covering them.
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
    :type feed_range_epk: ~azure.cosmos._routing.routing_range.Range
    :param overlapping: Overlapping partition-range dictionaries.
    :type overlapping: list[dict]
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
    """Tracks where a feed_range query is up to between page calls.

    Holds a single ordered queue of ``(sub-range, backend continuation)``
    pairs. The pagination loop:

      * peeks the queue head to learn the next sub-range to POST and
        the backend continuation (if any) to send with it,
      * updates the head's backend continuation when the backend
        returns a non-null one,
      * pops the head when the sub-range is drained,
      * on a partition split, replaces the head with one entry per
        child sub-range (each inheriting the parent's backend continuation).

    There is no separate "current vs. remaining" split. The head is
    ``queue[0]`` and later entries are queued behind it.

    Split-child insertion is tail-based so existing queued ranges
    remain ahead of newly discovered children.

    Not thread-safe. One instance is created per ``query_items`` call
    and is mutated only by that call's pagination loop (sync or async)
    — never shared across threads or concurrent tasks.
    """

    def __init__(
        self,
        queue: Iterable[Tuple[routing_range.Range, Optional[str]]],
        page_size_hint: Optional[int],
    ) -> None:
        self.queue: Deque[Tuple[routing_range.Range, Optional[str]]] = deque(queue)
        self.page_size_hint = page_size_hint

    @classmethod
    def from_inbound(
        cls,
        inbound: dict,
        page_size_hint: Optional[int],
    ) -> "_FeedRangePaginationState":
        """Build state from a decoded inbound token.

        :param inbound: Decoded inbound token payload.
        :type inbound: dict
        :param page_size_hint: Request page-size hint propagated to backend POSTs.
        :type page_size_hint: Optional[int]
        :returns: Pagination state initialized for resume.
        :rtype: _FeedRangePaginationState
        """
        return cls(_extract_resume_queue(inbound), page_size_hint)

    @classmethod
    def from_derived_feedranges(
        cls,
        feedranges: Iterable[routing_range.Range],
        page_size_hint: Optional[int],
    ) -> "_FeedRangePaginationState":
        """Build state from feedranges computed at startup (no backend
        continuations yet — every entry starts with ``bc = None``).

        :param feedranges: Derived feedranges ordered by ``min``.
        :type feedranges: Iterable[~azure.cosmos._routing.routing_range.Range]
        :param page_size_hint: Request page-size hint propagated to backend POSTs.
        :type page_size_hint: Optional[int]
        :returns: Pagination state initialized for first request.
        :rtype: _FeedRangePaginationState
        """
        return cls(((fr, None) for fr in feedranges), page_size_hint)

    @classmethod
    def from_single_feedrange_with_continuation(
        cls,
        feedrange: routing_range.Range,
        backend_continuation: Optional[str],
        page_size_hint: Optional[int],
    ) -> "_FeedRangePaginationState":
        """Build state for one feedrange where a backend continuation
        already exists.

        Used for legacy-token compatibility on full-PK queries:
        we keep the decoder strict, then bridge a legacy continuation
        string into the queue head's ``bc`` slot for the single target
        range.

        :param feedrange: Single feedrange to seed.
        :type feedrange: ~azure.cosmos._routing.routing_range.Range
        :param backend_continuation: Existing backend continuation for the range.
        :type backend_continuation: Optional[str]
        :param page_size_hint: Request page-size hint propagated to backend POSTs.
        :type page_size_hint: Optional[int]
        :returns: Pagination state initialized with one queued entry.
        :rtype: _FeedRangePaginationState
        """
        return cls(((feedrange, backend_continuation),), page_size_hint)

    @property
    def head_range(self) -> Optional[routing_range.Range]:
        """The sub-range at the head of the queue (the one the next
        backend POST will target), or ``None`` when the queue is drained.
        """
        return self.queue[0][0] if self.queue else None

    @property
    def head_bc(self) -> Optional[str]:
        """Backend continuation paired with the head sub-range, or
        ``None`` if the head has not been started yet (or has nothing
        more to fetch).
        """
        return self.queue[0][1] if self.queue else None

    def can_issue_request(self) -> bool:
        """Whether another backend POST can be issued for this page.

        :returns: ``True`` when the queue is non-empty.
        :rtype: bool
        """
        return bool(self.queue)

    def explode_on_multi_overlap(self, overlapping: List[dict]) -> bool:
        """If the head sub-range now spans more than one physical
        partition (Cosmos split it since the token was minted),
        replace the head with one entry per child sub-range and carry
        the parent backend continuation onto each child.

        Dequeue the parent and append child entries at the tail
        (preserving child EPK order). Each child inherits the
        parent ``bc`` so resume can continue after a split without
        replaying the entire child feed range.

        :param overlapping: Routing overlaps for the head sub-range.
        :type overlapping: list[dict]
        :returns: ``True`` when the head was split into multiple children.
        :rtype: bool
        """
        if not self.queue or len(overlapping) <= 1:
            return False
        head_range, parent_bc = self.queue[0]
        sub_feedranges = _derive_initial_feedranges(head_range, overlapping)
        if not sub_feedranges:
            return False
        self.queue.popleft()
        # Keep existing tail entries ahead of split children.
        for sub in sub_feedranges:
            self.queue.append((sub, parent_bc))
        return True

    def apply_post_result(self, items_returned: int, backend_continuation: Optional[str]) -> None:
        """Apply one backend response to the queue.

        :param items_returned: Number of logical rows returned by this POST.
        :type items_returned: int
        :param backend_continuation: Backend continuation for the head
            sub-range (``None`` when the head is drained).
        :type backend_continuation: Optional[str]
        """
        # Kept for call-site API symmetry and observability; page-size hints are
        # no longer decremented between backend requests.
        _ = items_returned
        if not self.queue:
            return
        head_range, _ = self.queue[0]
        if backend_continuation is not None:
            # Update head's bc in place; head sub-range itself is unchanged.
            self.queue[0] = (head_range, backend_continuation)
        else:
            # Head sub-range fully drained; advance to next entry.
            self.queue.popleft()

    def write_outbound_continuation(
        self,
        last_response_headers: MutableMapping[str, Any],
        resource_id: str,
        query: Any,
        feed_range_epk: routing_range.Range,
        query_hash: Optional[str] = None,
        feedrange_hash: Optional[str] = None,
    ) -> None:
        """Set or clear the outbound continuation header from the queue.

        Empty queue means the pagination loop ran out of sub-ranges; the
        header is removed and the caller's ``by_page`` loop terminates.
        Otherwise the entire queue is serialized as a fresh v=1 envelope
        via ``_build_outbound_token``.

        :param last_response_headers: Response headers to mutate.
        :type last_response_headers: MutableMapping[str, Any]
        :param resource_id: Collection resource ID.
        :type resource_id: str
        :param query: Query spec used for hashing.
        :type query: str or dict
        :param feed_range_epk: Original request feed range.
        :type feed_range_epk: ~azure.cosmos._routing.routing_range.Range
        :param query_hash: Optional precomputed query hash to embed in the outbound token.
        :type query_hash: Optional[str]
        :param feedrange_hash: Optional precomputed feed_range hash to embed in the outbound token.
        :type feedrange_hash: Optional[str]
        """
        if not self.queue:
            last_response_headers.pop(http_constants.HttpHeaders.Continuation, None)
            return
        last_response_headers[http_constants.HttpHeaders.Continuation] = _build_outbound_token(
            resource_id,
            query,
            feed_range_epk,
            self.queue,
            query_hash=query_hash,
            feedrange_hash=feedrange_hash,
        )


def _write_query_outbound_continuation(
    last_response_headers: MutableMapping[str, Any],
    pagination_state: _FeedRangePaginationState,
    resource_id: str,
    query: Any,
    feed_range_epk: routing_range.Range,
    is_full_pk_structured_scope: bool,
    emit_legacy_for_single_partition: bool,
    query_hash: Optional[str],
    feedrange_hash: Optional[str],
) -> None:
    """Write outbound continuation for feed-range pagination.

    Full-PK queries always emit the legacy single-string continuation
    so persisted bookmarks remain readable by older SDK versions.
    Feed-range/prefix queries emit legacy continuation when the caller's
    input scope currently maps to a single physical partition; otherwise
    they emit the structured envelope.

    :param last_response_headers: Response headers to mutate.
    :type last_response_headers: MutableMapping[str, Any]
    :param pagination_state: Current pagination state for this request.
    :type pagination_state: _FeedRangePaginationState
    :param resource_id: Collection resource ID.
    :type resource_id: str
    :param query: Query text/spec used for hash identity.
    :type query: Any
    :param feed_range_epk: Original request feed range.
    :type feed_range_epk: ~azure.cosmos._routing.routing_range.Range
    :param is_full_pk_structured_scope: Whether request scope is full-PK on structured path.
    :type is_full_pk_structured_scope: bool
    :param emit_legacy_for_single_partition: Whether non-full-PK scope currently maps to a
        single physical partition and can safely emit legacy continuation.
    :type emit_legacy_for_single_partition: bool
    :param query_hash: Precomputed query hash for outbound token identity, or ``None`` to
        compute lazily inside the structured-token writer when needed.
    :type query_hash: Optional[str]
    :param feedrange_hash: Precomputed feed range hash for outbound token identity, or
        ``None`` to compute lazily inside the structured-token writer when needed.
    :type feedrange_hash: Optional[str]
    :returns: None. Mutates ``last_response_headers`` in place.
    :rtype: None
    """
    if is_full_pk_structured_scope or emit_legacy_for_single_partition:
        legacy_outbound = pagination_state.head_bc
        if legacy_outbound is None:
            last_response_headers.pop(http_constants.HttpHeaders.Continuation, None)
        else:
            last_response_headers[http_constants.HttpHeaders.Continuation] = legacy_outbound
        return
    pagination_state.write_outbound_continuation(
        last_response_headers,
        resource_id,
        query,
        feed_range_epk,
        query_hash=query_hash,
        feedrange_hash=feedrange_hash,
    )



def _build_outbound_token(
    resource_id: str,
    query: Any,
    feed_range_epk: routing_range.Range,
    entries: Iterable[Tuple[routing_range.Range, Optional[str]]],
    query_hash: Optional[str] = None,
    feedrange_hash: Optional[str] = None,
) -> str:
    """Build and base64-encode the outbound continuation token from a
    queue of ``(range, backend_continuation)`` entries.

    Persists the queue as the wire-format ``c`` list in head-first order.

    :param resource_id: Collection resource ID.
    :type resource_id: str
    :param query: Query spec used for hashing.
    :type query: str or dict
    :param feed_range_epk: Original feed range for the request.
    :type feed_range_epk: ~azure.cosmos._routing.routing_range.Range
    :param entries: Ordered ``(range, bc)`` pairs to serialize.
    :type entries: Iterable[tuple[~azure.cosmos._routing.routing_range.Range, Optional[str]]]
    :param query_hash: Optional precomputed query hash to persist in the token envelope.
    :type query_hash: Optional[str]
    :param feedrange_hash: Optional precomputed feed_range hash to persist in the token envelope.
    :type feedrange_hash: Optional[str]
    :returns: Encoded continuation token.
    :rtype: str
    """
    payload = {
        _FIELD_VERSION: _TOKEN_VERSION,
        _FIELD_COLLECTION_RID: resource_id,
        _FIELD_QUERY_HASH: query_hash or _hash_query_spec(query),
        _FIELD_FEEDRANGE_HASH: feedrange_hash or _hash_feed_range(feed_range_epk),
        _FIELD_CONTINUATIONS: [
            {"min": r.min, "max": r.max, _FIELD_BACKEND_CONTINUATION: bc}
            for r, bc in entries
        ],
    }
    return _encode_token(payload)


# ----- Pagination-loop helpers shared by sync and async ------------------
def _normalize_max_item_count(raw_max_item_count: Any) -> Optional[int]:
    """Normalize the caller's ``maxItemCount`` to a positive page-size cap or
    ``None`` (unbounded).

    Three rules, applied in order:
      * ``None`` (caller did not set one) -> ``None`` (unbounded; backend
        decides page size).
      * Non-numeric values (e.g. a malformed string) -> ``None``. Raising
        here would change the error surface for callers that previously
        worked by accident; ``None`` keeps them working.
      * Any value ``<= 0`` -> ``None``. A zero or negative cap would make
        the pagination loop emit a continuation token without issuing any
        backend POST, which can produce an empty-page-with-continuation
        cycle on the caller side.

    :param raw_max_item_count: Raw ``maxItemCount`` value from options.
    :type raw_max_item_count: Any
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


def _count_page_items_from_partial_result(
    partial_result: Optional[dict[str, Any]],
    query: Any,
) -> int:
    """Return how many logical items should consume the remaining page-item count.

    Aggregate partial rows are merge-input fragments, not final logical
    rows, so they should not consume page items and force an early break.

    :param partial_result: One backend POST result.
    :type partial_result: Optional[dict[str, Any]]
    :param query: Query text or query spec dictionary.
    :type query: Any
    :returns: Number of items to subtract from the remaining page-item count.
    :rtype: int
    """
    if not partial_result:
        return 0
    docs = partial_result.get("Documents")
    if not isinstance(docs, list):
        return 0
    if len(docs) != 1:
        # Cosmos backend invariant: aggregate partial fragments are emitted as
        # single-element arrays. Non-singleton arrays are treated as regular rows.
        return len(docs)

    # Aggregate partials must be merged across overlaps before they count as rows.
    if _classify_aggregate_partial(docs, query) != _AggregatePartialClassification.NONE:
        return 0
    return 1


def _update_no_progress_page_count(
    current_no_progress_count: int,
    page_items_returned: int,
    previous_feedrange: Optional[routing_range.Range],
    previous_backend_continuation: Optional[str],
    head_feedrange: Optional[routing_range.Range],
    head_backend_continuation: Optional[str],
) -> int:
    """Track consecutive empty pages that still carry continuation.

    :param current_no_progress_count: Current consecutive no-progress page count.
    :type current_no_progress_count: int
    :param page_items_returned: Number of logical page items returned this iteration.
    :type page_items_returned: int
    :param previous_feedrange: Feedrange before processing this response.
    :type previous_feedrange: Optional[~azure.cosmos._routing.routing_range.Range]
    :param previous_backend_continuation: Backend continuation before response.
    :type previous_backend_continuation: Optional[str]
    :param head_feedrange: Feedrange after processing this response.
    :type head_feedrange: Optional[~azure.cosmos._routing.routing_range.Range]
    :param head_backend_continuation: Backend continuation after response.
    :type head_backend_continuation: Optional[str]
    :returns: Updated consecutive no-progress page count.
    :rtype: int
    """
    def _range_bounds(rng: Optional[routing_range.Range]) -> Optional[Tuple[str, str]]:
        if rng is None:
            return None
        return rng.min, rng.max

    if page_items_returned > 0:
        return 0
    if head_backend_continuation is None:
        return 0
    if _range_bounds(head_feedrange) != _range_bounds(previous_feedrange):
        return 0
    if head_backend_continuation != previous_backend_continuation:
        return 0

    # No logical rows and no cursor/feedrange movement: caller made no progress.
    return current_no_progress_count + 1


def _increment_explode_iterations_or_raise(current_explode_iterations: int) -> int:
    """Increment split re-resolution iteration count or raise on overflow.

    :param current_explode_iterations: Current explode-loop iteration count.
    :type current_explode_iterations: int
    :returns: Incremented explode-loop iteration count.
    :rtype: int
    """
    updated_iterations = current_explode_iterations + 1
    if updated_iterations > _MAX_MULTI_OVERLAP_EXPLODE_ITERATIONS:
        raise RuntimeError(
            "Exceeded {} split re-resolution iterations while expanding overlapping "
            "feed ranges. This indicates a stale/corrupted routing map response."
            .format(_MAX_MULTI_OVERLAP_EXPLODE_ITERATIONS)
        )
    return updated_iterations


def _apply_feedrange_request_headers(
    req_headers: MutableMapping[str, Any],
    overlapping: List[dict],
    partition_scope: routing_range.Range,
    head_feedrange: routing_range.Range,
    page_size_hint: Optional[int],
    inbound_continuation: Optional[str],
) -> None:
    """Populate ``req_headers`` for one backend POST against
    ``head_feedrange`` and the partition currently serving it.

    Routes by ``PartitionKeyRangeID`` and only adds the EPK filter
    headers when the current feed range is a strict sub-range of the
    partition. Page size and continuation are explicitly set or
    cleared so leftover state from the previous iteration cannot leak.

    :param req_headers: Mutable request headers to populate.
    :type req_headers: MutableMapping[str, Any]
    :param overlapping: Overlapping partition-range dictionaries.
    :type overlapping: list[dict]
    :param partition_scope: Union scope for overlapping partitions.
    :type partition_scope: ~azure.cosmos._routing.routing_range.Range
    :param head_feedrange: Feed range for the current backend request.
    :type head_feedrange: ~azure.cosmos._routing.routing_range.Range
    :param page_size_hint: Request page-size hint for the backend POST.
    :type page_size_hint: Optional[int]
    :param inbound_continuation: Continuation token for backend request.
    :type inbound_continuation: Optional[str]
    """
    pkr_id = overlapping[0]["id"]
    req_headers[http_constants.HttpHeaders.PartitionKeyRangeID] = pkr_id

    is_full_partition = (
        len(overlapping) == 1
        and head_feedrange.min == partition_scope.min
        and head_feedrange.max == partition_scope.max
    )
    if is_full_partition:
        req_headers.pop(http_constants.HttpHeaders.StartEpkString, None)
        req_headers.pop(http_constants.HttpHeaders.EndEpkString, None)
    else:
        req_headers[http_constants.HttpHeaders.StartEpkString] = head_feedrange.min
        req_headers[http_constants.HttpHeaders.EndEpkString] = head_feedrange.max
    req_headers[http_constants.HttpHeaders.ReadFeedKeyType] = "EffectivePartitionKeyRange"

    if page_size_hint is not None:
        req_headers[http_constants.HttpHeaders.PageSize] = str(page_size_hint)
    else:
        req_headers.pop(http_constants.HttpHeaders.PageSize, None)

    if inbound_continuation is not None:
        req_headers[http_constants.HttpHeaders.Continuation] = inbound_continuation
    else:
        req_headers.pop(http_constants.HttpHeaders.Continuation, None)
