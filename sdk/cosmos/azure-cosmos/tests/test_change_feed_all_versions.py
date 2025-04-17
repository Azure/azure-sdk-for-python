# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid
from datetime import datetime, timedelta, timezone

import pytest

import azure.cosmos.cosmos_client as cosmos_client
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
class TestChangeAllVersionsFeed:
    """Test to verify All Versions And Delete change feed behavior"""

    def test_query_change_feed_all_versions_and_deletes(self, setup):
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

        query_iterable = created_collection.query_items_change_feed(
            mode = mode,
            partition_key = 'pk1'
        )
        list(query_iterable)
        pk_cont_token = created_collection.client_connection.last_response_headers[E_TAG]
        new_documents = [{partition_key: f'pk{i}', ID: f'doc{i}'} for i in range(4)]
        created_items = []
        for document in new_documents:
            created_item = created_collection.create_item(body=document)
            created_items.append(created_item)
        query_iterable = created_collection.query_items_change_feed(
            continuation=pk_cont_token,
            mode=mode
        )
        expected_change_feeds = [{CURRENT: {ID: f'doc1'}, METADATA: {OPERATION_TYPE: CREATE}}]
        actual_change_feeds = list(query_iterable)
        assert_change_feed(expected_change_feeds, actual_change_feeds)

    def test_query_change_feed_all_versions_and_deletes_errors(self, setup):
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
