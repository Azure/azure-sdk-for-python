# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Preserve original failure inputs through compiled read-many fault injection."""

import inspect
import json
import time
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey, _rust
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError
from azure.cosmos.exceptions import CosmosClientTimeoutError
from config.settings import TestSettings


@pytest.fixture(scope="module")
def legacy_fault_database():
    with CosmosClient(
        TestSettings.host, TestSettings.masterKey, _backend="rust"
    ) as client:
        database = client.create_database(
            "read-items-fault-original-" + uuid.uuid4().hex
        )
        try:
            yield database
        finally:
            client.delete_database(database.id)


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize(
    "scenario,count,prefix,status,message",
    [
        ("unavailable", 10, "item", 503, "Injected Service Unavailable Error"),
        ("headers", 5, "item", 429, "Simulated query failure with headers"),
        (
            "throttle",
            5,
            "item_for_throttle",
            429,
            "Throttling error injected for testing",
        ),
        ("gone", 20, "item_for_gone", 410, "Gone error injected for testing"),
    ],
)
async def test_original_failure_and_retry_contracts_rust(
    legacy_fault_database,
    record_property,
    asynchronous,
    scenario,
    count,
    prefix,
    status,
    message,
):
    # Source: tests/test_read_items.py::TestReadItems.test_read_items_surfaces_exceptions
    # Source: tests/test_read_items_async.py::TestReadItemsAsync.test_read_items_surfaces_exceptions_async
    # Source: tests/test_read_items.py::TestReadItems.test_read_failure_preserves_headers
    # Source: tests/test_read_items_async.py::TestReadItemsAsync.test_read_failure_preserves_headers_async
    # Source: tests/test_read_items.py::TestReadItems.test_read_items_with_throttling_retry
    # Source: tests/test_read_items_async.py::TestReadItemsAsync.test_read_items_with_throttling_retry_async
    # Source: tests/test_read_items.py::TestReadItems.test_read_items_with_gone_retry
    # Source: tests/test_read_items_async.py::TestReadItemsAsync.test_read_items_with_gone_retry_async
    owned = legacy_fault_database.create_container(
        "original-" + uuid.uuid4().hex, partition_key=PartitionKey(path="/id")
    )
    client = None
    handle = None
    rule_id = uuid.uuid4().hex
    try:
        pairs = []
        for index in range(count):
            item_id = f"{prefix}_{index}_{uuid.uuid4()}"
            owned.create_item({"id": item_id, "data": index})
            pairs.append((item_id, item_id))
        headers = {"x-ms-retry-after-ms": "10"} if scenario == "throttle" else {}
        if scenario == "headers":
            headers = {
                "x-ms-request-charge": "12.34",
                "x-ms-activity-id": "a-fake-activity-id",
                "x-ms-session-token": "session-token-for-failure",
            }
        retry = scenario in ("throttle", "gone")
        rule = {
            "id": rule_id,
            "operation_type": "QueryItem",
            "container_id": owned.id,
            "status_code": status,
            "sub_status": 1002 if scenario == "gone" else 0,
            "enabled": False,
            "probability": 1.0,
            "hit_limit": 1 if retry else None,
            "response_headers": headers,
            "response_body": json.dumps({"message": message}).encode(),
        }
        client = (AsyncCosmosClient if asynchronous else CosmosClient)(
            TestSettings.host,
            TestSettings.masterKey,
            _backend="rust",
            retry_throttle_total=9 if retry else 0,
            _fault_injection_rules=[rule],
        )
        if asynchronous:
            await client.__aenter__()
        container = client.get_database_client(
            legacy_fault_database.id
        ).get_container_client(owned.id)

        async def read(**kwargs):
            result = container.read_items(items=pairs, **kwargs)
            return await result if asynchronous else result

        assert len(await read()) == count
        handle = client._adapter._ensure_driver_handle()
        if asynchronous:
            handle = await handle
        _rust._debug_set_fault_injection_rule_enabled(handle, rule_id, True)
        if retry:
            result = await read()
            assert len(result) == len(pairs)
            assert {item["id"] for item in result} == {item_id for item_id, _ in pairs}
            assert _rust._debug_fault_injection_rule_hit_count(handle, rule_id) == 1
        else:
            with pytest.raises(CosmosHttpResponseError) as caught:
                await read()
            assert caught.value.status_code == status
            if scenario == "unavailable":
                assert message in str(caught.value)
            else:
                assert caught.value.headers is not None
                for name, value in headers.items():
                    assert caught.value.headers.get(name) == value
            assert _rust._debug_fault_injection_rule_hit_count(handle, rule_id) >= 1
        record_property(
            "fault_hits", _rust._debug_fault_injection_rule_hit_count(handle, rule_id)
        )
        _rust._debug_set_fault_injection_rule_enabled(handle, rule_id, False)
        assert len(await read()) == count
    finally:
        if handle is not None:
            _rust._debug_set_fault_injection_rule_enabled(handle, rule_id, False)
        if client is not None:
            closed = client.close()
            if inspect.isawaitable(closed):
                await closed
        legacy_fault_database.delete_container(owned.id)


