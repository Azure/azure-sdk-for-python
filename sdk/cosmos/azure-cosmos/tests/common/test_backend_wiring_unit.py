# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Tests for choosing and wiring the backend (no network).

Each test uses plain Python objects and runs in about a second. They cover
three things:

1. Import guard: the compiled Rust module and the backend classes may only
   be imported by a short, named list of files. One test scans every source
   file and fails if anything else imports them.
2. Choosing a backend: the factory picks the backend from the constructor
   argument, then an environment variable, then a default. An unknown value
   fails right away at construction.
3. Routing: a container call goes to the Rust backend when one is set, and
   to the existing client otherwise.
"""
from __future__ import annotations

import asyncio
import concurrent.futures
import logging
import re
import threading
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.cosmos._backend.base import BackendResponse, PreparedClientConfig, PreparedRequest
from azure.cosmos._backend.base import raise_account_read_unsupported
from azure.cosmos._backend import _driver_registry
from azure.cosmos._backend._driver_registry import (
    StrictEngineIsolationError,
    ProxyPolicyConflictError,
    _reset_for_tests as _reset_driver_registry,
    make_credential_key,
    register_client_config,
    register_proxy_policy,
    release_client_config,
)
from azure.cosmos._backend.constants import (
    BACKEND_ENV_VAR,
    BACKEND_NAME_CORE_PYTHON,
    BACKEND_NAME_RUST,
    RUST_STRICT_ISOLATION_ENV_VAR,
)
from azure.cosmos._backend.factory import (
    _resolve_credential,
    build_client_config,
    make_backend,
    reject_unsupported_transport_settings,
    resolve_backend_name,
    resolve_strict_isolation,
)
from azure.cosmos._backend._async_credential_bridge import (
    AsyncCredentialBridgeReentrantError,
    AsyncTokenCredentialBridge,
)
from azure.cosmos._backend.rust import RustBackend
from azure.cosmos._helpers._item_dispatch import pick_backend
from azure.cosmos._helpers.item_helper import ItemHelper
from azure.cosmos.aio._backend.factory import make_async_backend
from azure.cosmos.aio._backend.rust import AsyncRustBackend
from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy
from azure.cosmos.container import ContainerProxy


@pytest.fixture(autouse=True)
def _isolate_driver_registry():
    """Reset the shared driver registry before and after each test so one test's
    clients can't make another test warn (or not warn) unexpectedly. The registry
    lives for the whole process, and these tests use unique endpoints, so a client
    finalized late only affects its own endpoint."""
    _reset_driver_registry()
    yield
    _reset_driver_registry()


# ---------------------------------------------------------------------------
# Import guard
# ---------------------------------------------------------------------------

# This file lives at tests/common/, so go up two folders to the repo root and
# then into azure/cosmos/.
_PKG_ROOT = Path(__file__).resolve().parents[2] / "azure" / "cosmos"

# Each name may only be imported by the files listed here. Anything else fails.
_ALLOWED = {
    # The compiled Rust module may only be imported by the two backend files.
    "_rust": {
        Path("_backend") / "rust.py",
        Path("aio") / "_backend" / "rust.py",
    },
    # The Rust backend class may only be imported by the factory that builds
    # it and the client that holds it.
    "RustBackend": {
        Path("_backend") / "factory.py",
        Path("cosmos_client.py"),
    },
    "AsyncRustBackend": {
        Path("aio") / "_backend" / "factory.py",
        Path("aio") / "_cosmos_client.py",
    },
}

# Matches both ``import X`` and ``from X import Y`` lines.
_IMPORT_RE = re.compile(
    r"^\s*(?:from\s+\S+\s+import\s+|import\s+).*",
    re.MULTILINE,
)


def _iter_py_files():
    for path in _PKG_ROOT.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        yield path


# Read each source file once and keep its import lines, so the test below can
# scan that list instead of re-reading every file for each guarded name.
def _collect_import_lines():
    cached = []
    for py in _iter_py_files():
        rel = py.relative_to(_PKG_ROOT)
        text = py.read_text(encoding="utf-8", errors="ignore")
        import_lines = _IMPORT_RE.findall(text)
        if import_lines:
            cached.append((rel, import_lines))
    return cached


_IMPORT_LINE_CACHE = _collect_import_lines()


@pytest.mark.parametrize("guarded_name,allowed_files", list(_ALLOWED.items()))
def test_import_guard(guarded_name, allowed_files):
    """Only the listed files may import the guarded name."""
    offenders = []
    name_re = re.compile(r"\b" + re.escape(guarded_name) + r"\b")
    for rel, import_lines in _IMPORT_LINE_CACHE:
        if rel in allowed_files:
            continue
        for line in import_lines:
            if name_re.search(line):
                offenders.append("{}: {}".format(rel, line.strip()))
    assert not offenders, (
        "{} is imported outside its allow-list:\n  ".format(guarded_name)
        + "\n  ".join(offenders)
    )


# ---------------------------------------------------------------------------
# Choosing a backend, and how bad input is rejected
# ---------------------------------------------------------------------------
#
# The factory picks the backend in this order: the constructor argument, then
# the COSMOS_BACKEND environment variable, then the default. The value must be
# "core-python" or "rust"; anything else fails at construction so a typo does
# not quietly fall back to the default.

def test_factory_default_returns_none(monkeypatch):
    """With nothing set, the factory picks the default, which is shown as
    ``None`` (there is no backend object for it)."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    backend = make_backend(None)
    assert backend is None


def test_factory_env_var_picks_rust(monkeypatch):
    """Setting the environment variable to "rust" builds a Rust backend.

    It needs an endpoint and key, passed the same way the client passes them.
    """
    monkeypatch.setenv(BACKEND_ENV_VAR, BACKEND_NAME_RUST)
    backend = make_backend(None, url="https://x.documents.azure.com", credential="k")
    assert isinstance(backend, RustBackend)
    assert backend.name == BACKEND_NAME_RUST


def test_factory_kwarg_overrides_env(monkeypatch):
    """The constructor argument wins over the environment variable."""
    monkeypatch.setenv(BACKEND_ENV_VAR, BACKEND_NAME_RUST)
    backend = make_backend(BACKEND_NAME_CORE_PYTHON)
    assert backend is None


def test_factory_invalid_value_fails_loud(monkeypatch):
    """An unknown constructor value fails at construction."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    with pytest.raises(ValueError, match="Invalid backend"):
        make_backend("turbo")


def test_factory_invalid_env_var_fails_loud(monkeypatch):
    """An unknown environment-variable value fails at construction."""
    monkeypatch.setenv(BACKEND_ENV_VAR, "turbo")
    with pytest.raises(ValueError, match="Invalid backend"):
        make_backend(None)


def test_factory_rust_without_master_key_fails_loud(monkeypatch):
    """Rust needs a master-key credential; anything else fails clearly at
    construction rather than later on the first request."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    with pytest.raises(ValueError, match="master-key credential"):
        make_backend(BACKEND_NAME_RUST, url="https://x.documents.azure.com", credential=None)


def test_async_factory_returns_async_backends(monkeypatch):
    """The async factory returns ``None`` for the default and an async Rust
    backend when Rust is asked for."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    assert make_async_backend(None) is None
    assert isinstance(
        make_async_backend(
            BACKEND_NAME_RUST,
            url="https://x.documents.azure.com",
            credential="k",
        ),
        AsyncRustBackend,
    )


def test_async_factory_invalid_value_fails_loud(monkeypatch):
    """The async factory rejects bad input the same way the sync one does."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    with pytest.raises(ValueError, match="Invalid backend"):
        make_async_backend("turbo")


# ---------------------------------------------------------------------------
# What the Rust backend does with a request
# ---------------------------------------------------------------------------
#
# With nothing to send, it returns None so the caller uses the existing
# client. With a real request it calls into the compiled module and wraps the
# result. When the compiled module is missing, it raises a clear error. The
# tests fake the compiled module so they run without a real account. The async
# backend behaves the same way.

def test_rust_backend_returns_none_for_no_prepared_request():
    """With nothing to send, the backend returns ``None`` so the caller uses
    the existing client."""
    backend = RustBackend(endpoint="https://x.documents.azure.com", master_key="k")
    assert backend.execute(prepared=None) is None


def test_rust_backend_dispatches_to_binding(monkeypatch):
    """With a request and the compiled module loaded, the backend calls into
    the module and wraps what it returns."""
    fake_module = MagicMock()
    fake_module.init_client.return_value = "handle-1"
    fake_module.create_item.return_value = (201, 0, {"etag": "v1"}, b'{"id":"x"}')
    monkeypatch.setattr("azure.cosmos._backend.rust._rust_module", fake_module)

    backend = RustBackend(endpoint="https://x.documents.azure.com", master_key="k")
    prepared = PreparedRequest(
        op="create_item",
        container_link="dbs/d/colls/c",
        body_bytes=b'{"id":"x"}',
        partition_key_header='["a"]',
        headers={},
    )
    resp = backend.execute(prepared)

    fake_module.init_client.assert_called_once_with(
        "https://x.documents.azure.com", "k", None
    )
    fake_module.create_item.assert_called_once_with("handle-1", prepared)
    assert resp.status_code == 201
    assert resp.body == b'{"id":"x"}'


def test_rust_backend_accepts_optional_diagnostics_from_binding(monkeypatch):
    """The backend accepts diagnostics returned by the binding."""
    fake_module = MagicMock()
    fake_module.init_client.return_value = "handle-1"
    fake_module.create_item.return_value = (
        201,
        0,
        {"etag": "v1"},
        b'{"id":"x"}',
        "activity=abc duration=8ms requests=1 charge=1RU status=201",
    )
    monkeypatch.setattr("azure.cosmos._backend.rust._rust_module", fake_module)

    backend = RustBackend(endpoint="https://x.documents.azure.com", master_key="k")
    prepared = PreparedRequest(
        op="create_item",
        container_link="dbs/d/colls/c",
        body_bytes=b'{"id":"x"}',
        partition_key_header='["a"]',
        headers={},
    )
    resp = backend.execute(prepared)

    assert resp.status_code == 201
    assert resp.diagnostics == "activity=abc duration=8ms requests=1 charge=1RU status=201"


def test_rust_backend_returns_structured_http_failure_tuple(monkeypatch):
    """A failed request (like a 409) comes back as a normal response with its
    status, sub-status, headers, and body -- not as an error."""
    fake_module = MagicMock()
    fake_module.init_client.return_value = "handle-1"
    fake_module.create_item.return_value = (
        409,
        1002,
        {
            "x-ms-activity-id": "act-409",
            "x-ms-retry-after-ms": "250",
            "x-ms-substatus": "1002",
        },
        b'{"code":"Conflict","message":"already exists"}',
    )
    monkeypatch.setattr("azure.cosmos._backend.rust._rust_module", fake_module)

    backend = RustBackend(endpoint="https://x.documents.azure.com", master_key="k")
    prepared = PreparedRequest(
        op="create_item",
        container_link="dbs/d/colls/c",
        body_bytes=b'{"id":"x"}',
        partition_key_header='["a"]',
        headers={},
    )

    resp = backend.execute(prepared)

    assert resp.status_code == 409
    assert resp.sub_status == 1002
    assert resp.headers["x-ms-activity-id"] == "act-409"
    assert resp.headers["x-ms-retry-after-ms"] == "250"
    assert resp.body == b'{"code":"Conflict","message":"already exists"}'


def test_rust_backend_logs_per_op_backend_telemetry(monkeypatch, caplog):
    """Each executed op emits a debug line naming the backend and op, so a
    migration can confirm from logs alone that traffic stays on the Rust path
    instead of silently falling back to core-python. The handle (which carries a
    credential fingerprint) must not appear in the line."""
    fake_module = MagicMock()
    fake_module.init_client.return_value = "handle-secret-fp"
    fake_module.create_item.return_value = (201, 0, {"etag": "v1"}, b'{"id":"x"}')
    monkeypatch.setattr("azure.cosmos._backend.rust._rust_module", fake_module)

    backend = RustBackend(endpoint="https://x.documents.azure.com", master_key="k")
    prepared = PreparedRequest(
        op="create_item",
        container_link="dbs/d/colls/c",
        body_bytes=b'{"id":"x"}',
        partition_key_header='["a"]',
        headers={},
    )
    with caplog.at_level(logging.DEBUG, logger="azure.cosmos._backend.rust"):
        backend.execute(prepared)
    # Close so the built handle is released here, under this test's fake module,
    # rather than leaking to a finalizer that would run during a later test.
    backend.close()

    messages = [r.getMessage() for r in caplog.records]
    assert any("backend=rust" in m and "op=create_item" in m for m in messages)
    # The handle is intentionally omitted -- it carries a credential fingerprint.
    assert all("handle-secret-fp" not in m for m in messages)


