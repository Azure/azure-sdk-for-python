# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Client budgets at the public boundary, with no service requests."""

import asyncio
import inspect
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.cosmos import CosmosClient
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos._backend import _binding_adapter_shared as shared
from azure.cosmos._backend import binding_adapter as sync_binding
from azure.cosmos.aio._backend import binding_adapter as async_binding
from azure.cosmos._backend.operations import OP_TO_BINDING_FUNCTION_NAME, get_page_binding_function_name
from azure.cosmos._backend.contracts import PreparedPageRequest, PreparedRequest
from azure.cosmos._backend.partition_key_input import BindingPartitionKey
from azure.cosmos.exceptions import CosmosClientTimeoutError, CosmosHttpResponseError
from azure.cosmos._backend.errors import BindingProtocolError


def _complete(value):
    return asyncio.run(value) if inspect.isawaitable(value) else value


def _response(status=201, headers=None, body=None):
    return status, 0, headers or {}, json.dumps(body or {"id": "sales"}).encode(), None


@pytest.fixture
def cold_async_client(monkeypatch):
    client = AsyncCosmosClient("https://alpha-bank.documents.azure.com", "key", timeout=1, _backend="rust")
    entered = threading.Event()
    finish = threading.Event()
    handle = object()
    workers = []

    def make_worker(*, target, args=(), name, daemon):
        worker = threading.Thread(target=target, args=args, name=name, daemon=daemon)
        workers.append(worker)
        return worker

    def acquire(*_args):
        entered.set()
        assert finish.wait(10), "test did not release acquisition"
        return handle

    native = SimpleNamespace(
        acquire_driver_handle=MagicMock(side_effect=acquire),
        release_driver_handle=MagicMock(),
        _DriverResponseError=type("_DriverResponseError", (RuntimeError,), {}),
        _DriverTransportError=type("_DriverTransportError", (RuntimeError,), {}),
    )
    monkeypatch.setattr(async_binding, "_rust_module", native)
    monkeypatch.setattr(shared, "threading", SimpleNamespace(Thread=make_worker, Lock=threading.Lock))
    try:
        yield SimpleNamespace(client=client, entered=entered, finish=finish, handle=handle, native=native)
    finally:
        # Let acquisition finish before restoring the binding used by this test.
        finish.set()
        for worker in workers:
            worker.join(timeout=5)
        asyncio.run(client.close())
        assert all(not worker.is_alive() for worker in workers)


@pytest.mark.parametrize(
    "operation", ["create_item", "read_item", "upsert_item", "replace_item", "patch_item", "delete_item"]
)
@pytest.mark.parametrize("client_default", [False, True], ids=["per-call", "client-default"])
def test_cold_async_item_timeout_returns_before_acquisition_finishes_rust(cold_async_client, operation, client_default):
    case = cold_async_client
    dispatch = AsyncMock(return_value=_response())
    setattr(case.native, operation + "_async", dispatch)
    container = case.client.get_database_client("sales").get_container_client("orders")
    body = {"id": "order-42", "pk": "A"}
    arguments = {
        "create_item": (body,),
        "read_item": ("order-42",),
        "upsert_item": (body,),
        "replace_item": ("order-42", body),
        "patch_item": ("order-42",),
        "delete_item": ("order-42",),
    }
    options = {} if client_default else {"timeout": 1}
    if operation not in ("create_item", "upsert_item"):
        options["partition_key"] = "A"
    if operation == "patch_item":
        options["patch_operations"] = [{"op": "set", "path": "/value", "value": 1}]

    async def run():
        try:
            with pytest.raises(CosmosClientTimeoutError):
                await asyncio.wait_for(getattr(container, operation)(*arguments[operation], **options), 2)
            assert not case.finish.is_set()
            pending = case.client._adapter._init_future
            assert pending is not None and not pending.done()
            dispatch.assert_not_called()
            # A later caller shares initialization rather than starting another worker.
            survivor = asyncio.create_task(case.client._adapter.initialize())
            case.finish.set()
            await asyncio.wait_for(survivor, 2)
            assert case.client._adapter._driver_handle is case.handle
            case.native.acquire_driver_handle.assert_called_once()
        finally:
            case.finish.set()
            pending = case.client._adapter._init_future
            if pending is not None:
                await asyncio.gather(asyncio.wrap_future(pending), return_exceptions=True)
            await case.client.close()
        case.native.release_driver_handle.assert_called_once_with(case.handle)

    asyncio.run(run())


