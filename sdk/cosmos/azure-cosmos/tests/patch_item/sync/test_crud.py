# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Original sync CRUD tests that patch items, re-run on the Rust path.

Source: ``tests/test_crud.py::TestCRUDOperations``. Each method keeps the
original steps and assertions; only setup changed. The client uses
``_backend="rust"`` and each test owns a uniquely named database with the
``/pk`` multi-partition container the original class setup provided, deleted
afterwards.
"""

import pytest
import os
from types import SimpleNamespace
import unittest
import uuid

import azure.cosmos.exceptions as exceptions
from azure.cosmos import CosmosClient
from azure.cosmos.http_constants import StatusCodes
from azure.cosmos.partition_key import PartitionKey


@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosLong
@pytest.mark.cosmosAADCircuitBreaker
class TestCRUDOperations(unittest.TestCase):

    def setUp(self):
        self.client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")
        self.addCleanup(self.client.close)
        self._db_id = "patch_item_crud_" + uuid.uuid4().hex
        self.databaseForTest = self.client.create_database(self._db_id)
        self.addCleanup(self.client.delete_database, self._db_id)
        self.configs = SimpleNamespace(TEST_MULTI_PARTITION_CONTAINER_ID="multi_partition_" + uuid.uuid4().hex[:8])
        self.databaseForTest.create_container(
            id=self.configs.TEST_MULTI_PARTITION_CONTAINER_ID, partition_key=PartitionKey(path="/pk"))

    def test_patch_operations_rust(self):
        # Source: tests/test_crud.py::TestCRUDOperations.test_patch_operations
        created_container = self.databaseForTest.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

        pkValue = "patch_item_pk" + str(uuid.uuid4())
        # Create item to patch
        item = {
            "id": "patch_item",
            "pk": pkValue,
            "prop": "prop1",
            "address": {
                "city": "Redmond"
            },
            "company": "Microsoft",
            "number": 3}
        created_container.create_item(item)
        # Define and run patch operations
        operations = [
            {"op": "add", "path": "/color", "value": "yellow"},
            {"op": "remove", "path": "/prop"},
            {"op": "replace", "path": "/company", "value": "CosmosDB"},
            {"op": "set", "path": "/address/new_city", "value": "Atlanta"},
            {"op": "incr", "path": "/number", "value": 7},
            {"op": "move", "from": "/color", "path": "/favorite_color"}
        ]
        patched_item = created_container.patch_item(item="patch_item", partition_key=pkValue,
                                                    patch_operations=operations)
        # Verify results from patch operations
        self.assertNotIn("color", patched_item)
        self.assertNotIn("prop", patched_item)
        self.assertEqual(patched_item.get("company"), "CosmosDB")
        self.assertEqual(patched_item.get("address").get("new_city"), "Atlanta")
        self.assertEqual(patched_item.get("number"), 10)
        self.assertEqual(patched_item.get("favorite_color"), "yellow")

        stored_item = created_container.read_item("patch_item", partition_key=pkValue)
        self.assertNotIn("color", stored_item)
        self.assertNotIn("prop", stored_item)
        self.assertEqual(stored_item.get("favorite_color"), "yellow")

        # Negative test - attempt to replace non-existent field
        operations = [{"op": "replace", "path": "/wrong_field", "value": "wrong_value"}]
        with self.assertRaises(exceptions.CosmosHttpResponseError) as caught:
            created_container.patch_item(item="patch_item", partition_key=pkValue, patch_operations=operations)
        self.assertEqual(caught.exception.status_code, StatusCodes.BAD_REQUEST)

        # Negative test - attempt to remove non-existent field
        operations = [{"op": "remove", "path": "/wrong_field"}]
        with self.assertRaises(exceptions.CosmosHttpResponseError) as caught:
            created_container.patch_item(item="patch_item", partition_key=pkValue, patch_operations=operations)
        self.assertEqual(caught.exception.status_code, StatusCodes.BAD_REQUEST)

        # Negative test - attempt to increment non-number field
        operations = [{"op": "incr", "path": "/company", "value": 3}]
        with self.assertRaises(exceptions.CosmosHttpResponseError) as caught:
            created_container.patch_item(item="patch_item", partition_key=pkValue, patch_operations=operations)
        self.assertEqual(caught.exception.status_code, StatusCodes.BAD_REQUEST)

        # Negative test - attempt to move from non-existent field
        operations = [{"op": "move", "from": "/wrong_field", "path": "/other_field"}]
        with self.assertRaises(exceptions.CosmosHttpResponseError) as caught:
            created_container.patch_item(item="patch_item", partition_key=pkValue, patch_operations=operations)
        self.assertEqual(caught.exception.status_code, StatusCodes.BAD_REQUEST)

    def test_conditional_patching_rust(self):
        # Source: tests/test_crud.py::TestCRUDOperations.test_conditional_patching
        created_container = self.databaseForTest.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)
        # Create item to patch
        pkValue = "patch_item_pk" + str(uuid.uuid4())
        item = {
            "id": "conditional_patch_item",
            "pk": pkValue,
            "prop": "prop1",
            "address": {
                "city": "Redmond"
            },
            "company": "Microsoft",
            "number": 3}
        created_container.create_item(item)

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
            created_container.patch_item(item="conditional_patch_item", partition_key=pkValue,
                                         patch_operations=operations, filter_predicate=filter_predicate)
        self.assertEqual(caught.exception.status_code, StatusCodes.PRECONDITION_FAILED)
        unchanged = created_container.read_item(item["id"], partition_key=pkValue)
        self.assertEqual({key: unchanged[key] for key in item}, item)
        self.assertNotIn("color", unchanged)
        self.assertNotIn("favorite_color", unchanged)

        # Run patch operations with correct filter
        filter_predicate = "from root where root.number = " + str(item.get("number"))
        patched_item = created_container.patch_item(item="conditional_patch_item", partition_key=pkValue,
                                                    patch_operations=operations, filter_predicate=filter_predicate)
        # Verify results from patch operations
        self.assertTrue(patched_item.get("color") is None)
        self.assertTrue(patched_item.get("prop") is None)
        self.assertEqual(patched_item.get("company"), "CosmosDB")
        self.assertEqual(patched_item.get("address").get("new_city"), "Atlanta")
        self.assertEqual(patched_item.get("number"), 10)
        self.assertEqual(patched_item.get("favorite_color"), "yellow")

        expected = {
            "id": item["id"], "pk": item["pk"], "company": "CosmosDB",
            "address": {"city": "Redmond", "new_city": "Atlanta"},
            "number": 10, "favorite_color": "yellow",
        }
        self.assertEqual({key: patched_item[key] for key in expected}, expected)
        stored = created_container.read_item(item["id"], partition_key=pkValue)
        self.assertEqual({key: stored[key] for key in expected}, expected)
        for result in (patched_item, stored):
            self.assertNotIn("color", result)
            self.assertNotIn("prop", result)


if __name__ == '__main__':
    unittest.main()
