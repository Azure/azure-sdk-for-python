# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# Rust behavior test
"""Authentication failures through real Rust-backed listing on the local emulator."""

import base64
import uuid
from urllib.parse import urlsplit

import pytest

from azure.cosmos import CosmosClient, _rust
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError
from config.diagnostics import _rust_fallback_count
from config.settings import TestSettings

pytestmark = [pytest.mark.asyncio, pytest.mark.cosmosEmulator]


# Source: (new) Incorrect-key authentication during lazy listing initialization.
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
async def test_incorrect_key_preserves_401_during_listing_rust(monkeypatch, record_property, asynchronous):
    """An invalid key is locally well formed; record where real authentication fails."""
    endpoint = TestSettings.host
    assert urlsplit(endpoint).hostname in ("localhost", "127.0.0.1", "::1")
    decoded = base64.b64decode(TestSettings.masterKey, validate=True)
    assert decoded
    incorrect_key = base64.b64encode(bytes([decoded[0] ^ 1]) + decoded[1:]).decode("ascii")
    calls = []
    acquire = _rust.acquire_driver_handle
    operation = "list_databases_async" if asynchronous else "list_databases"
    fetch = getattr(_rust, operation)

    def observed_acquire(*args, **kwargs):
        calls.append("acquire-start")
        handle = acquire(*args, **kwargs)
        calls.append("acquire-complete")
        return handle

    def observed_fetch(*args, **kwargs):
        calls.append(operation)
        return fetch(*args, **kwargs)

    monkeypatch.setattr(_rust, "acquire_driver_handle", observed_acquire)
    monkeypatch.setattr(_rust, operation, observed_fetch)
    client = (AsyncCosmosClient if asynchronous else CosmosClient)(endpoint, incorrect_key, _backend="rust")
    hooks = []
    fallback_before = _rust_fallback_count()
    try:
        pager = client.list_databases(timeout=10, response_hook=hooks.append).by_page()
        assert calls == [], "Constructing a listing unexpectedly initialized the driver"
        with pytest.raises(CosmosHttpResponseError) as caught:
            if asynchronous:
                await pager.__anext__()
            else:
                next(pager)
        assert caught.value.status_code == 401
        assert isinstance(caught.value.__cause__, _rust._DriverResponseError)
        assert caught.value.headers["x-ms-activity-id"]
        assert hooks == []
        assert pager.continuation_token is None
        assert _rust_fallback_count() == fallback_before
        assert calls == ["acquire-start"], "Recheck whether authentication now reaches the database-list request"
        with pytest.raises(RuntimeError, match="pager failed"):
            if asynchronous:
                await pager.__anext__()
            else:
                next(pager)
        assert calls == ["acquire-start"]
    finally:
        record_property("binding_calls", ",".join(calls))
        if asynchronous:
            await client.close()
        else:
            client.close()


# Source: (new) A driver-injected listing 401 after successful account initialization.
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
async def test_listing_response_preserves_401_after_initialization_rust(monkeypatch, record_property, asynchronous):
    endpoint = TestSettings.host
    assert urlsplit(endpoint).hostname in ("localhost", "127.0.0.1", "::1")
    rule_id = "listing-401-" + uuid.uuid4().hex
    activity_id = str(uuid.uuid4())
    rule = {
        "id": rule_id,
        "operation_type": "All",
        "status_code": 401,
        "sub_status": 1002,
        "response_body": b'{"code":"Unauthorized","message":"listing access denied"}',
        "response_headers": {"x-ms-activity-id": activity_id},
        "enabled": False,
    }
    client = (AsyncCosmosClient if asynchronous else CosmosClient)(
        endpoint, TestSettings.masterKey, _backend="rust", _fault_injection_rules=[rule]
    )
    handle = None
    calls = []
    hooks = []
    fallback_before = _rust_fallback_count()

    async def successful_listing():
        if asynchronous:
            return [database async for database in client.list_databases(timeout=10)]
        return list(client.list_databases(timeout=10))

    async def next_page(pager):
        if asynchronous:
            return await pager.__anext__()
        return next(pager)

    try:
        await successful_listing()
        handle = (
            await client._adapter._ensure_driver_handle() if asynchronous else client._adapter._ensure_driver_handle()
        )
        assert _rust._debug_fault_injection_rule_hit_count(handle, rule_id) == 0
        operation = "list_databases_async" if asynchronous else "list_databases"
        fetch = getattr(_rust, operation)
        acquire = _rust.acquire_driver_handle

        def observed_fetch(*args, **kwargs):
            assert args[0] is handle
            calls.append(operation)
            return fetch(*args, **kwargs)

        def observed_acquire(*args, **kwargs):
            calls.append("acquire")
            return acquire(*args, **kwargs)

        monkeypatch.setattr(_rust, operation, observed_fetch)
        monkeypatch.setattr(_rust, "acquire_driver_handle", observed_acquire)
        _rust._debug_set_fault_injection_rule_enabled(handle, rule_id, True)
        pager = client.list_databases(timeout=10, response_hook=hooks.append).by_page()
        assert calls == []
        with pytest.raises(CosmosHttpResponseError) as caught:
            await next_page(pager)
        error = caught.value
        assert error.status_code == 401
        assert error.sub_status == 1002
        assert error.headers["x-ms-activity-id"] == activity_id
        assert error.headers["x-ms-substatus"] == "1002"
        assert "listing access denied" in str(error)
        assert calls == [operation], "The failure must come from listing, not initialization"
        hits = _rust._debug_fault_injection_rule_hit_count(handle, rule_id)
        assert hits > 0
        assert hooks == []
        assert pager.continuation_token is None
        with pytest.raises(RuntimeError, match="pager failed"):
            await next_page(pager)
        assert calls == [operation]
        assert _rust._debug_fault_injection_rule_hit_count(handle, rule_id) == hits
        assert _rust_fallback_count() == fallback_before
        record_property("listing_fault_hits", hits)

        _rust._debug_set_fault_injection_rule_enabled(handle, rule_id, False)
        await successful_listing()
        assert len(calls) >= 2 and all(call == operation for call in calls)
        assert _rust._debug_fault_injection_rule_hit_count(handle, rule_id) == hits
        assert _rust_fallback_count() == fallback_before
    finally:
        record_property("binding_calls", ",".join(calls))
        if handle is not None:
            _rust._debug_set_fault_injection_rule_enabled(handle, rule_id, False)
        if asynchronous:
            await client.close()
        else:
            client.close()
