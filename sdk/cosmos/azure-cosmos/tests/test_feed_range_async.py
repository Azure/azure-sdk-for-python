# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import unittest
import uuid

import pytest

import test_config
from azure.cosmos._change_feed.feed_range_internal import FeedRangeInternalEpk
from azure.cosmos._routing.routing_range import Range
from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey

@pytest.mark.cosmosEmulator
# @pytest.mark.cosmosAAD  # TEMP: disabled to validate AAD pipeline using only test_aad.py
@pytest.mark.asyncio
class TestFeedRangeAsync(unittest.IsolatedAsyncioTestCase):
    """Tests to verify methods for operations on feed ranges
    """

    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_ID = test_config.TestConfig.TEST_MULTI_PARTITION_CONTAINER_ID

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

    async def asyncSetUp(self):
        # Key-auth client is used for control-plane operations in this test class.
        self.client = CosmosClient(self.host, self.masterKey)
        self.database_for_test = self.client.get_database_client(self.TEST_DATABASE_ID)
        # AAD (or key) client for data-plane operations
        self.data_client = test_config.TestConfig.create_data_client_async()
        self.data_database_for_test = self.data_client.get_database_client(self.TEST_DATABASE_ID)
        self.data_container_for_test = self.data_database_for_test.get_container_client(self.TEST_CONTAINER_ID)

    async def asyncTearDown(self):
        await self.client.close()
        await self.data_client.close()


    async def test_partition_key_to_feed_range_async(self):
        # Control-plane container creation.
        created_container_ref = await self.database_for_test.create_container(
            id='container_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/id")
        )
        # Data-plane proxy for feed_range operations
        created_container = self.data_database_for_test.get_container_client(created_container_ref.id)
        feed_range = await created_container.feed_range_from_partition_key("1")
        feed_range_epk = FeedRangeInternalEpk.from_json(feed_range)
        assert feed_range_epk.get_normalized_range() == Range("3C80B1B7310BB39F29CC4EA05BDD461E",
                                                                               "3c80b1b7310bb39f29cc4ea05bdd461f", True, False)
        await self.database_for_test.delete_container(created_container_ref)

    async def test_feed_range_is_subset_from_pk_async(self):
        epk_parent_feed_range = FeedRangeInternalEpk(Range("",
                                                           "FF",
                                                        True,
                                                        False)).to_dict()
        epk_child_feed_range = await self.data_container_for_test.feed_range_from_partition_key("1")
        assert await self.data_container_for_test.is_feed_range_subset(epk_parent_feed_range, epk_child_feed_range)

if __name__ == '__main__':
    unittest.main()
