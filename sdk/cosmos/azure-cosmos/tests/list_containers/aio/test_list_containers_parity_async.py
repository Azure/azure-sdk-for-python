# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Check async ``list_containers`` results on Python and Rust.

Here, parity means matching public behavior between Python and Rust. These
tests prove that populated, empty, and multi-page listings contain the same
container IDs. Customers depend on complete pages for management tools,
migrations, and safe provisioning.
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
def empty_database_id():
    """A database with no containers at all."""
    client = _admin_client()
    name = "parity_list_containers_a_empty_" + uuid.uuid4().hex[:8]
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
def populated_database_id():
    """A database holding a known set of containers."""
    client = _admin_client()
    name = "parity_list_containers_a_" + uuid.uuid4().hex[:8]
    database = client.create_database(id=name)
    for index in range(CONTAINER_COUNT):
        database.create_container(
            id="c{}_{}".format(index, uuid.uuid4().hex[:6]),
            partition_key=PartitionKey(path="/pk", kind="Hash"),
        )
    try:
        yield name
    finally:
        try:
            client.delete_database(name)
        except Exception:  # pylint: disable=broad-except
            pass
        client.close()


async def test_list_containers_returns_same_ids_async(populated_database_id):
    """Both engines report the same set of containers for the same database."""

    async def _do(client):
        """Collect container ids via the async iterator path."""
        database = client.get_database_client(populated_database_id)
        return sorted([c["id"] async for c in database.list_containers()])

    comparison = await run_on_both_backends_async(
        _do, description="async list_containers, populated database"
    )
    comparison.print_report()
    comparison.assert_functional_parity()
    assert len(comparison.core_python.return_value) == CONTAINER_COUNT


async def test_list_containers_on_empty_database_returns_empty_async(empty_database_id):
    """A database with no containers yields an empty list on both engines, not an error."""

    async def _do(client):
        """Drain the async iterator against the empty database."""
        database = client.get_database_client(empty_database_id)
        return sorted([c["id"] async for c in database.list_containers()])

    comparison = await run_on_both_backends_async(
        _do, description="async list_containers, empty database"
    )
    comparison.print_report()
    comparison.assert_functional_parity()
    assert comparison.rust.return_value == []


async def test_list_containers_paged_matches_async(populated_database_id):
    """Forcing several pages yields the same containers as a single-page read."""
    # One item per page checks that continuation tokens do not lose containers.

    async def _do(client):
        """List with ``max_item_count=1`` so continuation tokens are exercised."""
        database = client.get_database_client(populated_database_id)
        return sorted([c["id"] async for c in database.list_containers(max_item_count=1)])

    comparison = await run_on_both_backends_async(
        _do, description="async list_containers, one container per page"
    )
    comparison.print_report()
    comparison.assert_functional_parity()
    assert len(comparison.rust.return_value) == CONTAINER_COUNT
