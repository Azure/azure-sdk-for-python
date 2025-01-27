# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid
from datetime import datetime, timedelta, timezone
from time import sleep

import pytest
from _pytest.outcomes import fail

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
import test_config
from azure.cosmos.partition_key import PartitionKey
from azure.cosmos._change_feed.change_feed_state import ChangeFeedStateV2

ID = 'id'
CURRENT = 'current'
PREVIOUS = 'previous'
METADATA = 'metadata'
OPERATION_TYPE = 'operationType'
CREATE = 'create'
DELETE = 'delete'
E_TAG = 'etag'

@pytest.fixture(scope="class")
def setup():
    config = test_config.TestConfig()
    if (config.masterKey == '[YOUR_KEY_HERE]' or
            config.host == '[YOUR_ENDPOINT_HERE]'):
        raise Exception(
            "You must specify your Azure Cosmos account values for "
            "'masterKey' and 'host' at the top of this class to run the "
            "tests.")
    test_client = cosmos_client.CosmosClient(config.host, config.masterKey),
    return {
        "created_db": test_client[0].get_database_client(config.TEST_DATABASE_ID),
        "is_emulator": config.is_emulator
    }

def round_time():
    utc_now = datetime.now(timezone.utc)
    return utc_now - timedelta(microseconds=utc_now.microsecond)

def assert_change_feed(expected, actual):
    if len(actual) == 0:
        assert len(expected) == len(actual)
        return

    #TODO: remove this if we can add flag to get 'previous' always
    for item in actual:
        if METADATA in item and item[METADATA][OPERATION_TYPE] == DELETE:
            if ID in item[METADATA]:
                item[PREVIOUS] = {ID: item[METADATA][ID]}

    # Sort actual by operation_type and id
    actual = sorted(actual, key=lambda k: (k[METADATA][OPERATION_TYPE], k[CURRENT][ID]) if k[METADATA][OPERATION_TYPE] == CREATE else (k[METADATA][OPERATION_TYPE], k[PREVIOUS][ID]))

    for expected_change_feed, actual_change_feed in zip(expected, actual):
        for expected_type, expected_data in expected_change_feed.items():
            assert expected_type in actual_change_feed
            actual_data = actual_change_feed[expected_type]
            for key, value in expected_data.items():
                assert key in actual_data
                assert expected_data[key] == actual_data[key]

