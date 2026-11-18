# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Async original point-operation response-hook comparisons, run on the Rust path.

Each point operation's callback headers are compared with the same
operation's returned headers; delete_item has no body, so only the callback
is checked. Uses a test-owned database.
"""

import unittest
import uuid

import pytest

from config import clients, settings
from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosQuery
@pytest.mark.cosmosAADQuery
class TestQueryResponseHeadersAsync(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        config = settings.TestSettings
        self.key_client = CosmosClient(config.host, config.masterKey, _backend="rust")
        self.addAsyncCleanup(self.key_client.close)
        await self.key_client.__aenter__()
        database_id = "delete_response_hooks_async_" + uuid.uuid4().hex
        self.key_db = await self.key_client.create_database(database_id)
        self.addAsyncCleanup(self.key_client.delete_database, database_id)
        self.client = clients.create_data_client_async(_backend="rust")
        self.addAsyncCleanup(self.client.close)
        await self.client.__aenter__()
        self.created_db = self.client.get_database_client(database_id)

    async def _create_container_for_test(self, container_id, partition_key):
        await self.key_db.create_container(container_id, partition_key)
        return self.created_db.get_container_client(container_id)

    async def _delete_container_for_test(self, container_id):
        await self.key_db.delete_container(container_id)

    async def test_response_hook_parity_point_ops_async_rust(self):
        # Source: tests/test_query_response_headers_async.py::TestQueryResponseHeadersAsync.test_response_hook_parity_point_ops_async
        cid = "test_hookparity_point_async_" + str(uuid.uuid4())
        created_collection = await self._create_container_for_test(cid, PartitionKey(path="/pk"))
        try:
            captured = []

            def hook(headers, _body):
                captured.append(dict(headers))

            # create_item
            captured.clear()
            created = await created_collection.create_item(
                body={"pk": "p", "id": "doc1", "value": 1},
                response_hook=hook,
            )
            assert len(captured) == 1
            assert (
                created.get_response_headers()["x-ms-request-charge"]
                == captured[0]["x-ms-request-charge"]
            )

            # read_item
            captured.clear()
            read = await created_collection.read_item(
                item="doc1", partition_key="p", response_hook=hook,
            )
            assert len(captured) == 1
            assert (
                read.get_response_headers()["x-ms-request-charge"]
                == captured[0]["x-ms-request-charge"]
            )

            # replace_item
            captured.clear()
            replaced = await created_collection.replace_item(
                item="doc1",
                body={"pk": "p", "id": "doc1", "value": 2},
                response_hook=hook,
            )
            assert len(captured) == 1
            assert (
                replaced.get_response_headers()["x-ms-request-charge"]
                == captured[0]["x-ms-request-charge"]
            )

            # upsert_item
            captured.clear()
            upserted = await created_collection.upsert_item(
                body={"pk": "p", "id": "doc1", "value": 3},
                response_hook=hook,
            )
            assert len(captured) == 1
            assert (
                upserted.get_response_headers()["x-ms-request-charge"]
                == captured[0]["x-ms-request-charge"]
            )

            # delete_item: returns None, but the hook still fires once.
            captured.clear()
            await created_collection.delete_item(
                item="doc1", partition_key="p", response_hook=hook,
            )
            assert len(captured) == 1
            assert "x-ms-request-charge" in captured[0]
        finally:
            await self._delete_container_for_test(cid)
