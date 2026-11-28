# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Tests of how the client passes settings and requests to the compiled module
(azure.cosmos._rust), and how the client starts and closes.

The adapter (BindingAdapter, or AsyncBindingAdapter for async clients) is the
Python class that passes each request to the compiled module and turns its reply
into a response. The first time a client sends a request, the adapter asks the
compiled module for a handle: the object that holds the client's connection
state. The tests call this opening the handle. When the client closes, the
adapter gives the handle back to the compiled module; the tests call this
releasing the handle. Most tests replace the compiled module with a fake,
so they check what the Python code sends, not real HTTP traffic. A few tests check
the compiled module itself and are skipped when it is not built.
"""
from __future__ import annotations
import ast
from contextlib import contextmanager
from azure.cosmos._backend.capabilities import OperationRouting
from common.request_preparation import call_create_item_helper
from common.sdk_subprocess import sdk_python_command
from common.typed_requests import key_from_legacy_header, legacy_partition_key_from_request

import asyncio
import concurrent.futures
import importlib
import inspect
import json
import logging
import os
import re
import subprocess
import textwrap
import threading
import time
from dataclasses import FrozenInstanceError
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

import azure.cosmos.aio._cosmos_client as async_cosmos_client_module
import azure.cosmos.cosmos_client as sync_cosmos_client_module
from azure.cosmos import CosmosRuntime, ConnectionPoolOptions
from azure.cosmos._backend.cosmos_backend import CosmosBackend
from azure.cosmos._backend.contracts import ContainerMetadata
from azure.cosmos._backend.contracts import (
    BackendResponse,
    PreparedClientConfig,
    PreparedFaultInjectionRule,
    PreparedPageRequest,
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
    OP_READ_ITEMS,
    OP_GET_THROUGHPUT,
    OP_TO_BINDING_FUNCTION_NAME,
    STATELESS_PAGE_BINDING_FUNCTION_NAMES,
)
from azure.cosmos._backend.errors import PagePreflightError, UnsupportedQueryError
from azure.cosmos._backend._binding_adapter_shared import (
    BindingAdapterShared,
    configure_packaged_query_plan_interop,
    driver_transport_error_type,
    driver_unsupported_query_error_type,
)
from azure.cosmos._backend.constants import BACKEND_ENV_VAR, BACKEND_NAME_CORE_PYTHON, BACKEND_NAME_RUST
from azure.cosmos._backend.client_config import build_client_config
from azure.cosmos._backend import client_config as client_config_module
from azure.cosmos._backend.credentials import resolve_credential
from azure.cosmos._backend.factory import make_backend, resolve_backend_name
from azure.cosmos._backend.legacy import LEGACY_BACKEND
from azure.cosmos._backend._async_credential_bridge import AsyncTokenCredentialBridge
from azure.cosmos._backend.binding_adapter import BindingAdapter
from azure.cosmos._helpers._item_arguments import get_selected_backend
from azure.cosmos._helpers._item_operations import ItemHelper
from azure.cosmos.aio._backend.factory import make_async_backend
from azure.cosmos.aio._backend.legacy import ASYNC_LEGACY_BACKEND
from azure.cosmos.aio._backend.binding_adapter import AsyncBindingAdapter
from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy
from azure.cosmos.container import ContainerProxy
from azure.cosmos.documents import ConnectionPolicy
from azure.cosmos.partition_key import NonePartitionKeyValue


@pytest.fixture(autouse=True)
def _close_test_adapters(monkeypatch):
    """Close adapters before monkeypatch restores their fake compiled modules."""
    closers = []
    initialize = BindingAdapterShared._init_shared

    def initialize_and_track(adapter, *args, **kwargs):
        initialize(adapter, *args, **kwargs)
        closers.append(adapter.close)

    monkeypatch.setattr(BindingAdapterShared, "_init_shared", initialize_and_track)
    try:
        yield
    finally:
        for close in reversed(closers):
            if not close.__self__._closing:
                result = close()
                if inspect.isawaitable(result):
                    asyncio.run(result)


@pytest.mark.parametrize("async_mode", [False, True])
def test_unclosed_adapters_release_before_binding_mock_is_restored_rust(monkeypatch, async_mode):
    """Retained adapters must not release stale handles into a later test's mock."""
    module = importlib.import_module(
        "azure.cosmos.aio._backend.binding_adapter" if async_mode else "azure.cosmos._backend.binding_adapter"
    )
    adapter_type = AsyncBindingAdapter if async_mode else BindingAdapter
    fake_module = MagicMock()
    handle = fake_module.acquire_driver_handle.return_value
    monkeypatch.setattr(module, "_rust_module", fake_module)

    with contextmanager(_close_test_adapters.__wrapped__)(monkeypatch):
        adapter = adapter_type("https://x.documents.azure.com", master_key="k")
        acquired = adapter._ensure_driver_handle()
        if async_mode:
            acquired = asyncio.run(acquired)
        assert acquired is handle

    fake_module.release_driver_handle.assert_called_once_with(handle)
    later_module = MagicMock()
    monkeypatch.setattr(module, "_rust_module", later_module)
    adapter.__del__()
    later_module.release_driver_handle.assert_not_called()
    fake_module.release_driver_handle.assert_called_once_with(handle)


@pytest.mark.parametrize("factory", [make_backend, make_async_backend])
def test_client_headers_are_copied_and_call_headers_win_rust(factory):
    """Headers given to the client are copied when the client is created, so changing
    the original dict later has no effect. A header given on a call replaces the client
    header with the same name (names are not case-sensitive), for that call only. The
    client's copy cannot be changed.
    """
    from azure.core.utils import CaseInsensitiveDict

    client_headers = {"X-Application": "client", "x-default-only": "retained"}
    adapter = factory("rust", url="https://headers.example", credential="key", headers=client_headers)
    try:
        client_headers["X-Application"] = "next_request-mutation"
        prepared = PreparedRequest(
            "read_item", "dbs/db/colls/c", b"", key_from_legacy_header('["pk"]'),
            item_id="item", headers={"x-application": "call", "X-Call-Only": "once"},
        )
        merged = adapter._with_client_headers(prepared)
        assert dict(CaseInsensitiveDict(merged.headers)) == {
            "x-application": "call", "x-default-only": "retained", "X-Call-Only": "once",
        }
        assert prepared.headers == {"x-application": "call", "X-Call-Only": "once"}
        assert CaseInsensitiveDict(adapter._client_config.headers)["x-application"] == "client"
        next_request = adapter._with_client_headers(PreparedRequest(
            "read_item", "dbs/db/colls/c", b"", key_from_legacy_header('["pk"]'), item_id="item",
        ))
        assert CaseInsensitiveDict(next_request.headers)["x-application"] == "client"
        assert "X-Call-Only" not in next_request.headers
        with pytest.raises(TypeError):
            adapter._client_config.headers["x-application"] = "mutated"
    finally:
        closed = adapter.close()
        if inspect.isawaitable(closed):
            asyncio.run(closed)


@pytest.mark.parametrize("headers", [[], "", {"x-app": 1}, {1: "value"}])
def test_client_headers_reject_invalid_mappings_rust(headers):
    """Client headers must be a dict of string names to string values. Anything else raises TypeError."""
    with pytest.raises(TypeError):
        build_client_config(headers=headers)


def test_client_header_values_are_hidden_when_printed_rust():
    """Header values are not shown when the client settings are printed, because they
    may hold private data. An empty header dict adds no settings.
    """
    config = build_client_config(headers={"x-application": "private-value"})
    assert config is not None and "private-value" not in repr(config)
    assert build_client_config(headers={}) is None


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("paged", [False, True], ids=["point", "page"])
def test_client_headers_reach_single_and_paged_requests_rust(monkeypatch, asynchronous, paged):
    """For sync and async clients, and for single and paged requests, the request sent
    has the client headers merged with the call headers. A later call without headers
    sends only the client headers.
    """
    from azure.core.utils import CaseInsensitiveDict

    factory = make_async_backend if asynchronous else make_backend
    adapter = factory(
        "rust", url="https://headers.example", credential="key",
        headers={"X-Application": "client", "x-default-only": "retained"},
    )
    module = importlib.import_module(type(adapter).__module__)
    function_name = ("list_databases" if paged else "read_item") + ("_async" if asynchronous else "")
    sent_headers = []

    def execute(handle, prepared, **kwargs):
        assert handle == "test-handle"
        sent_headers.append(CaseInsensitiveDict(prepared.headers))
        return (200, 0, {}, b"{}", None)

    async def async_execute(*args, **kwargs):
        return execute(*args, **kwargs)

    monkeypatch.setattr(module._rust_module, function_name, async_execute if asynchronous else execute)
    monkeypatch.setattr(
        adapter, "_ensure_driver_handle",
        AsyncMock(return_value="test-handle") if asynchronous else MagicMock(return_value="test-handle"),
    )

    def request(headers):
        if paged:
            return PreparedPageRequest(op=OP_LIST_DATABASES, container_link="", headers=headers)
        return PreparedRequest(
            "read_item", "dbs/db/colls/c", b"", key_from_legacy_header('["pk"]'),
            item_id="item", headers=headers,
        )

    requests = (request({"x-application": "call", "x-call-only": "once"}), request({}))

    async def send_requests():
        try:
            for prepared in requests:
                if paged:
                    assert len([page async for page in adapter.execute_pages(prepared)]) == 1
                else:
                    assert (await adapter.execute(prepared)).status_code == 200
        finally:
            await adapter.close()

    if asynchronous:
        asyncio.run(send_requests())
    else:
        try:
            for prepared in requests:
                if paged:
                    assert len(list(adapter.execute_pages(prepared))) == 1
                else:
                    assert adapter.execute(prepared).status_code == 200
        finally:
            adapter.close()
    assert sent_headers == [
        CaseInsensitiveDict({"x-application": "call", "x-default-only": "retained", "x-call-only": "once"}),
        CaseInsensitiveDict({"x-application": "client", "x-default-only": "retained"}),
    ]


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("scope", ["client_default", "per_call", "override"])
def test_read_item_sends_client_and_call_headers_rust(monkeypatch, asynchronous, scope):
    """Calls the public read_item with no network. Checks which x-application value is
    sent: the client's when only the client sets it, and the call's when the call sets
    it, whether or not the client also does.
    """
    from azure.core.utils import CaseInsensitiveDict

    module = async_cosmos_client_module if asynchronous else sync_cosmos_client_module
    client_headers = {"x-application": "client"} if scope != "per_call" else {}
    call_headers = {"X-Application": "call"} if scope != "client_default" else {}
    client = module.CosmosClient("https://headers.invalid", "ZmFrZQ==", _backend="rust", headers=client_headers)
    adapter = client._adapter
    compiled_module = importlib.import_module(type(adapter).__module__)._rust_module
    fake = AsyncMock if asynchronous else MagicMock
    monkeypatch.setattr(adapter, "_ensure_driver_handle", fake(return_value="test-handle"))
    suffix = "_async" if asynchronous else ""
    monkeypatch.setattr(compiled_module, "get_container_metadata" + suffix, fake(return_value=("rid", ("/pk",), "Hash", None)))
    sent_headers = []
    expected = {"id": "order", "pk": "customer", "status": "paid"}

    def read(handle, prepared, **_kwargs):
        assert handle == "test-handle"
        sent_headers.append(CaseInsensitiveDict(prepared.headers))
        return 200, 0, {}, json.dumps(expected).encode(), None

    monkeypatch.setattr(compiled_module, "read_item" + suffix, fake(side_effect=read))
    container = client.get_database_client("sales").get_container_client("orders")
    kwargs = {"initial_headers": call_headers} if call_headers else {}

    async def read_and_close():
        try:
            return await container.read_item("order", partition_key="customer", **kwargs)
        finally:
            await client.close()

    if asynchronous:
        result = asyncio.run(read_and_close())
    else:
        try:
            result = container.read_item("order", partition_key="customer", **kwargs)
        finally:
            client.close()

    assert dict(result) == expected
    assert len(sent_headers) == 1
    assert sent_headers[0]["x-application"] == ("client" if scope == "client_default" else "call")


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
            for name in set(OP_TO_BINDING_FUNCTION_NAME.values()) | set(STATELESS_PAGE_BINDING_FUNCTION_NAMES.values())
            for suffix in ("", "_async")
        }
    ),
)
def test_compiled_functions_take_driver_handle_first_rust(method):
    """Every compiled-module function the SDK calls takes the handle as its first
    argument, named driver_handle.

    The SDK calls these functions by name, so a renamed argument would only fail when
    that operation is used. The argument can be passed by position or by name, because
    the SDK uses both. The old names handle and _handle must be gone. The list of
    functions comes from the same table the SDK uses, so new operations are checked
    automatically. Skipped when the compiled module is not built.
    """
    compiled_module = pytest.importorskip("azure.cosmos._rust")
    signature = inspect.signature(getattr(compiled_module, method))
    parameter = next(iter(signature.parameters.values()))
    assert parameter.name == "driver_handle"
    assert parameter.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert "handle" not in signature.parameters
    assert "_handle" not in signature.parameters


def test_release_driver_handle_rejects_a_plain_string_rust():
    """release_driver_handle accepts only a real handle. A string raises TypeError, and
    the old keyword name handle is not accepted.
    """
    compiled_module = pytest.importorskip("azure.cosmos._rust")
    with pytest.raises(TypeError, match="_DriverHandle"):
        compiled_module.release_driver_handle(driver_handle="unregistered-test-driver")
    with pytest.raises(TypeError):
        compiled_module.release_driver_handle(handle="unregistered-test-driver")


def test_query_plan_library_folder_is_set_when_present_rust(tmp_path, monkeypatch):
    """When the .libs folder exists next to the compiled module,
    AZURE_COSMOS_QUERYPLANINTEROP_DIR is set to it. This checks only the variable, not
    loading the library.
    """
    package_directory = tmp_path / "azure" / "cosmos"
    libs_directory = package_directory / ".libs"
    libs_directory.mkdir(parents=True)
    compiled_module = MagicMock()
    compiled_module.__file__ = str(package_directory / "_rust.pyd")
    monkeypatch.delenv("AZURE_COSMOS_QUERYPLANINTEROP_DIR", raising=False)

    configure_packaged_query_plan_interop(compiled_module)

    assert os.environ["AZURE_COSMOS_QUERYPLANINTEROP_DIR"] == str(
        libs_directory.resolve()
    )


def test_query_plan_library_folder_is_not_set_when_missing_rust(tmp_path, monkeypatch):
    """When the .libs folder does not exist, AZURE_COSMOS_QUERYPLANINTEROP_DIR is not set."""
    compiled_module = MagicMock()
    compiled_module.__file__ = str(tmp_path / "azure" / "cosmos" / "_rust.pyd")
    monkeypatch.delenv("AZURE_COSMOS_QUERYPLANINTEROP_DIR", raising=False)

    configure_packaged_query_plan_interop(compiled_module)

    assert "AZURE_COSMOS_QUERYPLANINTEROP_DIR" not in os.environ


def test_query_plan_library_folder_keeps_customer_value_rust(
    tmp_path, monkeypatch
):
    """If the customer already set AZURE_COSMOS_QUERYPLANINTEROP_DIR, the SDK keeps that value."""
    package_directory = tmp_path / "azure" / "cosmos"
    (package_directory / ".libs").mkdir(parents=True)
    compiled_module = MagicMock()
    compiled_module.__file__ = str(package_directory / "_rust.pyd")
    explicit_directory = tmp_path / "explicit"
    monkeypatch.setenv(
        "AZURE_COSMOS_QUERYPLANINTEROP_DIR", str(explicit_directory)
    )

    configure_packaged_query_plan_interop(compiled_module)

    assert os.environ["AZURE_COSMOS_QUERYPLANINTEROP_DIR"] == str(
        explicit_directory
    )


@pytest.mark.parametrize(
    "resolver",
    [driver_transport_error_type, driver_unsupported_query_error_type],
)
def test_error_types_match_nothing_without_compiled_module_rust(resolver):
    """Without the compiled module, looking up its error classes returns an empty tuple,
    so an except clause that uses it catches nothing.
    """
    assert resolver(None) == ()


@pytest.mark.parametrize(
    ("resolver", "error_name"),
    [
        (driver_transport_error_type, "_DriverTransportError"),
        (driver_unsupported_query_error_type, "_UnsupportedQueryFeatureError"),
    ],
)
def test_error_types_require_current_compiled_module_rust(resolver, error_name):
    """If the compiled module is from an older build and is missing an error class, the
    lookup raises RuntimeError asking for a rebuild. Without this, errors from the
    compiled module would not be turned into the SDK's Python errors.
    """
    with pytest.raises(RuntimeError, match=error_name):
        resolver(object())


