import unittest
import uuid
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos._retry_utility as retry_utility
from azure.cosmos._execution_context.query_execution_info import _PartitionedQueryExecutionInfo
import azure.cosmos.errors as errors
from azure.cosmos.partition_key import PartitionKey
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
        
        cls.client = cosmos_client.CosmosClient(cls.host, {'masterKey': cls.masterKey}, connection_policy=cls.connectionPolicy)
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

    def test_query_change_feed(self):
        created_collection = self.config.create_multi_partition_collection_with_custom_pk_if_not_exist(self.client)
        # The test targets partition #3
        pkRangeId = "2"

        # Read change feed without passing any options
        query_iterable = created_collection.query_items_change_feed()
        iter_list = list(query_iterable)
        self.assertEqual(len(iter_list), 0)

        # Read change feed from current should return an empty list
        query_iterable = created_collection.query_items_change_feed(partition_key_range_id=pkRangeId)
        iter_list = list(query_iterable)
        self.assertEqual(len(iter_list), 0)
        self.assertTrue('etag' in created_collection.client_connection.last_response_headers)
        self.assertNotEquals(created_collection.client_connection.last_response_headers['etag'], '')

        # Read change feed from beginning should return an empty list
        query_iterable = created_collection.query_items_change_feed(
            partition_key_range_id=pkRangeId,
            is_start_from_beginning=True
        )
        iter_list = list(query_iterable)
        self.assertEqual(len(iter_list), 0)
        self.assertTrue('etag' in created_collection.client_connection.last_response_headers)
        continuation1 = created_collection.client_connection.last_response_headers['etag']
        self.assertNotEquals(continuation1, '')

        # Create a document. Read change feed should return be able to read that document
        document_definition = {'pk': 'pk', 'id':'doc1'}
        created_collection.create_item(body=document_definition)
        query_iterable = created_collection.query_items_change_feed(
            partition_key_range_id=pkRangeId,
            is_start_from_beginning=True,
        )
        iter_list = list(query_iterable)
        self.assertEqual(len(iter_list), 1)
        self.assertEqual(iter_list[0]['id'], 'doc1')
        self.assertTrue('etag' in created_collection.client_connection.last_response_headers)
        continuation2 = created_collection.client_connection.last_response_headers['etag']
        self.assertNotEquals(continuation2, '')
        self.assertNotEquals(continuation2, continuation1)

        # Create two new documents. Verify that change feed contains the 2 new documents
        # with page size 1 and page size 100
        document_definition = {'pk': 'pk', 'id': 'doc2'}
        created_collection.create_item(body=document_definition)
        document_definition = {'pk': 'pk', 'id': 'doc3'}
        created_collection.create_item(body=document_definition)

        for pageSize in [1, 100]:
            # verify iterator
            query_iterable = created_collection.query_items_change_feed(
                partition_key_range_id=pkRangeId,
                continuation=continuation2,
                max_item_count=pageSize
            )
            it = query_iterable.__iter__()
            expected_ids = 'doc2.doc3.'
            actual_ids = ''
            for item in it:
                actual_ids += item['id'] + '.'    
            self.assertEqual(actual_ids, expected_ids)

            # verify fetch_next_block
            # the options is not copied, therefore it need to be restored
            query_iterable = created_collection.query_items_change_feed(
                partition_key_range_id=pkRangeId,
                continuation=continuation2,
                max_item_count=pageSize
            )
            count = 0
            expected_count = 2
            all_fetched_res = []
            while (True):
                fetched_res = query_iterable.fetch_next_block()
                self.assertEquals(len(fetched_res), min(pageSize, expected_count - count))
                count += len(fetched_res)
                all_fetched_res.extend(fetched_res)
                if len(fetched_res) == 0:
                    break
            actual_ids = ''
            for item in all_fetched_res:
                actual_ids += item['id'] + '.'
            self.assertEqual(actual_ids, expected_ids)
            # verify there's no more results
            self.assertEquals(query_iterable.fetch_next_block(), [])

        # verify reading change feed from the beginning
        query_iterable = created_collection.query_items_change_feed(
            partition_key_range_id=pkRangeId,
            is_start_from_beginning=True
        )
        expected_ids = ['doc1', 'doc2', 'doc3']
        it = query_iterable.__iter__()
        for i in range(0, len(expected_ids)):
            doc = next(it)
            self.assertEquals(doc['id'], expected_ids[i])
        self.assertTrue('etag' in created_collection.client_connection.last_response_headers)
        continuation3 = created_collection.client_connection.last_response_headers['etag']

        # verify reading empty change feed 
        query_iterable = created_collection.query_items_change_feed(
            partition_key_range_id=pkRangeId,
            continuation=continuation3,
            is_start_from_beginning=True
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
        # 1 call to get query plans, 1 call to get pkr, 10 calls to one partion with the documents, 1 call each to other 4 partitions
        self.validate_query_requests_count(query_iterable, 29)

        query_iterable = created_collection.query_items(
            query=query,
            max_item_count=100,
            enable_cross_partition_query=True
        )

        # 1 call to get query plan 1 calls to one partition with the documents, 1 call each to other 4 partitions
        self.validate_query_requests_count(query_iterable, 11)

    def validate_query_requests_count(self, query_iterable, expected_count):
        self.count = 0
        self.OriginalExecuteFunction = retry_utility.ExecuteFunction
        retry_utility.ExecuteFunction = self._MockExecuteFunction
        block = query_iterable.fetch_next_block()
        while block:
            block = query_iterable.fetch_next_block()
        retry_utility.ExecuteFunction = self.OriginalExecuteFunction
        self.assertEquals(self.count, expected_count)
        self.count = 0

    def _MockExecuteFunction(self, function, *args, **kwargs):
        self.count += 1
        return self.OriginalExecuteFunction(function, *args, **kwargs)

    def test_get_query_plan_through_gateway(self):
        created_collection = self.config.create_multi_partition_collection_with_custom_pk_if_not_exist(self.client)
        self._validate_query_plan("Select top 10 value count(c.id) from c", created_collection.container_link, 10, [], ['Count'], True, None, None, "None")
        self._validate_query_plan("Select * from c order by c._ts offset 5 limit 10", created_collection.container_link, None, ['Ascending'], [], False, 5, 10, "None")
        self._validate_query_plan("Select distinct value c.id from c order by c.id", created_collection.container_link, None, ['Ascending'], [], True, None, None, "Ordered")

    def _validate_query_plan(self, query, container_link, top, order_by, aggregate, select_value, offset, limit, distinct):
        query_plan_dict = self.client.client_connection._GetQueryPlanThroughGateway(query, container_link)
        query_execution_info = _PartitionedQueryExecutionInfo(query_plan_dict)
        self.assertTrue(query_execution_info.has_rewritten_query())
        self.assertEquals(query_execution_info.has_distinct_type(), distinct != "None")
        self.assertEquals(query_execution_info.get_distinct_type(), distinct)
        self.assertEquals(query_execution_info.has_top(), top is not None)
        self.assertEquals(query_execution_info.get_top(), top)
        self.assertEquals(query_execution_info.has_order_by(), len(order_by) > 0)
        self.assertListEqual(query_execution_info.get_order_by(), order_by)
        self.assertEquals(query_execution_info.has_aggregates(), len(aggregate) > 0)
        self.assertListEqual(query_execution_info.get_aggregates(), aggregate)
        self.assertEquals(query_execution_info.has_select_value(), select_value)
        self.assertEquals(query_execution_info.has_offset(), offset is not None)
        self.assertEquals(query_execution_info.get_offset(), offset)
        self.assertEquals(query_execution_info.has_limit(), limit is not None)
        self.assertEquals(query_execution_info.get_limit(), limit)

    def test_unsupported_queries(self):
        created_collection = self.config.create_multi_partition_collection_with_custom_pk_if_not_exist(self.client)
        queries = ['SELECT COUNT(1) FROM c', 'SELECT COUNT(1) + 5 FROM c', 'SELECT COUNT(1) + SUM(c) FROM c']
        for query in queries:
            query_iterable = created_collection.query_items(query=query, enable_cross_partition_query=True)
            try:
                list(query_iterable)
                self.fail()
            except errors.HTTPFailure as e:
                self.assertEqual(e.status_code, 400)

    def test_query_with_non_overlapping_pk_ranges(self):
        created_collection = self.config.create_multi_partition_collection_with_custom_pk_if_not_exist(self.client)
        query_iterable = created_collection.query_items("select * from c where c.pk='1' or c.pk='2'")
        self.assertListEqual(list(query_iterable), [])

    def test_offset_limit(self):
        created_collection = self.config.create_multi_partition_collection_with_custom_pk_if_not_exist(self.client)
        values = []
        for i in range(10):
            document_definition = {'pk': i, 'id': 'myId' + str(uuid.uuid4())}
            values.append(created_collection.create_item(body=document_definition)['pk'])

        self._validate_offset_limit(created_collection, 'SELECT * from c ORDER BY c.pk OFFSET 0 LIMIT 5', values[:5])
        self._validate_offset_limit(created_collection, 'SELECT * from c ORDER BY c.pk OFFSET 5 LIMIT 10', values[5:])
        self._validate_offset_limit(created_collection, 'SELECT * from c ORDER BY c.pk OFFSET 10 LIMIT 5', [])
        self._validate_offset_limit(created_collection, 'SELECT * from c ORDER BY c.pk OFFSET 100 LIMIT 1', [])

    def _validate_offset_limit(self, created_collection, query, results):
        query_iterable = created_collection.query_items(
            query=query,
            enable_cross_partition_query=True
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

        self._validate_distinct(created_collection, 'SELECT distinct c.%s from c ORDER BY c.%s' % (distinct_field, distinct_field),
                                self._get_distinct_docs(self._get_order_by_docs(padded_docs, distinct_field, None), distinct_field, None, True),
                                False, [distinct_field])

        self._validate_distinct(created_collection, 'SELECT distinct c.%s, c.%s from c ORDER BY c.%s, c.%s' % (distinct_field, pk_field, pk_field, distinct_field),
                                self._get_distinct_docs(self._get_order_by_docs(padded_docs, pk_field, distinct_field), distinct_field, pk_field, True),
                                False, [distinct_field, pk_field])

        self._validate_distinct(created_collection, 'SELECT distinct c.%s, c.%s from c ORDER BY c.%s, c.%s' % (distinct_field, pk_field, distinct_field, pk_field),
                                self._get_distinct_docs(self._get_order_by_docs(padded_docs, distinct_field, pk_field), distinct_field, pk_field, True),
                                False, [distinct_field, pk_field])

        self._validate_distinct(created_collection, 'SELECT distinct value c.%s from c ORDER BY c.%s' % (distinct_field, distinct_field),
                                self._get_distinct_docs(self._get_order_by_docs(padded_docs, distinct_field, None), distinct_field, None, True),
                                False, [distinct_field])

        self._validate_distinct(created_collection, 'SELECT distinct c.%s from c' % (distinct_field),
                                self._get_distinct_docs(padded_docs, distinct_field, None, False),
                                True, [distinct_field])

        self._validate_distinct(created_collection, 'SELECT distinct c.%s, c.%s from c' % (distinct_field, pk_field),
                                self._get_distinct_docs(padded_docs, distinct_field, pk_field, False),
                                True, [distinct_field, pk_field])

        self._validate_distinct(created_collection, 'SELECT distinct value c.%s from c' % (distinct_field),
                                self._get_distinct_docs(padded_docs, distinct_field, None, True),
                                True, [distinct_field])

        self._validate_distinct(created_collection, 'SELECT distinct c.%s from c ORDER BY c.%s' % (different_field, different_field), [],
                                True, [different_field])

        self._validate_distinct(created_collection, 'SELECT distinct c.%s from c' % (different_field), ['None'],
                                True, different_field)

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
        self.assertEquals(len(results), len(query_results))
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

if __name__ == "__main__":
    unittest.main()