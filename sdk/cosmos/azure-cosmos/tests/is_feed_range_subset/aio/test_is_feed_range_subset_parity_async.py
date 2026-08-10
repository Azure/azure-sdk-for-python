# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Async parity tests for ``Container.is_feed_range_subset``.

Async twin of ``test_is_feed_range_subset_parity.py``. Each test runs the same
subset check once on core-python and once on rust through the ``azure.cosmos.aio``
client, then compares the returned yes/no. During migration rust must return the
same answer core-python does for every feed-range pair, or a customer bucketing
session tokens by feed range across machines gets a silent read-your-own-writes
failure.

The pieces mirror the sync file: ``_feed_range`` builds one feed-range dict from
raw bounds, ``parity_container_id`` is one throwaway container the module shares
(created with a sync client so it stays an ordinary fixture), ``_run`` runs one
check on both backends and asserts they agree, and ``test_L0``..``test_L5`` are
the same six feed-range pairs as the sync file.
"""
from __future__ import annotations

import os
import uuid

import pytest

from azure.cosmos import PartitionKey
from azure.cosmos import CosmosClient as SyncCosmosClient
from azure.cosmos.aio import CosmosClient
from azure.cosmos._change_feed.feed_range_internal import FeedRangeInternalEpk
from azure.cosmos._routing.routing_range import Range
from common._parity_helpers import (
    run_on_both_backends_async,
    skip_unless_emulator,
    skip_unless_rust_binding,
)

pytestmark = [skip_unless_emulator(), skip_unless_rust_binding(), pytest.mark.asyncio]


def _feed_range(range_min, range_max, is_min_inclusive=True, is_max_inclusive=False):
    """Build a public feed-range dict from explicit EPK bounds."""
    return FeedRangeInternalEpk(
        Range(range_min, range_max, is_min_inclusive, is_max_inclusive)
    ).to_dict()


@pytest.fixture(scope="module")
def parity_container_id():
    # One throwaway container shared by every test in this module, created and
    # deleted with a sync client (kept sync so it is an ordinary pytest fixture,
    # not an async one). The subset check is a pure client-side computation, so
    # the container is only needed to hang the call on and to resolve
    # feed_range_from_partition_key.
    client = SyncCosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])
    db = client.create_database_if_not_exists("parity_db")
    container_id = "parity_is_feed_range_subset_async_" + uuid.uuid4().hex[:8]
    db.create_container(id=container_id, partition_key=PartitionKey(path="/id"))
    try:
        yield container_id
    finally:
        try:
            db.delete_container(container_id)
        except Exception:  # pylint: disable=broad-except
            pass


async def _run(container_id, parent, child, description, request_kwargs):
    """Run one subset check on both backends and assert they return the same answer."""
    async def _do(client):
        container = client.get_database_client("parity_db").get_container_client(container_id)
        return await container.is_feed_range_subset(parent, child)

    comparison = await run_on_both_backends_async(
        _do, description=description, request_kwargs=request_kwargs
    )
    comparison.print_report()
    comparison.assert_functional_parity()


async def test_is_feed_range_subset_narrow_inside_wide(parity_container_id):
    """A narrow range inside the full key space is a subset on both backends."""
    await _run(
        parity_container_id,
        _feed_range("", "FF"),
        _feed_range("3F", "7F"),
        description="async is_feed_range_subset narrow range inside full range",
        request_kwargs={"parent": "[,FF)", "child": "[3F,7F)"},
    )


async def test_is_feed_range_subset_wide_not_inside_narrow(parity_container_id):
    """The full key space is not a subset of a narrow range on either backend."""
    await _run(
        parity_container_id,
        _feed_range("3F", "7F"),
        _feed_range("", "FF"),
        description="async is_feed_range_subset full range not inside narrow range",
        request_kwargs={"parent": "[3F,7F)", "child": "[,FF)"},
    )


async def test_is_feed_range_subset_equal_ranges(parity_container_id):
    """Two identical ranges are subsets of each other on both backends."""
    await _run(
        parity_container_id,
        _feed_range("3F", "7F"),
        _feed_range("3F", "7F"),
        description="async is_feed_range_subset equal ranges",
        request_kwargs={"parent": "[3F,7F)", "child": "[3F,7F)"},
    )


async def test_is_feed_range_subset_disjoint_ranges(parity_container_id):
    """Two non-overlapping ranges are not subsets on either backend."""
    await _run(
        parity_container_id,
        _feed_range("3F", "7F"),
        _feed_range("", "2F"),
        description="async is_feed_range_subset disjoint ranges",
        request_kwargs={"parent": "[3F,7F)", "child": "[,2F)"},
    )


async def test_is_feed_range_subset_inclusive_exclusive_bounds(parity_container_id):
    """Inclusive/exclusive-bound pairs normalize the same way on both backends."""
    await _run(
        parity_container_id,
        _feed_range("3F", "7F", False, True),
        _feed_range("3F", "7F", True, True),
        description="async is_feed_range_subset inclusive/exclusive bounds (normalization path)",
        request_kwargs={"parent": "(3F,7F]", "child": "[3F,7F]"},
    )


async def test_is_feed_range_subset_from_partition_key(parity_container_id):
    """A key's feed range is a subset of the full key space on both backends."""
    async def _do(client):
        container = client.get_database_client("parity_db").get_container_client(parity_container_id)
        parent = _feed_range("", "FF")
        child = await container.feed_range_from_partition_key("1")
        return await container.is_feed_range_subset(parent, child)

    comparison = await run_on_both_backends_async(
        _do,
        description="async is_feed_range_subset key feed range inside full range",
        request_kwargs={"parent": "[,FF)", "child": "feed_range_from_partition_key('1')"},
    )
    comparison.print_report()
    comparison.assert_functional_parity()


@pytest.mark.parametrize("backend_name", ["core-python", "rust"])
async def test_L6_is_feed_range_subset_leaves_last_response_headers_untouched(parity_container_id, backend_name):
    """is_feed_range_subset is a pure client-side check with no wire call, so it must
    not overwrite ``client_connection.last_response_headers`` -- the headers left by
    the caller's previous real operation. This guards the fix that stopped the rust
    path from clobbering those headers with an empty set."""
    async with CosmosClient(
        os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend=backend_name
    ) as client:
        container = client.get_database_client("parity_db").get_container_client(parity_container_id)
        # A real operation to populate last_response_headers with wire headers.
        await container.upsert_item({"id": "warmup-" + uuid.uuid4().hex})
        before = dict(client.client_connection.last_response_headers or {})
        assert before, "warm-up did not populate last_response_headers on {}".format(backend_name)

        await container.is_feed_range_subset(_feed_range("", "FF"), _feed_range("3F", "7F"))

        after = dict(client.client_connection.last_response_headers or {})
        assert after == before, (
            "is_feed_range_subset changed last_response_headers on {}: "
            "had {} keys, now {}".format(backend_name, len(before), len(after))
        )


async def test_L7_is_feed_range_subset_inverted_range_matches_legacy(parity_container_id):
    """An inverted range (min > max) is a nonsensical opaque value the legacy compare
    tolerates. The rust driver rejects such bounds, so the rust path must fall back to
    legacy rather than raise -- both backends return the same answer and neither errors.
    Guards the invalid-range behavior-drift fix on the async path."""
    await _run(
        parity_container_id,
        _feed_range("7F", "3F"),
        _feed_range("3F", "7F"),
        description="[L7] async is_feed_range_subset inverted range falls back to legacy",
        request_kwargs={"parent": "[7F,3F) (inverted)", "child": "[3F,7F)"},
    )
