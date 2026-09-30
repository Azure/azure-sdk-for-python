# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Offline checks of client construction and partial-startup cleanup.

Inject startup failures and inspect backend state and mocked cleanup calls.
Binding validation is simulated where needed; no service operations are made.
"""
import asyncio
import concurrent.futures
import inspect
import subprocess
import sys
import threading
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.core.credentials import AccessToken

import azure.cosmos.cosmos_client as sync_client
import azure.cosmos.aio._cosmos_client as async_client
from azure.cosmos._backend import binding_adapter as sync_backend
from azure.cosmos.aio._backend import binding_adapter as async_backend
from azure.cosmos._backend.contracts import PreparedClientConfig
from azure.cosmos._backend.client_config import build_client_config
from azure.cosmos._retry_options import RetryOptions
from azure.cosmos.documents import ConnectionPolicy


@pytest.fixture(params=[sync_client, async_client], ids=["sync", "async"])
def module(request, monkeypatch):
    """Give each test both the sync and async client, with the legacy connection replaced.

    Replacing the legacy connection is what keeps these tests offline: it is the
    part that would otherwise contact the account during construction. It
    doubles as a witness -- a test can assert it was never built to prove that a
    bad argument was caught before startup began.
    """
    client = request.param
    monkeypatch.setattr(client, "CosmosClientConnection", MagicMock())
    return client


def close_backend(backend):
    """Close a backend without the caller needing to know if it is the sync or async one.

    The async close must be awaited and the sync one must not. Keeping that
    difference here lets each test read the same for both.
    """
    result = backend.close()
    if inspect.isawaitable(result):
        asyncio.run(result)


@pytest.mark.parametrize("enter", [False, True])
def test_rust_client_never_constructs_unused_python_pipeline(monkeypatch, enter):
    from azure.cosmos.aio import _cosmos_client_connection_async as connection_module

    factory = MagicMock(side_effect=AssertionError("unused Python pipeline constructed"))
    monkeypatch.setattr(connection_module, "AsyncPipelineClient", factory)
    client = async_client.CosmosClient("https://startup.invalid", "ZmFrZQ==", _backend="rust")
    initialize = AsyncMock()
    monkeypatch.setattr(client._adapter, "initialize", initialize)

    async def run():
        try:
            if enter:
                async with client:
                    assert "pipeline_client" not in vars(client.client_connection)
        finally:
            await client.close()
            await client.close()

    asyncio.run(run())
    factory.assert_not_called()
    assert initialize.await_count == int(enter)


def test_rust_startup_does_not_import_aiohttp_in_fresh_process():
    script = """
import asyncio
import sys
from unittest.mock import AsyncMock
from azure.cosmos.aio import CosmosClient
assert 'aiohttp' not in sys.modules
async def run():
    client = CosmosClient('https://startup.invalid', 'ZmFrZQ==', _backend='rust')
    client._adapter.initialize = AsyncMock()
    async with client:
        assert 'pipeline_client' not in vars(client.client_connection)
    assert 'aiohttp' not in sys.modules
    assert 'pipeline_client' not in vars(client.client_connection)
