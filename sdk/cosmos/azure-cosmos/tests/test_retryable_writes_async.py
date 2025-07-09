# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation. All rights reserved.

import pytest
import unittest
import uuid
from azure.cosmos.aio import CosmosClient, _retry_utility_async
from azure.cosmos import exceptions, documents
from azure.cosmos.partition_key import PartitionKey
import test_config  # Import test_config for configuration details


class TestRetryableWritesAsync(unittest.IsolatedAsyncioTestCase):
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_SINGLE_PARTITION_ID = "test-retryable_writes-container-" + str(uuid.uuid4())
    TEST_CONTAINER_MULTI_PARTITION_ID = "test-retryable_writes-multi-partition-container-" + str(uuid.uuid4())
    client: CosmosClient = None

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

    @classmethod
    async def asyncSetUp(self):
        self.client = CosmosClient(self.host, credential=self.masterKey)
        self.client.__aenter__()  # Ensure the client is properly initialized
        self.database = await self.client.create_database_if_not_exists(id=self.TEST_DATABASE_ID)
        self.container = await self.database.create_container_if_not_exists(
            id=self.TEST_CONTAINER_SINGLE_PARTITION_ID,
            partition_key=PartitionKey(path="/partitionKey", kind="Hash")
        )
        self.container_hpk = await self.database.create_container_if_not_exists(
            id=self.TEST_CONTAINER_MULTI_PARTITION_ID,
            partition_key=PartitionKey(path=["/state", "/city"], kind="MultiHash")
        )

    @classmethod
    async def asyncTearDown(self):
        await self.database.delete_container(self.TEST_CONTAINER_SINGLE_PARTITION_ID)
        await self.database.delete_container(self.TEST_CONTAINER_MULTI_PARTITION_ID)
        await self.client.close()

    async def test_retryable_writes(self):
        container = self.container

        # Mock retry_utility.execute to track retries
        original_execute = _retry_utility_async.ExecuteFunctionAsync
        me = self.MockExecuteFunction(original_execute)
        _retry_utility_async.ExecuteFunctionAsync = me

        # Test without retry_write for upsert_item
        test_item = {"id": "1", "partitionKey": "test", "data": "retryable write test"}
        try:
            await container.upsert_item(test_item)
            pytest.fail("Expected an exception without retry_write")
        except exceptions.CosmosHttpResponseError:
            assert me.counter == 1, "Expected no retries without retry_write"

        # Test with retry_write for upsert_item
        me.counter = 0  # Reset counter
        try:
            await container.upsert_item(test_item, retry_write=True)
        except exceptions.CosmosHttpResponseError as e:
            assert me.counter > 1, "Expected multiple retries due to simulated errors"
        finally:
            # Restore the original retry_utility.execute function
            _retry_utility_async.ExecuteFunctionAsync = original_execute

        # Verify the item was written
        read_item = await container.read_item(item=test_item['id'], partition_key=test_item['partitionKey'])
        assert read_item['id'] == test_item['id'], "Item was not written successfully after retries"

        # Mock retry_utility.execute to track retries
        original_execute = _retry_utility_async.ExecuteFunctionAsync
        me = self.MockExecuteFunction(original_execute)
        _retry_utility_async.ExecuteFunctionAsync = me

        # Test without retry_write for create_item
        test_item_create = {"id": "2", "partitionKey": "test", "data": "retryable create test"}
        try:
            await container.create_item(test_item_create)
            pytest.fail("Expected an exception without retry_write")
        except exceptions.CosmosHttpResponseError:
            assert me.counter == 1, "Expected no retries without retry_write"

        # Test with retry_write for create_item
        me.counter = 0  # Reset counter
        try:
            await container.create_item(test_item_create, retry_write=True)
        except exceptions.CosmosHttpResponseError as e:
            assert me.counter > 1, "Expected multiple retries due to simulated errors"
        finally:
            # Restore the original retry_utility.execute function
            _retry_utility_async.ExecuteFunctionAsync = original_execute

        # Verify the item was created
        read_item_create = await container.read_item(item=test_item_create['id'],
                                                     partition_key=test_item_create['partitionKey'])
        assert read_item_create['id'] == test_item_create['id'], "Item was not created successfully after retries"

    async def test_retryable_writes_hpk(self):
        """Test retryable writes for a container with hierarchical partition keys."""
        container = self.container_hpk

        # Mock retry_utility.execute to track retries
        original_execute = _retry_utility_async.ExecuteFunctionAsync
        me = self.MockExecuteFunction(original_execute)
        _retry_utility_async.ExecuteFunctionAsync = me

        # Test without retry_write for upsert_item
        test_item = {"id": "1", "state": "CA", "city": "San Francisco", "data": "retryable write test"}
        try:
            await container.upsert_item(test_item)
            pytest.fail("Expected an exception without retry_write")
        except exceptions.CosmosHttpResponseError:
            assert me.counter == 1, "Expected no retries without retry_write"

        # Test with retry_write for upsert_item
        me.counter = 0  # Reset counter
        try:
            await container.upsert_item(test_item, retry_write=True)
        except exceptions.CosmosHttpResponseError as e:
            assert me.counter > 1, "Expected multiple retries due to simulated errors"
        finally:
            # Restore the original retry_utility.execute function
            _retry_utility_async.ExecuteFunctionAsync = original_execute

        # Verify the item was written
        read_item = await container.read_item(item=test_item['id'], partition_key=[test_item['state'], test_item['city']])
        assert read_item['id'] == test_item['id'], "Item was not written successfully after retries"

        # Mock retry_utility.execute to track retries
        original_execute = _retry_utility_async.ExecuteFunctionAsync
        me = self.MockExecuteFunction(original_execute)
        _retry_utility_async.ExecuteFunctionAsync = me

        # Test without retry_write for create_item
        test_item_create = {"id": "2", "state": "NY", "city": "New York", "data": "retryable create test"}
        try:
            await container.create_item(test_item_create)
            pytest.fail("Expected an exception without retry_write")
        except exceptions.CosmosHttpResponseError:
            assert me.counter == 1, "Expected no retries without retry_write"

        # Test with retry_write for create_item
        me.counter = 0  # Reset counter
        try:
            await container.create_item(test_item_create, retry_write=True)
        except exceptions.CosmosHttpResponseError as e:
            assert me.counter > 1, "Expected multiple retries due to simulated errors"
        finally:
            # Restore the original retry_utility.execute function
            _retry_utility_async.ExecuteFunctionAsync = original_execute

        # Verify the item was created
        read_item_create = await container.read_item(item=test_item_create['id'],
                                                     partition_key=[test_item_create['state'], test_item_create['city']])
        assert read_item_create['id'] == test_item_create['id'], "Item was not created successfully after retries"

    class MockExecuteFunction(object):
        def __init__(self, org_func):
            self.org_func = org_func
            self.counter = 0

        async def __call__(self, func, *args, **kwargs):
            self.counter = self.counter + 1
            if self.counter < 2:
                # Simulate a retryable error on the second call
                raise exceptions.CosmosHttpResponseError(
                    status_code=408,
                    message="Simulated timeout error."
                )
            else:
                return await self.org_func(func, *args, **kwargs)