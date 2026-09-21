# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Live split-suite regression for incremental updates to already-split ranges.

Runs in the cosmosSplit and cosmosAADSplit lanes using TestConfig credentials.
Creates a temporary database and scales its `default` container from 400 to
20,000 to 40,000 RU/s. Async cleanup deletes the database on success or failure.

From the package directory with a provisioned-throughput test account configured:
    PYTHONPATH=.:tests python -m unittest tests.test_pk_range_child_update_live_async -v

This standalone runner avoids the package conftest's unrelated provisioning.
Each split has a ten-minute deadline. Missing the real child-update transition
fails the test rather than claiming that a split alone validates the fix.
"""

import asyncio
import json
import time
import unittest
from unittest.mock import patch

import pytest
import test_config

import azure.cosmos
from azure.cosmos import PartitionKey
from azure.cosmos._constants import _Constants
from azure.cosmos._routing.aio import routing_map_provider
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError
from azure.cosmos.http_constants import HttpHeaders


def _record(event, **fields):
    print(json.dumps({"event": event, "time": time.time(), **fields}), flush=True)


@pytest.mark.cosmosSplit
@pytest.mark.cosmosAADSplit
@pytest.mark.timeout(1500)
class TestPkRangeChildUpdateLiveAsync(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        configs = test_config.TestConfig
        self.key_client = CosmosClient(configs.host, configs.masterKey)
        self.addAsyncCleanup(self.key_client.close)
        await self.key_client.__aenter__()
        self.database = await test_config.retry_control_plane_async(
            self.key_client.create_database, test_config.unique_database_id("PKRangeChildUpdate")
        )
        self.addAsyncCleanup(self._delete_database)
        _record("database_created", database=self.database.id, sdk=azure.cosmos.__version__)
        self.key_container = await test_config.retry_control_plane_async(
            self.database.create_container, "default", partition_key=PartitionKey(path="/pk"), offer_throughput=400
        )
        self.client = configs.create_data_client_async(user_agent_suffix="habitat-migration-service")
        self.addAsyncCleanup(self.client.close)
        await self.client.__aenter__()
        self.container = self.client.get_database_client(self.database.id).get_container_client("default")
        properties = await self.container.read()
        self.feed_options = {_Constants.ContainerRID: properties["_rid"]}
        self.provider = self.client.client_connection._routing_map_provider
        self.routing_map = await self.provider.get_routing_map(self.container.container_link, self.feed_options)
        self.expected_ids = [f"item-{i:03d}" for i in range(50)]
        for item_id in self.expected_ids:
            await self.container.create_item({"id": item_id, "pk": item_id})
        self.scans = 0

    async def _delete_database(self):
        await asyncio.wait_for(
            test_config.retry_control_plane_async(self.key_client.delete_database, self.database.id), timeout=120
        )
        _record("database_deleted", database=self.database.id)

    async def _scan(self):
        items = self.container.query_items(
            query="SELECT * FROM c",
            feed_range={"Range": {"min": "", "max": "FF", "isMinInclusive": True, "isMaxInclusive": False}},
            max_item_count=10,
        )
        ids = [item["id"] async for item in items]
        self.assertEqual(sorted(ids), self.expected_ids)
        self.scans += 1

    async def _split_to(self, throughput):
        old_ids = set(self.routing_map._rangeById)
        _record("scale_start", throughput=throughput, previous_ids=sorted(old_ids))
        while True:
            try:
                await self.key_container.replace_throughput(throughput)
                break
            except CosmosHttpResponseError as error:
                if error.status_code != 423:
                    raise
                _record("waiting_for_previous_scale", throughput=throughput)
                await asyncio.sleep(5)
        while True:
            previous = self.routing_map
            self.routing_map = await self.provider.get_routing_map(
                self.container.container_link,
                self.feed_options,
                force_refresh=True,
                previous_routing_map=previous,
            )
            if self.routing_map.change_feed_etag != previous.change_feed_etag:
                _record(
                    "routing_map",
                    etag=self.routing_map.change_feed_etag,
                    ranges=[
                        {"id": r.id, "parents": r.parents, "status": r.status}
                        for r in self.routing_map.get_ordered_partition_key_ranges()
                    ],
                )
            await self._scan()
            new_ids = set(self.routing_map._rangeById)
            if new_ids.isdisjoint(old_ids) and len(new_ids) > len(old_ids):
                offer = await self.key_container.get_throughput()
                if not offer.properties["content"].get("isOfferReplacePending", False):
                    self.assertEqual(offer.offer_throughput, throughput)
                    _record("split_complete", throughput=throughput, ids=sorted(new_ids), scans=self.scans)
                    return
            await asyncio.sleep(1)

    async def test_existing_child_revision_does_not_full_reload(self):
        self.assertEqual(len(self.routing_map._rangeById), 1)
        await asyncio.wait_for(self._split_to(20000), timeout=600)
        self.assertTrue(all(r.parents for r in self.routing_map.get_ordered_partition_key_ranges()))

        original_read = self.client.client_connection._ReadPartitionKeyRanges
        original_process = routing_map_provider.process_fetched_ranges
        requested_etags = []
        child_updates = []

        def observe_read(link, options, **kwargs):
            requested_etags.append(kwargs["headers"].get(HttpHeaders.IfNoneMatch))
            return original_read(link, options, **kwargs)

        def observe_process(ranges, previous, collection_id, collection_link, new_etag):
            candidates = []
            if previous is not None:
                for raw in ranges:
                    cached = previous.get_range_by_partition_key_range_id(raw["id"])
                    parents = raw.get("parents") or []
                    if (
                        cached is not None
                        and parents
                        and all(parent not in previous._rangeById for parent in parents)
                        and raw.get("status") == "splitting"
                        and cached.status != "splitting"
                    ):
                        candidates.append({"id": raw["id"], "parents": parents, "status": raw["status"]})
            result = original_process(ranges, previous, collection_id, collection_link, new_etag)
            for update in candidates:
                child_updates.append(update)
                _record("existing_child_update_merged", **update)
            return result

        # Observe real service payloads and production processing; neither wrapper changes them.
        with patch.object(self.client.client_connection, "_ReadPartitionKeyRanges", new=observe_read), patch.object(
            routing_map_provider, "process_fetched_ranges", new=observe_process
        ):
            await asyncio.wait_for(self._split_to(40000), timeout=600)

        self.assertTrue(child_updates, "No real existing-child status transition was observed; fix not validated.")
        self.assertTrue(requested_etags)
        self.assertNotIn(None, requested_etags, "A full routing-map reload occurred during the second split.")
        await asyncio.wait_for(self._scan(), timeout=60)
        _record(
            "validated",
            child_updates=child_updates,
            metadata_requests=len(requested_etags),
            full_reloads=requested_etags.count(None),
            scans=self.scans,
        )


if __name__ == "__main__":
    unittest.main()
