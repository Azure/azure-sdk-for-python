# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid

import pytest

import azure.cosmos._retry_options as retry_options
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
import test_config
from azure.cosmos import _retry_utility, PartitionKey, documents
from azure.cosmos.http_constants import HttpHeaders, StatusCodes
from _fault_injection_transport import FaultInjectionTransport


def setup_method_with_custom_transport(
        custom_transport,
        **kwargs):
    connection_retry_policy = test_config.MockConnectionRetryPolicy(resource_type="docs")
    client = cosmos_client.CosmosClient(test_config.TestConfig.host, test_config.TestConfig.masterKey,
                                        transport=custom_transport, connection_retry_policy=connection_retry_policy, **kwargs)
    db = client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)
    container = db.get_container_client(test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID)
    return {"client": client, "db": db, "col": container, "retry_policy": connection_retry_policy}


@pytest.mark.cosmosEmulator
class TestRetryPolicy(unittest.TestCase):
    created_database = None
    client = None
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy
    counter = 0
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_SINGLE_PARTITION_ID = "test-retry-policy-container-" + str(uuid.uuid4())

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

        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey, consistency_level="Session",
                                                connection_policy=cls.connectionPolicy)
        cls.created_database = cls.client.get_database_client(cls.TEST_DATABASE_ID)
        cls.retry_after_in_milliseconds = 1000

    def setUp(self) -> None:
        self.created_collection = self.created_database.create_container(self.TEST_CONTAINER_SINGLE_PARTITION_ID,
                                                                         partition_key=PartitionKey("/pk"))

    def tearDown(self) -> None:
        try:
            self.created_database.delete_container(self.TEST_CONTAINER_SINGLE_PARTITION_ID)
        except exceptions.CosmosHttpResponseError:
            pass

    def test_resource_throttle_retry_policy_default_retry_after(self):
        connection_policy = TestRetryPolicy.connectionPolicy
        connection_policy.RetryOptions = retry_options.RetryOptions(5)

        self.original_execute_function = _retry_utility.ExecuteFunction
        try:
            _retry_utility.ExecuteFunction = self._MockExecuteFunction

            document_definition = {'id': str(uuid.uuid4()),
                                   'pk': 'pk',
                                   'name': 'sample document',
                                   'key': 'value'}

            try:
                self.created_collection.create_item(body=document_definition)
            except exceptions.CosmosHttpResponseError as e:
                self.assertEqual(e.status_code, StatusCodes.TOO_MANY_REQUESTS)
                self.assertEqual(connection_policy.RetryOptions.MaxRetryAttemptCount,
                                 self.created_collection.client_connection.last_response_headers[
                                     HttpHeaders.ThrottleRetryCount])
                self.assertGreaterEqual(self.created_collection.client_connection.last_response_headers[
                                            HttpHeaders.ThrottleRetryWaitTimeInMs],
                                        connection_policy.RetryOptions.MaxRetryAttemptCount *
                                        self.retry_after_in_milliseconds)
        finally:
            _retry_utility.ExecuteFunction = self.original_execute_function

    def test_resource_throttle_retry_policy_fixed_retry_after(self):
        connection_policy = TestRetryPolicy.connectionPolicy
        connection_policy.RetryOptions = retry_options.RetryOptions(5, 2000)

        self.original_execute_function = _retry_utility.ExecuteFunction
        try:
            _retry_utility.ExecuteFunction = self._MockExecuteFunction

            document_definition = {'id': str(uuid.uuid4()),
                                   'pk': 'pk',
                                   'name': 'sample document',
                                   'key': 'value'}

            try:
                self.created_collection.create_item(body=document_definition)
            except exceptions.CosmosHttpResponseError as e:
                self.assertEqual(e.status_code, StatusCodes.TOO_MANY_REQUESTS)
                self.assertEqual(connection_policy.RetryOptions.MaxRetryAttemptCount,
                                 self.created_collection.client_connection.last_response_headers[
                                     HttpHeaders.ThrottleRetryCount])
                self.assertGreaterEqual(self.created_collection.client_connection.last_response_headers[
                                            HttpHeaders.ThrottleRetryWaitTimeInMs],
                                        connection_policy.RetryOptions.MaxRetryAttemptCount * connection_policy.RetryOptions.FixedRetryIntervalInMilliseconds)

        finally:
            _retry_utility.ExecuteFunction = self.original_execute_function

    def test_resource_throttle_retry_policy_max_wait_time(self):
        connection_policy = TestRetryPolicy.connectionPolicy
        connection_policy.RetryOptions = retry_options.RetryOptions(5, 2000, 3)

        self.original_execute_function = _retry_utility.ExecuteFunction
        try:
            _retry_utility.ExecuteFunction = self._MockExecuteFunction

            document_definition = {'id': str(uuid.uuid4()),
                                   'pk': 'pk',
                                   'name': 'sample document',
                                   'key': 'value'}

            try:
                self.created_collection.create_item(body=document_definition)
            except exceptions.CosmosHttpResponseError as e:
                self.assertEqual(e.status_code, StatusCodes.TOO_MANY_REQUESTS)
                self.assertGreaterEqual(self.created_collection.client_connection.last_response_headers[
                                            HttpHeaders.ThrottleRetryWaitTimeInMs],
                                        connection_policy.RetryOptions.MaxWaitTimeInSeconds * 1000)
        finally:
            _retry_utility.ExecuteFunction = self.original_execute_function

    def test_resource_throttle_retry_policy_query(self):
        connection_policy = TestRetryPolicy.connectionPolicy
        connection_policy.RetryOptions = retry_options.RetryOptions(5)

        document_definition = {'id': str(uuid.uuid4()),
                               'pk': 'pk',
                               'name': 'sample document',
                               'key': 'value'}

        self.created_collection.create_item(body=document_definition)

        self.original_execute_function = _retry_utility.ExecuteFunction
        try:
            _retry_utility.ExecuteFunction = self._MockExecuteFunction

            try:
                list(self.created_collection.query_items(
                    {
                        'query': 'SELECT * FROM root r WHERE r.id=@id',
                        'parameters': [
                            {'name': '@id', 'value': document_definition['id']}
                        ]
                    }))
            except exceptions.CosmosHttpResponseError as e:
                self.assertEqual(e.status_code, StatusCodes.TOO_MANY_REQUESTS)
                self.assertEqual(connection_policy.RetryOptions.MaxRetryAttemptCount,
                                 self.created_collection.client_connection.last_response_headers[
                                     HttpHeaders.ThrottleRetryCount])
                self.assertGreaterEqual(self.created_collection.client_connection.last_response_headers[
                                            HttpHeaders.ThrottleRetryWaitTimeInMs],
                                        connection_policy.RetryOptions.MaxRetryAttemptCount * self.retry_after_in_milliseconds)
        finally:
            _retry_utility.ExecuteFunction = self.original_execute_function

    # TODO: Need to validate the query retries
    @pytest.mark.skip
    def test_default_retry_policy_for_query(self):
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
        self.original_execute_function = _retry_utility.ExecuteFunction
        try:
            mf = self.MockExecuteFunctionConnectionReset(self.original_execute_function)
            _retry_utility.ExecuteFunction = mf

            docs = self.created_collection.query_items(query="Select * from c order by c._ts", max_item_count=1,
                                                       enable_cross_partition_query=True)

            result_docs = list(docs)
            self.assertEqual(result_docs[0]['id'], document_definition_1['id'])
            self.assertEqual(result_docs[1]['id'], document_definition_2['id'])

            self.assertEqual(mf.counter, 27)
        finally:
            _retry_utility.ExecuteFunction = self.original_execute_function

    def test_default_retry_policy_for_create(self):
        document_definition = {'id': str(uuid.uuid4()),
                               'pk': 'pk',
                               'name': 'sample document',
                               'key': 'value'}

        try:
            self.original_execute_function = _retry_utility.ExecuteFunction
            mf = self.MockExecuteFunctionConnectionReset(self.original_execute_function)
            _retry_utility.ExecuteFunction = mf

            created_document = {}
            try:
                created_document = self.created_collection.create_item(body=document_definition)
            except exceptions.CosmosHttpResponseError as err:
                self.assertEqual(err.status_code, 10054)

            self.assertDictEqual(created_document, {})

            self.assertEqual(mf.counter, 1)
        finally:
            _retry_utility.ExecuteFunction = self.original_execute_function

    def test_timeout_failover_retry_policy_for_read(self):
        document_definition = {'id': 'failoverDoc',
                               'pk': 'pk',
                               'name': 'sample document',
                               'key': 'value'}

        created_document = self.created_collection.create_item(body=document_definition)
        self.original_execute_function = _retry_utility.ExecuteFunction
        try:
            mf = self.MockExecuteFunctionTimeout(self.original_execute_function)
            _retry_utility.ExecuteFunction = mf
            try:
                self.created_collection.read_item(item=created_document['id'], partition_key=created_document['pk'])
            except exceptions.CosmosHttpResponseError as err:
                self.assertEqual(err.status_code, 408)
        finally:
            _retry_utility.ExecuteFunction = self.original_execute_function

    def test_resource_throttle_retry_policy_with_retry_total(self):
        # Testing the kwarg retry_total still has ability to set throttle's max retry attempt count
        max_total_retries = 15
        with cosmos_client.CosmosClient(self.host, self.masterKey, retry_total=max_total_retries) as client:
            database = client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)
            container = database.get_container_client(test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID)
            try:
                self.original_execute_function = _retry_utility.ExecuteFunction
                _retry_utility.ExecuteFunction = self._MockExecuteFunction
                document_definition = {'id': str(uuid.uuid4()),
                                       'pk': 'pk',
                                       'name': 'sample document',
                                       'key': 'value'}
                container.create_item(body=document_definition)
            except exceptions.CosmosHttpResponseError as e:
                self.assertEqual(e.status_code, StatusCodes.TOO_MANY_REQUESTS)
                self.assertEqual(container.client_connection.connection_policy.RetryOptions.MaxRetryAttemptCount,
                                 container.client_connection.last_response_headers[
                                     HttpHeaders.ThrottleRetryCount])
                self.assertEqual(container.client_connection.connection_policy.ConnectionRetryConfiguration.total_retries, max_total_retries)
                self.assertGreaterEqual(container.client_connection.last_response_headers[
                                            HttpHeaders.ThrottleRetryWaitTimeInMs],
                                        container.client_connection.connection_policy.RetryOptions.MaxRetryAttemptCount *
                                        self.retry_after_in_milliseconds)
            finally:
                _retry_utility.ExecuteFunction = self.original_execute_function

    def test_resource_throttle_retry_policy_with_retry_throttle_total(self):
        #Testing the kwarg retry_throttle_total is behaving as expected
        with cosmos_client.CosmosClient(self.host, self.masterKey, retry_throttle_total=5) as client:
            database = client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)
            container = database.get_container_client(test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID)
            try:
                self.original_execute_function = _retry_utility.ExecuteFunction
                _retry_utility.ExecuteFunction = self._MockExecuteFunction
                document_definition = {'id': str(uuid.uuid4()),
                                       'pk': 'pk',
                                       'name': 'sample document',
                                       'key': 'value'}

                container.create_item(body=document_definition)
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
                _retry_utility.ExecuteFunction = self.original_execute_function

    def test_resource_throttle_retry_policy_precedence(self):
        # Tests if retry_throttle_total and retry_total are specified then retry_throttle_total should take precedence retry_total
        max_retry_throttle_retries = 15
        max_total_retries = 20

        with cosmos_client.CosmosClient(self.host, self.masterKey, retry_throttle_total=max_retry_throttle_retries, retry_total=max_total_retries) as client:
            database = client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)
            container = database.get_container_client(test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID)
            try:
                self.original_execute_function = _retry_utility.ExecuteFunction
                _retry_utility.ExecuteFunction = self._MockExecuteFunction
                document_definition = {'id': str(uuid.uuid4()),
                                       'pk': 'pk',
                                       'name': 'sample document',
                                       'key': 'value'}
                container.create_item(body=document_definition)
            except exceptions.CosmosHttpResponseError as e:
                self.assertEqual(e.status_code, StatusCodes.TOO_MANY_REQUESTS)
                self.assertEqual(container.client_connection.connection_policy.RetryOptions.MaxRetryAttemptCount,
                                 container.client_connection.last_response_headers[
                                     HttpHeaders.ThrottleRetryCount])
                self.assertEqual(container.client_connection.connection_policy.ConnectionRetryConfiguration.total_retries, max_total_retries)
                self.assertGreaterEqual(container.client_connection.last_response_headers[
                                            HttpHeaders.ThrottleRetryWaitTimeInMs],
                                        container.client_connection.connection_policy.RetryOptions.MaxRetryAttemptCount *
                                        self.retry_after_in_milliseconds)
            finally:
                _retry_utility.ExecuteFunction = self.original_execute_function

    def test_resource_connection_retry_policy_max_backoff(self):
        # Tests that kwarg retry_max_backoff sets both throttle and connection retry policy
        max_backoff_in_seconds = 10

        with cosmos_client.CosmosClient(self.host, self.masterKey, retry_backoff_max=max_backoff_in_seconds, retry_total=5) as client:
            database = client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)
            container = database.get_container_client(test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID)
            document_definition = {'id': str(uuid.uuid4()),
                                   'pk': 'pk',
                                   'name': 'sample document',
                                   'key': 'value'}
            try:
                self.original_execute_function = _retry_utility.ExecuteFunction
                mf = self.MockExecuteFunctionConnectionReset(self.original_execute_function)
                _retry_utility.ExecuteFunction = mf
                created_document = {}
                created_document = container.create_item(body=document_definition)
            except exceptions.CosmosHttpResponseError as err:
                self.assertEqual(err.status_code, 10054)
                self.assertEqual(container.client_connection.connection_policy.ConnectionRetryConfiguration.backoff_max, max_backoff_in_seconds)
                self.assertEqual(container.client_connection.connection_policy.RetryOptions._max_wait_time_in_seconds, max_backoff_in_seconds)
                self.assertDictEqual(created_document, {})
            finally:
                _retry_utility.ExecuteFunction = self.original_execute_function

    def test_resource_throttle_retry_policy_max_throttle_backoff(self):
        # Tests that kwarg retry_throttle_backoff_max sets the throttle max backoff retry independent of connection max backoff retry
        max_throttle_backoff_in_seconds = 10

        with cosmos_client.CosmosClient(self.host, self.masterKey, retry_throttle_backoff_max=max_throttle_backoff_in_seconds) as client:
            database = client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)
            container = database.get_container_client(test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID)
            document_definition = {'id': str(uuid.uuid4()),
                                   'pk': 'pk',
                                   'name': 'sample document',
                                   'key': 'value'}
            try:
                self.original_execute_function = _retry_utility.ExecuteFunction
                mf = self.MockExecuteFunctionConnectionReset(self.original_execute_function)
                _retry_utility.ExecuteFunction = mf
                created_document = {}
                created_document = container.create_item(body=document_definition)
            except exceptions.CosmosHttpResponseError as err:
                self.assertEqual(err.status_code, 10054)
                self.assertEqual(container.client_connection.connection_policy.RetryOptions._max_wait_time_in_seconds,
                                 max_throttle_backoff_in_seconds)
                self.assertDictEqual(created_document, {})
            finally:
                _retry_utility.ExecuteFunction = self.original_execute_function

    def test_resource_throttle_retry_policy_max_backoff_precedence(self):
        # Tests to ensure kwargs precedence is being respected between retry_backoff_max and retry_throttle_backoff_max
        max_backoff_in_seconds = 10
        max_throttle_backoff_in_seconds = 5

        with cosmos_client.CosmosClient(self.host, self.masterKey, retry_backoff_max=max_backoff_in_seconds,
                                        retry_throttle_backoff_max=max_throttle_backoff_in_seconds) as client:
            database = client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)
            container = database.get_container_client(test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID)
            document_definition = {'id': str(uuid.uuid4()),
                                   'pk': 'pk',
                                   'name': 'sample document',
                                   'key': 'value'}
            try:
                self.original_execute_function = _retry_utility.ExecuteFunction
                mf = self.MockExecuteFunctionConnectionReset(self.original_execute_function)
                _retry_utility.ExecuteFunction = mf
                created_document = {}
                created_document = container.create_item(body=document_definition)
            except exceptions.CosmosHttpResponseError as err:
                self.assertEqual(err.status_code, 10054)
                self.assertEqual(container.client_connection.connection_policy.ConnectionRetryConfiguration.backoff_max,
                                 max_backoff_in_seconds)
                self.assertEqual(container.client_connection.connection_policy.RetryOptions._max_wait_time_in_seconds,
                                 max_throttle_backoff_in_seconds)
                self.assertDictEqual(created_document, {})
            finally:
                _retry_utility.ExecuteFunction = self.original_execute_function

    def test_resource_throttle_and_connection_retry_total_retry_with_max_backoff(self):
        # Tests kwarg precedence respect with both max total retries and max backoff for both throttle and connection retry policies
        max_retry_throttle_retries = 15
        max_total_retries = 20
        max_throttle_backoff_in_seconds = 25
        max_backoff_in_seconds = 30

        with cosmos_client.CosmosClient(self.host, self.masterKey, retry_backoff_max=max_backoff_in_seconds,
                                        retry_throttle_backoff_max=max_throttle_backoff_in_seconds,
                                        retry_throttle_total=max_retry_throttle_retries,
                                        retry_total=max_total_retries) as client:

            database = client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)
            container = database.get_container_client(test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID)
            self.original_execute_function = _retry_utility.ExecuteFunction

            try:
                _retry_utility.ExecuteFunction = self._MockExecuteFunction
                document_definition = {'id': str(uuid.uuid4()),
                                       'pk': 'pk',
                                       'name': 'sample document',
                                       'key': 'value'}
                container.create_item(body=document_definition)
            except exceptions.CosmosHttpResponseError as e:
                self.assertEqual(e.status_code, StatusCodes.TOO_MANY_REQUESTS)
                self.assertEqual(container.client_connection.connection_policy.RetryOptions.MaxRetryAttemptCount,
                                 container.client_connection.last_response_headers[
                                     HttpHeaders.ThrottleRetryCount])
                self.assertEqual(container.client_connection.connection_policy.ConnectionRetryConfiguration.backoff_max,
                                 max_backoff_in_seconds)
                self.assertEqual(container.client_connection.connection_policy.RetryOptions._max_wait_time_in_seconds,
                                 max_throttle_backoff_in_seconds)
                self.assertEqual(container.client_connection.connection_policy.ConnectionRetryConfiguration.total_retries,
                    max_total_retries)
            finally:
                _retry_utility.ExecuteFunction = self.original_execute_function

    def test_patch_replace_no_retry(self):
        doc = {'id': str(uuid.uuid4()),
               'pk': str(uuid.uuid4()),
               'name': 'sample document',
               'key': 'value'}
        custom_transport =  FaultInjectionTransport()
        predicate = lambda r: (FaultInjectionTransport.predicate_is_operation_type(r, documents._OperationType.Patch)
                               or FaultInjectionTransport.predicate_is_operation_type(r, documents._OperationType.Replace))
        custom_transport.add_fault(predicate, lambda r: FaultInjectionTransport.error_after_delay(
            0,
            exceptions.CosmosHttpResponseError(
                status_code=502,
                message="Some random reverse proxy error.")))

        initialized_objects = setup_method_with_custom_transport(
            custom_transport,
        )
        container = initialized_objects["col"]
        connection_retry_policy = initialized_objects["retry_policy"]
        container.create_item(body=doc)
        operations = [{"op": "incr", "path": "/company", "value": 3}]
        with self.assertRaises(exceptions.CosmosHttpResponseError):
            container.patch_item(item=doc['id'], partition_key=doc['pk'], patch_operations=operations)
        assert connection_retry_policy.counter == 0
        with self.assertRaises(exceptions.CosmosHttpResponseError):
            doc['name'] = "something else"
            container.replace_item(item=doc['id'], body=doc)
        assert connection_retry_policy.counter == 0

    def _MockExecuteFunction(self, function, *args, **kwargs):
        response = test_config.FakeResponse({HttpHeaders.RetryAfterInMilliseconds: self.retry_after_in_milliseconds})
        raise exceptions.CosmosHttpResponseError(
            status_code=StatusCodes.TOO_MANY_REQUESTS,
            message="Request rate is too large",
            response=response)

    class MockExecuteFunctionTimeout(object):
        def __init__(self, org_func):
            self.org_func = org_func
            self.counter = 0

        def __call__(self, func, *args, **kwargs):
            raise exceptions.CosmosHttpResponseError(
                status_code=408,
                message="Timeout",
                response=test_config.FakeResponse({}))

    class MockExecuteFunctionConnectionReset(object):
        def __init__(self, org_func):
            self.org_func = org_func
            self.counter = 0

        def __call__(self, func, *args, **kwargs):
            self.counter = self.counter + 1
            if self.counter % 3 == 0:
                return self.org_func(func, *args, **kwargs)
            else:
                raise exceptions.CosmosHttpResponseError(
                    status_code=10054,
                    message="Connection was reset",
                    response=test_config.FakeResponse({}))

if __name__ == '__main__':
    unittest.main()
