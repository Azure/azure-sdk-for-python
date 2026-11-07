# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Real Rust create failures with independent persisted-state and recovery checks.

ResponseTimeout is a synthetic, pre-service transport failure, NOT evidence of a
committed write with a lost response. Post-commit coverage must use a separate
transport fault that actually forwards the request.
"""

import asyncio
from contextlib import AsyncExitStack
import inspect
import os
import uuid

import pytest
import pytest_asyncio

from azure.core.exceptions import ServiceResponseError
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from create_item._legacy_variants import assert_fields, observe_native_create
from create_item._legacy_variants import (  # pylint: disable=unused-import
    _make_variant_container_fixture,
    _variant_database_fixture,
)
from fault_injection._query_resume import set_rule

pytestmark = [
    pytest.mark.cosmosEmulator,
    pytest.mark.asyncio,
]


async def invoke(method, *args, **kwargs):
    if inspect.iscoroutinefunction(method):
        return await method(*args, **kwargs)
    return await asyncio.to_thread(method, *args, **kwargs)


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def asynchronous(request):
    return request.param


@pytest.fixture
def observer(make_variant_container):
    return make_variant_container(PartitionKey(path="/pk"))


@pytest_asyncio.fixture
async def fault_client(asynchronous):
    async with AsyncExitStack() as stack:

        async def make(rules):
            client_type = AsyncCosmosClient if asynchronous else CosmosClient
            client = client_type(
                os.environ["ACCOUNT_HOST"],
                os.environ["ACCOUNT_KEY"],
                _backend="rust",
                consistency_level="Session",
                timeout=20,
                retry_throttle_total=0,
                _fault_injection_rules=rules,
            )
            if asynchronous:
                await stack.enter_async_context(client)
            else:
                stack.enter_context(client)
            await invoke(client._adapter._ensure_driver_handle)
            return client

        yield make


def rule(container_id, operation_type="CreateItem", **result):
    return {
        "id": uuid.uuid4().hex,
        "operation_type": operation_type,
        "container_id": container_id,
        "probability": 1.0,
        **result,
    }


def target(client, database, observer):
    return client.get_database_client(database.id).get_container_client(observer.id)


async def assert_absent(observer, body):
    with pytest.raises(exceptions.CosmosResourceNotFoundError) as caught:
        await invoke(observer.read_item, body["id"], partition_key=body["pk"])
    assert caught.value.status_code == 404


async def assert_recovery(client, container, observer, body, fault, native):
    handle = await invoke(client._adapter._ensure_driver_handle)
    set_rule(handle, fault["id"], False)
    native.reset_mock()
    created = await invoke(container.create_item, body)
    native.assert_called_once()
    assert_fields(created, body)
    assert_fields(await invoke(observer.read_item, body["id"], partition_key=body["pk"]), body)
    with pytest.raises(exceptions.CosmosResourceExistsError) as duplicate:
        await invoke(container.create_item, body)
    assert duplicate.value.status_code == 409
    assert_fields(await invoke(observer.read_item, body["id"], partition_key=body["pk"]), body)


@pytest.mark.parametrize("error_type", ["ConnectionError", "ResponseTimeout"])
async def test_unsent_transport_failure_and_recovery_rust(
    asynchronous, fault_client, variant_database, observer, monkeypatch, error_type
):
    fault = rule(observer.id, error_type=error_type)
    client = await fault_client([fault])
    container = target(client, variant_database, observer)
    await invoke(container.read)
    native = observe_native_create(monkeypatch, client, "rust", asynchronous=asynchronous)
    body = {"id": uuid.uuid4().hex, "pk": "failure", "value": "original"}
    # The binding deliberately does not infer a public "not sent" guarantee
    # from a response-less driver error. Absence is established independently.
    with pytest.raises(ServiceResponseError) as caught:
        await invoke(container.create_item, body)
    assert caught.value.__cause__ is not None
    assert caught.value.__cause__.__class__.__name__ == "_DriverTransportError"
    native.assert_called_once()
    assert await invoke(client._adapter._debug_fault_injection_rule_hit_count, fault["id"]) > 0
    await assert_absent(observer, body)
    await assert_recovery(client, container, observer, body, fault, native)


async def test_operation_deadline_before_service_and_recovery_rust(
    asynchronous, fault_client, variant_database, observer, monkeypatch
):
    fault = rule(observer.id, status_code=502, delay_ms=2000)
    client = await fault_client([fault])
    container = target(client, variant_database, observer)
    await invoke(container.read)
    native = observe_native_create(monkeypatch, client, "rust", asynchronous=asynchronous)
    body = {"id": uuid.uuid4().hex, "pk": "timeout"}
    with pytest.raises(exceptions.CosmosClientTimeoutError):
        await invoke(container.create_item, body, timeout=1)
    native.assert_called_once()
    assert await invoke(client._adapter._debug_fault_injection_rule_hit_count, fault["id"]) == 1
    await assert_absent(observer, body)
    await assert_recovery(client, container, observer, body, fault, native)


@pytest.mark.parametrize("asynchronous", [True], ids=["async"])
async def test_cancel_pending_native_create_and_recovery_rust(
    asynchronous, fault_client, variant_database, observer, monkeypatch
):
    fault = rule(observer.id, status_code=502, delay_ms=2000)
    client = await fault_client([fault])
    container = target(client, variant_database, observer)
    await container.read()
    native = observe_native_create(monkeypatch, client, "rust", asynchronous=asynchronous)
    body = {"id": uuid.uuid4().hex, "pk": "cancel"}
    pending = asyncio.create_task(container.create_item(body))
    try:

        async def wait_for_native_fault():
            while not await client._adapter._debug_fault_injection_rule_hit_count(fault["id"]):
                await asyncio.sleep(0.01)

        await asyncio.wait_for(wait_for_native_fault(), timeout=5)
        assert not pending.done(), "Create completed before cancellation could be exercised"
    finally:
        pending.cancel()
        with pytest.raises(asyncio.CancelledError):
            await pending
    native.assert_called_once()
    await assert_absent(observer, body)
    await assert_recovery(client, container, observer, body, fault, native)


async def test_cold_metadata_failure_blocks_create_and_recovers_rust(
    asynchronous, fault_client, variant_database, observer, monkeypatch
):
    metadata = rule(observer.id, "MetadataReadContainer", status_code=403, sub_status=32002)
    guard = rule(observer.id, status_code=400, sub_status=32003)
    client = await fault_client([metadata, guard])
    container = target(client, variant_database, observer)
    native = observe_native_create(monkeypatch, client, "rust", asynchronous=asynchronous)
    body = {"id": uuid.uuid4().hex, "pk": "metadata"}
    with pytest.raises(exceptions.CosmosHttpResponseError) as caught:
        await invoke(container.create_item, body)
    assert (caught.value.status_code, caught.value.sub_status) == (403, 32002)
    native.assert_called_once()
    assert await invoke(client._adapter._debug_fault_injection_rule_hit_count, metadata["id"]) == 1
    assert await invoke(client._adapter._debug_fault_injection_rule_hit_count, guard["id"]) == 0
    await assert_absent(observer, body)

    handle = await invoke(client._adapter._ensure_driver_handle)
    set_rule(handle, metadata["id"], False)
    with pytest.raises(exceptions.CosmosHttpResponseError) as guarded:
        await invoke(container.create_item, body)
    assert (guarded.value.status_code, guarded.value.sub_status) == (400, 32003)
    assert await invoke(client._adapter._debug_fault_injection_rule_hit_count, guard["id"]) == 1
    await assert_absent(observer, body)
    await assert_recovery(client, container, observer, body, guard, native)


async def test_service_applies_create_indexing_directive_rust(
    asynchronous, fault_client, variant_database, observer, monkeypatch
):
    client = await fault_client([])
    container = target(client, variant_database, observer)
    native = observe_native_create(monkeypatch, client, "rust", asynchronous=asynchronous)
    marker = uuid.uuid4().hex
    bodies = [{"id": mode, "pk": marker, "marker": marker} for mode in ("default", "include", "exclude")]
    create_diagnostics = {}
    for body, options in zip(bodies, ({}, {"indexing_directive": "Include"}, {"indexing_directive": "Exclude"})):
        created = await invoke(container.create_item, body, **options)
        # Save the create's transport evidence before the observer performs a read.
        create_diagnostics[body["id"]] = created.get_response_headers().get(
            "x-ms-cosmos-sdk-diagnostics", "<missing create diagnostics; transport unconfirmed>"
        )
        assert_fields(created, body)
        assert_fields(await invoke(observer.read_item, body["id"], partition_key=marker), body)
    assert native.call_count == 3
    assert [call.args[1].settings.item.indexing_directive for call in native.call_args_list] == [
        None,
        "Include",
        "Exclude",
    ]

    def indexed_ids():
        return {
            row["id"]
            for row in observer.query_items(
                "SELECT c.id FROM c WHERE c.marker = @marker ORDER BY c.id",
                parameters=[{"name": "@marker", "value": marker}],
                partition_key=marker,
            )
        }

    # data_plane/gateway_v2 identifies Gateway 2.0; metadata/gateway does not.
    transport_evidence = "Create diagnostics (use data_plane entries, not metadata):\n" + "\n".join(
        f"{mode}: {create_diagnostics[mode]}" for mode in ("exclude", "include", "default")
    )
    print(transport_evidence)
    actual = await asyncio.to_thread(indexed_ids)
    assert actual == {
        "default",
        "include",
    }, f"Exclude reached native create but the service query still returns the item\n{transport_evidence}"
