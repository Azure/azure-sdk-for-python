# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Unit tests for the backend dispatch wiring.

These tests do not talk to a Cosmos account, an emulator, or the network.
Each one builds its inputs from plain Python objects and asserts on plain
Python return values. They run in roughly one second on a laptop and are
safe to run on every PR.

What they cover, grouped by responsibility:

  1. Import-guard.
     The compiled PyO3 module and the four concrete backend classes
     should only be imported by a small, named set of files. The first
     test walks every ``.py`` file under ``azure/cosmos/`` and fails the
     build if any other module imports one of those names. This catches,
     at PR-review time, anyone who reaches around the abstraction.

  2. Which backend the factory builds, and how it complains about
     bad input.
     The factory looks at three things in order — the constructor
     kwarg ``_backend=``, the ``COSMOS_BACKEND`` environment variable,
     and a hard-coded default of ``"core-python"`` — and returns
     whichever one wins. If the value it ends up with is not exactly
     ``"core-python"`` or ``"rust"``, it raises ``ValueError`` right
     there at client construction time so a typo cannot silently fall
     back to the default. The tests in this group cover every one of
     those rules down: default with nothing set, env var honored,
     kwarg overrides env var, both invalid-value paths.

  3. Container dispatch.
     The container's ``create_item`` reads the two type-named attributes
     on ``client_connection`` (``_rust_backend``, ``_core_python_backend``)
     and routes to whichever one is wired (Rust if present, core-python
     otherwise).
"""
from __future__ import annotations

import asyncio
import re
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
from azure.cosmos.aio._backend.factory import make_async_backend
from azure.cosmos.aio._backend.rust import AsyncRustBackend


# ---------------------------------------------------------------------------
# Import-guard
# ---------------------------------------------------------------------------

# This file lives at tests/common/, so we walk up two parents to reach the
# repo root, then descend into azure/cosmos/.
_PKG_ROOT = Path(__file__).resolve().parents[2] / "azure" / "cosmos"

# Each entry maps a guarded name (the compiled PyO3 module, or a concrete
# backend class) to the set of package-relative file paths that are allowed
# to import it. Anything outside the allow-list fails the test.
_ALLOWED = {
    # The compiled PyO3 module is only allowed inside the Rust backend wrappers.
    "_rust": {
        Path("_backend") / "rust.py",
        Path("aio") / "_backend" / "rust.py",
    },
    # The Rust backend class is imported by the factory (which constructs
    # it) and by the client (which holds it on a ``_rust_backend`` attribute
    # and uses isinstance to confirm what the factory returned).
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


# Walk every ``.py`` file under ``azure/cosmos/`` once at module load
# time and cache (relative-path, list-of-import-lines) tuples. The
# parametrised test below then scans the cache for each guarded name
# instead of re-reading every file five times. Same coverage, fifth
# the I/O.
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
    """No module outside the allow-list may import the guarded name."""
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
# Which backend the factory builds, and how it complains about bad input
# ---------------------------------------------------------------------------
#
# The factory consults three sources in order:
#   1. The constructor kwarg ``_backend=`` the caller passed.
#   2. The ``COSMOS_BACKEND`` environment variable.
#   3. The hard-coded default, ``"core-python"``.
#
# It returns whichever one wins, after checking that the value is exactly
# ``"core-python"`` or ``"rust"``. Any other value raises ``ValueError``
# at client construction time so a typo cannot silently fall back to the
# default. The tests below cover every one of those rules down.

def test_factory_default_returns_none(monkeypatch):
    """With no kwarg and no env var, the factory must pick core-python,
    which is now represented by ``None`` (no backend class wraps it)."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    backend = make_backend(None)
    assert backend is None


def test_factory_env_var_picks_rust(monkeypatch):
    """Setting the env var to ``rust`` must produce a RustBackend.

    The Rust backend needs an endpoint and a master-key credential at
    construction time, so those are passed in too — that's the same
    shape ``CosmosClient.__init__`` calls the factory with.
    """
    monkeypatch.setenv(BACKEND_ENV_VAR, BACKEND_NAME_RUST)
    backend = make_backend(None, url="https://x.documents.azure.com", credential="k")
    assert isinstance(backend, RustBackend)
    assert backend.name == BACKEND_NAME_RUST