@pytest.mark.parametrize(
    "module_name",
    [
        "azure.cosmos._backend.binding_adapter",
        "azure.cosmos.aio._backend.binding_adapter",
    ],
)
def test_import_does_not_set_query_plan_library_folder_rust(module_name, tmp_path):
    """Importing the SDK does not set AZURE_COSMOS_QUERYPLANINTEROP_DIR. It is set only
    when a client starts. Runs in a new Python process with a fake compiled module.
    """
    script = textwrap.dedent(
        f"""
        import importlib
        import os
        import sys
        import types
        from pathlib import Path

        import azure.cosmos

        package_directory = Path({str(tmp_path)!r}) / "azure" / "cosmos"
        libs_directory = package_directory / ".libs"
        libs_directory.mkdir(parents=True)
        os.environ.pop("AZURE_COSMOS_QUERYPLANINTEROP_DIR", None)
        fake_compiled_module = types.ModuleType("azure.cosmos._rust")
        fake_compiled_module.__file__ = str(package_directory / "_rust.pyd")
        fake_compiled_module._DriverTransportError = type("_DriverTransportError", (RuntimeError,), {{}})
        fake_compiled_module._DriverResponseError = type("_DriverResponseError", (RuntimeError,), {{}})
        fake_compiled_module._UnsupportedQueryFeatureError = type(
            "_UnsupportedQueryFeatureError", (RuntimeError,), {{}}
        )
        azure.cosmos._rust = fake_compiled_module
        sys.modules["azure.cosmos._rust"] = fake_compiled_module
        sys.modules.pop({module_name!r}, None)

        importlib.import_module({module_name!r})

        assert "AZURE_COSMOS_QUERYPLANINTEROP_DIR" not in os.environ
        """
    )

    result = subprocess.run(
        sdk_python_command(script),
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("adapter_type", [BindingAdapter, AsyncBindingAdapter])
def test_client_start_sets_query_plan_library_folder_first_rust(
    adapter_type, tmp_path, monkeypatch
):
    """AZURE_COSMOS_QUERYPLANINTEROP_DIR is not set when the client is created. It is set
    when the client starts, before the compiled module creates the handle.
    """
    package = tmp_path / "azure" / "cosmos"
    libs_directory = package / ".libs"
    libs_directory.mkdir(parents=True)
    monkeypatch.delenv("AZURE_COSMOS_QUERYPLANINTEROP_DIR", raising=False)
    compiled_module = MagicMock()
    compiled_module.__file__ = str(package / "_rust.pyd")

    def acquire(*args):
        assert os.environ["AZURE_COSMOS_QUERYPLANINTEROP_DIR"] == str(libs_directory.resolve())
        return "test-handle"

    compiled_module.acquire_driver_handle.side_effect = acquire
    adapter = adapter_type(endpoint="https://qpi.documents.azure.com", master_key="k")
    try:
        assert "AZURE_COSMOS_QUERYPLANINTEROP_DIR" not in os.environ
        assert adapter._initialize_driver(compiled_module) == "test-handle"
    finally:
        adapter.abort_construction()


@pytest.mark.parametrize("adapter_type", [BindingAdapter, AsyncBindingAdapter])
@pytest.mark.parametrize("explicit_runtime", [False, True])
@pytest.mark.parametrize("status", [401, 403, 404, 429])
def test_client_start_service_error_keeps_details_rust(adapter_type, explicit_runtime, status):
    """If the service returns an error (401, 403, 404 or 429) while the client starts,
    the caller gets CosmosHttpResponseError, or CosmosResourceNotFoundError for 404. The
    error keeps the status, sub-status, headers, diagnostics and message, with the
    original error as its cause. No handle is kept. Checked with and without a
    CosmosRuntime.
    """
    from azure.cosmos.exceptions import CosmosHttpResponseError, CosmosResourceNotFoundError

    compiled_module = MagicMock()
    compiled_module.__file__ = None
    compiled_module._DriverResponseError = type("_DriverResponseError", (RuntimeError,), {})
    response = (
        status,
        1002,
        {"x-ms-activity-id": "account-request", "x-ms-substatus": "1002", "x-ms-retry-after-ms": "25"},
        b'{"message":"account lookup failed"}',
        '{"request_count":1}',
    )
    service_error = compiled_module._DriverResponseError(response)
    compiled_module.acquire_driver_handle.side_effect = service_error
    runtime = MagicMock() if explicit_runtime else None
    adapter = adapter_type(endpoint="https://initialization.invalid", master_key="key")
    try:
        expected = CosmosResourceNotFoundError if status == 404 else CosmosHttpResponseError
        with pytest.raises(expected) as caught:
            adapter._initialize_driver(compiled_module, runtime)
        error = caught.value
        assert error.status_code == status
        assert error.sub_status == 1002
        assert error.headers["x-ms-activity-id"] == "account-request"
        assert error.headers["x-ms-retry-after-ms"] == "25"
        assert error.headers["x-ms-cosmos-sdk-diagnostics"] == '{"request_count":1}'
        assert "account lookup failed" in str(error)
        assert error.__cause__ is service_error
        compiled_module.acquire_driver_handle.assert_called_once_with(
            *adapter._acquire_driver_handle_args(),
            **({"runtime": runtime._handle} if explicit_runtime else {}),
        )
        assert adapter._driver_handle is None
    finally:
        adapter.abort_construction()


@pytest.mark.parametrize("adapter_type", [BindingAdapter, AsyncBindingAdapter])
@pytest.mark.parametrize("transport_failure", [False, True])
def test_client_start_error_without_response_rust(adapter_type, transport_failure):
    """If the client gets no response from the service while starting, the caller gets
    ServiceResponseError with the original error as its cause. Any other error reaches
    the caller unchanged. No handle is kept.
    """
    from azure.core.exceptions import ServiceResponseError

    compiled_module = MagicMock()
    compiled_module.__file__ = None
    compiled_module._DriverResponseError = type("_DriverResponseError", (RuntimeError,), {})
    compiled_module._DriverTransportError = type("_DriverTransportError", (RuntimeError,), {})
    start_error = (
        compiled_module._DriverTransportError("account transport failed")
        if transport_failure
        else RuntimeError("initialization task failed")
    )
    compiled_module.acquire_driver_handle.side_effect = start_error
    adapter = adapter_type(endpoint="https://initialization.invalid", master_key="key")
    try:
        expected = ServiceResponseError if transport_failure else RuntimeError
        with pytest.raises(expected) as caught:
            adapter._initialize_driver(compiled_module)
        if transport_failure:
            assert caught.value.__cause__ is start_error
            assert "account transport failed" in str(caught.value)
        else:
            assert caught.value is start_error
        compiled_module.acquire_driver_handle.assert_called_once()
        assert adapter._driver_handle is None
    finally:
        adapter.abort_construction()


def test_query_plan_library_folder_keeps_value_set_meanwhile_rust(tmp_path, monkeypatch):
    """If other code sets AZURE_COSMOS_QUERYPLANINTEROP_DIR while the SDK is looking for
    the folder, the SDK keeps that value.
    """
    libs_directory = tmp_path / ".libs"
    libs_directory.mkdir()
    compiled_module = MagicMock()
    compiled_module.__file__ = str(tmp_path / "_rust.pyd")
    monkeypatch.delenv("AZURE_COSMOS_QUERYPLANINTEROP_DIR", raising=False)
    original = Path.is_dir

    def is_dir(path):
        monkeypatch.setenv("AZURE_COSMOS_QUERYPLANINTEROP_DIR", "explicit-after-discovery")
        return original(path)

    monkeypatch.setattr(Path, "is_dir", is_dir)
    configure_packaged_query_plan_interop(compiled_module)
    assert os.environ["AZURE_COSMOS_QUERYPLANINTEROP_DIR"] == "explicit-after-discovery"


# ---------------------------------------------------------------------------
# Import guard
# ---------------------------------------------------------------------------

# This file lives at tests/common/, so go up two folders to the repo root and
# then into azure/cosmos/.
_PKG_ROOT = Path(__file__).resolve().parents[2] / "azure" / "cosmos"

# Each name may only be imported by the files listed here. Anything else fails.
_ALLOWED = {
    # Only these files may import the compiled module: the adapters and their
    # shared helper send requests and start clients, runtime.py creates
    # CosmosRuntime, and client_config.py checks whether the build includes
    # test-only fault rules.
    "_rust": {
        Path("runtime.py"),
        Path("_backend") / "binding_adapter.py",
        Path("aio") / "_backend" / "binding_adapter.py",
        Path("_backend") / "_binding_adapter_shared.py",
        Path("_backend") / "client_config.py",
    },
    # The adapter classes, which send requests to the compiled module, may only
    # be imported by the factory that builds them and the client that holds them.
    "BindingAdapter": {
        Path("_backend") / "factory.py",
        Path("cosmos_client.py"),
    },
    "AsyncBindingAdapter": {
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
    """Yield every Python file in the SDK package."""
    for path in _PKG_ROOT.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        yield path


# Read each source file once and keep its import lines, so the test below can
# scan that list instead of re-reading every file for each guarded name.
def _collect_import_lines():
    """Return the import lines of each SDK file, as (path, lines) pairs."""
    cached = []
    for path in _iter_py_files():
        relative_path = path.relative_to(_PKG_ROOT)
        text = path.read_text(encoding="utf-8", errors="ignore")
        # Skip imports inside `if TYPE_CHECKING:`. They are only for type hints
        # and never run.
        lines = text.splitlines(keepends=True)
        for node in ast.walk(ast.parse(text.lstrip("\ufeff"))):
            if isinstance(node, ast.If) and isinstance(node.test, ast.Name) and node.test.id == "TYPE_CHECKING":
                for child in node.body:
                    for index in range(child.lineno - 1, child.end_lineno):
                        lines[index] = "\n"
        text = "".join(lines)
        import_lines = _IMPORT_RE.findall(text)
        if import_lines:
            cached.append((relative_path, import_lines))
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
def test_public_throughput_and_feed_range_methods_do_not_select_backends_rust(
    proxy_type, method_name
):
    """Public methods delegate to family helpers instead of selecting an engine."""
    source = inspect.getsource(getattr(proxy_type, method_name))
    forbidden = (
        "_backend",
        "can_use_rust",
        "try_get_throughput_with_rust",
        "try_replace_throughput_with_rust",
        "try_read_feed_ranges_with_rust",
        "try_feed_range_from_partition_key_with_rust",
        "try_is_feed_range_subset_with_rust",
    )
    assert not [name for name in forbidden if name in source]


@pytest.mark.parametrize("guarded_name,allowed_files", list(_ALLOWED.items()))
def test_only_allowed_files_import_guarded_names_rust(guarded_name, allowed_files):
    """Only the files listed in _ALLOWED may import the compiled module or the
    adapter classes. This keeps every call into the compiled module in one place.
    """
    offenders = []
    name_re = re.compile(r"\b" + re.escape(guarded_name) + r"\b")
    for relative_path, import_lines in _IMPORT_LINE_CACHE:
        if relative_path in allowed_files:
            continue
        for line in import_lines:
            if name_re.search(line):
                offenders.append("{}: {}".format(relative_path, line.strip()))
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

@pytest.mark.parametrize("factory,adapter_type", [
    (make_backend, BindingAdapter), (make_async_backend, AsyncBindingAdapter),
])
def test_factory_default_returns_rust_backend_rust(monkeypatch, factory, adapter_type):
    """With nothing set, both factories construct Rust adapters."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    backend = factory(None, url="https://default.invalid", credential="ZmFrZQ==")
    try:
        assert isinstance(backend, adapter_type)
    finally:
        closed = backend.close()
        if inspect.isawaitable(closed):
            asyncio.run(closed)


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("connection_string", [False, True])
@pytest.mark.parametrize("environment,explicit,expected", [
    (None, None, "rust"),
    ("core-python", None, "core-python"),
    ("rust", "core-python", "core-python"),
    ("core-python", "rust", "rust"),
    ("core-python", "", "rust"),
])
def test_public_client_default_and_private_selection_rust(
    monkeypatch, asynchronous, connection_string, environment, explicit, expected,
):
    module = async_cosmos_client_module if asynchronous else sync_cosmos_client_module
    if environment is None:
        monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    else:
        monkeypatch.setenv(BACKEND_ENV_VAR, environment)
    connection = MagicMock()
    monkeypatch.setattr(module, "CosmosClientConnection", connection)
    options = {} if explicit is None else {"_backend": explicit}
    if connection_string:
        client = module.CosmosClient.from_connection_string(
            "AccountEndpoint=https://default.invalid;AccountKey=ZmFrZQ==;", **options
        )
    else:
        client = module.CosmosClient("https://default.invalid", "ZmFrZQ==", **options)
    try:
        assert client._adapter.name == expected
        assert connection.call_args.kwargs["_backend"] is client._adapter
    finally:
        closed = client._adapter.close()
        if inspect.isawaitable(closed):
            asyncio.run(closed)


def test_factory_env_var_picks_rust(monkeypatch):
    """Setting the environment variable to "rust" builds a Rust backend.

    It needs an endpoint and key, passed the same way the client passes them.
    """
    monkeypatch.setenv(BACKEND_ENV_VAR, BACKEND_NAME_RUST)
    backend = make_backend(None, url="https://x.documents.azure.com", credential="k")
    assert isinstance(backend, BindingAdapter)
    assert backend.name == BACKEND_NAME_RUST


def test_factory_kwarg_overrides_env_rust(monkeypatch):
    """The constructor argument wins over the environment variable."""
    monkeypatch.setenv(BACKEND_ENV_VAR, BACKEND_NAME_RUST)
    backend = make_backend(BACKEND_NAME_CORE_PYTHON)
    assert backend is LEGACY_BACKEND


def test_factory_invalid_value_fails_loud_rust(monkeypatch):
    """An unknown constructor value fails at construction."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    with pytest.raises(ValueError, match="Invalid backend"):
        make_backend("turbo")


def test_factory_invalid_env_var_fails_loud_rust(monkeypatch):
    """An unknown environment-variable value fails at construction."""
    monkeypatch.setenv(BACKEND_ENV_VAR, "turbo")
    with pytest.raises(ValueError, match="Invalid backend"):
        make_backend(None)


def test_client_without_credential_raises_rust(monkeypatch):
    """Creating a client with no credential raises ValueError."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    with pytest.raises(ValueError, match="master-key credential"):
        make_backend(BACKEND_NAME_RUST, url="https://x.documents.azure.com", credential=None)


def test_async_factory_returns_async_backends_rust(monkeypatch):
    """The async factory returns concrete legacy and Rust backends."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    assert make_async_backend(BACKEND_NAME_CORE_PYTHON) is ASYNC_LEGACY_BACKEND
    assert isinstance(
        make_async_backend(
            BACKEND_NAME_RUST,
            url="https://x.documents.azure.com",
            credential="k",
        ),
        AsyncBindingAdapter,
    )


def test_async_factory_invalid_value_fails_loud_rust(monkeypatch):
    """The async factory rejects bad input the same way the sync one does."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    with pytest.raises(ValueError, match="Invalid backend"):
        make_async_backend("turbo")


# ---------------------------------------------------------------------------
# How the adapter sends a request
# ---------------------------------------------------------------------------
#
# The adapter passes each prepared request to the matching function in the
# compiled module and wraps the reply. If no request is given, it raises an
# error. These tests use a fake compiled module, so they need no real account.
# The async adapter works the same way.

def test_execute_without_request_raises_rust():
    """Calling execute with no request raises TypeError."""
    adapter = BindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
    with pytest.raises(TypeError, match="PreparedRequest"):
        adapter.execute(prepared=None)


def test_execute_calls_compiled_module_and_wraps_reply_rust(monkeypatch):
    """execute opens a handle, calls the matching function in the compiled
    module, and returns its status and body."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    fake_module.create_item.return_value = (201, 0, {"etag": "v1"}, b'{"id":"x"}')
    monkeypatch.setattr("azure.cosmos._backend.binding_adapter._rust_module", fake_module)

    adapter = BindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
    prepared = PreparedRequest(
        op="create_item",
        container_link="dbs/d/colls/c",
        body_bytes=b'{"id":"x"}',
        partition_key=key_from_legacy_header('["a"]'),
        headers={},
    )
    response = adapter.execute(prepared)

    fake_module.acquire_driver_handle.assert_called_once_with(
        "https://x.documents.azure.com", "k", None
    )
    fake_module.create_item.assert_called_once_with("handle-1", prepared)
    assert response.status_code == 201
    assert response.body == b'{"id":"x"}'


def test_container_metadata_comes_from_compiled_module_rust(monkeypatch):
    """The adapter reads container details (resource id, partition key paths
    and kind) from the compiled module."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    fake_module.get_container_metadata.return_value = (
        "rid-1", ("/pk",), "Hash", None,
    )
    monkeypatch.setattr("azure.cosmos._backend.binding_adapter._rust_module", fake_module)

    adapter = BindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
    response = adapter.get_container_metadata("dbs/d/colls/c")

    fake_module.get_container_metadata.assert_called_once_with(
        "handle-1", "dbs/d/colls/c"
    )
    assert response.rid == "rid-1"
    assert response.partition_key_paths == ("/pk",)
    assert response.partition_key_kind == "Hash"


def test_container_metadata_raises_when_function_missing_rust(monkeypatch):
    """If the compiled module has no get_container_metadata function, the
    adapter raises NotImplementedError."""
    class OlderCompiledModule:
        """A compiled module from an older build that only knows how to open a handle."""

        @staticmethod
        def acquire_driver_handle(*_args):
            return "handle-1"

    monkeypatch.setattr(
        "azure.cosmos._backend.binding_adapter._rust_module", OlderCompiledModule()
    )
    adapter = BindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")

    with pytest.raises(NotImplementedError, match="get_container_metadata"):
        adapter.get_container_metadata("dbs/d/colls/c")


def test_query_items_sends_query_to_compiled_module_rust(monkeypatch):
    """A query sent through execute_pages reaches query_items in the compiled
    module, and the page and continuation token come back."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    fake_module.query_items.return_value = (
        200,
        0,
        {"x-ms-continuation": "ct-1"},
        b'{"Documents":[{"id":"x"}]}',
    )
    monkeypatch.setattr("azure.cosmos._backend.binding_adapter._rust_module", fake_module)

    adapter = BindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
    prepared = PreparedPageRequest(
        op=OP_QUERY_ITEMS,
        container_link="dbs/d/colls/c",
        query="SELECT * FROM c",
        partition_key=key_from_legacy_header('["a"]', extract=False),
        headers={},
    )
    pages = list(adapter.execute_pages(prepared))

    sent_request = fake_module.query_items.call_args.args[1]
    assert sent_request.op == OP_QUERY_ITEMS
    assert sent_request.body_bytes == b'{"query":"SELECT * FROM c"}'
    assert pages[0].status_code == 200
    assert pages[0].continuation == "ct-1"
    assert pages[0].body == b'{"Documents":[{"id":"x"}]}'


def test_paged_operations_are_not_single_response_operations_rust():
    """Operations that return pages are only sent through execute_pages, never
    through execute.

    read_items, read_all_items and change feed always use a saved position
    (cursor) between pages, so they only use fetch_page_with_cursor.
    """
    assert OP_QUERY_ITEMS not in OP_TO_BINDING_FUNCTION_NAME
    assert OP_READ_ITEMS not in OP_TO_BINDING_FUNCTION_NAME
    assert OP_READ_ALL_ITEMS not in OP_TO_BINDING_FUNCTION_NAME
    assert OP_LIST_DATABASES not in OP_TO_BINDING_FUNCTION_NAME
    assert OP_QUERY_DATABASES not in OP_TO_BINDING_FUNCTION_NAME
    assert OP_LIST_CONTAINERS not in OP_TO_BINDING_FUNCTION_NAME
    assert OP_QUERY_CONTAINERS not in OP_TO_BINDING_FUNCTION_NAME
    assert "query_items_change_feed" not in OP_TO_BINDING_FUNCTION_NAME
    assert STATELESS_PAGE_BINDING_FUNCTION_NAMES == {
        OP_QUERY_ITEMS: "query_items",
        OP_LIST_DATABASES: "list_databases",
        OP_QUERY_DATABASES: "query_databases",
        OP_LIST_CONTAINERS: "list_containers",
        OP_QUERY_CONTAINERS: "query_containers",
    }
    from azure.cosmos._backend.operations import RETAINED_PAGE_BINDING_FUNCTION_NAMES
    assert RETAINED_PAGE_BINDING_FUNCTION_NAMES == {
        OP_QUERY_ITEMS: "fetch_page_with_cursor",
        OP_READ_ITEMS: "fetch_page_with_cursor",
        OP_READ_ALL_ITEMS: "fetch_page_with_cursor",
        "query_items_change_feed": "fetch_page_with_cursor",
    }


def test_unsupported_query_raises_unsupported_query_error_rust(monkeypatch):
    """When the compiled module says a query feature is not supported, the
    adapter raises UnsupportedQueryError."""
    class _UnsupportedQueryFeatureError(RuntimeError):
        """The error the compiled module raises for an unsupported query feature."""

        pass

    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    fake_module.query_items.side_effect = _UnsupportedQueryFeatureError(
        "unsupported query feature"
    )
    monkeypatch.setattr("azure.cosmos._backend.binding_adapter._rust_module", fake_module)
    monkeypatch.setattr(
        "azure.cosmos._backend.binding_adapter._UNSUPPORTED_QUERY_ERROR",
        _UnsupportedQueryFeatureError,
    )

    adapter = BindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
    prepared = PreparedPageRequest(
        op=OP_QUERY_ITEMS,
        container_link="dbs/d/colls/c",
        query="SELECT VALUE COUNT(1) FROM c",
    )

    with pytest.raises(UnsupportedQueryError):
        list(adapter.execute_pages(prepared))


@pytest.mark.parametrize("op", [OP_READ_ITEMS, OP_READ_ALL_ITEMS])
def test_read_items_without_cursor_is_rejected_rust(monkeypatch, op):
    """read_items and read_all_items must use a cursor.

    Without one, the adapter raises PagePreflightError and calls nothing in the
    compiled module, even if an older build still has a function with that name.
    """
    fake_module = MagicMock()
    monkeypatch.setattr("azure.cosmos._backend.binding_adapter._rust_module", fake_module)

    adapter = BindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
    prepared = PreparedPageRequest(
        op=op,
        container_link="dbs/d/colls/c",
        partition_key=key_from_legacy_header("[]", extract=False),
        headers={},
    )
    with pytest.raises(PagePreflightError, match=f"does not yet support op='{op}'"):
        list(adapter.execute_pages(prepared))

    getattr(fake_module, op).assert_not_called()
    fake_module.fetch_page_with_cursor.assert_not_called()
    fake_module.acquire_driver_handle.assert_not_called()


def test_get_throughput_calls_compiled_module_rust(monkeypatch):
    """A get_throughput request reaches get_throughput in the compiled module,
    and the reply comes back unchanged."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    fake_module.get_throughput.return_value = (
        200,
        0,
        {"x-ms-continuation": "ct-read-offer"},
        b'{"Offers":[{"id":"offer-1","resource":"dbs/d/colls/c"}]}',
    )
    monkeypatch.setattr("azure.cosmos._backend.binding_adapter._rust_module", fake_module)

    adapter = BindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
    prepared = PreparedRequest(
        op=OP_GET_THROUGHPUT,
        container_link="dbs/d/colls/c",
        body_bytes=b'{"query":"SELECT * FROM root r WHERE r.resource=@link","parameters":[]}',
        partition_key=key_from_legacy_header("[]"),
        headers={},
    )
    response = adapter.execute(prepared)

    fake_module.get_throughput.assert_called_once_with("handle-1", prepared)
    assert response.status_code == 200
    assert b'"Offers"' in response.body


def test_read_feed_ranges_calls_compiled_module_rust(monkeypatch):
    """A read_feed_ranges request reaches read_feed_ranges in the compiled
    module, and the reply comes back unchanged."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    fake_module.read_feed_ranges.return_value = (
        200,
        0,
        {},
        b'{"PartitionKeyRanges":[{"id":"0","minInclusive":"","maxExclusive":"FF"}]}',
    )
    monkeypatch.setattr("azure.cosmos._backend.binding_adapter._rust_module", fake_module)

    adapter = BindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
    prepared = PreparedRequest(
        op=OP_READ_FEED_RANGES,
        container_link="dbs/d/colls/c",
        body_bytes=b'{"forceRefresh":true}',
        partition_key=key_from_legacy_header("[]"),
        headers={},
    )
    response = adapter.execute(prepared)

    fake_module.read_feed_ranges.assert_called_once_with("handle-1", prepared)
    assert response.status_code == 200
    assert b"PartitionKeyRanges" in response.body


def test_feed_range_from_partition_key_calls_compiled_module_rust(monkeypatch):
    """A feed_range_from_partition_key request reaches the function of the same
    name in the compiled module, and the reply comes back unchanged."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    fake_module.feed_range_from_partition_key.return_value = (
        200,
        0,
        {},
        b'{"Range":{"min":"3C","max":"3C","isMinInclusive":true,"isMaxInclusive":true}}',
    )
    monkeypatch.setattr("azure.cosmos._backend.binding_adapter._rust_module", fake_module)

    adapter = BindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
    prepared = PreparedRequest(
        op=OP_FEED_RANGE_FROM_PARTITION_KEY,
        container_link="dbs/d/colls/c",
        body_bytes=b"",
        partition_key=key_from_legacy_header('["a"]', feed_range=True),
        headers={},
    )
    response = adapter.execute(prepared)

    fake_module.feed_range_from_partition_key.assert_called_once_with("handle-1", prepared)
    assert response.status_code == 200
    assert b'"Range"' in response.body


@pytest.mark.parametrize("body", [b'{"id":"x"}', b""])
def test_reply_with_diagnostics_is_accepted_rust(monkeypatch, body):
    """The compiled module may add a diagnostics string to its reply. The
    adapter keeps it on the response, with or without a body."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    fake_module.create_item.return_value = (
        201,
        0,
        {"etag": "v1"},
        body,
        "activity=abc duration=8ms requests=1 charge=1RU status=201",
    )
    monkeypatch.setattr("azure.cosmos._backend.binding_adapter._rust_module", fake_module)

    adapter = BindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
    prepared = PreparedRequest(
        op="create_item",
        container_link="dbs/d/colls/c",
        body_bytes=b'{"id":"x"}',
        partition_key=key_from_legacy_header('["a"]'),
        headers={},
    )
    response = adapter.execute(prepared)

    assert response.status_code == 201
    assert response.sub_status == 0
    assert response.headers["etag"] == "v1"
    assert response.body == body
    assert response.diagnostics == "activity=abc duration=8ms requests=1 charge=1RU status=201"


