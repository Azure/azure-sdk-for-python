# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Async real-account integration tests for the /pkranges change-feed drain
loop. Mirror of ``test_pk_range_drain_integration.py``.

See that module's docstring for the contract being pinned.
"""

import uuid
from typing import List, Tuple

import pytest
import pytest_asyncio

import test_config
from azure.cosmos._routing.collection_routing_map import CollectionRoutingMap
from azure.cosmos._routing.routing_range import Range
from azure.cosmos.aio import CosmosClient
from azure.cosmos.partition_key import PartitionKey

CONFIG = test_config.TestConfig()
HOST = CONFIG.host
KEY = CONFIG.masterKey
DATABASE_ID = CONFIG.TEST_DATABASE_ID

REPRO_CONTAINER_ID = "PkRangeDrainIntegrationAsync-" + str(uuid.uuid4())
REPRO_PARTITION_KEY = "pk"
REPRO_THROUGHPUT = CONFIG.THROUGHPUT_FOR_5_PARTITIONS
REPRO_DOC_COUNT = 50


def _client() -> CosmosClient:
    return CosmosClient(HOST, KEY)


def _get_container(client: CosmosClient):
    db = client.get_database_client(DATABASE_ID)
    return db.get_container_client(REPRO_CONTAINER_ID)


def _ranges_as_pairs(routing_map_entries) -> List[Tuple[str, str]]:
    return sorted(
        (entry["minInclusive"], entry["maxExclusive"])
        for entry in routing_map_entries
    )


def _assert_complete_cover(pairs: List[Tuple[str, str]]) -> None:
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


@pytest_asyncio.fixture(scope="class", autouse=True)
async def setup_and_teardown_async():
    client = _client()
    try:
        db = client.get_database_client(DATABASE_ID)
        container = await db.create_container_if_not_exists(
            id=REPRO_CONTAINER_ID,
            partition_key=PartitionKey(path="/" + REPRO_PARTITION_KEY, kind="Hash"),
            offer_throughput=REPRO_THROUGHPUT)
        for i in range(REPRO_DOC_COUNT):
            await container.upsert_item({
                REPRO_PARTITION_KEY: f"pk-{i:04d}",
                "id": f"doc-{i:04d}",
                "value": i,
            })
        yield
        try:
            await db.delete_container(REPRO_CONTAINER_ID)
        except Exception:  # pylint: disable=broad-except
            pass
    finally:
        await client.close()


@pytest.mark.cosmosQuery
@pytest.mark.asyncio
@pytest.mark.usefixtures("setup_and_teardown_async")
class TestPkRangeDrainIntegrationAsync:
    """Async parity for the /pkranges drain-loop pagination contract."""

    async def test_drain_loop_paginates_pkranges_change_feed_async(self, monkeypatch):
        """Async mirror of the sync drain pagination test.

        Forces ``PAGE_SIZE_CHANGE_FEED = "1"`` and verifies the drain loop:

        * issues at least one ``_ReadPartitionKeyRanges`` page **per physical
          partition** (so the gateway is honoring the page-size override and
          the drain is genuinely paginating, not just terminating on a single
          page + 304), and
        * still produces a routing map identical to the default-page-size
          baseline, with a complete cover of ``["", "FF")``.
        """
        client = _client()
        try:
            container = _get_container(client)
            collection_link = container.container_link
            provider = client.client_connection._routing_map_provider
            document_client = client.client_connection

            # Baseline -- default page size.
            provider.clear_cache()
            baseline_entries = await provider.get_overlapping_ranges(
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

            # Spy + force PAGE_SIZE_CHANGE_FEED="1".
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
            paginated_entries = await provider.get_overlapping_ranges(
                collection_link,
                [Range.get_full_range()],
                feed_options=None,
                force_refresh=True,
            )
            paginated_pairs = _ranges_as_pairs(paginated_entries)

            # See sync mirror for rationale: with PAGE_SIZE_CHANGE_FEED="1"
            # we expect roughly one call per physical partition plus a
            # terminating empty/304 page. call_count >= len(baseline_pairs)
            # proves the gateway honored the page-size override and the
            # drain genuinely paginated -- not just "first page returned
            # everything, second page was the 304."
            assert call_count["n"] >= len(baseline_pairs), (
                f"Expected drain loop to issue at least one page per physical "
                f"partition (got {call_count['n']} call(s) for "
                f"{len(baseline_pairs)} partition(s)). Either the gateway is no "
                f"longer honoring PAGE_SIZE_CHANGE_FEED='1' or the drain loop "
                f"is short-circuiting prematurely."
            )

            _assert_complete_cover(paginated_pairs)
            assert paginated_pairs == baseline_pairs, (
                "Paginated routing map drifted from baseline:\n"
                f"  baseline:  {baseline_pairs}\n"
                f"  paginated: {paginated_pairs}"
            )
        finally:
            await client.close()


if __name__ == "__main__":
    import unittest
    unittest.main()
