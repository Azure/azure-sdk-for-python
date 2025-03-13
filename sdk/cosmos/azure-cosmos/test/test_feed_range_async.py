# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import unittest
import uuid

import pytest
import pytest_asyncio

import azure.cosmos.partition_key as partition_key
import test_config
from azure.cosmos._change_feed.feed_range_internal import FeedRangeInternalEpk
from azure.cosmos._routing.routing_range import Range
from azure.cosmos.aio import CosmosClient


@pytest_asyncio.fixture()
def setup():
    if (TestFeedRangeAsync.masterKey == '[YOUR_KEY_HERE]' or
            TestFeedRangeAsync.host == '[YOUR_ENDPOINT_HERE]'):
        raise Exception(
            "You must specify your Azure Cosmos account values for "
            "'masterKey' and 'host' at the top of this class to run the "
            "tests.")
    test_client = CosmosClient(TestFeedRangeAsync.host, test_config.TestConfig.masterKey),
    created_db = test_client[0].get_database_client(TestFeedRangeAsync.TEST_DATABASE_ID)
    return {
        "created_db": created_db,
        "created_collection": created_db.get_container_client(TestFeedRangeAsync.TEST_CONTAINER_ID)
    }

@pytest.mark.cosmosEmulator
@pytest.mark.asyncio
@pytest.mark.usefixtures("setup")
class TestFeedRangeAsync:
    """Tests to verify methods for operations on feed ranges
    """

    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_ID = test_config.TestConfig.TEST_MULTI_PARTITION_CONTAINER_ID


    async def test_partition_key_to_feed_range(self, setup):
        created_container = await setup["created_db"].create_container(
            id='container_' + str(uuid.uuid4()),
            partition_key=partition_key.PartitionKey(path="/id")
        )
        feed_range = await created_container.feed_range_from_partition_key("1")
        feed_range_epk = FeedRangeInternalEpk.from_json(feed_range)
        assert feed_range_epk.get_normalized_range() == Range("3C80B1B7310BB39F29CC4EA05BDD461E",
                                                                               "3c80b1b7310bb39f29cc4ea05bdd461f", True, False)
        await setup["created_db"].delete_container(created_container)

    async def test_feed_range_is_subset_from_pk(self, setup):
        epk_parent_feed_range = FeedRangeInternalEpk(Range("",
                                                           "FF",
                                                        True,
                                                        False)).to_dict()
        epk_child_feed_range = await setup["created_collection"].feed_range_from_partition_key("1")
        assert await setup["created_collection"].is_feed_range_subset(epk_parent_feed_range, epk_child_feed_range)

if __name__ == '__main__':
    unittest.main()
