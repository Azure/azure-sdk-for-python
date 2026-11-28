# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Tests for how a client releases its resources when it is closed, or when it
is discarded without being closed.

Terms used in this file:

- compiled module: ``azure.cosmos._rust``, the compiled part of the SDK that
  sends requests.
- adapter: the object the client uses to call the compiled module
  (BindingAdapter, or AsyncBindingAdapter for async clients).
- handle: the adapter's link to a connection in the compiled module. It is
  opened on the first request and released when the client closes. A request
  that already holds the handle can still finish after it is released.
- async credential: a credential whose ``get_token`` method is async, such as
  the credentials in ``azure.identity.aio``.
- token helper: when an async credential is used, the SDK wraps it in a token
  helper (AsyncTokenCredentialBridge) so the compiled module can get tokens.
  Close releases the token helper; the SDK never closes the customer's
  credential.
- cleanup without close: if a client is discarded without being closed, Python
  calls the adapter's ``__del__``, which releases what is left.

The compiled module and connections are replaced with fakes. The tests check
which release calls happen, in what order and how many times, and which errors
are logged or raised. They do not check that real network connections close.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import inspect
import logging
import subprocess
import sys
import textwrap
import threading
from contextlib import closing
from unittest.mock import AsyncMock, MagicMock

import pytest

from common.sdk_subprocess import sdk_python_command

import azure.cosmos.aio._cosmos_client as async_cosmos_client_module
import azure.cosmos.cosmos_client as sync_cosmos_client_module
import azure.cosmos.aio._backend.binding_adapter as async_adapter_module
import azure.cosmos._backend.binding_adapter as sync_adapter_module
from azure.cosmos._backend.constants import BACKEND_ENV_VAR, BACKEND_NAME_RUST

SYNC_URL = "https://close-sync.documents.azure.com"
ASYNC_URL = "https://close-async.documents.azure.com"


@pytest.mark.parametrize("async_mode", [False, True])
def test_adapter_rejects_compiled_module_without_handle_type_rust(monkeypatch, async_mode):
    """If the compiled module is too old to have the handle type
    (``_DriverHandle``), creating an adapter raises RuntimeError asking for a
    rebuild."""
    from azure.cosmos import _rust

    monkeypatch.delattr(_rust, "_DriverHandle")
    adapter_type = async_adapter_module.AsyncBindingAdapter if async_mode else sync_adapter_module.BindingAdapter
    with pytest.raises(RuntimeError, match="lacks owning driver handles"):
        adapter_type(SYNC_URL, master_key="key")


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize(
    "cause",
    [
        ModuleNotFoundError("No module named 'azure.cosmos._rust'"),
        ImportError("DLL load failed while importing _rust: The specified module could not be found."),
    ],
)
def test_adapter_reports_why_compiled_module_failed_to_load_rust(monkeypatch, async_mode, cause):
    """If the compiled module cannot be imported (it is missing, or a DLL fails to
    load), creating an adapter raises ImportError naming ``azure.cosmos._rust``,
    with the original error attached as the cause."""
    import importlib.abc
    import azure.cosmos

    class _FailingFinder(importlib.abc.MetaPathFinder):
        """Makes importing the compiled module fail with ``cause``."""

        def find_spec(self, name, path, target=None):
            if name == "azure.cosmos._rust":
                raise cause
            return None

    monkeypatch.delattr(azure.cosmos, "_rust", raising=False)
    monkeypatch.delitem(sys.modules, "azure.cosmos._rust", raising=False)
    monkeypatch.setattr(sys, "meta_path", [_FailingFinder(), *sys.meta_path])
    adapter_type = async_adapter_module.AsyncBindingAdapter if async_mode else sync_adapter_module.BindingAdapter
    with pytest.raises(ImportError) as caught:
        adapter_type(SYNC_URL, master_key="key")
    assert caught.value.name == "azure.cosmos._rust"
    assert caught.value.__cause__ is cause


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("recreate", [False, True])
@pytest.mark.parametrize("operation", ["execute", "metadata", "page"])
def test_request_in_progress_keeps_its_handle_when_client_closes_rust(monkeypatch, async_mode, recreate, operation):
    """A request that has already picked its handle keeps using that same handle,
    even if the client is closed before the request is sent.

    This is checked for a single request, a read of container details, and the
    first page of a list. Close releases the handle exactly once, and a new
    client then opens a new connection, not the released one. The compiled
    module is a fake that keeps a list of open connections.
    """
    from types import SimpleNamespace
    from azure.cosmos._backend.contracts import PreparedPageRequest, PreparedRequest
    from azure.cosmos._backend.partition_key_input import BindingPartitionKey

    # handle_picked is set when the request has picked its handle. resume lets
    # the paused request continue.
    handle_picked, resume = threading.Event(), threading.Event()
    # The fake compiled module's open connections. Opening reuses the one already
    # there; releasing the last handle to it removes it.
    open_connections = []
    # The handle each fake request call received.
    handles_used = []

    def acquire(*args, **kwargs):
        if not open_connections:
            open_connections.append(object())
        return SimpleNamespace(driver=open_connections[0], released=False)

    def release(handle):
        if not handle.released:
            handle.released = True
            if open_connections and open_connections[0] is handle.driver:
                open_connections.clear()

    def dispatch(handle, *args, **kwargs):
        handles_used.append(handle)
        if operation == "metadata":
            return "container-rid", ("/customerId",), "Hash", False
        return 200, 0, {}, b'{"Databases":[]}'

    fake_module = SimpleNamespace(
        acquire_driver_handle=acquire, release_driver_handle=MagicMock(side_effect=release)
    )
    for name in ("read_database", "get_container_metadata", "list_databases"):
        setattr(fake_module, name, dispatch)
        setattr(fake_module, name + "_async", AsyncMock(side_effect=dispatch))
    module = async_adapter_module if async_mode else sync_adapter_module
    adapter_type = module.AsyncBindingAdapter if async_mode else module.BindingAdapter
    monkeypatch.setattr(module, "_rust_module", fake_module)
    adapter = adapter_type(SYNC_URL, master_key="key")
    # The adapter's own method that returns the handle, opening it first if needed.
    real_ensure_handle = adapter._ensure_driver_handle
    # The handle the request picked, recorded just before it pauses.
    handles_picked = []

    def pause(handle):
        """Record the picked handle, then wait until the test lets the request continue."""
        handles_picked.append(handle)
        handle_picked.set()
        assert resume.wait(5), "close did not resume the pending operation"
        return handle

    # Replace the adapter's method so the request pauses right after picking its
    # handle. The test closes the client during this pause.
    if async_mode:
        async def paused_ensure():
            return await asyncio.to_thread(pause, await real_ensure_handle())
    else:
        def paused_ensure(**kwargs):
            return pause(real_ensure_handle(**kwargs))
    monkeypatch.setattr(adapter, "_ensure_driver_handle", paused_ensure)
    request = PreparedRequest(
        op="read_database", container_link="", body_bytes=b"",
        partition_key=BindingPartitionKey("cross_partition"), item_id="db",
    )

    def run_operation():
        if operation == "execute":
            result = adapter.execute(request)
        elif operation == "metadata":
            result = adapter.get_container_metadata("dbs/db/colls/c")
        else:
            pages = adapter.execute_pages(PreparedPageRequest(op="list_databases", container_link=""))
            if async_mode:
                async def read_page():
                    try:
                        return await anext(pages)
                    finally:
                        await pages.aclose()
                return asyncio.run(read_page())
            with closing(pages):
                return next(pages)
        return asyncio.run(result) if async_mode else result

    def close(client_adapter):
        result = client_adapter.close()
        if async_mode:
            asyncio.run(result)

    # A second client, created after close, to check that it opens a new connection.
    replacement = None
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        pending = executor.submit(run_operation)
        try:
            assert handle_picked.wait(5), "operation did not select its handle"
            close(adapter)
            assert adapter._driver_handle is None
            assert not open_connections
            if recreate:
                replacement = adapter_type(SYNC_URL, master_key="key")
                result = replacement._ensure_driver_handle()
                new_handle = asyncio.run(result) if async_mode else result
                assert new_handle.driver is not handles_picked[0].driver
            resume.set()
            pending.result(timeout=5)
            assert handles_used == handles_picked
            assert handles_used[0] is handles_picked[0]
            close(adapter)
            fake_module.release_driver_handle.assert_called_once_with(handles_picked[0])
        finally:
            resume.set()
            close(adapter)
            if replacement is not None:
                close(replacement)