asyncio.run(run())
"""
    result = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("failure", [RuntimeError("driver failed"), asyncio.CancelledError()])
def test_rust_startup_failure_does_not_construct_pipeline(monkeypatch, failure):
    from azure.cosmos.aio import _cosmos_client_connection_async as connection_module

    factory = MagicMock(side_effect=AssertionError("unused Python pipeline constructed"))
    monkeypatch.setattr(connection_module, "AsyncPipelineClient", factory)
    client = async_client.CosmosClient("https://startup.invalid", "ZmFrZQ==", _backend="rust")
    monkeypatch.setattr(client._adapter, "initialize", AsyncMock(side_effect=failure))

    async def run():
        with pytest.raises(type(failure)) as caught:
            await client.__aenter__()
        assert caught.value is failure
        assert client._adapter._closing
        assert client.client_connection._routing_map_provider._released

    asyncio.run(run())
    factory.assert_not_called()


def test_deferred_pipeline_is_created_once_on_retained_request(monkeypatch):
    from azure.cosmos.aio import _cosmos_client_connection_async as connection_module

    pipeline = MagicMock()
    pipeline.__aexit__ = AsyncMock()
    factory = MagicMock(return_value=pipeline)
    request = AsyncMock(return_value=({}, {}))
    monkeypatch.setattr(connection_module, "AsyncPipelineClient", factory)
    monkeypatch.setattr(connection_module.asynchronous_request, "AsynchronousRequest", request)
    client = async_client.CosmosClient("https://startup.invalid", "ZmFrZQ==", _backend="rust")
    connection = client.client_connection

    async def run():
        try:
            factory.assert_not_called()
            for _ in range(2):
                await connection.GetDatabaseAccount()
            assert connection.pipeline_client is pipeline
            factory.assert_called_once()
            assert request.await_count == 2
            assert request.call_args.kwargs["pipeline_client"] is pipeline
        finally:
            await client.close()
        pipeline.__aexit__.assert_awaited_once()

    asyncio.run(run())


def test_deferred_pipeline_construction_failure_is_not_cached(monkeypatch):
    from azure.cosmos.aio import _cosmos_client_connection_async as connection_module

    pipeline = MagicMock()
    pipeline.__aexit__ = AsyncMock()
    error = RuntimeError("pipeline construction failed")
    factory = MagicMock(side_effect=[error, pipeline])
    monkeypatch.setattr(connection_module, "AsyncPipelineClient", factory)
    client = async_client.CosmosClient("https://startup.invalid", "ZmFrZQ==", _backend="rust")
    try:
        with pytest.raises(RuntimeError) as caught:
            _ = client.client_connection.pipeline_client
        assert caught.value is error
        assert "pipeline_client" not in vars(client.client_connection)
        assert client.client_connection.pipeline_client is pipeline
        assert factory.call_count == 2
    finally:
        asyncio.run(client.close())
    pipeline.__aexit__.assert_awaited_once()


def test_legacy_custom_transport_keeps_eager_lifecycle(monkeypatch):
    from azure.core.pipeline.transport import AsyncHttpTransport

    transport = MagicMock(spec=AsyncHttpTransport)
    transport.__aenter__ = AsyncMock(return_value=transport)
    transport.__aexit__ = AsyncMock()
    client = async_client.CosmosClient(
        "https://startup.invalid", "ZmFrZQ==", _backend="core-python", transport=transport
    )
    assert "pipeline_client" in vars(client.client_connection)
    setup = AsyncMock()
    monkeypatch.setattr(client.client_connection, "_setup", setup)

    async def run():
        async with client:
            transport.__aenter__.assert_awaited_once()
            setup.assert_awaited_once()
        transport.__aexit__.assert_awaited_once()

    asyncio.run(run())


@pytest.mark.parametrize("async_mode", [False, True], ids=["sync", "async"])
def test_factory_forwards_every_declared_option_to_shared_construction(monkeypatch, async_mode):
    from azure.cosmos._backend import factory as sync_factory
    from azure.cosmos.aio._backend import factory as async_factory

    module = async_factory if async_mode else sync_factory
    factory = module.make_async_backend if async_mode else module.make_backend
    sync_parameters = inspect.signature(sync_factory.make_backend).parameters
    assert sync_parameters == inspect.signature(async_factory.make_async_backend).parameters
    shared_parameters = inspect.signature(sync_factory._make_backend).parameters
    assert set(shared_parameters) == set(sync_parameters) | {"rust_backend_type", "legacy_backend"}
    options = {name: object() for name in sync_parameters if name != "explicit"}
    shared = MagicMock(return_value=object())
    monkeypatch.setattr(module, "_make_backend", shared)

    assert factory("rust", **options) is shared.return_value
    shared.assert_called_once_with(
        "rust",
        rust_backend_type=module.AsyncBindingAdapter if async_mode else module.BindingAdapter,
        legacy_backend=module.ASYNC_LEGACY_BACKEND if async_mode else module.LEGACY_BACKEND,
        **options,
    )


@pytest.mark.parametrize("async_mode", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("failure_stage", [None, "config", "constructor"])
def test_factory_keeps_credential_guard_active_through_construction(
    monkeypatch, async_mode, failure_stage
):
    from contextlib import contextmanager
    from azure.cosmos._backend import factory as sync_factory
    from azure.cosmos.aio._backend import factory as async_factory

    module = async_factory if async_mode else sync_factory
    factory = module.make_async_backend if async_mode else module.make_backend
    events = []
    credential, result = object(), object()
    error = RuntimeError("construction failed")

    @contextmanager
    def guard(value):
        assert value is credential
        events.append("enter")
        try:
            yield "master-key", None
        finally:
            events.append("exit")

    def stage(name, value):
        def run(*args, **kwargs):
            assert events[0] == "enter" and "exit" not in events
            events.append(name)
            if name == failure_stage:
                raise error
            return value
        return run

    monkeypatch.setattr(sync_factory, "resolved_credential", guard)
    monkeypatch.setattr(sync_factory, "build_client_config", stage("config", PreparedClientConfig()))
    monkeypatch.setattr(
        module, "AsyncBindingAdapter" if async_mode else "BindingAdapter", stage("constructor", result)
    )
    if failure_stage is None:
        assert factory("rust", url="https://startup.invalid", credential=credential) is result
        assert events == ["enter", "config", "constructor", "exit"]
    else:
        with pytest.raises(RuntimeError) as caught:
            factory("rust", url="https://startup.invalid", credential=credential)
        assert caught.value is error
        stages = ["config", "constructor"]
        assert events == ["enter", *stages[:stages.index(failure_stage) + 1], "exit"]


@pytest.mark.parametrize("value", [-1, True, 1.5, "3", 2**32])
@pytest.mark.parametrize("nested", [False, True])
def test_invalid_retry_counts_fail_before_legacy_startup(module, value, nested):
    """A retry count that is not a whole number of attempts is refused before anything is
    started or reserved.

    Five bad values are covered: negative, true, a fraction, text, and a number
    too large to fit. True is the one worth naming -- Python treats it as the
    number one, so a check that only asks for a whole number would accept it and
    silently retry once.

    The same value is supplied two ways, directly and buried in a connection
    policy, because customers configure retries both ways and a check on only
    the direct argument would miss the other entirely.

    Neither the legacy startup ran nor was any reservation left against the
    account, so the mistake costs nothing and can be corrected and retried.
    """
    kwargs = {"retry_throttle_total": value}
    if nested:
        policy = ConnectionPolicy()
        policy.RetryOptions = RetryOptions(max_retry_attempt_count=value)
        kwargs = {"connection_policy": policy}
    with pytest.raises(ValueError, match="retry_throttle_total"):
        module.CosmosClient("https://startup.invalid", "ZmFrZQ==", _backend="rust", **kwargs)
    module.CosmosClientConnection.assert_not_called()


@pytest.mark.parametrize("name", ["preferred_locations", "excluded_locations"])
@pytest.mark.parametrize("value", [[123], [None], [True], [" "], {"West US": 1}, False])
def test_invalid_region_values_rejected_at_construction(module, name, value):
    """Reject the listed malformed region-list containers and entries.

    The assertion checks types/nonblank strings, error naming, and no legacy
    connection construction. It does not validate names against Azure's regions.
    """
    with pytest.raises(ValueError, match=name):
        module.CosmosClient("https://startup.invalid", "ZmFrZQ==", _backend="rust", **{name: value})
    module.CosmosClientConnection.assert_not_called()


@pytest.mark.parametrize("value", [-1, True, "30", float("nan"), float("inf"), 2**64 - 1, 2**64])
def test_invalid_retry_wait_rejected(value):
    """Reject the listed invalid cumulative throttle-wait budgets during config building.

    This setting is a total retry-wait budget, not the longest individual delay.
    """
    with pytest.raises(ValueError, match="retry_throttle_backoff_max"):
        build_client_config(None, throttling_max_retry_wait_time_seconds=value)


@pytest.mark.parametrize("stage", ["encoding", "auth", "policy", "legacy"])
def test_failed_constructor_unwinds_backend(module, monkeypatch, stage):
    """Failures at each startup stage close the partially constructed backend."""
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
    assert retained[0]._closing
    replacement = sync_backend.BindingAdapter(
        "https://startup.invalid", master_key="ZmFrZQ==",
        client_config=PreparedClientConfig(proxy_allowed=True, connection_timeout_seconds=3,
                                          read_timeout_seconds=30),
    )
    close_backend(retained[0])
    replacement.close()


def test_close_does_not_validate_or_replay_runtime_settings(monkeypatch):
    validator = MagicMock()
    monkeypatch.setattr("azure.cosmos._rust._validate_runtime_configuration", validator)
    first = sync_backend.BindingAdapter(
        "https://first.invalid", master_key="key",
        client_config=PreparedClientConfig(read_timeout_seconds=20),
    )
    other = sync_backend.BindingAdapter(
        "https://other.invalid", master_key="key",
        client_config=PreparedClientConfig(proxy_allowed=True, read_timeout_seconds=30),
    )
    assert validator.call_count == 2
    validator.reset_mock()
    validator.side_effect = ValueError("must not validate during close")
    first.close()
    other.close()
    validator.assert_not_called()


def test_close_during_initialization_releases_late_handle(monkeypatch):
    """Close releases a late acquired handle without publishing it."""
    started, finish = threading.Event(), threading.Event()

    def initialize(*args):
        started.set()
        assert finish.wait(10)
        return "test-handle"

    binding = SimpleNamespace(acquire_driver_handle=initialize, release_driver_handle=MagicMock())
    monkeypatch.setattr(async_backend, "_rust_module", binding)
    backend = async_backend.AsyncBindingAdapter(
        "https://account.invalid", master_key="key",
        client_config=PreparedClientConfig(proxy_allowed=True),
    )
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(backend._acquire_driver_handle)
        try:
            assert started.wait(10)
            close_backend(backend)
            replacement = sync_backend.BindingAdapter(
                "https://account.invalid", master_key="key",
                client_config=PreparedClientConfig(proxy_allowed=False),
            )
            replacement.close()
        finally:
            finish.set()
        with pytest.raises(RuntimeError, match="closed during initialization"):
            future.result(timeout=10)
    binding.release_driver_handle.assert_called_once_with("test-handle")


def test_failed_driver_build_leaves_runtime_validation_to_binding(monkeypatch):
    """A failed build and close cannot clear settings already fixed in the binding."""
    validator = MagicMock()
    monkeypatch.setattr("azure.cosmos._rust._validate_runtime_configuration", validator)

    def acquire(*args):
        validator.side_effect = ValueError("runtime settings already initialized")
        raise RuntimeError("driver failed")

    monkeypatch.setattr(
        sync_backend, "_rust_module", SimpleNamespace(acquire_driver_handle=acquire)
    )
    backend = sync_backend.BindingAdapter("https://account.invalid", master_key="key")
    with pytest.raises(RuntimeError, match="driver failed"):
        backend._ensure_driver_handle()
    backend.close()
    for config in (
        PreparedClientConfig(proxy_allowed=True),
        PreparedClientConfig(connection_timeout_seconds=3),
        PreparedClientConfig(read_timeout_seconds=30),
    ):
        with pytest.raises(ValueError, match="runtime settings already initialized"):
            sync_backend.BindingAdapter("https://other.invalid", master_key="key", client_config=config)


class AsyncCredential:
    """A credential that returns a token without contacting anything.

    Used to reach the bridge that lets a sync client use an async credential,
    which is what the credential-sharing test below inspects. The token's expiry
    is far in the future so nothing tries to refresh it mid-test.
    """

    async def get_token(self, *args, **kwargs):
        """Return a fixed fake token and expiry; no service validity is implied."""
        return AccessToken("test-token", 9999999999)


def test_failed_constructor_does_not_release_another_clients_credential_hold(module, monkeypatch):
    """A client that fails to start does not tear down the credential machinery a working
    client is still using.

    One client is built successfully and takes a token, which starts a
    background thread shared by everyone using that credential. A second client
    is then built with the same credential and fails.

    Cleaning up after the failure must not touch what the first client holds:
    the shared count is still one and the thread is still alive. Only when the
    first client itself closes does the thread stop.

    Getting this wrong would be nasty to diagnose. A failed construction
    anywhere in the program would silently break token renewal for an unrelated
    working client, which would keep running until its current token expired and
    then start failing to authenticate for no visible reason.
    """
    credential = AsyncCredential()
    first = module.CosmosClient("https://first.invalid", credential, _backend="rust")
    bridge = first._adapter._token_credential
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
    close_backend(first._adapter)
    assert bridge._closed and not thread.is_alive()


@pytest.mark.parametrize("cancelled", [False, True])
@pytest.mark.parametrize("backend_name", ["core-python", "rust"])
def test_async_entry_failure_closes_all_resources(monkeypatch, cancelled, backend_name):
    """If entering the async client fails, everything opened on the way in is closed
    again.

    Legacy entry can fail during account setup; Rust entry can fail while preparing
    the driver. The pipeline cleanup, the endpoint manager, and the routing
    information are each closed or released exactly once, with the backend
    marked closed and no reservation left on the account.

    Cancellation is covered alongside an ordinary error because it arrives by a
    different route and is easy to leave out of a cleanup path -- and the
    likeliest cause is a caller's own timeout around startup, which is not rare.
    A client abandoned there would hold its connections open until the program
    ended.
    """
    error = asyncio.CancelledError() if cancelled else RuntimeError("discovery failed")
    connection = SimpleNamespace(
        pipeline_client=SimpleNamespace(__aenter__=AsyncMock(), __aexit__=AsyncMock()),
        _setup=AsyncMock(side_effect=error),
        _global_endpoint_manager=SimpleNamespace(close=AsyncMock()),
        _routing_map_provider=SimpleNamespace(release=MagicMock()),
    )
    connection._close_pipeline = connection.pipeline_client.__aexit__
    monkeypatch.setattr(async_client, "CosmosClientConnection", MagicMock(return_value=connection))
    client = async_client.CosmosClient(
        "https://account.invalid", "ZmFrZQ==", _backend=backend_name, proxy_allowed=False
    )
    if backend_name == "rust":
        monkeypatch.setattr(client._adapter, "initialize", AsyncMock(side_effect=error))
    backend_close = AsyncMock(wraps=client._adapter.close)
    monkeypatch.setattr(client._adapter, "close", backend_close)

    async def run():
        with pytest.raises(type(error)):
            await client.__aenter__()

    asyncio.run(run())
    connection.pipeline_client.__aexit__.assert_awaited_once()
    connection._global_endpoint_manager.close.assert_awaited_once()
    connection._routing_map_provider.release.assert_called_once()
    backend_close.assert_awaited_once()
    if backend_name == "rust":
        assert client._adapter._closing
        connection._setup.assert_not_awaited()
        connection.pipeline_client.__aenter__.assert_not_awaited()


@pytest.fixture
def async_rust_startup(monkeypatch):
    connection = SimpleNamespace(
        url_connection="https://startup.invalid",
        pipeline_client=SimpleNamespace(__aenter__=AsyncMock(), __aexit__=AsyncMock()),
        _setup=AsyncMock(),
        _global_endpoint_manager=SimpleNamespace(close=AsyncMock()),
        _routing_map_provider=SimpleNamespace(release=MagicMock()),
    )
    connection._close_pipeline = connection.pipeline_client.__aexit__
    binding = SimpleNamespace(
        acquire_driver_handle=MagicMock(return_value="startup-handle"),
        release_driver_handle=MagicMock(),
        read_item_async=AsyncMock(return_value=(200, 0, {}, b'{"id":"order-42"}')),
    )
    monkeypatch.setattr(async_backend, "_rust_module", binding)
    monkeypatch.setattr(async_client, "CosmosClientConnection", MagicMock(return_value=connection))
    client = async_client.CosmosClient("https://startup.invalid", "ZmFrZQ==", _backend="rust")
    yield SimpleNamespace(client=client, connection=connection, binding=binding)
    asyncio.run(client.close())


def test_async_entry_waits_for_driver_and_first_read_reuses_it(async_rust_startup):
    env = async_rust_startup
    started, finish = threading.Event(), threading.Event()

    def acquire(*args):
        env.connection.pipeline_client.__aenter__.assert_not_awaited()
        started.set()
        assert finish.wait(5)
        return "startup-handle"

    env.binding.acquire_driver_handle.side_effect = acquire
    env.binding.acquire_driver_handle.assert_not_called()

    async def run():
        entry = asyncio.create_task(env.client.__aenter__())
        shared_initialization = None
        try:
            assert await asyncio.to_thread(started.wait, 2)
            assert not entry.done()
            env.binding.read_item_async.assert_not_called()
            shared_initialization = asyncio.create_task(env.client._adapter.initialize())
            await asyncio.sleep(0)
            assert not shared_initialization.done()
            finish.set()
            assert await asyncio.wait_for(entry, 5) is env.client
            await asyncio.wait_for(shared_initialization, 5)
            assert env.client._adapter._driver_handle == "startup-handle"
            await asyncio.gather(*(env.client._adapter.initialize() for _ in range(3)))
            container = env.client.get_database_client("sales").get_container_client("orders")
            assert (await container.read_item("order-42", partition_key="order-42"))["id"] == "order-42"
            env.binding.read_item_async.assert_awaited_once()
            assert env.binding.read_item_async.call_args.args[0] == "startup-handle"
            env.binding.acquire_driver_handle.assert_called_once()
            env.connection._setup.assert_not_awaited()
        finally:
            finish.set()
            await env.client.close()
            await asyncio.gather(entry, return_exceptions=True)
            if shared_initialization is not None:
                await asyncio.gather(shared_initialization, return_exceptions=True)

    asyncio.run(run())
    env.binding.release_driver_handle.assert_called_once_with("startup-handle")


def test_async_driver_failure_prevents_entry_and_cleans_up(async_rust_startup):
    env = async_rust_startup
    error = RuntimeError("account initialization failed")
    env.binding.acquire_driver_handle.side_effect = error

    async def run():
        with pytest.raises(RuntimeError) as caught:
            async with env.client:
                pytest.fail("Customer block must not run after failed account initialization")
        assert caught.value is error

    asyncio.run(run())
    assert env.client._adapter._closing
    env.connection.pipeline_client.__aexit__.assert_awaited_once()
    env.connection._global_endpoint_manager.close.assert_awaited_once()
    env.connection._routing_map_provider.release.assert_called_once()
    env.connection._setup.assert_not_awaited()
    env.binding.read_item_async.assert_not_called()
    env.binding.release_driver_handle.assert_not_called()


def test_cancelled_async_entry_releases_late_driver(async_rust_startup):
    env = async_rust_startup
    started, finish = threading.Event(), threading.Event()

    def acquire(*args):
        started.set()
        assert finish.wait(5)
        return "late-startup-handle"

    env.binding.acquire_driver_handle.side_effect = acquire

    async def run():
        entry = asyncio.create_task(env.client.__aenter__())
        try:
            assert await asyncio.to_thread(started.wait, 2)
            acquisition = env.client._adapter._init_future
            entry.cancel()
            with pytest.raises(asyncio.CancelledError):
                await asyncio.wait_for(entry, 2)
            assert env.client._adapter._closing
            env.connection.pipeline_client.__aexit__.assert_awaited_once()
            env.connection._global_endpoint_manager.close.assert_awaited_once()
            env.connection._routing_map_provider.release.assert_called_once()
            finish.set()
            with pytest.raises(RuntimeError, match="closed during initialization"):
                await asyncio.wait_for(acquisition, 5)
            assert env.client._adapter._driver_handle is None
        finally:
            finish.set()
            await env.client.close()
            await asyncio.gather(entry, return_exceptions=True)

    asyncio.run(run())
    env.binding.release_driver_handle.assert_called_once_with("late-startup-handle")
    env.connection._setup.assert_not_awaited()


def test_client_priority_defaults_are_captured(module):
    """Priority and throughput bucket given to the client are kept as defaults for later
    item calls.

    Both describe how the account should treat this client's work, so customers
    set them once on the client rather than on every call. Dropping them at
    construction would be invisible: every request would still succeed, just
    without the priority or bucket the customer was relying on to protect their
    important traffic.
    """
    client = module.CosmosClient(
        "https://account.invalid", "ZmFrZQ==", _backend="rust", priority="Low", throughput_bucket=3
    )
    assert client._item_context.defaults.priority == "Low"
    assert client._item_context.defaults.throughput_bucket == 3
    close_backend(client._adapter)


@pytest.mark.parametrize("backend_name", ["rust", "core-python"])
def test_client_and_proxies_share_the_adapter_field(module, backend_name):
    client = module.CosmosClient(
        "https://account.invalid", "ZmFrZQ==", _backend=backend_name
    )
    try:
        context = client._item_context
        assert context.adapter is client._adapter
        assert "_backend" not in vars(client)
        assert not hasattr(context, "backend")
        assert client.client_connection._backend is client._adapter

        database = client.get_database_client("sales")
        container = database.get_container_client("orders")
        assert database._item_context is context
        assert container._item_context is context
        assert container._item_context.adapter is client._adapter
    finally:
        close_backend(client._adapter)


def test_native_validation_does_not_initialize_or_reserve_runtime():
    """A fresh process proves that the real export permits different unused settings."""
    code = """
