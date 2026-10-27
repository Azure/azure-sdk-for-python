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
core-python and once on rust (via ``run_on_both_backends``), against separate
throwaway containers initially set to the same capacity. Both returned settings
and a fresh read must confirm the target; a no-op write cannot inherit the other
backend's change. ``_normalize_throughput`` reduces the returned
``ThroughputProperties`` to the customer-visible numbers so server-stamped fields
don't cause false mismatches. ``assert_functional_parity`` checks functional
results, not complete header equality. Header differences remain separate
audit evidence.

How this differs from the legacy tests: the ``legacy/`` copies re-run the old v4
tests on rust only and catch *contract* drift (wrong return type, a change that
doesn't take). These parity tests run *both* engines and catch *value* drift (rust
applies a different RU/s than core-python for the same container).

They run only when a real account and the compiled rust binding are both present.

Run with::

    pytest --noconftest tests/replace_throughput/sync/test_replace_throughput_parity.py -v
"""
from __future__ import annotations

import pytest

from azure.cosmos import ThroughputProperties
from common._parity_helpers import run_on_both_backends, skip_unless_emulator, skip_unless_rust_binding
from common.throughput_fixtures import container_for, autoscale_container_for, container_for_backend

pytestmark = [pytest.mark.cosmosEmulator, skip_unless_emulator(), skip_unless_rust_binding()]


def _normalize_throughput(throughput_properties):
    """Strip server-stamped fields, keeping only the customer-visible RU/s numbers for comparison."""
    # Reduce the throughput object to the customer-visible numbers, so the two engines
    # compare equal regardless of server-stamped fields (id/_rid/_ts) on the raw offer.
    return {
        "offer_throughput": throughput_properties.offer_throughput,
        "auto_scale_max_throughput": throughput_properties.auto_scale_max_throughput,
        "auto_scale_increment_percent": throughput_properties.auto_scale_increment_percent,
    }


def test_replace_throughput_int_applies_same_ru_rust(container_for):
    """replace_throughput(int) applies and reports the same RU/s on both backends."""
    # Without this, rust could set or report a different RU/s than core-python for the
    # same fixed target, and a scaler reading the confirmation would act on a wrong number.

    def _do(client):
        """Run ``replace_throughput(500)`` on the given client and return normalised RU/s."""
        container = container_for_backend(client, container_for)
        updated = _normalize_throughput(container.replace_throughput(500))
        assert updated["offer_throughput"] == 500
        assert _normalize_throughput(container.get_throughput()) == updated
        return updated

    comparison = run_on_both_backends(_do, description="replace_throughput(500)")
    comparison.print_report()
    comparison.assert_functional_parity()


def test_replace_throughput_object_applies_same_ru_rust(container_for):
    """replace_throughput(ThroughputProperties) applies the same RU/s on both backends."""

    def _do(client):
        """Run ``replace_throughput(ThroughputProperties(...))`` and return normalised RU/s."""
        container = container_for_backend(client, container_for)
        updated = _normalize_throughput(
            container.replace_throughput(ThroughputProperties(offer_throughput=500))
        )
        assert updated["offer_throughput"] == 500
        assert _normalize_throughput(container.get_throughput()) == updated
        return updated

    comparison = run_on_both_backends(
        _do, description="replace_throughput(ThroughputProperties(offer_throughput=500))"
    )
    comparison.print_report()
    comparison.assert_functional_parity()


def test_replace_throughput_autoscale_applies_same_ceiling_rust(autoscale_container_for):
    """replace_throughput of an autoscale ceiling behaves identically on both backends."""
    # Autoscale settings ride in the offer body, not a header; this proves the Rust
    # path sends and reads them back the same way core-python does.

    def _do(client):
        """Run autoscale ``replace_throughput`` and return normalised RU ceiling."""
        container = container_for_backend(client, autoscale_container_for)
        updated = _normalize_throughput(
            container.replace_throughput(ThroughputProperties(auto_scale_max_throughput=6000))
        )
        assert updated["auto_scale_max_throughput"] == 6000
        assert _normalize_throughput(container.get_throughput()) == updated
        return updated

    comparison = run_on_both_backends(
        _do, description="replace_throughput(ThroughputProperties(auto_scale_max_throughput=6000))"
    )
    comparison.print_report()
    comparison.assert_functional_parity()
