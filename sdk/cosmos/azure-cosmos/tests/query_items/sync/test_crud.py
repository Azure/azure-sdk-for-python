# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Original sync CRUD tests that call ``query_items``, re-run on the Rust path.

Source: ``tests/test_crud.py::TestCRUDOperations``. Each method keeps the
original steps, query inputs and assertions; only setup changed. Every client
uses ``_backend="rust"`` and each test owns a uniquely named database with the
``/pk`` container the original class setup provided, deleted afterwards.
Known Rust gaps are skipped at the failing step.
"""

import os
import time
import unittest
import uuid
from types import SimpleNamespace

import pytest
from azure.core import MatchConditions
from azure.core.pipeline.transport import RequestsTransport

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos import _retry_utility
from azure.cosmos.http_constants import HttpHeaders, StatusCodes
from azure.cosmos.partition_key import PartitionKey
from _client_transport import create_client_with_transport


@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosLong
@pytest.mark.cosmosAADCircuitBreaker
class TestCRUDOperations(unittest.TestCase):
    """Python CRUD Tests.
    """

    def __AssertHTTPFailureWithStatus(self, status_code, func, *args, **kwargs):
        """Assert HTTP failure with status.

        :Parameters:
            - `status_code`: int
            - `func`: function
        """
        try:
            func(*args, **kwargs)
            self.assertFalse(True, 'function should fail.')
        except exceptions.CosmosHttpResponseError as inst:
            self.assertEqual(inst.status_code, status_code)

    def setUp(self):
        self.host = os.environ["ACCOUNT_HOST"]
        self.masterKey = os.environ["ACCOUNT_KEY"]
        self.client = cosmos_client.CosmosClient(self.host, self.masterKey, _backend="rust")
        self.addCleanup(self.client.close)
        self._db_id = "qi_crud_" + uuid.uuid4().hex
        self.databaseForTest = self.client.create_database(self._db_id)
        self.addCleanup(self.client.delete_database, self._db_id)
        self.key_databaseForTest = self.databaseForTest
        self.configs = SimpleNamespace(
            TEST_DATABASE_ID=self._db_id,
            TEST_MULTI_PARTITION_CONTAINER_ID="multi_partition_" + uuid.uuid4().hex[:8])
        self.databaseForTest.create_container(
            id=self.configs.TEST_MULTI_PARTITION_CONTAINER_ID, partition_key=PartitionKey(path="/pk"))

    def _create_container_for_test(self, container_id, partition_key, **kwargs):
        """Create container via key-auth setup client (control-plane), return data-plane proxy."""
        self.key_databaseForTest.create_container(id=container_id, partition_key=partition_key, **kwargs)
        return self.databaseForTest.get_container_client(container_id)

    def _delete_container_for_test(self, container_id_or_container):
        """Delete container via key-auth setup client (control-plane)."""
        cid = container_id_or_container if isinstance(container_id_or_container, str) else container_id_or_container.id
        self.key_databaseForTest.delete_container(cid)

    def test_partitioned_collection_document_crud_and_query_rust(self):
        # Source: tests/test_crud.py::TestCRUDOperations.test_partitioned_collection_document_crud_and_query
        created_db = self.databaseForTest

        created_collection = self._create_container_for_test("crud-query-container", partition_key=PartitionKey("/pk"))

        document_definition = {'id': 'document',
                               'key': 'value',
                               'pk': 'pk'}

        created_document = created_collection.create_item(
            body=document_definition
        )

        self.assertEqual(created_document.get('id'), document_definition.get('id'))
        self.assertEqual(created_document.get('key'), document_definition.get('key'))

        # read document
        read_document = created_collection.read_item(
            item=created_document.get('id'),
            partition_key=created_document.get('pk')
        )

        self.assertEqual(read_document.get('id'), created_document.get('id'))
        self.assertEqual(read_document.get('key'), created_document.get('key'))

        # Read document feed doesn't require partitionKey as it's always a cross partition query
        documentlist = list(created_collection.read_all_items())
        self.assertEqual(1, len(documentlist))

        # replace document
        document_definition['key'] = 'new value'

        replaced_document = created_collection.replace_item(
            item=read_document,
            body=document_definition
        )

        self.assertEqual(replaced_document.get('key'), document_definition.get('key'))

        # upsert document(create scenario)
        new_document_definition = {'id': 'document2',
                               'key': 'value2',
                               'pk': 'pk'}

        upserted_document = created_collection.upsert_item(body=new_document_definition)

        self.assertEqual(upserted_document.get('id'), new_document_definition.get('id'))
        self.assertEqual(upserted_document.get('key'), new_document_definition.get('key'))

        documentlist = list(created_collection.read_all_items())
        self.assertEqual(2, len(documentlist))

        # delete document
        created_collection.delete_item(item=upserted_document, partition_key=upserted_document.get('pk'))

        # query document on the partition key specified in the predicate will pass even without setting enableCrossPartitionQuery or passing in the partitionKey value
        documentlist = list(created_collection.query_items(
            {
                'query': 'SELECT * FROM root r WHERE r.id=\'' + replaced_document.get('id') + '\''  # nosec
            }, enable_cross_partition_query=True))
        self.assertEqual(1, len(documentlist))

        # query document on any property other than partitionKey will fail without setting enableCrossPartitionQuery or passing in the partitionKey value
        try:
            list(created_collection.query_items(
                {
                    'query': 'SELECT * FROM root r WHERE r.key=\'' + replaced_document.get('key') + '\''  # nosec
                }))
        except Exception:
            pass

        # cross partition query
        documentlist = list(created_collection.query_items(
            query='SELECT * FROM root r WHERE r.key=\'' + replaced_document.get('key') + '\'',  # nosec
            enable_cross_partition_query=True
        ))

        self.assertEqual(1, len(documentlist))

        # query document by providing the partitionKey value
        documentlist = list(created_collection.query_items(
            query='SELECT * FROM root r WHERE r.key=\'' + replaced_document.get('key') + '\'',  # nosec
            partition_key=replaced_document.get('pk')
        ))

        self.assertEqual(1, len(documentlist))
        self._delete_container_for_test(created_collection.id)

    def test_document_crud_rust(self):
        # Source: tests/test_crud.py::TestCRUDOperations.test_document_crud
        # create database
        created_db = self.databaseForTest
        # create collection
        created_collection = self.databaseForTest.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)
        # read documents
        documents = list(created_collection.read_all_items())
        # create a document
        before_create_documents_count = len(documents)

        # create a document with auto ID generation
        document_definition = {'name': 'sample document',
                               'spam': 'eggs',
                               'key': 'value',
                               'pk': 'pk'}

        no_response = created_collection.create_item(body=document_definition, enable_automatic_id_generation=True, no_response=True)
        self.assertDictEqual(no_response, {})

        created_document = created_collection.create_item(body=document_definition, enable_automatic_id_generation=True)
        self.assertEqual(created_document.get('name'),
                         document_definition['name'])

        document_definition = {'name': 'sample document',
                               'spam': 'eggs',
                               'key': 'value',
                               'pk': 'pk',
                               'id': str(uuid.uuid4())}

        created_document = created_collection.create_item(body=document_definition)
        self.assertEqual(created_document.get('name'),
                         document_definition['name'])
        self.assertEqual(created_document.get('id'),
                         document_definition['id'])

        # duplicated documents are not allowed when 'id' is provided.
        duplicated_definition_with_id = document_definition.copy()
        self.__AssertHTTPFailureWithStatus(StatusCodes.CONFLICT,
                                           created_collection.create_item,
                                           duplicated_definition_with_id)
        # read documents after creation
        documents = list(created_collection.read_all_items())
        self.assertEqual(
            len(documents),
            before_create_documents_count + 3,
            'create should increase the number of documents')
        # query documents
        documents = list(created_collection.query_items(
            {
                'query': 'SELECT * FROM root r WHERE r.name=@name',
                'parameters': [
                    {'name': '@name', 'value': document_definition['name']}
                ]
            }, enable_cross_partition_query=True
        ))
        self.assertTrue(documents)
        documents = list(created_collection.query_items(
            {
                'query': 'SELECT * FROM root r WHERE r.name=@name',
                'parameters': [
                    {'name': '@name', 'value': document_definition['name']}
                ],
            }, enable_cross_partition_query=True,
            enable_scan_in_query=True
        ))
        self.assertTrue(documents)
        # replace document.
        created_document['name'] = 'replaced document'
        created_document['spam'] = 'not eggs'
        old_etag = created_document['_etag']
        replaced_document = created_collection.replace_item(
            item=created_document['id'],
            body=created_document
        )
        self.assertEqual(replaced_document['name'],
                         'replaced document',
                         'document id property should change')
        self.assertEqual(replaced_document['spam'],
                         'not eggs',
                         'property should have changed')
        self.assertEqual(created_document['id'],
                         replaced_document['id'],
                         'document id should stay the same')

        # replace document based on condition
        replaced_document['name'] = 'replaced document based on condition'
        replaced_document['spam'] = 'new spam field'

        # should fail for stale etag
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.PRECONDITION_FAILED,
            created_collection.replace_item,
            replaced_document['id'],
            replaced_document,
            if_match=old_etag,
        )

        # should fail if only etag specified
        with self.assertRaises(ValueError):
            created_collection.replace_item(
                etag=replaced_document['_etag'],
                item=replaced_document['id'],
                body=replaced_document
            )

        # should fail if only match condition specified
        with self.assertRaises(ValueError):
            created_collection.replace_item(
                match_condition=MatchConditions.IfNotModified,
                item=replaced_document['id'],
                body=replaced_document
            )
        with self.assertRaises(ValueError):
            created_collection.replace_item(
                match_condition=MatchConditions.IfModified,
                item=replaced_document['id'],
                body=replaced_document
            )

        # should fail if invalid match condition specified
        with self.assertRaises(TypeError):
            created_collection.replace_item(
                match_condition=replaced_document['_etag'],
                item=replaced_document['id'],
                body=replaced_document
            )

        # should pass for most recent etag
        replaced_document_conditional = created_collection.replace_item(
            match_condition=MatchConditions.IfNotModified,
            etag=replaced_document['_etag'],
            item=replaced_document['id'],
            body=replaced_document
        )
        self.assertEqual(replaced_document_conditional['name'],
                         'replaced document based on condition',
                         'document id property should change')
        self.assertEqual(replaced_document_conditional['spam'],
                         'new spam field',
                         'property should have changed')
        self.assertEqual(replaced_document_conditional['id'],
                         replaced_document['id'],
                         'document id should stay the same')
        # read document
        one_document_from_read = created_collection.read_item(
            item=replaced_document['id'],
            partition_key=replaced_document['pk']
        )
        self.assertEqual(replaced_document['id'],
                         one_document_from_read['id'])
        # delete document
        created_collection.delete_item(
            item=replaced_document,
            partition_key=replaced_document['pk']
        )
        # read documents after deletion
        self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND,
                                           created_collection.read_item,
                                           replaced_document['id'],
                                           replaced_document['id'])

    def test_geospatial_index_rust(self):
        # Source: tests/test_crud.py::TestCRUDOperations.test_geospatial_index
        db = self.databaseForTest
        # partial policy specified
        collection = self._create_container_for_test(
            container_id='collection with spatial index ' + str(uuid.uuid4()),
            partition_key=PartitionKey(path='/id', kind='Hash'),
            indexing_policy={
                'includedPaths': [
                    {
                        'path': '/"Location"/?',
                        'indexes': [
                            {
                                'kind': 'Spatial',
                                'dataType': 'Point'
                            }
                        ]
                    },
                    {
                        'path': '/'
                    }
                ]
            }
        )
        collection.create_item(
            body={
                'id': 'loc1',
                'Location': {
                    'type': 'Point',
                    'coordinates': [20.0, 20.0]
                }
            }
        )
        collection.create_item(
            body={
                'id': 'loc2',
                'Location': {
                    'type': 'Point',
                    'coordinates': [100.0, 100.0]
                }
            }
        )
        results = list(collection.query_items(
            query="SELECT * FROM root WHERE (ST_DISTANCE(root.Location, {type: 'Point', coordinates: [20.1, 20]}) < 20000)",
            enable_cross_partition_query=True
        ))
        self.assertEqual(1, len(results))
        self.assertEqual('loc1', results[0]['id'])

        self._delete_container_for_test(collection)

    def test_timeout_for_paged_request_rust(self):
        # Source: tests/test_crud.py::TestCRUDOperations.test_timeout_for_paged_request
        """Test that timeout applies to each individual page request, not cumulatively"""

        # Create container and add items
        created_container = self._create_container_for_test(
            container_id='paged_timeout_container_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk")
        )

        # Create enough items to ensure multiple pages
        for i in range(100):
            created_container.create_item({'id': f'item_{i}', 'pk': i % 10, 'data': 'x' * 1000})

        # Create a transport that delays each request
        class DelayedTransport(RequestsTransport):
            def __init__(self, delay_seconds=3):
                self.delay_seconds = delay_seconds
                super().__init__()

            def send(self, request, **kwargs):
                time.sleep(self.delay_seconds)
                return super().send(request, **kwargs)

        # Test with delayed transport
        delayed_transport = DelayedTransport(delay_seconds=3)
        client_with_delay = create_client_with_transport(cosmos_client.CosmosClient,
            self.host, self.masterKey, transport=delayed_transport, _backend="rust"
        )
        container_with_delay = client_with_delay.get_database_client(
            self.databaseForTest.id
        ).get_container_client(created_container.id)

        # Test 1: Timeout should apply per page
        item_pages = container_with_delay.query_items(
            query="SELECT * FROM c",
            enable_cross_partition_query=True,
            max_item_count=10,  # Small page size
            timeout=5  # Pass timeout here
        ).by_page()

        # First page should succeed with 5s timeout (3s delay < 5s timeout)
        first_page = list(next(item_pages))
        self.assertGreater(len(first_page), 0)

        # Second page should also succeed (timeout resets per page)
        second_page = list(next(item_pages))
        self.assertGreater(len(second_page), 0)

        # Test 2: Timeout too short should fail
        item_pages_short_timeout = container_with_delay.query_items(
            query="SELECT * FROM c",
            enable_cross_partition_query=True,
            max_item_count=10,
            timeout=2  # 2s timeout < 3s delay, should fail
        ).by_page()

        # Known gap 10: Closed by design: client-level proxy configuration, custom CA, client certificate, and transport options are excluded.
        # The Rust client never calls the injected DelayedTransport, so no request is delayed.
        pytest.skip("accepted-vnext-change: the Rust client ignores the injected custom transport, so the 3 s per-request delay never happens and the 2 s page timeout cannot fire (known gap 10, "
                    "docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-10). The per-page 5 s timeout steps ran.")
        with self.assertRaises(exceptions.CosmosClientTimeoutError):
            list(next(item_pages_short_timeout))

        # Cleanup
        self.key_databaseForTest.delete_container(created_container.id)

    def test_priority_level_rust(self):
        # Source: tests/test_crud.py::TestCRUDOperations.test_priority_level
        # These test verify if headers for priority level are sent
        # Feature must be enabled at the account level
        # If feature is not enabled the test will still pass as we just verify the headers were sent
        created_container = self.databaseForTest.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

        item1 = {"id": "item1", "pk": "pk1"}
        item2 = {"id": "item2", "pk": "pk2"}
        self.OriginalExecuteFunction = _retry_utility.ExecuteFunction
        self.addCleanup(setattr, _retry_utility, "ExecuteFunction", self.OriginalExecuteFunction)
        priority_headers = []

        # mock execute function to check if priority level set in headers

        def priority_mock_execute_function(function, *args, **kwargs):
            if args:
                priority_headers.append(args[4].headers[HttpHeaders.PriorityLevel]
                                              if HttpHeaders.PriorityLevel in args[4].headers else '')
            return self.OriginalExecuteFunction(function, *args, **kwargs)

        _retry_utility.ExecuteFunction = priority_mock_execute_function
        # upsert item with high priority
        created_container.upsert_item(body=item1, priority="High")
        # check if the priority level was passed
        # Known gap 6: Closed by design: `raw_request_hook` removed from both backends. Rust never calls legacy
        # _retry_utility.ExecuteFunction and its outgoing request headers are not observable.
        pytest.skip("internals-only: the priority header was observed by patching legacy "
                    "_retry_utility.ExecuteFunction; Rust outgoing request headers are not observable "
                    "(known gap 6, docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-6). The High-priority upsert ran.")
        self.assertEqual(priority_headers[-1], "High")
        # upsert item with low priority
        created_container.upsert_item(body=item2, priority="Low")
        # check that headers passed low priority
        self.assertEqual(priority_headers[-1], "Low")
        # Repeat for read operations
        item1_read = created_container.read_item("item1", "pk1", priority="High")
        self.assertEqual(priority_headers[-1], "High")
        item2_read = created_container.read_item("item2", "pk2", priority="Low")
        self.assertEqual(priority_headers[-1], "Low")
        # repeat for query
        query = list(created_container.query_items("Select * from c", partition_key="pk1", priority="High"))

        self.assertEqual(priority_headers[-1], "High")

        # Negative Test: Verify that if we send a value other than High or Low that it will not set the header value
        # and result in bad request
        try:
            item2_read = created_container.read_item("item2", "pk2", priority="Medium")
        except exceptions.CosmosHttpResponseError as e:
            self.assertEqual(e.status_code, StatusCodes.BAD_REQUEST)
        _retry_utility.ExecuteFunction = self.OriginalExecuteFunction
