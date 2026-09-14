# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Check async ``create_container`` results on Python and Rust.

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
from azure.core import MatchConditions

from azure.cosmos import CosmosClient, exceptions
from azure.cosmos.aio import ContainerProxy
from azure.cosmos.partition_key import PartitionKey
from common._parity_helpers import (
    _observed_backend_name,
    run_on_both_backends_async,
    run_target_operation_async,
    skip_unless_emulator,
    skip_unless_rust_binding,
)

pytestmark = [skip_unless_emulator(), skip_unless_rust_binding(), pytest.mark.asyncio]


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


@pytest.fixture(scope="module")
def database_id():
    """A throwaway database, deleted after the test along with everything created in it."""
    name = "parity_create_container_a_" + uuid.uuid4().hex[:8]
    with _admin_client() as client:
        try:
            client.create_database(id=name)
            yield name
        finally:
            try:
                client.delete_database(name)
            except exceptions.CosmosResourceNotFoundError:
                pass  # Creation may have failed before reaching the service.


def _per_engine_id(client, prefix):
    """Return a container id unique to this engine, so both engines can call create without conflict."""
    # A create cannot be repeated with the same id, so each engine gets its own.
    return "{}_{}".format(prefix, _observed_backend_name(client).replace("-", "_"))


async def test_create_container_with_explicit_settings_async(database_id):
    """Both engines create a container with the settings that were asked for."""

    async def _do(client):
        """Await a create with explicit settings and return the normalised properties."""
        database = client.get_database_client(database_id)
        container = await run_target_operation_async(client, lambda: database.create_container(
            id=_per_engine_id(client, "explicit"),
            partition_key=PartitionKey(path="/pk", kind="Hash"),
            indexing_policy={
                "indexingMode": "consistent",
                "automatic": True,
                "includedPaths": [{"path": "/*"}],
                "excludedPaths": [{"path": "/excluded/*"}],
            },
        ))
        return _normalize_container(await container.read())

    comparison = await run_on_both_backends_async(
        _do, description="async create_container, explicit partition key and indexing policy"
    )
    comparison.print_report()
    assert comparison.core_python.raised is None
    assert comparison.rust.raised is None
    comparison.assert_functional_parity()
    assert comparison.core_python.return_value["partitionKey"]["paths"] == ["/pk"]
    assert "/excluded/*" in comparison.rust.return_value["excludedPaths"]


async def test_create_container_default_indexing_policy_async(database_id):
    """With no indexing policy given, both engines get the same policy back from the service."""

    async def _do(client):
        """Await a create without an explicit indexing policy and return the normalised properties."""
        database = client.get_database_client(database_id)
        container = await run_target_operation_async(client, lambda: database.create_container(
            id=_per_engine_id(client, "defaults"),
            partition_key=PartitionKey(path="/pk", kind="Hash"),
        ))
        return _normalize_container(await container.read())

    comparison = await run_on_both_backends_async(
        _do, description="async create_container, no indexing policy given"
    )
    comparison.print_report()
    assert comparison.core_python.raised is None
    assert comparison.rust.raised is None
    comparison.assert_functional_parity()
    assert comparison.core_python.return_value["includedPaths"] == ["/*"]


async def test_create_container_return_shapes_async(database_id):
    """Both return shapes come back the same on both engines."""

    async def _do(client):
        """Await creates for both documented return shapes."""
        database = client.get_database_client(database_id)
        proxy_only = await run_target_operation_async(client, lambda: database.create_container(
            id=_per_engine_id(client, "shape_proxy"),
            partition_key=PartitionKey(path="/pk", kind="Hash"),
        ))
        with_properties = await run_target_operation_async(client, lambda: database.create_container(
            id=_per_engine_id(client, "shape_props"),
            partition_key=PartitionKey(path="/pk", kind="Hash"),
            return_properties=True,
        ))
        return {
            "default_is_proxy": isinstance(proxy_only, ContainerProxy),
            "pair_length": len(with_properties),
            "pair_first_is_proxy": isinstance(with_properties[0], ContainerProxy),
            "has_headers": len(with_properties[1].get_response_headers()) > 0,
        }

    comparison = await run_on_both_backends_async(
        _do, description="async create_container, both return shapes"
    )
    comparison.print_report()
    assert comparison.core_python.raised is None
    assert comparison.rust.raised is None
    comparison.assert_functional_parity()
    assert comparison.rust.return_value == {
        "default_is_proxy": True,
        "pair_length": 2,
        "pair_first_is_proxy": True,
        "has_headers": True,
    }


