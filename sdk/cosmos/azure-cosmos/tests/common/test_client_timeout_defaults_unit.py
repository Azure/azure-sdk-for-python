# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Client budgets at the public boundary, with no service requests."""
import asyncio
import inspect
import json
import time
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.cosmos import CosmosClient
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos._backend import binding_adapter as sync_binding
from azure.cosmos.aio._backend import binding_adapter as async_binding
from azure.cosmos._backend.operations import get_page_binding_function_name
from azure.cosmos.exceptions import CosmosClientTimeoutError


def _complete(value):
    return asyncio.run(value) if inspect.isawaitable(value) else value


def _response(status=201, headers=None, body=None):
    return status, 0, headers or {}, json.dumps(body or {"id": "sales"}).encode(), None


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def case(request, monkeypatch):
    asynchronous = request.param
    client_type = AsyncCosmosClient if asynchronous else CosmosClient
    client = client_type("https://alpha-bank.documents.azure.com", "key", timeout=1, _backend="rust")
    module = async_binding if asynchronous else sync_binding
    native = SimpleNamespace()
    mock_type = AsyncMock if asynchronous else MagicMock
    monkeypatch.setattr(module, "_rust_module", native)
    acquisition = mock_type(return_value="test-driver")
    monkeypatch.setattr(client._adapter, "_ensure_driver_handle", acquisition)

    def install(name, *, side_effect=None, result=None):
        function = mock_type(side_effect=side_effect, return_value=result)
        setattr(native, name + ("_async" if asynchronous else ""), function)
        return function

    yield SimpleNamespace(
        client=client, install=install, asynchronous=asynchronous,
        acquisition=acquisition, native=native,
    )
    _complete(client.close())


@pytest.fixture
def clock(monkeypatch):
    now = [100.0]
    monkeypatch.setattr(time, "monotonic", lambda: now[0])
    return now


@pytest.mark.parametrize(
    "options,expected",
    [
        ({}, 1),
        ({"timeout": 4}, 4),
        ({"request_options": {"timeout": 3}}, 3),
        ({"timeout": 4, "request_options": {"timeout": 3}}, 4),
        ({"timeout": None}, 1),
        ({"request_options": {"timeout": None}}, 1),
        ({"timeout": None, "request_options": {"timeout": 3}}, 1),
    ],
)
def test_default_override_and_next_call_reset(case, clock, options, expected):
    original = json.loads(json.dumps(options))
    dispatch = case.install("create_database", result=_response())
    _complete(case.client.create_database("sales", **options))
    _complete(case.client.create_database("sales"))
    assert [call.kwargs["timeout_seconds"] for call in dispatch.call_args_list] == [expected, 1]
    assert options == original


def test_driver_setup_consumes_default_budget_before_dispatch(case, clock):
    def setup():
        clock[0] += 1.25
        return "test-driver"

    case.acquisition.side_effect = setup
    dispatch = case.install("create_database", result=_response())
    with pytest.raises(CosmosClientTimeoutError):
        _complete(case.client.create_database("sales"))
    dispatch.assert_not_called()


@pytest.mark.parametrize("conflict", [False, True])
def test_get_or_create_shares_default_across_read_create_and_recovery(case, clock, conflict):
    calls = []

    def read(*args, **kwargs):
        calls.append(("read", kwargs["timeout_seconds"]))
        clock[0] += 0.25
        return _response(404 if len(calls) == 1 else 200)

    def create(*args, **kwargs):
        calls.append(("create", kwargs["timeout_seconds"]))
        clock[0] += 0.25
        return _response(409 if conflict else 201)

    case.install("read_database", side_effect=read)
    case.install("create_database", side_effect=create)
    result = _complete(case.client.create_database_if_not_exists("sales"))
    assert result.id == "sales"
    assert calls == [("read", 1), ("create", 0.75)] + ([("read", 0.5)] if conflict else [])


def test_get_or_create_does_not_reset_default_after_not_found(case, clock):
    calls = []

    def dispatch(status, **kwargs):
        calls.append(kwargs["timeout_seconds"])
        clock[0] += 0.75
        return _response(status)

    case.install("read_database", side_effect=lambda *a, **kw: dispatch(404, **kw))
    case.install("create_database", side_effect=lambda *a, **kw: dispatch(201, **kw))
    with pytest.raises(CosmosClientTimeoutError):
        _complete(case.client.create_database_if_not_exists("sales"))
    assert calls == [1, 0.25]


def test_native_default_expiration_uses_public_exception(case):
    failure = TimeoutError("native operation deadline")
    case.install("create_database", side_effect=failure)
    with pytest.raises(CosmosClientTimeoutError) as caught:
        _complete(case.client.create_database("sales"))
    assert caught.value.__cause__ is failure


def test_response_hook_timeout_is_not_reclassified(case):
    failure = TimeoutError("customer callback")
    hook = MagicMock(side_effect=failure)
    case.install("create_database", result=_response())
    with pytest.raises(TimeoutError) as caught:
        _complete(case.client.create_database("sales", response_hook=hook))
    assert caught.value is failure
    hook.assert_called_once()


def test_metadata_default_covers_setup_and_converts_native_expiration(case, clock):
    failure = TimeoutError("metadata deadline")
    dispatch = case.install("get_container_metadata", side_effect=failure)
    with pytest.raises(CosmosClientTimeoutError) as caught:
        _complete(case.client._adapter.get_container_metadata("dbs/sales/colls/orders"))
    assert caught.value.__cause__ is failure
    assert dispatch.call_args.kwargs["timeout_seconds"] == 1


