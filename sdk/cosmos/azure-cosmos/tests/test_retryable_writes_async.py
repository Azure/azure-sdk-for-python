# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation. All rights reserved.

import asyncio
import pytest
import uuid
from azure.core.exceptions import ServiceResponseError
from azure.core.rest import HttpRequest
from azure.cosmos.aio import CosmosClient, _retry_utility_async
from azure.cosmos import exceptions, ContainerProxy
from azure.cosmos.partition_key import PartitionKey
from _fault_injection_transport_async import FaultInjectionTransportAsync
from test_fault_injection_transport_async import TestFaultInjectionTransportAsync
from typing import Callable
import test_config  # Import test_config for configuration details

@pytest.mark.cosmosEmulator
class TestRetryableWritesAsync:
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
    async def asyncSetUp(cls):
        cls.client = CosmosClient(cls.host, credential=cls.masterKey)
        await cls.client.__aenter__()  # Ensure the client is properly initialized
        cls.database = await cls.client.create_database_if_not_exists(id=cls.TEST_DATABASE_ID)
        cls.container = await cls.database.create_container_if_not_exists(
            id=cls.TEST_CONTAINER_SINGLE_PARTITION_ID,
            partition_key=PartitionKey(path="/pk", kind="Hash")
        )
        cls.container_hpk = await cls.database.create_container_if_not_exists(
            id=cls.TEST_CONTAINER_MULTI_PARTITION_ID,
            partition_key=PartitionKey(path=["/state", "/city"], kind="MultiHash")
        )

    @classmethod
    async def asyncTearDown(cls):
        await cls.database.delete_container(cls.TEST_CONTAINER_SINGLE_PARTITION_ID)
        await cls.database.delete_container(cls.TEST_CONTAINER_MULTI_PARTITION_ID)
        await cls.client.close()

    async def test_retryable_writes_request_level_async(self):
        container = self.container

        # Mock retry_utility.execute to track retries
        original_execute = _retry_utility_async.ExecuteFunctionAsync
        me = self.MockExecuteFunction(original_execute)
        _retry_utility_async.ExecuteFunctionAsync = me

        # Test without retry_write for upsert_item
        test_item = {"id": "1", "pk": "test", "data": "retryable write test"}
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
        read_item = await container.read_item(item=test_item['id'], partition_key=test_item['pk'])
        assert read_item['id'] == test_item['id'], "Item was not written successfully after retries"

        # Mock retry_utility.execute to track retries
        original_execute = _retry_utility_async.ExecuteFunctionAsync
        me = self.MockExecuteFunction(original_execute)
        _retry_utility_async.ExecuteFunctionAsync = me

        # Test without retry_write for create_item
        test_item_create = {"id": "2", "pk": "test", "data": "retryable create test"}
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
                                                     partition_key=test_item_create['pk'])
        assert read_item_create['id'] == test_item_create['id'], "Item was not created successfully after retries"

        # Test without retry_write for patch_item
        test_item_patch = {"id": "3", "pk": "test", "data": "retryable patch test"}
        await container.create_item(test_item_patch)  # Create the item first

        # Mock retry_utility.execute to track retries
        original_execute = _retry_utility_async.ExecuteFunctionAsync
        me = self.MockExecuteFunction(original_execute)
        _retry_utility_async.ExecuteFunctionAsync = me

        try:
            await container.patch_item(item=test_item_patch['id'], partition_key=test_item_patch['pk'],
                                       patch_operations=[
                                           {"op": "replace", "path": "/data", "value": "patched data"}
                                       ])
            pytest.fail("Expected an exception without retry_write")
        except exceptions.CosmosHttpResponseError:
            assert me.counter == 1, "Expected no retries without retry_write"

        # Test with retry_write for patch_item
        me.counter = 0  # Reset counter
        try:
            await container.patch_item(item=test_item_patch['id'], partition_key=test_item_patch['pk'],
                                       patch_operations=[
                                           {"op": "replace", "path": "/data", "value": "patched data"}
                                       ], retry_write=True)
        except exceptions.CosmosHttpResponseError as e:
            assert me.counter > 1, "Expected multiple retries due to simulated errors"
        finally:
            # Restore the original retry_utility.execute function
            _retry_utility_async.ExecuteFunctionAsync = original_execute

        # Verify the item was patched
        read_item_patch = await container.read_item(item=test_item_patch['id'],
                                                    partition_key=test_item_patch['pk'])
        assert read_item_patch['data'] == "patched data", "Item was not patched successfully after retries"

        # Verify original execution function is used to upsert an item
        test_item = {"id": "5", "pk": "test", "data": "retryable write test"}
        await container.upsert_item(test_item)

        # Mock retry_utility.execute to track retries
        original_execute = _retry_utility_async.ExecuteFunctionAsync
        me = self.MockExecuteFunction(original_execute)
        _retry_utility_async.ExecuteFunctionAsync = me

        # Verify delete_item does not retry
        me.counter = 0  # Reset counter
        try:
            await container.delete_item(item=test_item['id'], partition_key=test_item['pk'])
            pytest.fail("Expected an exception without retry_write")
        except exceptions.CosmosHttpResponseError:
            assert me.counter == 1, "Expected no retries for delete_item"
        finally:
            # Restore the original retry_utility.execute function
            _retry_utility_async.ExecuteFunctionAsync = original_execute

        # Verify the item was not deleted
        read_item = await container.read_item(item=test_item['id'], partition_key=test_item['pk'])
        assert read_item['id'] == test_item['id'], "Item was unexpectedly deleted"

        # Mock retry_utility.execute to track retries
        original_execute = _retry_utility_async.ExecuteFunctionAsync
        me = self.MockExecuteFunction(original_execute)
        _retry_utility_async.ExecuteFunctionAsync = me

        me.counter = 0  # Reset counter
        try:
            await container.delete_item(item=test_item['id'], partition_key=test_item['pk'], retry_write=True)
        except exceptions.CosmosHttpResponseError:
            assert me.counter > 1, "Expected multiple retries due to simulated errors"
        finally:
            # Restore the original retry_utility.execute function
            _retry_utility_async.ExecuteFunctionAsync = original_execute

        try:
            await container.read_item(item=test_item['id'], partition_key=test_item['pk'])
            pytest.fail("Expected an exception for item that should have been deleted")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 404, "Expected item to be deleted but it was not"

    async def test_retryable_writes_client_level_write(self):
        """Test retryable writes for a container with retry_write set at the client level."""

        # Create a client with retry_write enabled
        client_with_retry = CosmosClient(self.host, credential=self.masterKey, retry_write=True)
        await client_with_retry.__aenter__()

        try:
            container = client_with_retry.get_database_client(self.TEST_DATABASE_ID).get_container_client(
                self.container.id)

            # Mock retry_utility.execute to track retries
            original_execute = _retry_utility_async.ExecuteFunctionAsync
            me = self.MockExecuteFunction(original_execute)
            _retry_utility_async.ExecuteFunctionAsync = me

            # Test upsert_item
            test_item = {"id": "4", "pk": "test", "data": "retryable write test"}
            try:
                await container.upsert_item(test_item)
            except exceptions.CosmosHttpResponseError as e:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"

            # Test create_item
            me.counter = 0  # Reset counter
            test_item_create = {"id": "5", "pk": "test", "data": "retryable create test"}
            try:
                await container.create_item(test_item_create)
            except exceptions.CosmosHttpResponseError as e:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"

            # Test patch_item
            me.counter = 0  # Reset counter
            test_patch_operations = [
                {"op": "add", "path": "/data", "value": "patched retryable write test"}
            ]
            try:
                await container.patch_item(item=test_item['id'], partition_key=test_item['pk'],
                                     patch_operations=test_patch_operations)
                pytest.fail("Expected an exception without retries")
            except exceptions.CosmosHttpResponseError:
                assert me.counter == 1, "Expected no retries for patch_item with client_retry_write"
            finally:
                # Restore the original retry_utility.execute function
                _retry_utility_async.ExecuteFunction = original_execute

            # Verify original execution function is used to upsert an item
            test_item = {"id": "4", "pk": "test", "data": "retryable write test"}
            await container.upsert_item(test_item)

            # Mock retry_utility.execute to track retries
            original_execute = _retry_utility_async.ExecuteFunctionAsync
            me = self.MockExecuteFunction(original_execute)
            _retry_utility_async.ExecuteFunction = me

            # Verify delete_item does not retry
            me.counter = 0  # Reset counter
            try:
                await container.delete_item(item=test_item['id'], partition_key=test_item['pk'])
            except exceptions.CosmosHttpResponseError:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"
            finally:
                # Restore the original retry_utility.execute function
                _retry_utility_async.ExecuteFunctionAsync = original_execute

            # Verify the item was deleted
            try:
                await container.read_item(item=test_item['id'], partition_key=test_item['pk'])
                pytest.fail("Expected an exception for item that should have been deleted")
            except exceptions.CosmosHttpResponseError as e:
                assert e.status_code == 404, "Expected item to be deleted but it was not"

            # Now we try it out with a write request with retry write enabled - which should retry once
            try:
                # Reset the function to reset the counter
                mf = self.MockExecuteServiceResponseException(AttributeError, None)
                _retry_utility_async.ExecuteFunctionAsync = mf
                await container.create_item({"id": str(uuid.uuid4()), "pk": str(uuid.uuid4())}, retry_write=True)
                pytest.fail("Exception was not raised.")
            except ServiceResponseError:
                assert mf.counter == 2
            finally:
                _retry_utility_async.ExecuteFunctionAsync = original_execute
        finally:
            if client_with_retry:
                await client_with_retry.close()

    async def test_retryable_writes_hpk_request_level_async(self):
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
        read_item = await container.read_item(item=test_item['id'], partition_key=[test_item['state'],
                                                                                   test_item['city']])
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
                                                     partition_key=[test_item_create['state'],
                                                                    test_item_create['city']])
        assert read_item_create['id'] == test_item_create['id'], "Item was not created successfully after retries"

        # Test without retry_write for patch_item
        test_item_patch_hpk = {"id": "3", "state": "TX", "city": "Austin", "data": "retryable patch test"}
        await container.create_item(test_item_patch_hpk)  # Create the item first

        # Mock retry_utility.execute to track retries
        original_execute = _retry_utility_async.ExecuteFunctionAsync
        me = self.MockExecuteFunction(original_execute)
        _retry_utility_async.ExecuteFunctionAsync = me

        try:
            await container.patch_item(item=test_item_patch_hpk['id'],
                                       partition_key=[test_item_patch_hpk['state'], test_item_patch_hpk['city']],
                                       patch_operations=[
                                           {"op": "replace", "path": "/data", "value": "patched data"}
                                       ])
            pytest.fail("Expected an exception without retry_write")
        except exceptions.CosmosHttpResponseError:
            assert me.counter == 1, "Expected no retries without retry_write"

        # Test with retry_write for patch_item
        me.counter = 0  # Reset counter
        try:
            await container.patch_item(item=test_item_patch_hpk['id'],
                                       partition_key=[test_item_patch_hpk['state'], test_item_patch_hpk['city']],
                                       patch_operations=[
                                           {"op": "replace", "path": "/data", "value": "patched data"}
                                       ], retry_write=True)
        except exceptions.CosmosHttpResponseError as e:
            assert me.counter > 1, "Expected multiple retries due to simulated errors"
        finally:
            # Restore the original retry_utility.execute function
            _retry_utility_async.ExecuteFunctionAsync = original_execute

        # Verify the item was patched
        read_item_patch_hpk = await container.read_item(item=test_item_patch_hpk['id'],
                                                        partition_key=[test_item_patch_hpk['state'],
                                                                       test_item_patch_hpk['city']])
        assert read_item_patch_hpk['data'] == "patched data", "Item was not patched successfully after retries"

        # Verify original execution function is used to upsert an item
        test_item = {"id": "1", "state": "CA", "city": "San Francisco", "data": "retryable write test"}
        await container.upsert_item(test_item)

        # Mock retry_utility.execute to track retries
        original_execute = _retry_utility_async.ExecuteFunctionAsync
        me = self.MockExecuteFunction(original_execute)
        _retry_utility_async.ExecuteFunctionAsync = me

        # Verify delete_item does not retry
        me.counter = 0  # Reset counter
        try:
            await container.delete_item(item=test_item['id'], partition_key=[test_item['state'], test_item['city']])
        except exceptions.CosmosHttpResponseError:
            assert me.counter == 1, "Expected no retries for delete_item"

        me.counter = 0  # Reset counter
        try:
            await container.delete_item(item=test_item['id'], partition_key=[test_item['state'], test_item['city']],
                                  retry_write=True)
        except exceptions.CosmosHttpResponseError:
            assert me.counter > 1, "Expected multiple retries due to simulated errors"
        finally:
            # Restore the original retry_utility.execute function
            _retry_utility_async.ExecuteFunctionAsync = original_execute

        # Verify the item was deleted
        try:
            await container.read_item(item=test_item['id'], partition_key=[test_item['state'], test_item['city']])
            pytest.fail("Expected an exception for item that should have been deleted")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 404, "Expected item to be deleted but it was not"

    async def test_retryable_writes_hpk_client_level_async(self):
        """Test retryable writes for a container with hierarchical partition keys and retry_write
        set at the client level."""
        # Create a client with retry_write enabled
        client_with_retry = CosmosClient(self.host, credential=self.masterKey, retry_write=True)
        await client_with_retry.__aenter__()
        try:
            container = client_with_retry.get_database_client(self.TEST_DATABASE_ID).get_container_client(
                self.container_hpk.id)

            # Mock retry_utility.execute to track retries
            original_execute = _retry_utility_async.ExecuteFunctionAsync
            me = self.MockExecuteFunction(original_execute)
            _retry_utility_async.ExecuteFunctionAsync = me

            # Test upsert_item
            test_item = {"id": "6", "state": "CA", "city": "San Francisco", "data": "retryable write test"}
            try:
                await container.upsert_item(test_item)
            except exceptions.CosmosHttpResponseError as e:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"

            # Test create_item
            me.counter = 0  # Reset counter
            test_item_create = {"id": "7", "state": "NY", "city": "New York", "data": "retryable create test"}
            try:
                await container.create_item(test_item_create)
            except exceptions.CosmosHttpResponseError as e:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"

            # Test patch_item
            me.counter = 0  # Reset counter
            test_patch_operations_hpk = [
                {"op": "add", "path": "/data", "value": "patched retryable write test"}
            ]
            try:
                await container.patch_item(item=test_item['id'], partition_key=[test_item['state'], test_item['city']],
                                     patch_operations=test_patch_operations_hpk)
                pytest.fail("Expected an exception without retries")
            except exceptions.CosmosHttpResponseError:
                assert me.counter == 1, "Expected no retries for patch_item with client_retry_write"
            finally:
                # Restore the original retry_utility.execute function
                _retry_utility_async.ExecuteFunction = original_execute

            test_item = {"id": "6", "state": "CA", "city": "San Francisco", "data": "retryable write test"}
            container.upsert_item(test_item)

            # Mock retry_utility.execute to track retries
            original_execute = _retry_utility_async.ExecuteFunctionAsync
            me = self.MockExecuteFunction(original_execute)
            _retry_utility_async.ExecuteFunctionAsync = me

            # Verify delete_item does not retry
            me.counter = 0  # Reset counter
            try:
                await container.delete_item(item=test_item['id'], partition_key=[test_item['state'], test_item['city']])
            except exceptions.CosmosHttpResponseError:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"
            finally:
                # Restore the original retry_utility.execute function
                _retry_utility_async.ExecuteFunctionAsync = original_execute

            # Verify the item was deleted
            try:
                await container.read_item(item=test_item['id'], partition_key=[test_item['state'], test_item['city']])
                pytest.fail("Expected an exception for item that should have been deleted")
            except exceptions.CosmosHttpResponseError as e:
                assert e.status_code == 404, "Expected item to be deleted but it was not"
        finally:
            await client_with_retry.close()

    @pytest.mark.parametrize("injected_error", [FaultInjectionTransportAsync.error_request_timeout(),
                             FaultInjectionTransportAsync.error_internal_server_error(),
                             FaultInjectionTransportAsync.error_service_response()])
    async def test_retryable_writes_mrw_request_level_async(self, injected_error):
        first_region_uri: str = test_config.TestConfig.local_host.replace("localhost", "127.0.0.1")
        second_region_uri: str = test_config.TestConfig.local_host
        custom_transport = FaultInjectionTransportAsync()

        # Inject topology transformation that would make Emulator look like a multiple write region account
        # account with two read regions
        is_get_account_predicate: Callable[[HttpRequest], bool] = lambda \
            r: FaultInjectionTransportAsync.predicate_is_database_account_call(r)
        emulator_as_multi_write_region_account_transformation = \
            lambda r, inner: FaultInjectionTransportAsync.transform_topology_mwr(
                first_region_name="First Region",
                second_region_name="Second Region",
                inner=inner)
        custom_transport.add_response_transformation(
            is_get_account_predicate,
            emulator_as_multi_write_region_account_transformation)

        # Inject rule to simulate regional outage in "First Region"
        is_request_to_first_region: Callable[[HttpRequest], bool] = lambda \
                r: FaultInjectionTransportAsync.predicate_targets_region(r, first_region_uri) and \
                   FaultInjectionTransportAsync.predicate_is_document_operation(r)

        custom_transport.add_fault(
            is_request_to_first_region,
            lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_region_down()))

        id_value: str = str(uuid.uuid4())
        document_definition = {'id': id_value,
                               'pk': id_value,
                               'name': 'sample document',
                               'key': 'value'}

        initialized_objects = await TestFaultInjectionTransportAsync.setup_method_with_custom_transport(
            custom_transport,
            preferred_locations=["First Region", "Second Region"],
            multiple_write_locations=True
        )
        try:
            container: ContainerProxy = initialized_objects["col"]

            create_document = await container.create_item(body=document_definition, retry_write=True)
            request = create_document.get_response_headers()["_request"]
            assert request.url.startswith(second_region_uri)

            upsert_document = await container.upsert_item(body=document_definition, retry_write=True)
            request = upsert_document.get_response_headers()["_request"]
            assert request.url.startswith(second_region_uri)

            replace_document = await container.replace_item(item=document_definition['id'], body=document_definition,
                                                      retry_write=True)
            request = replace_document.get_response_headers()["_request"]
            assert request.url.startswith(second_region_uri)

            operations = [{"op": "add", "path": "/favorite_color", "value": "red"}, ]
            patch_document = await container.patch_item(item=document_definition['id'],
                                                  partition_key=document_definition['pk'],
                                                  patch_operations=operations, retry_write=True)
            request = patch_document.get_response_headers()["_request"]
            assert request.url.startswith(second_region_uri)

        finally:
            await TestFaultInjectionTransportAsync.cleanup_method(initialized_objects)

    @pytest.mark.parametrize("injected_error", [FaultInjectionTransportAsync.error_request_timeout(),
                             FaultInjectionTransportAsync.error_internal_server_error(),
                             FaultInjectionTransportAsync.error_service_response()])
    async def test_retryable_writes_mrw_client_level_async(self, injected_error):
        first_region_uri: str = test_config.TestConfig.local_host.replace("localhost", "127.0.0.1")
        second_region_uri: str = test_config.TestConfig.local_host
        custom_transport = FaultInjectionTransportAsync()

        # Inject topology transformation that would make Emulator look like a multiple write region account
        is_get_account_predicate: Callable[[HttpRequest], bool] = lambda \
            r: FaultInjectionTransportAsync.predicate_is_database_account_call(r)
        emulator_as_multi_write_region_account_transformation = \
            lambda r, inner: FaultInjectionTransportAsync.transform_topology_mwr(
                first_region_name="First Region",
                second_region_name="Second Region",
                inner=inner)
        custom_transport.add_response_transformation(
            is_get_account_predicate,
            emulator_as_multi_write_region_account_transformation)

        # Inject rule to simulate regional outage in "First Region"
        is_request_to_first_region: Callable[[HttpRequest], bool] = lambda \
                r: FaultInjectionTransportAsync.predicate_targets_region(r, first_region_uri) and \
                   FaultInjectionTransportAsync.predicate_is_document_operation(r)

        custom_transport.add_fault(
            is_request_to_first_region,
            lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_region_down()))

        id_value: str = str(uuid.uuid4())
        document_definition = {'id': id_value,
                               'pk': id_value,
                               'name': 'sample document',
                               'key': 'value'}

        initialized_objects = await TestFaultInjectionTransportAsync.setup_method_with_custom_transport(
            custom_transport,
            preferred_locations=["First Region", "Second Region"],
            multiple_write_locations=True,
            retry_write=True
        )
        try:
            container: ContainerProxy = initialized_objects["col"]

            create_document = await container.create_item(body=document_definition)
            request = create_document.get_response_headers()["_request"]
            assert request.url.startswith(second_region_uri)

            upsert_document = await container.upsert_item(body=document_definition)
            request = upsert_document.get_response_headers()["_request"]
            assert request.url.startswith(second_region_uri)

            replace_document = await container.replace_item(item=document_definition['id'], body=document_definition)
            request = replace_document.get_response_headers()["_request"]
            assert request.url.startswith(second_region_uri)

            # Patch operation should not retry
            operations = [{"op": "add", "path": "/favorite_color", "value": "red"}, ]
            try:
                await container.patch_item(item=document_definition['id'], partition_key=document_definition['pk'],
                                     patch_operations=operations)
            except (ServiceResponseError, exceptions.CosmosHttpResponseError) as e:
                if isinstance(e, exceptions.CosmosHttpResponseError):
                    assert e.status_code in [408, 500], "Expected a retryable error for patch_item"

        finally:
            await TestFaultInjectionTransportAsync.cleanup_method(initialized_objects)

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
