# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Tests of backend selection, Python-to-binding dispatch, and lifecycle rules.

Most cases replace the native extension or connection with test doubles.
Their calls and counters establish Python wiring, not real HTTP activity,
native resource cleanup, or complete service behavior. Selected native
signature checks require the compiled extension and skip when unavailable.
"""
from __future__ import annotations
import ast
from azure.cosmos._backend.capabilities import OperationRouting
from common.request_preparation import call_create_item_helper
from common.typed_requests import key_from_legacy_header, legacy_partition_key_from_request

import asyncio
import concurrent.futures
import inspect
import logging
import os
import re
import subprocess
import sys
import textwrap
import threading
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

import azure.cosmos.aio._cosmos_client as async_cosmos_client_module
import azure.cosmos.cosmos_client as sync_cosmos_client_module
from azure.cosmos._backend.cosmos_backend import CosmosBackend
from azure.cosmos._backend.contracts import ContainerMetadata
from azure.cosmos._backend.contracts import (
    BackendResponse,
    PreparedClientConfig,
    PreparedFaultInjectionRule,
    PreparedQuery,
    PreparedRequest,
)
from azure.cosmos._backend.operations import (
    OP_FEED_RANGE_FROM_PARTITION_KEY,
    OP_LIST_CONTAINERS,
    OP_LIST_DATABASES,
    OP_QUERY_CONTAINERS,
    OP_QUERY_DATABASES,
    OP_QUERY_ITEMS,
    OP_READ_ALL_ITEMS,
    OP_READ_FEED_RANGES,
    OP_READ_OFFER,
    OP_TO_BINDING_METHOD,
    STATELESS_QUERY_TO_BINDING_METHOD,
)
from azure.cosmos._backend.errors import UnsupportedQueryError
from azure.cosmos._backend.errors import raise_account_read_unsupported
from azure.cosmos._backend import _driver_registry
from azure.cosmos._backend._shared import (
    configure_packaged_query_plan_interop,
    driver_transport_error_type,
    driver_unsupported_query_error_type,
)
from azure.cosmos._backend._driver_registry import (
    _StrictDriverIsolationError,
    ProxyPolicyConflictError,
    TransportTimeoutPolicyConflictError,
    _reset_for_tests as _reset_driver_registry,
    make_driver_identity,
    _register_client_identity,
    register_proxy_policy,
    register_transport_timeout_policy,
    _release_client_identity,
)
from azure.cosmos._backend.constants import (
    BACKEND_ENV_VAR,
    BACKEND_NAME_CORE_PYTHON,
    BACKEND_NAME_RUST,
    RUST_STRICT_ISOLATION_ENV_VAR,
)
from azure.cosmos._backend.client_config import build_client_config
from azure.cosmos._backend.credentials import resolve_credential
from azure.cosmos._backend.factory import (
    make_backend,
    resolve_backend_name,
    resolve_strict_isolation,
)
from azure.cosmos._backend.legacy import LEGACY_BACKEND
from azure.cosmos._backend.transport_settings import (
    reject_unsupported_transport_settings,
    resolve_client_transport_timeouts,
)
from azure.cosmos._backend._async_credential_bridge import (
    AsyncCredentialBridgeReentrantError,
    AsyncTokenCredentialBridge,
)
from azure.cosmos._backend.binding import RustBinding
from azure.cosmos._helpers._item_dispatch import get_selected_backend
from azure.cosmos._helpers._item_operations import ItemHelper
from azure.cosmos.aio._backend.factory import make_async_backend
from azure.cosmos.aio._backend.legacy import ASYNC_LEGACY_BACKEND
from azure.cosmos.aio._backend.binding import AsyncRustBinding
from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy
from azure.cosmos.container import ContainerProxy
from azure.cosmos.documents import ConnectionPolicy
from azure.cosmos.partition_key import NonePartitionKeyValue


@pytest.mark.parametrize(
    "method",
    sorted(
        {
            "release_driver_handle",
            "_debug_fault_injection_rule_hit_count",
            "get_container_metadata",
            "get_container_metadata_async",
        }
        | {
            name + suffix
            for name in set(OP_TO_BINDING_METHOD.values()) | set(STATELESS_QUERY_TO_BINDING_METHOD.values())
            for suffix in ("", "_async")
        }
    ),
)
def test_native_registry_binding_uses_driver_handle_parameter(method):
    """Every native entry point takes its driver as a first argument with one agreed name.

    Each of these is called from Python by name, and the names live in two places that
    are edited separately. If one side were renamed alone, the call would fail only when
    that operation was actually used -- which for the less common ones could be long
    after the change.

    The argument must also be positional as well as named, since callers use both forms.
    The two older names are checked to be gone: leaving one behind would let old code
    keep working while new code uses the new name, and the disagreement would go
    unnoticed until the old name was finally removed.

    The list is built from the same mapping the real code uses, so an operation added
    later is covered without anyone remembering to add it here. The whole test is skipped
    where the native part is not built.
    """
    binding = pytest.importorskip("azure.cosmos._rust")
    signature = inspect.signature(getattr(binding, method))
    parameter = next(iter(signature.parameters.values()))
    assert parameter.name == "driver_handle"
    assert parameter.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert "handle" not in signature.parameters
    assert "_handle" not in signature.parameters


def test_native_close_accepts_driver_handle_keyword():
    """Releasing a driver takes the agreed name, ignores one it never registered, and
    refuses the old name.

    The test above only reads signatures. This one actually calls, because a signature can
    say one thing while the code behind it expects another.

    Releasing something unknown must quietly do nothing. Release runs during cleanup,
    often after an error, and raising there would replace whatever went wrong originally
    with a complaint about tidying up.

    The old name must be refused outright rather than accepted and ignored, which would
    silently leak the driver it was meant to release.
    """
    binding = pytest.importorskip("azure.cosmos._rust")
    assert binding.release_driver_handle(driver_handle="unregistered-test-driver") is None
    with pytest.raises(TypeError):
        binding.release_driver_handle(handle="unregistered-test-driver")


@pytest.fixture(autouse=True)
def _isolate_driver_registry():
    """Reset the shared driver registry before and after each test so one test's
    clients can't make another test warn (or not warn) unexpectedly. The registry
    lives for the whole process, and these tests use unique endpoints, so a client
    finalized late only affects its own endpoint."""
    _reset_driver_registry()
    yield
    _reset_driver_registry()


def test_configure_packaged_query_plan_interop_uses_package_libs(tmp_path, monkeypatch):
    """An existing package .libs directory is selected for native-library lookup.

    This checks environment configuration, not loading the library or the
    number of query-plan requests made by the driver.
    """
    package_directory = tmp_path / "azure" / "cosmos"
    sidecar_directory = package_directory / ".libs"
    sidecar_directory.mkdir(parents=True)
    rust_module = MagicMock()
    rust_module.__file__ = str(package_directory / "_rust.pyd")
    monkeypatch.delenv("AZURE_COSMOS_QUERYPLANINTEROP_DIR", raising=False)

    configure_packaged_query_plan_interop(rust_module)

    assert os.environ["AZURE_COSMOS_QUERYPLANINTEROP_DIR"] == str(
        sidecar_directory.resolve()
    )


def test_configure_packaged_query_plan_interop_skips_missing_directory(tmp_path, monkeypatch):
    """A missing package .libs directory leaves the lookup override unset."""
    rust_module = MagicMock()
    rust_module.__file__ = str(tmp_path / "azure" / "cosmos" / "_rust.pyd")
    monkeypatch.delenv("AZURE_COSMOS_QUERYPLANINTEROP_DIR", raising=False)

    configure_packaged_query_plan_interop(rust_module)

    assert "AZURE_COSMOS_QUERYPLANINTEROP_DIR" not in os.environ


def test_configure_packaged_query_plan_interop_preserves_explicit_directory(
    tmp_path, monkeypatch
):
    """A caller-provided native-library directory has priority over the wheel."""
    package_directory = tmp_path / "azure" / "cosmos"
    (package_directory / ".libs").mkdir(parents=True)
    rust_module = MagicMock()
    rust_module.__file__ = str(package_directory / "_rust.pyd")
    explicit_directory = tmp_path / "explicit"
    monkeypatch.setenv(
        "AZURE_COSMOS_QUERYPLANINTEROP_DIR", str(explicit_directory)
    )

    configure_packaged_query_plan_interop(rust_module)

    assert os.environ["AZURE_COSMOS_QUERYPLANINTEROP_DIR"] == str(
        explicit_directory
    )


@pytest.mark.parametrize(
    "resolver",
    [driver_transport_error_type, driver_unsupported_query_error_type],
)
def test_binding_error_type_matches_nothing_without_extension(resolver):
    """Prove a missing Rust error type cannot match unrelated exceptions."""
    assert resolver(None) == ()


@pytest.mark.parametrize(
    ("resolver", "error_name"),
    [
        (driver_transport_error_type, "_DriverTransportError"),
        (driver_unsupported_query_error_type, "_UnsupportedQueryFeatureError"),
    ],
)
def test_binding_error_type_rejects_stale_extension(resolver, error_name):
    """Prove stale Rust error types are not reused after a module change."""
    with pytest.raises(RuntimeError, match=error_name):
        resolver(object())


@pytest.mark.parametrize(
    "module_name",
    [
        "azure.cosmos._backend.binding",
        "azure.cosmos.aio._backend.binding",
    ],
)
def test_backend_import_does_not_configure_process_query_plan_path(module_name, tmp_path):
    """Native-library discovery is configured at driver startup, not import."""
    script = textwrap.dedent(
        f"""
        import importlib
        import os
        import sys
        import types
        from pathlib import Path

        import azure.cosmos

        package_directory = Path({str(tmp_path)!r}) / "azure" / "cosmos"
        sidecar_directory = package_directory / ".libs"
        sidecar_directory.mkdir(parents=True)
        os.environ.pop("AZURE_COSMOS_QUERYPLANINTEROP_DIR", None)
        fake_rust = types.ModuleType("azure.cosmos._rust")
        fake_rust.__file__ = str(package_directory / "_rust.pyd")
        fake_rust._DriverTransportError = type("_DriverTransportError", (RuntimeError,), {{}})
        fake_rust._DriverResponseError = type("_DriverResponseError", (RuntimeError,), {{}})
        fake_rust._UnsupportedQueryFeatureError = type(
            "_UnsupportedQueryFeatureError", (RuntimeError,), {{}}
        )
        azure.cosmos._rust = fake_rust
        sys.modules["azure.cosmos._rust"] = fake_rust
        sys.modules.pop({module_name!r}, None)

        importlib.import_module({module_name!r})

        assert "AZURE_COSMOS_QUERYPLANINTEROP_DIR" not in os.environ
        """
    )

    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("backend_type", [RustBinding, AsyncRustBinding])
def test_driver_initialization_configures_query_plan_path_before_acquisition(
    backend_type, tmp_path, monkeypatch
):
    package = tmp_path / "azure" / "cosmos"
    sidecar = package / ".libs"
    sidecar.mkdir(parents=True)
    monkeypatch.delenv("AZURE_COSMOS_QUERYPLANINTEROP_DIR", raising=False)
    binding = MagicMock()
    binding.__file__ = str(package / "_rust.pyd")

    def acquire(*args):
        assert os.environ["AZURE_COSMOS_QUERYPLANINTEROP_DIR"] == str(sidecar.resolve())
        return "test-handle"

    binding.acquire_driver_handle.side_effect = acquire
    backend = backend_type(endpoint="https://qpi.documents.azure.com", master_key="k")
    try:
        assert "AZURE_COSMOS_QUERYPLANINTEROP_DIR" not in os.environ
        assert backend._initialize_driver(binding, lambda: None) == "test-handle"
    finally:
        backend.abort_construction()


def test_query_plan_configuration_preserves_override_added_during_discovery(tmp_path, monkeypatch):
    sidecar = tmp_path / ".libs"
    sidecar.mkdir()
    binding = MagicMock()
    binding.__file__ = str(tmp_path / "_rust.pyd")
    monkeypatch.delenv("AZURE_COSMOS_QUERYPLANINTEROP_DIR", raising=False)
    original = Path.is_dir

    def is_dir(path):
        monkeypatch.setenv("AZURE_COSMOS_QUERYPLANINTEROP_DIR", "explicit-after-discovery")
        return original(path)

    monkeypatch.setattr(Path, "is_dir", is_dir)
    configure_packaged_query_plan_interop(binding)
    assert os.environ["AZURE_COSMOS_QUERYPLANINTEROP_DIR"] == "explicit-after-discovery"


# ---------------------------------------------------------------------------
# Import guard
# ---------------------------------------------------------------------------

# This file lives at tests/common/, so go up two folders to the repo root and
# then into azure/cosmos/.
_PKG_ROOT = Path(__file__).resolve().parents[2] / "azure" / "cosmos"

# Each name may only be imported by the files listed here. Anything else fails.
_ALLOWED = {
    # Dispatch imports belong to the backends. The registry only asks the
    # binding for its side-effect-free cache identity.
    "_rust": {
        Path("_backend") / "binding.py",
        Path("aio") / "_backend" / "binding.py",
        Path("_backend") / "_driver_registry.py",
    },
    # The Rust backend class may only be imported by the factory that builds
    # it and the client that holds it.
    "RustBinding": {
        Path("_backend") / "factory.py",
        Path("cosmos_client.py"),
    },
    "AsyncRustBinding": {
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
    """Yield Python source files included in the import-boundary check."""
    for path in _PKG_ROOT.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        yield path


# Read each source file once and keep its import lines, so the test below can
# scan that list instead of re-reading every file for each guarded name.
def _collect_import_lines():
    """Return backend imports found outside their approved files."""
    cached = []
    for py in _iter_py_files():
        rel = py.relative_to(_PKG_ROOT)
        text = py.read_text(encoding="utf-8", errors="ignore")
        # Stub-only imports must not expand the runtime native-boundary allow-list.
        lines = text.splitlines(keepends=True)
        for node in ast.walk(ast.parse(text.lstrip("\ufeff"))):
            if isinstance(node, ast.If) and isinstance(node.test, ast.Name) and node.test.id == "TYPE_CHECKING":
                for child in node.body:
                    for index in range(child.lineno - 1, child.end_lineno):
                        lines[index] = "\n"
        text = "".join(lines)
        import_lines = _IMPORT_RE.findall(text)
        if import_lines:
            cached.append((rel, import_lines))
    return cached


_IMPORT_LINE_CACHE = _collect_import_lines()


@pytest.mark.parametrize(
    "proxy_type,method_name",
    [
        (ContainerProxy, "get_throughput"),
        (ContainerProxy, "replace_throughput"),
        (ContainerProxy, "read_feed_ranges"),
        (ContainerProxy, "feed_range_from_partition_key"),
        (ContainerProxy, "is_feed_range_subset"),
        (AsyncContainerProxy, "get_throughput"),
        (AsyncContainerProxy, "replace_throughput"),
        (AsyncContainerProxy, "read_feed_ranges"),
        (AsyncContainerProxy, "feed_range_from_partition_key"),
        (AsyncContainerProxy, "is_feed_range_subset"),
    ],
)
def test_public_throughput_and_feed_range_methods_do_not_select_backends(
    proxy_type, method_name
):
    """Public methods delegate to family helpers instead of selecting an engine."""
    source = inspect.getsource(getattr(proxy_type, method_name))
    forbidden = (
        "_backend",
        "can_use_rust",
        "try_read_offer_with_rust",
        "try_replace_offer_with_rust",
        "try_read_feed_ranges_with_rust",
        "try_feed_range_from_partition_key_with_rust",
        "try_is_feed_range_subset_with_rust",
    )
    assert not [name for name in forbidden if name in source]


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

def test_factory_default_returns_legacy_backend(monkeypatch):
    """With nothing set, the factory returns the concrete default backend."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    backend = make_backend(None)
    assert backend is LEGACY_BACKEND


def test_factory_env_var_picks_rust(monkeypatch):
    """Setting the environment variable to "rust" builds a Rust backend.

    It needs an endpoint and key, passed the same way the client passes them.
    """
    monkeypatch.setenv(BACKEND_ENV_VAR, BACKEND_NAME_RUST)
    backend = make_backend(None, url="https://x.documents.azure.com", credential="k")
    assert isinstance(backend, RustBinding)
    assert backend.name == BACKEND_NAME_RUST


