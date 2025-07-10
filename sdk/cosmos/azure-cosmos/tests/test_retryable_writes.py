# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import pytest
import unittest
import uuid
from azure.cosmos import CosmosClient, exceptions, documents, _retry_utility
from azure.cosmos.partition_key import PartitionKey
import test_config  # Import test_config for configuration details

@pytest.mark.cosmosEmulator
class TestRetryableWrites(unittest.TestCase):
    url = test_config.TestConfig.host
    key = test_config.TestConfig.masterKey
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_SINGLE_PARTITION_ID = "test-retryable_writes-container-" + str(uuid.uuid4())
    TEST_CONTAINER_MULTI_PARTITION_ID = "test-retryable_writes-multi-partition-container-" + str(uuid.uuid4())
    client: CosmosClient = None

    @classmethod
    def setUpClass(cls):
        cls.client = CosmosClient(cls.url, credential=cls.key)
        cls.database = cls.client.create_database_if_not_exists(id=cls.TEST_DATABASE_ID)
        cls.container = cls.database.create_container_if_not_exists(
            id=cls.TEST_CONTAINER_SINGLE_PARTITION_ID,
            partition_key=PartitionKey(path="/partitionKey", kind="Hash")
        )
        cls.container_hpk = cls.database.create_container_if_not_exists(
            id=cls.TEST_CONTAINER_MULTI_PARTITION_ID,
            partition_key=PartitionKey(path=["/state", "/city"], kind="MultiHash")
        )

    @classmethod
    def tearDownClass(cls):
        # Clean up the created containers
        cls.database.delete_container(cls.TEST_CONTAINER_SINGLE_PARTITION_ID)
        cls.database.delete_container(cls.TEST_CONTAINER_MULTI_PARTITION_ID)

    def test_retryable_writes(self):
        # Create a container for testing
        container = self.container

        # Mock retry_utility.execute to track retries
        original_execute = _retry_utility.ExecuteFunction
        me = self.MockExecuteFunction(original_execute)
        _retry_utility.ExecuteFunction = me

        # Test without retry_write for upsert_item
        test_item = {"id": "1", "partitionKey": "test", "data": "retryable write test"}
        try:
            container.upsert_item(test_item)
            pytest.fail("Expected an exception without retry_write")
        except exceptions.CosmosHttpResponseError:
            assert me.counter == 1, "Expected no retries without retry_write"

        # Test with retry_write for upsert_item
        me.counter = 0  # Reset counter
        try:
            container.upsert_item(test_item, retry_write=True)
        except exceptions.CosmosHttpResponseError as e:
            assert me.counter > 1, "Expected multiple retries due to simulated errors"
        finally:
            # Restore the original retry_utility.execute function
            _retry_utility.ExecuteFunction = original_execute

        # Verify the item was written
        read_item = container.read_item(item=test_item['id'], partition_key=test_item['partitionKey'])
        assert read_item['id'] == test_item['id'], "Item was not written successfully after retries"

        # Mock retry_utility.execute to track retries
        original_execute = _retry_utility.ExecuteFunction
        me = self.MockExecuteFunction(original_execute)
        _retry_utility.ExecuteFunction = me

        # Test without retry_write for create_item
        test_item_create = {"id": "2", "partitionKey": "test", "data": "retryable create test"}
        me.counter = 0  # Reset counter
        try:
            container.create_item(test_item_create)
            pytest.fail("Expected an exception without retry_write")
        except exceptions.CosmosHttpResponseError:
            assert me.counter == 1, "Expected no retries without retry_write"

        # Test with retry_write for create_item
        me.counter = 0  # Reset counter
        try:
            container.create_item(test_item_create, retry_write=True)
        except exceptions.CosmosHttpResponseError as e:
            assert me.counter > 1, "Expected multiple retries due to simulated errors"
        finally:
            # Restore the original retry_utility.execute function
            _retry_utility.ExecuteFunction = original_execute

        # Verify the item was created
        read_item_create = container.read_item(item=test_item_create['id'],
                                               partition_key=test_item_create['partitionKey'])
        assert read_item_create['id'] == test_item_create['id'], "Item was not created successfully after retries"

        # Mock retry_utility.execute to track retries
        original_execute = _retry_utility.ExecuteFunction
        me = self.MockExecuteFunction(original_execute)
        _retry_utility.ExecuteFunction = me
        # Test without retry_write for patch_item
        test_patch_operations = [
            {"op": "add", "path": "/data", "value": "patched retryable write test"}
        ]
        try:
            container.patch_item(item=test_item['id'], partition_key=test_item['partitionKey'],
                                 patch_operations=test_patch_operations)
            pytest.fail("Expected an exception without retry_write")
        except exceptions.CosmosHttpResponseError:
            assert me.counter == 1, "Expected no retries without retry_write"

        # Test with retry_write for patch_item
        me.counter = 0  # Reset counter
        try:
            container.patch_item(item=test_item['id'], partition_key=test_item['partitionKey'],
                                 patch_operations=test_patch_operations, retry_write=True)
        except exceptions.CosmosHttpResponseError as e:
            assert me.counter > 1, "Expected multiple retries due to simulated errors"
        finally:
            # Restore the original retry_utility.execute function
            _retry_utility.ExecuteFunction = original_execute

        # Verify the item was patched
        patched_item = container.read_item(item=test_item['id'], partition_key=test_item['partitionKey'])
        assert patched_item['data'] == "patched retryable write test", "Item was not patched successfully after retries"

    def test_retryable_writes_client_retry_write(self):
        """Test retryable writes for a container with retry_write set at the client level."""
        # Create a client with retry_write enabled
        client_with_retry = CosmosClient(self.url, credential=self.key, retry_write=True)
        container = client_with_retry.get_database_client(self.TEST_DATABASE_ID).get_container_client(self.container.id)

        # Mock retry_utility.execute to track retries
        original_execute = _retry_utility.ExecuteFunction
        me = self.MockExecuteFunction(original_execute)
        _retry_utility.ExecuteFunction = me

        # Test upsert_item
        test_item = {"id": "4", "partitionKey": "test", "data": "retryable write test"}
        try:
            container.upsert_item(test_item)
        except exceptions.CosmosHttpResponseError as e:
            assert me.counter > 1, "Expected multiple retries due to simulated errors"
        finally:
            # Restore the original retry_utility.execute function
            _retry_utility.ExecuteFunction = original_execute

        # Test create_item
        me.counter = 0  # Reset counter
        test_item_create = {"id": "5", "partitionKey": "test", "data": "retryable create test"}
        try:
            container.create_item(test_item_create)
        except exceptions.CosmosHttpResponseError as e:
            assert me.counter > 1, "Expected multiple retries due to simulated errors"
        finally:
            # Restore the original retry_utility.execute function
            _retry_utility.ExecuteFunction = original_execute

    def test_retryable_writes_hpk(self):
        """Test retryable writes for a container with hierarchical partition keys."""
        container = self.container_hpk

        # Mock retry_utility.execute to track retries
        original_execute = _retry_utility.ExecuteFunction
        me = self.MockExecuteFunction(original_execute)
        _retry_utility.ExecuteFunction = me

        # Test without retry_write for upsert_item
        test_item = {"id": "1", "state": "CA", "city": "San Francisco", "data": "retryable write test"}
        try:
            container.upsert_item(test_item)
            pytest.fail("Expected an exception without retry_write")
        except exceptions.CosmosHttpResponseError:
            assert me.counter == 1, "Expected no retries without retry_write"

        # Test with retry_write for upsert_item
        me.counter = 0  # Reset counter
        try:
            container.upsert_item(test_item, retry_write=True)
        except exceptions.CosmosHttpResponseError as e:
            assert me.counter > 1, "Expected multiple retries due to simulated errors"
        finally:
            # Restore the original retry_utility.execute function
            _retry_utility.ExecuteFunction = original_execute

        # Verify the item was written
        read_item = container.read_item(item=test_item['id'], partition_key=[test_item['state'], test_item['city']])
        assert read_item['id'] == test_item['id'], "Item was not written successfully after retries"

        # Mock retry_utility.execute to track retries
        original_execute = _retry_utility.ExecuteFunction
        me = self.MockExecuteFunction(original_execute)
        _retry_utility.ExecuteFunction = me

        # Test without retry_write for create_item
        test_item_create = {"id": "2", "state": "NY", "city": "New York", "data": "retryable create test"}
        try:
            container.create_item(test_item_create)
            pytest.fail("Expected an exception without retry_write")
        except exceptions.CosmosHttpResponseError:
            assert me.counter == 1, "Expected no retries without retry_write"

        # Test with retry_write for create_item
        me.counter = 0  # Reset counter
        try:
            container.create_item(test_item_create, retry_write=True)
        except exceptions.CosmosHttpResponseError as e:
            assert me.counter > 1, "Expected multiple retries due to simulated errors"
        finally:
            # Restore the original retry_utility.execute function
            _retry_utility.ExecuteFunction = original_execute

        # Verify the item was created
        read_item_create = container.read_item(item=test_item_create['id'],
                                               partition_key=[test_item_create['state'], test_item_create['city']])
        assert read_item_create['id'] == test_item_create['id'], "Item was not created successfully after retries"

        # Mock retry_utility.execute to track retries
        original_execute = _retry_utility.ExecuteFunction
        me = self.MockExecuteFunction(original_execute)
        _retry_utility.ExecuteFunction = me

        # Test without retry_write for patch_item
        test_patch_operations_hpk = [
            {"op": "add", "path": "/data", "value": "patched retryable write test"}
        ]
        try:
            container.patch_item(item=test_item['id'], partition_key=[test_item['state'], test_item['city']],
                                 patch_operations=test_patch_operations_hpk)
            pytest.fail("Expected an exception without retry_write")
        except exceptions.CosmosHttpResponseError:
            assert me.counter == 1, "Expected no retries without retry_write"

        # Test with retry_write for patch_item
        me.counter = 0  # Reset counter
        try:
            container.patch_item(item=test_item['id'], partition_key=[test_item['state'], test_item['city']],
                                 patch_operations=test_patch_operations_hpk, retry_write=True)
        except exceptions.CosmosHttpResponseError as e:
            assert me.counter > 1, "Expected multiple retries due to simulated errors"
        finally:
            # Restore the original retry_utility.execute function
            _retry_utility.ExecuteFunction = original_execute

        # Verify the item was patched
        patched_item_hpk = container.read_item(item=test_item['id'],
                                               partition_key=[test_item['state'], test_item['city']])
        assert patched_item_hpk[
                   'data'] == "patched retryable write test", "Item was not patched successfully after retries"

    def test_retryable_writes_hpk_client_retry_write(self):
        """Test retryable writes for a container with hierarchical partition keys and
        retry_write set at the client level."""
        # Create a client with retry_write enabled
        client_with_retry = CosmosClient(self.url, credential=self.key, retry_write=True)
        container = client_with_retry.get_database_client(self.TEST_DATABASE_ID).get_container_client(
            self.container_hpk.id)

        # Mock retry_utility.execute to track retries
        original_execute = _retry_utility.ExecuteFunction
        me = self.MockExecuteFunction(original_execute)
        _retry_utility.ExecuteFunction = me

        # Test upsert_item
        test_item = {"id": "6", "state": "CA", "city": "San Francisco", "data": "retryable write test"}
        try:
            container.upsert_item(test_item)
        except exceptions.CosmosHttpResponseError as e:
            assert me.counter > 1, "Expected multiple retries due to simulated errors"
        finally:
            # Restore the original retry_utility.execute function
            _retry_utility.ExecuteFunction = original_execute

        # Test create_item
        me.counter = 0  # Reset counter
        test_item_create = {"id": "7", "state": "NY", "city": "New York", "data": "retryable create test"}
        try:
            container.create_item(test_item_create)
        except exceptions.CosmosHttpResponseError as e:
            assert me.counter > 1, "Expected multiple retries due to simulated errors"
        finally:
            # Restore the original retry_utility.execute function
            _retry_utility.ExecuteFunction = original_execute

    class MockExecuteFunction(object):
        def __init__(self, org_func):
            self.org_func = org_func
            self.counter = 0

        def __call__(self, func, *args, **kwargs):
            self.counter = self.counter + 1
            if self.counter < 2:
                # Simulate a retryable error on the second call
                raise exceptions.CosmosHttpResponseError(
                    status_code=408,
                    message="Simulated timeout error."
                )
            else:
                return self.org_func(func, *args, **kwargs)

