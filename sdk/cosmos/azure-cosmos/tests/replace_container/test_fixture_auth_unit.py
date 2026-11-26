# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Keep replacement fixture credential/backend wiring independent of legacy tests."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
def test_replacement_fixture_keeps_aad_on_rust_rust(monkeypatch, asynchronous):
    from config import clients
    from replace_container import _container_setup as setup

    credential = object()
    monkeypatch.setattr(clients.TestSettings, "data_auth_mode", "aad")
    monkeypatch.setattr(clients.TestSettings, "is_emulator", False)
    monkeypatch.setattr(clients, "_aad_credential", lambda async_mode: credential)
    monkeypatch.setenv("ACCOUNT_HOST", "https://replacement-fixture.invalid")
    monkeypatch.setenv("ACCOUNT_KEY", "unit-test-key")
    data = AsyncMock() if asynchronous else MagicMock()
    data.get_database_client = MagicMock()
    constructor = MagicMock(return_value=data)
    monkeypatch.setattr(clients, "AsyncCosmosClient" if asynchronous else "CosmosClient", constructor)
    key = AsyncMock() if asynchronous else MagicMock()
    case = (setup.AsyncReplacementCase if asynchronous else setup.SyncReplacementCase)()
    monkeypatch.setattr(case, "_create_key_client", lambda: key)
    if asynchronous:
        async def run():
            try:
                await case.asyncSetUp()
            finally:
                while case._cleanups:
                    function, args, kwargs = case._cleanups.pop()
                    result = function(*args, **kwargs)
                    if asyncio.iscoroutine(result):
                        await result
        asyncio.run(run())
    else:
        try:
            case.setUp()
        finally:
            case.doCleanups()
    constructor.assert_called_once_with(
        "https://replacement-fixture.invalid", credential, _backend="rust",
    )
    key.create_database.assert_called_once()