def test_factory_kwarg_overrides_env(monkeypatch):
    """The constructor argument wins over the environment variable."""
    monkeypatch.setenv(BACKEND_ENV_VAR, BACKEND_NAME_RUST)
    backend = make_backend(BACKEND_NAME_CORE_PYTHON)
    assert backend is LEGACY_BACKEND


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
    """A missing credential raises; this case does not reject token credentials."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    with pytest.raises(ValueError, match="master-key credential"):
        make_backend(BACKEND_NAME_RUST, url="https://x.documents.azure.com", credential=None)


def test_async_factory_returns_async_backends(monkeypatch):
    """The async factory returns concrete legacy and Rust backends."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    assert make_async_backend(None) is ASYNC_LEGACY_BACKEND
    assert isinstance(
        make_async_backend(
            BACKEND_NAME_RUST,
            url="https://x.documents.azure.com",
            credential="k",
        ),
        AsyncRustBinding,
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
# A missing prepared request is rejected rather than used as a fallback signal.
# With a request, dispatch calls the binding and converts the result.
# When the compiled module is missing, it raises an error. The
# tests fake the compiled module so they run without a real account. The async
# backend behaves the same way.

def test_rust_backend_rejects_no_prepared_request():
    """Missing requests are caller errors, not fallback signals."""
    backend = RustBinding(endpoint="https://x.documents.azure.com", master_key="k")
    with pytest.raises(TypeError, match="PreparedRequest"):
        backend.execute(prepared=None)


def test_rust_backend_dispatches_to_binding(monkeypatch):
    """With a request and the compiled module loaded, the backend calls into
    the module and wraps what it returns."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    fake_module.create_item.return_value = (201, 0, {"etag": "v1"}, b'{"id":"x"}')
    monkeypatch.setattr("azure.cosmos._backend.binding._rust_module", fake_module)

    backend = RustBinding(endpoint="https://x.documents.azure.com", master_key="k")
    prepared = PreparedRequest(
        op="create_item",
        container_link="dbs/d/colls/c",
        body_bytes=b'{"id":"x"}',
        partition_key=key_from_legacy_header('["a"]'),
        headers={},
    )
    resp = backend.execute(prepared)

    fake_module.acquire_driver_handle.assert_called_once_with(
        "https://x.documents.azure.com", "k", None
    )
    fake_module.create_item.assert_called_once_with("handle-1", prepared)
    assert resp.status_code == 201
    assert resp.body == b'{"id":"x"}'


def test_rust_backend_resolves_container_metadata_through_binding(monkeypatch):
    """Prove sync Rust requests resolve container metadata through Rust."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    fake_module.get_container_metadata.return_value = (
        "rid-1", ("/pk",), "Hash", None,
    )
    monkeypatch.setattr("azure.cosmos._backend.binding._rust_module", fake_module)

    backend = RustBinding(endpoint="https://x.documents.azure.com", master_key="k")
    response = backend.get_container_metadata("dbs/d/colls/c")

    fake_module.get_container_metadata.assert_called_once_with(
        "handle-1", "dbs/d/colls/c"
    )
    assert response.rid == "rid-1"
    assert response.partition_key_paths == ("/pk",)
    assert response.partition_key_kind == "Hash"


def test_rust_backend_metadata_resolution_rejects_older_binding(monkeypatch):
    """Missing metadata capability must fail instead of consulting Python."""
    class OlderBinding:
        """Provide only the entry point available in an older extension."""

        @staticmethod
        def acquire_driver_handle(*_args):
            return "handle-1"

    monkeypatch.setattr(
        "azure.cosmos._backend.binding._rust_module", OlderBinding()
    )
    backend = RustBinding(endpoint="https://x.documents.azure.com", master_key="k")

    with pytest.raises(NotImplementedError, match="get_container_metadata"):
        backend.get_container_metadata("dbs/d/colls/c")


# The next two tests cover the newly-migrated query_items and read_feed_ranges on
# the sync Rust backend: each proves a prepared request is handed to the matching
# binding entry point and the binding's reply is returned unchanged. Without them a
# wiring mistake -- a wrong op-to-binding name, or a dropped reply -- could send
# these operations nowhere and no test would catch it.
def test_rust_backend_dispatches_query_items_to_binding(monkeypatch):
    """A prepared query routes through execute_pages to query_items."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    fake_module.query_items.return_value = (
        200,
        0,
        {"x-ms-continuation": "ct-1"},
        b'{"Documents":[{"id":"x"}]}',
    )
    monkeypatch.setattr("azure.cosmos._backend.binding._rust_module", fake_module)

    backend = RustBinding(endpoint="https://x.documents.azure.com", master_key="k")
    prepared = PreparedQuery(
        op=OP_QUERY_ITEMS,
        container_link="dbs/d/colls/c",
        query="SELECT * FROM c",
        partition_key=key_from_legacy_header('["a"]', extract=False),
        headers={},
    )
    pages = list(backend.execute_pages(prepared))

    binding_request = fake_module.query_items.call_args.args[1]
    assert binding_request.op == OP_QUERY_ITEMS
    assert binding_request.body_bytes == b'{"query":"SELECT * FROM c"}'
    assert pages[0].status_code == 200
    assert pages[0].continuation == "ct-1"
    assert pages[0].body == b'{"Documents":[{"id":"x"}]}'


def test_paged_operations_are_not_single_response_operations():
    """Feed operations live only in the paged dispatch map.

    This keeps query, read-all, and database-list pages out of the single-reply
    ``execute`` path.
    """
    assert OP_QUERY_ITEMS not in OP_TO_BINDING_METHOD
    assert OP_READ_ALL_ITEMS not in OP_TO_BINDING_METHOD
    assert OP_LIST_DATABASES not in OP_TO_BINDING_METHOD
    assert OP_QUERY_DATABASES not in OP_TO_BINDING_METHOD
    assert OP_LIST_CONTAINERS not in OP_TO_BINDING_METHOD
    assert OP_QUERY_CONTAINERS not in OP_TO_BINDING_METHOD
    assert "query_items_change_feed" not in OP_TO_BINDING_METHOD
    assert STATELESS_QUERY_TO_BINDING_METHOD == {
        OP_QUERY_ITEMS: "query_items",
        OP_READ_ALL_ITEMS: "read_all_items",
        OP_LIST_DATABASES: "list_databases",
        OP_QUERY_DATABASES: "query_databases",
        OP_LIST_CONTAINERS: "list_containers",
        OP_QUERY_CONTAINERS: "query_containers",
    }
    from azure.cosmos._backend.operations import CURSOR_QUERY_TO_BINDING_METHOD
    assert CURSOR_QUERY_TO_BINDING_METHOD == {
        OP_QUERY_ITEMS: "fetch_page_with_cursor",
        OP_READ_ALL_ITEMS: "fetch_page_with_cursor",
        "query_items_change_feed": "fetch_page_with_cursor",
    }


def test_rust_backend_surfaces_driver_query_capability_rejection(monkeypatch):
    """Translate the fake binding's query rejection to UnsupportedQueryError.

    The test checks error translation, not automatic replay through legacy.
    """
    class _UnsupportedQueryFeatureError(RuntimeError):
        """Represent a query feature rejected by the Rust driver."""

        pass

    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    fake_module.query_items.side_effect = _UnsupportedQueryFeatureError(
        "unsupported query feature"
    )
    monkeypatch.setattr("azure.cosmos._backend.binding._rust_module", fake_module)
    monkeypatch.setattr(
        "azure.cosmos._backend.binding._UNSUPPORTED_QUERY_ERROR",
        _UnsupportedQueryFeatureError,
    )

    backend = RustBinding(endpoint="https://x.documents.azure.com", master_key="k")
    prepared = PreparedQuery(
        op=OP_QUERY_ITEMS,
        container_link="dbs/d/colls/c",
        query="SELECT VALUE COUNT(1) FROM c",
    )

    with pytest.raises(UnsupportedQueryError):
        list(backend.execute_pages(prepared))


def test_rust_backend_dispatches_read_all_items_to_binding(monkeypatch):
    """A read_all_items prepared request routes to the binding's read_all_items entry point."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    fake_module.read_all_items.return_value = (
        200,
        0,
        {"x-ms-continuation": "ct-read-all"},
        b'{"Documents":[{"id":"x"}]}',
    )
    monkeypatch.setattr("azure.cosmos._backend.binding._rust_module", fake_module)

    backend = RustBinding(endpoint="https://x.documents.azure.com", master_key="k")
    prepared = PreparedQuery(
        op=OP_READ_ALL_ITEMS,
        container_link="dbs/d/colls/c",
        partition_key=key_from_legacy_header("[]", extract=False),
        headers={},
    )
    pages = list(backend.execute_pages(prepared))

    binding_request = fake_module.read_all_items.call_args.args[1]
    assert binding_request.op == OP_READ_ALL_ITEMS
    assert binding_request.body_bytes == b""
    assert pages[0].status_code == 200
    assert pages[0].continuation == "ct-read-all"
    assert pages[0].body == b'{"Documents":[{"id":"x"}]}'


def test_rust_backend_dispatches_read_offer_to_binding(monkeypatch):
    """A read_offer prepared request routes to the binding's read_offer entry point."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    fake_module.read_offer.return_value = (
        200,
        0,
        {"x-ms-continuation": "ct-read-offer"},
        b'{"Offers":[{"id":"offer-1","resource":"dbs/d/colls/c"}]}',
    )
    monkeypatch.setattr("azure.cosmos._backend.binding._rust_module", fake_module)

    backend = RustBinding(endpoint="https://x.documents.azure.com", master_key="k")
    prepared = PreparedRequest(
        op=OP_READ_OFFER,
        container_link="dbs/d/colls/c",
        body_bytes=b'{"query":"SELECT * FROM root r WHERE r.resource=@link","parameters":[]}',
        partition_key=key_from_legacy_header("[]"),
        headers={},
    )
    resp = backend.execute(prepared)

    fake_module.read_offer.assert_called_once_with("handle-1", prepared)
    assert resp.status_code == 200
    assert b'"Offers"' in resp.body


def test_rust_backend_dispatches_read_feed_ranges_to_binding(monkeypatch):
    """A read_feed_ranges prepared request routes to binding read_feed_ranges."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    fake_module.read_feed_ranges.return_value = (
        200,
        0,
        {},
        b'{"PartitionKeyRanges":[{"id":"0","minInclusive":"","maxExclusive":"FF"}]}',
    )
    monkeypatch.setattr("azure.cosmos._backend.binding._rust_module", fake_module)

    backend = RustBinding(endpoint="https://x.documents.azure.com", master_key="k")
    prepared = PreparedRequest(
        op=OP_READ_FEED_RANGES,
        container_link="dbs/d/colls/c",
        body_bytes=b'{"forceRefresh":true}',
        partition_key=key_from_legacy_header("[]"),
        headers={},
    )
    resp = backend.execute(prepared)

    fake_module.read_feed_ranges.assert_called_once_with("handle-1", prepared)
    assert resp.status_code == 200
    assert b"PartitionKeyRanges" in resp.body


def test_rust_backend_dispatches_feed_range_from_partition_key_to_binding(monkeypatch):
    """A feed_range_from_partition_key prepared request routes to the matching binding entry point."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    fake_module.feed_range_from_partition_key.return_value = (
        200,
        0,
        {},
        b'{"Range":{"min":"3C","max":"3C","isMinInclusive":true,"isMaxInclusive":true}}',
    )
    monkeypatch.setattr("azure.cosmos._backend.binding._rust_module", fake_module)

    backend = RustBinding(endpoint="https://x.documents.azure.com", master_key="k")
    prepared = PreparedRequest(
        op=OP_FEED_RANGE_FROM_PARTITION_KEY,
        container_link="dbs/d/colls/c",
        body_bytes=b"",
        partition_key=key_from_legacy_header('["a"]', feed_range=True),
        headers={},
    )
    resp = backend.execute(prepared)

    fake_module.feed_range_from_partition_key.assert_called_once_with("handle-1", prepared)
    assert resp.status_code == 200
    assert b'"Range"' in resp.body


def test_rust_backend_accepts_optional_diagnostics_from_binding(monkeypatch):
    """The backend accepts diagnostics returned by the binding."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    fake_module.create_item.return_value = (
        201,
        0,
        {"etag": "v1"},
        b'{"id":"x"}',
        "activity=abc duration=8ms requests=1 charge=1RU status=201",
    )
    monkeypatch.setattr("azure.cosmos._backend.binding._rust_module", fake_module)

    backend = RustBinding(endpoint="https://x.documents.azure.com", master_key="k")
    prepared = PreparedRequest(
        op="create_item",
        container_link="dbs/d/colls/c",
        body_bytes=b'{"id":"x"}',
        partition_key=key_from_legacy_header('["a"]'),
        headers={},
    )
    resp = backend.execute(prepared)

    assert resp.status_code == 201
    assert resp.diagnostics == "activity=abc duration=8ms requests=1 charge=1RU status=201"


def test_rust_backend_returns_structured_http_failure_tuple(monkeypatch):
    """A failed request (like a 409) comes back as a normal response with its
    status, sub-status, headers, and body -- not as an error."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
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
    monkeypatch.setattr("azure.cosmos._backend.binding._rust_module", fake_module)

    backend = RustBinding(endpoint="https://x.documents.azure.com", master_key="k")
    prepared = PreparedRequest(
        op="create_item",
        container_link="dbs/d/colls/c",
        body_bytes=b'{"id":"x"}',
        partition_key=key_from_legacy_header('["a"]'),
        headers={},
    )

    resp = backend.execute(prepared)

    assert resp.status_code == 409
    assert resp.sub_status == 1002
    assert resp.headers["x-ms-activity-id"] == "act-409"
    assert resp.headers["x-ms-retry-after-ms"] == "250"
    assert resp.body == b'{"code":"Conflict","message":"already exists"}'


def test_rust_backend_logs_per_op_backend_telemetry(monkeypatch, caplog):
    """Dispatch logs name the backend and operation without exposing the handle.

    A fake binding serves the call. The log is a selection/dispatch record,
    not proof of native or service execution.
    """
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-secret-fp"
    fake_module.create_item.return_value = (201, 0, {"etag": "v1"}, b'{"id":"x"}')
    monkeypatch.setattr("azure.cosmos._backend.binding._rust_module", fake_module)

    backend = RustBinding(endpoint="https://x.documents.azure.com", master_key="k")
    prepared = PreparedRequest(
        op="create_item",
        container_link="dbs/d/colls/c",
        body_bytes=b'{"id":"x"}',
        partition_key=key_from_legacy_header('["a"]'),
        headers={},
    )
    with caplog.at_level(logging.DEBUG, logger="azure.cosmos._backend.binding"):
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
    fake_module.acquire_driver_handle.return_value = "handle-secret-fp"
    fake_module.create_item_async = AsyncMock(return_value=(201, 0, {"etag": "v1"}, b'{"id":"x"}'))
    monkeypatch.setattr("azure.cosmos.aio._backend.binding._rust_module", fake_module)

    async def _run():
        backend = AsyncRustBinding(endpoint="https://x.documents.azure.com", master_key="k")
        prepared = PreparedRequest(
            op="create_item",
            container_link="dbs/d/colls/c",
            body_bytes=b'{"id":"x"}',
            partition_key=key_from_legacy_header('["a"]'),
            headers={},
        )
        await backend.execute(prepared)
        # Close so the built handle is released here, not leaked to a finalizer that
        # would run during a later test (and call that test's fake release_driver_handle).
        await backend.close()

    with caplog.at_level(logging.DEBUG, logger="azure.cosmos.aio._backend.binding"):
        asyncio.run(_run())

    messages = [r.getMessage() for r in caplog.records]
    assert any("backend=rust" in m and "op=create_item" in m for m in messages)
    assert all("handle-secret-fp" not in m for m in messages)


def test_rust_backend_propagates_transport_runtime_error(monkeypatch):
    """A real driver failure (not an HTTP response) is raised as an error."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    fake_module.create_item.side_effect = RuntimeError("driver execute_operation failed: DNS lookup failed")
    monkeypatch.setattr("azure.cosmos._backend.binding._rust_module", fake_module)

    backend = RustBinding(endpoint="https://x.documents.azure.com", master_key="k")
    prepared = PreparedRequest(
        op="create_item",
        container_link="dbs/d/colls/c",
        body_bytes=b'{"id":"x"}',
        partition_key=key_from_legacy_header('["a"]'),
        headers={},
    )

    with pytest.raises(RuntimeError, match="DNS lookup failed"):
        backend.execute(prepared)


def test_rust_backend_raises_when_binding_not_built(monkeypatch):
    """When the compiled module is missing, the backend raises a clear error
    pointing at the build step instead of failing in a confusing way later."""
    monkeypatch.setattr("azure.cosmos._backend.binding._rust_module", None)
    backend = RustBinding(endpoint="https://x.documents.azure.com", master_key="k")
    prepared = PreparedRequest(
        op="create_item",
        container_link="dbs/d/colls/c",
        body_bytes=b'{"id":"x"}',
        partition_key=key_from_legacy_header('["a"]'),
        headers={},
    )
    with pytest.raises(NotImplementedError, match="not present"):
        backend.execute(prepared)


def test_async_rust_backend_rejects_no_prepared_request():
    """Async execution has the same non-optional request contract."""
    async def _run():
        backend = AsyncRustBinding(endpoint="https://x.documents.azure.com", master_key="k")
        with pytest.raises(TypeError, match="PreparedRequest"):
            await backend.execute(prepared=None)
    asyncio.run(_run())


