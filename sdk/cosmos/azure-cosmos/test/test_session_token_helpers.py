# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import random
import time
import unittest
import uuid

import pytest

import azure.cosmos.cosmos_client as cosmos_client
import test_config
from azure.cosmos import DatabaseProxy
from azure.cosmos._feed_range import FeedRangeEpk
from azure.cosmos._routing.routing_range import Range
from azure.cosmos._session_token_helpers import is_compound_session_token, create_vector_session_token_and_pkrange_id

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
    # add one with several ranges being equal to one
    test_params = [ # split with two children
                   ([(("AA", "DD"), "0:1#51#3=52"), (("AA", "BB"),"1:1#55#3=52"), (("BB", "DD"),"2:1#54#3=52")],
                    ("AA", "DD"), "1:1#55#3=52,2:1#54#3=52"),
                    # split with one child
                   ([(("AA", "DD"), "0:1#51#3=52"), (("AA", "BB"),"1:1#55#3=52")],
                    ("AA", "DD"), "0:1#51#3=52,1:1#55#3=52"),
                    # several ranges being equal to one range
                   ([(("AA", "DD"), "0:1#42#3=52"), (("AA", "BB"), "1:1#51#3=52"),
                    (("BB", "CC"),"1:1#53#3=52"), (("CC", "DD"),"1:1#55#3=52")],
                    ("AA", "DD"), "1:1#55#3=52"),
                    # several ranges being equal to one range
                   ([(("AA", "DD"), "0:1#60#3=52"), (("AA", "BB"), "1:1#51#3=52"),
                    (("BB", "CC"),"1:1#53#3=52"), (("CC", "DD"),"1:1#55#3=52")],
                    ("AA", "DD"), "0:1#60#3=52"),
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
                    # overlapping ranges
                   ([(("AA", "CC"), "0:1#54#3=52"), (("BB", "FF"),"2:1#51#3=52")],
                    ("AA", "EE"), "0:1#54#3=52,2:1#51#3=52"),
                    # different version numbers
                   ([(("AA", "BB"), "0:1#54#3=52"), (("AA", "BB"),"0:2#57#3=53")],
                    ("AA", "BB"), "0:2#57#3=53")
                  ]
    actual_test_params = []
    for test_param in test_params:
        split_ranges = []
        for feed_range, session_token in test_param[0]:
            split_ranges.append((FeedRangeEpk(Range(feed_range[0], feed_range[1],
                                            True, False)), session_token))
        target_feed_range = FeedRangeEpk(Range(test_param[1][0], test_param[1][1], True, False))
        actual_test_params.append((split_ranges, target_feed_range, test_param[2]))
    return actual_test_params

def trigger_split(setup):
    print("Triggering a split in session token helpers")
    setup[COLLECTION].replace_throughput(11000)
    print("changed offer to 11k")
    print("--------------------------------")
    print("Waiting for split to complete")
    start_time = time.time()

    while True:
        offer = setup[COLLECTION].get_throughput()
        if offer.properties['content'].get('isOfferReplacePending', False):
            if time.time() - start_time > 60 * 25:  # timeout test at 25 minutes
                unittest.skip("Partition split didn't complete in time.")
            else:
                print("Waiting for split to complete")
                time.sleep(60)
        else:
            break

    print("Split in session token helpers has completed")

def create_items_logical_pk(setup, target_pk, previous_session_token, feed_ranges_and_session_tokens):
    target_session_token = ""
    for i in range(100):
        item = {
            'id': 'item' + str(uuid.uuid4()),
            'name': 'sample',
            'pk': 'A' + str(random.randint(1, 10))
        }
        setup[COLLECTION].create_item(item, session_token=previous_session_token)
        request_context = setup[COLLECTION].client_connection.last_response_headers["request_context"]
        if item['pk'] == target_pk:
            target_session_token = request_context["session_token"]
        previous_session_token = request_context["session_token"]
        feed_ranges_and_session_tokens.append((setup[COLLECTION].feed_range_from_partition_key(item['pk']),
                                               request_context["session_token"]))
    return target_session_token, previous_session_token

