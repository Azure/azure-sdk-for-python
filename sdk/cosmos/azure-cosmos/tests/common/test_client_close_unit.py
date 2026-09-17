# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Offline tests for client-owned cleanup and the existing error policy.

The Python backend is real; legacy connections and native release calls are
replaced so no service request is made. Explicit close and context-manager exit
must reach that backend directly. Repeated async closes share the same cleanup,
and a cancelled wait or unavailable worker must not lose Rust resources.
Backend cleanup failures remain logged; Python transport failures still raise.
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
import azure.cosmos.aio._backend.rust as async_rust_module
from azure.cosmos._backend.constants import BACKEND_ENV_VAR, BACKEND_NAME_RUST
from azure.cosmos._backend.legacy import LEGACY_BACKEND
from azure.cosmos.aio._backend.legacy import ASYNC_LEGACY_BACKEND

SYNC_URL = "https://close-sync.documents.azure.com"
ASYNC_URL = "https://close-async.documents.azure.com"


def _make_sync_client(monkeypatch):
    """Build a sync rust-backed client that touches no network.

    The client connection is replaced wholesale, so nothing here opens a socket.
    The rust backend is real but stays handle-less: the binding handle is created
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
    """Build an async rust-backed client that touches no network.

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
    """Leaving a ``with`` block must release the driver the same way ``close()`` does.

    ``close()`` delegates to ``__exit__``, but customers reach teardown through both
    doors, so both are pinned rather than assuming the delegation stays.
    """
    client = _make_sync_client(monkeypatch)
    calls = _record_backend_closes(monkeypatch, client)

    with client:
        pass

    assert calls == ["close"]


def test_sync_close_is_safe_to_call_twice(monkeypatch):
    """Closing an already-closed client must not raise.

    ``close()`` is public and documented as safe to repeat, and a client used as a
    context manager after an explicit close reaches teardown twice on its own. The
    backend tolerates this by taking its handle under a lock, so only the first call
    reaches the binding.
    """
    client = _make_sync_client(monkeypatch)
    calls = _record_backend_closes(monkeypatch, client)

    client.close()
    client.close()

    assert calls == ["close", "close"]


def test_sync_backend_close_failure_still_releases_the_routing_cache(monkeypatch):
    """A backend that fails to close must not strand the shared cache refcount.

    The partition-key-range cache is shared process-wide and released by refcount, so
    a skipped release keeps it alive for the life of the process. Teardown therefore
    isolates each step; this proves the isolation is real and not incidental ordering.
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
    the rust driver would leak precisely when teardown is already going wrong.
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
    """Leaving an ``async with`` block must release the driver.

    Async teardown is the more common shape for this client, since the recommended
    usage in the samples is ``async with CosmosClient(...)``.
    """
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
    client = _make_sync_client(monkeypatch)
    calls = _record_backend_closes(monkeypatch, client)
    del client.client_connection._backend

    assert client.close() is None

    assert calls == ["close"]


@pytest.mark.asyncio
async def test_async_close_uses_the_backend_owned_by_the_client(monkeypatch):
    client = _make_async_client(monkeypatch)
    calls = _record_async_backend_closes(monkeypatch, client)
    del client.client_connection._backend

    assert await client.close() is None

    assert calls == ["close"]


def _install_async_close_resources(monkeypatch, client):
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
    client = _make_async_client(monkeypatch)
    binding, credential = _install_async_close_resources(monkeypatch, client)
    binding.release_driver_handle.side_effect = RuntimeError("native cleanup failed")
    credential._close_cosmos_async_bridge.side_effect = RuntimeError(
        "bridge cleanup failed"
    )

    with caplog.at_level(logging.DEBUG):
        assert await client.close() is None

    assert "native cleanup failed" in caplog.text
    assert "bridge cleanup failed" in caplog.text
    binding.release_driver_handle.assert_called_once()
    credential._close_cosmos_async_bridge.assert_called_once()


@pytest.mark.asyncio
async def test_async_transport_error_still_reaches_caller_after_backend_cleanup(
    monkeypatch,
):
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
    assert list(inspect.signature(client_type.close).parameters) == ["self"]
    assert inspect.signature(client_type.close).return_annotation is None
    assert inspect.iscoroutinefunction(client_type.close) is asynchronous


def test_sync_close_preserves_stateless_legacy_backend(monkeypatch):
    client = _make_sync_client(monkeypatch)
    client._backend.close()
    client._backend = LEGACY_BACKEND

    assert client.close() is None
    assert client.close() is None
    assert client.client_connection.pipeline_client.__exit__.call_count == 2


@pytest.mark.asyncio
async def test_async_close_preserves_stateless_legacy_backend(monkeypatch):
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
    client = _make_async_client(monkeypatch)
    await client.close()
    submit = MagicMock(side_effect=AssertionError("closed client must not start work"))
    monkeypatch.setattr(asyncio.get_running_loop(), "run_in_executor", submit)

    with pytest.raises(RuntimeError, match="client is closed"):
        await client._backend._ensure_driver_handle()

    submit.assert_not_called()


@pytest.mark.asyncio
async def test_cleanup_runs_once_if_executor_queues_work_then_raises(monkeypatch):
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