def test_async_rust_backend_dispatches_to_binding(monkeypatch):
    """Await the fake async create entry point and convert its response tuple.

    This checks dispatch, not thread counts or native executor behavior.
    """
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    fake_module.create_item_async = AsyncMock(return_value=(201, 0, {"etag": "v1"}, b'{"id":"x"}'))
    monkeypatch.setattr("azure.cosmos.aio._backend.binding._rust_module", fake_module)

    async def _run():
        backend = AsyncRustBinding(endpoint="https://x.documents.azure.com", master_key="k")
        prepared = PreparedRequest(
            op="create_item",
            container_link="dbs/d/colls/c",
            body_bytes=b'{"id":"x"}',
            partition_key=key_from_legacy_header('["a"]'),
            headers={},
        )
        resp = await backend.execute(prepared)
        fake_module.acquire_driver_handle.assert_called_once()
        fake_module.create_item_async.assert_awaited_once_with("handle-1", prepared)
        assert resp.status_code == 201
        assert resp.body == b'{"id":"x"}'
    asyncio.run(_run())


def test_async_rust_backend_resolves_container_metadata_through_binding(monkeypatch):
    """Prove async Rust requests resolve container metadata through Rust."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    fake_module.get_container_metadata_async = AsyncMock(
        return_value=(
            "rid-1", ("/pk",), "Hash", None,
        )
    )
    monkeypatch.setattr("azure.cosmos.aio._backend.binding._rust_module", fake_module)

    async def _run():
        backend = AsyncRustBinding(
            endpoint="https://x.documents.azure.com", master_key="k"
        )
        response = await backend.get_container_metadata("dbs/d/colls/c")
        assert response.rid == "rid-1"
        assert response.partition_key_paths == ("/pk",)
        assert response.partition_key_kind == "Hash"

    asyncio.run(_run())
    fake_module.get_container_metadata_async.assert_awaited_once_with(
        "handle-1", "dbs/d/colls/c"
    )


def test_async_rust_backend_metadata_resolution_rejects_older_binding(monkeypatch):
    """An extension missing the typed metadata entry point fails explicitly."""
    class OlderBinding:
        """Provide only the entry point available in an older extension."""

        @staticmethod
        def acquire_driver_handle(*_args):
            return "handle-1"

    monkeypatch.setattr(
        "azure.cosmos.aio._backend.binding._rust_module", OlderBinding()
    )

    async def _run():
        backend = AsyncRustBinding(
            endpoint="https://x.documents.azure.com", master_key="k"
        )
        with pytest.raises(NotImplementedError, match="get_container_metadata_async"):
            await backend.get_container_metadata("dbs/d/colls/c")

    asyncio.run(_run())


# Async twins of the two dispatch tests above: the same check for query_items_async
# and read_feed_ranges_async, so the async path can't silently diverge from the sync one.
def test_async_rust_backend_dispatches_query_items_to_binding(monkeypatch):
    """Async prepared queries route through execute_pages to query_items_async."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    fake_module.query_items_async = AsyncMock(
        return_value=(200, 0, {"x-ms-continuation": "ct-1"}, b'{"Documents":[{"id":"x"}]}')
    )
    monkeypatch.setattr("azure.cosmos.aio._backend.binding._rust_module", fake_module)

    async def _run():
        backend = AsyncRustBinding(endpoint="https://x.documents.azure.com", master_key="k")
        prepared = PreparedQuery(
            op=OP_QUERY_ITEMS,
            container_link="dbs/d/colls/c",
            query="SELECT * FROM c",
            partition_key=key_from_legacy_header('["a"]', extract=False),
            headers={},
        )
        pages = [page async for page in backend.execute_pages(prepared)]
        binding_request = fake_module.query_items_async.await_args.args[1]
        assert binding_request.op == OP_QUERY_ITEMS
        assert binding_request.body_bytes == b'{"query":"SELECT * FROM c"}'
        assert pages[0].status_code == 200
        assert pages[0].continuation == "ct-1"
        assert pages[0].body == b'{"Documents":[{"id":"x"}]}'

    asyncio.run(_run())


def test_async_rust_backend_dispatches_read_all_items_to_binding(monkeypatch):
    """Async read_all_items prepared requests route to read_all_items_async."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    fake_module.read_all_items_async = AsyncMock(
        return_value=(200, 0, {"x-ms-continuation": "ct-read-all-async"}, b'{"Documents":[{"id":"x"}]}')
    )
    monkeypatch.setattr("azure.cosmos.aio._backend.binding._rust_module", fake_module)

    async def _run():
        backend = AsyncRustBinding(endpoint="https://x.documents.azure.com", master_key="k")
        prepared = PreparedQuery(
            op=OP_READ_ALL_ITEMS,
            container_link="dbs/d/colls/c",
            partition_key=key_from_legacy_header("[]", extract=False),
            headers={},
        )
        pages = [page async for page in backend.execute_pages(prepared)]
        binding_request = fake_module.read_all_items_async.await_args.args[1]
        assert binding_request.op == OP_READ_ALL_ITEMS
        assert binding_request.body_bytes == b""
        assert pages[0].status_code == 200
        assert pages[0].continuation == "ct-read-all-async"
        assert pages[0].body == b'{"Documents":[{"id":"x"}]}'

    asyncio.run(_run())


def test_async_rust_backend_surfaces_driver_query_capability_rejection(monkeypatch):
    """Translate an async fake-binding query rejection without testing legacy replay."""
    class _UnsupportedQueryFeatureError(RuntimeError):
        """Represent an async query feature rejected by the Rust driver."""

        pass

    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    fake_module.query_items_async = AsyncMock(
        side_effect=_UnsupportedQueryFeatureError("unsupported query feature")
    )
    monkeypatch.setattr("azure.cosmos.aio._backend.binding._rust_module", fake_module)
    monkeypatch.setattr(
        "azure.cosmos.aio._backend.binding._UNSUPPORTED_QUERY_ERROR",
        _UnsupportedQueryFeatureError,
    )

    async def _run():
        backend = AsyncRustBinding(
            endpoint="https://x.documents.azure.com", master_key="k"
        )
        prepared = PreparedQuery(
            op=OP_QUERY_ITEMS,
            container_link="dbs/d/colls/c",
            query="SELECT * FROM c ORDER BY c.ts",
        )
        with pytest.raises(UnsupportedQueryError):
            [page async for page in backend.execute_pages(prepared)]

    asyncio.run(_run())


def test_async_rust_backend_dispatches_read_offer_to_binding(monkeypatch):
    """Async read_offer prepared requests route to read_offer_async."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    fake_module.read_offer_async = AsyncMock(
        return_value=(200, 0, {"x-ms-continuation": "ct-read-offer-async"}, b'{"Offers":[{"id":"offer-1"}]}')
    )
    monkeypatch.setattr("azure.cosmos.aio._backend.binding._rust_module", fake_module)

    async def _run():
        backend = AsyncRustBinding(endpoint="https://x.documents.azure.com", master_key="k")
        prepared = PreparedRequest(
            op=OP_READ_OFFER,
            container_link="dbs/d/colls/c",
            body_bytes=b'{"query":"SELECT * FROM root r WHERE r.resource=@link","parameters":[]}',
            partition_key=key_from_legacy_header("[]"),
            headers={},
        )
        resp = await backend.execute(prepared)
        fake_module.read_offer_async.assert_awaited_once_with("handle-1", prepared)
        assert resp.status_code == 200
        assert b'"Offers"' in resp.body

    asyncio.run(_run())


def test_async_rust_backend_dispatches_read_feed_ranges_to_binding(monkeypatch):
    """Async read_feed_ranges prepared requests route to read_feed_ranges_async."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    fake_module.read_feed_ranges_async = AsyncMock(
        return_value=(
            200,
            0,
            {},
            b'{"PartitionKeyRanges":[{"id":"0","minInclusive":"","maxExclusive":"FF"}]}',
        )
    )
    monkeypatch.setattr("azure.cosmos.aio._backend.binding._rust_module", fake_module)

    async def _run():
        backend = AsyncRustBinding(endpoint="https://x.documents.azure.com", master_key="k")
        prepared = PreparedRequest(
            op=OP_READ_FEED_RANGES,
            container_link="dbs/d/colls/c",
            body_bytes=b'{"forceRefresh":false}',
            partition_key=key_from_legacy_header("[]"),
            headers={},
        )
        resp = await backend.execute(prepared)
        fake_module.read_feed_ranges_async.assert_awaited_once_with("handle-1", prepared)
        assert resp.status_code == 200
        assert b"PartitionKeyRanges" in resp.body

    asyncio.run(_run())


def test_async_rust_backend_dispatches_feed_range_from_partition_key_to_binding(monkeypatch):
    """Async feed_range_from_partition_key prepared requests route to the async binding entry point."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    fake_module.feed_range_from_partition_key_async = AsyncMock(
        return_value=(
            200,
            0,
            {},
            b'{"Range":{"min":"3C","max":"3C","isMinInclusive":true,"isMaxInclusive":true}}',
        )
    )
    monkeypatch.setattr("azure.cosmos.aio._backend.binding._rust_module", fake_module)

    async def _run():
        backend = AsyncRustBinding(endpoint="https://x.documents.azure.com", master_key="k")
        prepared = PreparedRequest(
            op=OP_FEED_RANGE_FROM_PARTITION_KEY,
            container_link="dbs/d/colls/c",
            body_bytes=b"",
            partition_key=key_from_legacy_header('["a"]', feed_range=True),
            headers={},
        )
        resp = await backend.execute(prepared)
        fake_module.feed_range_from_partition_key_async.assert_awaited_once_with("handle-1", prepared)
        assert resp.status_code == 200
        assert b'"Range"' in resp.body

    asyncio.run(_run())


def test_async_rust_backend_accepts_optional_diagnostics_from_binding(monkeypatch):
    """Async version: diagnostics returned by the binding are preserved."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    fake_module.create_item_async = AsyncMock(
        return_value=(
            201,
            0,
            {"etag": "v1"},
            b'{"id":"x"}',
            "activity=abc duration=7ms requests=1 charge=1RU status=201",
        )
    )
    monkeypatch.setattr("azure.cosmos.aio._backend.binding._rust_module", fake_module)

    async def _run():
        backend = AsyncRustBinding(endpoint="https://x.documents.azure.com", master_key="k")
        prepared = PreparedRequest(
            op="create_item",
            container_link="dbs/d/colls/c",
            body_bytes=b'{"id":"x"}',
            partition_key=key_from_legacy_header('["a"]'),
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
    fake_module.acquire_driver_handle.return_value = "handle-1"
    fake_module.create_item_async = AsyncMock(
        return_value=(
            404,
            0,
            {"x-ms-activity-id": "act-404"},
            b'{"code":"NotFound","message":"missing"}',
        )
    )
    monkeypatch.setattr("azure.cosmos.aio._backend.binding._rust_module", fake_module)

    async def _run():
        backend = AsyncRustBinding(endpoint="https://x.documents.azure.com", master_key="k")
        prepared = PreparedRequest(
            op="create_item",
            container_link="dbs/d/colls/c",
            body_bytes=b'{"id":"x"}',
            partition_key=key_from_legacy_header('["a"]'),
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
    fake_module.acquire_driver_handle.return_value = "handle-1"
    fake_module.create_item_async = AsyncMock(side_effect=RuntimeError("driver execute_operation failed: TLS handshake failed"))
    monkeypatch.setattr("azure.cosmos.aio._backend.binding._rust_module", fake_module)

    async def _run():
        backend = AsyncRustBinding(endpoint="https://x.documents.azure.com", master_key="k")
        prepared = PreparedRequest(
            op="create_item",
            container_link="dbs/d/colls/c",
            body_bytes=b'{"id":"x"}',
            partition_key=key_from_legacy_header('["a"]'),
            headers={},
        )
        with pytest.raises(RuntimeError, match="TLS handshake failed"):
            await backend.execute(prepared)

    asyncio.run(_run())


def test_async_rust_backend_raises_when_binding_not_built(monkeypatch):
    """Async version: a missing compiled module raises a clear error."""
    monkeypatch.setattr("azure.cosmos.aio._backend.binding._rust_module", None)

    async def _run():
        backend = AsyncRustBinding(endpoint="https://x.documents.azure.com", master_key="k")
        prepared = PreparedRequest(
            op="create_item",
            container_link="dbs/d/colls/c",
            body_bytes=b'{"id":"x"}',
            partition_key=key_from_legacy_header('["a"]'),
            headers={},
        )
        with pytest.raises(NotImplementedError, match="not present"):
            await backend.execute(prepared)
    asyncio.run(_run())


def test_async_backend_coalesces_concurrent_first_init_to_one_call(monkeypatch):
    """A burst of concurrent first-operations builds the client handle exactly
    once: every first-caller awaits one shared init future instead of each
    scheduling its own ``acquire_driver_handle`` build on a background thread."""
    init_calls = []
    fake_module = MagicMock()

    def _slow_init(*args):
        # Block briefly so the whole burst reaches _ensure_driver_handle while the first
        # init is still in flight on the executor thread -- the window in which
        # uncoalesced callers would each schedule their own offload.
        init_calls.append(args)
        time.sleep(0.05)
        return "handle-1"

    fake_module.acquire_driver_handle.side_effect = _slow_init
    fake_module.read_item_async = AsyncMock(return_value=(200, 0, {}, b"{}"))
    monkeypatch.setattr("azure.cosmos.aio._backend.binding._rust_module", fake_module)

    prepared = PreparedRequest(
        op="read_item",
        container_link="dbs/d/colls/c",
        body_bytes=b"",
        partition_key=key_from_legacy_header('["a"]'),
        headers={},
        item_id="x",
    )

    async def _run():
        backend = AsyncRustBinding(endpoint="https://x.documents.azure.com", master_key="k")
        await asyncio.gather(*(backend.execute(prepared) for _ in range(50)))

    asyncio.run(_run())
    assert len(init_calls) == 1, f"acquire_driver_handle should run once, ran {len(init_calls)} times"
    assert fake_module.read_item_async.await_count == 50


def test_async_backend_retries_init_after_failure(monkeypatch):
    """A failed init is not cached on the shared future: the next operation retries
    ``acquire_driver_handle`` rather than handing back the first failure forever."""
    attempts = []
    fake_module = MagicMock()

    def _flaky_init(*args):
        attempts.append(args)
        if len(attempts) == 1:
            raise RuntimeError("init boom")
        return "handle-1"

    fake_module.acquire_driver_handle.side_effect = _flaky_init
    fake_module.read_item_async = AsyncMock(return_value=(200, 0, {}, b"{}"))
    monkeypatch.setattr("azure.cosmos.aio._backend.binding._rust_module", fake_module)

    prepared = PreparedRequest(
        op="read_item",
        container_link="dbs/d/colls/c",
        body_bytes=b"",
        partition_key=key_from_legacy_header('["a"]'),
        headers={},
        item_id="x",
    )

    async def _run():
        backend = AsyncRustBinding(endpoint="https://x.documents.azure.com", master_key="k")
        # First op: init fails and surfaces to the caller.
        with pytest.raises(RuntimeError, match="init boom"):
            await backend.execute(prepared)
        # Second op: init is retried (not a cached failure) and succeeds.
        resp = await backend.execute(prepared)
        assert resp.status_code == 200
        await backend.close()

    asyncio.run(_run())
    assert len(attempts) == 2, f"init should be retried after failure, attempts={len(attempts)}"


def test_async_backend_close_during_init_closes_built_driver_handle(monkeypatch):
    """If close() runs while the first acquire_driver_handle is still building, the handle the
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

    fake_module.acquire_driver_handle.side_effect = _slow_init
    fake_module.release_driver_handle.side_effect = closed.append
    fake_module.read_item_async = AsyncMock(return_value=(200, 0, {}, b"{}"))
    monkeypatch.setattr("azure.cosmos.aio._backend.binding._rust_module", fake_module)

    prepared = PreparedRequest(
        op="read_item",
        container_link="dbs/d/colls/c",
        body_bytes=b"",
        partition_key=key_from_legacy_header('["a"]'),
        headers={},
        item_id="x",
    )

    async def _run():
        backend = AsyncRustBinding(endpoint="https://x.documents.azure.com", master_key="k")
        op = asyncio.ensure_future(backend.execute(prepared))
        # Wait until acquire_driver_handle is running on the build thread.
        await asyncio.get_running_loop().run_in_executor(None, init_in_flight.wait, 5)
        # close() returns without waiting for the build to finish: the build does not
        # hold _driver_handle_lock during acquire_driver_handle, so close() takes that lock right away.
        await asyncio.wait_for(backend.close(), timeout=2)
        # Let the build finish; it sees the client is closing and closes the handle it
        # built instead of leaving it open.
        allow_init_finish.set()
        with pytest.raises(Exception):
            await op

    asyncio.run(_run())
    assert closed == ["handle-1"], f"handle built during close should be closed, got {closed}"
    fake_module.acquire_driver_handle.assert_called_once()