@pytest.mark.parametrize("async_mode", [False, True])
def test_cleanup_without_close_releases_token_helper_on_background_thread_rust(async_mode, monkeypatch):
    """Cleanup without close releases the token helper on a background thread, so
    the calling thread is not blocked.

    No event loop is running. Running the cleanup again does not release it a
    second time.
    """
    from types import SimpleNamespace
    from azure.cosmos._backend import _binding_adapter_shared as shared

    # started: the release began. finish: lets the release end. finished: the release ended.
    started, finish, finished = threading.Event(), threading.Event(), threading.Event()
    # The thread ID of each token helper release.
    calls = []
    # Record each background thread the cleanup starts, so the test can wait for it.
    cleanup_threads = []

    def make_cleanup_thread(*, target, name, daemon):
        cleanup_thread = threading.Thread(target=target, name=name, daemon=daemon)
        cleanup_threads.append(cleanup_thread)
        return cleanup_thread

    def release_token_helper():
        calls.append(threading.get_ident())
        started.set()
        try:
            finish.wait(3)
        finally:
            finished.set()

    adapter_type = async_adapter_module.AsyncBindingAdapter if async_mode else sync_adapter_module.BindingAdapter
    adapter = adapter_type(
        SYNC_URL, token_credential=SimpleNamespace(_close_cosmos_async_bridge=release_token_helper)
    )
    monkeypatch.setattr(shared, "threading", SimpleNamespace(Thread=make_cleanup_thread))
    try:
        adapter.__del__()
        assert started.wait(2)
        assert not finished.is_set()
        adapter.__del__()
        assert calls == [calls[0]] and calls[0] != threading.get_ident()
    finally:
        finish.set()
        for cleanup_thread in cleanup_threads:
            cleanup_thread.join(timeout=2)
        assert all(not cleanup_thread.is_alive() for cleanup_thread in cleanup_threads), "cleanup thread did not finish"
    assert finished.is_set()


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("finalizing", [False, True])
def test_cleanup_without_close_falls_back_to_calling_thread_rust(
    async_mode, finalizing, monkeypatch, caplog,
):
    """If the background thread cannot start, cleanup releases the token helper
    and then the handle on the calling thread, once each, and logs a warning.

    While Python is shutting down, no thread is tried and nothing is logged.
    """
    from types import SimpleNamespace
    from azure.cosmos._backend import _binding_adapter_shared as shared

    # Each release, with the thread it ran on.
    calls = []
    credential = SimpleNamespace(
        _close_cosmos_async_bridge=MagicMock(
            side_effect=lambda: calls.append(("credential", threading.get_ident()))
        )
    )
    fake_module = SimpleNamespace(
        release_driver_handle=MagicMock(
            side_effect=lambda handle: calls.append((handle, threading.get_ident()))
        )
    )
    adapter_module = async_adapter_module if async_mode else sync_adapter_module
    adapter_type = adapter_module.AsyncBindingAdapter if async_mode else adapter_module.BindingAdapter
    monkeypatch.setattr(adapter_module, "_rust_module", fake_module)
    adapter = adapter_type(SYNC_URL, token_credential=credential)
    adapter._driver_handle = "handle-finalizer-fallback"

    # A background thread whose start() always fails.
    cleanup_thread = SimpleNamespace(start=MagicMock(side_effect=RuntimeError("cannot start thread")))
    thread_factory = MagicMock(return_value=cleanup_thread)
    monkeypatch.setattr(shared, "threading", SimpleNamespace(Thread=thread_factory))
    monkeypatch.setattr(sys, "is_finalizing", lambda: finalizing)
    # The thread that runs the cleanup; both releases must happen on it.
    finalizing_thread = threading.get_ident()

    with caplog.at_level(logging.WARNING, logger=shared.__name__):
        adapter.__del__()
        adapter.__del__()

    assert adapter._driver_handle is None
    assert adapter._token_credential is None
    assert calls == [
        ("credential", finalizing_thread),
        ("handle-finalizer-fallback", finalizing_thread),
    ]
    credential._close_cosmos_async_bridge.assert_called_once_with()
    fake_module.release_driver_handle.assert_called_once_with("handle-finalizer-fallback")
    if finalizing:
        thread_factory.assert_not_called()
        cleanup_thread.start.assert_not_called()
    else:
        thread_factory.assert_called_once()
        cleanup_thread.start.assert_called_once_with()
        assert thread_factory.call_args.kwargs["daemon"] is True
    assert [
        record.getMessage() for record in caplog.records
        if record.name == shared.__name__ and record.levelno == logging.WARNING
    ] == ([] if finalizing else ["Could not start finalizer worker; cleaning up on the finalizing thread"])


