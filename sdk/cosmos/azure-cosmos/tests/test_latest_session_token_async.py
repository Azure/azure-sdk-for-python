# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import random
import time
import unittest
import uuid

import pytest

from _split_test_utils import assert_no_stage_failures, snapshot_split_routing_map, split_stage, wait_for_split_ranges_async
import test_config
from azure.cosmos import PartitionKey
from azure.cosmos._change_feed.feed_range_internal import FeedRangeInternalEpk
from azure.cosmos._session_token_helpers import is_compound_session_token, parse_session_token
from azure.cosmos.aio import DatabaseProxy
from azure.cosmos.aio import CosmosClient
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
class TestLatestSessionTokenAsync(unittest.IsolatedAsyncioTestCase):
    """Test for session token helpers"""

    created_db: DatabaseProxy = None
    client: CosmosClient = None
    key_client: CosmosClient = None
    key_database: DatabaseProxy = None
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    configs = test_config.TestConfig
    TEST_DATABASE_ID = configs.TEST_DATABASE_ID

    async def asyncSetUp(self):
        self.key_client, self.key_database, self.client, self.database = (
            test_config.TestConfig.create_test_clients_async(self.TEST_DATABASE_ID))
        await self.key_client.__aenter__()
        self.addAsyncCleanup(self.key_client.close)
        await self.client.__aenter__()
        self.addAsyncCleanup(self.client.close)

    @pytest.mark.timeout(1500)
    async def test_change_feed_session_token_and_read_items_after_split_async(self):
        container_ref = await self.key_database.create_container(
            "test_grouped_partition_split_async_" + str(uuid.uuid4()), PartitionKey(path="/pk"), offer_throughput=400)
        self.addAsyncCleanup(self.key_database.delete_container, container_ref.id)
        container = self.database.get_container_client(container_ref.id)
        key_container_for_split = self.key_database.get_container_client(container.id)

        # Keep continuation and session state separate; routing maps are endpoint-shared.
        change_feed_client = test_config.TestConfig.create_data_client_async()
        self.addAsyncCleanup(change_feed_client.close)
        await change_feed_client.__aenter__()
        created_collection = change_feed_client.get_database_client(self.TEST_DATABASE_ID).get_container_client(
            container_ref.id)
        read_items_client = test_config.TestConfig.create_data_client_async()
        self.addAsyncCleanup(read_items_client.close)
        await read_items_client.__aenter__()
        read_items_container = read_items_client.get_database_client(self.TEST_DATABASE_ID).get_container_client(
            container_ref.id)

        with split_stage("change_feed_before"):
            query_iterable = created_collection.query_items_change_feed(start_time="Beginning")
            iter_list = [item async for item in query_iterable]
            assert len(iter_list) == 0
            continuation = created_collection.client_connection.last_response_headers['etag']
            assert continuation != ''
            document_definition = {'pk': 'pk', 'id': 'doc1'}
            await created_collection.create_item(body=document_definition)
            query_iterable = created_collection.query_items_change_feed(continuation=continuation)
            iter_list = [item async for item in query_iterable]
            assert len(iter_list) == 1
            continuation = created_collection.client_connection.last_response_headers['etag']

        with split_stage("read_items_before"):
            items_to_read = []
            item_ids = []
            for i in range(5):
                doc_id = f"item_split_{i}_{uuid.uuid4()}"
                item_ids.append(doc_id)
                await read_items_container.create_item({'id': doc_id, 'pk': doc_id, 'data': i})
                items_to_read.append((doc_id, doc_id))
            initial_read_items = await read_items_container.read_items(items=items_to_read)
            self.assertEqual(len(initial_read_items), len(items_to_read))

        with split_stage("logical_session_token_before"):
            feed_ranges_and_session_tokens = []
            previous_session_token = ""
            target_pk = 'A1'
            target_feed_range = await container.feed_range_from_partition_key(target_pk)
            target_session_token, previous_session_token = await self.create_items_logical_pk_async(
                container, target_feed_range, previous_session_token, feed_ranges_and_session_tokens)
            session_token = await container.get_latest_session_token(feed_ranges_and_session_tokens, target_feed_range)
            assert session_token == target_session_token

        with split_stage("physical_session_token_before"):
            phys_feed_ranges_and_session_tokens = []
            phys_previous_session_token = ""
            pk_feed_range = await container.feed_range_from_partition_key(target_pk)
            phys_target_session_token, phys_target_feed_range, phys_previous_session_token = await self.create_items_physical_pk_async(
                container, pk_feed_range, phys_previous_session_token, phys_feed_ranges_and_session_tokens)
            phys_session_token = await container.get_latest_session_token(
                phys_feed_ranges_and_session_tokens, phys_target_feed_range)
            assert phys_session_token == phys_target_session_token
            _, pre_split_session_token = parse_session_token(phys_session_token)
            feed_ranges_and_session_tokens.append((target_feed_range, session_token))

        with split_stage("change_feed_checkpoint"):
            # Carry the last writer's token across clients before checkpointing their writes.
            async for _ in created_collection.query_items_change_feed(
                continuation=continuation, session_token=phys_previous_session_token):
                pass
            continuation = created_collection.client_connection.last_response_headers['etag']
            assert continuation != ''

        with split_stage("split_and_convergence"):
            initial_ranges = [r async for r in key_container_for_split.client_connection._ReadPartitionKeyRanges(
                key_container_for_split.container_link)]
            self.assertEqual(len(initial_ranges), 1)
            collection_rid = (await key_container_for_split.read())["_rid"]
            restore_routing_map = snapshot_split_routing_map(container, collection_rid)
            deadline = time.monotonic() + test_config.SPLIT_TIMEOUT
            await test_config.TestConfig.trigger_split_async(key_container_for_split, 11000)
            await wait_for_split_ranges_async(key_container_for_split, initial_ranges[0]["id"], deadline)

        failures = []
        with split_stage("read_items_after", failures):
            restore_routing_map()
            final_read_items = await read_items_container.read_items(items=items_to_read)
            self.assertEqual(len(final_read_items), len(items_to_read))
            final_read_ids = {item['id'] for item in final_read_items}
            self.assertSetEqual(final_read_ids, set(item_ids))

        with split_stage("change_feed_after", failures):
            restore_routing_map()
            new_documents = [{'pk': 'pk2', 'id': 'doc2'}, {'pk': 'pk3', 'id': 'doc3'}, {'pk': 'pk4', 'id': 'doc4'}]
            expected_ids = ['doc2', 'doc3', 'doc4']
            for document in new_documents:
                await created_collection.create_item(body=document)
            query_iterable = created_collection.query_items_change_feed(continuation=continuation)
            actual_ids = [item['id'] async for item in query_iterable]
            assert actual_ids == expected_ids

        with split_stage("logical_session_token_after", failures):
            restore_routing_map()
            target_session_token, _ = await self.create_items_logical_pk_async(
                container, target_feed_range, session_token, feed_ranges_and_session_tokens)
            target_feed_range = await container.feed_range_from_partition_key(target_pk)
            session_token = await container.get_latest_session_token(feed_ranges_and_session_tokens, target_feed_range)
            assert session_token == target_session_token

        with split_stage("physical_session_token_after", failures):
            _, phys_target_feed_range, phys_previous_session_token = await self.create_items_physical_pk_async(
                container, pk_feed_range, phys_session_token, phys_feed_ranges_and_session_tokens)
            phys_session_token = await container.get_latest_session_token(
                phys_feed_ranges_and_session_tokens, phys_target_feed_range)
            pk_range_id, session_token = parse_session_token(phys_session_token)
            assert session_token.global_lsn >= pre_split_session_token.global_lsn
            assert '2' in pk_range_id

        assert_no_stage_failures(failures)

    async def test_latest_session_token_hpk(self):
        # create_container is control-plane and uses key_database (key-auth).
        container_ref = await self.key_database.create_container(
            "test_updated_session_token_hpk" + str(uuid.uuid4()),
            PartitionKey(path=["/state", "/city", "/zipcode"], kind="MultiHash"),
            offer_throughput=400)
        container = self.database.get_container_client(container_ref.id)
        feed_ranges_and_session_tokens = []
        previous_session_token = ""
        pk = ['CA', 'LA1', '90001']
        pk_feed_range = await container.feed_range_from_partition_key(pk)
        target_session_token, target_feed_range, previous_session_token = await self.create_items_physical_pk_async(container,
                                                                                                                     pk_feed_range,
                                                                                                                     previous_session_token,
                                                                                                                     feed_ranges_and_session_tokens,
                                                                                                                     True)

        session_token = await container.get_latest_session_token(feed_ranges_and_session_tokens, target_feed_range)
        assert session_token == target_session_token
        # Cleanup: control-plane -> key_database (key-auth)
        await self.key_database.delete_container(container.id)


    async def test_latest_session_token_logical_hpk(self):
        # create_container is control-plane and uses key_database (key-auth).
        container_ref = await self.key_database.create_container(
            "test_updated_session_token_from_logical_hpk" + str(uuid.uuid4()),
            PartitionKey(path=["/state", "/city", "/zipcode"], kind="MultiHash"),
            offer_throughput=400)
        container = self.database.get_container_client(container_ref.id)
        feed_ranges_and_session_tokens = []
        previous_session_token = ""
        target_pk = ['CA', 'LA1', '90001']
        target_feed_range = await container.feed_range_from_partition_key(target_pk)
        target_session_token, previous_session_token = await self.create_items_logical_pk_async(container, target_feed_range,
                                                                                                previous_session_token,
                                                                                                feed_ranges_and_session_tokens,
                                                                                                True)
        session_token = await container.get_latest_session_token(feed_ranges_and_session_tokens, target_feed_range)

        assert session_token == target_session_token
        # Cleanup: control-plane -> key_database (key-auth)
        await self.key_database.delete_container(container.id)

    @staticmethod
    async def create_items_logical_pk_async(container, target_pk_range, previous_session_token, feed_ranges_and_session_tokens, hpk=False):
        target_session_token = ""
        for i in range(100):
            item = create_item(hpk)
            response = await container.create_item(item, session_token=previous_session_token)
            session_token = response.get_response_headers()[HttpHeaders.SessionToken]
            pk = item['pk'] if not hpk else [item['state'], item['city'], item['zipcode']]
            pk_feed_range = await container.feed_range_from_partition_key(pk)
            pk_feed_range_epk = FeedRangeInternalEpk.from_json(pk_feed_range)
            target_feed_range_epk = FeedRangeInternalEpk.from_json(target_pk_range)
            if (pk_feed_range_epk.get_normalized_range() ==
                    target_feed_range_epk.get_normalized_range()):
                target_session_token = session_token
            previous_session_token = session_token
            feed_ranges_and_session_tokens.append((pk_feed_range,
                                                   session_token))
        return target_session_token, previous_session_token

    @staticmethod
    async def create_items_physical_pk_async(container, pk_feed_range, previous_session_token, feed_ranges_and_session_tokens, hpk=False):
        target_session_token = ""
        container_feed_ranges = [feed_range async for feed_range in container.read_feed_ranges()]
        target_feed_range = None
        for feed_range in container_feed_ranges:
            if await container.is_feed_range_subset(feed_range, pk_feed_range):
                target_feed_range = feed_range
                break

        for i in range(100):
            item = create_item(hpk)
            response = await container.create_item(item, session_token=previous_session_token)
            session_token = response.get_response_headers()[HttpHeaders.SessionToken]
            if hpk:
                pk = [item['state'], item['city'], item['zipcode']]
                curr_feed_range = await container.feed_range_from_partition_key(pk)
            else:
                curr_feed_range = await container.feed_range_from_partition_key(item['pk'])
            if await container.is_feed_range_subset(target_feed_range, curr_feed_range):
                target_session_token = session_token
            previous_session_token = session_token
            feed_ranges_and_session_tokens.append((curr_feed_range, session_token))

        return target_session_token, target_feed_range, previous_session_token

if __name__ == '__main__':
    unittest.main()
