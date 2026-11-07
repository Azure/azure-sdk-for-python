# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# Rust behavior test
"""Async ``replace_container`` on Rust applies new settings without losing items or leaking hook edits."""

import os
import uuid
from contextlib import ExitStack
from unittest.mock import patch

import pytest

from azure.cosmos import CosmosClient, exceptions
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos.partition_key import PartitionKey
from common._rust_checks import run_on_rust_async

pytestmark = [pytest.mark.asyncio]
PK = PartitionKey(path="/pk")


@pytest.fixture(scope="module")
def owned_database():
    name = "rust_replace_container_a_" + uuid.uuid4().hex
    with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as admin:
        try:
            yield admin.create_database(name)
        finally:
            try:
                admin.delete_database(name)
            except exceptions.CosmosResourceNotFoundError:
                pass


async def _replace(client, database, target, **kwargs):
    with ExitStack() as guards:
        for method in ("ReplaceContainer", "ReadContainer"):
            guards.enter_context(patch.object(
                client.client_connection, method,
                side_effect=AssertionError("Rust replacement entered legacy " + method),
            ))
        return await run_on_rust_async(client, lambda: database.replace_container(target, PK, **kwargs))


@pytest.mark.parametrize("target_kind", ["name", "mapping", "proxy"])
async def test_replace_container_applies_settings_and_keeps_items_async_rust(owned_database, target_kind):
    """Replacing by name, mapping or proxy applies default_ttl and the indexing policy and keeps existing items.

    default_ttl=None later clears the TTL. The hook runs once with diagnostics headers, and its edits reach
    neither the returned properties nor last_response_headers.
    """
    name = "properties_" + uuid.uuid4().hex
    original = owned_database.create_container(name, PK, indexing_policy={"indexingMode": "none"})
    original.create_item({"id": "kept", "pk": "p", "value": 42})
    snapshots = []

    class Hook:
        # A falsy hook must still be called.
        def __bool__(self):
            return False

        def __call__(self, headers, body):
            assert headers["x-ms-activity-id"]
            assert float(headers["x-ms-request-charge"]) > 0
            assert body["id"] == name and body["defaultTtl"] == 3600
            assert headers["x-ms-cosmos-sdk-diagnostics"]
            snapshots.append(dict(headers))
            headers["etag"] = "changed"
            body["id"] = "wrong"
            body["indexingPolicy"]["indexingMode"] = "none"

    async with AsyncCosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as client:
        database = client.get_database_client(owned_database.id)
        target = ({"id": name, "indexingPolicy": {"indexingMode": "none"}} if target_kind == "mapping"
                  else database.get_container_client(name) if target_kind == "proxy" else name)
        proxy, properties = await _replace(
            client, database, target, default_ttl=3600, return_properties=True, response_hook=Hook(),
            timeout=30, initial_headers={"x-company-trace": "replacement"},
        )
        assert proxy.id == name and properties["id"] == name
        assert properties["indexingPolicy"]["indexingMode"] == "consistent"
        assert properties.get_response_headers()["etag"] != "changed"
        assert client.client_connection.last_response_headers["etag"] != "changed"
        stored = original.read()
        assert stored["defaultTtl"] == 3600 and stored["indexingPolicy"]["indexingMode"] == "consistent"

        proxy = await _replace(client, database, name, default_ttl=None, timeout=30)
        assert proxy.id == name and not isinstance(proxy, tuple)
        assert "defaultTtl" not in original.read()

    assert len(snapshots) == 1
    assert original.read_item("kept", partition_key="p")["value"] == 42