def test_async_rust_backend_logs_per_op_backend_telemetry(monkeypatch, caplog):
    """Async version: the async backend emits the same per-op backend telemetry."""
    fake_module = MagicMock()
    fake_module.init_client.return_value = "handle-secret-fp"
    fake_module.create_item_async = AsyncMock(return_value=(201, 0, {"etag": "v1"}, b'{"id":"x"}'))
    monkeypatch.setattr("azure.cosmos.aio._backend.rust._rust_module", fake_module)

    async def _run():
        backend = AsyncRustBackend(endpoint="https://x.documents.azure.com", master_key="k")
        prepared = PreparedRequest(
            op="create_item",
            container_link="dbs/d/colls/c",
            body_bytes=b'{"id":"x"}',
            partition_key_header='["a"]',
            headers={},
        )
        await backend.execute(prepared)
        # Close so the built handle is released here, not leaked to a finalizer that
        # would run during a later test (and call that test's fake close_client).
        await backend.close()

    with caplog.at_level(logging.DEBUG, logger="azure.cosmos.aio._backend.rust"):
        asyncio.run(_run())

    messages = [r.getMessage() for r in caplog.records]
    assert any("backend=rust" in m and "op=create_item" in m for m in messages)
    assert all("handle-secret-fp" not in m for m in messages)


def test_rust_backend_propagates_transport_runtime_error(monkeypatch):
    """A real driver failure (not an HTTP response) is raised as an error."""
    fake_module = MagicMock()
    fake_module.init_client.return_value = "handle-1"
    fake_module.create_item.side_effect = RuntimeError("driver execute_operation failed: DNS lookup failed")
    monkeypatch.setattr("azure.cosmos._backend.rust._rust_module", fake_module)

    backend = RustBackend(endpoint="https://x.documents.azure.com", master_key="k")
    prepared = PreparedRequest(
        op="create_item",
        container_link="dbs/d/colls/c",
        body_bytes=b'{"id":"x"}',
        partition_key_header='["a"]',
        headers={},
    )

    with pytest.raises(RuntimeError, match="DNS lookup failed"):
        backend.execute(prepared)


def test_rust_backend_raises_when_binding_not_built(monkeypatch):
    """When the compiled module is missing, the backend raises a clear error
    pointing at the build step instead of failing in a confusing way later."""
    monkeypatch.setattr("azure.cosmos._backend.rust._rust_module", None)
    backend = RustBackend(endpoint="https://x.documents.azure.com", master_key="k")
    prepared = PreparedRequest(
        op="create_item",
        container_link="dbs/d/colls/c",
        body_bytes=b'{"id":"x"}',
        partition_key_header='["a"]',
        headers={},
    )
    with pytest.raises(NotImplementedError, match="not present"):
        backend.execute(prepared)


def test_async_rust_backend_returns_none_for_no_prepared_request():
    """Async version: with nothing to send, the backend returns ``None``."""
    async def _run():
        backend = AsyncRustBackend(endpoint="https://x.documents.azure.com", master_key="k")
        assert await backend.execute(prepared=None) is None
    asyncio.run(_run())


def test_async_rust_backend_dispatches_to_binding(monkeypatch):
    """Async version: the backend awaits the binding's async ``create_item_async``
    and wraps the result the same way -- no worker thread per call."""
    fake_module = MagicMock()
    fake_module.init_client.return_value = "handle-1"
    fake_module.create_item_async = AsyncMock(return_value=(201, 0, {"etag": "v1"}, b'{"id":"x"}'))
    monkeypatch.setattr("azure.cosmos.aio._backend.rust._rust_module", fake_module)

    async def _run():
        backend = AsyncRustBackend(endpoint="https://x.documents.azure.com", master_key="k")
        prepared = PreparedRequest(
            op="create_item",
            container_link="dbs/d/colls/c",
            body_bytes=b'{"id":"x"}',
            partition_key_header='["a"]',
            headers={},
        )
        resp = await backend.execute(prepared)
        fake_module.init_client.assert_called_once()
        fake_module.create_item_async.assert_awaited_once_with("handle-1", prepared)
        assert resp.status_code == 201
        assert resp.body == b'{"id":"x"}'
    asyncio.run(_run())


def test_async_rust_backend_accepts_optional_diagnostics_from_binding(monkeypatch):
    """Async version: diagnostics returned by the binding are preserved."""
    fake_module = MagicMock()
    fake_module.init_client.return_value = "handle-1"
    fake_module.create_item_async = AsyncMock(
        return_value=(
            201,
            0,
            {"etag": "v1"},
            b'{"id":"x"}',
            "activity=abc duration=7ms requests=1 charge=1RU status=201",
        )
    )
    monkeypatch.setattr("azure.cosmos.aio._backend.rust._rust_module", fake_module)

    async def _run():
        backend = AsyncRustBackend(endpoint="https://x.documents.azure.com", master_key="k")
        prepared = PreparedRequest(
            op="create_item",
            container_link="dbs/d/colls/c",
            body_bytes=b'{"id":"x"}',
            partition_key_header='["a"]',
            headers={},
        )
        resp = await backend.execute(prepared)
        assert resp.status_code == 201
        assert resp.diagnostics == "activity=abc duration=7ms requests=1 charge=1RU status=201"

    asyncio.run(_run())


def test_async_rust_backend_returns_structured_http_failure_tuple(monkeypatch):
    """Async version: a failed request comes back as a normal response, not an
    error."""
    fake_module = MagicMock()
    fake_module.init_client.return_value = "handle-1"
    fake_module.create_item_async = AsyncMock(
        return_value=(
            404,
            0,
            {"x-ms-activity-id": "act-404"},
            b'{"code":"NotFound","message":"missing"}',
        )
    )
    monkeypatch.setattr("azure.cosmos.aio._backend.rust._rust_module", fake_module)

    async def _run():
        backend = AsyncRustBackend(endpoint="https://x.documents.azure.com", master_key="k")
        prepared = PreparedRequest(
            op="create_item",
            container_link="dbs/d/colls/c",
            body_bytes=b'{"id":"x"}',
            partition_key_header='["a"]',
            headers={},
        )
        resp = await backend.execute(prepared)
        assert resp.status_code == 404
        assert resp.headers["x-ms-activity-id"] == "act-404"
        assert resp.body == b'{"code":"NotFound","message":"missing"}'

    asyncio.run(_run())


def test_async_rust_backend_propagates_transport_runtime_error(monkeypatch):
    """Async version: a real driver failure is raised as an error."""
    fake_module = MagicMock()
    fake_module.init_client.return_value = "handle-1"
    fake_module.create_item_async = AsyncMock(side_effect=RuntimeError("driver execute_operation failed: TLS handshake failed"))
    monkeypatch.setattr("azure.cosmos.aio._backend.rust._rust_module", fake_module)

    async def _run():
        backend = AsyncRustBackend(endpoint="https://x.documents.azure.com", master_key="k")
        prepared = PreparedRequest(
            op="create_item",
            container_link="dbs/d/colls/c",
            body_bytes=b'{"id":"x"}',
            partition_key_header='["a"]',
            headers={},
        )
        with pytest.raises(RuntimeError, match="TLS handshake failed"):
            await backend.execute(prepared)

    asyncio.run(_run())


def test_async_rust_backend_raises_when_binding_not_built(monkeypatch):
    """Async version: a missing compiled module raises a clear error."""
    monkeypatch.setattr("azure.cosmos.aio._backend.rust._rust_module", None)

    async def _run():
        backend = AsyncRustBackend(endpoint="https://x.documents.azure.com", master_key="k")
        prepared = PreparedRequest(
            op="create_item",
            container_link="dbs/d/colls/c",
            body_bytes=b'{"id":"x"}',
            partition_key_header='["a"]',
            headers={},
        )
        with pytest.raises(NotImplementedError, match="not present"):
            await backend.execute(prepared)
    asyncio.run(_run())


def test_async_backend_coalesces_concurrent_first_init_to_one_call(monkeypatch):
    """A burst of concurrent first-operations builds the client handle exactly
    once: every first-caller awaits one shared init future instead of each
    scheduling its own ``init_client`` build on a background thread."""
    init_calls = []
    fake_module = MagicMock()

    def _slow_init(*args):
        # Block briefly so the whole burst reaches _ensure_handle while the first
        # init is still in flight on the executor thread -- the window in which
        # uncoalesced callers would each schedule their own offload.
        init_calls.append(args)
        time.sleep(0.05)
        return "handle-1"

    fake_module.init_client.side_effect = _slow_init
    fake_module.read_item_async = AsyncMock(return_value=(200, 0, {}, b"{}"))
    monkeypatch.setattr("azure.cosmos.aio._backend.rust._rust_module", fake_module)

    prepared = PreparedRequest(
        op="read_item",
        container_link="dbs/d/colls/c",
        body_bytes=b"",
        partition_key_header='["a"]',
        headers={},
        item_id="x",
    )

    async def _run():
        backend = AsyncRustBackend(endpoint="https://x.documents.azure.com", master_key="k")
        await asyncio.gather(*(backend.execute(prepared) for _ in range(50)))

    asyncio.run(_run())
    assert len(init_calls) == 1, f"init_client should run once, ran {len(init_calls)} times"
    assert fake_module.read_item_async.await_count == 50


def test_async_backend_retries_init_after_failure(monkeypatch):
    """A failed init is not cached on the shared future: the next operation retries
    ``init_client`` rather than handing back the first failure forever."""
    attempts = []
    fake_module = MagicMock()

    def _flaky_init(*args):
        attempts.append(args)
        if len(attempts) == 1:
            raise RuntimeError("init boom")
        return "handle-1"

    fake_module.init_client.side_effect = _flaky_init
    fake_module.read_item_async = AsyncMock(return_value=(200, 0, {}, b"{}"))
    monkeypatch.setattr("azure.cosmos.aio._backend.rust._rust_module", fake_module)

    prepared = PreparedRequest(
        op="read_item",
        container_link="dbs/d/colls/c",
        body_bytes=b"",
        partition_key_header='["a"]',
        headers={},
        item_id="x",
    )

    async def _run():
        backend = AsyncRustBackend(endpoint="https://x.documents.azure.com", master_key="k")
        # First op: init fails and surfaces to the caller.
        with pytest.raises(RuntimeError, match="init boom"):
            await backend.execute(prepared)
        # Second op: init is retried (not a cached failure) and succeeds.
        resp = await backend.execute(prepared)
        assert resp.status_code == 200

    asyncio.run(_run())
    assert len(attempts) == 2, f"init should be retried after failure, attempts={len(attempts)}"


def test_async_backend_close_during_init_closes_built_handle(monkeypatch):
    """If close() runs while the first init_client is still building, the handle the
    build produces is closed (not left open), close() does not wait for the build to
    finish, and the operation that triggered the build fails with a closed-client
    error."""
    init_in_flight = threading.Event()
    allow_init_finish = threading.Event()
    closed = []
    fake_module = MagicMock()

    def _slow_init(*args):
        init_in_flight.set()
        allow_init_finish.wait(5)  # hold the build open until the test lets it finish
        return "handle-1"

    fake_module.init_client.side_effect = _slow_init
    fake_module.close_client.side_effect = closed.append
    fake_module.read_item_async = AsyncMock(return_value=(200, 0, {}, b"{}"))
    monkeypatch.setattr("azure.cosmos.aio._backend.rust._rust_module", fake_module)

    prepared = PreparedRequest(
        op="read_item",
        container_link="dbs/d/colls/c",
        body_bytes=b"",
        partition_key_header='["a"]',
        headers={},
        item_id="x",
    )

    async def _run():
        backend = AsyncRustBackend(endpoint="https://x.documents.azure.com", master_key="k")
        op = asyncio.ensure_future(backend.execute(prepared))
        # Wait until init_client is running on the build thread.
        await asyncio.get_running_loop().run_in_executor(None, init_in_flight.wait, 5)
        # close() returns without waiting for the build to finish: the build does not
        # hold _handle_lock during init_client, so close() takes that lock right away.
        await asyncio.wait_for(backend.close(), timeout=2)
        # Let the build finish; it sees the client is closing and closes the handle it
        # built instead of leaving it open.
        allow_init_finish.set()
        with pytest.raises(Exception):
            await op

    asyncio.run(_run())
    assert closed == ["handle-1"], f"handle built during close should be closed, got {closed}"
    fake_module.init_client.assert_called_once()


