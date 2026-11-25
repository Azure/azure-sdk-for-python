# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Native deletion failures preserve the database and allow a later successful delete."""

from contextlib import AsyncExitStack
import inspect
import time
import uuid
from urllib.parse import urlsplit

import pytest

from azure.cosmos import CosmosClient, _rust, exceptions
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from common.throughput_fixtures import owned_database, owned_database_async
from config.settings import TestSettings, unique_database_id

pytestmark = [pytest.mark.cosmosSdkFaultInjection, pytest.mark.asyncio, pytest.mark.cosmosEmulator]


# Source: (new) Persist the verified native deletion 401 and repeated-429 failure scenarios.
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("status", [401, 429], ids=["unauthorized", "repeated-throttling"])
async def test_delete_database_native_failure_preserves_database_and_recovers_rust(
    monkeypatch, record_property, asynchronous, status,
):
    assert urlsplit(TestSettings.host).hostname in ("localhost", "127.0.0.1", "::1")
    rule_id = "delete-failure-" + uuid.uuid4().hex
    activity_id = str(uuid.uuid4())
    rule = {
        "id": rule_id,
        "operation_type": "All",
        "status_code": status,
        "response_headers": {"x-ms-activity-id": activity_id},
        "probability": 1.0,
        "hit_limit": None,
        "enabled": False,
    }
    if status == 429:
        # Delayed responses exhaust the operation deadline before the retry-count limit.
        rule["delay_ms"] = 1000

    async def invoke(method, *args, **kwargs):
        result = method(*args, **kwargs)
        return await result if inspect.isawaitable(result) else result

    async with AsyncExitStack() as stack:
        client = (AsyncCosmosClient if asynchronous else CosmosClient)(
            TestSettings.host, TestSettings.masterKey, _backend="rust", _fault_injection_rules=[rule],
        )
        database_id = unique_database_id("delete-failure")
        if asynchronous:
            await stack.enter_async_context(client)
            database = await stack.enter_async_context(owned_database_async(client, database_id))
        else:
            stack.enter_context(client)
            database = stack.enter_context(owned_database(client, database_id))
        original = await invoke(database.read)
        handle = await invoke(client._adapter._ensure_driver_handle)
        assert _rust._debug_fault_injection_rule_hit_count(handle, rule_id) == 0
        operation = "delete_database_async" if asynchronous else "delete_database"
        native_delete = getattr(_rust, operation)
        calls = []

        def observed_delete(*args, **kwargs):
            assert args[0] is handle
            calls.append(operation)
            return native_delete(*args, **kwargs)

        monkeypatch.setattr(_rust, operation, observed_delete)
        hooks = []
        timeout = 3
        error_type = exceptions.CosmosHttpResponseError if status == 401 else exceptions.CosmosClientTimeoutError
        _rust._debug_set_fault_injection_rule_enabled(handle, rule_id, True)
        try:
            started = time.monotonic()
            with pytest.raises(error_type) as caught:
                await invoke(client.delete_database, database_id, timeout=timeout, response_hook=hooks.append)
            elapsed = time.monotonic() - started
            hits = _rust._debug_fault_injection_rule_hit_count(handle, rule_id)
            record_property("delete_fault_hits", hits)
            record_property("delete_elapsed_seconds", elapsed)
            assert calls == [operation], "The SDK must not replay deletion after a native failure"
            assert hooks == []
            if status == 401:
                assert caught.value.status_code == 401
                assert caught.value.headers["x-ms-activity-id"] == activity_id
                assert hits == 1
            else:
                assert hits >= 2, "Exercise native retries, not just a single throttled attempt"
                assert timeout - 0.5 <= elapsed < timeout + 5
        finally:
            # The rule matches all requests on this client; disable it before reads and cleanup.
            _rust._debug_set_fault_injection_rule_enabled(handle, rule_id, False)

        preserved = await invoke(database.read)
        assert preserved["id"] == database_id
        assert preserved["_rid"] == original["_rid"], "The original database must still exist"
        assert await invoke(client.delete_database, database_id, response_hook=hooks.append) is None
        assert calls == [operation, operation]
        assert len(hooks) == 1
        assert hooks[0]["x-ms-activity-id"]
        with pytest.raises(exceptions.CosmosResourceNotFoundError) as missing:
            await invoke(database.read)
        assert missing.value.status_code == 404
        assert _rust._debug_fault_injection_rule_hit_count(handle, rule_id) == hits