@pytest.mark.parametrize("outcome", ["reuse", "close", "failure"])
def test_timed_out_async_acquisition_preserves_late_worker_ownership_rust(cold_async_client, outcome):
    case = cold_async_client
    adapter = case.client._adapter
    request = PreparedRequest(
        op="read_item",
        container_link="dbs/sales/colls/orders",
        body_bytes=b"",
        partition_key=BindingPartitionKey("components", ("A",)),
        item_id="order-42",
    )
    case.native.read_item_async = AsyncMock(return_value=_response(200))
    error = RuntimeError("late acquisition failure")
    if outcome == "failure":

        def fail(*_args):
            case.entered.set()
            assert case.finish.wait(10)
            raise error

        case.native.acquire_driver_handle.side_effect = fail

    async def run():
        loop_errors = []
        loop = asyncio.get_running_loop()
        loop.set_exception_handler(lambda _loop, context: loop_errors.append(context))
        pending = None
        try:
            with pytest.raises(CosmosClientTimeoutError):
                await asyncio.wait_for(adapter.execute(request, deadline=time.monotonic() + 0.05), 2)
            pending = adapter._init_future
            assert pending is not None and not pending.done()
            case.native.read_item_async.assert_not_called()
            if outcome == "close":
                await adapter.close()
            case.finish.set()
            result = (await asyncio.gather(asyncio.wrap_future(pending), return_exceptions=True))[0]
            await asyncio.sleep(0)
            if outcome == "reuse":
                assert result is case.handle
                await adapter.execute(request, deadline=time.monotonic() + 2)
                case.native.acquire_driver_handle.assert_called_once()
                assert 0 < case.native.read_item_async.call_args.kwargs["timeout_seconds"] <= 2
            elif outcome == "close":
                assert isinstance(result, RuntimeError) and "closed during initialization" in str(result)
                assert adapter._driver_handle is None
                case.native.release_driver_handle.assert_called_once_with(case.handle)
            else:
                assert result is error
                assert adapter._driver_handle is None
                case.native.acquire_driver_handle.side_effect = None
                case.native.acquire_driver_handle.return_value = case.handle
                await adapter.execute(request)
                assert case.native.acquire_driver_handle.call_count == 2
            assert not loop_errors
        finally:
            case.finish.set()
            if pending is not None:
                await asyncio.gather(asyncio.wrap_future(pending), return_exceptions=True)
            await adapter.close()
            loop.set_exception_handler(None)
        case.native.release_driver_handle.assert_called_once_with(case.handle)

    asyncio.run(run())


def test_async_acquisition_starts_with_default_pool_busy_rust(cold_async_client):
    """A busy default pool blocks neither acquisition nor release of its late handle."""
    case = cold_async_client
    case.native.read_item_async = AsyncMock(return_value=_response(200))
    occupied = threading.Event()
    unblock = threading.Event()

    def occupy():
        occupied.set()
        assert unblock.wait(10), "test did not free the default pool"

    async def run():
        loop = asyncio.get_running_loop()
        loop.set_default_executor(ThreadPoolExecutor(max_workers=1))
        blocker = loop.run_in_executor(None, occupy)
        pending = None
        try:
            assert occupied.wait(2), "the default pool worker did not start"
            container = case.client.get_database_client("sales").get_container_client("orders")
            with pytest.raises(CosmosClientTimeoutError):
                await asyncio.wait_for(container.read_item("order-42", partition_key="A", timeout=1), 2)
            pending = case.client._adapter._init_future
            assert pending is not None and not pending.done()
            assert case.entered.is_set()
            assert not blocker.done()
            case.native.acquire_driver_handle.assert_called_once()
            case.native.release_driver_handle.assert_not_called()
            case.native.read_item_async.assert_not_called()
            # Keep the pool busy while close finishes and the acquisition thread releases the handle.
            await asyncio.wait_for(case.client.close(), 2)
            assert case.client._adapter._closing
            assert case.client._adapter._driver_handle is None
            case.finish.set()
            with pytest.raises(RuntimeError, match="closed during initialization"):
                await asyncio.wait_for(asyncio.wrap_future(pending), 2)
            case.native.release_driver_handle.assert_called_once_with(case.handle)
            case.native.read_item_async.assert_not_called()
            assert not blocker.done()
        finally:
            unblock.set()
            case.finish.set()
            await blocker
            if pending is not None:
                await asyncio.gather(asyncio.wrap_future(pending), return_exceptions=True)
            await case.client.close()

    asyncio.run(run())


