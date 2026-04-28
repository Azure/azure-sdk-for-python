# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Shared helpers for the structured ``feed_range`` continuation token.

Both the sync (``azure.cosmos._cosmos_client_connection``) and async
(``azure.cosmos.aio._cosmos_client_connection_async``) ``__QueryFeed``
implementations import from this module so that there is exactly one
source of truth for token wire-format, hash fingerprinting, and
routing-scope resolution. Only the pagination loop differs between the
two paths (sync vs. ``await``); the token logic does not.

The saved continuation tracks progress through the
caller's input ``feed_range`` as a single ordered list of
sub-ranges, each carrying its own backend continuation. We call
each entry a ``feedrange`` because it is exactly that — a sub-range
of the caller's ``feed_range``, represented as the same
``routing_range.Range`` type the rest of the routing code uses.
The wire format intentionally has no privileged "current" /
"remaining" split; iteration position is an in-memory concern of
``_FeedRangePaginationState``. This matches the Java SDK's
``FeedRangeCompositeContinuationImpl`` and lets a future
non-sequential / parallel-fetch loop fill any subset of the
per-entry backend continuations without a wire-format version bump.
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
# Ordered list of {min, max, bc} entries — one per sub-range of the
# caller's input feed_range. The wire format intentionally has NO
# privileged "current" slot: iteration position ("which slice am I on")
# is an in-memory concern of ``_FeedRangePaginationState`` and is
# reconstructed from the head of this list on resume. Modeled on the
# Java SDK's ``FeedRangeCompositeContinuationImpl`` (which persists a
# single ``Queue<CompositeContinuationToken>`` and likewise has no
# "current" field). This shape scales to non-sequential merges /
# parallel fan-out without a wire-format version bump: any subset of
# entries may carry a non-null ``bc`` simultaneously, all entries are
# structurally equal, and drain order is whatever the producer chooses.
_FIELD_CONTINUATIONS = "c"
# Backend continuation for ONE entry. Lives INSIDE each ``c[i]`` entry,
# never at the envelope level. ``null`` means "this sub-range has not
# been started, or has been fully drained".
_FIELD_BACKEND_CONTINUATION = "bc"
# Safety guard for repeated empty pages with no continuation/feedrange movement.
_MAX_CONSECUTIVE_NO_PROGRESS_PAGES = 1000


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

    :param feed_range: Input feed range.
    :type feed_range: ~azure.cosmos._routing.routing_range.Range
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
    A pre-fix opaque continuation falls into that bucket and the caller
    treats it as ``continuation_token=None`` (start fresh).

    Raises ``ValueError`` only when the input parses as our shape but
    is structurally invalid - an unknown ``v`` value or a missing
    required field. We fail loudly there so a token from a future SDK
    or a corrupted blob is not silently coerced into "start fresh".

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
    # Reject pre-fix shape that carried ``bc`` at the envelope level.
    # ``bc`` now lives INSIDE each ``c[i]`` entry; accepting an
    # envelope-level ``bc`` here would silently drop it on the floor.
    if _FIELD_BACKEND_CONTINUATION in decoded:
        raise ValueError(
            "Malformed feed_range continuation token: top-level 'bc' is not "
            "supported; 'bc' must live inside each 'c' entry."
        )

    entries = decoded.get(_FIELD_CONTINUATIONS)
    if not isinstance(entries, list) or not entries:
        # An empty list would mean "drained" — but the producer clears
        # the outbound continuation header in that case (see
        # ``_FeedRangePaginationState.write_outbound_continuation``),
        # so a token whose ``c`` list is empty cannot legitimately
        # exist on the wire.
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
) -> Tuple[routing_range.Range, Optional[str], List[routing_range.Range], List[Optional[str]]]:
    """Pull the head sub-range, its backend continuation, the
    remaining sub-ranges, and each remaining sub-range's backend
    continuation out of a v1 token.

    The wire format persists a single ordered list ``c`` of
    ``{min, max, bc}`` entries with no privileged "current" slot.
    The sequential pagination loop treats ``c[0]`` as the in-flight
    slice and ``c[1:]`` as queued behind it; a future parallel /
    non-sequential merge loop is free to drain entries in any order
    because every entry is structurally equal on the wire.

    :param inbound: Decoded inbound token payload.
    :type inbound: dict
    :returns: Head sub-range, head backend continuation,
        tail sub-ranges, and tail backend continuations
        (parallel to the tail sub-ranges).
    :rtype: tuple[~azure.cosmos._routing.routing_range.Range, Optional[str],
        list[~azure.cosmos._routing.routing_range.Range], list[Optional[str]]]
    """
    entries = inbound[_FIELD_CONTINUATIONS]
    head = entries[0]
    head_feedrange = _dict_to_range(head)
    current_bc = head.get(_FIELD_BACKEND_CONTINUATION)
    pending_feedranges: List[routing_range.Range] = []
    remaining_bcs: List[Optional[str]] = []
    for entry in entries[1:]:
        pending_feedranges.append(_dict_to_range(entry))
        remaining_bcs.append(entry.get(_FIELD_BACKEND_CONTINUATION))
    return head_feedrange, current_bc, pending_feedranges, remaining_bcs


