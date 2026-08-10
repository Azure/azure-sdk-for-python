# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Parity tests for ``Container.read_feed_ranges``: run the same call once on the existing
core-python engine and once on the rust engine, then compare the partition ranges returned.
Customers split a large read across these ranges to process partitions in parallel; during the
migration the rust path must return the same ranges. Without these tests, rust could return
different boundaries or miss a range and a customer splitting work by feed range would duplicate
or skip data unnoticed. They run only when a real account and the compiled rust binding are both
present."""
from __future__ import annotations

import os
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey
from common._parity_helpers import (
    run_on_both_backends,
    skip_unless_emulator,
    skip_unless_rust_binding,
)

pytestmark = [skip_unless_emulator(), skip_unless_rust_binding()]


@pytest.fixture
def container_for(request):
    # Fresh throwaway container per test, deleted afterward, so tests don't share data.
    client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])
    db = client.create_database_if_not_exists("parity_db")
    container_id = "parity_feed_ranges_" + request.node.name + "_" + uuid.uuid4().hex[:6]
    container = db.create_container(id=container_id, partition_key=PartitionKey(path="/pk"))
    yield container
    try:
        db.delete_container(container_id)
    except Exception:  # pylint: disable=broad-except
        pass


def _normalize_feed_ranges(feed_ranges):
    # Reduce each range to its (min, max) pair and sort, so the two engines compare equal
    # regardless of ordering or incidental fields.
    normalized = []
    for feed_range in feed_ranges:
        range_info = feed_range["Range"]
        normalized.append((range_info["min"], range_info["max"]))
    return sorted(normalized)


def test_read_feed_ranges_baseline(container_for):
    """Baseline read_feed_ranges returns the same normalized ranges."""
    # Without this, a basic divergence in the returned range boundaries would go unnoticed.

    def _do(client):
        container = client.get_database_client("parity_db").get_container_client(container_for.id)
        return _normalize_feed_ranges(list(container.read_feed_ranges()))

    comparison = run_on_both_backends(
        _do,
        description="read_feed_ranges baseline",
    )
    comparison.print_report()
    comparison.assert_functional_parity()


def test_read_feed_ranges_force_refresh(container_for):
    """Force-refresh read_feed_ranges stays equivalent on both backends."""
    # force_refresh=True bypasses the cached routing map and re-fetches the ranges; without
    # this, the rust force-refresh path could return stale or different ranges unnoticed.

    def _do(client):
        container = client.get_database_client("parity_db").get_container_client(container_for.id)
        return _normalize_feed_ranges(list(container.read_feed_ranges(force_refresh=True)))

    comparison = run_on_both_backends(
        _do,
        description="read_feed_ranges force_refresh=True",
    )
    comparison.print_report()
    comparison.assert_functional_parity()
