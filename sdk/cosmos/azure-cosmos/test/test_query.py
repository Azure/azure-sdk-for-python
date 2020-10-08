import unittest
import uuid
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos._retry_utility as retry_utility
from azure.cosmos._execution_context.query_execution_info import _PartitionedQueryExecutionInfo
import azure.cosmos.errors as errors
from azure.cosmos.partition_key import PartitionKey
from azure.cosmos._execution_context.base_execution_context import _QueryExecutionContextBase
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
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey, connection_policy=cls.connectionPolicy)
        cls.created_db = cls.config.create_database_if_not_exist(cls.client)

    def test_first_and_last_slashes_trimmed_for_query_string (self):
        created_collection = self.config.create_multi_partition_collection_with_custom_pk_if_not_exist(self.client)
        document_definition = {'pk': 'pk', 'id': 'myId'}
        created_collection.create_item(body=document_definition)

        query = 'SELECT * from c'
        query_iterable = created_collection.query_items(
            query=query,
            partition_key='pk'
        )
        iter_list = list(query_iterable)
        self.assertEqual(iter_list[0]['id'], 'myId')

    def test_query_change_feed_with_pk(self):
        self.query_change_feed(True)

    def test_query_change_feed_with_pk_range_id(self):
        self.query_change_feed(False)

    def query_change_feed(self, use_partition_key):
        created_collection = self.config.create_multi_partition_collection_with_custom_pk_if_not_exist(self.client)
        # The test targets partition #3
        partition_key = "pk"
        partition_key_range_id = 2
        partitionParam = {"partition_key": partition_key} if use_partition_key else {"partition_key_range_id": partition_key_range_id}

        # Read change feed without passing any options
        query_iterable = created_collection.query_items_change_feed()
        iter_list = list(query_iterable)
        self.assertEqual(len(iter_list), 0)

        # Read change feed from current should return an empty list
        query_iterable = created_collection.query_items_change_feed(**partitionParam)
        iter_list = list(query_iterable)
        self.assertEqual(len(iter_list), 0)
        self.assertTrue('etag' in created_collection.client_connection.last_response_headers)
        self.assertNotEqual(created_collection.client_connection.last_response_headers['etag'], '')

        # Read change feed from beginning should return an empty list
        query_iterable = created_collection.query_items_change_feed(
            is_start_from_beginning=True,
            **partitionParam
        )
        iter_list = list(query_iterable)
        self.assertEqual(len(iter_list), 0)
        self.assertTrue('etag' in created_collection.client_connection.last_response_headers)
        continuation1 = created_collection.client_connection.last_response_headers['etag']
        self.assertNotEqual(continuation1, '')

        # Create a document. Read change feed should return be able to read that document
        document_definition = {'pk': 'pk', 'id':'doc1'}
        created_collection.create_item(body=document_definition)
        query_iterable = created_collection.query_items_change_feed(
            is_start_from_beginning=True,
            **partitionParam
        )
        iter_list = list(query_iterable)
        self.assertEqual(len(iter_list), 1)
        self.assertEqual(iter_list[0]['id'], 'doc1')
        self.assertTrue('etag' in created_collection.client_connection.last_response_headers)
        continuation2 = created_collection.client_connection.last_response_headers['etag']
        self.assertNotEqual(continuation2, '')
        self.assertNotEqual(continuation2, continuation1)

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
                **partitionParam
            )
            it = query_iterable.__iter__()
            expected_ids = 'doc2.doc3.'
            actual_ids = ''
            for item in it:
                actual_ids += item['id'] + '.'
            self.assertEqual(actual_ids, expected_ids)

            # verify by_page
            # the options is not copied, therefore it need to be restored
            query_iterable = created_collection.query_items_change_feed(
                continuation=continuation2,
                max_item_count=pageSize,
                **partitionParam
            )
            count = 0
            expected_count = 2
            all_fetched_res = []
            for page in query_iterable.by_page():
                fetched_res = list(page)
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
            **partitionParam
        )
        expected_ids = ['doc1', 'doc2', 'doc3']
        it = query_iterable.__iter__()
        for i in range(0, len(expected_ids)):
            doc = next(it)
            self.assertEqual(doc['id'], expected_ids[i])
        self.assertTrue('etag' in created_collection.client_connection.last_response_headers)
        continuation3 = created_collection.client_connection.last_response_headers['etag']

        # verify reading empty change feed
        query_iterable = created_collection.query_items_change_feed(
            continuation=continuation3,
            is_start_from_beginning=True,
            **partitionParam
        )
        iter_list = list(query_iterable)
        self.assertEqual(len(iter_list), 0)

    def test_populate_query_metrics(self):
        created_collection = self.config.create_multi_partition_collection_with_custom_pk_if_not_exist(self.client)
        document_definition = {'pk': 'pk', 'id':'myId'}
        created_collection.create_item(body=document_definition)

        query = 'SELECT * from c'
        query_iterable = created_collection.query_items(
            query=query,
            partition_key='pk',
            populate_query_metrics=True
        )

        iter_list = list(query_iterable)
        self.assertEqual(iter_list[0]['id'], 'myId')

        METRICS_HEADER_NAME = 'x-ms-documentdb-query-metrics'
        self.assertTrue(METRICS_HEADER_NAME in created_collection.client_connection.last_response_headers)
        metrics_header = created_collection.client_connection.last_response_headers[METRICS_HEADER_NAME]
        # Validate header is well-formed: "key1=value1;key2=value2;etc"
        metrics = metrics_header.split(';')
        self.assertTrue(len(metrics) > 1)
        self.assertTrue(all(['=' in x for x in metrics]))

    @pytest.mark.xfail
    def test_max_item_count_honored_in_order_by_query(self):
        created_collection = self.config.create_multi_partition_collection_with_custom_pk_if_not_exist(self.client)
        docs = []
        for i in range(10):
            document_definition = {'pk': 'pk', 'id': 'myId' + str(uuid.uuid4())}
            docs.append(created_collection.create_item(body=document_definition))

        query = 'SELECT * from c ORDER BY c._ts'
        query_iterable = created_collection.query_items(
            query=query,
            max_item_count=1,
            enable_cross_partition_query=True
        )
        self.validate_query_requests_count(query_iterable, 15 * 2 + 1)

        query_iterable = created_collection.query_items(
            query=query,
            max_item_count=100,
            enable_cross_partition_query=True
        )

        self.validate_query_requests_count(query_iterable, 13)

    def validate_query_requests_count(self, query_iterable, expected_count):
        self.count = 0
        self.OriginalExecuteFunction = retry_utility.ExecuteFunction
        retry_utility.ExecuteFunction = self._MockExecuteFunction
        for block in query_iterable.by_page():
            assert len(list(block)) != 0
        retry_utility.ExecuteFunction = self.OriginalExecuteFunction
        self.assertEqual(self.count, expected_count)
        self.count = 0

    def _MockExecuteFunction(self, function, *args, **kwargs):
        self.count += 1
        return self.OriginalExecuteFunction(function, *args, **kwargs)

    def test_get_query_plan_through_gateway(self):
        created_collection = self.config.create_multi_partition_collection_with_custom_pk_if_not_exist(self.client)
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

    def _validate_query_plan(self, query, container_link, top, order_by, aggregate, select_value, offset, limit, distinct):
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

    def test_unsupported_queries(self):
        created_collection = self.config.create_multi_partition_collection_with_custom_pk_if_not_exist(self.client)
        queries = ['SELECT COUNT(1) FROM c', 'SELECT COUNT(1) + 5 FROM c', 'SELECT COUNT(1) + SUM(c) FROM c']
        for query in queries:
            query_iterable = created_collection.query_items(query=query, enable_cross_partition_query=True)
            try:
                list(query_iterable)
                self.fail()
            except errors.CosmosHttpResponseError as e:
                self.assertEqual(e.status_code, 400)

    def test_query_with_non_overlapping_pk_ranges(self):
        created_collection = self.config.create_multi_partition_collection_with_custom_pk_if_not_exist(self.client)
        query_iterable = created_collection.query_items("select * from c where c.pk='1' or c.pk='2'", enable_cross_partition_query=True)
        self.assertListEqual(list(query_iterable), [])

    def test_offset_limit(self):
        created_collection = self.config.create_multi_partition_collection_with_custom_pk_if_not_exist(self.client)
        max_item_counts = [0, 2, 5, 10]
        values = []
        for i in range(10):
            document_definition = {'pk': i, 'id': 'myId' + str(uuid.uuid4())}
            values.append(created_collection.create_item(body=document_definition)['pk'])

        for max_item_count in max_item_counts:
            self._validate_offset_limit(created_collection=created_collection,
                                        query='SELECT * from c ORDER BY c.pk OFFSET 0 LIMIT 5',
                                        max_item_count=max_item_count,
                                        results=values[:5])

            self._validate_offset_limit(created_collection=created_collection,
                                        query='SELECT * from c ORDER BY c.pk OFFSET 5 LIMIT 10',
                                        max_item_count=max_item_count,
                                        results=values[5:])

            self._validate_offset_limit(created_collection=created_collection,
                                        query='SELECT * from c ORDER BY c.pk OFFSET 10 LIMIT 5',
                                        max_item_count=max_item_count,
                                        results=[])

            self._validate_offset_limit(created_collection=created_collection,
                                        query='SELECT * from c ORDER BY c.pk OFFSET 100 LIMIT 1',
                                        max_item_count=max_item_count,
                                        results=[])

    def _validate_offset_limit(self, created_collection, query, max_item_count, results):
        query_iterable = created_collection.query_items(
            query=query,
            enable_cross_partition_query=True,
            max_item_count=max_item_count
        )
        self.assertListEqual(list(map(lambda doc: doc['pk'], list(query_iterable))), results)

    def test_distinct(self):
        created_database = self.config.create_database_if_not_exist(self.client)
        distinct_field = 'distinct_field'
        pk_field = "pk"
        different_field = "different_field"

        created_collection = created_database.create_container(
            id='collection with composite index ' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk", kind="Hash"),
            indexing_policy={
                "compositeIndexes": [
                    [{"path": "/" + pk_field, "order": "ascending"}, {"path": "/" + distinct_field, "order": "ascending"}],
                    [{"path": "/" + distinct_field, "order": "ascending"}, {"path": "/" + pk_field, "order": "ascending"}]
                ]
            }
        )
        documents = []
        for i in range(5):
            j = i
            while j > i - 5:
                document_definition = {pk_field: i, 'id': str(uuid.uuid4()), distinct_field: j}
                documents.append(created_collection.create_item(body=document_definition))
                document_definition = {pk_field: i, 'id': str(uuid.uuid4()), distinct_field: j}
                documents.append(created_collection.create_item(body=document_definition))
                document_definition = {pk_field: i, 'id': str(uuid.uuid4())}
                documents.append(created_collection.create_item(body=document_definition))
                j -= 1

        padded_docs = self._pad_with_none(documents, distinct_field)

        self._validate_distinct(created_collection=created_collection,
                                query='SELECT distinct c.%s from c ORDER BY c.%s' % (distinct_field, distinct_field),   # nosec
                                results=self._get_distinct_docs(self._get_order_by_docs(padded_docs, distinct_field, None), distinct_field, None, True),
                                is_select=False,
                                fields=[distinct_field])

        self._validate_distinct(created_collection=created_collection,
                                query='SELECT distinct c.%s, c.%s from c ORDER BY c.%s, c.%s' % (distinct_field, pk_field, pk_field, distinct_field),   # nosec
                                results=self._get_distinct_docs(self._get_order_by_docs(padded_docs, pk_field, distinct_field), distinct_field, pk_field, True),
                                is_select=False,
                                fields=[distinct_field, pk_field])

        self._validate_distinct(created_collection=created_collection,
                                query='SELECT distinct c.%s, c.%s from c ORDER BY c.%s, c.%s' % (distinct_field, pk_field, distinct_field, pk_field),   # nosec
                                results=self._get_distinct_docs(self._get_order_by_docs(padded_docs, distinct_field, pk_field), distinct_field, pk_field, True),
                                is_select=False,
                                fields=[distinct_field, pk_field])

        self._validate_distinct(created_collection=created_collection,
                                query='SELECT distinct value c.%s from c ORDER BY c.%s' % (distinct_field, distinct_field), # nosec
                                results=self._get_distinct_docs(self._get_order_by_docs(padded_docs, distinct_field, None), distinct_field, None, True),
                                is_select=False,
                                fields=[distinct_field])

        self._validate_distinct(created_collection=created_collection,
                                query='SELECT distinct c.%s from c' % (distinct_field), # nosec
                                results=self._get_distinct_docs(padded_docs, distinct_field, None, False),
                                is_select=True,
                                fields=[distinct_field])

        self._validate_distinct(created_collection=created_collection,
                                query='SELECT distinct c.%s, c.%s from c' % (distinct_field, pk_field), # nosec
                                results=self._get_distinct_docs(padded_docs, distinct_field, pk_field, False),
                                is_select=True,
                                fields=[distinct_field, pk_field])

        self._validate_distinct(created_collection=created_collection,
                                query='SELECT distinct value c.%s from c' % (distinct_field),   # nosec
                                results=self._get_distinct_docs(padded_docs, distinct_field, None, True),
                                is_select=True,
                                fields=[distinct_field])

        self._validate_distinct(created_collection=created_collection,
                                query='SELECT distinct c.%s from c ORDER BY c.%s' % (different_field, different_field), # nosec
                                results=[],
                                is_select=True,
                                fields=[different_field])

        self._validate_distinct(created_collection=created_collection,
                                query='SELECT distinct c.%s from c' % (different_field),    # nosec
                                results=['None'],
                                is_select=True,
                                fields=[different_field])

        created_database.delete_container(created_collection.id)

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

    def _validate_distinct(self, created_collection, query, results, is_select, fields):
        query_iterable = created_collection.query_items(
            query=query,
            enable_cross_partition_query=True
        )
        query_results = list(query_iterable)

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

    def test_distinct_on_different_types_and_field_orders(self):
        created_collection = self.config.create_multi_partition_collection_with_custom_pk_if_not_exist(self.client)
        self.payloads = [
            {'f1': 1, 'f2': 'value', 'f3': 100000000000000000, 'f4': [1, 2, '3'], 'f5': {'f6': {'f7': 2}}},
            {'f2': '\'value', 'f4': [1.0, 2, '3'], 'f5': {'f6': {'f7': 2.0}}, 'f1': 1.0, 'f3': 100000000000000000.00},
            {'f3': 100000000000000000.0, 'f5': {'f6': {'f7': 2}}, 'f2': '\'value', 'f1': 1, 'f4': [1, 2.0, '3']}
        ]
        self.OriginalExecuteFunction = _QueryExecutionContextBase.__next__
        _QueryExecutionContextBase.__next__ = self._MockNextFunction
        _QueryExecutionContextBase.next = self._MockNextFunction

        self._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct value c.f1 from c",
            expected_results=[1],
            get_mock_result=lambda x, i: (None, x[i]["f1"])
        )

        self._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct value c.f2 from c",
            expected_results=['value', '\'value'],
            get_mock_result=lambda x, i: (None, x[i]["f2"])
        )

        self._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct value c.f2 from c order by c.f2",
            expected_results=['\'value', 'value'],
            get_mock_result=lambda x, i: (x[i]["f2"], x[i]["f2"])
        )

        self._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct value c.f3 from c",
            expected_results=[100000000000000000],
            get_mock_result=lambda x, i: (None, x[i]["f3"])
        )

        self._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct value c.f4 from c",
            expected_results=[[1, 2, '3']],
            get_mock_result=lambda x, i: (None, x[i]["f4"])
        )

        self._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct value c.f5.f6 from c",
            expected_results=[{'f7': 2}],
            get_mock_result=lambda x, i: (None, x[i]["f5"]["f6"])
        )

        self._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct c.f1, c.f2, c.f3 from c",
            expected_results=[self.payloads[0], self.payloads[1]],
            get_mock_result=lambda x, i: (None, x[i])
        )

        self._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct c.f1, c.f2, c.f3 from c order by c.f1",
            expected_results=[self.payloads[0], self.payloads[1]],
            get_mock_result=lambda x, i: (i, x[i])
        )

        _QueryExecutionContextBase.__next__ = self.OriginalExecuteFunction
        _QueryExecutionContextBase.next = self.OriginalExecuteFunction

    def test_paging_with_continuation_token(self):
        created_collection = self.config.create_multi_partition_collection_with_custom_pk_if_not_exist(self.client)

        document_definition = {'pk': 'pk', 'id': '1'}
        created_collection.create_item(body=document_definition)
        document_definition = {'pk': 'pk', 'id': '2'}
        created_collection.create_item(body=document_definition)

        query = 'SELECT * from c'
        query_iterable = created_collection.query_items(
            query=query,
            partition_key='pk',
            max_item_count=1
        )
        pager = query_iterable.by_page()
        pager.next()
        token = pager.continuation_token
        second_page = list(pager.next())[0]

        pager = query_iterable.by_page(token)
        second_page_fetched_with_continuation_token = list(pager.next())[0]

        self.assertEqual(second_page['id'], second_page_fetched_with_continuation_token['id'])

    def test_cross_partition_query_with_continuation_token_fails(self):
        created_collection = self.config.create_multi_partition_collection_with_custom_pk_if_not_exist(self.client)
        query = 'SELECT * from c'
        query_iterable = created_collection.query_items(
            query=query,
            enable_cross_partition_query=True,
            max_item_count=1,
        )

        with self.assertRaises(ValueError):
            pager = query_iterable.by_page("fake_continuation_token")

    def _validate_distinct_on_different_types_and_field_orders(self, collection, query, expected_results, get_mock_result):
        self.count = 0
        self.get_mock_result = get_mock_result
        query_iterable = collection.query_items(query, enable_cross_partition_query=True)
        results = list(query_iterable)
        for i in range(len(expected_results)):
            if isinstance(results[i], dict):
                self.assertDictEqual(results[i], expected_results[i])
            elif isinstance(results[i], list):
                self.assertListEqual(results[i], expected_results[i])
            else:
                self.assertEqual(results[i], expected_results[i])
        self.count = 0

    def _MockNextFunction(self):
        if self.count < len(self.payloads):
            item, result = self.get_mock_result(self.payloads, self.count)
            self.count += 1
            if item is not None:
                return {'orderByItems': [{'item': item}], '_rid': 'fake_rid', 'payload': result}
            else:
                return result
            return result
        else:
            raise StopIteration


if __name__ == "__main__":
    unittest.main()