@pytest.mark.cosmosLong
@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosAADCircuitBreaker
@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
async def test_original_whole_call_timeout_rust(
    legacy_fault_database, record_property, asynchronous
):
    # Source: tests/test_crud.py::TestCRUDOperations.test_timeout_for_read_items
    # Source: tests/test_crud_async.py::TestCRUDOperationsAsync.test_timeout_for_read_items_async
    owned = legacy_fault_database.create_container(
        "multi_partition_container_" + str(uuid.uuid4()),
        partition_key=PartitionKey(path="/pk"),
        offer_throughput=11000,
    )
    client = None
    handle = None
    identifier = uuid.uuid4().hex
    try:
        assert (
            len(list(owned.read_feed_ranges())) > 1
        ), "Container should have multiple physical partitions."
        pairs = []
        for index in range(200):
            item_id = f"item_{index}_{uuid.uuid4()}"
            owned.create_item({"id": item_id, "pk": index % 10, "data": index})
            pairs.append((item_id, index % 10))
        rule = {
            "id": identifier,
            "operation_type": "QueryItem",
            "container_id": owned.id,
            "status_code": 429,
            "probability": 1.0,
            "hit_limit": None,
            "delay_ms": 3000,
            "enabled": False,
        }
        client = (AsyncCosmosClient if asynchronous else CosmosClient)(
            TestSettings.host,
            TestSettings.masterKey,
            _backend="rust",
            _fault_injection_rules=[rule],
        )
        if asynchronous:
            await client.__aenter__()
        container = client.get_database_client(
            legacy_fault_database.id
        ).get_container_client(owned.id)

        async def read(**kwargs):
            result = container.read_items(items=pairs, **kwargs)
            return await result if asynchronous else result

        assert len(await read()) == 200
        handle = client._adapter._ensure_driver_handle()
        if asynchronous:
            handle = await handle
        _rust._debug_set_fault_injection_rule_enabled(handle, identifier, True)
        started = time.monotonic()
        with pytest.raises(CosmosClientTimeoutError):
            await read(timeout=5)
        elapsed = time.monotonic() - started
        assert 5 < elapsed < 12
        hits = _rust._debug_fault_injection_rule_hit_count(handle, identifier)
        assert hits >= 2
        record_property("elapsed_seconds", elapsed)
        record_property("fault_hits", hits)
        _rust._debug_set_fault_injection_rule_enabled(handle, identifier, False)
        if not asynchronous:
            for index in range(500):
                item_id = f"item_{index}_{uuid.uuid4()}"
                owned.create_item({"id": item_id, "pk": index % 10, "data": index})
                pairs.append((item_id, index % 10))
            result = await read()
            assert {item["id"] for item in result} == {item_id for item_id, _ in pairs}
    finally:
        if handle is not None:
            _rust._debug_set_fault_injection_rule_enabled(handle, identifier, False)
        if client is not None:
            closed = client.close()
            if inspect.isawaitable(closed):
                await closed
        legacy_fault_database.delete_container(owned.id)
