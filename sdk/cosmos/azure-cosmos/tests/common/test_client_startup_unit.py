# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Offline tests for creating, starting and closing a CosmosClient.

Terms used in this file:

- compiled module: the part of the SDK that sends most requests to the service.
- adapter: the Python object that passes the client's requests to the compiled
  module.
- handle: the object the compiled module returns when the client first
  connects to the account.
- HTTP pipeline: the Python HTTP sender from ``azure.core``. A few requests
  still use it, so it is created only the first time one of them runs.
- partition-map cache: the record of which partition holds which data. All
  clients for the same account share it, and each client gives back its share
  when it closes.
- token helper: the object the async adapter creates when it first connects,
  so the compiled module can get tokens from an async credential.
- account refresh task: a background task in the async client that re-reads
  the account's regions and checks they can be reached.

The tests make startup steps fail on purpose and check that the client cleans
up whatever it already created. No request reaches a real account.
"""
import asyncio
import concurrent.futures
import inspect
import logging
import subprocess
import threading
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.core.credentials import AccessToken

import azure.cosmos.cosmos_client as sync_client
import azure.cosmos._cosmos_client_connection as sync_connection
import azure.cosmos.aio._cosmos_client as async_client
from azure.cosmos._backend import binding_adapter as sync_adapter_module
from azure.cosmos.aio._backend import binding_adapter as async_adapter_module
from azure.cosmos._backend.contracts import PreparedClientConfig
from azure.cosmos._backend.client_config import build_client_config
from azure.cosmos._retry_options import RetryOptions
from azure.cosmos.documents import ConnectionPolicy
from common.sdk_subprocess import sdk_python_command


@pytest.fixture(params=[sync_client, async_client], ids=["sync", "async"])
def module(request, monkeypatch):
    """Give each test both the sync and async client module, with the connection replaced.

    The client's connection object is replaced by a mock. A test can then check
    that the mock was never called, which proves a bad argument was rejected
    before the client started being built.
    """
    client = request.param
    monkeypatch.setattr(client, "CosmosClientConnection", MagicMock())
    return client


def close_adapter(adapter):
    """Close an adapter without the caller needing to know if it is the sync or async one.

    The async close must be awaited and the sync one must not. Keeping that
    difference here lets each test read the same for both.
    """
    result = adapter.close()
    if inspect.isawaitable(result):
        asyncio.run(result)


@pytest.mark.parametrize("use_with_block", [False, True], ids=["no-with-block", "with-block"])
def test_sync_client_does_not_create_http_pipeline_when_unused_rust(monkeypatch, use_with_block):
    """Creating a client, optionally using it in a ``with`` block, and closing it
    twice never creates the HTTP pipeline. Closing still closes the adapter and
    gives back the client's partition-map cache share."""
    make_pipeline = MagicMock(side_effect=AssertionError("unused HTTP pipeline created"))
    monkeypatch.setattr(sync_connection, "PipelineClient", make_pipeline)
    client = sync_client.CosmosClient("https://startup.invalid", "ZmFrZQ==", _backend="rust")
    try:
        if use_with_block:
            with client:
                assert "pipeline_client" not in vars(client.client_connection)
    finally:
        client.close()
        client.close()
    make_pipeline.assert_not_called()
    assert "pipeline_client" not in vars(client.client_connection)
    assert client._adapter._closing
    assert client.client_connection._routing_map_provider._released


def test_sync_with_block_error_closes_client_without_creating_http_pipeline_rust(monkeypatch):
    """An error raised inside the ``with`` block reaches the caller unchanged.
    The client is closed and no HTTP pipeline is created."""
    make_pipeline = MagicMock(side_effect=AssertionError("unused HTTP pipeline created"))
    monkeypatch.setattr(sync_connection, "PipelineClient", make_pipeline)
    client = sync_client.CosmosClient("https://startup.invalid", "ZmFrZQ==", _backend="rust")
    block_error = RuntimeError("customer block failed")
    with pytest.raises(RuntimeError) as caught:
        with client:
            raise block_error
    assert caught.value is block_error
    make_pipeline.assert_not_called()
    assert client._adapter._closing
    assert client.client_connection._routing_map_provider._released


def test_sync_construction_failure_does_not_create_http_pipeline_rust(monkeypatch):
    """If building the client fails partway through (here, while setting up the
    partition-map cache), the error reaches the caller unchanged and no HTTP
    pipeline is created."""
    make_pipeline = MagicMock(side_effect=AssertionError("unused HTTP pipeline created"))
    setup_error = RuntimeError("partition-map cache setup failed")
    monkeypatch.setattr(sync_connection, "PipelineClient", make_pipeline)
    monkeypatch.setattr(
        sync_connection.routing_map_provider, "SmartRoutingMapProvider", MagicMock(side_effect=setup_error),
    )
    with pytest.raises(RuntimeError) as caught:
        sync_client.CosmosClient("https://startup.invalid", "ZmFrZQ==", _backend="rust")
    assert caught.value is setup_error
    make_pipeline.assert_not_called()