def test_async_backend_propagates_cancellation_into_binding(monkeypatch):
    """Cancelling execute propagates into the fake binding coroutine.

    The coroutine records CancelledError and the caller receives cancellation.
    No Tokio task, connection cleanup, or service-side cancellation is tested.
    """
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    dispatch_cancelled = []

    async def _slow_read(_driver_handle, _prepared):
        try:
            await asyncio.sleep(10)
        except asyncio.CancelledError:
            dispatch_cancelled.append(True)
            raise
        return (200, 0, {}, b"{}")  # pragma: no cover - cancelled before here

    fake_module.read_item_async = _slow_read
    monkeypatch.setattr("azure.cosmos.aio._backend.binding._rust_module", fake_module)

    prepared = PreparedRequest(
        op="read_item",
        container_link="dbs/d/colls/c",
        body_bytes=b"",
        partition_key=key_from_legacy_header('["a"]'),
        headers={},
        item_id="x",
    )

    async def _run():
        backend = AsyncRustBinding(endpoint="https://x.documents.azure.com", master_key="k")
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
    a daemon thread, not run inline on the loop thread -- otherwise release_driver_handle
    would stall the loop. The config drop stays inline (it does not block)."""
    close_started = threading.Event()
    close_may_finish = threading.Event()
    close_thread_names = []
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-finalizer"
    fake_module.read_item_async = AsyncMock(return_value=(200, 0, {}, b"{}"))

    def _blocking_close(driver_handle):
        # Only this backend's close is measured. Other tests' async backends can be
        # garbage-collected during this test (their finalizers call this same
        # monkeypatched release_driver_handle); ignoring foreign handles keeps their thread
        # from polluting the measurement -- and keeps them from blocking on
        # close_may_finish, which could stall an inline GC finalizer.
        if driver_handle != "handle-finalizer":
            return
        close_thread_names.append(threading.current_thread().name)
        close_started.set()
        close_may_finish.wait(5)  # hold the close open to expose any inline block

    fake_module.release_driver_handle.side_effect = _blocking_close
    monkeypatch.setattr("azure.cosmos.aio._backend.binding._rust_module", fake_module)

    prepared = PreparedRequest(
        op="read_item",
        container_link="dbs/d/colls/c",
        body_bytes=b"",
        partition_key=key_from_legacy_header('["a"]'),
        headers={},
        item_id="x",
    )

    async def _run():
        backend = AsyncRustBinding(endpoint="https://x.documents.azure.com", master_key="k")
        await backend.execute(prepared)  # build the handle so the finalizer has work
        main_thread = threading.current_thread().name
        # Fire the finalizer while this loop is running.
        backend.__del__()
        # The offloaded close should start on another thread; meanwhile the loop
        # must keep turning even though release_driver_handle is still blocked.
        assert close_started.wait(2), "offloaded close did not start"
        for _ in range(5):
            await asyncio.sleep(0)  # would hang here if the close blocked the loop
        close_may_finish.set()
        return main_thread

    main_thread = asyncio.run(_run())
    assert close_thread_names, "release_driver_handle was never called"
    assert close_thread_names[0] != main_thread, (
        f"close ran on the loop thread {close_thread_names[0]!r}; must be offloaded"
    )
    assert close_thread_names[0] == "cosmos-rust-finalizer"


def test_helper_parses_backend_response_into_cosmos_dict(monkeypatch):
    """A successful backend response is turned into a dict the caller can read
    by key (like ``result["_etag"]``), the same shape the existing path
    returns.

    Uses a real ``CosmosBackend`` subclass (not a bare mock) so the helper runs
    the genuine ``run_operation`` template: build the prepared request, call
    ``execute``, then parse the reply into a ``CosmosDict``.
    """

    class _RustDispatchBackend(CosmosBackend):
        """Return a fixed response while recording the prepared request."""

        name = BACKEND_NAME_RUST

        def __init__(self, response):
            self._response = response
            self.captured = None

        def execute(self, prepared, *, deadline=None):
            self.captured = prepared
            return self._response

        def get_container_metadata(self, link):
            return ContainerMetadata("rid")

    backend = _RustDispatchBackend(
        BackendResponse(
            status_code=201,
            sub_status=0,
            headers=None,
            body=(
                b'{"id":"order-42","pk":"customerA","_etag":"\\"00000000-0000-0000-1234-567890abcdef\\"",'
                b'"_rid":"abc==","_self":"dbs/x/colls/y/docs/order-42","_ts":1746700000}'
            ),
            diagnostics=None,
        )
    )

    helper = ItemHelper(backend)
    result = call_create_item_helper(helper,
        container_link="dbs/x/colls/y",
        body={"id": "order-42", "pk": "customerA"},
    )

    # The result is a dict, so the caller reads fields by key.
    assert result["_etag"] == '"00000000-0000-0000-1234-567890abcdef"'
    assert result["id"] == "order-42"
    # The helper actually built and dispatched the prepared request to the backend.
    assert backend.captured is not None
    assert backend.captured.op == "create_item"


# NOTE: An older test for a "core-python backend" was removed when the core-python
# choice was represented purely by ``None``. The explicit
# ``LegacyBackend`` now exists again (see ``azure.cosmos._backend.legacy``): the
# item helper coerces a ``None`` selection to it so "use the existing client" runs
# through the same ``run_operation`` interface as Rust. Its own behavior is
# covered in test_legacy_backend_unit.py; the item-helper legacy path is covered
# by the fall-through tests in test_item_helper_unit.py.


def test_dataclasses_are_frozen():
    """Assignments to the tested request/response dataclass fields raise."""
    p = PreparedRequest(
        op="create_item",
        container_link="dbs/d/colls/c",
        body_bytes=b"{}",
        partition_key=key_from_legacy_header('["customerA"]'),
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
# PreparedClientConfig, and the backend hands it to acquire_driver_handle as the third
# argument. With nothing to carry, that third argument is None.

def test_build_client_config_returns_none_when_nothing_to_carry():
    """Absent or empty preferred locations alone produce no client config."""
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
    """Assigning a prepared configuration field raises FrozenInstanceError."""
    config = PreparedClientConfig(preferred_locations=("West US",))
    with pytest.raises(Exception):  # FrozenInstanceError
        setattr(config, "preferred_locations", ("East US",))


def test_native_driver_identity_distinguishes_every_config_field():
    """Every declared behavior-affecting field participates in the actual native key."""
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
        "connection_timeout_seconds": 1.5,
        "read_timeout_seconds": 30.0,
        "fault_injection_rules": (
            PreparedFaultInjectionRule(id="identity-check", operation_type="CreateItem", status_code=502),
        ),
    }

    field_names = {f.name for f in dataclasses.fields(PreparedClientConfig)}
    assert field_names == set(variants), (
        "PreparedClientConfig fields changed; update the `variants` map so the "
        "native identity guard covers every behavior-affecting field. "
        "Missing from test: {}; stale in test: {}".format(
            field_names - set(variants), set(variants) - field_names
        )
    )

    baseline = PreparedClientConfig()
    url = "https://config-identity.invalid"
    baseline_identity = make_driver_identity(url, "key", baseline, None)
    assert baseline_identity == make_driver_identity(url, "key", None, None)
    for name, value in variants.items():
        changed = dataclasses.replace(baseline, **{name: value})
        assert make_driver_identity(url, "key", changed, None) != baseline_identity, (
            "Changing field {!r} did not change native identity; "
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
    assert isinstance(with_locations, RustBinding)
    assert with_locations._client_config == PreparedClientConfig(
        preferred_locations=("West US", "East US")
    )

    without = make_backend(
        BACKEND_NAME_RUST, url="https://y.documents.azure.com", credential="k"
    )
    assert isinstance(without, RustBinding)
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
    assert isinstance(backend, AsyncRustBinding)
    assert backend._client_config == PreparedClientConfig(
        preferred_locations=("West US",)
    )


def test_sync_factory_carries_transport_timeouts_into_rust_backend(monkeypatch):
    """Prove sync backend creation preserves transport timeouts."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    backend = make_backend(
        BACKEND_NAME_RUST,
        url="https://timeouts-sync.documents.azure.com",
        credential="k",
        connection_timeout_seconds=2.5,
        read_timeout_seconds=45,
    )
    assert isinstance(backend, RustBinding)
    assert backend._client_config == PreparedClientConfig(
        connection_timeout_seconds=2.5,
        read_timeout_seconds=45.0,
    )


def test_async_factory_carries_transport_timeouts_into_rust_backend(monkeypatch):
    """Prove async backend creation preserves transport timeouts."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    backend = make_async_backend(
        BACKEND_NAME_RUST,
        url="https://timeouts-async.documents.azure.com",
        credential="k",
        connection_timeout_seconds=1.5,
        read_timeout_seconds=30,
    )
    assert isinstance(backend, AsyncRustBinding)
    assert backend._client_config == PreparedClientConfig(
        connection_timeout_seconds=1.5,
        read_timeout_seconds=30.0,
    )


def test_untuned_sync_client_carries_no_transport_timeouts(monkeypatch):
    """The untuned Python client carries no explicit native configuration.

    This does not initialize the native runtime. An untuned client that later
    initializes it can still freeze native defaults.
    """
    monkeypatch.setattr(
        sync_cosmos_client_module, "CosmosClientConnection", MagicMock()
    )
    client = sync_cosmos_client_module.CosmosClient(
        "https://client-sync.documents.azure.com",
        "key",
        _backend=BACKEND_NAME_RUST,
    )
    assert client._backend._client_config is None
    client._backend.close()


@pytest.mark.asyncio
async def test_async_client_carries_explicit_transport_timeouts(monkeypatch):
    """Prove async clients pass explicit transport timeouts to Rust."""
    monkeypatch.setattr(
        async_cosmos_client_module, "CosmosClientConnection", MagicMock()
    )
    client = async_cosmos_client_module.CosmosClient(
        "https://client-async.documents.azure.com",
        "key",
        _backend=BACKEND_NAME_RUST,
        connection_timeout=2.0,
        read_timeout=30.0,
    )
    assert client._backend._client_config == PreparedClientConfig(
        connection_timeout_seconds=2.0,
        read_timeout_seconds=30.0,
    )
    await client._backend.close()


def test_rust_backend_passes_client_config_to_acquire_driver_handle(monkeypatch):
    """The backend hands the client config to acquire_driver_handle as the third argument
    so the binding can apply it when it builds the driver."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    monkeypatch.setattr("azure.cosmos._backend.binding._rust_module", fake_module)

    config = PreparedClientConfig(preferred_locations=("West US", "East US"))
    backend = RustBinding(
        endpoint="https://x.documents.azure.com",
        master_key="k",
        client_config=config,
    )
    backend._ensure_driver_handle()

    fake_module.acquire_driver_handle.assert_called_once_with(
        "https://x.documents.azure.com", "k", config
    )


def test_async_rust_backend_passes_client_config_to_acquire_driver_handle(monkeypatch):
    """Async version: the config rides on the acquire_driver_handle call the same way."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    monkeypatch.setattr("azure.cosmos.aio._backend.binding._rust_module", fake_module)

    config = PreparedClientConfig(preferred_locations=("West US",))

    async def _run():
        backend = AsyncRustBinding(
            endpoint="https://x.documents.azure.com",
            master_key="k",
            client_config=config,
        )
        await backend._ensure_driver_handle()

    asyncio.run(_run())

    fake_module.acquire_driver_handle.assert_called_once_with(
        "https://x.documents.azure.com", "k", config
    )


class _ProxyGlobalRuntimeFakeModule:
    """Fake Rust module to test process-global proxy policy.

    The first client sets the proxy policy for the process. Later clients must
    use the same policy or leave it unset.
    """

    def __init__(self):
        """Start with no proxy choice recorded and no drivers handed out yet."""
        self._initialized_proxy_allowed = None
        self._next_driver_handle = 0

    def acquire_driver_handle(self, *args):
        """Model a proxy-policy conflict and return a distinct synthetic handle.

        This test double is not a full native runtime or driver cache.
        """
        config = args[2] if len(args) >= 3 else None
        requested = getattr(config, "proxy_allowed", None) if config is not None else None
        if self._initialized_proxy_allowed is None:
            self._initialized_proxy_allowed = requested
        elif requested is not None and requested != self._initialized_proxy_allowed:
            raise ValueError(
                "Rust runtime proxy configuration is process-global and was already initialized"
            )
        self._next_driver_handle += 1
        return "handle-{}".format(self._next_driver_handle)

    def release_driver_handle(self, _driver_handle):
        """Accept a release and do nothing, so closing a client is never what fails a test."""
        return None


def test_rust_backend_conflicting_proxy_allowed_raises_at_construction(monkeypatch):
    """Sync path: conflicting proxy policy fails at client construction."""
    fake_module = _ProxyGlobalRuntimeFakeModule()
    monkeypatch.setattr("azure.cosmos._backend.binding._rust_module", fake_module)

    first = RustBinding(
        endpoint="https://x.documents.azure.com",
        master_key="k",
        client_config=PreparedClientConfig(proxy_allowed=True),
    )
    with pytest.raises(ProxyPolicyConflictError, match="process-global"):
        RustBinding(
            endpoint="https://x.documents.azure.com",
            master_key="k",
            client_config=PreparedClientConfig(proxy_allowed=False),
        )
    first.close()


def test_rust_backend_unset_proxy_allowed_does_not_conflict(monkeypatch):
    """Sync path: an unset later value carries nothing and does not conflict."""
    fake_module = _ProxyGlobalRuntimeFakeModule()
    monkeypatch.setattr("azure.cosmos._backend.binding._rust_module", fake_module)

    first = RustBinding(
        endpoint="https://x.documents.azure.com",
        master_key="k",
        client_config=PreparedClientConfig(proxy_allowed=True),
    )
    second = RustBinding(
        endpoint="https://x.documents.azure.com",
        master_key="k",
        client_config=None,
    )

    first._ensure_driver_handle()
    second._ensure_driver_handle()


def test_async_rust_backend_conflicting_proxy_allowed_raises_at_construction(monkeypatch):
    """Async path: conflicting proxy policy fails at client construction."""
    fake_module = _ProxyGlobalRuntimeFakeModule()
    monkeypatch.setattr("azure.cosmos.aio._backend.binding._rust_module", fake_module)

    async def _run():
        first = AsyncRustBinding(
            endpoint="https://x.documents.azure.com",
            master_key="k",
            client_config=PreparedClientConfig(proxy_allowed=True),
        )
        with pytest.raises(ProxyPolicyConflictError, match="process-global"):
            AsyncRustBinding(
                endpoint="https://x.documents.azure.com",
                master_key="k",
                client_config=PreparedClientConfig(proxy_allowed=False),
            )
        await first.close()

    asyncio.run(_run())


# ---------------------------------------------------------------------------
# Carrying the other driver-understood startup settings (excluded_locations,
# throttling retry, hedging threshold) into the client config
# ---------------------------------------------------------------------------
#
# These ride the same PreparedClientConfig the binding reads at acquire_driver_handle time.
# Each is carried only when the customer actually expressed it, so an untuned
# client still produces no config; the binding receives None as its third argument.


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
    """No threshold/config tells the binding to explicitly disable hedging."""
    assert build_client_config(None, availability_strategy=False) is None


def test_build_client_config_hedging_none_carries_nothing():
    """An absent strategy uses the binding's disabled Python-client default."""
    assert build_client_config(None, availability_strategy=None) is None


@pytest.mark.parametrize("module", [sync_cosmos_client_module, async_cosmos_client_module],
                         ids=["sync", "async"])
