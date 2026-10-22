# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import pytest
import unittest
import uuid
from azure.core.exceptions import ServiceResponseError
from azure.core.rest import HttpRequest
from azure.core.pipeline.transport._requests_basic import RequestsTransport
from azure.cosmos import CosmosClient, ContainerProxy, DatabaseProxy, _retry_utility, exceptions
from azure.cosmos.partition_key import PartitionKey
from _fault_injection_transport import FaultInjectionTransport
from typing import Callable
import test_config  # Import test_config for configuration details

HPK_CONTAINER = "TestContainerHPK"

@pytest.fixture(scope="class")
def setup():
    config = test_config.TestConfig()
    if config.masterKey == '[YOUR_KEY_HERE]' or config.host == '[YOUR_ENDPOINT_HERE]':
        raise Exception(
            "You must specify your Azure Cosmos account values for "
            "'masterKey' and 'host' at the top of this class to run the "
            "tests.")
    test_client = CosmosClient(config.host, config.masterKey)
    database = test_client.create_database_if_not_exists(id=config.TEST_DATABASE_ID)
    created_container = database.create_container_if_not_exists(
        id=config.TEST_SINGLE_PARTITION_CONTAINER_ID,
        partition_key=PartitionKey(path="/pk")
    )
    container_hpk = database.create_container_if_not_exists(
        id=HPK_CONTAINER,
        partition_key=PartitionKey(path=["/state", "/city"], kind="MultiHash")
    )
    yield {"database": database, "container": created_container, "container_hpk": container_hpk}

