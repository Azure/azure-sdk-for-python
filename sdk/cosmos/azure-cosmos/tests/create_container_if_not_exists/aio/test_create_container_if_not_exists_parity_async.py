# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Side-by-side comparison tests for async ``DatabaseProxy.create_container_if_not_exists``.

Why these exist: the async client is a separate code path from the sync client,
so a sync comparison passing says nothing about the async one. This call has
two legs: if the container is not there it creates it, and if it is already
there it reads it and returns that instead. Application startup code calls it
on every process start, so the second leg runs far more often than the first,
and the two legs go down different lines of code. The legacy copies in this
folder run the old v4 checks on rust alone, so they catch a wrong return shape
but not rust taking the wrong leg. These tests do: same id, both engines,
compare.

What they do: each test uses ``run_on_both_backends_async``, which builds one
core-python client and one rust client, awaits the same closure against each,
and records the returned value, the response headers and any exception. For the
create leg a create cannot be repeated with the same id, so the closure derives
its container id from the engine it is running on -- ``_observed_backend_name``
reports which client it was handed -- and ``_normalize_container`` drops the id
so the two compare on settings alone. For the existing leg both engines
deliberately use the *same* id, because the whole point is that neither of them
creates anything.

Four cases, matching the sync file: the create leg, the existing leg, the
existing container's settings, and the ``return_properties`` shape on the
existing leg.

Scaffolding runs on the sync client on purpose. The call under test is the
async one inside each test; using a sync fixture avoids holding an event loop
open across the fixture boundary.

They run only when a real account and the compiled rust binding are both
present.

Run with::

    pytest --noconftest tests/create_container_if_not_exists/aio/test_create_container_if_not_exists_parity_async.py -v
"""
from __future__ import annotations

import os
import uuid

import pytest

from azure.cosmos import CosmosClient
from azure.cosmos.aio import ContainerProxy
from azure.cosmos.partition_key import PartitionKey
from common._parity_helpers import (
    _observed_backend_name,
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
    name = "parity_ccine_a_" + uuid.uuid4().hex[:8]
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


async def test_create_leg_async(database_id):
    """When the container is not there, both engines create it with the same settings."""

    async def _do(client):
        """Await ``create_container_if_not_exists`` on a fresh id and return its type and settings."""
        database = client.get_database_client(database_id)
        container = await database.create_container_if_not_exists(
            id="fresh_" + _observed_backend_name(client).replace("-", "_"),
            partition_key=PartitionKey(path="/pk", kind="Hash"),
        )
        return {
            "is_proxy": isinstance(container, ContainerProxy),
            "settings": _normalize_container(await container.read()),
        }

    comparison = await run_on_both_backends_async(
        _do, description="async create_container_if_not_exists, create leg"
    )
    comparison.print_report()
    comparison.assert_functional_parity()
    assert comparison.rust.return_value["is_proxy"] is True
    assert comparison.rust.return_value["settings"]["partitionKey"]["paths"] == ["/pk"]


async def test_existing_leg_returns_existing_container_async(database_id, existing_container_id):
    """When the container is already there, both engines return it rather than a new one."""
    # Both engines use the same id on purpose here: neither of them should be
    # creating anything, so there is nothing to collide.

    async def _do(client):
        """Await ``create_container_if_not_exists`` on an existing id and return the proxy and its id."""
        database = client.get_database_client(database_id)
        container = await database.create_container_if_not_exists(
            id=existing_container_id,
            partition_key=PartitionKey(path="/original", kind="Hash"),
        )
        return {"is_proxy": isinstance(container, ContainerProxy), "id": container.id}

    comparison = await run_on_both_backends_async(
        _do, description="async create_container_if_not_exists, existing leg"
    )
    comparison.print_report()
    comparison.assert_functional_parity()
    assert comparison.core_python.return_value["id"] == existing_container_id
    assert comparison.rust.return_value["id"] == existing_container_id


async def test_existing_leg_preserves_settings_async(database_id, existing_container_id):
    """The existing container keeps the settings it was created with on both engines."""
    # This is what catches the worst failure available to this call: taking the
    # create leg on a container that already exists would replace a customer's
    # container, and the returned proxy would look correct while the settings
    # underneath it silently reverted to the ones passed in.

    async def _do(client):
        """Await ``create_container_if_not_exists`` on an existing id and return the normalised settings."""
        database = client.get_database_client(database_id)
        container = await database.create_container_if_not_exists(
            id=existing_container_id,
            partition_key=PartitionKey(path="/original", kind="Hash"),
        )
        return _normalize_container(await container.read())

    comparison = await run_on_both_backends_async(
        _do, description="async create_container_if_not_exists, existing settings preserved"
    )
    comparison.print_report()
    comparison.assert_functional_parity()
    assert comparison.rust.return_value["partitionKey"]["paths"] == ["/original"]
    assert "/excluded/*" in comparison.rust.return_value["excludedPaths"]


async def test_existing_leg_return_properties_shape_async(database_id, existing_container_id):
    """With return_properties set, the existing leg gives the same pair on both engines."""
    # The headers in the second half are where a customer reads what the call
    # cost, and the existing leg costs less than the create leg. If rust left
    # them out, cost reporting would go quiet without any error.

    async def _do(client):
        """Await ``create_container_if_not_exists`` with ``return_properties`` and return the result shape."""
        database = client.get_database_client(database_id)
        result = await database.create_container_if_not_exists(
            id=existing_container_id,
            partition_key=PartitionKey(path="/original", kind="Hash"),
            return_properties=True,
        )
        return {
            "pair_length": len(result),
            "first_is_proxy": isinstance(result[0], ContainerProxy),
            "has_headers": len(result[1].get_response_headers()) > 0,
        }

    comparison = await run_on_both_backends_async(
        _do, description="async create_container_if_not_exists, existing leg with properties"
    )
    comparison.print_report()
    comparison.assert_functional_parity()
    assert comparison.rust.return_value == {
        "pair_length": 2,
        "first_is_proxy": True,
        "has_headers": True,
    }
