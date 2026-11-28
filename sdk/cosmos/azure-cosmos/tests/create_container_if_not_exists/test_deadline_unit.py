# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Shared container workflow budgets across the real Python adapter boundary."""
import asyncio
import inspect
import json
import socket
import subprocess
import time
from unittest.mock import MagicMock

import pytest

from common.sdk_subprocess import sdk_python_command
from config.diagnostics import fault_rule_hit_count, fault_rule_hit_count_async

from azure.cosmos import PartitionKey
from azure.cosmos.exceptions import CosmosClientTimeoutError, CosmosResourceNotFoundError
from azure.cosmos.http_constants import SubStatusCodes
from common.test_client_timeout_defaults_unit import client_setup as case, clock as clock


def _complete(value):
    return asyncio.run(value) if inspect.isawaitable(value) else value


def _response(status):
    body = {"message": "missing"} if status == 404 else {"id": "orders", "_rid": "rid"}
    return status, 0, {"x-ms-request-charge": "1"}, json.dumps(body).encode(), None


def _invoke(case, **kwargs):
    return _complete(case.client.get_database_client("sales").create_container_if_not_exists(
        "orders", PartitionKey(path="/pk"), **kwargs
    ))


@pytest.mark.parametrize("existing", [False, True])
@pytest.mark.parametrize("options,budget", [
    ({}, 1), ({"timeout": None}, 1), ({"timeout": 2}, 2),
    ({"timeout": 2, "request_options": {"timeout": 3}}, 2),
])
def test_read_and_create_share_budget_and_next_call_starts_fresh_rust(case, clock, existing, options, budget):
    calls = []

    def read(*_args, **kwargs):
        calls.append(("read", kwargs["timeout_seconds"]))
        clock[0] += 0.75
        return _response(200 if existing else 404)

    def create(*_args, **kwargs):
        calls.append(("create", kwargs["timeout_seconds"]))
        return _response(201)

    case.add_fake_request("read_container", side_effect=read)
    case.add_fake_request("create_container", side_effect=create)
    hook = MagicMock()
    assert _invoke(case, response_hook=hook, **options).id == "orders"
    assert calls == [("read", budget)] + ([] if existing else [("create", budget - 0.75)])
    hook.assert_called_once()
    calls.clear()
    assert _invoke(case).id == "orders"
    assert calls == [("read", 1)] + ([] if existing else [("create", 0.25)])


@pytest.mark.parametrize("phase", ["missing-read", "existing-read", "create"])
def test_expiry_prevents_later_requests_and_success_hook_rust(case, clock, phase):
    calls = []

    def read(*_args, **_kwargs):
        calls.append("read")
        clock[0] += 0.25 if phase == "create" else 1.25
        return _response(200 if phase == "existing-read" else 404)

    def create(*_args, **kwargs):
        calls.append("create")
        assert kwargs["timeout_seconds"] == 0.75
        clock[0] += 1
        return _response(201)

    case.add_fake_request("read_container", side_effect=read)
    case.add_fake_request("create_container", side_effect=create)
    hook = MagicMock()
    with pytest.raises(CosmosClientTimeoutError):
        _invoke(case, response_hook=hook)
    assert calls == (["read", "create"] if phase == "create" else ["read"])
    hook.assert_not_called()
    assert not case.client.client_connection._container_properties_cache


@pytest.mark.parametrize("existing", [False, True])
def test_customer_hook_timeout_is_not_reclassified_or_replayed_rust(case, clock, existing):
    read = case.add_fake_request("read_container", result=_response(200 if existing else 404))
    create = case.add_fake_request("create_container", result=_response(201))
    failure = TimeoutError("customer callback")

    def hook(*_args):
        clock[0] += 2
        raise failure

    with pytest.raises(TimeoutError) as caught:
        _invoke(case, response_hook=hook)
    assert caught.value is failure
    assert read.call_count == 1
    assert create.call_count == int(not existing)


