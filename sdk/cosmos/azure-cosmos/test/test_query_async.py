import unittest
import uuid
import azure.cosmos.aio._cosmos_client as cosmos_client
import azure.cosmos.aio._retry_utility_async as retry_utility
from azure.cosmos._execution_context.query_execution_info import _PartitionedQueryExecutionInfo
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
from azure.cosmos._execution_context.aio.base_execution_context import _QueryExecutionContextBase
from azure.cosmos.documents import _DistinctType
import pytest
import collections
import test_config

pytestmark = pytest.mark.cosmosEmulator


@pytest.mark.usefixtures("teardown")
class QueryTest(unittest.TestCase):
    """Test to ensure escaping of non-ascii characters from partition key"""

    config = test_config._test_config
    host = config.host
    masterKey = config.masterKey
    connectionPolicy = config.connectionPolicy

    @classmethod
    async def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey,
                                                consistency_level="Session", connection_policy=cls.connectionPolicy)
        cls.created_db = await cls.client.create_database_if_not_exists(cls.config.TEST_DATABASE_ID)

    async def test_first_and_last_slashes_trimmed_for_query_string(self):
        created_collection = await self.created_db.create_container_if_not_exists(
            "test_trimmed_slashes", PartitionKey(path="/pk"))
        doc_id = 'myId' + str(uuid.uuid4())
        document_definition = {'pk': 'pk', 'id': doc_id}
        await created_collection.create_item(body=document_definition)

        query = 'SELECT * from c'
        query_iterable = created_collection.query_items(
            query=query,
            partition_key='pk'
        )
        iter_list = [item async for item in query_iterable]
        self.assertEqual(iter_list[0]['id'], doc_id)

    async def test_query_change_feed_with_pk(self):
        created_collection = await self.created_db.create_container_if_not_exists(
            "change_feed_test_" + str(uuid.uuid4()),
            PartitionKey(path="/pk"))
        # The test targets partition #3
        partition_key = "pk"

        # Read change feed without passing any options
        query_iterable = created_collection.query_items_change_feed()
        iter_list = [item async for item in query_iterable]
        self.assertEqual(len(iter_list), 0)

        # Read change feed from current should return an empty list
        query_iterable = created_collection.query_items_change_feed(partition_key=partition_key)
        iter_list = [item async for item in query_iterable]
        self.assertEqual(len(iter_list), 0)
        self.assertTrue('etag' in created_collection.client_connection.last_response_headers)
        self.assertNotEqual(created_collection.client_connection.last_response_headers['etag'], '')

        # Read change feed from beginning should return an empty list
        query_iterable = created_collection.query_items_change_feed(
            is_start_from_beginning=True,
            partition_key=partition_key
        )
        iter_list = [item async for item in query_iterable]
        self.assertEqual(len(iter_list), 0)
        self.assertTrue('etag' in created_collection.client_connection.last_response_headers)
        continuation1 = created_collection.client_connection.last_response_headers['etag']
        self.assertNotEqual(continuation1, '')

        # Create a document. Read change feed should return be able to read that document
        document_definition = {'pk': 'pk', 'id': 'doc1'}
        await created_collection.create_item(body=document_definition)
        query_iterable = created_collection.query_items_change_feed(
            is_start_from_beginning=True,
            partition_key=partition_key
        )
        iter_list = [item async for item in query_iterable]
        self.assertEqual(len(iter_list), 1)
        self.assertEqual(iter_list[0]['id'], 'doc1')
        self.assertTrue('etag' in created_collection.client_connection.last_response_headers)
        continuation2 = created_collection.client_connection.last_response_headers['etag']
        self.assertNotEqual(continuation2, '')
        self.assertNotEqual(continuation2, continuation1)

        # Create two new documents. Verify that change feed contains the 2 new documents
        # with page size 1 and page size 100
        document_definition = {'pk': 'pk', 'id': 'doc2'}
        await created_collection.create_item(body=document_definition)
        document_definition = {'pk': 'pk', 'id': 'doc3'}
        await created_collection.create_item(body=document_definition)

        for pageSize in [1, 100]:
            # verify iterator
            query_iterable = created_collection.query_items_change_feed(
                continuation=continuation2,
                max_item_count=pageSize,
                partition_key=partition_key
            )
            it = query_iterable.__aiter__()
            expected_ids = 'doc2.doc3.'
            actual_ids = ''
            async for item in it:
                actual_ids += item['id'] + '.'
            self.assertEqual(actual_ids, expected_ids)

            # verify by_page
            # the options is not copied, therefore it need to be restored
            query_iterable = created_collection.query_items_change_feed(
                continuation=continuation2,
                max_item_count=pageSize,
                partition_key=partition_key
            )
            count = 0
            expected_count = 2
            all_fetched_res = []
            for page in query_iterable.by_page():
                fetched_res = [item async for item in page]
                self.assertEqual(len(fetched_res), min(pageSize, expected_count - count))
                count += len(fetched_res)
                all_fetched_res.extend(fetched_res)

            actual_ids = ''
            for item in all_fetched_res:
                actual_ids += item['id'] + '.'
            self.assertEqual(actual_ids, expected_ids)

        # verify reading change feed from the beginning
        query_iterable = created_collection.query_items_change_feed(
            is_start_from_beginning=True,
            partition_key=partition_key
        )
        expected_ids = ['doc1', 'doc2', 'doc3']
        it = query_iterable.__aiter__()
        for i in range(0, len(expected_ids)):
            doc = await it.__anext__()
            self.assertEqual(doc['id'], expected_ids[i])
        self.assertTrue('etag' in created_collection.client_connection.last_response_headers)
        continuation3 = created_collection.client_connection.last_response_headers['etag']

        # verify reading empty change feed
        query_iterable = created_collection.query_items_change_feed(
            continuation=continuation3,
            is_start_from_beginning=True,
            partition_key=partition_key
        )
        iter_list = [item async for item in query_iterable]
        self.assertEqual(len(iter_list), 0)

    async def test_query_change_feed_with_pk_range_id(self):
        created_collection = await self.created_db.create_container_if_not_exists("cf_test_" + str(uuid.uuid4()),
                                                                                  PartitionKey(path="/pk"))
        # The test targets partition #3
        partition_key_range_id = 0
        partition_param = {"partition_key_range_id": partition_key_range_id}

        # Read change feed without passing any options
        query_iterable = created_collection.query_items_change_feed()
        iter_list = [item async for item in query_iterable]
        self.assertEqual(len(iter_list), 0)

        # Read change feed from current should return an empty list
        query_iterable = created_collection.query_items_change_feed(**partition_param)
        iter_list = [item async for item in query_iterable]
        self.assertEqual(len(iter_list), 0)
        self.assertTrue('etag' in created_collection.client_connection.last_response_headers)
        self.assertNotEqual(created_collection.client_connection.last_response_headers['etag'], '')

        # Read change feed from beginning should return an empty list
        query_iterable = created_collection.query_items_change_feed(
            is_start_from_beginning=True,
            **partition_param
        )
        iter_list = [item async for item in query_iterable]
        self.assertEqual(len(iter_list), 0)
        self.assertTrue('etag' in created_collection.client_connection.last_response_headers)
        continuation1 = created_collection.client_connection.last_response_headers['etag']
        self.assertNotEqual(continuation1, '')

        # Create a document. Read change feed should return be able to read that document
        document_definition = {'pk': 'pk', 'id': 'doc1'}
        await created_collection.create_item(body=document_definition)
        query_iterable = created_collection.query_items_change_feed(
            is_start_from_beginning=True,
            **partition_param
        )
        iter_list = [item async for item in query_iterable]
        self.assertEqual(len(iter_list), 1)
        self.assertEqual(iter_list[0]['id'], 'doc1')
        self.assertTrue('etag' in created_collection.client_connection.last_response_headers)
        continuation2 = created_collection.client_connection.last_response_headers['etag']
        self.assertNotEqual(continuation2, '')
        self.assertNotEqual(continuation2, continuation1)

        # Create two new documents. Verify that change feed contains the 2 new documents
        # with page size 1 and page size 100
        document_definition = {'pk': 'pk', 'id': 'doc2'}
        await created_collection.create_item(body=document_definition)
        document_definition = {'pk': 'pk', 'id': 'doc3'}
        await created_collection.create_item(body=document_definition)

        for pageSize in [1, 100]:
            # verify iterator
            query_iterable = created_collection.query_items_change_feed(
                continuation=continuation2,
                max_item_count=pageSize,
                **partition_param
            )
            it = query_iterable.__aiter__()
            expected_ids = 'doc2.doc3.'
            actual_ids = ''
            async for item in it:
                actual_ids += item['id'] + '.'
            self.assertEqual(actual_ids, expected_ids)

            # verify by_page
            # the options is not copied, therefore it need to be restored
            query_iterable = created_collection.query_items_change_feed(
                continuation=continuation2,
                max_item_count=pageSize,
                **partition_param
            )
            count = 0
            expected_count = 2
            all_fetched_res = []
            for page in query_iterable.by_page():
                fetched_res = [item async for item in page]
                self.assertEqual(len(fetched_res), min(pageSize, expected_count - count))
                count += len(fetched_res)
                all_fetched_res.extend(fetched_res)

            actual_ids = ''
            for item in all_fetched_res:
                actual_ids += item['id'] + '.'
            self.assertEqual(actual_ids, expected_ids)

        # verify reading change feed from the beginning
        query_iterable = created_collection.query_items_change_feed(
            is_start_from_beginning=True,
            **partition_param
        )
        expected_ids = ['doc1', 'doc2', 'doc3']
        it = query_iterable.__aiter__()
        for i in range(0, len(expected_ids)):
            doc = next(it)
            self.assertEqual(doc['id'], expected_ids[i])
        self.assertTrue('etag' in created_collection.client_connection.last_response_headers)
        continuation3 = created_collection.client_connection.last_response_headers['etag']

        # verify reading empty change feed
        query_iterable = created_collection.query_items_change_feed(
            continuation=continuation3,
            is_start_from_beginning=True,
            **partition_param
        )
        iter_list = [item async for item in query_iterable]
        self.assertEqual(len(iter_list), 0)

    async def test_populate_query_metrics(self):
        created_collection = await self.created_db.create_container_if_not_exists("query_metrics_test",
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
        self.assertEqual(iter_list[0]['id'], doc_id)

        metrics_header_name = 'x-ms-documentdb-query-metrics'
        self.assertTrue(metrics_header_name in created_collection.client_connection.last_response_headers)
        metrics_header = created_collection.client_connection.last_response_headers[metrics_header_name]
        # Validate header is well-formed: "key1=value1;key2=value2;etc"
        metrics = metrics_header.split(';')
        self.assertTrue(len(metrics) > 1)
        self.assertTrue(all(['=' in x for x in metrics]))

    async def test_max_item_count_honored_in_order_by_query(self):
        created_collection = await self.created_db.create_container_if_not_exists(
            self.config.TEST_COLLECTION_MULTI_PARTITION_WITH_CUSTOM_PK_ID, PartitionKey(path="/pk"))
        docs = []
        for i in range(10):
            document_definition = {'pk': 'pk', 'id': 'myId' + str(uuid.uuid4())}
            docs.append(await created_collection.create_item(body=document_definition))

        query = 'SELECT * from c ORDER BY c._ts'
        query_iterable = created_collection.query_items(
            query=query,
            max_item_count=1
        )
        await self.validate_query_requests_count(query_iterable, 11 * 2 + 1)

        query_iterable = created_collection.query_items(
            query=query,
            max_item_count=100
        )

        await self.validate_query_requests_count(query_iterable, 5)

    async def validate_query_requests_count(self, query_iterable, expected_count):
        self.count = 0
        self.OriginalExecuteFunction = retry_utility.ExecuteFunctionAsync
        retry_utility.ExecuteFunctionAsync = self._MockExecuteFunction
        for block in query_iterable.by_page():
            assert len([item async for item in block]) != 0
        retry_utility.ExecuteFunctionAsync = self.OriginalExecuteFunction
        self.assertEqual(self.count, expected_count)
        self.count = 0

    async def _MockExecuteFunction(self, function, *args, **kwargs):
        self.count += 1
        return await self.OriginalExecuteFunction(function, *args, **kwargs)

    async def test_get_query_plan_through_gateway(self):
        created_collection = await self.created_db.create_container_if_not_exists(
            self.config.TEST_COLLECTION_MULTI_PARTITION_WITH_CUSTOM_PK_ID, PartitionKey(path="/pk"))
        self._validate_query_plan(query="Select top 10 value count(c.id) from c",
                                  container_link=created_collection.container_link,
                                  top=10,
                                  order_by=[],
                                  aggregate=['Count'],
                                  select_value=True,
                                  offset=None,
                                  limit=None,
                                  distinct=_DistinctType.NoneType)

        self._validate_query_plan(query="Select * from c order by c._ts offset 5 limit 10",
                                  container_link=created_collection.container_link,
                                  top=None,
                                  order_by=['Ascending'],
                                  aggregate=[],
                                  select_value=False,
                                  offset=5,
                                  limit=10,
                                  distinct=_DistinctType.NoneType)

        self._validate_query_plan(query="Select distinct value c.id from c order by c.id",
                                  container_link=created_collection.container_link,
                                  top=None,
                                  order_by=['Ascending'],
                                  aggregate=[],
                                  select_value=True,
                                  offset=None,
                                  limit=None,
                                  distinct=_DistinctType.Ordered)

    def _validate_query_plan(self, query, container_link, top, order_by, aggregate, select_value, offset, limit,
                             distinct):
        query_plan_dict = self.client.client_connection._GetQueryPlanThroughGateway(query, container_link)
        query_execution_info = _PartitionedQueryExecutionInfo(query_plan_dict)
        self.assertTrue(query_execution_info.has_rewritten_query())
        self.assertEqual(query_execution_info.has_distinct_type(), distinct != "None")
        self.assertEqual(query_execution_info.get_distinct_type(), distinct)
        self.assertEqual(query_execution_info.has_top(), top is not None)
        self.assertEqual(query_execution_info.get_top(), top)
        self.assertEqual(query_execution_info.has_order_by(), len(order_by) > 0)
        self.assertListEqual(query_execution_info.get_order_by(), order_by)
        self.assertEqual(query_execution_info.has_aggregates(), len(aggregate) > 0)
        self.assertListEqual(query_execution_info.get_aggregates(), aggregate)
        self.assertEqual(query_execution_info.has_select_value(), select_value)
        self.assertEqual(query_execution_info.has_offset(), offset is not None)
        self.assertEqual(query_execution_info.get_offset(), offset)
        self.assertEqual(query_execution_info.has_limit(), limit is not None)
        self.assertEqual(query_execution_info.get_limit(), limit)

    async def test_unsupported_queries(self):
        created_collection = await self.created_db.create_container_if_not_exists(
            self.config.TEST_COLLECTION_MULTI_PARTITION_WITH_CUSTOM_PK_ID, PartitionKey(path="/pk"))
        queries = ['SELECT COUNT(1) FROM c', 'SELECT COUNT(1) + 5 FROM c', 'SELECT COUNT(1) + SUM(c) FROM c']
        for query in queries:
            query_iterable = created_collection.query_items(query=query)
            try:
                results = [item async for item in query_iterable]
                self.fail()
            except exceptions.CosmosHttpResponseError as e:
                self.assertEqual(e.status_code, 400)

    async def test_query_with_non_overlapping_pk_ranges(self):
        created_collection = await self.created_db.create_container_if_not_exists(
            self.config.TEST_COLLECTION_MULTI_PARTITION_WITH_CUSTOM_PK_ID, PartitionKey(path="/pk"))
        query_iterable = created_collection.query_items("select * from c where c.pk='1' or c.pk='2'")
        self.assertListEqual([item async for item in query_iterable], [])

    async def test_offset_limit(self):
        created_collection = await self.created_db.create_container_if_not_exists("offset_limit_" + str(uuid.uuid4()),
                                                                                  PartitionKey(path="/pk"))
        values = []
        for i in range(10):
            document_definition = {'pk': i, 'id': 'myId' + str(uuid.uuid4())}
            values.append(await created_collection.create_item(body=document_definition)['pk'])

        await self._validate_offset_limit(created_collection=created_collection,
                                          query='SELECT * from c ORDER BY c.pk OFFSET 0 LIMIT 5',
                                          results=values[:5])

        await self._validate_offset_limit(created_collection=created_collection,
                                          query='SELECT * from c ORDER BY c.pk OFFSET 5 LIMIT 10',
                                          results=values[5:])

        await self._validate_offset_limit(created_collection=created_collection,
                                          query='SELECT * from c ORDER BY c.pk OFFSET 10 LIMIT 5',
                                          results=[])

        await self._validate_offset_limit(created_collection=created_collection,
                                          query='SELECT * from c ORDER BY c.pk OFFSET 100 LIMIT 1',
                                          results=[])

    async def _validate_offset_limit(self, created_collection, query, results):
        query_iterable = created_collection.query_items(query=query)
        self.assertListEqual(list(map(lambda doc: doc['pk'], [item async for item in query_iterable])), results)

    # TODO: Look into distinct query behavior to re-enable this test when possible
    @unittest.skip("intermittent failures in the pipeline")
    async def test_distinct(self):
        created_database = await self.config.create_database_if_not_exist(self.client)
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

        padded_docs = self._pad_with_none(documents, distinct_field)

        await self._validate_distinct(created_collection=created_collection,
                                      query='SELECT distinct c.%s from c ORDER BY c.%s' % (
                                          distinct_field, distinct_field),
                                      # nosec
                                      results=self._get_distinct_docs(
                                          self._get_order_by_docs(padded_docs, distinct_field, None), distinct_field,
                                          None,
                                          True),
                                      is_select=False,
                                      fields=[distinct_field])

        await self._validate_distinct(created_collection=created_collection,
                                      query='SELECT distinct c.%s, c.%s from c ORDER BY c.%s, c.%s' % (
                                          distinct_field, pk_field, pk_field, distinct_field),  # nosec
                                      results=self._get_distinct_docs(
                                          self._get_order_by_docs(padded_docs, pk_field, distinct_field),
                                          distinct_field,
                                          pk_field, True),
                                      is_select=False,
                                      fields=[distinct_field, pk_field])

        await self._validate_distinct(created_collection=created_collection,
                                      query='SELECT distinct c.%s, c.%s from c ORDER BY c.%s, c.%s' % (
                                          distinct_field, pk_field, distinct_field, pk_field),  # nosec
                                      results=self._get_distinct_docs(
                                          self._get_order_by_docs(padded_docs, distinct_field, pk_field),
                                          distinct_field,
                                          pk_field, True),
                                      is_select=False,
                                      fields=[distinct_field, pk_field])

        await self._validate_distinct(created_collection=created_collection,
                                      query='SELECT distinct value c.%s from c ORDER BY c.%s' % (
                                          distinct_field, distinct_field),  # nosec
                                      results=self._get_distinct_docs(
                                          self._get_order_by_docs(padded_docs, distinct_field, None), distinct_field,
                                          None,
                                          True),
                                      is_select=False,
                                      fields=[distinct_field])

        await self._validate_distinct(created_collection=created_collection,  # returns {} and is right number
                                      query='SELECT distinct c.%s from c' % (distinct_field),  # nosec
                                      results=self._get_distinct_docs(padded_docs, distinct_field, None, False),
                                      is_select=True,
                                      fields=[distinct_field])

        await self._validate_distinct(created_collection=created_collection,
                                      query='SELECT distinct c.%s, c.%s from c' % (distinct_field, pk_field),  # nosec
                                      results=self._get_distinct_docs(padded_docs, distinct_field, pk_field, False),
                                      is_select=True,
                                      fields=[distinct_field, pk_field])

        await self._validate_distinct(created_collection=created_collection,
                                      query='SELECT distinct value c.%s from c' % (distinct_field),  # nosec
                                      results=self._get_distinct_docs(padded_docs, distinct_field, None, True),
                                      is_select=True,
                                      fields=[distinct_field])

        await self._validate_distinct(created_collection=created_collection,
                                      query='SELECT distinct c.%s from c ORDER BY c.%s' % (
                                          different_field, different_field),
                                      # nosec
                                      results=[],
                                      is_select=True,
                                      fields=[different_field])

        await self._validate_distinct(created_collection=created_collection,
                                      query='SELECT distinct c.%s from c' % different_field,  # nosec
                                      results=['None'],
                                      is_select=True,
                                      fields=[different_field])

        await created_database.delete_container(created_collection.id)

    def _get_order_by_docs(self, documents, field1, field2):
        if field2 is None:
            return sorted(documents, key=lambda d: (d[field1] is not None, d[field1]))
        else:
            return sorted(documents, key=lambda d: (d[field1] is not None, d[field1], d[field2] is not None, d[field2]))

    def _get_distinct_docs(self, documents, field1, field2, is_order_by_or_value):
        if field2 is None:
            res = collections.OrderedDict.fromkeys(doc[field1] for doc in documents)
            if is_order_by_or_value:
                res = filter(lambda x: False if x is None else True, res)
        else:
            res = collections.OrderedDict.fromkeys(str(doc[field1]) + "," + str(doc[field2]) for doc in documents)
        return list(res)

    def _pad_with_none(self, documents, field):
        for doc in documents:
            if field not in doc:
                doc[field] = None
        return documents

    async def _validate_distinct(self, created_collection, query, results, is_select, fields):
        query_iterable = created_collection.query_items(query=query)
        query_results = [item async for item in query_iterable]

        self.assertEqual(len(results), len(query_results))
        query_results_strings = []
        result_strings = []
        for i in range(len(results)):
            query_results_strings.append(self._get_query_result_string(query_results[i], fields))
            result_strings.append(str(results[i]))
        if is_select:
            query_results_strings = sorted(query_results_strings)
            result_strings = sorted(result_strings)
        self.assertListEqual(result_strings, query_results_strings)

    def _get_query_result_string(self, query_result, fields):
        if type(query_result) is not dict:
            return str(query_result)
        res = str(query_result[fields[0]] if fields[0] in query_result else None)
        if len(fields) == 2:
            res = res + "," + str(query_result[fields[1]] if fields[1] in query_result else None)

        return res

    async def test_distinct_on_different_types_and_field_orders(self):
        created_collection = await self.created_db.create_container_if_not_exists(
            self.config.TEST_COLLECTION_MULTI_PARTITION_WITH_CUSTOM_PK_ID, PartitionKey(path="/pk"))
        self.payloads = [
            {'f1': 1, 'f2': 'value', 'f3': 100000000000000000, 'f4': [1, 2, '3'], 'f5': {'f6': {'f7': 2}}},
            {'f2': '\'value', 'f4': [1.0, 2, '3'], 'f5': {'f6': {'f7': 2.0}}, 'f1': 1.0, 'f3': 100000000000000000.00},
            {'f3': 100000000000000000.0, 'f5': {'f6': {'f7': 2}}, 'f2': '\'value', 'f1': 1, 'f4': [1, 2.0, '3']}
        ]
        self.OriginalExecuteFunction = _QueryExecutionContextBase.__anext__
        _QueryExecutionContextBase.__anext__ = self._MockNextFunction

        await self._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct value c.f1 from c",
            expected_results=[1],
            get_mock_result=lambda x, i: (None, x[i]["f1"])
        )

        await self._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct value c.f2 from c",
            expected_results=['value', '\'value'],
            get_mock_result=lambda x, i: (None, x[i]["f2"])
        )

        await self._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct value c.f2 from c order by c.f2",
            expected_results=['value', '\'value'],
            get_mock_result=lambda x, i: (x[i]["f2"], x[i]["f2"])
        )

        await self._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct value c.f3 from c",
            expected_results=[100000000000000000],
            get_mock_result=lambda x, i: (None, x[i]["f3"])
        )

        await self._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct value c.f4 from c",
            expected_results=[[1, 2, '3']],
            get_mock_result=lambda x, i: (None, x[i]["f4"])
        )

        await self._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct value c.f5.f6 from c",
            expected_results=[{'f7': 2}],
            get_mock_result=lambda x, i: (None, x[i]["f5"]["f6"])
        )

        await self._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct c.f1, c.f2, c.f3 from c",
            expected_results=[self.payloads[0], self.payloads[1]],
            get_mock_result=lambda x, i: (None, x[i])
        )

        await self._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct c.f1, c.f2, c.f3 from c order by c.f1",
            expected_results=[self.payloads[0], self.payloads[1]],
            get_mock_result=lambda x, i: (i, x[i])
        )

        _QueryExecutionContextBase.__anext__ = self.OriginalExecuteFunction
        _QueryExecutionContextBase.next = self.OriginalExecuteFunction

    async def test_paging_with_continuation_token(self):
        created_collection = await self.created_db.create_container_if_not_exists(
            self.config.TEST_COLLECTION_MULTI_PARTITION_WITH_CUSTOM_PK_ID, PartitionKey(path="/pk"))

        document_definition = {'pk': 'pk', 'id': '1'}
        await created_collection.create_item(body=document_definition)
        document_definition = {'pk': 'pk', 'id': '2'}
        await created_collection.create_item(body=document_definition)

        query = 'SELECT * from c'
        query_iterable = created_collection.query_items(
            query=query,
            partition_key='pk',
            max_item_count=1
        )
        pager = query_iterable.by_page()
        await pager.__anext__()
        token = pager.continuation_token

        second_page = [item async for item in await pager.__anext__()]

        pager = query_iterable.by_page(token)
        second_page_fetched_with_continuation_token = [item async for item in await pager.__anext__()][0]

        self.assertEqual(second_page['id'], second_page_fetched_with_continuation_token['id'])

    async def test_cross_partition_query_with_continuation_token(self):
        created_collection = await self.created_db.create_container_if_not_exists(
            self.config.TEST_COLLECTION_MULTI_PARTITION_ID,
            PartitionKey(path="/id"))
        document_definition = {'pk': 'pk1', 'id': '1'}
        await created_collection.create_item(body=document_definition)
        document_definition = {'pk': 'pk2', 'id': '2'}
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

        self.assertEqual(second_page['id'], second_page_fetched_with_continuation_token['id'])

    async def _validate_distinct_on_different_types_and_field_orders(self, collection, query, expected_results,
                                                                     get_mock_result):
        self.count = 0
        self.get_mock_result = get_mock_result
        query_iterable = collection.query_items(query)
        results = [item async for item in query_iterable]
        for i in range(len(expected_results)):
            if isinstance(results[i], dict):
                self.assertDictEqual(results[i], expected_results[i])
            elif isinstance(results[i], list):
                self.assertListEqual(results[i], expected_results[i])
            else:
                self.assertEqual(results[i], expected_results[i])
        self.count = 0

    async def test_value_max_query(self):
        container = await self.created_db.create_container_if_not_exists(
            self.config.TEST_COLLECTION_MULTI_PARTITION_WITH_CUSTOM_PK_ID, PartitionKey(path="/pk"))
        query = "Select value max(c.version) FROM c where c.isComplete = true and c.lookupVersion = @lookupVersion"
        query_results = container.query_items(query, parameters=[
            {"name": "@lookupVersion", "value": "console_csat"}  # cspell:disable-line
        ])

        self.assertListEqual([item async for item in query_results], [None])

    async def test_continuation_token_size_limit_query(self):
        container = await self.created_db.create_container_if_not_exists(
            self.config.TEST_COLLECTION_MULTI_PARTITION_WITH_CUSTOM_PK_ID, PartitionKey(path="/pk"))
        for i in range(1, 1000):
            await container.create_item(body=dict(pk='123', id=str(i), some_value=str(i % 3)))
        query = "Select * from c where c.some_value='2'"
        response_query = container.query_items(query, partition_key='123', max_item_count=100,
                                               continuation_token_limit=1)
        pager = response_query.by_page()
        await pager.__anext__()
        token = pager.continuation_token
        # Continuation token size should be below 1kb
        self.assertLessEqual(len(token.encode('utf-8')), 1024)
        await pager.__anext__()
        token = pager.continuation_token

        # verify a second time
        self.assertLessEqual(len(token.encode('utf-8')), 1024)
        await self.created_db.delete_container(container)

    def _MockNextFunction(self):
        if self.count < len(self.payloads):
            item, result = self.get_mock_result(self.payloads, self.count)
            self.count += 1
            if item is not None:
                return {'orderByItems': [{'item': item}], '_rid': 'fake_rid', 'payload': result}
            else:
                return result
        else:
            raise StopIteration