@pytest.mark.parametrize("extra_options", [{}, {"preferred_locations": ["West US"]}])
@pytest.mark.parametrize("options,threshold", [
    ({}, None),
    ({"availability_strategy": False}, None),
    ({"availability_strategy": None}, None),
    ({"availability_strategy": True}, 500),
    ({"availability_strategy": {"threshold_ms": 25}}, 25),
])
def test_public_constructor_preserves_hedging_choice(module, extra_options, options, threshold, monkeypatch):
    """The hedging choice survives the trip through the real client constructor, on both
    clients and alongside other settings.

    The tests just above check the setting is built correctly in isolation. This one
    checks it actually arrives, because the constructor is where a setting gets dropped
    by being read under the wrong name or overwritten by a later step.

    Sending a second copy of a request early is a cost-for-latency trade, so both
    directions matter: losing the choice makes requests slower than the customer asked
    for, and inventing one makes them pay for requests they never asked to send. Asking
    for nothing, asking for it off, and asking for it off by name must all end with
    nothing pinned rather than an explicit off.

    The second set of settings is there to check the two do not interfere -- a
    constructor that builds the configuration afresh for one of them would drop the
    other. No driver is acquired, so this never reaches the network.
    """
    monkeypatch.setattr(module, "CosmosClientConnection", MagicMock())
    client = module.CosmosClient(
        "https://hedging.invalid", "ZmFrZQ==", _backend="rust", **extra_options, **options
    )
    try:
        config = client._backend._client_config
        assert (config.hedging_threshold_ms if config is not None else None) == threshold
        assert client._backend._driver_handle is None
        if extra_options:
            assert config.preferred_locations == ("West US",)
    finally:
        result = client._backend.close()
        if inspect.isawaitable(result):
            asyncio.run(result)


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
        connection_timeout_seconds=2.5,
        read_timeout_seconds=45,
    )
    assert config == PreparedClientConfig(
        preferred_locations=("West US",),
        excluded_locations=("Central US",),
        throttling_max_retry_count=5,
        throttling_max_retry_wait_time_seconds=12,
        hedging_threshold_ms=25,
        user_agent_suffix="checkout-westus2",
        consistency_level="Eventual",
        connection_timeout_seconds=2.5,
        read_timeout_seconds=45.0,
    )


def test_resolve_client_transport_timeouts_reports_only_explicit_values():
    """A customer who named no timeout gets None, not the legacy defaults.

    These two values configure the process-wide Rust driver runtime, so reporting
    a default here would pin the whole process to it on behalf of a customer who
    never asked for it.
    """
    assert resolve_client_transport_timeouts({}) == (None, None)
    assert resolve_client_transport_timeouts({"connection_timeout": 2}) == (2, None)
    assert resolve_client_transport_timeouts({"read_timeout": 30}) == (None, 30)


def test_resolve_client_transport_timeouts_ignores_a_stock_connection_policy():
    """The public clients build a default ConnectionPolicy for every client, so a
    policy that still holds the stock values is not a customer choice."""
    assert resolve_client_transport_timeouts(
        {"connection_policy": ConnectionPolicy()}
    ) == (None, None)


def test_resolve_client_transport_timeouts_honors_alias_and_custom_policy():
    """The legacy millisecond alias keeps precedence and policy defaults still apply."""
    policy = ConnectionPolicy()
    policy.RequestTimeout = 3
    policy.ReadTimeout = 40
    assert resolve_client_transport_timeouts(
        {
            "connection_policy": policy,
            "connection_timeout": 2,
            "request_timeout": 750,
        }
    ) == (0.75, 40)


def test_build_client_config_carries_transport_timeouts():
    """Prove Rust client configuration includes transport timeouts."""
    config = build_client_config(
        None,
        connection_timeout_seconds=1.25,
        read_timeout_seconds=42.5,
    )
    assert config == PreparedClientConfig(
        connection_timeout_seconds=1.25,
        read_timeout_seconds=42.5,
    )


@pytest.mark.parametrize(
    "kwargs, message",
    [
        ({"connection_timeout_seconds": 0.05}, "at least 0.1"),
        ({"connection_timeout_seconds": 7}, "at most 6.0"),
        ({"read_timeout_seconds": 0}, "at least 0.1"),
        ({"read_timeout_seconds": float("inf")}, "must be finite"),
    ],
)
def test_build_client_config_rejects_driver_unsupported_transport_timeouts(
    kwargs, message
):
    """Prove unsupported timeout values fail instead of changing silently."""
    with pytest.raises(ValueError, match=message):
        build_client_config(None, **kwargs)


def test_build_client_config_carries_user_agent_suffix():
    """The prepared config retains the supplied suffix; no HTTP header is inspected."""
    config = build_client_config(None, user_agent_suffix="checkout-westus2")
    assert isinstance(config, PreparedClientConfig)
    assert config.user_agent_suffix == "checkout-westus2"


def test_build_client_config_only_user_agent_suffix_still_builds_config():
    """A suffix alone produces a config rather than None."""
    config = build_client_config(None, user_agent_suffix="order-service")
    assert config == PreparedClientConfig(user_agent_suffix="order-service")


def test_build_client_config_empty_user_agent_suffix_is_none():
    """An empty string (or absent) suffix carries nothing, like an empty location
    list, so an untuned client still produces no config."""
    assert build_client_config(None, user_agent_suffix="") is None
    assert build_client_config(None, user_agent_suffix=None) is None


@pytest.mark.parametrize("level", ["Eventual", "Session", "Strong"])
def test_build_client_config_carries_supported_consistency_level(level):
    """Each listed consistency name is retained in the prepared config."""
    config = build_client_config(None, consistency_level=level)
    assert config == PreparedClientConfig(consistency_level=level)


def test_build_client_config_only_consistency_still_builds_config():
    """A consistency setting alone produces a config rather than None."""
    config = build_client_config(None, consistency_level="Session")
    assert isinstance(config, PreparedClientConfig)
    assert config.consistency_level == "Session"


def test_build_client_config_no_consistency_carries_nothing():
    """An absent or empty consistency value leaves the config field unset."""
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
    """Unset proxy values do not reserve or conflict in the Python registry.

    No native runtime is initialized here. Native initialization with defaults
    is different from leaving a provisional Python reservation unset.
    """
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


def test_register_transport_timeout_policy_accepts_equal_values():
    """The Python policy registry accepts matching explicit timeout values."""
    config = build_client_config(
        None,
        connection_timeout_seconds=5,
        read_timeout_seconds=65,
    )
    register_transport_timeout_policy(config)
    register_transport_timeout_policy(config)


@pytest.mark.parametrize(
    "first, second",
    [
        ((5, 65), (4, 65)),
        ((5, 65), (5, 30)),
    ],
)
def test_register_transport_timeout_policy_rejects_conflicts(first, second):
    """The Python policy registry rejects differing explicit timeout values."""
    register_transport_timeout_policy(
        build_client_config(
            None,
            connection_timeout_seconds=first[0],
            read_timeout_seconds=first[1],
        )
    )
    with pytest.raises(TransportTimeoutPolicyConflictError, match="process-global"):
        register_transport_timeout_policy(
            build_client_config(
                None,
                connection_timeout_seconds=second[0],
                read_timeout_seconds=second[1],
            )
        )


@pytest.mark.parametrize("level", ["BoundedStaleness", "ConsistentPrefix"])
def test_build_client_config_rejects_unsupported_consistency_level(level):
    """This Python Rust-backend configuration rejects the two listed levels."""
    with pytest.raises(ValueError, match="not yet supported by the Rust binding"):
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
    assert isinstance(backend, RustBinding)
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
    assert isinstance(backend, AsyncRustBinding)
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
    """The explicit legacy backend leaves the core-python path unchanged."""
    assert raise_account_read_unsupported(LEGACY_BACKEND) is None


def test_account_read_guard_raises_for_rust_backend():
    """The Rust backend gets a clear not-yet-available error."""
    backend = MagicMock(name=BACKEND_NAME_RUST)
    backend.name = BACKEND_NAME_RUST
    with pytest.raises(NotImplementedError, match="not yet available through the Rust binding"):
        raise_account_read_unsupported(backend)


# ---------------------------------------------------------------------------
# Credential classification for the Rust backend (resolve_credential)
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
        """Return a fixed token with an expiry far in the future.

        Not awaited, which is what makes this the synchronous shape. The expiry is set
        far out so nothing here ever decides the token needs renewing.
        """
        return ("token-value", 9999999999)


class _AsyncTokenCredential:
    """A stand-in for an async credential, which the Rust backend wraps in a
    synchronous bridge."""

    async def get_token(self, *scopes, **kwargs):  # noqa: D401
        """The same fixed token, but awaited.

        Being awaited is the whole difference from the class above, and it is what the
        code under test looks for when deciding this one needs a bridge.
        """
        return ("token-value", 9999999999)


class _AsyncTokenInfoCredential:
    """An async credential that authenticates only through the newer
    ``get_token_info`` (azure-core ``SupportsTokenInfo``), with no ``get_token``.
    The Rust backend detects it as async and wraps it; the bridge drives
    ``get_token_info``."""

    async def get_token_info(self, *scopes, **kwargs):  # noqa: D401
        """The newer way to ask for a token, and the only one this credential offers.

        Deliberately without the older method, so code that only knows to look for that
        one would find nothing here and treat this as not a credential at all.
        """
        return ("token-value", 9999999999)


class _AsyncContextManagerCredential:
    """An ``azure.identity.aio``-shaped credential: an async context manager whose
    token method is async. Detected as async via the context-manager check."""

    async def __aenter__(self):
        """Enter as a context manager, which is the mark the code reads to tell this is
        asynchronous."""
        return self

    async def __aexit__(self, *exc):
        """Leave without doing anything; there is nothing real to shut down here."""
        return None

    async def get_token(self, *scopes, **kwargs):  # noqa: D401
        """The same fixed token, awaited like the real one from the identity library."""
        return ("token-value", 9999999999)


def test_resolve_credential_master_key_string():
    """A plain string credential is read as a master key, with no token credential."""
    assert resolve_credential("the-key") == ("the-key", None)


def test_resolve_credential_master_key_dict():
    """A ``{"masterKey": ...}`` dict is read as a master key, with no token credential."""
    assert resolve_credential({"masterKey": "the-key"}) == ("the-key", None)


def test_resolve_credential_sync_token_credential():
    """A sync token credential passes through as the token credential (no master key)."""
    cred = _SyncTokenCredential()
    master_key, token_credential = resolve_credential(cred)
    assert master_key is None
    assert token_credential is cred


def test_resolve_credential_async_token_credential_wrapped():
    """An async credential is accepted: it is wrapped in a bridge that
    drives its coroutine and exposes a synchronous get_token."""
    cred = _AsyncTokenCredential()
    master_key, token_credential = resolve_credential(cred)
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
    master_key, token_credential = resolve_credential(cred)
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
    master_key, token_credential = resolve_credential(cred)
    assert master_key is None
    assert isinstance(token_credential, AsyncTokenCredentialBridge)
    token_credential._close_cosmos_async_bridge()


def test_async_credential_bridge_close_is_idempotent():
    """A directly constructed, unshared bridge tolerates repeated close calls.

    Close before first use is also exercised. This does not test duplicate
    releases of an acquired bridge that still has other holders.
    """
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
        """Set up the signal a test waits on to know the token request has really begun."""
        self.started = threading.Event()

    async def get_token(self, *scopes, **kwargs):  # noqa: D401
        """Announce that the request started, then wait forever.

        This stands for a credential that has stopped responding -- an identity service
        that is unreachable, say. Waiting forever rather than failing is the awkward
        case, because there is nothing to notice unless something else puts a limit on
        the wait.

        The signal matters: without it a test could close the bridge before the request
        had begun and pass without exercising anything.
        """
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
        """Wait a moment, then return the fixed token.

        The pause is what makes overlap possible: it leaves a window in which several
        callers are waiting at once and a close can arrive in the middle of them.
        """
        await asyncio.sleep(0.01)
        return ("token-value", 9999999999)


def test_async_credential_bridge_dedups_same_credential_with_refcount():
    """The same async credential reused across clients yields one shared bridge,
    refcounted so only the last close tears the loop down."""
    cred = _AsyncTokenCredential()
    _, b1 = resolve_credential(cred)
    _, b2 = resolve_credential(cred)
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
        _, b3 = resolve_credential(cred)
        assert b3 is not b1
        b3._close_cosmos_async_bridge()
    finally:
        # Defensive: ensure nothing is left registered if an assert fired early.
        b1._close_cosmos_async_bridge()


def test_async_credential_bridge_distinct_credentials_get_distinct_bridges():
    """Two credential objects produce distinct Python bridges; no drivers are built."""
    c1 = _AsyncTokenCredential()
    c2 = _AsyncTokenCredential()
    _, b1 = resolve_credential(c1)
    _, b2 = resolve_credential(c2)
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
    master_key, token_credential = resolve_credential(cred)
    assert master_key is None
    assert token_credential is cred


def test_resolve_credential_resource_token_map_rejected_with_specific_message():
    """A {resource-link: token} map (per-user scoped tokens) is rejected with the
    resource-token message, not the generic one."""
    with pytest.raises(ValueError, match="resource-token"):
        resolve_credential({"dbs/x/colls/y": "resource-token"})


def test_resolve_credential_permission_feed_rejected_with_specific_message():
    """A permission feed (iterable of permission mappings) is rejected as a
    resource-token credential."""
    with pytest.raises(ValueError, match="resource-token"):
        resolve_credential([{"id": "perm", "_token": "t", "resource": "dbs/x"}])


def test_resolve_credential_none_rejected():
    """No credential is rejected: the Rust backend requires a master key or a token
    credential."""
    with pytest.raises(ValueError, match="master-key credential"):
        resolve_credential(None)


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
    assert isinstance(backend, RustBinding)
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
    assert isinstance(backend, AsyncRustBinding)
    assert backend._master_key is None
    assert backend._token_credential is cred


def test_make_backend_wraps_async_token_credential(monkeypatch):
    """The factory stores a bridge and no master key for an async credential.

    Constructing the backend does not prove that the credential can authenticate.
    """
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    cred = _AsyncTokenCredential()
    backend = make_backend(
        BACKEND_NAME_RUST,
        url="https://x.documents.azure.com",
        credential=cred,
    )
    assert isinstance(backend, RustBinding)
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
    assert isinstance(backend, AsyncRustBinding)
    assert backend._master_key is None
    assert isinstance(backend._token_credential, AsyncTokenCredentialBridge)


def test_rust_backend_passes_token_credential_to_acquire_driver_handle(monkeypatch):
    """With a token credential, acquire_driver_handle is called as (endpoint, None, config,
    credential) -- master key None, credential as the 4th argument."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    monkeypatch.setattr("azure.cosmos._backend.binding._rust_module", fake_module)

    cred = _SyncTokenCredential()
    backend = RustBinding(
        endpoint="https://x.documents.azure.com",
        token_credential=cred,
    )
    backend._ensure_driver_handle()

    fake_module.acquire_driver_handle.assert_called_once_with(
        "https://x.documents.azure.com", None, None, cred
    )


def test_async_rust_backend_passes_token_credential_to_acquire_driver_handle(monkeypatch):
    """Async version: the token credential rides as the 4th acquire_driver_handle arg."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    monkeypatch.setattr("azure.cosmos.aio._backend.binding._rust_module", fake_module)

    cred = _SyncTokenCredential()

    async def _run():
        backend = AsyncRustBinding(
            endpoint="https://x.documents.azure.com",
            token_credential=cred,
        )
        await backend._ensure_driver_handle()

    asyncio.run(_run())

    fake_module.acquire_driver_handle.assert_called_once_with(
        "https://x.documents.azure.com", None, None, cred
    )


# ---------------------------------------------------------------------------
# How a container call picks its backend
# ---------------------------------------------------------------------------
#
# The client always puts a concrete backend on the connection. A container call
# uses that backend, and the choice is made once per client.

def _make_sync_container_with_backend(backend):
    """Construct the real, connection-free proxy around a selected test backend."""
    mock_cc = MagicMock()
    mock_cc._backend = backend
    from azure.cosmos._helpers._item_context import ItemClientContext
    return ContainerProxy(mock_cc, "dbs/test", "test", _item_context=ItemClientContext(backend))


def _new_rust_backend():
    """Build a Rust backend with a throwaway endpoint and key. The tests fake
    the compiled module so nothing real runs."""
    return RustBinding(endpoint="https://x.documents.azure.com", master_key="k")


def _new_async_rust_backend():
    """Build an async Rust backend with standard fake dependencies."""
    return AsyncRustBinding(endpoint="https://x.documents.azure.com", master_key="k")


def test_container_dispatch_routes_to_rust_backend(monkeypatch):
    """A call on a Rust client reaches the Rust backend, shown by the faked
    module being called."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "h"
    fake_module.create_item.return_value = (201, 0, {}, b"{}")
    fake_module.get_container_metadata.return_value = ("rid", (), None, None)
    monkeypatch.setattr("azure.cosmos._backend.binding._rust_module", fake_module)

    container = _make_sync_container_with_backend(_new_rust_backend())
    container.create_item(body={"id": "x", "pk": "a"})
    assert fake_module.create_item.called, "Rust path should have been taken"


def test_container_dispatch_rejects_missing_backend():
    """A connection without the required concrete backend fails explicitly."""
    bare_cc = MagicMock(spec=[])  # a connection with no backend set at all
    container = ContainerProxy(bare_cc, "dbs/test", "test")
    with pytest.raises(RuntimeError, match="context supplied by CosmosClient"):
        container.create_item(body={"id": "x", "pk": "a"})


def test_async_container_dispatch_routes_to_async_rust_backend(monkeypatch):
    """Async version: a call on a Rust client reaches the Rust backend."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "h"
    fake_module.create_item_async = AsyncMock(return_value=(201, 0, {}, b"{}"))
    fake_module.get_container_metadata_async = AsyncMock(return_value=("rid", (), None, None))
    monkeypatch.setattr("azure.cosmos.aio._backend.binding._rust_module", fake_module)

    mock_cc = MagicMock()
    mock_cc._backend = _new_async_rust_backend()
    from azure.cosmos._helpers._item_context import ItemClientContext
    container = AsyncContainerProxy(
        mock_cc, "dbs/test", "test", _item_context=ItemClientContext(mock_cc._backend)
    )

    async def _run():
        await container.create_item(body={"id": "x", "pk": "a"})
        assert fake_module.create_item_async.called, "async Rust path should have been taken"

    asyncio.run(_run())


