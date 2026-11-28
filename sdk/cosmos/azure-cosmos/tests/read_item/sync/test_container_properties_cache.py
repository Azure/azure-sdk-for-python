# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Main's recreation assertions with warmed readers, not a restored Python cache.

Two readers load the original container before it is recreated. Setup supplies
the replacement partition keys explicitly to isolate reads from write gap 22.
"""
from contextlib import ExitStack
import unittest
import uuid

import pytest

from azure.cosmos import PartitionKey, exceptions
from common.throughput_fixtures import owned_database
from config import clients


@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
class TestContainerPropertiesCache(unittest.TestCase):
    def setUp(self):
        stack = ExitStack()
        self.addCleanup(stack.close)
        setup = stack.enter_context(clients.create_setup_client(_backend="rust"))
        self.database = stack.enter_context(owned_database(setup, "read-recreate-" + uuid.uuid4().hex))
        self.readers = [stack.enter_context(clients.create_data_client(_backend="rust")) for _ in range(2)]

    def _recreate(self, old_paths, new_paths, old_items, new_items, old_key):
        name = "orders"
        self.database.create_container(name, partition_key=PartitionKey(path=old_paths))
        with clients.create_data_client(_backend="rust") as writer:
            container = writer.get_database_client(self.database.id).get_container_client(name)
            saved = [container.create_item(body=item) for item in old_items]
        readers = [client.get_database_client(self.database.id).get_container_client(name) for client in self.readers]
        for reader in readers:
            reader.read_item(saved[0]["id"], partition_key=old_key)
        self.database.delete_container(name)
        self.database.create_container(name, partition_key=PartitionKey(path=new_paths))
        # Explicit setup keys avoid stale-key extraction (gap 22) without resetting the readers.
        with clients.create_data_client(_backend="rust") as writer:
            container = writer.get_database_client(self.database.id).get_container_client(name)
            for item in new_items:
                key = [item[path[1:]] for path in new_paths] if isinstance(new_paths, list) else item[new_paths[1:]]
                container.create_item(body=item, request_options={"partitionKey": key})
        return saved, readers

    def test_container_recreate_read_item_rust(self):
        # Source: tests/test_container_properties_cache.py::TestContainerPropertiesCache.test_container_recreate_read_item
        saved, readers = self._recreate(
            "/PK", "/partkey",
            [{"id": "item1", "PK": "val"}, {"id": "item2", "PK": "OtherValue"}],
            [{"id": "item1", "partkey": "val"}, {"id": "item2", "partkey": "DifferentValue"}],
            "val",
        )
        item_to_read, item_to_read2 = saved
        created_container = readers[0]
        with self.assertRaises(exceptions.CosmosHttpResponseError) as caught:
            created_container.read_item(item=item_to_read, partition_key="val")
        self.assertEqual(caught.exception.status_code, 404)
        read_item = created_container.read_item(item="item1", partition_key="val")
        self.assertNotEqual(read_item, item_to_read)
        with self.assertRaises(exceptions.CosmosHttpResponseError) as caught:
            readers[1].read_item(item=item_to_read2, partition_key="OtherValue")
        self.assertEqual(caught.exception.status_code, 404)

    def test_container_recreate_read_item_sub_partition_rust(self):
        # Source: tests/test_container_properties_cache.py::TestContainerPropertiesCache.test_container_recreate_read_item_sub_partition
        saved, readers = self._recreate(
            ["/country", "/state"], ["/county", "/city"],
            [{"id": "item1", "country": "USA", "state": "CA"},
             {"id": "item2", "country": "MEX", "state": "Michoac\u00e1n"}],
            [{"id": "item1", "county": "ventura", "city": "oxnard"}],
            ["USA", "CA"],
        )
        with self.assertRaises(exceptions.CosmosHttpResponseError) as caught:
            readers[0].read_item(item=saved[0], partition_key=["USA", "CA"])
        self.assertEqual(caught.exception.status_code, 404)