def test_cleanup_without_close_at_python_exit_has_no_warning_rust():
    """In a new Python process, an object still alive when Python exits is
    cleaned up during shutdown: the token helper is released, then the handle.

    No warning and no "Exception ignored" message is printed.
    """
    script = textwrap.dedent("""
        import os
        import sys
        from types import SimpleNamespace
        from azure.cosmos._backend._binding_adapter_shared import finalize_adapter_resources

        def release(handle, write=os.write, finalizing=sys.is_finalizing):
            write(1, f"released:{finalizing()}\\n".encode())

        def close_token_helper(write=os.write):
            write(1, b"token-helper\\n")

        class AbandonedResources:
            def __del__(
                self, finalize=finalize_adapter_resources, handle=object(),
                credential=SimpleNamespace(_close_cosmos_async_bridge=close_token_helper),
                fake_module=SimpleNamespace(release_driver_handle=release),
            ):
                finalize(credential, handle, fake_module)

        resources = AbandonedResources()
    """)
    result = subprocess.run(
        sdk_python_command(script), capture_output=True, text=True, timeout=15, check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == ["token-helper", "released:True"]
    assert "Could not start finalizer worker" not in result.stderr
    assert "Exception ignored" not in result.stderr


def test_cleanup_without_close_when_shutdown_starts_during_thread_start_rust(monkeypatch, caplog):
    """If Python starts shutting down while the background thread is starting,
    cleanup still releases the handle on the calling thread and logs nothing."""
    from types import SimpleNamespace
    from azure.cosmos._backend import _binding_adapter_shared as shared

    fake_module = SimpleNamespace(release_driver_handle=MagicMock())
    cleanup_thread = SimpleNamespace(start=MagicMock(side_effect=RuntimeError("cannot start thread")))
    monkeypatch.setattr(shared, "threading", SimpleNamespace(Thread=MagicMock(return_value=cleanup_thread)))
    # Python is not shutting down when the thread is started, but is by the time it fails.
    monkeypatch.setattr(sys, "is_finalizing", MagicMock(side_effect=[False, True]))
    with caplog.at_level(logging.WARNING, logger=shared.__name__):
        shared.finalize_adapter_resources(None, "handle", fake_module)
    cleanup_thread.start.assert_called_once_with()
    fake_module.release_driver_handle.assert_called_once_with("handle")
    assert not [record for record in caplog.records if record.name == shared.__name__]


def test_async_handle_opens_once_across_event_loops_rust(monkeypatch):
    """Eight requests on four event loops wait for the handle to open. It opens
    once and every request gets it.

    The adapter's record of the opening in progress (``_init_future``) is only
    read or changed while its lock is held. Close releases the handle once.
    """
    from types import SimpleNamespace

    class LockCheckingAdapter(async_adapter_module.AsyncBindingAdapter):
        """An adapter that fails the test if ``_init_future`` is used without holding the lock."""

        def __getattribute__(self, name):
            if name == "_init_future":
                assert object.__getattribute__(self, "_driver_handle_lock").locked()
            return super().__getattribute__(name)

        def __setattr__(self, name, value):
            if name == "_init_future":
                lock = self.__dict__.get("_driver_handle_lock")
                assert lock is None or lock.locked()
            super().__setattr__(name, value)

    # started: opening has begun. finish: lets opening complete.
    started, finish = threading.Event(), threading.Event()

    def acquire(*args):
        started.set()
        assert finish.wait(5)
        return "cross-loop-handle"

    fake_module = SimpleNamespace(acquire_driver_handle=MagicMock(side_effect=acquire),
                             release_driver_handle=MagicMock())
    monkeypatch.setattr(async_adapter_module, "_rust_module", fake_module)
    adapter = LockCheckingAdapter(ASYNC_URL, master_key="key")

    async def run():
        """Two requests on this event loop wait for the handle."""
        return await asyncio.gather(adapter._ensure_driver_handle(), adapter._ensure_driver_handle())

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(lambda: asyncio.run(run())) for _ in range(4)]
            try:
                assert started.wait(2)
            finally:
                finish.set()
            for future in futures:
                assert future.result(timeout=5) == ["cross-loop-handle", "cross-loop-handle"]
        fake_module.acquire_driver_handle.assert_called_once()
    finally:
        finish.set()
        asyncio.run(adapter.close())
    fake_module.release_driver_handle.assert_called_once_with("cross-loop-handle")


def test_cancelling_one_waiting_request_does_not_stop_handle_opening_rust(monkeypatch):
    """Two async requests wait for the handle to open. Cancelling one does not stop
    the opening: the other still gets the handle, and the handle opens only once.
    """
    from types import SimpleNamespace

    # started: opening has begun. finish: lets opening complete.
    started, finish = threading.Event(), threading.Event()

    def acquire(*args):
        started.set()
        assert finish.wait(5)
        return "shared-handle"

    fake_module = SimpleNamespace(acquire_driver_handle=MagicMock(side_effect=acquire),
                             release_driver_handle=MagicMock())
    monkeypatch.setattr(async_adapter_module, "_rust_module", fake_module)
    adapter = async_adapter_module.AsyncBindingAdapter(ASYNC_URL, master_key="key")

    async def run():
        first = asyncio.create_task(adapter._ensure_driver_handle())
        second = asyncio.create_task(adapter._ensure_driver_handle())
        try:
            assert await asyncio.to_thread(started.wait, 2)
            first.cancel()
            with pytest.raises(asyncio.CancelledError):
                await first
            assert not second.done()
            finish.set()
            assert await second == "shared-handle"
        finally:
            finish.set()
            await adapter.close()

    asyncio.run(run())
    fake_module.acquire_driver_handle.assert_called_once()


def _make_sync_client(monkeypatch):
    """Build a sync client that sends no requests.

    The client's internal connection object (``client_connection``) is a
    MagicMock, so no network connection is made. The adapter is real, but its
    handle is never opened, because no request is sent.
    """
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    monkeypatch.setattr(
        sync_cosmos_client_module, "CosmosClientConnection", MagicMock()
    )
    client = sync_cosmos_client_module.CosmosClient(
        SYNC_URL, "key", _backend=BACKEND_NAME_RUST
    )
    # Give the connection an HTTP pipeline, as if a request had already been sent,
    # so close has a pipeline to close.
    client.client_connection.pipeline_client = MagicMock()
    return client