def test_async_backend_propagates_cancellation_into_binding(monkeypatch):
    """Cancelling an awaited ``execute()`` cancels the underlying binding awaitable
    rather than swallowing the cancellation or shielding the call.

    This is the Python half of cancellation propagation: the Rust async path
    (``wire.rs``) aborts the spawned Tokio driver task when the awaitable it
    returned is dropped on cancellation, so a client-side timeout actually stops
    the in-flight operation instead of detaching it to run to completion. That
    abort only fires if the Python layer lets the cancellation reach the awaitable
    -- which this test pins down so a future change (e.g. wrapping dispatch in
    ``asyncio.shield``) can't silently defeat it."""
    fake_module = MagicMock()
    fake_module.init_client.return_value = "handle-1"
    dispatch_cancelled = []

    async def _slow_read(_handle, _prepared):
        try:
            await asyncio.sleep(10)
        except asyncio.CancelledError:
            dispatch_cancelled.append(True)
            raise
        return (200, 0, {}, b"{}")  # pragma: no cover - cancelled before here

    fake_module.read_item_async = _slow_read
    monkeypatch.setattr("azure.cosmos.aio._backend.rust._rust_module", fake_module)

    prepared = PreparedRequest(
        op="read_item",
        container_link="dbs/d/colls/c",
        body_bytes=b"",
        partition_key_header='["a"]',
        headers={},
        item_id="x",
    )

    async def _run():
        backend = AsyncRustBackend(endpoint="https://x.documents.azure.com", master_key="k")
        op = asyncio.ensure_future(backend.execute(prepared))
        # Let the op build the handle and reach the dispatch await, then cancel it.
        await asyncio.sleep(0.05)
        op.cancel()
        with pytest.raises(asyncio.CancelledError):
            await op

    asyncio.run(_run())
    assert dispatch_cancelled == [True], (
        "execute() must let cancellation reach the binding awaitable, so the Rust "
        "layer can abort the spawned driver task"
    )


def test_async_backend_finalizer_does_not_block_event_loop(monkeypatch):
    """If the finalizer fires while an event loop is running on this thread (GC
    collecting the client mid-run), the blocking driver close must be offloaded to
    a daemon thread, not run inline on the loop thread -- otherwise close_client
    would stall the loop. The config drop stays inline (it does not block)."""
    close_started = threading.Event()
    close_may_finish = threading.Event()
    close_thread_names = []
    fake_module = MagicMock()
    fake_module.init_client.return_value = "handle-finalizer"
    fake_module.read_item_async = AsyncMock(return_value=(200, 0, {}, b"{}"))

    def _blocking_close(handle):
        # Only this backend's close is measured. Other tests' async backends can be
        # garbage-collected during this test (their finalizers call this same
        # monkeypatched close_client); ignoring foreign handles keeps their thread
        # from polluting the measurement -- and keeps them from blocking on
        # close_may_finish, which could stall an inline GC finalizer.
        if handle != "handle-finalizer":
            return
        close_thread_names.append(threading.current_thread().name)
        close_started.set()
        close_may_finish.wait(5)  # hold the close open to expose any inline block

    fake_module.close_client.side_effect = _blocking_close
    monkeypatch.setattr("azure.cosmos.aio._backend.rust._rust_module", fake_module)

    prepared = PreparedRequest(
        op="read_item",
        container_link="dbs/d/colls/c",
        body_bytes=b"",
        partition_key_header='["a"]',
        headers={},
        item_id="x",
    )

    async def _run():
        backend = AsyncRustBackend(endpoint="https://x.documents.azure.com", master_key="k")
        await backend.execute(prepared)  # build the handle so the finalizer has work
        main_thread = threading.current_thread().name
        # Fire the finalizer while this loop is running.
        backend.__del__()
        # The offloaded close should start on another thread; meanwhile the loop
        # must keep turning even though close_client is still blocked.
        assert close_started.wait(2), "offloaded close did not start"
        for _ in range(5):
            await asyncio.sleep(0)  # would hang here if the close blocked the loop
        close_may_finish.set()
        return main_thread

    main_thread = asyncio.run(_run())
    assert close_thread_names, "close_client was never called"
    assert close_thread_names[0] != main_thread, (
        f"close ran on the loop thread {close_thread_names[0]!r}; must be offloaded"
    )
    assert close_thread_names[0] == "cosmos-rust-finalizer"


def test_helper_parses_backend_response_into_cosmos_dict(monkeypatch):
    """A successful backend response is turned into a dict the caller can read
    by key (like ``result["_etag"]``), the same shape the existing path
    returns."""

    backend = MagicMock()
    backend.name = BACKEND_NAME_RUST
    backend.execute.return_value = BackendResponse(
        status_code=201,
        sub_status=0,
        headers=None,
        body=(
            b'{"id":"order-42","pk":"customerA","_etag":"\\"00000000-0000-0000-1234-567890abcdef\\"",'
            b'"_rid":"abc==","_self":"dbs/x/colls/y/docs/order-42","_ts":1746700000}'
        ),
        diagnostics=None,
    )

    helper = ItemHelper(backend, client_connection=MagicMock())
    result = helper.create_item(
        container_link="dbs/x/colls/y",
        body={"id": "order-42", "pk": "customerA"},
    )

    # The result is a dict, so the caller reads fields by key.
    assert result["_etag"] == '"00000000-0000-0000-1234-567890abcdef"'
    assert result["id"] == "order-42"


# NOTE: An older test for a "core-python backend" was removed. There is no such
# class now; "use the existing client" is signalled by no backend being set,
# and the helper handles that. See the fall-through tests in
# test_item_helper_unit.py.


def test_dataclasses_are_frozen():
    """The request and response objects are frozen, so a backend can't change
    them by accident."""
    p = PreparedRequest(
        op="create_item",
        container_link="dbs/d/colls/c",
        body_bytes=b"{}",
        partition_key_header='["customerA"]',
        headers={"x-ms-version": "2020-07-15"},
    )
    with pytest.raises(Exception):  # FrozenInstanceError
        setattr(p, "body_bytes", b"different")

    r = BackendResponse(status_code=201)
    with pytest.raises(Exception):
        setattr(r, "status_code", 200)


# ---------------------------------------------------------------------------
# Carrying client-construction settings (preferred_locations) to the driver
# ---------------------------------------------------------------------------
#
# The factory folds the settings the Rust driver can honor into a
# PreparedClientConfig, and the backend hands it to init_client as the third
# argument. With nothing to carry the config stays None, so the binding call is
# identical to the original two-argument form.

def test_build_client_config_returns_none_when_nothing_to_carry():
    """No preferred_locations (absent or empty) -> no config object, so the
    binding call stays the plain two-argument form."""
    assert build_client_config(None) is None
    assert build_client_config([]) is None
    assert build_client_config(()) is None


def test_build_client_config_carries_preferred_locations():
    """A non-empty preferred_locations is captured, in order, as an immutable
    tuple on the config."""
    config = build_client_config(["West US", "East US"])
    assert isinstance(config, PreparedClientConfig)
    assert config.preferred_locations == ("West US", "East US")


def test_prepared_client_config_is_frozen():
    """The config is frozen so a backend cannot change what the client passed."""
    config = PreparedClientConfig(preferred_locations=("West US",))
    with pytest.raises(Exception):  # FrozenInstanceError
        setattr(config, "preferred_locations", ("East US",))


def test_prepared_client_config_repr_distinguishes_every_field():
    """Every behavior-affecting field must change ``repr()`` when it changes.

    Motivation (silent-correctness guard): the Rust binding keys its shared
    driver cache on ``salted_hash(PreparedClientConfig.__repr__())`` (see
    ``runtime.rs`` ``config_fingerprint``). The cache is correct only if the repr
    is *total* -- i.e. two configs that differ in any field the driver honors
    render different reprs. If a field were ever excluded from the repr (e.g. a
    future ``field(repr=False)`` or a hand-written ``__repr__`` that forgets a
    field), two semantically-different configs would hash equal and the second
    client would silently share a driver built with the first client's settings
    (regions, consistency, throttling, hedging, proxy). That failure is silent
    and dangerous, so this test pins repr totality.

    The check is field-driven: for every dataclass field we build a baseline and
    a variant that differs only in that field, and assert their reprs differ.
    Adding a new field with a distinguishable value below keeps this guard
    honest as the config grows.
    """
    import dataclasses

    # A distinguishable non-default value per field. Every declared field MUST
    # appear here, so adding a field without updating this map fails the test
    # (the assertion below), forcing a conscious decision.
    variants = {
        "preferred_locations": ("East US",),
        "excluded_locations": ("Central US",),
        "throttling_max_retry_count": 7,
        "throttling_max_retry_wait_time_seconds": 12.5,
        "hedging_threshold_ms": 250,
        "user_agent_suffix": "checkout-westus2",
        "consistency_level": "Eventual",
        "proxy_allowed": True,
    }

    field_names = {f.name for f in dataclasses.fields(PreparedClientConfig)}
    assert field_names == set(variants), (
        "PreparedClientConfig fields changed; update the `variants` map so the "
        "repr-totality guard covers every behavior-affecting field. "
        "Missing from test: {}; stale in test: {}".format(
            field_names - set(variants), set(variants) - field_names
        )
    )

    baseline = PreparedClientConfig()
    baseline_repr = repr(baseline)
    for name, value in variants.items():
        changed = dataclasses.replace(baseline, **{name: value})
        assert repr(changed) != baseline_repr, (
            "Changing field {!r} did not change PreparedClientConfig.__repr__; "
            "the Rust driver cache would treat these two configs as identical "
            "and silently share a driver.".format(name)
        )


def test_factory_carries_preferred_locations_into_rust_backend(monkeypatch):
    """make_backend folds preferred_locations into the backend's client config;
    with none passed, the config is None (unchanged behavior)."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    with_locations = make_backend(
        BACKEND_NAME_RUST,
        url="https://x.documents.azure.com",
        credential="k",
        preferred_locations=["West US", "East US"],
    )
    assert isinstance(with_locations, RustBackend)
    assert with_locations._client_config == PreparedClientConfig(
        preferred_locations=("West US", "East US")
    )

    without = make_backend(
        BACKEND_NAME_RUST, url="https://y.documents.azure.com", credential="k"
    )
    assert isinstance(without, RustBackend)
    assert without._client_config is None


def test_async_factory_carries_preferred_locations_into_rust_backend(monkeypatch):
    """The async factory carries preferred_locations the same way."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    backend = make_async_backend(
        BACKEND_NAME_RUST,
        url="https://x.documents.azure.com",
        credential="k",
        preferred_locations=["West US"],
    )
    assert isinstance(backend, AsyncRustBackend)
    assert backend._client_config == PreparedClientConfig(
        preferred_locations=("West US",)
    )


def test_rust_backend_passes_client_config_to_init_client(monkeypatch):
    """The backend hands the client config to init_client as the third argument
    so the binding can apply it when it builds the driver."""
    fake_module = MagicMock()
    fake_module.init_client.return_value = "handle-1"
    monkeypatch.setattr("azure.cosmos._backend.rust._rust_module", fake_module)

    config = PreparedClientConfig(preferred_locations=("West US", "East US"))
    backend = RustBackend(
        endpoint="https://x.documents.azure.com",
        master_key="k",
        client_config=config,
    )
    backend._ensure_handle()

    fake_module.init_client.assert_called_once_with(
        "https://x.documents.azure.com", "k", config
    )


def test_async_rust_backend_passes_client_config_to_init_client(monkeypatch):
    """Async version: the config rides on the init_client call the same way."""
    fake_module = MagicMock()
    fake_module.init_client.return_value = "handle-1"
    monkeypatch.setattr("azure.cosmos.aio._backend.rust._rust_module", fake_module)

    config = PreparedClientConfig(preferred_locations=("West US",))

    async def _run():
        backend = AsyncRustBackend(
            endpoint="https://x.documents.azure.com",
            master_key="k",
            client_config=config,
        )
        await backend._ensure_handle()

    asyncio.run(_run())

    fake_module.init_client.assert_called_once_with(
        "https://x.documents.azure.com", "k", config
    )


class _ProxyGlobalRuntimeFakeModule:
    """Fake Rust module to test process-global proxy policy.

    The first client sets the proxy policy for the process. Later clients must
    use the same policy or leave it unset.
    """

    def __init__(self):
        self._initialized_proxy_allowed = None
        self._next_handle = 0

    def init_client(self, *args):
        config = args[2] if len(args) >= 3 else None
        requested = getattr(config, "proxy_allowed", None) if config is not None else None
        if self._initialized_proxy_allowed is None:
            self._initialized_proxy_allowed = requested
        elif requested is not None and requested != self._initialized_proxy_allowed:
            raise ValueError(
                "Rust runtime proxy configuration is process-global and was already initialized"
            )
        self._next_handle += 1
        return "handle-{}".format(self._next_handle)

    def close_client(self, _handle):
        return None


def test_rust_backend_conflicting_proxy_allowed_raises_at_construction(monkeypatch):
    """Sync path: conflicting proxy policy fails at client construction."""
    fake_module = _ProxyGlobalRuntimeFakeModule()
    monkeypatch.setattr("azure.cosmos._backend.rust._rust_module", fake_module)

    RustBackend(
        endpoint="https://x.documents.azure.com",
        master_key="k",
        client_config=PreparedClientConfig(proxy_allowed=True),
    )
    with pytest.raises(ProxyPolicyConflictError, match="process-global"):
        RustBackend(
            endpoint="https://x.documents.azure.com",
            master_key="k",
            client_config=PreparedClientConfig(proxy_allowed=False),
        )


