# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Tests for client teardown reaching the rust driver (no network).

Closing a client has to release three separate things: the pipeline transport,
this client's reference to the shared rust driver, and the process-global
partition-key-range cache refcount. Only the first is core-python's own; the
other two were added for the rust backend and neither raises anything a caller
would notice if it silently stopped happening.

That silence is the reason these tests exist. ``__exit__`` finds the backend by
looking up an attribute name on the client connection::

    backend = getattr(self.client_connection, "_backend", None)

and then runs the close inside ``except Exception: pass``. So if the constructor
ever stops publishing the backend under the name teardown looks for, the lookup
returns ``None``, the ``if callable(...)`` guard is simply false, and teardown
completes reporting success while the rust driver's connection pool is never
released. Nothing throws, no existing test notices, and the leak only shows up
as a process that holds connections open until it exits.

The tests below pin the three properties that make teardown trustworthy:

1. Closing a client actually reaches the backend, through the same attribute
   lookup the real teardown path uses.
2. Closing twice is safe, because ``close()`` is public API and context-manager
   exit can follow an explicit close.
3. One failing step cannot cancel the others. A backend that raises must still
   leave the refcount released, and a failing transport must still release the
   backend -- otherwise a single bad teardown leaks everything after it.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

import azure.cosmos.aio._cosmos_client as async_cosmos_client_module
import azure.cosmos.cosmos_client as sync_cosmos_client_module
from azure.cosmos._backend.constants import BACKEND_ENV_VAR, BACKEND_NAME_RUST

SYNC_URL = "https://close-sync.documents.azure.com"
ASYNC_URL = "https://close-async.documents.azure.com"


def _make_sync_client(monkeypatch):
    """Build a sync rust-backed client that touches no network.

    The client connection is replaced wholesale, so nothing here opens a socket.
    The rust backend is real but stays handle-less: the binding handle is created
    lazily on first use, and these tests never issue an operation.

    Assigning to a ``MagicMock`` attribute keeps the assigned value, so whatever
    name the constructor publishes the backend under is the name teardown reads
    back -- which is exactly the wiring under test.
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
    """Replace the backend's close with a counter and return the recorded calls.

    Patching the real backend instance rather than substituting a stand-in object is
    deliberate: the recorded call only happens if teardown finds this exact backend
    through the client connection, so an empty list means the lookup broke.
    """
    calls = []
    monkeypatch.setattr(client._backend, "close", lambda: calls.append("close"))
    return calls


def _record_async_backend_closes(monkeypatch, client):
    """Async counterpart of :func:`_record_backend_closes`.

    The replacement is a coroutine function, so this also pins that async teardown
    awaits the result instead of dropping the returned coroutine on the floor. A
    dropped coroutine would still append to the list, so the await itself is
    asserted separately by the test that makes close raise.
    """
    calls = []

    async def _close():
        calls.append("close")

    monkeypatch.setattr(client._backend, "close", _close)
    return calls


def test_sync_close_releases_the_rust_backend(monkeypatch):
    """``close()`` must reach the backend, not just the pipeline.

    This is the leak-detector. The backend is found by name on the client
    connection, so the call only lands if the constructor published it under the
    name teardown reads.
    """
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
    """Async ``close()`` must reach the backend through the same lookup.

    The async client owns the same shared rust driver, so a missed release leaks the
    identical connection pool.
    """
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
