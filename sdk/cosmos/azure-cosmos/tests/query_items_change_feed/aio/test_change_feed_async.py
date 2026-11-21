# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Change-feed filter assertions using Rust-backed clients and SDK continuation tokens."""

import uuid

import pytest
from azure.cosmos.partition_key import PartitionKey
import pytest_asyncio
from azure.cosmos.aio import CosmosClient
from config.clients import create_data_client_async
from config.settings import TestSettings, unique_database_id


@pytest_asyncio.fixture()
async def setup():
    database_id = unique_database_id("query-change-feed-filters-async")
    # Closed decision: Rust owns endpoint discovery and multi-write routing
    #. Rust-backed clients reject the
    # original's multiple_write_locations argument (even False), so it is omitted.
    # Key-auth client for control-plane operations (create/delete containers)
    key_client = CosmosClient(TestSettings.host, TestSettings.masterKey, _backend="rust")
    await key_client.__aenter__()
    # Data-plane client (AAD when configured, else key auth)
    data_client = create_data_client_async(_backend="rust")
    await data_client.__aenter__()
    try:
        key_db = await key_client.create_database(database_id)
        try:
            yield {
                "key_db": key_db,
                "data_db": data_client.get_database_client(database_id),
                "is_emulator": TestSettings.is_emulator
            }
        finally:
            await key_client.delete_database(database_id)
    finally:
        await data_client.close()
        await key_client.close()



@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosQuery
@pytest.mark.cosmosAADCircuitBreaker
@pytest.mark.asyncio
@pytest.mark.usefixtures("setup")
class TestChangeFeedAsync:
    @pytest.mark.parametrize("change_feed_filter_param", ["partitionKey", "partitionKeyRangeId", "feedRange"])
    async def test_query_change_feed_with_different_filter_async_rust(self, change_feed_filter_param, setup):
        # Source: tests/test_change_feed_async.py::TestChangeFeedAsync.test_query_change_feed_with_different_filter_async
        # Core test: read the change feed scoped by each filter type (partition key /
        # range id / feed range), from current, from beginning, and from a continuation
        # token, and check new items show up and paging works. Without it, any of these
        # paths could silently return wrong or missing changes.

        created_collection_ref = await setup["key_db"].create_container(
            "change_feed_test_" + str(uuid.uuid4()),
            PartitionKey(path="/pk"))
        created_collection = setup["data_db"].get_container_client(created_collection_ref.id)

        if change_feed_filter_param == "partitionKey":
            filter_param = {"partition_key": "pk"}
        elif change_feed_filter_param == "partitionKeyRangeId":
            filter_param = {"partition_key_range_id": "0"}
        elif change_feed_filter_param == "feedRange":
            feed_ranges = [feed_range async for feed_range in created_collection.read_feed_ranges()]
            assert len(feed_ranges) == 1
            filter_param = {"feed_range": feed_ranges[0]}
        else:
            filter_param = None

        # Read change feed without passing any options
        query_iterable = created_collection.query_items_change_feed()
        iter_list = [item async for item in query_iterable]
        assert len(iter_list) == 0

        # Read change feed from current should return an empty list
        query_iterable = created_collection.query_items_change_feed(**filter_param)
        iter_list = [item async for item in query_iterable]
        assert len(iter_list) == 0
        if 'Etag' in created_collection.client_connection.last_response_headers:
            assert created_collection.client_connection.last_response_headers['Etag'] != ''
        elif 'etag' in created_collection.client_connection.last_response_headers:
            assert created_collection.client_connection.last_response_headers['etag'] != ''
        else:
            pytest.fail("No Etag or etag found in last response headers")

        # Read change feed from beginning should return an empty list
        query_iterable = created_collection.query_items_change_feed(
            is_start_from_beginning=True,
            **filter_param
        )
        pages = query_iterable.by_page()
        iter_list = [item async for page in pages async for item in page]
        assert len(iter_list) == 0
        continuation1 = pages.continuation_token
        assert continuation1

        # Create a document. Read change feed should return be able to read that document
        document_definition = {'pk': 'pk', 'id': 'doc1'}
        await created_collection.create_item(body=document_definition)
        query_iterable = created_collection.query_items_change_feed(
            is_start_from_beginning=True,
            **filter_param
        )
        pages = query_iterable.by_page()
        iter_list = [item async for page in pages async for item in page]
        assert len(iter_list) == 1
        assert iter_list[0]['id'] == 'doc1'
        continuation2 = pages.continuation_token
        assert continuation2
        assert continuation2 != continuation1

        # Create two new documents. Verify that change feed contains the 2 new documents
        # with page size 1 and page size 100
        document_definition = {'pk': 'pk', 'id': 'doc2'}
        await created_collection.create_item(body=document_definition)
        document_definition = {'pk': 'pk3', 'id': 'doc3'}
        await created_collection.create_item(body=document_definition)

        for pageSize in [2, 100]:
            # verify iterator
            query_iterable = created_collection.query_items_change_feed(
                continuation=continuation2,
                max_item_count=pageSize,
                **filter_param)
            it = query_iterable.__aiter__()
            expected_ids = 'doc2.doc3.'
            if "partition_key" in filter_param:
                expected_ids = 'doc2.'
            actual_ids = ''
            async for item in it:
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
            pages = query_iterable.by_page()
            async for items in await pages.__anext__():
                count += 1
                all_fetched_res.append(items)
            assert count == expected_count

            actual_ids = ''
            for item in all_fetched_res:
                actual_ids += item['id'] + '.'
            assert actual_ids == expected_ids

        # verify reading change feed from the beginning
        query_iterable = created_collection.query_items_change_feed(
            is_start_from_beginning=True,
            **filter_param
        )
        pages = query_iterable.by_page()
        it = (item async for page in pages async for item in page)
        expected_ids = 'doc1.doc2.doc3.'
        if "partition_key" in filter_param:
            expected_ids = 'doc1.doc2.'
        actual_ids = ''
        async for item in it:
            actual_ids += item['id'] + '.'
        assert actual_ids == expected_ids
        continuation3 = pages.continuation_token
        assert continuation3

        # verify reading empty change feed
        query_iterable = created_collection.query_items_change_feed(
            continuation=continuation3,
            is_start_from_beginning=True,
            **filter_param
        )
        iter_list = [item async for item in query_iterable]
        assert len(iter_list) == 0

        await setup["key_db"].delete_container(created_collection_ref.id)
