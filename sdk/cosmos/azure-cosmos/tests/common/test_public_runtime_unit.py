# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Runtime construction is real; client operation dispatch is isolated from Azure."""
import asyncio
from dataclasses import FrozenInstanceError
import gc
import inspect
import threading
import weakref
from unittest.mock import MagicMock

import pytest

from azure.cosmos import ConnectionPoolOptions, CosmosClient, CosmosRuntime, _rust
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos.documents import ConnectionPolicy


def close(client):
    result = client.close()
    if inspect.isawaitable(result):
        asyncio.run(result)


@pytest.mark.parametrize("field,value", [
    ("connection_timeout", True), ("connection_timeout", "2"),
    ("connection_timeout", float("nan")), ("connection_timeout", 0.09),
    ("connection_timeout", 7), ("data_http_request_timeout", float("inf")),
    ("data_http_request_timeout", 0), ("metadata_http_request_timeout", 66),
    ("idle_connection_timeout", 60), ("max_idle_connections_per_endpoint", 9),
    ("max_idle_connections_per_endpoint", True), ("proxy_allowed", 1),
    ("connection_timeout", 10**1000), ("data_http_request_timeout", 2**64),
])
def test_connection_options_validate_before_runtime_creation(field, value):
    with pytest.raises((TypeError, ValueError)):
        ConnectionPoolOptions(**{field: value})


def test_options_and_runtime_are_immutable():
    options = ConnectionPoolOptions(connection_timeout=2)
    with pytest.raises(FrozenInstanceError):
        options.connection_timeout = 3
    runtime = CosmosRuntime.create(connection_pool=options)
    with pytest.raises(FrozenInstanceError):
        runtime.connection_pool = ConnectionPoolOptions()
    with pytest.raises(TypeError, match="create"):
        CosmosRuntime()
    with pytest.raises(TypeError, match="connection_pool"):
        CosmosRuntime.create(connection_pool={})


def test_explicit_runtimes_initialize_immediately_and_remain_independent():
    first = CosmosRuntime.create(connection_pool=ConnectionPoolOptions(
        connection_timeout=2, data_http_request_timeout=8, metadata_http_request_timeout=20))
    second = CosmosRuntime.create(connection_pool=ConnectionPoolOptions(
        connection_timeout=5, data_http_request_timeout=12, metadata_http_request_timeout=30))
    duplicate = CosmosRuntime.create(connection_pool=first.connection_pool)
    assert first._handle.timeouts == (2, 8, 20)
    assert second._handle.timeouts == (5, 12, 30)
    assert duplicate._handle.id != first._handle.id
    assert duplicate != first


@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("data_timeout,metadata_timeout", [(120, 65), (0.1, 0.1), (65, 20)])
def test_data_and_metadata_attempt_limits_are_independent(is_async, data_timeout, metadata_timeout):
    options = ConnectionPoolOptions(
        connection_timeout=2,
        data_http_request_timeout=data_timeout,
        metadata_http_request_timeout=metadata_timeout,
    )
    runtime = (
        asyncio.run(CosmosRuntime.create_async(connection_pool=options))
        if is_async else CosmosRuntime.create(connection_pool=options)
    )
    assert runtime._handle.timeouts == (2, data_timeout, metadata_timeout)


def test_async_creation_returns_initialized_shareable_runtime():
    async def run():
        first, second = await asyncio.gather(
            CosmosRuntime.create_async(connection_pool=ConnectionPoolOptions(connection_timeout=2)),
            CosmosRuntime.create_async(connection_pool=ConnectionPoolOptions(connection_timeout=5)),
        )
        assert first._handle.timeouts[0] == 2
        assert second._handle.timeouts[0] == 5
        assert first._handle.id != second._handle.id
        return first

    runtime = asyncio.run(run())
    client = CosmosClient("https://runtime.invalid", "key", runtime=runtime, _backend="rust")
    try:
        assert client._adapter._runtime is runtime
    finally:
        close(client)


@pytest.mark.parametrize("client_type", [CosmosClient, AsyncCosmosClient])
@pytest.mark.parametrize("setting", [
    {"connection_timeout": 2}, {"request_timeout": 2000}, 
    {"proxy_allowed": False},
    {"data_http_request_timeout": 6}, {"metadata_http_request_timeout": 20},
])
def test_legacy_client_network_overrides_are_rejected(client_type, setting):
    with pytest.raises(TypeError, match="runtime|Runtime"):
        client_type("https://runtime.invalid", "key", _backend="rust", **setting)


@pytest.mark.parametrize("client_type", [CosmosClient, AsyncCosmosClient])
def test_nested_policy_timeouts_cannot_bypass_migration(client_type):
    policy = ConnectionPolicy()
    policy.RequestTimeout = 2
    with pytest.raises(TypeError, match="ConnectionPoolOptions"):
        client_type("https://runtime.invalid", "key", _backend="rust", connection_policy=policy)


