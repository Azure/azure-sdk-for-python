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
     back to the default. The tests in this group pin every one of
     those rules down: default with nothing set, env var honored,
     kwarg overrides env var, both invalid-value paths.

  3. Container dispatch.
     The container's ``create_item`` reads the two type-named attributes
     on ``client_connection`` (``_rust_backend``, ``_core_python_backend``)
     and routes to the right one — including the forced-fallback
     behavior for ``availability_strategy`` and ``retry_write``. The
     dispatch site also stamps the chosen backend's name into
     ``**kwargs`` under ``REQUEST_OPTION_BACKEND_KEY`` so that
     ``CosmosUserAgentPolicy`` can append it to the User-Agent header.

  4. User-agent policy.
     Two small tests verify the policy reads the per-request stamp from
     ``request.context.options`` and writes ``backend=<name>`` into the
     final User-Agent header — and that the absence of a stamp produces
     no ``backend=`` token at all.
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
    REQUEST_OPTION_BACKEND_KEY,
)
from azure.cosmos._backend.core_python import CorePythonBackend
from azure.cosmos._backend.factory import make_backend
from azure.cosmos._backend.rust import RustBackend
from azure.cosmos.aio._backend.core_python import AsyncCorePythonBackend
from azure.cosmos.aio._backend.factory import make_async_backend
from azure.cosmos.aio._backend.rust import AsyncRustBackend


# ---------------------------------------------------------------------------
# Import-guard
# ---------------------------------------------------------------------------

_PKG_ROOT = Path(__file__).resolve().parents[1] / "azure" / "cosmos"