def test_service_error_reply_is_returned_as_response_rust(monkeypatch):
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
    monkeypatch.setattr("azure.cosmos._backend.binding_adapter._rust_module", fake_module)

    adapter = BindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
    prepared = PreparedRequest(
        op="create_item",
        container_link="dbs/d/colls/c",
        body_bytes=b'{"id":"x"}',
        partition_key=key_from_legacy_header('["a"]'),
        headers={},
    )

    response = adapter.execute(prepared)

    assert response.status_code == 409
    assert response.sub_status == 1002
    assert response.headers["x-ms-activity-id"] == "act-409"
    assert response.headers["x-ms-retry-after-ms"] == "250"
    assert response.body == b'{"code":"Conflict","message":"already exists"}'


def test_request_log_names_operation_and_hides_handle_rust(monkeypatch, caplog):
    """Each request writes a debug log line with the operation name. The handle
    never appears in the log, because it is built from the account key.
    """
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-secret-fp"
    fake_module.create_item.return_value = (201, 0, {"etag": "v1"}, b'{"id":"x"}')
    monkeypatch.setattr("azure.cosmos._backend.binding_adapter._rust_module", fake_module)

    adapter = BindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
    prepared = PreparedRequest(
        op="create_item",
        container_link="dbs/d/colls/c",
        body_bytes=b'{"id":"x"}',
        partition_key=key_from_legacy_header('["a"]'),
        headers={},
    )
    with caplog.at_level(logging.DEBUG, logger="azure.cosmos._backend.binding_adapter"):
        adapter.execute(prepared)
    # Close now so the handle is released while this test's fake module is still
    # in place, and not later during another test.
    adapter.close()

    messages = [record.getMessage() for record in caplog.records]
    assert any("backend=rust" in message and "op=create_item" in message for message in messages)
    assert all("handle-secret-fp" not in message for message in messages)


def test_async_request_log_names_operation_and_hides_handle_rust(monkeypatch, caplog):
    """The async adapter writes the same debug log line and also hides the handle."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-secret-fp"
    fake_module.create_item_async = AsyncMock(return_value=(201, 0, {"etag": "v1"}, b'{"id":"x"}'))
    monkeypatch.setattr("azure.cosmos.aio._backend.binding_adapter._rust_module", fake_module)

    async def _run():
        adapter = AsyncBindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
        prepared = PreparedRequest(
            op="create_item",
            container_link="dbs/d/colls/c",
            body_bytes=b'{"id":"x"}',
            partition_key=key_from_legacy_header('["a"]'),
            headers={},
        )
        await adapter.execute(prepared)
        # Close now so the handle is released while this test's fake module is
        # still in place, and not later during another test.
        await adapter.close()

    with caplog.at_level(logging.DEBUG, logger="azure.cosmos.aio._backend.binding_adapter"):
        asyncio.run(_run())

    messages = [record.getMessage() for record in caplog.records]
    assert any("backend=rust" in message and "op=create_item" in message for message in messages)
    assert all("handle-secret-fp" not in message for message in messages)


def test_other_compiled_module_error_is_raised_unchanged_rust(monkeypatch):
    """Any other error from the compiled module (here a RuntimeError) is raised unchanged."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    fake_module.create_item.side_effect = RuntimeError("request failed: DNS lookup failed")
    monkeypatch.setattr("azure.cosmos._backend.binding_adapter._rust_module", fake_module)

    adapter = BindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
    prepared = PreparedRequest(
        op="create_item",
        container_link="dbs/d/colls/c",
        body_bytes=b'{"id":"x"}',
        partition_key=key_from_legacy_header('["a"]'),
        headers={},
    )

    with pytest.raises(RuntimeError, match="DNS lookup failed"):
        adapter.execute(prepared)


def test_missing_compiled_module_raises_import_error_rust(monkeypatch):
    """If the compiled module is not installed, execute raises ImportError right
    away with a clear message."""
    monkeypatch.setattr("azure.cosmos._backend.binding_adapter._rust_module", None)
    adapter = BindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
    prepared = PreparedRequest(
        op="create_item",
        container_link="dbs/d/colls/c",
        body_bytes=b'{"id":"x"}',
        partition_key=key_from_legacy_header('["a"]'),
        headers={},
    )
    with pytest.raises(ImportError, match="not present"):
        adapter.execute(prepared)


def test_async_execute_without_request_raises_rust():
    """Calling the async execute with no request raises TypeError."""
    async def _run():
        adapter = AsyncBindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
        with pytest.raises(TypeError, match="PreparedRequest"):
            await adapter.execute(prepared=None)
    asyncio.run(_run())


def test_async_execute_calls_compiled_module_and_wraps_reply_rust(monkeypatch):
    """The async execute opens a handle, waits for the async function in the
    compiled module, and returns its status and body."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    fake_module.create_item_async = AsyncMock(return_value=(201, 0, {"etag": "v1"}, b'{"id":"x"}'))
    monkeypatch.setattr("azure.cosmos.aio._backend.binding_adapter._rust_module", fake_module)

    async def _run():
        adapter = AsyncBindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
        prepared = PreparedRequest(
            op="create_item",
            container_link="dbs/d/colls/c",
            body_bytes=b'{"id":"x"}',
            partition_key=key_from_legacy_header('["a"]'),
            headers={},
        )
        response = await adapter.execute(prepared)
        fake_module.acquire_driver_handle.assert_called_once()
        fake_module.create_item_async.assert_awaited_once_with("handle-1", prepared)
        assert response.status_code == 201
        assert response.body == b'{"id":"x"}'
    asyncio.run(_run())


def test_async_container_metadata_comes_from_compiled_module_rust(monkeypatch):
    """The async adapter reads container details from the compiled module."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    fake_module.get_container_metadata_async = AsyncMock(
        return_value=(
            "rid-1", ("/pk",), "Hash", None,
        )
    )
    monkeypatch.setattr("azure.cosmos.aio._backend.binding_adapter._rust_module", fake_module)

    async def _run():
        adapter = AsyncBindingAdapter(
            endpoint="https://x.documents.azure.com", master_key="k"
        )
        response = await adapter.get_container_metadata("dbs/d/colls/c")
        assert response.rid == "rid-1"
        assert response.partition_key_paths == ("/pk",)
        assert response.partition_key_kind == "Hash"

    asyncio.run(_run())
    fake_module.get_container_metadata_async.assert_awaited_once_with(
        "handle-1", "dbs/d/colls/c"
    )


def test_async_container_metadata_raises_when_function_missing_rust(monkeypatch):
    """If the compiled module has no get_container_metadata_async function, the
    async adapter raises NotImplementedError."""
    class OlderCompiledModule:
        """A compiled module from an older build that only knows how to open a handle."""

        @staticmethod
        def acquire_driver_handle(*_args):
            return "handle-1"

    monkeypatch.setattr(
        "azure.cosmos.aio._backend.binding_adapter._rust_module", OlderCompiledModule()
    )

    async def _run():
        adapter = AsyncBindingAdapter(
            endpoint="https://x.documents.azure.com", master_key="k"
        )
        with pytest.raises(NotImplementedError, match="get_container_metadata_async"):
            await adapter.get_container_metadata("dbs/d/colls/c")

    asyncio.run(_run())


# The async versions of the tests above.
def test_async_query_items_sends_query_to_compiled_module_rust(monkeypatch):
    """A query sent through the async execute_pages reaches query_items_async in
    the compiled module, and the page and continuation token come back."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    fake_module.query_items_async = AsyncMock(
        return_value=(200, 0, {"x-ms-continuation": "ct-1"}, b'{"Documents":[{"id":"x"}]}')
    )
    monkeypatch.setattr("azure.cosmos.aio._backend.binding_adapter._rust_module", fake_module)

    async def _run():
        adapter = AsyncBindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
        prepared = PreparedPageRequest(
            op=OP_QUERY_ITEMS,
            container_link="dbs/d/colls/c",
            query="SELECT * FROM c",
            partition_key=key_from_legacy_header('["a"]', extract=False),
            headers={},
        )
        pages = [page async for page in adapter.execute_pages(prepared)]
        sent_request = fake_module.query_items_async.await_args.args[1]
        assert sent_request.op == OP_QUERY_ITEMS
        assert sent_request.body_bytes == b'{"query":"SELECT * FROM c"}'
        assert pages[0].status_code == 200
        assert pages[0].continuation == "ct-1"
        assert pages[0].body == b'{"Documents":[{"id":"x"}]}'

    asyncio.run(_run())


@pytest.mark.parametrize("op", [OP_READ_ITEMS, OP_READ_ALL_ITEMS])
def test_async_read_items_without_cursor_is_rejected_rust(monkeypatch, op):
    """The async adapter also rejects read_items and read_all_items without a
    cursor, and calls nothing in the compiled module."""
    fake_module = MagicMock()
    setattr(fake_module, f"{op}_async", AsyncMock())
    fake_module.fetch_page_with_cursor_async = AsyncMock()
    monkeypatch.setattr("azure.cosmos.aio._backend.binding_adapter._rust_module", fake_module)

    async def _run():
        adapter = AsyncBindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
        prepared = PreparedPageRequest(
            op=op,
            container_link="dbs/d/colls/c",
            partition_key=key_from_legacy_header("[]", extract=False),
            headers={},
        )
        with pytest.raises(PagePreflightError, match=f"does not yet support op='{op}'"):
            [page async for page in adapter.execute_pages(prepared)]

    asyncio.run(_run())
    getattr(fake_module, f"{op}_async").assert_not_awaited()
    fake_module.fetch_page_with_cursor_async.assert_not_awaited()
    fake_module.acquire_driver_handle.assert_not_called()


def test_async_unsupported_query_raises_unsupported_query_error_rust(monkeypatch):
    """When the compiled module says a query feature is not supported, the async
    adapter raises UnsupportedQueryError."""
    class _UnsupportedQueryFeatureError(RuntimeError):
        """The error the compiled module raises for an unsupported query feature."""

        pass

    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    fake_module.query_items_async = AsyncMock(
        side_effect=_UnsupportedQueryFeatureError("unsupported query feature")
    )
    monkeypatch.setattr("azure.cosmos.aio._backend.binding_adapter._rust_module", fake_module)
    monkeypatch.setattr(
        "azure.cosmos.aio._backend.binding_adapter._UNSUPPORTED_QUERY_ERROR",
        _UnsupportedQueryFeatureError,
    )

    async def _run():
        adapter = AsyncBindingAdapter(
            endpoint="https://x.documents.azure.com", master_key="k"
        )
        prepared = PreparedPageRequest(
            op=OP_QUERY_ITEMS,
            container_link="dbs/d/colls/c",
            query="SELECT * FROM c ORDER BY c.ts",
        )
        with pytest.raises(UnsupportedQueryError):
            [page async for page in adapter.execute_pages(prepared)]

    asyncio.run(_run())


def test_async_get_throughput_calls_compiled_module_rust(monkeypatch):
    """A get_throughput request reaches get_throughput_async in the compiled
    module, and the reply comes back unchanged."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    fake_module.get_throughput_async = AsyncMock(
        return_value=(200, 0, {"x-ms-continuation": "ct-read-offer-async"}, b'{"Offers":[{"id":"offer-1"}]}')
    )
    monkeypatch.setattr("azure.cosmos.aio._backend.binding_adapter._rust_module", fake_module)

    async def _run():
        adapter = AsyncBindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
        prepared = PreparedRequest(
            op=OP_GET_THROUGHPUT,
            container_link="dbs/d/colls/c",
            body_bytes=b'{"query":"SELECT * FROM root r WHERE r.resource=@link","parameters":[]}',
            partition_key=key_from_legacy_header("[]"),
            headers={},
        )
        response = await adapter.execute(prepared)
        fake_module.get_throughput_async.assert_awaited_once_with("handle-1", prepared)
        assert response.status_code == 200
        assert b'"Offers"' in response.body

    asyncio.run(_run())


def test_async_read_feed_ranges_calls_compiled_module_rust(monkeypatch):
    """A read_feed_ranges request reaches read_feed_ranges_async in the compiled
    module, and the reply comes back unchanged."""
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
    monkeypatch.setattr("azure.cosmos.aio._backend.binding_adapter._rust_module", fake_module)

    async def _run():
        adapter = AsyncBindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
        prepared = PreparedRequest(
            op=OP_READ_FEED_RANGES,
            container_link="dbs/d/colls/c",
            body_bytes=b'{"forceRefresh":false}',
            partition_key=key_from_legacy_header("[]"),
            headers={},
        )
        response = await adapter.execute(prepared)
        fake_module.read_feed_ranges_async.assert_awaited_once_with("handle-1", prepared)
        assert response.status_code == 200
        assert b"PartitionKeyRanges" in response.body

    asyncio.run(_run())


def test_async_feed_range_from_partition_key_calls_compiled_module_rust(monkeypatch):
    """A feed_range_from_partition_key request reaches
    feed_range_from_partition_key_async in the compiled module, and the reply
    comes back unchanged."""
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
    monkeypatch.setattr("azure.cosmos.aio._backend.binding_adapter._rust_module", fake_module)

    async def _run():
        adapter = AsyncBindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
        prepared = PreparedRequest(
            op=OP_FEED_RANGE_FROM_PARTITION_KEY,
            container_link="dbs/d/colls/c",
            body_bytes=b"",
            partition_key=key_from_legacy_header('["a"]', feed_range=True),
            headers={},
        )
        response = await adapter.execute(prepared)
        fake_module.feed_range_from_partition_key_async.assert_awaited_once_with("handle-1", prepared)
        assert response.status_code == 200
        assert b'"Range"' in response.body

    asyncio.run(_run())


def test_async_reply_with_diagnostics_is_accepted_rust(monkeypatch):
    """The async adapter keeps the diagnostics string from the compiled module's
    reply on the response."""
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
    monkeypatch.setattr("azure.cosmos.aio._backend.binding_adapter._rust_module", fake_module)

    async def _run():
        adapter = AsyncBindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
        prepared = PreparedRequest(
            op="create_item",
            container_link="dbs/d/colls/c",
            body_bytes=b'{"id":"x"}',
            partition_key=key_from_legacy_header('["a"]'),
            headers={},
        )
        response = await adapter.execute(prepared)
        assert response.status_code == 201
        assert response.diagnostics == "activity=abc duration=7ms requests=1 charge=1RU status=201"

    asyncio.run(_run())


def test_async_service_error_reply_is_returned_as_response_rust(monkeypatch):
    """A failed request (like a 404) comes back from the async adapter as a
    normal response with its status, headers and body, not as an error."""
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
    monkeypatch.setattr("azure.cosmos.aio._backend.binding_adapter._rust_module", fake_module)

    async def _run():
        adapter = AsyncBindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
        prepared = PreparedRequest(
            op="create_item",
            container_link="dbs/d/colls/c",
            body_bytes=b'{"id":"x"}',
            partition_key=key_from_legacy_header('["a"]'),
            headers={},
        )
        response = await adapter.execute(prepared)
        assert response.status_code == 404
        assert response.headers["x-ms-activity-id"] == "act-404"
        assert response.body == b'{"code":"NotFound","message":"missing"}'

    asyncio.run(_run())


