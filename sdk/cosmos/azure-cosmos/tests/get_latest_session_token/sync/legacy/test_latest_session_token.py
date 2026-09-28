# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Owned fixture for the original non-split live token tests.

The two test methods are copied from tests/test_latest_session_token.py.
Their original 100-write helpers are reused unchanged. The forced 11000-RU
split test is deliberately not included in this ordinary-account run.
"""

import os
import random
import unittest
import uuid

from azure.cosmos import CosmosClient, PartitionKey
import test_latest_session_token as original_tests


class TestLatestSessionToken(unittest.TestCase):
    def setUp(self):
        state = random.getstate()
        self.addCleanup(random.setstate, state)
        random.seed(0)
        self.client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")
        self.addCleanup(self.client.close)
        self.database = self.client.create_database("token_parity_" + uuid.uuid4().hex)
        self.addCleanup(self.client.delete_database, self.database.id)
        self.key_database = self.database
        print(f"\nOwned token-test database: {self.database.id}")

    create_items_logical_pk = staticmethod(original_tests.TestLatestSessionToken.create_items_logical_pk)
    create_items_physical_pk = staticmethod(original_tests.TestLatestSessionToken.create_items_physical_pk)

    def test_latest_session_token_hpk(self):
        container_ref = self.key_database.create_container(
            "test_updated_session_token_hpk" + str(uuid.uuid4()),
            PartitionKey(path=["/state", "/city", "/zipcode"], kind="MultiHash"),
            offer_throughput=400)
        container = self.database.get_container_client(container_ref.id)
        feed_ranges_and_session_tokens = []
        previous_session_token = ""
        pk = ['CA', 'LA1', '90001']
        pk_feed_range = container.feed_range_from_partition_key(pk)
        target_session_token, target_feed_range, previous_session_token = self.create_items_physical_pk(container,
                                                                                                        pk_feed_range,
                                                                                                        previous_session_token,
                                                                                                        feed_ranges_and_session_tokens,
                                                                                                        True)
        session_token = container.get_latest_session_token(feed_ranges_and_session_tokens, target_feed_range)
        assert session_token == target_session_token
        self.key_database.delete_container(container.id)

    def test_latest_session_token_logical_hpk(self):
        container_ref = self.key_database.create_container(
            "test_updated_session_token_from_logical_hpk" + str(uuid.uuid4()),
            PartitionKey(path=["/state", "/city", "/zipcode"], kind="MultiHash"),
            offer_throughput=400)
        container = self.database.get_container_client(container_ref.id)
        feed_ranges_and_session_tokens = []
        previous_session_token = ""
        target_pk = ['CA', 'LA1', '90001']
        target_feed_range = container.feed_range_from_partition_key(target_pk)
        target_session_token, previous_session_token = self.create_items_logical_pk(container, target_feed_range,
                                                                                    previous_session_token,
                                                                                    feed_ranges_and_session_tokens,
                                                                                    True)
        session_token = container.get_latest_session_token(feed_ranges_and_session_tokens, target_feed_range)
        assert session_token == target_session_token
        self.key_database.delete_container(container.id)
