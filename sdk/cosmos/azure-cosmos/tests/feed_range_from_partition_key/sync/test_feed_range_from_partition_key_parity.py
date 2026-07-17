# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Parity tests for ``Container.feed_range_from_partition_key``.

Each test runs the same call once on core-python and once on rust, then compares the
returned feed-range value. During migration, rust must return the same feed-range for a
given partition key so callers can safely reuse that value in downstream APIs.

These tests prove the two backends agree with each other across every key shape a customer can pass:
string, JSON-null, numeric, bool, NonePartitionKeyValue, and hierarchical full and prefix
keys. Without them, nothing would prove rust returns the same opaque value for those shapes,
and a hierarchical/prefix mismatch would reach customers as a silently wrong feed-range.
The hierarchical cases auto-skip when the account/emulator cannot create a MultiHash
container, which is why those shapes stay verified-by-implementation rather than fully
emulator-verified there.
"""
from __future__ import annotations

import os
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.partition_key import NonePartitionKeyValue
from common._parity_helpers import (
    run_on_both_backends,
    skip_unless_emulator,
    skip_unless_rust_binding,
)

pytestmark = [skip_unless_emulator(), skip_unless_rust_binding()]


@pytest.fixture
def container_for(request):
    # Fresh throwaway container per test, deleted afterward, so tests don't share data.
    client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])
    db = client.create_database_if_not_exists("parity_db")
    container_id = "parity_feed_range_from_pk_" + request.node.name + "_" + uuid.uuid4().hex[:6]
    container = db.create_container(id=container_id, partition_key=PartitionKey(path="/pk"))
    yield container
    try:
        db.delete_container(container_id)
    except Exception:  # pylint: disable=broad-except
        pass


@pytest.fixture
def container_for_multihash(request):
    # Dedicated hierarchical-PK container for full/prefix feed-range parity checks.
    client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])
    db = client.create_database_if_not_exists("parity_db")
    container_id = "parity_feed_range_from_pk_hpk_" + request.node.name + "_" + uuid.uuid4().hex[:6]
    try:
        container = db.create_container(
            id=container_id,
            partition_key=PartitionKey(path=["/tenant", "/region"], kind="MultiHash"),
        )
    except Exception as exc:  # pylint: disable=broad-except
        pytest.skip("Hierarchical partition-key container unsupported in this account/emulator: {}".format(exc))
    yield container
    try:
        db.delete_container(container_id)
    except Exception:  # pylint: disable=broad-except
        pass


def _normalize_feed_range(feed_range):
    range_info = feed_range["Range"]
    return (
        range_info["min"].upper(),
        range_info["max"].upper(),
        bool(range_info["isMinInclusive"]),
        bool(range_info["isMaxInclusive"]),
    )


def test_L0_feed_range_from_partition_key_baseline(container_for):
    """String partition key produces the same feed range on both backends."""
    run_suffix = uuid.uuid4().hex

    def _do(client):
        container = client.get_database_client("parity_db").get_container_client(container_for.id)
        pk_value = "pk-" + run_suffix[:8]
        container.upsert_item({"id": "id-" + run_suffix, "pk": pk_value})
        return _normalize_feed_range(container.feed_range_from_partition_key(pk_value))

    comparison = run_on_both_backends(
        _do,
        description="[L0] feed_range_from_partition_key baseline",
        request_kwargs={"partition_key": "string"},
    )
    comparison.print_report()
    comparison.assert_functional_parity()


def test_L2_feed_range_from_partition_key_numeric_partition_key(container_for):
    """Numeric partition key produces the same feed range on both backends."""
    run_suffix = uuid.uuid4().hex

    def _do(client):
        container = client.get_database_client("parity_db").get_container_client(container_for.id)
        pk_value = 4242
        container.upsert_item({"id": "id-num-" + run_suffix, "pk": pk_value})
        return _normalize_feed_range(container.feed_range_from_partition_key(pk_value))

    comparison = run_on_both_backends(
        _do,
        description="[L2] feed_range_from_partition_key numeric partition key",
        request_kwargs={"partition_key": 4242},
    )
    comparison.print_report()
    comparison.assert_functional_parity()


def test_L3_feed_range_from_partition_key_bool_partition_key(container_for):
    """Boolean partition key produces the same feed range on both backends."""
    run_suffix = uuid.uuid4().hex

    def _do(client):
        container = client.get_database_client("parity_db").get_container_client(container_for.id)
        pk_value = True
        container.upsert_item({"id": "id-bool-" + run_suffix, "pk": pk_value})
        return _normalize_feed_range(container.feed_range_from_partition_key(pk_value))

    comparison = run_on_both_backends(
        _do,
        description="[L3] feed_range_from_partition_key bool partition key",
        request_kwargs={"partition_key": True},
    )
    comparison.print_report()
    comparison.assert_functional_parity()


def test_L4_feed_range_from_partition_key_none_partition_key_value_branch(container_for):
    """NonePartitionKeyValue branch (`_Undefined` on non-system containers) is parity-safe."""

    def _do(client):
        container = client.get_database_client("parity_db").get_container_client(container_for.id)
        return _normalize_feed_range(container.feed_range_from_partition_key(NonePartitionKeyValue))

    comparison = run_on_both_backends(
        _do,
        description="[L4] feed_range_from_partition_key NonePartitionKeyValue branch",
        request_kwargs={"partition_key": "NonePartitionKeyValue"},
    )
    comparison.print_report()
    comparison.assert_functional_parity()


def test_L5_feed_range_from_partition_key_hpk_full_key(container_for_multihash):
    """Hierarchical full key (all PK components) is parity-safe."""
    run_suffix = uuid.uuid4().hex

    def _do(client):
        container = client.get_database_client("parity_db").get_container_client(container_for_multihash.id)
        tenant = "tenant-" + run_suffix[:4]
        region = "region-" + run_suffix[4:8]
        container.upsert_item({"id": "id-hpk-full-" + run_suffix, "tenant": tenant, "region": region})
        return _normalize_feed_range(container.feed_range_from_partition_key([tenant, region]))

    comparison = run_on_both_backends(
        _do,
        description="[L5] feed_range_from_partition_key hierarchical full key",
        request_kwargs={"partition_key": ["tenant", "region"]},
    )
    comparison.print_report()
    comparison.assert_functional_parity()


def test_L6_feed_range_from_partition_key_hpk_prefix_key(container_for_multihash):
    """Hierarchical prefix key (partial PK components) is parity-safe."""
    run_suffix = uuid.uuid4().hex

    def _do(client):
        container = client.get_database_client("parity_db").get_container_client(container_for_multihash.id)
        tenant = "tenant-" + run_suffix[:4]
        container.upsert_item({"id": "id-hpk-prefix-" + run_suffix, "tenant": tenant, "region": "region-a"})
        return _normalize_feed_range(container.feed_range_from_partition_key([tenant]))

    comparison = run_on_both_backends(
        _do,
        description="[L6] feed_range_from_partition_key hierarchical prefix key",
        request_kwargs={"partition_key": ["tenant"]},
    )
    comparison.print_report()
    comparison.assert_functional_parity()


def test_L1_feed_range_from_partition_key_null_partition_key(container_for):
    """JSON-null partition key maps to the same feed range on both backends."""

    def _do(client):
        container = client.get_database_client("parity_db").get_container_client(container_for.id)
        return _normalize_feed_range(container.feed_range_from_partition_key(None))

    comparison = run_on_both_backends(
        _do,
        description="[L1] feed_range_from_partition_key null partition key",
        request_kwargs={"partition_key": None},
    )
    comparison.print_report()
    comparison.assert_functional_parity()
