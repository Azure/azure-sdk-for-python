# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Whole-container read-many through the compiled driver, with no legacy connection."""

import asyncio
from dataclasses import replace
import inspect
import time
import uuid
from unittest.mock import MagicMock

import pytest

from azure.cosmos import CosmosClient, PartitionKey, _rust
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos._backend.contracts import PreparedRequest
from azure.cosmos._backend.partition_key_input import BindingPartitionKey
from azure.cosmos._backend.request_settings import QuerySettings, RequestSettings
from azure.cosmos._helpers._read_items import partition_key_identity
from azure.cosmos._telemetry import CompletionHandler
from azure.cosmos.exceptions import CosmosClientTimeoutError, CosmosHttpResponseError
from azure.cosmos.partition_key import NonePartitionKeyValue
from config.settings import TestSettings
from fault_injection._async_cancellation import wait_for_evidence
from read_items.test_read_items_native import native_database  # pylint: disable=unused-import
from read_all_items.test_read_all_items_contract_unit import ForbiddenConnection

pytestmark = pytest.mark.cosmosEmulator


async def collect(container, asynchronous, **kwargs):
    pager = container.read_all_items(**kwargs)
    return [row async for row in pager] if asynchronous else list(pager)


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_native_full_container_live_paging_and_empty_container_rust(native_database, asynchronous):
    client = (AsyncCosmosClient if asynchronous else CosmosClient)(
        TestSettings.host, TestSettings.masterKey, _backend="rust", timeout=30
    )
    if asynchronous:
        await client.__aenter__()
    try:
        container = client.get_database_client(native_database.id).get_container_client("items")
        container.client_connection = ForbiddenConnection()
        completed, captured, hooks = [], [], []
        container._item_context = replace(
            container._item_context, telemetry_handlers=(CompletionHandler(completed.append),)
        )
        adapter = client._adapter
        original = adapter.execute_pages

        def execute(prepared, **kwargs):
            assert prepared.op == "read_all_items" and prepared.query is None
            for page in original(prepared, **kwargs):
                captured.append(page)
                yield page

        async def execute_async(prepared, **kwargs):
            assert prepared.op == "read_all_items" and prepared.query is None
            async for page in original(prepared, **kwargs):
                captured.append(page)
                yield page

        adapter.execute_pages = execute_async if asynchronous else execute

        def hook(headers, body):
            hooks.append(dict(headers))
            headers["x-ms-continuation"] = "corrupt"
            body["Documents"].clear()

        rows = await collect(container, asynchronous, max_item_count=4, response_hook=hook)
        identities = {(row["id"], partition_key_identity(row.get("pk", NonePartitionKeyValue))) for row in rows}
        assert len(rows) == len(identities) == 76
        assert len(captured) > 2 and captured[-1].has_more is False
        assert all(page.continuation is None and page.continuation_supported is False for page in captured)
        assert all("x-ms-continuation" not in headers for headers in hooks)
        assert sum(float(h.get("x-ms-request-charge", 0)) for h in hooks) == pytest.approx(
            sum(float((p.headers or {}).get("x-ms-request-charge", 0)) for p in captured)
        )
        assert len(completed) == len(captured)
        assert all(event.operation == "read_all_items" and event.outcome == "success" for event in completed)
        adapter.execute_pages = original
        empty = native_database.create_container(id="empty-" + uuid.uuid4().hex, partition_key=PartitionKey(path="/pk"))
        empty_proxy = client.get_database_client(native_database.id).get_container_client(empty.id)
        empty_proxy.client_connection = ForbiddenConnection()
        assert await collect(empty_proxy, asynchronous) == []
    finally:
        closed = client.close()
        if inspect.isawaitable(closed):
            await closed


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["fetch_page_with_cursor", "fetch_page_with_cursor_async"])
@pytest.mark.parametrize("token", ["", "legacy-bookmark", "c1.driver", "c2.driver"])
async def test_compiled_read_all_rejects_resume_tokens_rust(native_database, method, token):
    container = native_database.get_container_client("items")
    handle = container._item_context.adapter._ensure_driver_handle()
    prepared = PreparedRequest(
        op="read_all_items", container_link=container.container_link, body_bytes=b"",
        partition_key=BindingPartitionKey("cross_partition"),
        settings=RequestSettings(query=QuerySettings(continuation=token)),
    )
    with pytest.raises(ValueError, match="does not support continuation"):
        result = getattr(_rust, method)(handle, prepared, _rust._ItemFeedCursor())
        if inspect.isawaitable(result):
            await result
    assert not hasattr(_rust, "read_all_items") and not hasattr(_rust, "read_all_items_async")


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("failure", ["retry", "gone", "failure", "later-page", "timeout"])
async def test_native_read_all_faults_and_fresh_enumeration_rust(native_database, asynchronous, failure):
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
        hook = MagicMock()
        pages = container.read_all_items(
            max_item_count=1, response_hook=hook, timeout=1 if failure == "timeout" else 10
        ).by_page()

        async def take_page():
            return [row async for row in await pages.__anext__()] if asynchronous else list(next(pages))

        if failure == "later-page":
            assert len(await take_page()) == 1
            handle = client._adapter._ensure_driver_handle()
            handle = await handle if asynchronous else handle
            _rust._debug_set_fault_injection_rule_enabled(handle, identifier, True)
        started = time.monotonic()
        if failure in ("failure", "later-page", "timeout"):
            expected = CosmosClientTimeoutError if failure == "timeout" else CosmosHttpResponseError
            with pytest.raises(expected) as caught:
                await take_page()
            if failure == "timeout":
                assert time.monotonic() - started < 3
            else:
                assert caught.value.status_code == 429
                assert caught.value.headers["x-ms-substatus"] == "32001"
            assert hook.call_count == (1 if failure == "later-page" else 0)
            with pytest.raises(RuntimeError, match="pager failed"):
                await take_page()
        else:
            assert len(await take_page()) == 1
        hits = client._adapter._debug_fault_injection_rule_hit_count(identifier)
        assert (await hits if asynchronous else hits) == 1
        assert len(await collect(container, asynchronous)) == 76
    finally:
        closed = client.close()
        if inspect.isawaitable(closed):
            await closed


@pytest.mark.asyncio
async def test_native_read_all_cancellation_releases_cursor_rust(native_database):
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
        pages = container.read_all_items().by_page()
        pending = asyncio.create_task(pages.__anext__())
        try:
            async def started():
                return await client._adapter._debug_fault_injection_rule_hit_count(identifier) == 1

            await wait_for_evidence(started, 5, "The read-all fault was not reached.")
            prepared = pages.state.config.prepared(None, pages.state.cursor, None)
            pending.cancel()
            with pytest.raises(asyncio.CancelledError):
                await asyncio.wait_for(pending, 1)
            with pytest.raises(RuntimeError, match="pager failed"):
                await pages.__anext__()

            async def native_stopped():
                fetch = client._adapter.execute_pages(prepared)
                try:
                    await fetch.__anext__()
                except RuntimeError as error:
                    if "Concurrent use of a retained feed cursor" in str(error):
                        return False
                    if "Feed cursor failed" in str(error):
                        return True
                    raise
                finally:
                    await fetch.aclose()
                pytest.fail("The cancelled native cursor remained reusable.")

            await wait_for_evidence(native_stopped, 1, "The cancelled native cursor was not released.")
            assert len(await collect(container, True)) == 76
        finally:
            if not pending.done():
                pending.cancel()
            await asyncio.gather(pending, return_exceptions=True)