@pytest.mark.cosmosEmulator
@pytest.mark.usefixtures("setup")
class TestRetryableWrites:
    host = test_config.TestConfig.host
    master_key = test_config.TestConfig.masterKey
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_SINGLE_PARTITION_ID = test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID
    TEST_CONTAINER_MULTI_PARTITION_ID = test_config.TestConfig.TEST_MULTI_PARTITION_CONTAINER_ID
    client: CosmosClient = None

    @staticmethod
    def setup_method_with_custom_transport(
            custom_transport: RequestsTransport,
            default_endpoint: str = host,
            key: str = master_key,
            database_id: str = TEST_DATABASE_ID,
            container_id: str = TEST_CONTAINER_SINGLE_PARTITION_ID,
            **kwargs):
        client = CosmosClient(default_endpoint, key, consistency_level="Session",
                              transport=custom_transport, **kwargs)
        db: DatabaseProxy = client.create_database_if_not_exists(database_id)
        container: ContainerProxy = db.create_container_if_not_exists(container_id, PartitionKey(path="/pk"))
        return {"client": client, "db": db, "col": container}

    def test_retryable_writes_request_level(self, setup):
        # Create a container for testing
        container = setup["container"]

        # Mock retry_utility.execute to track retries
        original_execute = _retry_utility.ExecuteFunction
        me = self.MockExecuteFunction(original_execute)
        _retry_utility.ExecuteFunction = me

        # Test without retry_write for upsert_item
        test_item = {"id": "1", "pk": "test", "data": "retryable write test"}
        try:
            container.upsert_item(test_item)
            pytest.fail("Expected an exception without retry_write")
        except exceptions.CosmosHttpResponseError:
            assert me.counter == 1, "Expected no retries without retry_write"

        # Test with retry_write for upsert_item
        me.counter = 0  # Reset counter
        try:
            container.upsert_item(test_item, retry_write=2)
        except exceptions.CosmosHttpResponseError as e:
            assert me.counter > 1, "Expected multiple retries due to simulated errors"
        finally:
            # Restore the original retry_utility.execute function
            _retry_utility.ExecuteFunction = original_execute

        # Verify the item was written
        read_item = container.read_item(item=test_item['id'], partition_key=test_item['pk'])
        assert read_item['id'] == test_item['id'], "Item was not written successfully after retries"

        # Mock retry_utility.execute to track retries
        original_execute = _retry_utility.ExecuteFunction
        me = self.MockExecuteFunction(original_execute)
        _retry_utility.ExecuteFunction = me

        # Test without retry_write for create_item
        test_item_create = {"id": "2", "pk": "test", "data": "retryable create test"}
        me.counter = 0  # Reset counter
        try:
            container.create_item(test_item_create)
            pytest.fail("Expected an exception without retry_write")
        except exceptions.CosmosHttpResponseError:
            assert me.counter == 1, "Expected no retries without retry_write"

        # Test with retry_write for create_item
        me.counter = 0  # Reset counter
        try:
            container.create_item(test_item_create, retry_write=2)
        except exceptions.CosmosHttpResponseError as e:
            assert me.counter > 1, "Expected multiple retries due to simulated errors"
        finally:
            # Restore the original retry_utility.execute function
            _retry_utility.ExecuteFunction = original_execute

        # Verify the item was created
        read_item_create = container.read_item(item=test_item_create['id'],
                                               partition_key=test_item_create['pk'])
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
            container.patch_item(item=test_item['id'], partition_key=test_item['pk'],
                                 patch_operations=test_patch_operations)
            pytest.fail("Expected an exception without retry_write")
        except exceptions.CosmosHttpResponseError:
            assert me.counter == 1, "Expected no retries without retry_write"

        # Test with retry_write for patch_item
        me.counter = 0  # Reset counter
        try:
            container.patch_item(item=test_item['id'], partition_key=test_item['pk'],
                                 patch_operations=test_patch_operations, retry_write=2)
        except exceptions.CosmosHttpResponseError as e:
            assert me.counter > 1, "Expected multiple retries due to simulated errors"
        finally:
            # Restore the original retry_utility.execute function
            _retry_utility.ExecuteFunction = original_execute

        # Verify the item was patched
        patched_item = container.read_item(item=test_item['id'], partition_key=test_item['pk'])
        assert patched_item['data'] == "patched retryable write test", "Item was not patched successfully after retries"

        # Verify original execution function is used to upsert an item
        test_item = {"id": "1", "pk": "test", "data": "retryable write test"}
        container.upsert_item(test_item)

        # Mock retry_utility.execute to track retries
        original_execute = _retry_utility.ExecuteFunction
        me = self.MockExecuteFunction(original_execute)
        _retry_utility.ExecuteFunction = me

        # Verify delete_item does not retry
        me.counter = 0  # Reset counter
        try:
            container.delete_item(item=test_item['id'], partition_key=test_item['pk'])
            pytest.fail("Expected an exception without retry_write")
        except exceptions.CosmosHttpResponseError:
            assert me.counter == 1, "Expected no retries for delete_item"

        # Verify the item was not deleted
        read_item = container.read_item(item=test_item['id'], partition_key=test_item['pk'])
        assert read_item['id'] == test_item['id'], "Item was unexpectedly deleted"

        me.counter = 0  # Reset counter
        try:
            container.delete_item(item=test_item['id'], partition_key=test_item['pk'], retry_write=2)
        except exceptions.CosmosHttpResponseError:
            assert me.counter > 1, "Expected multiple retries due to simulated errors"
        finally:
            # Restore the original retry_utility.execute function
            _retry_utility.ExecuteFunction = original_execute

        try:
            container.read_item(item=test_item['id'], partition_key=test_item['pk'])
            pytest.fail("Expected an exception for item that should have been deleted")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 404, "Expected item to be deleted but it was not"

        # Test replace item with retry_write

        test_item_replace = {"id": "3", "pk": "test", "data": "original data"}
        container.create_item(test_item_replace)
        # Mock retry_utility.execute to track retries
        original_execute = _retry_utility.ExecuteFunction
        me = self.MockExecuteFunction(original_execute)
        _retry_utility.ExecuteFunction = me
        # Test without retry_write for replace_item
        try:
            container.replace_item(item=test_item_replace['id'], body={"id": "3", "pk": "test", "data": "updated data"})
            pytest.fail("Expected an exception without retry_write")
        except exceptions.CosmosHttpResponseError:
            assert me.counter == 1, "Expected no retries without retry_write"
        # Test with retry_write for replace_item
        me.counter = 0  # Reset counter
        try:
            container.replace_item(item=test_item_replace['id'], body={"id": "3", "pk": "test",
                                                                       "data": "updated data"}, retry_write=2)
        except exceptions.CosmosHttpResponseError as e:
            assert me.counter > 1, "Expected multiple retries due to simulated errors"
        finally:
            # Restore the original retry_utility.execute function
            _retry_utility.ExecuteFunction = original_execute
        # Verify the item was replaced
        replaced_item = container.read_item(item=test_item_replace['id'],
                                            partition_key=test_item_replace['pk'])
        assert replaced_item['data'] == "updated data", "Item was not replaced successfully after retries"

    def test_retryable_writes_client_level(self, setup):
        """Test retryable writes for a container with retry_write set at the client level."""
        # Create a client with retry_write enabled
        client_with_retry = CosmosClient(self.host, credential=self.master_key, retry_write=2)
        container = client_with_retry.get_database_client(self.TEST_DATABASE_ID).get_container_client(setup['container'].id)

        # Mock retry_utility.execute to track retries
        original_execute = _retry_utility.ExecuteFunction
        me = self.MockExecuteFunction(original_execute)
        _retry_utility.ExecuteFunction = me

        # Test upsert_item
        test_item = {"id": "4", "pk": "test", "data": "retryable write test"}
        try:
            container.upsert_item(test_item)
        except exceptions.CosmosHttpResponseError as e:
            assert me.counter > 1, "Expected multiple retries due to simulated errors"

        # Test create_item
        me.counter = 0  # Reset counter
        test_item_create = {"id": "5", "pk": "test", "data": "retryable create test"}
        try:
            container.create_item(test_item_create)
        except exceptions.CosmosHttpResponseError as e:
            assert me.counter > 1, "Expected multiple retries due to simulated errors"

        # Test patch_item
        me.counter = 0  # Reset counter
        test_patch_operations = [
            {"op": "add", "path": "/data", "value": "patched retryable write test"}
        ]
        try:
            container.patch_item(item=test_item['id'], partition_key=test_item['pk'],
                                 patch_operations=test_patch_operations)
            pytest.fail("Expected an exception without retries")
        except exceptions.CosmosHttpResponseError:
            assert me.counter == 1, "Expected no retries for patch_item with client_retry_write"
        finally:
            # Restore the original retry_utility.execute function
            _retry_utility.ExecuteFunction = original_execute

        # Verify original execution function is used to upsert an item
        test_item = {"id": "4", "pk": "test", "data": "retryable write test"}
        container.upsert_item(test_item)

        # Mock retry_utility.execute to track retries
        original_execute = _retry_utility.ExecuteFunction
        me = self.MockExecuteFunction(original_execute)
        _retry_utility.ExecuteFunction = me

        # Verify delete_item does not retry
        me.counter = 0  # Reset counter
        try:
            container.delete_item(item=test_item['id'], partition_key=test_item['pk'])
        except exceptions.CosmosHttpResponseError:
            assert me.counter > 1, "Expected multiple retries due to simulated errors"
        finally:
            # Restore the original retry_utility.execute function
            _retry_utility.ExecuteFunction = original_execute

        # Verify the item was deleted
        try:
            container.read_item(item=test_item['id'], partition_key=test_item['pk'])
            pytest.fail("Expected an exception for item that should have been deleted")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 404, "Expected item to be deleted but it was not"

        # Test client level retry for service response error
        mf = self.MockExecuteServiceResponseException(Exception)
        try:
            # Reset the function to reset the counter
            _retry_utility.ExecuteFunction = mf
            container.create_item({"id": str(uuid.uuid4()), "pk": str(uuid.uuid4())})
            pytest.fail("Exception was not raised.")
        except ServiceResponseError:
            assert mf.counter == 2
        finally:
            _retry_utility.ExecuteFunction = original_execute

        # Test with replace item
        test_item_replace = {"id": "8", "pk": "test", "data": "original data"}
        container.create_item(test_item_replace)
        # Mock retry_utility.execute to track retries
        original_execute = _retry_utility.ExecuteFunction
        me = self.MockExecuteFunction(original_execute)
        _retry_utility.ExecuteFunction = me
        # Test replace item, writes will retry by default with client level retry_write
        try:
            container.replace_item(item=test_item_replace['id'], body={"id": "8", "pk": "test",
                                                                       "data": "updated data"})
        except exceptions.CosmosHttpResponseError as e:
            assert me.counter > 1, "Expected multiple retries due to simulated errors"
        finally:
            # Restore the original retry_utility.execute function
            _retry_utility.ExecuteFunction = original_execute
        # Verify the item was replaced
        replaced_item = container.read_item(item=test_item_replace['id'],
                                            partition_key=test_item_replace['pk'])
        assert replaced_item['data'] == "updated data", "Item was not replaced successfully after retries"

    def test_retryable_writes_hpk_request_level(self, setup):
        """Test retryable writes for a container with hierarchical partition keys."""
        container = setup["container_hpk"]

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
            container.upsert_item(test_item, retry_write=2)
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
            container.create_item(test_item_create, retry_write=2)
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
                                 patch_operations=test_patch_operations_hpk, retry_write=2)
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

        # Verify original execution function is used to upsert an item
        test_item = {"id": "1", "state": "CA", "city": "San Francisco", "data": "retryable write test"}
        container.upsert_item(test_item)

        # Mock retry_utility.execute to track retries
        original_execute = _retry_utility.ExecuteFunction
        me = self.MockExecuteFunction(original_execute)
        _retry_utility.ExecuteFunction = me

        # Verify delete_item does not retry
        me.counter = 0  # Reset counter
        try:
            container.delete_item(item=test_item['id'], partition_key=[test_item['state'], test_item['city']])
        except exceptions.CosmosHttpResponseError:
            assert me.counter == 1, "Expected no retries for delete_item"

        me.counter = 0  # Reset counter
        try:
            container.delete_item(item=test_item['id'], partition_key=[test_item['state'], test_item['city']],
                                  retry_write=2)
        except exceptions.CosmosHttpResponseError:
            assert me.counter > 1, "Expected multiple retries due to simulated errors"
        finally:
            # Restore the original retry_utility.execute function
            _retry_utility.ExecuteFunction = original_execute

        # Verify the item was deleted
        try:
            container.read_item(item=test_item['id'], partition_key=[test_item['state'], test_item['city']])
            pytest.fail("Expected an exception for item that should have been deleted")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 404, "Expected item to be deleted but it was not"

        # Test with replace item
        test_item_replace = {"id": "6", "state": "CA", "city": "San Francisco", "data": "original data"}
        container.create_item(test_item_replace)
        # Mock retry_utility.execute to track retries
        original_execute = _retry_utility.ExecuteFunction
        me = self.MockExecuteFunction(original_execute)
        _retry_utility.ExecuteFunction = me
        # Test replace item without retry_write
        try:
            container.replace_item(item=test_item_replace['id'], body={"id": "6", "state": "CA", "city": "San Francisco",
                                                                       "data": "updated data"})
            pytest.fail("Expected an exception without retry_write")
        except exceptions.CosmosHttpResponseError:
            assert me.counter == 1, "Expected no retries without retry_write"
        # Test replace item with retry_write
        me.counter = 0  # Reset counter
        try:
            container.replace_item(item=test_item_replace['id'], body={"id": "6", "state": "CA",
                                                                       "city": "San Francisco",
                                                                       "data": "updated data"}, retry_write=2)
        except exceptions.CosmosHttpResponseError as e:
            assert me.counter > 1, "Expected multiple retries due to simulated errors"
        finally:
            # Restore the original retry_utility.execute function
            _retry_utility.ExecuteFunction = original_execute
        # Verify the item was replaced
        replaced_item_hpk = container.read_item(item=test_item_replace['id'],
                                                partition_key=[test_item_replace['state'], test_item_replace['city']])
        assert replaced_item_hpk['data'] == "updated data", "Item was not replaced successfully after retries"

    def test_retryable_writes_hpk_client_level(self, setup):
        """Test retryable writes for a container with hierarchical partition keys and
        retry_write set at the client level."""
        # Create a client with retry_write enabled
        client_with_retry = CosmosClient(self.host, credential=self.master_key, retry_write=2)
        container = client_with_retry.get_database_client(self.TEST_DATABASE_ID).get_container_client(
            setup['container_hpk'].id)

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

        # Test create_item
        me.counter = 0  # Reset counter
        test_item_create = {"id": "7", "state": "NY", "city": "New York", "data": "retryable create test"}
        try:
            container.create_item(test_item_create)
        except exceptions.CosmosHttpResponseError as e:
            assert me.counter > 1, "Expected multiple retries due to simulated errors"

        # Test patch_item
        me.counter = 0  # Reset counter
        test_patch_operations_hpk = [
            {"op": "add", "path": "/data", "value": "patched retryable write test"}
        ]
        try:
            container.patch_item(item=test_item['id'], partition_key=[test_item['state'], test_item['city']],
                                 patch_operations=test_patch_operations_hpk)
            pytest.fail("Expected an exception without retries")
        except exceptions.CosmosHttpResponseError:
            assert me.counter == 1, "Expected no retries for patch_item with client_retry_write"
        finally:
            # Restore the original retry_utility.execute function
            _retry_utility.ExecuteFunction = original_execute

        # Verify original execution function is used to upsert an item
        test_item = {"id": "6", "state": "CA", "city": "San Francisco", "data": "retryable write test"}
        container.upsert_item(test_item)

        # Mock retry_utility.execute to track retries
        original_execute = _retry_utility.ExecuteFunction
        me = self.MockExecuteFunction(original_execute)
        _retry_utility.ExecuteFunction = me

        # Verify delete_item does not retry
        me.counter = 0  # Reset counter
        try:
            container.delete_item(item=test_item['id'], partition_key=[test_item['state'], test_item['city']])
        except exceptions.CosmosHttpResponseError:
            assert me.counter > 1, "Expected multiple retries due to simulated errors"
        finally:
            # Restore the original retry_utility.execute function
            _retry_utility.ExecuteFunction = original_execute

        # Verify the item was deleted
        try:
            container.read_item(item=test_item['id'], partition_key=[test_item['state'], test_item['city']])
            pytest.fail("Expected an exception for item that should have been deleted")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 404, "Expected item to be deleted but it was not"

        # Test client level retry for replace item
        test_item_replace = {"id": "8", "state": "CA", "city": "San Francisco", "data": "original data"}
        container.create_item(test_item_replace)
        # Mock retry_utility.execute to track retries
        original_execute = _retry_utility.ExecuteFunction
        me = self.MockExecuteFunction(original_execute)
        _retry_utility.ExecuteFunction = me
        # Test replace item, writes will retry by default with client level retry_write
        try:
            container.replace_item(item=test_item_replace['id'], body={"id": "8", "state": "CA",
                                                                       "city": "San Francisco",
                                                                       "data": "updated data"})
        except exceptions.CosmosHttpResponseError as e:
            assert me.counter > 1, "Expected multiple retries due to simulated errors"
        finally:
            # Restore the original retry_utility.execute function
            _retry_utility.ExecuteFunction = original_execute
        # Verify the item was replaced
        replaced_item_hpk = container.read_item(item=test_item_replace['id'],
                                                partition_key=[test_item_replace['state'], test_item_replace['city']])
        assert replaced_item_hpk['data'] == "updated data", "Item was not replaced successfully after retries"


    @pytest.mark.parametrize("injected_error", [FaultInjectionTransport.error_request_timeout(),
                             FaultInjectionTransport.error_internal_server_error(),
                             FaultInjectionTransport.error_service_response()])
    def test_retryable_writes_mrw_request_level(self, injected_error):
        # Verify cross regional retries when using retryable writes at request level with multiple write locations.
        # Need to test for 408s, 500s, and ServiceResponseError.
        first_region_uri: str = test_config.TestConfig.local_host.replace("localhost", "127.0.0.1")
        second_region_uri: str = test_config.TestConfig.local_host
        custom_transport = FaultInjectionTransport()

        # Inject topology transformation that would make Emulator look like a multiple write region account
        is_get_account_predicate: Callable[[HttpRequest], bool] = lambda \
            r: FaultInjectionTransport.predicate_is_database_account_call(r)
        emulator_as_multi_write_region_account_transformation = \
            lambda r, inner: FaultInjectionTransport.transform_topology_mwr(
                first_region_name="First Region",
                second_region_name="Second Region",
                inner=inner)
        custom_transport.add_response_transformation(
            is_get_account_predicate,
            emulator_as_multi_write_region_account_transformation)

        # Inject rule to simulate regional outage in "First Region" to test retry happens in next region
        is_request_to_first_region: Callable[[HttpRequest], bool] = lambda \
                r: FaultInjectionTransport.predicate_targets_region(r, first_region_uri) and \
                   FaultInjectionTransport.predicate_is_document_operation(r)

        custom_transport.add_fault(
            is_request_to_first_region,
            lambda r: injected_error)

        id_value: str = str(uuid.uuid4())
        document_definition = {'id': id_value,
                               'pk': id_value,
                               'name': 'sample document',
                               'key': 'value'}

        initialized_objects = self.setup_method_with_custom_transport(
            custom_transport,
            preferred_locations=["First Region", "Second Region"],
            multiple_write_locations=True
        )
        container: ContainerProxy = initialized_objects["col"]

        create_document = container.create_item(body=document_definition, retry_write=2)
        request = create_document.get_response_headers()["_request"]
        assert request.url.startswith(second_region_uri)

        upsert_document = container.upsert_item(body=document_definition, retry_write=2)
        request = upsert_document.get_response_headers()["_request"]
        assert request.url.startswith(second_region_uri)

        replace_document = container.replace_item(item=document_definition['id'], body=document_definition, retry_write=2)
        request = replace_document.get_response_headers()["_request"]
        assert request.url.startswith(second_region_uri)

        operations = [{"op": "add", "path": "/favorite_color", "value": "red"},]
        patch_document = container.patch_item(item=document_definition['id'], partition_key=document_definition['pk'],
                                                patch_operations=operations, retry_write=2)
        request = patch_document.get_response_headers()["_request"]
        assert request.url.startswith(second_region_uri)

    @pytest.mark.parametrize("injected_error", [FaultInjectionTransport.error_request_timeout(),
                             FaultInjectionTransport.error_internal_server_error(),
                             FaultInjectionTransport.error_service_response()])
    def test_retryable_writes_mrw_client_level(self, injected_error):
        # Verify cross regional retries when using retryable writes at client level with multiple write locations.
        # Need to test for 408s, 500s, and ServiceResponseError.
        first_region_uri: str = test_config.TestConfig.local_host.replace("localhost", "127.0.0.1")
        second_region_uri: str = test_config.TestConfig.local_host
        custom_transport = FaultInjectionTransport()

        # Inject topology transformation that would make Emulator look like a multiple write region account
        is_get_account_predicate: Callable[[HttpRequest], bool] = lambda \
            r: FaultInjectionTransport.predicate_is_database_account_call(r)
        emulator_as_multi_write_region_account_transformation = \
            lambda r, inner: FaultInjectionTransport.transform_topology_mwr(
                first_region_name="First Region",
                second_region_name="Second Region",
                inner=inner)
        custom_transport.add_response_transformation(
            is_get_account_predicate,
            emulator_as_multi_write_region_account_transformation)

        # Inject rule to simulate regional outage in "First Region" to test retry happens in next region
        is_request_to_first_region: Callable[[HttpRequest], bool] = lambda \
                r: FaultInjectionTransport.predicate_targets_region(r, first_region_uri) and \
                   FaultInjectionTransport.predicate_is_document_operation(r)

        custom_transport.add_fault(
            is_request_to_first_region,
            lambda r: injected_error)

        id_value: str = str(uuid.uuid4())
        document_definition = {'id': id_value,
                               'pk': id_value,
                               'name': 'sample document',
                               'key': 'value'}

        initialized_objects = self.setup_method_with_custom_transport(
            custom_transport,
            preferred_locations=["First Region", "Second Region"],
            multiple_write_locations=True,
            retry_write=2
        )
        container: ContainerProxy = initialized_objects["col"]

        create_document = container.create_item(body=document_definition)
        request = create_document.get_response_headers()["_request"]
        assert request.url.startswith(second_region_uri)

        upsert_document = container.upsert_item(body=document_definition)
        request = upsert_document.get_response_headers()["_request"]
        assert request.url.startswith(second_region_uri)

        replace_document = container.replace_item(item=document_definition['id'], body=document_definition)
        request = replace_document.get_response_headers()["_request"]
        assert request.url.startswith(second_region_uri)

        # Patch operation should not retry
        operations = [{"op": "add", "path": "/favorite_color", "value": "red"},]
        try:
            container.patch_item(item=document_definition['id'], partition_key=document_definition['pk'],
                                    patch_operations=operations)
        except (ServiceResponseError, exceptions.CosmosHttpResponseError) as e:
            if isinstance(e, exceptions.CosmosHttpResponseError):
                assert e.status_code in [408, 500], "Expected a retryable error for patch_item"

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

    class MockExecuteServiceResponseException(object):
        def __init__(self, err_type):
            self.err_type = err_type
            self.counter = 0

        def __call__(self, func, *args, **kwargs):
            self.counter = self.counter + 1
            exception = ServiceResponseError("mock exception")
            exception.exc_type = self.err_type
            raise exception

if __name__ == "__main__":
    unittest.main()