@pytest.mark.parametrize("expires", [False, True])
def test_conflict_reread_uses_remaining_budget_rust(case, clock, expires):
    calls = []

    def read(*_args, **kwargs):
        calls.append(("read", kwargs["timeout_seconds"]))
        if len(calls) == 1:
            clock[0] += 0.25
            return _response(404)
        return _response(200)

    def create(*_args, **kwargs):
        calls.append(("create", kwargs["timeout_seconds"]))
        clock[0] += 1 if expires else 0.25
        return _response(409)

    case.add_fake_request("read_container", side_effect=read)
    case.add_fake_request("create_container", side_effect=create)
    hook = MagicMock()
    if expires:
        with pytest.raises(CosmosClientTimeoutError):
            _invoke(case, response_hook=hook)
        hook.assert_not_called()
        assert not case.client.client_connection._container_properties_cache
    else:
        assert _invoke(case, response_hook=hook).id == "orders"
        hook.assert_called_once()
    assert calls == [("read", 1), ("create", 0.75)] + ([] if expires else [("read", 0.5)])


@pytest.mark.parametrize("outcome", ["ready", "deadline", "limit"])
def test_conflict_reread_waits_for_container_creation_rust(case, clock, monkeypatch, outcome):
    calls = []
    waits = []
    budget = 30 if outcome == "limit" else 1

    def wait(delay):
        waits.append(delay)
        clock[0] += delay

    async def wait_async(delay):
        wait(delay)

    monkeypatch.setattr(time, "sleep", wait)
    monkeypatch.setattr(asyncio, "sleep", wait_async)

    def read(*_args, **kwargs):
        calls.append(kwargs["timeout_seconds"])
        if len(calls) == 1:
            return _response(404)
        if outcome == "ready" and len(calls) == 4:
            return _response(200)
        return (
            404, SubStatusCodes.CONTAINER_CREATE_IN_PROGRESS, {},
            b'{"message":"Collection is not yet available for read. Please retry in some time."}', None,
        )

    case.add_fake_request("read_container", side_effect=read)
    create = case.add_fake_request("create_container", result=_response(409))
    hook = MagicMock()
    if outcome == "ready":
        proxy, properties = _invoke(case, response_hook=hook, return_properties=True, timeout=budget)
        assert proxy.id == properties["id"] == "orders"
        assert len(waits) == 2
        hook.assert_called_once()
    else:
        expected = CosmosClientTimeoutError if outcome == "deadline" else CosmosResourceNotFoundError
        with pytest.raises(expected) as caught:
            _invoke(case, response_hook=hook, timeout=budget)
        if outcome == "limit":
            assert caught.value.sub_status == SubStatusCodes.CONTAINER_CREATE_IN_PROGRESS
            assert 0 < sum(waits) < budget
        else:
            assert sum(waits) == pytest.approx(budget)
        hook.assert_not_called()
        assert not case.client.client_connection._container_properties_cache
    create.assert_called_once()
    assert 1 < len(calls) <= 11
    assert all(0 < delay <= 1 for delay in waits)
    assert all(0 < remaining <= budget for remaining in calls)
    assert calls[-1] < calls[0]


