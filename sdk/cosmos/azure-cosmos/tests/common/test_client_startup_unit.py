# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""No-network regression for transactional client startup and validation."""
import asyncio
import concurrent.futures
import inspect
import threading
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.core.credentials import AccessToken

import azure.cosmos.cosmos_client as sync_client
import azure.cosmos.aio._cosmos_client as async_client
from azure.cosmos._backend import _driver_registry as registry
from azure.cosmos._backend import rust as sync_backend
from azure.cosmos.aio._backend import rust as async_backend
from azure.cosmos._backend.contracts import PreparedClientConfig
from azure.cosmos._backend.client_config import build_client_config
from azure.cosmos._retry_options import RetryOptions
from azure.cosmos.documents import ConnectionPolicy


@pytest.fixture(autouse=True)
def reset_registry(monkeypatch):
    registry._reset_for_tests()
    monkeypatch.delenv("COSMOS_RUST_STRICT_ISOLATION", raising=False)
    yield
    registry._reset_for_tests()


@pytest.fixture(params=[sync_client, async_client], ids=["sync", "async"])
def module(request, monkeypatch):
    client = request.param
    monkeypatch.setattr(client, "CosmosClientConnection", MagicMock())
    return client


def close_backend(backend):
    result = backend.close()
    if inspect.isawaitable(result):
        asyncio.run(result)


@pytest.mark.parametrize("value", [-1, True, 1.5, "3", 2**32])
@pytest.mark.parametrize("nested", [False, True])
def test_invalid_retry_counts_fail_before_legacy_startup(module, value, nested):
    kwargs = {"retry_throttle_total": value}
    if nested:
        policy = ConnectionPolicy()
        policy.RetryOptions = RetryOptions(max_retry_attempt_count=value)
        kwargs = {"connection_policy": policy}
    with pytest.raises(ValueError, match="retry_throttle_total"):
        module.CosmosClient("https://startup.invalid", "ZmFrZQ==", _backend="rust", **kwargs)
    module.CosmosClientConnection.assert_not_called()
    assert registry._live_client_count("https://startup.invalid") == 0


@pytest.mark.parametrize("name", ["preferred_locations", "excluded_locations"])
@pytest.mark.parametrize("value", [[123], [None], [True], [" "], {"West US": 1}, False])
def test_invalid_region_values_rejected_at_construction(module, name, value):
    with pytest.raises(ValueError, match=name):
        module.CosmosClient("https://startup.invalid", "ZmFrZQ==", _backend="rust", **{name: value})
    module.CosmosClientConnection.assert_not_called()


@pytest.mark.parametrize("value", [-1, True, "30", float("nan"), float("inf"), 2**64 - 1, 2**64])
def test_invalid_retry_wait_rejected(value):
    with pytest.raises(ValueError, match="retry_throttle_backoff_max"):
        build_client_config(None, throttling_max_retry_wait_time_seconds=value)


@pytest.mark.parametrize("stage", ["encoding", "auth", "policy", "legacy"])
def test_failed_constructor_unwinds_backend_and_reservations(module, monkeypatch, stage):
    factory_name = "make_backend" if module is sync_client else "make_async_backend"
    factory = getattr(module, factory_name)
    retained = []

    def capture(*args, **kwargs):
        backend = factory(*args, **kwargs)
        retained.append(backend)
        return backend

    monkeypatch.setattr(module, factory_name, capture)
    kwargs = {"proxy_allowed": False, "connection_timeout": 2, "read_timeout": 25}
    error = RuntimeError("startup failed")
    if stage == "encoding":
        kwargs["enable_compact_utf8_item_writes"] = "invalid"
        expected = (TypeError, ValueError)
    else:
        target = {"auth": "_build_auth", "policy": "_build_connection_policy",
                  "legacy": "CosmosClientConnection"}[stage]
        monkeypatch.setattr(module, target, MagicMock(side_effect=error))
        expected = RuntimeError
    with pytest.raises(expected):
        module.CosmosClient("https://startup.invalid", "ZmFrZQ==", _backend="rust", **kwargs)
    assert len(retained) == 1
    assert retained[0]._closing and retained[0]._config_released
    assert registry._live_client_count("https://startup.invalid") == 0
    replacement = sync_backend.RustBackend(
        "https://startup.invalid", master_key="ZmFrZQ==",
        client_config=PreparedClientConfig(proxy_allowed=True, connection_timeout_seconds=3,
                                          read_timeout_seconds=30),
    )
    close_backend(retained[0])
    assert registry._live_client_count("https://startup.invalid") == 1
    replacement.close()


