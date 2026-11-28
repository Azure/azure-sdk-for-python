# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Rust-path copies of the sync query tests that seed items with upsert_item.

Setup owns a unique database with a multi-partition ``/pk`` container standing in for the
shared ``TEST_MULTI_PARTITION_CONTAINER_ID`` container, and always deletes it. Test bodies
are unchanged.
"""
import unittest
import uuid

import pytest

from azure.cosmos import CosmosClient
from azure.cosmos._routing.feed_range_continuation import _decode_token
from azure.cosmos.partition_key import PartitionKey
from config.clients import create_data_client, create_setup_client
from config.settings import TestSettings, unique_database_id


@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosQuery
@pytest.mark.cosmosAADQuery
class TestQuery(unittest.TestCase):
    """Rust-path copies of tests/test_query.py::TestQuery."""
    client: CosmosClient = None
    config = TestSettings

    @classmethod
    def setUpClass(cls):
        cls.TEST_DATABASE_ID = unique_database_id("upsert-query")
        cls.key_client = create_setup_client(_backend="rust")
        cls.addClassCleanup(cls.key_client.close)
        cls.key_db = cls.key_client.create_database(cls.TEST_DATABASE_ID)
        cls.addClassCleanup(cls.key_client.delete_database, cls.TEST_DATABASE_ID)
        cls.key_db.create_container(
            id=cls.config.TEST_MULTI_PARTITION_CONTAINER_ID,
            partition_key=PartitionKey(path="/" + cls.config.TEST_CONTAINER_PARTITION_KEY),
            offer_throughput=cls.config.THROUGHPUT_FOR_5_PARTITIONS)
        cls.client = create_data_client(_backend="rust")
        cls.addClassCleanup(cls.client.close)
        cls.created_db = cls.client.get_database_client(cls.TEST_DATABASE_ID)

    def test_full_pk_continuation_emits_service_token_by_default_rust(self):
        # Source: tests/test_query.py::TestQuery.test_full_pk_continuation_emits_legacy_by_default
        # A full-partition-key query must still hand back the legacy (opaque) continuation
        # token, not the new feed-range token: _decode_token returns None only for the legacy
        # form. Without this, changing the default token format could break customers who
        # stored an old token and replay it later.
        created_collection = self.created_db.get_container_client(self.config.TEST_MULTI_PARTITION_CONTAINER_ID)
        created_collection.upsert_item(body={'pk': 'pk', 'id': str(uuid.uuid4())})
        created_collection.upsert_item(body={'pk': 'pk', 'id': str(uuid.uuid4())})

        query_iterable = created_collection.query_items(
            query='SELECT * from c',
            partition_key='pk',
            max_item_count=1,
        )
        pager = query_iterable.by_page()
        pager.next()
        token = pager.continuation_token

        self.assertIsNotNone(token)
        self.assertIsNone(_decode_token(token))

    def test_full_pk_service_token_replay_resumes_same_page_rust(self):
        # Source: tests/test_query.py::TestQuery.test_full_pk_legacy_replay_resumes_same_page
        # Replaying that legacy continuation token must resume on the same next page. Without
        # this, a regression in legacy-token replay would drop or repeat results for customers
        # who page through query results.
        created_collection = self.created_db.get_container_client(self.config.TEST_MULTI_PARTITION_CONTAINER_ID)
        created_collection.upsert_item(body={'pk': 'pk', 'id': str(uuid.uuid4())})
        created_collection.upsert_item(body={'pk': 'pk', 'id': str(uuid.uuid4())})

        query_iterable = created_collection.query_items(
            query='SELECT * from c',
            partition_key='pk',
            max_item_count=1,
        )
        pager = query_iterable.by_page()
        pager.next()
        token = pager.continuation_token
        second_page = list(pager.next())[0]

        self.assertIsNotNone(token)
        self.assertIsNone(_decode_token(token))

        replay_pager = query_iterable.by_page(token)
        replay_second_page = list(replay_pager.next())[0]
        self.assertEqual(second_page['id'], replay_second_page['id'])

    def test_query_positional_args_rust(self):
        # Source: tests/test_query.py::TestQuery.test_query_positional_args
        container = self.created_db.get_container_client(self.config.TEST_MULTI_PARTITION_CONTAINER_ID)
        partition_key_value1 = "pk1"
        partition_key_value2 = "pk2"

        num_items = 10
        new_items = []
        for pk_value in [partition_key_value1, partition_key_value2]:
            for i in range(num_items):
                item = {
                    self.config.TEST_CONTAINER_PARTITION_KEY: pk_value,
                    'id': f"{pk_value}_{i}",
                    'name': 'sample name'
                }
                new_items.append(item)

        for item in new_items:
            container.upsert_item(body=item)

        query = "SELECT * FROM root r WHERE r.name=@name"
        parameters = [{'name': '@name', 'value': 'sample name'}]
        partition_key_value = partition_key_value2
        enable_cross_partition_query = True
        max_item_count = 3
        enable_scan_in_query = True
        populate_query_metrics = True
        pager = container.query_items(
            query,
            parameters,
            partition_key_value,
            enable_cross_partition_query,
            max_item_count,
            enable_scan_in_query,
            populate_query_metrics,
        ).by_page()

        ids = []
        for page in pager:
            items = list(page)
            num_items = len(items)
            for item in items:
                assert item['pk'] == partition_key_value
                ids.append(item['id'])
            assert num_items <= max_item_count
        assert ids == [item['id'] for item in new_items if item['pk'] == partition_key_value]


if __name__ == "__main__":
    unittest.main()
