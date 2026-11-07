# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""``create_container`` on Rust stores the settings the caller asked for.

A partition key cannot be changed after creation, so the stored settings must
be exactly what was requested.
"""
from __future__ import annotations

import os
import uuid

import pytest

from azure.cosmos import CosmosClient, exceptions
from azure.cosmos.partition_key import PartitionKey
from common._rust_checks import run_on_rust


def _rust_client():
    return CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")


@pytest.fixture(scope="module")
def database_id():
    """A throwaway database, deleted after the module along with everything created in it."""
    name = "rust_create_container_" + uuid.uuid4().hex[:8]
    with _rust_client() as client:
        try:
            client.create_database(id=name)
            yield name
        finally:
            try:
                client.delete_database(name)
            except exceptions.CosmosResourceNotFoundError:
                pass


def test_create_container_stores_explicit_partition_key_and_indexing_policy_rust(database_id):
    """A container created with an explicit partition key and indexing policy keeps both."""
    with _rust_client() as client:
        database = client.get_database_client(database_id)
        container = run_on_rust(client, lambda: database.create_container(
            id="explicit_" + uuid.uuid4().hex[:8],
            partition_key=PartitionKey(path="/pk", kind="Hash"),
            indexing_policy={
                "indexingMode": "consistent",
                "automatic": True,
                "includedPaths": [{"path": "/*"}],
                "excludedPaths": [{"path": "/excluded/*"}],
            },
        ))
        properties = container.read()

    assert properties["partitionKey"]["paths"] == ["/pk"]
    assert properties["partitionKey"]["kind"] == "Hash"
    policy = properties["indexingPolicy"]
    assert policy["indexingMode"] == "consistent"
    assert policy["automatic"] is True
    assert [path["path"] for path in policy["includedPaths"]] == ["/*"]
    assert "/excluded/*" in [path["path"] for path in policy["excludedPaths"]]


def test_create_container_persists_ttl_and_unique_keys_and_isolates_hook_rust(database_id):
    """default_ttl and unique_key_policy are stored; the hook runs once and its header edits stay private."""
    with _rust_client() as client:
        database = client.get_database_client(database_id)
        hooks = []

        def hook(headers, body):
            assert "X-MS-REQUEST-CHARGE" in headers
            hooks.append((headers, body))
            headers["x-hook-only"] = "private"

        container, properties = run_on_rust(client, lambda: database.create_container(
            "options_" + uuid.uuid4().hex[:8], PartitionKey(path="/tenant"),
            default_ttl=3600, unique_key_policy={"uniqueKeys": [{"paths": ["/code"]}]},
            timeout=10, initial_headers={"x-my-app": "provisioner"},
            response_hook=hook, return_properties=True,
        ))

        assert len(hooks) == 1
        assert hooks[0][1] is properties
        assert container.id == properties["id"]
        assert "x-hook-only" not in properties.get_response_headers()
        assert "x-hook-only" not in client.client_connection.last_response_headers
        assert properties["defaultTtl"] == 3600
        assert properties["uniqueKeyPolicy"] == {"uniqueKeys": [{"paths": ["/code"]}]}

        stored = container.read()
        assert stored["defaultTtl"] == 3600
        assert stored["uniqueKeyPolicy"] == {"uniqueKeys": [{"paths": ["/code"]}]}
