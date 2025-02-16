# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import os
import unittest
import uuid

import pytest

import azure.cosmos.aio._retry_utility_async as retry_utility
import azure.cosmos.exceptions as exceptions
import test_config
from azure.cosmos._execution_context.query_execution_info import _PartitionedQueryExecutionInfo
from azure.cosmos.aio import CosmosClient, DatabaseProxy, ContainerProxy
from azure.cosmos.documents import _DistinctType
from azure.cosmos.exceptions import CosmosHttpResponseError
from azure.cosmos.partition_key import PartitionKey

@pytest.mark.cosmosQuery
class TestQueryCrossPartitionAsync(unittest.IsolatedAsyncioTestCase):
    """Test to ensure escaping of non-ascii characters from partition key"""

    created_db: DatabaseProxy = None
    created_container: ContainerProxy = None
    client: CosmosClient = None
    config = test_config.TestConfig
    host = config.host
    masterKey = config.masterKey
    connectionPolicy = config.connectionPolicy
    TEST_CONTAINER_ID = str(uuid.uuid4())
    TEST_DATABASE_ID = config.TEST_DATABASE_ID

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
        self.created_container = await self.created_db.create_container(
            self.TEST_CONTAINER_ID,
            PartitionKey(path="/pk"),
            offer_throughput=test_config.TestConfig.THROUGHPUT_FOR_5_PARTITIONS)
        if self.host == "https://localhost:8081/":
            os.environ["AZURE_COSMOS_DISABLE_NON_STREAMING_ORDER_BY"] = "True"

    async def asyncTearDown(self):
        try:
            await self.created_db.delete_container(self.TEST_CONTAINER_ID)
        except CosmosHttpResponseError:
            pass
        finally:
            await self.client.close()

    async def test_first_and_last_slashes_trimmed_for_query_string_async(self):
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

    async def test_query_change_feed_with_pk_async(self):
        # The test targets partition #3
        partition_key = "pk"

        # Read change feed without passing any options
        query_iterable = self.created_container.query_items_change_feed()
        iter_list = [item async for item in query_iterable]
        assert len(iter_list) == 0

        # Read change feed from current should return an empty list
        query_iterable = self.created_container.query_items_change_feed(partition_key=partition_key)
        iter_list = [item async for item in query_iterable]
        assert len(iter_list) == 0
        if 'Etag' in self.created_container.client_connection.last_response_headers:
            assert self.created_container.client_connection.last_response_headers['Etag'] != ''
        elif 'etag' in self.created_container.client_connection.last_response_headers:
            assert self.created_container.client_connection.last_response_headers['etag'] != ''
        else:
            self.fail("No Etag or etag found in last response headers")

        # Read change feed from beginning should return an empty list
        query_iterable = self.created_container.query_items_change_feed(
            is_start_from_beginning=True,
            partition_key=partition_key
        )
        iter_list = [item async for item in query_iterable]
        assert len(iter_list) == 0
        if 'Etag' in self.created_container.client_connection.last_response_headers:
            continuation1 = self.created_container.client_connection.last_response_headers['Etag']
        elif 'etag' in self.created_container.client_connection.last_response_headers:
            continuation1 = self.created_container.client_connection.last_response_headers['etag']
        else:
            self.fail("No Etag or etag found in last response headers")
        assert continuation1 != ''

        # Create a document. Read change feed should return be able to read that document
        document_definition = {'pk': 'pk', 'id': 'doc1'}
        await self.created_container.create_item(body=document_definition)
        query_iterable = self.created_container.query_items_change_feed(
            is_start_from_beginning=True,
            partition_key=partition_key
        )
        iter_list = [item async for item in query_iterable]
        assert len(iter_list) == 1
        assert iter_list[0]['id'] == 'doc1'
        if 'Etag' in self.created_container.client_connection.last_response_headers:
            continuation2 = self.created_container.client_connection.last_response_headers['Etag']
        elif 'etag' in self.created_container.client_connection.last_response_headers:
            continuation2 = self.created_container.client_connection.last_response_headers['etag']
        else:
            self.fail("No Etag or etag found in last response headers")
        assert continuation2 != ''
        assert continuation2 != continuation1

        # Create two new documents. Verify that change feed contains the 2 new documents
        # with page size 1 and page size 100
        document_definition = {'pk': 'pk', 'id': 'doc2'}
        await self.created_container.create_item(body=document_definition)
        document_definition = {'pk': 'pk', 'id': 'doc3'}
        await self.created_container.create_item(body=document_definition)

        for pageSize in [2, 100]:
            # verify iterator
            query_iterable = self.created_container.query_items_change_feed(
                continuation=continuation2,
                max_item_count=pageSize,
                partition_key=partition_key)
            it = query_iterable.__aiter__()
            expected_ids = 'doc2.doc3.'
            actual_ids = ''
            async for item in it:
                actual_ids += item['id'] + '.'
            assert actual_ids == expected_ids

            # verify by_page
            # the options is not copied, therefore it need to be restored
            query_iterable = self.created_container.query_items_change_feed(
                continuation=continuation2,
                max_item_count=pageSize,
                partition_key=partition_key
            )
            count = 0
            expected_count = 2
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
        query_iterable = self.created_container.query_items_change_feed(
            is_start_from_beginning=True,
            partition_key=partition_key
        )
        expected_ids = ['doc1', 'doc2', 'doc3']
        it = query_iterable.__aiter__()
        for i in range(0, len(expected_ids)):
            doc = await it.__anext__()
            assert doc['id'] == expected_ids[i]
        if 'Etag' in self.created_container.client_connection.last_response_headers:
            continuation3 = self.created_container.client_connection.last_response_headers['Etag']
        elif 'etag' in self.created_container.client_connection.last_response_headers:
            continuation3 = self.created_container.client_connection.last_response_headers['etag']
        else:
            self.fail("No Etag or etag found in last response headers")

        # verify reading empty change feed
        query_iterable = self.created_container.query_items_change_feed(
            continuation=continuation3,
            is_start_from_beginning=True,
            partition_key=partition_key
        )
        iter_list = [item async for item in query_iterable]
        assert len(iter_list) == 0

    async def test_populate_query_metrics_async(self):
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

        metrics_header_name = 'x-ms-documentdb-query-metrics'
        assert metrics_header_name in self.created_container.client_connection.last_response_headers
        metrics_header = self.created_container.client_connection.last_response_headers[metrics_header_name]
        # Validate header is well-formed: "key1=value1;key2=value2;etc"
        metrics = metrics_header.split(';')
        assert len(metrics) > 1
        assert all(['=' in x for x in metrics])

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
        await self._validate_query_plan(query="Select top 10 value count(c.id) from c",
                                        container_link=self.created_container.container_link,
                                        top=10,
                                        order_by=[],
                                        aggregate=['Count'],
                                        select_value=True,
                                        offset=None,
                                        limit=None,
                                        distinct=_DistinctType.NoneType)

        await self._validate_query_plan(query="Select * from c order by c._ts offset 5 limit 10",
                                        container_link=self.created_container.container_link,
                                        top=None,
                                        order_by=['Ascending'],
                                        aggregate=[],
                                        select_value=False,
                                        offset=5,
                                        limit=10,
                                        distinct=_DistinctType.NoneType)

        await self._validate_query_plan(query="Select distinct value c.id from c order by c.id",
                                        container_link=self.created_container.container_link,
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
        queries = ['SELECT COUNT(1) FROM c', 'SELECT COUNT(1) + 5 FROM c', 'SELECT COUNT(1) + SUM(c) FROM c']
        for query in queries:
            query_iterable = self.created_container.query_items(query=query)
            try:
                results = [item async for item in query_iterable]
                self.fail("query '{}' should have failed".format(query))
            except exceptions.CosmosHttpResponseError as e:
                assert e.status_code == 400

    async def test_query_with_non_overlapping_pk_ranges_async(self):
        query_iterable = self.created_container.query_items("select * from c where c.pk='1' or c.pk='2'")
        assert [item async for item in query_iterable] == []

    async def test_offset_limit_async(self):
        values = []
        for i in range(10):
            document_definition = {'pk': i, 'id': 'myId' + str(uuid.uuid4()), 'value': i // 3}
            current_document = await self.created_container.create_item(body=document_definition)
            values.append(current_document['pk'])

        await self.config._validate_distinct_offset_limit(
            created_collection=self.created_container,
            query='SELECT DISTINCT c["value"] from c ORDER BY c.pk OFFSET 0 LIMIT 2',
            results=[0, 1])

        await self.config._validate_distinct_offset_limit(
            created_collection=self.created_container,
            query='SELECT DISTINCT c["value"] from c ORDER BY c.pk OFFSET 2 LIMIT 2',
            results=[2, 3])

        await self.config._validate_distinct_offset_limit(
            created_collection=self.created_container,
            query='SELECT DISTINCT c["value"] from c ORDER BY c.pk OFFSET 4 LIMIT 3',
            results=[])

        await self.config._validate_offset_limit(created_collection=self.created_container,
                                                 query='SELECT * from c ORDER BY c.pk OFFSET 0 LIMIT 5',
                                                 results=values[:5])

        await self.config._validate_offset_limit(created_collection=self.created_container,
                                                 query='SELECT * from c ORDER BY c.pk OFFSET 5 LIMIT 10',
                                                 results=values[5:])

        await self.config._validate_offset_limit(created_collection=self.created_container,
                                                 query='SELECT * from c ORDER BY c.pk OFFSET 10 LIMIT 5',
                                                 results=[])

        await self.config._validate_offset_limit(created_collection=self.created_container,
                                                 query='SELECT * from c ORDER BY c.pk OFFSET 100 LIMIT 1',
                                                 results=[])

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
        payloads = [
            {'id': str(uuid.uuid4()), 'f1': 1, 'f2': 'value', 'f3': 100000000000000000, 'f4': [1, 2, '3'],
             'f5': {'f6': {'f7': 2}}},
            {'id': str(uuid.uuid4()), 'f2': '\'value', 'f4': [1.0, 2, '3'], 'f5': {'f6': {'f7': 2.0}}, 'f1': 1.0,
             'f3': 100000000000000000.00},
            {'id': str(uuid.uuid4()), 'f3': 100000000000000000.0, 'f5': {'f6': {'f7': 2}}, 'f2': '\'value', 'f1': 1,
             'f4': [1, 2.0, '3']}
        ]
        for pay in payloads:
            await self.created_container.create_item(pay)

        await self.config._validate_distinct_on_different_types_and_field_orders(
            collection=self.created_container,
            query="Select distinct value c.f1 from c",
            expected_results=[1]
        )

        await self.config._validate_distinct_on_different_types_and_field_orders(
            collection=self.created_container,
            query="Select distinct value c.f2 from c",
            expected_results=['value', '\'value']
        )

        await self.config._validate_distinct_on_different_types_and_field_orders(
            collection=self.created_container,
            query="Select distinct value c.f2 from c order by c.f2",
            expected_results=['value', '\'value']
        )

        await self.config._validate_distinct_on_different_types_and_field_orders(
            collection=self.created_container,
            query="Select distinct value c.f3 from c",
            expected_results=[100000000000000000]
        )

        await self.config._validate_distinct_on_different_types_and_field_orders(
            collection=self.created_container,
            query="Select distinct value c.f4 from c",
            expected_results=[[1, 2, '3']]
        )

        await self.config._validate_distinct_on_different_types_and_field_orders(
            collection=self.created_container,
            query="Select distinct value c.f5.f6 from c",
            expected_results=[{'f7': 2}]
        )

        await self.config._validate_distinct_on_different_types_and_field_orders(
            collection=self.created_container,
            query="Select distinct c.f1, c.f2, c.f3 from c",
            expected_results=[{'f1': 1, 'f2': 'value', 'f3': 100000000000000000},
                              {'f1': 1.0, 'f2': '\'value', 'f3': 100000000000000000.00}]
        )

        await self.config._validate_distinct_on_different_types_and_field_orders(
            collection=self.created_container,
            query="Select distinct c.f1, c.f2, c.f3 from c order by c.f1",
            expected_results=[{'f1': 1, 'f2': 'value', 'f3': 100000000000000000},
                              {'f1': 1.0, 'f2': '\'value', 'f3': 100000000000000000.00}]
        )

    async def test_paging_with_continuation_token_async(self):
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

    async def test_cross_partition_query_with_continuation_token_async(self):
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

    async def test_value_max_query_async(self):
        await self.created_container.create_item(
            {"id": str(uuid.uuid4()), "isComplete": True, "version": 3, "lookupVersion": "console_version"})
        await self.created_container.create_item(
            {"id": str(uuid.uuid4()), "isComplete": True, "version": 2, "lookupVersion": "console_version"})
        query = "Select value max(c.version) FROM c where c.isComplete = true and c.lookupVersion = @lookupVersion"
        query_results = self.created_container.query_items(query, parameters=[
            {"name": "@lookupVersion", "value": "console_version"}
        ])
        item_list = [item async for item in query_results]
        assert len(item_list) == 1
        assert item_list[0] == 3

    async def test_continuation_token_size_limit_query_async(self):
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


if __name__ == '__main__':
    unittest.main()
