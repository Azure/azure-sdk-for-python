# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import unittest
import uuid

import pytest

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.partition_key as partition_key
import test_config

from azure.cosmos._change_feed.feed_range_internal import FeedRangeInternalEpk
from azure.cosmos._routing.routing_range import Range

@pytest.fixture(scope="class")
def setup():
    if (TestFeedRange.masterKey == '[YOUR_KEY_HERE]' or
            TestFeedRange.host == '[YOUR_ENDPOINT_HERE]'):
        raise Exception(
            "You must specify your Azure Cosmos account values for "
            "'masterKey' and 'host' at the top of this class to run the "
            "tests.")
    test_client = cosmos_client.CosmosClient(TestFeedRange.host, test_config.TestConfig.masterKey),
    created_db = test_client[0].get_database_client(TestFeedRange.TEST_DATABASE_ID)
    return {
        "created_db": created_db,
        "created_collection": created_db.get_container_client(TestFeedRange.TEST_CONTAINER_ID)
    }

test_subset_ranges = [(Range("", "FF", True, False),
                       Range("3F", "7F", True, False),
                       True),
                      (Range("3F", "7F", True, False),
                       Range("", "FF", True, False),
                       False),
                      (Range("3F", "7F", True, False),
                       Range("", "5F", True, False),
                       False),
                      (Range("3F", "7F", True, True),
                       Range("3F", "7F", True, True),
                       True),
                      (Range("3F", "7F", False, True),
                       Range("3F", "7F", True, True),
                       False),
                      (Range("3F", "7F", True, False),
                       Range("3F", "7F", True, True),
                       False),
                      (Range("3F", "7F", True, False),
                       Range("", "2F", True, False),
                       False),
                      (Range("3F", "3F", True, True),
                       Range("3F", "3F", True, True),
                       True),
                      (Range("3F", "3F", True, True),
                       Range("4F", "4F", True, True),
                       False)
                      ]


test_overlaps_ranges = [(Range("", "FF", True, False),
                       Range("3F", "7F", True, False),
                       True),
                      (Range("3F", "7F", True, False),
                       Range("", "FF", True, False),
                       True),
                      (Range("3F", "7F", True, False),
                       Range("", "5F", True, False),
                       True),
                      (Range("3F", "7F", True, False),
                       Range("3F", "7F", True, False),
                       True),
                      (Range("3F", "7F", True, False),
                       Range("", "2F", True, False),
                       False),
                      (Range("3F", "7F", True, False),
                       Range("6F", "FF", True, False),
                       True),
                      (Range("AA", "BB", True, False),
                       Range("CC", "FF", True, False),
                       False)]

@pytest.mark.cosmosEmulator
@pytest.mark.unittest
@pytest.mark.usefixtures("setup")
class TestFeedRange:
    """Tests to verify methods for operations on feed ranges
    """

    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_ID = test_config.TestConfig.TEST_MULTI_PARTITION_CONTAINER_ID


    def test_partition_key_to_feed_range(self, setup):
        created_container = setup["created_db"].create_container(
            id='container_' + str(uuid.uuid4()),
            partition_key=partition_key.PartitionKey(path="/id")
        )
        feed_range = created_container.feed_range_from_partition_key("1")
        feed_range_epk = FeedRangeInternalEpk.from_json(feed_range)
        assert feed_range_epk.get_normalized_range() == Range("3C80B1B7310BB39F29CC4EA05BDD461E",
                        "3c80b1b7310bb39f29cc4ea05bdd461f", True, False)
        setup["created_db"].delete_container(created_container)

    @pytest.mark.parametrize("parent_feed_range, child_feed_range, is_subset", test_subset_ranges)
    def test_feed_range_is_subset(self, setup, parent_feed_range, child_feed_range, is_subset):
        epk_parent_feed_range = FeedRangeInternalEpk(parent_feed_range).to_dict()
        epk_child_feed_range = FeedRangeInternalEpk(child_feed_range).to_dict()
        assert setup["created_collection"].is_feed_range_subset(epk_parent_feed_range, epk_child_feed_range) == is_subset

    def test_feed_range_is_subset_from_pk(self, setup):
        epk_parent_feed_range = FeedRangeInternalEpk(
            Range("", "FF", True, False)).to_dict()
        epk_child_feed_range = setup["created_collection"].feed_range_from_partition_key("1")
        assert setup["created_collection"].is_feed_range_subset(epk_parent_feed_range, epk_child_feed_range)

    @pytest.mark.parametrize("range1, range2, overlaps", test_overlaps_ranges)
    def test_overlaps(self, setup, range1, range2, overlaps):
        assert Range.overlaps(range1, range2) == overlaps

if __name__ == '__main__':
    unittest.main()
