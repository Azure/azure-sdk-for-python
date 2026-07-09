# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Backend-agnostic unit tests for the shared read_feed_ranges Rust-routing helpers.

These tests do not need the emulator or the Rust binding. They lock in exact
parity between the Rust payload parser and the legacy routing-map builder,
including the multi-partition / mixed-case EPK cases the end-to-end emulator
suites cannot reach (the emulator container is single-partition, so its only
range is ("", "FF"), which is invariant under upper-casing).
"""
from __future__ import annotations

import pytest

from azure.cosmos._change_feed.feed_range_internal import FeedRangeInternalEpk
from azure.cosmos._feed_ranges_rust_routing import (
    can_use_rust_backend_for_read_feed_ranges,
    parse_read_feed_ranges_payload,
)
from azure.cosmos._routing.routing_range import PartitionKeyRange, Range


def _legacy_feed_ranges(raw_ranges):
    """Reproduce the legacy read_feed_ranges output for the same raw ranges."""
    return [
        FeedRangeInternalEpk(Range.PartitionKeyRangeToRange(partition_key_range)).to_dict()
        for partition_key_range in raw_ranges
    ]


def test_rust_parser_matches_legacy_for_multi_range_mixed_case():
    """Rust payload → feed ranges must be byte-identical to the legacy builder.

    Uses multiple ranges with lowercase hex EPKs so a dropped .upper() (or any
    other divergence) would make the two backends produce different opaque
    feed-range values.
    """
    raw = [
        {"minInclusive": "", "maxExclusive": "3fffffffffffffff"},
        {"minInclusive": "3fffffffffffffff", "maxExclusive": "7fffffffffffffff"},
        {"minInclusive": "7fffffffffffffff", "maxExclusive": "ff"},
    ]

    rust_payload = {
        "PartitionKeyRanges": [
            {
                PartitionKeyRange.MinInclusive: r["minInclusive"],
                PartitionKeyRange.MaxExclusive: r["maxExclusive"],
            }
            for r in raw
        ]
    }

    rust_result = parse_read_feed_ranges_payload(rust_payload)
    legacy_result = _legacy_feed_ranges(raw)

    assert rust_result == legacy_result
    # And the bounds are normalized to upper-case (matching legacy).
    for feed_range in rust_result:
        assert feed_range["Range"]["min"] == feed_range["Range"]["min"].upper()
        assert feed_range["Range"]["max"] == feed_range["Range"]["max"].upper()


def test_rust_parser_matches_legacy_for_full_range():
    """Single full range parity (the shape the emulator suites exercise)."""
    raw = [{"minInclusive": "", "maxExclusive": "FF"}]
    rust_payload = {
        "PartitionKeyRanges": [
            {PartitionKeyRange.MinInclusive: "", PartitionKeyRange.MaxExclusive: "FF"}
        ]
    }
    assert parse_read_feed_ranges_payload(rust_payload) == _legacy_feed_ranges(raw)


def test_rust_parser_rejects_missing_partition_key_ranges():
    with pytest.raises(ValueError):
        parse_read_feed_ranges_payload({})


def test_rust_parser_rejects_non_list_partition_key_ranges():
    with pytest.raises(ValueError):
        parse_read_feed_ranges_payload({"PartitionKeyRanges": {"minInclusive": ""}})


def test_rust_parser_rejects_non_object_entry():
    with pytest.raises(ValueError):
        parse_read_feed_ranges_payload({"PartitionKeyRanges": ["not-an-object"]})


def test_rust_parser_rejects_non_string_bounds():
    with pytest.raises(ValueError):
        parse_read_feed_ranges_payload(
            {"PartitionKeyRanges": [{"minInclusive": 0, "maxExclusive": 1}]}
        )


def test_gate_requires_backend():
    assert can_use_rust_backend_for_read_feed_ranges(backend=None, kwargs={}) is False


def test_gate_allows_backend_with_no_kwargs():
    assert can_use_rust_backend_for_read_feed_ranges(backend=object(), kwargs={}) is True


def test_gate_falls_back_to_legacy_when_kwargs_present():
    # Legacy forwards unknown kwargs into routing-map reads; the Rust path must
    # stay off until each knob is mirrored, so any kwarg forces legacy.
    assert (
        can_use_rust_backend_for_read_feed_ranges(
            backend=object(), kwargs={"partition_key": "x"}
        )
        is False
    )