def test_sync_http_pipeline_created_on_first_use_and_reused_rust(monkeypatch):
    """The HTTP pipeline is not created at startup. The first request that needs
    it creates it, the second request reuses it, and leaving the ``with`` block
    closes it."""
    pipeline = MagicMock()
    make_pipeline = MagicMock(return_value=pipeline)
    send_request = MagicMock(return_value=({}, {}))
    monkeypatch.setattr(sync_connection, "PipelineClient", make_pipeline)
    monkeypatch.setattr(sync_connection.synchronized_request, "SynchronizedRequest", send_request)
    with sync_client.CosmosClient("https://startup.invalid", "ZmFrZQ==", _backend="rust") as client:
        make_pipeline.assert_not_called()
        # Reading account details is one of the requests that still uses the HTTP pipeline.
        for _ in range(2):
            client.client_connection.GetDatabaseAccount()
        assert client.client_connection.pipeline_client is pipeline
        make_pipeline.assert_called_once()
        assert send_request.call_count == 2
        assert send_request.call_args.kwargs["pipeline_client"] is pipeline
    pipeline.__exit__.assert_called_once()


def test_sync_failed_http_pipeline_creation_is_retried_on_next_use_rust(monkeypatch):
    """If creating the HTTP pipeline fails, the failure is not remembered. The
    next use tries again and succeeds, and closing the client closes that
    pipeline."""
    pipeline = MagicMock()
    creation_error = RuntimeError("pipeline creation failed")
    make_pipeline = MagicMock(side_effect=[creation_error, pipeline])
    monkeypatch.setattr(sync_connection, "PipelineClient", make_pipeline)
    client = sync_client.CosmosClient("https://startup.invalid", "ZmFrZQ==", _backend="rust")
    try:
        with pytest.raises(RuntimeError) as caught:
            _ = client.client_connection.pipeline_client
        assert caught.value is creation_error
        # The pipeline is saved on the connection only after it is created successfully.
        assert "pipeline_client" not in vars(client.client_connection)
        assert client.client_connection.pipeline_client is pipeline
        assert make_pipeline.call_count == 2
    finally:
        client.close()
    pipeline.__exit__.assert_called_once()


def test_sync_http_pipeline_created_once_when_threads_ask_at_same_time_rust(monkeypatch):
    """When four threads ask for the HTTP pipeline at the same moment, it is
    created only once and all four get the same one."""
    pipeline = MagicMock()
    make_pipeline = MagicMock(return_value=pipeline)
    monkeypatch.setattr(sync_connection, "PipelineClient", make_pipeline)
    # Makes the four threads wait for each other, so they ask at the same moment.
    all_threads_ready = threading.Barrier(4)
    with sync_client.CosmosClient("https://startup.invalid", "ZmFrZQ==", _backend="rust") as client:
        make_pipeline.assert_not_called()

        def get_pipeline():
            all_threads_ready.wait(timeout=5)
            return client.client_connection.pipeline_client

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as thread_pool:
            futures = [thread_pool.submit(get_pipeline) for _ in range(4)]
            assert all(future.result(timeout=5) is pipeline for future in futures)
        make_pipeline.assert_called_once()
    pipeline.__exit__.assert_called_once()


@pytest.mark.parametrize("use_with_block", [False, True], ids=["no-with-block", "with-block"])
def test_async_client_does_not_create_http_pipeline_when_unused_rust(monkeypatch, use_with_block):
    """Creating an async client, optionally using it in an ``async with`` block,
    and closing it twice never creates the HTTP pipeline."""
    from azure.cosmos.aio import _cosmos_client_connection_async as connection_module

    class CheckedConnection(connection_module.CosmosClientConnection):
        """The real connection, plus checks that it received the compiled-module
        adapter and that the private ``_backend`` option was not passed on to
        account setup."""

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            assert self._backend.name == "rust"
            assert "_backend" not in self._setup_kwargs

    make_pipeline = MagicMock(side_effect=AssertionError("unused HTTP pipeline created"))
    monkeypatch.setattr(connection_module, "AsyncPipelineClient", make_pipeline)
    monkeypatch.setattr(async_client, "CosmosClientConnection", CheckedConnection)
    client = async_client.CosmosClient("https://startup.invalid", "ZmFrZQ==", _backend="rust")
    # Replaces connecting to the account during async with, so the test stays offline.
    fake_connect = AsyncMock()
    monkeypatch.setattr(client._adapter, "initialize", fake_connect)

    async def run():
        try:
            if use_with_block:
                async with client:
                    assert "pipeline_client" not in vars(client.client_connection)
        finally:
            await client.close()
            await client.close()

    asyncio.run(run())
    make_pipeline.assert_not_called()
    assert fake_connect.await_count == int(use_with_block)


def test_async_client_startup_does_not_import_aiohttp_rust():
    """aiohttp is the HTTP library the async HTTP pipeline uses. In a new Python
    process, so no earlier test has imported it, this test checks that creating,
    entering and leaving an async client never imports it."""
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
        sdk_python_command(script), capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    "failure", [RuntimeError("startup failed"), asyncio.CancelledError()], ids=["error", "cancelled"]
)
def test_async_startup_failure_closes_client_without_creating_http_pipeline_rust(monkeypatch, failure):
    """If connecting to the account fails or is cancelled during ``async with``,
    the same error reaches the caller, the client is closed, and no HTTP
    pipeline is created."""
    from azure.cosmos.aio import _cosmos_client_connection_async as connection_module

    make_pipeline = MagicMock(side_effect=AssertionError("unused HTTP pipeline created"))
    monkeypatch.setattr(connection_module, "AsyncPipelineClient", make_pipeline)
    client = async_client.CosmosClient("https://startup.invalid", "ZmFrZQ==", _backend="rust")
    monkeypatch.setattr(client._adapter, "initialize", AsyncMock(side_effect=failure))

    async def run():
        with pytest.raises(type(failure)) as caught:
            await client.__aenter__()
        assert caught.value is failure
        assert client._adapter._closing
        assert client.client_connection._routing_map_provider._released

    asyncio.run(run())
    make_pipeline.assert_not_called()