def test_rust_backend_unset_proxy_allowed_does_not_conflict(monkeypatch):
    """Sync path: an unset later value carries nothing and does not conflict."""
    fake_module = _ProxyGlobalRuntimeFakeModule()
    monkeypatch.setattr("azure.cosmos._backend.rust._rust_module", fake_module)

    first = RustBackend(
        endpoint="https://x.documents.azure.com",
        master_key="k",
        client_config=PreparedClientConfig(proxy_allowed=True),
    )
    second = RustBackend(
        endpoint="https://x.documents.azure.com",
        master_key="k",
        client_config=None,
    )

    first._ensure_handle()
    second._ensure_handle()


def test_async_rust_backend_conflicting_proxy_allowed_raises_at_construction(monkeypatch):
    """Async path: conflicting proxy policy fails at client construction."""
    fake_module = _ProxyGlobalRuntimeFakeModule()
    monkeypatch.setattr("azure.cosmos.aio._backend.rust._rust_module", fake_module)

    async def _run():
        AsyncRustBackend(
            endpoint="https://x.documents.azure.com",
            master_key="k",
            client_config=PreparedClientConfig(proxy_allowed=True),
        )
        with pytest.raises(ProxyPolicyConflictError, match="process-global"):
            AsyncRustBackend(
                endpoint="https://x.documents.azure.com",
                master_key="k",
                client_config=PreparedClientConfig(proxy_allowed=False),
            )

    asyncio.run(_run())


# ---------------------------------------------------------------------------
# Carrying the other driver-understood startup settings (excluded_locations,
# throttling retry, hedging threshold) into the client config
# ---------------------------------------------------------------------------
#
# These ride the same PreparedClientConfig the binding reads at init_client time.
# Each is carried only when the customer actually expressed it, so an untuned
# client still produces no config (None) and the binding call stays the plain
# two-argument form.


def test_build_client_config_carries_excluded_locations():
    """excluded_locations is captured as an immutable tuple, like preferred."""
    config = build_client_config(None, excluded_locations=["Central US"])
    assert isinstance(config, PreparedClientConfig)
    assert config.excluded_locations == ("Central US",)
    assert config.preferred_locations == ()


def test_build_client_config_empty_excluded_locations_is_none():
    """Empty excluded_locations alone carries nothing."""
    assert build_client_config(None, excluded_locations=[]) is None


def test_build_client_config_carries_throttling_retry():
    """Both throttle dials are captured when tuned."""
    config = build_client_config(
        None,
        throttling_max_retry_count=9,
        throttling_max_retry_wait_time_seconds=30,
    )
    assert config.throttling_max_retry_count == 9
    assert config.throttling_max_retry_wait_time_seconds == 30


def test_build_client_config_partial_throttling_retry_leaves_other_none():
    """Tuning only the count leaves the wait at None (driver keeps its default)."""
    config = build_client_config(None, throttling_max_retry_count=3)
    assert config.throttling_max_retry_count == 3
    assert config.throttling_max_retry_wait_time_seconds is None


def test_build_client_config_hedging_true_uses_default_threshold():
    """availability_strategy=True carries the default threshold (500 ms)."""
    config = build_client_config(None, availability_strategy=True)
    assert config.hedging_threshold_ms == 500


def test_build_client_config_hedging_dict_uses_threshold_ms_and_drops_steps():
    """A dict carries threshold_ms; threshold_steps_ms has no driver home."""
    config = build_client_config(
        None, availability_strategy={"threshold_ms": 20, "threshold_steps_ms": 10}
    )
    assert config.hedging_threshold_ms == 20


def test_build_client_config_hedging_false_carries_nothing():
    """Explicit availability_strategy=False carries nothing (mirrors the client
    default of 'no strategy'); sync and async behave identically here."""
    assert build_client_config(None, availability_strategy=False) is None


def test_build_client_config_hedging_none_carries_nothing():
    """An absent availability_strategy carries nothing."""
    assert build_client_config(None, availability_strategy=None) is None


def test_build_client_config_hedging_invalid_threshold_raises():
    """A non-positive threshold_ms raises the same ValueError as the legacy path
    (validation reused from CrossRegionHedgingStrategy)."""
    with pytest.raises(ValueError, match="threshold_ms must be positive"):
        build_client_config(None, availability_strategy={"threshold_ms": 0})


def test_build_client_config_combines_all_settings():
    """All settings fold into one config object together."""
    config = build_client_config(
        ["West US"],
        excluded_locations=["Central US"],
        throttling_max_retry_count=5,
        throttling_max_retry_wait_time_seconds=12,
        availability_strategy={"threshold_ms": 25},
        user_agent_suffix="checkout-westus2",
        consistency_level="Eventual",
    )
    assert config == PreparedClientConfig(
        preferred_locations=("West US",),
        excluded_locations=("Central US",),
        throttling_max_retry_count=5,
        throttling_max_retry_wait_time_seconds=12,
        hedging_threshold_ms=25,
        user_agent_suffix="checkout-westus2",
        consistency_level="Eventual",
    )


def test_build_client_config_carries_user_agent_suffix():
    """A non-empty user_agent_suffix is carried for the driver to stamp on every
    request's User-Agent (the label that previously went nowhere on Rust)."""
    config = build_client_config(None, user_agent_suffix="checkout-westus2")
    assert isinstance(config, PreparedClientConfig)
    assert config.user_agent_suffix == "checkout-westus2"


def test_build_client_config_only_user_agent_suffix_still_builds_config():
    """A client that tunes nothing but the user-agent suffix must still produce a
    config (not None), so the label actually reaches the driver -- carrying it is
    the whole point of closing the 'suffix silently goes nowhere' gap."""
    config = build_client_config(None, user_agent_suffix="order-service")
    assert config == PreparedClientConfig(user_agent_suffix="order-service")


def test_build_client_config_empty_user_agent_suffix_is_none():
    """An empty string (or absent) suffix carries nothing, like an empty location
    list, so an untuned client still produces no config."""
    assert build_client_config(None, user_agent_suffix="") is None
    assert build_client_config(None, user_agent_suffix=None) is None


@pytest.mark.parametrize("level", ["Eventual", "Session", "Strong"])
def test_build_client_config_carries_supported_consistency_level(level):
    """Each supported consistency level is carried so the chosen level actually
    reaches the driver (the bug was that it silently went nowhere on Rust)."""
    config = build_client_config(None, consistency_level=level)
    assert config == PreparedClientConfig(consistency_level=level)


def test_build_client_config_only_consistency_still_builds_config():
    """A client that tunes nothing but the consistency level must still produce a
    config (not None), so the chosen level reaches the driver."""
    config = build_client_config(None, consistency_level="Session")
    assert isinstance(config, PreparedClientConfig)
    assert config.consistency_level == "Session"


def test_build_client_config_no_consistency_carries_nothing():
    """An absent (or empty) consistency level carries nothing, leaving the driver
    at the account default -- an untuned client is unchanged."""
    assert build_client_config(None, consistency_level=None) is None
    assert build_client_config(None, consistency_level="") is None


@pytest.mark.parametrize("proxy_allowed", [True, False])
def test_build_client_config_only_proxy_allowed_still_builds_config(proxy_allowed):
    """Proxy allowance is a runtime-level Rust switch; an explicit value must
    still produce a config even when no other startup setting is tuned."""
    config = build_client_config(None, proxy_allowed=proxy_allowed)
    assert isinstance(config, PreparedClientConfig)
    assert config.proxy_allowed is proxy_allowed


def test_build_client_config_rejects_non_bool_proxy_allowed():
    """proxy_allowed is a boolean contract; reject non-bool values at client
    construction instead of failing later at first operation."""
    with pytest.raises(ValueError, match="proxy_allowed must be a bool"):
        build_client_config(None, proxy_allowed="true")


@pytest.mark.parametrize("first, second", [(True, False), (False, True)])
def test_register_proxy_policy_rejects_later_differing_explicit_value(first, second):
    """proxy_allowed is process-global for the Rust runtime, so once one client sets
    an explicit value a later client requesting a *different* explicit value must fail
    fast at construction -- deterministically, instead of relying on the binding's late,
    race-determined OnceLock check at first operation. (_isolate_driver_registry resets
    the process policy between tests.)"""
    register_proxy_policy(build_client_config(None, proxy_allowed=first))
    with pytest.raises(ProxyPolicyConflictError, match="process-global"):
        register_proxy_policy(build_client_config(None, proxy_allowed=second))


@pytest.mark.parametrize("value", [True, False])
def test_register_proxy_policy_accepts_repeated_equal_value(value):
    """Two clients that agree on proxy_allowed are compatible: the second must not
    raise (idempotent), matching the binding allowing an equal value."""
    register_proxy_policy(build_client_config(None, proxy_allowed=value))
    register_proxy_policy(build_client_config(None, proxy_allowed=value))


@pytest.mark.parametrize("explicit", [True, False])
def test_register_proxy_policy_unset_client_never_sets_or_conflicts(explicit):
    """A client that leaves proxy_allowed unset (None) accepts whatever value wins and
    never establishes the policy itself -- mirroring the binding's proxy_allowed_conflicts
    (None never conflicts and None never pins). So None-before-explicit and
    explicit-before-None both pass, and the explicit value is the one that sticks."""
    # None first: it must not establish a policy, so a later explicit value is accepted.
    register_proxy_policy(build_client_config(None, proxy_allowed=None))
    register_proxy_policy(build_client_config(None, proxy_allowed=explicit))
    # And a None client after an explicit value is always compatible.
    register_proxy_policy(build_client_config(None, proxy_allowed=None))
    # The explicit value is now the policy: a later differing explicit value conflicts.
    with pytest.raises(ProxyPolicyConflictError):
        register_proxy_policy(build_client_config(None, proxy_allowed=not explicit))


def test_register_proxy_policy_tolerates_none_config():
    """An untuned client carries no config object at all (build_client_config returns
    None); the policy check must treat that exactly like proxy_allowed unset."""
    register_proxy_policy(None)
    # Still no policy established: an explicit value afterward sets it cleanly.
    register_proxy_policy(build_client_config(None, proxy_allowed=True))
    with pytest.raises(ProxyPolicyConflictError):
        register_proxy_policy(build_client_config(None, proxy_allowed=False))


@pytest.mark.parametrize("level", ["BoundedStaleness", "ConsistentPrefix"])
def test_build_client_config_rejects_unsupported_consistency_level(level):
    """Bounded Staleness / Consistent Prefix have no driver equivalent yet, so
    they are rejected rather than silently dropped."""
    with pytest.raises(ValueError, match="not yet supported on the Rust backend"):
        build_client_config(None, consistency_level=level)


def test_build_client_config_rejects_unknown_consistency_level():
    """An unrecognized consistency-level string is rejected, not dropped."""
    with pytest.raises(ValueError, match="not a recognized Cosmos consistency level"):
        build_client_config(None, consistency_level="Nonsense")


def test_factory_carries_all_startup_settings_into_rust_backend(monkeypatch):
    """make_backend folds every supported startup setting into the backend's
    client config."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    backend = make_backend(
        BACKEND_NAME_RUST,
        url="https://x.documents.azure.com",
        credential="k",
        excluded_locations=["Central US"],
        throttling_max_retry_count=7,
        throttling_max_retry_wait_time_seconds=20,
        availability_strategy=True,
        user_agent_suffix="checkout-westus2",
        consistency_level="Eventual",
        proxy_allowed=True,
    )
    assert isinstance(backend, RustBackend)
    assert backend._client_config == PreparedClientConfig(
        excluded_locations=("Central US",),
        throttling_max_retry_count=7,
        throttling_max_retry_wait_time_seconds=20,
        hedging_threshold_ms=500,
        user_agent_suffix="checkout-westus2",
        consistency_level="Eventual",
        proxy_allowed=True,
    )


def test_async_factory_carries_all_startup_settings_into_rust_backend(monkeypatch):
    """The async factory carries the same settings the same way."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    backend = make_async_backend(
        BACKEND_NAME_RUST,
        url="https://x.documents.azure.com",
        credential="k",
        excluded_locations=["Central US", "East US"],
        availability_strategy={"threshold_ms": 15},
        user_agent_suffix="reporting-eastus",
        consistency_level="Session",
        proxy_allowed=False,
    )
    assert isinstance(backend, AsyncRustBackend)
    assert backend._client_config == PreparedClientConfig(
        excluded_locations=("Central US", "East US"),
        hedging_threshold_ms=15,
        user_agent_suffix="reporting-eastus",
        consistency_level="Session",
        proxy_allowed=False,
    )


# ---------------------------------------------------------------------------
# get_database_account fails loudly on the Rust path (no core-python fallback)
# ---------------------------------------------------------------------------
#
# get_database_account is a client-level read that isn't routed through the
# backend dispatch; on a Rust-backed client it must raise a clear gap error
# instead of silently borrowing the legacy core-python connection.


def test_account_read_guard_is_noop_for_core_python():
    """No backend (core-python) -> the guard does nothing, legacy path runs."""
    assert raise_account_read_unsupported(None) is None


