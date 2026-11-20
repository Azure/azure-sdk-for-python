# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import asyncio
import time
import unittest
import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
import pytest_asyncio

import test_config
from azure.cosmos.aio import CosmosClient
from azure.cosmos._change_feed.aio.change_feed_iterable import ChangeFeedIterable
from azure.cosmos.partition_key import PartitionKey

ID = 'id'
CURRENT = 'current'
PREVIOUS = 'previous'
METADATA = 'metadata'
OPERATION_TYPE = 'operationType'
CREATE = 'create'
REPLACE = 'replace'
DELETE = 'delete'
E_TAG = 'etag'
VERSION = 'version'
TTL_SECONDS = 5
TTL_TEST_TIMEOUT_SECONDS = 250

@pytest_asyncio.fixture()
async def setup():
    config = test_config.TestConfig()
    if config.masterKey == '[YOUR_KEY_HERE]' or config.host == '[YOUR_ENDPOINT_HERE]':
        raise Exception(
            "You must specify your Azure Cosmos account values for "
            "'masterKey' and 'host' at the top of this class to run the "
            "tests.")
    # Key-auth client for control-plane (container create/delete)
    key_client = CosmosClient(config.host, config.masterKey)
    await key_client.__aenter__()
    key_db = key_client.get_database_client(config.TEST_DATABASE_ID)
    # AAD data client for data-plane operations
    data_client = config.create_data_client_async()
    await data_client.__aenter__()
    data_db = data_client.get_database_client(config.TEST_DATABASE_ID)

    yield {
        "key_db": key_db,
        "created_db": data_db,
        "is_emulator": config.is_emulator
    }
    await data_client.close()
    await key_client.close()

def round_time():
    utc_now = datetime.now(timezone.utc)
    return utc_now - timedelta(microseconds=utc_now.microsecond)


def _is_all_versions_and_deletes_not_enabled(error: Exception) -> bool:
    if not isinstance(error, Exception):
        return False
    if getattr(error, "status_code", None) != 400:
        return False
    message = str(error)
    return (
        "All Versions and Deletes" in message
        and "must be enabled" in message
    )

async def assert_change_feed(expected, actual):
    assert len(expected) == len(actual)

    # Delete entries don't have a current item, and previous is optional.
    def sort_key(change):
        return (
            change[METADATA][OPERATION_TYPE],
            change.get(CURRENT, {}).get(ID)
            or change.get(PREVIOUS, {}).get(ID)
            or change[METADATA].get(ID),
        )

    expected = sorted(expected, key=sort_key)
    actual = sorted(actual, key=sort_key)

    for expected_change_feed, actual_change_feed in zip(expected, actual):
        for expected_type, expected_data in expected_change_feed.items():
            assert expected_type in actual_change_feed
            actual_data = actual_change_feed[expected_type]
            for key, value in expected_data.items():
                assert key in actual_data
                assert expected_data[key] == actual_data[key]


