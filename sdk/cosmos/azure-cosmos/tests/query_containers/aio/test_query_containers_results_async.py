# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""Live async ``query_containers`` result membership on the Rust backend."""
from __future__ import annotations

import os
import uuid

import pytest

from azure.cosmos import CosmosClient as SyncCosmosClient, exceptions
from azure.cosmos.aio import CosmosClient
from azure.cosmos.partition_key import PartitionKey
from common._rust_checks import run_on_rust_async

pytestmark = [pytest.mark.asyncio]

CONTAINER_COUNT = 3


async def _query_ids(database_id, query, **kwargs):
    async with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as client:
        database = client.get_database_client(database_id)

        async def target():
            return sorted([row["id"] async for row in database.query_containers(query, **kwargs)])

        return await run_on_rust_async(client, target)


@pytest.fixture(scope="module")
def database_with_containers():
    client = SyncCosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")
    name = "rust_query_containers_a_" + uuid.uuid4().hex[:8]
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


async def test_query_with_no_match_returns_empty_async_rust(database_with_containers):
    """A parameterized filter that matches no container returns an empty result instead of raising."""
    database_id, _ = database_with_containers
    ids = await _query_ids(
        database_id, "SELECT * FROM root r WHERE r.id=@id",
        parameters=[{"name": "@id", "value": "definitely_not_here"}],
    )
    assert ids == []


async def test_select_all_query_returns_every_container_async_rust(database_with_containers):
    """An unfiltered ``SELECT *`` query passed as a query dict returns exactly the containers created."""
    database_id, container_ids = database_with_containers
    assert await _query_ids(database_id, {"query": "SELECT * FROM root r"}) == sorted(container_ids)


async def test_plain_string_query_returns_matching_containers_async_rust(database_with_containers):
    """A query passed as a bare string returns exactly the containers it matches."""
    database_id, container_ids = database_with_containers
    assert await _query_ids(database_id, "SELECT * FROM root r") == sorted(container_ids)