# Exercise read_feed_ranges through the public methods with fake bindings,
# including force_refresh and malformed payloads. Backend eligibility depends
# on the particular option, not merely whether any keyword was supplied.
def test_container_read_feed_ranges_routes_to_rust_backend(monkeypatch):
    """The force_refresh call reaches the fake Rust binding, not the legacy map."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "h"
    fake_module.read_feed_ranges.return_value = (
        200,
        0,
        {},
        b'{"PartitionKeyRanges":[{"id":"0","minInclusive":"","maxExclusive":"FF"}]}',
    )
    monkeypatch.setattr("azure.cosmos._backend.binding._rust_module", fake_module)

    container = _make_sync_container_with_backend(_new_rust_backend())
    container.client_connection._routing_map_provider = MagicMock()

    feed_ranges = list(container.read_feed_ranges(force_refresh=True))
    assert len(feed_ranges) == 1
    assert fake_module.read_feed_ranges.called
    assert not container.client_connection.refresh_routing_map_provider.called
    assert not container.client_connection._routing_map_provider.get_overlapping_ranges.called

    prepared = fake_module.read_feed_ranges.call_args.args[1]
    assert prepared.op == OP_READ_FEED_RANGES
    assert prepared.container_link == "dbs/test/colls/test"
    assert prepared.body_bytes == b'{"forceRefresh":true}'


def test_container_read_feed_ranges_with_kwargs_falls_back_to_legacy(monkeypatch):
    """Any extra kwargs keep read_feed_ranges on legacy routing-map provider."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "h"
    fake_module.read_feed_ranges.return_value = (
        200,
        0,
        {},
        b'{"PartitionKeyRanges":[{"id":"0","minInclusive":"","maxExclusive":"FF"}]}',
    )
    monkeypatch.setattr("azure.cosmos._backend.binding._rust_module", fake_module)

    container = _make_sync_container_with_backend(_new_rust_backend())
    container.client_connection._routing_map_provider = MagicMock()
    container.client_connection._routing_map_provider.get_overlapping_ranges.return_value = [
        {"id": "0", "minInclusive": "", "maxExclusive": "FF"}
    ]
    container._get_properties_with_options = MagicMock(return_value={})
    setattr(
        container,
        "_ContainerProxy__get_client_container_caches",
        lambda: {container.container_link: {"_rid": "rid-1"}},
    )

    feed_ranges = list(container.read_feed_ranges(force_refresh=True, excluded_locations=["West US"]))
    assert len(feed_ranges) == 1
    assert not fake_module.read_feed_ranges.called
    container.client_connection.refresh_routing_map_provider.assert_called_once()
    container.client_connection._routing_map_provider.get_overlapping_ranges.assert_called_once()


def test_container_read_feed_ranges_rust_payload_must_include_partition_key_ranges(monkeypatch):
    """Malformed Rust payload is rejected loudly instead of returning silent empty data."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "h"
    fake_module.read_feed_ranges.return_value = (200, 0, {}, b'{"unexpected":[]}')
    monkeypatch.setattr("azure.cosmos._backend.binding._rust_module", fake_module)

    container = _make_sync_container_with_backend(_new_rust_backend())
    with pytest.raises(ValueError, match="PartitionKeyRanges"):
        list(container.read_feed_ranges())


def test_async_container_read_feed_ranges_routes_to_rust_backend(monkeypatch):
    """Async read_feed_ranges uses Rust backend when available and kwargs are empty."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "h"
    fake_module.read_feed_ranges_async = AsyncMock(
        return_value=(
            200,
            0,
            {},
            b'{"PartitionKeyRanges":[{"id":"0","minInclusive":"","maxExclusive":"FF"}]}',
        )
    )
    monkeypatch.setattr("azure.cosmos.aio._backend.binding._rust_module", fake_module)

    mock_cc = MagicMock()
    mock_cc._backend = _new_async_rust_backend()
    mock_cc._routing_map_provider = MagicMock()
    mock_cc.refresh_routing_map_provider = AsyncMock()
    container = AsyncContainerProxy.__new__(AsyncContainerProxy)
    container.client_connection = mock_cc
    container.id = "test"
    container.database_link = "dbs/test"
    container.container_link = "dbs/test/colls/test"

    async def _run():
        return [feed_range async for feed_range in container.read_feed_ranges(force_refresh=True)]

    feed_ranges = asyncio.run(_run())
    assert len(feed_ranges) == 1
    assert fake_module.read_feed_ranges_async.await_count == 1
    mock_cc.refresh_routing_map_provider.assert_not_awaited()
    assert not mock_cc._routing_map_provider.get_overlapping_ranges.called

    prepared = fake_module.read_feed_ranges_async.await_args.args[1]
    assert prepared.op == OP_READ_FEED_RANGES
    assert prepared.container_link == "dbs/test/colls/test"
    assert prepared.body_bytes == b'{"forceRefresh":true}'


def test_async_container_read_feed_ranges_with_kwargs_falls_back_to_legacy(monkeypatch):
    """Async read_feed_ranges keeps legacy path when caller passes extra kwargs."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "h"
    fake_module.read_feed_ranges_async = AsyncMock(
        return_value=(
            200,
            0,
            {},
            b'{"PartitionKeyRanges":[{"id":"0","minInclusive":"","maxExclusive":"FF"}]}',
        )
    )
    monkeypatch.setattr("azure.cosmos.aio._backend.binding._rust_module", fake_module)

    mock_cc = MagicMock()
    mock_cc._backend = _new_async_rust_backend()
    mock_cc._routing_map_provider = MagicMock()
    mock_cc._routing_map_provider.get_overlapping_ranges = AsyncMock(
        return_value=[{"id": "0", "minInclusive": "", "maxExclusive": "FF"}]
    )
    mock_cc.refresh_routing_map_provider = AsyncMock()
    container = AsyncContainerProxy.__new__(AsyncContainerProxy)
    container.client_connection = mock_cc
    container.id = "test"
    container.database_link = "dbs/test"
    container.container_link = "dbs/test/colls/test"
    container._get_properties_with_options = AsyncMock(return_value={})
    setattr(
        container,
        "_ContainerProxy__get_client_container_caches",
        lambda: {container.container_link: {"_rid": "rid-1"}},
    )

    async def _run():
        return [
            feed_range
            async for feed_range in container.read_feed_ranges(
                force_refresh=True, excluded_locations=["West US"]
            )
        ]

    feed_ranges = asyncio.run(_run())
    assert len(feed_ranges) == 1
    assert fake_module.read_feed_ranges_async.await_count == 0
    mock_cc.refresh_routing_map_provider.assert_awaited_once()
    mock_cc._routing_map_provider.get_overlapping_ranges.assert_awaited_once()


def test_async_container_read_feed_ranges_rust_payload_must_include_partition_key_ranges(monkeypatch):
    """Async malformed Rust payload is rejected loudly."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "h"
    fake_module.read_feed_ranges_async = AsyncMock(return_value=(200, 0, {}, b'{"unexpected":[]}'))
    monkeypatch.setattr("azure.cosmos.aio._backend.binding._rust_module", fake_module)

    mock_cc = MagicMock()
    mock_cc._backend = _new_async_rust_backend()
    container = AsyncContainerProxy.__new__(AsyncContainerProxy)
    container.client_connection = mock_cc
    container.id = "test"
    container.database_link = "dbs/test"
    container.container_link = "dbs/test/colls/test"

    async def _run():
        return [feed_range async for feed_range in container.read_feed_ranges()]

    with pytest.raises(ValueError, match="PartitionKeyRanges"):
        asyncio.run(_run())


def test_container_feed_range_from_partition_key_routes_to_rust_backend(monkeypatch):
    """feed_range_from_partition_key uses Rust backend when available."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "h"
    fake_module.feed_range_from_partition_key.return_value = (
        200,
        0,
        {},
        b'{"Range":{"min":"3C","max":"3C","isMinInclusive":true,"isMaxInclusive":true}}',
    )
    monkeypatch.setattr("azure.cosmos._backend.binding._rust_module", fake_module)

    container = _make_sync_container_with_backend(_new_rust_backend())
    container._get_properties = MagicMock(side_effect=AssertionError("legacy fallback should not run"))

    feed_range = container.feed_range_from_partition_key("pk-a")
    assert feed_range["Range"]["min"] == "3C"
    assert feed_range["Range"]["isMaxInclusive"] is True
    assert fake_module.feed_range_from_partition_key.called

    prepared = fake_module.feed_range_from_partition_key.call_args.args[1]
    assert prepared.op == OP_FEED_RANGE_FROM_PARTITION_KEY
    assert prepared.container_link == "dbs/test/colls/test"
    assert legacy_partition_key_from_request(prepared) == '["pk-a"]'
    assert prepared.body_bytes == b""


def test_container_feed_range_from_partition_key_rejects_malformed_rust_payload(monkeypatch):
    """A malformed Rust feed-range payload (missing the ``Range`` envelope) raises
    rather than handing back a broken feed range."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "h"
    fake_module.feed_range_from_partition_key.return_value = (200, 0, {}, b'{"unexpected":{}}')
    monkeypatch.setattr("azure.cosmos._backend.binding._rust_module", fake_module)

    container = _make_sync_container_with_backend(_new_rust_backend())
    with pytest.raises(ValueError, match="Range"):
        container.feed_range_from_partition_key("pk-a")


def test_container_feed_range_from_partition_key_empty_sentinel_routes_to_rust_backend(monkeypatch):
    """The empty-partition-key sentinel (``NonePartitionKeyValue``) routes to the Rust
    backend with a cross-partition header (``"[]"``) and returns the full-range feed
    range the driver reports."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "h"
    fake_module.feed_range_from_partition_key.return_value = (
        200,
        0,
        {},
        b'{"Range":{"min":"00000000000000000000000000000000","max":"00000000000000000000000000000000","isMinInclusive":true,"isMaxInclusive":true}}',
    )
    monkeypatch.setattr("azure.cosmos._backend.binding._rust_module", fake_module)

    container = _make_sync_container_with_backend(_new_rust_backend())
    container._get_properties = MagicMock(
        return_value={"partitionKey": {"paths": ["/pk"], "kind": "Hash", "version": 2, "systemKey": True}}
    )

    feed_range = container.feed_range_from_partition_key(NonePartitionKeyValue)

    assert feed_range["Range"]["min"] == "00000000000000000000000000000000"
    assert feed_range["Range"]["max"] == "00000000000000000000000000000000"
    assert feed_range["Range"]["isMinInclusive"] is True
    assert feed_range["Range"]["isMaxInclusive"] is True
    assert fake_module.feed_range_from_partition_key.call_count == 1
    prepared = fake_module.feed_range_from_partition_key.call_args.args[1]
    assert legacy_partition_key_from_request(prepared) == "[]"


def test_container_feed_range_from_partition_key_empty_sequence_routes_to_rust_backend(monkeypatch):
    """An explicit empty partition-key sequence (``[]``) also routes to the Rust
    backend and returns the driver's feed range."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "h"
    fake_module.feed_range_from_partition_key.return_value = (
        200,
        0,
        {},
        b'{"Range":{"min":"","max":"","isMinInclusive":true,"isMaxInclusive":false}}',
    )
    monkeypatch.setattr("azure.cosmos._backend.binding._rust_module", fake_module)

    container = _make_sync_container_with_backend(_new_rust_backend())
    container._get_properties = MagicMock(
        return_value={
            "partitionKey": {"paths": ["/tenant", "/region"], "kind": "MultiHash", "version": 2}
        }
    )

    feed_range = container.feed_range_from_partition_key([])

    assert feed_range["Range"]["min"] == ""
    assert feed_range["Range"]["max"] == ""
    assert feed_range["Range"]["isMinInclusive"] is True
    assert feed_range["Range"]["isMaxInclusive"] is False
    assert fake_module.feed_range_from_partition_key.call_count == 1
    prepared = fake_module.feed_range_from_partition_key.call_args.args[1]
    assert legacy_partition_key_from_request(prepared) == "[[]]"


def test_async_container_feed_range_from_partition_key_routes_to_rust_backend(monkeypatch):
    """Async feed_range_from_partition_key uses Rust backend when available."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "h"
    fake_module.feed_range_from_partition_key_async = AsyncMock(
        return_value=(
            200,
            0,
            {},
            b'{"Range":{"min":"3C","max":"3C","isMinInclusive":true,"isMaxInclusive":true}}',
        )
    )
    monkeypatch.setattr("azure.cosmos.aio._backend.binding._rust_module", fake_module)

    mock_cc = MagicMock()
    mock_cc._backend = _new_async_rust_backend()
    container = AsyncContainerProxy.__new__(AsyncContainerProxy)
    container.client_connection = mock_cc
    container.id = "test"
    container.database_link = "dbs/test"
    container.container_link = "dbs/test/colls/test"

    async def _run():
        return await container.feed_range_from_partition_key("pk-a")

    feed_range = asyncio.run(_run())
    assert feed_range["Range"]["min"] == "3C"
    assert feed_range["Range"]["isMaxInclusive"] is True
    assert fake_module.feed_range_from_partition_key_async.await_count == 1

    prepared = fake_module.feed_range_from_partition_key_async.await_args.args[1]
    assert prepared.op == OP_FEED_RANGE_FROM_PARTITION_KEY
    assert prepared.container_link == "dbs/test/colls/test"
    assert legacy_partition_key_from_request(prepared) == '["pk-a"]'
    assert prepared.body_bytes == b""


def test_async_container_feed_range_from_partition_key_rejects_malformed_rust_payload(monkeypatch):
    """Async twin: a malformed async Rust feed-range payload raises."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "h"
    fake_module.feed_range_from_partition_key_async = AsyncMock(
        return_value=(200, 0, {}, b'{"unexpected":{}}')
    )
    monkeypatch.setattr("azure.cosmos.aio._backend.binding._rust_module", fake_module)

    mock_cc = MagicMock()
    mock_cc._backend = _new_async_rust_backend()
    container = AsyncContainerProxy.__new__(AsyncContainerProxy)
    container.client_connection = mock_cc
    container.id = "test"
    container.database_link = "dbs/test"
    container.container_link = "dbs/test/colls/test"

    async def _run():
        return await container.feed_range_from_partition_key("pk-a")

    with pytest.raises(ValueError, match="Range"):
        asyncio.run(_run())


def test_async_container_feed_range_from_partition_key_empty_sentinel_routes_to_rust_backend(monkeypatch):
    """Async twin: the empty-partition-key sentinel routes to the async Rust backend
    with a cross-partition header."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "h"
    fake_module.feed_range_from_partition_key_async = AsyncMock(
        return_value=(
            200,
            0,
            {},
            b'{"Range":{"min":"00000000000000000000000000000000","max":"00000000000000000000000000000000","isMinInclusive":true,"isMaxInclusive":true}}',
        )
    )
    monkeypatch.setattr("azure.cosmos.aio._backend.binding._rust_module", fake_module)

    mock_cc = MagicMock()
    mock_cc._backend = _new_async_rust_backend()
    container = AsyncContainerProxy.__new__(AsyncContainerProxy)
    container.client_connection = mock_cc
    container.id = "test"
    container.database_link = "dbs/test"
    container.container_link = "dbs/test/colls/test"
    container._get_properties = AsyncMock(
        return_value={"partitionKey": {"paths": ["/pk"], "kind": "Hash", "version": 2, "systemKey": True}}
    )

    async def _run():
        return await container.feed_range_from_partition_key(NonePartitionKeyValue)

    feed_range = asyncio.run(_run())
    assert feed_range["Range"]["min"] == "00000000000000000000000000000000"
    assert feed_range["Range"]["max"] == "00000000000000000000000000000000"
    assert feed_range["Range"]["isMinInclusive"] is True
    assert feed_range["Range"]["isMaxInclusive"] is True
    assert fake_module.feed_range_from_partition_key_async.await_count == 1
    prepared = fake_module.feed_range_from_partition_key_async.await_args.args[1]
    assert legacy_partition_key_from_request(prepared) == "[]"


def test_async_container_feed_range_from_partition_key_empty_sequence_routes_to_rust_backend(monkeypatch):
    """Async twin: an explicit empty partition-key sequence routes to the async Rust
    backend."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "h"
    fake_module.feed_range_from_partition_key_async = AsyncMock(
        return_value=(
            200,
            0,
            {},
            b'{"Range":{"min":"","max":"","isMinInclusive":true,"isMaxInclusive":false}}',
        )
    )
    monkeypatch.setattr("azure.cosmos.aio._backend.binding._rust_module", fake_module)

    mock_cc = MagicMock()
    mock_cc._backend = _new_async_rust_backend()
    container = AsyncContainerProxy.__new__(AsyncContainerProxy)
    container.client_connection = mock_cc
    container.id = "test"
    container.database_link = "dbs/test"
    container.container_link = "dbs/test/colls/test"
    container._get_properties_with_options = AsyncMock(
        return_value={
            "partitionKey": {"paths": ["/tenant", "/region"], "kind": "MultiHash", "version": 2}
        }
    )

    async def _run():
        return await container.feed_range_from_partition_key([])

    feed_range = asyncio.run(_run())
    assert feed_range["Range"]["min"] == ""
    assert feed_range["Range"]["max"] == ""
    assert feed_range["Range"]["isMinInclusive"] is True
    assert feed_range["Range"]["isMaxInclusive"] is False
    assert fake_module.feed_range_from_partition_key_async.await_count == 1
    prepared = fake_module.feed_range_from_partition_key_async.await_args.args[1]
    assert legacy_partition_key_from_request(prepared) == "[[]]"