@pytest.mark.cosmosEmulator
@pytest.mark.unittest
@pytest.mark.usefixtures("setup")
class TestChangeFeed:
    """Test to ensure escaping of non-ascii characters from partition key"""

    def test_get_feed_ranges(self, setup):
        created_collection = setup["created_db"].create_container("get_feed_ranges_" + str(uuid.uuid4()),
                                                              PartitionKey(path="/pk"))
        result = list(created_collection.read_feed_ranges())
        assert len(result) == 1

    @pytest.mark.parametrize("change_feed_filter_param", ["partitionKey", "partitionKeyRangeId", "feedRange"])
    def test_query_change_feed_with_different_filter(self, change_feed_filter_param, setup):
        created_collection = setup["created_db"].create_container("change_feed_test_" + str(uuid.uuid4()),
                                                              PartitionKey(path="/pk"))

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
        iter_list = list(query_iterable)
        assert len(iter_list) == 0
        assert 'etag' in created_collection.client_connection.last_response_headers
        continuation1 = created_collection.client_connection.last_response_headers['etag']
        assert continuation1 != ''

        # Create a document. Read change feed should return be able to read that document
        document_definition = {'pk': 'pk', 'id': 'doc1'}
        created_collection.create_item(body=document_definition)
        query_iterable = created_collection.query_items_change_feed(
            is_start_from_beginning=True,
            **filter_param
        )
        iter_list = list(query_iterable)
        assert len(iter_list) == 1
        assert iter_list[0]['id'] == 'doc1'
        assert 'etag' in created_collection.client_connection.last_response_headers
        continuation2 = created_collection.client_connection.last_response_headers['etag']
        assert continuation2 != ''
        assert continuation2 != continuation1

        # Create two new documents. Verify that change feed contains the 2 new documents
        # with page size 1 and page size 100
        document_definition = {'pk': 'pk', 'id': 'doc2'}
        created_collection.create_item(body=document_definition)
        document_definition = {'pk': 'pk', 'id': 'doc3'}
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
        expected_ids = ['doc1', 'doc2', 'doc3']
        it = query_iterable.__iter__()
        for i in range(0, len(expected_ids)):
            doc = next(it)
            assert doc['id'] == expected_ids[i]
        assert 'etag' in created_collection.client_connection.last_response_headers
        continuation3 = created_collection.client_connection.last_response_headers['etag']

        # verify reading empty change feed
        query_iterable = created_collection.query_items_change_feed(
            continuation=continuation3,
            is_start_from_beginning=True,
            **filter_param
        )
        iter_list = list(query_iterable)
        assert len(iter_list) == 0
        setup["created_db"].delete_container(created_collection.id)

    def test_query_change_feed_with_start_time(self, setup):
        created_collection = setup["created_db"].create_container_if_not_exists("query_change_feed_start_time_test",
                                                                            PartitionKey(path="/pk"))
        batchSize = 50

        def create_random_items(container, batch_size):
            for _ in range(batch_size):
                # Generate a Random partition key
                partition_key = 'pk' + str(uuid.uuid4())

                # Generate a random item
                item = {
                    'id': 'item' + str(uuid.uuid4()),
                    'partitionKey': partition_key,
                    'content': 'This is some random content',
                }

                try:
                    # Create the item in the container
                    container.upsert_item(item)
                except exceptions.CosmosHttpResponseError as e:
                    fail(e)

        # Create first batch of random items
        create_random_items(created_collection, batchSize)

        # wait for 1 second and record the time, then wait another second
        sleep(1)
        start_time = round_time()
        not_utc_time = datetime.now()
        sleep(1)

        # now create another batch of items
        create_random_items(created_collection, batchSize)

        # now query change feed based on start time
        change_feed_iter = list(created_collection.query_items_change_feed(start_time=start_time))
        totalCount = len(change_feed_iter)

        # now check if the number of items that were changed match the batch size
        assert totalCount == batchSize

        # negative test: pass in a valid time in the future
        future_time = start_time + timedelta(hours=1)
        change_feed_iter = list(created_collection.query_items_change_feed(start_time=future_time))
        totalCount = len(change_feed_iter)
        # A future time should return 0
        assert totalCount == 0

        # test a date that is not utc, will be converted to utc by sdk
        change_feed_iter = list(created_collection.query_items_change_feed(start_time=not_utc_time))
        totalCount = len(change_feed_iter)
        # Should equal batch size
        assert totalCount == batchSize

        setup["created_db"].delete_container(created_collection.id)

    def test_query_change_feed_with_multi_partition(self, setup):
        created_collection = setup["created_db"].create_container("change_feed_test_" + str(uuid.uuid4()),
                                                              PartitionKey(path="/pk"),
                                                              offer_throughput=11000)

        # create one doc and make sure change feed query can return the document
        new_documents = [
            {'pk': 'pk', 'id': 'doc1'},
            {'pk': 'pk2', 'id': 'doc2'},
            {'pk': 'pk3', 'id': 'doc3'},
            {'pk': 'pk4', 'id': 'doc4'}]
        expected_ids = ['doc1', 'doc2', 'doc3', 'doc4']

        for document in new_documents:
            created_collection.create_item(body=document)

        query_iterable = created_collection.query_items_change_feed(start_time="Beginning")
        it = query_iterable.__iter__()
        actual_ids = []
        for item in it:
            actual_ids.append(item['id'])

        assert actual_ids == expected_ids

    def test_query_change_feed_with_all_versions_and_deletes(self, setup):
        partition_key = 'pk'
        # 'retentionDuration' was required to enable `ALL_VERSIONS_AND_DELETES` for Emulator testing
        change_feed_policy = {"retentionDuration": 10} if setup["is_emulator"] else None
        created_collection = setup["created_db"].create_container("change_feed_test_" + str(uuid.uuid4()),
                                                                  PartitionKey(path=f"/{partition_key}"),
                                                                  change_feed_policy=change_feed_policy)
        mode = 'AllVersionsAndDeletes'

        ## Test Change Feed with empty collection(Save the continuation token)
        query_iterable = created_collection.query_items_change_feed(
            mode=mode,
        )
        expected_change_feeds = []
        actual_change_feeds = list(query_iterable)
        cont_token1 = created_collection.client_connection.last_response_headers[E_TAG]
        assert_change_feed(expected_change_feeds, actual_change_feeds)

        ## Test change_feed for created items from cont_token1 (Save the new continuation token)
        new_documents = [{partition_key: f'pk{i}', ID: f'doc{i}'} for i in range(4)]
        created_items = []
        for document in new_documents:
            created_item = created_collection.create_item(body=document)
            created_items.append(created_item)
        query_iterable = created_collection.query_items_change_feed(
            continuation=cont_token1,
            mode=mode,
        )

        expected_change_feeds = [{CURRENT: {ID: f'doc{i}'}, METADATA: {OPERATION_TYPE: CREATE}} for i in range(4)]
        actual_change_feeds = list(query_iterable)
        cont_token2 = created_collection.client_connection.last_response_headers['etag']
        assert_change_feed(expected_change_feeds, actual_change_feeds)

        ## Test change_feed for deleted items
        for item in created_items:
            created_collection.delete_item(item=item, partition_key=item['pk'])
        query_iterable = created_collection.query_items_change_feed(
            continuation=cont_token2,
            mode=mode,
        )

        expected_change_feeds = [{CURRENT: {}, PREVIOUS: {ID: f'doc{i}'}, METADATA: {OPERATION_TYPE: DELETE}} for i in range(4)]
        actual_change_feeds = list(query_iterable)
        assert_change_feed(expected_change_feeds, actual_change_feeds)

        ## Test change_feed for created/deleted items
        query_iterable = created_collection.query_items_change_feed(
            continuation=cont_token1,
            mode = mode
        )

        expected_change_feeds = [{CURRENT: {ID: f'doc{i}'}, METADATA: {OPERATION_TYPE: CREATE}} for i in range(4)]\
                                + [{CURRENT: {}, PREVIOUS: {ID: f'doc{i}'}, METADATA: {OPERATION_TYPE: DELETE}} for i in range(4)]
        actual_change_feeds = list(query_iterable)
        assert_change_feed(expected_change_feeds, actual_change_feeds)

    def test_query_change_feed_with_errors(self, setup):
        created_collection = setup["created_db"].create_container("change_feed_test_" + str(uuid.uuid4()),
                                                                  PartitionKey(path="/pk"))
        mode = 'AllVersionsAndDeletes'

        # Error if invalid mode was used
        with pytest.raises(ValueError) as e:
            created_collection.query_items_change_feed(
                mode="test_invalid_mode",
            )
        assert str(e.value) == "Invalid mode was used: 'test_invalid_mode'. Supported modes are ['LatestVersion', 'AllVersionsAndDeletes']."

        # Error if partition_key_range_id was used with FULL_FIDELITY_FEED
        with pytest.raises(ValueError) as e:
            created_collection.query_items_change_feed(
                partition_key_range_id="TestPartitionKeyRangeId",
                mode=mode,
            )
        assert str(e.value) == "'AllVersionsAndDeletes' mode is not supported if 'partition_key_range_id' was used. Please use 'feed_range' instead."

        # Error if is_start_from_beginning was in invalid type
        with pytest.raises(TypeError) as e:
            created_collection.query_items_change_feed(
                is_start_from_beginning="Now",
            )
        assert str(e.value) == "'is_start_from_beginning' must be 'bool' type, but given 'str'."

        # Error if is_start_from_beginning was used with FULL_FIDELITY_FEED
        with pytest.raises(ValueError) as e:
            created_collection.query_items_change_feed(
                is_start_from_beginning=True,
                mode=mode,
            )
        assert str(e.value) == "'AllVersionsAndDeletes' mode is only supported if 'is_start_from_beginning' is 'False'. Please use 'is_start_from_beginning=False' or 'continuation' instead."

        # Error if 'is_start_from_beginning' was used with 'start_time'
        with pytest.raises(ValueError) as e:
            created_collection.query_items_change_feed(
                is_start_from_beginning=True,
                start_time="Now",
            )
        assert str(e.value) == "'is_start_from_beginning' and 'start_time' are exclusive, please only set one of them."

        # Error if 'start_time' was invalid value
        invalid_time = "Invalid value"
        # TODO: previously it is throwing AttributeError, now has changed into ValueError, is it breaking change?
        with pytest.raises(ValueError) as e:
            created_collection.query_items_change_feed(start_time=invalid_time)
        assert str(e.value) == "'start_time' must be either 'Now' or 'Beginning', but given 'Invalid value'."

        # Error if 'start_time' was invalid type
        invalid_time = 1.2
        with pytest.raises(AttributeError) as e:
            created_collection.query_items_change_feed(start_time=invalid_time)
        assert str(e.value) == "'float' object has no attribute 'lower'"

        # Error if start_time was used with FULL_FIDELITY_FEED
        with pytest.raises(ValueError) as e:
            created_collection.query_items_change_feed(
                start_time=round_time(),
                mode=mode,
            )
        assert str(e.value) == "'AllVersionsAndDeletes' mode is only supported if 'start_time' is 'Now'. Please use 'start_time=\"Now\"' or 'continuation' instead."

        # Error if too many positional arguments
        with pytest.raises(TypeError) as e:
            created_collection.query_items_change_feed(
                "partition_key_range_id",
                False,
                "continuation",
                10,
                "extra_argument",
            )
        assert str(e.value) == "'query_items_change_feed()' takes 4 positional arguments but 5 were given."

        # Error if arguments are in both positional and keyword arguments list
        with pytest.raises(TypeError) as e:
            created_collection.query_items_change_feed(
                "partition_key_range_id",
                False,
                "continuation",
                10,
                continuation="123",
            )
        assert str(e.value) == "'query_items_change_feed()' got multiple values for argument 'continuation'."

        # Error if continuation is missing 'mode'
        with pytest.raises(ValueError) as e:
            continuation_json = {
                "containerRid": "",
                "startFrom": {'Type': 'Now'},
                "continuation": {'Range': {'isMaxInclusive': False, 'isMinInclusive': True, 'max': 'FF', 'min': ''}, 'continuation': [{'range': {'isMaxInclusive': False, 'isMinInclusive': True, 'max': '1FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF', 'min': ''}, 'token': '"1"'}, {'range': {'isMaxInclusive': False, 'isMinInclusive': True, 'max': 'FF', 'min': '1FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF'}, 'token': '"1"'}], 'rid': 'ksMfAMrReEg=', 'v': 'v2'},
            }
            ChangeFeedStateV2.from_continuation(
                container_link="",
                container_rid="",
                continuation_json=continuation_json,
            )
        assert str(e.value) == "Invalid continuation: [Missing mode]"

if __name__ == "__main__":
    unittest.main()
