# -*- coding: utf-8 -*-
# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""End-to-end test.
"""
import asyncio
import logging
import os
import time
import unittest
import urllib.parse as urllib
import uuid
from asyncio import sleep
from unittest import mock
import pytest
from aiohttp import web
from azure.core import MatchConditions
from azure.core.exceptions import AzureError, ServiceResponseError, ServiceRequestError
from azure.core.pipeline.transport import AioHttpTransport, AioHttpTransportResponse

import azure.cosmos.documents as documents
import azure.cosmos.exceptions as exceptions
import test_config
from azure.cosmos.aio import CosmosClient, _retry_utility_async, DatabaseProxy
from azure.cosmos.http_constants import HttpHeaders, StatusCodes
from azure.cosmos.partition_key import PartitionKey


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


class TimeoutTransport(AioHttpTransport):

    def __init__(self, response, passthrough=False):
        self._response = response
        self.passthrough = passthrough
        super().__init__()

    async def send(self, request, **kwargs):
        if self.passthrough:
            return await super().send(request, **kwargs)

        await asyncio.sleep(5)
        if isinstance(self._response, Exception):
            # The SDK's retry logic wraps the original error in a ServiceRequestError.
            # We raise it this way to properly simulate a transport-level timeout.
            raise self._response

        # This part of the mock is for simulating successful responses, not used in this specific timeout test.
        raw_response = web.Response(status=self._response, reason="mock")
        raw_response.read = mock.AsyncMock(return_value=b"")
        response = AioHttpTransportResponse(request, raw_response)
        await response.load_body()
        return response

@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosLong
@pytest.mark.cosmosAADCircuitBreaker
class TestCRUDOperationsAsync(unittest.IsolatedAsyncioTestCase):
    """Python CRUD Tests.
    """
    client: CosmosClient = None
    key_client: CosmosClient = None
    configs = test_config.TestConfig
    host = configs.host
    masterKey = configs.masterKey
    connectionPolicy = configs.connectionPolicy
    last_headers = []
    database_for_test: DatabaseProxy = None
    key_database_for_test: DatabaseProxy = None

    async def __assert_http_failure_with_status(self, status_code, func, *args, **kwargs):
        """Assert HTTP failure with status.

        :Parameters:
            - `status_code`: int
            - `func`: function
        """
        try:
            await func(*args, **kwargs)
            self.fail('function should fail.')
        except exceptions.CosmosHttpResponseError as inst:
            assert inst.status_code == status_code

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

    async def asyncSetUp(self):
        use_multiple_write_locations = False
        if os.environ.get("AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER", "False") == "True":
            use_multiple_write_locations = True
        # Key-auth async client for control-plane operations (create/delete containers, sprocs)
        self.key_client, self.key_database_for_test, self.client, self.database_for_test = (
            test_config.TestConfig.create_test_clients_async(self.configs.TEST_DATABASE_ID, multiple_write_locations=use_multiple_write_locations))
        await self.key_client.__aenter__()
        await self.client.__aenter__()

    async def asyncTearDown(self):
        await self.client.close()
        await self.key_client.close()

    async def _create_container_for_test(self, container_id, partition_key, **kwargs):
        """Create container via key-auth setup client (control-plane), return data-plane proxy."""
        await self.key_database_for_test.create_container(id=container_id, partition_key=partition_key, **kwargs)
        return self.database_for_test.get_container_client(container_id)

    async def _delete_container_for_test(self, container_id_or_container):
        """Delete container via key-auth setup client (control-plane)."""
        cid = container_id_or_container if isinstance(container_id_or_container, str) else container_id_or_container.id
        await self.key_database_for_test.delete_container(cid)

    @_skip_under_aad
    async def test_partitioned_collection_execute_stored_procedure_async(self):
        key_collection = self.key_database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)
        created_collection = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)
        document_id = str(uuid.uuid4())

        sproc = {
            'id': 'storedProcedure' + str(uuid.uuid4()),
            'body': (
                    'function () {' +
                    '   var client = getContext().getCollection();' +
                    '   client.createDocument(client.getSelfLink(), { id: "' + document_id + '", pk : 2}, ' +
                    '   {}, function(err, docCreated, options) { ' +
                    '   if(err) throw new Error(\'Error while creating document: \' + err.message);' +
                    '   else {' +
                    '   getContext().getResponse().setBody(1);' +
                    '        }' +
                    '   });}')
        }

        created_sproc = await key_collection.scripts.create_stored_procedure(body=sproc)

        # Partiton Key value same as what is specified in the stored procedure body
        result = await created_collection.scripts.execute_stored_procedure(sproc=created_sproc['id'], partition_key=2)
        assert result == 1

        # Partiton Key value different than what is specified in the stored procedure body will cause a bad request(400) error
        await self.__assert_http_failure_with_status(
            StatusCodes.BAD_REQUEST,
            created_collection.scripts.execute_stored_procedure,
            created_sproc['id'])

    async def test_partitioned_collection_partition_key_value_types_async(self):

        created_db = self.database_for_test

        created_collection = created_db.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

        document_definition = {'id': 'document1' + str(uuid.uuid4()),
                               'pk': None,
                               'spam': 'eggs'}

        # create document with partitionKey set as None here
        await created_collection.create_item(body=document_definition)

        document_definition = {'id': 'document1' + str(uuid.uuid4()),
                               'spam': 'eggs'}

        # create document with partitionKey set as Undefined here
        await created_collection.create_item(body=document_definition)

        document_definition = {'id': 'document1' + str(uuid.uuid4()),
                               'pk': True,
                               'spam': 'eggs'}

        # create document with bool partitionKey
        await created_collection.create_item(body=document_definition)

        document_definition = {'id': 'document1' + str(uuid.uuid4()),
                               'pk': 'value',
                               'spam': 'eggs'}

        # create document with string partitionKey
        await created_collection.create_item(body=document_definition)

        document_definition = {'id': 'document1' + str(uuid.uuid4()),
                               'pk': 100,
                               'spam': 'eggs'}

        # create document with int partitionKey
        await created_collection.create_item(body=document_definition)

        document_definition = {'id': 'document1' + str(uuid.uuid4()),
                               'pk': 10.50,
                               'spam': 'eggs'}

        # create document with float partitionKey
        await created_collection.create_item(body=document_definition)

        document_definition = {'name': 'sample document',
                               'spam': 'eggs',
                               'pk': 'value'}

        # Should throw an error because automatic id generation is disabled always.
        await self.__assert_http_failure_with_status(
            StatusCodes.BAD_REQUEST,
            created_collection.create_item,
            document_definition
        )

    async def test_partitioned_collection_conflict_crud_and_query_async(self):

        created_collection = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

        conflict_definition = {'id': 'new conflict',
                               'resourceId': 'doc1',
                               'operationType': 'create',
                               'resourceType': 'document'
                               }

        # read conflict here will return resource not found(404) since there is no conflict here
        await self.__assert_http_failure_with_status(
            StatusCodes.NOT_FOUND,
            created_collection.get_conflict,
            conflict_definition['id'],
            conflict_definition['id']
        )

        # Read conflict feed doesn't require partitionKey to be specified as it's a cross partition thing
        conflict_list = [conflict async for conflict in created_collection.list_conflicts()]
        assert len(conflict_list) == 0

        # delete conflict here will return resource not found(404) since there is no conflict here
        await self.__assert_http_failure_with_status(
            StatusCodes.NOT_FOUND,
            created_collection.delete_conflict,
            conflict_definition['id'],
            conflict_definition['id']
        )

        conflict_list = [conflict async for conflict in created_collection.query_conflicts(
            query='SELECT * FROM root r WHERE r.resourceType=\'' + conflict_definition.get('resourceType') + '\'')]

        assert len(conflict_list) == 0

        # query conflicts by providing the partitionKey value
        options = {'partitionKey': conflict_definition.get('id')}
        conflict_list = [conflict async for conflict in created_collection.query_conflicts(
            query='SELECT * FROM root r WHERE r.resourceType=\'' + conflict_definition.get('resourceType') + '\'',
            # nosec
            partition_key=conflict_definition['id']
        )]

        assert len(conflict_list) == 0

    async def test_document_crud_async(self):

        # create collection
        created_collection = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)
        # read documents
        document_list = [document async for document in created_collection.read_all_items()]
        # create a document
        before_create_documents_count = len(document_list)

        # create a document with auto ID generation
        document_definition = {'name': 'sample document',
                               'spam': 'eggs',
                               'key': 'value',
                               'pk': 'pk'}

        created_document = await created_collection.create_item(body=document_definition,
                                                                enable_automatic_id_generation=True)
        assert created_document.get('name') == document_definition['name']

        document_definition = {'name': 'sample document',
                               'spam': 'eggs',
                               'key': 'value',
                               'pk': 'pk',
                               'id': str(uuid.uuid4())}

        created_document = await created_collection.create_item(body=document_definition)
        assert created_document.get('name') == document_definition['name']
        assert created_document.get('id') == document_definition['id']

        # duplicated documents are not allowed when 'id' is provided.
        duplicated_definition_with_id = document_definition.copy()
        await self.__assert_http_failure_with_status(StatusCodes.CONFLICT,
                                                     created_collection.create_item,
                                                     duplicated_definition_with_id)
        # read documents after creation
        document_list = [document async for document in created_collection.read_all_items()]
        assert len(document_list) == before_create_documents_count + 2
        # query documents
        document_list = [document async for document in created_collection.query_items(
            query='SELECT * FROM root r WHERE r.name=@name',
            parameters=[{'name': '@name', 'value': document_definition['name']}]
        )]
        assert document_list is not None
        document_list = [document async for document in created_collection.query_items(
            query='SELECT * FROM root r WHERE r.name=@name',
            parameters=[
                {'name': '@name', 'value': document_definition['name']}
            ],
            enable_scan_in_query=True
        )]
        assert document_list is not None
        # replace document.
        created_document['name'] = 'replaced document'
        created_document['spam'] = 'not eggs'
        old_etag = created_document['_etag']
        replaced_document = await created_collection.replace_item(
            item=created_document['id'],
            body=created_document
        )
        assert replaced_document['name'] == 'replaced document'
        assert replaced_document['spam'] == 'not eggs'
        assert created_document['id'] == replaced_document['id']

        # replace document based on condition
        replaced_document['name'] = 'replaced document based on condition'
        replaced_document['spam'] = 'new spam field'

        # should fail for stale etag
        await self.__assert_http_failure_with_status(
            StatusCodes.PRECONDITION_FAILED,
            created_collection.replace_item,
            replaced_document['id'],
            replaced_document,
            if_match=old_etag,
        )

        # should fail if only etag specified
        try:
            await created_collection.replace_item(
                etag=replaced_document['_etag'],
                item=replaced_document['id'],
                body=replaced_document)
            self.fail("should fail if only etag specified")
        except ValueError:
            pass

        # should fail if only match condition specified
        try:
            await created_collection.replace_item(
                match_condition=MatchConditions.IfNotModified,
                item=replaced_document['id'],
                body=replaced_document)
            self.fail("should fail if only match condition specified")
        except ValueError:
            pass

        try:
            await created_collection.replace_item(
                match_condition=MatchConditions.IfModified,
                item=replaced_document['id'],
                body=replaced_document)
            self.fail("should fail if only match condition specified")
        except ValueError:
            pass

        # should fail if invalid match condition specified
        try:
            await created_collection.replace_item(
                match_condition=replaced_document['_etag'],
                item=replaced_document['id'],
                body=replaced_document)
            self.fail("should fail if invalid match condition specified")
        except TypeError:
            pass

        # should pass for most recent etag
        replaced_document_conditional = await created_collection.replace_item(
            match_condition=MatchConditions.IfNotModified,
            etag=replaced_document['_etag'],
            item=replaced_document['id'],
            body=replaced_document
        )
        assert replaced_document_conditional['name'] == 'replaced document based on condition'
        assert replaced_document_conditional['spam'] == 'new spam field'
        assert replaced_document_conditional['id'] == replaced_document['id']

        # read document
        one_document_from_read = await created_collection.read_item(
            item=replaced_document['id'],
            partition_key=replaced_document['pk']
        )
        assert replaced_document['id'] == one_document_from_read['id']
        # delete document
        await created_collection.delete_item(
            item=replaced_document,
            partition_key=replaced_document['pk']
        )
        # read documents after deletion
        await self.__assert_http_failure_with_status(StatusCodes.NOT_FOUND,
                                                     created_collection.read_item,
                                                     replaced_document['id'],
                                                     replaced_document['id'])

    async def test_document_upsert_async(self):

        # create collection
        created_collection = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

        # read documents and check count
        document_list = [document async for document in created_collection.read_all_items()]
        before_create_documents_count = len(document_list)

        # create document definition
        document_definition = {'id': 'doc',
                               'name': 'sample document',
                               'spam': 'eggs',
                               'key': 'value',
                               'pk': 'pk'}

        # create document using Upsert API
        created_document = await created_collection.upsert_item(body=document_definition)

        # verify id property
        assert created_document['id'] == document_definition['id']

        # test error for non-string id
        with self.assertRaises(TypeError):
            document_definition['id'] = 7
            await created_collection.upsert_item(body=document_definition)

        # read documents after creation and verify updated count
        document_list = [document async for document in created_collection.read_all_items()]
        assert len(document_list) == before_create_documents_count + 1

        # update document
        created_document['name'] = 'replaced document'
        created_document['spam'] = 'not eggs'

        # should replace document since it already exists
        upserted_document = await created_collection.upsert_item(body=created_document)

        # verify the changed properties
        assert upserted_document['name'] == created_document['name']
        assert upserted_document['spam'] == created_document['spam']

        # verify id property
        assert upserted_document['id'] == created_document['id']

        # read documents after upsert and verify count doesn't increases again
        document_list = [document async for document in created_collection.read_all_items()]
        assert len(document_list) == before_create_documents_count + 1

        created_document['id'] = 'new id'

        # Upsert should create new document since the id is different
        new_document = await created_collection.upsert_item(body=created_document)

        # Test modified access conditions
        created_document['spam'] = 'more eggs'
        await created_collection.upsert_item(body=created_document)
        with self.assertRaises(exceptions.CosmosHttpResponseError):
            await created_collection.upsert_item(
                body=created_document,
                match_condition=MatchConditions.IfNotModified,
                etag=new_document['_etag'])

        # verify id property
        assert created_document['id'] == new_document['id']

        # read documents after upsert and verify count increases
        document_list = [document async for document in created_collection.read_all_items()]
        assert len(document_list) == before_create_documents_count + 2

        # delete documents
        await created_collection.delete_item(item=upserted_document, partition_key=upserted_document['pk'])
        await created_collection.delete_item(item=new_document, partition_key=new_document['pk'])

        # read documents after delete and verify count remains the same
        document_list = [document async for document in created_collection.read_all_items()]
        assert len(document_list) == before_create_documents_count

    async def test_geospatial_index_async(self):
        db = self.database_for_test
        # partial policy specified
        collection = await self._create_container_for_test(
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
        try:
            await collection.create_item(
                body={
                    'id': 'loc1',
                    'Location': {
                        'type': 'Point',
                        'coordinates': [20.0, 20.0]
                    }
                }
            )
            await collection.create_item(
                body={
                    'id': 'loc2',
                    'Location': {
                        'type': 'Point',
                        'coordinates': [100.0, 100.0]
                    }
                }
            )
            results = [result async for result in collection.query_items(
                query="SELECT * FROM root WHERE (ST_DISTANCE(root.Location, {type: 'Point', coordinates: [20.1, 20]}) < 20000)")]
            assert len(results) == 1
            assert 'loc1' == results[0]['id']
        finally:
            await self._delete_container_for_test(collection.id)

    async def test_authorization_async(self):
        with self.assertRaises(ValueError):
            CosmosClient(TestCRUDOperationsAsync.host, {})

    @_skip_under_aad
    async def test_script_logging_execute_stored_procedure_async(self):

        created_collection = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

        sproc = {
            'id': 'storedProcedure' + str(uuid.uuid4()),
            'body': (
                    'function () {' +
                    '   var mytext = \'x\';' +
                    '   var myval = 1;' +
                    '   try {' +
                    '       console.log(\'The value of %s is %s.\', mytext, myval);' +
                    '       getContext().getResponse().setBody(\'Success!\');' +
                    '   }' +
                    '   catch (err) {' +
                    '       getContext().getResponse().setBody(\'inline err: [\' + err.number + \'] \' + err);' +
                    '   }'
                    '}')
        }

        created_sproc = await created_collection.scripts.create_stored_procedure(body=sproc)

        result = await created_collection.scripts.execute_stored_procedure(
            sproc=created_sproc['id'],
            partition_key=1
        )

        assert result == 'Success!'
        assert HttpHeaders.ScriptLogResults not in created_collection.scripts.client_connection.last_response_headers

        result = await created_collection.scripts.execute_stored_procedure(
            sproc=created_sproc['id'],
            enable_script_logging=True,
            partition_key=1
        )

        assert result == 'Success!'
        assert urllib.quote('The value of x is 1.') == created_collection.scripts.client_connection. \
            last_response_headers.get(HttpHeaders.ScriptLogResults)

        result = await created_collection.scripts.execute_stored_procedure(
            sproc=created_sproc['id'],
            enable_script_logging=False,
            partition_key=1
        )

        assert result == 'Success!'
        assert HttpHeaders.ScriptLogResults not in created_collection.scripts.client_connection.last_response_headers


    async def test_database_account_connection_timeout_async(self):
        connection_policy = documents.ConnectionPolicy()
        connection_policy.DBAConnectionTimeout = 0.000000000001
        with self.assertRaises(ServiceRequestError):
            async with CosmosClient(self.host, self.masterKey, connection_policy=connection_policy):
                print('Async initialization')


    async def test_read_collection_only_once_async(self):
        # Add filter to the filtered diagnostics handler
        mock_handler = test_config.MockHandler()
        logger = logging.getLogger("azure.cosmos")
        logger.setLevel(logging.INFO)
        logger.addHandler(mock_handler)

        async with CosmosClient(self.host, self.masterKey) as client:
            database = client.get_database_client(self.configs.TEST_DATABASE_ID)
            container = database.get_container_client(self.configs.TEST_SINGLE_PARTITION_CONTAINER_ID)

            # Perform 10 concurrent upserts
            tasks = [
                container.upsert_item(body={'id': str(uuid.uuid4()), 'name': f'sample-{i}'})
                for i in range(10)
            ]
            await asyncio.gather(*tasks)
        assert sum("'x-ms-thinclient-proxy-resource-type': 'colls'" in response.message for response in mock_handler.messages) == 1

    # TODO: Skipping this test to debug later
    @unittest.skip
    async def test_client_connection_retry_configuration_async(self):
        total_time_for_two_retries = await self.initialize_client_with_connection_urllib_retry_config(2)
        total_time_for_four_retries = await self.initialize_client_with_connection_urllib_retry_config(4)
        assert total_time_for_four_retries > total_time_for_two_retries

    async def initialize_client_with_connection_urllib_retry_config(self, retries):
        async with CosmosClient(TestCRUDOperationsAsync.host, TestCRUDOperationsAsync.masterKey,
                                retry_total=retries, retry_connect=retries, retry_read=retries,
                                retry_backoff_max=0.3,
                                connection_timeout=.000000001) as client:
            databaseForTest = client.get_database_client(self.configs.TEST_DATABASE_ID)
            container = databaseForTest.get_container_client(self.configs.TEST_SINGLE_PARTITION_CONTAINER_ID)
            start_time = time.time()
            # client does a getDatabaseAccount on initialization, which will not time out because
            # there is a forced timeout for those calls

            try:
                item = {'id': str(uuid.uuid4()), 'name': 'sample'}
                await container.create_item(body=item)
                print('Async initialization')
                self.fail()
            except AzureError as e:
                self.assertIsInstance(e, ServiceResponseError)
                end_time = time.time()
                return end_time - start_time

    async def test_timeout_on_connection_error_async(self):
        # Connection Refused: This is an active rejection from the target machine's operating system. It receives your
        # connection request but immediately sends back a response indicating that no process is listening on that port.
        # This is a fast failure.
        # Connection Timeout Setting: This occurs when your connection request receives no response at all within a
        # specified period. The client gives up waiting. This typically happens if the target machine is down,
        # unreachable due to network configuration, or a firewall is silently dropping the packets.
        # so in the below test connection_timeout setting has no bearing on the test outcome
        client = None
        try:
            with self.assertRaises((exceptions.CosmosClientTimeoutError, ServiceRequestError)):
                client = CosmosClient(
                    "https://localhost:9999",
                    TestCRUDOperationsAsync.masterKey,
                    retry_total=10,
                    connection_timeout=100,
                    timeout=2)
                # The __aenter__ call is what triggers the connection attempt.
                await client.__aenter__()
        finally:
            if client:
                await client.close()

    async def test_timeout_on_read_operation_async(self):
        error_response = ServiceResponseError("Read timeout")
        # Initialize transport with passthrough enabled for client setup
        timeout_transport = TimeoutTransport(error_response, passthrough=True)

        async with CosmosClient(
                self.host, self.masterKey, transport=timeout_transport) as client:
            # Disable passthrough to test the timeout on the next call
            timeout_transport.passthrough = False
            with self.assertRaises(exceptions.CosmosClientTimeoutError):
                await client.create_database_if_not_exists("test", timeout=2)


    async def test_timeout_on_throttling_error_async(self):
        # Throttling(429): Keeps retrying -> Eventually times out -> CosmosClientTimeoutError
        status_response = 429  # Uses Cosmos custom retry
        timeout_transport = TimeoutTransport(status_response, passthrough=True)
        async with CosmosClient(
                self.host, self.masterKey, transport=timeout_transport
                ) as client:
            print('Async initialization')
            timeout_transport.passthrough = False
            with self.assertRaises(exceptions.CosmosClientTimeoutError):
                await client.create_database_if_not_exists("test", timeout=20)

            databases = client.list_databases(timeout=12)
            with self.assertRaises(exceptions.CosmosClientTimeoutError):
                databases = [database async for database in databases]

    async def test_inner_exceptions_on_timeout_async(self):
        # Throttling(429): Keeps retrying -> Eventually times out -> CosmosClientTimeoutError
        status_response = 429  # Uses Cosmos custom retry
        timeout_transport = TimeoutTransport(status_response, passthrough=True)
        async with CosmosClient(
                self.host, self.masterKey, transport=timeout_transport
                ) as client:
            print('Async initialization')
            timeout_transport.passthrough = False
            with self.assertRaises(exceptions.CosmosClientTimeoutError) as cm :
                await client.create_database_if_not_exists("test", timeout=20)

        # Verify the inner_exception is set and is a 429 error
        self.assertIsNotNone(cm.exception.inner_exception)
        self.assertIsInstance(cm.exception.inner_exception, exceptions.CosmosHttpResponseError)
        self.assertEqual(cm.exception.inner_exception.status_code, 429)

    async def test_timeout_for_read_items_async(self):
        """Test that timeout is properly maintained across multiple partition requests for a single logical operation
        read_items is different as the results of this api are not paginated and we present the complete result set
        """

        # Create a container with multiple partitions
        created_container = await self._create_container_for_test(
            container_id='multi_partition_container_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=11000
        )
        try:
            pk_ranges = [
                pk async for pk in
                created_container.client_connection._ReadPartitionKeyRanges(created_container.container_link)
            ]
            self.assertGreater(len(pk_ranges), 1, "Container should have multiple physical partitions.")

            # 2. Create items across different logical partitions
            items_to_read = []
            all_item_ids = set()
            for i in range(200):
                doc_id = f"item_{i}_{uuid.uuid4()}"
                pk = i % 10
                all_item_ids.add(doc_id)
                await created_container.create_item({'id': doc_id, 'pk': pk, 'data': i})
                items_to_read.append((doc_id, pk))

            # Create a custom transport that introduces delays
            class DelayedTransport(AioHttpTransport):
                def __init__(self, delay_per_request=3):
                    self.delay_per_request = delay_per_request
                    self.request_count = 0
                    super().__init__()

                async def send(self, request, **kwargs):
                    self.request_count += 1
                    # Delay each request to simulate slow network
                    await asyncio.sleep(self.delay_per_request)  # 3 second delay
                    return await super().send(request, **kwargs)

            # Verify timeout fails when cumulative time exceeds limit
            delayed_transport = DelayedTransport(delay_per_request=3)

            async with CosmosClient(
                    self.host, self.masterKey, transport=delayed_transport
            ) as client_with_delay:

                container_with_delay = client_with_delay.get_database_client(
                    self.database_for_test.id
                ).get_container_client(created_container.id)

                start_time = time.time()

                with self.assertRaises(exceptions.CosmosClientTimeoutError):
                    # This should timeout because multiple partition requests * 3s delay > 5s timeout
                    await container_with_delay.read_items(
                        items=items_to_read,
                        timeout=5  # 5 second total timeout
                    )

            elapsed_time = time.time() - start_time
            # Should fail close to 5 seconds (not wait for all requests). Upper bound
            # is loose to absorb the cold-cache /pkranges drain (a 200+ETag fetch followed
            # by a 304 confirmation, see PR #47245) which adds one extra round trip --
            # under DelayedTransport(3s) that is +3s on top of the data-plane delay.
            self.assertLess(elapsed_time, 12)  # Allow overhead for the cold-cache drain round trips
            self.assertGreater(elapsed_time, 5)  # Should wait at least close to timeout
        finally:
            await self._delete_container_for_test(created_container.id)







    async def test_timeout_for_point_operation_async(self):
        """Test that point operations respect client timeout"""

        # Create a container for testing
        created_container = await self._create_container_for_test(
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
            await created_container.create_item(test_item)

            # Long timeout should succeed
            result = await created_container.read_item(
                item='test_item_1',
                partition_key='partition1',
                timeout=1.0  # 1 second timeout
            )
            self.assertEqual(result['id'], 'test_item_1')
        finally:
            await self._delete_container_for_test(created_container.id)

    async def test_timeout_for_paged_request_async(self):
        """Test that timeout applies to each individual page request, not cumulatively"""

        # Create container and add items
        created_container = await self._create_container_for_test(
            container_id='paged_timeout_container_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk")
        )

        # Create enough items to ensure multiple pages
        for i in range(100):
            await created_container.create_item({'id': f'item_{i}', 'pk': i % 10, 'data': 'x' * 1000})

        # Create a transport that delays each request
        class DelayedTransport(AioHttpTransport):
            def __init__(self, delay_seconds=1):
                self.delay_seconds = delay_seconds
                super().__init__()

            async def send(self, request, **kwargs):
                await asyncio.sleep(self.delay_seconds)
                return await super().send(request, **kwargs)

        # Test with delayed transport - reduced delay to 1 second for stability
        delayed_transport = DelayedTransport(delay_seconds=1)
        async with CosmosClient(
                self.host, self.masterKey, transport=delayed_transport
        ) as client_with_delay:
            container_with_delay = client_with_delay.get_database_client(
                self.database_for_test.id
            ).get_container_client(created_container.id)

            # Test 1: Timeout should apply per page
            item_pages = container_with_delay.query_items(
                query="SELECT * FROM c",
                #enable_cross_partition_query=True,
                max_item_count=10,  # Small page size
                timeout=3  # 3s timeout > 1s delay, should succeed
            ).by_page()

            # First page should succeed with 3s timeout (1s delay < 3s timeout)
            first_page = [item async for item in await item_pages.__anext__()]
            self.assertGreater(len(first_page), 0)

            # Second page should also succeed (timeout resets per page)
            second_page = [item async for item in await item_pages.__anext__()]
            self.assertGreater(len(second_page), 0)

            # Test 2: Timeout too short should fail
            item_pages_short_timeout = container_with_delay.query_items(
                query="SELECT * FROM c",
                #enable_cross_partition_query=True,
                max_item_count=10,
                timeout=0.5  # 0.5s timeout < 1s delay, should fail
            ).by_page()

            with self.assertRaises(exceptions.CosmosClientTimeoutError):
                first_page = [item async for item in await item_pages_short_timeout.__anext__()]

        # Cleanup
        await self.key_database_for_test.delete_container(created_container.id)

    # TODO: for read timeouts azure-core returns a ServiceResponseError, needs to be fixed in azure-core and then this test can be enabled

    # TODO: for read timeouts azure-core returns a ServiceResponseError, needs to be fixed in azure-core and then this test can be enabled



    async def test_query_iterable_functionality_async(self):

        collection = await self._create_container_for_test("query-iterable-container-async",
                                                            partition_key=PartitionKey("/pk"))
        doc1 = await collection.upsert_item(body={'id': 'doc1', 'prop1': 'value1'})
        doc2 = await collection.upsert_item(body={'id': 'doc2', 'prop1': 'value2'})
        doc3 = await collection.upsert_item(body={'id': 'doc3', 'prop1': 'value3'})
        await asyncio.sleep(1)
        resources = {
            'coll': collection,
            'doc1': doc1,
            'doc2': doc2,
            'doc3': doc3
        }
        # Validate QueryIterable by converting it to a list.
        results = resources['coll'].read_all_items(max_item_count=2)
        docs = [doc async for doc in results]
        assert 3 == len(docs)
        assert resources['doc1']['id'] == docs[0]['id']
        assert resources['doc2']['id'] == docs[1]['id']
        assert resources['doc3']['id'] == docs[2]['id']

        # Validate QueryIterable iterator with 'for'.
        results = resources['coll'].read_all_items(max_item_count=2)
        counter = 0
        # test QueryIterable with 'for'.
        async for doc in results:
            counter += 1
            if counter == 1:
                assert resources['doc1']['id'] == doc['id']
            elif counter == 2:
                assert resources['doc2']['id'] == doc['id']
            elif counter == 3:
                assert resources['doc3']['id'] == doc['id']
        assert counter == 3

        # Get query results page by page.
        results = resources['coll'].read_all_items(max_item_count=2)

        page_iter = results.by_page()
        first_block = [page async for page in await page_iter.__anext__()]
        assert 2 == len(first_block)
        assert resources['doc1']['id'] == first_block[0]['id']
        assert resources['doc2']['id'] == first_block[1]['id']
        assert 1 == len([page async for page in await page_iter.__anext__()])
        with self.assertRaises(StopAsyncIteration):
            await page_iter.__anext__()

        await self._delete_container_for_test(collection.id)

    @_skip_under_aad
    async def test_stored_procedure_functionality_async(self):

        # create collection
        collection = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

        sproc1 = {
            'id': 'storedProcedure1' + str(uuid.uuid4()),
            'body': (
                    'function () {' +
                    '  for (var i = 0; i < 1000; i++) {' +
                    '    var item = getContext().getResponse().getBody();' +
                    '    if (i > 0 && item != i - 1) throw \'body mismatch\';' +
                    '    getContext().getResponse().setBody(i);' +
                    '  }' +
                    '}')
        }

        retrieved_sproc = await collection.scripts.create_stored_procedure(body=sproc1)
        result = await collection.scripts.execute_stored_procedure(
            sproc=retrieved_sproc['id'],
            partition_key=1
        )
        assert result == 999
        sproc2 = {
            'id': 'storedProcedure2' + str(uuid.uuid4()),
            'body': (
                    'function () {' +
                    '  for (var i = 0; i < 10; i++) {' +
                    '    getContext().getResponse().appendValue(\'Body\', i);' +
                    '  }' +
                    '}')
        }
        retrieved_sproc2 = await collection.scripts.create_stored_procedure(body=sproc2)
        result = await collection.scripts.execute_stored_procedure(
            sproc=retrieved_sproc2['id'],
            partition_key=1
        )
        assert int(result) == 123456789
        sproc3 = {
            'id': 'storedProcedure3' + str(uuid.uuid4()),
            'body': (
                    'function (input) {' +
                    '  getContext().getResponse().setBody(' +
                    '      \'a\' + input.temp);' +
                    '}')
        }
        retrieved_sproc3 = await collection.scripts.create_stored_procedure(body=sproc3)
        result = await collection.scripts.execute_stored_procedure(
            sproc=retrieved_sproc3['id'],
            parameters={'temp': 'so'},
            partition_key=1
        )
        assert result == 'aso'

    async def test_get_resource_with_dictionary_and_object_async(self):

        created_db = self.database_for_test
        key_db = self.key_database_for_test

        # read database with id
        read_db = self.client.get_database_client(created_db.id)
        assert read_db.id == created_db.id

        # read database with instance
        read_db = self.client.get_database_client(created_db)
        assert read_db.id == created_db.id

        # read database with properties
        read_db = self.client.get_database_client(await created_db.read())
        assert read_db.id == created_db.id

        created_container = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)
        key_container = self.key_database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

        # read container with id
        read_container = created_db.get_container_client(created_container.id)
        assert read_container.id == created_container.id

        # read container with instance
        read_container = created_db.get_container_client(created_container)
        assert read_container.id == created_container.id

        # read container with properties
        created_properties = await created_container.read()
        read_container = created_db.get_container_client(created_properties)
        assert read_container.id == created_container.id

        created_item = await created_container.create_item({'id': '1' + str(uuid.uuid4()), 'pk': 'pk'})
        await sleep(5)

        # read item with id
        read_item = await created_container.read_item(item=created_item['id'], partition_key=created_item['pk'])
        assert read_item['id'] == created_item['id']

        # read item with properties
        read_item = await created_container.read_item(item=created_item, partition_key=created_item['pk'])
        assert read_item['id'] == created_item['id']

        # Sproc/trigger/UDF operations are control-plane; route through setup container.
        created_sproc = await key_container.scripts.create_stored_procedure({
            'id': 'storedProcedure' + str(uuid.uuid4()),
            'body': 'function () { }'
        })

        # read sproc with id
        read_sproc = await key_container.scripts.get_stored_procedure(created_sproc['id'])
        assert read_sproc['id'] == created_sproc['id']

        # read sproc with properties
        read_sproc = await key_container.scripts.get_stored_procedure(created_sproc)
        assert read_sproc['id'] == created_sproc['id']

        created_trigger = await key_container.scripts.create_trigger({
            'id': 'sample trigger' + str(uuid.uuid4()),
            'serverScript': 'function() {var x = 10;}',
            'triggerType': documents.TriggerType.Pre,
            'triggerOperation': documents.TriggerOperation.All
        })

        # read trigger with id
        read_trigger = await key_container.scripts.get_trigger(created_trigger['id'])
        assert read_trigger['id'] == created_trigger['id']

        # read trigger with properties
        read_trigger = await key_container.scripts.get_trigger(created_trigger)
        assert read_trigger['id'] == created_trigger['id']

        created_udf = await key_container.scripts.create_user_defined_function({
            'id': 'sample udf' + str(uuid.uuid4()),
            'body': 'function() {var x = 10;}'
        })

        # read udf with id
        read_udf = await key_container.scripts.get_user_defined_function(created_udf['id'])
        assert created_udf['id'] == read_udf['id']

        # read udf with properties
        read_udf = await key_container.scripts.get_user_defined_function(created_udf)
        assert created_udf['id'] == read_udf['id']


    async def test_delete_all_items_by_partition_key_async(self):
        # create container via setup client (control-plane)
        created_collection = await self._create_container_for_test(
            container_id='test_delete_all_items_by_partition_key_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path='/pk', kind='Hash')
        )
        # Create two partition keys
        partition_key1 = "{}-{}".format("Partition Key 1", str(uuid.uuid4()))
        partition_key2 = "{}-{}".format("Partition Key 2", str(uuid.uuid4()))

        # add items for partition key 1
        for i in range(1, 3):
            await created_collection.upsert_item(
                dict(id="item{}".format(i), pk=partition_key1)
            )

        # add items for partition key 2
        pk2_item = await created_collection.upsert_item(dict(id="item{}".format(3), pk=partition_key2))

        try:
            # delete all items for partition key 1
            await created_collection.delete_all_items_by_partition_key(partition_key1)
        except exceptions.CosmosHttpResponseError as e:
            error_text = " ".join(
                message for message in (getattr(e, "http_error_message", None), str(e))
                if message
            ).lower()
            if e.status_code == 400 and "partition key delete feature is disabled" in error_text:
                await self._delete_container_for_test(created_collection)
                pytest.skip("delete_all_items_by_partition_key is not enabled for this account")
            raise

        # check that only items from partition key 1 have been deleted
        items = [item async for item in created_collection.read_all_items()]

        # items should only have 1 item, and it should equal pk2_item
        self.assertDictEqual(pk2_item, items[0])

        # attempting to delete a non-existent partition key or passing none should not delete
        # anything and leave things unchanged
        await created_collection.delete_all_items_by_partition_key(None)

        # check that no changes were made by checking if the only item is still there
        items = [item async for item in created_collection.read_all_items()]

        # items should only have 1 item, and it should equal pk2_item
        self.assertDictEqual(pk2_item, items[0])

        await self._delete_container_for_test(created_collection)

    async def test_patch_operations_async(self):

        created_container = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

        # Create item to patch
        item_id = "patch_item_" + str(uuid.uuid4())
        item = {
            "id": item_id,
            "pk": "patch_item_pk",
            "prop": "prop1",
            "address": {
                "city": "Redmond"
            },
            "company": "Microsoft",
            "number": 3}
        await created_container.create_item(item)
        # Define and run patch operations
        operations = [
            {"op": "add", "path": "/color", "value": "yellow"},
            {"op": "remove", "path": "/prop"},
            {"op": "replace", "path": "/company", "value": "CosmosDB"},
            {"op": "set", "path": "/address/new_city", "value": "Atlanta"},
            {"op": "incr", "path": "/number", "value": 7},
            {"op": "move", "from": "/color", "path": "/favorite_color"}
        ]
        patched_item = await created_container.patch_item(item=item_id, partition_key="patch_item_pk",
                                                          patch_operations=operations)
        # Verify results from patch operations
        assert "color" not in patched_item
        assert "prop" not in patched_item
        assert patched_item.get("company") == "CosmosDB"
        assert patched_item.get("address").get("new_city") == "Atlanta"
        assert patched_item.get("number") == 10
        assert patched_item.get("favorite_color") == "yellow"

        stored_item = await created_container.read_item(item_id, partition_key="patch_item_pk")
        assert "color" not in stored_item
        assert "prop" not in stored_item
        assert stored_item.get("favorite_color") == "yellow"

        # Negative test - attempt to replace non-existent field
        operations = [{"op": "replace", "path": "/wrong_field", "value": "wrong_value"}]
        with self.assertRaises(exceptions.CosmosHttpResponseError) as caught:
            await created_container.patch_item(item=item_id, partition_key="patch_item_pk",
                                               patch_operations=operations)
        assert caught.exception.status_code == StatusCodes.BAD_REQUEST

        # Negative test - attempt to remove non-existent field
        operations = [{"op": "remove", "path": "/wrong_field"}]
        with self.assertRaises(exceptions.CosmosHttpResponseError) as caught:
            await created_container.patch_item(item=item_id, partition_key="patch_item_pk",
                                               patch_operations=operations)
        assert caught.exception.status_code == StatusCodes.BAD_REQUEST

        # Negative test - attempt to increment non-number field
        operations = [{"op": "incr", "path": "/company", "value": 3}]
        with self.assertRaises(exceptions.CosmosHttpResponseError) as caught:
            await created_container.patch_item(item=item_id, partition_key="patch_item_pk",
                                               patch_operations=operations)
        assert caught.exception.status_code == StatusCodes.BAD_REQUEST

        # Negative test - attempt to move from non-existent field
        operations = [{"op": "move", "from": "/wrong_field", "path": "/other_field"}]
        with self.assertRaises(exceptions.CosmosHttpResponseError) as caught:
            await created_container.patch_item(item=item_id, partition_key="patch_item_pk",
                                               patch_operations=operations)
        assert caught.exception.status_code == StatusCodes.BAD_REQUEST

    async def test_conditional_patching_async(self):

        created_container = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)
        # Create item to patch
        item_id = "conditional_patch_item_" + str(uuid.uuid4())
        item = {
            "id": item_id,
            "pk": "patch_item_pk",
            "prop": "prop1",
            "address": {
                "city": "Redmond"
            },
            "company": "Microsoft",
            "number": 3}
        await created_container.create_item(item)

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
            await created_container.patch_item(item=item_id, partition_key="patch_item_pk",
                                               patch_operations=operations, filter_predicate=filter_predicate)
        assert caught.exception.status_code == StatusCodes.PRECONDITION_FAILED
        unchanged = await created_container.read_item(item_id, partition_key="patch_item_pk")
        assert {key: unchanged[key] for key in item} == item
        assert "color" not in unchanged
        assert "favorite_color" not in unchanged

        # Run patch operations with correct filter
        filter_predicate = "from root where root.number = " + str(item.get("number"))
        patched_item = await created_container.patch_item(item=item_id, partition_key="patch_item_pk",
                                                          patch_operations=operations,
                                                          filter_predicate=filter_predicate)
        # Verify results from patch operations
        assert patched_item.get("color") is None
        assert patched_item.get("prop") is None
        assert patched_item.get("company") == "CosmosDB"
        assert patched_item.get("address").get("new_city") == "Atlanta"
        assert patched_item.get("number") == 10
        assert patched_item.get("favorite_color") == "yellow"

        expected = {
            "id": item["id"], "pk": item["pk"], "company": "CosmosDB",
            "address": {"city": "Redmond", "new_city": "Atlanta"},
            "number": 10, "favorite_color": "yellow",
        }
        assert {key: patched_item[key] for key in expected} == expected
        stored = await created_container.read_item(item_id, partition_key="patch_item_pk")
        assert {key: stored[key] for key in expected} == expected
        for result in (patched_item, stored):
            assert "color" not in result
            assert "prop" not in result

    # Temporarily commenting analytical storage tests until emulator support comes.
    #
    # async def test_create_container_with_analytical_store_off(self):
    #     # don't run test, for the time being, if running against the emulator
    #     if 'localhost' in self.host or '127.0.0.1' in self.host:
    #         return

    #     created_db = self.database_for_test
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

    #     created_db = self.database_for_test
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
    #     created_db = self.database_for_test
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

    async def test_priority_level_async(self):
        # These test verify if headers for priority level are sent
        # Feature must be enabled at the account level
        # If feature is not enabled the test will still pass as we just verify the headers were sent

        created_container = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)
        item1 = {"id": "item1", "pk": "pk1"}
        item2 = {"id": "item2", "pk": "pk2"}
        self.OriginalExecuteFunction = _retry_utility_async.ExecuteFunctionAsync
        priority_headers = []

        # mock execute function to check if priority level set in headers

        async def priority_mock_execute_function(function, *args, **kwargs):
            if args:
                priority_headers.append(args[4].headers[HttpHeaders.PriorityLevel]
                                              if HttpHeaders.PriorityLevel in args[4].headers else '')
            return await self.OriginalExecuteFunction(function, *args, **kwargs)

        _retry_utility_async.ExecuteFunctionAsync = priority_mock_execute_function
        # upsert item with high priority
        await created_container.upsert_item(body=item1, priority="High")
        # check if the priority level was passed
        assert priority_headers[-1] == "High"
        # upsert item with low priority
        await created_container.upsert_item(body=item2, priority="Low")
        # check that headers passed low priority
        assert priority_headers[-1] == "Low"
        # Repeat for read operations
        item1_read = await created_container.read_item("item1", "pk1", priority="High")
        assert priority_headers[-1] == "High"
        item2_read = await created_container.read_item("item2", "pk2", priority="Low")
        assert priority_headers[-1] == "Low"
        # repeat for query
        query = [doc async for doc in created_container.query_items("Select * from c",
                                                                    partition_key="pk1", priority="High")]

        assert priority_headers[-1] == "High"

        # Negative Test: Verify that if we send a value other than High or Low that it will not set the header value
        # and result in bad request
        try:
            item2_read = await created_container.read_item("item2", "pk2", priority="Medium")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == StatusCodes.BAD_REQUEST
        _retry_utility_async.ExecuteFunctionAsync = self.OriginalExecuteFunction

    async def _mock_execute_function(self, function, *args, **kwargs):
        if HttpHeaders.PartitionKey in args[4].headers:
            self.last_headers.append(args[4].headers[HttpHeaders.PartitionKey])
        return await self.OriginalExecuteFunction(function, *args, **kwargs)


if __name__ == '__main__':
    unittest.main()
