# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid
import os
from asyncio import sleep
from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from _pytest.outcomes import fail

import azure.cosmos.exceptions as exceptions
import test_config
from azure.cosmos.aio import CosmosClient
from azure.cosmos.partition_key import PartitionKey


@pytest_asyncio.fixture()
async def setup():
    use_multiple_write_locations = False
    if os.environ.get("AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER", "False") == "True":
        use_multiple_write_locations = True
    config = test_config.TestConfig()
    if config.masterKey == '[YOUR_KEY_HERE]' or config.host == '[YOUR_ENDPOINT_HERE]':
        raise Exception(
            "You must specify your Azure Cosmos account values for "
            "'masterKey' and 'host' at the top of this class to run the "
            "tests.")
    # Key-auth client for control-plane operations (create/delete containers)
    key_client = CosmosClient(config.host, config.masterKey, multiple_write_locations=use_multiple_write_locations)
    await key_client.__aenter__()
    key_db = key_client.get_database_client(config.TEST_DATABASE_ID)

    # Data-plane client (AAD when configured, else key auth)
    data_client = test_config.TestConfig.create_data_client_async()
    await data_client.__aenter__()
    data_db = data_client.get_database_client(config.TEST_DATABASE_ID)

    yield {
        "key_db": key_db,
        "data_db": data_db,
        "is_emulator": config.is_emulator
    }
    await data_client.close()
    await key_client.close()

def round_time():
    utc_now = datetime.now(timezone.utc)
    return utc_now - timedelta(microseconds=utc_now.microsecond)