def test_async_other_compiled_module_error_is_raised_unchanged_rust(monkeypatch):
    """The async version of the test above."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    fake_module.create_item_async = AsyncMock(side_effect=RuntimeError("request failed: TLS handshake failed"))
    monkeypatch.setattr("azure.cosmos.aio._backend.binding_adapter._rust_module", fake_module)

    async def _run():
        adapter = AsyncBindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
        prepared = PreparedRequest(
            op="create_item",
            container_link="dbs/d/colls/c",
            body_bytes=b'{"id":"x"}',
            partition_key=key_from_legacy_header('["a"]'),
            headers={},
        )
        with pytest.raises(RuntimeError, match="TLS handshake failed"):
            await adapter.execute(prepared)

    asyncio.run(_run())


def test_async_missing_compiled_module_raises_import_error_rust(monkeypatch):
    """If the compiled module is not installed, the async execute raises
    ImportError right away with a clear message."""
    monkeypatch.setattr("azure.cosmos.aio._backend.binding_adapter._rust_module", None)

    async def _run():
        adapter = AsyncBindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
        prepared = PreparedRequest(
            op="create_item",
            container_link="dbs/d/colls/c",
            body_bytes=b'{"id":"x"}',
            partition_key=key_from_legacy_header('["a"]'),
            headers={},
        )
        with pytest.raises(ImportError, match="not present"):
            await adapter.execute(prepared)
    asyncio.run(_run())


def test_async_concurrent_first_requests_open_one_handle_rust(monkeypatch):
    """When 50 requests start at the same time on a new client, the handle is
    opened only once. All 50 wait for that one open and then run."""
    open_calls = []
    fake_module = MagicMock()

    def _slow_open(*args):
        # Wait a little so all 50 requests arrive while the first open is still
        # running. Without the shared open, each of them would start its own.
        open_calls.append(args)
        time.sleep(0.05)
        return "handle-1"

    fake_module.acquire_driver_handle.side_effect = _slow_open
    fake_module.read_item_async = AsyncMock(return_value=(200, 0, {}, b"{}"))
    monkeypatch.setattr("azure.cosmos.aio._backend.binding_adapter._rust_module", fake_module)

    prepared = PreparedRequest(
        op="read_item",
        container_link="dbs/d/colls/c",
        body_bytes=b"",
        partition_key=key_from_legacy_header('["a"]'),
        headers={},
        item_id="x",
    )

    async def _run():
        adapter = AsyncBindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
        await asyncio.gather(*(adapter.execute(prepared) for _ in range(50)))

    asyncio.run(_run())
    assert len(open_calls) == 1, f"acquire_driver_handle should run once, ran {len(open_calls)} times"
    assert fake_module.read_item_async.await_count == 50


@pytest.mark.parametrize("close_during_creation", [False, True])
def test_async_handle_open_leaves_threads_for_token_and_close_rust(monkeypatch, close_during_creation):
    """Two clients for the same account open their handles on their own
    background threads. This leaves the shared thread pool free for the
    credential to get a token and for close to run, so neither waits forever."""
    from types import SimpleNamespace
    from azure.core.credentials import AccessToken
    from azure.cosmos.aio._backend import binding_adapter

    async def run():
        loop = asyncio.get_running_loop()
        loop.set_default_executor(concurrent.futures.ThreadPoolExecutor(max_workers=2))
        both_entered = asyncio.Event()
        token_submitted = asyncio.Event()
        finish_token = asyncio.Event()
        token_started = threading.Event()
        arrivals_lock = threading.Lock()
        creation_lock = threading.Lock()
        arrivals = []
        token_requests = []
        acquired = []
        released = []
        cached = False

        class Credential:
            async def get_token(self, *_scopes, **_kwargs):
                await both_entered.wait()
                token_submitted.set()

                def token_work():
                    token_started.set()
                    return AccessToken("test-token", 4102444800)

                token = await asyncio.to_thread(token_work)
                await finish_token.wait()
                return token

        def open_handle(_endpoint, _key, _config, credential):
            nonlocal cached
            with arrivals_lock:
                arrivals.append(credential)
                if len(arrivals) == 2:
                    loop.call_soon_threadsafe(both_entered.set)
            # Act like the compiled module: clients for the same account open one
            # at a time, and the first one asks the real token helper for a token.
            with creation_lock:
                if not cached:
                    request = credential._start_token_request("https://cosmos.azure.com/.default")
                    token_requests.append(request)
                    request.result(timeout=10)
                    cached = True
                handle = object()
                acquired.append(handle)
                return handle

        monkeypatch.setattr(
            binding_adapter,
            "_rust_module",
            SimpleNamespace(
                acquire_driver_handle=open_handle,
                release_driver_handle=released.append,
                _DriverResponseError=type("_DriverResponseError", (RuntimeError,), {}),
                _DriverTransportError=type("_DriverTransportError", (RuntimeError,), {}),
            ),
        )
        credential = Credential()
        adapters = [
            AsyncBindingAdapter("https://alpha-bank.documents.azure.com", token_credential=credential) for _ in range(2)
        ]
        initializations = [asyncio.create_task(adapter.initialize()) for adapter in adapters]
        closes = []
        try:
            await asyncio.wait_for(token_submitted.wait(), timeout=5)
            assert arrivals[0] is arrivals[1]
            if close_during_creation:
                closes = [asyncio.create_task(adapter.close()) for adapter in adapters]
                _, pending = await asyncio.wait(closes, timeout=2)
                assert not pending, "Opening handles blocked close from running"
                await asyncio.gather(*closes)
                results = await asyncio.wait_for(asyncio.gather(*initializations, return_exceptions=True), timeout=5)
                assert all(isinstance(result, BaseException) for result in results)
                assert not acquired
            else:
                finish_token.set()
                _, pending = await asyncio.wait(initializations, timeout=2)
                assert not pending, "Opening handles blocked the credential from getting a token"
                await asyncio.gather(*initializations)
                assert token_started.is_set()
                assert len(token_requests) == 1
                assert len(acquired) == 2
                assert acquired[0] is not acquired[1]
                await asyncio.wait_for(asyncio.gather(*(adapter.close() for adapter in adapters)), timeout=5)
                assert set(released) == set(acquired)
                assert len(released) == 2
        finally:
            # Let the fake credential finish even if the test fails, so cleanup does not hang.
            finish_token.set()
            for request in token_requests:
                request.cancel()
            await asyncio.wait_for(
                asyncio.gather(
                    *(adapter.close() for adapter in adapters),
                    *initializations,
                    *closes,
                    return_exceptions=True,
                ),
                timeout=10,
            )

    asyncio.run(run())


def test_stuck_handle_open_does_not_block_process_exit_rust():
    """If opening a handle never finishes, the program can still exit once its
    own work is done. The check runs in a separate Python process that must end
    within 5 seconds."""
    code = textwrap.dedent("""
        import asyncio
        import threading
        from types import SimpleNamespace
        from azure.cosmos.aio._backend import binding_adapter

        async def main():
            loop = asyncio.get_running_loop()
            started = asyncio.Event()
            def open_handle(*args):
                loop.call_soon_threadsafe(started.set)
                threading.Event().wait()
            binding_adapter._rust_module = SimpleNamespace(
                acquire_driver_handle=open_handle, release_driver_handle=lambda handle: None,
                _DriverResponseError=type("_DriverResponseError", (RuntimeError,), {}),
                _DriverTransportError=type("_DriverTransportError", (RuntimeError,), {}),
            )
            adapter = binding_adapter.AsyncBindingAdapter("https://exit.invalid", master_key="key")
            pending = asyncio.create_task(adapter.initialize())
            await asyncio.wait_for(started.wait(), timeout=3)
            await adapter.close()
            pending.cancel()
            await asyncio.gather(pending, return_exceptions=True)

        asyncio.run(main())
        print("main finished", flush=True)
    """)
    with subprocess.Popen(
        sdk_python_command(code), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    ) as process:
        try:
            stdout, stderr = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate(timeout=5)
            assert "main finished" in stdout, stderr
            pytest.fail("A stuck handle open kept the process from exiting after the program finished")
    assert process.returncode == 0, stderr
    assert "main finished" in stdout


def test_slow_handle_open_does_not_delay_other_account_rust(monkeypatch):
    """While 32 clients wait for a slow handle open on one account, a client for
    a different account still opens its handle right away."""
    from types import SimpleNamespace
    from azure.cosmos.aio._backend import binding_adapter

    waiter_count = 32

    async def run():
        loop = asyncio.get_running_loop()
        all_waiting = asyncio.Event()
        release_open = threading.Event()
        arrivals_lock, creation_lock = threading.Lock(), threading.Lock()
        arrivals = 0
        cached = False

        def open_handle(endpoint, *_args):
            nonlocal arrivals, cached
            if endpoint == "https://unrelated.invalid":
                return "unrelated-handle"
            with arrivals_lock:
                arrivals += 1
                if arrivals == waiter_count:
                    loop.call_soon_threadsafe(all_waiting.set)
            with creation_lock:
                if not cached:
                    assert release_open.wait(10), "the test never released the slow handle open"
                    cached = True
            return object()

        fake_compiled_module = SimpleNamespace(
            acquire_driver_handle=open_handle, release_driver_handle=MagicMock(),
            _DriverResponseError=type("_DriverResponseError", (RuntimeError,), {}),
            _DriverTransportError=type("_DriverTransportError", (RuntimeError,), {}),
        )
        monkeypatch.setattr(binding_adapter, "_rust_module", fake_compiled_module)
        matching = [
            AsyncBindingAdapter("https://matching.invalid", master_key="key")
            for _ in range(waiter_count)
        ]
        unrelated = AsyncBindingAdapter("https://unrelated.invalid", master_key="key")
        pending = [asyncio.create_task(adapter.initialize()) for adapter in matching]
        try:
            await asyncio.wait_for(all_waiting.wait(), timeout=5)
            unrelated_open = asyncio.create_task(unrelated.initialize())
            pending.append(unrelated_open)
            await asyncio.wait_for(asyncio.shield(unrelated_open), timeout=1)
            assert unrelated._driver_handle == "unrelated-handle"
            assert not release_open.is_set()
        finally:
            release_open.set()
            await asyncio.wait_for(asyncio.gather(*pending, return_exceptions=True), timeout=5)
            await asyncio.gather(*(adapter.close() for adapter in [*matching, unrelated]))

    asyncio.run(run())


def test_async_handle_open_retries_after_thread_start_failure_rust(monkeypatch):
    """If the background thread fails to start, initialize raises the error. The
    next call to initialize starts a new thread and succeeds."""
    from types import SimpleNamespace
    from azure.cosmos._backend import _binding_adapter_shared as shared
    from azure.cosmos.aio._backend import binding_adapter

    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    monkeypatch.setattr(binding_adapter, "_rust_module", fake_module)

    starts = 0

    def fail_first_start(*args, **kwargs):
        nonlocal starts
        starts += 1
        if starts == 1:
            return SimpleNamespace(start=MagicMock(side_effect=RuntimeError("acquisition start failed")))
        return threading.Thread(*args, **kwargs)

    monkeypatch.setattr(shared, "threading", SimpleNamespace(Thread=fail_first_start, Lock=threading.Lock))

    async def run():
        adapter = AsyncBindingAdapter("https://alpha-bank.documents.azure.com", master_key="key")
        try:
            with pytest.raises(RuntimeError, match="acquisition start failed"):
                await adapter.initialize()
            assert adapter._init_future is None
            fake_module.acquire_driver_handle.assert_not_called()
            await adapter.initialize()
            assert adapter._driver_handle == "handle-1"
        finally:
            await adapter.close()

    asyncio.run(run())
    assert starts == 2
    fake_module.acquire_driver_handle.assert_called_once()
    fake_module.release_driver_handle.assert_called_once_with("handle-1")


def test_async_handle_opens_after_event_loop_pool_shut_down_rust(monkeypatch):
    """The async client can still open and release its handle after the event
    loop has shut down its shared thread pool, because the handle opens on its
    own thread."""
    from azure.cosmos.aio._backend import binding_adapter

    fake_module = MagicMock()
    fake_module.acquire_driver_handle.side_effect = ["handle-1", "handle-2"]
    monkeypatch.setattr(binding_adapter, "_rust_module", fake_module)

    async def run(shutdown_default_executor):
        if shutdown_default_executor:
            await asyncio.get_running_loop().shutdown_default_executor()
        adapter = AsyncBindingAdapter("https://alpha-bank.documents.azure.com", master_key="key")
        try:
            await adapter.initialize()
        finally:
            await adapter.close()

    asyncio.run(run(False))
    asyncio.run(run(True))
    assert fake_module.acquire_driver_handle.call_count == 2
    assert [call.args[0] for call in fake_module.release_driver_handle.call_args_list] == ["handle-1", "handle-2"]


def test_async_handle_open_continues_after_first_caller_cancels_rust(monkeypatch):
    """If the first caller cancels while the handle is opening, the open keeps
    going. A later call from a different event loop waits for that same open, so
    the handle is opened only once."""
    from azure.cosmos.aio._backend import binding_adapter

    started, release_open = threading.Event(), threading.Event()
    fake_module = MagicMock()

    def open_handle(*_args):
        started.set()
        assert release_open.wait(5), "the test never released the handle open"
        return "shared-handle"

    fake_module.acquire_driver_handle.side_effect = open_handle
    monkeypatch.setattr(binding_adapter, "_rust_module", fake_module)
    adapter = AsyncBindingAdapter("https://shared-loops.invalid", master_key="key")

    async def cancel_waiter():
        pending = asyncio.create_task(adapter.initialize())
        try:
            assert await asyncio.to_thread(started.wait, 2)
        finally:
            pending.cancel()
            await asyncio.gather(pending, return_exceptions=True)

    async def finish_from_another_loop(original):
        pending = asyncio.create_task(adapter.initialize())
        try:
            await asyncio.sleep(0)
            assert adapter._init_future is original
            assert not original.cancelled()
        finally:
            release_open.set()
            await asyncio.wait_for(pending, timeout=2)

    try:
        asyncio.run(cancel_waiter())
        original = adapter._init_future
        assert original is not None
        asyncio.run(finish_from_another_loop(original))
        assert adapter._driver_handle == "shared-handle"
        fake_module.acquire_driver_handle.assert_called_once()
    finally:
        release_open.set()
        asyncio.run(adapter.close())
    fake_module.release_driver_handle.assert_called_once_with("shared-handle")


def test_async_handle_open_sees_caller_context_variables_rust(monkeypatch):
    """The handle opens on a different thread, but it still sees the caller's
    context variables (values set with contextvars.ContextVar, such as tracing ids)."""
    import contextvars
    from azure.cosmos.aio._backend import binding_adapter

    caller_value = contextvars.ContextVar("caller-value")
    caller_value.set("customer-call")
    caller = threading.get_ident()
    observed = []
    fake_module = MagicMock()

    def open_handle(*_args):
        observed.append((caller_value.get(), threading.get_ident()))
        return "context-handle"

    fake_module.acquire_driver_handle.side_effect = open_handle
    monkeypatch.setattr(binding_adapter, "_rust_module", fake_module)

    async def run():
        adapter = AsyncBindingAdapter("https://context.invalid", master_key="key")
        try:
            await adapter.initialize()
        finally:
            await adapter.close()

    asyncio.run(run())
    assert len(observed) == 1
    assert observed[0][0] == "customer-call"
    assert observed[0][1] != caller


@pytest.mark.parametrize("error_type", [RuntimeError, TimeoutError, asyncio.CancelledError])
def test_async_handle_open_retries_after_failure_rust(monkeypatch, error_type):
    """If opening the handle fails, the caller gets the original error with its
    cause. The next request tries to open the handle again instead of getting the
    same failure every time."""
    attempts = []
    error = error_type("init boom")
    original_cause = ValueError("credential cause")
    error.__cause__ = original_cause
    fake_module = MagicMock()
    fake_module._DriverResponseError = type("_DriverResponseError", (RuntimeError,), {})
    fake_module._DriverTransportError = type("_DriverTransportError", (RuntimeError,), {})

    def _fails_once(*args):
        attempts.append(args)
        if len(attempts) == 1:
            raise error
        return "handle-1"

    fake_module.acquire_driver_handle.side_effect = _fails_once
    fake_module.read_item_async = AsyncMock(return_value=(200, 0, {}, b"{}"))
    monkeypatch.setattr("azure.cosmos.aio._backend.binding_adapter._rust_module", fake_module)

    prepared = PreparedRequest(
        op="read_item",
        container_link="dbs/d/colls/c",
        body_bytes=b"",
        partition_key=key_from_legacy_header('["a"]'),
        headers={},
        item_id="x",
    )

    async def _run():
        adapter = AsyncBindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
        # First request: opening the handle fails and the caller gets the error.
        with pytest.raises(error_type, match="init boom") as caught:
            await adapter.execute(prepared)
        assert caught.value is error
        assert caught.value.__cause__ is original_cause
        # Second request: the handle opens and the request succeeds.
        response = await adapter.execute(prepared)
        assert response.status_code == 200
        await adapter.close()

    asyncio.run(_run())
    assert len(attempts) == 2, f"the handle open should be tried again after a failure, attempts={len(attempts)}"


def test_async_close_during_handle_open_releases_handle_later_rust(monkeypatch):
    """Close does not wait for a slow handle open. When the open finishes, the
    background thread releases the handle, and the waiting request fails with
    "closed during initialization"."""
    started, release_open = threading.Event(), threading.Event()
    open_threads = []
    release_threads = []
    fake_module = MagicMock()

    def open_handle(*_args):
        open_threads.append(threading.current_thread())
        started.set()
        assert release_open.wait(5), "the test never released the handle open"
        return "handle-1"

    fake_module.acquire_driver_handle.side_effect = open_handle
    fake_module.release_driver_handle.side_effect = lambda _handle: release_threads.append(threading.current_thread())
    fake_module.read_item_async = AsyncMock(return_value=(200, 0, {}, b"{}"))
    monkeypatch.setattr("azure.cosmos.aio._backend.binding_adapter._rust_module", fake_module)

    prepared = PreparedRequest(
        op="read_item",
        container_link="dbs/d/colls/c",
        body_bytes=b"",
        partition_key=key_from_legacy_header('["a"]'),
        headers={},
        item_id="x",
    )

    async def _run():
        adapter = AsyncBindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
        request_task = asyncio.create_task(adapter.execute(prepared))
        try:
            assert await asyncio.to_thread(started.wait, 2), "the handle open did not start"
            # Close must finish while the handle is still opening.
            await asyncio.wait_for(adapter.close(), timeout=2)
            assert adapter._closing
            assert adapter._driver_handle is None
            assert not release_open.is_set()
            assert not request_task.done()
            fake_module.release_driver_handle.assert_not_called()
            release_open.set()
            with pytest.raises(RuntimeError, match="closed during initialization"):
                await asyncio.wait_for(request_task, 2)
            assert adapter._driver_handle is None
            fake_module.read_item_async.assert_not_called()
        finally:
            release_open.set()
            await adapter.close()
            await asyncio.wait_for(asyncio.gather(request_task, return_exceptions=True), 5)

    try:
        asyncio.run(_run())
    finally:
        # Let the background thread finish before the fake module is removed, even if an assertion fails.
        release_open.set()
        for open_thread in open_threads:
            open_thread.join(timeout=5)
        assert all(not open_thread.is_alive() for open_thread in open_threads)
    fake_module.acquire_driver_handle.assert_called_once()
    fake_module.release_driver_handle.assert_called_once_with("handle-1")
    assert release_threads == open_threads


def test_async_cancel_reaches_compiled_module_rust(monkeypatch):
    """Cancelling execute also cancels the call into the compiled module, and the
    caller gets CancelledError."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    call_cancelled = []

    async def _slow_read(_driver_handle, _prepared):
        try:
            await asyncio.sleep(10)
        except asyncio.CancelledError:
            call_cancelled.append(True)
            raise
        return (200, 0, {}, b"{}")  # pragma: no cover - cancelled before here

    fake_module.read_item_async = _slow_read
    monkeypatch.setattr("azure.cosmos.aio._backend.binding_adapter._rust_module", fake_module)

    prepared = PreparedRequest(
        op="read_item",
        container_link="dbs/d/colls/c",
        body_bytes=b"",
        partition_key=key_from_legacy_header('["a"]'),
        headers={},
        item_id="x",
    )

    async def _run():
        adapter = AsyncBindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
        request_task = asyncio.ensure_future(adapter.execute(prepared))
        # Let the request open the handle and start the call, then cancel it.
        await asyncio.sleep(0.05)
        request_task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await request_task

    asyncio.run(_run())
    assert call_cancelled == [True], (
        "Cancelling execute() must also cancel the call into the compiled module"
    )


