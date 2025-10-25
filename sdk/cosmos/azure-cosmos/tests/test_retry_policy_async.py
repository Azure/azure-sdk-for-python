# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import asyncio
import os
import unittest
import uuid

import pytest

from azure.cosmos import documents

import azure.cosmos._retry_options as retry_options
import azure.cosmos.exceptions as exceptions
from azure.core.exceptions import ServiceRequestError
import test_config
from azure.cosmos.partition_key import PartitionKey
from azure.cosmos.http_constants import HttpHeaders, StatusCodes
from azure.cosmos.aio import CosmosClient
from azure.cosmos.aio import DatabaseProxy, ContainerProxy
import azure.cosmos.aio._retry_utility_async as _retry_utility
from azure.cosmos._retry_options import RetryOptions
from _fault_injection_transport_async import FaultInjectionTransportAsync
from azure.cosmos.http_constants import ResourceType
from azure.cosmos._constants import _Constants
from azure.cosmos._health_check_retry_policy import HealthCheckRetryPolicy

class ConnectionMode:
    """Represents the connection mode to be used by the client."""
    Gateway: int = 0
    """Use the Azure Cosmos gateway to route all requests. The gateway proxies
    requests to the right data partition.
    """

class ConnectionPolicy:
    #Represents the Connection policy associated with a CosmosClientConnection.
    __defaultRequestTimeout: int = 5  # seconds
    __defaultDBAConnectionTimeout: int = 3  # seconds
    __defaultReadTimeout: int = 65  # seconds
    __defaultDBAReadTimeout: int = 3 # seconds
    __defaultMaxBackoff: int = 1 # seconds

    def __init__(self) -> None:
        self.RequestTimeout: int = self.__defaultRequestTimeout
        self.DBAConnectionTimeout: int = self.__defaultDBAConnectionTimeout
        self.ReadTimeout: int = self.__defaultReadTimeout
        self.DBAReadTimeout: int = self.__defaultDBAReadTimeout
        self.MaxBackoff: int = self.__defaultMaxBackoff
        self.ConnectionMode: int = ConnectionMode.Gateway
        self.SSLConfiguration: Optional[SSLConfiguration] = None
        self.ProxyConfiguration: Optional[ProxyConfiguration] = None
        self.EnableEndpointDiscovery: bool = True
        self.PreferredLocations: List[str] = []
        self.ExcludedLocations = []
        self.RetryOptions: RetryOptions = RetryOptions()
        self.DisableSSLVerification: bool = False
        self.UseMultipleWriteLocations: bool = False
        self.ConnectionRetryConfiguration: Optional["ConnectionRetryPolicy"] = None
        self.ResponsePayloadOnWriteDisabled: bool = False

async def setup_method_with_custom_transport(
        custom_transport,
        **kwargs):
    connection_policy = ConnectionPolicy()
    connection_retry_policy = test_config.MockConnectionRetryPolicyAsync(resource_type="docs")
    connection_policy.ConnectionRetryConfiguration = connection_retry_policy
    client = CosmosClient(test_config.TestConfig.host, test_config.TestConfig.masterKey,
                          transport=custom_transport, connection_policy=connection_policy, **kwargs)
    db = client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)
    container = db.get_container_client(test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID)
    return {"client": client, "db": db, "col": container, "retry_policy": connection_retry_policy}