@pytest.mark.parametrize("client_type", [CosmosClient, AsyncCosmosClient])
@pytest.mark.parametrize("timeout", [0.5, True, float("nan"), float("inf"), 2**64])
def test_invalid_overall_client_timeouts_are_rejected(client_type, timeout):
    with pytest.raises(ValueError, match="timeout"):
        client_type("https://runtime.invalid", "key", _backend="rust", timeout=timeout)


@pytest.mark.parametrize("client_type", [CosmosClient, AsyncCosmosClient])
def test_overall_timeout_does_not_require_custom_runtime(client_type):
    client = client_type("https://runtime.invalid", "key", timeout=30, _backend="rust")
    try:
        assert client._adapter._runtime is None
        assert client._adapter._client_config.operation_timeout_seconds == 30
    finally:
        close(client)


@pytest.mark.parametrize("client_type", [CosmosClient, AsyncCosmosClient])
def test_selected_runtime_is_retained_and_passed_to_binding(client_type, monkeypatch):
    runtime = CosmosRuntime.create(connection_pool=ConnectionPoolOptions(connection_timeout=2))
    retained = weakref.ref(runtime)
    first = client_type("https://runtime.invalid", "key", runtime=runtime, _backend="rust")
    second = client_type("https://runtime.invalid", "key", runtime=runtime, _backend="rust")
    del runtime
    gc.collect()
    try:
        assert retained() is not None
        binding = MagicMock()
        binding.acquire_driver_handle.return_value = "driver"
        monkeypatch.setattr(
            "azure.cosmos._backend._binding_adapter_shared.configure_packaged_query_plan_interop",
            lambda _: None,
        )
        assert first._adapter._initialize_driver(binding, first._adapter._runtime) == "driver"
        assert binding.acquire_driver_handle.call_args.kwargs["runtime"] is retained()._handle
        close(first)
        assert second._adapter._runtime is retained()
    finally:
        close(first)
        close(second)
    gc.collect()
    assert retained() is None


def test_runtime_initialization_failures_are_not_hidden(monkeypatch):
    def fail(_):
        raise RuntimeError("runtime initialization failed")

    monkeypatch.setattr(_rust, "_create_runtime", fail)
    with pytest.raises(RuntimeError, match="initialization failed"):
        CosmosRuntime.create()


def test_async_runtime_failure_and_cancellation_propagate(monkeypatch):
    async def run():
        for error in (RuntimeError("initialization failed"), asyncio.CancelledError()):
            async def fail(_):
                await asyncio.sleep(0)
                raise error

            monkeypatch.setattr(_rust, "_create_runtime_async", fail)
            with pytest.raises(type(error)) as caught:
                await CosmosRuntime.create_async()
            assert caught.value is error

    asyncio.run(run())


@pytest.mark.parametrize("client_type", [CosmosClient, AsyncCosmosClient])
def test_invalid_runtime_is_rejected(client_type):
    with pytest.raises(TypeError, match="CosmosRuntime"):
        client_type("https://runtime.invalid", "key", runtime=object(), _backend="rust")
    with pytest.raises(ValueError, match="Rust"):
        client_type("https://runtime.invalid", "key", runtime=CosmosRuntime.create(), _backend="core-python")


def test_async_close_cannot_switch_an_acquisition_to_default_runtime(monkeypatch):
    from azure.cosmos.aio._backend.binding_adapter import AsyncBindingAdapter

    async def run():
        runtime = await CosmosRuntime.create_async()
        adapter = AsyncBindingAdapter("https://runtime.invalid", master_key="key", runtime=runtime)
        entered, resume = threading.Event(), threading.Event()
        binding = MagicMock()
        binding.acquire_driver_handle.return_value = "late-driver"
        monkeypatch.setattr("azure.cosmos.aio._backend.binding_adapter._rust_module", binding)
        initialize = adapter._initialize_driver

        def delayed_initialize(selected_binding, selected_runtime):
            entered.set()
            assert resume.wait(5), "test did not release acquisition"
            return initialize(selected_binding, selected_runtime)

        monkeypatch.setattr(adapter, "_initialize_driver", delayed_initialize)
        pending = asyncio.create_task(adapter._ensure_driver_handle())
        try:
            assert await asyncio.to_thread(entered.wait, 5), "acquisition did not start"
            await adapter.close()
            assert adapter._runtime is None
        finally:
            resume.set()
            with pytest.raises(RuntimeError, match="closed during initialization"):
                await pending
            await adapter.close()
        assert binding.acquire_driver_handle.call_args.kwargs["runtime"] is runtime._handle
        binding.release_driver_handle.assert_called_once_with("late-driver")

    asyncio.run(run())
