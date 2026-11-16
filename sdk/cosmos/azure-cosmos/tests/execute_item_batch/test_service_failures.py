# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Real native batch faults with independent storage checks and same-client recovery.

Pre-service faults prove absence, not lost responses. Post-service faults forward
the transaction before discarding its response; storage, not a reserved fault hit,
establishes commit before timeout/cancellation. No account topology is modified.
"""

import asyncio
from contextlib import AsyncExitStack
from copy import deepcopy
import inspect
from types import SimpleNamespace
from unittest.mock import Mock
import uuid

import pytest
import pytest_asyncio

from azure.core.exceptions import ServiceResponseError
from azure.cosmos import CosmosRuntime, PartitionKey, _rust, exceptions
from common.throughput_fixtures import owned_database
from config import clients, resources, settings
from fault_injection._query_resume import set_rule

pytestmark = [pytest.mark.cosmosEmulator, pytest.mark.cosmosAADLong, pytest.mark.asyncio]


async def invoke(method, *args, **kwargs):
    if inspect.iscoroutinefunction(method):
        return await method(*args, **kwargs)
    return await asyncio.to_thread(method, *args, **kwargs)


@pytest.fixture(scope="module", name="batch_database")
def _batch_database_fixture():
    with clients.create_setup_client(timeout=30) as client:
        with owned_database(client, settings.unique_database_id("batch-failures")) as database:
            yield database


@pytest.fixture(name="observer")
def _observer_fixture(batch_database):
    identifier = "orders_" + uuid.uuid4().hex
    owned = True
    try:
        try:
            container = resources.create_owned_container(
                batch_database, id=identifier, partition_key=PartitionKey("/pk")
            )
        except exceptions.CosmosResourceExistsError:
            owned = False
            raise
        yield container
    finally:
        if owned:
            try:
                resources.retry_control_plane(batch_database.delete_container, identifier)
            except exceptions.CosmosResourceNotFoundError:
                pass


@pytest.fixture(name="asynchronous", params=[False, True], ids=["sync", "async"])
def _asynchronous_fixture(request):
    return request.param


@pytest_asyncio.fixture(name="fault_client")
async def _fault_client_fixture(asynchronous, batch_database, observer, monkeypatch):
    async with AsyncExitStack() as stack:

        async def make(rules=(), **kwargs):
            factory = clients.create_data_client_async if asynchronous else clients.create_data_client
            client = factory(
                _backend="rust",
                consistency_level="Session",
                timeout=30,
                retry_throttle_total=0,
                _fault_injection_rules=rules,
                **kwargs
            )
            if asynchronous:
                await stack.enter_async_context(client)
            else:
                stack.enter_context(client)
            handle = await invoke(client._adapter._ensure_driver_handle)
            container = client.get_database_client(batch_database.id).get_container_client(observer.id)
            name = "execute_item_batch_async" if asynchronous else "execute_item_batch"
            native = Mock(wraps=getattr(_rust, name))
            monkeypatch.setattr(_rust, name, native)
            monkeypatch.setattr(
                client.client_connection,
                "Batch",
                Mock(side_effect=AssertionError("Rust batch called legacy Batch")),
            )
            return SimpleNamespace(client=client, container=container, handle=handle, native=native)

        yield make


def rule(observer, operation_type="BatchItem", **result):
    return {
        "id": uuid.uuid4().hex,
        "operation_type": operation_type,
        "container_id": observer.id,
        "probability": 1.0,
        **result,
    }


@pytest.fixture(name="transaction")
def _transaction_fixture(observer):
    key = uuid.uuid4().hex
    seed = {"id": "seed", "pk": key, "value": 0}
    observer.create_item(seed)
    return [
        ("create", ({"id": "first", "pk": key, "value": 1},)),
        ("replace", ("seed", dict(seed, value=1))),
        ("create", ({"id": "last", "pk": key, "value": 1},)),
    ]


def partition_key(operations):
    return operations[0][1][0]["pk"]


async def assert_state(observer, operations, *, committed):
    key = partition_key(operations)
    seed = await invoke(observer.read_item, "seed", partition_key=key)
    assert seed["value"] == (1 if committed else 0)
    for identifier in ("first", "last"):
        if committed:
            item = await invoke(observer.read_item, identifier, partition_key=key)
            assert (item["id"], item["pk"], item["value"]) == (identifier, key, 1)
        else:
            with pytest.raises(exceptions.CosmosResourceNotFoundError) as missing:
                await invoke(observer.read_item, identifier, partition_key=key)
            assert missing.value.status_code == 404


async def wait_for_commit(observer, operations):
    key = partition_key(operations)
    while True:
        try:
            await invoke(observer.read_item, "last", partition_key=key)
        except exceptions.CosmosResourceNotFoundError as missing:
            assert missing.status_code == 404
            await asyncio.sleep(0.05)
        else:
            await assert_state(observer, operations, committed=True)
            return


async def wait_for_fault(handle, identifier):
    while not await asyncio.to_thread(_rust._debug_fault_injection_rule_hit_count, handle, identifier):
        await asyncio.sleep(0.01)


async def recover(run, observer, operations, faults, *, committed):
    for fault in faults:
        set_rule(run.handle, fault["id"], False)
    key = partition_key(operations)
    run.native.reset_mock()
    if committed:
        replay = deepcopy(operations)
        replay[1][1][1]["value"] = 99
        with pytest.raises(exceptions.CosmosBatchOperationError) as duplicate:
            await invoke(run.container.execute_item_batch, replay, key)
        assert (duplicate.value.status_code, duplicate.value.error_index) == (409, 0)
        assert [item["statusCode"] for item in duplicate.value.operation_responses] == [409, 424, 424]
        await assert_state(observer, operations, committed=True)
        run.native.assert_called_once()
        operations = deepcopy(operations)
        operations[0][1][0]["id"] = "recovered-first"
        operations[2][1][0]["id"] = "recovered-last"
        run.native.reset_mock()
    results = await invoke(run.container.execute_item_batch, operations, key)
    run.native.assert_called_once()
    assert [item["statusCode"] for item in results] == [201, 200, 201]
    for operation in (operations[0], operations[2]):
        body = operation[1][0]
        actual = await invoke(observer.read_item, body["id"], partition_key=key)
        assert all(actual[field] == value for field, value in body.items())
    assert (await invoke(observer.read_item, "seed", partition_key=key))["value"] == 1


@pytest.mark.parametrize("error_type", ["ConnectionError", "ResponseTimeout"])
async def test_batch_unsent_transport_failure_and_recovery_rust(fault_client, observer, transaction, error_type):
    fault = rule(observer, error_type=error_type)
    run = await fault_client([fault])
    await invoke(run.container.read)
    hook = Mock()
    with pytest.raises(ServiceResponseError) as caught:
        await invoke(run.container.execute_item_batch, transaction, partition_key(transaction), response_hook=hook)
    assert caught.value.__cause__.__class__.__name__ == "_DriverTransportError"
    run.native.assert_called_once()
    hook.assert_not_called()
    assert _rust._debug_fault_injection_rule_hit_count(run.handle, fault["id"]) > 0
    await assert_state(observer, transaction, committed=False)
    await recover(run, observer, transaction, [fault], committed=False)


async def test_batch_lost_success_response_preserves_atomic_commit_rust(fault_client, observer, transaction):
    fault = rule(observer, error_type="ResponseTimeoutAfterService", hit_limit=1)
    run = await fault_client([fault])
    await invoke(run.container.read)
    hook = Mock()
    with pytest.raises((ServiceResponseError, exceptions.CosmosBatchOperationError)) as caught:
        await invoke(run.container.execute_item_batch, transaction, partition_key(transaction), response_hook=hook)
    if isinstance(caught.value, exceptions.CosmosBatchOperationError):
        assert (caught.value.status_code, caught.value.error_index) == (409, 0)
        assert [item["statusCode"] for item in caught.value.operation_responses] == [409, 424, 424]
    else:
        assert caught.value.__cause__.__class__.__name__ == "_DriverTransportError"
    run.native.assert_called_once()
    hook.assert_not_called()
    assert _rust._debug_fault_injection_rule_hit_count(run.handle, fault["id"]) == 1
    await assert_state(observer, transaction, committed=True)
    await recover(run, observer, transaction, [fault], committed=True)


@pytest.mark.parametrize("after_service", [False, True], ids=["before-service", "after-commit"])
async def test_batch_deadline_and_recovery_rust(fault_client, observer, transaction, after_service):
    result = {"error_type": "ResponseTimeoutAfterService"} if after_service else {"status_code": 502}
    fault = rule(observer, **result, delay_ms=30000, hit_limit=1)
    run = await fault_client([fault])
    await invoke(run.container.read)
    hook = Mock()
    pending = asyncio.create_task(
        invoke(
            run.container.execute_item_batch, transaction, partition_key(transaction), timeout=15, response_hook=hook
        )
    )
    try:
        if after_service:
            await asyncio.wait_for(wait_for_commit(observer, transaction), timeout=10)
            assert not pending.done(), "Batch response was not held after commit"
        with pytest.raises(exceptions.CosmosClientTimeoutError):
            await asyncio.wait_for(pending, timeout=20)
    finally:
        if not pending.done():
            pending.cancel()
            with pytest.raises(asyncio.CancelledError):
                await pending
    run.native.assert_called_once()
    hook.assert_not_called()
    assert _rust._debug_fault_injection_rule_hit_count(run.handle, fault["id"]) <= 1
    if not after_service:
        assert _rust._debug_fault_injection_rule_hit_count(run.handle, fault["id"]) == 1
    await assert_state(observer, transaction, committed=after_service)
    await recover(run, observer, transaction, [fault], committed=after_service)


@pytest.mark.parametrize("asynchronous", [True], ids=["async"])
@pytest.mark.parametrize("after_service", [False, True], ids=["before-service", "after-commit"])
async def test_batch_cancellation_and_recovery_rust(fault_client, observer, transaction, after_service):
    result = {"error_type": "ResponseTimeoutAfterService"} if after_service else {"status_code": 502}
    fault = rule(observer, **result, delay_ms=30000, hit_limit=1)
    run = await fault_client([fault])
    await run.container.read()
    hook = Mock()
    pending = asyncio.create_task(
        run.container.execute_item_batch(transaction, partition_key(transaction), response_hook=hook)
    )
    try:
        ready = wait_for_commit(observer, transaction) if after_service else wait_for_fault(run.handle, fault["id"])
        await asyncio.wait_for(ready, timeout=10)
        assert not pending.done(), "Batch finished before cancellation"
    finally:
        pending.cancel()
        with pytest.raises(asyncio.CancelledError):
            await pending
    run.native.assert_called_once()
    hook.assert_not_called()
    await assert_state(observer, transaction, committed=after_service)
    await recover(run, observer, transaction, [fault], committed=after_service)


async def test_batch_cold_metadata_failure_and_recovery_rust(fault_client, observer, transaction):
    metadata = rule(observer, "MetadataReadContainer", status_code=403, sub_status=32002)
    guard = rule(observer, status_code=400, sub_status=32003)
    # A new client can share warmed metadata through the default runtime.
    run = await fault_client([metadata, guard], runtime=await CosmosRuntime.create_async())
    hook = Mock()
    with pytest.raises(exceptions.CosmosHttpResponseError) as caught:
        await invoke(run.container.execute_item_batch, transaction, partition_key(transaction), response_hook=hook)
    assert (caught.value.status_code, caught.value.sub_status) == (403, 32002)
    assert _rust._debug_fault_injection_rule_hit_count(run.handle, metadata["id"]) == 1
    assert _rust._debug_fault_injection_rule_hit_count(run.handle, guard["id"]) == 0
    run.native.assert_called_once()
    hook.assert_not_called()
    await assert_state(observer, transaction, committed=False)
    set_rule(run.handle, metadata["id"], False)
    with pytest.raises(exceptions.CosmosHttpResponseError) as guarded:
        await invoke(run.container.execute_item_batch, transaction, partition_key(transaction))
    assert (guarded.value.status_code, guarded.value.sub_status) == (400, 32003)
    assert _rust._debug_fault_injection_rule_hit_count(run.handle, guard["id"]) == 1
    await assert_state(observer, transaction, committed=False)
    await recover(run, observer, transaction, [metadata, guard], committed=False)


async def regional_case(fault_client, observer, transaction, case, *, require_multiple):
    handle = await invoke(observer._item_context.adapter._ensure_driver_handle)
    writes, reads = _rust._debug_cached_account_regions(handle)
    assert writes, "Native account topology has no writable regions"
    if require_multiple and len(reads) < 2:
        pytest.skip("Regional batch matrix requires at least two deployed readable regions")
    preferred = list(reads[:2])
    first, second = preferred[0], preferred[-1]
    all_regions = list(dict.fromkeys([*reads, *writes]))
    client_exclusions, request_exclusions, expected = (
        ([], None, first),
        ([first], None, second),
        ([first], [], first),
        ([first], [second], first),
        ([first, second], [first], second),
        (all_regions, all_regions, writes[0]),
    )[case]
    if len(writes) == 1:
        expected = writes[0]
    else:
        assert set(preferred).issubset(set(writes)), "Preferred multi-write regions must both be writable"
    guards = [rule(observer, region=region, status_code=400, sub_status=32004) for region in writes]
    run = await fault_client(guards, preferred_locations=preferred, excluded_locations=client_exclusions)
    options = {} if request_exclusions is None else {"excluded_locations": request_exclusions}
    before = deepcopy(options)
    with pytest.raises(exceptions.CosmosHttpResponseError) as caught:
        await invoke(run.container.execute_item_batch, transaction, partition_key(transaction), **options)
    assert (caught.value.status_code, caught.value.sub_status) == (400, 32004)
    assert options == before
    run.native.assert_called_once()
    for guard in guards:
        assert _rust._debug_fault_injection_rule_hit_count(run.handle, guard["id"]) == int(guard["region"] == expected)
    await assert_state(observer, transaction, committed=False)
    await recover(run, observer, transaction, guards, committed=False)


@pytest.mark.parametrize("case", [0, 5], ids=["preferred-write", "all-excluded-fallback"])
async def test_batch_writable_region_policy_rust(fault_client, observer, transaction, case):
    await regional_case(fault_client, observer, transaction, case, require_multiple=False)


@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosAADCircuitBreaker
@pytest.mark.cosmosMultiRegion
@pytest.mark.parametrize("case", range(6))
async def test_batch_regional_exclusion_matrix_rust(fault_client, observer, transaction, case):
    await regional_case(fault_client, observer, transaction, case, require_multiple=True)
