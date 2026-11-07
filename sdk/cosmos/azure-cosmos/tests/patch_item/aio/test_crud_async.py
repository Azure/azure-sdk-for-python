# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Original async CRUD tests that patch items, re-run on the Rust path.

Source: ``tests/test_crud_async.py::TestCRUDOperationsAsync``. Each method
keeps the original steps and assertions; only setup changed. The client uses
``_backend="rust"`` and each test owns a uniquely named database with the
``/pk`` multi-partition container the original setup provided, deleted
afterwards.
"""

import pytest
import os
from types import SimpleNamespace
import unittest
import uuid

import azure.cosmos.exceptions as exceptions
from azure.cosmos.aio import CosmosClient
from azure.cosmos.http_constants import StatusCodes
from azure.cosmos.partition_key import PartitionKey


@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosLong
@pytest.mark.cosmosAADCircuitBreaker
class TestCRUDOperationsAsync(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")
        await self.client.__aenter__()
        self._db_id = "patch_item_crud_async_" + uuid.uuid4().hex
        self.database_for_test = None
        try:
            self.database_for_test = await self.client.create_database(self._db_id)
            self.configs = SimpleNamespace(
                TEST_MULTI_PARTITION_CONTAINER_ID="multi_partition_" + uuid.uuid4().hex[:8])
            await self.database_for_test.create_container(
                id=self.configs.TEST_MULTI_PARTITION_CONTAINER_ID, partition_key=PartitionKey(path="/pk"))
        except BaseException:
            await self.asyncTearDown()
            raise

    async def asyncTearDown(self):
        try:
            if self.database_for_test is not None:
                await self.client.delete_database(self._db_id)
        finally:
            await self.client.close()

    async def test_patch_operations_async_rust(self):
        # Source: tests/test_crud_async.py::TestCRUDOperationsAsync.test_patch_operations_async

        created_container = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

        # Create item to patch
        item_id = "patch_item_" + str(uuid.uuid4())
        item = {
            "id": item_id,
            "pk": "patch_item_pk",
            "prop": "prop1",
            "address": {
                "city": "Redmond"
            },
            "company": "Microsoft",
            "number": 3}
        await created_container.create_item(item)
        # Define and run patch operations
        operations = [
            {"op": "add", "path": "/color", "value": "yellow"},
            {"op": "remove", "path": "/prop"},
            {"op": "replace", "path": "/company", "value": "CosmosDB"},
            {"op": "set", "path": "/address/new_city", "value": "Atlanta"},
            {"op": "incr", "path": "/number", "value": 7},
            {"op": "move", "from": "/color", "path": "/favorite_color"}
        ]
        patched_item = await created_container.patch_item(item=item_id, partition_key="patch_item_pk",
                                                          patch_operations=operations)
        # Verify results from patch operations
        assert "color" not in patched_item
        assert "prop" not in patched_item
        assert patched_item.get("company") == "CosmosDB"
        assert patched_item.get("address").get("new_city") == "Atlanta"
        assert patched_item.get("number") == 10
        assert patched_item.get("favorite_color") == "yellow"

        stored_item = await created_container.read_item(item_id, partition_key="patch_item_pk")
        assert "color" not in stored_item
        assert "prop" not in stored_item
        assert stored_item.get("favorite_color") == "yellow"

        # Negative test - attempt to replace non-existent field
        operations = [{"op": "replace", "path": "/wrong_field", "value": "wrong_value"}]
        with self.assertRaises(exceptions.CosmosHttpResponseError) as caught:
            await created_container.patch_item(item=item_id, partition_key="patch_item_pk",
                                               patch_operations=operations)
        assert caught.exception.status_code == StatusCodes.BAD_REQUEST

        # Negative test - attempt to remove non-existent field
        operations = [{"op": "remove", "path": "/wrong_field"}]
        with self.assertRaises(exceptions.CosmosHttpResponseError) as caught:
            await created_container.patch_item(item=item_id, partition_key="patch_item_pk",
                                               patch_operations=operations)
        assert caught.exception.status_code == StatusCodes.BAD_REQUEST

        # Negative test - attempt to increment non-number field
        operations = [{"op": "incr", "path": "/company", "value": 3}]
        with self.assertRaises(exceptions.CosmosHttpResponseError) as caught:
            await created_container.patch_item(item=item_id, partition_key="patch_item_pk",
                                               patch_operations=operations)
        assert caught.exception.status_code == StatusCodes.BAD_REQUEST

        # Negative test - attempt to move from non-existent field
        operations = [{"op": "move", "from": "/wrong_field", "path": "/other_field"}]
        with self.assertRaises(exceptions.CosmosHttpResponseError) as caught:
            await created_container.patch_item(item=item_id, partition_key="patch_item_pk",
                                               patch_operations=operations)
        assert caught.exception.status_code == StatusCodes.BAD_REQUEST

    async def test_conditional_patching_async_rust(self):
        # Source: tests/test_crud_async.py::TestCRUDOperationsAsync.test_conditional_patching_async

        created_container = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)
        # Create item to patch
        item_id = "conditional_patch_item_" + str(uuid.uuid4())
        item = {
            "id": item_id,
            "pk": "patch_item_pk",
            "prop": "prop1",
            "address": {
                "city": "Redmond"
            },
            "company": "Microsoft",
            "number": 3}
        await created_container.create_item(item)

        # Define patch operations
        operations = [
            {"op": "add", "path": "/color", "value": "yellow"},
            {"op": "remove", "path": "/prop"},
            {"op": "replace", "path": "/company", "value": "CosmosDB"},
            {"op": "set", "path": "/address/new_city", "value": "Atlanta"},
            {"op": "incr", "path": "/number", "value": 7},
            {"op": "move", "from": "/color", "path": "/favorite_color"}
        ]

        # Run patch operations with wrong filter
        num_false = item.get("number") + 1
        filter_predicate = "from root where root.number = " + str(num_false)
        with self.assertRaises(exceptions.CosmosHttpResponseError) as caught:
            await created_container.patch_item(item=item_id, partition_key="patch_item_pk",
                                               patch_operations=operations, filter_predicate=filter_predicate)
        assert caught.exception.status_code == StatusCodes.PRECONDITION_FAILED
        unchanged = await created_container.read_item(item_id, partition_key="patch_item_pk")
        assert {key: unchanged[key] for key in item} == item
        assert "color" not in unchanged
        assert "favorite_color" not in unchanged

        # Run patch operations with correct filter
        filter_predicate = "from root where root.number = " + str(item.get("number"))
        patched_item = await created_container.patch_item(item=item_id, partition_key="patch_item_pk",
                                                          patch_operations=operations,
                                                          filter_predicate=filter_predicate)
        # Verify results from patch operations
        assert patched_item.get("color") is None
        assert patched_item.get("prop") is None
        assert patched_item.get("company") == "CosmosDB"
        assert patched_item.get("address").get("new_city") == "Atlanta"
        assert patched_item.get("number") == 10
        assert patched_item.get("favorite_color") == "yellow"

        expected = {
            "id": item["id"], "pk": item["pk"], "company": "CosmosDB",
            "address": {"city": "Redmond", "new_city": "Atlanta"},
            "number": 10, "favorite_color": "yellow",
        }
        assert {key: patched_item[key] for key in expected} == expected
        stored = await created_container.read_item(item_id, partition_key="patch_item_pk")
        assert {key: stored[key] for key in expected} == expected
        for result in (patched_item, stored):
            assert "color" not in result
            assert "prop" not in result


if __name__ == '__main__':
    unittest.main()
