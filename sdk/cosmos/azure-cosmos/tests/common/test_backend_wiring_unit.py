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

from azure.cosmos._backend.base import BackendResponse, PreparedClientConfig, PreparedRequest
from azure.cosmos._backend.base import raise_account_read_unsupported
from azure.cosmos._backend.constants import (
    BACKEND_ENV_VAR,
    BACKEND_NAME_CORE_PYTHON,
    BACKEND_NAME_RUST,
)
from azure.cosmos._backend.factory import _resolve_credential, build_client_config, make_backend
from azure.cosmos._backend.rust import RustBackend
from azure.cosmos._helpers._item_dispatch import pick_backend
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
        "https://x.documents.azure.com", "k", None
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
        BACKEND_NAME_RUST, url="https://x.documents.azure.com", credential="k"
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
    )
    assert config == PreparedClientConfig(
        preferred_locations=("West US",),
        excluded_locations=("Central US",),
        throttling_max_retry_count=5,
        throttling_max_retry_wait_time_seconds=12,
        hedging_threshold_ms=25,
    )


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
    )
    assert isinstance(backend, RustBackend)
    assert backend._client_config == PreparedClientConfig(
        excluded_locations=("Central US",),
        throttling_max_retry_count=7,
        throttling_max_retry_wait_time_seconds=20,
        hedging_threshold_ms=500,
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
    )
    assert isinstance(backend, AsyncRustBackend)
    assert backend._client_config == PreparedClientConfig(
        excluded_locations=("Central US", "East US"),
        hedging_threshold_ms=15,
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
    """Any non-None backend (the Rust path) -> a clear, tracked gap error."""
    backend = object()  # stands in for a RustBackend / AsyncRustBackend
    with pytest.raises(NotImplementedError, match="not yet available on the Rust backend"):
        raise_account_read_unsupported(backend)


# ---------------------------------------------------------------------------
# Credential classification for the Rust backend (_resolve_credential)
# ---------------------------------------------------------------------------
#
# The Rust backend accepts a master key (string or {"masterKey": ...}) or a
# *synchronous* token credential (forwarded to the driver, which calls its
# get_token during request signing). Async credentials and resource tokens are
# rejected at construction so an unsupported auth shape fails loudly up front.


class _SyncTokenCredential:
    """A minimal stand-in for a synchronous azure-identity credential."""

    def get_token(self, *scopes, **kwargs):  # noqa: D401
        return ("token-value", 9999999999)


class _AsyncTokenCredential:
    """A stand-in for an async credential, which the Rust backend rejects."""

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


def test_resolve_credential_async_token_credential_rejected():
    with pytest.raises(ValueError, match="async token credential"):
        _resolve_credential(_AsyncTokenCredential())


def test_resolve_credential_resource_token_dict_rejected():
    with pytest.raises(ValueError, match="master-key credential"):
        _resolve_credential({"dbs/x/colls/y": "resource-token"})


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
    fake_module.create_item.return_value = (201, 0, {}, b"{}")
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
        assert fake_module.create_item.called, "async Rust path should have been taken"

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