def test_timeout_conflict_does_not_leave_a_proxy_reservation():
    first = sync_backend.RustBackend(
        "https://first.invalid", master_key="key",
        client_config=PreparedClientConfig(read_timeout_seconds=20),
    )
    with pytest.raises(registry.TransportTimeoutPolicyConflictError):
        sync_backend.RustBackend(
            "https://failed.invalid", master_key="key",
            client_config=PreparedClientConfig(proxy_allowed=False, read_timeout_seconds=30),
        )
    other = sync_backend.RustBackend(
        "https://other.invalid", master_key="key",
        client_config=PreparedClientConfig(proxy_allowed=True, read_timeout_seconds=20),
    )
    first.close()
    with pytest.raises(registry.ProxyPolicyConflictError):
        sync_backend.RustBackend(
            "https://conflict.invalid", master_key="key",
            client_config=PreparedClientConfig(proxy_allowed=False),
        )
    other.close()
    replacement = sync_backend.RustBackend(
        "https://replacement.invalid", master_key="key",
        client_config=PreparedClientConfig(proxy_allowed=False, read_timeout_seconds=30),
    )
    replacement.close()


def test_strict_isolation_failure_rolls_back_new_runtime_reservations():
    first = sync_backend.RustBackend("https://account.invalid", master_key="key")
    with pytest.raises(registry.StrictDriverIsolationError):
        sync_backend.RustBackend(
            "https://account.invalid", master_key="key", strict_isolation=True,
            client_config=PreparedClientConfig(proxy_allowed=False, read_timeout_seconds=25),
        )
    assert registry._live_client_count("https://account.invalid") == 1
    other = sync_backend.RustBackend(
        "https://other.invalid", master_key="key",
        client_config=PreparedClientConfig(proxy_allowed=True, read_timeout_seconds=30),
    )
    first.close()
    other.close()


@pytest.mark.parametrize("frozen", [False, True])
def test_close_during_initialization_retains_inflight_reservation(monkeypatch, frozen):
    started, finish = threading.Event(), threading.Event()
    state = SimpleNamespace(settings=None)

    def initialize(*args):
        started.set()
        assert finish.wait(10)
        if frozen:
            state.settings = (True, None, None)
        return "test-handle"

    binding = SimpleNamespace(acquire_driver_handle=initialize, release_driver_handle=MagicMock())
    monkeypatch.setattr(async_backend, "_rust_module", binding)
    monkeypatch.setattr(async_backend, "_runtime_configuration", lambda: state.settings)
    backend = async_backend.AsyncRustBackend(
        "https://account.invalid", master_key="key",
        client_config=PreparedClientConfig(proxy_allowed=True),
    )
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(backend._build_driver_handle)
        try:
            assert started.wait(10)
            close_backend(backend)
            with pytest.raises(registry.ProxyPolicyConflictError):
                sync_backend.RustBackend(
                    "https://other.invalid", master_key="key",
                    client_config=PreparedClientConfig(proxy_allowed=False),
                )
        finally:
            finish.set()
        with pytest.raises(RuntimeError, match="closed during initialization"):
            future.result(timeout=10)
    binding.release_driver_handle.assert_called_once_with("test-handle")
    assert registry._live_client_count("https://account.invalid") == 0
    if frozen:
        with pytest.raises(registry.ProxyPolicyConflictError):
            sync_backend.RustBackend(
                "https://other.invalid", master_key="key",
                client_config=PreparedClientConfig(proxy_allowed=False),
            )
    else:
        replacement = sync_backend.RustBackend(
            "https://other.invalid", master_key="key",
            client_config=PreparedClientConfig(proxy_allowed=False),
        )
        replacement.close()


@pytest.mark.parametrize("settings", [(False, 2, 25), (None, None, None)])
def test_failed_driver_build_preserves_actually_initialized_runtime(monkeypatch, settings):
    monkeypatch.setattr(sync_backend, "_rust_module", SimpleNamespace(
        acquire_driver_handle=MagicMock(side_effect=RuntimeError("driver failed")),
    ))
    monkeypatch.setattr(sync_backend, "_runtime_configuration", lambda: settings)
    backend = sync_backend.RustBackend("https://account.invalid", master_key="key")
    with pytest.raises(RuntimeError, match="driver failed"):
        backend._ensure_driver_handle()
    backend.close()
    for config in (
        PreparedClientConfig(proxy_allowed=True),
        PreparedClientConfig(connection_timeout_seconds=3),
        PreparedClientConfig(read_timeout_seconds=30),
    ):
        with pytest.raises((registry.ProxyPolicyConflictError, registry.TransportTimeoutPolicyConflictError)):
            sync_backend.RustBackend("https://other.invalid", master_key="key", client_config=config)


class AsyncCredential:
    async def get_token(self, *args, **kwargs):
        return AccessToken("test-token", 9999999999)


