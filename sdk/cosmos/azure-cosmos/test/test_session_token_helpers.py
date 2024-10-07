# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import random
import unittest

import pytest

import azure.cosmos.cosmos_client as cosmos_client
import test_config
from azure.cosmos import DatabaseProxy
from azure.cosmos._feed_range import FeedRangeEpk
from azure.cosmos._routing.routing_range import Range

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
        "created_db": created_db,
        "created_collection": created_db.get_container_client(TestSessionTokenHelpers.TEST_COLLECTION_ID)
    }

def create_split_ranges():
    # add one with several ranges being equal to one
    test_params = [ # split with two children
                   ([(("AA", "DD"), "0:1#51#3=52"), (("AA", "BB"),"1:1#55#3=52"), (("BB", "DD"),"2:1#54#3=52")],
                    ("AA", "DD"), "1:1#55#3=52,2:1#54#3=52"),
                    # several ranges being equal to one range
                   ([(("AA", "DD"), "0:1#51#3=52"), (("AA", "BB"),"1:1#55#3=52")],
                    ("AA", "DD"), "0:1#51#3=52,1:1#55#3=52"),
                    # split with one child
                   ([(("AA", "DD"), "0:1#42#3=52"), (("AA", "BB"), "1:1#51#3=52"),
                    (("BB", "CC"),"1:1#53#3=52"), (("CC", "DD"),"1:1#55#3=52")],
                    ("AA", "DD"), "1:1#55#3=52"),
                    # merge with one child
                   ([(("AA", "DD"), "0:1#55#3=52"), (("AA", "BB"),"1:1#51#3=52")],
                    ("AA", "DD"), "0:1#55#3=52"),
                    # merge with two children
                   ([(("AA", "DD"), "0:1#55#3=52"), (("AA", "BB"),"1:1#51#3=52"), (("BB", "DD"),"2:1#54#3=52")],
                    ("AA", "DD"), "0:1#55#3=52"),
                    # compound session token
                   ([(("AA", "DD"), "2:1#54#3=52,1:1#55#3=52"), (("AA", "BB"),"0:1#51#3=52")],
                    ("AA", "BB"), "2:1#54#3=52,1:1#55#3=52,0:1#51#3=52"),
                    # several compound session token with one range
                   ([(("AA", "DD"), "2:1#57#3=52,1:1#57#3=52"), (("AA", "DD"),"2:1#56#3=52,1:1#58#3=52")],
                    ("AA", "DD"), "2:1#57#3=52,1:1#58#3=52"),
                    # Overlapping ranges
                   ([(("AA", "CC"), "0:1#54#3=52"), (("BB", "FF"),"2:1#51#3=52")],
                    ("AA", "EE"), "0:1#54#3=52,2:1#51#3=52")]
    actual_test_params = []
    for test_param in test_params:
        split_ranges = []
        for feed_range, session_token in test_param[0]:
            split_ranges.append((FeedRangeEpk(Range(feed_range[0], feed_range[1],
                                            True, False)), session_token))
        target_feed_range = FeedRangeEpk(Range(test_param[1][0], test_param[1][1], True, False))
        actual_test_params.append((split_ranges, target_feed_range, test_param[2]))
    return actual_test_params

@pytest.mark.cosmosEmulator
@pytest.mark.unittest
@pytest.mark.usefixtures("setup")
class TestSessionTokenHelpers:
    """Test for session token helpers"""

    created_db: DatabaseProxy = None
    client: cosmos_client.CosmosClient = None
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy
    configs = test_config.TestConfig
    TEST_DATABASE_ID = configs.TEST_DATABASE_ID
    TEST_COLLECTION_ID = configs.TEST_MULTI_PARTITION_CONTAINER_ID


    # have a test for split, merge, different versions, compound session tokens, hpk, and for normal case for several session tokens
    # have tests for all the scenarios in the testing plan
    # should try once with 35000 session tokens
    # check if pkrangeid is being filtered out
    def test_get_session_token_update(self, setup):
        feed_range = FeedRangeEpk(Range("AA", "BB", True, False))
        session_token = "0:1#54#3=50"
        feed_ranges_and_session_tokens = [(feed_range, session_token)]
        session_token = "0:1#51#3=52"
        feed_ranges_and_session_tokens.append((feed_range, session_token))
        session_token = setup["created_collection"].get_updated_session_token(feed_ranges_and_session_tokens, feed_range)
        assert session_token == "0:1#54#3=52"

    def test_many_session_tokens_update_same_range(self, setup):
        feed_range = FeedRangeEpk(Range("AA", "BB", True, False))
        feed_ranges_and_session_tokens = []
        for i in range(1000):
            session_token = "0:1#" + str(random.randint(1, 100)) + "#3=" + str(random.randint(1, 100))
            feed_ranges_and_session_tokens.append((feed_range, session_token))
        session_token = "0:1#101#3=101"
        feed_ranges_and_session_tokens.append((feed_range, session_token))
        updated_session_token = setup["created_collection"].get_updated_session_token(feed_ranges_and_session_tokens,
                                                                                      feed_range)
        assert updated_session_token == session_token

    @pytest.mark.parametrize("split_ranges, target_feed_range, expected_session_token", create_split_ranges())
    def test_simulated_splits_merges(self, setup, split_ranges, target_feed_range, expected_session_token):
        updated_session_token = setup["created_collection"].get_updated_session_token(split_ranges, target_feed_range)
        assert updated_session_token == expected_session_token

    def test_invalid_feed_range(self, setup):
        feed_range = FeedRangeEpk(Range("AA", "BB", True, False))
        session_token = "0:1#54#3=50"
        feed_ranges_and_session_tokens = [(feed_range, session_token)]
        with pytest.raises(ValueError, match='There were no overlapping feed ranges with the target.'):
            setup["created_collection"].get_updated_session_token(feed_ranges_and_session_tokens,
                            FeedRangeEpk(Range("CC", "FF", True, False)))




if __name__ == '__main__':
    unittest.main()
