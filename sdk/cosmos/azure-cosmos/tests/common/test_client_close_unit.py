# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Offline checks of client cleanup dispatch, ordering, and error handling.

Connections, native release calls, and credential-release hooks are mocked.
Assertions cover which cleanup calls occur, how concurrent callers wait,
and which failures are logged or propagated. They do not establish that
real native resources or credential threads have finished shutting down.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import inspect
import logging
import threading
from unittest.mock import AsyncMock, MagicMock

import pytest

import azure.cosmos.aio._cosmos_client as async_cosmos_client_module
import azure.cosmos.cosmos_client as sync_cosmos_client_module
import azure.cosmos.aio._backend.binding as async_rust_module
from azure.cosmos._backend.constants import BACKEND_ENV_VAR, BACKEND_NAME_RUST
from azure.cosmos._backend.legacy import LEGACY_BACKEND
from azure.cosmos.aio._backend.legacy import ASYNC_LEGACY_BACKEND

SYNC_URL = "https://close-sync.documents.azure.com"
ASYNC_URL = "https://close-async.documents.azure.com"


def _make_sync_client(monkeypatch):
    """Build a sync Rust-backed client that touches no network.

    The client connection is replaced wholesale, so nothing here opens a socket.
    The Rust backend is real but stays handle-less: the binding handle is created
    lazily on first use, and these tests never issue an operation.
    """
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    monkeypatch.setattr(
        sync_cosmos_client_module, "CosmosClientConnection", MagicMock()
    )
    return sync_cosmos_client_module.CosmosClient(
        SYNC_URL, "key", _backend=BACKEND_NAME_RUST
    )