def _make_async_client(monkeypatch):
    """Build an async client that sends no requests.

    The async client awaits several connection methods when it opens and closes,
    so those are replaced with AsyncMock, because a plain MagicMock cannot be
    awaited. The adapter's ``initialize`` is replaced too, so no handle is opened.
    """
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    monkeypatch.setattr(
        async_cosmos_client_module, "CosmosClientConnection", MagicMock()
    )
    client = async_cosmos_client_module.CosmosClient(
        ASYNC_URL, "key", _backend=BACKEND_NAME_RUST
    )
    connection = client.client_connection
    connection._setup = AsyncMock()
    connection._global_endpoint_manager.close = AsyncMock()
    connection.pipeline_client.__aenter__ = AsyncMock()
    connection.pipeline_client.__aexit__ = AsyncMock()
    connection._close_pipeline = connection.pipeline_client.__aexit__
    monkeypatch.setattr(client._adapter, "initialize", AsyncMock())
    return client


def _record_adapter_closes(monkeypatch, client):
    """Replace the adapter's close with one that records each call, and return the
    list of calls."""
    calls = []
    monkeypatch.setattr(client._adapter, "close", lambda: calls.append("close"))
    return calls


def _record_async_adapter_closes(monkeypatch, client):
    """The async version of ``_record_adapter_closes``.

    The replacement is async, so a call is recorded only if the client awaits it.
    """
    calls = []

    async def _close():
        calls.append("close")

    monkeypatch.setattr(client._adapter, "close", _close)
    return calls


def test_sync_close_closes_the_adapter_rust(monkeypatch):
    """``close()`` closes the adapter, not only the HTTP connection."""
    client = _make_sync_client(monkeypatch)
    calls = _record_adapter_closes(monkeypatch, client)

    client.close()

    assert calls == ["close"]


def test_sync_with_block_exit_closes_the_adapter_rust(monkeypatch):
    """Leaving a ``with client:`` block closes the adapter once."""
    client = _make_sync_client(monkeypatch)
    calls = _record_adapter_closes(monkeypatch, client)

    with client:
        pass

    assert calls == ["close"]


def test_sync_close_twice_does_not_raise_rust(monkeypatch):
    """Closing twice does not raise, closes the HTTP connection each time, and
    each close calls the adapter's close.

    The adapter itself makes the second call do nothing; that is tested
    separately.
    """
    client = _make_sync_client(monkeypatch)
    calls = _record_adapter_closes(monkeypatch, client)

    client.close()
    client.close()

    assert calls == ["close", "close"]
    assert client.client_connection.pipeline_client.__exit__.call_count == 2


def test_sync_adapter_close_error_still_releases_routing_cache_rust(monkeypatch):
    """The SDK keeps a cache of how each container's data is split into partitions
    (the routing cache). Clients for the same account share it, and each client
    gives up its share on close.

    If the adapter's close raises, close logs the error and still gives up the
    client's share.
    """
    client = _make_sync_client(monkeypatch)

    def _raise():
        raise RuntimeError("driver refused to close")

    monkeypatch.setattr(client._adapter, "close", _raise)

    client.close()

    assert client.client_connection._routing_map_provider.release.called


def test_sync_http_close_error_still_closes_the_adapter_rust(monkeypatch):
    """Close shuts down the HTTP connection first, then the adapter.

    If closing the HTTP connection raises, the adapter is still closed and the
    HTTP error reaches the caller.
    """
    client = _make_sync_client(monkeypatch)
    calls = _record_adapter_closes(monkeypatch, client)
    client.client_connection.pipeline_client.__exit__.side_effect = RuntimeError(
        "transport already gone"
    )

    with pytest.raises(RuntimeError):
        client.close()

    assert calls == ["close"]


@pytest.mark.asyncio
async def test_async_close_closes_the_adapter_rust(monkeypatch):
    """Async ``close()`` closes the adapter."""
    client = _make_async_client(monkeypatch)
    calls = _record_async_adapter_closes(monkeypatch, client)

    await client.close()

    assert calls == ["close"]


@pytest.mark.asyncio
async def test_async_with_block_exit_closes_the_adapter_rust(monkeypatch):
    """Leaving an ``async with client:`` block closes the adapter once."""
    client = _make_async_client(monkeypatch)
    calls = _record_async_adapter_closes(monkeypatch, client)

    async with client:
        pass

    assert calls == ["close"]


@pytest.mark.asyncio
async def test_async_close_awaits_the_adapter_close_rust(monkeypatch):
    """The client awaits the adapter's async close, instead of only calling it.

    The fake close records that it ran and then raises. The client logs the
    error and still releases its routing cache share.
    """
    client = _make_async_client(monkeypatch)
    awaited = []

    async def _close():
        awaited.append("awaited")
        raise RuntimeError("driver refused to close")

    monkeypatch.setattr(client._adapter, "close", _close)

    await client.close()

    assert awaited == ["awaited"]
    assert client.client_connection._routing_map_provider.release.called


@pytest.mark.asyncio
async def test_async_close_twice_does_not_raise_rust(monkeypatch):
    """Closing an async client twice does not raise, closes the HTTP connection
    each time, and each close calls the adapter's close."""
    client = _make_async_client(monkeypatch)
    calls = _record_async_adapter_closes(monkeypatch, client)

    await client.close()
    await client.close()

    assert calls == ["close", "close"]
    assert client.client_connection.pipeline_client.__aexit__.await_count == 2


def test_sync_close_uses_the_clients_own_adapter_rust(monkeypatch):
    """Close finds the adapter on the client itself, not through
    ``client_connection``.

    The test deletes ``client_connection``'s reference to the adapter
    (``_backend``), and close still closes the adapter once.
    """
    client = _make_sync_client(monkeypatch)
    calls = _record_adapter_closes(monkeypatch, client)
    del client.client_connection._backend

    assert client.close() is None

    assert calls == ["close"]


@pytest.mark.asyncio
async def test_async_close_uses_the_clients_own_adapter_rust(monkeypatch):
    """The async version of ``test_sync_close_uses_the_clients_own_adapter_rust``."""
    client = _make_async_client(monkeypatch)
    calls = _record_async_adapter_closes(monkeypatch, client)
    del client.client_connection._backend

    assert await client.close() is None

    assert calls == ["close"]


def _give_adapter_handle_and_token_helper(monkeypatch, client):
    """Give the async client's adapter a fake handle and a fake token helper, and
    replace the compiled module with a MagicMock.

    Return the fake module and the fake token helper, so a test can check their
    release calls.
    """
    fake_module = MagicMock()
    monkeypatch.setattr(async_adapter_module, "_rust_module", fake_module)
    token_helper = MagicMock(spec=["_close_cosmos_async_bridge"])
    client._adapter._driver_handle = "close-test-handle"
    client._adapter._token_credential = token_helper
    return fake_module, token_helper


