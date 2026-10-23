# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Opt-in async grouped real split with owned resources and retained assertions.

Python range polling is control-plane setup, not Rust routing-cache recovery.
The legacy data-cache injection is explicitly disabled for Rust.
"""

import os
import random
import time
import unittest
import uuid
from functools import partial

import pytest

from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient
from azure.cosmos._session_token_helpers import parse_session_token
from get_latest_session_token._fixtures import create_items_logical_pk_async, create_items_physical_pk_async
from get_latest_session_token._split_support import (
    SPLIT_TIMEOUT,
    assert_no_stage_failures,
    require_real_split,
    snapshot_split_routing_map,
    split_stage,
    trigger_split_async,
    wait_for_split_ranges_async,
)


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosSplit
@pytest.mark.skipif(
    os.environ.get("COSMOS_SESSION_TOKEN_REAL_SPLIT") != "1",
    reason="environment-gap: opt in with COSMOS_SESSION_TOKEN_REAL_SPLIT=1 to authorize 11000 RU/s",
)
class TestLatestSessionTokenRealSplitAsync(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        require_real_split()
        state = random.getstate()
        self.addCleanup(random.setstate, state)
        random.seed(0)
        self.create_data_client_async = partial(
            CosmosClient, os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust"
        )
        self.key_client = CosmosClient(
            os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="core-python"
        )
        self.addAsyncCleanup(self.key_client.close)
        await self.key_client.__aenter__()
        self.key_database = await self.key_client.create_database("token_parity_" + uuid.uuid4().hex)
        self.addAsyncCleanup(self.key_client.delete_database, self.key_database.id)
        self.TEST_DATABASE_ID = self.key_database.id
        self.client = self.create_data_client_async()
        self.addAsyncCleanup(self.client.close)
        await self.client.__aenter__()
        self.database = self.client.get_database_client(self.TEST_DATABASE_ID)
        print(f"\nOwned token-test database: {self.TEST_DATABASE_ID}")

    create_items_logical_pk_async = staticmethod(create_items_logical_pk_async)
    create_items_physical_pk_async = staticmethod(create_items_physical_pk_async)

    @pytest.mark.timeout(1500)
    async def test_change_feed_session_token_and_read_items_after_split_async_rust(self):
        # Source: tests/test_partition_split_scenarios_async.py::TestPartitionSplitScenariosAsync.test_change_feed_session_token_and_read_items_after_split_async
        container_ref = await self.key_database.create_container(
            "test_grouped_partition_split_async_" + str(uuid.uuid4()), PartitionKey(path="/pk"), offer_throughput=400)
        self.addAsyncCleanup(self.key_database.delete_container, container_ref.id)
        container = self.database.get_container_client(container_ref.id)
        key_container_for_split = self.key_database.get_container_client(container.id)

        # Keep continuation and session state separate.
        change_feed_client = self.create_data_client_async()
        self.addAsyncCleanup(change_feed_client.close)
        await change_feed_client.__aenter__()
        created_collection = change_feed_client.get_database_client(self.TEST_DATABASE_ID).get_container_client(
            container_ref.id)
        read_items_client = self.create_data_client_async()
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
            restore_routing_map = snapshot_split_routing_map(container, collection_rid, legacy_routing_cache=False)
            deadline = time.monotonic() + SPLIT_TIMEOUT
            await trigger_split_async(key_container_for_split, 11000)
            await wait_for_split_ranges_async(key_container_for_split, initial_ranges[0]["id"], deadline)

        failures = []
        with split_stage("read_items_after", failures) as diagnostics:
            restore_routing_map()
            final_read_items = await read_items_container.read_items(items=items_to_read)
            diagnostics.update(expected_count=len(items_to_read), actual_count=len(final_read_items))
            self.assertEqual(len(final_read_items), len(items_to_read))
            final_read_ids = {item['id'] for item in final_read_items}
            diagnostics.update(
                missing_count=len(set(item_ids) - final_read_ids),
                unexpected_count=len(final_read_ids - set(item_ids)),
            )
            self.assertSetEqual(final_read_ids, set(item_ids))

        with split_stage("change_feed_after", failures) as diagnostics:
            restore_routing_map()
            new_documents = [{'pk': 'pk2', 'id': 'doc2'}, {'pk': 'pk3', 'id': 'doc3'}, {'pk': 'pk4', 'id': 'doc4'}]
            expected_ids = ['doc2', 'doc3', 'doc4']
            for document in new_documents:
                await created_collection.create_item(body=document)
            query_iterable = created_collection.query_items_change_feed(continuation=continuation)
            actual_ids = [item['id'] async for item in query_iterable]
            diagnostics.update(
                expected_count=len(expected_ids), actual_count=len(actual_ids), ids_match=actual_ids == expected_ids
            )
            assert actual_ids == expected_ids

        with split_stage("logical_session_token_after", failures) as diagnostics:
            restore_routing_map()
            target_session_token, _ = await self.create_items_logical_pk_async(
                container, target_feed_range, session_token, feed_ranges_and_session_tokens)
            target_feed_range = await container.feed_range_from_partition_key(target_pk)
            session_token = await container.get_latest_session_token(feed_ranges_and_session_tokens, target_feed_range)
            diagnostics["token_matches"] = session_token == target_session_token
            assert session_token == target_session_token

        with split_stage("physical_session_token_after", failures) as diagnostics:
            _, phys_target_feed_range, phys_previous_session_token = await self.create_items_physical_pk_async(
                container, pk_feed_range, phys_session_token, phys_feed_ranges_and_session_tokens)
            phys_session_token = await container.get_latest_session_token(
                phys_feed_ranges_and_session_tokens, phys_target_feed_range)
            pk_range_id, session_token = parse_session_token(phys_session_token)
            diagnostics.update(
                lsn_not_regressed=session_token.global_lsn >= pre_split_session_token.global_lsn,
                expected_range_present='2' in pk_range_id,
            )
            assert session_token.global_lsn >= pre_split_session_token.global_lsn
            assert '2' in pk_range_id

        assert_no_stage_failures(failures)
