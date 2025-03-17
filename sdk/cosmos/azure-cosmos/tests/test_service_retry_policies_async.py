# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid

import pytest
from aiohttp.client_exceptions import (ClientConnectionError, ClientConnectionResetError,
                                       ClientOSError, ServerConnectionError)
from azure.core.exceptions import ServiceRequestError, ServiceResponseError

import test_config
from azure.cosmos import DatabaseAccount, _location_cache
from azure.cosmos._location_cache import RegionalRoutingContext
from azure.cosmos.aio import CosmosClient, _retry_utility_async, _global_endpoint_manager_async
from azure.cosmos.exceptions import CosmosHttpResponseError


@pytest.mark.cosmosEmulator
class TestServiceRetryPoliciesAsync(unittest.IsolatedAsyncioTestCase):
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_ID = test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID
    REGION1 = "West US"
    REGION2 = "East US"
    REGION3 = "West US 2"
    REGIONAL_ENDPOINT = RegionalRoutingContext(host, host)

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

    async def asyncSetUp(self):
        self.client = CosmosClient(self.host, self.masterKey)
        self.created_database = self.client.get_database_client(self.TEST_DATABASE_ID)
        self.created_container = self.created_database.get_container_client(self.TEST_CONTAINER_ID)

    async def asyncTearDown(self):
        await self.client.close()

    async def test_service_request_retry_policy_async(self):
        # ServiceRequestErrors will always retry, and will retry once per preferred region
        async with CosmosClient(self.host, self.masterKey) as mock_client:
            db = mock_client.get_database_client(self.TEST_DATABASE_ID)
            container = db.get_container_client(self.TEST_CONTAINER_ID)

            created_item = await container.create_item({"id": str(uuid.uuid4()), "pk": str(uuid.uuid4())})
            # Save the original function
            self.original_execute_function = _retry_utility_async.ExecuteFunctionAsync

            # Change the location cache to have 3 preferred read regions and 3 available read endpoints by location
            original_location_cache = mock_client.client_connection._global_endpoint_manager.location_cache
            original_location_cache.account_read_locations = [self.REGION1, self.REGION2, self.REGION3]
            original_location_cache.available_read_regional_endpoints_by_locations = {
                self.REGION1: self.REGIONAL_ENDPOINT,
                self.REGION2: self.REGIONAL_ENDPOINT,
                self.REGION3: self.REGIONAL_ENDPOINT}
            original_location_cache.read_regional_routing_contexts = [self.REGIONAL_ENDPOINT, self.REGIONAL_ENDPOINT,
                                                                      self.REGIONAL_ENDPOINT]
            try:
                # Mock the function to return the ServiceRequestException we retry
                mf = self.MockExecuteServiceRequestException()
                _retry_utility_async.ExecuteFunctionAsync = mf
                await container.read_item(created_item['id'], created_item['pk'])
                pytest.fail("Exception was not raised.")
            except ServiceRequestError:
                assert mf.counter == 3
            finally:
                _retry_utility_async.ExecuteFunctionAsync = self.original_execute_function

            # Now we change the location cache to have only 1 preferred read region
            original_location_cache.account_read_locations = [self.REGION1]
            original_location_cache.read_regional_routing_contexts = [self.REGIONAL_ENDPOINT]
            try:
                # Reset the function to reset the counter
                mf = self.MockExecuteServiceRequestException()
                _retry_utility_async.ExecuteFunctionAsync = mf
                await container.read_item(created_item['id'], created_item['pk'])
                pytest.fail("Exception was not raised.")
            except ServiceRequestError:
                assert mf.counter == 1
            finally:
                _retry_utility_async.ExecuteFunctionAsync = self.original_execute_function

            # Now we try it out with a write request
            original_location_cache.account_write_locations = [self.REGION1, self.REGION2]
            original_location_cache.write_regional_routing_contexts = [self.REGIONAL_ENDPOINT, self.REGIONAL_ENDPOINT]
            original_location_cache.available_write_regional_endpoints_by_locations = {
                self.REGION1: self.REGIONAL_ENDPOINT,
                self.REGION2: self.REGIONAL_ENDPOINT}
            try:
                # Reset the function to reset the counter
                mf = self.MockExecuteServiceRequestException()
                _retry_utility_async.ExecuteFunctionAsync = mf
                await container.create_item({"id": str(uuid.uuid4()), "pk": str(uuid.uuid4())})
                pytest.fail("Exception was not raised.")
            except ServiceRequestError:
                assert mf.counter == 2
            finally:
                _retry_utility_async.ExecuteFunctionAsync = self.original_execute_function

    async def test_service_response_retry_policy_async(self):
        # For ServiceResponseErrors, we only do cross region retries on read requests or on ClientConnectionErrors
        # We also only do retries within the ConnectionRetryPolicy for the cases above
        async with CosmosClient(self.host, self.masterKey) as mock_client:
            db = mock_client.get_database_client(self.TEST_DATABASE_ID)
            container = db.get_container_client(self.TEST_CONTAINER_ID)

            created_item = await container.create_item({"id": str(uuid.uuid4()), "pk": str(uuid.uuid4())})
            # Save the original function
            self.original_execute_function = _retry_utility_async.ExecuteFunctionAsync

            # Change the location cache to have 3 preferred read regions and 3 available read endpoints by location
            original_location_cache = mock_client.client_connection._global_endpoint_manager.location_cache
            original_location_cache.account_read_locations = [self.REGION1, self.REGION2, self.REGION3]
            original_location_cache.available_read_regional_endpoints_by_locations = {
                self.REGION1: self.REGIONAL_ENDPOINT,
                self.REGION2: self.REGIONAL_ENDPOINT,
                self.REGION3: self.REGIONAL_ENDPOINT}
            original_location_cache.read_regional_routing_contexts = [self.REGIONAL_ENDPOINT, self.REGIONAL_ENDPOINT,
                                                                      self.REGIONAL_ENDPOINT]
            try:
                # Mock the function to return the ClientConnectionError we retry
                mf = self.MockExecuteServiceResponseException(AttributeError, None)
                _retry_utility_async.ExecuteFunctionAsync = mf
                await container.read_item(created_item['id'], created_item['pk'])
                pytest.fail("Exception was not raised.")
            except ServiceResponseError:
                assert mf.counter == 3
            finally:
                _retry_utility_async.ExecuteFunctionAsync = self.original_execute_function

            # Now we change the location cache to have only 1 preferred read region
            original_location_cache.account_read_locations = [self.REGION1]
            original_location_cache.read_regional_routing_contexts = [self.REGIONAL_ENDPOINT]
            try:
                # Reset the function to reset the counter
                mf = self.MockExecuteServiceResponseException(AttributeError, None)
                _retry_utility_async.ExecuteFunctionAsync = mf
                await container.read_item(created_item['id'], created_item['pk'])
                pytest.fail("Exception was not raised.")
            except ServiceResponseError:
                assert mf.counter == 1
            finally:
                _retry_utility_async.ExecuteFunctionAsync = self.original_execute_function

            # Now we try it out with a write request
            original_location_cache.account_write_locations = [self.REGION1, self.REGION2]
            original_location_cache.write_regional_routing_contexts = [self.REGIONAL_ENDPOINT, self.REGIONAL_ENDPOINT]
            original_location_cache.available_write_regional_endpoints_by_locations = {
                self.REGION1: self.REGIONAL_ENDPOINT,
                self.REGION2: self.REGIONAL_ENDPOINT}
            try:
                # Reset the function to reset the counter
                mf = self.MockExecuteServiceResponseException(AttributeError, None)
                _retry_utility_async.ExecuteFunctionAsync = mf
                # Even though we have 2 preferred write endpoints,
                # we will only run the exception once due to no retries on write requests
                await container.create_item({"id": str(uuid.uuid4()), "pk": str(uuid.uuid4())})
                pytest.fail("Exception was not raised.")
            except ServiceResponseError:
                assert mf.counter == 1
            finally:
                _retry_utility_async.ExecuteFunctionAsync = self.original_execute_function

            # If we do a write request with a ClientConnectionError,
            # we will do cross-region retries like with read requests
            original_location_cache.account_write_locations = [self.REGION1, self.REGION2]
            original_location_cache.write_regional_routing_contexts = [self.REGIONAL_ENDPOINT, self.REGIONAL_ENDPOINT]
            original_location_cache.available_write_regional_endpoints_by_locations = {
                self.REGION1: self.REGIONAL_ENDPOINT,
                self.REGION2: self.REGIONAL_ENDPOINT}
            try:
                # Reset the function to reset the counter
                mf = self.MockExecuteServiceResponseException(ClientConnectionError, ClientConnectionError())
                _retry_utility_async.ExecuteFunctionAsync = mf
                await container.create_item({"id": str(uuid.uuid4()), "pk": str(uuid.uuid4())})
                pytest.fail("Exception was not raised.")
            except ServiceResponseError:
                assert mf.counter == 2
            finally:
                _retry_utility_async.ExecuteFunctionAsync = self.original_execute_function

    async def test_service_request_connection_retry_policy_async(self):
        # Mock the client retry policy to see the same-region retries that happen there
        exception = ServiceRequestError("mock exception")
        exception.exc_type = Exception
        connection_policy = self.connectionPolicy
        connection_retry_policy = test_config.MockConnectionRetryPolicyAsync(resource_type="docs", error=exception)
        connection_policy.ConnectionRetryConfiguration = connection_retry_policy
        async with CosmosClient(self.host, self.masterKey, connection_policy=connection_policy) as mock_client:
            db = mock_client.get_database_client(self.TEST_DATABASE_ID)
            container = db.get_container_client(self.TEST_CONTAINER_ID)

            # We retry ServiceRequestExceptions 3 times in the to the same endpoint before raising the exception
            # regardless of operation type
            try:
                await container.create_item({"id": str(uuid.uuid4()), "pk": str(uuid.uuid4())})
                pytest.fail("Exception was not raised.")
            except ServiceRequestError:
                assert connection_retry_policy.counter == 3

            try:
                await container.read_item("some_id", "some_pk")
                pytest.fail("Exception was not raised.")
            except ServiceRequestError:
                assert connection_retry_policy.counter == 3

    async def test_service_response_connection_retry_policy_async(self):
        # Mock the client retry policy to see the same-region retries that happen there
        exception = ServiceResponseError("mock exception")
        exception.exc_type = Exception
        connection_policy = self.connectionPolicy
        connection_retry_policy = test_config.MockConnectionRetryPolicyAsync(resource_type="docs", error=exception)
        connection_policy.ConnectionRetryConfiguration = connection_retry_policy
        async with CosmosClient(self.host, self.masterKey, connection_policy=connection_policy) as mock_client:
            db = mock_client.get_database_client(self.TEST_DATABASE_ID)
            container = db.get_container_client(self.TEST_CONTAINER_ID)

            # We retry ServiceResponseExceptions 3 times in the to the same endpoint before raising the exception
            # for read operations, but 0 times for write requests
            try:
                await container.create_item({"id": str(uuid.uuid4()), "pk": str(uuid.uuid4())})
                pytest.fail("Exception was not raised.")
            except ServiceResponseError:
                assert connection_retry_policy.counter == 0

            try:
                await container.read_item("some_id", "some_pk")
                pytest.fail("Exception was not raised.")
            except ServiceResponseError:
                assert connection_retry_policy.counter == 3

    async def test_service_response_errors_async(self):
        # Test for errors that are subclasses of ClientConnectionError for write requests
        # Save the original ExecuteAsyncFunction function
        self.original_execute_function = _retry_utility_async.ExecuteFunctionAsync
        async with CosmosClient(self.host, self.masterKey) as mock_client:
            db = mock_client.get_database_client(self.TEST_DATABASE_ID)
            container = db.get_container_client(self.TEST_CONTAINER_ID)
            await container.read()

            original_location_cache = mock_client.client_connection._global_endpoint_manager.location_cache
            original_location_cache.account_read_locations = [self.REGION1, self.REGION2, self.REGION3]
            original_location_cache.available_read_regional_endpoints_by_locations = {
                self.REGION1: self.REGIONAL_ENDPOINT,
                self.REGION2: self.REGIONAL_ENDPOINT,
                self.REGION3: self.REGIONAL_ENDPOINT}
            original_location_cache.read_regional_routing_contexts = [self.REGIONAL_ENDPOINT, self.REGIONAL_ENDPOINT,
                                                                      self.REGIONAL_ENDPOINT]
            original_location_cache.account_write_locations = [self.REGION1, self.REGION2]
            original_location_cache.write_regional_routing_contexts = [self.REGIONAL_ENDPOINT, self.REGIONAL_ENDPOINT]
            original_location_cache.available_write_regional_endpoints_by_locations = {
                self.REGION1: self.REGIONAL_ENDPOINT,
                self.REGION2: self.REGIONAL_ENDPOINT}
            try:
                # Start with a normal ServiceResponseException with no special casing
                mf = self.MockExecuteServiceResponseException(AttributeError, AttributeError())
                _retry_utility_async.ExecuteFunctionAsync = mf
                # Even though we have 2 preferred write endpoints,
                # we will only run the exception once due to no retries on write requests
                await container.create_item({"id": str(uuid.uuid4()), "pk": str(uuid.uuid4())})
                pytest.fail("Exception was not raised.")
            except ServiceResponseError:
                assert mf.counter == 1
            finally:
                _retry_utility_async.ExecuteFunctionAsync = self.original_execute_function

            # Now we test the base ClientConnectionError to see in-region retry
            try:
                # Reset the function to reset the counter
                mf = self.MockExecuteServiceResponseException(ClientConnectionError, ClientConnectionError())
                _retry_utility_async.ExecuteFunctionAsync = mf
                await container.create_item({"id": str(uuid.uuid4()), "pk": str(uuid.uuid4())})
                pytest.fail("Exception was not raised.")
            except ServiceResponseError:
                assert mf.counter == 2
                assert len(original_location_cache.location_unavailability_info_by_endpoint) == 1
                host_unavailable = original_location_cache.location_unavailability_info_by_endpoint.get(self.host)
                assert host_unavailable is not None
                assert len(host_unavailable.get('operationType')) == 1
                assert 'Write' in host_unavailable.get('operationType')
            finally:
                _retry_utility_async.ExecuteFunctionAsync = self.original_execute_function

            await container.read()
            # We send another request to the same error - since we marked one of the two in-region endpoints unavailable we don't retry
            try:
                # Reset the function to reset the counter
                mf = self.MockExecuteServiceResponseException(ClientConnectionError, ClientConnectionError())
                _retry_utility_async.ExecuteFunctionAsync = mf
                await container.create_item({"id": str(uuid.uuid4()), "pk": str(uuid.uuid4())})
                pytest.fail("Exception was not raised.")
            except ServiceResponseError:
                assert mf.counter == 1
                host_unavailable = original_location_cache.location_unavailability_info_by_endpoint.get(self.host)
                assert host_unavailable is not None
                assert len(host_unavailable.get('operationType')) == 1
                assert 'Write' in host_unavailable.get('operationType')
            finally:
                _retry_utility_async.ExecuteFunctionAsync = self.original_execute_function

            # Reset the location cache's unavailable endpoints in order to try the same with other exceptions
            original_location_cache.location_unavailability_info_by_endpoint = {}
            original_location_cache.write_regional_routing_contexts = [self.REGIONAL_ENDPOINT, self.REGIONAL_ENDPOINT]

            # Now we test ClientConnectionResetError, the subclass of ClientConnectionError
            try:
                # Reset the function to reset the counter
                mf = self.MockExecuteServiceResponseException(ClientConnectionResetError, ClientConnectionResetError())
                _retry_utility_async.ExecuteFunctionAsync = mf
                await container.create_item({"id": str(uuid.uuid4()), "pk": str(uuid.uuid4())})
                pytest.fail("Exception was not raised.")
            except ServiceResponseError:
                assert mf.counter == 2
                assert len(original_location_cache.location_unavailability_info_by_endpoint) == 1
                host_unavailable = original_location_cache.location_unavailability_info_by_endpoint.get(self.host)
                assert host_unavailable is not None
                assert len(host_unavailable.get('operationType')) == 1
                assert 'Write' in host_unavailable.get('operationType')
            finally:
                _retry_utility_async.ExecuteFunctionAsync = self.original_execute_function

            # Reset the location cache's unavailable endpoints in order to try the same with other exceptions
            original_location_cache.location_unavailability_info_by_endpoint = {}
            original_location_cache.write_regional_routing_contexts = [self.REGIONAL_ENDPOINT, self.REGIONAL_ENDPOINT]

            # Now we test ServerConnectionError, the subclass of ClientConnectionError
            try:
                # Reset the function to reset the counter
                mf = self.MockExecuteServiceResponseException(ServerConnectionError, ServerConnectionError())
                _retry_utility_async.ExecuteFunctionAsync = mf
                await container.create_item({"id": str(uuid.uuid4()), "pk": str(uuid.uuid4())})
                pytest.fail("Exception was not raised.")
            except ServiceResponseError:
                assert mf.counter == 2
            finally:
                _retry_utility_async.ExecuteFunctionAsync = self.original_execute_function

            # Reset the location cache's unavailable endpoints in order to try the same with other exceptions
            original_location_cache.location_unavailability_info_by_endpoint = {}
            original_location_cache.write_regional_routing_contexts = [self.REGIONAL_ENDPOINT, self.REGIONAL_ENDPOINT]

            # Now we test ClientOSError, the subclass of ClientConnectionError
            try:
                # Reset the function to reset the counter
                mf = self.MockExecuteServiceResponseException(ClientOSError, ClientOSError())
                _retry_utility_async.ExecuteFunctionAsync = mf
                await container.create_item({"id": str(uuid.uuid4()), "pk": str(uuid.uuid4())})
                pytest.fail("Exception was not raised.")
            except ServiceResponseError:
                assert mf.counter == 2
            finally:
                _retry_utility_async.ExecuteFunctionAsync = self.original_execute_function

    async def test_global_endpoint_manager_retry_async(self):
        # For this test we mock both the ConnectionRetryPolicy and the GetDatabaseAccountStub
        # - ConnectionRetryPolicy allows us to raise Service exceptions only for chosen requests and track endpoints used
        # - GetDatabaseAccountStub allows us to receive any number of endpoints for that call independent of account used
        exception = ServiceRequestError("mock exception")
        exception.exc_type = Exception
        self.original_get_database_account_stub = _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub
        _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub = self.MockGetDatabaseAccountStub
        connection_policy = self.connectionPolicy
        connection_retry_policy = test_config.MockConnectionRetryPolicyAsync(resource_type="docs", error=exception)
        connection_policy.ConnectionRetryConfiguration = connection_retry_policy
        async with CosmosClient(self.host, self.masterKey, connection_policy=connection_policy,
                                preferred_locations=[self.REGION1, self.REGION2]) as mock_client:
            db = mock_client.get_database_client(self.TEST_DATABASE_ID)
            container = db.get_container_client(self.TEST_CONTAINER_ID)

            try:
                await container.create_item({"id": str(uuid.uuid4()), "pk": str(uuid.uuid4())})
                pytest.fail("Exception was not raised.")
            except ServiceRequestError:
                assert connection_retry_policy.counter == 3
                # 4 total requests for each in-region (hub -> write locational endpoint)
                assert len(connection_retry_policy.request_endpoints) == 8
            except CosmosHttpResponseError as e:
                print(e)
            finally:
                _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub = self.original_get_database_account_stub

            # Now we try with a read request - reset the policy to reset the counter
            _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub = self.MockGetDatabaseAccountStub
            connection_retry_policy.request_endpoints = []
            try:
                await container.read_item("some_id", "some_pk")
                pytest.fail("Exception was not raised.")
            except ServiceRequestError:
                assert connection_retry_policy.counter == 3
                # 4 total requests in each main region (preferred read region 1 -> preferred read region 2)
                assert len(connection_retry_policy.request_endpoints) == 8
            finally:
                _global_endpoint_manager_async._GlobalEndpointManager._GetDatabaseAccountStub = self.original_get_database_account_stub

    class MockExecuteServiceRequestException(object):
        def __init__(self):
            self.counter = 0

        def __call__(self, func, *args, **kwargs):
            self.counter = self.counter + 1
            exception = ServiceRequestError("mock exception")
            exception.exc_type = Exception
            raise exception

    class MockExecuteServiceResponseException(object):
        def __init__(self, err_type, inner_exception):
            self.err_type = err_type
            self.inner_exception = inner_exception
            self.counter = 0

        def __call__(self, func, *args, **kwargs):
            self.counter = self.counter + 1
            exception = ServiceResponseError("mock exception")
            exception.exc_type = self.err_type
            exception.inner_exception = self.inner_exception
            raise exception

    async def MockGetDatabaseAccountStub(self, endpoint):
        read_regions = ["West US", "East US"]
        read_locations = []
        for loc in read_regions:
            read_locations.append({'databaseAccountEndpoint': endpoint, 'name': loc})
        write_regions = ["West US"]
        write_locations = []
        for loc in write_regions:

            locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(endpoint, loc)
            write_locations.append({'databaseAccountEndpoint': locational_endpoint, 'name': loc})
        multi_write = False

        db_acc = DatabaseAccount()
        db_acc.DatabasesLink = "/dbs/"
        db_acc.MediaLink = "/media/"
        db_acc._ReadableLocations = read_locations
        db_acc._WritableLocations = write_locations
        db_acc._EnableMultipleWritableLocations = multi_write
        db_acc.ConsistencyPolicy = {"defaultConsistencyLevel": "Session"}
        return db_acc
