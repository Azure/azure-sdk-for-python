# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Real-account integration tests for the /pkranges change-feed drain loop.

These tests pin the multi-page pagination contract for the routing-map
fetch path. They:

* Force ``PAGE_SIZE_CHANGE_FEED = "1"`` so the service returns one
  partition key range per page, exercising the drain loop across multiple
  pages even on small containers.
* Compare the paginated routing map against the baseline obtained with the
  default page size — both must produce the same set of physical partition
  key ranges and form a complete, gap-free cover of ``["", "FF")``.

Mocked unit-level coverage of the same drain loop lives in
``test_pk_range_drain.py`` / ``test_pk_range_drain_async.py``.

Async parity lives in ``test_pk_range_drain_integration_async.py``.
"""

import uuid
from typing import List, Tuple

import pytest

import test_config
from azure.cosmos import CosmosClient
from azure.cosmos._routing.collection_routing_map import CollectionRoutingMap
from azure.cosmos._routing.routing_range import Range
from azure.cosmos.partition_key import PartitionKey

CONFIG = test_config.TestConfig()
HOST = CONFIG.host
KEY = CONFIG.masterKey
DATABASE_ID = CONFIG.TEST_DATABASE_ID

# Dedicated container provisioned at THROUGHPUT_FOR_5_PARTITIONS so the
# routing map has multiple physical partition key ranges out of the box.
# With PAGE_SIZE_CHANGE_FEED forced to "1", the drain loop must issue at
# least one page per partition (>1 total), exercising pagination.
REPRO_CONTAINER_ID = "PkRangeDrainIntegration-" + str(uuid.uuid4())
REPRO_PARTITION_KEY = "pk"
REPRO_THROUGHPUT = CONFIG.THROUGHPUT_FOR_5_PARTITIONS
REPRO_DOC_COUNT = 50


def _client() -> CosmosClient:
    return CosmosClient(HOST, KEY)


def _get_container(client: CosmosClient):
    db = client.get_database_client(DATABASE_ID)
    return db.get_container_client(REPRO_CONTAINER_ID)


def _ranges_as_pairs(routing_map_entries) -> List[Tuple[str, str]]:
    """Normalize a list of partition-key-range dicts to sorted (min, max)
    string tuples for deterministic set comparison."""
    return sorted(
        (entry["minInclusive"], entry["maxExclusive"])
        for entry in routing_map_entries
    )


def _assert_complete_cover(pairs: List[Tuple[str, str]]) -> None:
    """Assert the (min, max) pairs form a contiguous, non-overlapping cover
    of ``["", "FF")`` -- the full effective-partition-key space."""
    assert pairs, "Routing map returned no partition key ranges"
    assert pairs[0][0] == CollectionRoutingMap.MinimumInclusiveEffectivePartitionKey, (
        f"First range must start at '' (got {pairs[0][0]!r})"
    )
    assert pairs[-1][1] == CollectionRoutingMap.MaximumExclusiveEffectivePartitionKey, (
        f"Last range must end at 'FF' (got {pairs[-1][1]!r})"
    )
    for prev, curr in zip(pairs, pairs[1:]):
        assert prev[1] == curr[0], (
            f"Gap or overlap detected: previous max {prev[1]!r} != next min {curr[0]!r}"
        )


@pytest.fixture(scope="class", autouse=True)
def setup_and_teardown():
    """Provision a multi-partition container and tear it down at end of class."""
    client = _client()
    db = client.get_database_client(DATABASE_ID)
    container = db.create_container_if_not_exists(
        id=REPRO_CONTAINER_ID,
        partition_key=PartitionKey(path="/" + REPRO_PARTITION_KEY, kind="Hash"),
        offer_throughput=REPRO_THROUGHPUT)
    for i in range(REPRO_DOC_COUNT):
        container.upsert_item({
            REPRO_PARTITION_KEY: f"pk-{i:04d}",
            "id": f"doc-{i:04d}",
            "value": i,
        })
    yield
    try:
        db.delete_container(REPRO_CONTAINER_ID)
    except Exception:  # pylint: disable=broad-except
        pass


@pytest.mark.cosmosQuery
class TestPkRangeDrainIntegration:
    """End-to-end checks that the /pkranges change-feed drain loop correctly
    paginates when the service returns more pages than the default page
    size would surface in a single request."""

    def test_drain_loop_paginates_pkranges_change_feed(self, monkeypatch):
        """Force ``PAGE_SIZE_CHANGE_FEED = "1"`` and verify the drain loop:

        * issues at least one ``_ReadPartitionKeyRanges`` page **per physical
          partition** (so the gateway is honoring the page-size override and
          the drain is genuinely paginating, not just terminating on a single
          page + 304), and
        * still produces a routing map identical to the default-page-size
          baseline, with a complete cover of ``["", "FF")``.

        A regression in the drain loop's continuation handling would surface
        here as either a single-page fetch (no pagination), a call count
        below the ranges-per-partition floor (gateway returning everything
        on one page despite ``PAGE_SIZE=1``), or a routing map that is
        missing/duplicating ranges relative to the baseline.
        """
        client = _client()
        container = _get_container(client)
        collection_link = container.container_link
        provider = client.client_connection._routing_map_provider
        document_client = client.client_connection

        # ----------------------------------------------------------------
        # Baseline: default PAGE_SIZE_CHANGE_FEED ("-1" => server default).
        # ----------------------------------------------------------------
        provider.clear_cache()
        baseline_entries = provider.get_overlapping_ranges(
            collection_link,
            [Range.get_full_range()],
            feed_options=None,
            force_refresh=True,
        )
        baseline_pairs = _ranges_as_pairs(baseline_entries)
        _assert_complete_cover(baseline_pairs)
        assert len(baseline_pairs) >= 2, (
            "Test container should provision multiple physical partitions; "
            f"got only {len(baseline_pairs)}. Check THROUGHPUT_FOR_5_PARTITIONS."
        )

        # ----------------------------------------------------------------
        # Paginated: force PAGE_SIZE_CHANGE_FEED="1" so each /pkranges page
        # returns exactly one range. Spy on the document client's
        # ``_ReadPartitionKeyRanges`` to count drain pages.
        # ----------------------------------------------------------------
        call_count = {"n": 0}
        original_read = document_client._ReadPartitionKeyRanges

        def counting_read(*args, **kwargs):
            call_count["n"] += 1
            return original_read(*args, **kwargs)

        monkeypatch.setattr(
            document_client, "_ReadPartitionKeyRanges", counting_read
        )
        monkeypatch.setattr(
            "azure.cosmos._routing._routing_map_provider_common.PAGE_SIZE_CHANGE_FEED",
            "1",
        )

        provider.clear_cache()
        paginated_entries = provider.get_overlapping_ranges(
            collection_link,
            [Range.get_full_range()],
            feed_options=None,
            force_refresh=True,
        )
        paginated_pairs = _ranges_as_pairs(paginated_entries)

        # The drain loop must have made at least one continuation request
        # per physical partition (with PAGE_SIZE_CHANGE_FEED="1", we expect
        # roughly one call per range plus a terminating empty/304 page). A
        # call_count >= len(baseline_pairs) proves the gateway honored the
        # page-size override and the drain genuinely paginated -- not just
        # "first page returned everything, second page was the 304." Strict
        # one-page-per-partition pagination is covered by the unit tests in
        # ``test_pk_range_drain.py``; the real value this integration test
        # adds is end-to-end correctness across the live drain + merge path.
        assert call_count["n"] >= len(baseline_pairs), (
            f"Expected drain loop to issue at least one page per physical "
            f"partition (got {call_count['n']} call(s) for "
            f"{len(baseline_pairs)} partition(s)). Either the gateway is no "
            f"longer honoring PAGE_SIZE_CHANGE_FEED='1' or the drain loop "
            f"is short-circuiting prematurely."
        )

        # Paginated routing map must match the baseline exactly (same set
        # of physical ranges) and form a complete cover.
        _assert_complete_cover(paginated_pairs)
        assert paginated_pairs == baseline_pairs, (
            "Paginated routing map drifted from baseline:\n"
            f"  baseline:  {baseline_pairs}\n"
            f"  paginated: {paginated_pairs}"
        )


if __name__ == "__main__":
    import unittest
    unittest.main()
