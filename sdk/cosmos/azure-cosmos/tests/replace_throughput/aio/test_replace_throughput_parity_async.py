# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Async side-by-side parity tests for ``Container.replace_throughput``.

See the sync sibling (``replace_throughput/sync/test_replace_throughput_parity.py``)
for the full rationale. This is the async surface: each test runs the same
``replace_throughput`` call once on core-python and once on rust against separate
throwaway containers with equal initial capacity. Returned values and subsequent
reads must both confirm the requested target.

They run only when a real account and the compiled rust binding are both present.

Run with::

    pytest --noconftest tests/replace_throughput/aio/test_replace_throughput_parity_async.py -v
"""
from __future__ import annotations

import pytest

from azure.cosmos import ThroughputProperties
from common._parity_helpers import run_on_both_backends_async, skip_unless_emulator, skip_unless_rust_binding
from common.throughput_fixtures import container_for, autoscale_container_for, container_for_backend

pytestmark = [skip_unless_emulator(), skip_unless_rust_binding()]


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
        container = container_for_backend(client, container_for)
        updated = _normalize_throughput(await container.replace_throughput(500))
        assert updated["offer_throughput"] == 500
        assert _normalize_throughput(await container.get_throughput()) == updated
        return updated

    comparison = await run_on_both_backends_async(_do, description="async replace_throughput(500)")
    comparison.print_report()
    comparison.assert_functional_parity()


@pytest.mark.asyncio
async def test_replace_throughput_object_applies_same_ru_async(container_for):
    """Async replace_throughput(ThroughputProperties) applies the same RU/s on both backends."""

    async def _do(client):
        """Await ``replace_throughput(ThroughputProperties(...))`` and return normalised RU/s."""
        container = container_for_backend(client, container_for)
        updated = _normalize_throughput(
            await container.replace_throughput(ThroughputProperties(offer_throughput=500))
        )
        assert updated["offer_throughput"] == 500
        assert _normalize_throughput(await container.get_throughput()) == updated
        return updated

    comparison = await run_on_both_backends_async(
        _do, description="async replace_throughput(ThroughputProperties(offer_throughput=500))"
    )
    comparison.print_report()
    comparison.assert_functional_parity()


@pytest.mark.asyncio
async def test_replace_throughput_autoscale_applies_same_ceiling_async(autoscale_container_for):
    """Async replace_throughput of an autoscale ceiling behaves identically on both backends."""

    async def _do(client):
        """Await autoscale ``replace_throughput`` and return normalised RU ceiling."""
        container = container_for_backend(client, autoscale_container_for)
        updated = _normalize_throughput(
            await container.replace_throughput(ThroughputProperties(auto_scale_max_throughput=6000))
        )
        assert updated["auto_scale_max_throughput"] == 6000
        assert _normalize_throughput(await container.get_throughput()) == updated
        return updated

    comparison = await run_on_both_backends_async(
        _do, description="async replace_throughput(ThroughputProperties(auto_scale_max_throughput=6000))"
    )
    comparison.print_report()
    comparison.assert_functional_parity()
