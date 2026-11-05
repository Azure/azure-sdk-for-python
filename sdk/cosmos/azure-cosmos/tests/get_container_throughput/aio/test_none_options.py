# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Keep the original async explicit-None throughput contract on Rust."""

from contextlib import AsyncExitStack
import os
import unittest
import uuid

import pytest

from common.throughput_fixtures import owned_database_async

from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient


@pytest.mark.cosmosEmulator
class TestNoneOptionsAsync(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.key_client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")
        self.addAsyncCleanup(self.key_client.close)
        cleanup = AsyncExitStack()
        self.addAsyncCleanup(cleanup.aclose)
        database = await cleanup.enter_async_context(owned_database_async(
            self.key_client, "throughput_none_" + uuid.uuid4().hex,
        ))
        self.key_container = await database.create_container(
            id="orders", partition_key=PartitionKey(path="/pk"), offer_throughput=400,
        )

    async def test_get_throughput_none_options_async_rust(self):
        # Source: tests/test_none_options_async.py::TestNoneOptionsAsync.test_get_throughput_none_options_async
        tp = await self.key_container.get_throughput(response_hook=None)
        assert tp.offer_throughput > 0
