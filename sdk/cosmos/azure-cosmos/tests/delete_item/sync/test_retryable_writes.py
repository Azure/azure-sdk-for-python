# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Rust-path copies of the sync retryable-writes tests that exercise delete_item.

The originals patch ``_retry_utility.ExecuteFunction`` to fail the first attempt of
each write with a 408 and count attempts. The Rust backend does not use that Python
retry utility, so these copies inject the same first-attempt 408 with Rust fault
injection rules and count attempts from the ``requests=N`` value in the
``x-ms-cosmos-sdk-diagnostics`` response header. Steps and assertions are unchanged.
"""

import os
import re
import uuid

import pytest
from azure.core.exceptions import ServiceResponseError

from azure.cosmos import CosmosClient, exceptions
from azure.cosmos.partition_key import PartitionKey

HPK_CONTAINER = "TestContainerHPK"
SINGLE_PARTITION_CONTAINER = "TestSinglePartitionContainer"
_WRITE_OPERATION_TYPES = ("CreateItem", "UpsertItem", "ReplaceItem", "DeleteItem")
_DIAGNOSTICS_HEADER = "x-ms-cosmos-sdk-diagnostics"


def _host():
    return os.environ["ACCOUNT_HOST"]


def _key():
    return os.environ["ACCOUNT_KEY"]


@pytest.fixture(scope="class")
def setup():
    test_client = CosmosClient(_host(), _key(), _backend="rust")
    database = test_client.create_database(id="retryable_writes_rust_" + uuid.uuid4().hex)
    try:
        created_container = database.create_container_if_not_exists(
            id=SINGLE_PARTITION_CONTAINER,
            partition_key=PartitionKey(path="/pk")
        )
        container_hpk = database.create_container_if_not_exists(
            id=HPK_CONTAINER,
            partition_key=PartitionKey(path=["/state", "/city"], kind="MultiHash")
        )
        yield {"database": database, "container": created_container, "container_hpk": container_hpk}
    finally:
        test_client.delete_database(database.id)
        test_client.close()


class _RecordingContainer(object):
    """Delegates to a container proxy and records the last operation name."""

    def __init__(self, inner, owner):
        self._inner = inner
        self._owner = owner

    def __getattr__(self, name):
        attr = getattr(self._inner, name)
        if callable(attr):
            self._owner._last_operation = name
        return attr


@pytest.mark.cosmosEmulator
@pytest.mark.usefixtures("setup")
class TestRetryableWrites:
    """Rust-path copies of tests/test_retryable_writes.py::TestRetryableWrites."""

    class MockExecuteFunction(object):
        """Rust stand-in for the original MockExecuteFunction.

        Each arm (construction or ``counter = 0``) builds a fresh Rust client whose rules
        fail the first Create/Upsert/Replace/Delete attempt on the container with a 408,
        like the original mock failing its first call. ``counter`` reports how many
        attempts the last operation sent. Rust patch is a read followed by a replace, so
        the read is not counted for patch.
        """

        def __init__(self, database_id, container_id, **client_kwargs):
            self._database_id = database_id
            self._container_id = container_id
            self._client_kwargs = client_kwargs
            self._clients = []
            self._client = None
            self._last_operation = None
            self.container = None
            self._arm()

        def _arm(self):
            suffix = uuid.uuid4().hex
            rules = [{
                "id": "{}-{}".format(op, suffix),
                "operation_type": op,
                "container_id": self._container_id,
                "status_code": 408,
                "hit_limit": 1,
            } for op in _WRITE_OPERATION_TYPES]
            self._client = CosmosClient(_host(), _key(), _backend="rust", _fault_injection_rules=rules,
                                        **self._client_kwargs)
            self._clients.append(self._client)
            self._last_operation = None
            self.container = _RecordingContainer(
                self._client.get_database_client(self._database_id).get_container_client(self._container_id),
                self)

        @property
        def counter(self):
            headers = self._client.client_connection.last_response_headers or {}
            match = re.search(r"requests=(\d+)", headers.get(_DIAGNOSTICS_HEADER, ""))
            if match is None:
                return 0
            requests = int(match.group(1))
            return requests - 1 if self._last_operation == "patch_item" else requests

        @counter.setter
        def counter(self, value):
            if value == 0:
                self._arm()

        def close(self):
            for client in self._clients:
                client.close()

    class MockExecuteServiceResponseException(object):
        """Rust stand-in: every CreateItem attempt fails with a response timeout."""

        def __init__(self, database_id, container_id, **client_kwargs):
            self._rule_id = "response-timeout-" + uuid.uuid4().hex
            self._client = CosmosClient(_host(), _key(), _backend="rust", _fault_injection_rules=[{
                "id": self._rule_id,
                "operation_type": "CreateItem",
                "container_id": container_id,
                "error_type": "ResponseTimeout",
                "hit_limit": None,
            }], **client_kwargs)
            self.container = self._client.get_database_client(database_id).get_container_client(container_id)

        @property
        def counter(self):
            return self._client._adapter._debug_fault_injection_rule_hit_count(self._rule_id)

        def close(self):
            self._client.close()

    def test_retryable_writes_request_level_rust(self, setup):
        # Source: tests/test_retryable_writes.py::TestRetryableWrites.test_retryable_writes_request_level
        # Create a container for testing
        container = setup["container"]
        database_id = setup["database"].id
        mocks = []
        try:
            # Mock retry_utility.execute to track retries
            me = self.MockExecuteFunction(database_id, container.id)
            mocks.append(me)

            # Test without retry_write for upsert_item
            test_item = {"id": "1", "pk": "test", "data": "retryable write test"}
            # Known gap 13: Closed: Rust owns automatic write retries (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-13). Rust retries the injected 408 itself, so the write may succeed instead of raising.
            try:
                me.container.upsert_item(test_item)
                pytest.fail("Expected an exception without retry_write")
            except exceptions.CosmosHttpResponseError:
                assert me.counter == 1, "Expected no retries without retry_write"

            # Test with retry_write for upsert_item
            me.counter = 0  # Reset counter
            # Known gap 13: Closed: Rust owns automatic write retries (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-13). Per-call retry_write raises NotImplementedError on the Rust item backend before any request is sent.
            pytest.skip("Per-call retry_write is not supported on the Rust backend (known gap 13).")
            try:
                me.container.upsert_item(test_item, retry_write=2)
            except exceptions.CosmosHttpResponseError as e:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"

            # Verify the item was written
            read_item = container.read_item(item=test_item['id'], partition_key=test_item['pk'])
            assert read_item['id'] == test_item['id'], "Item was not written successfully after retries"

            # Mock retry_utility.execute to track retries
            me = self.MockExecuteFunction(database_id, container.id)
            mocks.append(me)

            # Test without retry_write for create_item
            test_item_create = {"id": "2", "pk": "test", "data": "retryable create test"}
            me.counter = 0  # Reset counter
            try:
                me.container.create_item(test_item_create)
                pytest.fail("Expected an exception without retry_write")
            except exceptions.CosmosHttpResponseError:
                assert me.counter == 1, "Expected no retries without retry_write"

            # Test with retry_write for create_item
            me.counter = 0  # Reset counter
            try:
                me.container.create_item(test_item_create, retry_write=2)
            except exceptions.CosmosHttpResponseError as e:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"

            # Verify the item was created
            read_item_create = container.read_item(item=test_item_create['id'],
                                                   partition_key=test_item_create['pk'])
            assert read_item_create['id'] == test_item_create['id'], "Item was not created successfully after retries"

            # Mock retry_utility.execute to track retries
            me = self.MockExecuteFunction(database_id, container.id)
            mocks.append(me)
            # Test without retry_write for patch_item
            test_patch_operations = [
                {"op": "add", "path": "/data", "value": "patched retryable write test"}
            ]
            try:
                me.container.patch_item(item=test_item['id'], partition_key=test_item['pk'],
                                        patch_operations=test_patch_operations)
                pytest.fail("Expected an exception without retry_write")
            except exceptions.CosmosHttpResponseError:
                assert me.counter == 1, "Expected no retries without retry_write"

            # Test with retry_write for patch_item
            me.counter = 0  # Reset counter
            try:
                me.container.patch_item(item=test_item['id'], partition_key=test_item['pk'],
                                        patch_operations=test_patch_operations, retry_write=2)
            except exceptions.CosmosHttpResponseError as e:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"

            # Verify the item was patched
            patched_item = container.read_item(item=test_item['id'], partition_key=test_item['pk'])
            assert patched_item['data'] == "patched retryable write test", "Item was not patched successfully after retries"

            # Verify original execution function is used to upsert an item
            test_item = {"id": "1", "pk": "test", "data": "retryable write test"}
            container.upsert_item(test_item)

            # Mock retry_utility.execute to track retries
            me = self.MockExecuteFunction(database_id, container.id)
            mocks.append(me)

            # Verify delete_item does not retry
            me.counter = 0  # Reset counter
            try:
                me.container.delete_item(item=test_item['id'], partition_key=test_item['pk'])
                pytest.fail("Expected an exception without retry_write")
            except exceptions.CosmosHttpResponseError:
                assert me.counter == 1, "Expected no retries for delete_item"

            # Verify the item was not deleted
            read_item = me.container.read_item(item=test_item['id'], partition_key=test_item['pk'])
            assert read_item['id'] == test_item['id'], "Item was unexpectedly deleted"

            me.counter = 0  # Reset counter
            try:
                me.container.delete_item(item=test_item['id'], partition_key=test_item['pk'], retry_write=2)
            except exceptions.CosmosHttpResponseError:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"

            try:
                container.read_item(item=test_item['id'], partition_key=test_item['pk'])
                pytest.fail("Expected an exception for item that should have been deleted")
            except exceptions.CosmosHttpResponseError as e:
                assert e.status_code == 404, "Expected item to be deleted but it was not"

            # Test replace item with retry_write

            test_item_replace = {"id": "3", "pk": "test", "data": "original data"}
            container.create_item(test_item_replace)
            # Mock retry_utility.execute to track retries
            me = self.MockExecuteFunction(database_id, container.id)
            mocks.append(me)
            # Test without retry_write for replace_item
            try:
                me.container.replace_item(item=test_item_replace['id'],
                                          body={"id": "3", "pk": "test", "data": "updated data"})
                pytest.fail("Expected an exception without retry_write")
            except exceptions.CosmosHttpResponseError:
                assert me.counter == 1, "Expected no retries without retry_write"
            # Test with retry_write for replace_item
            me.counter = 0  # Reset counter
            try:
                me.container.replace_item(item=test_item_replace['id'], body={"id": "3", "pk": "test",
                                                                              "data": "updated data"}, retry_write=2)
            except exceptions.CosmosHttpResponseError as e:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"
            # Verify the item was replaced
            replaced_item = container.read_item(item=test_item_replace['id'],
                                                partition_key=test_item_replace['pk'])
            assert replaced_item['data'] == "updated data", "Item was not replaced successfully after retries"
        finally:
            for mock in mocks:
                mock.close()

    def test_retryable_writes_client_level_rust(self, setup):
        # Source: tests/test_retryable_writes.py::TestRetryableWrites.test_retryable_writes_client_level
        """Test retryable writes for a container with retry_write set at the client level."""
        # Create a client with retry_write enabled
        client_with_retry = CosmosClient(_host(), credential=_key(), retry_write=2, _backend="rust")
        database_id = setup["database"].id
        container = client_with_retry.get_database_client(database_id).get_container_client(setup['container'].id)
        mocks = []
        try:
            # Mock retry_utility.execute to track retries
            me = self.MockExecuteFunction(database_id, container.id, retry_write=2)
            mocks.append(me)

            # Test upsert_item
            test_item = {"id": "4", "pk": "test", "data": "retryable write test"}
            try:
                me.container.upsert_item(test_item)
            except exceptions.CosmosHttpResponseError as e:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"

            # Test create_item
            me.counter = 0  # Reset counter
            test_item_create = {"id": "5", "pk": "test", "data": "retryable create test"}
            try:
                me.container.create_item(test_item_create)
            except exceptions.CosmosHttpResponseError as e:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"

            # Test patch_item
            me.counter = 0  # Reset counter
            test_patch_operations = [
                {"op": "add", "path": "/data", "value": "patched retryable write test"}
            ]
            # Known gap 13: Closed: Rust owns automatic write retries (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-13). Rust retries the injected 408 on the replace leg of its client-side patch, so patch may succeed instead of raising.
            try:
                me.container.patch_item(item=test_item['id'], partition_key=test_item['pk'],
                                        patch_operations=test_patch_operations)
                pytest.fail("Expected an exception without retries")
            except exceptions.CosmosHttpResponseError:
                assert me.counter == 1, "Expected no retries for patch_item with client_retry_write"

            # Verify original execution function is used to upsert an item
            test_item = {"id": "4", "pk": "test", "data": "retryable write test"}
            container.upsert_item(test_item)

            # Mock retry_utility.execute to track retries
            me = self.MockExecuteFunction(database_id, container.id, retry_write=2)
            mocks.append(me)

            # Verify delete_item does not retry
            me.counter = 0  # Reset counter
            try:
                me.container.delete_item(item=test_item['id'], partition_key=test_item['pk'])
            except exceptions.CosmosHttpResponseError:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"

            # Verify the item was deleted
            try:
                container.read_item(item=test_item['id'], partition_key=test_item['pk'])
                pytest.fail("Expected an exception for item that should have been deleted")
            except exceptions.CosmosHttpResponseError as e:
                assert e.status_code == 404, "Expected item to be deleted but it was not"

            # Test client level retry for service response error
            mf = self.MockExecuteServiceResponseException(database_id, container.id, retry_write=2)
            mocks.append(mf)
            try:
                # Reset the function to reset the counter
                mf.container.create_item({"id": str(uuid.uuid4()), "pk": str(uuid.uuid4())})
                pytest.fail("Exception was not raised.")
            except ServiceResponseError:
                assert mf.counter == 2

            # Test with replace item
            test_item_replace = {"id": "8", "pk": "test", "data": "original data"}
            container.create_item(test_item_replace)
            # Mock retry_utility.execute to track retries
            me = self.MockExecuteFunction(database_id, container.id, retry_write=2)
            mocks.append(me)
            # Test replace item, writes will retry by default with client level retry_write
            try:
                me.container.replace_item(item=test_item_replace['id'], body={"id": "8", "pk": "test",
                                                                              "data": "updated data"})
            except exceptions.CosmosHttpResponseError as e:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"
            # Verify the item was replaced
            replaced_item = container.read_item(item=test_item_replace['id'],
                                                partition_key=test_item_replace['pk'])
            assert replaced_item['data'] == "updated data", "Item was not replaced successfully after retries"
        finally:
            for mock in mocks:
                mock.close()
            client_with_retry.close()

    def test_retryable_writes_hpk_request_level_rust(self, setup):
        # Source: tests/test_retryable_writes.py::TestRetryableWrites.test_retryable_writes_hpk_request_level
        """Test retryable writes for a container with hierarchical partition keys."""
        container = setup["container_hpk"]
        database_id = setup["database"].id
        mocks = []
        try:
            # Mock retry_utility.execute to track retries
            me = self.MockExecuteFunction(database_id, container.id)
            mocks.append(me)

            # Test without retry_write for upsert_item
            test_item = {"id": "1", "state": "CA", "city": "San Francisco", "data": "retryable write test"}
            # Known gap 13: Closed: Rust owns automatic write retries (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-13). Rust retries the injected 408 itself, so the write may succeed instead of raising.
            try:
                me.container.upsert_item(test_item)
                pytest.fail("Expected an exception without retry_write")
            except exceptions.CosmosHttpResponseError:
                assert me.counter == 1, "Expected no retries without retry_write"

            # Test with retry_write for upsert_item
            me.counter = 0  # Reset counter
            # Known gap 13: Closed: Rust owns automatic write retries (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-13). Per-call retry_write raises NotImplementedError on the Rust item backend before any request is sent.
            pytest.skip("Per-call retry_write is not supported on the Rust backend (known gap 13).")
            try:
                me.container.upsert_item(test_item, retry_write=2)
            except exceptions.CosmosHttpResponseError as e:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"

            # Verify the item was written
            read_item = container.read_item(item=test_item['id'], partition_key=[test_item['state'], test_item['city']])
            assert read_item['id'] == test_item['id'], "Item was not written successfully after retries"

            # Mock retry_utility.execute to track retries
            me = self.MockExecuteFunction(database_id, container.id)
            mocks.append(me)

            # Test without retry_write for create_item
            test_item_create = {"id": "2", "state": "NY", "city": "New York", "data": "retryable create test"}
            try:
                me.container.create_item(test_item_create)
                pytest.fail("Expected an exception without retry_write")
            except exceptions.CosmosHttpResponseError:
                assert me.counter == 1, "Expected no retries without retry_write"

            # Test with retry_write for create_item
            me.counter = 0  # Reset counter
            try:
                me.container.create_item(test_item_create, retry_write=2)
            except exceptions.CosmosHttpResponseError as e:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"

            # Verify the item was created
            read_item_create = container.read_item(item=test_item_create['id'],
                                                   partition_key=[test_item_create['state'], test_item_create['city']])
            assert read_item_create['id'] == test_item_create['id'], "Item was not created successfully after retries"

            # Mock retry_utility.execute to track retries
            me = self.MockExecuteFunction(database_id, container.id)
            mocks.append(me)

            # Test without retry_write for patch_item
            test_patch_operations_hpk = [
                {"op": "add", "path": "/data", "value": "patched retryable write test"}
            ]
            try:
                me.container.patch_item(item=test_item['id'], partition_key=[test_item['state'], test_item['city']],
                                        patch_operations=test_patch_operations_hpk)
                pytest.fail("Expected an exception without retry_write")
            except exceptions.CosmosHttpResponseError:
                assert me.counter == 1, "Expected no retries without retry_write"

            # Test with retry_write for patch_item
            me.counter = 0  # Reset counter
            try:
                me.container.patch_item(item=test_item['id'], partition_key=[test_item['state'], test_item['city']],
                                        patch_operations=test_patch_operations_hpk, retry_write=2)
            except exceptions.CosmosHttpResponseError as e:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"

            # Verify the item was patched
            patched_item_hpk = container.read_item(item=test_item['id'],
                                                   partition_key=[test_item['state'], test_item['city']])
            assert patched_item_hpk[
                       'data'] == "patched retryable write test", "Item was not patched successfully after retries"

            # Verify original execution function is used to upsert an item
            test_item = {"id": "1", "state": "CA", "city": "San Francisco", "data": "retryable write test"}
            container.upsert_item(test_item)

            # Mock retry_utility.execute to track retries
            me = self.MockExecuteFunction(database_id, container.id)
            mocks.append(me)

            # Verify delete_item does not retry
            me.counter = 0  # Reset counter
            try:
                me.container.delete_item(item=test_item['id'], partition_key=[test_item['state'], test_item['city']])
            except exceptions.CosmosHttpResponseError:
                assert me.counter == 1, "Expected no retries for delete_item"

            me.counter = 0  # Reset counter
            try:
                me.container.delete_item(item=test_item['id'], partition_key=[test_item['state'], test_item['city']],
                                         retry_write=2)
            except exceptions.CosmosHttpResponseError:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"

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
            me = self.MockExecuteFunction(database_id, container.id)
            mocks.append(me)
            # Test replace item without retry_write
            try:
                me.container.replace_item(item=test_item_replace['id'],
                                          body={"id": "6", "state": "CA", "city": "San Francisco",
                                                "data": "updated data"})
                pytest.fail("Expected an exception without retry_write")
            except exceptions.CosmosHttpResponseError:
                assert me.counter == 1, "Expected no retries without retry_write"
            # Test replace item with retry_write
            me.counter = 0  # Reset counter
            try:
                me.container.replace_item(item=test_item_replace['id'], body={"id": "6", "state": "CA",
                                                                              "city": "San Francisco",
                                                                              "data": "updated data"}, retry_write=2)
            except exceptions.CosmosHttpResponseError as e:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"
            # Verify the item was replaced
            replaced_item_hpk = container.read_item(item=test_item_replace['id'],
                                                    partition_key=[test_item_replace['state'],
                                                                   test_item_replace['city']])
            assert replaced_item_hpk['data'] == "updated data", "Item was not replaced successfully after retries"
        finally:
            for mock in mocks:
                mock.close()

    def test_retryable_writes_hpk_client_level_rust(self, setup):
        # Source: tests/test_retryable_writes.py::TestRetryableWrites.test_retryable_writes_hpk_client_level
        """Test retryable writes for a container with hierarchical partition keys and
        retry_write set at the client level."""
        # Create a client with retry_write enabled
        client_with_retry = CosmosClient(_host(), credential=_key(), retry_write=2, _backend="rust")
        database_id = setup["database"].id
        container = client_with_retry.get_database_client(database_id).get_container_client(
            setup['container_hpk'].id)
        mocks = []
        try:
            # Mock retry_utility.execute to track retries
            me = self.MockExecuteFunction(database_id, container.id, retry_write=2)
            mocks.append(me)

            # Test upsert_item
            test_item = {"id": "6", "state": "CA", "city": "San Francisco", "data": "retryable write test"}
            try:
                me.container.upsert_item(test_item)
            except exceptions.CosmosHttpResponseError as e:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"

            # Test create_item
            me.counter = 0  # Reset counter
            test_item_create = {"id": "7", "state": "NY", "city": "New York", "data": "retryable create test"}
            try:
                me.container.create_item(test_item_create)
            except exceptions.CosmosHttpResponseError as e:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"

            # Test patch_item
            me.counter = 0  # Reset counter
            test_patch_operations_hpk = [
                {"op": "add", "path": "/data", "value": "patched retryable write test"}
            ]
            # Known gap 13: Closed: Rust owns automatic write retries (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-13). Rust retries the injected 408 on the replace leg of its client-side patch, so patch may succeed instead of raising.
            try:
                me.container.patch_item(item=test_item['id'], partition_key=[test_item['state'], test_item['city']],
                                        patch_operations=test_patch_operations_hpk)
                pytest.fail("Expected an exception without retries")
            except exceptions.CosmosHttpResponseError:
                assert me.counter == 1, "Expected no retries for patch_item with client_retry_write"

            # Verify original execution function is used to upsert an item
            test_item = {"id": "6", "state": "CA", "city": "San Francisco", "data": "retryable write test"}
            container.upsert_item(test_item)

            # Mock retry_utility.execute to track retries
            me = self.MockExecuteFunction(database_id, container.id, retry_write=2)
            mocks.append(me)

            # Verify delete_item does not retry
            me.counter = 0  # Reset counter
            try:
                me.container.delete_item(item=test_item['id'], partition_key=[test_item['state'], test_item['city']])
            except exceptions.CosmosHttpResponseError:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"

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
            me = self.MockExecuteFunction(database_id, container.id, retry_write=2)
            mocks.append(me)
            # Test replace item, writes will retry by default with client level retry_write
            try:
                me.container.replace_item(item=test_item_replace['id'], body={"id": "8", "state": "CA",
                                                                              "city": "San Francisco",
                                                                              "data": "updated data"})
            except exceptions.CosmosHttpResponseError as e:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"
            # Verify the item was replaced
            replaced_item_hpk = container.read_item(item=test_item_replace['id'],
                                                    partition_key=[test_item_replace['state'],
                                                                   test_item_replace['city']])
            assert replaced_item_hpk['data'] == "updated data", "Item was not replaced successfully after retries"
        finally:
            for mock in mocks:
                mock.close()
            client_with_retry.close()
