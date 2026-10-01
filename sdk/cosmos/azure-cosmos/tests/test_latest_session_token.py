# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import random
import time
import unittest
import uuid

import pytest

from _split_test_utils import assert_no_stage_failures, split_stage, wait_for_split_ranges
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
@pytest.mark.cosmosAADSplit
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

    @classmethod
    def tearDownClass(cls):
        cls.client.close()
        cls.key_client.close()

    @pytest.mark.timeout(1500)
    def test_change_feed_session_token_and_read_items_after_split(self):
        container_ref = self.key_database.create_container(
            "test_grouped_partition_split_" + str(uuid.uuid4()), PartitionKey(path="/pk"), offer_throughput=400)
        self.addCleanup(self.key_database.delete_container, container_ref.id)
        container = self.database.get_container_client(container_ref.id)
        key_container_for_split = self.key_database.get_container_client(container.id)

        with split_stage("change_feed_before"):
            self.assertEqual(list(container.query_items_change_feed(start_time="Beginning")), [])
            continuation = container.client_connection.last_response_headers["etag"]
            self.assertTrue(continuation)
            container.create_item({"pk": "pk", "id": "doc1"})
            initial = list(container.query_items_change_feed(continuation=continuation))
            self.assertEqual([item["id"] for item in initial], ["doc1"])
            continuation = container.client_connection.last_response_headers["etag"]

        with split_stage("read_items_before"):
            items_to_read = []
            for i in range(5):
                item_id = "item_split_{}_{}".format(i, uuid.uuid4())
                container.create_item({"id": item_id, "pk": item_id, "data": i})
                items_to_read.append((item_id, item_id))
            initial_read = container.read_items(items=items_to_read)
            self.assertEqual(len(initial_read), len(items_to_read))
            self.assertEqual({item["id"] for item in initial_read}, {item_id for item_id, _ in items_to_read})

        with split_stage("logical_session_token_before"):
            feed_ranges_and_session_tokens = []
            target_pk = "A1"
            target_feed_range = container.feed_range_from_partition_key(target_pk)
            target_token, _ = self.create_items_logical_pk(
                container, target_feed_range, "", feed_ranges_and_session_tokens)
            logical_token = container.get_latest_session_token(feed_ranges_and_session_tokens, target_feed_range)
            self.assertTrue(logical_token == target_token, "Pre-split logical session token differs")

        with split_stage("physical_session_token_before"):
            physical_tokens = []
            pk_feed_range = container.feed_range_from_partition_key(target_pk)
            target_token, physical_range, _ = self.create_items_physical_pk(
                container, pk_feed_range, "", physical_tokens)
            physical_token = container.get_latest_session_token(physical_tokens, physical_range)
            self.assertTrue(physical_token == target_token, "Pre-split physical session token differs")
            _, pre_split_token = parse_session_token(physical_token)
            feed_ranges_and_session_tokens.append((target_feed_range, logical_token))

        with split_stage("change_feed_checkpoint"):
            pre_split_changes = list(container.query_items_change_feed(continuation=continuation))
            self.assertEqual(len(pre_split_changes), 205)
            continuation = container.client_connection.last_response_headers["etag"]
            self.assertTrue(continuation)

        with split_stage("split_and_convergence"):
            initial_ranges = list(key_container_for_split.client_connection._ReadPartitionKeyRanges(
                key_container_for_split.container_link))
            self.assertEqual(len(initial_ranges), 1)
            deadline = time.monotonic() + test_config.SPLIT_TIMEOUT
            test_config.TestConfig.trigger_split(key_container_for_split, 11000)
            wait_for_split_ranges(key_container_for_split, initial_ranges[0]["id"], deadline)

        failures = []
        with split_stage("read_items_after", failures):
            final_read = container.read_items(items=items_to_read)
            self.assertEqual(len(final_read), len(items_to_read))
            self.assertEqual({item["id"] for item in final_read}, {item_id for item_id, _ in items_to_read})

        with split_stage("change_feed_after", failures):
            for item_id, pk in (("doc2", "pk2"), ("doc3", "pk3"), ("doc4", "pk4")):
                container.create_item({"id": item_id, "pk": pk})
            changes = list(container.query_items_change_feed(continuation=continuation))
            self.assertEqual([item["id"] for item in changes], ["doc2", "doc3", "doc4"])

        with split_stage("logical_session_token_after", failures):
            target_token, _ = self.create_items_logical_pk(
                container, target_feed_range, logical_token, feed_ranges_and_session_tokens)
            updated_feed_range = container.feed_range_from_partition_key(target_pk)
            latest = container.get_latest_session_token(feed_ranges_and_session_tokens, updated_feed_range)
            self.assertTrue(latest == target_token, "Post-split logical session token differs")

        with split_stage("physical_session_token_after", failures):
            _, physical_range, _ = self.create_items_physical_pk(
                container, pk_feed_range, physical_token, physical_tokens)
            latest = container.get_latest_session_token(physical_tokens, physical_range)
            pk_range_id, post_split_token = parse_session_token(latest)
            self.assertGreaterEqual(post_split_token.global_lsn, pre_split_token.global_lsn)
            self.assertIn("2", pk_range_id)

        assert_no_stage_failures(failures)

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
