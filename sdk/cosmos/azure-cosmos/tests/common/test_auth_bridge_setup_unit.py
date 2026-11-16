# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Offline guards for provisioning in the live async credential-sharing tests."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from auth.aio import test_async_credential_bridge_sharing_async as sharing


@pytest.mark.parametrize("shared", [True, False], ids=["shared", "distinct"])
@pytest.mark.parametrize("failure", [None, "create_item", "read_item", "delete_container"])
def test_bridge_scenarios_reserve_management_operations_for_key_client_rust(monkeypatch, shared, failure):
    key = "offline-setup-key"
    monkeypatch.setenv("ACCOUNT_HOST", "https://offline.invalid")
    monkeypatch.setenv("ACCOUNT_KEY", key)
    credentials, clients, bridges, operations = [], [], {}, []
    injected = RuntimeError(f"injected {failure}")

    def credential():
        result = SimpleNamespace(close=AsyncMock())
        credentials.append(result)
        return result

    class Client:
        def __init__(self, host, auth, *, _backend):
            assert host == "https://offline.invalid"
            assert _backend == "rust"
            self.key_auth = auth == key
            self.auth = auth
            self.closed = False
            clients.append(self)

        async def __aenter__(self):
            if not self.key_auth:
                bridge = bridges.setdefault(id(self.auth), SimpleNamespace(_loop=asyncio.get_running_loop()))
                self._adapter = SimpleNamespace(_token_credential=bridge)
            return self

        async def __aexit__(self, *args):
            self.closed = True

        async def create_database_if_not_exists(self, name):
            assert self.key_auth, "AAD clients must not provision databases"
            operations.append(("create_database", self, name))
            return self.get_database_client(name)

        def get_database_client(self, name):
            async def create_container(*, id, partition_key):
                assert self.key_auth, "AAD clients must not provision containers"
                operations.append(("create_container", self, id))
                return container(id)

            async def delete_container(id):
                assert self.key_auth, "AAD clients must not delete containers"
                operations.append(("delete_container", self, id))
                if failure == "delete_container":
                    raise injected

            def container(id):
                async def create_item(*, body):
                    assert not self.key_auth, "item writes must still exercise the token client"
                    operations.append(("create_item", self, body["id"]))
                    if failure == "create_item":
                        raise injected
                    return body

                async def read_item(item_id, *, partition_key):
                    assert not self.key_auth, "item reads must still exercise the token clients"
                    operations.append(("read_item", self, item_id))
                    if failure == "read_item":
                        raise injected
                    return {"id": item_id}

                return SimpleNamespace(create_item=create_item, read_item=read_item)

            return SimpleNamespace(
                id=name,
                create_container=create_container,
                delete_container=delete_container,
                get_container_client=container,
            )

    monkeypatch.setattr(sharing, "CosmosClient", Client)
    monkeypatch.setattr(sharing, "make_async_token_credential", credential)
    scenario = (
        sharing.test_shared_async_credential_uses_one_bridge_on_application_loop_rust
        if shared
        else sharing.test_distinct_async_credentials_do_not_share_a_bridge_rust
    )
    if failure:
        with pytest.raises(RuntimeError) as caught:
            scenario()
        assert caught.value is injected
    else:
        scenario()

    assert len(credentials) == (1 if shared else 2)
    token_clients = [client for client in clients if not client.key_auth]
    assert len(token_clients) == (sharing._SHARED_CLIENT_COUNT if shared else 2)
    assert len(clients) == len(token_clients) + 1
    management = [(op, client, resource) for op, client, resource in operations if client.key_auth]
    assert [op for op, _, _ in management] == ["create_database", "create_container", "delete_container"]
    assert management[1][2] == management[2][2]
    if failure is None:
        assert [client for op, client, _ in operations if op == "read_item"] == token_clients
    assert all(client.closed for client in clients)
    for token in credentials:
        token.close.assert_awaited_once_with()
