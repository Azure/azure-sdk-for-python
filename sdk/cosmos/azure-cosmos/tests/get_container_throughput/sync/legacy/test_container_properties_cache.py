# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Original stale-container throughput assertions with test-owned resources."""

from copy import deepcopy
import os
import unittest
import uuid

from azure.cosmos import CosmosClient, PartitionKey


class TestContainerPropertiesCache(unittest.TestCase):
    def setUp(self):
        self.client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")
        self.addCleanup(self.client.close)
        self.database = self.client.create_database("throughput_recreate_" + uuid.uuid4().hex)
        self.addCleanup(self.client.delete_database, self.database.id)

    def _check_recreation(self, old_paths, new_paths):
        container_name = "orders"
        self.database.create_container(container_name, partition_key=PartitionKey(path=old_paths), offer_throughput=600)
        cache = self.client.client_connection._container_properties_cache
        old_cache = deepcopy(cache)
        self.database.delete_container(container_name)
        created_container = self.database.create_container(
            container_name, partition_key=PartitionKey(path=new_paths), offer_throughput=800,
        )
        cache.clear()
        cache.update(deepcopy(old_cache))
        offer = created_container.get_throughput()
        self.assertEqual(offer.offer_throughput, 800)
        cache.clear()
        cache.update(deepcopy(old_cache))
        new_throughput = 900
        new_offer = created_container.replace_throughput(new_throughput)
        self.assertEqual(new_offer.offer_throughput, new_throughput)
        self.assertEqual(created_container.get_throughput().offer_throughput, new_throughput)

    def test_offer_throughput_container_recreate_rust(self):
        # Source: tests/test_container_properties_cache.py::TestContainerPropertiesCache.test_offer_throughput_container_recreate
        self._check_recreation("/PK", "/partkey")

    def test_offer_throughput_container_recreate_sub_partition_rust(self):
        # Source: tests/test_container_properties_cache.py::TestContainerPropertiesCache.test_offer_throughput_container_recreate_sub_partition
        self._check_recreation(["/country", "/state"], ["/county", "/city"])
