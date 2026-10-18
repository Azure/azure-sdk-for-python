# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Original helper assertions with an explicitly selected, closed client.

The test methods retain tests/test_session_token_helpers.py inputs and
assertions. The utility needs no existing database or container. Only account
initialization occurs outside the measured utility calls.
"""

import os
import random

import pytest

from azure.cosmos import CosmosClient
from azure.cosmos._change_feed.feed_range_internal import FeedRangeInternalEpk
from azure.cosmos._routing.routing_range import Range
from test_session_token_helpers import create_split_ranges


COLLECTION = "created_collection"


@pytest.fixture(scope="class")
def setup():
    with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as client:
        yield {COLLECTION: client.get_database_client("unused").get_container_client("orders")}


@pytest.fixture(autouse=True)
def deterministic_observations():
    state = random.getstate()
    random.seed(0)
    try:
        yield
    finally:
        random.setstate(state)


class TestSessionTokenHelpers:
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
        target_feed_range = FeedRangeInternalEpk(Range(target_feed_range[0], target_feed_range[1],
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
