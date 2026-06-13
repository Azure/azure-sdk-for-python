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
import re
import threading
import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from azure.cosmos._backend.base import BackendResponse, PreparedRequest
from azure.cosmos._backend.constants import (
    BACKEND_ENV_VAR,
    BACKEND_NAME_CORE_PYTHON,
    BACKEND_NAME_RUST,
)
from azure.cosmos._backend.factory import make_backend
from azure.cosmos._backend.rust import RustBackend
from azure.cosmos._helpers.item_helper import ItemHelper
from azure.cosmos.aio._backend.factory import make_async_backend
from azure.cosmos.aio._backend.rust import AsyncRustBackend
from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy
from azure.cosmos.container import ContainerProxy


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
        "https://x.documents.azure.com", "k"
    )
    fake_module.create_item.assert_called_once_with("handle-1", prepared)
    assert resp.status_code == 201
    assert resp.body == b'{"id":"x"}'


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
    """Async version: the backend runs the call on a worker thread and wraps
    the result the same way."""
    fake_module = MagicMock()
    fake_module.init_client.return_value = "handle-1"
    fake_module.create_item.return_value = (201, 0, {"etag": "v1"}, b'{"id":"x"}')
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
        fake_module.create_item.assert_called_once_with("handle-1", prepared)
        assert resp.status_code == 201
        assert resp.body == b'{"id":"x"}'
    asyncio.run(_run())


def test_async_rust_backend_returns_structured_http_failure_tuple(monkeypatch):
    """Async version: a failed request comes back as a normal response, not an
    error."""
    fake_module = MagicMock()
    fake_module.init_client.return_value = "handle-1"
    fake_module.create_item.return_value = (
        404,
        0,
        {"x-ms-activity-id": "act-404"},
        b'{"code":"NotFound","message":"missing"}',
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
    fake_module.create_item.side_effect = RuntimeError("driver execute_operation failed: TLS handshake failed")
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
    mock_cc._rust_backend = rust_backend
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
    fake_module.create_item.return_value = (201, 0, {}, b"{}")
    monkeypatch.setattr("azure.cosmos.aio._backend.rust._rust_module", fake_module)

    mock_cc = MagicMock()
    mock_cc._rust_backend = _new_async_rust_backend()
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
        assert fake_module.create_item.called, "async Rust path should have been taken"

    asyncio.run(_run())


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

    def slow_init(_endpoint, _key):
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

    def slow_init(_endpoint, _key):
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

