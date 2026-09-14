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

from azure.cosmos import CosmosClient, exceptions
from azure.cosmos.partition_key import PartitionKey
from common._parity_helpers import (
    run_on_both_backends,
    run_target_operation,
    skip_unless_emulator,
    skip_unless_rust_binding,
)

pytestmark = [skip_unless_emulator(), skip_unless_rust_binding()]

CONTAINER_COUNT = 3


def _admin_client():
    """Return a plain ``CosmosClient`` for fixture setup and teardown."""
    return CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="core-python")


def _ids(containers):
    """Return sorted container ids so order-insensitive membership can be compared."""
    return sorted(container["id"] for container in containers)


@pytest.fixture(scope="module")
def empty_database_id():
    """A database with no containers at all."""
    client = _admin_client()
    name = "parity_list_containers_empty_" + uuid.uuid4().hex[:8]
    try:
        client.create_database(id=name)
        yield name
    finally:
        try:
            client.delete_database(name)
        except exceptions.CosmosResourceNotFoundError:
            pass
        finally:
            client.close()


@pytest.fixture(scope="module")
def populated_database_id():
    """A database holding a known set of containers."""
    client = _admin_client()
    name = "parity_list_containers_" + uuid.uuid4().hex[:8]
    try:
        database = client.create_database(id=name)
        for index in range(CONTAINER_COUNT):
            database.create_container(
                id="c{}".format(index),
                partition_key=PartitionKey(path="/pk", kind="Hash"),
            )
        yield name
    finally:
        try:
            client.delete_database(name)
        except exceptions.CosmosResourceNotFoundError:
            pass
        finally:
            client.close()


def test_list_containers_returns_same_ids(populated_database_id):
    """Both engines report the same set of containers for the same database."""

    def _do(client):
        """Collect and sort container ids from the sync iterator."""
        database = client.get_database_client(populated_database_id)
        return run_target_operation(client, lambda: _ids(database.list_containers()))

    comparison = run_on_both_backends(_do, description="list_containers, populated database")
    comparison.print_report()
    assert comparison.core_python.raised is None and comparison.rust.raised is None
    comparison.assert_functional_parity()
    assert comparison.rust.return_value == ["c0", "c1", "c2"]


def test_list_containers_on_empty_database_returns_empty(empty_database_id):
    """A database with no containers yields an empty list on both engines, not an error."""

    def _do(client):
        """Drain the sync iterator against the empty database."""
        database = client.get_database_client(empty_database_id)
        return run_target_operation(client, lambda: _ids(database.list_containers()))

    comparison = run_on_both_backends(_do, description="list_containers, empty database")
    comparison.print_report()
    assert comparison.core_python.raised is None and comparison.rust.raised is None
    comparison.assert_functional_parity()
    assert comparison.rust.return_value == []


def test_list_containers_paged_matches(populated_database_id):
    """Forcing several pages yields the same containers as a single-page read."""
    # One item per page checks that continuation tokens do not lose containers.

    def _do(client):
        """List with ``max_item_count=1`` so continuation tokens are exercised."""
        database = client.get_database_client(populated_database_id)
        def target():
            pages = [list(page) for page in database.list_containers(max_item_count=1).by_page()]
            assert len(pages) == CONTAINER_COUNT
            assert all(len(page) == 1 for page in pages)
            return _ids([item for page in pages for item in page])
        return run_target_operation(client, target)

    comparison = run_on_both_backends(_do, description="list_containers, one container per page")
    comparison.print_report()
    assert comparison.core_python.raised is None and comparison.rust.raised is None
    comparison.assert_functional_parity()
    assert comparison.rust.return_value == ["c0", "c1", "c2"]


def test_list_containers_continuation_resume(populated_database_id):
    def run(client):
        database = client.get_database_client(populated_database_id)

        def target():
            pages = database.list_containers(max_item_count=1).by_page()
            first = list(next(pages))
            token = pages.continuation_token
            assert len(first) == 1 and token
            rest = [item for page in pages for item in page]
            replay = [item for page in database.list_containers(max_item_count=1).by_page(
                continuation_token=token
            ) for item in page]
            assert replay == rest
            assert not set(_ids(first)).intersection(_ids(rest))
            return _ids(first + replay)
        return run_target_operation(client, target)

    comparison = run_on_both_backends(run, description="list_containers bookmark resumption")
    assert comparison.core_python.raised is None and comparison.rust.raised is None
    comparison.assert_functional_parity()
    assert comparison.rust.return_value == ["c0", "c1", "c2"]


def test_list_containers_options_and_page_hooks(populated_database_id):
    def run(client):
        database = client.get_database_client(populated_database_id)

        def target():
            snapshots = []

            class Hook:
                def __bool__(self):
                    return False

                def __call__(self, headers):
                    assert headers["x-ms-activity-id"]
                    assert float(headers["x-ms-request-charge"]) > 0
                    if client.client_connection._backend.name == "rust":
                        assert headers["x-ms-cosmos-sdk-diagnostics"]
                    headers["x-hook-mutation"] = "isolated"
                    snapshots.append(headers)

            pager = database.list_containers(
                max_item_count=1, timeout=10, read_timeout=None,
                initial_headers={"x-company-trace": "list-containers"}, response_hook=Hook(),
            )
            assert snapshots == []
            rows = []
            for page in pager.by_page():
                rows.extend(page)
                assert "x-hook-mutation" not in client.client_connection.last_response_headers
            assert len(snapshots) == CONTAINER_COUNT
            assert len({headers["x-ms-activity-id"] for headers in snapshots}) == CONTAINER_COUNT
            return _ids(rows)
        return run_target_operation(client, target)

    comparison = run_on_both_backends(run, description="list_containers lazy page hooks and timeout")
    assert comparison.core_python.raised is None and comparison.rust.raised is None
    comparison.assert_functional_parity()
    assert comparison.rust.return_value == ["c0", "c1", "c2"]
