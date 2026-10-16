# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Retain legacy async autoscale-container assertions with isolated Rust-selected fixtures."""

import os
import unittest
import uuid

from azure.cosmos import PartitionKey, ThroughputProperties, exceptions
from azure.cosmos.aio import CosmosClient


class TestAutoScaleAsync(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")
        self.database = await self.client.create_database("container_autoscale_" + uuid.uuid4().hex)

    async def asyncTearDown(self):
        try:
            await self.client.delete_database(self.database.id)
        finally:
            await self.client.close()

    async def test_autoscale_create_container_async(self):
        # Source: tests/test_auto_scale_async.py::TestAutoScaleAsync.test_autoscale_create_container_async
        container = await self.database.create_container(
            id="container_with_auto_scale_settings", partition_key=PartitionKey(path="/id"),
            offer_throughput=ThroughputProperties(auto_scale_max_throughput=5000, auto_scale_increment_percent=0),
        )
        result = await container.get_throughput()
        assert result.auto_scale_max_throughput == 5000
        assert result.auto_scale_increment_percent == 0
        assert result.offer_throughput is None
        await self.database.delete_container(container)
        with self.assertRaises(exceptions.CosmosHttpResponseError) as caught:
            await self.database.create_container(
                id="container_with_wrong_auto_scale_settings", partition_key=PartitionKey(path="/id"),
                offer_throughput=ThroughputProperties(auto_scale_max_throughput=-200, auto_scale_increment_percent=0),
            )
        assert "Requested throughput -200 is less than required minimum throughput 1000" in str(caught.exception)
        container = await self.database.create_container_if_not_exists(
            id="container_with_auto_scale_settings", partition_key=PartitionKey(path="/id"),
            offer_throughput=ThroughputProperties(auto_scale_max_throughput=1000, auto_scale_increment_percent=3),
        )
        result = await container.get_throughput()
        assert result.auto_scale_max_throughput == 1000
        assert result.auto_scale_increment_percent == 3
