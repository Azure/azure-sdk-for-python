# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Rust-path copies of the async retryable-writes tests that exercise replace_item.

The originals patch ``_retry_utility_async.ExecuteFunctionAsync`` to fail the first
attempt of each write with a 408 and count attempts. The Rust backend does not use
that Python retry utility, so these copies inject the same first-attempt 408 with Rust
fault injection rules and count attempts from the ``requests=N`` value in the
``x-ms-cosmos-sdk-diagnostics`` response header. Steps and assertions are unchanged.
"""

import asyncio
import os
import re
import uuid
from typing import Callable

import pytest
import pytest_asyncio
from azure.core.exceptions import ServiceResponseError
from azure.core.pipeline.transport._aiohttp import AioHttpTransport
from azure.core.rest import HttpRequest

from azure.cosmos import exceptions, ContainerProxy, DatabaseProxy
from azure.cosmos.aio import CosmosClient
from azure.cosmos.partition_key import PartitionKey
from _fault_injection_transport_async import FaultInjectionTransportAsync

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


@pytest_asyncio.fixture()
async def setup():
    test_client = CosmosClient(_host(), _key(), _backend="rust")
    await test_client.__aenter__()
    database = await test_client.create_database(id="replace_item_retryable_writes_async_" + uuid.uuid4().hex)
    try:
        created_container = await database.create_container_if_not_exists(
            id=SINGLE_PARTITION_CONTAINER,
            partition_key=PartitionKey(path="/pk")
        )
        container_hpk = await database.create_container_if_not_exists(
            id=HPK_CONTAINER,
            partition_key=PartitionKey(path=["/state", "/city"], kind="MultiHash")
        )
        yield {"database": database, "container": created_container, "container_hpk": container_hpk}
    finally:
        await test_client.delete_database(database.id)
        await test_client.close()


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
@pytest.mark.asyncio
@pytest.mark.usefixtures("setup")
class TestRetryableWritesAsync:
    """Rust-path copies of tests/test_retryable_writes_async.py::TestRetryableWritesAsync."""
    TEST_DATABASE_ID = "replace_item_retryable_writes_mrw_async_" + uuid.uuid4().hex
    TEST_CONTAINER_SINGLE_PARTITION_ID = SINGLE_PARTITION_CONTAINER

    @staticmethod
    async def setup_method_with_custom_transport(
            custom_transport: AioHttpTransport,
            default_endpoint: str = None,
            key: str = None,
            database_id: str = TEST_DATABASE_ID,
            container_id: str = TEST_CONTAINER_SINGLE_PARTITION_ID,
            **kwargs):
        client = CosmosClient(default_endpoint or _host(), key or _key(), consistency_level="Session",
                              transport=custom_transport, enable_diagnostics_logging=True, _backend="rust", **kwargs)
        await client.__aenter__()
        db: DatabaseProxy = await client.create_database_if_not_exists(database_id)
        container: ContainerProxy = await db.create_container_if_not_exists(container_id, PartitionKey(path="/pk"))
        return {"client": client, "db": db, "col": container}

    @staticmethod
    async def cleanup_method(initialized_objects):
        # Stand-in for TestFaultInjectionTransportAsync.cleanup_method: close the method client.
        await initialized_objects["client"].close()

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

        async def close(self):
            for client in self._clients:
                await client.close()

    @pytest.mark.skip(
        reason="accepted-vnext-change: Gap 13 - This copied legacy test expects upsert_item "
        "to fail without retrying when retry_write is omitted. Rust decides which write "
        "failures to retry automatically, so omitting retry_write does not disable retries."
    )
    async def test_retryable_writes_request_level_async_rust(self, setup):
        # Source: tests/test_retryable_writes_async.py::TestRetryableWritesAsync.test_retryable_writes_request_level_async
        container = setup['container']
        database_id = setup['database'].id
        mocks = []
        try:
            # Mock retry_utility.execute to track retries
            me = self.MockExecuteFunction(database_id, container.id)
            mocks.append(me)

            # Test without retry_write for upsert_item
            test_item = {"id": "1", "pk": "test", "data": "retryable write test"}
            # Known gap 13: Closed: Rust owns automatic write retries (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-13). Rust retries the injected 408 itself, so the write may succeed instead of raising.
            try:
                await me.container.upsert_item(test_item)
                pytest.fail("Expected an exception without retry_write")
            except exceptions.CosmosHttpResponseError:
                assert me.counter == 1, "Expected no retries without retry_write"

            # Test with retry_write for upsert_item
            me.counter = 0  # Reset counter
            # Known gap 13: Closed: Rust owns automatic write retries (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-13). Per-call retry_write raises NotImplementedError on the Rust item backend before any request is sent.
            pytest.skip("accepted-vnext-change: per-call retry_write is not supported on the Rust backend (known gap 13).")
            try:
                await me.container.upsert_item(test_item, retry_write=2)
            except exceptions.CosmosHttpResponseError as e:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"

            # Verify the item was written
            read_item = await container.read_item(item=test_item['id'], partition_key=test_item['pk'])
            assert read_item['id'] == test_item['id'], "Item was not written successfully after retries"

            # Mock retry_utility.execute to track retries
            me = self.MockExecuteFunction(database_id, container.id)
            mocks.append(me)

            # Test without retry_write for create_item
            test_item_create = {"id": "2", "pk": "test", "data": "retryable create test"}
            try:
                await me.container.create_item(test_item_create)
                pytest.fail("Expected an exception without retry_write")
            except exceptions.CosmosHttpResponseError:
                assert me.counter == 1, "Expected no retries without retry_write"

            # Test with retry_write for create_item
            me.counter = 0  # Reset counter
            try:
                await me.container.create_item(test_item_create, retry_write=2)
            except exceptions.CosmosHttpResponseError as e:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"

            # Verify the item was created
            read_item_create = await container.read_item(item=test_item_create['id'],
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
                await me.container.patch_item(item=test_item_create['id'], partition_key=test_item_create['pk'],
                                              patch_operations=test_patch_operations)
                pytest.fail("Expected an exception without retry_write")
            except exceptions.CosmosHttpResponseError:
                assert me.counter == 1, "Expected no retries without retry_write"

            # Test with retry_write for patch_item
            me.counter = 0  # Reset counter
            try:
                await me.container.patch_item(item=test_item_create['id'], partition_key=test_item_create['pk'],
                                              patch_operations=test_patch_operations, retry_write=2)
            except exceptions.CosmosHttpResponseError as e:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"

            # Verify the item was patched
            patched_item = await container.read_item(item=test_item_create['id'], partition_key=test_item_create['pk'])
            assert patched_item['data'] == "patched retryable write test", "Item was not patched successfully after retries"

            # Verify original execution function is used to upsert an item
            test_item = {"id": "5", "pk": "test", "data": "retryable write test"}
            await container.upsert_item(test_item)

            # Mock retry_utility.execute to track retries
            me = self.MockExecuteFunction(database_id, container.id)
            mocks.append(me)

            # Verify delete_item does not retry
            me.counter = 0  # Reset counter
            try:
                await me.container.delete_item(item=test_item['id'], partition_key=test_item['pk'])
                pytest.fail("Expected an exception without retry_write")
            except exceptions.CosmosHttpResponseError:
                assert me.counter == 1, "Expected no retries for delete_item"

            # Verify the item was not deleted
            read_item = await container.read_item(item=test_item['id'], partition_key=test_item['pk'])
            assert read_item['id'] == test_item['id'], "Item was unexpectedly deleted"

            # Mock retry_utility.execute to track retries
            me = self.MockExecuteFunction(database_id, container.id)
            mocks.append(me)

            me.counter = 0  # Reset counter
            try:
                await me.container.delete_item(item=test_item['id'], partition_key=test_item['pk'], retry_write=2)
            except exceptions.CosmosHttpResponseError:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"

            try:
                await container.read_item(item=test_item['id'], partition_key=test_item['pk'])
                pytest.fail("Expected an exception for item that should have been deleted")
            except exceptions.CosmosHttpResponseError as e:
                assert e.status_code == 404, "Expected item to be deleted but it was not"

            # Now we test it out with a replace request without retry write enabled - which should not retry

            # First create an item to replace
            test_item_replace = {"id": str(uuid.uuid4()), "pk": "test", "data": "replace test"}
            await container.create_item(test_item_replace)

            # Mock execute function
            me = self.MockExecuteFunction(database_id, container.id)
            mocks.append(me)
            me.counter = 0  # Reset counter
            try:
                await me.container.replace_item(item=test_item_replace['id'], body={"id": test_item_replace['id'],
                                                                                     "pk": "test",
                                                                                     "data": "original data"})
                pytest.fail("Expected an exception without retry_write")
            except exceptions.CosmosHttpResponseError:
                assert me.counter == 1, "Expected no retries for replace_item without retry_write"

            # Test with retry_write for replace_item
            me.counter = 0  # Reset counter
            try:
                await me.container.replace_item(item=test_item_replace['id'], body={"id": test_item_replace['id'],
                                                                                     "pk": "test",
                                                                                     "data": "replaced data"},
                                                retry_write=2)
            except exceptions.CosmosHttpResponseError as e:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"

            # Verify the item was replaced
            read_item_replace = await container.read_item(item=test_item_replace['id'],
                                                          partition_key=test_item_replace['pk'])
            assert read_item_replace['data'] == "replaced data", "Item was not replaced successfully after retries"
        finally:
            for mock in mocks:
                await mock.close()

    async def test_retryable_writes_client_level_write_rust(self, setup):
        # Source: tests/test_retryable_writes_async.py::TestRetryableWritesAsync.test_retryable_writes_client_level_write
        """Test retryable writes for a container with retry_write set at the client level."""

        # Create a client with retry_write enabled
        client_with_retry = CosmosClient(_host(), credential=_key(), retry_write=2, _backend="rust")
        await client_with_retry.__aenter__()
        database_id = setup['database'].id
        mocks = []

        try:
            container = client_with_retry.get_database_client(database_id).get_container_client(
                setup['container'].id)

            # Mock retry_utility.execute to track retries
            me = self.MockExecuteFunction(database_id, container.id, retry_write=2)
            mocks.append(me)

            # Test upsert_item
            test_item = {"id": "4", "pk": "test", "data": "retryable write test"}
            try:
                await me.container.upsert_item(test_item)
            except exceptions.CosmosHttpResponseError as e:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"

            # Test create_item
            me.counter = 0  # Reset counter
            test_item_create = {"id": "5", "pk": "test", "data": "retryable create test"}
            try:
                await me.container.create_item(test_item_create)
            except exceptions.CosmosHttpResponseError as e:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"

            # Test patch_item
            me.counter = 0  # Reset counter
            test_patch_operations = [
                {"op": "add", "path": "/data", "value": "patched retryable write test"}
            ]
            # Known gap 13: Closed: Rust owns automatic write retries (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-13). Rust retries the injected 408 on the replace leg of its client-side patch, so patch may succeed instead of raising.
            try:
                await me.container.patch_item(item=test_item['id'], partition_key=test_item['pk'],
                                              patch_operations=test_patch_operations)
                pytest.fail("Expected an exception without retries")
            except exceptions.CosmosHttpResponseError:
                assert me.counter == 1, "Expected no retries for patch_item with client_retry_write"

            # Verify original execution function is used to upsert an item
            test_item = {"id": "4", "pk": "test", "data": "retryable write test"}
            await container.upsert_item(test_item)

            # Mock retry_utility.execute to track retries
            me = self.MockExecuteFunction(database_id, container.id, retry_write=2)
            mocks.append(me)

            # Verify delete_item does not retry
            me.counter = 0  # Reset counter
            try:
                await me.container.delete_item(item=test_item['id'], partition_key=test_item['pk'])
            except exceptions.CosmosHttpResponseError:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"

            # Verify the item was deleted
            try:
                await container.read_item(item=test_item['id'], partition_key=test_item['pk'])
                pytest.fail("Expected an exception for item that should have been deleted")
            except exceptions.CosmosHttpResponseError as e:
                assert e.status_code == 404, "Expected item to be deleted but it was not"

            # Test replace item on client level with retry_write enabled
            # First create an item to replace
            test_item_replace = {"id": str(uuid.uuid4()), "pk": "test", "data": "original data"}
            await container.create_item(test_item_replace)
            # Mock execute function
            me = self.MockExecuteFunction(database_id, container.id, retry_write=2)
            mocks.append(me)
            me.counter = 0  # Reset counter
            try:
                await me.container.replace_item(item=test_item_replace['id'], body={"id": test_item_replace['id'],
                                                                                     "pk": "test",
                                                                                     "data": "replaced data"})
            except exceptions.CosmosHttpResponseError:
                assert me.counter > 1, "Expected multiple retries for replace_item with retry_write enabled"
            # Verify the item was replaced
            read_item_replace = await container.read_item(item=test_item_replace['id'],
                                                          partition_key=test_item_replace['pk'])
            assert read_item_replace['data'] == "replaced data", "Item was not replaced successfully after retries"
        finally:
            for mock in mocks:
                await mock.close()
            if client_with_retry:
                await client_with_retry.close()

    @pytest.mark.skip(
        reason="accepted-vnext-change: Gap 13 - This copied legacy test expects upsert_item "
        "to fail without retrying when retry_write is omitted. Rust decides which write "
        "failures to retry automatically, so omitting retry_write does not disable retries."
    )
    async def test_retryable_writes_hpk_request_level_async_rust(self, setup):
        # Source: tests/test_retryable_writes_async.py::TestRetryableWritesAsync.test_retryable_writes_hpk_request_level_async
        """Test retryable writes for a container with hierarchical partition keys."""
        container = setup['container_hpk']
        database_id = setup['database'].id
        mocks = []
        try:
            # Mock retry_utility.execute to track retries
            me = self.MockExecuteFunction(database_id, container.id)
            mocks.append(me)

            # Test without retry_write for upsert_item
            test_item = {"id": "1", "state": "CA", "city": "San Francisco", "data": "retryable write test"}
            # Known gap 13: Closed: Rust owns automatic write retries (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-13). Rust retries the injected 408 itself, so the write may succeed instead of raising.
            try:
                await me.container.upsert_item(test_item)
                pytest.fail("Expected an exception without retry_write")
            except exceptions.CosmosHttpResponseError:
                assert me.counter == 1, "Expected no retries without retry_write"

            # Test with retry_write for upsert_item
            me.counter = 0  # Reset counter
            # Known gap 13: Closed: Rust owns automatic write retries (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-13). Per-call retry_write raises NotImplementedError on the Rust item backend before any request is sent.
            pytest.skip("accepted-vnext-change: per-call retry_write is not supported on the Rust backend (known gap 13).")
            try:
                await me.container.upsert_item(test_item, retry_write=2)
            except exceptions.CosmosHttpResponseError as e:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"

            # Verify the item was written
            read_item = await container.read_item(item=test_item['id'], partition_key=[test_item['state'],
                                                                                       test_item['city']])
            assert read_item['id'] == test_item['id'], "Item was not written successfully after retries"

            # Mock retry_utility.execute to track retries
            me = self.MockExecuteFunction(database_id, container.id)
            mocks.append(me)

            # Test without retry_write for create_item
            test_item_create = {"id": "2", "state": "NY", "city": "New York", "data": "retryable create test"}
            try:
                await me.container.create_item(test_item_create)
                pytest.fail("Expected an exception without retry_write")
            except exceptions.CosmosHttpResponseError:
                assert me.counter == 1, "Expected no retries without retry_write"

            # Test with retry_write for create_item
            me.counter = 0  # Reset counter
            try:
                await me.container.create_item(test_item_create, retry_write=2)
            except exceptions.CosmosHttpResponseError as e:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"

            # Verify the item was created
            read_item_create = await container.read_item(item=test_item_create['id'],
                                                         partition_key=[test_item_create['state'],
                                                                        test_item_create['city']])
            assert read_item_create['id'] == test_item_create['id'], "Item was not created successfully after retries"

            # Mock retry_utility.execute to track retries
            me = self.MockExecuteFunction(database_id, container.id)
            mocks.append(me)

            test_patch_operations = [
                {"op": "add", "path": "/year", "value": "2025"}
            ]
            # Test without retry_write for patch_item
            try:
                await me.container.patch_item(item=test_item['id'],
                                              partition_key=[test_item['state'], test_item['city']],
                                              patch_operations=test_patch_operations)
                pytest.fail("Expected an exception without retry_write")
            except exceptions.CosmosHttpResponseError:
                assert me.counter == 1, "Expected no retries without retry_write"

            # Now properly replace with retry_write
            me.counter = 0  # Reset counter
            await me.container.patch_item(item=test_item['id'],
                                          partition_key=[test_item['state'], test_item['city']],
                                          patch_operations=test_patch_operations,
                                          retry_write=2)
            assert me.counter == 2

            # Verify the item was patched
            patched_item = await container.read_item(item=test_item['id'],
                                                     partition_key=[test_item['state'],
                                                                    test_item['city']])
            assert patched_item['year'] == "2025", "Item was not patched successfully after retries"

            # Verify original execution function is used to upsert an item
            test_item = {"id": "1", "state": "CA", "city": "San Francisco", "data": "retryable write test"}
            await container.upsert_item(test_item)

            # Mock retry_utility.execute to track retries
            me = self.MockExecuteFunction(database_id, container.id)
            mocks.append(me)

            # Verify delete_item does not retry
            me.counter = 0  # Reset counter
            try:
                await me.container.delete_item(item=test_item['id'],
                                               partition_key=[test_item['state'], test_item['city']])
            except exceptions.CosmosHttpResponseError:
                assert me.counter == 1, "Expected no retries for delete_item"

            me.counter = 0  # Reset counter
            try:
                await me.container.delete_item(item=test_item['id'],
                                               partition_key=[test_item['state'], test_item['city']],
                                               retry_write=2)
            except exceptions.CosmosHttpResponseError:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"

            # Verify the item was deleted
            try:
                await container.read_item(item=test_item['id'], partition_key=[test_item['state'], test_item['city']])
                pytest.fail("Expected an exception for item that should have been deleted")
            except exceptions.CosmosHttpResponseError as e:
                assert e.status_code == 404, "Expected item to be deleted but it was not"

            # Now we test it out with a replace request without retry write enabled - which should not retry
            # First create an item to replace
            test_item_replace = {"id": str(uuid.uuid4()), "state": "TX", "city": "Austin", "data": "replace test"}
            await container.create_item(test_item_replace)
            # Mock execute function
            me = self.MockExecuteFunction(database_id, container.id)
            mocks.append(me)
            me.counter = 0  # Reset counter
            try:
                await me.container.replace_item(item=test_item_replace['id'], body={"id": test_item_replace['id'],
                                                                                     "state": "TX",
                                                                                     "city": "Austin",
                                                                                     "data": "original data"})
                pytest.fail("Expected an exception without retry_write")
            except exceptions.CosmosHttpResponseError:
                assert me.counter == 1, "Expected no retries for replace_item without retry_write"
            # Test with retry_write for replace_item
            me.counter = 0  # Reset counter
            try:
                await me.container.replace_item(item=test_item_replace['id'], body={"id": test_item_replace['id'],
                                                                                     "state": "TX",
                                                                                     "city": "Austin",
                                                                                     "data": "replaced data"},
                                                retry_write=2)
            except exceptions.CosmosHttpResponseError as e:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"

            # Verify the item was replaced
            read_item_replace = await container.read_item(item=test_item_replace['id'],
                                                          partition_key=[test_item_replace['state'],
                                                                         test_item_replace['city']])
            assert read_item_replace['data'] == "replaced data", "Item was not replaced successfully after retries"
        finally:
            for mock in mocks:
                await mock.close()

    @pytest.mark.skip(
        reason="accepted-vnext-change: Gap 13 - This copied legacy test expects patch_item "
        "to fail without retrying, even when retry_write is set on the client. "
        "Rust decides which write failures to retry automatically, so it does not "
        "preserve this legacy no-retry guarantee."
    )
    async def test_retryable_writes_hpk_client_level_async_rust(self, setup):
        # Source: tests/test_retryable_writes_async.py::TestRetryableWritesAsync.test_retryable_writes_hpk_client_level_async
        """Test retryable writes for a container with hierarchical partition keys and retry_write
        set at the client level."""
        # Create a client with retry_write enabled
        client_with_retry = CosmosClient(_host(), credential=_key(), retry_write=2, _backend="rust")
        await client_with_retry.__aenter__()
        database_id = setup['database'].id
        mocks = []
        try:
            container = client_with_retry.get_database_client(database_id).get_container_client(
                setup['container_hpk'].id)

            # Mock retry_utility.execute to track retries
            me = self.MockExecuteFunction(database_id, container.id, retry_write=2)
            mocks.append(me)

            # Test upsert_item
            test_item = {"id": "6", "state": "CA", "city": "San Francisco", "data": "retryable write test"}
            try:
                await me.container.upsert_item(test_item)
            except exceptions.CosmosHttpResponseError as e:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"

            # Test create_item
            me.counter = 0  # Reset counter
            test_item_create = {"id": "7", "state": "NY", "city": "New York", "data": "retryable create test"}
            try:
                await me.container.create_item(test_item_create)
            except exceptions.CosmosHttpResponseError as e:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"

            # Test patch_item
            me.counter = 0  # Reset counter
            test_patch_operations_hpk = [
                {"op": "add", "path": "/data", "value": "patched retryable write test"}
            ]
            # Known gap 13: Closed: Rust owns automatic write retries (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-13). Rust retries the injected 408 on the replace leg of its client-side patch, so patch may succeed instead of raising.
            try:
                await me.container.patch_item(item=test_item['id'],
                                              partition_key=[test_item['state'], test_item['city']],
                                              patch_operations=test_patch_operations_hpk)
                pytest.fail("Expected an exception without retries")
            except exceptions.CosmosHttpResponseError:
                assert me.counter == 1, "Expected no retries for patch_item with client_retry_write"

            test_item = {"id": "6", "state": "CA", "city": "San Francisco", "data": "retryable write test"}
            await container.upsert_item(test_item)

            # Mock retry_utility.execute to track retries
            me = self.MockExecuteFunction(database_id, container.id, retry_write=2)
            mocks.append(me)

            # Verify delete_item does not retry
            me.counter = 0  # Reset counter
            try:
                await me.container.delete_item(item=test_item['id'],
                                               partition_key=[test_item['state'], test_item['city']])
            except exceptions.CosmosHttpResponseError:
                assert me.counter > 1, "Expected multiple retries due to simulated errors"

            # Verify the item was deleted
            try:
                await container.read_item(item=test_item['id'], partition_key=[test_item['state'], test_item['city']])
                pytest.fail("Expected an exception for item that should have been deleted")
            except exceptions.CosmosHttpResponseError as e:
                assert e.status_code == 404, "Expected item to be deleted but it was not"

            # Now we try a replace request with retry write enabled - which should retry once

            # Create an item to replace
            test_item_replace = {"id": str(uuid.uuid4()), "state": "TX", "city": "Austin", "data": "original data"}
            await container.create_item(test_item_replace)
            # Mock execute function
            me = self.MockExecuteFunction(database_id, container.id, retry_write=2)
            mocks.append(me)
            me.counter = 0  # Reset counter
            try:
                await me.container.replace_item(item=test_item_replace['id'], body={"id": test_item_replace['id'],
                                                                                     "state": "TX",
                                                                                     "city": "Austin",
                                                                                     "data": "replaced data"})
            except exceptions.CosmosHttpResponseError:
                assert me.counter > 1, "Expected multiple retries for replace_item with retry_write enabled"
            # Verify the item was replaced
            read_item_replace = await container.read_item(item=test_item_replace['id'],
                                                          partition_key=[test_item_replace['state'],
                                                                         test_item_replace['city']])
            assert read_item_replace['data'] == "replaced data", "Item was not replaced successfully after retries"

        finally:
            for mock in mocks:
                await mock.close()
            await client_with_retry.close()

    @pytest.mark.parametrize("injected_error", [FaultInjectionTransportAsync.error_request_timeout(),
                             FaultInjectionTransportAsync.error_internal_server_error(),
                             FaultInjectionTransportAsync.error_service_response()])
    async def test_retryable_writes_mrw_request_level_async_rust(self, injected_error):
        # Source: tests/test_retryable_writes_async.py::TestRetryableWritesAsync.test_retryable_writes_mrw_request_level_async
        first_region_uri: str = _LOCAL_HOST.replace("localhost", "127.0.0.1")
        second_region_uri: str = _LOCAL_HOST
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

        # Known gap 10: Closed by design: client-level proxy configuration, custom CA, client certificate, and transport options are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-10). The Rust client cannot take the custom transport that fakes the multi-write topology and fails the first region, so the client cannot be built.
        # Known gap 6: Closed by design: `raw_request_hook` removed from both backends (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-6). The Rust-sent request is not exposed as get_response_headers()["_request"], so the region URL checks cannot run.
        # Known gap 13: Closed: Rust owns automatic write retries (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-13). Per-call retry_write raises NotImplementedError on the Rust item backend.
        pytest.skip("accepted-vnext-change: custom transport (multi-write topology and regional fault injection) "
                    "is not accepted by the Rust client (known gap 10); the request URL is not observable "
                    "(known gap 6); per-call retry_write is not supported (known gap 13).")
        initialized_objects = await self.setup_method_with_custom_transport(
            custom_transport,
            preferred_locations=["First Region", "Second Region"],
            multiple_write_locations=True
        )
        try:
            container: ContainerProxy = initialized_objects["col"]

            create_document = await container.create_item(body=document_definition, retry_write=2)
            request = create_document.get_response_headers()["_request"]
            assert request.url.startswith(second_region_uri)

            upsert_document = await container.upsert_item(body=document_definition, retry_write=2)
            request = upsert_document.get_response_headers()["_request"]
            assert request.url.startswith(second_region_uri)

            replace_document = await container.replace_item(item=document_definition['id'], body=document_definition,
                                                      retry_write=2)
            request = replace_document.get_response_headers()["_request"]
            assert request.url.startswith(second_region_uri)

            operations = [{"op": "add", "path": "/favorite_color", "value": "red"}, ]
            patch_document = await container.patch_item(item=document_definition['id'],
                                                  partition_key=document_definition['pk'],
                                                  patch_operations=operations, retry_write=2)
            request = patch_document.get_response_headers()["_request"]
            assert request.url.startswith(second_region_uri)

        finally:
            await self.cleanup_method(initialized_objects)

    @pytest.mark.parametrize("injected_error", [FaultInjectionTransportAsync.error_request_timeout(),
                             FaultInjectionTransportAsync.error_internal_server_error(),
                             FaultInjectionTransportAsync.error_service_response()])
    async def test_retryable_writes_mrw_client_level_async_rust(self, injected_error):
        # Source: tests/test_retryable_writes_async.py::TestRetryableWritesAsync.test_retryable_writes_mrw_client_level_async
        first_region_uri: str = _LOCAL_HOST.replace("localhost", "127.0.0.1")
        second_region_uri: str = _LOCAL_HOST
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

        # Known gap 10: Closed by design: client-level proxy configuration, custom CA, client certificate, and transport options are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-10). The Rust client cannot take the custom transport that fakes the multi-write topology and fails the first region, so the client cannot be built.
        # Known gap 6: Closed by design: `raw_request_hook` removed from both backends (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-6). The Rust-sent request is not exposed as get_response_headers()["_request"], so the region URL checks cannot run.
        pytest.skip("accepted-vnext-change: custom transport (multi-write topology and regional fault injection) "
                    "is not accepted by the Rust client (known gap 10); the request URL is not observable "
                    "(known gap 6).")
        initialized_objects = await self.setup_method_with_custom_transport(
            custom_transport,
            preferred_locations=["First Region", "Second Region"],
            multiple_write_locations=True,
            retry_write=2
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
            await self.cleanup_method(initialized_objects)