@pytest.mark.parametrize("cancel_first", [False, True], ids=["timeout", "cancellation"])
def test_one_async_waiter_leaving_does_not_cancel_shared_acquisition_rust(cold_async_client, cancel_first):
    case = cold_async_client
    adapter = case.client._adapter
    request = PreparedRequest(
        op="read_item",
        container_link="dbs/sales/colls/orders",
        body_bytes=b"",
        partition_key=BindingPartitionKey("components", ("A",)),
        item_id="order-42",
    )
    dispatch = AsyncMock(return_value=_response(200))
    case.native.read_item_async = dispatch

    async def run():
        first = asyncio.create_task(adapter.execute(request, deadline=time.monotonic() + (5 if cancel_first else 0.1)))
        survivor = asyncio.create_task(adapter.execute(request, deadline=time.monotonic() + 5))
        try:
            while not case.entered.is_set():
                await asyncio.sleep(0)
            if cancel_first:
                first.cancel()
            with pytest.raises(asyncio.CancelledError if cancel_first else CosmosClientTimeoutError):
                await asyncio.wait_for(first, 2)
            assert not survivor.done()
            assert adapter._init_future is not None and not adapter._init_future.done()
            dispatch.assert_not_called()
            case.finish.set()
            await asyncio.wait_for(survivor, 2)
            case.native.acquire_driver_handle.assert_called_once()
            dispatch.assert_awaited_once()
            assert dispatch.call_args.args[0] is case.handle
        finally:
            case.finish.set()
            await asyncio.gather(first, survivor, return_exceptions=True)
            await adapter.close()
        case.native.release_driver_handle.assert_called_once_with(case.handle)

    asyncio.run(run())


@pytest.mark.parametrize("path", ["execute", "metadata", "page"])
@pytest.mark.parametrize("expired", [False, True])
def test_async_auxiliary_paths_bound_acquisition_with_same_deadline_rust(cold_async_client, path, expired):
    case = cold_async_client
    adapter = case.client._adapter
    dispatch = AsyncMock()
    name = {
        "execute": "read_item_async",
        "metadata": "get_container_metadata_async",
        "page": get_page_binding_function_name("list_databases", uses_cursor=False) + "_async",
    }[path]
    setattr(case.native, name, dispatch)

    async def run():
        deadline = time.monotonic() + (-1 if expired else 0.05)
        pages = None
        try:
            if path == "execute":
                operation = adapter.execute(
                    PreparedRequest(
                        op="read_item",
                        container_link="dbs/sales/colls/orders",
                        body_bytes=b"",
                        partition_key=BindingPartitionKey("components", ("A",)),
                        item_id="order-42",
                    ),
                    deadline=deadline,
                )
            elif path == "metadata":
                operation = adapter.get_container_metadata("dbs/sales/colls/orders", deadline=deadline)
            else:
                pages = adapter.execute_pages(
                    PreparedPageRequest(op="list_databases", container_link=""), deadline=deadline
                )
                operation = pages.__anext__()
            with pytest.raises(CosmosClientTimeoutError):
                await asyncio.wait_for(operation, 2)
            dispatch.assert_not_called()
            if expired:
                assert adapter._init_future is None
                case.native.acquire_driver_handle.assert_not_called()
            else:
                assert adapter._init_future is not None and not adapter._init_future.done()
        finally:
            case.finish.set()
            if adapter._init_future is not None:
                await asyncio.gather(asyncio.wrap_future(adapter._init_future), return_exceptions=True)
            if pages is not None:
                await pages.aclose()
            await adapter.close()

    asyncio.run(run())


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("name", sorted(OP_TO_BINDING_FUNCTION_NAME.values()))
def test_native_execute_exports_accept_generic_adapter_keywords_rust(name, asynchronous):
    from azure.cosmos import _rust

    function = getattr(_rust, name + ("_async" if asynchronous else ""))
    parameters = inspect.signature(function).parameters
    for keyword, default in (("timeout_seconds", None), ("include_attempts", False)):
        assert keyword in parameters, f"{function.__name__} must accept {keyword}"
        assert parameters[keyword].kind == inspect.Parameter.KEYWORD_ONLY
        assert parameters[keyword].default is default
    # Reach request validation through the real export, not a permissive mock.
    prepared = SimpleNamespace(protocol_version=PreparedRequest.protocol_version, op="wrong-operation")
    with pytest.raises(ValueError, match="PreparedRequest.op"):
        function(None, prepared, timeout_seconds=0.125, include_attempts=True)


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
        client=client,
        install=install,
        asynchronous=asynchronous,
        acquisition=acquisition,
        native=native,
    )
    _complete(client.close())


