# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Bound synchronous waits without abandoning ownership of driver acquisition.

Native acquisition and dispatch are simulated. Public calls and real Python
threads establish waiter timing and ownership, not live driver cancellation.
"""

import contextvars
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from azure.cosmos import CosmosClient
from azure.cosmos._backend import binding_adapter
from azure.cosmos._backend.contracts import PreparedPageRequest, PreparedRequest
from azure.cosmos._backend.partition_key_input import BindingPartitionKey
from azure.cosmos.exceptions import CosmosClientTimeoutError


@pytest.fixture
def cold_client(monkeypatch):
    client = CosmosClient("https://alpha-bank.documents.azure.com", "key", timeout=1, _backend="rust")
    entered, finish = threading.Event(), threading.Event()
    handle = object()

    def acquire(*_args, **_kwargs):
        entered.set()
        assert finish.wait(5), "test did not release acquisition"
        return handle

    native = SimpleNamespace(
        acquire_driver_handle=MagicMock(side_effect=acquire),
        release_driver_handle=MagicMock(),
    )
    monkeypatch.setattr(binding_adapter, "_rust_module", native)
    yield SimpleNamespace(client=client, entered=entered, finish=finish, handle=handle, native=native)
    finish.set()
    pending = getattr(client._adapter, "_init_future", None)
    if pending is not None:
        pending.exception(timeout=5)
    client.close()


@pytest.mark.parametrize(
    "operation", ["create_item", "read_item", "upsert_item", "replace_item", "patch_item", "delete_item"]
)
@pytest.mark.parametrize("client_default", [False, True], ids=["per-call", "client-default"])
def test_sync_cold_item_timeout_returns_before_acquisition_finishes_rust(cold_client, operation, client_default):
    case = cold_client
    dispatch = MagicMock()
    setattr(case.native, operation, dispatch)
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

    with ThreadPoolExecutor(max_workers=1) as pool:
        pending = pool.submit(getattr(container, operation), *arguments[operation], **options)
        try:
            assert case.entered.wait(2)
            with pytest.raises(CosmosClientTimeoutError):
                pending.result(timeout=2)
            assert not case.finish.is_set()
            dispatch.assert_not_called()
        finally:
            case.finish.set()
    assert case.client._adapter._ensure_driver_handle() is case.handle
    case.native.acquire_driver_handle.assert_called_once()


@pytest.mark.parametrize(
    "path,expired",
    [(path, expired) for path in ("execute", "metadata", "page") for expired in (False, True)] + [("ranges", False)],
)
def test_sync_auxiliary_paths_bound_acquisition_rust(cold_client, path, expired):
    case = cold_client
    adapter = case.client._adapter
    dispatch = MagicMock()
    deadline = time.monotonic() + (-1 if expired else 0.1)
    if path == "metadata":
        case.native.get_container_metadata = dispatch
        call = lambda: adapter.get_container_metadata("dbs/sales/colls/orders", deadline=deadline)
    elif path == "page":
        case.native.list_databases = dispatch
        call = lambda: next(
            adapter.execute_pages(PreparedPageRequest(op="list_databases", container_link=""), deadline=deadline)
        )
    elif path == "ranges":
        case.native.read_feed_ranges = dispatch
        container = case.client.get_database_client("sales").get_container_client("orders")
        call = lambda: list(container.read_feed_ranges())
    else:
        case.native.read_database = dispatch
        prepared = PreparedRequest(
            op="read_database",
            container_link="",
            body_bytes=b"",
            partition_key=BindingPartitionKey("cross_partition"),
            item_id="sales",
        )
        call = lambda: adapter.execute(prepared, deadline=deadline)
    with ThreadPoolExecutor(max_workers=1) as pool:
        pending = pool.submit(call)
        try:
            with pytest.raises(CosmosClientTimeoutError):
                pending.result(timeout=2)
            assert not case.finish.is_set()
            dispatch.assert_not_called()
            if expired:
                case.native.acquire_driver_handle.assert_not_called()
            else:
                assert case.entered.is_set()
        finally:
            case.finish.set()


def test_sync_waiters_share_acquisition_but_not_deadlines_rust(cold_client):
    case = cold_client
    ensure = case.client._adapter._ensure_driver_handle
    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(ensure, deadline=time.monotonic() + 0.1)
        try:
            assert case.entered.wait(2)
            survivor = pool.submit(ensure, deadline=time.monotonic() + 3)
            with pytest.raises(CosmosClientTimeoutError):
                first.result(timeout=2)
            assert not survivor.done()
            case.native.acquire_driver_handle.assert_called_once()
            case.finish.set()
            assert survivor.result(timeout=2) is case.handle
        finally:
            case.finish.set()
    assert ensure() is case.handle


def test_sync_completed_acquisition_leaves_only_remaining_time_for_dispatch_rust(cold_client):
    case = cold_client

    def acquire(*_args, **_kwargs):
        time.sleep(0.05)
        return case.handle

    case.native.acquire_driver_handle.side_effect = acquire
    case.native.create_database = MagicMock(return_value=(201, 0, {}, b'{"id":"sales"}', None))
    assert case.client.create_database("sales").id == "sales"
    assert 0 < case.native.create_database.call_args.kwargs["timeout_seconds"] <= 0.95
    case.native.acquire_driver_handle.assert_called_once()


def test_sync_close_releases_late_acquisition_without_waiting_rust(cold_client):
    case = cold_client
    adapter = case.client._adapter
    with pytest.raises(CosmosClientTimeoutError):
        adapter._ensure_driver_handle(deadline=time.monotonic() + 0.1)
    pending = adapter._init_future
    with ThreadPoolExecutor(max_workers=1) as pool:
        try:
            pool.submit(case.client.close).result(timeout=1)
            assert not case.finish.is_set()
            assert adapter._driver_handle is None
            case.native.release_driver_handle.assert_not_called()
        finally:
            case.finish.set()
    with pytest.raises(RuntimeError, match="closed during initialization"):
        pending.result(timeout=2)
    case.native.release_driver_handle.assert_called_once_with(case.handle)
    with pytest.raises(RuntimeError, match="closed"):
        adapter._ensure_driver_handle()
    case.client.close()
    case.native.release_driver_handle.assert_called_once_with(case.handle)


@pytest.mark.parametrize("error", [RuntimeError("acquisition failed"), TimeoutError("credential timeout")])
def test_sync_acquisition_preserves_original_failure_and_allows_retry_rust(cold_client, error):
    case = cold_client
    case.native.acquire_driver_handle.side_effect = [error, case.handle]
    ensure = case.client._adapter._ensure_driver_handle
    with pytest.raises(type(error)) as caught:
        ensure(deadline=time.monotonic() + 1)
    assert caught.value is error
    assert ensure(deadline=time.monotonic() + 1) is case.handle
    assert case.native.acquire_driver_handle.call_count == 2


def test_sync_acquisition_worker_preserves_context_rust(cold_client):
    marker = contextvars.ContextVar("acquisition-test")
    marker.set("customer-call")
    caller = threading.get_ident()
    observed = []

    def acquire(*_args, **_kwargs):
        observed.append((marker.get(), threading.get_ident()))
        return cold_client.handle

    cold_client.native.acquire_driver_handle.side_effect = acquire
    assert cold_client.client._adapter._ensure_driver_handle() is cold_client.handle
    assert observed[0][0] == "customer-call"
    assert observed[0][1] != caller


def test_sync_close_preserves_inputs_of_pending_acquisition_rust(cold_client, monkeypatch):
    case = cold_client
    adapter = case.client._adapter
    credential = SimpleNamespace(get_token=MagicMock())
    runtime = SimpleNamespace(_handle=object())
    adapter._master_key = None
    adapter._token_credential = credential
    adapter._runtime = runtime
    initialize = adapter._initialize_driver

    def delayed_initialize(binding, selected_runtime, **kwargs):
        case.entered.set()
        assert case.finish.wait(5)
        return initialize(binding, selected_runtime, **kwargs)

    monkeypatch.setattr(adapter, "_initialize_driver", delayed_initialize)
    try:
        with pytest.raises(CosmosClientTimeoutError):
            adapter._ensure_driver_handle(deadline=time.monotonic() + 0.1)
        pending = adapter._init_future
        assert case.entered.is_set()
        case.client.close()
        assert adapter._runtime is None
        assert adapter._token_credential is None
    finally:
        case.finish.set()
    with pytest.raises(RuntimeError, match="closed during initialization"):
        pending.result(timeout=2)
    assert case.native.acquire_driver_handle.call_args.args[3] is credential
    assert case.native.acquire_driver_handle.call_args.kwargs["runtime"] is runtime._handle
    case.native.release_driver_handle.assert_called_once_with(case.handle)
    credential.get_token.assert_not_called()


def test_sync_late_acquisition_failure_allows_retry_rust(cold_client, caplog):
    case = cold_client
    error = RuntimeError("private acquisition details")

    def fail(*_args, **_kwargs):
        case.entered.set()
        assert case.finish.wait(5)
        raise error

    case.native.acquire_driver_handle.side_effect = fail
    with caplog.at_level("DEBUG", logger=binding_adapter.__name__):
        try:
            with pytest.raises(CosmosClientTimeoutError):
                case.client._adapter._ensure_driver_handle(deadline=time.monotonic() + 0.1)
            pending = case.client._adapter._init_future
        finally:
            case.finish.set()
        assert pending.exception(timeout=2) is error
    assert "private acquisition details" not in caplog.text
    case.native.acquire_driver_handle.side_effect = None
    case.native.acquire_driver_handle.return_value = case.handle
    assert case.client._adapter._ensure_driver_handle() is case.handle
    assert case.native.acquire_driver_handle.call_count == 2


def test_sync_acquisition_worker_start_failure_is_not_cached_rust(cold_client, monkeypatch):
    original = binding_adapter.threading
    error = RuntimeError("cannot start worker")
    thread = SimpleNamespace(start=MagicMock(side_effect=error))
    monkeypatch.setattr(binding_adapter, "threading", SimpleNamespace(Thread=MagicMock(return_value=thread)))
    with pytest.raises(RuntimeError) as caught:
        cold_client.client._adapter._ensure_driver_handle()
    assert caught.value is error
    cold_client.native.acquire_driver_handle.assert_not_called()
    monkeypatch.setattr(binding_adapter, "threading", original)
    cold_client.finish.set()
    assert cold_client.client._adapter._ensure_driver_handle() is cold_client.handle
