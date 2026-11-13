# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""Live ``query_containers`` result membership on the Rust backend."""
from __future__ import annotations

import os
import uuid

import pytest

from azure.cosmos import CosmosClient, exceptions
from azure.cosmos.partition_key import PartitionKey
from common._rust_checks import run_on_rust

CONTAINER_COUNT = 3


def _rust_client():
    return CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")


def _query_ids(client, database, query, **kwargs):
    return run_on_rust(client, lambda: sorted(row["id"] for row in database.query_containers(query, **kwargs)))


@pytest.fixture(scope="module")
def database_with_containers():
    client = _rust_client()
    name = "rust_query_containers_" + uuid.uuid4().hex[:8]
    container_ids = []
    try:
        database = client.create_database(id=name)
        for index in range(CONTAINER_COUNT):
            container_id = "c{}".format(index)
            database.create_container(id=container_id, partition_key=PartitionKey(path="/pk", kind="Hash"))
            container_ids.append(container_id)
        yield name, container_ids
    finally:
        try:
            client.delete_database(name)
        except exceptions.CosmosResourceNotFoundError:
            pass
        finally:
            client.close()


@pytest.fixture
def client():
    rust_client = _rust_client()
    try:
        yield rust_client
    finally:
        rust_client.close()


def test_query_with_no_match_returns_empty_rust(client, database_with_containers):
    """A parameterized filter that matches no container returns an empty result instead of raising."""
    database_id, _ = database_with_containers
    database = client.get_database_client(database_id)
    ids = _query_ids(client, database, {
        "query": "SELECT * FROM root r WHERE r.id=@id",
        "parameters": [{"name": "@id", "value": "definitely_not_here"}],
    })
    assert ids == []


def test_select_all_query_returns_every_container_rust(client, database_with_containers):
    """An unfiltered ``SELECT *`` query passed as a query dict returns exactly the containers created."""
    database_id, container_ids = database_with_containers
    database = client.get_database_client(database_id)
    assert _query_ids(client, database, {"query": "SELECT * FROM root r"}) == sorted(container_ids)


def test_plain_string_query_returns_matching_containers_rust(client, database_with_containers):
    """A query passed as a bare string returns exactly the containers it matches."""
    database_id, container_ids = database_with_containers
    database = client.get_database_client(database_id)
    assert _query_ids(client, database, "SELECT * FROM root r") == sorted(container_ids)
