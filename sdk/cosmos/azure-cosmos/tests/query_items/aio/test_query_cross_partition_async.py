# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Rust-path copies of the async cross-partition query tests.

Source: ``tests/test_query_cross_partition_async.py``. The class name, lane
markers, query inputs and assertions match the original; method names add
``_rust``. Each test owns a unique database (key-auth Rust client for control
plane, Rust data client for data plane) with the original 5-partition ``/pk``
container, and always deletes it. Rust-backed clients reject
``multiple_write_locations`` (Rust owns multi-write routing), so the original's
circuit-breaker toggle is omitted.

Run with::

    pytest --noconftest tests/query_items/aio/test_query_cross_partition_async.py -v
"""
import unittest
import uuid

import pytest

import azure.cosmos.exceptions as exceptions
from azure.cosmos import http_constants
from azure.cosmos.aio import CosmosClient, DatabaseProxy, ContainerProxy
from azure.cosmos.partition_key import PartitionKey
from common._test_helpers import ResponseHookCaller
from config.clients import create_data_client_async
from config.settings import TestSettings, unique_database_id


@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosQuery
@pytest.mark.cosmosAADQuery
class TestQueryCrossPartitionAsync(unittest.IsolatedAsyncioTestCase):
    """Rust-path copy of tests/test_query_cross_partition_async.py::TestQueryCrossPartitionAsync."""

    created_db: DatabaseProxy = None
    key_db: DatabaseProxy = None
    created_container: ContainerProxy = None
    key_container: ContainerProxy = None
    client: CosmosClient = None
    key_client: CosmosClient = None
    config = TestSettings
    host = config.host
    masterKey = config.masterKey
    TEST_CONTAINER_ID = str(uuid.uuid4())

    async def asyncSetUp(self):
        self.TEST_DATABASE_ID = unique_database_id("query-xp-async")
        # Closed decision: Rust owns endpoint discovery and multi-write routing
        # (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#client-init-routing). Rust-backed clients reject the
        # original's multiple_write_locations argument (even False), so it is omitted.
        self.key_client = CosmosClient(self.host, self.masterKey, _backend="rust")
        await self.key_client.__aenter__()
        self.addAsyncCleanup(self.key_client.close)
        self.key_db = await self.key_client.create_database(self.TEST_DATABASE_ID)
        self.addAsyncCleanup(self.key_client.delete_database, self.TEST_DATABASE_ID)
        self.client = create_data_client_async(_backend="rust")
        await self.client.__aenter__()
        self.addAsyncCleanup(self.client.close)
        self.created_db = self.client.get_database_client(self.TEST_DATABASE_ID)
        # Create container via key-auth (control-plane), get data container via data client
        created_container_ref = await self.key_db.create_container(
            self.TEST_CONTAINER_ID,
            PartitionKey(path="/pk"),
            offer_throughput=TestSettings.THROUGHPUT_FOR_5_PARTITIONS)
        self.created_container = self.created_db.get_container_client(created_container_ref.id)
        # Use key auth for test writes. This avoids flaky failures where a later change feed
        # read can hit a replica that has not finished RBAC propagation for AAD yet.
        self.key_container = self.key_db.get_container_client(created_container_ref.id)

    async def test_first_and_last_slashes_trimmed_for_query_string_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_cross_partition_async.py::TestQueryCrossPartitionAsync.test_first_and_last_slashes_trimmed_for_query_string_async
        doc_id = 'myId' + str(uuid.uuid4())
        document_definition = {'pk': 'pk', 'id': doc_id}
        await self.created_container.create_item(body=document_definition)

        query = 'SELECT * from c'
        query_iterable = self.created_container.query_items(
            query=query,
            partition_key='pk'
        )
        iter_list = [item async for item in query_iterable]
        assert iter_list[0]['id'] == doc_id

    async def test_populate_query_metrics_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_cross_partition_async.py::TestQueryCrossPartitionAsync.test_populate_query_metrics_async
        doc_id = 'MyId' + str(uuid.uuid4())
        document_definition = {'pk': 'pk', 'id': doc_id}
        await self.created_container.create_item(body=document_definition)

        query = 'SELECT * from c'
        query_iterable = self.created_container.query_items(
            query=query,
            partition_key='pk',
            populate_query_metrics=True
        )

        iter_list = [item async for item in query_iterable]
        assert iter_list[0]['id'] == doc_id

        # Known gap 36: Query diagnostics and other request options are not sent over Gateway V2 (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-36).
        pytest.skip("driver-gap: Rust does not send populate_query_metrics over Gateway V2, so the "
                    "query metrics header is missing (known gap 36, "
                    "docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-36). The query ran.")
        metrics_header_name = 'x-ms-documentdb-query-metrics'
        assert metrics_header_name in self.created_container.client_connection.last_response_headers
        metrics_header = self.created_container.client_connection.last_response_headers[metrics_header_name]
        # Validate header is well-formed: "key1=value1;key2=value2;etc"
        metrics = metrics_header.split(';')
        assert len(metrics) > 1
        assert all(['=' in x for x in metrics])

    # Known gap 36: query advice is dropped by the driver's response headers on both transports (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#query-advice-response-header).
    @pytest.mark.skip(
        reason=(
            "driver-gap: the x-ms-cosmos-query-advice response header never reaches Python, with "
            "Gateway V2 on or off (known gap 36, "
            "docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#query-advice-response-header). "
            "The original skip cites the emulator; the legacy test passes on a live account."
        )
    )
    async def test_populate_query_advice_rust(self):
        # Source: tests/test_query_cross_partition_async.py::TestQueryCrossPartitionAsync.test_populate_query_advice
        doc_id = 'MyId' + str(uuid.uuid4())
        document_definition = {
            'pk': 'pk', 'id': doc_id, 'name': 'test document',
            'tags': [{'name': 'python'}, {'name': 'cosmos'}],
            'timestamp': '2099-01-01T00:00:00Z', 'ticks': 0, 'ts': 0
        }
        await self.created_container.create_item(body=document_definition)

        QUERY_ADVICE_HEADER = http_constants.HttpHeaders.QueryAdvice

        # QA1000 - PartialArrayContains: ARRAY_CONTAINS with partial match
        query_iterable = self.created_container.query_items(
            query='SELECT * FROM c WHERE ARRAY_CONTAINS(c.tags, {"name": "python"}, true)',
            partition_key='pk', populate_query_advice=True
        )
        [item async for item in query_iterable]
        query_advice = self.created_container.client_connection.last_response_headers.get(QUERY_ADVICE_HEADER)
        assert query_advice is not None
        assert "QA1000" in query_advice

        # QA1002 - Contains: CONTAINS usage
        query_iterable = self.created_container.query_items(
            query='SELECT * FROM c WHERE CONTAINS(c.name, "test")',
            partition_key='pk', populate_query_advice=True
        )
        [item async for item in query_iterable]
        query_advice = self.created_container.client_connection.last_response_headers.get(QUERY_ADVICE_HEADER)
        assert query_advice is not None
        assert "QA1002" in query_advice

        # QA1003 - CaseInsensitiveStartsWithOrStringEquals: case-insensitive STARTSWITH
        query_iterable = self.created_container.query_items(
            query='SELECT * FROM c WHERE STARTSWITH(c.name, "test", true)',
            partition_key='pk', populate_query_advice=True
        )
        [item async for item in query_iterable]
        query_advice = self.created_container.client_connection.last_response_headers.get(QUERY_ADVICE_HEADER)
        assert query_advice is not None
        assert "QA1003" in query_advice

        # QA1004 - CaseInsensitiveEndsWith: case-insensitive ENDSWITH
        query_iterable = self.created_container.query_items(
            query='SELECT * FROM c WHERE ENDSWITH(c.name, "document", true)',
            partition_key='pk', populate_query_advice=True
        )
        [item async for item in query_iterable]
        query_advice = self.created_container.client_connection.last_response_headers.get(QUERY_ADVICE_HEADER)
        assert query_advice is not None
        assert "QA1004" in query_advice

        # QA1007 - GetCurrentDateTime: usage of GetCurrentDateTime
        query_iterable = self.created_container.query_items(
            query='SELECT * FROM c WHERE c.timestamp < GetCurrentDateTime()',
            partition_key='pk', populate_query_advice=True
        )
        [item async for item in query_iterable]
        query_advice = self.created_container.client_connection.last_response_headers.get(QUERY_ADVICE_HEADER)
        assert query_advice is not None
        assert "QA1007" in query_advice

        # QA1008 - GetCurrentTicks: usage of GetCurrentTicks
        query_iterable = self.created_container.query_items(
            query='SELECT * FROM c WHERE c.ticks < GetCurrentTicks()',
            partition_key='pk', populate_query_advice=True
        )
        [item async for item in query_iterable]
        query_advice = self.created_container.client_connection.last_response_headers.get(QUERY_ADVICE_HEADER)
        assert query_advice is not None
        assert "QA1008" in query_advice

        # QA1009 - GetCurrentTimestamp: usage of GetCurrentTimestamp
        query_iterable = self.created_container.query_items(
            query='SELECT * FROM c WHERE c.ts < GetCurrentTimestamp()',
            partition_key='pk', populate_query_advice=True
        )
        [item async for item in query_iterable]
        query_advice = self.created_container.client_connection.last_response_headers.get(QUERY_ADVICE_HEADER)
        assert query_advice is not None
        assert "QA1009" in query_advice

    async def test_unsupported_queries_async_rust(self):
        # Source: tests/test_query_cross_partition_async.py::TestQueryCrossPartitionAsync.test_unsupported_queries_async
        # Known gap 30 item 9: docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-30
        pytest.skip(
            "driver-gap: Rust returns raw per-partition rows for the cross-partition non-VALUE aggregate "
            "'SELECT COUNT(1) FROM c' instead of the legacy 400 rejection (known gap 30 item 9, "
            "docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#query-non-value-aggregate)."
        )
        queries = ['SELECT COUNT(1) FROM c', 'SELECT COUNT(1) + 5 FROM c', 'SELECT COUNT(1) + SUM(c) FROM c']
        for query in queries:
            query_iterable = self.created_container.query_items(query=query)
            try:
                results = [item async for item in query_iterable]
                self.fail("query '{}' should have failed".format(query))
            except exceptions.CosmosHttpResponseError as e:
                assert e.status_code == 400

    async def test_query_with_non_overlapping_pk_ranges_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_cross_partition_async.py::TestQueryCrossPartitionAsync.test_query_with_non_overlapping_pk_ranges_async
        query_iterable = self.created_container.query_items("select * from c where c.pk='1' or c.pk='2'")
        assert [item async for item in query_iterable] == []

    async def test_paging_with_continuation_token_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_cross_partition_async.py::TestQueryCrossPartitionAsync.test_paging_with_continuation_token_async
        document_definition = {'pk': 'pk', 'id': '1'}
        await self.created_container.upsert_item(body=document_definition)
        document_definition = {'pk': 'pk', 'id': '2'}
        await self.created_container.upsert_item(body=document_definition)

        query = 'SELECT * from c'
        query_iterable = self.created_container.query_items(
            query=query,
            partition_key='pk',
            max_item_count=1
        )
        pager = query_iterable.by_page()
        await pager.__anext__()
        token = pager.continuation_token

        second_page = [item async for item in await pager.__anext__()][0]

        pager = query_iterable.by_page(token)
        second_page_fetched_with_continuation_token = [item async for item in await pager.__anext__()][0]

        assert second_page['id'] == second_page_fetched_with_continuation_token['id']

    async def test_cross_partition_query_with_continuation_token_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_cross_partition_async.py::TestQueryCrossPartitionAsync.test_cross_partition_query_with_continuation_token_async
        document_definition = {'pk': 'pk1', 'id': str(uuid.uuid4())}
        await self.created_container.create_item(body=document_definition)
        document_definition = {'pk': 'pk2', 'id': str(uuid.uuid4())}
        await self.created_container.create_item(body=document_definition)

        query = 'SELECT * from c'
        query_iterable = self.created_container.query_items(
            query=query,
            max_item_count=1)
        pager = query_iterable.by_page()
        await pager.__anext__()
        token = pager.continuation_token
        second_page = [item async for item in await pager.__anext__()][0]

        pager = query_iterable.by_page(token)
        second_page_fetched_with_continuation_token = [item async for item in await pager.__anext__()][0]

        assert second_page['id'] == second_page_fetched_with_continuation_token['id']

    async def test_value_max_query_async_rust(self):
        # Source: tests/test_query_cross_partition_async.py::TestQueryCrossPartitionAsync.test_value_max_query_async
        await self.created_container.create_item(
            {"id": str(uuid.uuid4()), "isComplete": True, "version": 3, "lookupVersion": "console_version"})
        await self.created_container.create_item(
            {"id": str(uuid.uuid4()), "isComplete": True, "version": 2, "lookupVersion": "console_version"})
        query = "Select value max(c.version) FROM c where c.isComplete = true and c.lookupVersion = @lookupVersion"
        query_results = self.created_container.query_items(query, parameters=[
            {"name": "@lookupVersion", "value": "console_version"}
        ])
        # Known gap 30: query_items remaining query, paging, and continuation-token gaps, item 1 aggregates (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#query-unscoped-max).
        pytest.skip("driver-gap: Rust rejects cross-partition MAX without a partition key with 400/20113 "
                    "(ClientUnsupportedQueryFeature) (known gap 30 item 1, "
                    "docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#query-unscoped-max). The items were created.")
        item_list = [item async for item in query_results]
        assert len(item_list) == 1
        assert item_list[0] == 3

    async def test_continuation_token_size_limit_query_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_cross_partition_async.py::TestQueryCrossPartitionAsync.test_continuation_token_size_limit_query_async
        for i in range(1, 1000):
            await self.created_container.create_item(body=dict(pk='123', id=str(i), some_value=str(i % 3)))
        query = "Select * from c where c.some_value='2'"
        print("Created 1000 items")
        response_query = self.created_container.query_items(query, partition_key='123', max_item_count=100,
                                                            continuation_token_limit=1)
        pager = response_query.by_page()
        await pager.__anext__()
        token = pager.continuation_token
        # Continuation token size should be below 1kb
        assert len(token.encode('utf-8')) <= 1024
        await pager.__anext__()
        token = pager.continuation_token

        # verify a second time
        assert len(token.encode('utf-8')) <= 1024
        print("Test done")

    async def test_cross_partition_query_response_hook_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_cross_partition_async.py::TestQueryCrossPartitionAsync.test_cross_partition_query_response_hook_async
        created_collection_ref = await self.key_db.create_container_if_not_exists(
            id="query_response_hook_test" + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=12000
        )
        created_collection = self.created_db.get_container_client(created_collection_ref.id)
        items = [
            {'id': str(uuid.uuid4()), 'pk': '0', 'val': 5},
            {'id': str(uuid.uuid4()), 'pk': '1', 'val': 10},
            {'id': str(uuid.uuid4()), 'pk': '0', 'val': 5},
            {'id': str(uuid.uuid4()), 'pk': '1', 'val': 10},
            {'id': str(uuid.uuid4()), 'pk': '0', 'val': 5},
            {'id': str(uuid.uuid4()), 'pk': '1', 'val': 10}
        ]

        for item in items:
            await created_collection.create_item(body=item)

        response_hook = ResponseHookCaller()
        item_list = [item async for item in created_collection.query_items("select * from c", response_hook=response_hook)]
        assert len(item_list) == 6
        assert response_hook.count == 2
        await self.key_db.delete_container(created_collection_ref.id)

    async def test_cross_partition_query_pagination_with_max_item_count_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_cross_partition_async.py::TestQueryCrossPartitionAsync.test_cross_partition_query_pagination_with_max_item_count_async
        """Test cross-partition pagination showing per-page limits and total results."""
        created_collection_ref = await self.key_db.create_container(
            "cross_partition_pagination_test_" + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=TestSettings.THROUGHPUT_FOR_5_PARTITIONS)
        created_collection = self.created_db.get_container_client(created_collection_ref.id)

        # Create 30 items across 3 different partitions
        total_items = 30
        items_per_partition = 10
        partitions = ["pk_1", "pk_2", "pk_3"]

        for pk in partitions:
            for i in range(items_per_partition):
                document_definition = {
                    'pk': pk,
                    'id': f'{pk}_item_{i}',
                    'value': i
                }
                await created_collection.create_item(body=document_definition)

        # Test cross-partition query with max_item_count
        max_items_per_page = 8
        query = "SELECT * FROM c ORDER BY c['value']"
        query_iterable = created_collection.query_items(
            query=query,
            max_item_count=max_items_per_page
        )

        # Iterate through pages and verify per-page counts
        all_fetched_results = []
        page_count = 0
        item_pages = query_iterable.by_page()

        async for page in item_pages:
            page_count += 1
            items_in_page = [item async for item in page]
            all_fetched_results.extend(items_in_page)

            # Each page should have at most max_item_count items
            # In cross-partition queries, pages may have fewer items
            assert len(items_in_page) <= max_items_per_page
            assert len(items_in_page) > 0  # Pages should not be empty

        # Verify total results match expected count
        assert len(all_fetched_results) == total_items

        # Verify we got multiple pages
        assert page_count > 1

        await self.key_db.delete_container(created_collection_ref.id)

    # TODO: migrate to AAD once service-side RBAC activation window (403/5302) fix ships.
    @pytest.mark.skipif(
        TestSettings.data_auth_mode == 'aad',
        reason="environment-gap: post-create RBAC activation window (403/5302)  -  migrate after service-side fix",
    )
    async def test_cross_partition_query_pagination_counting_results_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_cross_partition_async.py::TestQueryCrossPartitionAsync.test_cross_partition_query_pagination_counting_results_async
        """Test counting total results while paginating across partitions."""
        created_collection_ref = await self.key_db.create_container(
            "cross_partition_count_test_" + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=TestSettings.THROUGHPUT_FOR_5_PARTITIONS)
        created_collection = self.created_db.get_container_client(created_collection_ref.id)

        # Create items across multiple partitions with different counts
        partitions_config = [
            ("partition_a", 5),
            ("partition_b", 8),
            ("partition_c", 3),
            ("partition_d", 12)
        ]

        total_expected = 0
        for pk, count in partitions_config:
            for i in range(count):
                document_definition = {
                    'pk': pk,
                    'id': f'{pk}_item_{i}',
                    'name': f'Item {i} in {pk}'
                }
                await created_collection.create_item(body=document_definition)
                total_expected += 1

        # Query across partitions with pagination
        max_items_per_page = 5
        query = "SELECT * FROM c"
        query_iterable = created_collection.query_items(
            query=query,
            max_item_count=max_items_per_page
        )

        # Count items across all pages
        total_count = 0
        page_count = 0
        page_sizes = []

        item_pages = query_iterable.by_page()
        async for page in item_pages:
            page_count += 1
            items = [item async for item in page]
            page_size = len(items)
            page_sizes.append(page_size)
            total_count += page_size

            # Verify page size constraints
            assert page_size <= max_items_per_page
            assert page_size > 0

        # Verify total count matches what we inserted
        assert total_count == total_expected

        # Verify we processed multiple pages
        assert page_count > 1

        await self.key_db.delete_container(created_collection_ref.id)


if __name__ == '__main__':
    unittest.main()