def test_async_finalizer_releases_handle_on_background_thread_rust(monkeypatch):
    """When Python cleans up an async client that was not closed (__del__), the
    handle is released on a background thread, so the event loop keeps running
    while the release finishes. If that thread cannot start, the release runs on
    the calling thread instead; test_client_close_unit.py covers that case.
    """
    from azure.cosmos._backend import _binding_adapter_shared as shared

    release_started = threading.Event()
    allow_release = threading.Event()
    release_finished = threading.Event()
    release_threads = []
    release_workers = []
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-finalizer"
    fake_module.read_item_async = AsyncMock(return_value=(200, 0, {}, b"{}"))

    def make_worker(*, target, name, daemon):
        release_worker = threading.Thread(target=target, name=name, daemon=daemon)
        release_workers.append(release_worker)
        return release_worker

    def blocking_release(driver_handle):
        # Other clients may be cleaned up while the fake module is in place.
        # Only pause on this test's handle.
        if driver_handle != "handle-finalizer":
            return
        release_threads.append(threading.current_thread())
        release_started.set()
        try:
            allow_release.wait(5)
        finally:
            release_finished.set()

    fake_module.release_driver_handle.side_effect = blocking_release
    monkeypatch.setattr("azure.cosmos.aio._backend.binding_adapter._rust_module", fake_module)

    prepared = PreparedRequest(
        op="read_item",
        container_link="dbs/d/colls/c",
        body_bytes=b"",
        partition_key=key_from_legacy_header('["a"]'),
        headers={},
        item_id="x",
    )

    async def _run():
        adapter = AsyncBindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
        await adapter.execute(prepared)
        event_loop_thread = threading.current_thread()
        monkeypatch.setattr(shared, "threading", SimpleNamespace(Thread=make_worker))
        try:
            adapter.__del__()
            assert release_started.wait(2), "the release thread did not start"
            for _ in range(5):
                await asyncio.sleep(0)
            assert not release_finished.is_set(), "release finished before the test allowed it"
            return event_loop_thread
        finally:
            allow_release.set()
            for release_worker in release_workers:
                release_worker.join(timeout=2)
            assert all(not release_worker.is_alive() for release_worker in release_workers), "the release thread did not finish"

    event_loop_thread = asyncio.run(_run())
    assert release_finished.is_set()
    assert len(release_threads) == 1
    assert release_threads[0] is not event_loop_thread
    assert release_threads[0].name == "cosmos-rust-finalizer"
    assert release_threads[0].daemon


def test_create_item_reply_is_returned_as_dict_rust(monkeypatch):
    """A successful create_item reply is returned as a dict, so the caller reads
    fields by key (like ``result["_etag"]``).

    The fake adapter is a real CosmosBackend subclass, so the item helper follows
    its normal steps: build the request, call execute, then read the reply.
    """

    class _FakeAdapter(CosmosBackend):
        """Return a fixed response while recording the prepared request."""

        name = BACKEND_NAME_RUST

        def __init__(self, response):
            self._response = response
            self.sent_request = None

        def execute(self, prepared, *, deadline=None):
            self.sent_request = prepared
            return self._response

        def get_container_metadata(self, link):
            return ContainerMetadata("rid")

    adapter = _FakeAdapter(
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

    helper = ItemHelper(adapter)
    result = call_create_item_helper(helper,
        container_link="dbs/x/colls/y",
        body={"id": "order-42", "pk": "customerA"},
    )

    # The result is a dict, so the caller reads fields by key.
    assert result["_etag"] == '"00000000-0000-0000-1234-567890abcdef"'
    assert result["id"] == "order-42"
    # The helper built the request and sent it to the adapter.
    assert adapter.sent_request is not None
    assert adapter.sent_request.op == "create_item"


def test_request_and_response_cannot_be_changed_rust():
    """A PreparedRequest or BackendResponse cannot be changed after it is created."""
    request = PreparedRequest(
        op="create_item",
        container_link="dbs/d/colls/c",
        body_bytes=b"{}",
        partition_key=key_from_legacy_header('["customerA"]'),
        headers={"x-ms-version": "2020-07-15"},
    )
    with pytest.raises(FrozenInstanceError):
        setattr(request, "body_bytes", b"different")

    response = BackendResponse(status_code=201)
    with pytest.raises(FrozenInstanceError):
        setattr(response, "status_code", 200)


@pytest.mark.parametrize("async_mode", [False, True])
def test_unsupported_operation_does_not_open_handle_rust(monkeypatch, async_mode):
    """An operation the adapter does not know raises NotImplementedError before
    any handle is opened."""
    module = "azure.cosmos.aio._backend.binding_adapter" if async_mode else "azure.cosmos._backend.binding_adapter"
    fake_module = MagicMock()
    monkeypatch.setattr(module + "._rust_module", fake_module)
    adapter = (AsyncBindingAdapter if async_mode else BindingAdapter)(
        "https://unsupported.invalid", master_key="key"
    )
    prepared = PreparedRequest(
        op="not-a-supported-operation", container_link="", body_bytes=b"",
        partition_key=key_from_legacy_header('["key"]'),
    )
    try:
        with pytest.raises(NotImplementedError, match="does not yet support"):
            if async_mode:
                asyncio.run(adapter.execute(prepared))
            else:
                adapter.execute(prepared)
        fake_module.acquire_driver_handle.assert_not_called()
        assert adapter._driver_handle is None
    finally:
        adapter.abort_construction()


# ---------------------------------------------------------------------------
# Client settings passed to the compiled module
# ---------------------------------------------------------------------------
#
# The factory collects client settings, such as preferred_locations, into a
# PreparedClientConfig. The adapter passes it to the compiled module when it opens
# the handle. If there are no settings to pass, it sends None.

@pytest.mark.parametrize("backend_type", [BindingAdapter, AsyncBindingAdapter])
@pytest.mark.parametrize("reverse", [False, True])
def test_clients_for_same_account_can_use_different_settings_rust(backend_type, reverse):
    """Two clients for the same account can be created with different settings,
    in either order. Each keeps its own settings, and neither opens a handle
    until it is used."""
    configs = [
        PreparedClientConfig(preferred_locations=("West US",)),
        PreparedClientConfig(preferred_locations=("East US",)),
    ]
    if reverse:
        configs.reverse()
    clients = []
    try:
        for config in configs:
            clients.append(backend_type("https://same-account.invalid", master_key="key", client_config=config))
        assert all(client._driver_handle is None for client in clients)
        assert [client._client_config for client in clients] == configs
    finally:
        for client in clients:
            client.abort_construction()


def test_build_client_config_returns_none_when_nothing_to_carry_rust():
    """With no settings, or an empty preferred_locations list, there is nothing
    to pass, so build_client_config returns None."""
    assert build_client_config(None) is None
    assert build_client_config([]) is None
    assert build_client_config(()) is None


def test_build_client_config_carries_preferred_locations_rust():
    """A non-empty preferred_locations is captured, in order, as an immutable
    tuple on the config."""
    config = build_client_config(["West US", "East US"])
    assert isinstance(config, PreparedClientConfig)
    assert config.preferred_locations == ("West US", "East US")


def test_client_config_cannot_be_changed_rust():
    """A PreparedClientConfig cannot be changed after it is created."""
    config = PreparedClientConfig(preferred_locations=("West US",))
    with pytest.raises(Exception):  # FrozenInstanceError
        setattr(config, "preferred_locations", ("East US",))


def test_factory_passes_preferred_locations_to_adapter_rust(monkeypatch):
    """make_backend puts preferred_locations into the adapter's client config.
    With no locations, the config is None."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    with_locations = make_backend(
        BACKEND_NAME_RUST,
        url="https://x.documents.azure.com",
        credential="k",
        preferred_locations=["West US", "East US"],
    )
    assert isinstance(with_locations, BindingAdapter)
    assert with_locations._client_config == PreparedClientConfig(
        preferred_locations=("West US", "East US")
    )

    without_locations = make_backend(
        BACKEND_NAME_RUST, url="https://y.documents.azure.com", credential="k"
    )
    assert isinstance(without_locations, BindingAdapter)
    assert without_locations._client_config is None


def test_async_factory_passes_preferred_locations_to_adapter_rust(monkeypatch):
    """The async factory carries preferred_locations the same way."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    adapter = make_async_backend(
        BACKEND_NAME_RUST,
        url="https://x.documents.azure.com",
        credential="k",
        preferred_locations=["West US"],
    )
    assert isinstance(adapter, AsyncBindingAdapter)
    assert adapter._client_config == PreparedClientConfig(
        preferred_locations=("West US",)
    )


def test_factory_passes_runtime_to_adapter_rust(monkeypatch):
    """make_backend gives the adapter the runtime that was passed in. Connection
    settings such as timeouts stay on the runtime, so the client config stays None."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    runtime = CosmosRuntime.create(connection_pool=ConnectionPoolOptions(
        connection_timeout=2.5, data_http_request_timeout=45))
    adapter = make_backend(
        BACKEND_NAME_RUST,
        url="https://timeouts-sync.documents.azure.com",
        credential="k",
        runtime=runtime,
    )
    assert isinstance(adapter, BindingAdapter)
    assert adapter._runtime is runtime
    assert adapter._client_config is None
    adapter.close()


def test_async_factory_passes_runtime_to_adapter_rust(monkeypatch):
    """make_async_backend also gives the adapter the runtime that was passed in,
    and the client config stays None."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    runtime = CosmosRuntime.create(connection_pool=ConnectionPoolOptions(
        connection_timeout=1.5, data_http_request_timeout=30))
    adapter = make_async_backend(
        BACKEND_NAME_RUST,
        url="https://timeouts-async.documents.azure.com",
        credential="k",
        runtime=runtime,
    )
    assert isinstance(adapter, AsyncBindingAdapter)
    assert adapter._runtime is runtime
    assert adapter._client_config is None
    asyncio.run(adapter.close())


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("log_level", [logging.INFO, logging.DEBUG])
async def test_client_construction_logs_only_at_debug_rust(monkeypatch, caplog, asynchronous, log_level):
    """Creating a client writes one log line at DEBUG level, and nothing at INFO level."""
    module = async_cosmos_client_module if asynchronous else sync_cosmos_client_module
    monkeypatch.setattr(module, "CosmosClientConnection", MagicMock())
    with caplog.at_level(log_level, logger=module.__name__):
        client = module.CosmosClient(
            "https://client-logging.documents.azure.com",
            "key",
            _backend=BACKEND_NAME_RUST,
        )
    try:
        records = [
            record for record in caplog.records
            if record.name == module.__name__
            and record.msg == "Cosmos client constructed with default backend=%s"
        ]
        if log_level == logging.DEBUG:
            assert len(records) == 1
            assert records[0].levelno == logging.DEBUG
            assert records[0].getMessage() == (
                f"Cosmos client constructed with default backend={client._adapter.name}"
            )
        else:
            assert records == []
    finally:
        if asynchronous:
            await client._adapter.close()
        else:
            client._adapter.close()


def test_client_without_settings_has_no_client_config_rust(monkeypatch):
    """A client created with no extra settings has no client config (None)."""
    monkeypatch.setattr(
        sync_cosmos_client_module, "CosmosClientConnection", MagicMock()
    )
    client = sync_cosmos_client_module.CosmosClient(
        "https://client-sync.documents.azure.com",
        "key",
        _backend=BACKEND_NAME_RUST,
    )
    assert client._adapter._client_config is None
    client._adapter.close()


@pytest.mark.asyncio
async def test_async_client_keeps_runtime_passed_in_rust(monkeypatch):
    """An async client created with runtime= keeps that runtime, and its client
    config stays None."""
    monkeypatch.setattr(
        async_cosmos_client_module, "CosmosClientConnection", MagicMock()
    )
    runtime = await CosmosRuntime.create_async(connection_pool=ConnectionPoolOptions(
        connection_timeout=2, data_http_request_timeout=30))
    client = async_cosmos_client_module.CosmosClient(
        "https://client-async.documents.azure.com",
        "key",
        _backend=BACKEND_NAME_RUST,
        runtime=runtime,
    )
    assert client._adapter._runtime is runtime
    assert client._adapter._client_config is None
    await client._adapter.close()


def test_client_config_is_sent_when_handle_opens_rust(monkeypatch):
    """When the adapter opens the handle, it sends the client config to the
    compiled module along with the endpoint and key."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    monkeypatch.setattr("azure.cosmos._backend.binding_adapter._rust_module", fake_module)

    config = PreparedClientConfig(preferred_locations=("West US", "East US"))
    adapter = BindingAdapter(
        endpoint="https://x.documents.azure.com",
        master_key="k",
        client_config=config,
    )
    adapter._ensure_driver_handle()

    fake_module.acquire_driver_handle.assert_called_once_with(
        "https://x.documents.azure.com", "k", config
    )


def test_async_client_config_is_sent_when_handle_opens_rust(monkeypatch):
    """The async adapter sends the client config the same way."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    monkeypatch.setattr("azure.cosmos.aio._backend.binding_adapter._rust_module", fake_module)

    config = PreparedClientConfig(preferred_locations=("West US",))

    async def _run():
        adapter = AsyncBindingAdapter(
            endpoint="https://x.documents.azure.com",
            master_key="k",
            client_config=config,
        )
        await adapter._ensure_driver_handle()

    asyncio.run(_run())

    fake_module.acquire_driver_handle.assert_called_once_with(
        "https://x.documents.azure.com", "k", config
    )


@pytest.mark.parametrize("first_proxy,initialize_second", [(None, False), (True, False), (True, True)])
def test_each_client_sends_its_own_runtime_rust(monkeypatch, first_proxy, initialize_second):
    """Two clients for the same account each send their own runtime (or None)
    when they open their handle, whichever client opens first."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.side_effect = ["first", "second"]
    monkeypatch.setattr("azure.cosmos._backend.binding_adapter._rust_module", fake_module)
    first_runtime = (
        CosmosRuntime.create(connection_pool=ConnectionPoolOptions(proxy_allowed=first_proxy))
        if first_proxy is not None else None
    )
    first_client = BindingAdapter(
        endpoint="https://x.documents.azure.com",
        master_key="k",
        runtime=first_runtime,
    )
    second_client = BindingAdapter(
        endpoint="https://x.documents.azure.com", master_key="k",
        runtime=CosmosRuntime.create(connection_pool=ConnectionPoolOptions(proxy_allowed=False)),
    )
    try:
        fake_module.acquire_driver_handle.assert_not_called()
        for adapter in ((second_client, first_client) if initialize_second else (first_client, second_client)):
            adapter._ensure_driver_handle()
            expected = adapter._runtime._handle if adapter._runtime is not None else None
            assert fake_module.acquire_driver_handle.call_args.kwargs.get("runtime") is expected
    finally:
        first_client.close()
        second_client.close()


def test_proxy_setting_in_client_config_is_rejected_rust(monkeypatch):
    """proxy_allowed can only be set on a runtime. Putting it in the client
    config raises ValueError, and a client created afterwards still works."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "driver"
    monkeypatch.setattr("azure.cosmos._backend.binding_adapter._rust_module", fake_module)

    with pytest.raises(ValueError, match="CosmosRuntime"):
        BindingAdapter(
            endpoint="https://x.documents.azure.com",
            master_key="k",
            client_config=SimpleNamespace(proxy_allowed=True),
        )
    client = BindingAdapter(
        endpoint="https://x.documents.azure.com",
        master_key="k",
        client_config=None,
    )

    client._ensure_driver_handle()
    client.close()