async def test_create_container_conflict_async(database_id):
    """Creating a container whose id is taken raises the same typed conflict on both engines."""
    taken_id = "already_taken_" + uuid.uuid4().hex[:8]
    admin = _admin_client()
    admin.get_database_client(database_id).create_container(
        id=taken_id, partition_key=PartitionKey(path="/pk", kind="Hash")
    )
    admin.close()

    async def _do(client):
        """Await a create whose id is taken, expecting a conflict error."""
        database = client.get_database_client(database_id)
        return await run_target_operation_async(client, lambda: database.create_container(
            id=taken_id, partition_key=PartitionKey(path="/pk", kind="Hash")
        ))

    comparison = await run_on_both_backends_async(
        _do, description="async create_container, id already taken"
    )
    comparison.print_report()
    comparison.assert_functional_exception_parity()
    assert isinstance(comparison.rust.raised, exceptions.CosmosResourceExistsError)
    assert isinstance(comparison.core_python.raised, exceptions.CosmosResourceExistsError)
    assert comparison.rust.raised.status_code == 409


async def test_create_container_supported_options_and_hook_async(database_id):
    async def _do(client):
        database = client.get_database_client(database_id)
        hooks = []

        def hook(headers, body):
            assert "X-MS-REQUEST-CHARGE" in headers
            hooks.append((headers, body))
            headers["x-hook-only"] = "private"

        container, properties = await run_target_operation_async(client, lambda: database.create_container(
            _per_engine_id(client, "options"), PartitionKey(path="/tenant"),
            default_ttl=3600, unique_key_policy={"uniqueKeys": [{"paths": ["/code"]}]},
            timeout=10, read_timeout=None, initial_headers={"x-my-app": "provisioner"},
            response_hook=hook, return_properties=True,
        ))
        assert len(hooks) == 1
        assert hooks[0][1] is properties
        assert container.id == properties["id"]
        assert "x-hook-only" not in properties.get_response_headers()
        assert "x-hook-only" not in client.client_connection.last_response_headers
        assert properties["defaultTtl"] == 3600
        assert properties["uniqueKeyPolicy"] == {"uniqueKeys": [{"paths": ["/code"]}]}
        return {"ttl": properties["defaultTtl"], "unique_key_policy": properties["uniqueKeyPolicy"],
                "hook_count": len(hooks)}

    comparison = await run_on_both_backends_async(
        _do, description="async create_container supported options and isolated hook",
    )
    assert comparison.core_python.raised is None
    assert comparison.rust.raised is None
    comparison.assert_functional_parity()


@pytest.mark.parametrize("condition", [MatchConditions.IfNotModified, MatchConditions.IfModified, MatchConditions.IfPresent])
async def test_create_container_preserves_conditional_request_behavior_async(database_id, condition):
    async def _do(client):
        database = client.get_database_client(database_id)
        container = await run_target_operation_async(client, lambda: database.create_container(
            _per_engine_id(client, "condition_" + condition.name), PartitionKey(path="/pk"),
            etag='"unused"', match_condition=condition,
        ))
        return {"created_expected_id": container.id == _per_engine_id(client, "condition_" + condition.name)}

    comparison = await run_on_both_backends_async(_do, description=f"async create_container conditional {condition.name}")
    assert comparison.core_python.raised is None
    assert comparison.rust.raised is None
    assert comparison.rust.return_value == {"created_expected_id": True}
    comparison.assert_functional_parity()
