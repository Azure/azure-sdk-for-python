# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Backend-agnostic unit tests for the ``is_feed_range_subset`` Rust-routing helpers
(gate / prepared-request builder / payload parser).

These tests do not need the emulator or the Rust binding. They run in milliseconds
with no network and lock in the shape of the request the binding receives and the
answer the parser reads back, plus the error handling for a malformed payload.
Without them, a regression in the request shape or the payload parser would surface
only in a slow emulator run.
"""
from __future__ import annotations

import json

import pytest

from azure.cosmos._backend.operations import OP_IS_FEED_RANGE_SUBSET
from azure.cosmos._change_feed.feed_range_internal import FeedRangeInternalEpk
from azure.cosmos._routing.routing_range import Range
from azure.cosmos._feed_ranges_rust_routing import (
    build_is_feed_range_subset_prepared_request,
    can_use_rust_backend_for_is_feed_range_subset,
    parse_is_feed_range_subset_payload,
)


def _feed_range(range_min, range_max, is_min_inclusive=True, is_max_inclusive=False):
    """Build a public feed range from explicit boundaries."""
    return FeedRangeInternalEpk(
        Range(range_min, range_max, is_min_inclusive, is_max_inclusive)
    ).to_dict()


# ---------------------------------------------------------------------------
# Gate
# ---------------------------------------------------------------------------

def test_gate_requires_backend():
    """Python handles the check when Rust is unavailable."""
    assert can_use_rust_backend_for_is_feed_range_subset(backend=None) is False


def test_gate_allows_backend():
    """Rust handles a supported subset check."""
    assert can_use_rust_backend_for_is_feed_range_subset(backend=object()) is True


# ---------------------------------------------------------------------------
# Prepared-request builder
# ---------------------------------------------------------------------------

def test_builds_prepared_request_with_both_feed_ranges_in_body():
    """The Rust request contains the correct parent and child feed ranges."""
    parent = _feed_range("", "FF")
    child = _feed_range("3F", "7F")
    prepared = build_is_feed_range_subset_prepared_request(
        parent_feed_range=parent, child_feed_range=child
    )
    assert prepared.op == OP_IS_FEED_RANGE_SUBSET
    # No container to target for a pure client-side check.
    assert prepared.container_link == ""
    assert prepared.partition_key_header == "[]"
    # Both feed ranges ride verbatim in the body under "parent" / "child".
    body = json.loads(prepared.body_bytes)
    assert body == {"parent": parent, "child": child}


# ---------------------------------------------------------------------------
# Payload parser
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("value", [True, False])
def test_parses_boolean_answer(value):
    """Rust Boolean results preserve the Python public result."""
    assert parse_is_feed_range_subset_payload({"IsSubset": value}) is value


def test_parser_rejects_missing_is_subset():
    """A missing result raises the expected public parsing error."""
    with pytest.raises(ValueError):
        parse_is_feed_range_subset_payload({})


def test_parser_rejects_non_boolean_is_subset():
    """A non-Boolean result raises the expected public parsing error."""
    with pytest.raises(ValueError):
        parse_is_feed_range_subset_payload({"IsSubset": "true"})
