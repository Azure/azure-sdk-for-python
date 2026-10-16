# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Check async database throughput replacements on Python and Rust.

Here, parity means matching public behavior between Python and Rust. These
tests prove that fixed and autoscale changes are stored and read back with the
same values. They also keep the current missing-throughput error behavior
visible. Customers rely on read-back values to confirm shared capacity changes.
"""
from __future__ import annotations

import os
import uuid
from contextlib import ExitStack

import pytest

from azure.cosmos import CosmosClient, ThroughputProperties, exceptions
from common._parity_helpers import _observed_backend_name, run_on_both_backends_async, skip_unless_emulator, skip_unless_rust_binding
from common.parity_provisioning import create_owned_database

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


@pytest.fixture
def database_per_backend():
    """Use separate databases for changes and one shared database for missing offers.

    Neither engine can replace a missing offer, so that case can share a
    database and compare the complete error message, including its target.
    Setup runs on the sync client on purpose: it is only scaffolding, the call
    under test is the async one inside each test, and a sync fixture avoids
    holding an event loop open across the fixture boundary.
    """
    client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])
    created = {}

    def _make(offer_throughput):
        """Create isolated targets for writes, or a shared target for rejection."""
        backends = ("core-python",) if offer_throughput is None else ("core-python", "rust")
        for backend_name in backends:
            database_id = "parity_repl_db_a_{}_{}".format(
                backend_name.replace("-", ""), uuid.uuid4().hex[:6]
            )
            created[backend_name] = database_id
            create_owned_database(client, id=database_id, offer_throughput=offer_throughput)
        if offer_throughput is None:
            created["rust"] = created["core-python"]
        return created

    yield _make

    def delete_owned_database(database_id):
        try:
            client.delete_database(database_id)
        except exceptions.CosmosResourceNotFoundError:
            pass

    with ExitStack() as cleanup:
        cleanup.callback(client.close)
        for database_id in set(created.values()):
            cleanup.callback(delete_owned_database, database_id)


def _database_for(client, created):
    """Pick the database belonging to whichever engine this client is."""
    return client.get_database_client(created[_observed_backend_name(client)])


async def test_replace_throughput_fixed_async(database_per_backend):
    """Async: changing a fixed RU/s number lands the same value on both engines."""
    # The value is read back so the check covers what reached the server, not
    # only what the SDK handed back.
    created = database_per_backend(1000)

    async def _do(client):
        """Replace fixed throughput then read it back on one engine."""
        database = _database_for(client, created)
        await database.replace_throughput(2000)
        return _normalize_throughput(await database.get_throughput())

    comparison = await run_on_both_backends_async(
        _do, description="async database replace_throughput, fixed RU/s"
    )
    comparison.print_report()
    comparison.assert_functional_parity()
    assert comparison.rust.return_value["offer_throughput"] == 2000


async def test_replace_throughput_autoscale_async(database_per_backend):
    """Async: changing an autoscale ceiling and step lands the same values on both engines."""
    # Read-back proves the nested autoscale settings reached the service.
    created = database_per_backend(
        ThroughputProperties(auto_scale_max_throughput=5000, auto_scale_increment_percent=0)
    )

    async def _do(client):
        """Replace autoscale settings then read them back on one engine."""
        database = _database_for(client, created)
        await database.replace_throughput(
            ThroughputProperties(auto_scale_max_throughput=7000, auto_scale_increment_percent=20)
        )
        return _normalize_throughput(await database.get_throughput())

    comparison = await run_on_both_backends_async(
        _do, description="async database replace_throughput, autoscale"
    )
    comparison.print_report()
    comparison.assert_functional_parity()
    assert comparison.rust.return_value["auto_scale_max_throughput"] == 7000
    assert comparison.rust.return_value["auto_scale_increment_percent"] == 20


async def test_replace_throughput_without_provisioned_throughput_async(database_per_backend):
    """Both async implementations reject replacing a missing offer with a typed 404."""
    created = database_per_backend(None)

    async def _do(client):
        """Attempt a throughput change on a database that owns no offer."""
        database = _database_for(client, created)
        return _normalize_throughput(await database.replace_throughput(2000))

    comparison = await run_on_both_backends_async(
        _do, description="async database replace_throughput, no throughput"
    )
    comparison.print_report()

    assert isinstance(comparison.rust.raised, exceptions.CosmosResourceNotFoundError), (
        "rust should report a missing offer as a typed 404, got {!r}".format(
            comparison.rust.raised
        )
    )
    assert comparison.rust.raised.status_code == 404
    assert isinstance(comparison.core_python.raised, exceptions.CosmosResourceNotFoundError), (
        "core-python should report a missing offer as a typed 404, got {!r}".format(
            comparison.core_python.raised
        )
    )
    assert comparison.core_python.raised.status_code == 404
    comparison.assert_exception_parity()
