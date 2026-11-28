# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Original async read-all assertions on isolated Rust-backed resources."""

import unittest
import uuid

import pytest
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos import PartitionKey
from config.clients import create_data_client_async, create_setup_client_async


class _OwnedReadAllTests(unittest.IsolatedAsyncioTestCase):
    """The key client owns databases and containers; the data client (AAD in
    AAD lanes) does item work, as in the originals."""

    async def asyncSetUp(self):
        self.key_client = create_setup_client_async(_backend="rust")
        self.addAsyncCleanup(self.key_client.close)
        await self.key_client.__aenter__()
        self.client = create_data_client_async(_backend="rust")
        self.addAsyncCleanup(self.client.close)
        await self.client.__aenter__()
        self.key_database = await self.key_client.create_database(
            "read-all-original-" + uuid.uuid4().hex
        )
        self.addAsyncCleanup(self.key_client.delete_database, self.key_database.id)
        self.test_database = self.client.get_database_client(self.key_database.id)

    async def _create_container_for_test(self, container_id, partition_key):
        await self.key_database.create_container(
            container_id, partition_key=partition_key
        )
        return self.test_database.get_container_client(container_id)

    async def _delete_container_for_test(self, container_id):
        await self.key_database.delete_container(container_id)


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosQuery
@pytest.mark.cosmosAADQuery
class TestQueryResponseHeadersAsync(_OwnedReadAllTests):

    async def test_read_all_items_response_headers_async_rust(self):
        """read_all_items pagers expose the same headers contract as queries."""
        # Source: tests/test_query_response_headers_async.py::TestQueryResponseHeadersAsync.test_read_all_items_response_headers_async
        cid = "test_headers_readall_async_" + str(uuid.uuid4())
        created_collection = await self._create_container_for_test(
            cid, PartitionKey(path="/pk")
        )
        try:
            for i in range(8):
                await created_collection.create_item(
                    body={"pk": "test", "id": f"item_{i}"}
                )

            paged = created_collection.read_all_items(max_item_count=3)
            items = [item async for item in paged]
            assert len(items) == 8

            assert hasattr(
                paged, "get_response_headers"
            ), "read_all_items pager must expose get_response_headers"
            headers = paged.get_response_headers()
            assert isinstance(headers, CaseInsensitiveDict)
            assert "x-ms-request-charge" in headers
        finally:
            await self._delete_container_for_test(cid)
