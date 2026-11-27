# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Durable credential and read-target checks, independent of migration tooling."""

import asyncio
import inspect
from unittest.mock import AsyncMock, MagicMock, call

import pytest

from config import clients
from read_container import _container_setup as setup


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("auth", ["key", "aad"])
def test_read_fixture_uses_configured_rust_data_credential_rust(monkeypatch, asynchronous, auth):
    credential = object()
    monkeypatch.setattr(clients.TestSettings, "host", "https://read-fixture.invalid")
    monkeypatch.setattr(clients.TestSettings, "masterKey", "unit-test-key")
    monkeypatch.setattr(clients.TestSettings, "data_auth_mode", auth)
    monkeypatch.setattr(clients.TestSettings, "is_emulator", False)
    credential_factory = MagicMock(return_value=credential)
    monkeypatch.setattr(clients, "_aad_credential", credential_factory)
    key, data = (AsyncMock(), AsyncMock()) if asynchronous else (MagicMock(), MagicMock())
    key_db = key.create_database.return_value
    key_db.database_link = "dbs/owned"
    data_db = MagicMock()
    data.get_database_client = MagicMock(return_value=data_db)
    proxy = setup.AsyncContainerProxy if asynchronous else setup.ContainerProxy
    data_container = proxy(data.client_connection, "dbs/owned", "orders")
    data_db.get_container_client.return_value = data_container
    constructor = MagicMock(side_effect=[key, data])
    monkeypatch.setattr(clients, "AsyncCosmosClient" if asynchronous else "CosmosClient", constructor)
    read = AsyncMock(return_value={"id": "orders"}) if asynchronous else MagicMock(return_value={"id": "orders"})
    monkeypatch.setattr(proxy, "read", read)
    key_container = proxy(key.client_connection, "dbs/owned", "orders")
    case = (setup.AsyncContainerReadCase if asynchronous else setup.SyncContainerReadCase)()

    def checked_call(client, operation):
        assert client is data
        return operation()

    monkeypatch.setattr(setup, "run_on_rust_async" if asynchronous else "run_on_rust", checked_call)

    async def run():
        try:
            result = case.asyncSetUp() if asynchronous else case.setUp()
            if inspect.isawaitable(result):
                await result
            result = proxy.read(key_container, populate_quota_info=True)
            if inspect.isawaitable(result):
                result = await result
            assert result == {"id": "orders"}
            assert case.test_database is data_db
            assert data_db.create_container == key_db.create_container
            assert data_db.delete_container == key_db.delete_container
        finally:
            while case._cleanups:
                function, args, kwargs = case._cleanups.pop()
                result = function(*args, **kwargs)
                if inspect.isawaitable(result):
                    await result

    asyncio.run(run())
    assert constructor.call_args_list == [
        call("https://read-fixture.invalid", "unit-test-key", _backend="rust"),
        call("https://read-fixture.invalid", credential if auth == "aad" else "unit-test-key", _backend="rust"),
    ]
    read.assert_called_once_with(data_container, populate_quota_info=True)
    key.create_database.assert_called_once()
    data.create_database.assert_not_called()
    if auth == "aad":
        credential_factory.assert_called_once_with(asynchronous)
    else:
        credential_factory.assert_not_called()
