# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Retain legacy async autoscale-container assertions with isolated Rust-selected fixtures."""

from contextlib import AsyncExitStack
import os
import unittest
import uuid

import pytest

from common.throughput_fixtures import owned_database_async

from azure.cosmos import PartitionKey, ThroughputProperties, exceptions
from azure.cosmos.aio import CosmosClient


@pytest.mark.cosmosEmulator
class TestAutoScaleAsync(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")
        self.addAsyncCleanup(self.client.close)
        cleanup = AsyncExitStack()
        self.addAsyncCleanup(cleanup.aclose)
        self.database = await cleanup.enter_async_context(owned_database_async(
            self.client, "container_autoscale_" + uuid.uuid4().hex,
        ))

    async def test_autoscale_create_container_async_rust(self):
        # Source: tests/test_auto_scale_async.py::TestAutoScaleAsync.test_autoscale_create_container_async
        container = await self.database.create_container(
            id="container_with_auto_scale_settings", partition_key=PartitionKey(path="/id"),
            offer_throughput=ThroughputProperties(auto_scale_max_throughput=5000, auto_scale_increment_percent=0),
        )
        created_container_properties = await container.get_throughput()
        assert created_container_properties.auto_scale_max_throughput == 5000
        assert created_container_properties.auto_scale_increment_percent == 0
        assert created_container_properties.offer_throughput is None
        await self.database.delete_container(container)
        with self.assertRaises(exceptions.CosmosHttpResponseError) as e:
            await self.database.create_container(
                id="container_with_wrong_auto_scale_settings", partition_key=PartitionKey(path="/id"),
                offer_throughput=ThroughputProperties(auto_scale_max_throughput=-200, auto_scale_increment_percent=0),
            )
        assert "Requested throughput -200 is less than required minimum throughput 1000" in str(e.exception)
        container = await self.database.create_container_if_not_exists(
            id="container_with_auto_scale_settings", partition_key=PartitionKey(path="/id"),
            offer_throughput=ThroughputProperties(auto_scale_max_throughput=1000, auto_scale_increment_percent=3),
        )
        created_container_properties = await container.get_throughput()
        assert created_container_properties.auto_scale_max_throughput == 1000
        assert created_container_properties.auto_scale_increment_percent == 3
