# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import random
import unittest

import pytest

import azure.cosmos.cosmos_client as cosmos_client
import test_config
from azure.cosmos import DatabaseProxy
from azure.cosmos._change_feed.feed_range_internal import FeedRangeInternalEpk
from azure.cosmos._routing.routing_range import Range

COLLECTION = "created_collection"
DATABASE = "created_db"
@pytest.fixture(scope="class")
def setup():
    if (TestSessionTokenHelpers.masterKey == '[YOUR_KEY_HERE]' or
            TestSessionTokenHelpers.host == '[YOUR_ENDPOINT_HERE]'):
        raise Exception(
            "You must specify your Azure Cosmos account values for "
            "'masterKey' and 'host' at the top of this class to run the "
            "tests.")
    test_client = cosmos_client.CosmosClient(TestSessionTokenHelpers.host, test_config.TestConfig.masterKey),
    created_db = test_client[0].get_database_client(TestSessionTokenHelpers.TEST_DATABASE_ID)
    return {
        DATABASE: created_db,
        COLLECTION: created_db.get_container_client(TestSessionTokenHelpers.TEST_COLLECTION_ID)
    }

def create_split_ranges():
    return [        # split with two children
                   ([(("AA", "DD"), "0:1#51#3=52"), (("AA", "BB"),"1:1#55#3=52"), (("BB", "DD"),"2:1#54#3=52")],
                    ("AA", "DD"), "1:1#55#3=52,2:1#54#3=52"),
                    # same range different partition key range ids
                   ([(("AA", "DD"), "1:1#51#3=52"), (("AA", "DD"),"0:1#55#3=52")],
                    ("AA", "DD"), "0:1#55#3=52"),
                    # split with one child
                   ([(("AA", "DD"), "0:1#51#3=52"), (("AA", "BB"),"1:1#55#3=52")],
                    ("AA", "DD"), "0:1#51#3=52,1:1#55#3=52"),
                    # Highest GLSN, which is 55 in this         # cspell:disable-line
                    # ex. "1:1#55#3=52", is the one that will be returned because
                    # it is higher than all of the other feed range contained in the same
                    # range
                   ([(("AA", "DD"), "0:1#42#3=52"), (("AA", "BB"), "1:1#51#3=52"),
                    (("BB", "CC"),"1:1#53#3=52"), (("CC", "DD"),"1:1#55#3=52")],
                    ("AA", "DD"), "1:1#55#3=52"),
                    # Highest GLSN, which is 60 in this            # cspell:disable-line
                    # ex. "1:1#60#3=52", is the one that will be returned because
                    # it is higher than all of the other feed range contained in the same
                    # range with some of them overlapping with each other
                   ([(("AA", "DD"), "0:1#60#3=52"), (("AA", "BB"), "1:1#51#3=52"),
                    (("BB", "CC"),"1:1#53#3=52"), (("CC", "DD"),"1:1#55#3=52")],
                    ("AA", "DD"), "0:1#60#3=52"),
                    # AA-DD can be created from the other ranges
                    # but the GLSN's are not all larger than the one  # cspell:disable-line
                    # in the AA-DD range so we just compound as cannot make
                    # conclusions in this case
                   ([(("AA", "DD"), "0:1#60#3=52"), (("AA", "BB"), "1:1#51#3=52"),
                    (("BB", "CC"),"1:1#66#3=52"), (("CC", "DD"),"1:1#55#3=52")],
                    ("AA", "DD"), "0:1#60#3=52,1:1#66#3=52"),
                    # merge with one child
                   ([(("AA", "DD"), "3:1#55#3=52"), (("AA", "BB"),"1:1#51#3=52")],
                    ("AA", "DD"), "3:1#55#3=52"),
                    # merge with two children
                   ([(("AA", "DD"), "3:1#55#3=52"), (("AA", "BB"),"1:1#51#3=52"), (("BB", "DD"),"2:1#54#3=52")],
                    ("AA", "DD"), "3:1#55#3=52"),
                    # compound session token
                   ([(("AA", "DD"), "2:1#54#3=52,1:1#55#3=52"), (("AA", "BB"),"0:1#51#3=52")],
                    ("AA", "BB"), "2:1#54#3=52,1:1#55#3=52,0:1#51#3=52"),
                    # several compound session token with one range
                   ([(("AA", "DD"), "2:1#57#3=52,1:1#57#3=52"), (("AA", "DD"),"2:1#56#3=52,1:1#58#3=52")],
                    ("AA", "DD"), "2:1#57#3=52,1:1#58#3=52"),
                    # overlapping ranges
                   ([(("AA", "CC"), "0:1#54#3=52"), (("BB", "FF"),"2:1#51#3=52")],
                    ("AA", "EE"), "0:1#54#3=52,2:1#51#3=52"),
                    # different version numbers
                   ([(("AA", "BB"), "0:1#54#3=52"), (("AA", "BB"),"0:2#57#3=53")],
                    ("AA", "BB"), "0:2#57#3=53"),
                    # mixed scenarios
                   ([(("AA", "DD"), "3:1#60#3=53"), (("AA", "BB"), "1:1#54#3=52"), (("AA", "BB"), "1:1#52#3=53"),
                     (("BB", "CC"),"1:1#53#3=52"), (("BB", "CC"),"6:1#70#3=55,4:1#90#3=52"),
                     (("CC", "DD"),"1:1#55#3=52")], ("AA", "DD"), "3:1#60#3=53,6:1#70#3=55,4:1#90#3=52")
                  ]