@pytest.mark.parametrize("first_proxy,initialize_second", [(None, False), (True, False), (True, True)])
def test_async_each_client_sends_its_own_runtime_rust(monkeypatch, first_proxy, initialize_second):
    """Two async clients for the same account each send their own runtime (or
    None), whichever client opens first."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.side_effect = ["first", "second"]
    monkeypatch.setattr("azure.cosmos.aio._backend.binding_adapter._rust_module", fake_module)

    async def _run():
        first_runtime = (
            await CosmosRuntime.create_async(connection_pool=ConnectionPoolOptions(proxy_allowed=first_proxy))
            if first_proxy is not None else None
        )
        first_client = AsyncBindingAdapter(
            endpoint="https://x.documents.azure.com",
            master_key="k",
            runtime=first_runtime,
        )
        second_client = AsyncBindingAdapter(
            endpoint="https://x.documents.azure.com", master_key="k",
            runtime=await CosmosRuntime.create_async(connection_pool=ConnectionPoolOptions(proxy_allowed=False)),
        )
        try:
            fake_module.acquire_driver_handle.assert_not_called()
            for adapter in ((second_client, first_client) if initialize_second else (first_client, second_client)):
                await adapter._ensure_driver_handle()
                expected = adapter._runtime._handle if adapter._runtime is not None else None
                assert fake_module.acquire_driver_handle.call_args.kwargs.get("runtime") is expected
        finally:
            await first_client.close()
            await second_client.close()

    asyncio.run(_run())


# ---------------------------------------------------------------------------
# Other client settings in the client config
# ---------------------------------------------------------------------------
#
# excluded_locations, throttle retries, hedging (availability_strategy), the
# User-Agent suffix and the consistency level go into the same
# PreparedClientConfig. Each one is added only when the user sets it, so a client
# with no settings still has no config (None).


def test_build_client_config_carries_excluded_locations_rust():
    """excluded_locations is stored as a tuple, the same way as preferred_locations."""
    config = build_client_config(None, excluded_locations=["Central US"])
    assert isinstance(config, PreparedClientConfig)
    assert config.excluded_locations == ("Central US",)
    assert config.preferred_locations == ()


def test_build_client_config_empty_excluded_locations_is_none_rust():
    """An empty excluded_locations list on its own gives no config (None)."""
    assert build_client_config(None, excluded_locations=[]) is None


def test_build_client_config_carries_throttling_retry_rust():
    """Both throttle retry settings (the retry count and the maximum wait time)
    are stored when set."""
    config = build_client_config(
        None,
        throttling_max_retry_count=9,
        throttling_max_retry_wait_time_seconds=30,
    )
    assert config.throttling_max_retry_count == 9
    assert config.throttling_max_retry_wait_time_seconds == 30


def test_build_client_config_partial_throttling_retry_leaves_other_none_rust():
    """Setting only the retry count leaves the wait time as None, so the default
    wait time is used."""
    config = build_client_config(None, throttling_max_retry_count=3)
    assert config.throttling_max_retry_count == 3
    assert config.throttling_max_retry_wait_time_seconds is None


def test_build_client_config_hedging_true_uses_default_threshold_rust():
    """availability_strategy=True carries the default threshold (500 ms)."""
    config = build_client_config(None, availability_strategy=True)
    assert config.hedging_threshold_ms == 500


def test_build_client_config_hedging_dict_uses_threshold_ms_and_rejects_steps_rust():
    """A dict sets the threshold from threshold_ms. threshold_steps_ms is not
    supported and raises TypeError."""
    config = build_client_config(None, availability_strategy={"threshold_ms": 20})
    assert config.hedging_threshold_ms == 20
    with pytest.raises(TypeError, match="threshold_steps_ms"):
        build_client_config(
            None, availability_strategy={"threshold_ms": 20, "threshold_steps_ms": 10}
        )


def test_build_client_config_hedging_false_carries_nothing_rust():
    """availability_strategy=False gives no config, so hedging stays off."""
    assert build_client_config(None, availability_strategy=False) is None


def test_build_client_config_hedging_none_carries_nothing_rust():
    """availability_strategy=None gives no config, so hedging stays off (the default)."""
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
def test_client_keeps_hedging_setting_rust(module, extra_options, options, threshold, monkeypatch):
    """Sync and async clients keep the hedging threshold they were given.

    Leaving availability_strategy out, or setting it to None or False, leaves the
    threshold unset, which means hedging is off. preferred_locations is kept too,
    and no handle is opened.
    """
    monkeypatch.setattr(module, "CosmosClientConnection", MagicMock())
    strategy_validator = MagicMock(wraps=client_config_module.CrossRegionHedgingStrategy)
    monkeypatch.setattr(client_config_module, "CrossRegionHedgingStrategy", strategy_validator)
    client = module.CosmosClient(
        "https://hedging.invalid", "ZmFrZQ==", _backend="rust", **extra_options, **options
    )
    try:
        config = client._adapter._client_config
        assert (config.hedging_threshold_ms if config is not None else None) == threshold
        assert client._client_context.defaults.hedging_threshold_ms == threshold
        if isinstance(options.get("availability_strategy"), dict):
            strategy_validator.assert_called_once_with(options["availability_strategy"])
        assert client._adapter._driver_handle is None
        if extra_options:
            assert config.preferred_locations == ("West US",)
    finally:
        result = client._adapter.close()
        if inspect.isawaitable(result):
            asyncio.run(result)


def test_build_client_config_hedging_invalid_threshold_raises_rust():
    """A threshold_ms of zero or less raises ValueError."""
    with pytest.raises(ValueError, match="threshold_ms must be positive"):
        build_client_config(None, availability_strategy={"threshold_ms": 0})


def test_build_client_config_combines_all_settings_rust():
    """All settings can be set together in one config."""
    config = build_client_config(
        ["West US"],
        excluded_locations=["Central US"],
        throttling_max_retry_count=5,
        throttling_max_retry_wait_time_seconds=12,
        availability_strategy={"threshold_ms": 25},
        user_agent_suffix="checkout-westus2",
        consistency_level="Eventual",
        operation_timeout_seconds=2.5,
    )
    assert config == PreparedClientConfig(
        preferred_locations=("West US",),
        excluded_locations=("Central US",),
        throttling_max_retry_count=5,
        throttling_max_retry_wait_time_seconds=12,
        hedging_threshold_ms=25,
        user_agent_suffix="checkout-westus2",
        consistency_level="Eventual",
        operation_timeout_seconds=2.5,
    )


@pytest.mark.parametrize("make_config", [build_client_config, PreparedClientConfig])
@pytest.mark.parametrize("name,value", [("connection_timeout_seconds", 2), ("proxy_allowed", False)])
def test_client_config_rejects_network_settings_rust(make_config, name, value):
    """Network settings such as connection_timeout_seconds and proxy_allowed
    belong on the runtime. Passing them to the client config raises TypeError."""
    with pytest.raises(TypeError, match=name):
        make_config(**{name: value})


def test_build_client_config_carries_user_agent_suffix_rust():
    """The User-Agent suffix is stored in the config."""
    config = build_client_config(None, user_agent_suffix="checkout-westus2")
    assert isinstance(config, PreparedClientConfig)
    assert config.user_agent_suffix == "checkout-westus2"


def test_build_client_config_only_user_agent_suffix_still_builds_config_rust():
    """A suffix alone produces a config rather than None."""
    config = build_client_config(None, user_agent_suffix="order-service")
    assert config == PreparedClientConfig(user_agent_suffix="order-service")


def test_build_client_config_empty_user_agent_suffix_is_none_rust():
    """An empty or missing suffix gives no config (None)."""
    assert build_client_config(None, user_agent_suffix="") is None
    assert build_client_config(None, user_agent_suffix=None) is None


@pytest.mark.parametrize("level", ["Eventual", "ConsistentPrefix", "Session", "BoundedStaleness", "Strong"])
def test_build_client_config_carries_supported_consistency_level_rust(level):
    """Each supported consistency level is stored in the config."""
    config = build_client_config(None, consistency_level=level)
    assert config == PreparedClientConfig(consistency_level=level)


def test_build_client_config_only_consistency_still_builds_config_rust():
    """A consistency setting alone produces a config rather than None."""
    config = build_client_config(None, consistency_level="Session")
    assert isinstance(config, PreparedClientConfig)
    assert config.consistency_level == "Session"


def test_build_client_config_no_consistency_carries_nothing_rust():
    """A missing or empty consistency level gives no config (None)."""
    assert build_client_config(None, consistency_level=None) is None
    assert build_client_config(None, consistency_level="") is None


@pytest.mark.parametrize(
    "first_config, second_config",
    [
        (None, SimpleNamespace(proxy_allowed=True)),
        (SimpleNamespace(proxy_allowed=True), SimpleNamespace(proxy_allowed=False)),
        (SimpleNamespace(proxy_allowed=False), SimpleNamespace(proxy_allowed=True)),
        (SimpleNamespace(proxy_allowed=True), SimpleNamespace(proxy_allowed=True)),
        (SimpleNamespace(connection_timeout_seconds=2), SimpleNamespace(connection_timeout_seconds=5)),
    ],
)
def test_adapter_rejects_network_settings_in_client_config_rust(first_config, second_config):
    """Creating an adapter with a network setting (proxy_allowed or
    connection_timeout_seconds) in its client config raises ValueError, even
    before any request. An adapter with no config is created normally."""
    endpoint = "https://unused-clients.documents.azure.com"
    for config in (first_config, second_config):
        if config is None:
            adapter = BindingAdapter(endpoint, master_key="key")
            assert adapter._driver_handle is None
            adapter.close()
        else:
            with pytest.raises(ValueError, match="CosmosRuntime"):
                BindingAdapter(endpoint, master_key="key", client_config=config)


def test_adapter_requires_settings_check_in_compiled_module_rust(monkeypatch):
    """If the compiled module is too old to have _validate_runtime_configuration,
    creating an adapter raises RuntimeError that asks for a rebuild."""
    monkeypatch.delattr("azure.cosmos._rust._validate_runtime_configuration")
    endpoint = "https://outdated-extension.documents.azure.com"
    with pytest.raises(RuntimeError, match="_validate_runtime_configuration; rebuild"):
        BindingAdapter(endpoint, master_key="key")


def test_settings_check_error_is_raised_unchanged_rust(monkeypatch):
    """If the compiled module's settings check fails, creating the adapter raises
    that same error. The check is called once with the client config."""
    error = RuntimeError("cached runtime initialization failure")
    settings_check = MagicMock(side_effect=error)
    monkeypatch.setattr("azure.cosmos._rust._validate_runtime_configuration", settings_check)
    endpoint = "https://failed-preflight.documents.azure.com"
    config = PreparedClientConfig(operation_timeout_seconds=2)
    with pytest.raises(RuntimeError) as caught:
        BindingAdapter(endpoint, master_key="key", client_config=config)
    assert caught.value is error
    settings_check.assert_called_once_with(config)


@pytest.mark.parametrize("level", ["Nonsense", "LatestCommitted", "GlobalStrong", "Default", "eventual"])
def test_build_client_config_rejects_unknown_consistency_level_rust(level):
    """An unknown consistency level raises ValueError. Names are case-sensitive,
    so "eventual" is rejected."""
    with pytest.raises(ValueError, match="not a recognized Cosmos consistency level"):
        build_client_config(None, consistency_level=level)


@pytest.mark.parametrize("factory", [make_backend, make_async_backend])
@pytest.mark.parametrize("level", ["Eventual", "ConsistentPrefix", "Session", "BoundedStaleness", "Strong"])
def test_factories_keep_consistency_level_rust(factory, level):
    """Both factories store the consistency level in the client config without
    opening a handle."""
    adapter = factory(
        BACKEND_NAME_RUST,
        url="https://consistency.documents.azure.com",
        credential="key",
        consistency_level=level,
    )
    assert adapter._client_config.consistency_level == level
    assert adapter._driver_handle is None


def test_factory_passes_all_settings_to_adapter_rust(monkeypatch):
    """make_backend puts every supported client setting into the adapter's
    client config."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    adapter = make_backend(
        BACKEND_NAME_RUST,
        url="https://x.documents.azure.com",
        credential="k",
        excluded_locations=["Central US"],
        throttling_max_retry_count=7,
        throttling_max_retry_wait_time_seconds=20,
        availability_strategy=True,
        user_agent_suffix="checkout-westus2",
        consistency_level="Eventual",
    )
    assert isinstance(adapter, BindingAdapter)
    assert adapter._client_config == PreparedClientConfig(
        excluded_locations=("Central US",),
        throttling_max_retry_count=7,
        throttling_max_retry_wait_time_seconds=20,
        hedging_threshold_ms=500,
        user_agent_suffix="checkout-westus2",
        consistency_level="Eventual",
    )


def test_async_factory_passes_all_settings_to_adapter_rust(monkeypatch):
    """The async factory carries the same settings the same way."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    adapter = make_async_backend(
        BACKEND_NAME_RUST,
        url="https://x.documents.azure.com",
        credential="k",
        excluded_locations=["Central US", "East US"],
        availability_strategy={"threshold_ms": 15},
        user_agent_suffix="reporting-eastus",
        consistency_level="Session",
    )
    assert isinstance(adapter, AsyncBindingAdapter)
    assert adapter._client_config == PreparedClientConfig(
        excluded_locations=("Central US", "East US"),
        hedging_threshold_ms=15,
        user_agent_suffix="reporting-eastus",
        consistency_level="Session",
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("backend", [BACKEND_NAME_CORE_PYTHON, BACKEND_NAME_RUST])
async def test_client_has_no_get_database_account_rust(monkeypatch, asynchronous, backend):
    """CosmosClient has no get_database_account or _get_database_account method, and
    creating a client does not read the account."""
    module = async_cosmos_client_module if asynchronous else sync_cosmos_client_module
    connection = MagicMock()
    monkeypatch.setattr(module, "CosmosClientConnection", MagicMock(return_value=connection))
    client = module.CosmosClient(
        "https://account-surface.documents.azure.com", "key", _backend=backend,
    )
    try:
        for name in ("get_database_account", "_get_database_account"):
            assert not hasattr(module.CosmosClient, name)
            with pytest.raises(AttributeError, match=name):
                getattr(client, name)
        connection.GetDatabaseAccount.assert_not_called()
    finally:
        if asynchronous:
            await client._adapter.close()
        else:
            client._adapter.close()


# ---------------------------------------------------------------------------
# Which credentials a client accepts (resolve_credential)
# ---------------------------------------------------------------------------
#
# A client accepts an account key or a Microsoft Entra token credential. Async
# clients also accept async credentials, which they call through a small token
# helper (AsyncTokenCredentialBridge). Resource tokens are not supported and are
# rejected when the client is created.


class _SyncTokenCredential:
    """A fake sync credential."""

    def get_token(self, *scopes, **kwargs):  # noqa: D401
        """Return a fixed token that does not expire during the test."""
        return ("token-value", 9999999999)


class _AsyncTokenCredential:
    """A fake async credential: its get_token is async."""

    async def get_token(self, *scopes, **kwargs):  # noqa: D401
        """Return the same fixed token, from an async method."""
        return ("token-value", 9999999999)


class _AsyncTokenInfoCredential:
    """A fake async credential that only has get_token_info (the newer token method
    in azure-core), with no get_token."""

    async def get_token_info(self, *scopes, **kwargs):  # noqa: D401
        """Return the fixed token. With no get_token, the SDK must also look for
        get_token_info."""
        return ("token-value", 9999999999)


class _AsyncContextManagerCredential:
    """A fake credential shaped like those in azure.identity.aio: it works with
    ``async with``, and its get_token is async."""

    async def __aenter__(self):
        """Return the credential itself."""
        return self

    async def __aexit__(self, *exc):
        """Do nothing."""
        return None

    async def get_token(self, *scopes, **kwargs):  # noqa: D401
        """Return the fixed token."""
        return ("token-value", 9999999999)


def test_resolve_credential_master_key_string_rust():
    """A plain string credential is read as an account key, with no token credential."""
    assert resolve_credential("the-key") == ("the-key", None)


def test_resolve_credential_master_key_dict_rust():
    """A ``{"masterKey": ...}`` dict is read as an account key, with no token credential."""
    assert resolve_credential({"masterKey": "the-key"}) == ("the-key", None)


def test_resolve_credential_sync_token_credential_rust():
    """A sync token credential is returned as it is, with no account key."""
    credential = _SyncTokenCredential()
    master_key, token_credential = resolve_credential(credential)
    assert master_key is None
    assert token_credential is credential


def test_resolve_credential_async_token_credential_requires_async_client_rust():
    """An async credential raises TypeError for a sync client. An async client keeps
    it as it is."""
    credential = _AsyncTokenCredential()
    with pytest.raises(TypeError, match="Synchronous CosmosClient"):
        resolve_credential(credential)
    master_key, token_credential = resolve_credential(credential, allow_async=True)
    assert master_key is None
    assert token_credential is credential


def test_resolve_credential_async_get_token_info_only_credential_works_rust(credential_owner_loop):
    """A credential that only has an async get_token_info is accepted, and the token
    helper gets tokens from it."""
    credential = _AsyncTokenInfoCredential()
    master_key, kept_credential = resolve_credential(credential, allow_async=True)
    assert master_key is None
    token_credential = AsyncTokenCredentialBridge.acquire(kept_credential, loop=credential_owner_loop)
    assert isinstance(token_credential, AsyncTokenCredentialBridge)
    try:
        assert token_credential._start_token_request("https://cosmos.azure.com/.default").result(timeout=5) == (
            "token-value",
            9999999999,
        )
    finally:
        token_credential._close_cosmos_async_bridge()


def test_resolve_credential_async_context_manager_credential_is_kept_rust():
    """A credential used with ``async with`` is treated as async and kept as it is."""
    credential = _AsyncContextManagerCredential()
    master_key, token_credential = resolve_credential(credential, allow_async=True)
    assert master_key is None
    assert token_credential is credential


def test_token_helper_close_can_be_called_twice_rust(credential_owner_loop):
    """Closing a token helper twice, or before it was used, does not raise."""
    helper = AsyncTokenCredentialBridge(_AsyncTokenCredential(), loop=credential_owner_loop)
    # Close before the helper is used.
    helper._close_cosmos_async_bridge()
    helper = AsyncTokenCredentialBridge(_AsyncTokenCredential(), loop=credential_owner_loop)
    assert helper._start_token_request("scope").result(timeout=5) == ("token-value", 9999999999)
    helper._close_cosmos_async_bridge()
    helper._close_cosmos_async_bridge()  # second close is a no-op


class _SlowAsyncCredential:
    """A fake async credential whose get_token waits 10 ms, so several requests are
    still waiting when close is called."""

    async def get_token(self, *scopes, **kwargs):  # noqa: D401
        """Wait 10 ms, then return the fixed token."""
        await asyncio.sleep(0.01)
        return ("token-value", 9999999999)


def test_clients_with_same_credential_share_one_token_helper_rust(credential_owner_loop):
    """Two clients with the same credential share one token helper. It closes only when
    the last client releases it, and the event loop keeps running. A later client gets
    a new helper."""
    credential = _AsyncTokenCredential()
    acquired = []
    try:
        helper1 = AsyncTokenCredentialBridge.acquire(credential, loop=credential_owner_loop)
        acquired.append(helper1)
        helper2 = AsyncTokenCredentialBridge.acquire(credential, loop=credential_owner_loop)
        acquired.append(helper2)
        assert helper1 is helper2, "the same credential should share one token helper"
        assert helper1._refcount == 2
        assert helper1._start_token_request("scope").result(timeout=5) == ("token-value", 9999999999)
        # One use remains, so the helper can still handle token requests.
        helper1._close_cosmos_async_bridge()
        assert helper1._refcount == 1
        assert not helper1._closed
        assert helper1._start_token_request("scope").result(timeout=5) == ("token-value", 9999999999)
        # The last release closes the helper, not the customer event loop.
        helper2._close_cosmos_async_bridge()
        assert helper2._closed
        assert credential_owner_loop.is_running()
        # A later acquisition gets a new helper, not the closed one.
        helper3 = AsyncTokenCredentialBridge.acquire(credential, loop=credential_owner_loop)
        acquired.append(helper3)
        assert helper3 is not helper1
        helper3._close_cosmos_async_bridge()
    finally:
        # Release any remaining uses, even if an assertion fails.
        for helper in acquired:
            if helper._refcount:
                helper._close_cosmos_async_bridge()


def test_different_credentials_get_different_token_helpers_rust(credential_owner_loop):
    """Two different credential objects get two different token helpers."""
    credential1 = _AsyncTokenCredential()
    credential2 = _AsyncTokenCredential()
    helper1 = AsyncTokenCredentialBridge.acquire(credential1, loop=credential_owner_loop)
    helper2 = AsyncTokenCredentialBridge.acquire(credential2, loop=credential_owner_loop)
    try:
        assert helper1 is not helper2
    finally:
        helper1._close_cosmos_async_bridge()
        helper2._close_cosmos_async_bridge()


def test_token_helper_close_during_requests_does_not_hang_rust(credential_owner_loop):
    """Closing the token helper while 8 threads are asking for tokens does not hang.
    Each thread either stops normally or gets a RuntimeError or CancelledError."""
    credential = _SlowAsyncCredential()
    helper = AsyncTokenCredentialBridge(credential, loop=credential_owner_loop)
    stop = threading.Event()
    successes: list = []
    outcomes: list = []

    def worker():
        while not stop.is_set():
            try:
                helper._start_token_request("scope").result(timeout=5)
                successes.append(1)
            except Exception as exc:  # noqa: BLE001
                outcomes.append(type(exc).__name__)
                return
        outcomes.append("stopped")

    threads = [threading.Thread(target=worker, name=f"token-request-{i}") for i in range(8)]
    for thread in threads:
        thread.start()
    # Let some calls succeed and several overlap before the close.
    time.sleep(0.2)
    helper._close_cosmos_async_bridge()
    stop.set()
    for thread in threads:
        thread.join(timeout=5)
        assert not thread.is_alive(), "a thread did not stop after close"
    assert successes, "no token request completed before close"
    # Every thread stopped normally or caught an error; none hung.
    assert len(outcomes) == len(threads)
    assert set(outcomes) <= {"stopped", "RuntimeError", "CancelledError"}


def test_resolve_credential_resource_token_map_is_rejected_rust():
    """A ``{resource-link: token}`` map (resource tokens) raises ValueError saying
    resource tokens are not supported and pointing to Microsoft Entra."""
    with pytest.raises(ValueError, match="resource-token") as error:
        resolve_credential({"dbs/x/colls/y": "resource-token"})
    assert "intentionally excluded" in str(error.value)
    assert "Microsoft Entra" in str(error.value)


def test_resolve_credential_permission_list_is_rejected_rust():
    """A list of permissions (which carry resource tokens) raises the same ValueError."""
    with pytest.raises(ValueError, match="resource-token") as error:
        resolve_credential([{"id": "perm", "_token": "t", "resource": "dbs/x"}])
    assert "intentionally excluded" in str(error.value)


def test_factory_passes_sync_token_credential_to_adapter_rust(monkeypatch):
    """make_backend gives the adapter the sync token credential and no account key."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    credential = _SyncTokenCredential()
    adapter = make_backend(
        BACKEND_NAME_RUST,
        url="https://x.documents.azure.com",
        credential=credential,
    )
    assert isinstance(adapter, BindingAdapter)
    assert adapter._master_key is None
    assert adapter._token_credential is credential


