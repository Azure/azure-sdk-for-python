# -*- coding: utf-8 -*-
# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""End-to-end test.
"""
import logging
import threading
import time
import unittest
import urllib.parse as urllib
import uuid
import os

import pytest
import requests
from azure.core import MatchConditions
from azure.core.exceptions import AzureError, ServiceResponseError, ServiceRequestError
from azure.core.pipeline.transport import RequestsTransport, RequestsTransportResponse
from urllib3.util.retry import Retry

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.documents as documents
import azure.cosmos.exceptions as exceptions
import test_config
from azure.cosmos import _retry_utility
from azure.cosmos.http_constants import HttpHeaders, StatusCodes
from azure.cosmos.partition_key import PartitionKey
from _client_transport import create_client_with_transport


# Server-side scripts CRUD (sproc/trigger/UDF create/list/get/replace/delete)
# is not in the AAD/RBAC data-plane action set today.
# Empirically these operations return 403 under AAD in data-plane tests.
# Stored procedure EXECUTE is currently also skipped under AAD in this class.
# TODO: re-enable these under AAD once the service exposes RBAC actions for these APIs.
_skip_under_aad = pytest.mark.skipif(
    test_config.TestConfig.data_auth_mode == 'aad',
    reason="server-side scripts CRUD is not authorized via AAD/RBAC "
           "data plane today (403).",
)


class TimeoutTransport(RequestsTransport):

    def __init__(self, response, passthrough=False):
        self._response = response
        self.passthrough = passthrough
        super(TimeoutTransport, self).__init__()

    def send(self, *args, **kwargs):
        if self.passthrough:
            return super(TimeoutTransport, self).send(*args, **kwargs)

        time.sleep(5)
        if isinstance(self._response, Exception):
            raise self._response
        output = requests.Response()
        output.status_code = self._response
        response = RequestsTransportResponse(None, output)
        return response

@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosLong
@pytest.mark.cosmosAADCircuitBreaker
class TestCRUDOperations(unittest.TestCase):
    """Python CRUD Tests.
    """

    configs = test_config.TestConfig
    host = configs.host
    masterKey = configs.masterKey
    connectionPolicy = configs.connectionPolicy
    last_headers = []
    client: cosmos_client.CosmosClient = None
    key_client: cosmos_client.CosmosClient = None

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

    @classmethod
    def setUpClass(cls):
        use_multiple_write_locations = False
        if os.environ.get("AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER", "False") == "True":
            use_multiple_write_locations = True
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")
        # Key-auth client for control-plane operations (create/delete containers, sprocs)
        cls.key_client, cls.key_databaseForTest, cls.client, cls.databaseForTest = (
            test_config.TestConfig.create_test_clients(cls.configs.TEST_DATABASE_ID, multiple_write_locations=use_multiple_write_locations))

    @classmethod
    def tearDownClass(cls):
        if cls.client:
            cls.client.close()
        if cls.key_client:
            cls.key_client.close()

    def _create_container_for_test(self, container_id, partition_key, **kwargs):
        """Create container via key-auth setup client (control-plane), return data-plane proxy."""
        # Container creation is a control-plane operation routed through key_client (key-auth).
        self.key_databaseForTest.create_container(id=container_id, partition_key=partition_key, **kwargs)
        return self.databaseForTest.get_container_client(container_id)

    def _delete_container_for_test(self, container_id_or_container):
        """Delete container via key-auth setup client (control-plane)."""
        cid = container_id_or_container if isinstance(container_id_or_container, str) else container_id_or_container.id
        self.key_databaseForTest.delete_container(cid)

    def test_partitioned_collection_document_crud_and_query(self):
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

    def test_partitioned_collection_partition_key_value_types(self):
        created_db = self.databaseForTest

        created_collection = created_db.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

        document_definition = {'id': 'document1' + str(uuid.uuid4()),
                               'pk': None,
                               'spam': 'eggs'}

        # create document with partitionKey set as None here
        created_collection.create_item(body=document_definition)

        document_definition = {'id': 'document1' + str(uuid.uuid4()),
                               'spam': 'eggs'}

        # create document with partitionKey set as Undefined here
        created_collection.create_item(body=document_definition)

        document_definition = {'id': 'document1' + str(uuid.uuid4()),
                               'pk': True,
                               'spam': 'eggs'}

        # create document with bool partitionKey
        created_collection.create_item(body=document_definition)

        document_definition = {'id': 'document1' + str(uuid.uuid4()),
                               'pk': 'value',
                               'spam': 'eggs'}

        # create document with string partitionKey
        created_collection.create_item(body=document_definition)

        document_definition = {'id': 'document1' + str(uuid.uuid4()),
                               'pk': 100,
                               'spam': 'eggs'}

        # create document with int partitionKey
        created_collection.create_item(body=document_definition)

        document_definition = {'id': 'document1' + str(uuid.uuid4()),
                               'pk': 10.50,
                               'spam': 'eggs'}

        # create document with float partitionKey
        created_collection.create_item(body=document_definition)

        document_definition = {'name': 'sample document',
                               'spam': 'eggs',
                               'pk': 'value'}

        # Should throw an error because automatic id generation is disabled always.
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.BAD_REQUEST,
            created_collection.create_item,
            document_definition
        )

    def test_document_crud(self):
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

    def test_read_collection_only_once(self):
        # Add filter to the filtered diagnostics handler
        mock_handler = test_config.MockHandler()
        logger = logging.getLogger("azure.cosmos")
        logger.setLevel(logging.INFO)
        logger.addHandler(mock_handler)

        client = cosmos_client.CosmosClient(self.host, self.masterKey)
        database = client.get_database_client(self.configs.TEST_DATABASE_ID)
        container = database.get_container_client(self.configs.TEST_SINGLE_PARTITION_CONTAINER_ID)

        def upsert_worker():
            # Synchronously perform the upsert item operation
            container.upsert_item(body={'id': str(uuid.uuid4()), 'name': f'sample-'})

        # Perform 10 concurrent upserts
        threads = []
        for i in range(10):
            t = threading.Thread(target=upsert_worker)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()
        assert sum("'x-ms-thinclient-proxy-resource-type': 'colls'" in response.message for response in mock_handler.messages) == 1


    def test_document_upsert(self):
        # create database
        created_db = self.databaseForTest

        # create collection
        created_collection = self.databaseForTest.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

        # read documents and check count
        documents = list(created_collection.read_all_items())
        before_create_documents_count = len(documents)

        # create document definition
        document_definition = {'id': 'doc',
                               'name': 'sample document',
                               'spam': 'eggs',
                               'pk': 'pk',
                               'key': 'value'}

        # create document using Upsert API
        created_document = created_collection.upsert_item(body=document_definition)

        # verify id property
        self.assertEqual(created_document['id'],
                         document_definition['id'])

        # test error for non-string id
        with self.assertRaises(TypeError):
            document_definition['id'] = 7
            created_collection.upsert_item(body=document_definition)

        # read documents after creation and verify updated count
        documents = list(created_collection.read_all_items())
        self.assertEqual(
            len(documents),
            before_create_documents_count + 1,
            'create should increase the number of documents')

        stored_document = created_collection.read_item(item='doc', partition_key='pk')
        self.assertEqual(
            {key: stored_document[key] for key in ('id', 'name', 'spam', 'pk', 'key')},
            {'id': 'doc', 'name': 'sample document', 'spam': 'eggs', 'pk': 'pk', 'key': 'value'})

        # update document
        created_document['name'] = 'replaced document'
        created_document['spam'] = 'not eggs'

        # should replace document since it already exists
        upserted_document = created_collection.upsert_item(body=created_document)

        # verify the changed properties
        self.assertEqual(upserted_document['name'],
                         created_document['name'],
                         'document name property should change')
        self.assertEqual(upserted_document['spam'],
                         created_document['spam'],
                         'property should have changed')

        # verify id property
        self.assertEqual(upserted_document['id'],
                         created_document['id'],
                         'document id should stay the same')

        # read documents after upsert and verify count doesn't increases again
        documents = list(created_collection.read_all_items())
        self.assertEqual(
            len(documents),
            before_create_documents_count + 1,
            'number of documents should remain same')

        stored_document = created_collection.read_item(item='doc', partition_key='pk')
        self.assertEqual(
            {key: stored_document[key] for key in ('id', 'name', 'spam', 'pk', 'key')},
            {'id': 'doc', 'name': 'replaced document', 'spam': 'not eggs', 'pk': 'pk', 'key': 'value'})

        created_document['id'] = 'new id'

        # Upsert should create new document since the id is different
        new_document = created_collection.upsert_item(body=created_document)

        # Test modified access conditions
        created_document['spam'] = 'more eggs'
        created_collection.upsert_item(body=created_document)
        with self.assertRaises(exceptions.CosmosHttpResponseError):
            created_collection.upsert_item(
                body=created_document,
                match_condition=MatchConditions.IfNotModified,
                etag=new_document['_etag'])

        # verify id property
        self.assertEqual(created_document['id'],
                         new_document['id'],
                         'document id should be same')

        # read documents after upsert and verify count increases
        documents = list(created_collection.read_all_items())
        self.assertEqual(
            len(documents),
            before_create_documents_count + 2,
            'upsert should increase the number of documents')

        # delete documents
        created_collection.delete_item(item=upserted_document, partition_key=upserted_document['pk'])
        created_collection.delete_item(item=new_document, partition_key=new_document['pk'])

        # read documents after delete and verify count is same as original
        documents = list(created_collection.read_all_items())
        self.assertEqual(
            len(documents),
            before_create_documents_count,
            'number of documents should remain same')

    def test_geospatial_index(self):
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

    def test_authorization(self):
        with self.assertRaises(ValueError):
            cosmos_client.CosmosClient(TestCRUDOperations.host, {}, "Session",
                                       connection_policy=TestCRUDOperations.connectionPolicy)


    def test_database_account_connection_timeout(self):
        connection_policy = documents.ConnectionPolicy()
        connection_policy.DBAConnectionTimeout = 0.000000000001
        with self.assertRaises(ServiceRequestError):
            with cosmos_client.CosmosClient(self.host, self.masterKey, connection_policy=connection_policy):
                print('initialization')


    # TODO: Skipping this test to debug later
    @unittest.skip
    def test_client_connection_retry_configuration(self):
        total_time_for_two_retries = self.initialize_client_with_connection_core_retry_config(2)
        total_time_for_three_retries = self.initialize_client_with_connection_core_retry_config(3)
        self.assertGreater(total_time_for_three_retries, total_time_for_two_retries)

    def initialize_client_with_connection_core_retry_config(self, retries):
        start_time = time.time()
        try:
            cosmos_client.CosmosClient(
                "https://localhost:9999",
                TestCRUDOperations.masterKey,
                "Session",
                retry_total=retries,
                retry_read=retries,
                retry_connect=retries,
                retry_status=retries)
            self.fail()
        except AzureError as e:
            end_time = time.time()
            return end_time - start_time

    def test_timeout_on_connection_error(self):
        # Connection Refused: This is an active rejection from the target machine's operating system. It receives your
        # connection request but immediately sends back a response indicating that no process is listening on that port.
        # This is a fast failure.
        # Connection Timeout Setting: This occurs when your connection request receives no response at all within a
        # specified period. The client gives up waiting. This typically happens if the target machine is down,
        # unreachable due to network configuration, or a firewall is silently dropping the packets.
        # so in the below test connection_timeout setting has no bearing on the test outcome
        # catching both exceptions to make the test the test reliable in different environment as
        # the underlying operating system and network stack handle the connection attempt to a non-existent port in different ways

        with self.assertRaises((exceptions.CosmosClientTimeoutError, ServiceRequestError)):
            cosmos_client.CosmosClient(
                "https://localhost:9999",
                TestCRUDOperations.masterKey,
                retry_total=50,
                connection_timeout=100,
                timeout=10)

    def test_timeout_on_read_operation(self):
        error_response = ServiceResponseError("Read timeout")
        # Initialize transport with passthrough enabled for client setup
        timeout_transport = TimeoutTransport(error_response, passthrough=True)

        client = create_client_with_transport(cosmos_client.CosmosClient,
            self.host, self.masterKey, "Session", transport=timeout_transport)
        timeout_transport.passthrough = False
        with self.assertRaises(exceptions.CosmosClientTimeoutError):
            client.create_database_if_not_exists("test", timeout=2)

    def test_timeout_on_throttling_error(self):
        # Throttling(429): Keeps retrying -> Eventually times out -> CosmosClientTimeoutError
        status_response = 429  # Uses Cosmos custom retry
        timeout_transport = TimeoutTransport(status_response, passthrough=True)
        client = create_client_with_transport(cosmos_client.CosmosClient,
            self.host, self.masterKey, "Session", transport=timeout_transport)

        timeout_transport.passthrough = False
        with self.assertRaises(exceptions.CosmosClientTimeoutError):
            client.create_database_if_not_exists("test", timeout=30)

        databases = client.list_databases(timeout=29)
        with self.assertRaises(exceptions.CosmosClientTimeoutError):
            list(databases)

    def test_inner_exceptions_on_timeout(self):
        # Throttling(429): Keeps retrying -> Eventually times out -> CosmosClientTimeoutError
        status_response = 429  # Uses Cosmos custom retry
        timeout_transport = TimeoutTransport(status_response, passthrough=True)
        client = create_client_with_transport(cosmos_client.CosmosClient,
            self.host, self.masterKey, "Session", transport=timeout_transport)

        timeout_transport.passthrough = False
        with self.assertRaises(exceptions.CosmosClientTimeoutError) as cm:
            client.create_database_if_not_exists("test", timeout=30)

        # Verify the inner_exception is set and is a 429 error
        self.assertIsNotNone(cm.exception.inner_exception)
        self.assertIsInstance(cm.exception.inner_exception, exceptions.CosmosHttpResponseError)
        self.assertEqual(cm.exception.inner_exception.status_code, 429)

    def test_timeout_for_read_items(self):
        """Test that timeout is properly maintained across multiple partition requests for a single logical operation
        read_items is different as the results of this api are not paginated and we present the complete result set
        """

        # Create a container with multiple partitions
        created_container = self._create_container_for_test(
            container_id='multi_partition_container_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=11000
        )
        client_with_delay = None
        try:
            pk_ranges = list(created_container.client_connection._ReadPartitionKeyRanges(
                created_container.container_link))
            self.assertGreater(len(pk_ranges), 1, "Container should have multiple physical partitions.")

            # 2. Create items across different logical partitions
            items_to_read = []
            all_item_ids = set()
            for i in range(200):
                doc_id = f"item_{i}_{uuid.uuid4()}"
                pk = i % 10
                all_item_ids.add(doc_id)
                created_container.create_item({'id': doc_id, 'pk': pk, 'data': i})
                items_to_read.append((doc_id, pk))

            # Create a custom transport that introduces delays
            class DelayedTransport(RequestsTransport):
                def __init__(self, delay_per_request=3):
                    self.delay_per_request = delay_per_request
                    self.request_count = 0
                    super().__init__()

                def send(self, request, **kwargs):
                    self.request_count += 1
                    # Delay each request to simulate slow network (3s, exceeds 5s timeout with >=2 partitions)
                    time.sleep(self.delay_per_request)
                    return super().send(request, **kwargs)

            # Verify timeout fails when cumulative time exceeds limit
            delayed_transport = DelayedTransport(delay_per_request=3)
            client_with_delay = create_client_with_transport(cosmos_client.CosmosClient,
                self.host,
                self.masterKey,
                transport=delayed_transport
            )
            container_with_delay = client_with_delay.get_database_client(
                self.databaseForTest.id
            ).get_container_client(created_container.id)

            start_time = time.time()
            with self.assertRaises(exceptions.CosmosClientTimeoutError):
                # This should timeout because multiple partition requests * 3s delay > 5s timeout
                list(container_with_delay.read_items(
                    items = items_to_read,
                    timeout = 5  # 5 second total timeout
                ))

            elapsed_time = time.time() - start_time

            # Should fail close to 5 seconds (not wait for all requests). Upper bound
            # is loose to absorb the cold-cache /pkranges drain (a 200+ETag fetch followed
            # by a 304 confirmation, see PR #47245) which adds one extra round trip --
            # under DelayedTransport(3s) that is +3s on top of the data-plane delay.
            self.assertLess(elapsed_time, 12)  # Allow overhead for the cold-cache drain round trips
            self.assertGreater(elapsed_time, 5)  # Should wait at least close to timeout

            # Verify operation succeeds when no timeout is passed(default is close to 7 days)
            start_time = time.time()
            # add few more items
            for i in range(500):
                doc_id = f"item_{i}_{uuid.uuid4()}"
                pk = i % 10
                all_item_ids.add(doc_id)
                created_container.create_item({'id': doc_id, 'pk': pk, 'data': i})
                items_to_read.append((doc_id, pk))

            items = list(container_with_delay.read_items(
                items=items_to_read,
            ))

            elapsed_time = time.time() - start_time
        finally:
            if client_with_delay:
                client_with_delay.close()
            self._delete_container_for_test(created_container.id)


    def test_timeout_for_paged_request(self):
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
            self.host, self.masterKey, transport=delayed_transport
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

        with self.assertRaises(exceptions.CosmosClientTimeoutError):
            list(next(item_pages_short_timeout))

        # Cleanup
        self.key_databaseForTest.delete_container(created_container.id)

    def test_timeout_for_point_operation(self):
        """Test that point operations respect client timeout"""

        # Create a container for testing
        created_container = self._create_container_for_test(
            container_id='point_op_timeout_container_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk")
        )
        try:
            # Create a test item
            test_item = {
                'id': 'test_item_1',
                'pk': 'partition1',
                'data': 'test_data'
            }
            created_container.create_item(test_item)

            # Test 1: Short timeout should fail
            with self.assertRaises(exceptions.CosmosClientTimeoutError):
                created_container.read_item(
                    item='test_item_1',
                    partition_key='partition1',
                    timeout=0.00000002  # very small timeout to force failure
                )

            # Test 2: Long timeout should succeed
            result = created_container.read_item(
                item='test_item_1',
                partition_key='partition1',
                timeout=3.0
            )
            self.assertEqual(result['id'], 'test_item_1')
        finally:
            self._delete_container_for_test(created_container.id)





    # TODO: for read timeouts azure-core returns a ServiceResponseError, needs to be fixed in azure-core and then this test can be enabled

    # TODO: for read timeouts azure-core returns a ServiceResponseError, needs to be fixed in azure-core and then this test can be enabled


    def test_query_iterable_functionality(self):
        collection = self._create_container_for_test("query-iterable-container",
                                                     partition_key=PartitionKey("/pk"))

        doc1 = collection.create_item(body={'id': 'doc1', 'prop1': 'value1', 'pk': 'pk'})
        doc2 = collection.create_item(body={'id': 'doc2', 'prop1': 'value2', 'pk': 'pk'})
        doc3 = collection.create_item(body={'id': 'doc3', 'prop1': 'value3', 'pk': 'pk'})
        resources = {
            'coll': collection,
            'doc1': doc1,
            'doc2': doc2,
            'doc3': doc3
        }

        results = resources['coll'].read_all_items(max_item_count=2)
        docs = list(iter(results))
        self.assertEqual(3,
                         len(docs),
                         'QueryIterable should return all documents' +
                         ' using continuation')
        self.assertEqual(resources['doc1']['id'], docs[0]['id'])
        self.assertEqual(resources['doc2']['id'], docs[1]['id'])
        self.assertEqual(resources['doc3']['id'], docs[2]['id'])

        # Validate QueryIterable iterator with 'for'.
        results = resources['coll'].read_all_items(max_item_count=2)
        counter = 0
        # test QueryIterable with 'for'.
        for doc in iter(results):
            counter += 1
            if counter == 1:
                self.assertEqual(resources['doc1']['id'],
                                 doc['id'],
                                 'first document should be doc1')
            elif counter == 2:
                self.assertEqual(resources['doc2']['id'],
                                 doc['id'],
                                 'second document should be doc2')
            elif counter == 3:
                self.assertEqual(resources['doc3']['id'],
                                 doc['id'],
                                 'third document should be doc3')
        self.assertEqual(counter, 3)

        # Get query results page by page.
        results = resources['coll'].read_all_items(max_item_count=2)

        page_iter = results.by_page()
        first_block = list(next(page_iter))
        self.assertEqual(2, len(first_block), 'First block should have 2 entries.')
        self.assertEqual(resources['doc1']['id'], first_block[0]['id'])
        self.assertEqual(resources['doc2']['id'], first_block[1]['id'])
        self.assertEqual(1, len(list(next(page_iter))), 'Second block should have 1 entry.')
        with self.assertRaises(StopIteration):
            next(page_iter)

        self._delete_container_for_test(collection.id)

    def test_get_resource_with_dictionary_and_object(self):
        created_db = self.databaseForTest

        # read database with id
        read_db = self.client.get_database_client(created_db.id)
        self.assertEqual(read_db.id, created_db.id)

        # read database with instance
        read_db = self.client.get_database_client(created_db)
        self.assertEqual(read_db.id, created_db.id)

        # read database with properties
        read_db = self.client.get_database_client(created_db.read())
        self.assertEqual(read_db.id, created_db.id)

        created_container = self.databaseForTest.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

        # read container with id
        read_container = created_db.get_container_client(created_container.id)
        self.assertEqual(read_container.id, created_container.id)

        # read container with instance
        read_container = created_db.get_container_client(created_container)
        self.assertEqual(read_container.id, created_container.id)

        # read container with properties
        created_properties = created_container.read()
        read_container = created_db.get_container_client(created_properties)
        self.assertEqual(read_container.id, created_container.id)

        created_item = created_container.create_item({'id': '1' + str(uuid.uuid4()), 'pk': 'pk'})

        # read item with id
        read_item = created_container.read_item(item=created_item['id'], partition_key=created_item['pk'])
        self.assertEqual(read_item['id'], created_item['id'])

        # read item with properties
        read_item = created_container.read_item(item=created_item, partition_key=created_item['pk'])
        self.assertEqual(read_item['id'], created_item['id'])

    def test_delete_all_items_by_partition_key(self):
        # create container via setup client (control-plane)
        created_collection = self._create_container_for_test(
            container_id='test_delete_all_items_by_partition_key_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path='/pk', kind='Hash')
        )
        # Create two partition keys
        partition_key1 = "{}-{}".format("Partition Key 1", str(uuid.uuid4()))
        partition_key2 = "{}-{}".format("Partition Key 2", str(uuid.uuid4()))

        # add items for partition key 1
        for i in range(1, 3):
            created_collection.upsert_item(
                dict(id="item{}".format(i), pk=partition_key1)
            )

        # add items for partition key 2

        pk2_item = created_collection.upsert_item(dict(id="item{}".format(3), pk=partition_key2))

        try:
            # delete all items for partition key 1
            created_collection.delete_all_items_by_partition_key(partition_key1)
        except exceptions.CosmosHttpResponseError as e:
            error_text = " ".join(
                message for message in (getattr(e, "http_error_message", None), str(e))
                if message
            ).lower()
            if e.status_code == 400 and "partition key delete feature is disabled" in error_text:
                self._delete_container_for_test(created_collection)
                pytest.skip("delete_all_items_by_partition_key is not enabled for this account")
            raise

        # check that only items from partition key 1 have been deleted
        items = list(created_collection.read_all_items())

        # items should only have 1 item, and it should equal pk2_item
        self.assertDictEqual(pk2_item, items[0])

        # attempting to delete a non-existent partition key or passing none should not delete
        # anything and leave things unchanged
        created_collection.delete_all_items_by_partition_key(None)

        # check that no changes were made by checking if the only item is still there
        items = list(created_collection.read_all_items())

        # items should only have 1 item, and it should equal pk2_item
        self.assertDictEqual(pk2_item, items[0])

        self._delete_container_for_test(created_collection)

    def test_patch_operations(self):
        created_container = self.databaseForTest.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

        pkValue = "patch_item_pk" + str(uuid.uuid4())
        # Create item to patch
        item = {
            "id": "patch_item",
            "pk": pkValue,
            "prop": "prop1",
            "address": {
                "city": "Redmond"
            },
            "company": "Microsoft",
            "number": 3}
        created_container.create_item(item)
        # Define and run patch operations
        operations = [
            {"op": "add", "path": "/color", "value": "yellow"},
            {"op": "remove", "path": "/prop"},
            {"op": "replace", "path": "/company", "value": "CosmosDB"},
            {"op": "set", "path": "/address/new_city", "value": "Atlanta"},
            {"op": "incr", "path": "/number", "value": 7},
            {"op": "move", "from": "/color", "path": "/favorite_color"}
        ]
        patched_item = created_container.patch_item(item="patch_item", partition_key=pkValue,
                                                    patch_operations=operations)
        # Verify results from patch operations
        self.assertNotIn("color", patched_item)
        self.assertNotIn("prop", patched_item)
        self.assertEqual(patched_item.get("company"), "CosmosDB")
        self.assertEqual(patched_item.get("address").get("new_city"), "Atlanta")
        self.assertEqual(patched_item.get("number"), 10)
        self.assertEqual(patched_item.get("favorite_color"), "yellow")

        stored_item = created_container.read_item("patch_item", partition_key=pkValue)
        self.assertNotIn("color", stored_item)
        self.assertNotIn("prop", stored_item)
        self.assertEqual(stored_item.get("favorite_color"), "yellow")

        # Negative test - attempt to replace non-existent field
        operations = [{"op": "replace", "path": "/wrong_field", "value": "wrong_value"}]
        with self.assertRaises(exceptions.CosmosHttpResponseError) as caught:
            created_container.patch_item(item="patch_item", partition_key=pkValue, patch_operations=operations)
        self.assertEqual(caught.exception.status_code, StatusCodes.BAD_REQUEST)

        # Negative test - attempt to remove non-existent field
        operations = [{"op": "remove", "path": "/wrong_field"}]
        with self.assertRaises(exceptions.CosmosHttpResponseError) as caught:
            created_container.patch_item(item="patch_item", partition_key=pkValue, patch_operations=operations)
        self.assertEqual(caught.exception.status_code, StatusCodes.BAD_REQUEST)

        # Negative test - attempt to increment non-number field
        operations = [{"op": "incr", "path": "/company", "value": 3}]
        with self.assertRaises(exceptions.CosmosHttpResponseError) as caught:
            created_container.patch_item(item="patch_item", partition_key=pkValue, patch_operations=operations)
        self.assertEqual(caught.exception.status_code, StatusCodes.BAD_REQUEST)

        # Negative test - attempt to move from non-existent field
        operations = [{"op": "move", "from": "/wrong_field", "path": "/other_field"}]
        with self.assertRaises(exceptions.CosmosHttpResponseError) as caught:
            created_container.patch_item(item="patch_item", partition_key=pkValue, patch_operations=operations)
        self.assertEqual(caught.exception.status_code, StatusCodes.BAD_REQUEST)

    def test_conditional_patching(self):
        created_container = self.databaseForTest.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)
        # Create item to patch
        pkValue = "patch_item_pk" + str(uuid.uuid4())
        item = {
            "id": "conditional_patch_item",
            "pk": pkValue,
            "prop": "prop1",
            "address": {
                "city": "Redmond"
            },
            "company": "Microsoft",
            "number": 3}
        created_container.create_item(item)

        # Define patch operations
        operations = [
            {"op": "add", "path": "/color", "value": "yellow"},
            {"op": "remove", "path": "/prop"},
            {"op": "replace", "path": "/company", "value": "CosmosDB"},
            {"op": "set", "path": "/address/new_city", "value": "Atlanta"},
            {"op": "incr", "path": "/number", "value": 7},
            {"op": "move", "from": "/color", "path": "/favorite_color"}
        ]

        # Run patch operations with wrong filter
        num_false = item.get("number") + 1
        filter_predicate = "from root where root.number = " + str(num_false)
        with self.assertRaises(exceptions.CosmosHttpResponseError) as caught:
            created_container.patch_item(item="conditional_patch_item", partition_key=pkValue,
                                         patch_operations=operations, filter_predicate=filter_predicate)
        self.assertEqual(caught.exception.status_code, StatusCodes.PRECONDITION_FAILED)
        unchanged = created_container.read_item(item["id"], partition_key=pkValue)
        self.assertEqual({key: unchanged[key] for key in item}, item)
        self.assertNotIn("color", unchanged)
        self.assertNotIn("favorite_color", unchanged)

        # Run patch operations with correct filter
        filter_predicate = "from root where root.number = " + str(item.get("number"))
        patched_item = created_container.patch_item(item="conditional_patch_item", partition_key=pkValue,
                                                    patch_operations=operations, filter_predicate=filter_predicate)
        # Verify results from patch operations
        self.assertTrue(patched_item.get("color") is None)
        self.assertTrue(patched_item.get("prop") is None)
        self.assertEqual(patched_item.get("company"), "CosmosDB")
        self.assertEqual(patched_item.get("address").get("new_city"), "Atlanta")
        self.assertEqual(patched_item.get("number"), 10)
        self.assertEqual(patched_item.get("favorite_color"), "yellow")

        expected = {
            "id": item["id"], "pk": item["pk"], "company": "CosmosDB",
            "address": {"city": "Redmond", "new_city": "Atlanta"},
            "number": 10, "favorite_color": "yellow",
        }
        self.assertEqual({key: patched_item[key] for key in expected}, expected)
        stored = created_container.read_item(item["id"], partition_key=pkValue)
        self.assertEqual({key: stored[key] for key in expected}, expected)
        for result in (patched_item, stored):
            self.assertNotIn("color", result)
            self.assertNotIn("prop", result)

    # Temporarily commenting analytical storage tests until emulator support comes.
    # def test_create_container_with_analytical_store_off(self):
    #     # don't run test, for the time being, if running against the emulator
    #     if 'localhost' in self.host or '127.0.0.1' in self.host:
    #         return

    #     created_db = self.databaseForTest
    #     collection_id = 'test_create_container_with_analytical_store_off_' + str(uuid.uuid4())
    #     collection_indexing_policy = {'indexingMode': 'consistent'}
    #     created_recorder = RecordDiagnostics()
    #     created_collection = created_db.create_container(id=collection_id,
    #                                                      indexing_policy=collection_indexing_policy,
    #                                                      partition_key=PartitionKey(path="/pk", kind="Hash"),
    #                                                      response_hook=created_recorder)
    #     properties = created_collection.read()
    #     ttl_key = "analyticalStorageTtl"
    #     self.assertTrue(ttl_key not in properties or properties[ttl_key] == None)

    # def test_create_container_with_analytical_store_on(self):
    #     # don't run test, for the time being, if running against the emulator
    #     if 'localhost' in self.host or '127.0.0.1' in self.host:
    #         return

    #     created_db = self.databaseForTest
    #     collection_id = 'test_create_container_with_analytical_store_on_' + str(uuid.uuid4())
    #     collection_indexing_policy = {'indexingMode': 'consistent'}
    #     created_recorder = RecordDiagnostics()
    #     created_collection = created_db.create_container(id=collection_id,
    #                                                      analytical_storage_ttl=-1,
    #                                                      indexing_policy=collection_indexing_policy,
    #                                                      partition_key=PartitionKey(path="/pk", kind="Hash"),
    #                                                      response_hook=created_recorder)
    #     properties = created_collection.read()
    #     ttl_key = "analyticalStorageTtl"
    #     self.assertTrue(ttl_key in properties and properties[ttl_key] == -1)

    # def test_create_container_if_not_exists_with_analytical_store_on(self):
    #     # don't run test, for the time being, if running against the emulator
    #     if 'localhost' in self.host or '127.0.0.1' in self.host:
    #         return

    #     # first, try when we know the container doesn't exist.
    #     created_db = self.databaseForTest
    #     collection_id = 'test_create_container_if_not_exists_with_analytical_store_on_' + str(uuid.uuid4())
    #     collection_indexing_policy = {'indexingMode': 'consistent'}
    #     created_recorder = RecordDiagnostics()
    #     created_collection = created_db.create_container_if_not_exists(id=collection_id,
    #                                                                    analytical_storage_ttl=-1,
    #                                                                    indexing_policy=collection_indexing_policy,
    #                                                                    partition_key=PartitionKey(path="/pk", kind="Hash"),
    #                                                                    response_hook=created_recorder)
    #     properties = created_collection.read()
    #     ttl_key = "analyticalStorageTtl"
    #     self.assertTrue(ttl_key in properties and properties[ttl_key] == -1)

    #     # next, try when we know the container DOES exist. This way both code paths are tested.
    #     created_collection = created_db.create_container_if_not_exists(id=collection_id,
    #                                                                    analytical_storage_ttl=-1,
    #                                                                    indexing_policy=collection_indexing_policy,
    #                                                                    partition_key=PartitionKey(path="/pk", kind="Hash"),
    #                                                                    response_hook=created_recorder)
    #     properties = created_collection.read()
    #     ttl_key = "analyticalStorageTtl"
    #     self.assertTrue(ttl_key in properties and properties[ttl_key] == -1)

    def test_priority_level(self):
        # These test verify if headers for priority level are sent
        # Feature must be enabled at the account level
        # If feature is not enabled the test will still pass as we just verify the headers were sent
        created_container = self.databaseForTest.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

        item1 = {"id": "item1", "pk": "pk1"}
        item2 = {"id": "item2", "pk": "pk2"}
        self.OriginalExecuteFunction = _retry_utility.ExecuteFunction
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

    def _MockExecuteFunction(self, function, *args, **kwargs):
        if HttpHeaders.PartitionKey in args[4].headers:
            self.last_headers.append(args[4].headers[HttpHeaders.PartitionKey])
        return self.OriginalExecuteFunction(function, *args, **kwargs)


if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit as inst:
        if inst.args[0] is True:  # raised by sys.exit(True) when tests failed
            raise
