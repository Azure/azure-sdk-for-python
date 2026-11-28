# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Checks the setup of the live tests in auth\aio\test_async_credential_bridge_sharing_async.py
without an account.

Those tests use token clients: clients that sign in with a token credential
(Microsoft Entra ID) instead of the account key. A separate account-key client
creates the database and container and deletes the container at the end. This
file runs the live tests with a fake CosmosClient and checks that each client
does only its own job, and that everything is closed even when a step fails.
"""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from auth.aio import test_async_credential_bridge_sharing_async as live_tests


@pytest.mark.parametrize("shared", [True, False], ids=["shared", "distinct"])
@pytest.mark.parametrize("failing_step", [None, "create_item", "read_item", "delete_container"])
def test_live_sharing_tests_use_account_key_client_for_setup_rust(monkeypatch, shared, failing_step):
    """Runs each live test with one shared credential and with two separate credentials.
    In each run, one step fails (creating the item, reading the item, or deleting the
    container) or no step fails. Checks that:
    - the account-key client creates the database and container, and deletes that
      same container
    - token clients write and read the item; when no step fails, every token client
      reads it
    - the error from the failing step reaches the caller unchanged
    - every client is closed, and every credential is closed exactly once
    """
    account_key = "offline-setup-key"
    monkeypatch.setenv("ACCOUNT_HOST", "https://offline.invalid")
    monkeypatch.setenv("ACCOUNT_KEY", account_key)
    credentials, clients, token_helpers, operations = [], [], {}, []
    step_error = RuntimeError(f"{failing_step} failed")

    def credential():
        result = SimpleNamespace(close=AsyncMock())
        credentials.append(result)
        return result

    # A fake CosmosClient that records which client did each step.
    class Client:
        def __init__(self, host, auth, *, _backend):
            assert host == "https://offline.invalid"
            assert _backend == "rust"
            self.key_auth = auth == account_key
            self.auth = auth
            self.closed = False
            clients.append(self)

        async def __aenter__(self):
            if not self.key_auth:
                # Each token client gets the token helper for its credential.
                bridge = token_helpers.setdefault(id(self.auth), SimpleNamespace(_loop=asyncio.get_running_loop()))
                self._adapter = SimpleNamespace(_token_credential=bridge)
            return self

        async def __aexit__(self, *args):
            self.closed = True

        async def create_database_if_not_exists(self, name):
            assert self.key_auth, "Token clients must not create databases"
            operations.append(("create_database", self, name))
            return self.get_database_client(name)

        def get_database_client(self, name):
            async def create_container(*, id, partition_key):
                assert self.key_auth, "Token clients must not create containers"
                operations.append(("create_container", self, id))
                return container(id)

            async def delete_container(id):
                assert self.key_auth, "Token clients must not delete containers"
                operations.append(("delete_container", self, id))
                if failing_step == "delete_container":
                    raise step_error

            def container(id):
                async def create_item(*, body):
                    assert not self.key_auth, "Item writes must use a token client"
                    operations.append(("create_item", self, body["id"]))
                    if failing_step == "create_item":
                        raise step_error
                    return body

                async def read_item(item_id, *, partition_key):
                    assert not self.key_auth, "Item reads must use a token client"
                    operations.append(("read_item", self, item_id))
                    if failing_step == "read_item":
                        raise step_error
                    return {"id": item_id}

                return SimpleNamespace(create_item=create_item, read_item=read_item)

            return SimpleNamespace(
                id=name,
                create_container=create_container,
                delete_container=delete_container,
                get_container_client=container,
            )

    monkeypatch.setattr(live_tests, "CosmosClient", Client)
    monkeypatch.setattr(live_tests, "make_async_token_credential", credential)
    scenario = (
        live_tests.test_shared_async_credential_uses_one_bridge_on_application_loop_rust
        if shared
        else live_tests.test_distinct_async_credentials_do_not_share_a_bridge_rust
    )
    if failing_step:
        with pytest.raises(RuntimeError) as caught:
            scenario()
        assert caught.value is step_error
    else:
        scenario()

    assert len(credentials) == (1 if shared else 2)
    token_clients = [client for client in clients if not client.key_auth]
    assert len(token_clients) == (live_tests._SHARED_CLIENT_COUNT if shared else 2)
    assert len(clients) == len(token_clients) + 1
    management = [(op, client, resource) for op, client, resource in operations if client.key_auth]
    assert [op for op, _, _ in management] == ["create_database", "create_container", "delete_container"]
    assert management[1][2] == management[2][2]
    if failing_step is None:
        assert [client for op, client, _ in operations if op == "read_item"] == token_clients
    assert all(client.closed for client in clients)
    for token in credentials:
        token.close.assert_awaited_once_with()
