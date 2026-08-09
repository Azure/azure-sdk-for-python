# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Check database throughput reads on Python and Rust.

Here, parity means matching public behavior between Python and Rust. These
tests prove that fixed and autoscale values match, the deprecated name still
warns, and missing throughput keeps its current typed-error behavior visible.
Customers use these values for shared capacity and cost planning.
"""
from __future__ import annotations

import os
import uuid
import warnings

import pytest

from azure.cosmos import CosmosClient, ThroughputProperties, exceptions
from common._parity_helpers import (
    run_on_both_backends,
    skip_unless_emulator,
    skip_unless_rust_binding,
)

pytestmark = [skip_unless_emulator(), skip_unless_rust_binding()]


def _admin_client():
    """Build a sync ``CosmosClient`` from the standard emulator environment variables."""
    return CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])


def _normalize_throughput(throughput_properties):
    """Return the customer-visible fields so engine-internal fields do not affect equality."""
    # Reduce the result to the numbers a customer reads, so the two engines
    # compare equal regardless of server-stamped fields on the raw offer.
    return {
        "offer_throughput": throughput_properties.offer_throughput,
        "auto_scale_max_throughput": throughput_properties.auto_scale_max_throughput,
        "auto_scale_increment_percent": throughput_properties.auto_scale_increment_percent,
    }


def _database_with_throughput(request, offer_throughput):
    """Create a throwaway database with the given throughput and delete it after."""
    client = _admin_client()
    database_id = "parity_get_db_tp_" + request.node.name[:24] + "_" + uuid.uuid4().hex[:6]
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
def fixed_throughput_database(request):
    """A throwaway database provisioned at 1000 RU/s."""
    yield from _database_with_throughput(request, 1000)


@pytest.fixture
def autoscale_database(request):
    """A throwaway database provisioned with a 5000 RU/s autoscale ceiling."""
    yield from _database_with_throughput(
        request,
        ThroughputProperties(auto_scale_max_throughput=5000, auto_scale_increment_percent=2),
    )


@pytest.fixture
def database_without_throughput(request):
    """A database created with no throughput of its own."""
    client = _admin_client()
    database_id = "parity_get_db_notp_" + uuid.uuid4().hex[:6]
    client.create_database(id=database_id)
    try:
        yield database_id
    finally:
        try:
            client.delete_database(database_id)
        except Exception:  # pylint: disable=broad-except
            pass
        client.close()


def test_get_throughput_fixed(fixed_throughput_database):
    """get_throughput reports the same fixed RU/s on both engines."""

    def _do(client):
        """Read fixed throughput from one engine."""
        database = client.get_database_client(fixed_throughput_database))
    comparison.print_report()
    comparison.assert_functional_parity()
    assert comparison.core_python.return_value["offer_throughput"] == 1000


def test_get_throughput_autoscale(autoscale_database):
    """get_throughput reports the same autoscale ceiling and step on both engines."""
    # Autoscale values arrive in different fields from a fixed number, so a
    # fixed-number comparison alone would not catch rust mis-reading them.

    def _do(client):
        """Read autoscale throughput from one engine."""
        database = client.get_database_client(autoscale_database))
    comparison.print_report()
    comparison.assert_functional_parity()
    assert comparison.core_python.return_value["auto_scale_max_throughput"] == 5000
    assert comparison.core_python.return_value["offer_throughput"] is None


def test_read_offer_matches_get_throughput(fixed_throughput_database):
    """The deprecated read_offer name returns the same numbers on both engines."""
    # read_offer forwards to get_throughput. If routing were wired into
    # get_throughput only, read_offer would quietly keep using the old engine.

    def _do(client):
        """Read via the deprecated name from one engine."""
        database = client.get_database_client(fixed_throughput_database)
            warnings.simplefilter("ignore", DeprecationWarning)
            return _normalize_throughput(database.read_offer())

    comparison = run_on_both_backends(_do, description="database read_offer, fixed RU/s")
    comparison.print_report()
    comparison.assert_functional_parity()
    assert comparison.rust.return_value["offer_throughput"] == 1000


def test_read_offer_still_warns(fixed_throughput_database):
    """read_offer still warns that it is deprecated when rust serves the read."""
    # The warning is the only signal telling customers to move to get_throughput.
    # Routing the call through a helper must not swallow it.
    client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")
    try:
        database = client.get_database_client(fixed_throughput_database)
        with pytest.warns(DeprecationWarning):
            database.read_offer()
    finally:
        client.close()


def test_get_throughput_without_provisioned_throughput(database_without_throughput):
    """A database with no throughput of its own: rust raises a typed 404, core-python crashes."""
    # Keep the known difference visible until Python also returns the typed 404.
    def _do(client):
        database = client.get_database_client(database_without_throughput)
        return _normalize_throughput(database.get_throughput())

    comparison = run_on_both_backends(_do, description="database get_throughput, no throughput")
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
