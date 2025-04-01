# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid

import pytest

import azure.cosmos._retry_options as retry_options
import azure.cosmos.exceptions as exceptions
import test_config
from azure.cosmos.partition_key import PartitionKey
from azure.cosmos.http_constants import HttpHeaders, StatusCodes
from azure.cosmos.aio import CosmosClient
from azure.cosmos.aio import DatabaseProxy, ContainerProxy
import azure.cosmos.aio._retry_utility_async as _retry_utility
from azure.cosmos._retry_options import RetryOptions

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
        self.RetryOptions: RetryOptions = RetryOptions()
        self.DisableSSLVerification: bool = False
        self.UseMultipleWriteLocations: bool = False
        self.ConnectionRetryConfiguration: Optional["ConnectionRetryPolicy"] = None
        self.ResponsePayloadOnWriteDisabled: bool = False

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

if __name__ == '__main__':
    unittest.main()