def test_async_http_pipeline_created_on_first_use_and_reused_rust(monkeypatch):
    """The async HTTP pipeline is not created at startup. The first request that
    needs it creates it, the second request reuses it, and closing the client
    closes it."""
    from azure.cosmos.aio import _cosmos_client_connection_async as connection_module

    pipeline = MagicMock()
    pipeline.__aexit__ = AsyncMock()
    make_pipeline = MagicMock(return_value=pipeline)
    send_request = AsyncMock(return_value=({}, {}))
    monkeypatch.setattr(connection_module, "AsyncPipelineClient", make_pipeline)
    monkeypatch.setattr(connection_module.asynchronous_request, "AsynchronousRequest", send_request)
    client = async_client.CosmosClient("https://startup.invalid", "ZmFrZQ==", _backend="rust")
    connection = client.client_connection

    async def run():
        try:
            make_pipeline.assert_not_called()
            # Reading account details is one of the requests that still uses the HTTP pipeline.
            for _ in range(2):
                await connection.GetDatabaseAccount()
            assert connection.pipeline_client is pipeline
            make_pipeline.assert_called_once()
            assert send_request.await_count == 2
            assert send_request.call_args.kwargs["pipeline_client"] is pipeline
        finally:
            await client.close()
        pipeline.__aexit__.assert_awaited_once()

    asyncio.run(run())


def test_async_failed_http_pipeline_creation_is_retried_on_next_use_rust(monkeypatch):
    """If creating the async HTTP pipeline fails, the failure is not remembered.
    The next use tries again and succeeds, and closing the client closes that
    pipeline."""
    from azure.cosmos.aio import _cosmos_client_connection_async as connection_module

    pipeline = MagicMock()
    pipeline.__aexit__ = AsyncMock()
    creation_error = RuntimeError("pipeline creation failed")
    make_pipeline = MagicMock(side_effect=[creation_error, pipeline])
    monkeypatch.setattr(connection_module, "AsyncPipelineClient", make_pipeline)
    client = async_client.CosmosClient("https://startup.invalid", "ZmFrZQ==", _backend="rust")
    try:
        with pytest.raises(RuntimeError) as caught:
            _ = client.client_connection.pipeline_client
        assert caught.value is creation_error
        # The pipeline is saved on the connection only after it is created successfully.
        assert "pipeline_client" not in vars(client.client_connection)
        assert client.client_connection.pipeline_client is pipeline
        assert make_pipeline.call_count == 2
    finally:
        asyncio.run(client.close())
    pipeline.__aexit__.assert_awaited_once()


@pytest.mark.parametrize("async_mode", [False, True], ids=["sync", "async"])
def test_sync_and_async_adapter_factories_pass_every_option_through_rust(monkeypatch, async_mode):
    """The adapter factory is the function the client calls to create its
    adapter. The sync and async factories take the same options, and each
    passes every option unchanged to the shared code that builds the adapter."""
    from azure.cosmos._backend import factory as sync_factory
    from azure.cosmos.aio._backend import factory as async_factory

    factory_module = async_factory if async_mode else sync_factory
    make_adapter = factory_module.make_async_backend if async_mode else factory_module.make_backend
    sync_parameters = inspect.signature(sync_factory.make_backend).parameters
    assert sync_parameters == inspect.signature(async_factory.make_async_backend).parameters
    shared_parameters = inspect.signature(sync_factory._make_backend).parameters
    # The shared builder also takes the adapter class to create, the adapter used
    # when the original pure-Python request path is selected, and whether async
    # credentials are allowed.
    assert set(shared_parameters) == set(sync_parameters) | {
        "rust_backend_type",
        "legacy_backend",
        "allow_async_credential",
    }
    assert shared_parameters["allow_async_credential"].default is False
    # Each option gets its own object, so the test can see it arrive unchanged.
    option_values = {name: object() for name in sync_parameters if name != "explicit"}
    shared_builder = MagicMock(return_value=object())
    monkeypatch.setattr(factory_module, "_make_backend", shared_builder)

    assert make_adapter("rust", **option_values) is shared_builder.return_value
    shared_builder.assert_called_once_with(
        "rust",
        rust_backend_type=factory_module.AsyncBindingAdapter if async_mode else factory_module.BindingAdapter,
        legacy_backend=factory_module.ASYNC_LEGACY_BACKEND if async_mode else factory_module.LEGACY_BACKEND,
        **({"allow_async_credential": True} if async_mode else {}),
        **option_values,
    )


