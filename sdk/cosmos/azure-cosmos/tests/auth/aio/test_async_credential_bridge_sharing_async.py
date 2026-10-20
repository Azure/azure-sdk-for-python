# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Integration test for async-credential bridge sharing.

When several ``CosmosClient`` instances are built from the same async credential
on the Rust path, this test checks bridge identity, successful reads, and the
application-loop ownership without creating credential threads. It does not
inspect native driver identity or count token callbacks.

Runs on the emulator or a real Entra tenant (COSMOS_AAD_*), and only when the
Rust binding is present. Uses ``asyncio.run`` directly (no pytest-asyncio).
"""

from __future__ import annotations

import asyncio
import os
import threading
import uuid
from contextlib import AsyncExitStack

import pytest

from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey

from common._parity_helpers import skip_unless_emulator, skip_unless_rust_binding
from auth._token_credentials import make_async_token_credential, skip_unless_token_auth

pytestmark = [pytest.mark.cosmosEmulator, pytest.mark.cosmosRustAAD,
              skip_unless_emulator(), skip_unless_rust_binding(), skip_unless_token_auth()]

# Guard against reintroducing the retired private credential thread.
_BRIDGE_THREAD_NAME = "cosmos-async-credential"

_SHARED_CLIENT_COUNT = 4


def _bridge_thread_count() -> int:
    """Return the number of active asynchronous credential worker threads."""
    return sum(1 for t in threading.enumerate() if t.name == _BRIDGE_THREAD_NAME)


def test_shared_async_credential_uses_one_bridge_on_application_loop_rust():
    """Shared credentials use one bridge on the caller's loop without a private thread."""

    async def main():
        credential = make_async_token_credential()
        host = os.environ["ACCOUNT_HOST"]
        before = _bridge_thread_count()

        async with AsyncExitStack() as stack:
            if hasattr(credential, "close"):
                stack.push_async_callback(credential.close)
            clients = [
                await stack.enter_async_context(
                    CosmosClient(host, credential, _backend="rust")
                )
                for _ in range(_SHARED_CLIENT_COUNT)
            ]

            # Async entry has acquired the shared bridge on this application loop.
            bridges = {id(c._adapter._token_credential) for c in clients}  # noqa: SLF001
            assert len(bridges) == 1, (
                "clients sharing one async credential must share one bridge, "
                "got {} distinct bridges".format(len(bridges))
            )

            # Read through every client. Cached tokens can serve later requests,
            # so successful reads do not imply one credential callback per client.
            db = await clients[0].create_database_if_not_exists("parity_db")
            cname = "auth_aio_share_" + uuid.uuid4().hex[:8]
            cont = await db.create_container(id=cname, partition_key=PartitionKey(path="/pk"))
            try:
                item_id = uuid.uuid4().hex
                await cont.create_item(body={"id": item_id, "pk": "a", "n": 1})
                for client in clients:
                    container = client.get_database_client("parity_db").get_container_client(cname)
                    read = await container.read_item(item_id, partition_key="a")
                    assert read["id"] == item_id, "each shared-credential client must read the item"

                assert all(c._adapter._token_credential._loop is asyncio.get_running_loop() for c in clients)
                assert _bridge_thread_count() == before
            finally:
                await db.delete_container(cname)

        assert _bridge_thread_count() == before
        assert asyncio.get_running_loop().is_running()

    asyncio.run(main())


def test_distinct_async_credentials_do_not_share_a_bridge_rust():
    """Distinct credentials have distinct bridges, both on the application loop."""

    async def main():
        host = os.environ["ACCOUNT_HOST"]
        before = _bridge_thread_count()
        cred_a = make_async_token_credential()
        cred_b = make_async_token_credential()
        assert cred_a is not cred_b, "test needs two distinct credential instances"

        async with AsyncExitStack() as stack:
            for credential in (cred_a, cred_b):
                if hasattr(credential, "close"):
                    stack.push_async_callback(credential.close)
            client_a = await stack.enter_async_context(CosmosClient(host, cred_a, _backend="rust"))
            client_b = await stack.enter_async_context(CosmosClient(host, cred_b, _backend="rust"))

            bridge_a = client_a._adapter._token_credential  # noqa: SLF001
            bridge_b = client_b._adapter._token_credential  # noqa: SLF001
            assert bridge_a is not bridge_b, "distinct credentials must map to distinct bridges"

            assert bridge_a._loop is bridge_b._loop is asyncio.get_running_loop()
            db = await client_a.create_database_if_not_exists("parity_db")
            cname = "auth_aio_distinct_" + uuid.uuid4().hex[:8]
            cont = await db.create_container(id=cname, partition_key=PartitionKey(path="/pk"))
            try:
                item_id = uuid.uuid4().hex
                await cont.create_item(body={"id": item_id, "pk": "a", "n": 1})
                for client in (client_a, client_b):
                    container = client.get_database_client("parity_db").get_container_client(cname)
                    read = await container.read_item(item_id, partition_key="a")
                    assert read["id"] == item_id
                assert _bridge_thread_count() == before
            finally:
                await db.delete_container(cname)

        assert _bridge_thread_count() == before
        assert asyncio.get_running_loop().is_running()

    asyncio.run(main())
