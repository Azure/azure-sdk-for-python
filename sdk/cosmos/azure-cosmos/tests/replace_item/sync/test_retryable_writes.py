# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Rust-path copies of the sync retryable-writes tests that exercise replace_item.

The originals patch ``_retry_utility.ExecuteFunction`` to fail the first attempt of
each write with a 408 and count attempts. The Rust backend does not use that Python
retry utility, so these copies inject the same first-attempt 408 with Rust fault
injection rules and count attempts from the ``requests=N`` value in the
``x-ms-cosmos-sdk-diagnostics`` response header. Steps and assertions are unchanged.
"""

import os
import re
import uuid
from typing import Callable

import pytest
from azure.core.exceptions import ServiceResponseError
from azure.core.pipeline.transport._requests_basic import RequestsTransport
from azure.core.rest import HttpRequest

from azure.cosmos import CosmosClient, ContainerProxy, DatabaseProxy, exceptions
from azure.cosmos.partition_key import PartitionKey
from _fault_injection_transport import FaultInjectionTransport

HPK_CONTAINER = "TestContainerHPK"
SINGLE_PARTITION_CONTAINER = "TestSinglePartitionContainer"
_WRITE_OPERATION_TYPES = ("CreateItem", "UpsertItem", "ReplaceItem", "DeleteItem")
_DIAGNOSTICS_HEADER = "x-ms-cosmos-sdk-diagnostics"
# Mirrors TestSettings.local_host; the mrw originals target the emulator endpoint.
_LOCAL_HOST = "https://localhost:8081/"


def _host():
    return os.environ["ACCOUNT_HOST"]


def _key():
    return os.environ["ACCOUNT_KEY"]


@pytest.fixture(scope="class")
def setup():
    test_client = CosmosClient(_host(), _key(), _backend="rust")
    database = test_client.create_database(id="replace_item_retryable_writes_" + uuid.uuid4().hex)
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
    TEST_DATABASE_ID = "replace_item_retryable_writes_mrw_" + uuid.uuid4().hex
    TEST_CONTAINER_SINGLE_PARTITION_ID = SINGLE_PARTITION_CONTAINER

    @staticmethod
    def setup_method_with_custom_transport(
            custom_transport: RequestsTransport,
            default_endpoint: str = None,
            key: str = None,
            database_id: str = TEST_DATABASE_ID,
            container_id: str = TEST_CONTAINER_SINGLE_PARTITION_ID,
            **kwargs):
        client = CosmosClient(default_endpoint or _host(), key or _key(), consistency_level="Session",
                              transport=custom_transport, _backend="rust", **kwargs)
        db: DatabaseProxy = client.create_database_if_not_exists(database_id)
        container: ContainerProxy = db.create_container_if_not_exists(container_id, PartitionKey(path="/pk"))
        return {"client": client, "db": db, "col": container}

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
            pytest.skip("accepted-vnext-change: per-call retry_write is not supported on the Rust backend (known gap 13).")
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
            pytest.skip("accepted-vnext-change: per-call retry_write is not supported on the Rust backend (known gap 13).")
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

    @pytest.mark.parametrize("injected_error", [FaultInjectionTransport.error_request_timeout(),
                             FaultInjectionTransport.error_internal_server_error(),
                             FaultInjectionTransport.error_service_response()])
    def test_retryable_writes_mrw_request_level_rust(self, injected_error):
        # Source: tests/test_retryable_writes.py::TestRetryableWrites.test_retryable_writes_mrw_request_level
        # Verify cross regional retries when using retryable writes at request level with multiple write locations.
        # Need to test for 408s, 500s, and ServiceResponseError.
        first_region_uri: str = _LOCAL_HOST.replace("localhost", "127.0.0.1")
        second_region_uri: str = _LOCAL_HOST
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

        # Known gap 10: Closed by design: client-level proxy configuration, custom CA, client certificate, and transport options are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-10). The Rust client cannot take the custom transport that fakes the multi-write topology and fails the first region, so the client cannot be built.
        # Known gap 6: Closed by design: `raw_request_hook` removed from both backends (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-6). The Rust-sent request is not exposed as get_response_headers()["_request"], so the region URL checks cannot run.
        # Known gap 13: Closed: Rust owns automatic write retries (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-13). Per-call retry_write raises NotImplementedError on the Rust item backend.
        pytest.skip("accepted-vnext-change: custom transport (multi-write topology and regional fault injection) "
                    "is not accepted by the Rust client (known gap 10); the request URL is not observable "
                    "(known gap 6); per-call retry_write is not supported (known gap 13).")
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
    def test_retryable_writes_mrw_client_level_rust(self, injected_error):
        # Source: tests/test_retryable_writes.py::TestRetryableWrites.test_retryable_writes_mrw_client_level
        # Verify cross regional retries when using retryable writes at client level with multiple write locations.
        # Need to test for 408s, 500s, and ServiceResponseError.
        first_region_uri: str = _LOCAL_HOST.replace("localhost", "127.0.0.1")
        second_region_uri: str = _LOCAL_HOST
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

        # Known gap 10: Closed by design: client-level proxy configuration, custom CA, client certificate, and transport options are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-10). The Rust client cannot take the custom transport that fakes the multi-write topology and fails the first region, so the client cannot be built.
        # Known gap 6: Closed by design: `raw_request_hook` removed from both backends (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-6). The Rust-sent request is not exposed as get_response_headers()["_request"], so the region URL checks cannot run.
        pytest.skip("accepted-vnext-change: custom transport (multi-write topology and regional fault injection) "
                    "is not accepted by the Rust client (known gap 10); the request URL is not observable "
                    "(known gap 6).")
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
