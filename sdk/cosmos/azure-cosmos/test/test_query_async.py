import uuid
from azure.cosmos.aio import CosmosClient
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
class TestQueryAsync:
    """Test to ensure escaping of non-ascii characters from partition key"""

    config = test_config._test_config
    host = config.host
    masterKey = config.masterKey
    connectionPolicy = config.connectionPolicy

    @classmethod
    async def _set_up(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")
        cls.client = CosmosClient(cls.host, cls.masterKey)
        cls.created_db = await cls.client.create_database_if_not_exists(test_config._test_config.TEST_DATABASE_ID)

    @pytest.mark.asyncio
    async def test_first_and_last_slashes_trimmed_for_query_string_async(self):
        await self._set_up()
        created_collection = await self.created_db.create_container_if_not_exists(
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

    @pytest.mark.asyncio
    async def test_query_change_feed_with_pk_async(self):
        await self._set_up()
        created_collection = await self.created_db.create_container_if_not_exists(
            "change_feed_test_" + str(uuid.uuid4()),
            PartitionKey(path="/pk"))
        # The test targets partition #3
        partition_key = "pk"

        # Read change feed without passing any options
        query_iterable = created_collection.query_items_change_feed()
        iter_list = [item async for item in query_iterable]
        assert len(iter_list) == 0

        # Read change feed from current should return an empty list
        query_iterable = created_collection.query_items_change_feed(partition_key=partition_key)
        iter_list = [item async for item in query_iterable]
        assert len(iter_list) == 0
        if 'Etag' in created_collection.client_connection.last_response_headers:
            assert created_collection.client_connection.last_response_headers['Etag'] != ''
        elif 'etag' in created_collection.client_connection.last_response_headers:
            assert created_collection.client_connection.last_response_headers['etag'] != ''
        else:
            pytest.fail("No Etag or etag found in last response headers")

        # Read change feed from beginning should return an empty list
        query_iterable = created_collection.query_items_change_feed(
            is_start_from_beginning=True,
            partition_key=partition_key
        )
        iter_list = [item async for item in query_iterable]
        assert len(iter_list) == 0
        if 'Etag' in created_collection.client_connection.last_response_headers:
            continuation1 = created_collection.client_connection.last_response_headers['Etag']
        elif 'etag' in created_collection.client_connection.last_response_headers:
            continuation1 = created_collection.client_connection.last_response_headers['etag']
        else:
            pytest.fail("No Etag or etag found in last response headers")
        assert continuation1 != ''

        # Create a document. Read change feed should return be able to read that document
        document_definition = {'pk': 'pk', 'id': 'doc1'}
        await created_collection.create_item(body=document_definition)
        query_iterable = created_collection.query_items_change_feed(
            is_start_from_beginning=True,
            partition_key=partition_key
        )
        iter_list = [item async for item in query_iterable]
        assert len(iter_list) == 1
        assert iter_list[0]['id'] == 'doc1'
        if 'Etag' in created_collection.client_connection.last_response_headers:
            continuation2 = created_collection.client_connection.last_response_headers['Etag']
        elif 'etag' in created_collection.client_connection.last_response_headers:
            continuation2 = created_collection.client_connection.last_response_headers['etag']
        else:
            pytest.fail("No Etag or etag found in last response headers")
        assert continuation2 != ''
        assert continuation2 != continuation1

        # Create two new documents. Verify that change feed contains the 2 new documents
        # with page size 1 and page size 100
        document_definition = {'pk': 'pk', 'id': 'doc2'}
        await created_collection.create_item(body=document_definition)
        document_definition = {'pk': 'pk', 'id': 'doc3'}
        await created_collection.create_item(body=document_definition)

        for pageSize in [2, 100]:
            # verify iterator
            query_iterable = created_collection.query_items_change_feed(
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
            query_iterable = created_collection.query_items_change_feed(
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
        query_iterable = created_collection.query_items_change_feed(
            is_start_from_beginning=True,
            partition_key=partition_key
        )
        expected_ids = ['doc1', 'doc2', 'doc3']
        it = query_iterable.__aiter__()
        for i in range(0, len(expected_ids)):
            doc = await it.__anext__()
            assert doc['id'] == expected_ids[i]
        if 'Etag' in created_collection.client_connection.last_response_headers:
            continuation3 = created_collection.client_connection.last_response_headers['Etag']
        elif 'etag' in created_collection.client_connection.last_response_headers:
            continuation3 = created_collection.client_connection.last_response_headers['etag']
        else:
            pytest.fail("No Etag or etag found in last response headers")

        # verify reading empty change feed
        query_iterable = created_collection.query_items_change_feed(
            continuation=continuation3,
            is_start_from_beginning=True,
            partition_key=partition_key
        )
        iter_list = [item async for item in query_iterable]
        assert len(iter_list) == 0

    @pytest.mark.asyncio
    async def test_query_change_feed_with_pk_range_id_async(self):
        await self._set_up()
        created_collection = await self.created_db.create_container_if_not_exists("cf_test_" + str(uuid.uuid4()),
                                                                                  PartitionKey(path="/pk"))
        # The test targets partition #3
        partition_key_range_id = 0
        partition_param = {"partition_key_range_id": partition_key_range_id}

        # Read change feed without passing any options
        query_iterable = created_collection.query_items_change_feed()
        iter_list = [item async for item in query_iterable]
        assert len(iter_list) == 0

        # Read change feed from current should return an empty list
        query_iterable = created_collection.query_items_change_feed(**partition_param)
        iter_list = [item async for item in query_iterable]
        assert len(iter_list) == 0
        if 'Etag' in created_collection.client_connection.last_response_headers:
            assert created_collection.client_connection.last_response_headers['Etag']
        elif 'etag' in created_collection.client_connection.last_response_headers:
            assert created_collection.client_connection.last_response_headers['etag']
        else:
            pytest.fail("No Etag or etag found in last response headers")

        # Read change feed from beginning should return an empty list
        query_iterable = created_collection.query_items_change_feed(
            is_start_from_beginning=True,
            **partition_param
        )
        iter_list = [item async for item in query_iterable]
        assert len(iter_list) == 0
        if 'Etag' in created_collection.client_connection.last_response_headers:
            continuation1 = created_collection.client_connection.last_response_headers['Etag']
        elif 'etag' in created_collection.client_connection.last_response_headers:
            continuation1 = created_collection.client_connection.last_response_headers['etag']
        else:
            pytest.fail("No Etag or etag found in last response headers")
        assert continuation1 != ''

        # Create a document. Read change feed should return be able to read that document
        document_definition = {'pk': 'pk', 'id': 'doc1'}
        await created_collection.create_item(body=document_definition)
        query_iterable = created_collection.query_items_change_feed(
            is_start_from_beginning=True,
            **partition_param
        )
        iter_list = [item async for item in query_iterable]
        assert len(iter_list) == 1
        assert iter_list[0]['id'] == 'doc1'
        if 'Etag' in created_collection.client_connection.last_response_headers:
            continuation2 = created_collection.client_connection.last_response_headers['Etag']
        elif 'etag' in created_collection.client_connection.last_response_headers:
            continuation2 = created_collection.client_connection.last_response_headers['etag']
        else:
            pytest.fail("No Etag or etag found in last response headers")
        assert continuation2 != ''
        assert continuation2 != continuation1

        # Create two new documents. Verify that change feed contains the 2 new documents
        # with page size 1 and page size 100
        document_definition = {'pk': 'pk', 'id': 'doc2'}
        await created_collection.create_item(body=document_definition)
        document_definition = {'pk': 'pk', 'id': 'doc3'}
        await created_collection.create_item(body=document_definition)

        for pageSize in [2, 100]:
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
            assert actual_ids == expected_ids

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
        query_iterable = created_collection.query_items_change_feed(
            is_start_from_beginning=True,
            **partition_param
        )
        expected_ids = ['doc1', 'doc2', 'doc3']
        it = query_iterable.__aiter__()
        for i in range(0, len(expected_ids)):
            doc = await it.__anext__()
            assert doc['id'] == expected_ids[i]
        if 'Etag' in created_collection.client_connection.last_response_headers:
            continuation3 = created_collection.client_connection.last_response_headers['Etag']
        elif 'etag' in created_collection.client_connection.last_response_headers:
            continuation3 = created_collection.client_connection.last_response_headers['etag']
        else:
            pytest.fail("No Etag or etag found in last response headers")

        # verify reading empty change feed
        query_iterable = created_collection.query_items_change_feed(
            continuation=continuation3,
            is_start_from_beginning=True,
            **partition_param
        )
        iter_list = [item async for item in query_iterable]
        assert len(iter_list) == 0

    @pytest.mark.asyncio
    async def test_populate_query_metrics_async(self):
        await self._set_up()
        created_collection = await self.created_db.create_container_if_not_exists("query_metrics_test" + str(uuid.uuid4()),
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

    @pytest.mark.asyncio
    async def test_max_item_count_honored_in_order_by_query_async(self):
        await self._set_up()
        created_collection = await self.created_db.create_container_if_not_exists(str(uuid.uuid4()),
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
        await self.validate_query_requests_count(query_iterable, 12 * 2 + 1)

        query_iterable = created_collection.query_items(
            query=query,
            max_item_count=100
        )

        await self.validate_query_requests_count(query_iterable, 5)

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

    @pytest.mark.asyncio
    async def test_get_query_plan_through_gateway_async(self):
        await self._set_up()
        created_collection = await self.created_db.create_container_if_not_exists(
            str(uuid.uuid4()), PartitionKey(path="/pk"))
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

    @pytest.mark.asyncio
    async def test_unsupported_queries_async(self):
        await self._set_up()
        created_collection = await self.created_db.create_container_if_not_exists(
            str(uuid.uuid4()), PartitionKey(path="/pk"))
        queries = ['SELECT COUNT(1) FROM c', 'SELECT COUNT(1) + 5 FROM c', 'SELECT COUNT(1) + SUM(c) FROM c']
        for query in queries:
            query_iterable = created_collection.query_items(query=query)
            try:
                results = [item async for item in query_iterable]
                pytest.fail("query '{}' should have failed".format(query))
            except exceptions.CosmosHttpResponseError as e:
                assert e.status_code == 400

    @pytest.mark.asyncio
    async def test_query_with_non_overlapping_pk_ranges_async(self):
        await self._set_up()
        created_collection = await self.created_db.create_container_if_not_exists(
            str(uuid.uuid4()), PartitionKey(path="/pk"))
        query_iterable = created_collection.query_items("select * from c where c.pk='1' or c.pk='2'")
        assert [item async for item in query_iterable] == []

    @pytest.mark.asyncio
    async def test_offset_limit_async(self):
        await self._set_up()
        created_collection = await self.created_db.create_container_if_not_exists("offset_limit_" + str(uuid.uuid4()),
                                                                                  PartitionKey(path="/pk"))
        values = []
        for i in range(10):
            document_definition = {'pk': i, 'id': 'myId' + str(uuid.uuid4()), 'value': i // 3}
            current_document = await created_collection.create_item(body=document_definition)
            values.append(current_document['pk'])

        await self._validate_distinct_offset_limit(created_collection=created_collection,
                                             query='SELECT DISTINCT c["value"] from c ORDER BY c.pk OFFSET 0 LIMIT 2',
                                             results=[0, 1])

        await self._validate_distinct_offset_limit(created_collection=created_collection,
                                             query='SELECT DISTINCT c["value"] from c ORDER BY c.pk OFFSET 2 LIMIT 2',
                                             results=[2, 3])
        
        await self._validate_distinct_offset_limit(created_collection=created_collection,
                                             query='SELECT DISTINCT c["value"] from c ORDER BY c.pk OFFSET 4 LIMIT 3',
                                             results=[])

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
        assert list(map(lambda doc: doc['pk'], [item async for item in query_iterable])) == results

    async def _validate_distinct_offset_limit(self, created_collection, query, results):
        query_iterable = created_collection.query_items(query=query)
        assert list(map(lambda doc: doc['value'], [item async for item in query_iterable])) == results

    # TODO: Look into distinct query behavior to re-enable this test when possible
    @pytest.mark.skip("intermittent failures in the pipeline")
    async def test_distinct_async(self):
        await self._set_up()
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

        assert len(results) == len(query_results)
        query_results_strings = []
        result_strings = []
        for i in range(len(results)):
            query_results_strings.append(self._get_query_result_string(query_results[i], fields))
            result_strings.append(str(results[i]))
        if is_select:
            query_results_strings = sorted(query_results_strings)
            result_strings = sorted(result_strings)
        assert result_strings == query_results_strings

    def _get_query_result_string(self, query_result, fields):
        if type(query_result) is not dict:
            return str(query_result)
        res = str(query_result[fields[0]] if fields[0] in query_result else None)
        if len(fields) == 2:
            res = res + "," + str(query_result[fields[1]] if fields[1] in query_result else None)

        return res

    @pytest.mark.asyncio
    async def test_distinct_on_different_types_and_field_orders_async(self):
        await self._set_up()
        created_collection = await self.created_db.create_container_if_not_exists(
            str(uuid.uuid4()), PartitionKey(path="/id"))
        payloads = [
            {'id': str(uuid.uuid4()), 'f1': 1, 'f2': 'value', 'f3': 100000000000000000, 'f4': [1, 2, '3'], 'f5': {'f6': {'f7': 2}}},
            {'id': str(uuid.uuid4()), 'f2': '\'value', 'f4': [1.0, 2, '3'], 'f5': {'f6': {'f7': 2.0}}, 'f1': 1.0, 'f3': 100000000000000000.00},
            {'id': str(uuid.uuid4()), 'f3': 100000000000000000.0, 'f5': {'f6': {'f7': 2}}, 'f2': '\'value', 'f1': 1, 'f4': [1, 2.0, '3']}
        ]
        for pay in payloads:
            await created_collection.create_item(pay)

        await self._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct value c.f1 from c",
            expected_results=[1]
        )

        await self._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct value c.f2 from c",
            expected_results=['value', '\'value']
        )

        await self._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct value c.f2 from c order by c.f2",
            expected_results=['value', '\'value']
        )

        await self._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct value c.f3 from c",
            expected_results=[100000000000000000]
        )

        await self._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct value c.f4 from c",
            expected_results=[[1, 2, '3']]
        )

        await self._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct value c.f5.f6 from c",
            expected_results=[{'f7': 2}]
        )

        await self._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct c.f1, c.f2, c.f3 from c",
            expected_results=[{'f1': 1, 'f2': 'value', 'f3': 100000000000000000},
                              {'f1': 1.0, 'f2': '\'value', 'f3': 100000000000000000.00}]
        )

        await self._validate_distinct_on_different_types_and_field_orders(
            collection=created_collection,
            query="Select distinct c.f1, c.f2, c.f3 from c order by c.f1",
            expected_results=[{'f1': 1, 'f2': 'value', 'f3': 100000000000000000},
                              {'f1': 1.0, 'f2': '\'value', 'f3': 100000000000000000.00}]
        )

    @pytest.mark.asyncio
    async def test_paging_with_continuation_token_async(self):
        await self._set_up()
        created_collection = await self.created_db.create_container_if_not_exists(
            str(uuid.uuid4()), PartitionKey(path="/pk"))

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

    @pytest.mark.asyncio
    async def test_cross_partition_query_with_continuation_token_async(self):
        await self._set_up()
        created_collection = await self.created_db.create_container_if_not_exists(
            str(uuid.uuid4()),
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

        assert second_page['id'] == second_page_fetched_with_continuation_token['id']

    async def _validate_distinct_on_different_types_and_field_orders(self, collection, query, expected_results):
        query_iterable = collection.query_items(query)
        results = [item async for item in query_iterable]
        for i in range(len(expected_results)):
            assert results[i] in expected_results

    @pytest.mark.asyncio
    async def test_value_max_query_async(self):
        await self._set_up()
        container = await self.created_db.create_container_if_not_exists(
            str(uuid.uuid4()), PartitionKey(path="/id"))
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

    @pytest.mark.asyncio
    async def test_continuation_token_size_limit_query_async(self):
        await self._set_up()
        container = await self.created_db.create_container_if_not_exists(
            str(uuid.uuid4()), PartitionKey(path="/pk"))
        for i in range(1, 1000):
            await container.create_item(body=dict(pk='123', id=str(i), some_value=str(i % 3)))
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
