# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Original async stale-container throughput assertions with owned resources."""

from copy import deepcopy
import os
import unittest
import uuid

from azure.cosmos import PartitionKey, exceptions
from azure.cosmos.aio import CosmosClient


class TestContainerPropertiesCacheAsync(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")
        self.addAsyncCleanup(self.client.close)
        self.database = await self.client.create_database("throughput_recreate_" + uuid.uuid4().hex)
        self.addAsyncCleanup(self.client.delete_database, self.database.id)

    async def _check_recreation(self, old_paths, new_paths):
        container_name = "orders"
        try:
            await self.database.create_container(
                container_name, partition_key=PartitionKey(path=old_paths), offer_throughput=600,
            )
        except exceptions.CosmosResourceExistsError:
            assert False, "Container Should not Already Exist."
        cache = self.client.client_connection._container_properties_cache
        old_cache = deepcopy(cache)
        await self.database.delete_container(container_name)
        try:
            created_container = await self.database.create_container(
                container_name, partition_key=PartitionKey(path=new_paths), offer_throughput=800,
            )
        except exceptions.CosmosResourceExistsError:
            assert False, "Container Should not Already Exist."
        cache.clear()
        cache.update(deepcopy(old_cache))
        try:
            offer = await created_container.get_throughput()
            assert offer.offer_throughput == 800
        except exceptions.CosmosHttpResponseError as e:
            assert False, "{}".format(e.http_error_message)
        cache.clear()
        cache.update(deepcopy(old_cache))
        new_throughput = 900
        try:
            new_offer = await created_container.replace_throughput(new_throughput)
            assert new_offer.offer_throughput == new_throughput
        except exceptions.CosmosHttpResponseError as e:
            assert False, "{}".format(e.http_error_message)
        self.assertEqual((await created_container.get_throughput()).offer_throughput, new_throughput)

    async def test_offer_throughput_container_recreate_async(self):
        # Source: tests/test_container_properties_cache_async.py::TestContainerPropertiesCache.test_offer_throughput_container_recreate_async
        await self._check_recreation("/PK", "/partkey")

    async def test_offer_throughput_container_recreate_sub_partition_async(self):
        # Source: tests/test_container_properties_cache_async.py::TestContainerPropertiesCache.test_offer_throughput_container_recreate_sub_partition_async
        await self._check_recreation(["/country", "/state"], ["/county", "/city"])
