# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Side-by-side parity tests for ``Container.replace_throughput`` (changing a
container's provisioned RU/s).

Why these exist: customers call ``replace_throughput`` to raise capacity before a
spike and lower it afterward, and automation reads the returned RU/s to confirm the
change took. During the migration to the rust engine the rust path must set and
report the exact same number as the existing core-python path. Without these tests,
rust could apply a different RU/s than core-python for the same call and a scaler
would act on a wrong confirmation.

What they do: each test runs the same ``replace_throughput`` call once on
core-python and once on rust (via ``run_on_both_backends``), against the *same*
throwaway container, and asserts the two agree on the applied RU/s. A fixed absolute
target (not read-then-add) keeps both runs deterministic -- core-python sets 500,
rust sets 500, both report 500. ``_normalize_throughput`` reduces the returned
``ThroughputProperties`` to the customer-visible numbers so server-stamped fields
don't cause false mismatches. ``assert_functional_parity`` ignores the known rust
gap where it reports fewer response headers than core-python -- a reporting
difference, not a behaviour difference.

How this differs from the legacy tests: the ``legacy/`` copies re-run the old v4
tests on rust only and catch *contract* drift (wrong return type, a change that
doesn't take). These parity tests run *both* engines and catch *value* drift (rust
applies a different RU/s than core-python for the same container).

They run only when a real account and the compiled rust binding are both present.

Run with::

    pytest --noconftest tests/replace_throughput/sync/test_replace_throughput_parity.py -v
"""
from __future__ import annotations

import os
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey, ThroughputProperties
from common._parity_helpers import (
    run_on_both_backends,
    skip_unless_emulator,
    skip_unless_rust_binding,
)

pytestmark = [skip_unless_emulator(), skip_unless_rust_binding()]


@pytest.fixture
def container_for(request):
    """A dedicated-throughput throwaway container, so ``replace_throughput`` has an offer to update."""
    # Fresh throwaway container per test, deleted afterward, so tests don't share data.
    # Created with dedicated throughput (offer_throughput) because replace_throughput
    # only has an offer to change when the container owns one.
    client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])
    db = client.create_database_if_not_exists("parity_db")
    container_id = "parity_replace_tp_" + request.node.name + "_" + uuid.uuid4().hex[:6]
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


def test_replace_throughput_int_applies_same_ru(container_for):
    """replace_throughput(int) applies and reports the same RU/s on both backends."""
    # Without this, rust could set or report a different RU/s than core-python for the
    # same fixed target, and a scaler reading the confirmation would act on a wrong number.

    def _do(client):
        """Run ``replace_throughput(500)`` on the given client and return normalised RU/s."""
        container = client.get_database_client("parity_db").get_container_client(container_for.id)
        return _normalize_throughput(container.replace_throughput(500))

    comparison = run_on_both_backends(_do, description="replace_throughput(500)")
    comparison.print_report()
    comparison.assert_functional_parity()


def test_replace_throughput_object_applies_same_ru(container_for):
    """replace_throughput(ThroughputProperties) applies the same RU/s on both backends."""

    def _do(client):
        """Run ``replace_throughput(ThroughputProperties(...))`` and return normalised RU/s."""
        container = client.get_database_client("parity_db").get_container_client(container_for.id)
        return _normalize_throughput(
            container.replace_throughput(ThroughputProperties(offer_throughput=500))
        )

    comparison = run_on_both_backends(
        _do, description="replace_throughput(ThroughputProperties(offer_throughput=500))"
    )
    comparison.print_report()
    comparison.assert_functional_parity()


@pytest.fixture
def autoscale_container_for(request):
    """An autoscale throwaway container, so the autoscale offer body is exercised in parity tests."""
    # Fresh throwaway autoscale container per test. Autoscale is the throughput model
    # a plain int can't express, so it exercises the offer-body path that carries
    # offerAutopilotSettings rather than a single offerThroughput number.
    client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])
    db = client.create_database_if_not_exists("parity_db")
    container_id = "parity_replace_tp_as_" + request.node.name + "_" + uuid.uuid4().hex[:6]
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


def test_replace_throughput_autoscale_applies_same_ceiling(autoscale_container_for):
    """replace_throughput of an autoscale ceiling behaves identically on both backends."""
    # Autoscale settings ride in the offer body, not a header; this proves the Rust
    # path sends and reads them back the same way core-python does.

    def _do(client):
        """Run autoscale ``replace_throughput`` and return normalised RU ceiling."""
        container = client.get_database_client("parity_db").get_container_client(autoscale_container_for.id)
        return _normalize_throughput(
            container.replace_throughput(ThroughputProperties(auto_scale_max_throughput=6000))
        )

    comparison = run_on_both_backends(
        _do, description="replace_throughput(ThroughputProperties(auto_scale_max_throughput=6000))"
    )
    comparison.print_report()
    comparison.assert_functional_parity()
