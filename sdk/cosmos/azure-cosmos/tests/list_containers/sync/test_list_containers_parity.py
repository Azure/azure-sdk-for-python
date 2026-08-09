# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Check ``list_containers`` results on Python and Rust.

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
    run_on_both_backends,
    skip_unless_emulator,
    skip_unless_rust_binding,
)

pytestmark = [skip_unless_emulator(), skip_unless_rust_binding()]

CONTAINER_COUNT = 3


def _admin_client():
    """Return a plain ``CosmosClient`` for fixture setup and teardown."""
    return CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])


def _ids(containers):
    """Return sorted container ids so order-insensitive membership can be compared."""
    return sorted(container["id"] for container in containers)


@pytest.fixture
def empty_database_id():
    """A database with no containers at all."""
    client = _admin_client()
    name = "parity_list_containers_empty_" + uuid.uuid4().hex[:8]
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
    name = "parity_list_containers_" + uuid.uuid4().hex[:8]
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


def test_list_containers_returns_same_ids(populated_database_id):
    """Both engines report the same set of containers for the same database."""

    def _do(client):
        """Collect and sort container ids from the sync iterator."""
        database = client.get_database_client(populated_database_id)
        return _ids(database.list_containers())

    comparison = run_on_both_backends(_do, description="list_containers, populated database")
    comparison.print_report()
    comparison.assert_functional_parity()
    assert len(comparison.core_python.return_value) == CONTAINER_COUNT


def test_list_containers_on_empty_database_returns_empty(empty_database_id):
    """A database with no containers yields an empty list on both engines, not an error."""

    def _do(client):
        """Drain the sync iterator against the empty database."""
        database = client.get_database_client(empty_database_id)
        return _ids(database.list_containers())

    comparison = run_on_both_backends(_do, description="list_containers, empty database")
    comparison.print_report()
    comparison.assert_functional_parity()
    assert comparison.rust.return_value == []


def test_list_containers_paged_matches(populated_database_id):
    """Forcing several pages yields the same containers as a single-page read."""
    # One item per page checks that continuation tokens do not lose containers.

    def _do(client):
        """List with ``max_item_count=1`` so continuation tokens are exercised."""
        database = client.get_database_client(populated_database_id)
        return _ids(database.list_containers(max_item_count=1))

    comparison = run_on_both_backends(_do, description="list_containers, one container per page")
    comparison.print_report()
    comparison.assert_functional_parity()
    assert len(comparison.rust.return_value) == CONTAINER_COUNT