def create_items_physical_pk(setup, pk_feed_range, previous_session_token, feed_ranges_and_session_tokens):
    target_session_token = ""
    container_feed_ranges = setup[COLLECTION].read_feed_ranges()
    target_feed_range = None
    for feed_range in container_feed_ranges:
        if setup[COLLECTION].is_feed_range_subset(feed_range, pk_feed_range):
            target_feed_range = feed_range
            break

    for i in range(100):
        item = {
            'id': 'item' + str(uuid.uuid4()),
            'name': 'sample',
            'pk': 'A' + str(random.randint(1, 10))
        }
        setup[COLLECTION].create_item(item, session_token=previous_session_token)
        request_context = setup[COLLECTION].client_connection.last_response_headers["request_context"]
        curr_feed_range = setup[COLLECTION].feed_range_from_partition_key(item['pk'])
        if setup[COLLECTION].is_feed_range_subset(target_feed_range, curr_feed_range):
            target_session_token = request_context["session_token"]
        previous_session_token = request_context["session_token"]
        feed_ranges_and_session_tokens.append((curr_feed_range,
                                               request_context["session_token"]))

    return target_session_token, target_feed_range, previous_session_token

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
    TEST_COLLECTION_ID = configs.TEST_SINGLE_PARTITION_CONTAINER_ID

    def test_get_session_token_update(self, setup):
        feed_range = FeedRangeEpk(Range("AA", "BB", True, False))
        session_token = "0:1#54#3=50"
        feed_ranges_and_session_tokens = [(feed_range, session_token)]
        session_token = "0:1#51#3=52"
        feed_ranges_and_session_tokens.append((feed_range, session_token))
        session_token = setup[COLLECTION].get_updated_session_token(feed_ranges_and_session_tokens, feed_range)
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

    def test_many_session_tokens_update(self, setup):
        feed_range = FeedRangeEpk(Range("AA", "BB", True, False))
        feed_ranges_and_session_tokens = []
        for i in range(1000):
            session_token = "0:1#" + str(random.randint(1, 100)) + "#3=" + str(random.randint(1, 100))
            feed_ranges_and_session_tokens.append((feed_range, session_token))

        # adding irrelevant feed ranges
        feed_range1 = FeedRangeEpk(Range("CC", "FF", True, False))
        feed_range2 = FeedRangeEpk(Range("00", "55", True, False))
        for i in range(1000):
            session_token = "0:1#" + str(random.randint(1, 100)) + "#3=" + str(random.randint(1, 100))
            if i % 2 == 0:
                feed_ranges_and_session_tokens.append((feed_range1, session_token))
            else:
                feed_ranges_and_session_tokens.append((feed_range2, session_token))
        session_token = "0:1#101#3=101"
        feed_ranges_and_session_tokens.append((feed_range, session_token))
        updated_session_token = setup["created_collection"].get_updated_session_token(feed_ranges_and_session_tokens,
                                                                                      feed_range)
        assert updated_session_token == session_token

    @pytest.mark.parametrize("split_ranges, target_feed_range, expected_session_token", create_split_ranges())
    def test_simulated_splits_merges(self, setup, split_ranges, target_feed_range, expected_session_token):
        updated_session_token = setup[COLLECTION].get_updated_session_token(split_ranges, target_feed_range)
        assert updated_session_token == expected_session_token

    def test_invalid_feed_range(self, setup):
        feed_range = FeedRangeEpk(Range("AA", "BB", True, False))
        session_token = "0:1#54#3=50"
        feed_ranges_and_session_tokens = [(feed_range, session_token)]
        with pytest.raises(ValueError, match='There were no overlapping feed ranges with the target.'):
            setup["created_collection"].get_updated_session_token(feed_ranges_and_session_tokens,
                            FeedRangeEpk(Range("CC", "FF", True, False)))

    def test_updated_session_token_from_logical_pk(self, setup):
        feed_ranges_and_session_tokens = []
        previous_session_token = ""
        target_pk = 'A1'
        target_session_token, previous_session_token = create_items_logical_pk(setup, target_pk, previous_session_token, feed_ranges_and_session_tokens)
        target_feed_range = setup[COLLECTION].feed_range_from_partition_key(target_pk)
        session_token = setup[COLLECTION].get_updated_session_token(feed_ranges_and_session_tokens, target_feed_range)

        assert session_token == target_session_token

        trigger_split(setup)

        target_session_token, _ = create_items_logical_pk(setup, target_pk, session_token, feed_ranges_and_session_tokens)
        target_feed_range = setup[COLLECTION].feed_range_from_partition_key(target_pk)
        session_token = setup[COLLECTION].get_updated_session_token(feed_ranges_and_session_tokens, target_feed_range)

        assert session_token == target_session_token


    def test_updated_session_token_from_physical_pk(self, setup):
        feed_ranges_and_session_tokens = []
        previous_session_token = ""
        pk_feed_range = setup[COLLECTION].feed_range_from_partition_key('A1')
        target_session_token, target_feed_range, previous_session_token = create_items_physical_pk(setup, pk_feed_range,
                                                                           previous_session_token,
                                                                           feed_ranges_and_session_tokens)

        session_token = setup[COLLECTION].get_updated_session_token(feed_ranges_and_session_tokens, target_feed_range)
        assert session_token == target_session_token

        trigger_split(setup)

        _, target_feed_range, previous_session_token = create_items_physical_pk(setup, pk_feed_range,
                                                                           session_token,
                                                                           feed_ranges_and_session_tokens)

        session_token = setup[COLLECTION].get_updated_session_token(feed_ranges_and_session_tokens, target_feed_range)
        assert is_compound_session_token(session_token)
        session_tokens = session_token.split(",")
        assert len(session_tokens) == 2
        pk_range_id1, session_token1 = create_vector_session_token_and_pkrange_id(session_tokens[0])
        pk_range_id2, session_token2 = create_vector_session_token_and_pkrange_id(session_tokens[1])
        pk_range_ids = [pk_range_id1, pk_range_id2]

        assert 320 == (session_token1.global_lsn + session_token2.global_lsn)
        assert 1 in pk_range_ids
        assert 2 in pk_range_ids





if __name__ == '__main__':
    unittest.main()
