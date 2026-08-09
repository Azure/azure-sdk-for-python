# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Check async ``ContainerProxy.read`` results on Python and Rust.

Here, parity means matching public behavior between Python and Rust. These
tests prove that stored partition-key and indexing settings match and that a
missing container raises the same typed error. They also prove that options
Rust cannot honor stay on Python, so requested statistics and quota data are
not silently omitted.
"""
from __future__ import annotations

import os
import uuid

import pytest

from azure.cosmos import CosmosClient, exceptions
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos.partition_key import PartitionKey
from common._parity_helpers import (
    _binding_operation_count,
    run_on_both_backends_async,
    skip_unless_emulator,
    skip_unless_rust_binding,
)

pytestmark = [skip_unless_emulator(), skip_unless_rust_binding(), pytest.mark.asyncio]


def _admin_client():
    """A privileged client for database and container setup and teardown, not the client under test."""
    return CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])


def _normalize_container(properties):
    """Strip server-stamped fields, keeping only the settings the caller asked for."""
    # Reduce the result to the settings a customer reads, so the two engines
    # compare equal regardless of fields the service stamps on every document.
    return {
        "id": properties["id"],
        "partitionKey": dict(properties["partitionKey"]),
        "indexingMode": properties["indexingPolicy"]["indexingMode"],
        "includedPaths": sorted(
            path["path"] for path in properties["indexingPolicy"].get("includedPaths", [])
        ),
        "excludedPaths": sorted(
            path["path"] for path in properties["indexingPolicy"].get("excludedPaths", [])
        ),
    }


@pytest.fixture
def database_id():
    """A throwaway database, deleted after the test along with everything created in it."""
    client = _admin_client()
    name = "parity_read_container_a_" + uuid.uuid4().hex[:8]
    client.create_database(id=name)
    try:
        yield name
    finally:
        try:
            client.delete_database(name)
        except Exception:  # pylint: disable=broad-except
            pass
        client.close()


@pytest.fixture
def container_id(database_id):
    """A container with a non-default indexing policy, so the read has something to lose."""
    client = _admin_client()
    name = "read_target_" + uuid.uuid4().hex[:8]
    client.get_database_client(database_id).create_container(
        id=name,
        partition_key=PartitionKey(path="/pk", kind="Hash"),
        indexing_policy={
            "indexingMode": "consistent",
            "includedPaths": [{"path": "/*"}],
            "excludedPaths": [{"path": "/excluded/*"}],
        },
    )
    try:
        yield name
    finally:
        client.close()


async def test_read_container_properties_async(database_id, container_id):
    """Async read returns the same partition key and indexing policy on both engines."""

    async def _do(client):
        """Await a container read and return its normalised properties."""
        container = client.get_database_client(database_id).get_container_client(container_id)
        return _normalize_container(await container.read())

    comparison = await run_on_both_backends_async(
        _do, description="async container read, custom indexing policy"
    )
    comparison.print_report()
    comparison.assert_functional_parity()
    assert comparison.core_python.return_value["partitionKey"]["paths"] == ["/pk"]
    assert "/excluded/*" in comparison.core_python.return_value["excludedPaths"]


async def test_read_container_with_quota_and_statistics_stays_on_legacy_path_async(
    database_id, container_id
):
    """A read asking for statistics or quota usage does not go to rust, on either engine."""
    # Unsupported options stay on Python so requested fields are not dropped.
    client = AsyncCosmosClient(
        os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust"
    )
    try:
        container = client.get_database_client(database_id).get_container_client(container_id)
        before = _binding_operation_count()
        properties = await container.read(
            populate_partition_key_range_statistics=True,
            populate_quota_info=True,
        )
        after = _binding_operation_count()

        assert properties.get("statistics") is not None, (
            "the caller asked for per-partition statistics and did not get them"
        )
        assert (
            client.client_connection.last_response_headers.get("x-ms-resource-usage") is not None
        ), "the caller asked for quota usage and did not get it"
        assert after == before, (
            "a read requesting statistics or quota info reached rust; the driver may now "
            "support these options, in which case is_read_container_rust_eligible should "
            "stop excluding them"
        )
    finally:
        await client.close()


async def test_read_missing_container_raises_404_async(database_id):
    """Reading a container that is not there raises the same typed 404 on both engines."""
    missing_id = "never_created_" + uuid.uuid4().hex[:8]

    async def _do(client):
        """Await a read of a container that does not exist, expecting a 404 error."""
        container = client.get_database_client(database_id).get_container_client(missing_id)
        return await container.read()

    comparison = await run_on_both_backends_async(
        _do, description="async container read, missing container"
    )
    comparison.print_report()
    comparison.assert_functional_exception_parity()
    assert isinstance(comparison.rust.raised, exceptions.CosmosResourceNotFoundError)
    assert isinstance(comparison.core_python.raised, exceptions.CosmosResourceNotFoundError)
    assert comparison.rust.raised.status_code == 404
