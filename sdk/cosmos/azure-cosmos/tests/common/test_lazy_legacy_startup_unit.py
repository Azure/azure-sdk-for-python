# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Offline checks of lazy legacy account setup with the real connection classes."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos import _cosmos_client_connection as sync_connection
from azure.cosmos import cosmos_client as sync_client
from azure.cosmos.aio import _cosmos_client as async_client
from azure.cosmos.aio import _cosmos_client_connection_async as async_connection
from azure.cosmos._backend.legacy import LEGACY_BACKEND
from azure.cosmos.aio._backend.legacy import ASYNC_LEGACY_BACKEND
from azure.cosmos.documents import DatabaseAccount
from common.test_connection_free_items_unit import Backend, AsyncBackend


def make_client(monkeypatch, async_mode, backend_name="rust", consistency=None):
    account = DatabaseAccount()
    account.ConsistencyPolicy = {"defaultConsistencyLevel": "Session"}
    call = AsyncMock if async_mode else MagicMock
    manager = MagicMock()
    manager._GetDatabaseAccount = call(return_value=account)
    manager.force_refresh_on_startup = call()
    manager.close = call()
    pipeline = MagicMock()
    if async_mode:
        pipeline.__aenter__ = AsyncMock()
        pipeline.__aexit__ = AsyncMock()
    module = async_connection if async_mode else sync_connection
    client_module = async_client if async_mode else sync_client
    manager_name = "_GlobalPartitionEndpointManagerForPerPartitionAutomaticFailover"
    if async_mode:
        manager_name += "Async"
    monkeypatch.setattr(module, manager_name, MagicMock(return_value=manager))
    monkeypatch.setattr(
        module, "AsyncPipelineClient" if async_mode else "PipelineClient",
        MagicMock(return_value=pipeline),
    )
    if backend_name == "rust":
        backend = AsyncBackend() if async_mode else Backend()
        backend.name = "rust"
    else:
        backend = ASYNC_LEGACY_BACKEND if async_mode else LEGACY_BACKEND
    monkeypatch.setattr(
        client_module, "make_async_backend" if async_mode else "make_backend",
        MagicMock(return_value=backend),
    )
    client = client_module.CosmosClient(
        "https://lazy-startup.invalid", "ZmFrZQ==",
        _backend=backend_name, consistency_level=consistency,
    )
    return SimpleNamespace(client=client, connection=client.client_connection,
                           manager=manager, pipeline=pipeline, account=account)


