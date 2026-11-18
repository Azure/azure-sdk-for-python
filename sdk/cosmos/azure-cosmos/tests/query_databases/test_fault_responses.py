# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# Rust behavior test
"""Database-query failures after successful initialization, using driver faults."""

import time
import uuid
from urllib.parse import urlsplit

import pytest

from azure.cosmos import CosmosClient, _rust
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos.exceptions import CosmosClientTimeoutError, CosmosHttpResponseError
from config.diagnostics import _rust_fallback_count
from config.settings import TestSettings

pytestmark = [pytest.mark.asyncio, pytest.mark.cosmosEmulator]


# Source: (new) Compiled database-query 401 propagation and repeated-429 deadlines.
@pytest.mark.timeout(45)
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("status_code", [401, 429], ids=["unauthorized", "throttled-timeout"])
async def test_query_fault_after_initialization_rust(monkeypatch, record_property, asynchronous, status_code):
    endpoint = TestSettings.host
    assert urlsplit(endpoint).hostname in ("localhost", "127.0.0.1", "::1")
    rule_id = "query-fault-" + uuid.uuid4().hex
    activity_id = str(uuid.uuid4())
    rule = {
        "id": rule_id,
        "operation_type": "All",
        "status_code": status_code,
        "enabled": False,
        "probability": 1.0,
        "hit_limit": None,
    }
    if status_code == 401:
        rule.update(
            sub_status=1002,
            response_body=b'{"code":"Unauthorized","message":"database query access denied"}',
            response_headers={"x-ms-activity-id": activity_id},
        )
    else:
        rule["delay_ms"] = 1000
    timeout = 3 if status_code == 429 else 10
    expected_error = CosmosClientTimeoutError if status_code == 429 else CosmosHttpResponseError
    client = (AsyncCosmosClient if asynchronous else CosmosClient)(
        endpoint, TestSettings.masterKey, _backend="rust", _fault_injection_rules=[rule]
    )
    query = "SELECT * FROM root r WHERE r.id=@id"
    parameters = [{"name": "@id", "value": "query-fault-missing-" + uuid.uuid4().hex}]
    calls = []
    hooks = []
    handle = None
    fallback_before = _rust_fallback_count()

    async def successful_query():
        iterable = client.query_databases(query, parameters=parameters, timeout=10)
        if asynchronous:
            rows = [database async for database in iterable]
        else:
            rows = list(iterable)
        assert rows == []

    async def next_page(pager):
        if asynchronous:
            return await pager.__anext__()
        return next(pager)

    try:
        await successful_query()
        handle = (
            await client._adapter._ensure_driver_handle() if asynchronous else client._adapter._ensure_driver_handle()
        )
        assert _rust._debug_fault_injection_rule_hit_count(handle, rule_id) == 0
        operation = "query_databases_async" if asynchronous else "query_databases"
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
        pager = client.query_databases(
            query, parameters=parameters, timeout=timeout, response_hook=hooks.append
        ).by_page()
        assert calls == []
        bookmark = pager.continuation_token
        started = time.monotonic()
        with pytest.raises(expected_error) as caught:
            await next_page(pager)
        elapsed = time.monotonic() - started
        hits = _rust._debug_fault_injection_rule_hit_count(handle, rule_id)
        record_property("fault_hits", hits)
        record_property("elapsed_seconds", elapsed)
        record_property("timeout_seconds", timeout)
        if status_code == 401:
            error = caught.value
            assert error.status_code == 401
            assert error.sub_status == 1002
            assert error.headers["x-ms-activity-id"] == activity_id
            assert error.headers["x-ms-substatus"] == "1002"
            assert "database query access denied" in str(error)
            assert hits == 1
        else:
            assert hits >= 2, "The driver did not retry the injected 429"
            assert timeout - 0.5 <= elapsed < timeout + 5, "The query did not exhaust its timeout budget"
        assert calls == [operation], "The failure must come from querying, not initialization"
        assert hooks == []
        assert pager.continuation_token == bookmark
        assert _rust_fallback_count() == fallback_before

        with pytest.raises(RuntimeError, match="pager failed"):
            await next_page(pager)
        assert calls == [operation]
        assert _rust._debug_fault_injection_rule_hit_count(handle, rule_id) == hits

        _rust._debug_set_fault_injection_rule_enabled(handle, rule_id, False)
        await successful_query()
        assert calls == [operation, operation]
        assert _rust._debug_fault_injection_rule_hit_count(handle, rule_id) == hits
        assert _rust_fallback_count() == fallback_before
    finally:
        record_property("binding_calls", ",".join(calls))
        record_property("fallback_delta", _rust_fallback_count() - fallback_before)
        if handle is not None:
            _rust._debug_set_fault_injection_rule_enabled(handle, rule_id, False)
        if asynchronous:
            await client.close()
        else:
            client.close()