def test_async_factory_passes_sync_token_credential_to_adapter_rust(monkeypatch):
    """The async factory carries a sync token credential the same way."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    credential = _SyncTokenCredential()
    adapter = make_async_backend(
        BACKEND_NAME_RUST,
        url="https://x.documents.azure.com",
        credential=credential,
    )
    assert isinstance(adapter, AsyncBindingAdapter)
    assert adapter._master_key is None
    assert adapter._token_credential is credential


def test_factory_rejects_async_token_credential_rust(monkeypatch):
    """make_backend (used by the sync client) raises TypeError for an async credential."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    credential = _AsyncTokenCredential()
    with pytest.raises(TypeError, match="Synchronous CosmosClient"):
        make_backend(
            BACKEND_NAME_RUST,
            url="https://x.documents.azure.com",
            credential=credential,
        )


def test_async_factory_keeps_async_credential_rust(monkeypatch):
    """make_async_backend keeps an async credential as it is, even when no event loop
    is running yet."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    credential = _AsyncTokenCredential()
    adapter = make_async_backend(
        BACKEND_NAME_RUST,
        url="https://x.documents.azure.com",
        credential=credential,
    )
    assert isinstance(adapter, AsyncBindingAdapter)
    assert adapter._master_key is None
    assert adapter._token_credential is credential


def test_token_credential_is_sent_when_handle_opens_rust(monkeypatch):
    """With a token credential, the adapter opens the handle with the endpoint, no
    account key, no client config and the credential."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    monkeypatch.setattr("azure.cosmos._backend.binding_adapter._rust_module", fake_module)

    credential = _SyncTokenCredential()
    adapter = BindingAdapter(
        endpoint="https://x.documents.azure.com",
        token_credential=credential,
    )
    adapter._ensure_driver_handle()

    fake_module.acquire_driver_handle.assert_called_once_with(
        "https://x.documents.azure.com", None, None, credential
    )


def test_async_token_credential_is_sent_when_handle_opens_rust(monkeypatch):
    """The async adapter sends the token credential the same way."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    monkeypatch.setattr("azure.cosmos.aio._backend.binding_adapter._rust_module", fake_module)

    credential = _SyncTokenCredential()

    async def _run():
        adapter = AsyncBindingAdapter(
            endpoint="https://x.documents.azure.com",
            token_credential=credential,
        )
        await adapter._ensure_driver_handle()

    asyncio.run(_run())

    fake_module.acquire_driver_handle.assert_called_once_with(
        "https://x.documents.azure.com", None, None, credential
    )


# ---------------------------------------------------------------------------
# How a container call reaches the adapter
# ---------------------------------------------------------------------------
#
# The client gives each container a client context that holds the adapter. A
# container call sends its request through that adapter.

def _make_container_with_adapter(adapter):
    """Build a ContainerProxy that uses the given adapter and a fake connection."""
    fake_connection = MagicMock()
    fake_connection._backend = adapter
    from azure.cosmos._helpers._client_context import CosmosClientContext
    return ContainerProxy(fake_connection, "dbs/test", "test", _client_context=CosmosClientContext(adapter))


def _new_adapter():
    """Build an adapter with a test endpoint and key. The tests fake the compiled
    module, so no request is sent over the network."""
    return BindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")


def _new_async_adapter():
    """Build an async adapter with a test endpoint and key."""
    return AsyncBindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")


def test_container_call_reaches_compiled_module_rust(monkeypatch):
    """create_item on a container sends the request to the compiled module."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "h"
    fake_module.create_item.return_value = (201, 0, {}, b"{}")
    fake_module.get_container_metadata.return_value = ("rid", (), None, None)
    monkeypatch.setattr("azure.cosmos._backend.binding_adapter._rust_module", fake_module)

    container = _make_container_with_adapter(_new_adapter())
    try:
        container.create_item(body={"id": "x", "pk": "a"})
        assert fake_module.create_item.called, "create_item did not reach the compiled module"
    finally:
        container._client_context.adapter.close()


def test_container_without_client_context_raises_rust():
    """A ContainerProxy built directly, without a CosmosClient, raises RuntimeError when it
    is used."""
    fake_connection = MagicMock(spec=[])  # a connection with no adapter
    container = ContainerProxy(fake_connection, "dbs/test", "test")
    with pytest.raises(RuntimeError, match="context supplied by CosmosClient"):
        container.create_item(body={"id": "x", "pk": "a"})


def test_async_container_call_reaches_compiled_module_rust(monkeypatch):
    """The async version of test_container_call_reaches_compiled_module_rust."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "h"
    fake_module.create_item_async = AsyncMock(return_value=(201, 0, {}, b"{}"))
    fake_module.get_container_metadata_async = AsyncMock(return_value=("rid", (), None, None))
    monkeypatch.setattr("azure.cosmos.aio._backend.binding_adapter._rust_module", fake_module)

    fake_connection = MagicMock()
    fake_connection._backend = _new_async_adapter()
    try:
        from azure.cosmos._helpers._client_context import CosmosClientContext
        container = AsyncContainerProxy(
            fake_connection, "dbs/test", "test", _client_context=CosmosClientContext(fake_connection._backend)
        )

        async def _run():
            await container.create_item(body={"id": "x", "pk": "a"})
            assert fake_module.create_item_async.called, "create_item did not reach the compiled module"

        asyncio.run(_run())
    finally:
        asyncio.run(fake_connection._backend.close())


# read_feed_ranges and feed_range_from_partition_key, called on the container.
# read_feed_ranges supports only the timeout option; any other option raises
# NotImplementedError.
def test_container_read_feed_ranges_sends_request_rust(monkeypatch):
    """read_feed_ranges(force_refresh=True) sends one request to the compiled module and
    does not look up ranges in the client connection."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "h"
    fake_module.read_feed_ranges.return_value = (
        200,
        0,
        {},
        b'{"PartitionKeyRanges":[{"id":"0","minInclusive":"","maxExclusive":"FF"}]}',
    )
    monkeypatch.setattr("azure.cosmos._backend.binding_adapter._rust_module", fake_module)

    container = _make_container_with_adapter(_new_adapter())
    try:
        container.client_connection._routing_map_provider = MagicMock()

        feed_ranges = list(container.read_feed_ranges(force_refresh=True))
        assert len(feed_ranges) == 1
        assert fake_module.read_feed_ranges.called
        assert not container.client_connection.refresh_routing_map_provider.called
        assert not container.client_connection._routing_map_provider.get_overlapping_ranges.called

        sent_request = fake_module.read_feed_ranges.call_args.args[1]
        assert sent_request.op == OP_READ_FEED_RANGES
        assert sent_request.container_link == "dbs/test/colls/test"
        assert sent_request.body_bytes == b'{"forceRefresh":true}'
    finally:
        container._client_context.adapter.close()


def test_container_read_feed_ranges_with_unsupported_option_raises_rust(monkeypatch):
    """read_feed_ranges with an option other than timeout (here excluded_locations) raises
    NotImplementedError and sends no request."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "h"
    fake_module.read_feed_ranges.return_value = (
        200,
        0,
        {},
        b'{"PartitionKeyRanges":[{"id":"0","minInclusive":"","maxExclusive":"FF"}]}',
    )
    monkeypatch.setattr("azure.cosmos._backend.binding_adapter._rust_module", fake_module)

    container = _make_container_with_adapter(_new_adapter())
    try:
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

        with pytest.raises(NotImplementedError, match="read_feed_ranges"):
            list(container.read_feed_ranges(force_refresh=True, excluded_locations=["West US"]))
        assert not fake_module.read_feed_ranges.called
        container._get_properties_with_options.assert_not_called()
        container.client_connection.refresh_routing_map_provider.assert_not_called()
        container.client_connection._routing_map_provider.get_overlapping_ranges.assert_not_called()
    finally:
        container._client_context.adapter.close()


def test_container_read_feed_ranges_reply_without_ranges_raises_rust(monkeypatch):
    """A reply without a PartitionKeyRanges field raises ValueError instead of returning an
    empty list."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "h"
    fake_module.read_feed_ranges.return_value = (200, 0, {}, b'{"unexpected":[]}')
    monkeypatch.setattr("azure.cosmos._backend.binding_adapter._rust_module", fake_module)

    container = _make_container_with_adapter(_new_adapter())
    try:
        with pytest.raises(ValueError, match="PartitionKeyRanges"):
            list(container.read_feed_ranges())
    finally:
        container._client_context.adapter.close()


def test_async_container_read_feed_ranges_sends_request_rust(monkeypatch):
    """The async version of test_container_read_feed_ranges_sends_request_rust."""
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
    monkeypatch.setattr("azure.cosmos.aio._backend.binding_adapter._rust_module", fake_module)

    fake_connection = MagicMock()
    fake_connection._backend = _new_async_adapter()
    try:
        fake_connection._routing_map_provider = MagicMock()
        fake_connection.refresh_routing_map_provider = AsyncMock()
        container = AsyncContainerProxy.__new__(AsyncContainerProxy)
        container.client_connection = fake_connection
        container.id = "test"
        container.database_link = "dbs/test"
        container.container_link = "dbs/test/colls/test"

        async def _run():
            return [feed_range async for feed_range in container.read_feed_ranges(force_refresh=True)]

        feed_ranges = asyncio.run(_run())
        assert len(feed_ranges) == 1
        assert fake_module.read_feed_ranges_async.await_count == 1
        fake_connection.refresh_routing_map_provider.assert_not_awaited()
        assert not fake_connection._routing_map_provider.get_overlapping_ranges.called

        sent_request = fake_module.read_feed_ranges_async.await_args.args[1]
        assert sent_request.op == OP_READ_FEED_RANGES
        assert sent_request.container_link == "dbs/test/colls/test"
        assert sent_request.body_bytes == b'{"forceRefresh":true}'
    finally:
        asyncio.run(fake_connection._backend.close())


def test_async_container_read_feed_ranges_with_unsupported_option_raises_rust(monkeypatch):
    """The async version of test_container_read_feed_ranges_with_unsupported_option_raises_rust."""
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
    monkeypatch.setattr("azure.cosmos.aio._backend.binding_adapter._rust_module", fake_module)

    fake_connection = MagicMock()
    fake_connection._backend = _new_async_adapter()
    try:
        fake_connection._routing_map_provider = MagicMock()
        fake_connection._routing_map_provider.get_overlapping_ranges = AsyncMock(
            return_value=[{"id": "0", "minInclusive": "", "maxExclusive": "FF"}]
        )
        fake_connection.refresh_routing_map_provider = AsyncMock()
        container = AsyncContainerProxy.__new__(AsyncContainerProxy)
        container.client_connection = fake_connection
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

        with pytest.raises(NotImplementedError, match="read_feed_ranges"):
            asyncio.run(_run())
        assert fake_module.read_feed_ranges_async.await_count == 0
        container._get_properties_with_options.assert_not_called()
        fake_connection.refresh_routing_map_provider.assert_not_awaited()
        fake_connection._routing_map_provider.get_overlapping_ranges.assert_not_awaited()
    finally:
        asyncio.run(fake_connection._backend.close())


def test_async_container_read_feed_ranges_reply_without_ranges_raises_rust(monkeypatch):
    """The async version of test_container_read_feed_ranges_reply_without_ranges_raises_rust."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "h"
    fake_module.read_feed_ranges_async = AsyncMock(return_value=(200, 0, {}, b'{"unexpected":[]}'))
    monkeypatch.setattr("azure.cosmos.aio._backend.binding_adapter._rust_module", fake_module)

    fake_connection = MagicMock()
    fake_connection._backend = _new_async_adapter()
    try:
        container = AsyncContainerProxy.__new__(AsyncContainerProxy)
        container.client_connection = fake_connection
        container.id = "test"
        container.database_link = "dbs/test"
        container.container_link = "dbs/test/colls/test"

        async def _run():
            return [feed_range async for feed_range in container.read_feed_ranges()]

        with pytest.raises(ValueError, match="PartitionKeyRanges"):
            asyncio.run(_run())
    finally:
        asyncio.run(fake_connection._backend.close())


def test_container_feed_range_from_partition_key_sends_request_rust(monkeypatch):
    """feed_range_from_partition_key sends the partition key to the compiled module and
    returns the range from its reply."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "h"
    fake_module.feed_range_from_partition_key.return_value = (
        200,
        0,
        {},
        b'{"Range":{"min":"3C","max":"3C","isMinInclusive":true,"isMaxInclusive":true}}',
    )
    monkeypatch.setattr("azure.cosmos._backend.binding_adapter._rust_module", fake_module)

    container = _make_container_with_adapter(_new_adapter())
    try:
        container._get_properties = MagicMock(side_effect=AssertionError("container properties should not be read"))

        feed_range = container.feed_range_from_partition_key("pk-a")
        assert feed_range["Range"]["min"] == "3C"
        assert feed_range["Range"]["isMaxInclusive"] is True
        assert fake_module.feed_range_from_partition_key.called

        sent_request = fake_module.feed_range_from_partition_key.call_args.args[1]
        assert sent_request.op == OP_FEED_RANGE_FROM_PARTITION_KEY
        assert sent_request.container_link == "dbs/test/colls/test"
        assert legacy_partition_key_from_request(sent_request) == '["pk-a"]'
        assert sent_request.body_bytes == b""
    finally:
        container._client_context.adapter.close()


def test_container_feed_range_from_partition_key_reply_without_range_raises_rust(monkeypatch):
    """A reply without a Range field raises ValueError instead of returning a broken feed
    range."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "h"
    fake_module.feed_range_from_partition_key.return_value = (200, 0, {}, b'{"unexpected":{}}')
    monkeypatch.setattr("azure.cosmos._backend.binding_adapter._rust_module", fake_module)

    container = _make_container_with_adapter(_new_adapter())
    try:
        with pytest.raises(ValueError, match="Range"):
            container.feed_range_from_partition_key("pk-a")
    finally:
        container._client_context.adapter.close()


def test_container_feed_range_from_none_partition_key_value_rust(monkeypatch):
    """NonePartitionKeyValue (no partition key value) is sent as ``"[]"``, and the range
    from the reply is returned."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "h"
    fake_module.feed_range_from_partition_key.return_value = (
        200,
        0,
        {},
        b'{"Range":{"min":"00000000000000000000000000000000","max":"00000000000000000000000000000000","isMinInclusive":true,"isMaxInclusive":true}}',
    )
    monkeypatch.setattr("azure.cosmos._backend.binding_adapter._rust_module", fake_module)

    container = _make_container_with_adapter(_new_adapter())
    try:
        container._get_properties = MagicMock(
            return_value={"partitionKey": {"paths": ["/pk"], "kind": "Hash", "version": 2, "systemKey": True}}
        )

        feed_range = container.feed_range_from_partition_key(NonePartitionKeyValue)

        assert feed_range["Range"]["min"] == "00000000000000000000000000000000"
        assert feed_range["Range"]["max"] == "00000000000000000000000000000000"
        assert feed_range["Range"]["isMinInclusive"] is True
        assert feed_range["Range"]["isMaxInclusive"] is True
        assert fake_module.feed_range_from_partition_key.call_count == 1
        sent_request = fake_module.feed_range_from_partition_key.call_args.args[1]
        assert legacy_partition_key_from_request(sent_request) == "[]"
    finally:
        container._client_context.adapter.close()


def test_container_feed_range_from_empty_list_partition_key_rust(monkeypatch):
    """An empty list ``[]`` as the partition key is sent as ``"[[]]"``, and the range from
    the reply is returned."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "h"
    fake_module.feed_range_from_partition_key.return_value = (
        200,
        0,
        {},
        b'{"Range":{"min":"","max":"","isMinInclusive":true,"isMaxInclusive":false}}',
    )
    monkeypatch.setattr("azure.cosmos._backend.binding_adapter._rust_module", fake_module)

    container = _make_container_with_adapter(_new_adapter())
    try:
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
        sent_request = fake_module.feed_range_from_partition_key.call_args.args[1]
        assert legacy_partition_key_from_request(sent_request) == "[[]]"
    finally:
        container._client_context.adapter.close()


def test_async_container_feed_range_from_partition_key_sends_request_rust(monkeypatch):
    """The async version of test_container_feed_range_from_partition_key_sends_request_rust."""
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
    monkeypatch.setattr("azure.cosmos.aio._backend.binding_adapter._rust_module", fake_module)

    fake_connection = MagicMock()
    fake_connection._backend = _new_async_adapter()
    try:
        container = AsyncContainerProxy.__new__(AsyncContainerProxy)
        container.client_connection = fake_connection
        container.id = "test"
        container.database_link = "dbs/test"
        container.container_link = "dbs/test/colls/test"

        async def _run():
            return await container.feed_range_from_partition_key("pk-a")

        feed_range = asyncio.run(_run())
        assert feed_range["Range"]["min"] == "3C"
        assert feed_range["Range"]["isMaxInclusive"] is True
        assert fake_module.feed_range_from_partition_key_async.await_count == 1

        sent_request = fake_module.feed_range_from_partition_key_async.await_args.args[1]
        assert sent_request.op == OP_FEED_RANGE_FROM_PARTITION_KEY
        assert sent_request.container_link == "dbs/test/colls/test"
        assert legacy_partition_key_from_request(sent_request) == '["pk-a"]'
        assert sent_request.body_bytes == b""
    finally:
        asyncio.run(fake_connection._backend.close())


def test_async_container_feed_range_from_partition_key_reply_without_range_raises_rust(monkeypatch):
    """The async version of test_container_feed_range_from_partition_key_reply_without_range_raises_rust."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "h"
    fake_module.feed_range_from_partition_key_async = AsyncMock(
        return_value=(200, 0, {}, b'{"unexpected":{}}')
    )
    monkeypatch.setattr("azure.cosmos.aio._backend.binding_adapter._rust_module", fake_module)

    fake_connection = MagicMock()
    fake_connection._backend = _new_async_adapter()
    try:
        container = AsyncContainerProxy.__new__(AsyncContainerProxy)
        container.client_connection = fake_connection
        container.id = "test"
        container.database_link = "dbs/test"
        container.container_link = "dbs/test/colls/test"

        async def _run():
            return await container.feed_range_from_partition_key("pk-a")

        with pytest.raises(ValueError, match="Range"):
            asyncio.run(_run())
    finally:
        asyncio.run(fake_connection._backend.close())


