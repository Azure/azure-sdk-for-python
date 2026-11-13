# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Original async read-all assertions on isolated Rust-backed resources."""

import unittest
import uuid

import pytest
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos import PartitionKey, exceptions
from azure.cosmos.aio import CosmosClient
from azure.cosmos.http_constants import StatusCodes
from config.settings import TestSettings


class _OwnedReadAllTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = CosmosClient(
            TestSettings.host, TestSettings.masterKey, _backend="rust"
        )
        self.addAsyncCleanup(self.client.close)
        await self.client.__aenter__()
        self.database = await self.client.create_database(
            "read-all-original-" + uuid.uuid4().hex
        )
        self.addAsyncCleanup(self.client.delete_database, self.database.id)

    async def _create_container_for_test(self, container_id, partition_key):
        return await self.database.create_container(
            container_id, partition_key=partition_key
        )

    async def _delete_container_for_test(self, container_id):
        await self.database.delete_container(container_id)


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


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
class TestTransactionalBatchAsync(_OwnedReadAllTests):

    async def test_batch_delete_async_rust(self):
        # Source: tests/test_transactional_batch_async.py::TestTransactionalBatchAsync.test_batch_delete_async
        cid = "batch_delete_async" + str(uuid.uuid4())
        container = await self._create_container_for_test(
            cid, PartitionKey(path="/company")
        )
        create_batch = []
        delete_batch = []
        for i in range(10):
            item_id = str(uuid.uuid4())
            create_batch.append(("create", ({"id": item_id, "company": "Microsoft"},)))
            delete_batch.append(("delete", (item_id,)))

        batch_response = await container.execute_item_batch(
            batch_operations=create_batch, partition_key="Microsoft"
        )
        assert len(batch_response) == 10
        all_items = [item async for item in container.read_all_items()]
        assert len(all_items) == 10

        batch_response = await container.execute_item_batch(
            batch_operations=delete_batch, partition_key="Microsoft"
        )
        assert len(batch_response) == 10
        all_items = [item async for item in container.read_all_items()]
        assert len(all_items) == 0

        # delete non-existent item
        batch = [("delete", ("new-item",)), ("delete", ("new-item",))]

        try:
            await container.execute_item_batch(
                batch_operations=batch, partition_key="Microsoft"
            )
            self.fail("Request should have failed.")
        except exceptions.CosmosBatchOperationError as e:
            assert e.status_code == StatusCodes.NOT_FOUND
            assert e.error_index == 0
            operation_results = e.operation_responses
            assert len(operation_results) == 2
            assert operation_results[0].get("statusCode") == StatusCodes.NOT_FOUND
            assert (
                operation_results[1].get("statusCode") == StatusCodes.FAILED_DEPENDENCY
            )

        await self._delete_container_for_test(cid)
