# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Parity tests for ``Container.is_feed_range_subset``.

Each test runs the same subset check once on core-python and once on rust, then
compares the returned yes/no. ``is_feed_range_subset`` answers whether one feed
range sits entirely inside another; customers rely on it when they bucket their
own session tokens by feed range across machines, so during migration rust must
return the same answer core-python does for every feed-range pair.

These tests prove the two backends agree with each other across the pair
shapes a customer can pass: a narrow range inside a wide one, the reverse, equal
ranges, disjoint ranges, inclusive/exclusive-bound pairs that exercise the
normalization step, and a real "which container slice does this key fall in"
lookup built from ``feed_range_from_partition_key``. Without it, nothing would
prove rust returns the same answer for those pairs, and a mismatch would reach
customers as a session token filed under the wrong bucket -- a silent
read-your-own-writes failure.

The pieces in this file:
  * ``_feed_range`` -- build one public feed-range dict from raw EPK bounds, so a
    test can hand-craft the exact parent/child pair it wants to check.
  * ``parity_container`` -- one throwaway container the whole module shares (the
    subset check needs a container object to call the method on, nothing more).
  * ``_run`` -- run one subset check on both backends and assert they agree.
  * ``test_L0``..``test_L5`` -- one feed-range pair each (narrow-inside-wide, the
    reverse, equal, disjoint, an inclusive/exclusive pair, and a real key lookup).
