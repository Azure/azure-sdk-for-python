# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Side-by-side comparison tests for ``DatabaseProxy.create_container_if_not_exists``.

Why these exist: this call has two legs. If the container is not there it
creates it; if it is already there it reads it and returns that instead.
Application startup code calls it on every process start, so the second leg
runs far more often than the first, and the two legs go down different lines of
code. The legacy copies in this folder run the old v4 checks on rust alone, so
they catch a wrong return shape. They cannot catch rust taking the wrong leg --
recreating a container that already exists, or returning settings that differ
from what core-python returns -- because they never run core-python. These
tests do: same id, both engines, compare.

What they do: each test uses ``run_on_both_backends``, which builds one
core-python client and one rust client, runs the same closure against each, and
records the returned value, the response headers and any exception. For the
create leg a create cannot be repeated with the same id, so the closure derives
its container id from the engine it is running on -- ``_observed_backend_name``
reports which client it was handed -- and ``_normalize_container`` drops the id
so the two compare on settings alone. For the existing leg both engines
deliberately use the *same* id, because the whole point is that neither of them
creates anything.

Four cases, each covering something the others do not:

* the create leg, where the container is not there yet;
* the existing leg, where it is -- this is the leg that runs on every restart;
* the existing leg checked against the container's real settings, which is what
  catches rust silently replacing a container instead of reading it;
* the ``return_properties`` shape on the existing leg, since that is where a
  customer reads what the call cost, and the cost differs between the legs.

They run only when a real account and the compiled rust binding are both
present.

Run with::

    pytest --noconftest tests/create_container_if_not_exists/sync/test_create_container_if_not_exists_parity.py -v
"""
from __future__ import annotations

import os
import uuid

import pytest

from azure.cosmos import ContainerProxy, CosmosClient
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
    # Drop the id along with the server-stamped fields, so a create-leg result
    # from one engine compares against the other despite different names.
    return {
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
    name = "parity_ccine_" + uuid.uuid4().hex[:8]
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
def existing_container_id(database_id):
    """A container that is already there, with settings the call must not change."""
    client = _admin_client()
    name = "existing_" + uuid.uuid4().hex[:8]
    client.get_database_client(database_id).create_container(
        id=name,
        partition_key=PartitionKey(path="/original", kind="Hash"),
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


def test_create_leg(database_id):
    """When the container is not there, both engines create it with the same settings."""
    # This is the leg that runs once, on a customer's very first deployment.

    def _do(client):
        """Call ``create_container_if_not_exists`` on a fresh id and return its type and settings."""
        database = client.get_database_client(database_id)
        container = database.create_container_if_not_exists(
            id="fresh_" + _observed_backend_name(client).replace("-", "_"),
            partition_key=PartitionKey(path="/pk", kind="Hash"),
        )
        return {
            "is_proxy": isinstance(container, ContainerProxy),
            "settings": _normalize_container(container.read()),
        }

    comparison = run_on_both_backends(
        _do, description="create_container_if_not_exists, create leg"
    )
    comparison.print_report()
    comparison.assert_functional_parity()
    assert comparison.rust.return_value["is_proxy"] is True
    assert comparison.rust.return_value["settings"]["partitionKey"]["paths"] == ["/pk"]


def test_existing_leg_returns_existing_container(database_id, existing_container_id):
    """When the container is already there, both engines return it rather than a new one."""
    # Both engines use the same id on purpose here: neither of them should be
    # creating anything, so there is nothing to collide.

    def _do(client):
        """Call ``create_container_if_not_exists`` on an existing id and return the proxy and its id."""
        database = client.get_database_client(database_id)
        container = database.create_container_if_not_exists(
            id=existing_container_id,
            partition_key=PartitionKey(path="/original", kind="Hash"),
        )
        return {"is_proxy": isinstance(container, ContainerProxy), "id": container.id}

    comparison = run_on_both_backends(
        _do, description="create_container_if_not_exists, existing leg"
    )
    comparison.print_report()
    comparison.assert_functional_parity()
    assert comparison.core_python.return_value["id"] == existing_container_id
    assert comparison.rust.return_value["id"] == existing_container_id


def test_existing_leg_preserves_settings(database_id, existing_container_id):
    """The existing container keeps the settings it was created with on both engines."""
    # This is what catches the worst failure available to this call: taking the
    # create leg on a container that already exists would replace a customer's
    # container, and the returned proxy would look correct while the settings
    # underneath it silently reverted to the ones passed in.

    def _do(client):
        """Call ``create_container_if_not_exists`` on an existing id and return the normalised settings."""
        database = client.get_database_client(database_id)
        container = database.create_container_if_not_exists(
            id=existing_container_id,
            partition_key=PartitionKey(path="/original", kind="Hash"),
        )
        return _normalize_container(container.read())

    comparison = run_on_both_backends(
        _do, description="create_container_if_not_exists, existing settings preserved"
    )
    comparison.print_report()
    comparison.assert_functional_parity()
    assert comparison.rust.return_value["partitionKey"]["paths"] == ["/original"]
    assert "/excluded/*" in comparison.rust.return_value["excludedPaths"]


def test_existing_leg_return_properties_shape(database_id, existing_container_id):
    """With return_properties set, the existing leg gives the same pair on both engines."""
    # The headers in the second half are where a customer reads what the call
    # cost, and the existing leg costs less than the create leg. If rust left
    # them out, cost reporting would go quiet without any error.

    def _do(client):
        """Call ``create_container_if_not_exists`` with ``return_properties`` and return the result shape."""
        database = client.get_database_client(database_id)
        result = database.create_container_if_not_exists(
            id=existing_container_id,
            partition_key=PartitionKey(path="/original", kind="Hash"),
            return_properties=True,
        )
        return {
            "pair_length": len(result),
            "first_is_proxy": isinstance(result[0], ContainerProxy),
            "has_headers": len(result[1].get_response_headers()) > 0,
        }

    comparison = run_on_both_backends(
        _do, description="create_container_if_not_exists, existing leg with properties"
    )
    comparison.print_report()
    comparison.assert_functional_parity()
    assert comparison.rust.return_value == {
        "pair_length": 2,
        "first_is_proxy": True,
        "has_headers": True,
    }
