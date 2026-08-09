# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Async parity tests for ``Container.feed_range_from_partition_key``.

Each test runs the same async call once on core-python and once on rust, then compares the
returned feed-range value.

These tests prove the two backends agree with each other across every key shape
a customer can pass. Without them, an async-only divergence (for example the async path
building a different prepared request) would reach customers as a silently wrong
feed-range that the sync parity suite cannot catch.
"""
from __future__ import annotations

import os
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.partition_key import NonePartitionKeyValue
from common._parity_helpers import (
    run_on_both_backends_async,
    skip_unless_emulator,
    skip_unless_rust_binding,
)

pytestmark = [skip_unless_emulator(), skip_unless_rust_binding()]


@pytest.fixture
def container_for(request):
    # Fresh throwaway container per test, deleted afterward, so tests don't share data.
    client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])
    db = client.create_database_if_not_exists("parity_db")
    container_id = "parity_feed_range_from_pk_async_" + request.node.name + "_" + uuid.uuid4().hex[:6]
    container = db.create_container(id=container_id, partition_key=PartitionKey(path="/pk"))
    yield container
    try:
        db.delete_container(container_id)
    except Exception:  # pylint: disable=broad-except
        pass


@pytest.fixture
def container_for_multihash(request):
    # Dedicated hierarchical-PK container for full/prefix async parity checks.
    client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])
    db = client.create_database_if_not_exists("parity_db")
    container_id = "parity_feed_range_from_pk_hpk_async_" + request.node.name + "_" + uuid.uuid4().hex[:6]
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
    """Return comparable public boundaries and inclusion flags."""
    range_info = feed_range["Range"]
    return (
        range_info["min"].upper(),
        range_info["max"].upper(),
        bool(range_info["isMinInclusive"]),
        bool(range_info["isMaxInclusive"]),
    )


@pytest.mark.asyncio
async def test_L0_feed_range_from_partition_key_baseline_async(container_for):
    """Async string partition key produces the same feed range on both backends."""
    run_suffix = uuid.uuid4().hex

    async def _do(client):
        container = client.get_database_client("parity_db").get_container_client(container_for.id)
        pk_value = "pk-" + run_suffix[:8]
        await container.upsert_item({"id": "id-" + run_suffix, "pk": pk_value})
        feed_range = await container.feed_range_from_partition_key(pk_value)
        return _normalize_feed_range(feed_range)

    comparison = await run_on_both_backends_async(
        _do,
        description="[L0] async feed_range_from_partition_key baseline",
        request_kwargs={"partition_key": "string"},
    )
    comparison.print_report()
    comparison.assert_functional_parity()


@pytest.mark.asyncio
async def test_L2_feed_range_from_partition_key_numeric_partition_key_async(container_for):
    """Async numeric partition key produces the same feed range on both backends."""
    run_suffix = uuid.uuid4().hex

    async def _do(client):
        container = client.get_database_client("parity_db").get_container_client(container_for.id)
        pk_value = 4242
        await container.upsert_item({"id": "id-num-" + run_suffix, "pk": pk_value})
        feed_range = await container.feed_range_from_partition_key(pk_value)
        return _normalize_feed_range(feed_range)

    comparison = await run_on_both_backends_async(
        _do,
        description="[L2] async feed_range_from_partition_key numeric partition key",
        request_kwargs={"partition_key": 4242},
    )
    comparison.print_report()
    comparison.assert_functional_parity()


@pytest.mark.asyncio
async def test_L3_feed_range_from_partition_key_bool_partition_key_async(container_for):
    """Async boolean partition key produces the same feed range on both backends."""
    run_suffix = uuid.uuid4().hex

    async def _do(client):
        container = client.get_database_client("parity_db").get_container_client(container_for.id)
        pk_value = True
        await container.upsert_item({"id": "id-bool-" + run_suffix, "pk": pk_value})
        feed_range = await container.feed_range_from_partition_key(pk_value)
        return _normalize_feed_range(feed_range)

    comparison = await run_on_both_backends_async(
        _do,
        description="[L3] async feed_range_from_partition_key bool partition key",
        request_kwargs={"partition_key": True},
    )
    comparison.print_report()
    comparison.assert_functional_parity()


@pytest.mark.asyncio
async def test_L4_feed_range_from_partition_key_none_partition_key_value_branch_async(container_for):
    """Async NonePartitionKeyValue branch (`_Undefined` on non-system containers) is parity-safe."""

    async def _do(client):
        container = client.get_database_client("parity_db").get_container_client(container_for.id)
        feed_range = await container.feed_range_from_partition_key(NonePartitionKeyValue)
        return _normalize_feed_range(feed_range)

    comparison = await run_on_both_backends_async(
        _do,
        description="[L4] async feed_range_from_partition_key NonePartitionKeyValue branch",
        request_kwargs={"partition_key": "NonePartitionKeyValue"},
    )
    comparison.print_report()
    comparison.assert_functional_parity()


@pytest.mark.asyncio
async def test_L5_feed_range_from_partition_key_hpk_full_key_async(container_for_multihash):
    """Async hierarchical full key (all PK components) is parity-safe."""
    run_suffix = uuid.uuid4().hex

    async def _do(client):
        container = client.get_database_client("parity_db").get_container_client(container_for_multihash.id)
        tenant = "tenant-" + run_suffix[:4]
        region = "region-" + run_suffix[4:8]
        await container.upsert_item({"id": "id-hpk-full-" + run_suffix, "tenant": tenant, "region": region})
        feed_range = await container.feed_range_from_partition_key([tenant, region])
        return _normalize_feed_range(feed_range)

    comparison = await run_on_both_backends_async(
        _do,
        description="[L5] async feed_range_from_partition_key hierarchical full key",
        request_kwargs={"partition_key": ["tenant", "region"]},
    )
    comparison.print_report()
    comparison.assert_functional_parity()


@pytest.mark.asyncio
async def test_L6_feed_range_from_partition_key_hpk_prefix_key_async(container_for_multihash):
    """Async hierarchical prefix key (partial PK components) is parity-safe."""
    run_suffix = uuid.uuid4().hex

    async def _do(client):
        container = client.get_database_client("parity_db").get_container_client(container_for_multihash.id)
        tenant = "tenant-" + run_suffix[:4]
        await container.upsert_item({"id": "id-hpk-prefix-" + run_suffix, "tenant": tenant, "region": "region-a"})
        feed_range = await container.feed_range_from_partition_key([tenant])
        return _normalize_feed_range(feed_range)

    comparison = await run_on_both_backends_async(
        _do,
        description="[L6] async feed_range_from_partition_key hierarchical prefix key",
        request_kwargs={"partition_key": ["tenant"]},
    )
    comparison.print_report()
    comparison.assert_functional_parity()


@pytest.mark.asyncio
async def test_L1_feed_range_from_partition_key_null_partition_key_async(container_for):
    """Async JSON-null partition key maps to the same feed range on both backends."""

    async def _do(client):
        container = client.get_database_client("parity_db").get_container_client(container_for.id)
        feed_range = await container.feed_range_from_partition_key(None)
        return _normalize_feed_range(feed_range)

    comparison = await run_on_both_backends_async(
        _do,
        description="[L1] async feed_range_from_partition_key null partition key",
        request_kwargs={"partition_key": None},
    )
    comparison.print_report()
    comparison.assert_functional_parity()