def test_account_read_guard_raises_for_rust_backend():
    """Any non-None backend (the Rust path) -> a clear not-yet-available error."""
    backend = object()  # stands in for a RustBackend / AsyncRustBackend
    with pytest.raises(NotImplementedError, match="not yet available on the Rust backend"):
        raise_account_read_unsupported(backend)


# ---------------------------------------------------------------------------
# Credential classification for the Rust backend (_resolve_credential)
# ---------------------------------------------------------------------------
#
# The Rust backend accepts a master key (string or {"masterKey": ...}) or a
# token credential. A *synchronous* token credential is forwarded to the driver
# as-is; an *async* token credential is wrapped in an AsyncTokenCredentialBridge
# that drives its coroutine on a dedicated loop thread and exposes the synchronous
# get_token the driver calls. Resource tokens are still rejected at construction
# (the driver has no resource-token auth branch yet) so that unsupported shape
# fails loudly up front.


class _SyncTokenCredential:
    """A minimal stand-in for a synchronous azure-identity credential."""

    def get_token(self, *scopes, **kwargs):  # noqa: D401
        return ("token-value", 9999999999)


class _AsyncTokenCredential:
    """A stand-in for an async credential, which the Rust backend wraps in a
    synchronous bridge."""

    async def get_token(self, *scopes, **kwargs):  # noqa: D401
        return ("token-value", 9999999999)


class _AsyncTokenInfoCredential:
    """An async credential that authenticates only through the newer
    ``get_token_info`` (azure-core ``SupportsTokenInfo``), with no ``get_token``.
    The Rust backend detects it as async and wraps it; the bridge drives
    ``get_token_info``."""

    async def get_token_info(self, *scopes, **kwargs):  # noqa: D401
        return ("token-value", 9999999999)


class _AsyncContextManagerCredential:
    """An ``azure.identity.aio``-shaped credential: an async context manager whose
    token method is async. Detected as async via the context-manager check."""

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return None

    async def get_token(self, *scopes, **kwargs):  # noqa: D401
        return ("token-value", 9999999999)


def test_resolve_credential_master_key_string():
    assert _resolve_credential("the-key") == ("the-key", None)


def test_resolve_credential_master_key_dict():
    assert _resolve_credential({"masterKey": "the-key"}) == ("the-key", None)


def test_resolve_credential_sync_token_credential():
    cred = _SyncTokenCredential()
    master_key, token_credential = _resolve_credential(cred)
    assert master_key is None
    assert token_credential is cred


def test_resolve_credential_async_token_credential_wrapped():
    """An async credential is no longer rejected: it is wrapped in a bridge that
    drives its coroutine and exposes a synchronous get_token."""
    cred = _AsyncTokenCredential()
    master_key, token_credential = _resolve_credential(cred)
    assert master_key is None
    assert isinstance(token_credential, AsyncTokenCredentialBridge)
    try:
        # The bridge runs the coroutine on its own loop thread and returns the
        # result synchronously -- exactly what the driver's sync get_token needs.
        assert token_credential.get_token("https://cosmos.azure.com/.default") == (
            "token-value",
            9999999999,
        )
    finally:
        token_credential._close_cosmos_async_bridge()


def test_resolve_credential_async_get_token_info_only_wrapped():
    """An async credential exposing only get_token_info (no get_token) is wrapped
    too; the bridge drives get_token_info."""
    cred = _AsyncTokenInfoCredential()
    master_key, token_credential = _resolve_credential(cred)
    assert master_key is None
    assert isinstance(token_credential, AsyncTokenCredentialBridge)
    try:
        assert token_credential.get_token("https://cosmos.azure.com/.default") == (
            "token-value",
            9999999999,
        )
    finally:
        token_credential._close_cosmos_async_bridge()


def test_resolve_credential_async_context_manager_credential_wrapped():
    """The azure.identity.aio shape (async context manager + async get_token) is
    wrapped via the async detector."""
    cred = _AsyncContextManagerCredential()
    master_key, token_credential = _resolve_credential(cred)
    assert master_key is None
    assert isinstance(token_credential, AsyncTokenCredentialBridge)
    token_credential._close_cosmos_async_bridge()


def test_async_credential_bridge_close_is_idempotent():
    """Closing the bridge stops its loop thread and is safe to call more than
    once (and before it ever started a loop)."""
    bridge = AsyncTokenCredentialBridge(_AsyncTokenCredential())
    # Close before first use: no loop thread was started, still a no-op.
    bridge._close_cosmos_async_bridge()
    bridge = AsyncTokenCredentialBridge(_AsyncTokenCredential())
    assert bridge.get_token("scope") == ("token-value", 9999999999)
    bridge._close_cosmos_async_bridge()
    bridge._close_cosmos_async_bridge()  # second close is a no-op


class _HangingAsyncCredential:
    """An async credential whose get_token never returns until it is cancelled."""

    def __init__(self):
        self.started = threading.Event()

    async def get_token(self, *scopes, **kwargs):  # noqa: D401
        self.started.set()
        # Block until the bridge's loop is torn down and cancels this task.
        await asyncio.Event().wait()
        return ("never", 0)  # pragma: no cover - unreachable


def test_async_credential_bridge_close_unblocks_in_flight_get_token():
    """Closing the bridge while a get_token is waiting must release the caller,
    not hang it forever."""
    cred = _HangingAsyncCredential()
    bridge = AsyncTokenCredentialBridge(cred)
    result: list = []

    def _call():
        try:
            bridge.get_token("scope")
            result.append(("returned",))
        except Exception as exc:  # noqa: BLE001
            result.append(("error", type(exc).__name__, str(exc)))

    caller = threading.Thread(target=_call, name="fake-driver-worker")
    caller.start()
    # Wait until the credential coroutine is running on the loop.
    assert cred.started.wait(timeout=5), "credential coroutine never started"
    bridge._close_cosmos_async_bridge()
    caller.join(timeout=5)
    assert not caller.is_alive(), "get_token did not return after close (permanent hang)"
    assert result and result[0][0] == "error", f"expected an error, got {result}"
    # The error is a clear RuntimeError, not a bare cancellation.
    assert "closed" in result[0][2].lower()


def test_async_credential_bridge_token_timeout_bounds_the_wait():
    """A finite token_timeout caps the wait and raises TimeoutError instead of
    blocking forever on a hung credential."""

    cred = _HangingAsyncCredential()
    bridge = AsyncTokenCredentialBridge(cred, token_timeout=0.5)
    try:
        start = time.monotonic()
        with pytest.raises(concurrent.futures.TimeoutError):
            bridge.get_token("scope")
        assert time.monotonic() - start < 4, "token_timeout did not bound the wait"
    finally:
        bridge._close_cosmos_async_bridge()


def test_async_credential_bridge_rejects_call_from_loop_thread():
    """Calling get_token from the bridge's own background thread must raise instead of
    deadlocking."""
    cred = _AsyncTokenCredential()
    bridge = AsyncTokenCredentialBridge(cred)
    try:
        # Prime the background thread.
        assert bridge.get_token("scope") == ("token-value", 9999999999)
        outcome: list = []

        def _reenter():
            try:
                bridge.get_token("scope")
                outcome.append(("returned", None))
            except Exception as exc:  # noqa: BLE001
                outcome.append(("error", exc))

        # Schedule the re-entrant call on the bridge's own background thread.
        bridge._loop.call_soon_threadsafe(_reenter)
        # Give the background thread a moment to run the callback.
        for _ in range(50):
            if outcome:
                break
            time.sleep(0.05)
        assert outcome, "re-entrant call never ran"
        assert outcome[0][0] == "error"
        assert isinstance(outcome[0][1], AsyncCredentialBridgeReentrantError)
    finally:
        bridge._close_cosmos_async_bridge()


class _SlowAsyncCredential:
    """An async credential whose get_token takes a little time, so concurrent
    calls overlap with a close."""

    async def get_token(self, *scopes, **kwargs):  # noqa: D401
        await asyncio.sleep(0.01)
        return ("token-value", 9999999999)


def test_async_credential_bridge_dedups_same_credential_with_refcount():
    """The same async credential reused across clients yields one shared bridge,
    refcounted so only the last close tears the loop down."""
    cred = _AsyncTokenCredential()
    _, b1 = _resolve_credential(cred)
    _, b2 = _resolve_credential(cred)
    assert b1 is b2, "same credential should map to the same bridge"
    assert b1._refcount == 2
    try:
        assert b1.get_token("scope") == ("token-value", 9999999999)
        # First close: one holder remains, so the loop stays up and usable.
        b1._close_cosmos_async_bridge()
        assert b1._refcount == 1
        assert b1._loop is not None
        assert b1.get_token("scope") == ("token-value", 9999999999)
        # Last close: now the loop is torn down.
        b2._close_cosmos_async_bridge()
        assert b2._loop is None
        # A fresh acquire after teardown builds a new bridge, not the closed one.
        _, b3 = _resolve_credential(cred)
        assert b3 is not b1
        b3._close_cosmos_async_bridge()
    finally:
        # Defensive: ensure nothing is left registered if an assert fired early.
        b1._close_cosmos_async_bridge()


def test_async_credential_bridge_distinct_credentials_get_distinct_bridges():
    """Different credential objects must not share a bridge (or a driver)."""
    c1 = _AsyncTokenCredential()
    c2 = _AsyncTokenCredential()
    _, b1 = _resolve_credential(c1)
    _, b2 = _resolve_credential(c2)
    try:
        assert b1 is not b2
    finally:
        b1._close_cosmos_async_bridge()
        b2._close_cosmos_async_bridge()


def test_async_credential_bridge_concurrent_get_token_and_close_race():
    """Many threads calling get_token while another closes must all finish; calls
    after the close fail cleanly instead of hanging."""
    cred = _SlowAsyncCredential()
    bridge = AsyncTokenCredentialBridge(cred)
    stop = threading.Event()
    successes: list = []
    outcomes: list = []

    def worker():
        while not stop.is_set():
            try:
                bridge.get_token("scope")
                successes.append(1)
            except Exception as exc:  # noqa: BLE001
                outcomes.append(type(exc).__name__)
                return
        outcomes.append("stopped")

    threads = [threading.Thread(target=worker, name=f"driver-worker-{i}") for i in range(8)]
    for t in threads:
        t.start()
    # Let some calls succeed and several overlap before the close.
    time.sleep(0.2)
    bridge._close_cosmos_async_bridge()
    stop.set()
    for t in threads:
        t.join(timeout=5)
        assert not t.is_alive(), "a worker did not return after close (permanent hang)"
    assert successes, "no get_token completed before close"
    # Every worker recorded a clean outcome (a stop or a caught error), none hung.
    assert len(outcomes) == len(threads)


def test_async_credential_bridge_join_timeout_is_configurable(monkeypatch):
    """The loop-thread join timeout honors the env var, and a constructor arg wins."""
    monkeypatch.setenv("COSMOS_ASYNC_CREDENTIAL_CLOSE_TIMEOUT", "0.25")
    b = AsyncTokenCredentialBridge(_AsyncTokenCredential())
    assert b._join_timeout == 0.25
    b._close_cosmos_async_bridge()
    # Explicit constructor value overrides the env var.
    b2 = AsyncTokenCredentialBridge(_AsyncTokenCredential(), join_timeout=1.5)
    assert b2._join_timeout == 1.5
    b2._close_cosmos_async_bridge()
    # A bad env value falls back to the 5s default.
    monkeypatch.setenv("COSMOS_ASYNC_CREDENTIAL_CLOSE_TIMEOUT", "not-a-number")
    b3 = AsyncTokenCredentialBridge(_AsyncTokenCredential())
    assert b3._join_timeout == 5.0
    b3._close_cosmos_async_bridge()


def test_resolve_credential_sync_credential_not_false_positived():
    """A plain synchronous credential must NOT be misread as async by the broader
    detector -- it is accepted as a token credential."""
    cred = _SyncTokenCredential()
    master_key, token_credential = _resolve_credential(cred)
    assert master_key is None
    assert token_credential is cred


def test_resolve_credential_resource_token_map_rejected_with_specific_message():
    """A {resource-link: token} map (per-user scoped tokens) is rejected with the
    resource-token message, not the generic one."""
    with pytest.raises(ValueError, match="resource-token"):
        _resolve_credential({"dbs/x/colls/y": "resource-token"})


def test_resolve_credential_permission_feed_rejected_with_specific_message():
    """A permission feed (iterable of permission mappings) is rejected as a
    resource-token credential."""
    with pytest.raises(ValueError, match="resource-token"):
        _resolve_credential([{"id": "perm", "_token": "t", "resource": "dbs/x"}])


def test_resolve_credential_none_rejected():
    with pytest.raises(ValueError, match="master-key credential"):
        _resolve_credential(None)