@pytest.mark.parametrize("async_mode", [False, True])
def test_rust_startup_and_item_read_do_not_initialize_legacy(monkeypatch, async_mode):
    env = make_client(monkeypatch, async_mode)
    container = env.client.get_database_client("sales").get_container_client("orders")

    async def run():
        async with env.client:
            assert (await container.read_item("x", partition_key="p"))["id"] == "x"

    if async_mode:
        asyncio.run(run())
    else:
        with env.client:
            assert container.read_item("x", partition_key="p")["id"] == "x"
    env.manager._GetDatabaseAccount.assert_not_called()
    env.manager.force_refresh_on_startup.assert_not_called()
    assert not env.connection._setup_complete
    assert env.connection.session is None


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("backend_name", ["core-python", "rust"])
@pytest.mark.parametrize("consistency", [None, "Eventual"])
def test_first_legacy_read_initializes_state_and_later_reads_reuse_it(
    monkeypatch, async_mode, backend_name, consistency,
):
    env = make_client(monkeypatch, async_mode, backend_name, consistency)
    expected_consistency = consistency or "Session"
    sessions = []

    def send(path, request, headers, **kwargs):
        assert env.connection._setup_complete
        assert headers["x-ms-consistency-level"] == expected_consistency
        sessions.append(env.connection.session)
        return {"id": "offer"}, CaseInsensitiveDict()

    transport = AsyncMock(side_effect=send) if async_mode else MagicMock(side_effect=send)
    monkeypatch.setattr(env.connection, "_CosmosClientConnection__Get", transport)
    if backend_name == "rust":
        env.manager._GetDatabaseAccount.assert_not_called()

    async def run():
        async with env.client:
            assert env.manager._GetDatabaseAccount.call_count == (backend_name == "core-python")
            for _ in range(2):
                assert (await env.connection.Read("offers/id/", "offers", "id", None))["id"] == "offer"

    if async_mode:
        asyncio.run(run())
    else:
        with env.client:
            for _ in range(2):
                assert env.connection.Read("offers/id/", "offers", "id", None)["id"] == "offer"
    env.manager._GetDatabaseAccount.assert_called_once()
    env.manager.force_refresh_on_startup.assert_called_once_with(env.account)
    assert sessions[0] is sessions[1]
    assert (sessions[0] is not None) == (expected_consistency == "Session")


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("override", [None, "Eventual"])
def test_first_legacy_request_merges_setup_defaults_without_changing_caller_headers(
    monkeypatch, async_mode, override,
):
    env = make_client(monkeypatch, async_mode)
    initial_headers = {"x-example": "retained"}
    if override:
        initial_headers["x-ms-consistency-level"] = override
    original = initial_headers.copy()

    def send(path, request, headers, **kwargs):
        assert env.connection.session is not None
        assert headers["x-ms-consistency-level"] == (override or "Session")
        assert headers["x-example"] == "retained"
        return {"id": "offer"}, CaseInsensitiveDict()

    transport = AsyncMock(side_effect=send) if async_mode else MagicMock(side_effect=send)
    monkeypatch.setattr(env.connection, "_CosmosClientConnection__Get", transport)

    async def run():
        async with env.client:
            await env.connection.Read("offers/id", "offers", "id", initial_headers)

    if async_mode:
        asyncio.run(run())
    else:
        with env.client:
            env.connection.Read("offers/id", "offers", "id", initial_headers)
    assert initial_headers == original
    transport.assert_called_once()


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("query", [False, True])
@pytest.mark.parametrize("override", [None, "Eventual"])
def test_legacy_feed_setup_precedes_header_and_session_preparation(
    monkeypatch, async_mode, query, override,
):
    env = make_client(monkeypatch, async_mode)
    initial_headers = {"x-example": "retained"}
    if override:
        initial_headers["x-ms-consistency-level"] = override
    seen = []

    def send(*args, **kwargs):
        headers = args[-1]
        assert env.connection._setup_complete
        assert env.connection.session is not None
        assert headers["x-ms-consistency-level"] == (override or "Session")
        assert headers["x-example"] == "retained"
        seen.append(headers)
        return {"Offers": []}, CaseInsensitiveDict()

    transport = AsyncMock(side_effect=send) if async_mode else MagicMock(side_effect=send)
    monkeypatch.setattr(
        env.connection, "_CosmosClientConnection__Post" if query else "_CosmosClientConnection__Get",
        transport,
    )

    def feed():
        options = {"initialHeaders": initial_headers}
        return env.connection.QueryOffers("SELECT * FROM c" if query else None, options=options)

    async def run():
        async with env.client:
            for _ in range(2):
                assert [item async for item in feed()] == []

    if async_mode:
        asyncio.run(run())
    else:
        with env.client:
            for _ in range(2):
                assert list(feed()) == []
    assert len(seen) == 2
    env.manager._GetDatabaseAccount.assert_called_once()