"""
from __future__ import annotations

import os
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos._change_feed.feed_range_internal import FeedRangeInternalEpk
from azure.cosmos._routing.routing_range import Range
from common._parity_helpers import (
    run_on_both_backends,
    skip_unless_emulator,
    skip_unless_rust_binding,
)

pytestmark = [skip_unless_emulator(), skip_unless_rust_binding()]


def _feed_range(range_min, range_max, is_min_inclusive=True, is_max_inclusive=False):
    """Build a public feed-range dict from explicit EPK bounds."""
    return FeedRangeInternalEpk(
        Range(range_min, range_max, is_min_inclusive, is_max_inclusive)
    ).to_dict()


@pytest.fixture(scope="module")
def parity_container():
    # One throwaway container shared by every test in this module. The subset
    # check is a pure client-side computation, so the container is only needed
    # to hang the call on and to resolve feed_range_from_partition_key.
    client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])
    db = client.create_database_if_not_exists("parity_db")
    container_id = "parity_is_feed_range_subset_" + uuid.uuid4().hex[:8]
    container = db.create_container(id=container_id, partition_key=PartitionKey(path="/id"))
    yield container
    try:
        db.delete_container(container_id)
    except Exception:  # pylint: disable=broad-except
        pass


def _run(container_id, parent, child, description, request_kwargs):
    """Run one subset check on both backends and assert they return the same answer."""
    def _do(client):
        container = client.get_database_client("parity_db").get_container_client(container_id)
        return container.is_feed_range_subset(parent, child)

    comparison = run_on_both_backends(
        _do, description=description, request_kwargs=request_kwargs
    )
    comparison.print_report()
    comparison.assert_functional_parity()


def test_L0_is_feed_range_subset_narrow_inside_wide(parity_container):
    """A narrow range inside the full key space is a subset on both backends."""
    _run(
        parity_container.id,
        _feed_range("", "FF"),
        _feed_range("3F", "7F"),
        description="[L0] is_feed_range_subset narrow range inside full range",
        request_kwargs={"parent": "[,FF)", "child": "[3F,7F)"},
    )


def test_L1_is_feed_range_subset_wide_not_inside_narrow(parity_container):
    """The full key space is not a subset of a narrow range on either backend."""
    _run(
        parity_container.id,
        _feed_range("3F", "7F"),
        _feed_range("", "FF"),
        description="[L1] is_feed_range_subset full range not inside narrow range",
        request_kwargs={"parent": "[3F,7F)", "child": "[,FF)"},
    )


def test_L2_is_feed_range_subset_equal_ranges(parity_container):
    """Two identical ranges are subsets of each other on both backends."""
    _run(
        parity_container.id,
        _feed_range("3F", "7F"),
        _feed_range("3F", "7F"),
        description="[L2] is_feed_range_subset equal ranges",
        request_kwargs={"parent": "[3F,7F)", "child": "[3F,7F)"},
    )


def test_L3_is_feed_range_subset_disjoint_ranges(parity_container):
    """Two non-overlapping ranges are not subsets on either backend."""
    _run(
        parity_container.id,
        _feed_range("3F", "7F"),
        _feed_range("", "2F"),
        description="[L3] is_feed_range_subset disjoint ranges",
        request_kwargs={"parent": "[3F,7F)", "child": "[,2F)"},
    )


def test_L4_is_feed_range_subset_inclusive_exclusive_bounds(parity_container):
    """Inclusive/exclusive-bound pairs normalize the same way on both backends."""
    _run(
        parity_container.id,
        _feed_range("3F", "7F", False, True),
        _feed_range("3F", "7F", True, True),
        description="[L4] is_feed_range_subset inclusive/exclusive bounds (normalization path)",
        request_kwargs={"parent": "(3F,7F]", "child": "[3F,7F]"},
    )


def test_L5_is_feed_range_subset_from_partition_key(parity_container):
    """A key's feed range is a subset of the full key space on both backends.

    This is the real customer shape: find which container slice a key falls into
    by checking the key's feed range against the container's wider slices.
    """
    def _do(client):
        container = client.get_database_client("parity_db").get_container_client(parity_container.id)
        parent = _feed_range("", "FF")
        child = container.feed_range_from_partition_key("1")
        return container.is_feed_range_subset(parent, child)

    comparison = run_on_both_backends(
        _do,
        description="[L5] is_feed_range_subset key feed range inside full range",
        request_kwargs={"parent": "[,FF)", "child": "feed_range_from_partition_key('1')"},
    )
    comparison.print_report()
    comparison.assert_functional_parity()


@pytest.mark.parametrize("backend_name", ["core-python", "rust"])
def test_L6_is_feed_range_subset_leaves_last_response_headers_untouched(parity_container, backend_name):
    """is_feed_range_subset is a pure client-side check with no wire call, so it must
    not overwrite ``client_connection.last_response_headers`` -- the headers left by
    the caller's previous real operation. This guards the fix that stopped the rust
    path from clobbering those headers with an empty set."""
    client = CosmosClient(
        os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend=backend_name
    )
    container = client.get_database_client("parity_db").get_container_client(parity_container.id)
    # A real operation to populate last_response_headers with wire headers.
    container.upsert_item({"id": "warmup-" + uuid.uuid4().hex})
    before = dict(client.client_connection.last_response_headers or {})
    assert before, "warm-up did not populate last_response_headers on {}".format(backend_name)

    container.is_feed_range_subset(_feed_range("", "FF"), _feed_range("3F", "7F"))

    after = dict(client.client_connection.last_response_headers or {})
    assert after == before, (
        "is_feed_range_subset changed last_response_headers on {}: "
        "had {} keys, now {}".format(backend_name, len(before), len(after))
    )


def test_L7_is_feed_range_subset_inverted_range_matches_legacy(parity_container):
    """An inverted range (min > max) is a nonsensical opaque value the legacy compare
    tolerates (it never validates min <= max). The rust driver rejects such bounds, so
    the rust path must fall back to legacy rather than raise -- both backends return the
    same answer and neither errors. Guards the invalid-range behavior-drift fix."""
    inverted_parent = _feed_range("7F", "3F")
    child = _feed_range("3F", "7F")
    _run(
        parity_container.id,
        inverted_parent,
        child,
        description="[L7] is_feed_range_subset inverted range falls back to legacy",
        request_kwargs={"parent": "[7F,3F) (inverted)", "child": "[3F,7F)"},
    )