def test_make_backend_carries_sync_token_credential(monkeypatch):
    """A sync token credential lands on the backend as token_credential, with no
    master key."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    cred = _SyncTokenCredential()
    backend = make_backend(
        BACKEND_NAME_RUST,
        url="https://x.documents.azure.com",
        credential=cred,
    )
    assert isinstance(backend, RustBackend)
    assert backend._master_key is None
    assert backend._token_credential is cred


def test_async_make_backend_carries_sync_token_credential(monkeypatch):
    """The async factory carries a sync token credential the same way."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    cred = _SyncTokenCredential()
    backend = make_async_backend(
        BACKEND_NAME_RUST,
        url="https://x.documents.azure.com",
        credential=cred,
    )
    assert isinstance(backend, AsyncRustBackend)
    assert backend._master_key is None
    assert backend._token_credential is cred


def test_make_backend_wraps_async_token_credential(monkeypatch):
    """An async credential lands on the sync backend wrapped in a bridge, with no
    master key -- so an async credential now builds a working Rust client."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    cred = _AsyncTokenCredential()
    backend = make_backend(
        BACKEND_NAME_RUST,
        url="https://x.documents.azure.com",
        credential=cred,
    )
    assert isinstance(backend, RustBackend)
    assert backend._master_key is None
    assert isinstance(backend._token_credential, AsyncTokenCredentialBridge)


def test_async_make_backend_wraps_async_token_credential(monkeypatch):
    """The async factory wraps an async credential the same way."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    cred = _AsyncTokenCredential()
    backend = make_async_backend(
        BACKEND_NAME_RUST,
        url="https://x.documents.azure.com",
        credential=cred,
    )
    assert isinstance(backend, AsyncRustBackend)
    assert backend._master_key is None
    assert isinstance(backend._token_credential, AsyncTokenCredentialBridge)


def test_rust_backend_passes_token_credential_to_init_client(monkeypatch):
    """With a token credential, init_client is called as (endpoint, None, config,
    credential) -- master key None, credential as the 4th argument."""
    fake_module = MagicMock()
    fake_module.init_client.return_value = "handle-1"
    monkeypatch.setattr("azure.cosmos._backend.rust._rust_module", fake_module)

    cred = _SyncTokenCredential()
    backend = RustBackend(
        endpoint="https://x.documents.azure.com",
        token_credential=cred,
    )
    backend._ensure_handle()

    fake_module.init_client.assert_called_once_with(
        "https://x.documents.azure.com", None, None, cred
    )


def test_async_rust_backend_passes_token_credential_to_init_client(monkeypatch):
    """Async version: the token credential rides as the 4th init_client arg."""
    fake_module = MagicMock()
    fake_module.init_client.return_value = "handle-1"
    monkeypatch.setattr("azure.cosmos.aio._backend.rust._rust_module", fake_module)

    cred = _SyncTokenCredential()

    async def _run():
        backend = AsyncRustBackend(
            endpoint="https://x.documents.azure.com",
            token_credential=cred,
        )
        await backend._ensure_handle()

    asyncio.run(_run())

    fake_module.init_client.assert_called_once_with(
        "https://x.documents.azure.com", None, None, cred
    )


# ---------------------------------------------------------------------------
# How a container call picks its backend
# ---------------------------------------------------------------------------
#
# The client puts a Rust backend on the connection only when Rust was chosen;
# otherwise there is none. A container call uses the Rust backend if it is set
# and the existing client otherwise. The choice is made once per client.

def _make_sync_container_with_backends(rust_backend, core_python_backend):
    """Build a container without running its constructor (which would open a
    network connection).

    Pass ``rust_backend=None`` for a client with no backend; pass a Rust
    backend for a Rust client. ``core_python_backend`` is kept for older test
    signatures and is always ``None``.
    """
    mock_cc = MagicMock()
    mock_cc._backend = rust_backend
    mock_cc._core_python_backend = core_python_backend
    container = ContainerProxy.__new__(ContainerProxy)
    container.client_connection = mock_cc
    container.id = "test"
    container.database_link = "dbs/test"
    container.container_link = "dbs/test/colls/test"
    return container


def _new_rust_backend():
    """Build a Rust backend with a throwaway endpoint and key. The tests fake
    the compiled module so nothing real runs."""
    return RustBackend(endpoint="https://x.documents.azure.com", master_key="k")


def _new_async_rust_backend():
    return AsyncRustBackend(endpoint="https://x.documents.azure.com", master_key="k")


def test_container_dispatch_routes_to_rust_backend(monkeypatch):
    """A call on a Rust client reaches the Rust backend, shown by the faked
    module being called."""
    fake_module = MagicMock()
    fake_module.init_client.return_value = "h"
    fake_module.create_item.return_value = (201, 0, {}, b"{}")
    monkeypatch.setattr("azure.cosmos._backend.rust._rust_module", fake_module)

    container = _make_sync_container_with_backends(_new_rust_backend(), None)
    try:
        container.create_item(body={"id": "x", "pk": "a"})
    except Exception:
        # The call may fail later (the fake connection is missing things);
        # we only check that the Rust module was reached.
        pass
    assert fake_module.create_item.called, "Rust path should have been taken"


def test_container_dispatch_skipped_when_backend_attrs_absent():
    """A container built over a connection with no backend set at all skips
    the backend and does not fail."""
    bare_cc = MagicMock(spec=[])  # a connection with no backend set at all
    container = ContainerProxy.__new__(ContainerProxy)
    container.client_connection = bare_cc
    container.id = "test"
    container.database_link = "dbs/test"
    container.container_link = "dbs/test/colls/test"
    try:
        container.create_item(body={"id": "x", "pk": "a"})
    except NotImplementedError:
        pytest.fail("dispatch should have been skipped on a bare client_connection")
    except Exception:
        pass


def test_async_container_dispatch_routes_to_async_rust_backend(monkeypatch):
    """Async version: a call on a Rust client reaches the Rust backend."""
    fake_module = MagicMock()
    fake_module.init_client.return_value = "h"
    fake_module.create_item_async = AsyncMock(return_value=(201, 0, {}, b"{}"))
    monkeypatch.setattr("azure.cosmos.aio._backend.rust._rust_module", fake_module)

    mock_cc = MagicMock()
    mock_cc._backend = _new_async_rust_backend()
    mock_cc._core_python_backend = None
    container = AsyncContainerProxy.__new__(AsyncContainerProxy)
    container.client_connection = mock_cc
    container.id = "test"
    container.database_link = "dbs/test"
    container.container_link = "dbs/test/colls/test"

    async def _run():
        try:
            await container.create_item(body={"id": "x", "pk": "a"})
        except Exception:
            pass
        assert fake_module.create_item_async.called, "async Rust path should have been taken"

    asyncio.run(_run())


# ---------------------------------------------------------------------------
# How pick_backend selects the backend off a client_connection
# ---------------------------------------------------------------------------
#
# pick_backend reads the ``_backend`` attribute off the connection. It reads
# the instance ``__dict__`` directly so a connection with the attribute unset
# yields ``None`` (the legacy-path signal) instead of a truthy auto-created
# attribute; a connection without ``__dict__`` (``__slots__``) is read via
# getattr.


class _PlainConnection:
    """A stand-in for client_connection with a real instance ``__dict__``."""


class _SlotsConnection:
    """A connection whose attributes live in ``__slots__`` (no ``__dict__``),
    exercising pick_backend's getattr fallback branch."""

    __slots__ = ("_backend",)


def test_pick_backend_returns_backend_when_set():
    """With ``_backend`` set, it is returned."""
    conn = _PlainConnection()
    backend = object()
    conn._backend = backend
    assert pick_backend(conn) is backend


def test_pick_backend_returns_none_when_backend_is_none():
    """An explicit ``_backend = None`` (core-python) yields ``None``."""
    conn = _PlainConnection()
    conn._backend = None
    assert pick_backend(conn) is None


def test_pick_backend_returns_none_when_unset():
    """No ``_backend`` attribute at all -> ``None`` (use the legacy path)."""
    assert pick_backend(_PlainConnection()) is None


def test_pick_backend_uses_getattr_fallback_for_slots_connection():
    """A connection without ``__dict__`` (``__slots__``) is read via getattr."""
    conn = _SlotsConnection()
    backend = object()
    conn._backend = backend
    assert pick_backend(conn) is backend


# ---------------------------------------------------------------------------
# The client handle is built only once, even under concurrency
# ---------------------------------------------------------------------------
#
# The first call builds the handle; a lock makes sure that a burst of first
# calls builds it only once, instead of each building and discarding one.
# Without the lock these tests would see eight builds.


def test_rust_backend_init_handle_serialised_under_concurrent_threads(monkeypatch):
    """Eight threads starting at once build the handle only once."""
    count_lock = threading.Lock()
    calls = {"n": 0}

    def slow_init(_endpoint, _key, _config):
        with count_lock:
            calls["n"] += 1
        time.sleep(0.02)  # hold long enough for the others to queue up
        return "handle-1"

    fake_module = MagicMock()
    fake_module.init_client.side_effect = slow_init
    monkeypatch.setattr("azure.cosmos._backend.rust._rust_module", fake_module)

    backend = RustBackend(endpoint="https://x.documents.azure.com", master_key="k")
    ready = threading.Barrier(8)
    results = []

    def worker():
        ready.wait()  # start all eight at the same time
        results.append(backend._ensure_handle())

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert calls["n"] == 1
    assert results == ["handle-1"] * 8


def test_async_rust_backend_init_handle_serialised_under_concurrent_tasks(monkeypatch):
    """Eight coroutines starting at once build the handle only once."""
    count_lock = threading.Lock()
    calls = {"n": 0}

    def slow_init(_endpoint, _key, _config):
        with count_lock:
            calls["n"] += 1
        time.sleep(0.02)
        return "handle-1"

    fake_module = MagicMock()
    fake_module.init_client.side_effect = slow_init
    monkeypatch.setattr("azure.cosmos.aio._backend.rust._rust_module", fake_module)

    async def _run():
        backend = AsyncRustBackend(
            endpoint="https://x.documents.azure.com", master_key="k"
        )
        return await asyncio.gather(*[backend._ensure_handle() for _ in range(8)])

    results = asyncio.run(_run())

    assert calls["n"] == 1
    assert results == ["handle-1"] * 8


def test_async_rust_backend_init_handle_serialised_across_event_loops(monkeypatch):
    """Two loops on different threads still build the handle only once."""
    count_lock = threading.Lock()
    calls = {"n": 0}

    def slow_init(_endpoint, _key, _config):
        with count_lock:
            calls["n"] += 1
        time.sleep(0.02)
        return "handle-1"

    fake_module = MagicMock()
    fake_module.init_client.side_effect = slow_init
    monkeypatch.setattr("azure.cosmos.aio._backend.rust._rust_module", fake_module)

    backend = AsyncRustBackend(endpoint="https://x.documents.azure.com", master_key="k")
    ready = threading.Barrier(2)
    results = []

    def worker():
        ready.wait()

        async def _run():
            return await backend._ensure_handle()

        results.append(asyncio.run(_run()))

    threads = [threading.Thread(target=worker) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert calls["n"] == 1
    assert results == ["handle-1", "handle-1"]


def test_rust_backend_close_releases_handle_once(monkeypatch):
    """close() removes a built handle once and is idempotent."""
    fake_module = MagicMock()
    fake_module.init_client.return_value = "handle-1"
    monkeypatch.setattr("azure.cosmos._backend.rust._rust_module", fake_module)

    backend = RustBackend(endpoint="https://x.documents.azure.com", master_key="k")
    backend._ensure_handle()
    backend.close()
    backend.close()

    fake_module.close_client.assert_called_once_with("handle-1")


def test_async_rust_backend_close_releases_handle_once(monkeypatch):
    """Async close() removes a built handle once and is idempotent."""
    fake_module = MagicMock()
    fake_module.init_client.return_value = "handle-1"
    monkeypatch.setattr("azure.cosmos.aio._backend.rust._rust_module", fake_module)

    async def _run():
        backend = AsyncRustBackend(endpoint="https://x.documents.azure.com", master_key="k")
        await backend._ensure_handle()
        await backend.close()
        await backend.close()

    asyncio.run(_run())

    fake_module.close_client.assert_called_once_with("handle-1")


# ---------------------------------------------------------------------------
# Transport / TLS knobs the Rust path can't honor fail loud at construction
# ---------------------------------------------------------------------------
#
# The Rust driver owns its own HTTP/TLS stack and has no hook for explicit proxy
# objects, a custom CA, a client certificate, or a stand-in transport. Rather
# than silently ignoring these (and failing later with opaque connection/cert
# errors far from the call site), the factory rejects them at construction with
# a clear message naming the setting. core-python is unaffected -- it still
# honors them.

_M15_URL = "https://x.documents.azure.com"


@pytest.mark.parametrize(
    "setting,value",
    [
        ("proxy_config", object()),
        ("proxies", {"https": "http://proxy:8080"}),
        ("connection_cert", "/etc/ssl/client.pem"),
        ("ssl_config", object()),
        ("transport", object()),
        ("connection_verify", False),
        ("connection_verify", "/etc/ssl/corp-ca.pem"),
    ],
)
def test_make_backend_rejects_unsupported_transport_settings_on_rust(monkeypatch, setting, value):
    """Each transport/TLS knob the Rust path can't honor is rejected at
    construction, naming the setting."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    with pytest.raises(ValueError, match=setting):
        make_backend(BACKEND_NAME_RUST, url=_M15_URL, credential="k", **{setting: value})


def test_make_backend_connection_verify_true_or_none_does_not_trip(monkeypatch):
    """Ordinary TLS verification (the default) must NOT trip the gate -- only a
    disable (False) or a custom CA path (str) is unsupported."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    assert isinstance(
        make_backend(BACKEND_NAME_RUST, url=_M15_URL, credential="k", connection_verify=True),
        RustBackend,
    )
    assert isinstance(
        make_backend(BACKEND_NAME_RUST, url=_M15_URL, credential="k", connection_verify=None),
        RustBackend,
    )