def _make_async_client(monkeypatch):
    """Build an async Rust-backed client that touches no network.

    Async entry and teardown await four connection calls between them, so those four
    attributes have to be awaitable; a plain ``MagicMock`` returns a value that
    ``await`` rejects. The rest of the connection stays a ``MagicMock``.
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
    return client


def _record_backend_closes(monkeypatch, client):
    """Record calls to the backend owned by this client."""
    calls = []
    monkeypatch.setattr(client._backend, "close", lambda: calls.append("close"))
    return calls


def _record_async_backend_closes(monkeypatch, client):
    """Async counterpart of :func:`_record_backend_closes`.

    The replacement is a coroutine function, so this also pins that async teardown
    awaits the result. An unawaited coroutine would never append to the list.
    """
    calls = []

    async def _close():
        calls.append("close")

    monkeypatch.setattr(client._backend, "close", _close)
    return calls


def test_sync_close_releases_the_rust_backend(monkeypatch):
    """``close()`` must reach the backend, not just the Python HTTP resources."""
    client = _make_sync_client(monkeypatch)
    calls = _record_backend_closes(monkeypatch, client)

    client.close()

    assert calls == ["close"]


def test_sync_context_manager_exit_releases_the_rust_backend(monkeypatch):
    """Context-manager exit invokes the backend-close recorder once."""
    client = _make_sync_client(monkeypatch)
    calls = _record_backend_closes(monkeypatch, client)

    with client:
        pass

    assert calls == ["close"]


def test_sync_close_is_safe_to_call_twice(monkeypatch):
    """Two public close calls invoke the replacement backend-close hook twice.

    The real backend's handle-release guard is not exercised by this recorder.
    """
    client = _make_sync_client(monkeypatch)
    calls = _record_backend_closes(monkeypatch, client)

    client.close()
    client.close()

    assert calls == ["close", "close"]


def test_sync_backend_close_failure_still_releases_the_routing_cache(monkeypatch):
    """A failing backend close still reaches the mocked routing-cache release.

    The assertion checks that release was called, not the cache's refcount.
    """
    client = _make_sync_client(monkeypatch)

    def _raise():
        raise RuntimeError("driver refused to close")

    monkeypatch.setattr(client._backend, "close", _raise)

    client.close()

    assert client.client_connection._routing_map_provider.release.called


def test_sync_transport_close_failure_still_releases_the_rust_backend(monkeypatch):
    """A failing pipeline must not cancel the driver release that follows it.

    Transport shutdown runs before the backend release, so without the ``finally``
    the Rust driver would leak precisely when teardown is already going wrong.
    """
    client = _make_sync_client(monkeypatch)
    calls = _record_backend_closes(monkeypatch, client)
    client.client_connection.pipeline_client.__exit__.side_effect = RuntimeError(
        "transport already gone"
    )

    with pytest.raises(RuntimeError):
        client.close()

    assert calls == ["close"]


@pytest.mark.asyncio
async def test_async_close_releases_the_rust_backend(monkeypatch):
    """Async ``close()`` must reach the backend owned by this client."""
    client = _make_async_client(monkeypatch)
    calls = _record_async_backend_closes(monkeypatch, client)

    await client.close()

    assert calls == ["close"]


@pytest.mark.asyncio
async def test_async_context_manager_exit_releases_the_rust_backend(monkeypatch):
    """Async context-manager exit awaits the backend-close recorder."""
    client = _make_async_client(monkeypatch)
    calls = _record_async_backend_closes(monkeypatch, client)

    async with client:
        pass

    assert calls == ["close"]


@pytest.mark.asyncio
async def test_async_close_awaits_a_coroutine_backend_close(monkeypatch):
    """The awaitable returned by the async backend must actually be awaited.

    Async backend close hands its blocking work to a thread and awaits it, so a
    teardown that called the coroutine function without awaiting would return before
    any of that work ran -- and would leak while looking successful. Raising inside
    the coroutine makes the difference observable: the error can only be swallowed by
    teardown if teardown awaited far enough to see it.
    """
    client = _make_async_client(monkeypatch)
    awaited = []

    async def _close():
        awaited.append("awaited")
        raise RuntimeError("driver refused to close")

    monkeypatch.setattr(client._backend, "close", _close)

    await client.close()

    assert awaited == ["awaited"]
    assert client.client_connection._routing_map_provider.release.called


@pytest.mark.asyncio
async def test_async_close_is_safe_to_call_twice(monkeypatch):
    """Closing an already-closed async client must not raise."""
    client = _make_async_client(monkeypatch)
    calls = _record_async_backend_closes(monkeypatch, client)

    await client.close()
    await client.close()

    assert calls == ["close", "close"]


def test_sync_close_uses_the_backend_owned_by_the_client(monkeypatch):
    """Closing finds the backend on the client itself, not through the legacy connection.

    The reference held by the legacy connection is removed first, and closing
    still releases the backend exactly once. The client is what the customer
    holds and what owns the backend, so that is where cleanup must look.

    Reaching through the legacy connection would work today and break the moment
    that object is simplified or replaced -- and it would break by silently
    skipping cleanup, leaving the driver running, rather than by raising.
    """
    client = _make_sync_client(monkeypatch)
    calls = _record_backend_closes(monkeypatch, client)
    del client.client_connection._backend

    assert client.close() is None

    assert calls == ["close"]


@pytest.mark.asyncio
async def test_async_close_uses_the_backend_owned_by_the_client(monkeypatch):
    """The async client also closes the backend it owns rather than one found through the
    legacy connection.

    Same reasoning as the sync case, checked separately because the two closing
    paths are written independently and only one of them would be fixed if the
    lookup were changed in one place.
    """
    client = _make_async_client(monkeypatch)
    calls = _record_async_backend_closes(monkeypatch, client)
    del client.client_connection._backend

    assert await client.close() is None

    assert calls == ["close"]


def _install_async_close_resources(monkeypatch, client):
    """Install a synthetic driver handle and mocked credential-release hook.

    No driver or credential thread is created. The returned mocks expose
    cleanup invocations for the following tests.
    """
    binding = MagicMock()
    monkeypatch.setattr(async_rust_module, "_rust_module", binding)
    credential = MagicMock(spec=["_close_cosmos_async_bridge"])
    client._backend._driver_handle = "close-test-driver"
    client._backend._token_credential = credential
    return binding, credential


@pytest.mark.parametrize("resources", ["driver-and-bridge", "bridge-only", "unused"])
def test_async_close_after_executor_shutdown_releases_resources(
    monkeypatch, caplog, resources
):
    """With no worker threads left to run cleanup on, the async client cleans up on its
    own thread instead of giving up.

    Releasing the driver blocks, so cleanup normally runs on a worker thread to
    avoid stalling the event loop. During program shutdown those workers are
    already gone -- which is exactly when clients get closed. Refusing to clean
    up there would strand the driver and its threads for the life of the
    process.

    Three combinations are covered: both resources held, only the credential
    bridge, and neither. Each is released once and only if it was actually held,
    closing twice is safe, and nothing new is started on the way out.

    Falling back to the calling thread is recorded in the log, since it means
    the loop was briefly blocked. When there was nothing to release, nothing is
    logged -- an ordinary close must not leave a message implying something
    unusual happened.
    """
    client = _make_async_client(monkeypatch)
    binding, credential = _install_async_close_resources(monkeypatch, client)
    if resources != "driver-and-bridge":
        client._backend._driver_handle = None
    if resources == "unused":
        client._backend._token_credential = None
    caplog.clear()

    async def run():
        await asyncio.get_running_loop().shutdown_default_executor()
        assert await client.close() is None
        assert await client.close() is None

    asyncio.run(run())

    assert binding.release_driver_handle.call_count == (
        resources == "driver-and-bridge"
    )
    assert credential._close_cosmos_async_bridge.call_count == (resources != "unused")
    binding.acquire_driver_handle.assert_not_called()
    assert client._backend._driver_handle is None
    assert client._backend._token_credential is None
    if resources == "unused":
        assert not caplog.records
    else:
        assert "cleaning up on the calling thread" in caplog.text


@pytest.mark.parametrize("cancel_first", [False, True])
def test_repeated_async_close_waits_for_original_cleanup(monkeypatch, cancel_first):
    """A second close waits for the cleanup already running instead of starting its own or
    returning early.

    Cleanup is held partway through and a second close is started. It does not
    finish while the first is still working, and when it does return the
    resources were released exactly once.

    Returning early would be the tempting shortcut and the wrong one: the caller
    would believe the client was closed and move on -- typically to exiting the
    program -- while the driver was still being torn down.

    The second run cancels the first caller before the second arrives. Cleanup
    was started by the client, not owned by whoever asked for it, so one
    caller's cancellation must not abandon it. Otherwise a timeout around close
    would leave the driver permanently half-released.
    """
    client = _make_async_client(monkeypatch)
    binding, credential = _install_async_close_resources(monkeypatch, client)
    allow_finish = threading.Event()
    finished = threading.Event()

    async def run():
        loop = asyncio.get_running_loop()
        started = asyncio.Event()

        def release(_handle):
            loop.call_soon_threadsafe(started.set)
            try:
                assert allow_finish.wait(5), "cleanup worker timed out"
            finally:
                finished.set()

        binding.release_driver_handle.side_effect = release
        first = asyncio.create_task(client.close())
        second = None
        try:
            await asyncio.wait_for(started.wait(), 2)
            if cancel_first:
                first.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await first
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
    binding.release_driver_handle.assert_called_once_with("close-test-driver")
    credential._close_cosmos_async_bridge.assert_called_once_with()


def test_async_backend_close_completion_is_shared_across_event_loops(monkeypatch):
    """Two closes from two different event loops still produce one cleanup, and the second
    waits for the first.

    Each thread runs its own loop, which is what happens when a client is shared
    across threads or closed from a shutdown handler that starts a fresh loop.

    The waiting cannot be built from anything tied to a single loop. Something
    that only works within one loop would let the second close sail past while
    the first was still releasing the driver, and would release it twice. The
    resources are confirmed released exactly once.
    """
    client = _make_async_client(monkeypatch)
    binding, credential = _install_async_close_resources(monkeypatch, client)
    started = threading.Event()
    allow_finish = threading.Event()
    finished = threading.Event()

    def release(_handle):
        started.set()
        try:
            assert allow_finish.wait(5), "cleanup worker timed out"
        finally:
            finished.set()

    binding.release_driver_handle.side_effect = release

    def close_on_new_loop():
        asyncio.run(client._backend.close())

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(close_on_new_loop)
        second = None
        try:
            assert started.wait(2), "cleanup did not start"
            second = executor.submit(close_on_new_loop)
            with pytest.raises(concurrent.futures.TimeoutError):
                second.result(timeout=0.05)
            assert not finished.is_set()
        finally:
            allow_finish.set()
            first.result(timeout=2)
            if second is not None:
                second.result(timeout=2)

    binding.release_driver_handle.assert_called_once_with("close-test-driver")
    credential._close_cosmos_async_bridge.assert_called_once_with()


def test_completed_async_close_does_not_schedule_more_work(monkeypatch):
    """A second close submits no executor work and repeats no native/bridge release."""
    client = _make_async_client(monkeypatch)
    binding, credential = _install_async_close_resources(monkeypatch, client)

    async def run():
        await client.close()
        submit = MagicMock(side_effect=AssertionError("already closed"))
        monkeypatch.setattr(asyncio.get_running_loop(), "run_in_executor", submit)
        await client.close()
        submit.assert_not_called()

    asyncio.run(run())
    binding.release_driver_handle.assert_called_once()
    credential._close_cosmos_async_bridge.assert_called_once()


@pytest.mark.asyncio
async def test_async_close_preserves_logged_native_and_bridge_errors(
    monkeypatch, caplog
):
    """When releasing resources fails, closing still succeeds and both failures are
    written to the log.

    Both cleanup steps are made to fail. Close returns normally, and each
    failure appears in the log with its own message.

    Raising instead would be worse than useless. Close is usually called while
    shutting down or unwinding from another error, so an exception there would
    replace the problem the customer is actually trying to diagnose with one
    they can do nothing about.

    Both steps run even though the first failed -- the second is not skipped --
    and both messages are kept rather than one replacing the other, so support
    can see everything that went wrong.
    """
    client = _make_async_client(monkeypatch)
    binding, credential = _install_async_close_resources(monkeypatch, client)
    binding.release_driver_handle.side_effect = RuntimeError("native cleanup failed")
    credential._close_cosmos_async_bridge.side_effect = RuntimeError(
        "bridge cleanup failed"
    )

    with caplog.at_level(logging.DEBUG):
        assert await client.close() is None

    assert "Failed releasing native resources" in caplog.text
    assert "native cleanup failed" not in caplog.text
    assert "bridge cleanup failed" in caplog.text
    binding.release_driver_handle.assert_called_once()
    credential._close_cosmos_async_bridge.assert_called_once()


@pytest.mark.asyncio
async def test_async_transport_error_still_reaches_caller_after_backend_cleanup(
    monkeypatch,
):
    """A failure closing the transport does reach the caller, and the backend is still
    released first.

    This is the deliberate counterpart to the test above. Failures releasing the
    SDK's own Rust resources are logged, because the caller cannot act on them.
    A transport failure is different: it is the same error the legacy client
    always raised, and customers have handling built around it, so it is passed
    through unchanged.

    Either way the backend is released exactly once. The error does not cut
    cleanup short.
    """
    client = _make_async_client(monkeypatch)
    calls = _record_async_backend_closes(monkeypatch, client)
    failure = RuntimeError("transport cleanup failed")
    client.client_connection.pipeline_client.__aexit__.side_effect = failure

    with pytest.raises(RuntimeError) as error:
        await client.close()

    assert error.value is failure
    assert calls == ["close"]


@pytest.mark.parametrize(
    "client_type, asynchronous",
    [
        (sync_cosmos_client_module.CosmosClient, False),
        (async_cosmos_client_module.CosmosClient, True),
    ],
)
def test_close_public_signature_is_unchanged(client_type, asynchronous):
    """Check close's parameter list, None return annotation, and coroutine status.

    This is introspection, not an assertion about a runtime return value.
    """
    assert list(inspect.signature(client_type.close).parameters) == ["self"]
    assert inspect.signature(client_type.close).return_annotation is None
    assert inspect.iscoroutinefunction(client_type.close) is asynchronous


def test_sync_close_preserves_stateless_legacy_backend(monkeypatch):
    """A client using the legacy backend can be closed repeatedly, and the transport is
    closed each time.

    The legacy backend holds nothing of its own, so there is no state to guard
    and every close passes straight through to the transport -- twice here, once
    per call.

    That differs from the Rust backend, where later closes do nothing. The
    difference is deliberate and is preserved rather than tidied away: this is
    what the legacy client has always done, and code that closes more than once
    depends on the transport being closed each time.
    """
    client = _make_sync_client(monkeypatch)
    client._backend.close()
    client._backend = LEGACY_BACKEND

    assert client.close() is None
    assert client.close() is None
    assert client.client_connection.pipeline_client.__exit__.call_count == 2


@pytest.mark.asyncio
async def test_async_close_preserves_stateless_legacy_backend(monkeypatch):
    """The async legacy backend behaves the same way: every close reaches the transport.

    Checked separately from the sync case because the two have separate closing
    paths, and the async one additionally has to await the transport each time.
    """
    client = _make_async_client(monkeypatch)
    await client._backend.close()
    client._backend = ASYNC_LEGACY_BACKEND

    assert await client.close() is None
    assert await client.close() is None
    assert client.client_connection.pipeline_client.__aexit__.await_count == 2


@pytest.mark.asyncio
async def test_async_cleanup_still_releases_driver_if_bridge_helper_raises(
    monkeypatch, caplog
):
    """If the helper that is supposed to swallow credential cleanup errors raises anyway,
    the driver is still released.

    That helper exists precisely so bridge failures cannot disturb anything
    else, so it raising is a bug in the safety net itself. Cleanup has to
    survive it regardless.

    The driver handle is the resource that matters most here -- it is held by
    the Rust side and nothing else will ever give it back. Close still succeeds,
    and the unexpected failure is logged so the broken helper can be found
    rather than passing unnoticed.
    """
    client = _make_async_client(monkeypatch)
    binding, _ = _install_async_close_resources(monkeypatch, client)
    monkeypatch.setattr(
        async_rust_module,
        "close_credential_bridge_quietly",
        MagicMock(side_effect=RuntimeError("unexpected bridge cleanup failure")),
    )

    assert await client.close() is None

    binding.release_driver_handle.assert_called_once_with("close-test-driver")
    assert "Failed closing async client backend" in caplog.text
    assert "unexpected bridge cleanup failure" in caplog.text


@pytest.mark.asyncio
async def test_closed_async_backend_does_not_schedule_initialization(monkeypatch):
    """A closed client refuses to start a driver rather than quietly building one.

    After closing, an operation is attempted and fails with a message saying the
    client is closed, without any work being handed to a worker thread.

    Building a driver here would undo the close: the program would be left
    holding Rust resources belonging to a client the customer already finished
    with, and nothing would ever release them. The refusal also names the real
    problem, which is use after close, rather than surfacing as a strange
    failure deeper down.
    """
    client = _make_async_client(monkeypatch)
    await client.close()
    submit = MagicMock(side_effect=AssertionError("closed client must not start work"))
    monkeypatch.setattr(asyncio.get_running_loop(), "run_in_executor", submit)

    with pytest.raises(RuntimeError, match="client is closed"):
        await client._backend._ensure_driver_handle()

    submit.assert_not_called()


@pytest.mark.asyncio
async def test_cleanup_runs_once_if_executor_queues_work_then_raises(monkeypatch):
    """A simulated submit failure after queuing does not cause duplicate cleanup.

    The fallback runs first; the saved job is then invoked manually. Both
    resource-release mocks must still have exactly one call. This matters
    because a duplicate native release could decrement another client's hold.
    """
    client = _make_async_client(monkeypatch)
    binding, credential = _install_async_close_resources(monkeypatch, client)
    queued = []

    def submit(_executor, work):
        queued.append(work)
        raise RuntimeError("could not start a worker after queuing")

    monkeypatch.setattr(asyncio.get_running_loop(), "run_in_executor", submit)
    await client.close()
    assert len(queued) == 1
    queued[0]()

    binding.release_driver_handle.assert_called_once_with("close-test-driver")
    credential._close_cosmos_async_bridge.assert_called_once_with()


@pytest.mark.asyncio
@pytest.mark.parametrize("cancelled", [False, True])
async def test_cleanup_survives_worker_failure_before_job_starts(
    monkeypatch, caplog, cancelled
):
    """If the worker never runs the cleanup, the client does it instead rather than
    waiting forever.

    Two ways of never running are covered: the worker fails to start, and the
    work is cancelled before it begins. In both, close finishes well within its
    time limit and the resources are released exactly once.

    Waiting on something that will never happen is the failure to avoid here.
    Close would simply hang, usually during shutdown, and the program would not
    exit -- a symptom with nothing in it to point at the client.

    The log records that background cleanup did not complete, so the cause is
    visible even though the customer sees an ordinary close.
    """
    client = _make_async_client(monkeypatch)
    binding, credential = _install_async_close_resources(monkeypatch, client)
    loop = asyncio.get_running_loop()
    work = loop.create_future()
    if cancelled:
        work.cancel()
    else:
        work.set_exception(RuntimeError("worker could not initialize"))
    monkeypatch.setattr(loop, "run_in_executor", MagicMock(return_value=work))

    assert await asyncio.wait_for(client.close(), 2) is None

    binding.release_driver_handle.assert_called_once_with("close-test-driver")
    credential._close_cosmos_async_bridge.assert_called_once_with()
    assert "Background client cleanup did not complete" in caplog.text


@pytest.mark.parametrize("transport_fails", [False, True])
def test_sync_context_manager_preserves_existing_error_precedence(
    monkeypatch, transport_fails
):
    """When leaving a block fails in more than one way, which error the caller sees is
    unchanged from the legacy client.

    Releasing the Rust backend fails in both runs and never wins. That is the
    new part of closing, and it must not displace an error the customer already
    knew how to handle.

    Of the other two, a transport failure replaces the application's own error,
    and with no transport failure the application's error comes through. The
    first is not obviously desirable -- the customer's error is the more useful
    one -- but it is what the legacy client has always done, and this pins it
    rather than quietly changing which exception escapes existing blocks.
    """
    client = _make_sync_client(monkeypatch)
    application_error = ValueError("application failed")
    transport_error = RuntimeError("transport cleanup failed")
    monkeypatch.setattr(
        client._backend,
        "close",
        MagicMock(side_effect=RuntimeError("backend cleanup failed")),
    )
    if transport_fails:
        client.client_connection.pipeline_client.__exit__.side_effect = transport_error
    expected = transport_error if transport_fails else application_error

    with pytest.raises(type(expected)) as error:
        with client:
            raise application_error

    assert error.value is expected


@pytest.mark.asyncio
@pytest.mark.parametrize("transport_fails", [False, True])
async def test_async_context_manager_preserves_existing_error_precedence(
    monkeypatch, transport_fails
):
    """The async block follows the same order of precedence as the sync one.

    Backend cleanup failures never surface, a transport failure replaces the
    application's error, and otherwise the application's error comes through.
    Checked separately because the async exit path is written on its own and
    could easily end up ordering these differently.
    """
    client = _make_async_client(monkeypatch)
    application_error = ValueError("application failed")
    transport_error = RuntimeError("transport cleanup failed")
    monkeypatch.setattr(
        client._backend,
        "close",
        AsyncMock(side_effect=RuntimeError("backend cleanup failed")),
    )
    if transport_fails:
        client.client_connection.pipeline_client.__aexit__.side_effect = transport_error
    expected = transport_error if transport_fails else application_error

    with pytest.raises(type(expected)) as error:
        async with client:
            raise application_error

    assert error.value is expected