@pytest.mark.parametrize("resources", ["handle-and-token-helper", "handle-only", "token-helper-only", "nothing"])
def test_async_close_after_thread_pool_shutdown_cleans_up_on_calling_thread_rust(
    monkeypatch, caplog, resources
):
    """Async close normally releases the token helper and the handle on the event
    loop's default pool of background threads (its thread pool). If the thread
    pool has been shut down, close does the release on the calling thread and
    logs a warning.

    This is checked with both, either one, or neither to release. Closing twice
    releases each one once and never opens a handle. If there is nothing to
    release, nothing is logged.
    """
    client = _make_async_client(monkeypatch)
    fake_module, token_helper = _give_adapter_handle_and_token_helper(monkeypatch, client)
    has_handle = resources in ("handle-and-token-helper", "handle-only")
    has_token_helper = resources in ("handle-and-token-helper", "token-helper-only")
    # The thread each release ran on.
    cleanup_threads = []
    fake_module.release_driver_handle.side_effect = lambda _handle: cleanup_threads.append(threading.get_ident())
    token_helper._close_cosmos_async_bridge.side_effect = lambda: cleanup_threads.append(threading.get_ident())
    if not has_handle:
        client._adapter._driver_handle = None
    if not has_token_helper:
        client._adapter._token_credential = None
    caplog.clear()

    async def run():
        event_loop_thread = threading.get_ident()
        await asyncio.get_running_loop().shutdown_default_executor()
        assert await client.close() is None
        assert await client.close() is None
        assert cleanup_threads == [event_loop_thread] * sum((has_handle, has_token_helper))

    asyncio.run(run())

    assert fake_module.release_driver_handle.call_count == has_handle
    assert token_helper._close_cosmos_async_bridge.call_count == has_token_helper
    fake_module.acquire_driver_handle.assert_not_called()
    assert client._adapter._driver_handle is None
    assert client._adapter._token_credential is None
    if resources == "nothing":
        assert not caplog.records
    else:
        assert "cleaning up on the calling thread" in caplog.text


@pytest.mark.parametrize("cancel_first", [False, True])
def test_second_async_close_waits_for_cleanup_in_progress_rust(monkeypatch, cancel_first):
    """A second close waits for the cleanup the first close started.

    The fake handle release is paused, and the second close must not finish
    until the release is let go. This is also checked when the first close is
    cancelled before the second starts. In both cases cleanup finishes, and
    each release happens once.
    """
    client = _make_async_client(monkeypatch)
    fake_module, token_helper = _give_adapter_handle_and_token_helper(monkeypatch, client)
    # allow_finish lets the paused release end. finished is set when it has ended.
    allow_finish = threading.Event()
    finished = threading.Event()

    async def run():
        loop = asyncio.get_running_loop()
        started = asyncio.Event()

        def release(_handle):
            loop.call_soon_threadsafe(started.set)
            try:
                assert allow_finish.wait(5), "background cleanup timed out"
            finally:
                finished.set()

        fake_module.release_driver_handle.side_effect = release
        first = asyncio.create_task(client.close())
        second = None
        try:
            await asyncio.wait_for(started.wait(), 2)
            if cancel_first:
                first.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await first
                client.client_connection._routing_map_provider.release.assert_called_once_with()
            second = asyncio.create_task(client.close())
            with pytest.raises(asyncio.TimeoutError):
                await asyncio.wait_for(asyncio.shield(second), 0.05)
            assert not finished.is_set()
        finally:
            allow_finish.set()
            await asyncio.wait_for(
                asyncio.gather(
                    *[task for task in (first, second) if task is not None],
                    return_exceptions=True,
                ),
                2,
            )
        assert finished.is_set()
        assert second is not None and second.result() is None

    asyncio.run(run())
    fake_module.release_driver_handle.assert_called_once_with("close-test-handle")
    token_helper._close_cosmos_async_bridge.assert_called_once_with()


@pytest.mark.parametrize("cancel_first", [False, True], ids=["waiting", "cancelled"])
def test_async_close_cleanup_error_reaches_every_caller_rust(monkeypatch, caplog, cancel_first):
    """If cleanup raises while a close call is waiting, the error is raised to that
    caller and to any later close call.

    If the first caller had cancelled its wait, a debug message is logged
    instead, without the error text. In both cases Python does not warn that an
    error was never retrieved.
    """
    client = _make_async_client(monkeypatch)
    fake_module, _ = _give_adapter_handle_and_token_helper(monkeypatch, client)
    adapter = client._adapter
    caplog.set_level(logging.DEBUG, logger=async_adapter_module.__name__)
    loop = asyncio.new_event_loop()
    allow_finish = threading.Event()
    cleanup_error = RuntimeError("injected late cleanup error")
    wrap_future = asyncio.wrap_future
    # Records whether close retrieved the error of its wait, so Python does not
    # warn that it was never retrieved.
    error_observers = []

    def observe_wrapping(future, *, loop=None):
        """Wrap the future as usual, and record calls to exception() on close's wait."""
        wrapped = wrap_future(future, loop=loop)
        if future is adapter._close_future:
            observer = MagicMock(wraps=wrapped.exception)
            monkeypatch.setattr(wrapped, "exception", observer)
            error_observers.append(observer)
        return wrapped

    monkeypatch.setattr(asyncio, "wrap_future", observe_wrapping)

    async def run():
        started = asyncio.Event()
        completed = asyncio.Event()

        def fail_cleanup(_credential):
            """Pause until the test lets cleanup continue, then raise."""
            loop.call_soon_threadsafe(started.set)
            assert allow_finish.wait(5), "background cleanup timed out"
            raise cleanup_error

        fake_token_helper_release = MagicMock(side_effect=fail_cleanup)
        monkeypatch.setattr(async_adapter_module, "close_credential_bridge_quietly", fake_token_helper_release)
        first = asyncio.create_task(adapter.close())
        try:
            await asyncio.wait_for(started.wait(), 2)
            adapter._close_future.add_done_callback(
                lambda _future: loop.call_soon_threadsafe(completed.set)
            )
            if cancel_first:
                first.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await first
                assert not adapter._close_future.cancelled()
                assert not adapter._close_future.done()

            allow_finish.set()
            await asyncio.wait_for(completed.wait(), 2)
            if not cancel_first:
                with pytest.raises(RuntimeError) as raised:
                    await first
                assert raised.value is cleanup_error

            with pytest.raises(RuntimeError) as raised:
                await adapter.close()
            assert raised.value is cleanup_error
            assert adapter._close_future.exception() is cleanup_error
            fake_token_helper_release.assert_called_once()
        finally:
            allow_finish.set()
            await asyncio.wait_for(asyncio.gather(first, return_exceptions=True), 2)

    try:
        loop.run_until_complete(asyncio.wait_for(run(), 10))
        loop.run_until_complete(loop.shutdown_default_executor())
        loop.run_until_complete(asyncio.sleep(0))
        assert len(error_observers) == 1
        error_observers[0].assert_called()
    finally:
        allow_finish.set()
        try:
            loop.run_until_complete(loop.shutdown_default_executor())
        finally:
            # Retrieve even on regression failure, so the test itself leaves no warning.
            for observer in error_observers:
                observer()
            loop.close()

    fake_module.release_driver_handle.assert_called_once_with("close-test-handle")
    message = "Async client cleanup failed after its close wait was cancelled"
    assert (message in caplog.text) == cancel_first
    assert str(cleanup_error) not in caplog.text