@pytest.fixture(params=[
    "create_item", "read_item", "upsert_item", "replace_item", "patch_item", "delete_item",
])
def item_timeout_case(case, request):
    operation = request.param
    container = case.client.get_database_client("sales").get_container_client("orders")
    body = {"id": "order-42", "pk": "A"}
    dispatch = case.install(
        operation, result=_response(204 if operation == "delete_item" else 200, body=body),
    )

    def call(options):
        kwargs = dict(options)
        if operation in ("create_item", "upsert_item"):
            return _complete(getattr(container, operation)(body, **kwargs))
        kwargs["partition_key"] = "A"
        if operation == "replace_item":
            return _complete(container.replace_item("order-42", body, **kwargs))
        if operation == "patch_item":
            kwargs["patch_operations"] = [{"op": "set", "path": "/value", "value": 1}]
        return _complete(getattr(container, operation)("order-42", **kwargs))

    return SimpleNamespace(call=call, dispatch=dispatch, acquisition=case.acquisition)


@pytest.mark.parametrize("nested", [False, True], ids=["keyword", "request-options"])
@pytest.mark.parametrize(
    "timeout",
    [0, -1, 0.5, True, False, float("nan"), float("inf"), float("-inf"), "1", 2**64, 10**1000],
    ids=["zero", "negative", "subsecond", "true", "false", "nan", "infinity",
         "negative-infinity", "string", "upper-bound", "overflow"],
)
def test_invalid_item_timeout_is_value_error_before_driver_acquisition_rust(
    item_timeout_case, timeout, nested,
):
    options = {"request_options": {"timeout": timeout}} if nested else {"timeout": timeout}
    with pytest.raises(ValueError, match="timeout must be None or a finite number of seconds"):
        item_timeout_case.call(options)
    item_timeout_case.acquisition.assert_not_called()
    item_timeout_case.dispatch.assert_not_called()


@pytest.mark.parametrize("nested", [False, True], ids=["keyword", "request-options"])
@pytest.mark.parametrize("timeout", [None, 1, 1.5])
def test_valid_item_timeout_preserves_default_and_override_rust(item_timeout_case, timeout, nested):
    options = {"request_options": {"timeout": timeout}} if nested else {"timeout": timeout}
    item_timeout_case.call(options)
    item_timeout_case.dispatch.assert_called_once()
    prepared = item_timeout_case.dispatch.call_args.args[1]
    assert prepared.settings.timeout_seconds == (1 if timeout is None else timeout)


def test_explicit_item_timeout_overrides_invalid_nested_timeout_rust(item_timeout_case):
    item_timeout_case.call({"timeout": 1.5, "request_options": {"timeout": float("nan")}})
    item_timeout_case.dispatch.assert_called_once()
    assert item_timeout_case.dispatch.call_args.args[1].settings.timeout_seconds == 1.5


@pytest.fixture
def clock(monkeypatch):
    now = [100.0]
    monkeypatch.setattr(time, "monotonic", lambda: now[0])
    return now


def test_local_feed_range_uses_real_export_with_timeout_and_telemetry_rust(case, monkeypatch):
    from azure.cosmos import _rust

    module = async_binding if case.asynchronous else sync_binding
    monkeypatch.setattr(module, "_rust_module", _rust)
    if case.asynchronous:
        _rust._create_runtime()
    contribution = MagicMock()
    contribution.response.side_effect = lambda envelope: envelope[0]
    operation = MagicMock()
    operation.begin_contribution.return_value = contribution
    monkeypatch.setattr(module, "get_operation", lambda *_: operation)
    feed_range = {"Range": {"min": "", "max": "FF", "isMinInclusive": True, "isMaxInclusive": False}}
    prepared = PreparedRequest(
        op="is_feed_range_subset",
        container_link="dbs/sales/colls/orders",
        body_bytes=json.dumps({"parent": feed_range, "child": feed_range}).encode(),
        partition_key=BindingPartitionKey("cross_partition"),
    )
    response = _complete(case.client._adapter.execute(prepared))
    assert json.loads(response.body) == {"IsSubset": True}
    contribution.response.assert_called_once()
    envelope = contribution.response.call_args.args[0]
    assert len(envelope) == 2
    assert envelope[1] is None
    contribution.error.assert_not_called()


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
def test_default_override_and_next_call_reset_rust(case, clock, options, expected):
    original = json.loads(json.dumps(options))
    dispatch = case.install("create_database", result=_response())
    _complete(case.client.create_database("sales", **options))
    _complete(case.client.create_database("sales"))
    assert [call.kwargs["timeout_seconds"] for call in dispatch.call_args_list] == [expected, 1]
    assert options == original


