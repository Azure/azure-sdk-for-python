# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Original non-split async token assertions with owned, closed resources.

Test methods and retained 100-write helpers were copied from
tests/test_partition_split_scenarios_async.py. The forced 11000-RU split test
is in a separate opt-in file, outside this ordinary-account run.
"""

import os
import random
import unittest
import uuid

import pytest

from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient
from get_latest_session_token._fixtures import create_items_logical_pk_async, create_items_physical_pk_async


@pytest.mark.cosmosEmulator
class TestLatestSessionTokenAsync(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        state = random.getstate()
        self.addCleanup(random.setstate, state)
        random.seed(0)
        self.client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")
        self.addAsyncCleanup(self.client.close)
        await self.client.__aenter__()
        self.database = await self.client.create_database("token_parity_" + uuid.uuid4().hex)
        self.addAsyncCleanup(self.client.delete_database, self.database.id)
        self.key_database = self.database
        print(f"\nOwned token-test database: {self.database.id}")

    create_items_logical_pk_async = staticmethod(create_items_logical_pk_async)
    create_items_physical_pk_async = staticmethod(create_items_physical_pk_async)

    async def test_latest_session_token_hpk_rust(self):
        # Source: tests/test_partition_split_scenarios_async.py::TestPartitionSplitScenariosAsync.test_latest_session_token_hpk
        container_ref = await self.key_database.create_container(
            "test_updated_session_token_hpk" + str(uuid.uuid4()),
            PartitionKey(path=["/state", "/city", "/zipcode"], kind="MultiHash"),
            offer_throughput=400)
        container = self.database.get_container_client(container_ref.id)
        feed_ranges_and_session_tokens = []
        previous_session_token = ""
        pk = ['CA', 'LA1', '90001']
        pk_feed_range = await container.feed_range_from_partition_key(pk)
        target_session_token, target_feed_range, previous_session_token = await self.create_items_physical_pk_async(container,
                                                                                                                     pk_feed_range,
                                                                                                                     previous_session_token,
                                                                                                                     feed_ranges_and_session_tokens,
                                                                                                                     True)
        session_token = await container.get_latest_session_token(feed_ranges_and_session_tokens, target_feed_range)
        assert session_token == target_session_token
        await self.key_database.delete_container(container.id)

    async def test_latest_session_token_logical_hpk_rust(self):
        # Source: tests/test_partition_split_scenarios_async.py::TestPartitionSplitScenariosAsync.test_latest_session_token_logical_hpk
        container_ref = await self.key_database.create_container(
            "test_updated_session_token_from_logical_hpk" + str(uuid.uuid4()),
            PartitionKey(path=["/state", "/city", "/zipcode"], kind="MultiHash"),
            offer_throughput=400)
        container = self.database.get_container_client(container_ref.id)
        feed_ranges_and_session_tokens = []
        previous_session_token = ""
        target_pk = ['CA', 'LA1', '90001']
        target_feed_range = await container.feed_range_from_partition_key(target_pk)
        target_session_token, previous_session_token = await self.create_items_logical_pk_async(container, target_feed_range,
                                                                                                previous_session_token,
                                                                                                feed_ranges_and_session_tokens,
                                                                                                True)
        session_token = await container.get_latest_session_token(feed_ranges_and_session_tokens, target_feed_range)
        assert session_token == target_session_token
        await self.key_database.delete_container(container.id)