# ---------------------------------------------------------------------------
# How get_selected_backend selects the backend off a client_connection
# ---------------------------------------------------------------------------
#
# get_selected_backend reads the ``_backend`` attribute off the connection. It reads
# the instance ``__dict__`` directly rather than creating a mock attribute.
# An unset backend violates the concrete-backend invariant and raises.
# A connection without ``__dict__`` (``__slots__``) is read via getattr.


class _PlainConnection:
    """A stand-in for client_connection with a real instance ``__dict__``."""


class _SlotsConnection:
    """A connection whose attributes live in ``__slots__`` (no ``__dict__``),
    exercising get_selected_backend's getattr fallback branch."""

    __slots__ = ("_backend",)


def test_pick_backend_returns_backend_when_set():
    """With ``_backend`` set, it is returned."""
    conn = _PlainConnection()
    backend = object()
    conn._backend = backend
    assert get_selected_backend(conn) is backend


def test_pick_backend_rejects_unset_backend():
    """A connection without ``_backend`` violates the invariant."""
    with pytest.raises(RuntimeError, match="concrete Cosmos backend"):
        get_selected_backend(_PlainConnection())


def test_pick_backend_uses_getattr_fallback_for_slots_connection():
    """A connection without ``__dict__`` (``__slots__``) is read via getattr."""
    conn = _SlotsConnection()
    backend = object()
    conn._backend = backend
    assert get_selected_backend(conn) is backend


# ---------------------------------------------------------------------------
# The client handle is built only once, even under concurrency
# ---------------------------------------------------------------------------
#
# The first call builds the handle; a lock makes sure that a burst of first
# calls builds it only once, instead of each building and discarding one.
# The measured acquisition count checks this run, not every possible schedule.


def test_rust_backend_init_driver_handle_serialised_under_concurrent_threads(monkeypatch):
    """Eight submitted calls produce one fake handle acquisition in this run."""
    count_lock = threading.Lock()
    calls = {"n": 0}

    def slow_init(_endpoint, _key, _config):
        with count_lock:
            calls["n"] += 1
        time.sleep(0.02)  # hold long enough for the others to queue up
        return "handle-1"

    fake_module = MagicMock()
    fake_module.acquire_driver_handle.side_effect = slow_init
    monkeypatch.setattr("azure.cosmos._backend.binding._rust_module", fake_module)

    backend = RustBinding(endpoint="https://x.documents.azure.com", master_key="k")
    ready = threading.Barrier(8)
    results = []

    def worker():
        ready.wait()  # start all eight at the same time
        results.append(backend._ensure_driver_handle())

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert calls["n"] == 1
    assert results == ["handle-1"] * 8


def test_async_rust_backend_init_driver_handle_serialised_under_concurrent_tasks(monkeypatch):
    """Eight coroutines starting at once build the handle only once."""
    count_lock = threading.Lock()
    calls = {"n": 0}

    def slow_init(_endpoint, _key, _config):
        with count_lock:
            calls["n"] += 1
        time.sleep(0.02)
        return "handle-1"

    fake_module = MagicMock()
    fake_module.acquire_driver_handle.side_effect = slow_init
    monkeypatch.setattr("azure.cosmos.aio._backend.binding._rust_module", fake_module)

    async def _run():
        backend = AsyncRustBinding(
            endpoint="https://x.documents.azure.com", master_key="k"
        )
        return await asyncio.gather(*[backend._ensure_driver_handle() for _ in range(8)])

    results = asyncio.run(_run())

    assert calls["n"] == 1
    assert results == ["handle-1"] * 8


def test_async_rust_backend_init_driver_handle_serialised_across_event_loops(monkeypatch):
    """Two loops on different threads still build the handle only once."""
    count_lock = threading.Lock()
    calls = {"n": 0}

    def slow_init(_endpoint, _key, _config):
        with count_lock:
            calls["n"] += 1
        time.sleep(0.02)
        return "handle-1"

    fake_module = MagicMock()
    fake_module.acquire_driver_handle.side_effect = slow_init
    monkeypatch.setattr("azure.cosmos.aio._backend.binding._rust_module", fake_module)

    backend = AsyncRustBinding(endpoint="https://x.documents.azure.com", master_key="k")
    ready = threading.Barrier(2)
    results = []

    def worker():
        ready.wait()

        async def _run():
            return await backend._ensure_driver_handle()

        results.append(asyncio.run(_run()))

    threads = [threading.Thread(target=worker) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert calls["n"] == 1
    assert results == ["handle-1", "handle-1"]


def test_rust_backend_close_releases_driver_handle_once(monkeypatch):
    """close() removes a built handle once and is idempotent."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    monkeypatch.setattr("azure.cosmos._backend.binding._rust_module", fake_module)

    backend = RustBinding(endpoint="https://x.documents.azure.com", master_key="k")
    backend._ensure_driver_handle()
    backend.close()
    backend.close()

    fake_module.release_driver_handle.assert_called_once_with("handle-1")


def test_async_rust_backend_close_releases_driver_handle_once(monkeypatch):
    """Async close() removes a built handle once and is idempotent."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    monkeypatch.setattr("azure.cosmos.aio._backend.binding._rust_module", fake_module)

    async def _run():
        backend = AsyncRustBinding(endpoint="https://x.documents.azure.com", master_key="k")
        await backend._ensure_driver_handle()
        await backend.close()
        await backend.close()

    asyncio.run(_run())

    fake_module.release_driver_handle.assert_called_once_with("handle-1")


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
        RustBinding,
    )
    assert isinstance(
        make_backend(BACKEND_NAME_RUST, url=_M15_URL, credential="k", connection_verify=None),
        RustBinding,
    )


def test_reject_unsupported_transport_settings_no_op_when_unset():
    """Nothing set (and an empty proxies dict = 'no proxy') does not raise."""
    reject_unsupported_transport_settings()
    reject_unsupported_transport_settings(proxies={})


def test_make_backend_core_python_ignores_transport_settings(monkeypatch):
    """Core Python honors these settings through the explicit legacy backend
    without applying Rust-only validation."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    assert make_backend(
        None,
        url=_M15_URL,
        credential="k",
        transport=object(),
        proxies={"https": "http://proxy:8080"},
        connection_verify=False,
    ) is LEGACY_BACKEND


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
# _StrictDriverIsolationError when a later client's config differs from the first
# live client's, making the fragmentation loud and early. Each test uses a unique
# endpoint so a client finalized late in another test can't disturb its count (the
# _isolate_driver_registry autouse fixture also resets state).


def _rust_backend(url, config=None, strict=False):
    """Build a sync Rust backend with standard fake dependencies."""
    return RustBinding(
        endpoint=url, master_key="k", client_config=config, strict_isolation=strict
    )


def test_second_client_different_config_default_isolates_silently(recwarn):
    """Default-mode backend construction accepts the two configs without warnings.

    No handle is acquired, so native driver isolation is not measured.
    """
    url = "https://m16-different.documents.azure.com"
    first = _rust_backend(url, PreparedClientConfig(preferred_locations=("West US",)))
    second = _rust_backend(url, PreparedClientConfig(preferred_locations=("East US",)))
    assert first is not None and second is not None
    # No warning of any kind is emitted -- isolation is silent now.
    assert len(recwarn) == 0


def test_second_client_different_config_strict_raises():
    """Strict mode: a second client whose config differs from the first live
    client's raises _StrictDriverIsolationError at construction."""
    url = "https://m16-strict-different.documents.azure.com"
    first = _rust_backend(
        url, PreparedClientConfig(preferred_locations=("West US",)), strict=True
    )
    with pytest.raises(_StrictDriverIsolationError):
        _rust_backend(
            url, PreparedClientConfig(preferred_locations=("East US",)), strict=True
        )
    assert first is not None
    # The failed client must not have counted itself against the endpoint.
    assert _driver_registry._live_client_count(url) == 1


def test_strict_same_config_does_not_raise():
    """Equal configs allow two strict-mode Python registrations at one endpoint."""
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
    identity = make_driver_identity(url, "k", cfg, None)
    _register_client_identity(url, cfg, driver_identity=identity)
    _register_client_identity(url, cfg, driver_identity=identity)
    assert _driver_registry._live_client_count(url) == 2
    _release_client_identity(url, cfg, driver_identity=identity)
    assert _driver_registry._live_client_count(url) == 1
    _release_client_identity(url, cfg, driver_identity=identity)
    assert url not in _driver_registry._REGISTRY
    _release_client_identity(url, cfg, driver_identity=identity)  # extra release: no-op
    assert url not in _driver_registry._REGISTRY


def test_registry_strict_raise_does_not_increment_count():
    """A strict-mode conflict raises *without* recording, so the failed client never
    counts against the endpoint and the existing client's count stays correct."""
    url = "https://m16-strict-count.documents.azure.com"
    cfg_a = PreparedClientConfig(preferred_locations=("West US",))
    cfg_b = PreparedClientConfig(preferred_locations=("East US",))
    _register_client_identity(url, cfg_a, driver_identity=make_driver_identity(url, "k", cfg_a, None))
    assert _driver_registry._live_client_count(url) == 1
    with pytest.raises(_StrictDriverIsolationError):
        _register_client_identity(
            url, cfg_b, driver_identity=make_driver_identity(url, "k", cfg_b, None), strict=True
        )
    # Count unchanged -- the failed registration did not enter the count.
    assert _driver_registry._live_client_count(url) == 1


# ---------------------------------------------------------------------------
# Python reservation guard: track endpoint, credential, and config registrations,
# not a census of initialized native engines. These cover:
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
    _register_client_identity(
        url, cfg, driver_identity=make_driver_identity(url, None, cfg, cred_a), strict=True
    )
    with pytest.raises(_StrictDriverIsolationError):
        _register_client_identity(
            url, cfg, driver_identity=make_driver_identity(url, None, cfg, cred_b), strict=True
        )
    # Only the first engine is recorded.
    assert _driver_registry._live_client_count(url) == 1


def test_strict_same_credential_and_config_shares():
    """Same endpoint, credential, and config -> one engine, shared, no raise."""
    url = "https://m16-cred-same.documents.azure.com"
    cfg = PreparedClientConfig(preferred_locations=("West US",))
    cred = _Cred()
    identity = make_driver_identity(url, None, cfg, cred)
    _register_client_identity(url, cfg, driver_identity=identity, strict=True)
    _register_client_identity(url, cfg, driver_identity=identity, strict=True)
    assert _driver_registry._live_client_count(url) == 2


def test_strict_baseline_not_stale_after_first_engine_closes():
    """The strict-isolation baseline must track live engines, not the first registrant.
    With engines X and Y both live (default mode), closing X must not leave a later
    strict client compared against the gone X -- a client matching Y is fine, and only
    one matching neither raises."""
    url = "https://m16-stale-baseline.documents.azure.com"
    cfg_x = PreparedClientConfig(preferred_locations=("West US",))
    cfg_y = PreparedClientConfig(preferred_locations=("East US",))
    identity_x = make_driver_identity(url, "k", cfg_x, None)
    identity_y = make_driver_identity(url, "k", cfg_y, None)
    _register_client_identity(url, cfg_x, driver_identity=identity_x)
    _register_client_identity(url, cfg_y, driver_identity=identity_y)
    _release_client_identity(url, cfg_x, driver_identity=identity_x)
    # A strict client matching the still-live Y shares it -- no false positive.
    _register_client_identity(url, cfg_y, driver_identity=identity_y, strict=True)
    assert _driver_registry._live_client_count(url) == 2
    # A strict client matching neither live engine (X is gone) correctly raises.
    cfg_z = PreparedClientConfig(preferred_locations=("Central US",))
    with pytest.raises(_StrictDriverIsolationError):
        _register_client_identity(
            url, cfg_z, driver_identity=make_driver_identity(url, "k", cfg_z, None), strict=True
        )


def test_endpoint_canonicalization_coalesces_url_variants():
    """Trailing-slash and host-case variants of one account must share a
    bucket, so the strict guard is not bypassed by a cosmetic URL difference."""
    base = "https://M16-Canon.documents.azure.com"
    variant = "https://m16-canon.documents.azure.com/"
    cfg_a = PreparedClientConfig(preferred_locations=("West US",))
    cfg_b = PreparedClientConfig(preferred_locations=("East US",))
    _register_client_identity(
        base, cfg_a, driver_identity=make_driver_identity(base, "k", cfg_a, None), strict=True
    )
    with pytest.raises(_StrictDriverIsolationError):
        _register_client_identity(
            variant, cfg_b, driver_identity=make_driver_identity(variant, "k", cfg_b, None), strict=True
        )
    # Both spellings resolve to the same live count.
    assert _driver_registry._live_client_count(base) == 1
    assert _driver_registry._live_client_count(variant) == 1


def test_canonicalization_keeps_distinct_accounts_separate():
    """Canonicalization must never collapse genuinely different accounts."""
    a = "https://m16-acct-a.documents.azure.com"
    b = "https://m16-acct-b.documents.azure.com"
    cfg = PreparedClientConfig(preferred_locations=("West US",))
    _register_client_identity(a, cfg, driver_identity=make_driver_identity(a, "k", cfg, None), strict=True)
    # Different account, even with a different config, never conflicts.
    other_cfg = PreparedClientConfig(preferred_locations=("East US",))
    _register_client_identity(
        b, other_cfg, driver_identity=make_driver_identity(b, "k", other_cfg, None), strict=True
    )
    assert _driver_registry._live_client_count(a) == 1
    assert _driver_registry._live_client_count(b) == 1


@pytest.mark.parametrize("backend_type", [RustBinding, AsyncRustBinding])
@pytest.mark.parametrize("variant,shared", [
    ("https://m16-native-identity.documents.azure.com/", True),
    ("https://M16-NATIVE-IDENTITY.documents.azure.com", True),
    ("https://m16-native-identity.documents.azure.com:443", True),
    ("https://m16-native-identity.documents.azure.com?ignored-by-account-grouping", False),
])
def test_strict_endpoint_variants_use_native_identity(backend_type, variant, shared):
    """Canonical URL spellings share identity; meaningful URL differences do not."""
    url = "https://m16-native-identity.documents.azure.com"
    first = backend_type(endpoint=url, master_key="k", strict_isolation=True)
    second = None
    try:
        assert (first._driver_identity == make_driver_identity(variant, "k", None, None)) is shared
        if shared:
            second = backend_type(endpoint=variant, master_key="k", strict_isolation=True)
        else:
            with pytest.raises(_StrictDriverIsolationError):
                backend_type(endpoint=variant, master_key="k", strict_isolation=True)
        assert _driver_registry._live_client_count(url) == (2 if shared else 1)
        assert _driver_registry._live_client_count(variant) == (2 if shared else 1)
    finally:
        if second is not None:
            second.abort_construction()
        first.abort_construction()
    assert _driver_registry._live_client_count(url) == 0


@pytest.mark.parametrize("backend_type", [RustBinding, AsyncRustBinding])
def test_strict_equal_configs_ignore_numeric_repr_differences(backend_type):
    """Equivalent typed numeric values do not create separate drivers."""
    url = "https://m16-config-identity.documents.azure.com"
    first_config = PreparedClientConfig(throttling_max_retry_wait_time_seconds=0.0)
    second_config = PreparedClientConfig(throttling_max_retry_wait_time_seconds=-0.0)
    assert first_config == second_config
    assert repr(first_config) != repr(second_config)
    first = backend_type(endpoint=url, master_key="k", client_config=first_config, strict_isolation=True)
    second = None
    try:
        assert first._driver_identity == make_driver_identity(url, "k", second_config, None)
        second = backend_type(endpoint=url, master_key="k", client_config=second_config, strict_isolation=True)
        assert _driver_registry._live_client_count(url) == 2
    finally:
        if second is not None:
            second.abort_construction()
        first.abort_construction()