def test_failed_constructor_does_not_release_another_clients_credential_hold(module, monkeypatch):
    credential = AsyncCredential()
    first = module.CosmosClient("https://first.invalid", credential, _backend="rust")
    bridge = first._backend._token_credential
    bridge.get_token("test-scope")
    thread = bridge._thread
    retained = []
    factory_name = "make_backend" if module is sync_client else "make_async_backend"
    factory = getattr(module, factory_name)

    def capture(*args, **kwargs):
        backend = factory(*args, **kwargs)
        retained.append(backend)
        return backend

    monkeypatch.setattr(module, factory_name, capture)
    monkeypatch.setattr(module, "CosmosClientConnection", MagicMock(side_effect=RuntimeError("startup")))
    with pytest.raises(RuntimeError, match="startup"):
        module.CosmosClient("https://second.invalid", credential, _backend="rust")
    close_backend(retained[0])
    assert bridge._refcount == 1 and thread.is_alive()
    close_backend(first._backend)
    assert bridge._closed and not thread.is_alive()


@pytest.mark.parametrize("cancelled", [False, True])
def test_async_entry_failure_closes_all_resources(monkeypatch, cancelled):
    error = asyncio.CancelledError() if cancelled else RuntimeError("discovery failed")
    connection = SimpleNamespace(
        pipeline_client=SimpleNamespace(__aenter__=AsyncMock(), __aexit__=AsyncMock()),
        _setup=AsyncMock(side_effect=error),
        _global_endpoint_manager=SimpleNamespace(close=AsyncMock()),
        _routing_map_provider=SimpleNamespace(release=MagicMock()),
    )
    monkeypatch.setattr(async_client, "CosmosClientConnection", MagicMock(return_value=connection))
    client = async_client.CosmosClient(
        "https://account.invalid", "ZmFrZQ==", _backend="rust", proxy_allowed=False
    )

    async def run():
        with pytest.raises(type(error)):
            await client.__aenter__()

    asyncio.run(run())
    connection.pipeline_client.__aexit__.assert_awaited_once()
    connection._global_endpoint_manager.close.assert_awaited_once()
    connection._routing_map_provider.release.assert_called_once()
    assert client._backend._closing and registry._live_client_count("https://account.invalid") == 0


def test_client_priority_defaults_are_captured(module):
    client = module.CosmosClient(
        "https://account.invalid", "ZmFrZQ==", _backend="rust", priority="Low", throughput_bucket=3
    )
    assert client._item_context.defaults.priority == "Low"
    assert client._item_context.defaults.throughput_bucket == 3
    close_backend(client._backend)


def test_frozen_timeout_compares_native_nanosecond_precision():
    registry.freeze_runtime_policy((None, 2.123456789, 25.123456789))
    backend = sync_backend.RustBackend(
        "https://account.invalid", master_key="key",
        client_config=PreparedClientConfig(
            connection_timeout_seconds=2.1234567891, read_timeout_seconds=25.1234567891
        ),
    )
    backend.close()
    with pytest.raises(registry.TransportTimeoutPolicyConflictError):
        sync_backend.RustBackend(
            "https://other.invalid", master_key="key",
            client_config=PreparedClientConfig(connection_timeout_seconds=2.1234567896),
        )


@pytest.mark.parametrize("stage", ["account", "consistency"])
def test_real_sync_connection_releases_partial_startup_resources(monkeypatch, stage):
    from azure.cosmos import _cosmos_client_connection as connection_module

    error = RuntimeError("account startup failed")
    manager, pipeline, routing = MagicMock(), MagicMock(), MagicMock()
    if stage == "account":
        manager._GetDatabaseAccount.side_effect = error
    else:
        monkeypatch.setattr(
            connection_module.CosmosClientConnection, "_set_client_consistency_level",
            MagicMock(side_effect=error),
        )
    monkeypatch.setattr(
        connection_module, "_GlobalPartitionEndpointManagerForPerPartitionAutomaticFailover",
        MagicMock(return_value=manager),
    )
    monkeypatch.setattr(connection_module, "PipelineClient", MagicMock(return_value=pipeline))
    monkeypatch.setattr(
        connection_module.routing_map_provider, "SmartRoutingMapProvider", MagicMock(return_value=routing)
    )
    with pytest.raises(RuntimeError) as failure:
        sync_client.CosmosClient(
            "https://account.invalid", "ZmFrZQ==", _backend="rust", proxy_allowed=False
        )
    assert failure.value is error
    routing.release.assert_called_once()
    pipeline.close.assert_called_once()
    manager.force_refresh_on_startup.assert_not_called()
    assert registry._live_client_count("https://account.invalid") == 0
