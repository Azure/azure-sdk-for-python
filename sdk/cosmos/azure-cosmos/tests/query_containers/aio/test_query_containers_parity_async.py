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
from unittest.mock import patch

import pytest

from azure.cosmos import CosmosClient, exceptions
from azure.cosmos.partition_key import PartitionKey
from common._parity_helpers import (
    run_on_both_backends_async,
    run_target_operation_async,
    skip_unless_emulator,
    skip_unless_rust_binding,
)

pytestmark = [skip_unless_emulator(), skip_unless_rust_binding(), pytest.mark.asyncio]

CONTAINER_COUNT = 3


def _admin_client():
    """Return a plain ``CosmosClient`` for fixture setup and teardown."""
    return CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="core-python")


async def _query_ids(client, database, query, **kwargs):
    async def target():
        return sorted([row["id"] async for row in database.query_containers(query, **kwargs)])
    return await run_target_operation_async(client, target)


@pytest.fixture(scope="module")
def database_with_containers():
    """A database holding a known set of containers, and the ids it holds."""
    client = _admin_client()
    name = "parity_query_containers_a_" + uuid.uuid4().hex[:8]
    container_ids = []
    try:
        database = client.create_database(id=name)
        for index in range(CONTAINER_COUNT):
            container_id = "c{}".format(index)
            database.create_container(
                id=container_id,
                partition_key=PartitionKey(path="/pk", kind="Hash"),
            )
            container_ids.append(container_id)
        yield name, container_ids
    finally:
        try:
            client.delete_database(name)
        except exceptions.CosmosResourceNotFoundError:
            pass
        finally:
            client.close()


async def test_query_containers_by_id_matches_async(database_with_containers):
    """A parameterised query for one container returns it on both engines."""
    database_id, container_ids = database_with_containers
    target = container_ids[1]

    async def _do(client):
        """Run the parameterised query and collect matching ids via the async iterator."""
        database = client.get_database_client(database_id)
        return await _query_ids(
            client, database, "SELECT * FROM root r WHERE r.id=@id",
            parameters=[{"name": "@id", "value": target}],
        )

    comparison = await run_on_both_backends_async(
        _do, description="async query_containers, by id"
    )
    comparison.print_report()
    assert comparison.core_python.raised is None and comparison.rust.raised is None
    comparison.assert_functional_parity()
    assert comparison.rust.return_value == [target]


async def test_query_containers_no_match_is_empty_async(database_with_containers):
    """A query matching nothing returns an empty result on both engines, not an error."""
    database_id, _ = database_with_containers

    async def _do(client):
        """Query for a container that does not exist and drain the async iterator."""
        database = client.get_database_client(database_id)
        return await _query_ids(
            client, database, "SELECT * FROM root r WHERE r.id=@id",
            parameters=[{"name": "@id", "value": "definitely_not_here"}],
        )

    comparison = await run_on_both_backends_async(
        _do, description="async query_containers, no match"
    )
    comparison.print_report()
    assert comparison.core_python.raised is None and comparison.rust.raised is None
    comparison.assert_functional_parity()
    assert comparison.rust.return_value == []


async def test_query_containers_select_all_matches_full_membership_async(database_with_containers):
    """An unfiltered query agrees with the containers actually created."""
    database_id, container_ids = database_with_containers

    async def _do(client):
        """Run ``SELECT * FROM root r`` and collect ids via the async iterator."""
        database = client.get_database_client(database_id)
        return await _query_ids(client, database, {"query": "SELECT * FROM root r"})

    comparison = await run_on_both_backends_async(
        _do, description="async query_containers, select all"
    )
    comparison.print_report()
    assert comparison.core_python.raised is None and comparison.rust.raised is None
    comparison.assert_functional_parity()
    assert comparison.rust.return_value == sorted(container_ids)


async def test_query_containers_string_query_matches_async(database_with_containers):
    """A query passed as a bare string behaves the same on both engines."""
    database_id, container_ids = database_with_containers

    async def _do(client):
        """Pass the query as a plain string and drain the async iterator."""
        database = client.get_database_client(database_id)
        return await _query_ids(client, database, "SELECT * FROM root r")

    comparison = await run_on_both_backends_async(
        _do, description="async query_containers, string query"
    )
    comparison.print_report()
    assert comparison.core_python.raised is None and comparison.rust.raised is None
    comparison.assert_functional_parity()
    assert comparison.rust.return_value == sorted(container_ids)


async def test_query_containers_pages_and_resumption_async(database_with_containers):
    database_id, container_ids = database_with_containers

    async def run(client):
        database = client.get_database_client(database_id)

        async def target():
            query = "SELECT * FROM c WHERE c.id != @excluded"
            options = {"parameters": [{"name": "@excluded", "value": "not_here"}], "max_item_count": 1}
            pages = database.query_containers(query, **options).by_page()
            first = [item async for item in await pages.__anext__()]
            token = pages.continuation_token
            assert len(first) == 1 and token
            remaining_pages = [[item async for item in page] async for page in pages]
            assert len(remaining_pages) == CONTAINER_COUNT - 1
            assert all(len(page) == 1 for page in remaining_pages)
            rest = [item for page in remaining_pages for item in page]
            replay = [item async for page in database.query_containers(query, **options).by_page(
                continuation_token=token
            ) async for item in page]
            assert replay == rest
            assert not {item["id"] for item in first}.intersection(item["id"] for item in replay)
            return sorted(item["id"] for item in first + replay)

        return await run_target_operation_async(client, target)

    comparison = await run_on_both_backends_async(run, description="async query_containers pages and resumption")
    assert comparison.core_python.raised is None and comparison.rust.raised is None
    comparison.assert_functional_parity()
    assert comparison.rust.return_value == sorted(container_ids)


@pytest.mark.parametrize("timeout", [None, 10])
async def test_query_containers_page_hooks_and_timeout_async(database_with_containers, timeout):
    database_id, container_ids = database_with_containers

    async def run(client):
        database = client.get_database_client(database_id)

        async def target():
            snapshots = []

            class Hook:
                def __bool__(self):
                    return False

                def __call__(self, headers):
                    assert headers["x-ms-activity-id"]
                    assert float(headers["x-ms-request-charge"]) > 0
                    if client.client_connection._backend.name == "rust":
                        assert headers["x-ms-cosmos-sdk-diagnostics"]
                    snapshots.append(headers)
                    headers["x-local"] = "mutation"

            pager = database.query_containers(
                "SELECT * FROM c", max_item_count=1, timeout=timeout, read_timeout=None,
                initial_headers={"x-company-trace": "query-containers"}, response_hook=Hook(),
            )
            assert snapshots == []
            connection = client.client_connection
            with patch.object(connection, "_CosmosClientConnection__QueryFeed",
                              wraps=connection._CosmosClientConnection__QueryFeed) as fetch:
                rows = [row async for row in pager]
            assert len(snapshots) == fetch.call_count >= CONTAINER_COUNT
            assert len({headers["x-ms-activity-id"] for headers in snapshots}) == len(snapshots)
            assert "x-local" not in client.client_connection.last_response_headers
            return sorted(row["id"] for row in rows)

        return await run_target_operation_async(client, target)

    comparison = await run_on_both_backends_async(run, description="async query_containers hooks and timeout")
    assert comparison.core_python.raised is None and comparison.rust.raised is None
    comparison.assert_functional_parity()
    assert comparison.rust.return_value == sorted(container_ids)