def _explode_feedrange_on_multi_overlap(
    head_feedrange: routing_range.Range,
    overlapping: List[dict],
    pending_feedranges: Deque[routing_range.Range],
    pending_backend_continuations: Deque[Optional[str]],
) -> Tuple[routing_range.Range, Deque[routing_range.Range], Deque[Optional[str]], bool]:
    """If a saved feedrange now spans more than one physical partition
    (Cosmos split it), slice it into one sub-feedrange per child.

    The split children all start with ``bc = None`` (their parent's
    backend continuation referenced the old partition id and would be
    rejected by the new children).

    :param head_feedrange: Feed range currently being resumed.
    :type head_feedrange: ~azure.cosmos._routing.routing_range.Range
    :param overlapping: Partition ranges overlapping ``head_feedrange``.
    :type overlapping: list[dict]
    :param pending_feedranges: Not-yet-visited feed ranges.
    :type pending_feedranges: Deque[~azure.cosmos._routing.routing_range.Range]
    :param pending_backend_continuations: Per-feedrange backend continuation
        tokens, parallel to ``pending_feedranges``.
    :type pending_backend_continuations: Deque[Optional[str]]
    :returns: New current feedrange, updated remaining feedranges,
        updated parallel backend continuations, and split indicator.
    :rtype: tuple[~azure.cosmos._routing.routing_range.Range,
        Deque[~azure.cosmos._routing.routing_range.Range],
        Deque[Optional[str]], bool]
    """
    if len(overlapping) <= 1:
        return head_feedrange, pending_feedranges, pending_backend_continuations, False
    sub_feedranges = _derive_initial_feedranges(head_feedrange, overlapping)
    if not sub_feedranges:
        return head_feedrange, pending_feedranges, pending_backend_continuations, False
    queued_remaining = deque(sub_feedranges[1:])
    queued_remaining.extend(pending_feedranges)
    queued_bcs: Deque[Optional[str]] = deque(None for _ in sub_feedranges[1:])
    queued_bcs.extend(pending_backend_continuations)
    return sub_feedranges[0], queued_remaining, queued_bcs, True


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

    One of these is created per ``query_items`` call and used by both
    the sync and async pagination loops. It remembers:

      * which slice of the input feed_range we are reading right now,
      * the slices we still have to read after that,
      * the backend continuation token for each slice (one for the
        slice in progress, optionally one per remaining slice for a
        future parallel-fetch loop), and
      * how many items we are still allowed to return on this page.

    Today's loop reads one slice at a time and only ever fills in the
    backend continuation for the slice it is on. Storing one slot per
    slice lets a future parallel-fetch loop fill in more of them
    without changing the saved-token wire format.
    """

    def __init__(
        self,
        head_feedrange: Optional[routing_range.Range],
        pending_feedranges: Iterable[routing_range.Range],
        backend_continuation: Optional[str],
        remaining_page_item_count: Optional[int],
        pending_backend_continuations: Optional[Iterable[Optional[str]]] = None,
    ) -> None:
        self.head_feedrange = head_feedrange
        self.pending_feedranges: Deque[routing_range.Range] = deque(pending_feedranges)
        self.backend_continuation = backend_continuation
        self.remaining_page_item_count = remaining_page_item_count
        if pending_backend_continuations is None:
            # Sequential loop default: every not-yet-visited slice has no
            # backend continuation of its own.
            self.pending_backend_continuations: Deque[Optional[str]] = deque(
                None for _ in self.pending_feedranges
            )
        else:
            self.pending_backend_continuations = deque(pending_backend_continuations)
            if len(self.pending_backend_continuations) != len(self.pending_feedranges):
                raise ValueError(
                    "pending_backend_continuations must be parallel to pending_feedranges."
                )

    @classmethod
    def from_inbound(
        cls,
        inbound: dict,
        remaining_page_item_count: Optional[int],
    ) -> "_FeedRangePaginationState":
        """Build state from a decoded inbound token.

        :param inbound: Decoded inbound token payload.
        :type inbound: dict
        :param remaining_page_item_count: Remaining items allowed in this logical page.
        :type remaining_page_item_count: Optional[int]
        :returns: Pagination state initialized for resume.
        :rtype: _FeedRangePaginationState
        """
        (
            head_feedrange,
            current_bc,
            pending_feedranges,
            remaining_bcs,
        ) = _extract_resume_state(inbound)
        return cls(
            head_feedrange,
            pending_feedranges,
            current_bc,
            remaining_page_item_count,
            pending_backend_continuations=remaining_bcs,
        )

    @classmethod
    def from_derived_feedranges(
        cls,
        feedranges: List[routing_range.Range],
        remaining_page_item_count: Optional[int],
    ) -> "_FeedRangePaginationState":
        """Build state from the first/remaining feedranges computed at startup.

        :param feedranges: Derived feedranges ordered by ``min``.
        :type feedranges: list[~azure.cosmos._routing.routing_range.Range]
        :param remaining_page_item_count: Remaining items allowed in this logical page.
        :type remaining_page_item_count: Optional[int]
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
        if self.head_feedrange is None:
            return False
        if self.remaining_page_item_count is not None and self.remaining_page_item_count <= 0:
            return False
        return True

    def explode_on_multi_overlap(self, overlapping: List[dict]) -> bool:
        """Split current feedrange when routing now overlaps multiple partitions.

        :param overlapping: Routing overlaps for ``head_feedrange``.
        :type overlapping: list[dict]
        :returns: ``True`` when current feedrange was exploded.
        :rtype: bool
        """
        if self.head_feedrange is None:
            return False
        (
            self.head_feedrange,
            self.pending_feedranges,
            self.pending_backend_continuations,
            did_explode,
        ) = _explode_feedrange_on_multi_overlap(
            self.head_feedrange,
            overlapping,
            self.pending_feedranges,
            self.pending_backend_continuations,
        )
        if did_explode:
            self.backend_continuation = None
        return did_explode

    def apply_post_result(self, items_returned: int, backend_continuation: Optional[str]) -> None:
        """Apply one backend response to pagination state.

        :param items_returned: Number of documents returned by this POST.
        :type items_returned: int
        :param backend_continuation: Continuation for current feedrange.
        :type backend_continuation: Optional[str]
        """
        if self.remaining_page_item_count is not None:
            self.remaining_page_item_count -= items_returned

        self.backend_continuation = backend_continuation
        if backend_continuation is not None:
            return
        if not self.pending_feedranges:
            self.head_feedrange = None
            return
        # Pop the next slice into ``head_feedrange`` along with whatever
        # backend continuation was saved for it (None for the sequential
        # loop; a real bc for the future parallel-loop case).
        self.head_feedrange = self.pending_feedranges.popleft()
        self.backend_continuation = (
            self.pending_backend_continuations.popleft()
            if self.pending_backend_continuations
            else None
        )

    def write_outbound_continuation(
        self,
        last_response_headers: MutableMapping[str, Any],
        resource_id: str,
        query: Any,
        feed_range_epk: routing_range.Range,
    ) -> None:
        """Set or clear the outbound continuation header from current state.

        ``head_feedrange = None`` means the pagination loop ran out of
        feedranges; in that case the header is removed and the caller's
        ``by_page`` loop terminates. Otherwise a fresh v=1 envelope is
        stamped onto the header via ``_build_outbound_token``.

        :param last_response_headers: Response headers to mutate.
        :type last_response_headers: MutableMapping[str, Any]
        :param resource_id: Collection resource ID.
        :type resource_id: str
        :param query: Query spec used for hashing.
        :type query: str or dict
        :param feed_range_epk: Original request feed range.
        :type feed_range_epk: ~azure.cosmos._routing.routing_range.Range
        """
        if self.head_feedrange is None:
            last_response_headers.pop(http_constants.HttpHeaders.Continuation, None)
            return
        last_response_headers[http_constants.HttpHeaders.Continuation] = _build_outbound_token(
            resource_id,
            query,
            feed_range_epk,
            self.head_feedrange,
            self.pending_feedranges,
            self.backend_continuation,
            pending_backend_continuations=self.pending_backend_continuations,
        )


