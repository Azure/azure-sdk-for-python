# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid

import pytest
import pytest_asyncio

import azure.cosmos.exceptions as exceptions
import test_config
from azure.cosmos import PartitionKey
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

    client = CosmosClient(TestTimeoutRetryPolicyAsync.host, TestTimeoutRetryPolicyAsync.masterKey, consistency_level="Session",
                          connection_policy=TestTimeoutRetryPolicyAsync.connectionPolicy)
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
            mf = self.MockExecuteFunction(self.original_execute_function, 5, error_code)
            _retry_utility_async.ExecuteFunctionAsync = mf
            await setup[COLLECTION].read_item(item=created_document['id'],
                                              partition_key=created_document['pk'])
            pytest.fail("Exception was not raised.")
        except exceptions.CosmosHttpResponseError as err:
            assert err.status_code == error_code
        finally:
            _retry_utility_async.ExecuteFunctionAsync = self.original_execute_function

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

        def __call__(self, func, global_endpoint_manager, *args, **kwargs):
            if self.counter != 0 and self.counter >= self.num_exceptions:
                return self.org_func(func, global_endpoint_manager, *args, **kwargs)
            else:
                self.counter += 1
                raise exceptions.CosmosHttpResponseError(
                    status_code=self.status_code,
                    message="Some Exception",
                    response=test_config.FakeResponse({}))



if __name__ == '__main__':
    unittest.main()
