# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Real Rust read-many, including driver batching, paging and full-key validation."""

import asyncio
from dataclasses import replace
import inspect
import json
import time
import uuid
from unittest.mock import MagicMock

import pytest

from azure.cosmos import CosmosClient, PartitionKey, _rust
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos._backend.contracts import PreparedRequest, ReadManyItem
from azure.cosmos._backend.partition_key_input import BindingPartitionKey
from azure.cosmos._backend.request_settings import QuerySettings, RequestSettings
from azure.cosmos._helpers._read_items import partition_key_identity
from azure.cosmos._telemetry import CompletionHandler
from azure.cosmos.exceptions import CosmosClientTimeoutError, CosmosHttpResponseError
from azure.cosmos.partition_key import NonePartitionKeyValue
from config.settings import TestSettings
from fault_injection._async_cancellation import wait_for_evidence
from ._helpers import ForbiddenConnection

pytestmark = pytest.mark.cosmosEmulator


@pytest.fixture(scope="module")
def native_database():
    with CosmosClient(TestSettings.host, TestSettings.masterKey, _backend="rust", timeout=30) as client:
        database = client.create_database("read-many-native-" + uuid.uuid4().hex)
        try:
            container = database.create_container(id="items", partition_key=PartitionKey(path="/pk"))
            for index in range(70):
                container.create_item({"id": str(index), "pk": "p", "nested": [index], "text": "\u00e9"})
            for key in (True, 1, False, 0, None):
                container.create_item({"id": "typed", "pk": key})
            container.create_item({"id": "typed"})
            hpk = database.create_container(
                id="hpk", partition_key=PartitionKey(path=["/tenant", "/user"], kind="MultiHash")
            )
            hpk.create_item({"id": "a", "tenant": "t", "user": "u"})
            yield database
        finally:
            client.delete_database(database.id)


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_native_collection_paging_keys_and_read_all_live_cursor_rust(native_database, asynchronous):
    client = (AsyncCosmosClient if asynchronous else CosmosClient)(
        TestSettings.host, TestSettings.masterKey, _backend="rust", timeout=30
    )
    if asynchronous:
        await client.__aenter__()
    try:
        container = client.get_database_client(native_database.id).get_container_client("items")
        container.client_connection = ForbiddenConnection()
        container._get_properties_with_options = MagicMock(side_effect=AssertionError("legacy metadata"))
        completed = []
        container._item_context = replace(
            container._item_context, telemetry_handlers=(CompletionHandler(completed.append),)
        )
        adapter = container._item_context.adapter
        original = adapter.execute_pages
        captured = []

        def execute(*args, **kwargs):
            for page in original(*args, **kwargs):
                captured.append(page)
                yield page

        async def execute_async(*args, **kwargs):
            async for page in original(*args, **kwargs):
                captured.append(page)
                yield page

        adapter.execute_pages = execute_async if asynchronous else execute
        pairs = [(str(index), "p") for index in reversed(range(70))]
        pairs.extend([("69", "p"), ("missing", "p")])
        hook = MagicMock()
        result = container.read_items(pairs, max_item_count=4, response_hook=hook)
        result = await result if asynchronous else result
        assert [(row["id"], row["pk"]) for row in result] == pairs[:-1]
        assert result[0] is not result[-1] and result[0]["nested"] is not result[-1]["nested"]
        assert all(row["text"] == "\u00e9" for row in result)
        assert len(captured) > 2 and any(page.has_more for page in captured)
        assert all(page.continuation is None for page in captured)
        assert captured[-1].has_more is False
        charge = sum(float((page.headers or {}).get("x-ms-request-charge", 0)) for page in captured)
        assert float(result.get_response_headers()["x-ms-request-charge"]) == pytest.approx(charge)
        assert charge > 0
        hook.assert_called_once_with(result.get_response_headers(), result)
        assert len(completed) == len(captured)
        assert all(event.operation == "read_items" and event.outcome == "success" for event in completed)

        keys = [True, 1, False, 0, None, NonePartitionKeyValue]
        result = container.read_items([("typed", key) for key in keys])
        result = await result if asynchronous else result
        assert [partition_key_identity(row.get("pk", NonePartitionKeyValue)) for row in result] == [
            partition_key_identity(key) for key in keys
        ]
        container._get_properties_with_options.assert_not_called()
        adapter.execute_pages = original

        pages = container.read_all_items(max_item_count=5).by_page()
        if asynchronous:
            first = [row async for row in await pages.__anext__()]
        else:
            first = list(next(pages))
        with pytest.raises(NotImplementedError, match="cannot be bookmarked"):
            _ = pages.continuation_token
        if asynchronous:
            rest = [row async for group in pages async for row in group]
        else:
            rest = [row for group in pages for row in group]
        all_rows = first + rest
        identities = {(row["id"], partition_key_identity(row.get("pk", NonePartitionKeyValue))) for row in all_rows}
        assert len(all_rows) == len(identities) == 76
    finally:
        result = client.close()
        if inspect.isawaitable(result):
            await result


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("failure", ["retry", "gone", "failure", "later-page", "timeout"])
async def test_native_read_many_faults_and_same_client_recovery_rust(native_database, asynchronous, failure):
    identifier = uuid.uuid4().hex
    rule = {
        "id": identifier, "operation_type": "QueryItem", "container_id": "items",
        "status_code": 410 if failure == "gone" else 429,
        "sub_status": 1002 if failure == "gone" else 32001,
        "probability": 1.0, "hit_limit": 1, "delay_ms": 5000 if failure == "timeout" else 0,
        "enabled": failure != "later-page",
    }
    client = (AsyncCosmosClient if asynchronous else CosmosClient)(
        TestSettings.host, TestSettings.masterKey, _backend="rust", timeout=20,
        retry_throttle_total=2 if failure == "retry" else 0, _fault_injection_rules=[rule],
    )
    if asynchronous:
        await client.__aenter__()
    try:
        container = client.get_database_client(native_database.id).get_container_client("items")
        container.client_connection = ForbiddenConnection()
        delivered = []
        if failure == "later-page":
            handle = client._adapter._ensure_driver_handle()
            handle = await handle if asynchronous else handle
            original = client._adapter.execute_pages

            def arm(response):
                if not delivered:
                    _rust._debug_set_fault_injection_rule_enabled(handle, identifier, True)
                delivered.append(response)

            def execute(*args, **kwargs):
                for response in original(*args, **kwargs):
                    arm(response)
                    yield response

            async def execute_async(*args, **kwargs):
                async for response in original(*args, **kwargs):
                    arm(response)
                    yield response

            client._adapter.execute_pages = execute_async if asynchronous else execute
        hook = MagicMock()
        pairs = [("0", "p"), ("1", "p")]
        started = time.monotonic()
        if failure in ("failure", "later-page", "timeout"):
            expected = CosmosClientTimeoutError if failure == "timeout" else CosmosHttpResponseError
            with pytest.raises(expected) as caught:
                result = container.read_items(
                    pairs, max_item_count=1, response_hook=hook, timeout=1 if failure == "timeout" else 10
                )
                if asynchronous:
                    await result
            if failure == "timeout":
                assert time.monotonic() - started < 3
            else:
                assert caught.value.status_code == 429
                assert caught.value.headers["x-ms-substatus"] == "32001"
            hook.assert_not_called()
            if failure == "later-page":
                assert [response.status_code for response in delivered] == [200, 429]
                partial = json.loads(delivered[0].body)["Documents"]
                assert len(partial) == 1 and partial[0]["id"] in ("0", "1")
        else:
            result = container.read_items(pairs, response_hook=hook)
            result = await result if asynchronous else result
            assert [row["id"] for row in result] == ["0", "1"]
            hook.assert_called_once()
        hits = client._adapter._debug_fault_injection_rule_hit_count(identifier)
        assert (await hits if asynchronous else hits) == 1
        recovered = container.read_items(pairs)
        recovered = await recovered if asynchronous else recovered
        assert [row["id"] for row in recovered] == ["0", "1"]
    finally:
        result = client.close()
        if inspect.isawaitable(result):
            await result


