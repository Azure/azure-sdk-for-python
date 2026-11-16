# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""``create_container_if_not_exists`` on Rust returns an existing container unchanged.

Application startup calls this on every process start, so the existing-container
leg must read the container rather than reconcile it with the requested settings.
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
    name = "rust_ccine_" + uuid.uuid4().hex[:8]
    with _rust_client() as client:
        try:
            client.create_database(id=name)
            yield name
        finally:
            try:
                client.delete_database(name)
            except exceptions.CosmosResourceNotFoundError:
                pass


@pytest.fixture
def existing_container_id(database_id):
    """A container that is already there, with settings the call must not change."""
    name = "existing_" + uuid.uuid4().hex[:8]
    with _rust_client() as client:
        client.get_database_client(database_id).create_container(
            id=name,
            partition_key=PartitionKey(path="/original", kind="Hash"),
            indexing_policy={
                "indexingMode": "consistent",
                "includedPaths": [{"path": "/*"}],
                "excludedPaths": [{"path": "/excluded/*"}],
            },
        )
    return name


def test_existing_container_keeps_original_settings_rust(database_id, existing_container_id):
    """Asking for different settings on an existing container returns its original partition key and policy."""
    with _rust_client() as client:
        database = client.get_database_client(database_id)
        container = run_on_rust(client, lambda: database.create_container_if_not_exists(
            id=existing_container_id,
            partition_key=PartitionKey(path="/different", kind="Hash"),
            default_ttl=99,
            indexing_policy={"indexingMode": "none"},
        ))
        properties = container.read()

    assert container.id == existing_container_id
    assert properties["partitionKey"]["paths"] == ["/original"]
    assert properties["indexingPolicy"]["indexingMode"] == "consistent"
    assert "/excluded/*" in [path["path"] for path in properties["indexingPolicy"]["excludedPaths"]]
    assert "defaultTtl" not in properties
