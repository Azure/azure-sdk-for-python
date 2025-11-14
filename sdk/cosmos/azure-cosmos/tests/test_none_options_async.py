# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import unittest
import uuid
from typing import Optional

import pytest

from azure.cosmos.aio import CosmosClient, DatabaseProxy
from azure.cosmos import PartitionKey
import test_config


@pytest.mark.cosmosLong
class TestNoneOptions(unittest.IsolatedAsyncioTestCase):
    configs = test_config.TestConfig
    host = configs.host
    masterKey = configs.masterKey
    connectionPolicy = configs.connectionPolicy

    async def asyncSetUp(self):
        use_multiple_write_locations = False
        if os.environ.get("AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER", "False") == "True":
            use_multiple_write_locations = True
        self.client = CosmosClient(self.host, self.masterKey, multiple_write_locations=use_multiple_write_locations)
        await self.client.__aenter__()
        self.database = self.client.get_database_client(self.configs.TEST_DATABASE_ID)
        self.container = self.database.get_container_client(self.configs.TEST_SINGLE_PARTITION_CONTAINER_ID)



    async def asyncTearDown(self):
        await self.client.close()

    async def _create_sample_item(self):
        item = {"id": str(uuid.uuid4()), "pk": "pk-value", "value": 42}
        await self.container.create_item(item, pre_trigger_include=None, post_trigger_include=None, indexing_directive=None,
                                     enable_automatic_id_generation=False, session_token=None, initial_headers=None,
                                     priority=None, no_response=None, retry_write=None, throughput_bucket=None)
        return item

    async def test_container_read_none_options(self):
        result = await self.container.read(populate_partition_key_range_statistics=None, populate_quota_info=None,
                                      priority=None, initial_headers=None)
        assert result

    async def test_container_create_item_none_options(self):
        item = {"id": str(uuid.uuid4()), "pk": "pk-value", "value": 1}
        created = await self.container.create_item(item, pre_trigger_include=None, post_trigger_include=None,
                                               indexing_directive=None, enable_automatic_id_generation=False,
                                               session_token=None, initial_headers=None, priority=None, no_response=None,
                                               retry_write=None, throughput_bucket=None)
        assert created["id"] == item["id"]

    async def test_container_read_item_none_options(self):
        item = await self._create_sample_item(container)
        read_back = await self.container.read_item(item["id"], partition_key=item["pk"], post_trigger_include=None,
                                              session_token=None, initial_headers=None,
                                              max_integrated_cache_staleness_in_ms=None, priority=None,
                                              throughput_bucket=None)
        assert read_back["id"] == item["id"]

    async def test_container_read_all_items_none_options(self):
        await self._create_sample_item()
        pager = self.container.read_all_items(max_item_count=None, session_token=None, initial_headers=None,
                                         max_integrated_cache_staleness_in_ms=None, priority=None,
                                         throughput_bucket=None)
        items = [item async for item in pager]
        assert len(items) >= 1

    async def test_container_read_items_none_options(self):
        item = await self._create_sample_item()
        results = await self.container.read_items([(item["id"], item["pk"])], max_concurrency=None, consistency_level=None,
                                              session_token=None, initial_headers=None, excluded_locations=None,
                                              priority=None, throughput_bucket=None)
        assert any(r["id"] == item["id"] for r in results)

    async def test_container_query_items_none_options_partition(self):
        await self._create_sample_item()
        pager = self.container.query_items("SELECT * FROM c", continuation_token_limit=None, enable_scan_in_query=None,
                                      initial_headers=None, max_integrated_cache_staleness_in_ms=None, max_item_count=None,
                                      parameters=None, partition_key=None, populate_index_metrics=None,
                                      populate_query_metrics=None, priority=None, response_hook=None, session_token=None,
                                      throughput_bucket=None)
        items = [doc async for doc in pager]
        assert len(items) >= 1