@pytest.mark.parametrize("async_mode", [False, True])
def test_permitted_fallback_initializes_legacy_before_dispatch(monkeypatch, async_mode):
    from azure.cosmos._backend.capabilities import OperationRouting
    from azure.cosmos._backend.operations import OP_READ_OFFER
    from azure.cosmos._backend.cosmos_backend import CosmosBackend
    from azure.cosmos.aio._backend.cosmos_backend import AsyncCosmosBackend

    env = make_client(monkeypatch, async_mode)

    def send(path, request, headers, **kwargs):
        assert env.connection._setup_complete
        assert headers["x-ms-consistency-level"] == "Session"
        return {"id": "offer"}, CaseInsensitiveDict()

    transport = AsyncMock(side_effect=send) if async_mode else MagicMock(side_effect=send)
    monkeypatch.setattr(env.connection, "_CosmosClientConnection__Get", transport)
    options = dict(
        routing=OperationRouting(OP_READ_OFFER, supported=False),
        build_request=MagicMock(side_effect=AssertionError("must select the permitted fallback")),
        process_response=MagicMock(side_effect=AssertionError("must keep legacy response processing")),
        legacy_call=lambda: env.connection.Read("offers/id", "offers", "id", None),
    )

    async def run():
        async with env.client:
            result = await AsyncCosmosBackend.run_operation(env.client._backend, **options)
            assert result["id"] == "offer"

    if async_mode:
        asyncio.run(run())
    else:
        with env.client:
            assert CosmosBackend.run_operation(env.client._backend, **options)["id"] == "offer"
    env.manager._GetDatabaseAccount.assert_called_once()


@pytest.mark.parametrize("async_mode", [False, True])
def test_concurrent_legacy_initialization_is_shared(monkeypatch, async_mode):
    env = make_client(monkeypatch, async_mode)

    async def run():
        started, finish = asyncio.Event(), asyncio.Event()

        async def fetch(**kwargs):
            started.set()
            await finish.wait()
            return env.account

        env.manager._GetDatabaseAccount.side_effect = fetch
        tasks = [asyncio.create_task(env.connection._setup()) for _ in range(4)]
        await asyncio.wait_for(started.wait(), timeout=5)
        finish.set()
        try:
            await asyncio.wait_for(asyncio.gather(*tasks), timeout=5)
        finally:
            await env.client.close()

    if async_mode:
        asyncio.run(run())
    else:
        import threading
        started, finish = threading.Event(), threading.Event()

        def fetch(**kwargs):
            started.set()
            assert finish.wait(5)
            return env.account

        env.manager._GetDatabaseAccount.side_effect = fetch
        try:
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(env.connection._setup) for _ in range(4)]
                assert started.wait(5)
                finish.set()
                for future in futures:
                    future.result(timeout=5)
        finally:
            finish.set()
            env.client.close()
    env.manager._GetDatabaseAccount.assert_called_once()
    env.manager.force_refresh_on_startup.assert_called_once()
    assert env.connection._setup_complete


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("stage", ["account", "refresh"])
def test_failed_setup_is_not_published_and_can_be_retried(monkeypatch, async_mode, stage):
    env = make_client(monkeypatch, async_mode)
    call = env.manager._GetDatabaseAccount if stage == "account" else env.manager.force_refresh_on_startup
    call.side_effect = [RuntimeError("setup failed"), env.account if stage == "account" else None]

    async def run():
        try:
            with pytest.raises(RuntimeError, match="setup failed"):
                await env.connection._setup()
            assert not env.connection._setup_complete
            assert "database_account" not in env.connection._setup_kwargs
            await env.connection._setup()
        finally:
            await env.client.close()

    if async_mode:
        asyncio.run(run())
    else:
        try:
            with pytest.raises(RuntimeError, match="setup failed"):
                env.connection._setup()
            assert not env.connection._setup_complete
            env.connection._setup()
        finally:
            env.client.close()
    assert env.connection._setup_complete
    assert env.manager._GetDatabaseAccount.call_count == 2


def test_cancelled_legacy_setup_can_be_retried(monkeypatch):
    env = make_client(monkeypatch, True)
    env.manager.force_refresh_on_startup.side_effect = [asyncio.CancelledError(), None]

    async def run():
        try:
            with pytest.raises(asyncio.CancelledError):
                await env.connection._setup()
            assert not env.connection._setup_complete
            assert "database_account" not in env.connection._setup_kwargs
            await env.connection._setup()
        finally:
            await env.client.close()

    asyncio.run(run())
    assert env.connection._setup_complete
    assert env.manager._GetDatabaseAccount.call_count == 2
