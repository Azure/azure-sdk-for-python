# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Check database throughput replacements on Python and Rust.

Here, parity means matching public behavior between Python and Rust. These
tests prove that fixed and autoscale changes are stored and read back with the
same values. They also keep the current missing-throughput error behavior
visible. Customers rely on read-back values to confirm shared capacity changes.
"""
from __future__ import annotations

import os
import uuid

import pytest

from azure.cosmos import CosmosClient, ThroughputProperties, exceptions
from common._parity_helpers import (
    _observed_backend_name,
    run_on_both_backends,
    skip_unless_emulator,
    skip_unless_rust_binding,
)

pytestmark = [skip_unless_emulator(), skip_unless_rust_binding()]


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
def database_per_backend(request):
    """One fresh database per engine, so neither engine changes the other's database.

    A read can be repeated against the same database and still be a fair
    comparison. A change cannot: whichever engine ran second would be changing a
    database that already holds the new value, and would pass even if it did
    nothing. The fixture hands out a separate database for each engine and
    deletes both afterwards.
    """
    client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])
    created = {}

    def _make(offer_throughput):
        """Create one database per engine and register them for teardown."""
        for backend_name in ("core-python", "rust"):
            database_id = "parity_repl_db_{}_{}".format(
                backend_name.replace("-", ""), uuid.uuid4().hex[:6]
            )
            client.create_database(id=database_id, offer_throughput=offer_throughput)
            created[backend_name] = database_id
        return created

    yield _make

    for database_id in created.values():
        try:
            client.delete_database(database_id)
        except Exception:  # pylint: disable=broad-except
            pass
    client.close()


def _database_for(client, created):
    """Pick the database belonging to whichever engine this client is."""
    return client.get_database_client(created[_observed_backend_name(client)])


def test_replace_throughput_fixed(database_per_backend):
    """Changing a fixed RU/s number reports the same result on both engines."""
    created = database_per_backend(1000)

    def _do(client):
        """Replace fixed throughput on one engine."""
        return _normalize_throughput(_database_for(client, created).replace_throughput(2000))

    comparison = run_on_both_backends(_do, description="database replace_throughput, fixed RU/s")
    comparison.print_report()
    comparison.assert_functional_parity()
    assert comparison.rust.return_value["offer_throughput"] == 2000


def test_replace_throughput_autoscale(database_per_backend):
    """Changing an autoscale ceiling and step lands the same values on both engines."""
    # Read-back proves the nested autoscale settings reached the service.
    created = database_per_backend(
        ThroughputProperties(auto_scale_max_throughput=5000, auto_scale_increment_percent=2)
    )

    def _do(client):
        """Replace autoscale settings then read them back on one engine."""
        database = _database_for(client, created)
        database.replace_throughput(
            ThroughputProperties(auto_scale_max_throughput=7000, auto_scale_increment_percent=20)
        )
        return _normalize_throughput(database.get_throughput())

    comparison = run_on_both_backends(_do, description="database replace_throughput, autoscale")
    comparison.print_report()
    comparison.assert_functional_parity()
    assert comparison.rust.return_value["auto_scale_max_throughput"] == 7000
    assert comparison.rust.return_value["auto_scale_increment_percent"] == 20


def test_replace_throughput_persists(database_per_backend):
    """Reading back after the change returns the new number on both engines."""
    created = database_per_backend(1000)

    def _do(client):
        """Replace fixed throughput then read it back on one engine."""
        database = _database_for(client, created)
        database.replace_throughput(3000)
        return _normalize_throughput(database.get_throughput())

    comparison = run_on_both_backends(
        _do, description="database replace_throughput then read back"
    )
    comparison.print_report()
    comparison.assert_functional_parity()
    assert comparison.rust.return_value["offer_throughput"] == 3000


def test_replace_throughput_without_provisioned_throughput():
    """Changing throughput on a database that owns none: rust raises a typed 404."""
    # Keep the known difference visible until Python also returns the typed 404.
    client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])
    created = {}
    try:
        for backend_name in ("core-python", "rust"):
            database_id = "parity_repl_db_notp_{}_{}".format(
                backend_name.replace("-", ""), uuid.uuid4().hex[:6]
            )
            client.create_database(id=database_id)
            created[backend_name] = database_id

        def _do(inner_client):
            return _normalize_throughput(
                _database_for(inner_client, created).replace_throughput(2000)
            )

        comparison = run_on_both_backends(
            _do, description="database replace_throughput, no throughput"
        )
        comparison.print_report()

        assert isinstance(comparison.rust.raised, exceptions.CosmosResourceNotFoundError), (
            "rust should report a missing offer as a typed 404, got {!r}".format(
                comparison.rust.raised
            )
        )
        assert comparison.rust.raised.status_code == 404
        assert isinstance(comparison.core_python.raised, AttributeError), (
            "core-python is expected to crash in its retry policy for this case; if it "
            "now raises a Cosmos error, the defect is fixed and this test should require "
            "matching typed errors on both engines instead. Got {!r}".format(
                comparison.core_python.raised
            )
        )
    finally:
        for database_id in created.values():
            try:
                client.delete_database(database_id)
            except Exception:  # pylint: disable=broad-except
                pass
        client.close()