# Each entry maps a guarded name (the compiled PyO3 module, or a concrete
# backend class) to the set of package-relative file paths that are allowed
# to import it. Anything outside the allow-list fails the test.
_ALLOWED = {
    # The compiled PyO3 module is only allowed inside the Rust backend wrappers.
    "_azure_cosmos_pyo3": {
        Path("_backend") / "rust.py",
        Path("aio") / "_backend" / "rust.py",
    },
    # Concrete backend classes are imported by the factory (which constructs
    # them) and by the client (which holds them in two type-named attributes
    # — _core_python_backend and _rust_backend — and uses isinstance to
    # decide which slot the factory's return value belongs in).
    "CorePythonBackend": {
        Path("_backend") / "factory.py",
        Path("cosmos_client.py"),
    },
    "RustBackend": {
        Path("_backend") / "factory.py",
        Path("cosmos_client.py"),
    },
    "AsyncCorePythonBackend": {
        Path("aio") / "_backend" / "factory.py",
        Path("aio") / "_cosmos_client.py",
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


@pytest.mark.parametrize("guarded_name,allowed_files", list(_ALLOWED.items()))
def test_import_guard(guarded_name, allowed_files):
    """No module outside the allow-list may import the guarded name."""
    offenders = []
    name_re = re.compile(r"\b" + re.escape(guarded_name) + r"\b")
    for py in _iter_py_files():
        rel = py.relative_to(_PKG_ROOT)
        if rel in allowed_files:
            continue
        text = py.read_text(encoding="utf-8", errors="ignore")
        for line in _IMPORT_RE.findall(text):
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
# default. The tests below pin every one of those rules down.

def test_factory_default_is_core_python(monkeypatch):
    """With no kwarg and no env var, the factory must pick core-python."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    backend = make_backend(None)
    assert isinstance(backend, CorePythonBackend)
    assert backend.name == BACKEND_NAME_CORE_PYTHON


def test_factory_env_var_picks_rust(monkeypatch):
    """Setting the env var to ``rust`` must produce a RustBackend."""
    monkeypatch.setenv(BACKEND_ENV_VAR, BACKEND_NAME_RUST)
    backend = make_backend(None)
    assert isinstance(backend, RustBackend)
    assert backend.name == BACKEND_NAME_RUST


def test_factory_kwarg_overrides_env(monkeypatch):
    """An explicit kwarg always wins over the env var."""
    monkeypatch.setenv(BACKEND_ENV_VAR, BACKEND_NAME_RUST)
    backend = make_backend(BACKEND_NAME_CORE_PYTHON)
    assert isinstance(backend, CorePythonBackend)


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


def test_async_factory_returns_async_backends(monkeypatch):
    """The async factory must return the async backend classes."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    assert isinstance(make_async_backend(None), AsyncCorePythonBackend)
    assert isinstance(make_async_backend(BACKEND_NAME_RUST), AsyncRustBackend)


def test_async_factory_invalid_value_fails_loud(monkeypatch):
    """The async factory must enforce the same validation as the sync one."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    with pytest.raises(ValueError, match="Invalid backend"):
        make_async_backend("turbo")


# ---------------------------------------------------------------------------
# What each backend's create_item method does today
# ---------------------------------------------------------------------------
#
# The two concrete backends behave very differently right now and these
# tests pin both behaviors down so a future change cannot quietly flip
# either one:
#
#   - CorePythonBackend.create_item returns ``None``. That is how it
#     tells the container's dispatch site "I have nothing to return;
#     fall through to the existing in-place create_item code." Once
#     the helper layer takes over request prep and response parsing,
#     this will switch to returning a real ``BackendResponse``; until
#     then ``None`` is the contract.
#
#   - RustBackend.create_item raises ``NotImplementedError`` on every
#     call. That is the expected behavior for the dispatch-only slice:
#     a developer who runs the existing test suite with
#     ``COSMOS_BACKEND=rust`` should see every create_item test fail
#     loudly. Failing loud proves the dispatch wiring works
#     end-to-end and prevents anyone from accidentally shipping a
#     half-implemented Rust path that silently no-ops.
#
# Both behaviors are duplicated for the async siblings.
# ---------------------------------------------------------------------------

def test_rust_backend_create_item_raises():
    """Today, every Rust create_item call must raise loudly so that
    running the existing test suite with COSMOS_BACKEND=rust fails the
    create_item tests instead of silently passing."""
    with pytest.raises(NotImplementedError, match="not implemented yet"):
        RustBackend().create_item(prepared=None)


def test_async_rust_backend_create_item_raises():
    """Same loud-fail contract on the async side."""
    async def _run():
        with pytest.raises(NotImplementedError, match="not implemented yet"):
            await AsyncRustBackend().create_item(prepared=None)
    asyncio.run(_run())


def test_core_python_backend_create_item_returns_none():
    """Today, returning None is how core-python tells the dispatch site
    to fall through to the existing in-place create_item code."""
    assert CorePythonBackend().create_item(prepared=None) is None


def test_async_core_python_backend_create_item_returns_none():
    """Same fall-through contract on the async side."""
    async def _run():
        assert await AsyncCorePythonBackend().create_item(prepared=None) is None
    asyncio.run(_run())


def test_dataclasses_are_frozen():
    """Both PreparedRequest and BackendResponse are intentionally frozen so
    that backends cannot mutate their inputs or outputs by accident."""
    p = PreparedRequest(
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
#   - ``_core_python_backend`` is always present. It is the default and
#     the always-available fallback.
#   - ``_rust_backend`` is present only when the caller selected Rust
#     as the default for this client (via the ``_backend="rust"`` kwarg
#     or the ``COSMOS_BACKEND=rust`` env var). Otherwise it is ``None``.
#
# When a container's ``create_item`` runs, it reads both attributes and
# then asks two questions:
#
#   1. Is a Rust backend even attached to this client?
#   2. Does the call use a kwarg the Rust path cannot handle yet —
#      specifically ``availability_strategy`` (multi-region hedging)
#      or ``retry_write`` (non-idempotent write retries)?
#
# It picks Rust only if a Rust backend exists *and* neither of those
# two kwargs is set. Otherwise the call goes to the core-python
# backend. After it has decided, the dispatch site stamps the chosen
# backend's name into ``**kwargs`` under ``REQUEST_OPTION_BACKEND_KEY``
# so that ``CosmosUserAgentPolicy`` can append ``backend=<name>`` to
# the User-Agent header for that single request.
#
# The tests below cover: routing to Rust on a Rust-default client,
# the two forced-fallback paths (``availability_strategy`` and
# ``retry_write``), the safety net that lets a ``Container`` whose
# ``client_connection`` was built outside ``CosmosClient`` skip
# dispatch silently, and the same Rust-routing contract on the async
# container.
# ---------------------------------------------------------------------------

def _make_sync_container_with_backends(rust_backend, core_python_backend):
    """Build a sync Container without going through __init__ (which would
    open a network connection to a Cosmos account).

    Pass ``rust_backend=None`` to model a client whose default is
    core-python; pass a ``RustBackend`` instance to model a Rust-default
    client. ``core_python_backend`` is always present.
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


def test_container_dispatch_routes_to_rust_backend():
    """A Rust-default client with an unrestricted call must hit RustBackend."""
    container = _make_sync_container_with_backends(RustBackend(), CorePythonBackend())
    with pytest.raises(NotImplementedError, match="not implemented yet"):
        container.create_item(body={"id": "x", "pk": "a"})


def test_container_dispatch_falls_back_to_core_python_for_availability_strategy():
    """availability_strategy must force the core-python path on a
    Rust-default client. We assert only that NotImplementedError is not
    raised — any later failure is the core-python path tripping on the
    incomplete mock, which still confirms the dispatch decision."""
    container = _make_sync_container_with_backends(RustBackend(), CorePythonBackend())
    try:
        container.create_item(
            body={"id": "x", "pk": "a"},
            availability_strategy={"threshold_ms": 500},
        )
    except NotImplementedError:
        pytest.fail("availability_strategy should have forced the core-python path")
    except Exception:
        pass


def test_container_dispatch_falls_back_to_core_python_for_retry_write():
    """retry_write must force the core-python path for the same reason."""
    container = _make_sync_container_with_backends(RustBackend(), CorePythonBackend())
    try:
        container.create_item(body={"id": "x", "pk": "a"}, retry_write=3)
    except NotImplementedError:
        pytest.fail("retry_write should have forced the core-python path")
    except Exception:
        pass


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


def test_async_container_dispatch_routes_to_async_rust_backend():
    """Same Rust-routing contract on the async container."""
    from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy
    mock_cc = MagicMock()
    mock_cc._rust_backend = AsyncRustBackend()
    mock_cc._core_python_backend = AsyncCorePythonBackend()
    container = AsyncContainerProxy.__new__(AsyncContainerProxy)
    container.client_connection = mock_cc
    container.id = "test"
    container.database_link = "dbs/test"
    container.container_link = "dbs/test/colls/test"

    async def _run():
        with pytest.raises(NotImplementedError, match="not implemented yet"):
            await container.create_item(body={"id": "x", "pk": "a"})

    asyncio.run(_run())


# ---------------------------------------------------------------------------
# How the chosen backend's name reaches the User-Agent header
# ---------------------------------------------------------------------------
#
# ``CosmosUserAgentPolicy`` is the place where the per-request backend
# tag actually shows up on the wire. The policy reads a single key
# (``REQUEST_OPTION_BACKEND_KEY``, currently ``"cosmos_backend"``) out
# of the request's context options and, if it finds one, appends
# ``backend=<name>`` to the User-Agent header right before the request
# leaves the SDK.
#
# That key is written by the container's dispatch site — *after* it
# has resolved any forced fallback — so a request that fell back to
# core-python on a Rust-default client correctly reports
# ``backend=core-python`` server-side, not ``backend=rust``. Without
# this round-trip the server-side log would lie about which path
# actually ran.
#
# The tests below cover both halves of that round-trip independently:
# two tests prove the policy reacts correctly to the presence and
# absence of the stamp, and two more prove that the dispatch site
# always sets the stamp to the name of the backend that actually
# handled the call (including the forced-fallback case).
# ---------------------------------------------------------------------------

def _make_ua_policy_request(options):
    """Build a minimal request stand-in exposing ``context.options`` as a
    plain dict and ``http_request.headers`` as a plain dict.

    The real ``PipelineContext.options`` is built from constructor kwargs
    and not all azure-core versions let arbitrary keys round-trip; we
    only need the policy to see a mutable mapping on each side, so a
    MagicMock with two real dicts hung off it is the cleanest fixture.
    """
    request = MagicMock()
    request.context.options = dict(options)
    request.http_request.headers = {}
    return request


def test_user_agent_policy_appends_backend_suffix():
    """A per-request backend stamp must surface in the final User-Agent
    header as ``backend=<name>``."""
    from azure.cosmos._user_agent_policy import CosmosUserAgentPolicy
    policy = CosmosUserAgentPolicy(base_user_agent="azsdk-python-cosmos/4.x")
    request = _make_ua_policy_request({REQUEST_OPTION_BACKEND_KEY: BACKEND_NAME_RUST})
    policy.on_request(request)
    # The base UserAgentPolicy consumes ``user_agent`` from options and
    # writes the final value into the request's User-Agent header.
    ua = request.http_request.headers.get("User-Agent", "")
    assert "backend={}".format(BACKEND_NAME_RUST) in ua, (
        "expected backend={} in UA, got: {!r}".format(BACKEND_NAME_RUST, ua)
    )


def test_user_agent_policy_no_backend_suffix_when_unset():
    """Without a stamp, the UA must not carry a ``backend=`` token."""
    from azure.cosmos._user_agent_policy import CosmosUserAgentPolicy
    policy = CosmosUserAgentPolicy(base_user_agent="azsdk-python-cosmos/4.x")
    request = _make_ua_policy_request({})
    policy.on_request(request)
    ua = request.http_request.headers.get("User-Agent", "")
    assert "backend=" not in ua


def test_container_dispatch_stamps_backend_in_kwargs():
    """The dispatch site must inject the backend name into kwargs under
    REQUEST_OPTION_BACKEND_KEY so the user-agent policy can pick it up.
    Default client (no Rust backend) → stamps ``core-python``."""
    container = _make_sync_container_with_backends(None, CorePythonBackend())
    captured = {}

    def fake_create_item(**kwargs):
        captured.update(kwargs)
        return MagicMock()

    container.client_connection.CreateItem = fake_create_item
    # Avoid the container-properties cache lookup by short-circuiting it.
    container._get_properties_with_options = lambda _opts: None  # type: ignore[attr-defined]
    container._ContainerProxy__get_client_container_caches = lambda: {  # type: ignore[attr-defined]
        container.container_link: {"_rid": "rid"}
    }
    try:
        container.create_item(body={"id": "x", "pk": "a"})
    except Exception:
        pass
    assert captured.get(REQUEST_OPTION_BACKEND_KEY) == BACKEND_NAME_CORE_PYTHON


def test_container_dispatch_stamps_core_python_when_forced_fallback():
    """A Rust-default client that falls back must stamp ``core-python``
    so the server-side log reflects the path that actually ran."""
    container = _make_sync_container_with_backends(RustBackend(), CorePythonBackend())
    captured = {}

    def fake_create_item(**kwargs):
        captured.update(kwargs)
        return MagicMock()

    container.client_connection.CreateItem = fake_create_item
    container._get_properties_with_options = lambda _opts: None  # type: ignore[attr-defined]
    container._ContainerProxy__get_client_container_caches = lambda: {  # type: ignore[attr-defined]
        container.container_link: {"_rid": "rid"}
    }
    try:
        container.create_item(body={"id": "x", "pk": "a"}, retry_write=3)
    except Exception:
        pass
    assert captured.get(REQUEST_OPTION_BACKEND_KEY) == BACKEND_NAME_CORE_PYTHON

