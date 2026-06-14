# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import asyncio
import os
import unittest
import uuid
from asyncio import gather
from unittest.mock import patch

import pytest

import azure.cosmos.aio._retry_utility_async as retry_utility
import azure.cosmos.aio._asynchronous_request as _asynchronous_request
import azure.cosmos.exceptions as exceptions
import azure.cosmos.cosmos_client as sync_cosmos_client
import test_config
from azure.cosmos import http_constants, _endpoint_discovery_retry_policy
from azure.cosmos._routing.feed_range_continuation import _decode_token
from azure.cosmos._execution_context.query_execution_info import _PartitionedQueryExecutionInfo
from azure.cosmos._retry_options import RetryOptions
from azure.cosmos.aio import CosmosClient, DatabaseProxy, ContainerProxy
from azure.cosmos.documents import _DistinctType
from azure.cosmos.partition_key import PartitionKey

@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosQuery
@pytest.mark.cosmosAADQuery
class TestQueryAsync(unittest.IsolatedAsyncioTestCase):
    """Test to ensure escaping of non-ascii characters from partition key"""

    created_db: DatabaseProxy = None
    created_container: ContainerProxy = None
    client: CosmosClient = None
    key_client: sync_cosmos_client.CosmosClient = None
    key_db = None
    config = test_config.TestConfig
    TEST_CONTAINER_ID = config.TEST_MULTI_PARTITION_CONTAINER_ID
    TEST_DATABASE_ID = config.TEST_DATABASE_ID
    host = config.host
    masterKey = config.masterKey
    connectionPolicy = config.connectionPolicy

    @classmethod
    def setUpClass(cls):
        cls.use_multiple_write_locations = False
        if os.environ.get("AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER", "False") == "True":
            cls.use_multiple_write_locations = True
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")
        # key_client is a sync key-auth client used for control-plane operations
        # (create/delete containers) inside async tests. This works but is not ideal  -  a future
        # cleanup could use an async key-auth client instead once the project decides on async
        # key-auth client handling.
        # NOTE: pass ``multiple_write_locations`` so circuit-breaker runs keep
        # multi-write-region routing aligned with sync ``test_query.py``.
        cls.key_client = sync_cosmos_client.CosmosClient(
            cls.host, cls.masterKey, multiple_write_locations=cls.use_multiple_write_locations
        )
        cls.key_db = cls.key_client.get_database_client(cls.TEST_DATABASE_ID)

    @classmethod
    def tearDownClass(cls):
        # Close the sync key-auth setup client created in setUpClass to release its
        # underlying requests.Session (otherwise it leaks until process exit).
        if cls.key_client is not None:
            cls.key_client.close()

    async def asyncSetUp(self):
        # AAD (or key, depending on env var) async client for data-plane operations
        self.client = test_config.TestConfig.create_data_client_async()
        await self.client.__aenter__()
        self.created_db = self.client.get_database_client(self.TEST_DATABASE_ID)

    async def asyncTearDown(self):
        await self.client.close()

    def _create_container_for_test(self, container_id, partition_key, **kwargs):
        """Create container via sync key-auth setup client (control-plane), return async data-plane proxy."""
        self.key_db.create_container(id=container_id, partition_key=partition_key, **kwargs)
        return self.created_db.get_container_client(container_id)

    def _create_container_if_not_exists_for_test(self, container_id, partition_key, **kwargs):
        """Create container if not exists via sync key-auth setup client, return async data-plane proxy."""
        self.key_db.create_container_if_not_exists(id=container_id, partition_key=partition_key, **kwargs)
        return self.created_db.get_container_client(container_id)

    def _delete_container_for_test(self, container_id):
        """Delete container via sync key-auth setup client (control-plane)."""
        self.key_db.delete_container(container_id)


    async def test_first_and_last_slashes_trimmed_for_query_string_async(self):
        container_id = str(uuid.uuid4())
        created_collection = self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        doc_id = 'myId' + str(uuid.uuid4())
        document_definition = {'pk': 'pk', 'id': doc_id}
        await created_collection.create_item(body=document_definition)
        await asyncio.sleep(1)

        query = 'SELECT * from c'
        query_iterable = created_collection.query_items(
            query=query,
            partition_key='pk'
        )
        iter_list = [item async for item in query_iterable]
        assert iter_list[0]['id'] == doc_id

        self._delete_container_for_test(container_id)

    @pytest.mark.asyncio
    async def test_populate_query_metrics_async(self):
        container_id = "query_metrics_test" + str(uuid.uuid4())
        created_collection = self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        doc_id = 'MyId' + str(uuid.uuid4())
        document_definition = {'pk': 'pk', 'id': doc_id}
        await created_collection.create_item(body=document_definition)
        await asyncio.sleep(1)

        query = 'SELECT * from c'
        query_iterable = created_collection.query_items(
            query=query,
            partition_key='pk',
            populate_query_metrics=True
        )

        iter_list = [item async for item in query_iterable]
        assert iter_list[0]['id'] == doc_id

        metrics_header_name = 'x-ms-documentdb-query-metrics'
        assert metrics_header_name in created_collection.client_connection.last_response_headers
        metrics_header = created_collection.client_connection.last_response_headers[metrics_header_name]
        # Validate header is well-formed: "key1=value1;key2=value2;etc"
        metrics = metrics_header.split(';')
        assert len(metrics) > 1
        assert all(['=' in x for x in metrics])

        self._delete_container_for_test(container_id)

    async def test_populate_index_metrics_async(self):
        container_id = "index_metrics_test" + str(uuid.uuid4())
        created_collection = self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        doc_id = 'MyId' + str(uuid.uuid4())
        document_definition = {'pk': 'pk', 'id': doc_id}
        await created_collection.create_item(body=document_definition)
        await asyncio.sleep(1)

        query = 'SELECT * from c'
        query_iterable = created_collection.query_items(
            query=query,
            partition_key='pk',
            populate_index_metrics=True
        )

        iter_list = [item async for item in query_iterable]
        assert iter_list[0]['id'] == doc_id

        index_header_name = http_constants.HttpHeaders.IndexUtilization
        assert index_header_name in created_collection.client_connection.last_response_headers
        index_metrics = created_collection.client_connection.last_response_headers[index_header_name]
        assert index_metrics != {}
        assert 'UtilizedSingleIndexes' in index_metrics
        assert 'PotentialSingleIndexes' in index_metrics
        assert 'UtilizedCompositeIndexes' in index_metrics
        assert 'PotentialCompositeIndexes' in index_metrics

        # Backend index diagnostics can vary by region/build; validate stable signal instead of exact payload.
        candidate_indexes = list(index_metrics.get('UtilizedSingleIndexes', []))
        candidate_indexes.extend(index_metrics.get('PotentialSingleIndexes', []))
        assert any(
            idx.get('FilterExpression') == ''
            and idx.get('IndexImpactScore') == 'High'
            and idx.get('IndexSpec') in ('/pk/?', '/_epk/?')
            for idx in candidate_indexes
        )

        self._delete_container_for_test(container_id)

    @pytest.mark.skip(reason="Emulator does not support query advisor yet")
    async def test_populate_query_advice_async(self):
        container_id = "query_advice_test" + str(uuid.uuid4())
        created_collection = self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        doc_id = 'MyId' + str(uuid.uuid4())
        document_definition = {
            'pk': 'pk', 'id': doc_id, 'name': 'test document',
            'tags': [{'name': 'python'}, {'name': 'cosmos'}],
            'timestamp': '2099-01-01T00:00:00Z', 'ticks': 0, 'ts': 0
        }
        await created_collection.create_item(body=document_definition)
        await asyncio.sleep(1)

        QUERY_ADVICE_HEADER = http_constants.HttpHeaders.QueryAdvice

        # QA1000 - PartialArrayContains: ARRAY_CONTAINS with partial match
        query_iterable = created_collection.query_items(
            query='SELECT * FROM c WHERE ARRAY_CONTAINS(c.tags, {"name": "python"}, true)',
            partition_key='pk', populate_query_advice=True
        )
        [item async for item in query_iterable]
        query_advice = created_collection.client_connection.last_response_headers.get(QUERY_ADVICE_HEADER)
        assert query_advice is not None
        assert "QA1000" in query_advice

        # QA1002 - Contains: CONTAINS usage
        query_iterable = created_collection.query_items(
            query='SELECT * FROM c WHERE CONTAINS(c.name, "test")',
            partition_key='pk', populate_query_advice=True
        )
        [item async for item in query_iterable]
        query_advice = created_collection.client_connection.last_response_headers.get(QUERY_ADVICE_HEADER)
        assert query_advice is not None
        assert "QA1002" in query_advice

        # QA1003 - CaseInsensitiveStartsWithOrStringEquals: case-insensitive STARTSWITH
        query_iterable = created_collection.query_items(
            query='SELECT * FROM c WHERE STARTSWITH(c.name, "test", true)',
            partition_key='pk', populate_query_advice=True
        )
        [item async for item in query_iterable]
        query_advice = created_collection.client_connection.last_response_headers.get(QUERY_ADVICE_HEADER)
        assert query_advice is not None
        assert "QA1003" in query_advice

        # QA1004 - CaseInsensitiveEndsWith: case-insensitive ENDSWITH
        query_iterable = created_collection.query_items(
            query='SELECT * FROM c WHERE ENDSWITH(c.name, "document", true)',
            partition_key='pk', populate_query_advice=True
        )
        [item async for item in query_iterable]
        query_advice = created_collection.client_connection.last_response_headers.get(QUERY_ADVICE_HEADER)
        assert query_advice is not None
        assert "QA1004" in query_advice

        # QA1007 - GetCurrentDateTime: usage of GetCurrentDateTime
        query_iterable = created_collection.query_items(
            query='SELECT * FROM c WHERE c.timestamp < GetCurrentDateTime()',
            partition_key='pk', populate_query_advice=True
        )
        [item async for item in query_iterable]
        query_advice = created_collection.client_connection.last_response_headers.get(QUERY_ADVICE_HEADER)
        assert query_advice is not None
        assert "QA1007" in query_advice

        # QA1008 - GetCurrentTicks: usage of GetCurrentTicks
        query_iterable = created_collection.query_items(
            query='SELECT * FROM c WHERE c.ticks < GetCurrentTicks()',
            partition_key='pk', populate_query_advice=True
        )
        [item async for item in query_iterable]
        query_advice = created_collection.client_connection.last_response_headers.get(QUERY_ADVICE_HEADER)
        assert query_advice is not None
        assert "QA1008" in query_advice

        # QA1009 - GetCurrentTimestamp: usage of GetCurrentTimestamp
        query_iterable = created_collection.query_items(
            query='SELECT * FROM c WHERE c.ts < GetCurrentTimestamp()',
            partition_key='pk', populate_query_advice=True
        )
        [item async for item in query_iterable]
        query_advice = created_collection.client_connection.last_response_headers.get(QUERY_ADVICE_HEADER)
        assert query_advice is not None
        assert "QA1009" in query_advice

        self._delete_container_for_test(container_id)

    # TODO: Need to validate the query request count logic
    @pytest.mark.skip
    async def test_max_item_count_honored_in_order_by_query_async(self):
        container_id = str(uuid.uuid4())
        created_collection = self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        docs = []
        for i in range(10):
            document_definition = {'pk': 'pk', 'id': 'myId' + str(uuid.uuid4())}
            docs.append(await created_collection.create_item(body=document_definition))

        query = 'SELECT * from c ORDER BY c._ts'
        query_iterable = created_collection.query_items(
            query=query,
            max_item_count=1
        )
        await self.validate_query_requests_count(query_iterable, 25)

        query_iterable = created_collection.query_items(
            query=query,
            max_item_count=100
        )

        await self.validate_query_requests_count(query_iterable, 5)

        self._delete_container_for_test(container_id)

    async def validate_query_requests_count(self, query_iterable, expected_count):
        self.count = 0
        self.OriginalExecuteFunction = retry_utility.ExecuteFunctionAsync
        retry_utility.ExecuteFunctionAsync = self._mock_execute_function
        item_pages = query_iterable.by_page()
        while True:
            try:
                page = await item_pages.__anext__()
                assert len([item async for item in page]) > 0
            except StopAsyncIteration:
                break
        retry_utility.ExecuteFunctionAsync = self.OriginalExecuteFunction
        assert self.count == expected_count
        self.count = 0

    async def _mock_execute_function(self, function, *args, **kwargs):
        self.count += 1
        return await self.OriginalExecuteFunction(function, *args, **kwargs)

    async def test_get_query_plan_through_gateway_async(self):
        created_collection = self.created_db.get_container_client(self.config.TEST_MULTI_PARTITION_CONTAINER_ID)
        await self._validate_query_plan(query="Select top 10 value count(c.id) from c",
                                        container_link=created_collection.container_link,
                                        top=10,
                                        order_by=[],
                                        aggregate=['Count'],
                                        select_value=True,
                                        offset=None,
                                        limit=None,
                                        distinct=_DistinctType.NoneType)

        await self._validate_query_plan(query="Select * from c order by c._ts offset 5 limit 10",
                                        container_link=created_collection.container_link,
                                        top=None,
                                        order_by=['Ascending'],
                                        aggregate=[],
                                        select_value=False,
                                        offset=5,
                                        limit=10,
                                        distinct=_DistinctType.NoneType)

        await self._validate_query_plan(query="Select distinct value c.id from c order by c.id",
                                        container_link=created_collection.container_link,
                                        top=None,
                                        order_by=['Ascending'],
                                        aggregate=[],
                                        select_value=True,
                                        offset=None,
                                        limit=None,
                                        distinct=_DistinctType.Ordered)

    async def _validate_query_plan(self, query, container_link, top, order_by, aggregate, select_value, offset, limit,
                                   distinct):
        query_plan_dict = await self.client.client_connection._GetQueryPlanThroughGateway(query, container_link)
        query_execution_info = _PartitionedQueryExecutionInfo(query_plan_dict)
        assert query_execution_info.has_rewritten_query()
        assert query_execution_info.has_distinct_type() == (distinct != "None")
        assert query_execution_info.get_distinct_type() == distinct
        assert query_execution_info.has_top() == (top is not None)
        assert query_execution_info.get_top() == top
        assert query_execution_info.has_order_by() == (len(order_by) > 0)
        assert query_execution_info.get_order_by() == order_by
        assert query_execution_info.has_aggregates() == (len(aggregate) > 0)
        assert query_execution_info.get_aggregates() == aggregate
        assert query_execution_info.has_select_value() == select_value
        assert query_execution_info.has_offset() == (offset is not None)
        assert query_execution_info.get_offset() == offset
        assert query_execution_info.has_limit() == (limit is not None)
        assert query_execution_info.get_limit() == limit

    async def test_unsupported_queries_async(self):
        created_collection = self.created_db.get_container_client(self.config.TEST_MULTI_PARTITION_CONTAINER_ID)
        queries = ['SELECT COUNT(1) FROM c', 'SELECT COUNT(1) + 5 FROM c', 'SELECT COUNT(1) + SUM(c) FROM c']
        for query in queries:
            query_iterable = created_collection.query_items(query=query)
            try:
                results = [item async for item in query_iterable]
                self.fail("query '{}' should have failed".format(query))
            except exceptions.CosmosHttpResponseError as e:
                assert e.status_code == 400

    async def test_query_with_non_overlapping_pk_ranges_async(self):
        created_collection = self.created_db.get_container_client(self.config.TEST_MULTI_PARTITION_CONTAINER_ID)
        query_iterable = created_collection.query_items("select * from c where c.pk='1' or c.pk='2'")
        assert [item async for item in query_iterable] == []

    async def test_offset_limit_async(self):
        container_id = "offset_limit_" + str(uuid.uuid4())
        created_collection = self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        values = []
        for i in range(10):
            document_definition = {'pk': i, 'id': 'myId' + str(uuid.uuid4()), 'value': i // 3}
            current_document = await created_collection.create_item(body=document_definition)
            values.append(current_document['pk'])

        await self.config._validate_distinct_offset_limit(
            created_collection=created_collection,
            query='SELECT DISTINCT c["value"] from c ORDER BY c.pk OFFSET 0 LIMIT 2',
            results=[0, 1])

        await self.config._validate_distinct_offset_limit(
            created_collection=created_collection,
            query='SELECT DISTINCT c["value"] from c ORDER BY c.pk OFFSET 2 LIMIT 2',
            results=[2, 3])

        await self.config._validate_distinct_offset_limit(
            created_collection=created_collection,
            query='SELECT DISTINCT c["value"] from c ORDER BY c.pk OFFSET 4 LIMIT 3',
            results=[])

        await self.config._validate_offset_limit(created_collection=created_collection,
                                                 query='SELECT * from c ORDER BY c.pk OFFSET 0 LIMIT 5',
                                                 results=values[:5])

        await self.config._validate_offset_limit(created_collection=created_collection,
                                                 query='SELECT * from c ORDER BY c.pk OFFSET 5 LIMIT 10',
                                                 results=values[5:])

        await self.config._validate_offset_limit(created_collection=created_collection,
                                                 query='SELECT * from c ORDER BY c.pk OFFSET 10 LIMIT 5',
                                                 results=[])

        await self.config._validate_offset_limit(created_collection=created_collection,
                                                 query='SELECT * from c ORDER BY c.pk OFFSET 100 LIMIT 1',
                                                 results=[])

        self._delete_container_for_test(container_id)

    async def test_distinct_async(self):
        distinct_field = 'distinct_field'
        pk_field = "pk"
        different_field = "different_field"

        container_id = 'collection with composite index ' + str(uuid.uuid4())
        created_collection = self._create_container_for_test(
            container_id,
            partition_key=PartitionKey(path="/pk", kind="Hash"),
            indexing_policy={
                "compositeIndexes": [
                    [{"path": "/" + pk_field, "order": "ascending"},
                     {"path": "/" + distinct_field, "order": "ascending"}],
                    [{"path": "/" + distinct_field, "order": "ascending"},
                     {"path": "/" + pk_field, "order": "ascending"}]
                ]
            }
        )
        documents = []
        for i in range(5):
            j = i
            while j > i - 5:
                document_definition = {pk_field: i, 'id': str(uuid.uuid4()), distinct_field: j}
                documents.append(await created_collection.create_item(body=document_definition))
                document_definition = {pk_field: i, 'id': str(uuid.uuid4()), distinct_field: j}
                documents.append(await created_collection.create_item(body=document_definition))
                document_definition = {pk_field: i, 'id': str(uuid.uuid4())}
                documents.append(await created_collection.create_item(body=document_definition))
                j -= 1

        padded_docs = self.config._pad_with_none(documents, distinct_field)

        await self.config._validate_distinct(created_collection=created_collection,  # returns {} and is right number
                                             query='SELECT distinct c.%s from c' % distinct_field,  # nosec
                                             results=self.config._get_distinct_docs(padded_docs, distinct_field, None, False),
                                             is_select=True,
                                             fields=[distinct_field])

        await self.config._validate_distinct(created_collection=created_collection,
                                             query='SELECT distinct c.%s, c.%s from c' % (distinct_field, pk_field),
                                             # nosec
                                             results=self.config._get_distinct_docs(padded_docs, distinct_field, pk_field, False),
                                             is_select=True,
                                             fields=[distinct_field, pk_field])

        await self.config._validate_distinct(created_collection=created_collection,
                                             query='SELECT distinct value c.%s from c' % distinct_field,  # nosec
                                             results=self.config._get_distinct_docs(padded_docs, distinct_field, None, True),
                                             is_select=True,
                                             fields=[distinct_field])

        await self.config._validate_distinct(created_collection=created_collection,
                                             query='SELECT distinct c.%s from c' % different_field,  # nosec
                                             results=['None'],
                                             is_select=True,
                                             fields=[different_field])

        self._delete_container_for_test(container_id)

    # TODO: migrate to AAD once service-side RBAC activation window (403/5302) fix ships.
    @pytest.mark.skipif(
        test_config.TestConfig.data_auth_mode == 'aad',
        reason="post-create RBAC activation window (403/5302)  -  migrate after service-side fix",
    )
    async def test_distinct_on_different_types_and_field_orders_async(self):
        container_id = "test-distinct-container-" + str(uuid.uuid4())
        created_collection = self._create_container_for_test(
            container_id,
            partition_key=PartitionKey("/pk"),
            offer_throughput=self.config.THROUGHPUT_FOR_5_PARTITIONS)
        payloads = [
            {'id': str(uuid.uuid4()), 'f1': 1, 'f2': 'value', 'f3': 100000000000000000, 'f4': [1, 2, '3'],
             'f5': {'f6': {'f7': 2}}},
            {'id': str(uuid.uuid4()), 'f2': '\'value', 'f4': [1.0, 2, '3'], 'f5': {'f6': {'f7': 2.0}}, 'f1': 1.0,
             'f3': 100000000000000000.00},
            {'id': str(uuid.uuid4()), 'f3': 100000000000000000.0, 'f5': {'f6': {'f7': 2}}, 'f2': '\'value', 'f1': 1,
             'f4': [1, 2.0, '3']}
        ]
        for pay in payloads:
            await created_collection.create_item(pay)

        await self.config._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct value c.f1 from c",
            expected_results=[1]
        )

        await self.config._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct value c.f2 from c",
            expected_results=['value', '\'value']
        )

        await self.config._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct value c.f2 from c order by c.f2",
            expected_results=['value', '\'value']
        )

        await self.config._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct value c.f3 from c",
            expected_results=[100000000000000000]
        )

        await self.config._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct value c.f4 from c",
            expected_results=[[1, 2, '3']]
        )

        await self.config._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct value c.f5.f6 from c",
            expected_results=[{'f7': 2}]
        )

        await self.config._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct c.f1, c.f2, c.f3 from c",
            expected_results=[{'f1': 1, 'f2': 'value', 'f3': 100000000000000000},
                              {'f1': 1.0, 'f2': '\'value', 'f3': 100000000000000000.00}]
        )

        await self.config._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct c.f1, c.f2, c.f3 from c order by c.f1",
            expected_results=[{'f1': 1, 'f2': 'value', 'f3': 100000000000000000},
                              {'f1': 1.0, 'f2': '\'value', 'f3': 100000000000000000.00}]
        )

        self._delete_container_for_test(container_id)

    async def test_paging_with_continuation_token_async(self):
        created_collection = self.created_db.get_container_client(self.config.TEST_MULTI_PARTITION_CONTAINER_ID)

        document_definition = {'pk': 'pk', 'id': '1'}
        await created_collection.upsert_item(body=document_definition)
        document_definition = {'pk': 'pk', 'id': '2'}
        await created_collection.upsert_item(body=document_definition)

        query = 'SELECT * from c'
        query_iterable = created_collection.query_items(
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

    async def test_cross_partition_query_with_continuation_token_async(self):
        created_collection = self.created_db.get_container_client(self.config.TEST_MULTI_PARTITION_CONTAINER_ID)
        document_definition = {'pk': 'pk1', 'id': str(uuid.uuid4())}
        await created_collection.create_item(body=document_definition)
        document_definition = {'pk': 'pk2', 'id': str(uuid.uuid4())}
        await created_collection.create_item(body=document_definition)

        query = 'SELECT * from c'
        query_iterable = created_collection.query_items(
            query=query,
            max_item_count=1)
        pager = query_iterable.by_page()
        await pager.__anext__()
        token = pager.continuation_token
        second_page = [item async for item in await pager.__anext__()][0]

        pager = query_iterable.by_page(token)
        second_page_fetched_with_continuation_token = [item async for item in await pager.__anext__()][0]

        assert second_page['id'] == second_page_fetched_with_continuation_token['id']

    async def test_full_pk_continuation_emits_legacy_by_default_async(self):
        """Full partition-key queries return legacy continuation tokens by default."""
        created_collection = self.created_db.get_container_client(self.config.TEST_MULTI_PARTITION_CONTAINER_ID)
        await created_collection.upsert_item(body={'pk': 'pk', 'id': str(uuid.uuid4())})
        await created_collection.upsert_item(body={'pk': 'pk', 'id': str(uuid.uuid4())})

        query_iterable = created_collection.query_items(
            query='SELECT * from c',
            partition_key='pk',
            max_item_count=1,
        )
        pager = query_iterable.by_page()
        await pager.__anext__()
        token = pager.continuation_token

        assert token is not None
        assert _decode_token(token) is None


    async def test_full_pk_legacy_replay_resumes_same_page_async(self):
        created_collection = self.created_db.get_container_client(self.config.TEST_MULTI_PARTITION_CONTAINER_ID)
        await created_collection.upsert_item(body={'pk': 'pk', 'id': str(uuid.uuid4())})
        await created_collection.upsert_item(body={'pk': 'pk', 'id': str(uuid.uuid4())})

        query_iterable = created_collection.query_items(
            query='SELECT * from c',
            partition_key='pk',
            max_item_count=1,
        )
        pager = query_iterable.by_page()
        await pager.__anext__()
        token = pager.continuation_token
        second_page = [item async for item in await pager.__anext__()][0]

        assert token is not None
        assert _decode_token(token) is None

        replay_pager = query_iterable.by_page(token)
        replay_second_page = [item async for item in await replay_pager.__anext__()][0]
        assert second_page['id'] == replay_second_page['id']


    async def test_cross_partition_query_with_none_partition_key_async(self):
        created_collection = self.created_db.get_container_client(self.config.TEST_MULTI_PARTITION_CONTAINER_ID)
        document_definition = {'pk': 'pk1', 'id': str(uuid.uuid4())}
        await created_collection.create_item(body=document_definition)
        document_definition = {'pk': 'pk2' , 'id': str(uuid.uuid4())}
        await created_collection.create_item(body=document_definition)

        query = 'SELECT * from c'
        query_iterable = created_collection.query_items(
            query=query,
            partition_key=None)

        assert len([item async for item in query_iterable]) >= 2

    async def test_value_max_query_results_async(self):
        container = self.created_db.get_container_client(self.config.TEST_MULTI_PARTITION_CONTAINER_ID)
        await container.create_item(
            {"id": str(uuid.uuid4()), "isComplete": True, "version": 3, "lookupVersion": "console_version"})
        await container.create_item(
            {"id": str(uuid.uuid4()), "isComplete": True, "version": 2, "lookupVersion": "console_version"})
        query = "Select value max(c.version) FROM c where c.isComplete = true and c.lookupVersion = @lookupVersion"
        query_results = container.query_items(query, parameters=[
            {"name": "@lookupVersion", "value": "console_version"}
        ])
        item_list = [item async for item in query_results]
        assert len(item_list) == 1
        assert item_list[0] == 3

    async def test_continuation_token_size_limit_query_async(self):
        container = self.created_db.get_container_client(self.config.TEST_MULTI_PARTITION_CONTAINER_ID)
        for i in range(1, 1000):
            await container.create_item(body=dict(pk='123', id=str(uuid.uuid4()), some_value=str(i % 3)))
        query = "Select * from c where c.some_value='2'"
        response_query = container.query_items(query, partition_key='123', max_item_count=100,
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

    async def test_cosmos_query_retryable_error_async(self):
        async def query_items(database):
            # Tests to make sure 429 exception is surfaced when retries run out in the first page of a query.
            try:
                # create_container here is control-plane. Using key_db (sync, key-auth).
                # Container access for data is through the async AAD client.
                self.key_db.create_container(
                    id="query_retryable_error_test", partition_key=PartitionKey(path="/pk"), offer_throughput=400
                )
                container = database.get_container_client("query_retryable_error_test")
            except exceptions.CosmosResourceExistsError:
                container = database.get_container_client("query_retryable_error_test")
            query = "SELECT * FROM c"
            try:
                query_iterable = [d async for d in container.query_items(query, max_item_count=10)]
                if len(query_iterable) == 0:
                    # Query should not return empty if it has items to query on a retryable exception is raised
                    pytest.fail("Expected 429 Exception.")
            except exceptions.CosmosHttpResponseError as ex:
                # A retryable exception should be surfaced when retries run out
                assert ex.status_code == 429

        self._create_container_if_not_exists_for_test("query_retryable_error_test", PartitionKey(path="/pk"))
        created_collection = self.created_db.get_container_client("query_retryable_error_test")
        # Created items to query
        for _ in range(150):
            partition_key = 'pk' + str(uuid.uuid4())
            item = {
                'id': 'item' + str(uuid.uuid4()),
                'partitionKey': partition_key,
                'content': 'This is some random content',
            }

            try:
                await created_collection.upsert_item(item)
            except exceptions.CosmosHttpResponseError as e:
                pytest.fail(e)
        # Set retry options to fail much more easily to avoid too much concurrency
        retry_options = RetryOptions(max_retry_attempt_count=1,
                                     fixed_retry_interval_in_milliseconds=1, max_wait_time_in_seconds=1)
        old_retry = self.client.client_connection.connection_policy.RetryOptions
        self.client.client_connection.connection_policy.RetryOptions = retry_options
        self._create_container_if_not_exists_for_test("query_retryable_error_test", PartitionKey(path="/pk"))
        # Force a 429 exception by having multiple concurrent queries.
        num_queries = 4
        await gather(*[query_items(self.created_db) for _ in range(num_queries)])

        self.client.client_connection.connection_policy.RetryOptions = old_retry
        self._delete_container_for_test("query_retryable_error_test")

    async def test_query_request_params_none_retry_policy_async(self):
        container_id = "query_request_params_none_retry_policy_" + str(uuid.uuid4())
        created_collection = self._create_container_if_not_exists_for_test(
            container_id, PartitionKey(path="/pk"))
        items = [
            {'id': str(uuid.uuid4()), 'pk': 'test', 'val': 5},
            {'id': str(uuid.uuid4()), 'pk': 'test', 'val': 5},
            {'id': str(uuid.uuid4()), 'pk': 'test', 'val': 5}
        ]

        for item in items:
            await created_collection.create_item(body=item)

        self.OriginalExecuteFunction = retry_utility.ExecuteFunctionAsync
        # Test session retry will properly push the exception when retries run out
        retry_utility.ExecuteFunctionAsync = self._MockExecuteFunctionSessionRetry
        try:
            query = "SELECT * FROM c"
            items = created_collection.query_items(
                query=query,
            )
            fetch_results = [item async for item in items]
            pytest.fail("Expected 404.1002 Exception.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == http_constants.StatusCodes.NOT_FOUND
            assert e.sub_status == http_constants.SubStatusCodes.READ_SESSION_NOTAVAILABLE

        # Test endpoint discovery retry
        retry_utility.ExecuteFunctionAsync = self._MockExecuteFunctionEndPointRetry
        _endpoint_discovery_retry_policy.EndpointDiscoveryRetryPolicy.Max_retry_attempt_count = 3
        _endpoint_discovery_retry_policy.EndpointDiscoveryRetryPolicy.Retry_after_in_milliseconds = 10
        try:
            query = "SELECT * FROM c"
            items = created_collection.query_items(
                query=query,
            )
            fetch_results = [item async for item in items]
            pytest.fail("Expected 403.3 Exception.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == http_constants.StatusCodes.FORBIDDEN
            assert e.sub_status == http_constants.SubStatusCodes.WRITE_FORBIDDEN
        _endpoint_discovery_retry_policy.EndpointDiscoveryRetryPolicy.Max_retry_attempt_count = 120
        _endpoint_discovery_retry_policy.EndpointDiscoveryRetryPolicy.Retry_after_in_milliseconds = 1000

        # Finally lets test timeout failover retry
        retry_utility.ExecuteFunctionAsync = self._MockExecuteFunctionTimeoutFailoverRetry
        try:
            query = "SELECT * FROM c"
            items = created_collection.query_items(
                query=query,
            )
            fetch_results = [item async for item in items]
            pytest.fail("Expected 408 Exception.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == http_constants.StatusCodes.REQUEST_TIMEOUT
        retry_utility.ExecuteFunctionAsync = self.OriginalExecuteFunction
        self._delete_container_for_test(container_id)

    async def test_partitioned_query_response_hook_async(self):
        container_id = "query_response_hook_test" + str(uuid.uuid4())
        created_collection = self._create_container_if_not_exists_for_test(
            container_id, PartitionKey(path="/pk"))
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

        response_hook = test_config.ResponseHookCaller()
        item_list = [item async for item in created_collection.query_items("select * from c", partition_key="0", response_hook=response_hook)]
        assert len(item_list) == 3
        assert response_hook.count == 1
        self._delete_container_for_test(container_id)

    async def test_query_pagination_with_max_item_count_async(self):
        """Test pagination showing per-page limits and total results counting."""
        container_id = "pagination_test_" + str(uuid.uuid4())
        created_collection = self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        
        total_items = 20
        partition_key_value = "test_pk"
        for i in range(total_items):
            document_definition = {
                'pk': partition_key_value,
                'id': f'item_{i}',
                'value': i
            }
            await created_collection.create_item(body=document_definition)
        
        max_items_per_page = 7
        query = "SELECT * FROM c WHERE c.pk = @pk ORDER BY c['value']"
        query_iterable = created_collection.query_items(
            query=query,
            parameters=[{"name": "@pk", "value": partition_key_value}],
            partition_key=partition_key_value,
            max_item_count=max_items_per_page
        )
        
        all_fetched_results = []
        page_count = 0
        item_pages = query_iterable.by_page()
        
        async for page in item_pages:
            page_count += 1
            items_in_page = [item async for item in page]
            all_fetched_results.extend(items_in_page)
            assert len(items_in_page) <= max_items_per_page
        
        assert len(all_fetched_results) == total_items
        assert page_count == 3
        
        for i, item in enumerate(all_fetched_results):
            assert item['value'] == i
        
        self._delete_container_for_test(container_id)
    
    async def test_query_pagination_without_max_item_count_async(self):
        """Test pagination behavior without specifying max_item_count."""
        container_id = "pagination_no_max_test_" + str(uuid.uuid4())
        created_collection = self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        
        total_items = 15
        partition_key_value = "test_pk_2"
        for i in range(total_items):
            document_definition = {
                'pk': partition_key_value,
                'id': f'item_{i}',
                'value': i
            }
            await created_collection.create_item(body=document_definition)
        
        query = "SELECT * FROM c WHERE c.pk = @pk"
        query_iterable = created_collection.query_items(
            query=query,
            parameters=[{"name": "@pk", "value": partition_key_value}],
            partition_key=partition_key_value
        )
        
        all_results = [item async for item in query_iterable]
        assert len(all_results) == total_items
        
        self._delete_container_for_test(container_id)

    async def _MockExecuteFunctionSessionRetry(self, function, *args, **kwargs):
        if args:
            if args[1].operation_type == 'SqlQuery':
                ex_to_raise = exceptions.CosmosHttpResponseError(status_code=http_constants.StatusCodes.NOT_FOUND,
                                                                 message="Read Session is Not Available")
                ex_to_raise.sub_status = http_constants.SubStatusCodes.READ_SESSION_NOTAVAILABLE
                raise ex_to_raise
        return await self.OriginalExecuteFunction(function, *args, **kwargs)

    async def _MockExecuteFunctionEndPointRetry(self, function, *args, **kwargs):
        if args:
            if args[1].operation_type == 'SqlQuery':
                ex_to_raise = exceptions.CosmosHttpResponseError(status_code=http_constants.StatusCodes.FORBIDDEN,
                                                                 message="End Point Discovery")
                ex_to_raise.sub_status = http_constants.SubStatusCodes.WRITE_FORBIDDEN
                raise ex_to_raise
        return await self.OriginalExecuteFunction(function, *args, **kwargs)

    async def _MockExecuteFunctionTimeoutFailoverRetry(self, function, *args, **kwargs):
        if args:
            if args[1].operation_type == 'SqlQuery':
                ex_to_raise = exceptions.CosmosHttpResponseError(status_code=http_constants.StatusCodes.REQUEST_TIMEOUT,
                                                                 message="Timeout Failover")
                raise ex_to_raise
        return await self.OriginalExecuteFunction(function, *args, **kwargs)

    async def test_query_items_with_parameters_none_async(self):
        """Test that query_items handles parameters=None correctly (issue #43662)."""
        container_id = "test_params_none_" + str(uuid.uuid4())
        created_collection = self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        
        # Create test documents
        doc1_id = 'doc1_' + str(uuid.uuid4())
        doc2_id = 'doc2_' + str(uuid.uuid4())
        await created_collection.create_item(body={'pk': 'pk1', 'id': doc1_id, 'value1': 1})
        await created_collection.create_item(body={'pk': 'pk2', 'id': doc2_id, 'value1': 2})

        # Test 1: Explicitly passing parameters=None should not cause TypeError
        query = 'SELECT * FROM c'
        query_iterable = created_collection.query_items(
            query=query,
            parameters=None
        )
        results = [item async for item in query_iterable]
        assert len(results) == 2

        # Test 2: parameters=None with partition_key should work
        query_iterable = created_collection.query_items(
            query=query,
            parameters=None,
            partition_key='pk1'
        )
        results = [item async for item in query_iterable]
        assert len(results) == 1
        assert results[0]['id'] == doc1_id

        # Test 3: Verify parameterized query still works with actual parameters
        query_with_params = 'SELECT * FROM c WHERE c.value1 = @value'
        query_iterable = created_collection.query_items(
            query=query_with_params,
            parameters=[{'name': '@value', 'value': 2}]
        )
        results = [item async for item in query_iterable]
        assert len(results) == 1
        assert results[0]['id'] == doc2_id

        # Test 4: Query without parameters argument should work (default behavior)
        query_iterable = created_collection.query_items(
            query=query
        )
        results = [item async for item in query_iterable]
        assert len(results) == 2

        self._delete_container_for_test(container_id)

    async def test_query_items_parameters_none_with_options_async(self):
        """Test parameters=None works with various query options."""
        container_id = "test_params_none_opts_" + str(uuid.uuid4())
        created_collection = self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        
        # Create multiple test documents
        for i in range(5):
            doc_id = f'doc_{i}_' + str(uuid.uuid4())
            await created_collection.create_item(body={'pk': 'test', 'id': doc_id, 'index': i})

        # Test with parameters=None and max_item_count
        query = 'SELECT * FROM c ORDER BY c.index'
        query_iterable = created_collection.query_items(
            query=query,
            parameters=None,
            partition_key='test',
            max_item_count=2
        )
        
        # Verify pagination works
        page_count = 0
        total_items = 0
        async for page in query_iterable.by_page():
            page_count += 1
            items = [item async for item in page]
            total_items += len(items)
            assert len(items) <= 2
        
        assert total_items == 5
        assert page_count >= 2  # Should have multiple pages

        # Test with parameters=None and populate_query_metrics
        query_iterable = created_collection.query_items(
            query=query,
            parameters=None,
            partition_key='test',
            populate_query_metrics=True
        )
        results = [item async for item in query_iterable]
        assert len(results) == 5
        
        # Verify query metrics were populated
        metrics_header_name = 'x-ms-documentdb-query-metrics'
        assert metrics_header_name in created_collection.client_connection.last_response_headers

        self._delete_container_for_test(container_id)


    # Async variants of the by_page() read_timeout coverage. Verify
    # that the per-request and client-level read_timeout reach every
    # page fetch when results are walked one page at a time.

    def _capture_pipeline_read_timeouts_async(self):
        # Wraps the outgoing async HTTP call so each request records
        # its URL and the read_timeout the SDK passed along with it.
        captured = []
        original = _asynchronous_request._PipelineRunFunction

        async def _wrapper(pipeline_client, request, **kwargs):
            captured.append((str(request.url), kwargs.get("read_timeout")))
            return await original(pipeline_client, request, **kwargs)

        return captured, patch.object(
            _asynchronous_request, "_PipelineRunFunction", side_effect=_wrapper
        )

    @staticmethod
    def _doc_call_timeouts(captured):
        # Keep only document page fetches. Other internal calls have
        # their own timeout settings and are not part of these tests.
        return [rt for (url, rt) in captured if "/docs" in url]

    async def test_read_timeout_propagates_through_by_page_paging_async(self):
        # Per-request read_timeout should reach every page fetch across
        # single-partition queries, cross-partition queries, full reads,
        # and change feeds when results are walked via by_page().
        container_id = "by_page_read_timeout_async_" + str(uuid.uuid4())
        container = self._create_container_for_test(
            container_id, PartitionKey(path="/pk"), offer_throughput=11000,
        )
        try:
            for i in range(6):
                await container.create_item({"id": f"item_{i}_{uuid.uuid4()}", "pk": i % 2, "data": i})

            request_level_timeout = 25

            # Single-partition query paged with by_page().
            captured, ctx = self._capture_pipeline_read_timeouts_async()
            with ctx:
                pages = container.query_items(
                    query="SELECT * FROM c WHERE c.pk = @pk",
                    parameters=[{"name": "@pk", "value": 0}],
                    partition_key=0,
                    max_item_count=1,
                    read_timeout=request_level_timeout,
                ).by_page()
                async for page in pages:
                    [item async for item in page]
            doc_timeouts = self._doc_call_timeouts(captured)
            self.assertGreater(len(doc_timeouts), 0, "expected at least one page fetch")
            self.assertTrue(
                all(rt == request_level_timeout for rt in doc_timeouts),
                f"single-partition by_page() dropped read_timeout on some pages: {doc_timeouts}",
            )

            # Cross-partition query paged with by_page().
            captured, ctx = self._capture_pipeline_read_timeouts_async()
            with ctx:
                pages = container.query_items(
                    query="SELECT * FROM c",
                    max_item_count=1,
                    read_timeout=request_level_timeout,
                ).by_page()
                async for page in pages:
                    [item async for item in page]
            doc_timeouts = self._doc_call_timeouts(captured)
            self.assertGreater(len(doc_timeouts), 0)
            self.assertTrue(
                all(rt == request_level_timeout for rt in doc_timeouts),
                f"cross-partition by_page() dropped read_timeout on some pages: {doc_timeouts}",
            )

            # read_all_items paged with by_page().
            captured, ctx = self._capture_pipeline_read_timeouts_async()
            with ctx:
                pages = container.read_all_items(
                    max_item_count=2,
                    read_timeout=request_level_timeout,
                ).by_page()
                async for page in pages:
                    [item async for item in page]
            doc_timeouts = self._doc_call_timeouts(captured)
            self.assertGreater(len(doc_timeouts), 0)
            self.assertTrue(
                all(rt == request_level_timeout for rt in doc_timeouts),
                f"read_all_items by_page() dropped read_timeout on some pages: {doc_timeouts}",
            )

            # Change feed paged with by_page().
            captured, ctx = self._capture_pipeline_read_timeouts_async()
            with ctx:
                pages = container.query_items_change_feed(
                    start_time="Beginning",
                    max_item_count=2,
                    read_timeout=request_level_timeout,
                ).by_page()
                async for page in pages:
                    [item async for item in page]
            doc_timeouts = self._doc_call_timeouts(captured)
            self.assertGreater(len(doc_timeouts), 0)
            self.assertTrue(
                all(rt == request_level_timeout for rt in doc_timeouts),
                f"change feed by_page() dropped read_timeout on some pages: {doc_timeouts}",
            )
        finally:
            self._delete_container_for_test(container_id)

    async def test_client_level_read_timeout_propagates_through_by_page_paging_async(self):
        # When the async client is built with a read_timeout and the
        # caller does not pass a per-request one, that client value
        # should still reach every page fetch.
        container_id = "by_page_client_read_timeout_async_" + str(uuid.uuid4())
        container = self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        try:
            for i in range(4):
                await container.create_item({"id": f"item_{i}_{uuid.uuid4()}", "pk": "p", "data": i})

            client_timeout = 22

            async with test_config.TestConfig.create_data_client_async(read_timeout=client_timeout) as ct_client:
                ct_container = ct_client.get_database_client(self.TEST_DATABASE_ID) \
                                        .get_container_client(container_id)

                captured, ctx = self._capture_pipeline_read_timeouts_async()
                with ctx:
                    pages = ct_container.query_items(
                        query="SELECT * FROM c WHERE c.pk = @pk",
                        parameters=[{"name": "@pk", "value": "p"}],
                        partition_key="p",
                        max_item_count=1,
                    ).by_page()
                    async for page in pages:
                        [item async for item in page]
                doc_timeouts = self._doc_call_timeouts(captured)
                self.assertGreater(len(doc_timeouts), 0)
                self.assertTrue(
                    all(rt == client_timeout for rt in doc_timeouts),
                    f"client-level read_timeout did not reach all pages: {doc_timeouts}",
                )
        finally:
            self._delete_container_for_test(container_id)

    async def test_client_level_short_read_timeout_propagates_on_by_page_async(self):
        # A tiny client-level read_timeout should still flow through to
        # by_page() fetches. Avoid asserting wall-clock timeout failure
        # since timer granularity differs across environments.
        container_id = "by_page_short_client_async_" + str(uuid.uuid4())
        container = self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        try:
            for i in range(3):
                await container.create_item({"id": f"item_{i}_{uuid.uuid4()}", "pk": "p", "data": i})

            short_timeout = 0.000000000001
            async with test_config.TestConfig.create_data_client_async(read_timeout=short_timeout) as short_client:
                short_container = short_client.get_database_client(self.TEST_DATABASE_ID) \
                                              .get_container_client(container_id)

                captured = []
                original = _asynchronous_request._PipelineRunFunction

                async def _capture_and_clamp_timeout(pipeline_client, request, **kwargs):
                    captured.append((str(request.url), kwargs.get("read_timeout")))
                    if kwargs.get("read_timeout") is not None and kwargs["read_timeout"] < 1:
                        kwargs = dict(kwargs)
                        kwargs["read_timeout"] = 1
                    return await original(pipeline_client, request, **kwargs)

                with patch.object(
                    _asynchronous_request, "_PipelineRunFunction", side_effect=_capture_and_clamp_timeout
                ):
                    pages = short_container.query_items(
                        query="SELECT * FROM c WHERE c.pk = @pk",
                        parameters=[{"name": "@pk", "value": "p"}],
                        partition_key="p",
                        max_item_count=1,
                    ).by_page()
                    async for page in pages:
                        [item async for item in page]
                doc_timeouts = [rt for (url, rt) in captured if "/docs" in url]
                self.assertGreater(len(doc_timeouts), 0)
                self.assertTrue(
                    all(rt == short_timeout for rt in doc_timeouts),
                    f"client-level short read_timeout did not reach all pages: {doc_timeouts}",
                )
        finally:
            self._delete_container_for_test(container_id)

    # Aggregate queries (COUNT, SUM, MAX) take a separate execution path
    # from regular queries. The tests below confirm a per-request
    # read_timeout still reaches every page fetch on that path. GROUP BY
    # is excluded because the Python SDK does not declare it as
    # supported and the gateway rejects those queries. ``c.amount`` is
    # used instead of ``c.value`` because ``VALUE`` is a SQL keyword.

    async def test_read_timeout_propagates_through_by_page_value_count_aggregate_async(self):
        container_id = "by_page_count_agg_async_" + str(uuid.uuid4())
        container = self._create_container_for_test(
            container_id, PartitionKey(path="/pk"), offer_throughput=11000,
        )
        try:
            for i in range(6):
                await container.create_item({"id": f"item_{i}_{uuid.uuid4()}", "pk": i % 2, "amount": i + 10})

            request_level_timeout = 25
            captured, ctx = self._capture_pipeline_read_timeouts_async()
            with ctx:
                pages = container.query_items(
                    query="SELECT VALUE COUNT(1) FROM c",
                    max_item_count=1,
                    read_timeout=request_level_timeout,
                ).by_page()
                async for page in pages:
                    [item async for item in page]
            doc_timeouts = self._doc_call_timeouts(captured)
            self.assertGreater(len(doc_timeouts), 0, "expected at least one page fetch")
            self.assertTrue(
                all(rt == request_level_timeout for rt in doc_timeouts),
                f"VALUE COUNT aggregate by_page() dropped read_timeout on some pages: {doc_timeouts}",
            )
        finally:
            self._delete_container_for_test(container_id)

    async def test_read_timeout_propagates_through_by_page_value_sum_aggregate_async(self):
        container_id = "by_page_sum_agg_async_" + str(uuid.uuid4())
        container = self._create_container_for_test(
            container_id, PartitionKey(path="/pk"), offer_throughput=11000,
        )
        try:
            for i in range(6):
                await container.create_item({"id": f"item_{i}_{uuid.uuid4()}", "pk": i % 2, "amount": i + 10})

            request_level_timeout = 25
            captured, ctx = self._capture_pipeline_read_timeouts_async()
            with ctx:
                pages = container.query_items(
                    query="SELECT VALUE SUM(c.amount) FROM c WHERE IS_NUMBER(c.amount)",
                    max_item_count=1,
                    read_timeout=request_level_timeout,
                ).by_page()
                async for page in pages:
                    [item async for item in page]
            doc_timeouts = self._doc_call_timeouts(captured)
            self.assertGreater(len(doc_timeouts), 0)
            self.assertTrue(
                all(rt == request_level_timeout for rt in doc_timeouts),
                f"VALUE SUM aggregate by_page() dropped read_timeout on some pages: {doc_timeouts}",
            )
        finally:
            self._delete_container_for_test(container_id)

    async def test_read_timeout_propagates_through_by_page_value_max_aggregate_async(self):
        # MAX exercises the same MultiExecutionAggregator path GROUP BY
        # would, but is actually supported by the Python SDK.
        container_id = "by_page_max_agg_async_" + str(uuid.uuid4())
        container = self._create_container_for_test(
            container_id, PartitionKey(path="/pk"), offer_throughput=11000,
        )
        try:
            for i in range(6):
                await container.create_item({"id": f"item_{i}_{uuid.uuid4()}", "pk": i % 2, "amount": i + 10})

            request_level_timeout = 25
            captured, ctx = self._capture_pipeline_read_timeouts_async()
            with ctx:
                pages = container.query_items(
                    query="SELECT VALUE MAX(c.amount) FROM c",
                    max_item_count=1,
                    read_timeout=request_level_timeout,
                ).by_page()
                async for page in pages:
                    [item async for item in page]
            doc_timeouts = self._doc_call_timeouts(captured)
            self.assertGreater(len(doc_timeouts), 0)
            self.assertTrue(
                all(rt == request_level_timeout for rt in doc_timeouts),
                f"VALUE MAX aggregate by_page() dropped read_timeout on some pages: {doc_timeouts}",
            )
        finally:
            self._delete_container_for_test(container_id)

    async def test_client_level_read_timeout_propagates_through_aggregate_by_page_async(self):
        # Async mirror of test_client_level_read_timeout_propagates_through_aggregate_by_page.
        container_id = "by_page_client_agg_async_" + str(uuid.uuid4())
        container = self._create_container_for_test(
            container_id, PartitionKey(path="/pk"), offer_throughput=11000,
        )
        try:
            for i in range(6):
                await container.create_item({"id": f"item_{i}_{uuid.uuid4()}", "pk": i % 2, "amount": i + 10})

            client_timeout = 22

            async with test_config.TestConfig.create_data_client_async(read_timeout=client_timeout) as ct_client:
                ct_container = ct_client.get_database_client(self.TEST_DATABASE_ID) \
                                        .get_container_client(container_id)

                for query in (
                    "SELECT VALUE COUNT(1) FROM c",
                    "SELECT VALUE SUM(c.amount) FROM c WHERE IS_NUMBER(c.amount)",
                    "SELECT VALUE MAX(c.amount) FROM c",
                ):
                    captured, ctx = self._capture_pipeline_read_timeouts_async()
                    with ctx:
                        pages = ct_container.query_items(
                            query=query,
                            max_item_count=1,
                        ).by_page()
                        async for page in pages:
                            [item async for item in page]
                    doc_timeouts = self._doc_call_timeouts(captured)
                    self.assertGreater(
                        len(doc_timeouts), 0,
                        f"no /docs/ fetches for aggregate query {query!r}",
                    )
                    # See sync sibling test for why ``None`` is tolerated.
                    non_none = [rt for rt in doc_timeouts if rt is not None]
                    self.assertGreater(
                        len(non_none), 0,
                        f"every /docs/ call dropped read_timeout for aggregate {query!r}",
                    )
                    self.assertTrue(
                        all(rt == client_timeout for rt in non_none),
                        f"client-level read_timeout did not reach all pages for "
                        f"aggregate {query!r}: {doc_timeouts}",
                    )
        finally:
            self._delete_container_for_test(container_id)

    # by_page() coverage for the outer timeout, connection_timeout,
    # resume from a continuation token, and the cross-partition AVG
    # error. See the sync siblings in test_query.py for the rationale.

    def _capture_pipeline_kwarg_async(self, kwarg_name):
        captured = []
        original = _asynchronous_request._PipelineRunFunction

        async def _wrapper(pipeline_client, request, **kwargs):
            captured.append((str(request.url), kwargs.get(kwarg_name)))
            return await original(pipeline_client, request, **kwargs)

        return captured, patch.object(
            _asynchronous_request, "_PipelineRunFunction", side_effect=_wrapper,
        )

    async def test_outer_timeout_propagates_through_by_page_paging_async(self):
        # The outer wall-clock timeout must reach every page fetch when
        # a cross-partition query is walked one page at a time.
        container_id = "by_page_outer_timeout_async_" + str(uuid.uuid4())
        container = self._create_container_for_test(
            container_id, PartitionKey(path="/pk"), offer_throughput=11000,
        )
        try:
            for i in range(6):
                await container.create_item(
                    {"id": f"item_{i}_{uuid.uuid4()}", "pk": i % 2, "data": i}
                )

            outer_timeout = 15
            captured, ctx = self._capture_pipeline_kwarg_async("timeout")
            with ctx:
                pages = container.query_items(
                    query="SELECT * FROM c",
                    max_item_count=1,
                    timeout=outer_timeout,
                ).by_page()
                async for page in pages:
                    [item async for item in page]
            doc_values = [t for (url, t) in captured if "/docs" in url]
            self.assertGreater(len(doc_values), 0)
            non_none = [t for t in doc_values if t is not None]
            self.assertGreater(len(non_none), 0)
            for t in non_none:
                self.assertLessEqual(t, outer_timeout)
        finally:
            self._delete_container_for_test(container_id)

    async def test_connection_timeout_propagates_through_by_page_paging_async(self):
        # connection_timeout is per-attempt; it must reach every page
        # fetch as the same exact value the caller passed in.
        container_id = "by_page_conn_timeout_async_" + str(uuid.uuid4())
        container = self._create_container_for_test(
            container_id, PartitionKey(path="/pk"), offer_throughput=11000,
        )
        try:
            for i in range(6):
                await container.create_item(
                    {"id": f"item_{i}_{uuid.uuid4()}", "pk": i % 2, "data": i}
                )

            connection_timeout = 27
            captured, ctx = self._capture_pipeline_kwarg_async("connection_timeout")
            with ctx:
                pages = container.query_items(
                    query="SELECT * FROM c",
                    max_item_count=1,
                    connection_timeout=connection_timeout,
                ).by_page()
                async for page in pages:
                    [item async for item in page]
            doc_values = [t for (url, t) in captured if "/docs" in url]
            self.assertGreater(len(doc_values), 0)
            self.assertTrue(all(t == connection_timeout for t in doc_values))
        finally:
            self._delete_container_for_test(container_id)

    async def test_avg_aggregate_by_page_raises_value_error_cross_partition_async(self):
        # A VALUE AVG query across multiple partitions must raise
        # ValueError. A single-partition AVG is verified as a control.
        container_id = "by_page_avg_cross_async_" + str(uuid.uuid4())
        container = self._create_container_for_test(
            container_id, PartitionKey(path="/pk"), offer_throughput=11000,
        )
        try:
            for i in range(20):
                await container.create_item(
                    {"id": f"item_{i}_{uuid.uuid4()}", "pk": f"pk_{i}", "amount": i + 10}
                )

            # A feed range that covers the full hash space forces the
            # query to fan out across every physical partition.
            full_range = test_config.create_range(
                range_min="",
                range_max="FF",
                is_min_inclusive=True,
                is_max_inclusive=False,
            )
            feed_range = test_config.create_feed_range_in_dict(full_range)

            with self.assertRaises(ValueError) as cm:
                pages = container.query_items(
                    query="SELECT VALUE AVG(c.amount) FROM c",
                    feed_range=feed_range,
                    max_item_count=1,
                ).by_page()
                async for page in pages:
                    [item async for item in page]
            self.assertIn("AVG", str(cm.exception).upper())

            # Control: a single-partition AVG must still succeed.
            single_pages = container.query_items(
                query="SELECT VALUE AVG(c.amount) FROM c WHERE c.pk = @pk",
                parameters=[{"name": "@pk", "value": "pk_0"}],
                partition_key="pk_0",
                max_item_count=1,
            ).by_page()
            single_result = []
            async for page in single_pages:
                async for item in page:
                    single_result.append(item)
            self.assertEqual(len(single_result), 1)
        finally:
            self._delete_container_for_test(container_id)

    async def test_read_timeout_propagates_through_by_page_resume_async(self):
        # When the caller resumes paging on a new pager built from a
        # continuation token, the per-request read_timeout must reach
        # every page fetch on the resumed pager too.
        container_id = "by_page_resume_timeout_async_" + str(uuid.uuid4())
        container = self._create_container_for_test(
            container_id, PartitionKey(path="/pk"), offer_throughput=11000,
        )
        try:
            for i in range(10):
                await container.create_item(
                    {"id": f"item_{i}_{uuid.uuid4()}", "pk": "p", "data": i}
                )

            request_level_timeout = 19

            # Pull one page and capture its continuation token. This
            # initial call runs outside the capture context because we
            # only want to assert on the resumed pager.
            first_pages = container.query_items(
                query="SELECT * FROM c WHERE c.pk = @pk",
                parameters=[{"name": "@pk", "value": "p"}],
                partition_key="p",
                max_item_count=2,
            ).by_page()
            first_page = await first_pages.__anext__()
            _ = [item async for item in first_page]
            continuation = first_pages.continuation_token
            self.assertIsNotNone(continuation)

            captured, ctx = self._capture_pipeline_read_timeouts_async()
            with ctx:
                resumed_pages = container.query_items(
                    query="SELECT * FROM c WHERE c.pk = @pk",
                    parameters=[{"name": "@pk", "value": "p"}],
                    partition_key="p",
                    max_item_count=2,
                    read_timeout=request_level_timeout,
                ).by_page(continuation_token=continuation)
                async for page in resumed_pages:
                    [item async for item in page]
            doc_timeouts = self._doc_call_timeouts(captured)
            self.assertGreater(len(doc_timeouts), 0)
            self.assertTrue(all(rt == request_level_timeout for rt in doc_timeouts))
        finally:
            self._delete_container_for_test(container_id)


if __name__ == '__main__':
    unittest.main()
