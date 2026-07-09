# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Async ``test_paging_with_continuation_token_async`` test against the
``_backend="rust"`` path.

Self-contained: builds its own database + container in ``asyncSetUp``
and deletes them in ``asyncTearDown``. The class name and method name
match the source at ``tests/test_query_async.py`` so test IDs differ
only by path.

Run with::

    pytest --noconftest tests/query_items/aio/legacy/test_query_async.py -v
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
class TestQueryAsync(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.client = CosmosClient(HOST, KEY, _backend="rust")
        await self.client.__aenter__()
        self._db_id = "legacy_query_paging_async_" + uuid.uuid4().hex[:8]
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

    async def test_paging_with_continuation_token_async(self):
        # Source: tests/test_query_async.py::TestQueryAsync.test_paging_with_continuation_token_async
        await self.container.upsert_item({"pk": "pk", "id": "1"})
        await self.container.upsert_item({"pk": "pk", "id": "2"})

        query_iterable = self.container.query_items(
            query="SELECT * from c",
            partition_key="pk",
            max_item_count=1,
        )
        pager = query_iterable.by_page()
        await pager.__anext__()
        token = pager.continuation_token
        second_page = [item async for item in await pager.__anext__()][0]

        replay_pager = query_iterable.by_page(token)
        replay_second_page = [item async for item in await replay_pager.__anext__()][0]
        assert second_page["id"] == replay_second_page["id"]

