# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Owned fixture for the original non-split live token tests.

The two test methods are copied from tests/test_partition_split_scenarios.py.
Their original 100-write helpers are owned by the retained suite. These tests
do not split partitions; they keep the original's split-lane markers. The
forced 11000-RU split test is in a separate file; it runs only in the CI
split lane, or locally with COSMOS_SESSION_TOKEN_REAL_SPLIT=1.
"""

import random
import unittest
import uuid

import pytest

from azure.cosmos import PartitionKey
from config.clients import create_data_client, create_setup_client
from get_latest_session_token._fixtures import create_items_logical_pk, create_items_physical_pk


@pytest.mark.cosmosSplit
@pytest.mark.cosmosAADSplit
class TestLatestSessionToken(unittest.TestCase):
    def setUp(self):
        state = random.getstate()
        self.addCleanup(random.setstate, state)
        random.seed(0)
        # Key client owns the database and containers; the data client (AAD in
        # AAD lanes) writes items and reads tokens, as in the original.
        self.key_client = create_setup_client(_backend="rust")
        self.addCleanup(self.key_client.close)
        self.client = create_data_client(_backend="rust")
        self.addCleanup(self.client.close)
        self.key_database = self.key_client.create_database("token_parity_" + uuid.uuid4().hex)
        self.addCleanup(self.key_client.delete_database, self.key_database.id)
        self.database = self.client.get_database_client(self.key_database.id)
        print(f"\nOwned token-test database: {self.key_database.id}")

    create_items_logical_pk = staticmethod(create_items_logical_pk)
    create_items_physical_pk = staticmethod(create_items_physical_pk)

    def test_latest_session_token_hpk_rust(self):
        # Source: tests/test_partition_split_scenarios.py::TestPartitionSplitScenarios.test_latest_session_token_hpk
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

    def test_latest_session_token_logical_hpk_rust(self):
        # Source: tests/test_partition_split_scenarios.py::TestPartitionSplitScenarios.test_latest_session_token_logical_hpk
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