@pytest.mark.cosmosEmulator
@pytest.mark.unittest
@pytest.mark.usefixtures("setup")
class TestSessionTokenHelpers:
    """Test for session token helpers"""

    created_db: DatabaseProxy = None
    client: cosmos_client.CosmosClient = None
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    configs = test_config.TestConfig
    TEST_DATABASE_ID = configs.TEST_DATABASE_ID
    TEST_COLLECTION_ID = configs.TEST_SINGLE_PARTITION_CONTAINER_ID

    def test_get_session_token_update(self, setup):
        feed_range = FeedRangeInternalEpk(
            Range("AA", "BB", True, False)).to_dict()
        session_token = "0:1#54#3=50"
        feed_ranges_and_session_tokens = [(feed_range, session_token)]
        session_token = "0:1#51#3=52"
        feed_ranges_and_session_tokens.append((feed_range, session_token))
        session_token = setup[COLLECTION].get_latest_session_token(feed_ranges_and_session_tokens, feed_range)
        assert session_token == "0:1#54#3=52"

    def test_many_session_tokens_update_same_range(self, setup):
        feed_range = FeedRangeInternalEpk(
            Range("AA", "BB", True, False)).to_dict()
        feed_ranges_and_session_tokens = []
        for i in range(1000):
            session_token = "0:1#" + str(random.randint(1, 100)) + "#3=" + str(random.randint(1, 100))
            feed_ranges_and_session_tokens.append((feed_range, session_token))
        session_token = "0:1#101#3=101"
        feed_ranges_and_session_tokens.append((feed_range, session_token))
        updated_session_token = setup["created_collection"].get_latest_session_token(feed_ranges_and_session_tokens,
                                                                                     feed_range)
        assert updated_session_token == session_token

    def test_many_session_tokens_update(self, setup):
        feed_range = FeedRangeInternalEpk(
            Range("AA", "BB", True, False)).to_dict()
        feed_ranges_and_session_tokens = []
        for i in range(1000):
            session_token = "0:1#" + str(random.randint(1, 100)) + "#3=" + str(random.randint(1, 100))
            feed_ranges_and_session_tokens.append((feed_range, session_token))

        # adding irrelevant feed ranges
        feed_range1 = FeedRangeInternalEpk(
            Range("CC", "FF", True, False)).to_dict()
        feed_range2 = FeedRangeInternalEpk(
            Range("00", "55", True, False)).to_dict()
        for i in range(1000):
            session_token = "0:1#" + str(random.randint(1, 100)) + "#3=" + str(random.randint(1, 100))
            if i % 2 == 0:
                feed_ranges_and_session_tokens.append((feed_range1, session_token))
            else:
                feed_ranges_and_session_tokens.append((feed_range2, session_token))
        session_token = "0:1#101#3=101"
        feed_ranges_and_session_tokens.append((feed_range, session_token))
        updated_session_token = setup["created_collection"].get_latest_session_token(feed_ranges_and_session_tokens,
                                                                                     feed_range)
        assert updated_session_token == session_token

    @pytest.mark.parametrize("split_ranges, target_feed_range, expected_session_token", create_split_ranges())
    def test_simulated_splits_merges(self, setup, split_ranges, target_feed_range, expected_session_token):
        actual_split_ranges = []
        for feed_range, session_token in split_ranges:
            actual_split_ranges.append((FeedRangeInternalEpk(Range(feed_range[0], feed_range[1],
                                                True, False)).to_dict(), session_token))
        target_feed_range = FeedRangeInternalEpk(Range(target_feed_range[0], target_feed_range[1][1],
                                               True, False)).to_dict()
        updated_session_token = setup[COLLECTION].get_latest_session_token(actual_split_ranges, target_feed_range)
        assert updated_session_token == expected_session_token

    def test_invalid_feed_range(self, setup):
        feed_range = FeedRangeInternalEpk(
            Range("AA", "BB", True, False)).to_dict()
        session_token = "0:1#54#3=50"
        feed_ranges_and_session_tokens = [(feed_range, session_token)]
        with pytest.raises(ValueError, match='There were no overlapping feed ranges with the target.'):
            setup["created_collection"].get_latest_session_token(feed_ranges_and_session_tokens,
                                                                 FeedRangeInternalEpk(Range(
                                                                      "CC",
                                                                      "FF",
                                                                      True,
                                                                      False)).to_dict())

if __name__ == '__main__':
    unittest.main()