def test_async_container_feed_range_from_none_partition_key_value_rust(monkeypatch):
    """The async version of test_container_feed_range_from_none_partition_key_value_rust."""
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
    monkeypatch.setattr("azure.cosmos.aio._backend.binding_adapter._rust_module", fake_module)

    fake_connection = MagicMock()
    fake_connection._backend = _new_async_adapter()
    try:
        container = AsyncContainerProxy.__new__(AsyncContainerProxy)
        container.client_connection = fake_connection
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
        sent_request = fake_module.feed_range_from_partition_key_async.await_args.args[1]
        assert legacy_partition_key_from_request(sent_request) == "[]"
    finally:
        asyncio.run(fake_connection._backend.close())


def test_async_container_feed_range_from_empty_list_partition_key_rust(monkeypatch):
    """The async version of test_container_feed_range_from_empty_list_partition_key_rust."""
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
    monkeypatch.setattr("azure.cosmos.aio._backend.binding_adapter._rust_module", fake_module)

    fake_connection = MagicMock()
    fake_connection._backend = _new_async_adapter()
    try:
        container = AsyncContainerProxy.__new__(AsyncContainerProxy)
        container.client_connection = fake_connection
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
        sent_request = fake_module.feed_range_from_partition_key_async.await_args.args[1]
        assert legacy_partition_key_from_request(sent_request) == "[[]]"
    finally:
        asyncio.run(fake_connection._backend.close())


# ---------------------------------------------------------------------------
# Reading the adapter from the connection (get_selected_backend)
# ---------------------------------------------------------------------------
#
# Some SDK code reads the adapter from the connection's ``_backend`` attribute.
# get_selected_backend looks in the connection's ``__dict__`` (the attributes
# actually set on it) first, and uses getattr for connections without one.
# A connection with no adapter raises RuntimeError.


class _PlainConnection:
    """A fake connection that keeps its attributes in ``__dict__``, like a normal object."""


class _SlotsConnection:
    """A fake connection that keeps its attributes in ``__slots__``, so it has no
    ``__dict__``."""

    __slots__ = ("_backend",)


def test_get_selected_backend_returns_adapter_rust():
    """get_selected_backend returns the adapter stored as ``_backend`` on the connection."""
    connection = _PlainConnection()
    adapter = object()
    connection._backend = adapter
    assert get_selected_backend(connection) is adapter


def test_get_selected_backend_without_adapter_raises_rust():
    """A connection with no ``_backend`` raises RuntimeError."""
    with pytest.raises(RuntimeError, match="concrete Cosmos backend"):
        get_selected_backend(_PlainConnection())


def test_get_selected_backend_reads_slots_connection_rust():
    """A connection with no ``__dict__`` (it uses ``__slots__``) is read with getattr."""
    connection = _SlotsConnection()
    adapter = object()
    connection._backend = adapter
    assert get_selected_backend(connection) is adapter


# ---------------------------------------------------------------------------
# The handle opens only once
# ---------------------------------------------------------------------------
#
# The first request opens the handle. Requests that arrive while it is opening
# wait for that same open. If the open fails, they all get the same error, and
# a later request tries again.


@pytest.mark.parametrize("first_attempt_fails", [False, True], ids=["reuse", "retry-after-failure"])
def test_concurrent_first_requests_open_one_handle_rust(monkeypatch, first_attempt_fails):
    """Two threads that need the handle at the same time share one open. If the open
    fails, both get the same error, and the next request opens the handle again."""
    first_started = threading.Event()
    finish_first = threading.Event()
    second_waiting = threading.Event()
    first_error = RuntimeError("first open failed")
    fake_module = MagicMock()
    fake_module._DriverResponseError = type("_DriverResponseError", (RuntimeError,), {})
    fake_module._DriverTransportError = type("_DriverTransportError", (RuntimeError,), {})
    monkeypatch.setattr("azure.cosmos._backend.binding_adapter._rust_module", fake_module)
    adapter = BindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
    wait_lock = threading.Lock()
    waiters = []

    def observed_wait(futures, timeout=None):
        with wait_lock:
            waiters.append(tuple(futures))
            if len(waiters) == 2:
                second_waiting.set()
        return concurrent.futures.wait(futures, timeout=timeout)

    monkeypatch.setattr("azure.cosmos._backend.binding_adapter.wait", observed_wait)

    def fake_open_handle(_endpoint, _key, _config):
        assert adapter._driver_handle is None
        if fake_module.acquire_driver_handle.call_count == 1:
            first_started.set()
            assert finish_first.wait(5), "the first open was not allowed to finish"
            if first_attempt_fails:
                raise first_error
        return "handle-1"

    fake_module.acquire_driver_handle.side_effect = fake_open_handle
    results = [concurrent.futures.Future(), concurrent.futures.Future()]

    def get_handle_in_thread(result):
        try:
            result.set_result(adapter._ensure_driver_handle())
        except BaseException as error:
            result.set_exception(error)

    threads = [threading.Thread(target=get_handle_in_thread, args=(result,), daemon=True) for result in results]
    started_threads = []
    try:
        threads[0].start()
        started_threads.append(threads[0])
        assert first_started.wait(5), "the first caller did not start opening the handle"
        threads[1].start()
        started_threads.append(threads[1])
        assert second_waiting.wait(5), "the second caller did not wait for the first open"
        assert waiters[0] == waiters[1]
        assert adapter._driver_handle is None
        assert not results[0].done()
        assert not results[1].done()
        fake_module.acquire_driver_handle.assert_called_once()

        finish_first.set()
        if first_attempt_fails:
            for result in results:
                with pytest.raises(RuntimeError) as caught:
                    result.result(timeout=5)
                assert caught.value is first_error
            assert adapter._driver_handle is None
            assert adapter._ensure_driver_handle() == "handle-1"
        else:
            assert results[0].result(timeout=5) == "handle-1"
            assert results[1].result(timeout=5) == "handle-1"
        assert adapter._driver_handle == "handle-1"
        assert adapter._ensure_driver_handle() == "handle-1"
        assert fake_module.acquire_driver_handle.call_count == (2 if first_attempt_fails else 1)
    finally:
        finish_first.set()
        for thread in started_threads:
            thread.join(timeout=5)
        assert all(not thread.is_alive() for thread in started_threads), "a thread did not finish"
        adapter.close()
    fake_module.release_driver_handle.assert_called_once_with("handle-1")


def test_async_requests_from_two_event_loops_open_one_handle_rust(monkeypatch):
    """Two threads, each running its own event loop, open the handle only once."""
    count_lock = threading.Lock()
    open_count = {"n": 0}

    def fake_slow_open_handle(_endpoint, _key, _config):
        with count_lock:
            open_count["n"] += 1
        time.sleep(0.02)
        return "handle-1"

    fake_module = MagicMock()
    fake_module.acquire_driver_handle.side_effect = fake_slow_open_handle
    monkeypatch.setattr("azure.cosmos.aio._backend.binding_adapter._rust_module", fake_module)

    adapter = AsyncBindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
    ready = threading.Barrier(2)
    results = []

    def get_handle_in_thread():
        ready.wait()

        async def _run():
            return await adapter._ensure_driver_handle()

        results.append(asyncio.run(_run()))

    threads = [threading.Thread(target=get_handle_in_thread) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert open_count["n"] == 1
    assert results == ["handle-1", "handle-1"]


def test_async_close_twice_releases_handle_once_rust(monkeypatch):
    """Calling close twice on the async adapter releases the handle only once."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    monkeypatch.setattr("azure.cosmos.aio._backend.binding_adapter._rust_module", fake_module)

    async def _run():
        adapter = AsyncBindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
        await adapter._ensure_driver_handle()
        await adapter.close()
        await adapter.close()

    asyncio.run(_run())

    fake_module.release_driver_handle.assert_called_once_with("handle-1")


# ---------------------------------------------------------------------------
# Bad client inputs raise a clear ValueError when the client is created.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("bad", [123, 1.5, True, ["rust"], {"name": "rust"}, object()])
def test_resolve_backend_name_non_string_raises_valueerror_rust(monkeypatch, bad):
    """A non-string _backend= must raise a clear ValueError, not an opaque
    AttributeError from calling .strip() on a non-string."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    with pytest.raises(ValueError, match="Invalid backend"):
        resolve_backend_name(bad)


@pytest.mark.parametrize("arg_name", ["preferred_locations", "excluded_locations"])
def test_client_config_rejects_single_string_region_rust(arg_name):
    """A single string such as ``"West US"`` for preferred_locations or excluded_locations
    raises ValueError. Without this check, the string would be split into one region per
    letter."""
    with pytest.raises(ValueError, match=r"list of region names, such as \['West US'\], not a single string"):
        build_client_config(**{arg_name: "West US"})


@pytest.mark.parametrize("arg_name", ["preferred_locations", "excluded_locations"])
def test_client_config_rejects_bytes_region_rust(arg_name):
    """Bytes such as ``b"West US"`` are rejected the same way."""
    with pytest.raises(ValueError, match=r"list of region names, such as \['West US'\], not a single string"):
        build_client_config(**{arg_name: b"West US"})


def test_client_config_accepts_one_region_in_a_list_rust():
    """A list with one region, such as ``["West US"]``, is accepted."""
    config = build_client_config(["West US"])
    assert config == PreparedClientConfig(preferred_locations=("West US",))


@pytest.mark.parametrize("bad_master_key", [None, 123, b"key", {"k": "v"}, "", "   "])
def test_resolve_credential_rejects_bad_master_key_in_dict_rust(bad_master_key):
    """A ``{"masterKey": ...}`` dict whose key is empty, blank or not a string raises
    ValueError."""
    with pytest.raises(ValueError, match="'masterKey' entry to be a non-empty string"):
        resolve_credential({"masterKey": bad_master_key})


@pytest.mark.parametrize("blank_key", ["", "   ", "\n"])
def test_resolve_credential_rejects_blank_account_key_rust(blank_key):
    """An empty or blank account key string raises ValueError."""
    with pytest.raises(ValueError, match=r"^The account key must be a non-empty string\.$"):
        resolve_credential(blank_key)


def test_resolve_credential_generator_gets_general_error_rust():
    """An object that can be looped over but is not a list (here a generator) is not
    treated as a list of permissions. It gets the general "unsupported credential"
    ValueError."""
    def _generator():
        yield {"id": "perm"}

    with pytest.raises(ValueError, match="requires a master-key credential"):
        resolve_credential(_generator())


def test_resolve_backend_name_normalizes_case_and_whitespace_rust(monkeypatch):
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


def test_resolve_backend_name_empty_means_default_rust(monkeypatch):
    """An empty or whitespace-only value counts as 'not specified' and uses the
    default rather than raising."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    assert resolve_backend_name(None) == BACKEND_NAME_RUST
    assert resolve_backend_name("") == BACKEND_NAME_RUST
    assert resolve_backend_name("   ") == BACKEND_NAME_RUST
    monkeypatch.setenv(BACKEND_ENV_VAR, "")
    assert resolve_backend_name(None) == BACKEND_NAME_RUST
    monkeypatch.setenv(BACKEND_ENV_VAR, "   ")
    assert resolve_backend_name(None) == BACKEND_NAME_RUST


def test_resolve_backend_name_still_rejects_genuine_typos_rust(monkeypatch):
    """Normalization is only case/whitespace -- a real typo (and underscore
    spelling, which is not an alias) still fails loud."""
    monkeypatch.delenv(BACKEND_ENV_VAR, raising=False)
    for bad in ("turbo", "rustt", "core_python", "python"):  # cspell:disable-line
        with pytest.raises(ValueError, match="Invalid backend"):
            resolve_backend_name(bad)


# ---------------------------------------------------------------------------
# Network failures raise ServiceResponseError
# ---------------------------------------------------------------------------
#
# When a request gets no HTTP reply (for example, the connection drops), the
# compiled module raises _DriverTransportError. The adapter raises azure-core's
# ServiceResponseError instead, with the same message, so customer code can catch
# it like other azure-core network errors. The request may still have reached
# the service.


def _network_failure_test_request():
    """Return a read_item request for the network-failure tests."""
    return PreparedRequest(
        op="read_item",
        container_link="dbs/d/colls/c",
        body_bytes=b"",
        partition_key=key_from_legacy_header('["a"]'),
        headers={},
    )


class _FakeDriverTransportError(RuntimeError):
    """A fake of the compiled module's network-failure error."""
    pass


def test_network_failure_raises_service_response_error_rust(monkeypatch):
    """A network failure from the compiled module raises ServiceResponseError with the same
    message, and keeps the original error as its cause."""
    from azure.core.exceptions import ServiceResponseError
    import azure.cosmos._backend.binding_adapter as adapter_module

    adapter = BindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
    adapter._driver_handle = "handle"  # pretend the handle is already open
    monkeypatch.setattr(adapter_module, "_rust_module", object())  # pretend the compiled module is installed
    monkeypatch.setattr(
        adapter_module, "_DRIVER_TRANSPORT_ERROR", _FakeDriverTransportError
    )

    network_error_type = adapter_module._DRIVER_TRANSPORT_ERROR
    message = "Request failed: status 503 (ServiceUnavailable): boom"

    def fail_with_network_error(driver_handle, prepared):
        raise network_error_type(message)

    monkeypatch.setattr(adapter_module, "_binding_function_for_op", lambda op: fail_with_network_error)

    try:
        with pytest.raises(ServiceResponseError) as raised:
            adapter.execute(_network_failure_test_request())
        assert str(raised.value) == message
        assert isinstance(raised.value.__cause__, network_error_type)
    finally:
        adapter.close()


def test_async_network_failure_raises_service_response_error_rust(monkeypatch):
    """The async version of the test above."""
    from azure.core.exceptions import ServiceResponseError
    import azure.cosmos.aio._backend.binding_adapter as async_adapter_module

    adapter = AsyncBindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
    adapter._driver_handle = "handle"  # pretend the handle is already open
    monkeypatch.setattr(async_adapter_module, "_rust_module", object())
    monkeypatch.setattr(
        async_adapter_module, "_DRIVER_TRANSPORT_ERROR", _FakeDriverTransportError
    )

    network_error_type = async_adapter_module._DRIVER_TRANSPORT_ERROR
    message = "Request failed: status 503 (ServiceUnavailable): boom"

    async def fail_with_network_error(driver_handle, prepared):
        raise network_error_type(message)

    monkeypatch.setattr(async_adapter_module, "_binding_function_for_op", lambda op: fail_with_network_error)

    async def run():
        try:
            with pytest.raises(ServiceResponseError) as raised:
                await adapter.execute(_network_failure_test_request())
            assert str(raised.value) == message
            assert isinstance(raised.value.__cause__, network_error_type)
        finally:
            await adapter.close()

    asyncio.run(run())


def test_list_databases_network_failure_raises_service_response_error_rust(monkeypatch):
    """A network failure while listing databases also raises ServiceResponseError, and the
    fallback function passed in is not called."""
    from azure.core.exceptions import ServiceResponseError
    import azure.cosmos._backend.binding_adapter as adapter_module

    adapter = BindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
    adapter._driver_handle = "handle"
    monkeypatch.setattr(adapter_module, "_rust_module", object())
    monkeypatch.setattr(
        adapter_module, "_DRIVER_TRANSPORT_ERROR", _FakeDriverTransportError
    )
    network_error_type = adapter_module._DRIVER_TRANSPORT_ERROR

    def fail_with_network_error(_driver_handle, _prepared):
        raise network_error_type("Listing databases failed: transport closed")

    monkeypatch.setattr(adapter_module, "_binding_function_by_name", lambda _op: fail_with_network_error)
    fallback_calls = []

    try:
        with pytest.raises(ServiceResponseError):
            adapter.run_page_operation(
                build_request=lambda: PreparedPageRequest(
                    op=OP_LIST_DATABASES, container_link="", headers={}
                ),
                routing=OperationRouting(OP_LIST_DATABASES, True),
                legacy_call=lambda: fallback_calls.append("called"),
                process_response=lambda page: page,
            )
        assert fallback_calls == []
    finally:
        adapter.close()


def test_async_list_databases_network_failure_raises_service_response_error_rust(monkeypatch):
    """The async version of the test above."""
    from azure.core.exceptions import ServiceResponseError
    import azure.cosmos.aio._backend.binding_adapter as async_adapter_module

    adapter = AsyncBindingAdapter(endpoint="https://x.documents.azure.com", master_key="k")
    adapter._driver_handle = "handle"
    monkeypatch.setattr(async_adapter_module, "_rust_module", object())
    monkeypatch.setattr(
        async_adapter_module, "_DRIVER_TRANSPORT_ERROR", _FakeDriverTransportError
    )
    network_error_type = async_adapter_module._DRIVER_TRANSPORT_ERROR

    async def fail_with_network_error(_driver_handle, _prepared):
        raise network_error_type("Listing databases failed: transport closed")

    monkeypatch.setattr(async_adapter_module, "_binding_function_by_name", lambda _op: fail_with_network_error)
    fallback_calls = []

    async def run():
        def build_request():
            return PreparedPageRequest(op=OP_LIST_DATABASES, container_link="", headers={})

        try:
            with pytest.raises(ServiceResponseError):
                await adapter.run_page_operation(
                    build_request=build_request,
                    routing=OperationRouting(OP_LIST_DATABASES, True),
                    legacy_call=lambda: fallback_calls.append("called"),
                    process_response=lambda page: page,
                )
            assert fallback_calls == []
        finally:
            await adapter.close()

    asyncio.run(run())


# --- Closing the client, and cleanup when client creation fails ---


def _make_closed_adapter(monkeypatch, endpoint):
    """Build an adapter with a fake compiled module, open its handle, then close it."""
    fake_module = MagicMock()
    fake_module.acquire_driver_handle.return_value = "handle-1"
    monkeypatch.setattr("azure.cosmos._backend.binding_adapter._rust_module", fake_module)
    adapter = BindingAdapter(
        endpoint=endpoint,
        master_key="key",
        token_credential=None,
        client_config=None,
    )
    assert adapter._ensure_driver_handle() == "handle-1"
    adapter.close()
    return adapter, fake_module


def test_closed_client_does_not_reopen_handle_rust(monkeypatch):
    """After close, the adapter raises RuntimeError instead of opening a new handle, so a
    closed client cannot keep sending requests."""
    adapter, fake_module = _make_closed_adapter(
        monkeypatch, "https://reopen.documents.azure.com"
    )
    with pytest.raises(RuntimeError, match="closed"):
        adapter._ensure_driver_handle()
    assert fake_module.acquire_driver_handle.call_count == 1


def test_close_twice_releases_handle_once_rust(monkeypatch):
    """Calling close twice releases the handle only once."""
    adapter, fake_module = _make_closed_adapter(
        monkeypatch, "https://double-close.documents.azure.com"
    )
    adapter.close()
    adapter.close()
    assert fake_module.release_driver_handle.call_count == 1


class _FakeAsyncCredential:
    """A fake async credential. Its get_token is never called."""

    async def get_token(self, *scopes, **kwargs):
        """Fail if called."""
        raise AssertionError("get_token should not be called")


@pytest.mark.parametrize(
    "bad_kwargs",
    [
        {"consistency_level": "Unknown"},
        {"operation_timeout": 0.5},
        {"preferred_locations": "West US"},
    ],
)
def test_failed_async_client_creation_leaves_no_token_helper_rust(bad_kwargs):
    """When creating an async client fails because of a bad setting, no token helper is
    left behind for its credential."""
    from azure.cosmos._backend import _async_credential_bridge as token_helper_module

    credential = _FakeAsyncCredential()
    with pytest.raises(ValueError):
        make_async_backend(
            BACKEND_NAME_RUST,
            url="https://failed-create.documents.azure.com",
            credential=credential,
            **bad_kwargs,
        )
    assert all(key[0] != id(credential) for key in token_helper_module._REGISTRY)