@pytest.mark.parametrize("operation", ["create", "read", "upsert", "replace", "patch", "delete"])
def test_item_operations_inherit_client_default(case, clock, operation):
    body = {"id": "order-42", "customerId": "customer-17"}
    case.install("get_container_metadata", result=("orders-rid", ("/customerId",), "Hash", False))
    dispatch = case.install(operation + "_item", result=_response(200, body=body))
    container = case.client.get_database_client("sales").get_container_client("orders")
    if operation in ("create", "upsert"):
        kwargs = {"body": body}
    elif operation == "replace":
        kwargs = {"item": "order-42", "body": body}
    elif operation == "patch":
        kwargs = {
            "item": "order-42", "partition_key": "customer-17",
            "patch_operations": [{"op": "add", "path": "/processed", "value": True}],
        }
    else:
        kwargs = {"item": "order-42", "partition_key": "customer-17"}
    _complete(getattr(container, operation + "_item")(**kwargs))
    assert dispatch.call_args.kwargs["timeout_seconds"] == 1


@pytest.mark.parametrize(
    "options,expected",
    [({}, 1), ({"timeout": 3}, 3), ({"feed_options": {"timeout": 2}}, 2)],
)
def test_each_page_gets_fresh_default_after_application_delay(case, clock, options, expected):
    budgets = []

    def fetch(*args, **kwargs):
        budgets.append(kwargs["timeout_seconds"])
        clock[0] += 0.25
        return _response(
            200, {"x-ms-continuation": "next"} if len(budgets) == 1 else {},
            {"Databases": [{"id": "sales"}]},
        )

    name = get_page_binding_function_name("list_databases", uses_cursor=False)
    case.install(name, side_effect=fetch)
    original = json.loads(json.dumps(options))
    pages = case.client.list_databases(**options).by_page()

    async def next_async_page():
        page = await pages.__anext__()
        return [item async for item in page]

    def next_page():
        return asyncio.run(next_async_page()) if case.asynchronous else list(next(pages))

    assert next_page() == [{"id": "sales"}]
    clock[0] += 100
    assert next_page() == [{"id": "sales"}]
    assert budgets == [expected, expected]
    assert options == original


def test_page_default_expiration_uses_public_exception(case):
    failure = TimeoutError("native page deadline")
    name = get_page_binding_function_name("list_databases", uses_cursor=False)
    case.install(name, side_effect=failure)
    pages = case.client.list_databases().by_page()
    with pytest.raises(CosmosClientTimeoutError) as caught:
        if case.asynchronous:
            asyncio.run(pages.__anext__())
        else:
            next(pages)
    assert caught.value.__cause__ is failure


@pytest.mark.parametrize("resource", ["database", "container"])
@pytest.mark.parametrize("operation", ["get", "replace"])
def test_default_does_not_become_unsupported_explicit_throughput_option(case, monkeypatch, resource, operation):
    database = case.client.get_database_client("sales")
    if resource == "container":
        if case.asynchronous:
            from azure.cosmos.aio import _container as module
        else:
            from azure.cosmos import container as module
        helper = "_get_throughput" if operation == "get" else "_replace_container_throughput"
        proxy = database.get_container_client("orders")
    else:
        if case.asynchronous:
            from azure.cosmos.aio import _database as module
        else:
            from azure.cosmos import database as module
        helper = operation + "_database_throughput" + ("_async" if case.asynchronous else "")
        proxy = database
    replacement = AsyncMock(return_value="throughput") if case.asynchronous else MagicMock(return_value="throughput")
    monkeypatch.setattr(module, helper, replacement)
    method = proxy.get_throughput if operation == "get" else proxy.replace_throughput
    assert _complete(method(*(() if operation == "get" else (400,)))) == "throughput"
    assert "timeout" not in replacement.call_args.kwargs["kwargs"]
    assert case.client._adapter._client_config.operation_timeout_seconds == 1


def test_async_cancellation_remains_cancellation(monkeypatch):
    async def run():
        client = AsyncCosmosClient(
            "https://alpha-bank.documents.azure.com", "key", timeout=1, _backend="rust"
        )
        started = asyncio.Event()
        cancelled = asyncio.Event()

        async def dispatch(*args, **kwargs):
            started.set()
            try:
                await asyncio.Future()
            finally:
                cancelled.set()

        monkeypatch.setattr(
            async_binding, "_rust_module", SimpleNamespace(create_database_async=dispatch)
        )
        monkeypatch.setattr(client._adapter, "_ensure_driver_handle", AsyncMock(return_value="test-driver"))
        task = asyncio.create_task(client.create_database("sales"))
        try:
            await started.wait()
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
            assert cancelled.is_set()
        finally:
            await client.close()

    asyncio.run(run())


def test_async_default_expires_while_waiting_for_driver_setup(monkeypatch):
    async def run():
        client = AsyncCosmosClient(
            "https://alpha-bank.documents.azure.com", "key", timeout=1, _backend="rust"
        )
        cancelled = asyncio.Event()
        dispatch = AsyncMock(return_value=_response())

        async def setup():
            try:
                await asyncio.Future()
            finally:
                cancelled.set()

        monkeypatch.setattr(
            async_binding, "_rust_module", SimpleNamespace(create_database_async=dispatch)
        )
        monkeypatch.setattr(client._adapter, "_ensure_driver_handle", setup)
        try:
            with pytest.raises(CosmosClientTimeoutError):
                await asyncio.wait_for(client.create_database("sales"), timeout=3)
            assert cancelled.is_set()
            dispatch.assert_not_called()
        finally:
            await client.close()

    asyncio.run(run())