@pytest.mark.cosmosEmulator
@pytest.mark.unittest
@pytest.mark.asyncio
class TestAllVersionsChangeFeedResponseAsync:
    async def test_previous_images_are_preserved_async(self):
        changes = [
            {
                CURRENT: {ID: "item", "pk": "pk", VERSION: 1},
                METADATA: {OPERATION_TYPE: CREATE},
            },
            {
                CURRENT: {ID: "item", "pk": "pk", VERSION: 2},
                PREVIOUS: {ID: "item", "pk": "pk", VERSION: 1, "_etag": "old-etag"},
                METADATA: {OPERATION_TYPE: REPLACE, "previousImageLSN": 1},
            },
            {
                CURRENT: {},
                PREVIOUS: {ID: "item", "pk": "pk", VERSION: 2, "_etag": "new-etag"},
                METADATA: {OPERATION_TYPE: DELETE, ID: "item", "timeToLiveExpired": False},
            },
            {
                CURRENT: {},
                METADATA: {OPERATION_TYPE: DELETE, ID: "expired", "timeToLiveExpired": True},
            },
        ]
        iterable = object.__new__(ChangeFeedIterable)
        iterable._client = SimpleNamespace(last_response_headers={E_TAG: '"continuation"'})

        continuation, unpacked = await iterable._unpack(changes)

        assert continuation == '"continuation"'
        assert unpacked is changes
        assert unpacked[1][PREVIOUS][VERSION] == 1
        assert unpacked[2][PREVIOUS][VERSION] == 2
        assert PREVIOUS not in unpacked[3]


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
@pytest.mark.asyncio
@pytest.mark.usefixtures("setup")
class TestAllVersionsChangeFeedAsync:
    """Test to verify All Versions And Delete change feed behavior"""

    async def test_query_change_feed_all_versions_and_deletes_async(self, setup):
        partition_key = 'pk'
        # 'retentionDuration' was required to enable `ALL_VERSIONS_AND_DELETES` for Emulator testing
        change_feed_policy = {"retentionDuration": 10} if setup["is_emulator"] else None
        cid = "change_feed_test_" + str(uuid.uuid4())
        # Container creation is control-plane and uses key-auth key_db.
        await setup["key_db"].create_container(cid,
                                                  PartitionKey(path=f"/{partition_key}"),
                                                  change_feed_policy=change_feed_policy)
        created_collection = setup["created_db"].get_container_client(cid)

        mode = 'AllVersionsAndDeletes'

        ## Test Change Feed with empty collection(Save the continuation token)
        try:
            query_iterable = created_collection.query_items_change_feed(
                mode=mode,
            )
            expected_change_feeds = []
            actual_change_feeds = [item async for item in query_iterable]
        except Exception as e:
            if _is_all_versions_and_deletes_not_enabled(e):
                pytest.skip("Change Feed 'All Versions and Deletes' capability is not enabled on this account.")
            raise
        cont_token1 = created_collection.client_connection.last_response_headers[E_TAG]
        await assert_change_feed(expected_change_feeds, actual_change_feeds)

        ## Test change_feed for created items from cont_token1 (Save the new continuation token)
        new_documents = [{partition_key: f'pk{i}', ID: f'doc{i}'} for i in range(4)]
        created_items = []
        for document in new_documents:
            created_item = await created_collection.create_item(body=document)
            created_items.append(created_item)
        query_iterable = created_collection.query_items_change_feed(
            continuation=cont_token1,
            mode=mode,
        )

        expected_change_feeds = [{CURRENT: {ID: f'doc{i}'}, METADATA: {OPERATION_TYPE: CREATE}} for i in range(4)]
        actual_change_feeds = [item async for item in query_iterable]
        cont_token2 = created_collection.client_connection.last_response_headers['etag']
        await assert_change_feed(expected_change_feeds, actual_change_feeds)

        ## Test change_feed for replaced items
        replaced_items = []
        for item in created_items:
            replacement = {partition_key: item[partition_key], ID: item[ID], VERSION: 2}
            replaced_items.append(await created_collection.replace_item(item=item[ID], body=replacement))
        query_iterable = created_collection.query_items_change_feed(
            continuation=cont_token2,
            mode=mode,
        )

        expected_change_feeds = [
            {CURRENT: {ID: f'doc{i}', VERSION: 2}, METADATA: {OPERATION_TYPE: REPLACE}}
            for i in range(4)
        ]
        actual_change_feeds = [item async for item in query_iterable]
        cont_token3 = created_collection.client_connection.last_response_headers[E_TAG]
        await assert_change_feed(expected_change_feeds, actual_change_feeds)

        ## Test change_feed for deleted items
        for item in replaced_items:
            await created_collection.delete_item(item=item, partition_key=item['pk'])
        query_iterable = created_collection.query_items_change_feed(
            continuation=cont_token3,
            mode=mode,
        )

        expected_change_feeds = []
        for i in range(4):
            expected_change = {
                CURRENT: {},
                METADATA: {OPERATION_TYPE: DELETE, ID: f'doc{i}'},
            }
            if setup["is_emulator"]:
                expected_change[PREVIOUS] = {
                    ID: f'doc{i}',
                    partition_key: f'pk{i}',
                    VERSION: 2,
                }
            expected_change_feeds.append(expected_change)
        actual_change_feeds = [item async for item in query_iterable]
        await assert_change_feed(expected_change_feeds, actual_change_feeds)

        ## Test change_feed for created/replaced/deleted items
        query_iterable = created_collection.query_items_change_feed(
            continuation=cont_token1,
            mode=mode
        )

        expected_change_feeds = [{CURRENT: {ID: f'doc{i}'}, METADATA: {OPERATION_TYPE: CREATE}} for i in range(4)] \
                                + [{CURRENT: {ID: f'doc{i}', VERSION: 2},
                                    METADATA: {OPERATION_TYPE: REPLACE}} for i in range(4)] \
                                + expected_change_feeds
        actual_change_feeds = [item async for item in query_iterable]
        await assert_change_feed(expected_change_feeds, actual_change_feeds)

        query_iterable = created_collection.query_items_change_feed(
            mode = mode,
            partition_key = 'pk1'
        )
        empty_list = [item async for item in query_iterable]
        pk_cont_token = created_collection.client_connection.last_response_headers[E_TAG]
        new_documents = [{partition_key: f'pk{i}', ID: f'doc{i}'} for i in range(4)]
        created_items = []
        for document in new_documents:
            created_item = await created_collection.create_item(body=document)
            created_items.append(created_item)
        query_iterable = created_collection.query_items_change_feed(
            continuation=pk_cont_token,
            mode=mode
        )
        expected_change_feeds = [{CURRENT: {ID: f'doc1'}, METADATA: {OPERATION_TYPE: CREATE}}]
        actual_change_feeds = [item async for item in query_iterable]
        await assert_change_feed(expected_change_feeds, actual_change_feeds)

    @pytest.mark.timeout(TTL_TEST_TIMEOUT_SECONDS + 50)
    async def test_query_change_feed_ttl_delete_async(self, setup):
        if not setup["is_emulator"]:
            pytest.skip("TTL expiration timing is validated only against the emulator.")

        partition_key = 'pk'
        cid = "change_feed_ttl_test_" + str(uuid.uuid4())
        await setup["key_db"].create_container(
            cid,
            PartitionKey(path=f"/{partition_key}"),
            default_ttl=-1,
            change_feed_policy={"retentionDuration": 10},
        )
        created_collection = setup["created_db"].get_container_client(cid)

        initial_feed = created_collection.query_items_change_feed(mode='AllVersionsAndDeletes')
        _ = [item async for item in initial_feed]
        continuation = created_collection.client_connection.last_response_headers[E_TAG]
        await created_collection.create_item(
            body={ID: 'ttl-item', partition_key: 'ttl-pk', 'ttl': TTL_SECONDS}
        )

        ttl_delete = None
        deadline = time.monotonic() + TTL_TEST_TIMEOUT_SECONDS
        while time.monotonic() < deadline:
            changes = [
                item async for item in created_collection.query_items_change_feed(continuation=continuation)
            ]
            continuation = created_collection.client_connection.last_response_headers[E_TAG]
            ttl_delete = next(
                (
                    change for change in changes
                    if change[METADATA][OPERATION_TYPE] == DELETE
                    and change[METADATA].get("timeToLiveExpired") is True
                ),
                None,
            )
            if ttl_delete is not None:
                break
            await asyncio.sleep(1)

        assert ttl_delete is not None, "Timed out waiting for the TTL delete change."
        assert ttl_delete[METADATA][ID] == 'ttl-item'
        assert ttl_delete[METADATA]["partitionKey"] == {partition_key: 'ttl-pk'}
        assert ttl_delete.get(PREVIOUS) is None

    async def test_query_change_feed_all_versions_and_deletes_errors_async(self, setup):
        cid = "change_feed_test_" + str(uuid.uuid4())
        # Container creation is control-plane and uses key-auth key_db.
        await setup["key_db"].create_container(cid, PartitionKey(path="/pk"))
        created_collection = setup["created_db"].get_container_client(cid)
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
                is_start_from_beginning="Now",
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

if __name__ == '__main__':
    unittest.main()
