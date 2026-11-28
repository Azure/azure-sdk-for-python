# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Offline tests for the time limit on CosmosClient operations.

The ``timeout`` setting is the most time, in seconds, that one operation may
take, including retries. It can be set on the client as the default for every
operation, or on a single call. When the time runs out, the operation raises
``CosmosClientTimeoutError``.

Terms used in this file:

- compiled module: the part of the SDK that sends most requests to the service.
- adapter: the Python object that passes the client's requests to the compiled
  module.
- handle: the object the compiled module returns when the client first
  connects to the account. The client uses it for every later request.
- connect thread: the background thread the async client uses to connect, so
  the event loop is not blocked. Every caller waiting for the connect shares it.
- feed range: a part of a container's data, set by a range of partition key
  values.
- diagnostics recording: when turned on, the SDK records details of each
  request attempt, such as retries, for logging.
- throttled: the service replied 429 (too many requests) and the SDK waits
  before retrying.

Most tests replace the compiled module with a fake. No request reaches a real
account.
"""

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
from azure.cosmos._backend import binding_adapter as sync_adapter_module
from azure.cosmos.aio._backend import binding_adapter as async_adapter_module
from azure.cosmos._backend.operations import OP_TO_BINDING_FUNCTION_NAME, get_page_binding_function_name
from azure.cosmos._backend.contracts import PreparedPageRequest, PreparedRequest
from azure.cosmos._backend.partition_key_input import BindingPartitionKey
from azure.cosmos.exceptions import CosmosClientTimeoutError, CosmosHttpResponseError
from azure.cosmos._backend.errors import BindingProtocolError


def _await_if_needed(value):
    """Return the value, first running it to the end if it is an async call.

    This lets one test cover both the sync and async clients.
    """
    return asyncio.run(value) if inspect.isawaitable(value) else value


def _fake_reply(status=201, headers=None, body=None):
    """Build a fake reply from the compiled module: status code, sub-status,
    headers, body and diagnostics (None here)."""
    return status, 0, headers or {}, json.dumps(body or {"id": "sales"}).encode(), None


@pytest.fixture
def async_client_still_connecting(monkeypatch):
    """Async client with a 1-second default time limit. Its connect stays in
    progress until the test sets ``let_connect_finish``."""
    client = AsyncCosmosClient("https://alpha-bank.documents.azure.com", "key", timeout=1, _backend="rust")
    connect_started = threading.Event()
    let_connect_finish = threading.Event()
    fake_handle = object()
    connect_threads = []

    def record_connect_thread(*, target, args=(), name, daemon):
        thread = threading.Thread(target=target, args=args, name=name, daemon=daemon)
        connect_threads.append(thread)
        return thread

    def slow_open_handle(*_args):
        connect_started.set()
        assert let_connect_finish.wait(10), "test did not let the connect finish"
        return fake_handle

    fake_module = SimpleNamespace(
        acquire_driver_handle=MagicMock(side_effect=slow_open_handle),
        release_driver_handle=MagicMock(),
        _DriverResponseError=type("_DriverResponseError", (RuntimeError,), {}),
        _DriverTransportError=type("_DriverTransportError", (RuntimeError,), {}),
    )
    monkeypatch.setattr(async_adapter_module, "_rust_module", fake_module)
    monkeypatch.setattr(shared, "threading", SimpleNamespace(Thread=record_connect_thread, Lock=threading.Lock))
    try:
        yield SimpleNamespace(
            client=client,
            connect_started=connect_started,
            let_connect_finish=let_connect_finish,
            fake_handle=fake_handle,
            fake_module=fake_module,
        )
    finally:
        # Let the connect finish before the fake module is removed.
        let_connect_finish.set()
        for thread in connect_threads:
            thread.join(timeout=5)
        asyncio.run(client.close())
        assert all(not thread.is_alive() for thread in connect_threads)


@pytest.mark.parametrize(
    "operation", ["create_item", "read_item", "upsert_item", "replace_item", "patch_item", "delete_item"]
)
@pytest.mark.parametrize("client_default", [False, True], ids=["per-call", "client-default"])
def test_async_item_call_times_out_while_client_is_still_connecting_rust(
    async_client_still_connecting, operation, client_default
):
    """An item call whose time limit runs out while the client is still
    connecting raises ``CosmosClientTimeoutError`` straight away.

    The connect keeps going. A later caller waits for that same connect and
    gets its handle, so the client connects to the account only once. The time
    limit comes from either the call or the client default.
    """
    setup = async_client_still_connecting
    send_request = AsyncMock(return_value=_fake_reply())
    setattr(setup.fake_module, operation + "_async", send_request)
    container = setup.client.get_database_client("sales").get_container_client("orders")
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
            assert not setup.let_connect_finish.is_set()
            connect_result = setup.client._adapter._init_future
            assert connect_result is not None and not connect_result.done()
            send_request.assert_not_called()
            # A later caller waits for the same connect instead of starting a new one.
            later_caller = asyncio.create_task(setup.client._adapter.initialize())
            setup.let_connect_finish.set()
            await asyncio.wait_for(later_caller, 2)
            assert setup.client._adapter._driver_handle is setup.fake_handle
            setup.fake_module.acquire_driver_handle.assert_called_once()
        finally:
            setup.let_connect_finish.set()
            connect_result = setup.client._adapter._init_future
            if connect_result is not None:
                await asyncio.gather(asyncio.wrap_future(connect_result), return_exceptions=True)
            await setup.client.close()
        setup.fake_module.release_driver_handle.assert_called_once_with(setup.fake_handle)

    asyncio.run(run())


@pytest.mark.parametrize("outcome", ["reuse", "close", "failure"])
def test_connect_that_finishes_after_a_timeout_is_handled_correctly_rust(async_client_still_connecting, outcome):
    """A request times out while the client is still connecting, and the
    connect finishes afterwards. Three cases:

    - reuse: the connect succeeds, and the next request uses its handle
      without connecting again.
    - close: the client was closed in the meantime, so the handle is released
      and the connect raises "closed during initialization".
    - failure: the connect fails, and the next request starts a new connect.

    No case leaves an unhandled error on the event loop.
    """
    setup = async_client_still_connecting
    adapter = setup.client._adapter
    read_request = PreparedRequest(
        op="read_item",
        container_link="dbs/sales/colls/orders",
        body_bytes=b"",
        partition_key=BindingPartitionKey("components", ("A",)),
        item_id="order-42",
    )
    setup.fake_module.read_item_async = AsyncMock(return_value=_fake_reply(200))
    connect_error = RuntimeError("late connect failure")
    if outcome == "failure":

        def failing_open_handle(*_args):
            setup.connect_started.set()
            assert setup.let_connect_finish.wait(10)
            raise connect_error

        setup.fake_module.acquire_driver_handle.side_effect = failing_open_handle

    async def run():
        unhandled_loop_errors = []
        loop = asyncio.get_running_loop()
        loop.set_exception_handler(lambda _loop, context: unhandled_loop_errors.append(context))
        connect_result = None
        try:
            with pytest.raises(CosmosClientTimeoutError):
                await asyncio.wait_for(adapter.execute(read_request, deadline=time.monotonic() + 0.05), 2)
            connect_result = adapter._init_future
            assert connect_result is not None and not connect_result.done()
            setup.fake_module.read_item_async.assert_not_called()
            if outcome == "close":
                await adapter.close()
            setup.let_connect_finish.set()
            connect_outcome = (await asyncio.gather(asyncio.wrap_future(connect_result), return_exceptions=True))[0]
            await asyncio.sleep(0)
            if outcome == "reuse":
                assert connect_outcome is setup.fake_handle
                await adapter.execute(read_request, deadline=time.monotonic() + 2)
                setup.fake_module.acquire_driver_handle.assert_called_once()
                assert 0 < setup.fake_module.read_item_async.call_args.kwargs["timeout_seconds"] <= 2
            elif outcome == "close":
                assert isinstance(connect_outcome, RuntimeError)
                assert "closed during initialization" in str(connect_outcome)
                assert adapter._driver_handle is None
                setup.fake_module.release_driver_handle.assert_called_once_with(setup.fake_handle)
            else:
                assert connect_outcome is connect_error
                assert adapter._driver_handle is None
                setup.fake_module.acquire_driver_handle.side_effect = None
                setup.fake_module.acquire_driver_handle.return_value = setup.fake_handle
                await adapter.execute(read_request)
                assert setup.fake_module.acquire_driver_handle.call_count == 2
            assert not unhandled_loop_errors
        finally:
            setup.let_connect_finish.set()
            if connect_result is not None:
                await asyncio.gather(asyncio.wrap_future(connect_result), return_exceptions=True)
            await adapter.close()
            loop.set_exception_handler(None)
        setup.fake_module.release_driver_handle.assert_called_once_with(setup.fake_handle)

    asyncio.run(run())


def test_async_connect_works_while_event_loop_thread_pool_is_busy_rust(async_client_still_connecting):
    """The event loop's default thread pool is kept busy for the whole test.

    The client can still connect, time out, close and release the handle that
    arrives later, because it connects on its own connect thread.
    """
    setup = async_client_still_connecting
    setup.fake_module.read_item_async = AsyncMock(return_value=_fake_reply(200))
    pool_busy = threading.Event()
    free_pool = threading.Event()

    def keep_pool_busy():
        pool_busy.set()
        assert free_pool.wait(10), "test did not free the default pool"

    async def run():
        loop = asyncio.get_running_loop()
        loop.set_default_executor(ThreadPoolExecutor(max_workers=1))
        pool_task = loop.run_in_executor(None, keep_pool_busy)
        connect_result = None
        try:
            assert pool_busy.wait(2), "the default pool thread did not start"
            container = setup.client.get_database_client("sales").get_container_client("orders")
            with pytest.raises(CosmosClientTimeoutError):
                await asyncio.wait_for(container.read_item("order-42", partition_key="A", timeout=1), 2)
            connect_result = setup.client._adapter._init_future
            assert connect_result is not None and not connect_result.done()
            assert setup.connect_started.is_set()
            assert not pool_task.done()
            setup.fake_module.acquire_driver_handle.assert_called_once()
            setup.fake_module.release_driver_handle.assert_not_called()
            setup.fake_module.read_item_async.assert_not_called()
            # Keep the pool busy while the client closes and the connect thread releases the handle.
            await asyncio.wait_for(setup.client.close(), 2)
            assert setup.client._adapter._closing
            assert setup.client._adapter._driver_handle is None
            setup.let_connect_finish.set()
            with pytest.raises(RuntimeError, match="closed during initialization"):
                await asyncio.wait_for(asyncio.wrap_future(connect_result), 2)
            setup.fake_module.release_driver_handle.assert_called_once_with(setup.fake_handle)
            setup.fake_module.read_item_async.assert_not_called()
            assert not pool_task.done()
        finally:
            free_pool.set()
            setup.let_connect_finish.set()
            await pool_task
            if connect_result is not None:
                await asyncio.gather(asyncio.wrap_future(connect_result), return_exceptions=True)
            await setup.client.close()

    asyncio.run(run())


@pytest.mark.parametrize("cancel_first", [False, True], ids=["timeout", "cancellation"])
def test_one_caller_giving_up_does_not_stop_the_shared_connect_rust(async_client_still_connecting, cancel_first):
    """Two requests wait for the same connect. If the first one times out or
    is cancelled, the connect keeps going, and the second request still
    completes using its handle."""
    setup = async_client_still_connecting
    adapter = setup.client._adapter
    read_request = PreparedRequest(
        op="read_item",
        container_link="dbs/sales/colls/orders",
        body_bytes=b"",
        partition_key=BindingPartitionKey("components", ("A",)),
        item_id="order-42",
    )
    send_request = AsyncMock(return_value=_fake_reply(200))
    setup.fake_module.read_item_async = send_request

    async def run():
        first_deadline = time.monotonic() + (5 if cancel_first else 0.1)
        first_request = asyncio.create_task(adapter.execute(read_request, deadline=first_deadline))
        second_request = asyncio.create_task(adapter.execute(read_request, deadline=time.monotonic() + 5))
        try:
            while not setup.connect_started.is_set():
                await asyncio.sleep(0)
            if cancel_first:
                first_request.cancel()
            with pytest.raises(asyncio.CancelledError if cancel_first else CosmosClientTimeoutError):
                await asyncio.wait_for(first_request, 2)
            assert not second_request.done()
            assert adapter._init_future is not None and not adapter._init_future.done()
            send_request.assert_not_called()
            setup.let_connect_finish.set()
            await asyncio.wait_for(second_request, 2)
            setup.fake_module.acquire_driver_handle.assert_called_once()
            send_request.assert_awaited_once()
            assert send_request.call_args.args[0] is setup.fake_handle
        finally:
            setup.let_connect_finish.set()
            await asyncio.gather(first_request, second_request, return_exceptions=True)
            await adapter.close()
        setup.fake_module.release_driver_handle.assert_called_once_with(setup.fake_handle)

    asyncio.run(run())


@pytest.mark.parametrize("request_kind", ["item", "container-details", "page"])
@pytest.mark.parametrize("time_already_up", [False, True])
def test_every_request_kind_counts_connect_time_against_its_time_limit_rust(
    async_client_still_connecting, request_kind, time_already_up
):
    """Item requests, container-detail reads and page fetches all count time
    spent connecting against their time limit. If the time is already used up,
    no connect is started at all."""
    setup = async_client_still_connecting
    adapter = setup.client._adapter
    send_request = AsyncMock()
    function_name = {
        "item": "read_item_async",
        "container-details": "get_container_metadata_async",
        "page": get_page_binding_function_name("list_databases", uses_cursor=False) + "_async",
    }[request_kind]
    setattr(setup.fake_module, function_name, send_request)

    async def run():
        deadline = time.monotonic() + (-1 if time_already_up else 0.05)
        pages = None
        try:
            if request_kind == "item":
                call = adapter.execute(
                    PreparedRequest(
                        op="read_item",
                        container_link="dbs/sales/colls/orders",
                        body_bytes=b"",
                        partition_key=BindingPartitionKey("components", ("A",)),
                        item_id="order-42",
                    ),
                    deadline=deadline,
                )
            elif request_kind == "container-details":
                call = adapter.get_container_metadata("dbs/sales/colls/orders", deadline=deadline)
            else:
                pages = adapter.execute_pages(
                    PreparedPageRequest(op="list_databases", container_link=""), deadline=deadline
                )
                call = pages.__anext__()
            with pytest.raises(CosmosClientTimeoutError):
                await asyncio.wait_for(call, 2)
            send_request.assert_not_called()
            if time_already_up:
                assert adapter._init_future is None
                setup.fake_module.acquire_driver_handle.assert_not_called()
            else:
                assert adapter._init_future is not None and not adapter._init_future.done()
        finally:
            setup.let_connect_finish.set()
            if adapter._init_future is not None:
                await asyncio.gather(asyncio.wrap_future(adapter._init_future), return_exceptions=True)
            if pages is not None:
                await pages.aclose()
            await adapter.close()

    asyncio.run(run())


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("function_name", sorted(OP_TO_BINDING_FUNCTION_NAME.values()))
def test_compiled_request_functions_accept_time_limit_and_attempt_details_rust(function_name, asynchronous):
    """Every request function in the compiled module, sync and async, accepts
    two keyword-only arguments from the adapter: ``timeout_seconds`` (the time
    left, default None) and ``include_attempts`` (also return details of each
    request attempt, default False).

    Each real function is called with both keywords and a request for the
    wrong operation, to show that the keywords are accepted and the request is
    still checked.
    """
    from azure.cosmos import _rust

    request_function = getattr(_rust, function_name + ("_async" if asynchronous else ""))
    parameters = inspect.signature(request_function).parameters
    for keyword, default in (("timeout_seconds", None), ("include_attempts", False)):
        assert keyword in parameters, f"{request_function.__name__} must accept {keyword}"
        assert parameters[keyword].kind == inspect.Parameter.KEYWORD_ONLY
        assert parameters[keyword].default is default
    # Call the real function, not a fake, so the request check really runs.
    wrong_request = SimpleNamespace(protocol_version=PreparedRequest.protocol_version, op="wrong-operation")
    with pytest.raises(ValueError, match="PreparedRequest.op"):
        request_function(None, wrong_request, timeout_seconds=0.125, include_attempts=True)


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def client_setup(request, monkeypatch):
    """Sync or async client with a 1-second default time limit.

    Connecting is replaced by a fake that returns the handle ``"fake-handle"``
    straight away. ``add_fake_request(name, ...)`` adds a fake request function
    to a fake compiled module.
    """
    asynchronous = request.param
    client_type = AsyncCosmosClient if asynchronous else CosmosClient
    client = client_type("https://alpha-bank.documents.azure.com", "key", timeout=1, _backend="rust")
    adapter_module = async_adapter_module if asynchronous else sync_adapter_module
    fake_module = SimpleNamespace()
    mock_type = AsyncMock if asynchronous else MagicMock
    monkeypatch.setattr(adapter_module, "_rust_module", fake_module)
    open_handle = mock_type(return_value="fake-handle")
    monkeypatch.setattr(client._adapter, "_ensure_driver_handle", open_handle)

    def add_fake_request(name, *, side_effect=None, result=None):
        fake_function = mock_type(side_effect=side_effect, return_value=result)
        setattr(fake_module, name + ("_async" if asynchronous else ""), fake_function)
        return fake_function

    yield SimpleNamespace(
        client=client,
        add_fake_request=add_fake_request,
        asynchronous=asynchronous,
        open_handle=open_handle,
        fake_module=fake_module,
    )
    _await_if_needed(client.close())


@pytest.fixture(params=[
    "create_item", "read_item", "upsert_item", "replace_item", "patch_item", "delete_item",
])
def item_call(client_setup, request):
    """One of the six item operations on container ``orders``, with a faked
    reply. ``call(options)`` runs it with the given options."""
    operation = request.param
    container = client_setup.client.get_database_client("sales").get_container_client("orders")
    body = {"id": "order-42", "pk": "A"}
    send_request = client_setup.add_fake_request(
        operation, result=_fake_reply(204 if operation == "delete_item" else 200, body=body),
    )

    def call(options):
        kwargs = dict(options)
        if operation in ("create_item", "upsert_item"):
            return _await_if_needed(getattr(container, operation)(body, **kwargs))
        kwargs["partition_key"] = "A"
        if operation == "replace_item":
            return _await_if_needed(container.replace_item("order-42", body, **kwargs))
        if operation == "patch_item":
            kwargs["patch_operations"] = [{"op": "set", "path": "/value", "value": 1}]
        return _await_if_needed(getattr(container, operation)("order-42", **kwargs))

    return SimpleNamespace(call=call, send_request=send_request, open_handle=client_setup.open_handle)


@pytest.mark.parametrize("nested", [False, True], ids=["keyword", "request-options"])
@pytest.mark.parametrize(
    "timeout",
    [0, -1, 0.5, True, False, float("nan"), float("inf"), float("-inf"), "1", 2**64, 10**1000],
    ids=["zero", "negative", "subsecond", "true", "false", "nan", "infinity",
         "negative-infinity", "string", "upper-bound", "overflow"],
)
def test_invalid_item_time_limit_raises_value_error_before_connecting_rust(
    item_call, timeout, nested,
):
    """An item time limit must be None, or a finite number of seconds that is
    at least 1 and less than 2**64.

    Any other value, including True and False, raises ValueError before the
    client connects or sends anything. This applies to ``timeout=`` and to the
    timeout inside ``request_options``.
    """
    options = {"request_options": {"timeout": timeout}} if nested else {"timeout": timeout}
    with pytest.raises(ValueError, match="timeout must be None or a finite number of seconds"):
        item_call.call(options)
    item_call.open_handle.assert_not_called()
    item_call.send_request.assert_not_called()


@pytest.mark.parametrize("nested", [False, True], ids=["keyword", "request-options"])
@pytest.mark.parametrize("timeout", [None, 1, 1.5])
def test_valid_item_time_limit_is_used_and_none_means_client_default_rust(item_call, timeout, nested):
    """A valid time limit on an item call is passed on as given. None means
    the client default (1 second here)."""
    options = {"request_options": {"timeout": timeout}} if nested else {"timeout": timeout}
    item_call.call(options)
    item_call.send_request.assert_called_once()
    sent_request = item_call.send_request.call_args.args[1]
    assert sent_request.settings.timeout_seconds == (1 if timeout is None else timeout)


def test_timeout_keyword_wins_over_request_options_timeout_rust(item_call):
    """When ``timeout=`` is given, the timeout inside ``request_options`` is
    ignored, even if it is invalid."""
    item_call.call({"timeout": 1.5, "request_options": {"timeout": float("nan")}})
    item_call.send_request.assert_called_once()
    assert item_call.send_request.call_args.args[1].settings.timeout_seconds == 1.5


@pytest.fixture
def clock(monkeypatch):
    """Fake clock for ``time.monotonic``. A test moves time forward by adding
    seconds to ``clock[0]``."""
    now = [100.0]
    monkeypatch.setattr(time, "monotonic", lambda: now[0])
    return now


def test_feed_range_subset_check_runs_locally_with_diagnostics_rust(client_setup, monkeypatch):
    """Checking whether one feed range is inside another is worked out by the
    compiled module without calling the service.

    This test uses the real compiled module. It checks the answer, and that
    diagnostics recording gets the result with no request-attempt details,
    because no request was sent.
    """
    from azure.cosmos import _rust

    adapter_module = async_adapter_module if client_setup.asynchronous else sync_adapter_module
    monkeypatch.setattr(adapter_module, "_rust_module", _rust)
    if client_setup.asynchronous:
        # Async calls need the compiled module's background runtime to be
        # started first. Normally connecting does this.
        _rust._create_runtime()
    diagnostics_entry = MagicMock()
    diagnostics_entry.response.side_effect = lambda recorded_reply: recorded_reply[0]
    diagnostics_recording = MagicMock()
    diagnostics_recording.begin_contribution.return_value = diagnostics_entry
    monkeypatch.setattr(adapter_module, "get_operation", lambda *_: diagnostics_recording)
    feed_range = {"Range": {"min": "", "max": "FF", "isMinInclusive": True, "isMaxInclusive": False}}
    subset_request = PreparedRequest(
        op="is_feed_range_subset",
        container_link="dbs/sales/colls/orders",
        body_bytes=json.dumps({"parent": feed_range, "child": feed_range}).encode(),
        partition_key=BindingPartitionKey("cross_partition"),
    )
    response = _await_if_needed(client_setup.client._adapter.execute(subset_request))
    assert json.loads(response.body) == {"IsSubset": True}
    diagnostics_entry.response.assert_called_once()
    recorded_reply = diagnostics_entry.response.call_args.args[0]
    assert len(recorded_reply) == 2
    assert recorded_reply[1] is None
    diagnostics_entry.error.assert_not_called()


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
def test_call_time_limit_applies_to_that_call_only_rust(client_setup, clock, options, expected):
    """A time limit given on one call applies to that call only, and the next
    call goes back to the client default.

    ``timeout=`` wins over ``request_options``, and ``timeout=None`` means the
    client default. The caller's options are not changed.
    """
    options_before = json.loads(json.dumps(options))
    send_request = client_setup.add_fake_request("create_database", result=_fake_reply())
    _await_if_needed(client_setup.client.create_database("sales", **options))
    _await_if_needed(client_setup.client.create_database("sales"))
    assert [call.kwargs["timeout_seconds"] for call in send_request.call_args_list] == [expected, 1]
    assert options == options_before


def test_time_spent_connecting_counts_against_time_limit_rust(client_setup, clock):
    """Connecting takes 1.25 seconds, longer than the 1-second default, so the
    call times out before any request is sent."""
    def slow_connect(**_kwargs):
        clock[0] += 1.25
        return "fake-handle"

    client_setup.open_handle.side_effect = slow_connect
    send_request = client_setup.add_fake_request("create_database", result=_fake_reply())
    with pytest.raises(CosmosClientTimeoutError):
        _await_if_needed(client_setup.client.create_database("sales"))
    send_request.assert_not_called()


def _collect_feed_ranges(result, asynchronous):
    """Read all feed ranges from a sync list or an async iterator."""
    async def collect():
        return [value async for value in result]

    return asyncio.run(collect()) if asynchronous else list(result)


@pytest.mark.parametrize("options,expected", [({}, 1), ({"timeout": 5}, 5), ({"timeout": None}, 1)])
@pytest.mark.parametrize("force_refresh", [False, True])
def test_read_feed_ranges_time_limit_starts_when_reading_begins_rust(
    client_setup, clock, options, expected, force_refresh
):
    """``read_feed_ranges`` does nothing until its results are read, so the
    time limit starts then, not when it is called.

    Time spent connecting (0.25 seconds here) comes out of the limit. The
    ``force_refresh`` choice is passed on, and a later call without options
    uses the client default.
    """
    def slow_connect(**_kwargs):
        clock[0] += 0.25
        return "fake-handle"

    client_setup.open_handle.side_effect = slow_connect
    send_request = client_setup.add_fake_request(
        "read_feed_ranges",
        result=_fake_reply(200, body={"PartitionKeyRanges": [{"minInclusive": "", "maxExclusive": "FF"}]}),
    )
    container = client_setup.client.get_database_client("sales").get_container_client("orders")
    feed_ranges = container.read_feed_ranges(force_refresh=force_refresh, **options)
    client_setup.open_handle.assert_not_called()
    send_request.assert_not_called()
    # Time that passes before the results are read does not count.
    clock[0] += 100
    ranges = _collect_feed_ranges(feed_ranges, client_setup.asynchronous)
    assert ranges == [{"Range": {"min": "", "max": "FF", "isMinInclusive": True, "isMaxInclusive": False}}]
    assert send_request.call_args.kwargs["timeout_seconds"] == expected - 0.25
    assert json.loads(send_request.call_args.args[1].body_bytes) == {"forceRefresh": force_refresh}

    clock[0] += 100
    _collect_feed_ranges(container.read_feed_ranges(), client_setup.asynchronous)
    assert send_request.call_args.kwargs["timeout_seconds"] == 0.75
    assert send_request.call_count == 2


def test_read_feed_ranges_times_out_when_connecting_uses_all_the_time_rust(client_setup, clock):
    """Connecting takes longer than the time limit. The limit does not start
    again after connecting, so reading feed ranges times out and no request is
    sent."""
    def slow_connect(**_kwargs):
        clock[0] += 1.25
        return "fake-handle"

    client_setup.open_handle.side_effect = slow_connect
    send_request = client_setup.add_fake_request("read_feed_ranges")
    container = client_setup.client.get_database_client("sales").get_container_client("orders")
    with pytest.raises(CosmosClientTimeoutError):
        _collect_feed_ranges(container.read_feed_ranges(), client_setup.asynchronous)
    send_request.assert_not_called()


@pytest.mark.parametrize("conflict", [False, True])
def test_create_database_if_not_exists_shares_one_time_limit_rust(client_setup, clock, conflict):
    """``create_database_if_not_exists`` reads the database, creates it if it
    is missing, and reads again if another client created it first (409
    conflict). All steps share one time limit, so each step gets only the time
    that is left."""
    steps = []

    def fake_read(*args, **kwargs):
        steps.append(("read", kwargs["timeout_seconds"]))
        clock[0] += 0.25
        return _fake_reply(404 if len(steps) == 1 else 200)

    def fake_create(*args, **kwargs):
        steps.append(("create", kwargs["timeout_seconds"]))
        clock[0] += 0.25
        return _fake_reply(409 if conflict else 201)

    client_setup.add_fake_request("read_database", side_effect=fake_read)
    client_setup.add_fake_request("create_database", side_effect=fake_create)
    result = _await_if_needed(client_setup.client.create_database_if_not_exists("sales"))
    assert result.id == "sales"
    assert steps == [("read", 1), ("create", 0.75)] + ([("read", 0.5)] if conflict else [])


def test_create_database_if_not_exists_times_out_when_steps_use_all_the_time_rust(client_setup, clock):
    """Each step takes 0.75 seconds. The read gets the full 1 second, and the
    create gets only the 0.25 seconds left.

    The time is used up when the create finishes, so the call raises
    ``CosmosClientTimeoutError``, even though the create worked. The limit does
    not start again after the "not found" reply.
    """
    time_given = []

    def fake_step(status, **kwargs):
        time_given.append(kwargs["timeout_seconds"])
        clock[0] += 0.75
        return _fake_reply(status)

    client_setup.add_fake_request("read_database", side_effect=lambda *a, **kw: fake_step(404, **kw))
    client_setup.add_fake_request("create_database", side_effect=lambda *a, **kw: fake_step(201, **kw))
    with pytest.raises(CosmosClientTimeoutError):
        _await_if_needed(client_setup.client.create_database_if_not_exists("sales"))
    assert time_given == [1, 0.25]


def test_time_out_in_compiled_module_raises_cosmos_client_timeout_error_rust(client_setup):
    """When the compiled module runs out of time it raises Python's ``TimeoutError``.
    The caller gets ``CosmosClientTimeoutError`` instead, with the original error
    as its cause.
    """
    time_out = TimeoutError("operation time ran out")
    client_setup.add_fake_request("create_database", side_effect=time_out)
    with pytest.raises(CosmosClientTimeoutError) as caught:
        _await_if_needed(client_setup.client.create_database("sales"))
    assert caught.value.__cause__ is time_out


@pytest.mark.parametrize("operation", ["get_or_create", "metadata", "page"])
@pytest.mark.parametrize(
    "status",
    [None, (429, 0), (429, 3200)],
    ids=["not-throttled", "throttled-no-substatus", "throttled-with-substatus"],
)
def test_time_out_while_throttled_keeps_the_429_as_the_cause_rust(client_setup, operation, status):
    """If the last request before the time ran out was throttled,
    ``CosmosClientTimeoutError.inner_exception`` is a ``CosmosHttpResponseError``
    with status 429 and the sub-status, if there was one. It has no headers, and
    its message says the response details are unavailable. Otherwise
    ``inner_exception`` is the original ``TimeoutError``.

    This holds for ``create_database_if_not_exists``, container-detail reads and
    page fetches. The response hook is not called, and no create is tried after
    the time-out.
    """
    time_out = TimeoutError("operation time ran out")
    if status is not None:
        # The compiled module attaches the last throttle status to the error like this.
        time_out.__dict__["_cosmos_timeout_throttle_status"] = status
    response_hook = MagicMock()
    fake_create = client_setup.add_fake_request("create_database", result=_fake_reply())
    if operation == "get_or_create":
        client_setup.add_fake_request("read_database", side_effect=time_out)
        run_call = lambda: _await_if_needed(
            client_setup.client.create_database_if_not_exists("sales", response_hook=response_hook)
        )
    elif operation == "metadata":
        client_setup.add_fake_request("get_container_metadata", side_effect=time_out)
        run_call = lambda: _await_if_needed(
            client_setup.client._adapter.get_container_metadata("dbs/sales/colls/orders")
        )
    else:
        name = get_page_binding_function_name("list_databases", uses_cursor=False)
        client_setup.add_fake_request(name, side_effect=time_out)
        pages = client_setup.client.list_databases(response_hook=response_hook).by_page()
        run_call = lambda: _await_if_needed(pages.__anext__()) if client_setup.asynchronous else next(pages)
    with pytest.raises(CosmosClientTimeoutError) as caught:
        run_call()
    assert caught.value.__cause__ is time_out
    if status is None:
        assert caught.value.inner_exception is time_out
    else:
        cause = caught.value.inner_exception
        assert isinstance(cause, CosmosHttpResponseError)
        assert cause.status_code == 429
        assert cause.sub_status == (status[1] or None)
        assert cause.headers == {}
        assert "response details are unavailable" in cause.message
    response_hook.assert_not_called()
    fake_create.assert_not_called()


@pytest.mark.parametrize("status", [(503, 0), (429, -1), (429, True), (429,), None])
def test_invalid_throttle_status_on_time_out_is_reported_rust(status):
    """The throttle status attached to a time-out must be exactly
    ``(429, sub-status)``. Anything else means the compiled module sent back bad
    data, so the SDK raises ``BindingProtocolError`` instead of guessing.
    """
    time_out = TimeoutError("operation time ran out")
    time_out.__dict__["_cosmos_timeout_throttle_status"] = status
    with pytest.raises(BindingProtocolError, match="invalid timeout throttle status"):
        shared.operation_timeout_error(time_out)


def test_timeout_error_from_response_hook_is_not_changed_rust(client_setup):
    """A ``TimeoutError`` raised by the customer's own response hook reaches the
    caller unchanged. It is not turned into ``CosmosClientTimeoutError``.
    """
    hook_error = TimeoutError("customer callback")
    response_hook = MagicMock(side_effect=hook_error)
    client_setup.add_fake_request("create_database", result=_fake_reply())
    with pytest.raises(TimeoutError) as caught:
        _await_if_needed(client_setup.client.create_database("sales", response_hook=response_hook))
    assert caught.value is hook_error
    response_hook.assert_called_once()


def test_container_details_read_uses_client_default_and_reports_time_out_rust(client_setup, clock):
    """Reading container details uses the client default time limit (1 second here).
    If the compiled module times out, the caller gets ``CosmosClientTimeoutError``.
    """
    time_out = TimeoutError("metadata deadline")
    send_request = client_setup.add_fake_request("get_container_metadata", side_effect=time_out)
    with pytest.raises(CosmosClientTimeoutError) as caught:
        _await_if_needed(client_setup.client._adapter.get_container_metadata("dbs/sales/colls/orders"))
    assert caught.value.__cause__ is time_out
    assert send_request.call_args.kwargs["timeout_seconds"] == 1


@pytest.mark.parametrize("operation", ["create", "read", "upsert", "replace", "patch", "delete"])
def test_item_operations_use_client_default_time_limit_rust(client_setup, clock, operation):
    """Create, read, upsert, replace, patch and delete use the client default time
    limit when the call does not give one.
    """
    body = {"id": "order-42", "customerId": "customer-17"}
    client_setup.add_fake_request("get_container_metadata", result=("orders-rid", ("/customerId",), "Hash", False))
    send_request = client_setup.add_fake_request(operation + "_item", result=_fake_reply(200, body=body))
    container = client_setup.client.get_database_client("sales").get_container_client("orders")
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
    _await_if_needed(getattr(container, operation + "_item")(**kwargs))
    assert send_request.call_args.kwargs["timeout_seconds"] == 1


@pytest.mark.parametrize(
    "options,expected",
    [({}, 1), ({"timeout": 3}, 3), ({"feed_options": {"timeout": 2}}, 2)],
)
def test_each_page_fetch_gets_the_full_time_limit_rust(client_setup, clock, options, expected):
    """Each page fetch gets the full time limit. Time the customer app spends between
    pages does not count. The limit comes from the client default, ``timeout=``
    or ``feed_options``, and the caller's options are not changed.
    """
    time_given = []

    def fake_fetch_page(*args, **kwargs):
        time_given.append(kwargs["timeout_seconds"])
        clock[0] += 0.25
        return _fake_reply(
            200,
            {"x-ms-continuation": "next"} if len(time_given) == 1 else {},
            {"Databases": [{"id": "sales"}]},
        )

    function_name = get_page_binding_function_name("list_databases", uses_cursor=False)
    client_setup.add_fake_request(function_name, side_effect=fake_fetch_page)
    options_before = json.loads(json.dumps(options))
    pages = client_setup.client.list_databases(**options).by_page()

    async def next_async_page():
        page = await pages.__anext__()
        return [item async for item in page]

    def next_page():
        return asyncio.run(next_async_page()) if client_setup.asynchronous else list(next(pages))

    assert next_page() == [{"id": "sales"}]
    # The customer app takes a long time before asking for the next page.
    clock[0] += 100
    assert next_page() == [{"id": "sales"}]
    assert time_given == [expected, expected]
    assert options == options_before


def test_page_fetch_time_out_raises_cosmos_client_timeout_error_rust(client_setup):
    """When a page fetch runs out of time, the caller gets
    ``CosmosClientTimeoutError``, with the original error as its cause.
    """
    time_out = TimeoutError("page time ran out")
    function_name = get_page_binding_function_name("list_databases", uses_cursor=False)
    client_setup.add_fake_request(function_name, side_effect=time_out)
    pages = client_setup.client.list_databases().by_page()
    with pytest.raises(CosmosClientTimeoutError) as caught:
        if client_setup.asynchronous:
            asyncio.run(pages.__anext__())
        else:
            next(pages)
    assert caught.value.__cause__ is time_out


@pytest.mark.parametrize("resource", ["database", "container"])
@pytest.mark.parametrize("operation", ["get", "replace"])
def test_throughput_calls_use_client_default_time_limit_rust(
    client_setup, monkeypatch, resource, operation
):
    """``get_throughput`` and ``replace_throughput`` on a database or container use
    the client default time limit (1 second here) when the call does not give one.
    Calling them does not change the client's default.
    """
    database = client_setup.client.get_database_client("sales")
    if resource == "container":
        if client_setup.asynchronous:
            from azure.cosmos.aio import _container as throughput_module
        else:
            from azure.cosmos import container as throughput_module
        helper_name = "_get_throughput" if operation == "get" else "_replace_container_throughput"
        resource_client = database.get_container_client("orders")
    else:
        if client_setup.asynchronous:
            from azure.cosmos.aio import _database as throughput_module
        else:
            from azure.cosmos import database as throughput_module
        helper_name = operation + "_database_throughput" + ("_async" if client_setup.asynchronous else "")
        resource_client = database
    mock_type = AsyncMock if client_setup.asynchronous else MagicMock
    fake_helper = mock_type(return_value="throughput")
    monkeypatch.setattr(throughput_module, helper_name, fake_helper)
    throughput_call = resource_client.get_throughput if operation == "get" else resource_client.replace_throughput
    assert _await_if_needed(throughput_call(*(() if operation == "get" else (400,)))) == "throughput"
    assert fake_helper.call_args.kwargs["kwargs"]["timeout"] == 1
    assert client_setup.client._adapter._client_config.operation_timeout_seconds == 1


def test_cancelled_async_call_raises_cancelled_error_not_time_out_rust(monkeypatch):
    """Cancelling an async call raises ``asyncio.CancelledError``, not a time-out
    error, and the request in progress is stopped.
    """
    async def run():
        client = AsyncCosmosClient("https://alpha-bank.documents.azure.com", "key", timeout=1, _backend="rust")
        request_started = asyncio.Event()
        request_stopped = asyncio.Event()

        async def slow_request(*args, **kwargs):
            request_started.set()
            try:
                await asyncio.Future()
            finally:
                request_stopped.set()

        monkeypatch.setattr(async_adapter_module, "_rust_module", SimpleNamespace(create_database_async=slow_request))
        monkeypatch.setattr(client._adapter, "_ensure_driver_handle", AsyncMock(return_value="fake-handle"))
        call_task = asyncio.create_task(client.create_database("sales"))
        try:
            await request_started.wait()
            call_task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await call_task
            assert request_stopped.is_set()
        finally:
            await client.close()

    asyncio.run(run())


def test_async_time_limit_runs_out_while_connecting_rust(monkeypatch):
    """If the time limit runs out while the async client is still connecting, the
    call raises ``CosmosClientTimeoutError``. The wait for the connect is stopped,
    and no request is sent.
    """
    async def run():
        client = AsyncCosmosClient("https://alpha-bank.documents.azure.com", "key", timeout=1, _backend="rust")
        connect_stopped = asyncio.Event()
        send_request = AsyncMock(return_value=_fake_reply())

        async def never_connects():
            try:
                await asyncio.Future()
            finally:
                connect_stopped.set()

        monkeypatch.setattr(async_adapter_module, "_rust_module", SimpleNamespace(create_database_async=send_request))
        monkeypatch.setattr(client._adapter, "_ensure_driver_handle", never_connects)
        try:
            with pytest.raises(CosmosClientTimeoutError):
                await asyncio.wait_for(client.create_database("sales"), timeout=3)
            assert connect_stopped.is_set()
            send_request.assert_not_called()
        finally:
            await client.close()

    asyncio.run(run())