def test_reject_unsupported_transport_settings_no_op_when_unset():
    """Nothing set (and an empty proxies dict = 'no proxy') does not raise."""
    reject_unsupported_transport_settings()
    reject_unsupported_transport_settings(proxies={})


def test_make_backend_core_python_ignores_transport_settings(monkeypatch):
    """core-python honors these settings as before; the factory returns None and
    never raises for them, even when several are set."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    assert (
        make_backend(
            None,
            url=_M15_URL,
            credential="k",
            transport=object(),
            proxies={"https": "http://proxy:8080"},
            connection_verify=False,
        )
        is None
    )


def test_make_async_backend_rejects_transport_on_rust(monkeypatch):
    """The async factory rejects the same unsupported settings the same way."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    with pytest.raises(ValueError, match="transport"):
        make_async_backend(BACKEND_NAME_RUST, url=_M15_URL, credential="k", transport=object())


def test_make_async_backend_rejects_connection_cert_on_rust(monkeypatch):
    """Async twin: a client certificate is rejected at construction."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    with pytest.raises(ValueError, match="connection_cert"):
        make_async_backend(
            BACKEND_NAME_RUST, url=_M15_URL, credential="k", connection_cert="/etc/ssl/c.pem"
        )


# ---------------------------------------------------------------------------
# Per-account engine isolation: default silent-isolate vs. opt-in strict raise
# ---------------------------------------------------------------------------
#
# The Rust binding keys its driver cache by (endpoint, credential, config), so a
# second client to one account with a *different* config gets its own engine that
# honors its settings -- nothing is silently dropped. By default that isolation is
# silent (no warning). Strict isolation mode (opt-in) instead *raises*
# StrictEngineIsolationError when a later client's config differs from the first
# live client's, making the fragmentation loud and early. Each test uses a unique
# endpoint so a client finalized late in another test can't disturb its count (the
# _isolate_driver_registry autouse fixture also resets state).


def _rust_backend(url, config=None, strict=False):
    return RustBackend(
        endpoint=url, master_key="k", client_config=config, strict_isolation=strict
    )


def test_second_client_different_config_default_isolates_silently(recwarn):
    """Default mode: a second client with a different config is built fine (its own
    isolated engine) and emits no warning -- the silent-isolation behavior."""
    url = "https://m16-different.documents.azure.com"
    first = _rust_backend(url, PreparedClientConfig(preferred_locations=("West US",)))
    second = _rust_backend(url, PreparedClientConfig(preferred_locations=("East US",)))
    assert first is not None and second is not None
    # No warning of any kind is emitted -- isolation is silent now.
    assert len(recwarn) == 0


def test_second_client_different_config_strict_raises():
    """Strict mode: a second client whose config differs from the first live
    client's raises StrictEngineIsolationError at construction."""
    url = "https://m16-strict-different.documents.azure.com"
    first = _rust_backend(
        url, PreparedClientConfig(preferred_locations=("West US",)), strict=True
    )
    with pytest.raises(StrictEngineIsolationError):
        _rust_backend(
            url, PreparedClientConfig(preferred_locations=("East US",)), strict=True
        )
    assert first is not None
    # The failed client must not have counted itself against the endpoint.
    assert _driver_registry._live_client_count(url) == 1


def test_strict_same_config_does_not_raise():
    """Strict mode: a second client with the *same* config shares the engine and
    does not raise (separate-but-equal configs compare equal by value)."""
    url = "https://m16-strict-same.documents.azure.com"
    first = _rust_backend(
        url, PreparedClientConfig(preferred_locations=("West US",)), strict=True
    )
    second = _rust_backend(
        url, PreparedClientConfig(preferred_locations=("West US",)), strict=True
    )
    assert first is not None and second is not None
    assert _driver_registry._live_client_count(url) == 2


def test_strict_two_untuned_clients_do_not_raise():
    """Strict mode: two untuned (None) clients to one account match and don't raise."""
    url = "https://m16-strict-untuned.documents.azure.com"
    first = _rust_backend(url, None, strict=True)
    second = _rust_backend(url, None, strict=True)
    assert first is not None and second is not None


def test_strict_different_endpoints_do_not_raise():
    """Strict mode: different endpoints never conflict, whatever their configs."""
    a = _rust_backend(
        "https://m16-strict-a.documents.azure.com",
        PreparedClientConfig(preferred_locations=("West US",)),
        strict=True,
    )
    b = _rust_backend(
        "https://m16-strict-b.documents.azure.com",
        PreparedClientConfig(preferred_locations=("East US",)),
        strict=True,
    )
    assert a is not None and b is not None


def test_strict_releases_on_close_then_new_config_ok():
    """After the first client closes, the endpoint is forgotten, so a new client
    with a different config starts fresh and does not raise even in strict mode."""
    url = "https://m16-strict-release.documents.azure.com"
    first = _rust_backend(
        url, PreparedClientConfig(preferred_locations=("West US",)), strict=True
    )
    first.close()
    # Fresh "first" for the endpoint now -- no conflict.
    second = _rust_backend(
        url, PreparedClientConfig(preferred_locations=("East US",)), strict=True
    )
    assert second is not None


def test_backend_close_releases_registration_once():
    """close() releases the endpoint registration exactly once; a double close
    doesn't over-decrement, so another client to the same account stays counted."""
    url = "https://m16-refcount.documents.azure.com"
    first = _rust_backend(url, None)
    second = _rust_backend(url, None)
    assert _driver_registry._live_client_count(url) == 2
    first.close()
    first.close()  # idempotent -- _config_released guards the second release
    assert _driver_registry._live_client_count(url) == 1
    second.close()
    assert url not in _driver_registry._REGISTRY


def test_registry_register_release_refcount():
    """The registry itself: register increments, release drops, the entry is
    removed at zero, and an extra release is a harmless no-op."""
    url = "https://m16-registry.documents.azure.com"
    cfg = PreparedClientConfig(preferred_locations=("West US",))
    register_client_config(url, cfg)
    register_client_config(url, cfg)  # same engine -> no conflict, count 2
    assert _driver_registry._live_client_count(url) == 2
    release_client_config(url, cfg)
    assert _driver_registry._live_client_count(url) == 1
    release_client_config(url, cfg)
    assert url not in _driver_registry._REGISTRY
    release_client_config(url, cfg)  # extra release: no-op, no underflow
    assert url not in _driver_registry._REGISTRY


def test_registry_strict_raise_does_not_increment_count():
    """A strict-mode conflict raises *without* recording, so the failed client never
    counts against the endpoint and the existing client's count stays correct."""
    url = "https://m16-strict-count.documents.azure.com"
    cfg_a = PreparedClientConfig(preferred_locations=("West US",))
    cfg_b = PreparedClientConfig(preferred_locations=("East US",))
    register_client_config(url, cfg_a)
    assert _driver_registry._live_client_count(url) == 1
    with pytest.raises(StrictEngineIsolationError):
        register_client_config(url, cfg_b, strict=True)
    # Count unchanged -- the failed registration did not enter the count.
    assert _driver_registry._live_client_count(url) == 1


# ---------------------------------------------------------------------------
# Engine-identity guard: the registry mirrors the binding's (endpoint, credential,
# config) cache key, so the strict check tracks the *set of live engines* per account
# -- not just the first client's config. These cover the three axes that set fixed:
# stale baseline, the credential axis, and endpoint canonicalization.
# ---------------------------------------------------------------------------


class _Cred:
    """A stand-in token credential -- keyed by object identity, like azure-identity
    credentials are. Two instances are two identities."""


def test_strict_credential_axis_different_credentials_raise():
    """Same endpoint and config but a *different* credential would build a second
    engine (the binding keys on credential too), so strict mode must raise."""
    url = "https://m16-cred-axis.documents.azure.com"
    cfg = PreparedClientConfig(preferred_locations=("West US",))
    cred_a, cred_b = _Cred(), _Cred()
    register_client_config(
        url, cfg, credential_key=make_credential_key(None, cred_a), strict=True
    )
    with pytest.raises(StrictEngineIsolationError):
        register_client_config(
            url, cfg, credential_key=make_credential_key(None, cred_b), strict=True
        )
    # Only the first engine is recorded.
    assert _driver_registry._live_client_count(url) == 1


def test_strict_same_credential_and_config_shares():
    """Same endpoint, credential, and config -> one engine, shared, no raise."""
    url = "https://m16-cred-same.documents.azure.com"
    cfg = PreparedClientConfig(preferred_locations=("West US",))
    cred = _Cred()
    key = make_credential_key(None, cred)
    register_client_config(url, cfg, credential_key=key, strict=True)
    register_client_config(url, cfg, credential_key=key, strict=True)
    assert _driver_registry._live_client_count(url) == 2


def test_strict_baseline_not_stale_after_first_engine_closes():
    """Finding 1: the baseline must track live engines, not the first registrant.
    With engines X and Y both live (default mode), closing X must not leave a later
    strict client compared against the gone X -- a client matching Y is fine, and only
    one matching neither raises."""
    url = "https://m16-stale-baseline.documents.azure.com"
    cfg_x = PreparedClientConfig(preferred_locations=("West US",))
    cfg_y = PreparedClientConfig(preferred_locations=("East US",))
    register_client_config(url, cfg_x)  # engine X
    register_client_config(url, cfg_y)  # engine Y (default mode allows the second)
    release_client_config(url, cfg_x)   # X gone; only Y is live now
    # A strict client matching the still-live Y shares it -- no false positive.
    register_client_config(url, cfg_y, strict=True)
    assert _driver_registry._live_client_count(url) == 2
    # A strict client matching neither live engine (X is gone) correctly raises.
    cfg_z = PreparedClientConfig(preferred_locations=("Central US",))
    with pytest.raises(StrictEngineIsolationError):
        register_client_config(url, cfg_z, strict=True)


def test_endpoint_canonicalization_coalesces_url_variants():
    """Finding 3: trailing-slash and host-case variants of one account must share a
    bucket, so the strict guard is not bypassed by a cosmetic URL difference."""
    base = "https://M16-Canon.documents.azure.com"
    variant = "https://m16-canon.documents.azure.com/"
    cfg_a = PreparedClientConfig(preferred_locations=("West US",))
    cfg_b = PreparedClientConfig(preferred_locations=("East US",))
    register_client_config(base, cfg_a, strict=True)
    with pytest.raises(StrictEngineIsolationError):
        register_client_config(variant, cfg_b, strict=True)
    # Both spellings resolve to the same live count.
    assert _driver_registry._live_client_count(base) == 1
    assert _driver_registry._live_client_count(variant) == 1


def test_canonicalization_keeps_distinct_accounts_separate():
    """Canonicalization must never collapse genuinely different accounts."""
    a = "https://m16-acct-a.documents.azure.com"
    b = "https://m16-acct-b.documents.azure.com"
    cfg = PreparedClientConfig(preferred_locations=("West US",))
    register_client_config(a, cfg, strict=True)
    # Different account, even with a different config, never conflicts.
    register_client_config(b, PreparedClientConfig(preferred_locations=("East US",)), strict=True)
    assert _driver_registry._live_client_count(a) == 1
    assert _driver_registry._live_client_count(b) == 1


def test_make_credential_key_does_not_expose_master_key():
    """Secret hygiene: the master-key identity is a non-reversible fingerprint, not the
    plaintext, yet equal keys fingerprint equal and different keys do not."""
    secret = "super-secret-master-key=="
    key = make_credential_key(secret, None)
    assert secret not in str(key)
    assert key == make_credential_key(secret, None)
    assert key != make_credential_key("a-different-key", None)
    # A token credential keys by object identity, matching the binding's pointer.
    cred = _Cred()
    assert make_credential_key(None, cred) == id(cred)


def test_release_with_wrong_engine_is_noop():
    """Releasing an engine that was never registered must not corrupt the live count
    of the engine that *is* registered."""
    url = "https://m16-release-mismatch.documents.azure.com"
    cfg = PreparedClientConfig(preferred_locations=("West US",))
    register_client_config(url, cfg)
    # Release a different config (a different engine) -- harmless no-op.
    release_client_config(url, PreparedClientConfig(preferred_locations=("East US",)))
    assert _driver_registry._live_client_count(url) == 1
    release_client_config(url, cfg)
    assert url not in _driver_registry._REGISTRY


