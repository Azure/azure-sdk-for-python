# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""Async ``delete_container`` on Rust removes the container and reports a missing one as 404."""
import os
import uuid
from unittest.mock import patch

import pytest

from azure.cosmos import CosmosClient, exceptions
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos.partition_key import PartitionKey
from common._rust_checks import run_on_rust_async

pytestmark = [pytest.mark.asyncio]


def _rust_client():
    return AsyncCosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")


@pytest.fixture(scope="module")
def owned_database():
    name = "rust_delete_container_a_" + uuid.uuid4().hex
    with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as admin:
        try:
            yield admin.create_database(name)
        finally:
            try:
                admin.delete_database(name)
            except exceptions.CosmosResourceNotFoundError:
                pass


def _target(database, name, kind):
    if kind == "mapping":
        return {"id": name}
    if kind == "proxy":
        return database.get_container_client(name)
    return name


def _no_legacy_delete(client):
    return patch.object(
        client.client_connection, "DeleteContainer", side_effect=AssertionError("Rust deletion used legacy Python")
    )


@pytest.mark.parametrize("target_kind", ["name", "mapping", "proxy"])
async def test_delete_container_returns_none_and_repeat_delete_raises_not_found_async_rust(
    owned_database, target_kind
):
    """Deleting by name, mapping or proxy returns None, calls the hook once with no body, and a repeat raises 404."""
    name = "container_" + uuid.uuid4().hex
    owned_database.create_container(name, PartitionKey(path="/id"))
    calls = []

    class Hook:
        # A falsy hook must still be called.
        def __bool__(self):
            return False

        def __call__(self, headers, body):
            assert body is None
            assert headers["X-MS-ACTIVITY-ID"]
            headers["x-test-mutation"] = "isolated"
            calls.append(body)

    async with _rust_client() as client:
        database = client.get_database_client(owned_database.id)
        target = _target(database, name, target_kind)
        with _no_legacy_delete(client):
            assert await run_on_rust_async(
                client, lambda: database.delete_container(target, response_hook=Hook(), timeout=30)
            ) is None
            assert "x-test-mutation" not in client.client_connection.last_response_headers
            with pytest.raises(exceptions.CosmosResourceNotFoundError):
                await run_on_rust_async(client, lambda: database.delete_container(target, timeout=30))

    assert calls == [None]
    with pytest.raises(exceptions.CosmosResourceNotFoundError):
        owned_database.get_container_client(name).read()


@pytest.mark.parametrize("warm", [False, True], ids=["cold", "warm"])
async def test_delete_container_after_metadata_resolution_async_rust(owned_database, warm):
    """A container already resolved by an item call is deleted with one hook call; a missing one raises 404 hookless."""
    name = "resolution_" + uuid.uuid4().hex
    if warm:
        owned_database.create_container(name, PartitionKey(path="/id"))
    hooks = []

    def hook(headers, body):
        hooks.append(body)

    async def delete():
        async with _rust_client() as client:
            database = client.get_database_client(owned_database.id)
            if warm:
                # An item operation resolves this container in the same Rust driver.
                item = await database.get_container_client(name).create_item({"id": "warm", "value": 42})
                assert item["id"] == "warm" and item["value"] == 42
            with _no_legacy_delete(client):
                return await run_on_rust_async(
                    client, lambda: database.delete_container(name, response_hook=hook, timeout=30)
                )

    if warm:
        assert await delete() is None
        assert hooks == [None]
    else:
        with pytest.raises(exceptions.CosmosResourceNotFoundError):
            await delete()
        assert hooks == []
    with pytest.raises(exceptions.CosmosResourceNotFoundError):
        owned_database.get_container_client(name).read()
