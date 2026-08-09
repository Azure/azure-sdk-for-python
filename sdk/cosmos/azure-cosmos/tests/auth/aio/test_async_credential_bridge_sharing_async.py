# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Integration test for async-credential bridge sharing.

When several ``CosmosClient`` instances are built from the same async credential
on the rust path, they share one ``AsyncTokenCredentialBridge`` -- and so one
background loop thread and one driver -- instead of one per client. Each client
must still sign and read, and the loop thread must be gone once the last client
closes.

Runs on the emulator or a real Entra tenant (COSMOS_AAD_*), and only when the
rust binding is present. Uses ``asyncio.run`` directly (no pytest-asyncio).
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

# The bridge names its loop thread; count these to check one thread serves all
# clients, not one per client.
_BRIDGE_THREAD_NAME = "cosmos-async-credential"

_SHARED_CLIENT_COUNT = 4


def _bridge_thread_count() -> int:
    """Return the number of active asynchronous credential worker threads."""
    return sum(1 for t in threading.enumerate() if t.name == _BRIDGE_THREAD_NAME)


def test_shared_async_credential_uses_one_bridge_and_thread():
    """Clients sharing one async credential share one bridge and loop thread, all
    read, and the thread is gone after the last close."""

    async def main():
        credential = make_async_token_credential()
        host = os.environ["ACCOUNT_HOST"]
        before = _bridge_thread_count()

        async with AsyncExitStack() as stack:
            clients = [
                await stack.enter_async_context(
                    CosmosClient(host, credential, _backend="rust")
                )
                for _ in range(_SHARED_CLIENT_COUNT)
            ]

            # Dedup happens at construction: clients with the same credential must
            # hold the same bridge object.
            bridges = {id(c._backend._token_credential) for c in clients}  # noqa: SLF001
            assert len(bridges) == 1, (
                "clients sharing one async credential must share one bridge, "
                "got {} distinct bridges".format(len(bridges))
            )

            # Run a real operation through every client so the shared bridge signs
            # for all of them against the live account.
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

                # Exactly one bridge loop thread was started -- not one per client.
                assert _bridge_thread_count() - before == 1, (
                    "shared credential must run a single bridge loop thread"
                )
            finally:
                await db.delete_container(cname)

        # Every client is now closed; the last close stopped the shared loop
        # thread. The daemon thread exits just after join, so wait briefly before
        # checking it is gone.
        for _ in range(100):
            if _bridge_thread_count() == before:
                break
            await asyncio.sleep(0.05)
        assert _bridge_thread_count() == before, (
            "the shared bridge loop thread should be gone after the last client closed"
        )

    asyncio.run(main())


def test_distinct_async_credentials_do_not_share_a_bridge():
    """Two different async credentials must not share a bridge or loop thread,
    even against the same account."""

    async def main():
        host = os.environ["ACCOUNT_HOST"]
        before = _bridge_thread_count()
        cred_a = make_async_token_credential()
        cred_b = make_async_token_credential()
        assert cred_a is not cred_b, "test needs two distinct credential instances"

        async with AsyncExitStack() as stack:
            client_a = await stack.enter_async_context(CosmosClient(host, cred_a, _backend="rust"))
            client_b = await stack.enter_async_context(CosmosClient(host, cred_b, _backend="rust"))

            bridge_a = client_a._backend._token_credential  # noqa: SLF001
            bridge_b = client_b._backend._token_credential  # noqa: SLF001
            assert bridge_a is not bridge_b, "distinct credentials must map to distinct bridges"

            # Sign in both so each starts its own loop thread, so the count is
            # two, not one, when the credentials differ.
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
                assert _bridge_thread_count() - before == 2, (
                    "two distinct credentials must each run their own loop thread"
                )
            finally:
                await db.delete_container(cname)

        for _ in range(100):
            if _bridge_thread_count() == before:
                break
            await asyncio.sleep(0.05)
        assert _bridge_thread_count() == before, "both bridge loop threads should be gone after close"

    asyncio.run(main())
