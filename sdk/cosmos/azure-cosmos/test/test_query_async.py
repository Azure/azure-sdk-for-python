# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import os
import unittest
import uuid
from asyncio import gather

import pytest

import azure.cosmos.aio._retry_utility_async as retry_utility
import azure.cosmos.exceptions as exceptions
import test_config
from azure.cosmos import http_constants, _endpoint_discovery_retry_policy
from azure.cosmos._execution_context.query_execution_info import _PartitionedQueryExecutionInfo
from azure.cosmos._retry_options import RetryOptions
from azure.cosmos.aio import CosmosClient, DatabaseProxy, ContainerProxy
from azure.cosmos.documents import _DistinctType
from azure.cosmos.partition_key import PartitionKey

@pytest.mark.cosmosQuery
class TestQueryAsync(unittest.IsolatedAsyncioTestCase):
    """Test to ensure escaping of non-ascii characters from partition key"""

    created_db: DatabaseProxy = None
    created_container: ContainerProxy = None
    client: CosmosClient = None
    config = test_config.TestConfig
    TEST_CONTAINER_ID = config.TEST_MULTI_PARTITION_CONTAINER_ID
    TEST_DATABASE_ID = config.TEST_DATABASE_ID
    host = config.host
    masterKey = config.masterKey
    connectionPolicy = config.connectionPolicy

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

    async def asyncSetUp(self):
        self.client = CosmosClient(self.host, self.masterKey)
        self.created_db = self.client.get_database_client(self.TEST_DATABASE_ID)
        if self.host == "https://localhost:8081/":
            os.environ["AZURE_COSMOS_DISABLE_NON_STREAMING_ORDER_BY"] = "True"

    async def asyncTearDown(self):
        await self.client.close()

    async def test_first_and_last_slashes_trimmed_for_query_string_async(self):
        created_collection = await self.created_db.create_container(
            str(uuid.uuid4()), PartitionKey(path="/pk"))
        doc_id = 'myId' + str(uuid.uuid4())
        document_definition = {'pk': 'pk', 'id': doc_id}
        await created_collection.create_item(body=document_definition)

        query = 'SELECT * from c'
        query_iterable = created_collection.query_items(
            query=query,
            partition_key='pk'
        )
        iter_list = [item async for item in query_iterable]
        assert iter_list[0]['id'] == doc_id

        await self.created_db.delete_container(created_collection.id)

    @pytest.mark.asyncio
    async def test_populate_query_metrics_async(self):
        created_collection = await self.created_db.create_container(
            "query_metrics_test" + str(uuid.uuid4()),
            PartitionKey(path="/pk"))
        doc_id = 'MyId' + str(uuid.uuid4())
        document_definition = {'pk': 'pk', 'id': doc_id}
        await created_collection.create_item(body=document_definition)

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

        await self.created_db.delete_container(created_collection.id)

    async def test_populate_index_metrics_async(self):
        created_collection = await self.created_db.create_container(
            "index_metrics_test" + str(uuid.uuid4()),
            PartitionKey(path="/pk"))
        doc_id = 'MyId' + str(uuid.uuid4())
        document_definition = {'pk': 'pk', 'id': doc_id}
        await created_collection.create_item(body=document_definition)

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
        expected_index_metrics = {'UtilizedSingleIndexes': [{'FilterExpression': '', 'IndexSpec': '/pk/?',
                                                             'FilterPreciseSet': True, 'IndexPreciseSet': True,
                                                             'IndexImpactScore': 'High'}],
                                  'PotentialSingleIndexes': [], 'UtilizedCompositeIndexes': [],
                                  'PotentialCompositeIndexes': []}
        assert expected_index_metrics == index_metrics

        await self.created_db.delete_container(created_collection.id)

    # TODO: Need to validate the query request count logic
    @pytest.mark.skip
    async def test_max_item_count_honored_in_order_by_query_async(self):
        created_collection = await self.created_db.create_container(str(uuid.uuid4()),
                                                                    PartitionKey(path="/pk"))
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

        await self.created_db.delete_container(created_collection.id)

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
        created_collection = await self.created_db.create_container("offset_limit_" + str(uuid.uuid4()),
                                                                    PartitionKey(path="/pk"))
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

        await self.created_db.delete_container(created_collection.id)

    async def test_distinct_async(self):
        created_database = self.created_db
        distinct_field = 'distinct_field'
        pk_field = "pk"
        different_field = "different_field"

        created_collection = await created_database.create_container(
            id='collection with composite index ' + str(uuid.uuid4()),
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
                                             results=self.config._get_distinct_docs(padded_docs, distinct_field, None,
                                                                                    False),
                                             is_select=True,
                                             fields=[distinct_field])

        await self.config._validate_distinct(created_collection=created_collection,
                                             query='SELECT distinct c.%s, c.%s from c' % (distinct_field, pk_field),
                                             # nosec
                                             results=self.config._get_distinct_docs(padded_docs, distinct_field,
                                                                                    pk_field, False),
                                             is_select=True,
                                             fields=[distinct_field, pk_field])

        await self.config._validate_distinct(created_collection=created_collection,
                                             query='SELECT distinct value c.%s from c' % distinct_field,  # nosec
                                             results=self.config._get_distinct_docs(padded_docs, distinct_field, None,
                                                                                    True),
                                             is_select=True,
                                             fields=[distinct_field])

        await self.config._validate_distinct(created_collection=created_collection,
                                             query='SELECT distinct c.%s from c' % different_field,  # nosec
                                             results=['None'],
                                             is_select=True,
                                             fields=[different_field])

        await created_database.delete_container(created_collection.id)

    async def test_distinct_on_different_types_and_field_orders_async(self):
        created_collection = await self.created_db.create_container(
            id="test-distinct-container-" + str(uuid.uuid4()),
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

        await self.created_db.delete_container(created_collection.id)

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

    async def test_value_max_query_async(self):
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
                container = await database.create_container(
                    id="query_retryable_error_test", partition_key=PartitionKey(path="/pk"), offer_throughput=400
                )
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

        created_collection = await self.created_db.create_container_if_not_exists("query_retryable_error_test",
                                                                                  PartitionKey(path="/pk"))
        # Created items to query
        for _ in range(150):
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
                await created_collection.upsert_item(item)
            except exceptions.CosmosHttpResponseError as e:
                pytest.fail(e)
        # Set retry options to fail much more easily to avoid too much concurrency
        retry_options = RetryOptions(max_retry_attempt_count=1,
                                     fixed_retry_interval_in_milliseconds=1, max_wait_time_in_seconds=1)
        old_retry = self.client.client_connection.connection_policy.RetryOptions
        self.client.client_connection.connection_policy.RetryOptions = retry_options
        created_collection = await self.created_db.create_container_if_not_exists("query_retryable_error_test",
                                                                                  PartitionKey(path="/pk"))
        # Force a 429 exception by having multiple concurrent queries.
        num_queries = 4
        await gather(*[query_items(self.created_db) for _ in range(num_queries)])

        self.client.client_connection.connection_policy.RetryOptions = old_retry
        await self.created_db.delete_container(created_collection.id)

    async def test_query_request_params_none_retry_policy(self):
        created_collection = await self.created_db.create_container_if_not_exists(
            id="query_request_params_none_retry_policy_" + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk")
        )
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
                enable_cross_partition_query=True
            )
            fetch_results = [item async for item in items]
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 404
            assert e.sub_status == 1002

        # Test endpoint discovery retry
        retry_utility.ExecuteFunctionAsync = self._MockExecuteFunctionEndPointRetry
        _endpoint_discovery_retry_policy.EndpointDiscoveryRetryPolicy.Max_retry_attempt_count = 3
        _endpoint_discovery_retry_policy.EndpointDiscoveryRetryPolicy.Retry_after_in_milliseconds = 10
        try:
            query = "SELECT * FROM c"
            items = created_collection.query_items(
                query=query,
                enable_cross_partition_query=True
            )
            fetch_results = [item async for item in items]
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
                enable_cross_partition_query=True
            )
            fetch_results = [item async for item in items]
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == http_constants.StatusCodes.REQUEST_TIMEOUT
        retry_utility.ExecuteFunctionAsync = self.OriginalExecuteFunction
        await self.created_db.delete_container(created_collection.id)

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


if __name__ == '__main__':
    unittest.main()
