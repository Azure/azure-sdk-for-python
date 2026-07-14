# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Async side-by-side parity tests for ``Container.get_throughput`` (the
throughput/offer read, deprecated alias ``read_offer``).

Why these exist: customers call ``get_throughput`` to see their provisioned
RU/s and autoscale ceiling, and they wire those numbers into cost and capacity
dashboards. During the migration to the rust engine the rust path must report
the exact same numbers as the existing core-python path. Without these tests,
rust could return a different RU/s or autoscale ceiling and a customer watching
capacity would act on a wrong number without anyone noticing.

What they do: each test runs the same ``get_throughput`` call once on
core-python and once on rust (via ``run_on_both_backends_async``), reduces each
result to the customer-visible numbers with ``_normalize_throughput`` (so
server-stamped fields like ``id`` / ``_rid`` / ``_ts`` don't cause false
mismatches), and asserts the two agree. ``assert_functional_parity`` ignores
the known rust gap where it reports fewer response headers than core-python --
that's a reporting difference, not a behaviour difference.

How this differs from the legacy tests: the ``legacy/`` copies re-run the old
v4 tests on rust only and catch *contract* drift (wrong object type, wrong
offer body). These parity tests run *both* engines and catch *value* drift
(rust reports a different RU/s than core-python for the same container).

They run only when a real account and the compiled rust binding are both
present.

Run with::

    pytest --noconftest tests/read_offer/aio/test_read_offer_parity_async.py -v
"""
from __future__ import annotations

import os
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey
from common._parity_helpers import (
    run_on_both_backends_async,
    skip_unless_emulator,
    skip_unless_rust_binding,
)

pytestmark = [skip_unless_emulator(), skip_unless_rust_binding()]


@pytest.fixture
def container_for(request):
    # Fresh throwaway container per test, deleted afterward, so tests don't share data.
    # The container is created with dedicated throughput (offer_throughput) because
    # get_throughput only returns an offer when the container owns one.
    client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])
    db = client.create_database_if_not_exists("parity_db")
    container_id = "parity_read_offer_async_" + request.node.name + "_" + uuid.uuid4().hex[:6]
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
    # Reduce the throughput object to the customer-visible numbers, so the two engines
    # compare equal regardless of server-stamped fields (id/_rid/_ts) on the raw offer.
    return {
        "offer_throughput": throughput_properties.offer_throughput,
        "auto_scale_max_throughput": throughput_properties.auto_scale_max_throughput,
        "auto_scale_increment_percent": throughput_properties.auto_scale_increment_percent,
    }


@pytest.mark.asyncio
async def test_get_throughput_baseline_async(container_for):
    """Async baseline get_throughput returns the same RU/s on both backends."""
    # Without this, a basic divergence in the reported RU/s would go unnoticed.

    async def _do(client):
        container = client.get_database_client("parity_db").get_container_client(container_for.id)
        return _normalize_throughput(await container.get_throughput())

    comparison = await run_on_both_backends_async(
        _do,
        description="async get_throughput baseline",
    )
    comparison.print_report()
    comparison.assert_functional_parity()
