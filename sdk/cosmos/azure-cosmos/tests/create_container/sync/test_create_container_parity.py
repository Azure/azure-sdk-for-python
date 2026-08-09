# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Check ``create_container`` results on Python and Rust.

Here, parity means matching public behavior between Python and Rust. These
tests prove that requested partition-key and indexing settings are preserved,
both documented return shapes stay stable, and duplicate IDs raise the same
typed error. Customers cannot change a partition key after creation, so the
stored settings must be trustworthy.
"""
from __future__ import annotations

import os
import uuid

import pytest

from azure.cosmos import ContainerProxy, CosmosClient, exceptions
from azure.cosmos.partition_key import PartitionKey
from common._parity_helpers import (
    _observed_backend_name,
    run_on_both_backends,
    skip_unless_emulator,
    skip_unless_rust_binding,
)

pytestmark = [skip_unless_emulator(), skip_unless_rust_binding()]


def _admin_client():
    """A privileged client for database and container setup and teardown, not the client under test."""
    return CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])


def _normalize_container(properties):
    """Strip server-stamped fields, keeping only the settings the caller asked for."""
    # Drop the id along with the server-stamped fields. Each engine creates its
    # own container under its own name, so the names differ by design and only
    # the settings are meant to match.
    return {
        "partitionKey": dict(properties["partitionKey"]),
        "indexingMode": properties["indexingPolicy"]["indexingMode"],
        "automatic": properties["indexingPolicy"].get("automatic"),
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
    name = "parity_create_container_" + uuid.uuid4().hex[:8]
    client.create_database(id=name)
    try:
        yield name
    finally:
        try:
            client.delete_database(name)
        except Exception:  # pylint: disable=broad-except
            pass
        client.close()


def _per_engine_id(client, prefix):
    """Return a container id unique to this engine, so both engines can call create without conflict."""
    # A create cannot be repeated with the same id, so each engine gets its own.
    return "{}_{}".format(prefix, _observed_backend_name(client).replace("-", "_"))


def test_create_container_with_explicit_settings(database_id):
    """Both engines create a container with the settings that were asked for."""

    def _do(client):
        """Create a container with explicit settings and return the normalised properties."""
        database = client.get_database_client(database_id)
        container = database.create_container(
            id=_per_engine_id(client, "explicit"),
            partition_key=PartitionKey(path="/pk", kind="Hash"),
            indexing_policy={
                "indexingMode": "consistent",
                "automatic": True,
                "includedPaths": [{"path": "/*"}],
                "excludedPaths": [{"path": "/excluded/*"}],
            },
        )
        return _normalize_container(container.read())

    comparison = run_on_both_backends(
        _do, description="create_container, explicit partition key and indexing policy"
    )
    comparison.print_report()
    comparison.assert_functional_parity()
    assert comparison.core_python.return_value["partitionKey"]["paths"] == ["/pk"]
    assert "/excluded/*" in comparison.rust.return_value["excludedPaths"]


def test_create_container_default_indexing_policy(database_id):
    """With no indexing policy given, both engines get the same policy back from the service."""

    def _do(client):
        """Create a container without an explicit indexing policy and return the normalised properties."""
        database = client.get_database_client(database_id)
        container = database.create_container(
            id=_per_engine_id(client, "defaults"),
            partition_key=PartitionKey(path="/pk", kind="Hash"),
        )
        return _normalize_container(container.read())

    comparison = run_on_both_backends(
        _do, description="create_container, no indexing policy given"
    )
    comparison.print_report()
    comparison.assert_functional_parity()
    assert comparison.core_python.return_value["includedPaths"] == ["/*"]


def test_create_container_return_shapes(database_id):
    """Both return shapes come back the same on both engines."""

    def _do(client):
        """Create two containers to exercise both documented return shapes."""
        database = client.get_database_client(database_id)
        proxy_only = database.create_container(
            id=_per_engine_id(client, "shape_proxy"),
            partition_key=PartitionKey(path="/pk", kind="Hash"),
        )
        with_properties = database.create_container(
            id=_per_engine_id(client, "shape_props"),
            partition_key=PartitionKey(path="/pk", kind="Hash"),
            return_properties=True,
        )
        return {
            "default_is_proxy": isinstance(proxy_only, ContainerProxy),
            "pair_length": len(with_properties),
            "pair_first_is_proxy": isinstance(with_properties[0], ContainerProxy),
            "has_headers": len(with_properties[1].get_response_headers()) > 0,
        }

    comparison = run_on_both_backends(_do, description="create_container, both return shapes")
    comparison.print_report()
    comparison.assert_functional_parity()
    assert comparison.rust.return_value == {
        "default_is_proxy": True,
        "pair_length": 2,
        "pair_first_is_proxy": True,
        "has_headers": True,
    }


def test_create_container_conflict(database_id):
    """Creating a container whose id is taken raises the same typed conflict on both engines."""
    taken_id = "already_taken_" + uuid.uuid4().hex[:8]
    admin = _admin_client()
    admin.get_database_client(database_id).create_container(
        id=taken_id, partition_key=PartitionKey(path="/pk", kind="Hash")
    )
    admin.close()

    def _do(client):
        """Attempt to create a container whose id is taken, expecting a conflict error."""
        database = client.get_database_client(database_id)
        return database.create_container(
            id=taken_id, partition_key=PartitionKey(path="/pk", kind="Hash")
        )

    comparison = run_on_both_backends(_do, description="create_container, id already taken")
    comparison.print_report()
    comparison.assert_functional_exception_parity()
    assert isinstance(comparison.rust.raised, exceptions.CosmosResourceExistsError)
    assert isinstance(comparison.core_python.raised, exceptions.CosmosResourceExistsError)
    assert comparison.rust.raised.status_code == 409