def test_async_second_client_different_config_strict_raises():
    url = "https://m16-async-strict-different.documents.azure.com"
    first = AsyncRustBackend(
        endpoint=url,
        master_key="k",
        client_config=PreparedClientConfig(preferred_locations=("West US",)),
        strict_isolation=True,
    )
    with pytest.raises(StrictEngineIsolationError):
        AsyncRustBackend(
            endpoint=url,
            master_key="k",
            client_config=PreparedClientConfig(preferred_locations=("East US",)),
            strict_isolation=True,
        )
    assert first is not None
    assert _driver_registry._live_client_count(url) == 1


def test_async_second_client_different_config_default_isolates(recwarn):
    url = "https://m16-async-default-different.documents.azure.com"
    first = AsyncRustBackend(
        endpoint=url,
        master_key="k",
        client_config=PreparedClientConfig(preferred_locations=("West US",)),
    )
    second = AsyncRustBackend(
        endpoint=url,
        master_key="k",
        client_config=PreparedClientConfig(preferred_locations=("East US",)),
    )
    assert first is not None and second is not None
    assert len(recwarn) == 0


# ---------------------------------------------------------------------------
# Strict-isolation toggle: factory resolution and end-to-end wiring
# ---------------------------------------------------------------------------


def test_resolve_strict_isolation_precedence(monkeypatch):
    """Explicit kwarg wins; otherwise the env var decides; unset/empty is off."""
    # Explicit True/False beats the env var.
    monkeypatch.setenv(RUST_STRICT_ISOLATION_ENV_VAR, "false")
    assert resolve_strict_isolation(True) is True
    monkeypatch.setenv(RUST_STRICT_ISOLATION_ENV_VAR, "true")
    assert resolve_strict_isolation(False) is False
    # No explicit value -> the env var decides, case- and whitespace-insensitively.
    for truthy in ("1", "true", "TRUE", "Yes", "on", "  on  ", "ON\n"):
        monkeypatch.setenv(RUST_STRICT_ISOLATION_ENV_VAR, truthy)
        assert resolve_strict_isolation(None) is True
    for falsy in ("0", "false", "FALSE", "no", "off", " off ", ""):
        monkeypatch.setenv(RUST_STRICT_ISOLATION_ENV_VAR, falsy)
        assert resolve_strict_isolation(None) is False
    # Unset -> off.
    monkeypatch.delenv(RUST_STRICT_ISOLATION_ENV_VAR, raising=False)
    assert resolve_strict_isolation(None) is False


def test_resolve_strict_isolation_rejects_unrecognized(monkeypatch):
    """A safety toggle is never silently disabled: an unrecognized value (a typo
    that clearly meant 'on') raises instead of quietly leaving the guard off."""
    for bad in ("treu", "enabled", "2", "yes please", "tru e"):
        monkeypatch.setenv(RUST_STRICT_ISOLATION_ENV_VAR, bad)
        with pytest.raises(ValueError, match="COSMOS_RUST_STRICT_ISOLATION"):
            resolve_strict_isolation(None)
    # An explicit kwarg still wins and never consults the (bad) env var.
    monkeypatch.setenv(RUST_STRICT_ISOLATION_ENV_VAR, "treu")
    assert resolve_strict_isolation(True) is True
    assert resolve_strict_isolation(False) is False


# ---------------------------------------------------------------------------
# Input-validation robustness: bad-typed inputs fail early and clearly at
# construction, rather than throwing the wrong exception, failing later in a
# murkier place, or (worst) silently producing wrong behavior.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("bad", [123, 1.5, True, ["rust"], {"name": "rust"}, object()])
def test_resolve_backend_name_non_string_raises_valueerror(monkeypatch, bad):
    """A non-string _backend= must raise a clear ValueError, not an opaque
    AttributeError from calling .strip() on a non-string."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    with pytest.raises(ValueError, match="Invalid backend"):
        resolve_backend_name(bad)


@pytest.mark.parametrize("bad", ["true", "false", "", 1, 0, [], object()])
def test_resolve_strict_isolation_rejects_non_bool_explicit(monkeypatch, bad):
    """The explicit strict_isolation value must be a real bool. A truthy non-bool
    like the string 'false' would otherwise silently turn the safety guard ON."""
    monkeypatch.delenv(RUST_STRICT_ISOLATION_ENV_VAR, raising=False)
    with pytest.raises(ValueError, match="strict_isolation must be a bool"):
        resolve_strict_isolation(bad)


@pytest.mark.parametrize("arg_name", ["preferred_locations", "excluded_locations"])
def test_build_client_config_rejects_bare_string_locations(arg_name):
    """A bare string region is rejected: tuple('West US') would silently become
    seven one-character 'regions', which is never what the customer meant."""
    with pytest.raises(ValueError, match="sequence of region-name strings"):
        build_client_config(**{arg_name: "West US"})


@pytest.mark.parametrize("arg_name", ["preferred_locations", "excluded_locations"])
def test_build_client_config_rejects_bytes_locations(arg_name):
    """Bytes are rejected for the same reason a bare string is."""
    with pytest.raises(ValueError, match="sequence of region-name strings"):
        build_client_config(**{arg_name: b"West US"})


def test_build_client_config_accepts_single_region_in_a_list():
    """The correct shape -- a one-element list -- carries exactly that one region,
    proving the guard does not over-reject real sequences."""
    config = build_client_config(["West US"])
    assert config == PreparedClientConfig(preferred_locations=("West US",))


@pytest.mark.parametrize("bad_master_key", [None, 123, b"key", {"k": "v"}, ""])
def test_resolve_credential_rejects_non_string_master_key_in_dict(bad_master_key):
    """A {'masterKey': <non-string or empty>} dict is rejected at construction with
    a clear message, instead of being accepted and failing later in a murkier
    place."""
    with pytest.raises(ValueError, match="'masterKey' entry to be a non-empty string"):
        _resolve_credential({"masterKey": bad_master_key})


def test_resolve_credential_rejects_empty_master_key_string():
    """An empty master-key string is rejected up front rather than accepted and
    failing later."""
    with pytest.raises(ValueError, match="non-empty master-key string"):
        _resolve_credential("")


def test_resolve_credential_iterable_non_sequence_gets_generic_message():
    """An unusual custom credential object that merely happens to be iterable (a
    generator, here) but is not a concrete sequence is NOT mislabeled a
    resource-token credential; it falls through to the generic message."""
    def _gen():
        yield {"id": "perm"}

    with pytest.raises(ValueError, match="requires a master-key credential"):
        _resolve_credential(_gen())


def test_resolve_backend_name_normalizes_case_and_whitespace(monkeypatch):
    """Case and surrounding whitespace are tolerated (env vars and copy-paste
    routinely add a trailing newline or odd case); the canonical name comes back."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    for variant in ("rust", "RUST", "Rust", " rust", "rust\n", "  rust  "):
        assert resolve_backend_name(variant) == BACKEND_NAME_RUST
    for variant in ("core-python", "CORE-PYTHON", " Core-Python "):
        assert resolve_backend_name(variant) == BACKEND_NAME_CORE_PYTHON
    # Same normalization on the env-var path.
    monkeypatch.setenv(BACKEND_ENV_VAR, "  RUST\n")
    assert resolve_backend_name(None) == BACKEND_NAME_RUST


def test_resolve_backend_name_empty_means_default(monkeypatch):
    """An empty or whitespace-only value counts as 'not specified' and uses the
    default rather than raising."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    assert resolve_backend_name(None) == BACKEND_NAME_CORE_PYTHON
    assert resolve_backend_name("") == BACKEND_NAME_CORE_PYTHON
    assert resolve_backend_name("   ") == BACKEND_NAME_CORE_PYTHON
    monkeypatch.setenv(BACKEND_ENV_VAR, "")
    assert resolve_backend_name(None) == BACKEND_NAME_CORE_PYTHON
    monkeypatch.setenv(BACKEND_ENV_VAR, "   ")
    assert resolve_backend_name(None) == BACKEND_NAME_CORE_PYTHON


def test_resolve_backend_name_still_rejects_genuine_typos(monkeypatch):
    """Normalization is only case/whitespace -- a real typo (and underscore
    spelling, which is not an alias) still fails loud."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    for bad in ("turbo", "rustt", "core_python", "python"):
        with pytest.raises(ValueError, match="Invalid backend"):
            resolve_backend_name(bad)


def test_make_backend_threads_strict_isolation_kwarg():
    """make_backend(strict_isolation=True) builds a strict backend: a second client
    with a different config to the same account raises at construction."""
    url = "https://m16-factory-strict.documents.azure.com"
    first = make_backend(
        BACKEND_NAME_RUST,
        url=url,
        credential="k",
        preferred_locations=["West US"],
        strict_isolation=True,
    )
    assert first is not None and first._strict_isolation is True
    with pytest.raises(StrictEngineIsolationError):
        make_backend(
            BACKEND_NAME_RUST,
            url=url,
            credential="k",
            preferred_locations=["East US"],
            strict_isolation=True,
        )


def test_make_backend_strict_isolation_defaults_off():
    """Without the toggle (and no env var), the backend is non-strict: a second
    differently-configured client is built fine (its own isolated engine)."""
    url = "https://m16-factory-default.documents.azure.com"
    first = make_backend(
        BACKEND_NAME_RUST, url=url, credential="k", preferred_locations=["West US"]
    )
    second = make_backend(
        BACKEND_NAME_RUST, url=url, credential="k", preferred_locations=["East US"]
    )
    assert first is not None and first._strict_isolation is False
    assert second is not None


def test_make_backend_strict_isolation_from_env(monkeypatch):
    """The COSMOS_RUST_STRICT_ISOLATION env var enables strict mode when no explicit
    kwarg is given."""
    monkeypatch.setenv(RUST_STRICT_ISOLATION_ENV_VAR, "true")
    url = "https://m16-factory-env-strict.documents.azure.com"
    first = make_backend(BACKEND_NAME_RUST, url=url, credential="k")
    assert first is not None and first._strict_isolation is True

# ---------------------------------------------------------------------------
# Response-less driver errors map to azure-core ServiceResponseError (A2)
# ---------------------------------------------------------------------------
#
# When a driver op fails *without* a wire response (transport failure,
# client-side validation, a pre-HTTP timeout), the binding raises a typed
# DriverTransportError (a RuntimeError subclass). The backends translate it into
# azure-core's ServiceResponseError so customer
# `except (ServiceRequestError, ServiceResponseError)` handlers and the SDK's
# transport-retry policies behave the same as on the legacy azure-core path,
# instead of seeing a bare RuntimeError.


def _transport_test_request():
    return PreparedRequest(
        op="read_item",
        container_link="dbs/d/colls/c",
        body_bytes=b"",
        partition_key_header='["a"]',
        headers={},
    )


def test_sync_backend_maps_transport_error_to_service_response_error(monkeypatch):
    """A DriverTransportError from the sync dispatch surfaces as ServiceResponseError,
    preserving the driver's status/message in the new exception."""
    from azure.core.exceptions import ServiceResponseError
    import azure.cosmos._backend.rust as rust_mod

    backend = RustBackend(endpoint="https://x.documents.azure.com", master_key="k")
    backend._handle = "handle"  # skip the (blocking) handle build
    monkeypatch.setattr(rust_mod, "_rust_module", object())  # pretend binding present

    transport_exc_type = rust_mod._DRIVER_TRANSPORT_ERROR
    message = "driver execute_singleton_operation failed: status 503 (ServiceUnavailable): boom"

    def boom(handle, prepared):
        raise transport_exc_type(message)

    monkeypatch.setattr(rust_mod, "_resolve_dispatch", lambda op: boom)

    with pytest.raises(ServiceResponseError) as excinfo:
        backend.execute(_transport_test_request())
    assert "ServiceUnavailable" in str(excinfo.value)
    assert isinstance(excinfo.value.__cause__, transport_exc_type)


def test_async_backend_maps_transport_error_to_service_response_error(monkeypatch):
    """The async backend performs the same translation on its await path."""
    from azure.core.exceptions import ServiceResponseError
    import azure.cosmos.aio._backend.rust as async_rust_mod

    backend = AsyncRustBackend(endpoint="https://x.documents.azure.com", master_key="k")
    backend._handle = "handle"  # skip the (background-thread) handle build
    monkeypatch.setattr(async_rust_mod, "_rust_module", object())

    transport_exc_type = async_rust_mod._DRIVER_TRANSPORT_ERROR
    message = "driver execute_singleton_operation failed: status 503 (ServiceUnavailable): boom"

    async def boom(handle, prepared):
        raise transport_exc_type(message)

    monkeypatch.setattr(async_rust_mod, "_resolve_async_dispatch", lambda op: boom)

    async def run():
        with pytest.raises(ServiceResponseError) as excinfo:
            await backend.execute(_transport_test_request())
        assert "ServiceUnavailable" in str(excinfo.value)
        assert isinstance(excinfo.value.__cause__, transport_exc_type)

    asyncio.run(run())