@pytest.mark.asyncio
@pytest.mark.parametrize("phase", ["account-refresh", "http", "adapter"])
@pytest.mark.parametrize("context_manager", [False, True])
async def test_cancelled_async_close_releases_only_its_routing_cache_share_rust(
    monkeypatch, phase, context_manager
):
    """Async close has four steps: stop the task that refreshes account details,
    close the HTTP connection, close the adapter, and give up the client's
    routing cache share.

    If one step is cancelled, the other steps still run, and the client gives up
    only its own share; another client for the same account keeps its share.
    Closing again does not give up the share a second time. This is checked for
    ``close()`` and for leaving an ``async with`` block.
    """
    from types import SimpleNamespace
    from azure.cosmos._routing.aio import routing_map_provider

    client = _make_async_client(monkeypatch)
    connection = SimpleNamespace(url_connection=ASYNC_URL)
    # Two routing cache shares for the same account: one for this client, one for
    # another client.
    this_clients_share = routing_map_provider.PartitionKeyRangeCache(connection)
    other_clients_share = routing_map_provider.PartitionKeyRangeCache(connection)
    client.client_connection._routing_map_provider = this_clients_share
    endpoint = this_clients_share._endpoint
    steps = {
        "account-refresh": client.client_connection._global_endpoint_manager.close,
        "http": client.client_connection.pipeline_client.__aexit__,
        "adapter": AsyncMock(),
    }
    monkeypatch.setattr(client._adapter, "close", steps["adapter"])
    steps[phase].side_effect = asyncio.CancelledError()
    try:
        assert routing_map_provider._shared_cache_refcounts[endpoint] == 2
        with pytest.raises(asyncio.CancelledError):
            if context_manager:
                async with client:
                    pass
            else:
                await client.close()

        assert this_clients_share._released
        assert not other_clients_share._released
        assert routing_map_provider._shared_cache_refcounts[endpoint] == 1
        for stage in steps.values():
            stage.assert_awaited_once()

        steps[phase].side_effect = None
        await client.close()
        assert routing_map_provider._shared_cache_refcounts[endpoint] == 1
        other_clients_share.release()
        assert endpoint not in routing_map_provider._shared_cache_refcounts
        assert endpoint not in routing_map_provider._shared_routing_map_cache
    finally:
        this_clients_share.release()
        other_clients_share.release()


def test_async_close_on_two_event_loops_shares_one_cleanup_rust(monkeypatch):
    """Two close calls on two event loops, each on its own thread, wait for the
    same cleanup.

    The fake handle release is paused. The test checks that both calls are
    waiting, and that the second has not finished. After the release is let go,
    both calls return, and each release happens once.
    """
    client = _make_async_client(monkeypatch)
    fake_module, token_helper = _give_adapter_handle_and_token_helper(monkeypatch, client)
    started = threading.Event()
    # allow_finish lets the paused release end. finished is set when it has ended.
    allow_finish = threading.Event()
    finished = threading.Event()
    # Set when a close call has started waiting for the cleanup.
    close_wait_started = threading.Event()
    wrap_future = asyncio.wrap_future

    def observe_wrapping(future, *, loop=None):
        wrapped = wrap_future(future, loop=loop)
        if future is client._adapter._close_future:
            # Signal on the next loop turn, after close has reached its wait.
            asyncio.get_running_loop().call_soon(close_wait_started.set)
        return wrapped

    monkeypatch.setattr(asyncio, "wrap_future", observe_wrapping)

    def release(_handle):
        started.set()
        try:
            assert allow_finish.wait(5), "background cleanup timed out"
        finally:
            finished.set()

    fake_module.release_driver_handle.side_effect = release

    def close_on_new_loop():
        asyncio.run(client._adapter.close())

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(close_on_new_loop)
        second = None
        try:
            assert started.wait(2), "cleanup did not start"
            assert close_wait_started.wait(2), "first caller did not reach the cleanup wait"
            close_wait_started.clear()
            second = executor.submit(close_on_new_loop)
            assert close_wait_started.wait(2), "second caller did not reach the cleanup wait"
            with pytest.raises(concurrent.futures.TimeoutError):
                second.result(timeout=0.05)
            assert not finished.is_set()
        finally:
            allow_finish.set()
            first.result(timeout=2)
            if second is not None:
                second.result(timeout=2)

    fake_module.release_driver_handle.assert_called_once_with("close-test-handle")
    token_helper._close_cosmos_async_bridge.assert_called_once_with()


def test_async_close_after_finished_close_does_nothing_rust(monkeypatch):
    """After a close has finished, a second close sends no work to the thread pool
    and releases nothing again."""
    client = _make_async_client(monkeypatch)
    fake_module, token_helper = _give_adapter_handle_and_token_helper(monkeypatch, client)

    async def run():
        await client.close()
        submit = MagicMock(side_effect=AssertionError("already closed"))
        monkeypatch.setattr(asyncio.get_running_loop(), "run_in_executor", submit)
        await client.close()
        submit.assert_not_called()

    asyncio.run(run())
    fake_module.release_driver_handle.assert_called_once()
    token_helper._close_cosmos_async_bridge.assert_called_once()


@pytest.mark.asyncio
async def test_async_close_logs_release_errors_without_raising_rust(
    monkeypatch, caplog
):
    """If releasing the handle or the token helper raises, close still calls each
    release once, logs both failures and returns None.

    The handle error's text is left out of the log, because it can contain the
    handle. The token helper error's text is logged.
    """
    client = _make_async_client(monkeypatch)
    fake_module, token_helper = _give_adapter_handle_and_token_helper(monkeypatch, client)
    fake_module.release_driver_handle.side_effect = RuntimeError("handle release failed")
    token_helper._close_cosmos_async_bridge.side_effect = RuntimeError(
        "token helper release failed"
    )

    with caplog.at_level(logging.DEBUG):
        assert await client.close() is None

    assert "Failed releasing the driver handle" in caplog.text
    assert "handle release failed" not in caplog.text
    assert "token helper release failed" in caplog.text
    fake_module.release_driver_handle.assert_called_once()
    token_helper._close_cosmos_async_bridge.assert_called_once()


