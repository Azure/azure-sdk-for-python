# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Async ``test_container_query_items_none_options_partition_async`` test against
the ``_backend="rust"`` path.

Self-contained: builds its own database + container in ``asyncSetUp``
and deletes them in ``asyncTearDown``. The class name and method name
match the source at ``tests/test_none_options_async.py`` so test IDs
differ only by path.

Run with::

    pytest --noconftest tests/query_items/aio/legacy/test_none_options_async.py -v
"""
import os
import unittest
import uuid

import pytest

from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


@pytest.mark.cosmosEmulator
class TestNoneOptionsAsync(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.client = CosmosClient(HOST, KEY, _backend="rust")
        await self.client.__aenter__()
        self._db_id = "legacy_query_none_options_async_" + uuid.uuid4().hex[:8]
        self._container_id = "c_" + uuid.uuid4().hex[:8]
        self.database = await self.client.create_database(self._db_id)
        self.container = await self.database.create_container(
            id=self._container_id,
            partition_key=PartitionKey(path="/pk"),
        )

    async def asyncTearDown(self):
        try:
            await self.client.delete_database(self._db_id)
        except Exception:  # pylint: disable=broad-except
            pass
        await self.client.close()

    async def test_container_query_items_none_options_partition_async(self):
        # Source: tests/test_none_options_async.py::TestNoneOptionsAsync.test_container_query_items_none_options_partition_async
        item = {"id": str(uuid.uuid4()), "pk": "pk-value", "value": 42}
        await self.container.create_item(item)
        pager = self.container.query_items(
            "SELECT * FROM c",
            continuation_token_limit=None,
            enable_scan_in_query=None,
            initial_headers=None,
            max_integrated_cache_staleness_in_ms=None,
            max_item_count=None,
            parameters=None,
            partition_key=None,
            populate_index_metrics=None,
            populate_query_advice=None,
            populate_query_metrics=None,
            priority=None,
            response_hook=None,
            session_token=None,
            throughput_bucket=None,
        )
        items = [doc async for doc in pager]
        assert len(items) >= 1