def test_factory_kwarg_overrides_env(monkeypatch):
    """An explicit kwarg always wins over the env var."""
    monkeypatch.setenv(BACKEND_ENV_VAR, BACKEND_NAME_RUST)
    backend = make_backend(BACKEND_NAME_CORE_PYTHON)
    assert backend is None


def test_factory_invalid_value_fails_loud(monkeypatch):
    """An unknown kwarg value must raise at client construction time."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    with pytest.raises(ValueError, match="Invalid backend"):
        make_backend("turbo")


def test_factory_invalid_env_var_fails_loud(monkeypatch):
    """An unknown env var value must raise at client construction time."""
    monkeypatch.setenv(BACKEND_ENV_VAR, "turbo")
    with pytest.raises(ValueError, match="Invalid backend"):
        make_backend(None)


def test_factory_rust_without_master_key_fails_loud(monkeypatch):
    """Rust requires master-key auth today; any other credential shape
    must surface a clear ValueError at construction time rather than
    failing later on the first request."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    with pytest.raises(ValueError, match="master-key credential"):
        make_backend(BACKEND_NAME_RUST, url="https://x.documents.azure.com", credential=None)


def test_async_factory_returns_async_backends(monkeypatch):
    """The async factory must return ``None`` for the default selection
    and an ``AsyncRustBackend`` instance when Rust is asked for."""
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
    """The async factory must enforce the same validation as the sync one."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    with pytest.raises(ValueError, match="Invalid backend"):
        make_async_backend("turbo")


# ---------------------------------------------------------------------------
# What each backend's create_item method does today
# ---------------------------------------------------------------------------
#
# CorePythonBackend.create_item returns ``None``. That is how it tells
# the container's dispatch site "I have nothing to return; fall through
# to the existing in-place create_item code." Once the helper layer
# takes over request prep and response parsing, this will switch to
# returning a real ``BackendResponse``; until then ``None`` is the
# contract.
#
# RustBackend.create_item also returns ``None`` for ``prepared=None``
# (the same transitional contract — caller still owns request prep).
# When called with a real ``PreparedRequest`` it forwards into the
# compiled binding. The tests below mock the binding with a
# ``MagicMock`` so they exercise the dispatch path without needing a
# real Cosmos account.
#
# When the compiled binding is *not* present in the environment (a fresh
# clone before ``maturin develop`` ran), ``create_item`` raises
# ``NotImplementedError`` instead. That's covered by a separate test
# below using monkeypatch to clear the module-level reference.
#
# Both behaviors are duplicated for the async siblings.
# ---------------------------------------------------------------------------

def test_rust_backend_returns_none_for_no_prepared_request():
    """The transitional contract: no PreparedRequest means the caller
    still owns request prep, so the backend signals 'fall through' by
    returning None."""
    backend = RustBackend(endpoint="https://x.documents.azure.com", master_key="k")
    assert backend.execute(prepared=None) is None


def test_rust_backend_dispatches_to_binding(monkeypatch):
    """With a real PreparedRequest and a loaded binding, the backend
    must call the binding's create_item with the handle and prepared,
    and wrap the 4-tuple it returns as a BackendResponse."""
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


def test_rust_backend_raises_when_binding_not_built(monkeypatch):
    """A fresh checkout before ``maturin develop`` has no compiled
    binding. The backend must raise a clear NotImplementedError instead
    of failing later with a confusing AttributeError."""
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
    """Same transitional contract on the async side."""
    async def _run():
        backend = AsyncRustBackend(endpoint="https://x.documents.azure.com", master_key="k")
        assert await backend.execute(prepared=None) is None
    asyncio.run(_run())


def test_async_rust_backend_dispatches_to_binding(monkeypatch):
    """The async backend offloads the synchronous binding call to the
    default executor and wraps the result the same way the sync sibling
    does."""
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


def test_async_rust_backend_raises_when_binding_not_built(monkeypatch):
    """Fresh-checkout failure mode on the async side."""
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
    """When the chosen backend returns a real BackendResponse, the
    helper hands it to the response parser, which produces a CosmosDict
    customer code can index by key (``result["_etag"]``).

    This is the contract that lets a Rust round-trip return the same
    shape the legacy CreateItem path always returned. Without this
    wiring, a successful Rust call would surface a raw BackendResponse
    to customer code and ``result["_etag"]`` would raise TypeError.
    """
    from azure.cosmos._helpers.item_helper import ItemHelper

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

    # CosmosDict subclasses dict, so key lookup works the v4 way.
    assert result["_etag"] == '"00000000-0000-0000-1234-567890abcdef"'
    assert result["id"] == "order-42"


# NOTE: The historical ``test_core_python_backend_create_item_returns_none``
# test was removed. ``CorePythonBackend`` / ``AsyncCorePythonBackend`` no
# longer exist; the "fall through to legacy" signal is now the absence of
# any backend on the connection (``_rust_backend is None``), and the helper
# handles that directly. See the fall-through tests in
# ``test_item_helper_unit.py``.


def test_dataclasses_are_frozen():
    """Both PreparedRequest and BackendResponse are intentionally frozen so
    that backends cannot mutate their inputs or outputs by accident."""
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
# How Container.create_item picks which backend handles a single call
# ---------------------------------------------------------------------------
#
# The client construction code attaches two attributes onto
# ``client_connection``, named after the two backend types:
#
#   - ``_core_python_backend`` is always present. It is the default
#     and the always-available path.
#   - ``_rust_backend`` is present only when the caller selected Rust
#     as the default for this client (via the ``_backend="rust"``
#     kwarg or the ``COSMOS_BACKEND=rust`` env var). Otherwise it is
#     ``None``.
#
# When a container's ``create_item`` runs, it reads both attributes
# and picks Rust if it is wired, core-python otherwise. The decision
# is per-client (made once at construction), not per-call.
#
# The tests below cover: routing to Rust on a Rust-default client,
# the safety net that lets a ``Container`` whose ``client_connection``
# was built outside ``CosmosClient`` skip dispatch silently, and the
# same Rust-routing contract on the async container.
# ---------------------------------------------------------------------------

def _make_sync_container_with_backends(rust_backend, core_python_backend):
    """Build a sync Container without going through __init__ (which would
    open a network connection to a Cosmos account).

    Pass ``rust_backend=None`` to model a client whose default is
    core-python; pass a ``RustBackend`` instance to model a Rust-default
    client. ``core_python_backend`` is kept for historical test signatures
    — it is no longer a real class today, so callers pass ``None`` (the
    "no backend wired, fall through to legacy" signal).
    """
    from azure.cosmos.container import ContainerProxy
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
    """Build a RustBackend with throwaway endpoint+key. Tests below mock
    the binding so no real init_client / network call ever runs."""
    return RustBackend(endpoint="https://x.documents.azure.com", master_key="k")


def _new_async_rust_backend():
    return AsyncRustBackend(endpoint="https://x.documents.azure.com", master_key="k")


def test_container_dispatch_routes_to_rust_backend(monkeypatch):
    """A Rust-default client with an unrestricted call must hit the
    RustBackend's create_item — verified by checking the binding mock
    saw the call."""
    fake_module = MagicMock()
    fake_module.init_client.return_value = "h"
    fake_module.create_item.return_value = (201, 0, {}, b"{}")
    monkeypatch.setattr("azure.cosmos._backend.rust._rust_module", fake_module)

    container = _make_sync_container_with_backends(_new_rust_backend(), None)
    try:
        container.create_item(body={"id": "x", "pk": "a"})
    except Exception:
        # The dispatch may still raise downstream (mocked client_connection
        # is missing many things); we only care that the binding mock was
        # consulted, which proves the dispatch went to the Rust path.
        pass
    assert fake_module.create_item.called, "Rust path should have been taken"



def test_container_dispatch_skipped_when_backend_attrs_absent():
    """Some existing tests build a ContainerProxy directly with a mocked
    client_connection that has no backend attributes. The dispatch site
    must silently skip itself in that case so those tests keep passing."""
    from azure.cosmos.container import ContainerProxy
    bare_cc = MagicMock(spec=[])  # no _core_python_backend / _rust_backend at all
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
    """Same Rust-routing contract on the async container."""
    from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy
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