@pytest.mark.asyncio
async def test_async_http_close_error_reaches_caller_after_adapter_close_rust(
    monkeypatch,
):
    """If closing the HTTP connection raises, close raises that same error to the
    caller. The adapter is still closed, once, before the error reaches the
    caller.

    This is different from the test above: errors releasing the handle or token
    helper are only logged, but an HTTP close error is raised.
    """
    client = _make_async_client(monkeypatch)
    adapter_closes = _record_async_adapter_closes(monkeypatch, client)
    http_close_error = RuntimeError("HTTP close failed")
    client.client_connection.pipeline_client.__aexit__.side_effect = http_close_error

    with pytest.raises(RuntimeError) as raised:
        await client.close()

    assert raised.value is http_close_error
    assert adapter_closes == ["close"]


@pytest.mark.parametrize(
    "client_type, asynchronous",
    [
        (sync_cosmos_client_module.CosmosClient, False),
        (async_cosmos_client_module.CosmosClient, True),
    ],
)
def test_close_signature_rust(client_type, asynchronous):
    """close takes no arguments other than self, is annotated to return None, and
    is a coroutine only on the async client.
    """
    assert list(inspect.signature(client_type.close).parameters) == ["self"]
    assert inspect.signature(client_type.close).return_annotation is None
    assert inspect.iscoroutinefunction(client_type.close) is asynchronous


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("option", ["timeout", "response_hook", "initial_headers"])
def test_close_rejects_request_options_before_cleanup_rust(monkeypatch, asynchronous, option):
    """close does not accept request options such as ``timeout``.

    Passing one raises TypeError before any cleanup starts: the adapter is not
    marked as closing, and the routing cache share is kept.
    """
    make_client = _make_async_client if asynchronous else _make_sync_client
    client = make_client(monkeypatch)
    try:
        with pytest.raises(TypeError, match=option):
            client.close(**{option: None})
        assert not client._adapter._closing
        client.client_connection._routing_map_provider.release.assert_not_called()
    finally:
        if asynchronous:
            asyncio.run(client.close())
        else:
            client.close()


@pytest.mark.asyncio
async def test_async_close_does_not_start_until_awaited_rust(monkeypatch):
    """Calling async ``close()`` without awaiting it does nothing yet.

    The adapter is not marked as closing, the account refresh task and HTTP
    connection stay open, and the routing cache share is kept. Awaiting it does
    the close.
    """
    client = _make_async_client(monkeypatch)
    close_call = client.close()
    try:
        assert not client._adapter._closing
        client.client_connection._global_endpoint_manager.close.assert_not_awaited()
        client.client_connection.pipeline_client.__aexit__.assert_not_awaited()
        client.client_connection._routing_map_provider.release.assert_not_called()
    finally:
        assert await close_call is None
    assert client._adapter._closing


@pytest.mark.parametrize("has_handle", [False, True], ids=["no-handle", "has-handle"])
@pytest.mark.parametrize("public_close", [False, True], ids=["adapter", "client"])
def test_sync_close_releases_handle_when_reading_credential_raises_rust(
    monkeypatch, caplog, has_handle, public_close
):
    """If looking up the release method on the stored credential raises, the handle
    is still released, and the error is not hidden.

    The adapter's close raises the error; the client's close logs it and returns
    None. In both cases the adapter is marked closed, holds no handle or
    credential, and a second close does nothing. This is checked with and
    without a handle.
    """
    client = _make_sync_client(monkeypatch)
    fake_module = MagicMock()
    monkeypatch.setattr(sync_adapter_module, "_rust_module", fake_module)
    lookup_error = RuntimeError("looking up release failed")

    class CredentialWithBrokenRelease:
        @property
        def _close_cosmos_async_bridge(self):
            raise lookup_error

    adapter = client._adapter
    adapter._token_credential = CredentialWithBrokenRelease()
    adapter._driver_handle = "close-test-handle" if has_handle else None
    close_method = client.close if public_close else adapter.close

    with caplog.at_level(logging.DEBUG):
        if public_close:
            assert close_method() is None
            assert "Failed closing client backend" in caplog.text
            assert str(lookup_error) in caplog.text
        else:
            with pytest.raises(RuntimeError) as raised:
                close_method()
            assert raised.value is lookup_error

    assert adapter._closing
    assert adapter._driver_handle is None
    assert adapter._token_credential is None
    assert close_method() is None
    if has_handle:
        fake_module.release_driver_handle.assert_called_once_with("close-test-handle")
    else:
        fake_module.release_driver_handle.assert_not_called()


@pytest.mark.asyncio
async def test_async_close_releases_handle_when_token_helper_release_raises_rust(
    monkeypatch, caplog
):
    """If releasing the token helper raises an unexpected error, the handle is
    still released. The client's close logs the error and returns None.
    """
    client = _make_async_client(monkeypatch)
    fake_module, _ = _give_adapter_handle_and_token_helper(monkeypatch, client)
    monkeypatch.setattr(
        async_adapter_module,
        "close_credential_bridge_quietly",
        MagicMock(side_effect=RuntimeError("unexpected token helper release failure")),
    )

    assert await client.close() is None

    fake_module.release_driver_handle.assert_called_once_with("close-test-handle")
    assert "Failed closing async client backend" in caplog.text
    assert "unexpected token helper release failure" in caplog.text


@pytest.mark.asyncio
async def test_closed_async_client_does_not_open_a_handle_rust(monkeypatch):
    """After close, asking the adapter for a handle raises an error saying the
    client is closed, and no work is sent to the thread pool.

    Opening a new handle here would leave resources open that nothing would
    release.
    """
    client = _make_async_client(monkeypatch)
    await client.close()
    # Fails the test if any work is sent to the thread pool.
    submit = MagicMock(side_effect=AssertionError("closed client must not start work"))
    monkeypatch.setattr(asyncio.get_running_loop(), "run_in_executor", submit)

    with pytest.raises(RuntimeError, match="client is closed"):
        await client._adapter._ensure_driver_handle()

    submit.assert_not_called()


