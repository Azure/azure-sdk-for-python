# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Check async ``query_containers`` results on Python and Rust.

Here, parity means matching public behavior between Python and Rust. These
tests prove that parameters, empty results, full results, and string queries
return the same container IDs. Customers use these queries to find resources
before provisioning or managing them.
"""
from __future__ import annotations

import os
import uuid

import pytest

from azure.cosmos import CosmosClient
from azure.cosmos.partition_key import PartitionKey
from common._parity_helpers import (
    run_on_both_backends_async,
    skip_unless_emulator,
    skip_unless_rust_binding,
)

pytestmark = [skip_unless_emulator(), skip_unless_rust_binding(), pytest.mark.asyncio]

CONTAINER_COUNT = 3


def _admin_client():
    """Return a plain ``CosmosClient`` for fixture setup and teardown."""
    return CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])


@pytest.fixture
def database_with_containers():
    """A database holding a known set of containers, and the ids it holds."""
    client = _admin_client()
    name = "parity_query_containers_a_" + uuid.uuid4().hex[:8]
    database = client.create_database(id=name)
    container_ids = []
    for index in range(CONTAINER_COUNT):
        container_id = "c{}_{}".format(index, uuid.uuid4().hex[:6])
        database.create_container(
            id=container_id,
            partition_key=PartitionKey(path="/pk", kind="Hash"),
        )
        container_ids.append(container_id)
    try:
        yield name, container_ids
    finally:
        try:
            client.delete_database(name)
        except Exception:  # pylint: disable=broad-except
            pass
        client.close()


async def test_query_containers_by_id_matches_async(database_with_containers):
    """A parameterised query for one container returns it on both engines."""
    database_id, container_ids = database_with_containers
    target = container_ids[1]

    async def _do(client):
        """Run the parameterised query and collect matching ids via the async iterator."""
        database = client.get_database_client(database_id)
        return sorted([
            c["id"]
            async for c in database.query_containers(
                query="SELECT * FROM root r WHERE r.id=@id",
                parameters=[{"name": "@id", "value": target}],
            )
        ])

    comparison = await run_on_both_backends_async(
        _do, description="async query_containers, by id"
    )
    comparison.print_report()
    comparison.assert_functional_parity()
    assert comparison.rust.return_value == [target]


async def test_query_containers_no_match_is_empty_async(database_with_containers):
    """A query matching nothing returns an empty result on both engines, not an error."""
    database_id, _ = database_with_containers

    async def _do(client):
        """Query for a container that does not exist and drain the async iterator."""
        database = client.get_database_client(database_id)
        return sorted([
            c["id"]
            async for c in database.query_containers(
                query="SELECT * FROM root r WHERE r.id=@id",
                parameters=[{"name": "@id", "value": "definitely_not_here"}],
            )
        ])

    comparison = await run_on_both_backends_async(
        _do, description="async query_containers, no match"
    )
    comparison.print_report()
    comparison.assert_functional_parity()
    assert comparison.rust.return_value == []


async def test_query_containers_select_all_matches_full_membership_async(database_with_containers):
    """An unfiltered query agrees with the containers actually created."""
    database_id, container_ids = database_with_containers

    async def _do(client):
        """Run ``SELECT * FROM root r`` and collect ids via the async iterator."""
        database = client.get_database_client(database_id)
        return sorted([
            c["id"] async for c in database.query_containers(query="SELECT * FROM root r")
        ])

    comparison = await run_on_both_backends_async(
        _do, description="async query_containers, select all"
    )
    comparison.print_report()
    comparison.assert_functional_parity()
    assert comparison.rust.return_value == sorted(container_ids)


async def test_query_containers_string_query_matches_async(database_with_containers):
    """A query passed as a bare string behaves the same on both engines."""
    database_id, container_ids = database_with_containers

    async def _do(client):
        """Pass the query as a plain string and drain the async iterator."""
        database = client.get_database_client(database_id)
        return sorted([c["id"] async for c in database.query_containers("SELECT * FROM root r")])

    comparison = await run_on_both_backends_async(
        _do, description="async query_containers, string query"
    )
    comparison.print_report()
    comparison.assert_functional_parity()
    assert comparison.rust.return_value == sorted(container_ids)
