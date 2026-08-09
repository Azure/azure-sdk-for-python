# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Async side-by-side parity tests for ``Container.replace_throughput``.

See the sync sibling (``replace_throughput/sync/test_replace_throughput_parity.py``)
for the full rationale. This is the async surface: each test runs the same
``replace_throughput`` call once on core-python and once on rust against the *same*
throwaway container and asserts the two agree on the applied RU/s. A fixed absolute
target keeps both runs deterministic.

They run only when a real account and the compiled rust binding are both present.

Run with::

    pytest --noconftest tests/replace_throughput/aio/test_replace_throughput_parity_async.py -v
"""
from __future__ import annotations

import os
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey, ThroughputProperties
from common._parity_helpers import (
    run_on_both_backends_async,
    skip_unless_emulator,
    skip_unless_rust_binding,
)

pytestmark = [skip_unless_emulator(), skip_unless_rust_binding()]


@pytest.fixture
def container_for(request):
    """A dedicated-throughput throwaway container, so ``replace_throughput`` has an offer to update."""
    # Fresh throwaway container per test, deleted afterward, so tests don't share data.
    # Created with dedicated throughput (offer_throughput) because replace_throughput
    # only has an offer to change when the container owns one. A plain (core-python)
    # client sets it up; the parity call itself runs on both engines below.
    client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])
    db = client.create_database_if_not_exists("parity_db")
    container_id = "parity_replace_tp_async_" + request.node.name + "_" + uuid.uuid4().hex[:6]
    container = db.create_container(
        id=container_id,
        partition_key=PartitionKey(path="/pk"),
        offer_throughput=400,
    )
    yield container
    try:
        db.delete_container(container_id)
    except Exception:  # pylint: disable=broad-except
        pass


def _normalize_throughput(throughput_properties):
    """Strip server-stamped fields, keeping only the customer-visible RU/s numbers for comparison."""
    # Reduce the throughput object to the customer-visible numbers, so the two engines
    # compare equal regardless of server-stamped fields (id/_rid/_ts) on the raw offer.
    return {
        "offer_throughput": throughput_properties.offer_throughput,
        "auto_scale_max_throughput": throughput_properties.auto_scale_max_throughput,
        "auto_scale_increment_percent": throughput_properties.auto_scale_increment_percent,
    }


@pytest.mark.asyncio
async def test_replace_throughput_int_applies_same_ru_async(container_for):
    """Async replace_throughput(int) applies and reports the same RU/s on both backends."""

    async def _do(client):
        """Await ``replace_throughput(500)`` on the given async client and return normalised RU/s."""
        container = client.get_database_client("parity_db").get_container_client(container_for.id)
        return _normalize_throughput(await container.replace_throughput(500))

    comparison = await run_on_both_backends_async(_do, description="async replace_throughput(500)")
    comparison.print_report()
    comparison.assert_functional_parity()


@pytest.mark.asyncio
async def test_replace_throughput_object_applies_same_ru_async(container_for):
    """Async replace_throughput(ThroughputProperties) applies the same RU/s on both backends."""

    async def _do(client):
        """Await ``replace_throughput(ThroughputProperties(...))`` and return normalised RU/s."""
        container = client.get_database_client("parity_db").get_container_client(container_for.id)
        return _normalize_throughput(
            await container.replace_throughput(ThroughputProperties(offer_throughput=500))
        )

    comparison = await run_on_both_backends_async(
        _do, description="async replace_throughput(ThroughputProperties(offer_throughput=500))"
    )
    comparison.print_report()
    comparison.assert_functional_parity()


@pytest.fixture
def autoscale_container_for(request):
    """An autoscale throwaway container, so the autoscale offer body is exercised in parity tests."""
    # Fresh throwaway autoscale container per test. Autoscale is the throughput model
    # a plain int can't express, so it exercises the offer-body path that carries
    # offerAutopilotSettings rather than a single offerThroughput number. A plain
    # (core-python) client sets it up; the parity call itself runs on both engines.
    client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])
    db = client.create_database_if_not_exists("parity_db")
    container_id = "parity_replace_tp_as_async_" + request.node.name + "_" + uuid.uuid4().hex[:6]
    container = db.create_container(
        id=container_id,
        partition_key=PartitionKey(path="/pk"),
        offer_throughput=ThroughputProperties(auto_scale_max_throughput=5000),
    )
    yield container
    try:
        db.delete_container(container_id)
    except Exception:  # pylint: disable=broad-except
        pass


@pytest.mark.asyncio
async def test_replace_throughput_autoscale_applies_same_ceiling_async(autoscale_container_for):
    """Async replace_throughput of an autoscale ceiling behaves identically on both backends."""

    async def _do(client):
        """Await autoscale ``replace_throughput`` and return normalised RU ceiling."""
        container = client.get_database_client("parity_db").get_container_client(autoscale_container_for.id)
        return _normalize_throughput(
            await container.replace_throughput(ThroughputProperties(auto_scale_max_throughput=6000))
        )

    comparison = await run_on_both_backends_async(
        _do, description="async replace_throughput(ThroughputProperties(auto_scale_max_throughput=6000))"
    )
    comparison.print_report()
    comparison.assert_functional_parity()