from azure.cosmos import _rust
from azure.cosmos._backend.contracts import PreparedClientConfig
assert not hasattr(_rust, "_driver_identity")
assert _rust._runtime_configuration() is None
for config in (
    None,
    PreparedClientConfig(proxy_allowed=True, connection_timeout_seconds=2),
    PreparedClientConfig(proxy_allowed=False, connection_timeout_seconds=5),
):
    assert _rust._validate_runtime_configuration(config) is None
    assert _rust._runtime_configuration() is None
"""
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, timeout=30, check=False
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("stage", ["account", "consistency"])
def test_real_sync_connection_releases_partial_startup_resources(monkeypatch, stage):
    """The real legacy connection cleans up after itself when its own startup fails partway.

    Two failure points are covered: fetching the account information, and
    settling the consistency level just after. Both happen inside the real
    connection code rather than a stand-in, which is the point -- everything
    else in this file replaces that code, so this is the one place its own
    cleanup is exercised.

    The routing information is released, the transport is closed, the original
    error reaches the caller unchanged, and no reservation is left on the
    account. The refresh that would normally follow a successful start is
    confirmed not to have run, so failed startup does not go on doing work in
    the background for a client that does not exist.
    """
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
            "https://account.invalid", "ZmFrZQ==", _backend="core-python"
        )
    assert failure.value is error
    routing.release.assert_called_once()
    pipeline.close.assert_called_once()
    manager.force_refresh_on_startup.assert_not_called()