@pytest.mark.parametrize("async_mode", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize(
    "failing_step", [None, "settings", "adapter"], ids=["none-fail", "settings-fail", "adapter-fail"]
)
def test_adapter_factory_passes_credential_through_untouched_rust(monkeypatch, async_mode, failing_step):
    """The adapter factory hands the customer's credential to the adapter as-is.
    It does not ask the credential for a token, close it, or create the token
    helper. This holds when every step succeeds, and when preparing settings or
    creating the adapter fails."""
    from azure.cosmos._backend import factory as sync_factory
    from azure.cosmos._backend._async_credential_bridge import AsyncTokenCredentialBridge
    from azure.cosmos.aio._backend import factory as async_factory

    factory_module = async_factory if async_mode else sync_factory
    make_adapter = factory_module.make_async_backend if async_mode else factory_module.make_backend
    steps_run = []
    credential = SimpleNamespace(
        get_token=AsyncMock() if async_mode else MagicMock(),
        close=AsyncMock() if async_mode else MagicMock(),
    )
    adapter = object()
    step_error = RuntimeError("construction failed")
    create_token_helper = MagicMock(side_effect=AssertionError("factory created a token helper"))
    monkeypatch.setattr(AsyncTokenCredentialBridge, "acquire", create_token_helper)

    def fake_step(name, value):
        def run(*args, **kwargs):
            steps_run.append(name)
            if name == "adapter":
                assert kwargs["master_key"] is None
                assert kwargs["token_credential"] is credential
            if name == failing_step:
                raise step_error
            return value

        return run

    monkeypatch.setattr(sync_factory, "build_client_config", fake_step("settings", PreparedClientConfig()))
    monkeypatch.setattr(
        factory_module, "AsyncBindingAdapter" if async_mode else "BindingAdapter", fake_step("adapter", adapter)
    )
    if failing_step is None:
        assert make_adapter("rust", url="https://startup.invalid", credential=credential) is adapter
        assert steps_run == ["settings", "adapter"]
    else:
        with pytest.raises(RuntimeError) as caught:
            make_adapter("rust", url="https://startup.invalid", credential=credential)
        assert caught.value is step_error
        all_steps = ["settings", "adapter"]
        assert steps_run == all_steps[: all_steps.index(failing_step) + 1]
    create_token_helper.assert_not_called()
    credential.get_token.assert_not_called()
    credential.close.assert_not_called()


@pytest.mark.parametrize("value", [-1, True, 1.5, "3", 2**32])
@pytest.mark.parametrize("in_connection_policy", [False, True], ids=["direct", "in-connection-policy"])
def test_invalid_retry_count_rejected_before_client_is_built_rust(module, value, in_connection_policy):
    """A retry count must be a whole number from 0 to 2**32 - 1.

    Five bad values are rejected: negative, True, a fraction, text, and a
    number that is too large. True is included because Python treats it as 1,
    so a check that only asked for a whole number would accept it.

    Each value is given two ways, directly as ``retry_throttle_total`` and
    inside a ``ConnectionPolicy``, because customers set retries both ways. The
    client's connection object is never created.
    """
    client_options = {"retry_throttle_total": value}
    if in_connection_policy:
        policy = ConnectionPolicy()
        policy.RetryOptions = RetryOptions(max_retry_attempt_count=value)
        client_options = {"connection_policy": policy}
    with pytest.raises(ValueError, match="retry_throttle_total"):
        module.CosmosClient("https://startup.invalid", "ZmFrZQ==", _backend="rust", **client_options)
    module.CosmosClientConnection.assert_not_called()


@pytest.mark.parametrize("option_name", ["preferred_locations", "excluded_locations"])
@pytest.mark.parametrize("value", [[123], [None], [True], [" "], {"West US": 1}, False])
def test_invalid_region_list_rejected_before_client_is_built_rust(module, option_name, value):
    """``preferred_locations`` and ``excluded_locations`` must be lists of
    non-blank region names.

    A list holding a number, None, True or a blank name is rejected, and so are
    a dict and False. The error names the option, and the client's connection
    object is never created. Only the shape is checked, not whether the region
    exists.
    """
    with pytest.raises(ValueError, match=option_name):
        module.CosmosClient("https://startup.invalid", "ZmFrZQ==", _backend="rust", **{option_name: value})
    module.CosmosClientConnection.assert_not_called()


@pytest.mark.parametrize("value", [-1, True, "30", float("nan"), float("inf"), 2**64 - 1, 2**64])
def test_invalid_throttle_retry_wait_rejected_rust(value):
    """``throttle_retry_wait_threshold_seconds`` is the most total time the
    client waits across all retries of a throttled (HTTP 429) request.

    Negative values, True, text, NaN, infinity and numbers of 2**64 or more are
    rejected while the client options are prepared. 2**64 - 1 is rejected too,
    because converting it to a float rounds it up to 2**64.
    """
    with pytest.raises(ValueError, match="throttle_retry_wait_threshold_seconds"):
        build_client_config(None, throttling_max_retry_wait_time_seconds=value)


@pytest.mark.parametrize("failing_step", ["compact-writes-option", "credential", "connection-policy", "connection"])
def test_client_construction_failure_closes_adapter_without_opening_handle_rust(module, monkeypatch, failing_step):
    """If building the client fails after its adapter is created, the adapter is
    closed. No handle is opened or released, because the adapter never connected.

    Four failure points are covered: an invalid ``enable_compact_utf8_item_writes``
    value, and errors while reading the credential, building the connection
    policy, and creating the connection object.
    """
    # Stands in for the compiled module, so a real handle can't be opened.
    fake_module = SimpleNamespace(acquire_driver_handle=MagicMock(), release_driver_handle=MagicMock())
    monkeypatch.setattr(sync_adapter_module if module is sync_client else async_adapter_module, "_rust_module", fake_module)
    factory_name = "make_backend" if module is sync_client else "make_async_backend"
    real_make_adapter = getattr(module, factory_name)
    created_adapters = []

    def record_adapter(*args, **kwargs):
        adapter = real_make_adapter(*args, **kwargs)
        created_adapters.append(adapter)
        return adapter

    monkeypatch.setattr(module, factory_name, record_adapter)
    client_options = {"timeout": 25}
    step_error = RuntimeError("startup failed")
    if failing_step == "compact-writes-option":
        client_options["enable_compact_utf8_item_writes"] = "invalid"
        expected_error_type = TypeError
    else:
        failing_function = {"credential": "_build_auth", "connection-policy": "_build_connection_policy",
                            "connection": "CosmosClientConnection"}[failing_step]
        monkeypatch.setattr(module, failing_function, MagicMock(side_effect=step_error))
        expected_error_type = RuntimeError
    try:
        with pytest.raises(expected_error_type) as raised:
            module.CosmosClient("https://startup.invalid", "ZmFrZQ==", _backend="rust", **client_options)
        if failing_step == "compact-writes-option":
            assert str(raised.value) == "enable_compact_utf8_item_writes must be a bool."
        else:
            assert raised.value is step_error
        assert len(created_adapters) == 1
        assert created_adapters[0]._closing
        assert created_adapters[0]._driver_handle is None
    finally:
        for adapter in created_adapters:
            close_adapter(adapter)
    fake_module.acquire_driver_handle.assert_not_called()
    fake_module.release_driver_handle.assert_not_called()


@pytest.mark.parametrize("client_module", [sync_client, async_client], ids=["sync", "async"])
def test_construction_error_reaches_caller_when_adapter_cleanup_also_fails_rust(client_module, monkeypatch, caplog):
    """If building the client fails and cleaning up the adapter afterwards also
    fails, the caller still gets the original error. The cleanup error is logged
    as a warning."""
    fake_module = SimpleNamespace(acquire_driver_handle=MagicMock(), release_driver_handle=MagicMock())
    monkeypatch.setattr(
        sync_adapter_module if client_module is sync_client else async_adapter_module, "_rust_module", fake_module
    )
    monkeypatch.setattr(client_module, "CosmosClientConnection", MagicMock())
    startup_error = RuntimeError("client construction failed")
    cleanup_error = RuntimeError("construction cleanup failed")
    failing_cleanup = MagicMock(side_effect=cleanup_error)
    adapter_class = (
        sync_adapter_module.BindingAdapter if client_module is sync_client else async_adapter_module.AsyncBindingAdapter
    )
    monkeypatch.setattr(adapter_class, "abort_construction", failing_cleanup)
    monkeypatch.setattr(client_module, "_build_auth", MagicMock(side_effect=startup_error))

    with caplog.at_level(logging.WARNING, logger="azure.cosmos._client_lifecycle"):
        with pytest.raises(RuntimeError) as raised:
            client_module.CosmosClient("https://startup.invalid", "ZmFrZQ==", _backend="rust")

    assert raised.value is startup_error
    failing_cleanup.assert_called_once_with()
    cleanup_records = [
        record for record in caplog.records
        if record.name == "azure.cosmos._client_lifecycle" and record.levelno == logging.WARNING
    ]
    assert len(cleanup_records) == 1
    assert cleanup_records[0].getMessage() == "Failed to release resources after client startup failure"
    assert cleanup_records[0].exc_info[1] is cleanup_error
    fake_module.acquire_driver_handle.assert_not_called()
    fake_module.release_driver_handle.assert_not_called()


def test_closing_adapter_does_not_recheck_settings_rust(monkeypatch):
    """Each new adapter asks the compiled module to check its settings once, when
    the adapter is created. Closing an adapter does not run that check again, so
    closing can't fail because of it."""
    check_settings = MagicMock()
    monkeypatch.setattr("azure.cosmos._rust._validate_runtime_configuration", check_settings)
    first_adapter = sync_adapter_module.BindingAdapter(
        "https://first.invalid", master_key="key",
        client_config=PreparedClientConfig(operation_timeout_seconds=20),
    )
    second_adapter = sync_adapter_module.BindingAdapter(
        "https://other.invalid", master_key="key",
        client_config=PreparedClientConfig(operation_timeout_seconds=30),
    )
    assert check_settings.call_count == 2
    check_settings.reset_mock()
    check_settings.side_effect = ValueError("must not check settings during close")
    first_adapter.close()
    second_adapter.close()
    check_settings.assert_not_called()


def test_close_while_connecting_releases_handle_when_it_arrives_rust(monkeypatch):
    """If the client is closed while it is still connecting, the handle is
    released as soon as it arrives and is never used. The waiting caller gets a
    'closed during initialization' error."""
    connect_started, let_connect_finish = threading.Event(), threading.Event()

    def slow_open_handle(*args):
        connect_started.set()
        assert let_connect_finish.wait(10)
        return "test-handle"

    fake_module = SimpleNamespace(acquire_driver_handle=slow_open_handle, release_driver_handle=MagicMock())
    monkeypatch.setattr(async_adapter_module, "_rust_module", fake_module)
    adapter = async_adapter_module.AsyncBindingAdapter(
        "https://account.invalid", master_key="key",
        client_config=PreparedClientConfig(operation_timeout_seconds=30),
    )
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as thread_pool:
        connect_result = thread_pool.submit(lambda: asyncio.run(adapter._ensure_driver_handle()))
        try:
            assert connect_started.wait(10)
            close_adapter(adapter)
            # A new client for the same account can be created and closed while
            # the first one is still connecting.
            new_adapter = sync_adapter_module.BindingAdapter(
                "https://account.invalid", master_key="key",
                client_config=PreparedClientConfig(operation_timeout_seconds=20),
            )
            new_adapter.close()
        finally:
            let_connect_finish.set()
        with pytest.raises(RuntimeError, match="closed during initialization"):
            connect_result.result(timeout=10)
    fake_module.release_driver_handle.assert_called_once_with("test-handle")


def test_new_adapter_still_checks_settings_after_failed_connect_rust(monkeypatch):
    """After a client fails to connect and is closed, each new adapter still asks
    the compiled module to check its settings, and an error from that check
    reaches the caller."""
    check_settings = MagicMock()
    monkeypatch.setattr("azure.cosmos._rust._validate_runtime_configuration", check_settings)
    connect_error = RuntimeError("connect failed")

    def failing_open_handle(*args):
        check_settings.side_effect = ValueError("runtime settings already initialized")
        raise connect_error

    monkeypatch.setattr(
        sync_adapter_module,
        "_rust_module",
        SimpleNamespace(
            # The adapter looks up these two error types on the compiled module.
            _DriverResponseError=type("_DriverResponseError", (RuntimeError,), {}),
            _DriverTransportError=type("_DriverTransportError", (RuntimeError,), {}),
            acquire_driver_handle=failing_open_handle,
        ),
    )
    adapter = sync_adapter_module.BindingAdapter("https://account.invalid", master_key="key")
    with pytest.raises(RuntimeError, match="connect failed") as raised:
        adapter._ensure_driver_handle()
    assert raised.value is connect_error
    adapter.close()
    for settings in (
        SimpleNamespace(proxy_allowed=True),
        SimpleNamespace(connection_timeout_seconds=3),
    ):
        with pytest.raises(ValueError, match="runtime settings already initialized"):
            sync_adapter_module.BindingAdapter("https://other.invalid", master_key="key", client_config=settings)


class FakeAsyncCredential:
    """An async credential that returns a fixed token without contacting anything.

    The token does not expire during the test, so nothing tries to refresh it.
    """

    async def get_token(self, *args, **kwargs):
        """Return a fixed fake token."""
        return AccessToken("test-token", 9999999999)


def test_failed_client_does_not_close_token_helper_shared_with_another_client_rust(monkeypatch):
    """Clients that use the same async credential share one token helper. If a
    second client fails while it is being built, the first client's token helper
    stays open and still works. It closes only when the first client closes, and
    closing it does not stop the event loop."""
    credential = FakeAsyncCredential()
    first_client = async_client.CosmosClient("https://first.invalid", credential, _backend="rust")
    failed_adapters = []
    real_make_adapter = async_client.make_async_backend

    def record_adapter(*args, **kwargs):
        adapter = real_make_adapter(*args, **kwargs)
        failed_adapters.append(adapter)
        return adapter

    monkeypatch.setattr(
        async_adapter_module,
        "_rust_module",
        SimpleNamespace(
            acquire_driver_handle=MagicMock(return_value=object()),
            release_driver_handle=MagicMock(),
        ),
    )

    async def run():
        try:
            await first_client._adapter.initialize()
            token_helper = first_client._adapter._token_credential
            token = await asyncio.wrap_future(token_helper._start_token_request("test-scope"))
            assert token.token == "test-token"
            monkeypatch.setattr(async_client, "make_async_backend", record_adapter)
            startup_error = RuntimeError("startup")
            monkeypatch.setattr(async_client, "CosmosClientConnection", MagicMock(side_effect=startup_error))
            with pytest.raises(RuntimeError, match="startup") as raised:
                async_client.CosmosClient("https://second.invalid", credential, _backend="rust")
            assert raised.value is startup_error
            assert len(failed_adapters) == 1
            # _refcount is the number of clients using this token helper.
            assert token_helper._refcount == 1 and not token_helper._closed
            assert failed_adapters[0]._token_credential is None
            await failed_adapters[0].close()
            assert token_helper._refcount == 1 and not token_helper._closed
        finally:
            for adapter in failed_adapters:
                await adapter.close()
            await first_client.close()
        assert token_helper._closed
        assert asyncio.get_running_loop().is_running()

    asyncio.run(run())


@pytest.mark.parametrize("cancelled", [False, True])
@pytest.mark.parametrize("pipeline_close_fails", [False, True])
def test_async_startup_failure_closes_all_resources_rust(
    monkeypatch, caplog, cancelled, pipeline_close_fails
):
    """If connecting fails or is cancelled while ``async with`` starts the client,
    the client cleans up everything it created.

    It closes the adapter and the HTTP pipeline, stops the account refresh task,
    and gives back its share of the partition-map cache. If closing the HTTP
    pipeline also fails, that error is logged as a warning and the caller still
    gets the original error. The code inside the ``async with`` block never runs.
    """
    startup_error = asyncio.CancelledError() if cancelled else RuntimeError("connect failed")
    pipeline_close_error = RuntimeError("pipeline close failed")
    connection = SimpleNamespace(
        pipeline_client=SimpleNamespace(
            __aenter__=AsyncMock(),
            __aexit__=AsyncMock(side_effect=pipeline_close_error if pipeline_close_fails else None),
        ),
        _setup=AsyncMock(),
        _global_endpoint_manager=SimpleNamespace(close=AsyncMock()),
        _routing_map_provider=SimpleNamespace(release=MagicMock()),
    )
    connection._close_pipeline = connection.pipeline_client.__aexit__
    monkeypatch.setattr(async_client, "CosmosClientConnection", MagicMock(return_value=connection))
    client = async_client.CosmosClient(
        "https://account.invalid", "ZmFrZQ==", _backend="rust"
    )
    monkeypatch.setattr(client._adapter, "initialize", AsyncMock(side_effect=startup_error))
    adapter_close = AsyncMock(wraps=client._adapter.close)
    monkeypatch.setattr(client._adapter, "close", adapter_close)

    async def run():
        with pytest.raises(type(startup_error)) as caught:
            async with client:
                pytest.fail("Customer block must not run after failed startup")
        assert caught.value is startup_error

    with caplog.at_level(logging.WARNING, logger=async_client.__name__):
        asyncio.run(run())
    cleanup_records = [
        record for record in caplog.records
        if record.name == async_client.__name__
        and record.getMessage() == "Failed cleanup after async client entry"
    ]
    assert len(cleanup_records) == int(pipeline_close_fails)
    if pipeline_close_fails:
        assert cleanup_records[0].levelno == logging.WARNING
        assert cleanup_records[0].exc_info[1] is pipeline_close_error
    connection.pipeline_client.__aexit__.assert_awaited_once()
    connection._global_endpoint_manager.close.assert_awaited_once()
    connection._routing_map_provider.release.assert_called_once()
    adapter_close.assert_awaited_once()
    assert client._adapter._closing
    connection._setup.assert_not_awaited()
    connection.pipeline_client.__aenter__.assert_not_awaited()


@pytest.fixture
def async_client_setup(monkeypatch):
    """Async client that uses a fake compiled module.

    Connecting returns the handle ``"startup-handle"``, and reading an item
    returns item ``order-42``.
    """
    connection = SimpleNamespace(
        url_connection="https://startup.invalid",
        pipeline_client=SimpleNamespace(__aenter__=AsyncMock(), __aexit__=AsyncMock()),
        _setup=AsyncMock(),
        _global_endpoint_manager=SimpleNamespace(close=AsyncMock()),
        _routing_map_provider=SimpleNamespace(release=MagicMock()),
    )
    connection._close_pipeline = connection.pipeline_client.__aexit__
    fake_module = SimpleNamespace(
        _DriverResponseError=type("_DriverResponseError", (RuntimeError,), {}),
        _DriverTransportError=type("_DriverTransportError", (RuntimeError,), {}),
        acquire_driver_handle=MagicMock(return_value="startup-handle"),
        release_driver_handle=MagicMock(),
        read_item_async=AsyncMock(return_value=(200, 0, {}, b'{"id":"order-42"}')),
    )
    monkeypatch.setattr(async_adapter_module, "_rust_module", fake_module)
    monkeypatch.setattr(async_client, "CosmosClientConnection", MagicMock(return_value=connection))
    client = async_client.CosmosClient("https://startup.invalid", "ZmFrZQ==", _backend="rust")
    yield SimpleNamespace(client=client, connection=connection, fake_module=fake_module)
    asyncio.run(client.close())


def test_async_with_waits_for_connect_and_reads_reuse_the_handle_rust(async_client_setup):
    """Entering ``async with`` waits until the client has connected and has a handle.

    A second connect started meanwhile waits for the same handle instead of
    opening another. The client connects to the account only once, later reads
    use that handle, and closing the client releases it.
    """
    setup = async_client_setup
    connect_started, let_connect_finish = threading.Event(), threading.Event()

    def slow_open_handle(*args):
        setup.connection.pipeline_client.__aenter__.assert_not_awaited()
        connect_started.set()
        assert let_connect_finish.wait(5)
        return "startup-handle"

    setup.fake_module.acquire_driver_handle.side_effect = slow_open_handle
    setup.fake_module.acquire_driver_handle.assert_not_called()

    async def run():
        enter_task = asyncio.create_task(setup.client.__aenter__())
        second_connect = None
        try:
            assert await asyncio.to_thread(connect_started.wait, 2)
            assert not enter_task.done()
            setup.fake_module.read_item_async.assert_not_called()
            second_connect = asyncio.create_task(setup.client._adapter.initialize())
            await asyncio.sleep(0)
            assert not second_connect.done()
            let_connect_finish.set()
            assert await asyncio.wait_for(enter_task, 5) is setup.client
            await asyncio.wait_for(second_connect, 5)
            assert setup.client._adapter._driver_handle == "startup-handle"
            await asyncio.gather(*(setup.client._adapter.initialize() for _ in range(3)))
            container = setup.client.get_database_client("sales").get_container_client("orders")
            assert (await container.read_item("order-42", partition_key="order-42"))["id"] == "order-42"
            setup.fake_module.read_item_async.assert_awaited_once()
            assert setup.fake_module.read_item_async.call_args.args[0] == "startup-handle"
            setup.fake_module.acquire_driver_handle.assert_called_once()
            setup.connection._setup.assert_not_awaited()
        finally:
            let_connect_finish.set()
            await setup.client.close()
            await asyncio.gather(enter_task, return_exceptions=True)
            if second_connect is not None:
                await asyncio.gather(second_connect, return_exceptions=True)

    asyncio.run(run())
    setup.fake_module.release_driver_handle.assert_called_once_with("startup-handle")


def test_async_connect_failure_stops_async_with_and_cleans_up_rust(async_client_setup):
    """If connecting fails, the caller gets the error, the code inside
    ``async with`` never runs, and the client cleans up.

    No handle was opened, so none is released.
    """
    setup = async_client_setup
    connect_error = RuntimeError("account connect failed")
    setup.fake_module.acquire_driver_handle.side_effect = connect_error

    async def run():
        with pytest.raises(RuntimeError) as caught:
            async with setup.client:
                pytest.fail("Customer block must not run after failed connect")
        assert caught.value is connect_error

    asyncio.run(run())
    assert setup.client._adapter._closing
    setup.connection.pipeline_client.__aexit__.assert_awaited_once()
    setup.connection._global_endpoint_manager.close.assert_awaited_once()
    setup.connection._routing_map_provider.release.assert_called_once()
    setup.connection._setup.assert_not_awaited()
    setup.fake_module.read_item_async.assert_not_called()
    setup.fake_module.release_driver_handle.assert_not_called()


def test_cancelled_async_with_releases_handle_that_arrives_later_rust(async_client_setup):
    """If ``async with`` is cancelled while the client is connecting, the client
    closes straight away.

    The connect keeps running in the background. When its handle arrives, the
    client releases it and raises "closed during initialization".
    """
    setup = async_client_setup
    connect_started, let_connect_finish = threading.Event(), threading.Event()
    connect_threads = []

    def slow_open_handle(*args):
        connect_threads.append(threading.current_thread())
        connect_started.set()
        assert let_connect_finish.wait(5), "test did not let the connect finish"
        return "late-startup-handle"

    setup.fake_module.acquire_driver_handle.side_effect = slow_open_handle

    async def run():
        enter_task = asyncio.create_task(setup.client.__aenter__())
        connect_result = None
        try:
            assert await asyncio.to_thread(connect_started.wait, 2)
            connect_result = setup.client._adapter._init_future
            assert connect_result is not None and not connect_result.done()
            enter_task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await asyncio.wait_for(enter_task, 2)
            assert setup.client._adapter._closing
            assert setup.client._adapter._driver_handle is None
            assert not connect_result.cancelled()
            setup.fake_module.release_driver_handle.assert_not_called()
            setup.connection.pipeline_client.__aexit__.assert_awaited_once()
            setup.connection._global_endpoint_manager.close.assert_awaited_once()
            setup.connection._routing_map_provider.release.assert_called_once()
            let_connect_finish.set()
            with pytest.raises(RuntimeError, match="closed during initialization"):
                await asyncio.wait_for(asyncio.wrap_future(connect_result), 5)
            assert setup.client._adapter._driver_handle is None
        finally:
            let_connect_finish.set()
            await setup.client.close()
            await asyncio.gather(enter_task, return_exceptions=True)
            if connect_result is not None:
                await asyncio.wait_for(
                    asyncio.gather(asyncio.wrap_future(connect_result), return_exceptions=True), 5
                )

    try:
        asyncio.run(run())
    finally:
        # Let the connect thread finish before the fake module is removed, even if an assertion fails.
        let_connect_finish.set()
        for thread in connect_threads:
            thread.join(timeout=5)
        assert all(not thread.is_alive() for thread in connect_threads)
    setup.fake_module.acquire_driver_handle.assert_called_once()
    setup.fake_module.release_driver_handle.assert_called_once_with("late-startup-handle")
    setup.fake_module.read_item_async.assert_not_called()
    setup.connection._setup.assert_not_awaited()


def test_client_priority_defaults_are_captured_rust(module):
    """Priority and throughput bucket set on the client become the defaults for
    its item requests.

    If they were dropped, requests would still succeed, just without the
    priority or bucket the customer set. That is easy to miss, so this test
    checks they are stored.
    """
    client = module.CosmosClient(
        "https://account.invalid", "ZmFrZQ==", _backend="rust", priority="Low", throughput_bucket=3
    )
    assert client._client_context.defaults.priority == "Low"
    assert client._client_context.defaults.throughput_bucket == 3
    close_adapter(client._adapter)


def test_client_database_and_container_share_one_adapter_rust(module):
    """The client, its connection, and the database and container clients made
    from it all use the same adapter."""
    client = module.CosmosClient(
        "https://account.invalid", "ZmFrZQ==", _backend="rust"
    )
    try:
        context = client._client_context
        assert context.adapter is client._adapter
        assert client.client_connection._backend is client._adapter

        database = client.get_database_client("sales")
        container = database.get_container_client("orders")
        assert database._client_context is context
        assert container._client_context is context
        assert container._client_context.adapter is client._adapter
    finally:
        close_adapter(client._adapter)


def test_checking_client_settings_does_not_build_default_runtime_rust():
    """A runtime (``CosmosRuntime``) holds the connection settings that clients share.

    If the customer does not pass one, the SDK builds a default runtime when a
    client first connects. Checking client settings must not build it early.
    The check runs in a new Python process, so no earlier test has already
    built the default runtime.
    """
    code = """
from azure.cosmos import _rust
from azure.cosmos._backend.contracts import PreparedClientConfig
# _runtime_configuration() returns None until the default runtime is built.
assert _rust._runtime_configuration() is None
for config in (
    None,
    PreparedClientConfig(operation_timeout_seconds=2),
    PreparedClientConfig(operation_timeout_seconds=5),
):
    assert _rust._validate_runtime_configuration(config) is None
    assert _rust._runtime_configuration() is None
"""
    result = subprocess.run(
        sdk_python_command(code), capture_output=True, text=True, timeout=30, check=False
    )
    assert result.returncode == 0, result.stdout + result.stderr