@pytest.mark.asyncio
async def test_native_read_many_cancellation_releases_cursor_rust(native_database):
    identifier = uuid.uuid4().hex
    rule = {
        "id": identifier, "operation_type": "QueryItem", "container_id": "items",
        "status_code": 429, "probability": 1.0, "hit_limit": 1, "delay_ms": 5000,
    }
    async with AsyncCosmosClient(
        TestSettings.host, TestSettings.masterKey, _backend="rust", timeout=20,
        _fault_injection_rules=[rule],
    ) as client:
        container = client.get_database_client(native_database.id).get_container_client("items")
        container.client_connection = ForbiddenConnection()
        adapter = client._adapter
        original = adapter.execute_pages
        captured = []

        async def execute(prepared, **kwargs):
            captured.append(prepared)
            async for response in original(prepared, **kwargs):
                yield response

        adapter.execute_pages = execute
        hook = MagicMock()
        pending = asyncio.create_task(container.read_items([("0", "p"), ("1", "p")], response_hook=hook))
        try:
            async def started():
                while await adapter._debug_fault_injection_rule_hit_count(identifier) == 0:
                    await asyncio.sleep(0.01)

            await asyncio.wait_for(started(), 5)
            assert not pending.done()
            pending.cancel()
            with pytest.raises(asyncio.CancelledError):
                await asyncio.wait_for(pending, 1)
            hook.assert_not_called()
            adapter.execute_pages = original
            async def native_stopped():
                pages = original(captured[0])
                try:
                    await pages.__anext__()
                except RuntimeError as error:
                    if "Concurrent use of a retained feed cursor" in str(error):
                        return False
                    if "Feed cursor failed" in str(error):
                        return True
                    raise
                finally:
                    await pages.aclose()
                pytest.fail("The cancelled cursor remained reusable.")

            await wait_for_evidence(native_stopped, 1, "The cancelled native fetch did not release its cursor.")
            recovered = await container.read_items([("0", "p"), ("1", "p")])
            assert [row["id"] for row in recovered] == ["0", "1"]
            assert await adapter._debug_fault_injection_rule_hit_count(identifier) == 1
        finally:
            if not pending.done():
                pending.cancel()
            await asyncio.gather(pending, return_exceptions=True)


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["fetch_page_with_cursor", "fetch_page_with_cursor_async"])
@pytest.mark.parametrize("invalid", ["prefix", "continuation", "untyped"])
async def test_compiled_read_many_rejects_invalid_selection_rust(native_database, method, invalid):
    container = native_database.get_container_client("hpk")
    handle = container._item_context.adapter._ensure_driver_handle()
    key = BindingPartitionKey("components", ("t",) if invalid == "prefix" else ("t", "u"))
    request = PreparedRequest(
        op="read_items", container_link=container.container_link, body_bytes=b"",
        partition_key=BindingPartitionKey("cross_partition"),
        read_many_items=(ReadManyItem("a", key),),
        settings=RequestSettings(query=QuerySettings(continuation="c2.not-allowed" if invalid == "continuation" else None)),
    )
    if invalid == "untyped":
        object.__setattr__(request, "read_many_items", ({"item_id": "a", "partition_key": key},))
    with pytest.raises((ValueError, TypeError, AttributeError)):
        result = getattr(_rust, method)(handle, request, _rust._ItemFeedCursor())
        if inspect.isawaitable(result):
            await result