@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosQuery
@pytest.mark.cosmosAADCircuitBreaker
@pytest.mark.asyncio
@pytest.mark.usefixtures("setup")
class TestChangeFeedAsync:
    """Test to ensure escaping of non-ascii characters from partition key"""


    async def test_get_feed_ranges(self, setup):
        created_collection_ref = await setup["key_db"].create_container("get_feed_ranges_" + str(uuid.uuid4()),
                                                              PartitionKey(path="/pk"))
        created_collection = setup["data_db"].get_container_client(created_collection_ref.id)
        result = [feed_range async for feed_range in created_collection.read_feed_ranges()]
        assert len(result) == 1

    @pytest.mark.parametrize("change_feed_filter_param", ["partitionKey", "partitionKeyRangeId", "feedRange"])
    async def test_query_change_feed_with_different_filter_async(self, change_feed_filter_param, setup):

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
            fail("No Etag or etag found in last response headers")

        # Read change feed from beginning should return an empty list
        query_iterable = created_collection.query_items_change_feed(
            is_start_from_beginning=True,
            **filter_param
        )
        iter_list = [item async for item in query_iterable]
        assert len(iter_list) == 0
        if 'Etag' in created_collection.client_connection.last_response_headers:
            continuation1 = created_collection.client_connection.last_response_headers['Etag']
        elif 'etag' in created_collection.client_connection.last_response_headers:
            continuation1 = created_collection.client_connection.last_response_headers['etag']
        else:
            fail("No Etag or etag found in last response headers")
        assert continuation1 != ''

        # Create a document. Read change feed should return be able to read that document
        document_definition = {'pk': 'pk', 'id': 'doc1'}
        await created_collection.create_item(body=document_definition)
        query_iterable = created_collection.query_items_change_feed(
            is_start_from_beginning=True,
            **filter_param
        )
        iter_list = [item async for item in query_iterable]
        assert len(iter_list) == 1
        assert iter_list[0]['id'] == 'doc1'
        if 'Etag' in created_collection.client_connection.last_response_headers:
            continuation2 = created_collection.client_connection.last_response_headers['Etag']
        elif 'etag' in created_collection.client_connection.last_response_headers:
            continuation2 = created_collection.client_connection.last_response_headers['etag']
        else:
            fail("No Etag or etag found in last response headers")
        assert continuation2 != ''
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
        it = query_iterable.__aiter__()
        expected_ids = 'doc1.doc2.doc3.'
        if "partition_key" in filter_param:
            expected_ids = 'doc1.doc2.'
        actual_ids = ''
        async for item in it:
            actual_ids += item['id'] + '.'
        assert actual_ids == expected_ids
        if 'Etag' in created_collection.client_connection.last_response_headers:
            continuation3 = created_collection.client_connection.last_response_headers['Etag']
        elif 'etag' in created_collection.client_connection.last_response_headers:
            continuation3 = created_collection.client_connection.last_response_headers['etag']
        else:
            fail("No Etag or etag found in last response headers")

        # verify reading empty change feed
        query_iterable = created_collection.query_items_change_feed(
            continuation=continuation3,
            is_start_from_beginning=True,
            **filter_param
        )
        iter_list = [item async for item in query_iterable]
        assert len(iter_list) == 0

        await setup["key_db"].delete_container(created_collection_ref.id)

    @pytest.mark.asyncio
    async def test_query_change_feed_with_start_time(self, setup):
        container_id = "query_change_feed_start_time_test_" + str(uuid.uuid4())
        created_collection_ref = await setup["key_db"].create_container(
            container_id,
            PartitionKey(path="/pk")
        )
        created_collection = setup["data_db"].get_container_client(created_collection_ref.id)
        batchSize = 50

        async def create_random_items(container, batch_size):
            created_ids = set()
            for _ in range(batch_size):
                # Generate a Random partition key
                partition_key = 'pk' + str(uuid.uuid4())

                # Generate a random item
                item = {
                    'id': 'item' + str(uuid.uuid4()),
                    'pk': partition_key,
                    'content': 'This is some random content',
                }

                try:
                    # Create the item in the container
                    await container.upsert_item(item)
                    created_ids.add(item['id'])
                except exceptions.CosmosHttpResponseError as e:
                    pytest.fail(str(e))
            return created_ids

        try:
            # Create first batch of random items
            first_batch_ids = await create_random_items(created_collection, batchSize)

            # wait for 1 second and record the time, then wait another second
            await sleep(1)
            start_time = round_time()
            # Use an equivalent instant in a non-UTC timezone to validate SDK timezone normalization.
            not_utc_time = start_time.astimezone(timezone(timedelta(hours=5, minutes=30)))
            await sleep(1)

            # now create another batch of items
            second_batch_ids = await create_random_items(created_collection, batchSize)

            # now query change feed based on start time
            change_feed_iter = [i async for i in created_collection.query_items_change_feed(start_time=start_time)]
            change_feed_ids = {item['id'] for item in change_feed_iter}

            # start_time is second-granular; boundary writes from the first batch can be included.
            assert second_batch_ids.issubset(change_feed_ids)
            assert change_feed_ids.issubset(first_batch_ids.union(second_batch_ids))

            # negative test: pass in a valid time in the future
            future_time = start_time + timedelta(hours=1)
            change_feed_iter = [i async for i in created_collection.query_items_change_feed(start_time=future_time)]
            # A future time should return 0
            assert len(change_feed_iter) == 0

            # test a date that is not utc, will be converted to utc by sdk
            change_feed_iter = [i async for i in created_collection.query_items_change_feed(start_time=not_utc_time)]
            change_feed_non_utc_ids = {item['id'] for item in change_feed_iter}
            assert change_feed_non_utc_ids == change_feed_ids
        finally:
            await setup["key_db"].delete_container(created_collection_ref.id)

    async def test_query_change_feed_with_multi_partition_async(self, setup):
        created_collection_ref = await setup["key_db"].create_container("change_feed_test_" + str(uuid.uuid4()),
                                                              PartitionKey(path="/pk"),
                                                              offer_throughput=11000)
        created_collection = setup["data_db"].get_container_client(created_collection_ref.id)

        # create one doc and make sure change feed query can return the document
        new_documents = [
            {'pk': 'pk', 'id': 'doc1'},
            {'pk': 'pk2', 'id': 'doc2'},
            {'pk': 'pk3', 'id': 'doc3'},
            {'pk': 'pk4', 'id': 'doc4'}]
        expected_ids = ['doc1', 'doc2', 'doc3', 'doc4']

        for document in new_documents:
            await created_collection.create_item(body=document)

        query_iterable = created_collection.query_items_change_feed(start_time="Beginning")
        it = query_iterable.__aiter__()
        actual_ids = []
        async for item in it:
            actual_ids.append(item['id'])

        assert actual_ids == expected_ids

if __name__ == '__main__':
    unittest.main()

