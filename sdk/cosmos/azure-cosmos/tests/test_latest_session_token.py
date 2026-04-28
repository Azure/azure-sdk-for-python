# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import random
import unittest
import uuid

import pytest

import azure.cosmos.cosmos_client as cosmos_client
import test_config
from azure.cosmos import DatabaseProxy, PartitionKey
from azure.cosmos._change_feed.feed_range_internal import FeedRangeInternalEpk
from azure.cosmos._session_token_helpers import is_compound_session_token, parse_session_token
from azure.cosmos.http_constants import HttpHeaders


def create_item(hpk):
    if hpk:
        item = {
            'id': 'item' + str(uuid.uuid4()),
            'name': 'sample',
            'state': 'CA',
            'city': 'LA' + str(random.randint(1, 10)),
            'zipcode': '90001'
        }
    else:
        item = {
            'id': 'item' + str(uuid.uuid4()),
            'name': 'sample',
            'pk': 'A' + str(random.randint(1, 10))
        }
    return item


@pytest.mark.cosmosSplit
# @pytest.mark.cosmosAAD  # TEMP: disabled to validate AAD pipeline using only test_aad.py
class TestLatestSessionToken(unittest.TestCase):
    """Test for session token helpers"""

    created_db: DatabaseProxy = None
    client: cosmos_client.CosmosClient = None
    key_database: DatabaseProxy = None
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    configs = test_config.TestConfig
    TEST_DATABASE_ID = configs.TEST_DATABASE_ID

    @classmethod
    def setUpClass(cls):
        cls.key_client, cls.key_database, cls.client, cls.database = (
            test_config.TestConfig.create_test_clients(cls.TEST_DATABASE_ID))

    def test_latest_session_token_from_pk(self):
        container_ref = self.key_database.create_container("test_updated_session_token_from_logical_pk" + str(uuid.uuid4()),
                                                             PartitionKey(path="/pk"),
                                                             offer_throughput=400)
        container = self.database.get_container_client(container_ref.id)
        # testing with storing session tokens by feed range that maps to logical pk
        feed_ranges_and_session_tokens = []
        previous_session_token = ""
        target_pk = 'A1'
        target_feed_range = container.feed_range_from_partition_key(target_pk)
        target_session_token, previous_session_token = self.create_items_logical_pk(container, target_feed_range,
                                                                                    previous_session_token,
                                                                                    feed_ranges_and_session_tokens)
        session_token = container.get_latest_session_token(feed_ranges_and_session_tokens, target_feed_range)
        assert session_token == target_session_token

        # testing with storing session tokens by feed range that maps to physical pk
        phys_feed_ranges_and_session_tokens = []
        phys_previous_session_token = ""
        pk_feed_range = container.feed_range_from_partition_key(target_pk)
        phys_target_session_token, phys_target_feed_range, phys_previous_session_token = self.create_items_physical_pk(container, pk_feed_range,
                                                                                                        phys_previous_session_token,
                                                                                                        phys_feed_ranges_and_session_tokens)

        phys_session_token = container.get_latest_session_token(phys_feed_ranges_and_session_tokens, phys_target_feed_range)
        assert phys_session_token == phys_target_session_token
        _, pre_split_session_token = parse_session_token(phys_session_token)

        feed_ranges_and_session_tokens.append((target_feed_range, session_token))

        # trigger_split() calls replace_throughput() which is a control-plane operation
        # and must run through the key-auth client (AAD Data Contributor cannot replace offers).
        key_container_for_split = self.key_database.get_container_client(container.id)
        test_config.TestConfig.trigger_split(key_container_for_split, 11000)

        # testing with storing session tokens by feed range that maps to logical pk post split
        target_session_token, _ = self.create_items_logical_pk(container, target_feed_range, session_token,
                                                               feed_ranges_and_session_tokens)
        target_feed_range = container.feed_range_from_partition_key(target_pk)
        session_token = container.get_latest_session_token(feed_ranges_and_session_tokens, target_feed_range)

        assert session_token == target_session_token

        # testing with storing session tokens by feed range that maps to physical pk post split
        _, phys_target_feed_range, phys_previous_session_token = self.create_items_physical_pk(container, pk_feed_range,
                                                                                     phys_session_token,
                                                                                     phys_feed_ranges_and_session_tokens)

        phys_session_token = container.get_latest_session_token(phys_feed_ranges_and_session_tokens, phys_target_feed_range)
        pk_range_id, session_token = parse_session_token(phys_session_token)

        assert session_token.global_lsn >= pre_split_session_token.global_lsn
        assert '2' in pk_range_id
        self.key_database.delete_container(container.id)

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

    @staticmethod
    def create_items_logical_pk(container, target_pk_range, previous_session_token, feed_ranges_and_session_tokens, hpk=False):
        target_session_token = ""
        for i in range(100):
            item = create_item(hpk)
            response = container.create_item(item, session_token=previous_session_token)
            session_token = response.get_response_headers()[HttpHeaders.SessionToken]
            pk = item['pk'] if not hpk else [item['state'], item['city'], item['zipcode']]
            pk_range = container.feed_range_from_partition_key(pk)
            pk_feed_range_epk = FeedRangeInternalEpk.from_json(pk_range)
            target_feed_range_epk = FeedRangeInternalEpk.from_json(target_pk_range)
            if (pk_feed_range_epk.get_normalized_range() ==
                    target_feed_range_epk.get_normalized_range()):
                target_session_token = session_token
            previous_session_token = session_token
            feed_ranges_and_session_tokens.append((pk_range,
                                               session_token))
        return target_session_token, previous_session_token

    @staticmethod
    def create_items_physical_pk(container, pk_feed_range, previous_session_token, feed_ranges_and_session_tokens, hpk=False):
        target_session_token = ""
        container_feed_ranges = list(container.read_feed_ranges())
        target_feed_range = None
        for feed_range in container_feed_ranges:
            if container.is_feed_range_subset(feed_range, pk_feed_range):
                target_feed_range = feed_range
                break

        for i in range(100):
            item = create_item(hpk)
            response = container.create_item(item, session_token=previous_session_token)
            session_token = response.get_response_headers()[HttpHeaders.SessionToken]
            if hpk:
                pk = [item['state'], item['city'], item['zipcode']]
                curr_feed_range = container.feed_range_from_partition_key(pk)
            else:
                curr_feed_range = container.feed_range_from_partition_key(item['pk'])
            if container.is_feed_range_subset(target_feed_range, curr_feed_range):
                target_session_token = session_token
            previous_session_token = session_token
            feed_ranges_and_session_tokens.append((curr_feed_range, session_token))

        return target_session_token, target_feed_range, previous_session_token

if __name__ == '__main__':
    unittest.main()
