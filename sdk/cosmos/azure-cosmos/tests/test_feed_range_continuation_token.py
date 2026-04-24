# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Unit tests for ``azure.cosmos._routing.feed_range_continuation``.

These tests do NOT touch the network. They cover the wire-format
contracts for the structured ``feed_range`` continuation token:

* ``TestTokenRoundTrip`` - ``_decode_token(_encode_token(p))`` returns
  a structurally-equivalent dict; the wire form is valid base64 of
  valid JSON; the JSON contains the seven required keys.
* ``TestVersionMismatchRejected`` - a token whose ``v`` field is set
  but is not the SDK's current version raises ``ValueError`` with a
  message naming both the offending and the supported version.
* ``TestIdentityFingerprintMismatch`` - a valid v=1 token whose ``cr``
  / ``qh`` / ``frh`` fingerprints disagree with the current request
  raises ``ValueError`` with a message naming the failing field.
  (Validation lives in the call sites; this test exercises the same
  hash-based equality the call sites use.)
* ``TestExplodeOnMultiOverlap`` - when a saved feedrange resolves to
  more than one physical partition on resume (the post-split case),
  the call site must slice the feedrange into one sub-feedrange per
  child before POSTing. These tests pin the geometry of that slice
  without touching the network.
"""

import base64
import json

import pytest

from azure.cosmos import http_constants
from azure.cosmos._routing import routing_range
from azure.cosmos._routing.feed_range_continuation import (
    _MAX_CONSECUTIVE_NO_PROGRESS_PAGES,
    _apply_feedrange_request_headers,
    _build_outbound_token,
    _build_scope_from_overlaps,
    _count_page_items_from_partial_result,
    _decode_token,
    _derive_initial_feedranges,
    _encode_token,
    _hash_feed_range,
    _hash_query_spec,
    _normalize_max_item_count,
    _update_no_progress_page_count,
    _validate_token_identity,
    _FIELD_BACKEND_CONTINUATION,
    _FIELD_COLLECTION_RID,
    _FIELD_CURRENT_FEEDRANGE,
    _FIELD_FEEDRANGE_HASH,
    _FIELD_QUERY_HASH,
    _FIELD_REMAINING_FEEDRANGES,
    _FIELD_VERSION,
    _TOKEN_VERSION,
)


# Fixed inputs reused across the round-trip / mismatch tests so each
# assertion compares against a known-good baseline.
# cspell:ignore AOXB BFFFFFFFFFFFFFFF BAAAAAAAAAA
_RID = "Yxs1AOXBSp4="
_QUERY = {"query": "SELECT * FROM c WHERE c.x = @x",
          "parameters": [{"name": "@x", "value": 7}]}
_FEED_RANGE = routing_range.Range(
    range_min="3FFFFFFFFFFFFFFF",
    range_max="BFFFFFFFFFFFFFFF",
    isMinInclusive=True,
    isMaxInclusive=False,
)
_CURRENT_FEEDRANGE = routing_range.Range(
    range_min="3FFFFFFFFFFFFFFF",
    range_max="7FFFFFFFFFFFFFFF",
    isMinInclusive=True,
    isMaxInclusive=False,
)
_REMAINING_FEEDRANGE = routing_range.Range(
    range_min="7FFFFFFFFFFFFFFF",
    range_max="BFFFFFFFFFFFFFFF",
    isMinInclusive=True,
    isMaxInclusive=False,
)
_BACKEND_CONT = "+RID:~Yxs1AOXBSp4BAAAAAAAAAA==#RT:1#TRC:5#ISV:2#IEO:65567"


def _mk_range(mn: str, mx: str) -> routing_range.Range:
    return routing_range.Range(range_min=mn, range_max=mx, isMinInclusive=True, isMaxInclusive=False)


def _make_valid_token_payload() -> dict:
    """Build a structurally-complete v=1 token payload over the fixtures."""
    return {
        _FIELD_VERSION: _TOKEN_VERSION,
        _FIELD_COLLECTION_RID: _RID,
        _FIELD_QUERY_HASH: _hash_query_spec(_QUERY),
        _FIELD_FEEDRANGE_HASH: _hash_feed_range(_FEED_RANGE),
        _FIELD_CURRENT_FEEDRANGE: {"min": _CURRENT_FEEDRANGE.min, "max": _CURRENT_FEEDRANGE.max},
        _FIELD_REMAINING_FEEDRANGES: [
            {"min": _REMAINING_FEEDRANGE.min, "max": _REMAINING_FEEDRANGE.max}
        ],
        _FIELD_BACKEND_CONTINUATION: _BACKEND_CONT,
    }


# ---------------------------------------------------------------------- #
# Token round-trip
# ---------------------------------------------------------------------- #
class TestTokenRoundTrip:
    """``_encode_token`` -> ``_decode_token`` is structurally lossless and
    the wire form is base64-encoded JSON containing all seven required
    fields."""

    def test_round_trip_preserves_all_fields(self):
        payload = _make_valid_token_payload()
        wire = _encode_token(payload)
        decoded = _decode_token(wire)
        assert decoded == payload

    def test_wire_form_is_base64_of_json(self):
        payload = _make_valid_token_payload()
        wire = _encode_token(payload)
        # Wire form must be ASCII-safe and base64-decodable; the decoded
        # bytes must be valid UTF-8 JSON; the JSON must be a dict.
        raw = base64.b64decode(wire, validate=True)
        as_json = json.loads(raw.decode("utf-8"))
        assert isinstance(as_json, dict)

    def test_wire_form_contains_seven_required_keys(self):
        payload = _make_valid_token_payload()
        wire = _encode_token(payload)
        decoded_json = json.loads(base64.b64decode(wire, validate=True).decode("utf-8"))
        required = {
            _FIELD_VERSION,
            _FIELD_COLLECTION_RID,
            _FIELD_QUERY_HASH,
            _FIELD_FEEDRANGE_HASH,
            _FIELD_CURRENT_FEEDRANGE,
            _FIELD_REMAINING_FEEDRANGES,
            _FIELD_BACKEND_CONTINUATION,
        }
        assert required.issubset(decoded_json.keys())

    def test_build_outbound_token_emits_valid_token(self):
        wire = _build_outbound_token(
            resource_id=_RID,
            query=_QUERY,
            feed_range_epk=_FEED_RANGE,
            current_feedrange=_CURRENT_FEEDRANGE,
            remaining_feedranges=[_REMAINING_FEEDRANGE],
            backend_continuation=_BACKEND_CONT,
        )
        decoded = _decode_token(wire)
        assert decoded is not None
        assert decoded[_FIELD_VERSION] == _TOKEN_VERSION
        assert decoded[_FIELD_COLLECTION_RID] == _RID
        assert decoded[_FIELD_QUERY_HASH] == _hash_query_spec(_QUERY)
        assert decoded[_FIELD_FEEDRANGE_HASH] == _hash_feed_range(_FEED_RANGE)
        assert decoded[_FIELD_CURRENT_FEEDRANGE] == {
            "min": _CURRENT_FEEDRANGE.min, "max": _CURRENT_FEEDRANGE.max,
        }
        assert decoded[_FIELD_REMAINING_FEEDRANGES] == [
            {"min": _REMAINING_FEEDRANGE.min, "max": _REMAINING_FEEDRANGE.max}
        ]
        assert decoded[_FIELD_BACKEND_CONTINUATION] == _BACKEND_CONT

    def test_none_and_empty_inputs_decode_to_none(self):
        # An empty / missing continuation must NOT raise - the call site
        # treats it as "first call, derive feedranges from the routing map".
        assert _decode_token(None) is None
        assert _decode_token("") is None


# ---------------------------------------------------------------------- #
# Version-mismatch rejection
# ---------------------------------------------------------------------- #
class TestVersionMismatchRejected:
    """A token that decodes as our shape but with a non-current ``v``
    raises ``ValueError`` rather than being silently misinterpreted."""

    def test_future_version_raises(self):
        payload = _make_valid_token_payload()
        payload[_FIELD_VERSION] = 999
        wire = _encode_token(payload)
        with pytest.raises(ValueError) as excinfo:
            _decode_token(wire)
        msg = str(excinfo.value)
        assert "999" in msg
        assert str(_TOKEN_VERSION) in msg

    def test_zero_version_raises(self):
        payload = _make_valid_token_payload()
        payload[_FIELD_VERSION] = 0
        wire = _encode_token(payload)
        with pytest.raises(ValueError):
            _decode_token(wire)

    def test_missing_cf_raises(self):
        payload = _make_valid_token_payload()
        del payload[_FIELD_CURRENT_FEEDRANGE]
        wire = _encode_token(payload)
        with pytest.raises(ValueError) as excinfo:
            _decode_token(wire)
        assert "cf" in str(excinfo.value)

    def test_missing_rf_raises(self):
        payload = _make_valid_token_payload()
        del payload[_FIELD_REMAINING_FEEDRANGES]
        wire = _encode_token(payload)
        with pytest.raises(ValueError) as excinfo:
            _decode_token(wire)
        assert "rf" in str(excinfo.value)


class TestMalformedV1TokenRejected:
    """Malformed v1 tokens should raise ValueError at decode time.

    This prevents downstream call-sites from seeing KeyError when indexing
    required identity and feedrange fields.
    """

    def test_missing_cr_raises(self):
        payload = _make_valid_token_payload()
        del payload[_FIELD_COLLECTION_RID]
        with pytest.raises(ValueError) as excinfo:
            _decode_token(_encode_token(payload))
        assert "cr" in str(excinfo.value)

    def test_missing_qh_raises(self):
        payload = _make_valid_token_payload()
        del payload[_FIELD_QUERY_HASH]
        with pytest.raises(ValueError) as excinfo:
            _decode_token(_encode_token(payload))
        assert "qh" in str(excinfo.value)

    def test_missing_frh_raises(self):
        payload = _make_valid_token_payload()
        del payload[_FIELD_FEEDRANGE_HASH]
        with pytest.raises(ValueError) as excinfo:
            _decode_token(_encode_token(payload))
        assert "frh" in str(excinfo.value)

    def test_missing_current_feedrange_min_raises(self):
        payload = _make_valid_token_payload()
        del payload[_FIELD_CURRENT_FEEDRANGE]["min"]
        with pytest.raises(ValueError) as excinfo:
            _decode_token(_encode_token(payload))
        assert "cf.min" in str(excinfo.value)

    def test_malformed_remaining_feedrange_entry_raises(self):
        payload = _make_valid_token_payload()
        payload[_FIELD_REMAINING_FEEDRANGES] = ["not-an-object"]
        with pytest.raises(ValueError) as excinfo:
            _decode_token(_encode_token(payload))
        assert "rf[0]" in str(excinfo.value)

    def test_non_string_backend_continuation_raises(self):
        payload = _make_valid_token_payload()
        payload[_FIELD_BACKEND_CONTINUATION] = 123
        with pytest.raises(ValueError) as excinfo:
            _decode_token(_encode_token(payload))
        assert "bc" in str(excinfo.value)


# ---------------------------------------------------------------------- #
# Identity-fingerprint mismatch rejection
# ---------------------------------------------------------------------- #
class TestIdentityFingerprintMismatch:
    """A valid v=1 token replayed against a different collection / query /
    feed_range produces a fingerprint mismatch the call site rejects.

    The hash helpers are deterministic and the call-site validators in
    ``__QueryFeed`` compare ``inbound[_FIELD_*]`` to ``_hash_*(current)``
    and raise ``ValueError`` on mismatch. These tests exercise the
    equality contract those validators rely on; the live equivalents
    of the call-site raise live in
    ``test_query_feed_range_multipartition*.py``."""

    def test_collection_rid_mismatch_detected(self):
        payload = _make_valid_token_payload()
        decoded = _decode_token(_encode_token(payload))
        assert decoded is not None
        # Same call-site shape: compare cr to current resource_id.
        assert decoded[_FIELD_COLLECTION_RID] == _RID
        assert decoded[_FIELD_COLLECTION_RID] != "different-collection-rid=="

    def test_query_text_change_changes_hash(self):
        original = _hash_query_spec(_QUERY)
        modified = _hash_query_spec({
            "query": "SELECT * FROM c WHERE c.x = @x AND c.y = 1",
            "parameters": _QUERY["parameters"],
        })
        assert original != modified, (
            "query-text change must produce a different hash so the "
            "call site can reject the resume")

    def test_query_parameter_value_change_changes_hash(self):
        original = _hash_query_spec(_QUERY)
        modified = _hash_query_spec({
            "query": _QUERY["query"],
            "parameters": [{"name": "@x", "value": 8}],
        })
        assert original != modified

    def test_query_parameter_name_change_changes_hash(self):
        original = _hash_query_spec(_QUERY)
        modified = _hash_query_spec({
            "query": _QUERY["query"],
            "parameters": [{"name": "@y", "value": 7}],
        })
        assert original != modified

    def test_query_string_form_hashes_consistently(self):
        # When the caller passes a plain string (no parameters) the hash
        # must still be deterministic and stable.
        h1 = _hash_query_spec("SELECT * FROM c")
        h2 = _hash_query_spec("SELECT * FROM c")
        h3 = _hash_query_spec("SELECT VALUE c FROM c")
        assert h1 == h2
        assert h1 != h3

    def test_feed_range_change_changes_hash(self):
        original = _hash_feed_range(_FEED_RANGE)
        wider = _hash_feed_range(routing_range.Range(
            range_min=_FEED_RANGE.min,
            range_max="FFFFFFFFFFFFFFFF",
            isMinInclusive=True, isMaxInclusive=False,
        ))
        narrower = _hash_feed_range(routing_range.Range(
            range_min=_FEED_RANGE.min,
            range_max="9FFFFFFFFFFFFFFF",
            isMinInclusive=True, isMaxInclusive=False,
        ))
        assert original != wider
        assert original != narrower
        assert wider != narrower

    def test_feed_range_hash_is_stable(self):
        # Same feed_range -> same hash on every call (no random state).
        h1 = _hash_feed_range(_FEED_RANGE)
        h2 = _hash_feed_range(_FEED_RANGE)
        assert h1 == h2

    def test_call_site_replay_against_other_collection_raises(self):
        """Drive the production validator (``_validate_token_identity``)
        with a token built for ``_RID`` and resume against a different
        collection rid. It must raise ``ValueError`` whose message names
        the failing field, matching the call-site contract in
        ``__QueryFeed`` (sync and async)."""
        payload = _make_valid_token_payload()
        inbound = _decode_token(_encode_token(payload))
        assert inbound is not None

        with pytest.raises(ValueError) as excinfo:
            _validate_token_identity(
                inbound,
                resource_id="different-collection-rid==",
                query=_QUERY,
                feed_range_epk=_FEED_RANGE,
            )
        assert "collection" in str(excinfo.value).lower()

    def test_call_site_replay_with_different_query_raises(self):
        payload = _make_valid_token_payload()
        inbound = _decode_token(_encode_token(payload))
        assert inbound is not None

        with pytest.raises(ValueError) as excinfo:
            _validate_token_identity(
                inbound,
                resource_id=_RID,
                query={"query": "SELECT c.id FROM c", "parameters": []},
                feed_range_epk=_FEED_RANGE,
            )
        assert "query" in str(excinfo.value).lower()

    def test_call_site_replay_with_different_feed_range_raises(self):
        payload = _make_valid_token_payload()
        inbound = _decode_token(_encode_token(payload))
        assert inbound is not None

        other_feed_range = routing_range.Range(
            range_min="0000000000000000",
            range_max="3FFFFFFFFFFFFFFF",
            isMinInclusive=True,
            isMaxInclusive=False,
        )
        with pytest.raises(ValueError) as excinfo:
            _validate_token_identity(
                inbound,
                resource_id=_RID,
                query=_QUERY,
                feed_range_epk=other_feed_range,
            )
        assert "feed_range" in str(excinfo.value).lower()


# ---------------------------------------------------------------------- #
# Explode-on-multi-overlap - post-split fan-out unit contract
# ---------------------------------------------------------------------- #
class TestExplodeOnMultiOverlap:
    """Reproduces the customer scenario at the unit-test layer, no network
    needed.

    Concrete setup: the customer's feed range ``[05C1D9D5..., 05C1D9F5...)``
    lived inside one physical partition ``X`` on Day 1. On Day N Cosmos
    split ``X`` at the midpoint ``M = 05C1D9E4...`` into
    ``X1 = [05C1D9D5..., 05C1D9E4...)`` and
    ``X2 = [05C1D9E4..., 05C1D9F5...)``. The same ``{min, max}`` string
    the customer's worker has on disk now resolves to two physical
    partitions, not one.

    A continuation token saved on Day 1 carries
    ``current_feedrange = [05C1D9D5..., 05C1D9F5...)`` (the whole of old
    ``X``). On Day N the SDK re-resolves that feedrange against the live
    routing map and gets back two overlaps: ``X1`` and ``X2``. If the
    call site just POSTs once with ``PartitionKeyRangeID = X1`` and
    ``EndEpkString = 05C1D9F5...``, every row that physically lives on
    ``X2`` is silently dropped - the backend's EPK filter only returns
    rows on the partition the request was routed to. That's how the
    slow ``test_post_split_resume_async`` came back with 69 of the
    expected 88 ids on the run that flagged this.

    The fix the call site applies (``__QueryFeed``, sync and async) is:
    when ``len(overlapping) > 1``, hand ``current_feedrange`` and the
    new children to ``_derive_initial_feedranges``. That returns one
    sub-feedrange per child, each one the intersection of the child's
    range with the saved feedrange - for the customer's case,
    ``[05C1D9D5..., 05C1D9E4...)`` for ``X1`` and
    ``[05C1D9E4..., 05C1D9F5...)`` for ``X2``. The first sub-feedrange
    becomes the new ``current_feedrange``, the rest are prepended to
    ``remaining_feedranges``, and the parent's saved
    ``next_backend_cont`` is dropped (it referenced ``X``'s id and
    won't decode against either child). The next loop iteration then
    sees a single overlap and falls through to the normal
    single-partition route.

    The tests below pin the four properties the call site relies on:

      * the slice produces one sub-feedrange per child,
      * the sub-feedranges cover the saved feedrange end-to-end with no
        gap and no overlap,
      * the order is by EPK ``min`` regardless of what order the
        routing map returned the children,
      * each sub-feedrange, fed back through ``_build_scope_from_overlaps``
        against its own child, resolves to a single overlap (so the
        next loop iteration takes the single-partition route, not the
        slice branch again).

    The slow live coverage is ``test_post_split_resume[_async]`` in
    ``test_query_feed_range_multipartition*.py`` (the 10-minute
    ``cosmosSplit`` test). These six tests run in a fraction of a
    second and pin the same contract without waiting on Cosmos to
    actually split a partition."""

    @staticmethod
    def _pkr(pkr_id: str, mn: str, mx: str) -> dict:
        # The minimal partition_key_range dict shape that the routing
        # map provider hands back. _build_scope_from_overlaps and
        # _derive_initial_feedranges both consume this shape directly.
        return {"id": pkr_id, "minInclusive": mn, "maxExclusive": mx}

    def test_two_child_split_slices_into_two_sub_feedranges(self):
        # The customer's exact case, with the hex range simplified for
        # readability:
        #   parent       saved_feedrange = [05C1D9D5..., 05C1D9F5...)   (old X)
        #   children     X1              = [05C1D9D5..., 05C1D9E4...)
        #                X2              = [05C1D9E4..., 05C1D9F5...)
        # Re-resolving saved_feedrange on Day N returns [X1, X2]; the
        # slice must hand back one sub-feedrange per child.
        saved_feedrange = routing_range.Range(
            range_min="05C1D9D533F364", range_max="05C1D9F59FF5A0",
            isMinInclusive=True, isMaxInclusive=False)
        x1 = self._pkr("X1", "05C1D9D533F364", "05C1D9E4000000")
        x2 = self._pkr("X2", "05C1D9E4000000", "05C1D9F59FF5A0")

        sub_feedranges = _derive_initial_feedranges(saved_feedrange, [x1, x2])

        assert len(sub_feedranges) == 2, (
            "Day-N resolution returned 2 children but the slice "
            "produced {} sub-feedranges".format(len(sub_feedranges)))
        assert (sub_feedranges[0].min, sub_feedranges[0].max) == (
            "05C1D9D533F364", "05C1D9E4000000"), (
            "first sub-feedrange should be the X1 slice of the saved feedrange")
        assert (sub_feedranges[1].min, sub_feedranges[1].max) == (
            "05C1D9E4000000", "05C1D9F59FF5A0"), (
            "second sub-feedrange should be the X2 slice of the saved feedrange")

    def test_sub_feedranges_partition_parent_exactly(self):
        # A wider variant of the customer's case: imagine the saved
        # feedrange sits inside an even bigger old partition that has
        # since split into THREE children. The slice must still cover
        # the saved feedrange end-to-end - every row that was returnable
        # under the old layout must still be reachable under the new
        # one, no gap (= missing rows) and no overlap (= duplicates).
        saved_feedrange = routing_range.Range(
            range_min="20", range_max="E0",
            isMinInclusive=True, isMaxInclusive=False)
        children = [
            self._pkr("c1", "00", "55"),
            self._pkr("c2", "55", "AA"),
            self._pkr("c3", "AA", "FF"),
        ]
        sub_feedranges = _derive_initial_feedranges(saved_feedrange, children)

        bounds = [(s.min, s.max) for s in sub_feedranges]
        assert bounds == [("20", "55"), ("55", "AA"), ("AA", "E0")], (
            "sub-feedranges must be the intersections of each child with "
            "the saved feedrange; got {}".format(bounds))
        # First sub-feedrange starts where the saved feedrange starts;
        # last one ends where it ends. Anything else loses rows at the
        # edges.
        assert bounds[0][0] == saved_feedrange.min
        assert bounds[-1][1] == saved_feedrange.max
        # And the sub-feedranges butt up against each other with no gap
        # and no overlap.
        for i in range(len(bounds) - 1):
            assert bounds[i][1] == bounds[i + 1][0], (
                "sub-feedranges {} and {} have a gap or overlap at the "
                "boundary; rows in between would be missed or "
                "duplicated".format(bounds[i], bounds[i + 1]))

    def test_sub_feedranges_are_deterministically_ordered(self):
        # The routing map provider doesn't promise any particular order
        # when it returns the children. The call site prepends the
        # leftover sub-feedranges to remaining_feedranges, so if the
        # order depended on what the provider happened to return, two
        # different SDK processes resuming the same token could end up
        # walking the children in different orders - and emit different
        # outbound tokens halfway through. Pin EPK-min order regardless
        # of input order.
        saved_feedrange = routing_range.Range(
            range_min="05C1D9D533F364", range_max="05C1D9F59FF5A0",
            isMinInclusive=True, isMaxInclusive=False)
        x1 = self._pkr("X1", "05C1D9D533F364", "05C1D9E4000000")
        x2 = self._pkr("X2", "05C1D9E4000000", "05C1D9F59FF5A0")

        forward = _derive_initial_feedranges(saved_feedrange, [x1, x2])
        reverse = _derive_initial_feedranges(saved_feedrange, [x2, x1])

        assert ([(r.min, r.max) for r in forward]
                == [(r.min, r.max) for r in reverse]), (
            "slice result depended on input child order; resuming the "
            "same token from two processes would diverge")

    def test_each_sub_feedrange_resolves_to_a_single_child(self):
        # Why the slice is correct end-to-end: after slicing, the
        # NEW current_feedrange is X1's slice, and the next iteration
        # of the __QueryFeed loop re-resolves it against the routing
        # map. That re-resolution must come back with exactly one
        # overlap (X1) - otherwise we'd loop into the slice branch a
        # second time. Same for X2 once X1 is drained. This pins the
        # invariant that each sub-feedrange routes cleanly to one
        # partition, which is what lets the rest of the loop fall
        # through to the single-partition POST.
        saved_feedrange = routing_range.Range(
            range_min="05C1D9D533F364", range_max="05C1D9F59FF5A0",
            isMinInclusive=True, isMaxInclusive=False)
        children = [
            self._pkr("X1", "05C1D9D533F364", "05C1D9E4000000"),
            self._pkr("X2", "05C1D9E4000000", "05C1D9F59FF5A0"),
        ]
        sub_feedranges = _derive_initial_feedranges(saved_feedrange, children)

        for sb in sub_feedranges:
            owning_child = next(c for c in children
                                if c["minInclusive"] <= sb.min < c["maxExclusive"])
            overlaps, scope = _build_scope_from_overlaps([owning_child], sb)
            assert len(overlaps) == 1, (
                "sub-feedrange [{}, {}) re-resolved to {} overlaps; the next "
                "loop iteration would slice again".format(
                    sb.min, sb.max, len(overlaps)))
            assert (scope.min, scope.max) == (sb.min, sb.max), (
                "sub-feedrange [{}, {}) routes to a partition whose scope is "
                "[{}, {}); the EPK filter would over-fetch or "
                "under-fetch".format(sb.min, sb.max, scope.min, scope.max))

    def test_no_split_single_overlap_is_not_sliced(self):
        # The "feed range fits inside one child" path: most of the
        # customer's thousands of feed ranges sat entirely inside one
        # of the two children after the split, so they still resolve
        # to a single overlap on Day N. The slice branch is gated by
        # `if len(overlapping) > 1`, so for these the call site goes
        # straight to the single-partition POST. This is the negative
        # control - verifying nothing in our slice helpers fires
        # spuriously for the common safe case.
        feed_range = routing_range.Range(
            range_min="40", range_max="60",
            isMinInclusive=True, isMaxInclusive=False)
        overlaps, scope = _build_scope_from_overlaps(
            [self._pkr("c1", "00", "80")], feed_range)
        assert len(overlaps) == 1
        assert (scope.min, scope.max) == ("00", "80"), (
            "single-overlap re-resolution returned the wrong "
            "partition scope")

    def test_three_child_split_slices_into_three(self):
        # The customer's case is 1->2 because Cosmos split X once. But
        # nothing in the design caps it there - over enough wall-clock
        # time, X1 and X2 can themselves split, and a saved feedrange
        # from before all of those splits will resolve to 3+ overlaps.
        # Pin that the slice handles N children the same way it
        # handles 2: one sub-feedrange per child, in EPK order,
        # covering the saved feedrange.
        saved_feedrange = routing_range.Range(
            range_min="00", range_max="FF",
            isMinInclusive=True, isMaxInclusive=False)
        children = [
            self._pkr("c1", "00", "55"),
            self._pkr("c2", "55", "AA"),
            self._pkr("c3", "AA", "FF"),
        ]
        sub_feedranges = _derive_initial_feedranges(saved_feedrange, children)

        assert len(sub_feedranges) == 3
        assert [(s.min, s.max) for s in sub_feedranges] == [
            ("00", "55"), ("55", "AA"), ("AA", "FF"),
        ]


# ---------------------------------------------------------------------- #
# max_item_count normalization
# ---------------------------------------------------------------------- #
class TestNormalizeMaxItemCount:
    """``_normalize_max_item_count`` collapses unset / non-numeric / non-positive
    values to ``None`` (unbounded) and passes positive ints through unchanged.

    The pagination loop interprets ``None`` as "no client-side cap" and any
    positive int as the per-page budget. A zero or negative cap would make
    the loop exit before issuing any POST while still emitting a
    continuation token, leaving the caller in an empty-page-with-continuation
    cycle - so those cases must be normalized to ``None``."""

    def test_none_passes_through(self):
        assert _normalize_max_item_count(None) is None

    def test_positive_int_passes_through(self):
        assert _normalize_max_item_count(5) == 5

    def test_positive_str_is_parsed(self):
        assert _normalize_max_item_count("25") == 25

    def test_zero_is_treated_as_unbounded(self):
        assert _normalize_max_item_count(0) is None

    def test_negative_is_treated_as_unbounded(self):
        assert _normalize_max_item_count(-1) is None

    def test_non_numeric_is_treated_as_unbounded(self):
        assert _normalize_max_item_count("not-a-number") is None

    def test_object_is_treated_as_unbounded(self):
        assert _normalize_max_item_count(object()) is None


# ---------------------------------------------------------------------- #
# Request-header shaping
# ---------------------------------------------------------------------- #
class TestApplyFeedrangeRequestHeaders:
    """``_apply_feedrange_request_headers`` sets and clears routing/page/token
    headers correctly for both full-partition and sub-range requests."""

    @pytest.mark.parametrize(
        "current_feedrange,expect_epk_headers",
        [
            # full-partition request -> EPK headers must be cleared
            (_mk_range("10", "20"), False),
            # strict sub-range request -> EPK headers must be stamped
            (_mk_range("12", "18"), True),
        ],
    )
    def test_epk_headers_match_full_vs_subrange(self, current_feedrange, expect_epk_headers):
        req_headers = {
            # pre-populate with stale values to prove clear behavior
            http_constants.HttpHeaders.StartEpkString: "stale-start",
            http_constants.HttpHeaders.EndEpkString: "stale-end",
        }
        overlapping = [{"id": "7", "minInclusive": "10", "maxExclusive": "20"}]
        partition_scope = _mk_range("10", "20")

        _apply_feedrange_request_headers(
            req_headers=req_headers,
            overlapping=overlapping,
            partition_scope=partition_scope,
            current_feedrange=current_feedrange,
            remaining_page_item_count=None,
            inbound_continuation=None,
        )

        assert req_headers[http_constants.HttpHeaders.PartitionKeyRangeID] == "7"
        assert req_headers[http_constants.HttpHeaders.ReadFeedKeyType] == "EffectivePartitionKeyRange"
        if expect_epk_headers:
            assert req_headers[http_constants.HttpHeaders.StartEpkString] == current_feedrange.min
            assert req_headers[http_constants.HttpHeaders.EndEpkString] == current_feedrange.max
        else:
            assert http_constants.HttpHeaders.StartEpkString not in req_headers
            assert http_constants.HttpHeaders.EndEpkString not in req_headers

    @pytest.mark.parametrize(
        "remaining_page_item_count,inbound_continuation,expect_page_size,expect_continuation",
        [
            (5, "abc", True, True),
            (None, "abc", False, True),
            (5, None, True, False),
            (None, None, False, False),
        ],
    )
    def test_page_size_and_continuation_are_set_or_cleared(
        self,
        remaining_page_item_count,
        inbound_continuation,
        expect_page_size,
        expect_continuation,
    ):
        req_headers = {
            # pre-populate stale values; helper should clear when args are None
            http_constants.HttpHeaders.PageSize: "999",
            http_constants.HttpHeaders.Continuation: "stale-cont",
        }
        overlapping = [{"id": "9", "minInclusive": "30", "maxExclusive": "40"}]
        partition_scope = _mk_range("30", "40")
        current_feedrange = _mk_range("30", "40")

        _apply_feedrange_request_headers(
            req_headers=req_headers,
            overlapping=overlapping,
            partition_scope=partition_scope,
            current_feedrange=current_feedrange,
            remaining_page_item_count=remaining_page_item_count,
            inbound_continuation=inbound_continuation,
        )

        if expect_page_size:
            assert req_headers[http_constants.HttpHeaders.PageSize] == str(remaining_page_item_count)
        else:
            assert http_constants.HttpHeaders.PageSize not in req_headers

        if expect_continuation:
            assert req_headers[http_constants.HttpHeaders.Continuation] == inbound_continuation
        else:
            assert http_constants.HttpHeaders.Continuation not in req_headers


class TestBudgetCounting:
    """Budget accounting treats aggregate partial rows as merge fragments."""

    def test_standard_documents_consume_budget(self):
        partial_result = {"Documents": [{"id": "1"}, {"id": "2"}]}
        assert _count_page_items_from_partial_result(partial_result, "SELECT * FROM c") == 2

    def test_object_aggregate_partial_does_not_consume_budget(self):
        partial_result = {"Documents": [{"_aggregate": {"count": 7}}]}
        assert _count_page_items_from_partial_result(partial_result, "SELECT COUNT(1) FROM c") == 0

    def test_value_aggregate_partial_does_not_consume_budget(self):
        partial_result = {"Documents": [7]}
        assert _count_page_items_from_partial_result(partial_result, "SELECT VALUE COUNT(1) FROM c") == 0

    def test_value_non_aggregate_numeric_row_consumes_budget(self):
        partial_result = {"Documents": [7]}
        assert _count_page_items_from_partial_result(partial_result, "SELECT VALUE c.value FROM c") == 1

    def test_value_non_aggregate_boolean_row_consumes_budget(self):
        partial_result = {"Documents": [True]}
        assert _count_page_items_from_partial_result(partial_result, "SELECT VALUE c.flag FROM c") == 1


class TestEmptyPageStallCounter:
    """No-progress guard only counts empty pages that still carry continuation."""

    def test_increments_on_empty_page_with_continuation(self):
        current_feedrange = _mk_range("10", "20")
        assert _update_no_progress_page_count(
            3,
            page_items_returned=0,
            previous_feedrange=current_feedrange,
            previous_backend_continuation="token",
            current_feedrange=current_feedrange,
            current_backend_continuation="token",
        ) == 4

    def test_resets_when_items_are_returned(self):
        current_feedrange = _mk_range("10", "20")
        assert _update_no_progress_page_count(
            5,
            page_items_returned=1,
            previous_feedrange=current_feedrange,
            previous_backend_continuation="token",
            current_feedrange=current_feedrange,
            current_backend_continuation="token",
        ) == 0

    def test_resets_when_continuation_is_none(self):
        assert _update_no_progress_page_count(
            _MAX_CONSECUTIVE_NO_PROGRESS_PAGES - 1,
            page_items_returned=0,
            previous_feedrange=_mk_range("10", "20"),
            previous_backend_continuation="token",
            current_feedrange=_mk_range("20", "30"),
            current_backend_continuation=None,
        ) == 0

    def test_resets_when_continuation_advances(self):
        current_feedrange = _mk_range("10", "20")
        assert _update_no_progress_page_count(
            8,
            page_items_returned=0,
            previous_feedrange=current_feedrange,
            previous_backend_continuation="token-1",
            current_feedrange=current_feedrange,
            current_backend_continuation="token-2",
        ) == 0


