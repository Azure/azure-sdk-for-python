# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Check async database throughput reads on Python and Rust.

Here, parity means matching public behavior between Python and Rust. These
tests prove that fixed and autoscale values match and keep the current missing
throughput error behavior visible. Customers use these values for shared
capacity and cost planning.
"""
from __future__ import annotations

import os
import uuid

import pytest

from azure.cosmos import CosmosClient, ThroughputProperties, exceptions
from common._parity_helpers import (
    run_on_both_backends_async,
    skip_unless_emulator,
    skip_unless_rust_binding,
)

pytestmark = [skip_unless_emulator(), skip_unless_rust_binding(), pytest.mark.asyncio]


def _normalize_throughput(throughput_properties):
    """Return the customer-visible fields so engine-internal fields do not affect equality."""
    # Reduce the result to the numbers a customer reads, so the two engines
    # compare equal regardless of server-stamped fields on the raw offer.
    return {
        "offer_throughput": throughput_properties.offer_throughput,
        "auto_scale_max_throughput": throughput_properties.auto_scale_max_throughput,
        "auto_scale_increment_percent": throughput_properties.auto_scale_increment_percent,
    }


def _database_with_throughput(offer_throughput):
    """Create a throwaway database with the given throughput and delete it after.

    Setup runs on the sync client on purpose: it is only scaffolding, the call
    under test is the async one inside each test, and a sync fixture avoids
    holding an event loop open across the fixture boundary.
    """
    client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])
    database_id = "parity_get_db_tp_a_" + uuid.uuid4().hex[:8]
    if offer_throughput is None:
        client.create_database(id=database_id)
    else:
        client.create_database(id=database_id, offer_throughput=offer_throughput)
    try:
        yield database_id
    finally:
        try:
            client.delete_database(database_id)
        except Exception:  # pylint: disable=broad-except
            pass
        client.close()


@pytest.fixture
def fixed_throughput_database():
    """A throwaway database provisioned at 1000 RU/s."""
    yield from _database_with_throughput(1000)


@pytest.fixture
def autoscale_database():
    """A throwaway database provisioned with a 5000 RU/s autoscale ceiling."""
    yield from _database_with_throughput(
        ThroughputProperties(auto_scale_max_throughput=5000, auto_scale_increment_percent=2)
    )


@pytest.fixture
def database_without_throughput():
    """A throwaway database created with no throughput of its own."""
    yield from _database_with_throughput(None)


async def test_get_throughput_fixed_async(fixed_throughput_database):
    """Async get_throughput reports the same fixed RU/s on both engines."""

    async def _do(client):
        """Read fixed throughput from one engine."""
        database = client.get_database_client(fixed_throughput_database)
        return _normalize_throughput(await database.get_throughput())

    comparison = await run_on_both_backends_async(
        _do, description="async database get_throughput, fixed RU/s"
    )
    comparison.print_report()
    comparison.assert_functional_parity()
    assert comparison.core_python.return_value["offer_throughput"] == 1000


async def test_get_throughput_autoscale_async(autoscale_database):
    """Async get_throughput reports the same autoscale ceiling and step on both engines."""
    # Autoscale values arrive in different fields from a fixed number, so a
    # fixed-number comparison alone would not catch rust mis-reading them.

    async def _do(client):
        """Read autoscale throughput from one engine."""
        database = client.get_database_client(autoscale_database)
        return _normalize_throughput(await database.get_throughput())

    comparison = await run_on_both_backends_async(
        _do, description="async database get_throughput, autoscale"
    )
    comparison.print_report()
    comparison.assert_functional_parity()
    assert comparison.core_python.return_value["auto_scale_max_throughput"] == 5000
    assert comparison.core_python.return_value["offer_throughput"] is None


async def test_get_throughput_without_provisioned_throughput_async(database_without_throughput):
    """A database with no throughput: rust raises a typed 404, core-python crashes."""
    # Keep the known difference visible until Python also returns the typed 404.

    async def _do(client):
        """Attempt to read throughput on a database that owns no offer."""
        database = client.get_database_client(database_without_throughput)
        return _normalize_throughput(await database.get_throughput())

    comparison = await run_on_both_backends_async(
        _do, description="async database get_throughput, no throughput"
    )
    comparison.print_report()

    assert isinstance(comparison.rust.raised, exceptions.CosmosResourceNotFoundError), (
        "rust should report a missing offer as a typed 404, got {!r}".format(comparison.rust.raised)
    )
    assert comparison.rust.raised.status_code == 404
    assert isinstance(comparison.core_python.raised, AttributeError), (
        "core-python is expected to crash in its retry policy for this case; if it now "
        "raises a Cosmos error, the defect is fixed and this test should require "
        "matching typed errors on both engines instead. Got {!r}".format(
            comparison.core_python.raised
        )
    )