def test_same_config_repr_cannot_hide_different_native_settings():
    """Identical representations cannot cause drivers with different routing to share."""
    class SameReprConfig(PreparedClientConfig):
        def __repr__(self):
            return "same-native-config-representation"

    url = "https://m16-native-config.documents.azure.com"
    first_config = SameReprConfig(preferred_locations=("West US",))
    second_config = SameReprConfig(preferred_locations=("East US",))
    assert first_config != second_config
    first_identity = make_driver_identity(url, "k", first_config, None)
    second_identity = make_driver_identity(url, "k", second_config, None)
    assert first_identity != second_identity
    _register_client_identity(url, first_config, driver_identity=first_identity, strict=True)
    with pytest.raises(_StrictDriverIsolationError):
        _register_client_identity(url, second_config, driver_identity=second_identity, strict=True)
    assert _driver_registry._live_client_count(url) == 1
    _release_client_identity(url, first_config, driver_identity=first_identity)
    assert _driver_registry._live_client_count(url) == 0


def test_native_identity_never_reads_config_repr():
    class NoReprConfig(PreparedClientConfig):
        def __repr__(self):
            raise AssertionError("identity must not call repr")

    url = "https://no-repr.invalid"
    assert make_driver_identity(url, "key", NoReprConfig(read_timeout_seconds=30), None) == (
        make_driver_identity(url, "key", PreparedClientConfig(read_timeout_seconds=30.0), None)
    )


def test_native_identity_includes_every_fault_rule_field():
    import dataclasses

    base = PreparedFaultInjectionRule(id="rule", operation_type="CreateItem", status_code=429)
    variants = {
        "id": "other", "operation_type": "ReadItem", "status_code": 503,
        "sub_status": 1002, "container_id": "container", "region": "East US",
        "delay_ms": 5, "probability": 0.5, "hit_limit": 2, "enabled": False,
    }
    assert set(variants) == {field.name for field in dataclasses.fields(base)}
    url = "https://fault-identity.invalid"
    original = make_driver_identity(url, "key", PreparedClientConfig(fault_injection_rules=(base,)), None)
    for field, value in variants.items():
        rule = dataclasses.replace(base, **{field: value})
        changed = make_driver_identity(url, "key", PreparedClientConfig(fault_injection_rules=(rule,)), None)
        assert changed != original, field


def test_driver_identity_does_not_initialize_runtime_or_call_credential():
    script = textwrap.dedent("""
        from azure.cosmos import _rust
        from azure.cosmos._backend._driver_registry import make_driver_identity

        class Credential:
            def get_token(self, *args, **kwargs):
                raise AssertionError("identity lookup must not request a token")

        credential = Credential()
        assert _rust._runtime_configuration() is None
        identity = make_driver_identity("https://identity.documents.azure.com", None, None, credential)
        assert isinstance(identity, str)
        assert _rust._runtime_configuration() is None
    """)
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True, text=True, timeout=30, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_driver_identity_missing_export_fails_without_registration(monkeypatch):
    from azure.cosmos import _rust

    monkeypatch.delattr(_rust, "_driver_identity")
    url = "https://m16-missing-identity.documents.azure.com"
    with pytest.raises(RuntimeError, match="does not export _driver_identity"):
        _rust_backend(url)
    assert _driver_registry._live_client_count(url) == 0


def test_make_driver_identity_uses_native_key_without_plaintext_master_key():
    """Check delegation, sample stability, inequality, and plaintext omission.

    These assertions do not establish cryptographic irreversibility or
    collision freedom for arbitrary inputs.
    """
    from azure.cosmos import _rust

    url = "https://m16-identity.documents.azure.com"
    secret = "super-secret-master-key=="
    key = make_driver_identity(url, secret, None, None)
    assert key == _rust._driver_identity(url, secret)
    assert secret not in key
    assert key == make_driver_identity(url, secret, None, None)
    assert key != make_driver_identity(url, "a-different-key", None, None)
    cred = _Cred()
    assert make_driver_identity(url, None, None, cred) == _rust._driver_identity(url, credential=cred)


def test_release_with_wrong_engine_is_noop():
    """Releasing an engine that was never registered must not corrupt the live count
    of the engine that *is* registered."""
    url = "https://m16-release-mismatch.documents.azure.com"
    cfg = PreparedClientConfig(preferred_locations=("West US",))
    identity = make_driver_identity(url, "k", cfg, None)
    _register_client_identity(url, cfg, driver_identity=identity)
    # Release a different config (a different engine) -- harmless no-op.
    other_cfg = PreparedClientConfig(preferred_locations=("East US",))
    _release_client_identity(
        url, other_cfg, driver_identity=make_driver_identity(url, "k", other_cfg, None)
    )
    assert _driver_registry._live_client_count(url) == 1
    _release_client_identity(url, cfg, driver_identity=identity)
    assert url not in _driver_registry._REGISTRY


def test_async_second_client_different_config_strict_raises():
    """Strict isolation (async): a second client to the same endpoint with a
    different config raises ``_StrictDriverIsolationError`` instead of silently sharing
    the first client's engine."""
    url = "https://m16-async-strict-different.documents.azure.com"
    first = AsyncRustBinding(
        endpoint=url,
        master_key="k",
        client_config=PreparedClientConfig(preferred_locations=("West US",)),
        strict_isolation=True,
    )
    with pytest.raises(_StrictDriverIsolationError):
        AsyncRustBinding(
            endpoint=url,
            master_key="k",
            client_config=PreparedClientConfig(preferred_locations=("East US",)),
            strict_isolation=True,
        )
    assert first is not None
    assert _driver_registry._live_client_count(url) == 1


def test_async_second_client_different_config_default_isolates(recwarn):
    """Async backend construction accepts distinct configs without warning.

    This checks Python registration, not native driver construction.
    """
    url = "https://m16-async-default-different.documents.azure.com"
    first = AsyncRustBinding(
        endpoint=url,
        master_key="k",
        client_config=PreparedClientConfig(preferred_locations=("West US",)),
    )
    second = AsyncRustBinding(
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
        resolve_credential({"masterKey": bad_master_key})


def test_resolve_credential_rejects_empty_master_key_string():
    """An empty master-key string is rejected up front rather than accepted and
    failing later."""
    with pytest.raises(ValueError, match=r"^The account key must be a non-empty string\.$"):
        resolve_credential("")


def test_resolve_credential_iterable_non_sequence_gets_generic_message():
    """An unusual custom credential object that merely happens to be iterable (a
    generator, here) but is not a concrete sequence is NOT mislabeled a
    resource-token credential; it falls through to the generic message."""
    def _gen():
        yield {"id": "perm"}

    with pytest.raises(ValueError, match="requires a master-key credential"):
        resolve_credential(_gen())


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
    with pytest.raises(_StrictDriverIsolationError):
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
# These fake _DriverTransportError failures are translated to ServiceResponseError
# for customer exception handling. A response-less failure need not precede HTTP
# or service work. Translation alone does not run legacy transport-retry policies;
# other response-less binding errors may follow different mappings.


def _transport_test_request():
    """Return a prepared request used by transport-error tests."""
    return PreparedRequest(
        op="read_item",
        container_link="dbs/d/colls/c",
        body_bytes=b"",
        partition_key=key_from_legacy_header('["a"]'),
        headers={},
    )


class _FakeDriverTransportError(RuntimeError):
    """Represent a transport failure raised by the fake Rust driver."""
    pass


def test_sync_backend_maps_transport_error_to_service_response_error(monkeypatch):
    """A _DriverTransportError from the sync dispatch surfaces as ServiceResponseError,
    preserving the driver's status/message in the new exception."""
    from azure.core.exceptions import ServiceResponseError
    import azure.cosmos._backend.binding as rust_mod

    backend = RustBinding(endpoint="https://x.documents.azure.com", master_key="k")
    backend._driver_handle = "handle"  # skip the (blocking) handle build
    monkeypatch.setattr(rust_mod, "_rust_module", object())  # pretend binding present
    monkeypatch.setattr(
        rust_mod, "_DRIVER_TRANSPORT_ERROR", _FakeDriverTransportError
    )

    transport_exc_type = rust_mod._DRIVER_TRANSPORT_ERROR
    message = "driver execute_singleton_operation failed: status 503 (ServiceUnavailable): boom"

    def boom(driver_handle, prepared):
        raise transport_exc_type(message)

    monkeypatch.setattr(rust_mod, "_get_binding_function", lambda op: boom)

    with pytest.raises(ServiceResponseError) as excinfo:
        backend.execute(_transport_test_request())
    assert "ServiceUnavailable" in str(excinfo.value)
    assert isinstance(excinfo.value.__cause__, transport_exc_type)


def test_async_backend_maps_transport_error_to_service_response_error(monkeypatch):
    """The async backend performs the same translation on its await path."""
    from azure.core.exceptions import ServiceResponseError
    import azure.cosmos.aio._backend.binding as async_rust_mod

    backend = AsyncRustBinding(endpoint="https://x.documents.azure.com", master_key="k")
    backend._driver_handle = "handle"  # skip the (background-thread) handle build
    monkeypatch.setattr(async_rust_mod, "_rust_module", object())
    monkeypatch.setattr(
        async_rust_mod, "_DRIVER_TRANSPORT_ERROR", _FakeDriverTransportError
    )

    transport_exc_type = async_rust_mod._DRIVER_TRANSPORT_ERROR
    message = "driver execute_singleton_operation failed: status 503 (ServiceUnavailable): boom"

    async def boom(driver_handle, prepared):
        raise transport_exc_type(message)

    monkeypatch.setattr(async_rust_mod, "_get_binding_function", lambda op: boom)

    async def run():
        with pytest.raises(ServiceResponseError) as excinfo:
            await backend.execute(_transport_test_request())
        assert "ServiceUnavailable" in str(excinfo.value)
        assert isinstance(excinfo.value.__cause__, transport_exc_type)

    asyncio.run(run())


def test_sync_list_databases_transport_error_does_not_replay_legacy(monkeypatch):
    """A response-less list_databases failure is translated, not replayed."""
    from azure.core.exceptions import ServiceResponseError
    import azure.cosmos._backend.binding as rust_mod

    backend = RustBinding(endpoint="https://x.documents.azure.com", master_key="k")
    backend._driver_handle = "handle"
    monkeypatch.setattr(rust_mod, "_rust_module", object())
    monkeypatch.setattr(
        rust_mod, "_DRIVER_TRANSPORT_ERROR", _FakeDriverTransportError
    )
    transport_exc_type = rust_mod._DRIVER_TRANSPORT_ERROR

    def boom(_driver_handle, _prepared):
        raise transport_exc_type("driver list_databases failed: transport closed")

    monkeypatch.setattr(rust_mod, "_get_page_dispatch", lambda _op: boom)
    legacy_calls = []

    with pytest.raises(ServiceResponseError):
        backend.run_page_operation(
            build_request=lambda: PreparedQuery(
                op=OP_LIST_DATABASES, container_link="", headers={}
            ),
            routing=OperationRouting(OP_LIST_DATABASES, True),
            legacy_call=lambda: legacy_calls.append("legacy"),
            process_response=lambda page: page,
        )

    assert legacy_calls == []


def test_async_list_databases_transport_error_does_not_replay_legacy(monkeypatch):
    """The async list_databases transport mapping also avoids legacy replay."""
    from azure.core.exceptions import ServiceResponseError
    import azure.cosmos.aio._backend.binding as async_rust_mod

    backend = AsyncRustBinding(endpoint="https://x.documents.azure.com", master_key="k")
    backend._driver_handle = "handle"
    monkeypatch.setattr(async_rust_mod, "_rust_module", object())
    monkeypatch.setattr(
        async_rust_mod, "_DRIVER_TRANSPORT_ERROR", _FakeDriverTransportError
    )
    transport_exc_type = async_rust_mod._DRIVER_TRANSPORT_ERROR

    async def boom(_driver_handle, _prepared):
        raise transport_exc_type("driver list_databases failed: transport closed")

    monkeypatch.setattr(async_rust_mod, "_get_page_dispatch", lambda _op: boom)
    legacy_calls = []

    async def run():
        def build_request():
            return PreparedQuery(op=OP_LIST_DATABASES, container_link="", headers={})

        with pytest.raises(ServiceResponseError):
            await backend.run_page_operation(
                build_request=build_request,
                routing=OperationRouting(OP_LIST_DATABASES, True),
                legacy_call=lambda: legacy_calls.append("legacy"),
                process_response=lambda page: page,
            )

    asyncio.run(run())
    assert legacy_calls == []


# --- Regressions for the Rust client lifecycle and process-wide runtime policy ---


def test_untuned_client_does_not_pin_process_wide_transport_timeouts():
    """Unset and explicit timeout reservations coexist before native initialization.

    Only Python policy registration is exercised. Initializing the native runtime
    with default values can still constrain later explicit settings.
    """
    register_transport_timeout_policy(build_client_config(None))
    register_transport_timeout_policy(
        build_client_config(None, connection_timeout_seconds=2.0)
    )
    # The reverse order must work too: a tuned client first, then an untuned one.
    _reset_driver_registry()
    register_transport_timeout_policy(
        build_client_config(None, connection_timeout_seconds=2.0)
    )
    register_transport_timeout_policy(build_client_config(None))


def test_untuned_and_tuned_rust_clients_can_both_be_constructed(monkeypatch):
    """Public client construction permits coexistence before native initialization."""
    monkeypatch.setattr(
        sync_cosmos_client_module, "CosmosClientConnection", MagicMock()
    )
    untuned = sync_cosmos_client_module.CosmosClient(
        "https://coexist.documents.azure.com", "key", _backend=BACKEND_NAME_RUST
    )
    tuned = sync_cosmos_client_module.CosmosClient(
        "https://coexist.documents.azure.com",
        "key",
        _backend=BACKEND_NAME_RUST,
        connection_timeout=2.0,
    )
    assert untuned._backend._client_config is None
    assert tuned._backend._client_config.connection_timeout_seconds == 2.0
    untuned._backend.close()
    tuned._backend.close()


def _make_closed_rust_backend(monkeypatch, endpoint):
    """Build a Rust backend over a stub binding, open its handle, then close it."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    monkeypatch.setattr("azure.cosmos._backend.binding._rust_module", fake_module)
    backend = RustBinding(
        endpoint=endpoint,
        master_key="key",
        token_credential=None,
        client_config=None,
    )
    assert backend._ensure_driver_handle() == "handle-1"
    backend.close()
    return backend, fake_module


def test_sync_backend_refuses_to_reopen_after_close(monkeypatch):
    """A closed sync client must refuse work, not silently reopen.

    close() clears the handle, so without a closed flag the next operation saw a
    client that looked brand new and quietly took a second reference on the shared
    Rust driver -- an operation on a closed client appeared to succeed. The async
    backend already refused; this is the sync half of that rule.
    """
    backend, fake_module = _make_closed_rust_backend(
        monkeypatch, "https://reopen.documents.azure.com"
    )
    with pytest.raises(RuntimeError, match="closed"):
        backend._ensure_driver_handle()
    assert fake_module.acquire_driver_handle.call_count == 1


def test_sync_backend_close_is_idempotent(monkeypatch):
    """Closing twice must release the shared driver exactly once.

    release_driver_handle drops one reference per call, so a second close would decrement a
    driver another client may still be using.
    """
    backend, fake_module = _make_closed_rust_backend(
        monkeypatch, "https://double-close.documents.azure.com"
    )
    backend.close()
    backend.close()
    assert fake_module.release_driver_handle.call_count == 1


class _FakeAsyncCredential:
    """An async token credential, the shape that gets wrapped in a bridge."""

    async def get_token(self, *scopes, **kwargs):
        """Never actually called; its being a coroutine is what matters here."""
        raise AssertionError("the driver should not reach this credential")


@pytest.mark.parametrize(
    "bad_kwargs",
    [
        {"consistency_level": "BoundedStaleness"},
        {"connection_timeout_seconds": 99.0},
        {"preferred_locations": "West US"},
    ],
)
def test_failed_construction_releases_the_async_credential_bridge(bad_kwargs):
    """Invalid constructor options leave no bridge registration for this credential.

    Wrapping/acquiring a bridge is lazy and need not start its loop thread.
    This assertion inspects the registry, not native or thread cleanup.
    """
    from azure.cosmos._backend import _async_credential_bridge as bridge_module

    credential = _FakeAsyncCredential()
    with pytest.raises(ValueError):
        make_backend(
            BACKEND_NAME_RUST,
            url="https://bridge-leak.documents.azure.com",
            credential=credential,
            **bad_kwargs,
        )
    assert id(credential) not in bridge_module._REGISTRY