def _build_outbound_token(
    resource_id: str,
    query: Any,
    feed_range_epk: routing_range.Range,
    head_feedrange: routing_range.Range,
    pending_feedranges: Iterable[routing_range.Range],
    backend_continuation: Optional[str],
    pending_backend_continuations: Optional[Iterable[Optional[str]]] = None,
) -> str:
    """Build and base64-encode the outbound continuation token.

    Persists a single ordered ``c`` list of ``{min, max, bc}`` entries
    — head first, then each remaining sub-range in order — with no
    privileged "current" slot on the wire. The sequential loop's
    notion of "the slice I'm on" is reconstructed in memory from
    ``c[0]`` on resume; a future parallel-fetch / non-sequential
    merge loop can record per-slice progress simply by setting more
    ``c[i].bc`` entries non-null, without any wire-format version bump.

    :param resource_id: Collection resource ID.
    :type resource_id: str
    :param query: Query spec used for hashing.
    :type query: str or dict
    :param feed_range_epk: Original feed range for the request.
    :type feed_range_epk: ~azure.cosmos._routing.routing_range.Range
    :param head_feedrange: Sub-range whose backend continuation is
        ``backend_continuation`` (becomes ``c[0]`` on the wire).
    :type head_feedrange: ~azure.cosmos._routing.routing_range.Range
    :param pending_feedranges: Sub-ranges queued behind the head
        (become ``c[1:]`` on the wire).
    :type pending_feedranges: list[~azure.cosmos._routing.routing_range.Range]
    :param backend_continuation: Service continuation for ``c[0]``.
    :type backend_continuation: Optional[str]
    :param pending_backend_continuations: Per-slice backend continuations parallel
        to ``pending_feedranges`` (sequential loop default: all ``None``).
    :type pending_backend_continuations: Optional[list[Optional[str]]]
    :returns: Encoded continuation token.
    :rtype: str
    """
    remaining_list = list(pending_feedranges)
    if pending_backend_continuations is None:
        remaining_bcs: List[Optional[str]] = [None] * len(remaining_list)
    else:
        remaining_bcs = list(pending_backend_continuations)
        if len(remaining_bcs) != len(remaining_list):
            raise ValueError(
                "pending_backend_continuations must be parallel to pending_feedranges."
            )
    entries: List[dict] = [
        {
            "min": head_feedrange.min,
            "max": head_feedrange.max,
            _FIELD_BACKEND_CONTINUATION: backend_continuation,
        }
    ]
    for r, bc in zip(remaining_list, remaining_bcs):
        entries.append({"min": r.min, "max": r.max, _FIELD_BACKEND_CONTINUATION: bc})
    payload = {
        _FIELD_VERSION: _TOKEN_VERSION,
        _FIELD_COLLECTION_RID: resource_id,
        _FIELD_QUERY_HASH: _hash_query_spec(query),
        _FIELD_FEEDRANGE_HASH: _hash_feed_range(feed_range_epk),
        _FIELD_CONTINUATIONS: entries,
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


def _apply_feedrange_request_headers(
    req_headers: MutableMapping[str, Any],
    overlapping: List[dict],
    partition_scope: routing_range.Range,
    head_feedrange: routing_range.Range,
    remaining_page_item_count: Optional[int],
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
    :param remaining_page_item_count: Remaining items allowed in this logical page.
    :type remaining_page_item_count: Optional[int]
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

    if remaining_page_item_count is not None:
        req_headers[http_constants.HttpHeaders.PageSize] = str(remaining_page_item_count)
    else:
        req_headers.pop(http_constants.HttpHeaders.PageSize, None)

    if inbound_continuation is not None:
        req_headers[http_constants.HttpHeaders.Continuation] = inbound_continuation
    else:
        req_headers.pop(http_constants.HttpHeaders.Continuation, None)

