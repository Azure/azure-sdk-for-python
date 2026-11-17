# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Change-feed filter assertions using Rust-backed clients and SDK continuation tokens."""

import uuid

import pytest
from azure.cosmos.partition_key import PartitionKey
from config.clients import create_data_client, create_setup_client
from config.settings import TestSettings, unique_database_id


@pytest.fixture(scope="class")
def setup():
    # Build two clients: a key-auth client for create/delete container (control plane)
    # and a data-plane client (AAD or key) for the change feed reads.
    database_id = unique_database_id("query-change-feed-filters")
    # Closed decision: Rust owns endpoint discovery and multi-write routing
    #. Rust-backed clients reject the
    # original's multiple_write_locations argument (even False), so it is omitted.
    key_client = create_setup_client(_backend="rust")
    data_client = create_data_client(_backend="rust")
    try:
        key_db = key_client.create_database(database_id)
        try:
            yield {
                "key_db": key_db,
                "data_db": data_client.get_database_client(database_id),
                "is_emulator": TestSettings.is_emulator
            }
        finally:
            key_client.delete_database(database_id)
    finally:
        data_client.close()
        key_client.close()



@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosQuery
@pytest.mark.cosmosAADCircuitBreaker
@pytest.mark.unittest
@pytest.mark.usefixtures("setup")
class TestChangeFeed:
    @pytest.mark.parametrize("change_feed_filter_param", ["partitionKey", "partitionKeyRangeId", "feedRange"])
    def test_query_change_feed_with_different_filter_rust(self, change_feed_filter_param, setup):
        # Source: tests/test_change_feed.py::TestChangeFeed.test_query_change_feed_with_different_filter
        # Core test: read the change feed scoped by each filter type (partition key /
        # range id / feed range), from current, from beginning, and from a continuation
        # token, and check new items show up and paging works. Without it, any of these
        # paths could silently return wrong or missing changes.
        created_collection_ref = setup["key_db"].create_container(
            f"change_feed_test_{change_feed_filter_param}_{str(uuid.uuid4())}",
            PartitionKey(path="/pk"))
        created_collection = setup["data_db"].get_container_client(created_collection_ref.id)
        # Read change feed without passing any options
        query_iterable = created_collection.query_items_change_feed()
        iter_list = list(query_iterable)
        assert len(iter_list) == 0

        if change_feed_filter_param == "partitionKey":
            filter_param = {"partition_key": "pk"}
        elif change_feed_filter_param == "partitionKeyRangeId":
            filter_param = {"partition_key_range_id": "0"}
        elif change_feed_filter_param == "feedRange":
            feed_ranges = list(created_collection.read_feed_ranges())
            assert len(feed_ranges) == 1
            filter_param = {"feed_range": feed_ranges[0]}
        else:
            filter_param = None

        # Read change feed from current should return an empty list
        query_iterable = created_collection.query_items_change_feed(**filter_param)
        iter_list = list(query_iterable)
        assert len(iter_list) == 0
        assert 'etag' in created_collection.client_connection.last_response_headers
        assert created_collection.client_connection.last_response_headers['etag'] !=''

        # Read change feed from beginning should return an empty list
        query_iterable = created_collection.query_items_change_feed(
            is_start_from_beginning=True,
            **filter_param
        )
        pages = query_iterable.by_page()
        iter_list = [item for page in pages for item in page]
        assert len(iter_list) == 0
        assert 'etag' in created_collection.client_connection.last_response_headers
        continuation1 = pages.continuation_token
        assert continuation1

        # Create a document. Read change feed should return be able to read that document
        document_definition = {'pk': 'pk', 'id': 'doc1'}
        created_collection.create_item(body=document_definition)
        query_iterable = created_collection.query_items_change_feed(
            is_start_from_beginning=True,
            **filter_param
        )
        pages = query_iterable.by_page()
        iter_list = [item for page in pages for item in page]
        assert len(iter_list) == 1
        assert iter_list[0]['id'] == 'doc1'
        assert 'etag' in created_collection.client_connection.last_response_headers
        continuation2 = pages.continuation_token
        assert continuation2
        assert continuation2 != continuation1

        # Create two new documents. Verify that change feed contains the 2 new documents
        # with page size 1 and page size 100
        document_definition = {'pk': 'pk', 'id': 'doc2'}
        created_collection.create_item(body=document_definition)
        document_definition = {'pk': 'pk3', 'id': 'doc3'}
        created_collection.create_item(body=document_definition)

        for pageSize in [1, 100]:
            # verify iterator
            query_iterable = created_collection.query_items_change_feed(
                continuation=continuation2,
                max_item_count=pageSize,
                **filter_param
            )
            it = query_iterable.__iter__()
            expected_ids = 'doc2.doc3.'
            if "partition_key" in filter_param:
                expected_ids = 'doc2.'
            actual_ids = ''
            for item in it:
                actual_ids += item['id'] + '.'
            assert actual_ids == expected_ids

            # verify by_page
            # the options is not copied, therefore it need to be restored
            query_iterable = created_collection.query_items_change_feed(
                continuation=continuation2,
                max_item_count=pageSize,
                **filter_param
            )
            count = 0
            expected_count = 2
            if "partition_key" in filter_param:
                expected_count = 1
            all_fetched_res = []
            for page in query_iterable.by_page():
                fetched_res = list(page)
                assert len(fetched_res) == min(pageSize, expected_count - count)
                count += len(fetched_res)
                all_fetched_res.extend(fetched_res)

            actual_ids = ''
            for item in all_fetched_res:
                actual_ids += item['id'] + '.'
            assert actual_ids == expected_ids

        # verify reading change feed from the beginning
        query_iterable = created_collection.query_items_change_feed(
            is_start_from_beginning=True,
            **filter_param
        )
        expected_ids = 'doc1.doc2.doc3.'
        if "partition_key" in filter_param:
            expected_ids = 'doc1.doc2.'
        pages = query_iterable.by_page()
        it = (item for page in pages for item in page)
        actual_ids = ''
        for item in it:
            actual_ids += item['id'] + '.'
        assert actual_ids == expected_ids
        assert 'etag' in created_collection.client_connection.last_response_headers
        continuation3 = pages.continuation_token
        assert continuation3

        # verify reading empty change feed
        query_iterable = created_collection.query_items_change_feed(
            continuation=continuation3,
            is_start_from_beginning=True,
            **filter_param
        )
        iter_list = list(query_iterable)
        assert len(iter_list) == 0
        setup["key_db"].delete_container(created_collection.id)