@pytest.mark.asyncio
async def test_cleanup_runs_once_if_thread_pool_queues_work_then_raises_rust(monkeypatch):
    """Sending the cleanup to the thread pool can fail after the work was already
    queued. Close then cleans up on the calling thread.

    When the queued work runs later it does nothing, so each release happens
    once. Releasing the token helper twice could give up another client's share
    of it.
    """
    client = _make_async_client(monkeypatch)
    fake_module, token_helper = _give_adapter_handle_and_token_helper(monkeypatch, client)
    # The work that was queued before sending raised.
    queued_work = []

    def submit(_executor, work):
        queued_work.append(work)
        raise RuntimeError("could not start a background thread after queuing")

    monkeypatch.setattr(asyncio.get_running_loop(), "run_in_executor", submit)
    await client.close()
    assert len(queued_work) == 1
    queued_work[0]()

    fake_module.release_driver_handle.assert_called_once_with("close-test-handle")
    token_helper._close_cosmos_async_bridge.assert_called_once_with()


@pytest.mark.asyncio
async def test_close_waits_for_started_cleanup_if_sending_it_raises_rust(monkeypatch):
    """Sending the cleanup to the thread pool can raise after the cleanup has
    already started on a background thread. Close does not run the cleanup
    again; it waits for the started cleanup to finish.

    The handle release is paused, and the test checks that close has not
    returned before letting the release end. Each release happens once, and a
    later close does nothing.
    """
    client = _make_async_client(monkeypatch)
    fake_module, token_helper = _give_adapter_handle_and_token_helper(monkeypatch, client)
    loop = asyncio.get_running_loop()
    # release_started is set when the background release begins. allow_finish lets it end.
    release_started = threading.Event()
    allow_finish = threading.Event()
    # send_failed is set after sending the work to the thread pool has raised.
    send_failed = asyncio.Event()
    # background_result holds how the background cleanup ended.
    background_result = concurrent.futures.Future()
    background_threads = []

    def paused_release(_handle):
        release_started.set()
        assert allow_finish.wait(5), "background cleanup timed out"

    def submit(_executor, work):
        def run():
            try:
                work()
            except BaseException as error:
                background_result.set_exception(error)
            else:
                background_result.set_result(None)

        thread = threading.Thread(target=run)
        background_threads.append(thread)
        thread.start()
        assert release_started.wait(2), "background thread did not reach the handle release"
        # This runs once close has handled the send error and yielded to the event loop.
        loop.call_soon(send_failed.set)
        raise RuntimeError("sending failed after cleanup started")

    fake_module.release_driver_handle.side_effect = paused_release
    submit_mock = MagicMock(side_effect=submit)
    monkeypatch.setattr(loop, "run_in_executor", submit_mock)
    close_task = asyncio.create_task(client.close())
    try:
        await asyncio.wait_for(send_failed.wait(), 2)
        assert client._adapter._close_future.running()
        assert not background_result.done()
        assert not close_task.done(), "close returned before its background cleanup finished"
        fake_module.release_driver_handle.assert_called_once_with("close-test-handle")
        token_helper._close_cosmos_async_bridge.assert_called_once_with()
    finally:
        allow_finish.set()
        try:
            await asyncio.wait_for(close_task, 2)
        finally:
            for thread in background_threads:
                thread.join(timeout=2)
                assert not thread.is_alive(), "background cleanup did not finish"

    assert background_result.result(timeout=2) is None
    assert close_task.result() is None
    assert client._adapter._close_future.result(timeout=2) is None
    await client.close()
    submit_mock.assert_called_once()
    fake_module.release_driver_handle.assert_called_once_with("close-test-handle")
    token_helper._close_cosmos_async_bridge.assert_called_once_with()


@pytest.mark.asyncio
@pytest.mark.parametrize("cancelled", [False, True])
async def test_close_cleans_up_on_calling_thread_if_background_work_fails_rust(
    monkeypatch, caplog, cancelled
):
    """If the work sent to the thread pool fails or is cancelled before it runs,
    close does the cleanup on the calling thread (here, the event loop's
    thread).

    Close finishes, each release happens once on that thread, and a warning is
    logged.
    """
    client = _make_async_client(monkeypatch)
    fake_module, token_helper = _give_adapter_handle_and_token_helper(monkeypatch, client)
    event_loop_thread = threading.get_ident()
    # The thread each release ran on.
    cleanup_threads = []
    fake_module.release_driver_handle.side_effect = lambda _handle: cleanup_threads.append(threading.get_ident())
    token_helper._close_cosmos_async_bridge.side_effect = lambda: cleanup_threads.append(threading.get_ident())
    loop = asyncio.get_running_loop()
    failed_work = loop.create_future()
    if cancelled:
        failed_work.cancel()
    else:
        failed_work.set_exception(RuntimeError("background work could not start"))
    monkeypatch.setattr(loop, "run_in_executor", MagicMock(return_value=failed_work))

    assert await asyncio.wait_for(client.close(), 2) is None

    fake_module.release_driver_handle.assert_called_once_with("close-test-handle")
    token_helper._close_cosmos_async_bridge.assert_called_once_with()
    assert cleanup_threads == [event_loop_thread, event_loop_thread]
    assert "Background client cleanup did not complete" in caplog.text


@pytest.mark.parametrize("http_close_fails", [False, True])
def test_sync_with_block_error_precedence_rust(
    monkeypatch, http_close_fails
):
    """When leaving a ``with`` block fails in more than one way, this checks which
    error the caller sees.

    Closing the adapter fails in both runs, and that error is only logged. If
    closing the HTTP connection also fails, its error replaces the error raised
    inside the block. Otherwise the error raised inside the block reaches the
    caller.
    """
    client = _make_sync_client(monkeypatch)
    application_error = ValueError("application failed")
    http_close_error = RuntimeError("HTTP close failed")
    monkeypatch.setattr(
        client._adapter,
        "close",
        MagicMock(side_effect=RuntimeError("adapter close failed")),
    )
    if http_close_fails:
        client.client_connection.pipeline_client.__exit__.side_effect = http_close_error
    expected = http_close_error if http_close_fails else application_error

    with pytest.raises(type(expected)) as raised:
        with client:
            raise application_error

    assert raised.value is expected


@pytest.mark.asyncio
@pytest.mark.parametrize("http_close_fails", [False, True])
async def test_async_with_block_error_precedence_rust(
    monkeypatch, http_close_fails
):
    """The same check for an ``async with`` block."""
    client = _make_async_client(monkeypatch)
    application_error = ValueError("application failed")
    http_close_error = RuntimeError("HTTP close failed")
    monkeypatch.setattr(
        client._adapter,
        "close",
        AsyncMock(side_effect=RuntimeError("adapter close failed")),
    )
    if http_close_fails:
        client.client_connection.pipeline_client.__aexit__.side_effect = http_close_error
    expected = http_close_error if http_close_fails else application_error

    with pytest.raises(type(expected)) as raised:
        async with client:
            raise application_error

    assert raised.value is expected
