# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid

import pytest
import pytest_asyncio

import azure.cosmos.exceptions as exceptions
import test_config
from azure.cosmos import PartitionKey
from azure.cosmos._location_cache import RegionalRoutingContext, EndpointOperationType
from azure.cosmos.aio import CosmosClient, _retry_utility_async

COLLECTION = "created_collection"
@pytest_asyncio.fixture()
async def setup():
    if (TestTimeoutRetryPolicyAsync.masterKey == '[YOUR_KEY_HERE]' or
            TestTimeoutRetryPolicyAsync.host == '[YOUR_ENDPOINT_HERE]'):
        raise Exception(
            "You must specify your Azure Cosmos account values for "
            "'masterKey' and 'host' at the top of this class to run the "
            "tests.")

    client = CosmosClient(TestTimeoutRetryPolicyAsync.host, TestTimeoutRetryPolicyAsync.masterKey, consistency_level="Session")
    created_database = client.get_database_client(TestTimeoutRetryPolicyAsync.TEST_DATABASE_ID)
    created_collection = await created_database.create_container(TestTimeoutRetryPolicyAsync.TEST_CONTAINER_SINGLE_PARTITION_ID,
                                                                 partition_key=PartitionKey("/pk"))
    yield {
        COLLECTION: created_collection
    }

    await created_database.delete_container(TestTimeoutRetryPolicyAsync.TEST_CONTAINER_SINGLE_PARTITION_ID)
    await client.close()




def error_codes():
    return [408, 500, 502, 503]


@pytest.mark.cosmosEmulator
@pytest.mark.asyncio
@pytest.mark.usefixtures("setup")
class TestTimeoutRetryPolicyAsync:
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_SINGLE_PARTITION_ID = "test-timeout-retry-policy-container-" + str(uuid.uuid4())

    @pytest.mark.parametrize("error_code", error_codes())
    async def test_timeout_failover_retry_policy_for_read_success_async(self, setup, error_code):
        document_definition = {'id': 'failoverDoc-' + str(uuid.uuid4()),
                               'pk': 'pk',
                               'name': 'sample document',
                               'key': 'value'}

        created_document = await setup[COLLECTION].create_item(body=document_definition)
        self.original_execute_function = _retry_utility_async.ExecuteFunctionAsync
        try:
            # should retry once and then succeed
            mf = self.MockExecuteFunction(self.original_execute_function, 1, error_code)
            _retry_utility_async.ExecuteFunctionAsync = mf
            doc = await setup[COLLECTION].read_item(item=created_document['id'],
                                                    partition_key=created_document['pk'])
            assert doc == created_document
        finally:
            _retry_utility_async.ExecuteFunctionAsync = self.original_execute_function

    @pytest.mark.parametrize("error_code", error_codes())
    async def test_timeout_failover_retry_policy_for_read_failure_async(self, setup, error_code):
        document_definition = {'id': 'failoverDoc-' + str(uuid.uuid4()),
                               'pk': 'pk',
                               'name': 'sample document',
                               'key': 'value'}

        created_document = await setup[COLLECTION].create_item(body=document_definition)
        self.original_execute_function = _retry_utility_async.ExecuteFunctionAsync
        try:
            # should retry once and then succeed
            mf = self.MockExecuteFunction(self.original_execute_function, 2, error_code)
            _retry_utility_async.ExecuteFunctionAsync = mf
            await setup[COLLECTION].read_item(item=created_document['id'],
                                              partition_key=created_document['pk'])
            pytest.fail("Exception was not raised.")
        except exceptions.CosmosHttpResponseError as err:
            assert err.status_code == error_code
        finally:
            _retry_utility_async.ExecuteFunctionAsync = self.original_execute_function

    @pytest.mark.parametrize("error_code", error_codes())
    async def test_cross_region_retry_async(self, setup, error_code):
        mock_client = CosmosClient(self.host, self.masterKey)
        db = mock_client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(self.TEST_CONTAINER_SINGLE_PARTITION_ID)
        document_definition = {'id': 'failoverDoc' + str(uuid.uuid4()),
                               'pk': 'pk',
                               'name': 'sample document',
                               'key': 'value'}

        created_document = await container.create_item(body=document_definition)
        self.original_execute_function = _retry_utility_async.ExecuteFunctionAsync
        original_location_cache = mock_client.client_connection._global_endpoint_manager.location_cache
        fake_endpoint = "other-region"
        regional_routing_context = RegionalRoutingContext(self.host, self.host)
        regional_routing_context_2 = RegionalRoutingContext(fake_endpoint, fake_endpoint)
        region_1 = "East US"
        region_2 = "West US"
        original_location_cache.account_read_locations = [region_1, region_2]
        original_location_cache.account_read_regional_routing_contexts_by_location = {region_1: regional_routing_context,
                                                                                  region_2: regional_routing_context_2
                                                                                  }
        original_location_cache.read_regional_routing_contexts = [regional_routing_context, regional_routing_context_2]
        try:
            # should retry once and then succeed
            mf = self.MockExecuteFunctionCrossRegion(self.original_execute_function, error_code, fake_endpoint)
            _retry_utility_async.ExecuteFunctionAsync = mf
            await container.read_item(item=created_document['id'], partition_key=created_document['pk'])
        finally:
            _retry_utility_async.ExecuteFunctionAsync = self.original_execute_function
            await mock_client.close()

    @pytest.mark.parametrize("error_code", error_codes())
    async def test_timeout_failover_retry_policy_for_write_failure_async(self, setup, error_code):
        document_definition = {'id': 'failoverDoc' + str(uuid.uuid4()),
                               'pk': 'pk',
                               'name': 'sample document',
                               'key': 'value'}

        self.original_execute_function = _retry_utility_async.ExecuteFunctionAsync
        try:
            # timeouts should fail immediately for writes
            mf = self.MockExecuteFunction(self.original_execute_function,0, error_code)
            _retry_utility_async.ExecuteFunctionAsync = mf
            try:
                await setup[COLLECTION].create_item(body=document_definition)
                pytest.fail("Exception was not raised.")
            except exceptions.CosmosHttpResponseError as err:
                assert err.status_code == error_code
        finally:
            _retry_utility_async.ExecuteFunctionAsync = self.original_execute_function

    class MockExecuteFunction(object):
        def __init__(self, org_func, num_exceptions, status_code):
            self.org_func = org_func
            self.counter = 0
            self.num_exceptions = num_exceptions
            self.status_code = status_code

        async def __call__(self, func, global_endpoint_manager, *args, **kwargs):
            if self.counter != 0 and self.counter >= self.num_exceptions:
                return await self.org_func(func, global_endpoint_manager, *args, **kwargs)
            else:
                self.counter += 1
                raise exceptions.CosmosHttpResponseError(
                    status_code=self.status_code,
                    message="Some Exception",
                    response=test_config.FakeResponse({}))

    class MockExecuteFunctionCrossRegion(object):
        def __init__(self, org_func, status_code, location_endpoint_to_route):
            self.org_func = org_func
            self.counter = 0
            self.status_code = status_code
            self.location_endpoint_to_route = location_endpoint_to_route

        async def __call__(self, func, *args, **kwargs):
            if self.counter == 1:
                assert args[1].location_endpoint_to_route == self.location_endpoint_to_route
                args[1].location_endpoint_to_route = test_config.TestConfig.host
                return await self.org_func(func, *args, **kwargs)
            else:
                self.counter += 1
                raise exceptions.CosmosHttpResponseError(
                    status_code=self.status_code,
                    message="Some Exception",
                    response=test_config.FakeResponse({}))



if __name__ == '__main__':
    unittest.main()
