# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Check database throughput reads on Python and Rust.

Here, parity means matching public behavior between Python and Rust. These
tests prove that fixed and autoscale values match and missing throughput
keeps its current typed-error behavior visible.
Customers use these values for shared capacity and cost planning.
"""
from __future__ import annotations

import os
from copy import deepcopy
import uuid

import pytest

from azure.cosmos import CosmosClient, ThroughputProperties, exceptions
from common._parity_helpers import (
    run_on_both_backends, run_target_operation, skip_unless_emulator, skip_unless_rust_binding,
)
from common.parity_provisioning import create_owned_database

pytestmark = [skip_unless_emulator(), skip_unless_rust_binding()]


def _admin_client():
    """Build a sync ``CosmosClient`` from the standard emulator environment variables."""
    return CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])


def _normalize_throughput(throughput_properties):
    """Compare the public fields and complete offer properties for the same database."""
    return {
        "offer_throughput": throughput_properties.offer_throughput,
        "auto_scale_max_throughput": throughput_properties.auto_scale_max_throughput,
        "auto_scale_increment_percent": throughput_properties.auto_scale_increment_percent,
        "properties": throughput_properties.properties,
    }


def _database_with_throughput(request, offer_throughput):
    """Create a throwaway database with the given throughput and delete it after."""
    client = _admin_client()
    database_id = "parity_get_db_tp_" + request.node.name[:24] + "_" + uuid.uuid4().hex[:6]
    try:
        create_owned_database(client, id=database_id, offer_throughput=offer_throughput)
        yield database_id
    finally:
        try:
            client.delete_database(database_id)
        except exceptions.CosmosResourceNotFoundError:
            pass
        finally:
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
    try:
        create_owned_database(client, id=database_id)
        yield database_id
    finally:
        try:
            client.delete_database(database_id)
        except exceptions.CosmosResourceNotFoundError:
            pass
        finally:
            client.close()


def test_get_throughput_fixed(fixed_throughput_database):
    """get_throughput reports the same fixed RU/s on both engines."""

    def _do(client):
        """Read fixed throughput from one engine."""
        database = client.get_database_client(fixed_throughput_database)
        return _normalize_throughput(run_target_operation(client, database.get_throughput))

    comparison = run_on_both_backends(_do, description="database get_throughput, fixed RU/s")
    comparison.print_report()
    comparison.assert_functional_parity()
    assert comparison.core_python.return_value["offer_throughput"] == 1000


def test_get_throughput_autoscale(autoscale_database):
    """get_throughput reports the same autoscale ceiling and step on both engines."""
    # Autoscale values arrive in different fields from a fixed number, so a
    # fixed-number comparison alone would not catch rust mis-reading them.

    def _do(client):
        """Read autoscale throughput from one engine."""
        database = client.get_database_client(autoscale_database)
        return _normalize_throughput(run_target_operation(client, database.get_throughput))

    comparison = run_on_both_backends(_do, description="database get_throughput, autoscale")
    comparison.print_report()
    comparison.assert_functional_parity()
    assert comparison.core_python.return_value["auto_scale_max_throughput"] == 5000
    assert comparison.core_python.return_value["auto_scale_increment_percent"] == 2
    assert comparison.core_python.return_value["offer_throughput"] is None


def test_get_throughput_without_provisioned_throughput(database_without_throughput):
    """Both implementations report a missing database offer as a typed 404."""
    def _do(client):
        database = client.get_database_client(database_without_throughput)
        return _normalize_throughput(run_target_operation(client, database.get_throughput))

    comparison = run_on_both_backends(_do, description="database get_throughput, no throughput")
    comparison.print_report()

    assert isinstance(comparison.rust.raised, exceptions.CosmosResourceNotFoundError), (
        "rust should report a missing offer as a typed 404, got {!r}".format(comparison.rust.raised)
    )
    assert comparison.rust.raised.status_code == 404
    assert isinstance(comparison.core_python.raised, exceptions.CosmosResourceNotFoundError)
    assert comparison.core_python.raised.status_code == 404
    comparison.assert_functional_parity()


@pytest.mark.parametrize("warm", [False, True])
def test_get_throughput_preserves_inputs_and_callback_result(fixed_throughput_database, warm):
    def read(client):
        database = client.get_database_client(fixed_throughput_database)
        if warm:
            database.read()
        options = {"initialHeaders": {"x-ms-client-request-id": "database-throughput-parity"}}
        original = deepcopy(options)
        callbacks = []

        def hook(headers, offers):
            callbacks.append((dict(headers), deepcopy(list(offers))))
            headers.clear()
            offers[0]["content"]["offerThroughput"] = 999

        result = run_target_operation(
            client, lambda: database.get_throughput(request_options=options, response_hook=hook)
        )
        assert options == original
        assert len(callbacks) == 1
        assert result.offer_throughput == 1000
        assert callbacks[0][1][0]["content"]["offerThroughput"] == 1000
        headers = result.get_response_headers()
        assert float(headers["x-ms-request-charge"]) > 0
        assert dict(headers) == callbacks[0][0]
        database.read()
        assert result.get_response_headers() == headers
        return _normalize_throughput(result)

    comparison = run_on_both_backends(
        read, description=f"database get_throughput ownership, warm properties={warm}",
        request_kwargs={"request_options": {"initialHeaders": {
            "x-ms-client-request-id": "database-throughput-parity",
        }}},
    )
    comparison.assert_functional_parity()


@pytest.mark.parametrize("options", [
    {"read_timeout": 2},
    {"availability_strategy": {"type": "hedging"}},
    {"initial_headers": {"Accept": "unsupported"}},
])
def test_rust_database_read_rejects_unsupported_inputs(monkeypatch, options):
    with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as client:
        database = client.get_database_client("not-requested")

        def unexpected_request(*args, **kwargs):
            pytest.fail("unsupported input must be rejected before metadata or legacy execution")

        monkeypatch.setattr(database, "_get_properties", unexpected_request)
        monkeypatch.setattr(client.client_connection, "QueryOffers", unexpected_request)
        with pytest.raises(NotImplementedError, match="legacy Python path"):
            run_target_operation(
                client, lambda: database.get_throughput(**options), expect_rust=False,
            )