def test_driver_setup_consumes_default_budget_before_dispatch_rust(case, clock):
    def setup(**_kwargs):
        clock[0] += 1.25
        return "test-driver"

    case.acquisition.side_effect = setup
    dispatch = case.install("create_database", result=_response())
    with pytest.raises(CosmosClientTimeoutError):
        _complete(case.client.create_database("sales"))
    dispatch.assert_not_called()


def _collect_feed_ranges(result, asynchronous):
    async def collect():
        return [value async for value in result]

    return asyncio.run(collect()) if asynchronous else list(result)


@pytest.mark.parametrize("options,expected", [({}, 1), ({"timeout": 5}, 5), ({"timeout": None}, 1)])
@pytest.mark.parametrize("force_refresh", [False, True])
def test_feed_range_discovery_keeps_default_and_override_budgets_rust(case, clock, options, expected, force_refresh):
    def setup(**_kwargs):
        clock[0] += 0.25
        return "test-driver"

    case.acquisition.side_effect = setup
    dispatch = case.install(
        "read_feed_ranges",
        result=_response(200, body={"PartitionKeyRanges": [{"minInclusive": "", "maxExclusive": "FF"}]}),
    )
    container = case.client.get_database_client("sales").get_container_client("orders")
    result = container.read_feed_ranges(force_refresh=force_refresh, **options)
    case.acquisition.assert_not_called()
    dispatch.assert_not_called()
    clock[0] += 100
    values = _collect_feed_ranges(result, case.asynchronous)
    assert values == [{"Range": {"min": "", "max": "FF", "isMinInclusive": True, "isMaxInclusive": False}}]
    assert dispatch.call_args.kwargs["timeout_seconds"] == expected - 0.25
    assert json.loads(dispatch.call_args.args[1].body_bytes) == {"forceRefresh": force_refresh}

    clock[0] += 100
    _collect_feed_ranges(container.read_feed_ranges(), case.asynchronous)
    assert dispatch.call_args.kwargs["timeout_seconds"] == 0.75
    assert dispatch.call_count == 2


def test_feed_range_discovery_does_not_restart_budget_after_setup_rust(case, clock):
    def setup(**_kwargs):
        clock[0] += 1.25
        return "test-driver"

    case.acquisition.side_effect = setup
    dispatch = case.install("read_feed_ranges")
    container = case.client.get_database_client("sales").get_container_client("orders")
    with pytest.raises(CosmosClientTimeoutError):
        _collect_feed_ranges(container.read_feed_ranges(), case.asynchronous)
    dispatch.assert_not_called()


@pytest.mark.parametrize("conflict", [False, True])
def test_get_or_create_shares_default_across_read_create_and_recovery_rust(case, clock, conflict):
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


def test_get_or_create_does_not_reset_default_after_not_found_rust(case, clock):
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


def test_native_default_expiration_uses_public_exception_rust(case):
    failure = TimeoutError("native operation deadline")
    case.install("create_database", side_effect=failure)
    with pytest.raises(CosmosClientTimeoutError) as caught:
        _complete(case.client.create_database("sales"))
    assert caught.value.__cause__ is failure


