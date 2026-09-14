# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Check ``ContainerProxy.read`` results on Python and Rust.

Here, parity means matching public behavior between Python and Rust. These
tests prove that stored partition-key and indexing settings match and that a
missing container raises the same typed error. Quota and partition statistics
must use the selected backend and retain their requested data. Customers use
these settings to inspect storage and request costs.
"""
from __future__ import annotations

import os
import uuid

import pytest
from azure.core import MatchConditions

from azure.cosmos import CosmosClient, exceptions
from azure.cosmos.partition_key import PartitionKey
from common._parity_helpers import (
    run_target_operation,
    run_on_both_backends,
    skip_unless_emulator,
    skip_unless_rust_binding,
)

pytestmark = [skip_unless_emulator(), skip_unless_rust_binding()]


def _admin_client():
    """A privileged client for database and container setup and teardown, not the client under test."""
    return CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")


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


@pytest.fixture(scope="module")
def database_id():
    """A throwaway database, deleted after the test."""
    client = _admin_client()
    name = "parity_read_container_" + uuid.uuid4().hex
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
def container_id(database_id):
    """A container with a non-default indexing policy, so the read has something to lose."""
    client = _admin_client()
    name = "read_target_" + uuid.uuid4().hex[:8]
    try:
        client.get_database_client(database_id).create_container(
            id=name,
            partition_key=PartitionKey(path="/pk", kind="Hash"),
            indexing_policy={
                "indexingMode": "consistent",
                "includedPaths": [{"path": "/*"}],
                "excludedPaths": [{"path": "/excluded/*"}],
            },
        )
        yield name
    finally:
        client.close()


def test_read_container_properties(database_id, container_id):
    """read returns the same partition key and indexing policy on both engines."""

    def _do(client):
        """Read the container and return its normalised properties."""
        container = client.get_database_client(database_id).get_container_client(container_id)
        return _normalize_container(run_target_operation(client, container.read))

    comparison = run_on_both_backends(_do, description="container read, custom indexing policy")
    comparison.print_report()
    comparison.assert_functional_parity()
    assert comparison.core_python.return_value["partitionKey"]["paths"] == ["/pk"]
    assert "/excluded/*" in comparison.core_python.return_value["excludedPaths"]


@pytest.mark.parametrize("quota,statistics", [(True, False), (False, True), (True, True), (False, False), (None, None)])
def test_read_container_quota_and_statistics_use_selected_backend(database_id, container_id, quota, statistics):
    """Requested statistics and quota values match, with no Rust-to-Python fallback."""
    def read_metadata(client):
        container = client.get_database_client(database_id).get_container_client(container_id)
        properties = run_target_operation(
            client, lambda: container.read(
                populate_partition_key_range_statistics=statistics,
                populate_quota_info=quota, read_timeout=None,
            ),
        )
        headers = properties.get_response_headers()
        assert ("statistics" in properties) == bool(statistics)
        assert ("x-ms-resource-usage" in headers) == bool(quota)
        assert ("x-ms-resource-quota" in headers) == bool(quota)
        return {
            "properties": _normalize_container(properties),
            "statistics": properties.get("statistics"),
            "quota": headers.get("x-ms-resource-quota"),
            "usage": headers.get("x-ms-resource-usage"),
        }

    comparison = run_on_both_backends(read_metadata, description="container metadata extras")
    comparison.print_report()
    comparison.assert_functional_parity()


@pytest.mark.parametrize("condition", [MatchConditions.IfPresent, MatchConditions.IfNotModified])
def test_read_container_conditions(database_id, container_id, condition):
    def read_conditionally(client):
        container = client.get_database_client(database_id).get_container_client(container_id)
        etag = container.read()["_etag"] if condition == MatchConditions.IfNotModified else '"unused"'
        return _normalize_container(run_target_operation(
            client, lambda: container.read(etag=etag, match_condition=condition),
        ))

    run_on_both_backends(read_conditionally, description="conditional container read").assert_functional_parity()


def test_read_container_response_hook_cannot_change_cached_partition_key(database_id, container_id):
    def read_with_hook(client):
        container = client.get_database_client(database_id).get_container_client(container_id)
        calls = []

        def response_hook(headers, properties):
            calls.append(properties["id"])
            headers.clear()
            properties["partitionKey"]["paths"][0] = "/changed-by-hook"
            properties["indexingPolicy"].clear()

        properties = run_target_operation(client, lambda: container.read(response_hook=response_hook))
        assert calls == [container_id]
        assert properties.get_response_headers()
        assert properties["partitionKey"]["paths"] == ["/pk"]
        assert properties["indexingPolicy"]
        cached = client.client_connection._container_properties_cache[container.container_link]
        assert cached["partitionKey"]["paths"] == ["/pk"]
        return _normalize_container(properties)

    run_on_both_backends(read_with_hook, description="container response-hook isolation").assert_functional_parity()


def test_read_missing_container_raises_404(database_id):
    """Reading a container that is not there raises the same typed 404 on both engines."""
    missing_id = "never_created_" + uuid.uuid4().hex[:8]

    def _do(client):
        """Attempt to read a container that does not exist, expecting a 404 error."""
        container = client.get_database_client(database_id).get_container_client(missing_id)
        return run_target_operation(client, container.read)

    comparison = run_on_both_backends(_do, description="container read, missing container")
    comparison.print_report()
    comparison.assert_functional_exception_parity()
    assert isinstance(comparison.rust.raised, exceptions.CosmosResourceNotFoundError)
    assert isinstance(comparison.core_python.raised, exceptions.CosmosResourceNotFoundError)
    assert comparison.rust.raised.status_code == 404