@pytest.mark.cosmosEmulator
class TestRetryPolicyAsync(unittest.IsolatedAsyncioTestCase):
    created_database: DatabaseProxy = None
    created_collection: ContainerProxy = None
    client: CosmosClient = None
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    connectionPolicy = ConnectionPolicy()
    counter = 0
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_SINGLE_PARTITION_ID = "test-retry-policy-container-" + str(uuid.uuid4())
    retry_after_in_milliseconds = 1000

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
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

    async def test_resource_throttle_retry_policy_default_retry_after_async(self):
        connection_policy = TestRetryPolicyAsync.connectionPolicy
        connection_policy.RetryOptions = retry_options.RetryOptions(5)
        async with CosmosClient(self.host, self.masterKey, connection_policy=connection_policy) as client:
            database = client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)
            container = database.get_container_client(test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID)

            self.original_execute_function = _retry_utility.ExecuteFunctionAsync
            try:
                _retry_utility.ExecuteFunctionAsync = self._MockExecuteFunction

                document_definition = {'id': str(uuid.uuid4()),
                                       'pk': 'pk',
                                       'name': 'sample document',
                                       'key': 'value'}

                try:
                    await container.create_item(body=document_definition)
                except exceptions.CosmosHttpResponseError as e:
                    self.assertEqual(e.status_code, StatusCodes.TOO_MANY_REQUESTS)
                    self.assertEqual(connection_policy.RetryOptions.MaxRetryAttemptCount,
                                     container.client_connection.last_response_headers[
                                         HttpHeaders.ThrottleRetryCount])
                    self.assertGreaterEqual(container.client_connection.last_response_headers[
                                                HttpHeaders.ThrottleRetryWaitTimeInMs],
                                            connection_policy.RetryOptions.MaxRetryAttemptCount *
                                            self.retry_after_in_milliseconds)
            finally:
                _retry_utility.ExecuteFunctionAsync = self.original_execute_function

    async def test_resource_throttle_retry_policy_fixed_retry_after_async(self):
        connection_policy = TestRetryPolicyAsync.connectionPolicy
        connection_policy.RetryOptions = retry_options.RetryOptions(5, 2000)
        async with CosmosClient(self.host, self.masterKey, connection_policy=connection_policy) as client:
            database = client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)
            container = database.get_container_client(test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID)
            self.original_execute_function = _retry_utility.ExecuteFunctionAsync
            try:
                _retry_utility.ExecuteFunctionAsync = self._MockExecuteFunction

                document_definition = {'id': str(uuid.uuid4()),
                                       'pk': 'pk',
                                       'name': 'sample document',
                                       'key': 'value'}

                try:
                    await container.create_item(body=document_definition)
                except exceptions.CosmosHttpResponseError as e:
                    self.assertEqual(e.status_code, StatusCodes.TOO_MANY_REQUESTS)
                    self.assertEqual(connection_policy.RetryOptions.MaxRetryAttemptCount,
                                     container.client_connection.last_response_headers[
                                         HttpHeaders.ThrottleRetryCount])
                    self.assertGreaterEqual(container.client_connection.last_response_headers[
                                                HttpHeaders.ThrottleRetryWaitTimeInMs],
                                            connection_policy.RetryOptions.MaxRetryAttemptCount * connection_policy.RetryOptions.FixedRetryIntervalInMilliseconds)

            finally:
                _retry_utility.ExecuteFunctionAsync = self.original_execute_function

    async def test_resource_throttle_retry_policy_max_wait_time_async(self):
        connection_policy = TestRetryPolicyAsync.connectionPolicy
        connection_policy.RetryOptions = retry_options.RetryOptions(5, 2000, 3)
        async with CosmosClient(self.host, self.masterKey, connection_policy=connection_policy) as client:
            database = client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)
            container = database.get_container_client(test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID)
            self.original_execute_function = _retry_utility.ExecuteFunctionAsync
            try:
                _retry_utility.ExecuteFunctionAsync = self._MockExecuteFunction

                document_definition = {'id': str(uuid.uuid4()),
                                       'pk': 'pk',
                                       'name': 'sample document',
                                       'key': 'value'}

                try:
                    await container.create_item(body=document_definition)
                except exceptions.CosmosHttpResponseError as e:
                    self.assertEqual(e.status_code, StatusCodes.TOO_MANY_REQUESTS)
                    self.assertGreaterEqual(container.client_connection.last_response_headers[
                                                HttpHeaders.ThrottleRetryWaitTimeInMs],
                                            connection_policy.RetryOptions.MaxWaitTimeInSeconds * 1000)
            finally:
                _retry_utility.ExecuteFunctionAsync = self.original_execute_function

    async def test_resource_throttle_retry_policy_query_async(self):
        connection_policy = TestRetryPolicyAsync.connectionPolicy
        connection_policy.RetryOptions = retry_options.RetryOptions(5)

        document_definition = {'id': str(uuid.uuid4()),
                               'pk': 'pk',
                               'name': 'sample document',
                               'key': 'value'}
        async with CosmosClient(self.host, self.masterKey, connection_policy=connection_policy) as client:
            database = client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)
            container = database.get_container_client(test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID)
            await container.create_item(body=document_definition)

            self.original_execute_function = _retry_utility.ExecuteFunctionAsync
            try:
                _retry_utility.ExecuteFunctionAsync = self._MockExecuteFunction

                try:
                    query_results = container.query_items(
                        {
                            'query': 'SELECT * FROM root r WHERE r.id=@id',
                            'parameters': [
                                {'name': '@id', 'value': document_definition['id']}
                            ]
                        })
                    async for item in query_results:
                        pass
                except exceptions.CosmosHttpResponseError as e:
                    self.assertEqual(e.status_code, StatusCodes.TOO_MANY_REQUESTS)
                    self.assertEqual(connection_policy.RetryOptions.MaxRetryAttemptCount,
                                     container.client_connection.last_response_headers[
                                         HttpHeaders.ThrottleRetryCount])
                    self.assertGreaterEqual(container.client_connection.last_response_headers[
                                                HttpHeaders.ThrottleRetryWaitTimeInMs],
                                            connection_policy.RetryOptions.MaxRetryAttemptCount * self.retry_after_in_milliseconds)
            finally:
                _retry_utility.ExecuteFunctionAsync = self.original_execute_function

    # TODO: Need to validate the query retries
    @pytest.mark.skip
    async def test_default_retry_policy_for_query_async(self):
        document_definition_1 = {'id': str(uuid.uuid4()),
                                 'pk': 'pk',
                                 'name': 'sample document',
                                 'key': 'value'}
        document_definition_2 = {'id': str(uuid.uuid4()),
                                 'pk': 'pk',
                                 'name': 'sample document',
                                 'key': 'value'}

        self.created_collection.create_item(body=document_definition_1)
        self.created_collection.create_item(body=document_definition_2)
        self.original_execute_function = _retry_utility.ExecuteFunctionAsync
        try:
            mf = self.MockExecuteFunctionConnectionReset(self.original_execute_function)
            _retry_utility.ExecuteFunctionAsync = mf

            docs = await self.created_collection.query_items(query="Select * from c order by c._ts", max_item_count=1,
                                                             enable_cross_partition_query=True)

            result_docs = list(docs)
            self.assertEqual(result_docs[0]['id'], document_definition_1['id'])
            self.assertEqual(result_docs[1]['id'], document_definition_2['id'])

            self.assertEqual(mf.counter, 27)
        finally:
            _retry_utility.ExecuteFunctionAsync = self.original_execute_function

    async def test_default_retry_policy_for_create_async(self):
        document_definition = {'id': str(uuid.uuid4()),
                               'pk': 'pk',
                               'name': 'sample document',
                               'key': 'value'}
        async with CosmosClient(self.host, self.masterKey) as client:
            database = client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)
            container = await database.create_container_if_not_exists(test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID,
                                                                      partition_key=PartitionKey("/pk"))
            try:
                self.original_execute_function = _retry_utility.ExecuteFunctionAsync
                mf = self.MockExecuteFunctionConnectionReset(self.original_execute_function)
                _retry_utility.ExecuteFunctionAsync = mf

                created_document = {}
                try:
                    created_document = await container.create_item(body=document_definition)
                except exceptions.CosmosHttpResponseError as err:
                    self.assertEqual(err.status_code, 10054)

                self.assertDictEqual(created_document, {})

                self.assertEqual(mf.counter, 1)
            finally:
                _retry_utility.ExecuteFunctionAsync = self.original_execute_function

    async def test_timeout_failover_retry_policy_for_read_async(self):
        document_definition = {'id': 'failoverDoc',
                               'pk': 'pk',
                               'name': 'sample document',
                               'key': 'value'}
        async with CosmosClient(self.host, self.masterKey) as client:
            database = client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)
            container = database.get_container_client(test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID)
            created_document = await container.create_item(body=document_definition)
            self.original_execute_function = _retry_utility.ExecuteFunctionAsync
            try:
                mf = self.MockExecuteFunctionTimeout(self.original_execute_function)
                _retry_utility.ExecuteFunctionAsync = mf
                try:
                    await container.read_item(item=created_document['id'], partition_key=created_document['pk'])
                except exceptions.CosmosHttpResponseError as err:
                    self.assertEqual(err.status_code, 408)
            finally:
                _retry_utility.ExecuteFunctionAsync = self.original_execute_function

    async def test_resource_throttle_retry_policy_with_retry_total_async(self):
        # Testing the kwarg retry_total still has ability to set throttle's max retry attempt count
        max_total_retries = 15
        async with CosmosClient(self.host, self.masterKey, retry_total=max_total_retries) as client:
            database = client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)
            container = database.get_container_client(test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID)
            try:
                self.original_execute_function = _retry_utility.ExecuteFunctionAsync
                _retry_utility.ExecuteFunctionAsync = self._MockExecuteFunction
                document_definition = {'id': str(uuid.uuid4()),
                                       'pk': 'pk',
                                       'name': 'sample document',
                                       'key': 'value'}
                await container.create_item(body=document_definition)
            except exceptions.CosmosHttpResponseError as e:
                self.assertEqual(e.status_code, StatusCodes.TOO_MANY_REQUESTS)
                self.assertEqual(container.client_connection.connection_policy.RetryOptions.MaxRetryAttemptCount,
                                 container.client_connection.last_response_headers[
                                     HttpHeaders.ThrottleRetryCount])
                self.assertEqual(
                    container.client_connection.connection_policy.ConnectionRetryConfiguration.total_retries,
                    max_total_retries)
                self.assertGreaterEqual(container.client_connection.last_response_headers[
                                            HttpHeaders.ThrottleRetryWaitTimeInMs],
                                        container.client_connection.connection_policy.RetryOptions.MaxRetryAttemptCount *
                                        self.retry_after_in_milliseconds)
            finally:
                _retry_utility.ExecuteFunctionAsync = self.original_execute_function

    async def test_resource_throttle_retry_policy_with_retry_throttle_total_async(self):
        # Testing the kwarg retry_throttle_total is behaving as expected
        async with CosmosClient(self.host, self.masterKey, retry_throttle_total=5) as client:
            database = client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)
            container = database.get_container_client(test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID)
            try:
                self.original_execute_function = _retry_utility.ExecuteFunctionAsync
                _retry_utility.ExecuteFunctionAsync = self._MockExecuteFunction
                document_definition = {'id': str(uuid.uuid4()),
                                       'pk': 'pk',
                                       'name': 'sample document',
                                       'key': 'value'}

                await container.create_item(body=document_definition)
            except exceptions.CosmosHttpResponseError as e:
                self.assertEqual(e.status_code, StatusCodes.TOO_MANY_REQUESTS)
                self.assertEqual(container.client_connection.connection_policy.RetryOptions.MaxRetryAttemptCount,
                                 container.client_connection.last_response_headers[
                                     HttpHeaders.ThrottleRetryCount])
                self.assertGreaterEqual(container.client_connection.last_response_headers[
                                            HttpHeaders.ThrottleRetryWaitTimeInMs],
                                        container.client_connection.connection_policy.RetryOptions.MaxRetryAttemptCount *
                                        self.retry_after_in_milliseconds)
            finally:
                _retry_utility.ExecuteFunctionAsync = self.original_execute_function

    async def test_resource_throttle_retry_policy_precedence_async(self):
        # Tests if retry_throttle_total and retry_total are specified then retry_throttle_total should take precedence retry_total
        max_retry_throttle_retries = 15
        max_total_retries = 20

        async with CosmosClient(self.host, self.masterKey, retry_throttle_total=max_retry_throttle_retries,
                                retry_total=max_total_retries) as client:
            database = client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)
            container = database.get_container_client(test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID)
            try:
                self.original_execute_function = _retry_utility.ExecuteFunctionAsync
                _retry_utility.ExecuteFunctionAsync = self._MockExecuteFunction
                document_definition = {'id': str(uuid.uuid4()),
                                       'pk': 'pk',
                                       'name': 'sample document',
                                       'key': 'value'}
                await container.create_item(body=document_definition)
            except exceptions.CosmosHttpResponseError as e:
                self.assertEqual(e.status_code, StatusCodes.TOO_MANY_REQUESTS)
                self.assertEqual(container.client_connection.connection_policy.RetryOptions.MaxRetryAttemptCount,
                                 container.client_connection.last_response_headers[
                                     HttpHeaders.ThrottleRetryCount])
                self.assertEqual(
                    container.client_connection.connection_policy.ConnectionRetryConfiguration.total_retries,
                    max_total_retries)
                self.assertGreaterEqual(container.client_connection.last_response_headers[
                                            HttpHeaders.ThrottleRetryWaitTimeInMs],
                                        container.client_connection.connection_policy.RetryOptions.MaxRetryAttemptCount *
                                        self.retry_after_in_milliseconds)
            finally:
                _retry_utility.ExecuteFunctionAsync = self.original_execute_function

    async def test_resource_connection_retry_policy_max_backoff_async(self):
        # Tests that kwarg retry_max_backoff sets both throttle and connection retry policy
        max_backoff_in_seconds = 10

        async with CosmosClient(self.host, self.masterKey, retry_backoff_max=max_backoff_in_seconds,
                                retry_total=5) as client:
            database = client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)
            container = database.get_container_client(test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID)
            document_definition = {'id': str(uuid.uuid4()),
                                   'pk': 'pk',
                                   'name': 'sample document',
                                   'key': 'value'}
            try:
                self.original_execute_function = _retry_utility.ExecuteFunctionAsync
                mf = self.MockExecuteFunctionConnectionReset(self.original_execute_function)
                _retry_utility.ExecuteFunctionAsync = mf
                created_document = {}
                created_document = await container.create_item(body=document_definition)
            except exceptions.CosmosHttpResponseError as err:
                self.assertEqual(err.status_code, 10054)
                self.assertEqual(container.client_connection.connection_policy.ConnectionRetryConfiguration.backoff_max,
                                 max_backoff_in_seconds)
                self.assertEqual(container.client_connection.connection_policy.RetryOptions._max_wait_time_in_seconds,
                                 max_backoff_in_seconds)
                self.assertDictEqual(created_document, {})
            finally:
                _retry_utility.ExecuteFunctionAsync = self.original_execute_function

    async def test_resource_throttle_retry_policy_max_throttle_backoff_async(self):
        # Tests that kwarg retry_throttle_backoff_max sets the throttle max backoff retry independent of connection max backoff retry
        max_throttle_backoff_in_seconds = 10

        async with CosmosClient(self.host, self.masterKey,
                                retry_throttle_backoff_max=max_throttle_backoff_in_seconds) as client:
            database = client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)
            container = database.get_container_client(test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID)
            document_definition = {'id': str(uuid.uuid4()),
                                   'pk': 'pk',
                                   'name': 'sample document',
                                   'key': 'value'}
            try:
                self.original_execute_function = _retry_utility.ExecuteFunctionAsync
                mf = self.MockExecuteFunctionConnectionReset(self.original_execute_function)
                _retry_utility.ExecuteFunctionAsync = mf
                created_document = {}
                created_document = await container.create_item(body=document_definition)
            except exceptions.CosmosHttpResponseError as err:
                self.assertEqual(err.status_code, 10054)
                self.assertEqual(container.client_connection.connection_policy.RetryOptions._max_wait_time_in_seconds,
                                 max_throttle_backoff_in_seconds)
                self.assertDictEqual(created_document, {})
            finally:
                _retry_utility.ExecuteFunctionAsync = self.original_execute_function

    async def test_resource_throttle_retry_policy_max_backoff_precedence_async(self):
        # Tests to ensure kwargs precedence is being respected between retry_backoff_max and retry_throttle_backoff_max
        max_backoff_in_seconds = 10
        max_throttle_backoff_in_seconds = 5

        async with CosmosClient(self.host, self.masterKey, retry_backoff_max=max_backoff_in_seconds,
                                retry_throttle_backoff_max=max_throttle_backoff_in_seconds) as client:
            database = client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)
            container = database.get_container_client(test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID)
            document_definition = {'id': str(uuid.uuid4()),
                                   'pk': 'pk',
                                   'name': 'sample document',
                                   'key': 'value'}
            try:
                self.original_execute_function = _retry_utility.ExecuteFunctionAsync
                mf = self.MockExecuteFunctionConnectionReset(self.original_execute_function)
                _retry_utility.ExecuteFunctionAsync = mf
                created_document = {}
                created_document = await container.create_item(body=document_definition)
            except exceptions.CosmosHttpResponseError as err:
                self.assertEqual(err.status_code, 10054)
                self.assertEqual(container.client_connection.connection_policy.ConnectionRetryConfiguration.backoff_max,
                                 max_backoff_in_seconds)
                self.assertEqual(container.client_connection.connection_policy.RetryOptions._max_wait_time_in_seconds,
                                 max_throttle_backoff_in_seconds)
                self.assertDictEqual(created_document, {})
            finally:
                _retry_utility.ExecuteFunctionAsync = self.original_execute_function

    async def test_resource_throttle_and_connection_retry_total_retry_with_max_backoff_async(self):
        # Tests kwarg precedence respect with both max total retries and max backoff for both throttle and connection retry policies
        max_retry_throttle_retries = 5
        max_total_retries = 10
        max_throttle_backoff_in_seconds = 15
        max_backoff_in_seconds = 20

        async with CosmosClient(self.host, self.masterKey, retry_backoff_max=max_backoff_in_seconds,
                                retry_throttle_backoff_max=max_throttle_backoff_in_seconds,
                                retry_throttle_total=max_retry_throttle_retries,
                                retry_total=max_total_retries) as client:

            database = client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)
            container = database.get_container_client(test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID)
            self.original_execute_function = _retry_utility.ExecuteFunctionAsync

            try:
                _retry_utility.ExecuteFunctionAsync = self._MockExecuteFunction
                document_definition = {'id': str(uuid.uuid4()),
                                       'pk': 'pk',
                                       'name': 'sample document',
                                       'key': 'value'}
                await container.create_item(body=document_definition)
            except exceptions.CosmosHttpResponseError as e:
                self.assertEqual(e.status_code, StatusCodes.TOO_MANY_REQUESTS)
                self.assertEqual(container.client_connection.connection_policy.RetryOptions.MaxRetryAttemptCount,
                                 container.client_connection.last_response_headers[
                                     HttpHeaders.ThrottleRetryCount])
                self.assertEqual(container.client_connection.connection_policy.ConnectionRetryConfiguration.backoff_max,
                                 max_backoff_in_seconds)
                self.assertEqual(container.client_connection.connection_policy.RetryOptions._max_wait_time_in_seconds,
                                 max_throttle_backoff_in_seconds)
                self.assertEqual(
                    container.client_connection.connection_policy.ConnectionRetryConfiguration.total_retries,
                    max_total_retries)
            finally:
                _retry_utility.ExecuteFunctionAsync = self.original_execute_function

    async def test_patch_replace_no_retry_async(self):
        doc = {'id': str(uuid.uuid4()),
               'pk': str(uuid.uuid4()),
               'name': 'sample document',
               'key': 'value'}
        custom_transport =  FaultInjectionTransportAsync()
        predicate = lambda r: (FaultInjectionTransportAsync.predicate_is_operation_type(r, documents._OperationType.Patch)
                               or FaultInjectionTransportAsync.predicate_is_operation_type(r, documents._OperationType.Replace))
        custom_transport.add_fault(predicate, lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_after_delay(
            0,
            exceptions.CosmosHttpResponseError(
                status_code=502,
                message="Some random reverse proxy error."))))

        initialized_objects = await setup_method_with_custom_transport(
            custom_transport,
        )
        container = initialized_objects["col"]
        connection_retry_policy = initialized_objects["retry_policy"]
        await container.create_item(body=doc)
        operations = [{"op": "incr", "path": "/company", "value": 3}]
        with self.assertRaises(exceptions.CosmosHttpResponseError):
            await container.patch_item(item=doc['id'], partition_key=doc['pk'], patch_operations=operations)
        assert connection_retry_policy.counter == 0
        with self.assertRaises(exceptions.CosmosHttpResponseError):
            doc['name'] = "something else"
            await container.replace_item(item=doc['id'], body=doc)
        assert connection_retry_policy.counter == 0
        # Cleanup
        await initialized_objects["client"].close()

    async def test_health_check_retry_policy_async(self):
        os.environ['AZURE_COSMOS_HEALTH_CHECK_MAX_RETRIES'] = '5'
        os.environ['AZURE_COSMOS_HEALTH_CHECK_RETRY_AFTER_MS'] = '2'
        max_retries = int(os.environ['AZURE_COSMOS_HEALTH_CHECK_MAX_RETRIES'])
        retry_after_ms = int(os.environ['AZURE_COSMOS_HEALTH_CHECK_RETRY_AFTER_MS'])
        self.original_execute_function = _retry_utility.ExecuteFunctionAsync
        mock_execute = self.MockExecuteFunctionHealthCheck(self.original_execute_function)
        _retry_utility.ExecuteFunctionAsync = mock_execute

        try:
            with self.assertRaises(exceptions.CosmosHttpResponseError) as context:
                async with CosmosClient( self.host,
                        self.masterKey):
                   pass

            self.assertEqual(context.exception.status_code, 503)
            # The total number of calls will be the initial call + the number of retries
            self.assertEqual(mock_execute.counter, max_retries + 1)
            # Assert retry interval from environment variable
            policy = HealthCheckRetryPolicy(ConnectionPolicy())
            self.assertEqual(policy.retry_after_in_milliseconds, retry_after_ms)
        finally:
            del os.environ["AZURE_COSMOS_HEALTH_CHECK_MAX_RETRIES"]
            del os.environ["AZURE_COSMOS_HEALTH_CHECK_RETRY_AFTER_MS"]
            _retry_utility.ExecuteFunctionAsync = self.original_execute_function

    async def test_health_check_retry_policy_defaults_async(self):

        self.original_execute_function = _retry_utility.ExecuteFunctionAsync
        mock_execute = self.MockExecuteFunctionHealthCheckServiceRequestError(self.original_execute_function)
        _retry_utility.ExecuteFunctionAsync = mock_execute

        try:
            with self.assertRaises(ServiceRequestError):
                async with CosmosClient(self.host, self.masterKey):
                   pass

            # Should use default retry attempts from _constants.py
            self.assertEqual(
                mock_execute.counter,
                _Constants.AZURE_COSMOS_HEALTH_CHECK_MAX_RETRIES_DEFAULT + 1
            )

            # Verify default retry time in ms
            policy = HealthCheckRetryPolicy(ConnectionPolicy())
            self.assertEqual(
                policy.retry_after_in_milliseconds,
                _Constants.AZURE_COSMOS_HEALTH_CHECK_RETRY_AFTER_MS_DEFAULT
            )
        finally:
            _retry_utility.ExecuteFunctionAsync = self.original_execute_function

    async def test_health_check_retry_with_service_request_error_async(self):
        self.original_execute_function = _retry_utility.ExecuteFunctionAsync
        mock_execute = self.MockExecuteFunctionHealthCheckServiceRequestError(self.original_execute_function)
        _retry_utility.ExecuteFunctionAsync = mock_execute

        try:
            with self.assertRaises(ServiceRequestError):
                async with CosmosClient(self.host, self.masterKey):
                   pass # Triggers database account read

            # Should use default retry attempts from _constants.py
            self.assertEqual(
                mock_execute.counter,
                _Constants.AZURE_COSMOS_HEALTH_CHECK_MAX_RETRIES_DEFAULT + 1
            )
            # Verify default retry time in ms
            policy = HealthCheckRetryPolicy(ConnectionPolicy())
            self.assertEqual(
                policy.retry_after_in_milliseconds,
                _Constants.AZURE_COSMOS_HEALTH_CHECK_RETRY_AFTER_MS_DEFAULT
            )
        finally:
            _retry_utility.ExecuteFunctionAsync = self.original_execute_function

    class MockExecuteFunctionHealthCheckServiceRequestError(object):
        def __init__(self, org_func):
            self.org_func = org_func
            self.counter = 0

        async def __call__(self, func, *args, **kwargs):
            # The second argument to the internal _request function is the RequestObject.
            request_object = args[1]
            if (request_object.operation_type == documents._OperationType.Read and
                    request_object.resource_type == ResourceType.DatabaseAccount):
                self.counter += 1
                raise ServiceRequestError("mocked service request error")
            return await self.org_func(func, *args, **kwargs)

    class MockExecuteFunctionDBAError(object):
        def __init__(self, org_func, error):
            self.org_func = org_func
            self.counter = 0
            self.error = error

        async def __call__(self, func, *args, **kwargs):
            # The second argument to the internal _request function is the RequestObject.
            request_object = args[1]
            if (request_object.operation_type == documents._OperationType.Read and
                    request_object.resource_type == ResourceType.DatabaseAccount):
                self.counter += 1
                raise self.error
            return await self.org_func(func, *args, **kwargs)

    class MockExecuteFunctionDBA(object):
        def __init__(self, org_func):
            self.org_func = org_func
            self.counter = 0

        async def __call__(self, func, *args, **kwargs):
            # The second argument to the internal _request function is the RequestObject.
            request_object = args[1]
            if (request_object.operation_type == documents._OperationType.Read and
                    request_object.resource_type == ResourceType.DatabaseAccount):
                self.counter += 1
            return await self.org_func(func, *args, **kwargs)

    async def _MockExecuteFunction(self, function, *args, **kwargs):
        response = test_config.FakeResponse({HttpHeaders.RetryAfterInMilliseconds: self.retry_after_in_milliseconds})
        raise exceptions.CosmosHttpResponseError(
            status_code=StatusCodes.TOO_MANY_REQUESTS,
            message="Request rate is too large",
            response=response)

    class MockExecuteFunctionTimeout(object):
        def __init__(self, org_func):
            self.org_func = org_func
            self.counter = 0

        async def __call__(self, func, *args, **kwargs):
            raise exceptions.CosmosHttpResponseError(
                status_code=408,
                message="Timeout",
                response=test_config.FakeResponse({}))

    class MockExecuteFunctionConnectionReset(object):
        def __init__(self, org_func):
            self.org_func = org_func
            self.counter = 0

        async def __call__(self, func, *args, **kwargs):
            self.counter = self.counter + 1
            if self.counter % 3 == 0:
                return await self.org_func(func, *args, **kwargs)
            else:
                raise exceptions.CosmosHttpResponseError(
                    status_code=10054,
                    message="Connection was reset",
                    response=test_config.FakeResponse({}))

    class MockExecuteFunctionHealthCheck(object):
        def __init__(self, org_func):
            self.org_func = org_func
            self.counter = 0

        async def __call__(self, func, *args, **kwargs):
            # The second argument to the internal _request function is the RequestObject.
            request_object = args[1]
            if (request_object.operation_type == documents._OperationType.Read and
                    request_object.resource_type == ResourceType.DatabaseAccount):
                self.counter += 1
                raise exceptions.CosmosHttpResponseError(
                    status_code=503,
                    message="Service Unavailable.")
            return await self.org_func(func, *args, **kwargs)

if __name__ == '__main__':
    unittest.main()