@pytest.mark.parametrize("operation", ["get_or_create", "metadata", "page"])
@pytest.mark.parametrize("status", [None, (429, 0), (429, 3200)])
def test_driver_timeout_preserves_only_available_throttle_cause_rust(case, operation, status):
    failure = TimeoutError("driver operation deadline")
    if status is not None:
        failure.__dict__["_cosmos_timeout_throttle_status"] = status
    hook = MagicMock()
    create = case.install("create_database", result=_response())
    if operation == "get_or_create":
        case.install("read_database", side_effect=failure)
        call = lambda: _complete(case.client.create_database_if_not_exists("sales", response_hook=hook))
    elif operation == "metadata":
        case.install("get_container_metadata", side_effect=failure)
        call = lambda: _complete(case.client._adapter.get_container_metadata("dbs/sales/colls/orders"))
    else:
        name = get_page_binding_function_name("list_databases", uses_cursor=False)
        case.install(name, side_effect=failure)
        pages = case.client.list_databases(response_hook=hook).by_page()
        call = lambda: _complete(pages.__anext__()) if case.asynchronous else next(pages)
    with pytest.raises(CosmosClientTimeoutError) as caught:
        call()
    assert caught.value.__cause__ is failure
    if status is None:
        assert caught.value.inner_exception is failure
    else:
        inner = caught.value.inner_exception
        assert isinstance(inner, CosmosHttpResponseError)
        assert inner.status_code == 429
        assert inner.sub_status == (status[1] or None)
        assert inner.headers == {}
        assert "response details are unavailable" in inner.message
    hook.assert_not_called()
    create.assert_not_called()


@pytest.mark.parametrize("status", [(503, 0), (429, -1), (429, True), (429,), None])
def test_driver_timeout_rejects_malformed_throttle_metadata_rust(status):
    failure = TimeoutError("driver operation deadline")
    failure.__dict__["_cosmos_timeout_throttle_status"] = status
    with pytest.raises(BindingProtocolError, match="invalid timeout throttle status"):
        shared.operation_timeout_error(failure)


def test_response_hook_timeout_is_not_reclassified_rust(case):
    failure = TimeoutError("customer callback")
    hook = MagicMock(side_effect=failure)
    case.install("create_database", result=_response())
    with pytest.raises(TimeoutError) as caught:
        _complete(case.client.create_database("sales", response_hook=hook))
    assert caught.value is failure
    hook.assert_called_once()


def test_metadata_default_covers_setup_and_converts_native_expiration_rust(case, clock):
    failure = TimeoutError("metadata deadline")
    dispatch = case.install("get_container_metadata", side_effect=failure)
    with pytest.raises(CosmosClientTimeoutError) as caught:
        _complete(case.client._adapter.get_container_metadata("dbs/sales/colls/orders"))
    assert caught.value.__cause__ is failure
    assert dispatch.call_args.kwargs["timeout_seconds"] == 1


@pytest.mark.parametrize("operation", ["create", "read", "upsert", "replace", "patch", "delete"])
def test_item_operations_inherit_client_default_rust(case, clock, operation):
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
            "item": "order-42",
            "partition_key": "customer-17",
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
def test_each_page_gets_fresh_default_after_application_delay_rust(case, clock, options, expected):
    budgets = []

    def fetch(*args, **kwargs):
        budgets.append(kwargs["timeout_seconds"])
        clock[0] += 0.25
        return _response(
            200,
            {"x-ms-continuation": "next"} if len(budgets) == 1 else {},
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


def test_page_default_expiration_uses_public_exception_rust(case):
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
def test_default_does_not_become_unsupported_explicit_throughput_option_rust(case, monkeypatch, resource, operation):
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
    assert replacement.call_args.kwargs["kwargs"]["timeout"] == 1
    assert case.client._adapter._client_config.operation_timeout_seconds == 1


def test_async_cancellation_remains_cancellation_rust(monkeypatch):
    async def run():
        client = AsyncCosmosClient("https://alpha-bank.documents.azure.com", "key", timeout=1, _backend="rust")
        started = asyncio.Event()
        cancelled = asyncio.Event()

        async def dispatch(*args, **kwargs):
            started.set()
            try:
                await asyncio.Future()
            finally:
                cancelled.set()

        monkeypatch.setattr(async_binding, "_rust_module", SimpleNamespace(create_database_async=dispatch))
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


def test_async_default_expires_while_waiting_for_driver_setup_rust(monkeypatch):
    async def run():
        client = AsyncCosmosClient("https://alpha-bank.documents.azure.com", "key", timeout=1, _backend="rust")
        cancelled = asyncio.Event()
        dispatch = AsyncMock(return_value=_response())

        async def setup():
            try:
                await asyncio.Future()
            finally:
                cancelled.set()

        monkeypatch.setattr(async_binding, "_rust_module", SimpleNamespace(create_database_async=dispatch))
        monkeypatch.setattr(client._adapter, "_ensure_driver_handle", setup)
        try:
            with pytest.raises(CosmosClientTimeoutError):
                await asyncio.wait_for(client.create_database("sales"), timeout=3)
            assert cancelled.is_set()
            dispatch.assert_not_called()
        finally:
            await client.close()

    asyncio.run(run())