@pytest.mark.parametrize("case", [True], indirect=True, ids=["async"])
def test_cancellation_stops_container_creation_wait_rust(case, monkeypatch):
    transient = (404, SubStatusCodes.CONTAINER_CREATE_IN_PROGRESS, {}, b'{"message":"creating"}', None)
    read = case.add_fake_request("read_container", side_effect=[_response(404), transient])
    create = case.add_fake_request("create_container", result=_response(409))
    hook = MagicMock()

    async def cancel(_delay):
        raise asyncio.CancelledError()

    monkeypatch.setattr(asyncio, "sleep", cancel)
    with pytest.raises(asyncio.CancelledError):
        _invoke(case, response_hook=hook)
    assert read.call_count == 2
    create.assert_called_once()
    hook.assert_not_called()


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("operation", ["create-if-missing", "delete", "replace"])
def test_real_binding_bounds_container_workflows_rust(asynchronous, operation):
    # Isolate native runtimes from the mocked clocks and adapters in this suite.
    result = subprocess.run(
        sdk_python_command(
            "from create_container_if_not_exists.test_deadline_unit import "
            "_run_delayed_container_workflow; "
            f"_run_delayed_container_workflow({asynchronous!r}, {operation!r})"
        ),
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def _run_delayed_container_workflow(asynchronous, operation):
    """Two 600 ms responses must not fit into a one-second operation.

    Fault injection answers every request inside the Rust driver, so nothing
    goes over the network. The endpoint is a port nobody listens on, so any
    request a rule does not answer fails instead of passing silently.
    """
    from azure.cosmos import ConnectionPoolOptions, CosmosClient, CosmosRuntime
    from azure.cosmos.aio import CosmosClient as AsyncCosmosClient

    with socket.socket() as unused:
        unused.bind(("127.0.0.1", 0))
        endpoint = f"http://127.0.0.1:{unused.getsockname()[1]}"
    location = {"name": "East US", "databaseAccountEndpoint": endpoint}
    account = {"id": "test", "_rid": "AQAAAA==", "_self": "",
               "writableLocations": [location], "readableLocations": [location]}
    properties = {
        "id": "orders", "_rid": "AQAAAIABAAA=", "_self": "dbs/AQAAAA==/colls/AQAAAIABAAA=/",
        "partitionKey": {"paths": ["/pk"], "kind": "Hash", "version": 2},
    }
    missing = operation == "create-if-missing"
    write_status = {"create-if-missing": 201, "replace": 200, "delete": 204}[operation]
    # The first matching rule wins, so the container read must come before the
    # catch-all rule that answers the create, replace, or delete.
    rules = [
        {"id": "account", "operation_type": "MetadataReadDatabaseAccount", "status_code": 200,
         "response_body": json.dumps(account).encode(), "probability": 1.0},
        {"id": "read", "operation_type": "MetadataReadContainer", "delay_ms": 600,
         "status_code": 404 if missing else 200,
         "response_body": json.dumps({"code": "NotFound"} if missing else properties).encode(),
         "probability": 1.0},
        {"id": "write", "operation_type": "All", "delay_ms": 600, "status_code": write_status,
         "response_body": b"" if write_status == 204 else json.dumps(properties).encode(),
         "probability": 1.0},
    ]
    runtime = CosmosRuntime.create(connection_pool=ConnectionPoolOptions(proxy_allowed=False))
    client_type = AsyncCosmosClient if asynchronous else CosmosClient
    client = client_type(
        endpoint, "ZmFrZQ==", _backend="rust", timeout=1, runtime=runtime,
        _fault_injection_rules=rules,
    )
    hook = MagicMock()

    async def hit_count(rule_id):
        counter = fault_rule_hit_count_async if asynchronous else fault_rule_hit_count
        return await _awaited(counter(client._adapter, rule_id))

    async def run():
        try:
            if asynchronous:
                await asyncio.wait_for(client._adapter.initialize(), 5)
            else:
                client._adapter._ensure_driver_handle(deadline=time.monotonic() + 5)
            started = time.monotonic()
            with pytest.raises(CosmosClientTimeoutError):
                database = client.get_database_client("sales")
                if operation == "delete":
                    result = database.delete_container("orders", response_hook=hook)
                elif operation == "replace":
                    result = database.replace_container(
                        "orders", PartitionKey(path="/pk"), response_hook=hook
                    )
                else:
                    result = database.create_container_if_not_exists(
                        "orders", PartitionKey(path="/pk"), response_hook=hook
                    )
                await _awaited(result)
            elapsed = time.monotonic() - started
            # Each step alone fits in one second; only running them one after
            # the other on a shared budget runs out of time.
            assert 0.8 <= elapsed < 1.5, elapsed
            assert await hit_count("read") == 1
            assert await hit_count("write") == 1
            hook.assert_not_called()
        finally:
            await _awaited(client.close())

    asyncio.run(run())


async def _awaited(value):
    return await value if inspect.isawaitable(value) else value


@pytest.mark.parametrize("expire_source_read", [False, True])
def test_gsi_source_read_shares_get_or_create_budget_rust(case, clock, expire_source_read):
    calls = []

    def read(*_args, **kwargs):
        calls.append(("read", kwargs["timeout_seconds"]))
        if len(calls) == 1:
            clock[0] += 0.25
            return _response(404)
        clock[0] += 1 if expire_source_read else 0.25
        return _response(200)

    def create(*_args, **kwargs):
        calls.append(("create", kwargs["timeout_seconds"]))
        return _response(201)

    case.add_fake_request("read_container", side_effect=read)
    case.add_fake_request("create_container", side_effect=create)
    hook = MagicMock()
    options = {"global_secondary_index": {"sourceCollectionId": "source"}, "response_hook": hook}
    if expire_source_read:
        with pytest.raises(CosmosClientTimeoutError):
            _invoke(case, **options)
        hook.assert_not_called()
    else:
        assert _invoke(case, **options).id == "orders"
        hook.assert_called_once()
    assert calls == [("read", 1), ("read", 0.75)] + (
        [] if expire_source_read else [("create", 0.5)]
    )
