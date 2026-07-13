# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Async ``test_query_iterable_functionality_async`` test against the
``_backend="rust"`` path.

Self-contained: builds its own database + container in ``asyncSetUp``
and deletes them in ``asyncTearDown``. The class name and method name
match the source at ``tests/test_crud_async.py`` so test IDs differ
only by path.

Run with::

    pytest --noconftest tests/read_all_items/aio/legacy/test_crud_async.py -v
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
class TestCRUDOperationsAsync(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.client = CosmosClient(HOST, KEY, _backend="rust")
        await self.client.__aenter__()
        self._db_id = "legacy_read_all_crud_async_" + uuid.uuid4().hex[:8]
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

    async def test_query_iterable_functionality_async(self):
        # Source: tests/test_crud_async.py::TestCRUDOperationsAsync.test_query_iterable_functionality_async
        # End-to-end on the real Rust driver: read_all_items takes no partition key,
        # so this is a whole-container read served through the Rust query fast path.
        # If it were routed to a native read-feed the driver would reject it and this
        # would error -- which is why running it against a real account matters.
        doc1 = await self.container.upsert_item(body={"id": "doc1", "prop1": "value1"})
        doc2 = await self.container.upsert_item(body={"id": "doc2", "prop1": "value2"})
        doc3 = await self.container.upsert_item(body={"id": "doc3", "prop1": "value3"})
        resources = {
            "coll": self.container,
            "doc1": doc1,
            "doc2": doc2,
            "doc3": doc3,
        }

        results = resources["coll"].read_all_items(max_item_count=2)
        docs = [doc async for doc in results]
        assert 3 == len(docs)
        assert resources["doc1"]["id"] == docs[0]["id"]
        assert resources["doc2"]["id"] == docs[1]["id"]
        assert resources["doc3"]["id"] == docs[2]["id"]

        results = resources["coll"].read_all_items(max_item_count=2)
        counter = 0
        async for doc in results:
            counter += 1
            if counter == 1:
                assert resources["doc1"]["id"] == doc["id"]
            elif counter == 2:
                assert resources["doc2"]["id"] == doc["id"]
            elif counter == 3:
                assert resources["doc3"]["id"] == doc["id"]
        assert counter == 3

        results = resources["coll"].read_all_items(max_item_count=2)
        page_iter = results.by_page()
        first_block = [page async for page in await page_iter.__anext__()]
        assert 2 == len(first_block)
        assert resources["doc1"]["id"] == first_block[0]["id"]
        assert resources["doc2"]["id"] == first_block[1]["id"]
        assert 1 == len([page async for page in await page_iter.__anext__()])
        with self.assertRaises(StopAsyncIteration):
            await page_iter.__anext__()

