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
from copy import deepcopy
import uuid

import pytest

from azure.cosmos import CosmosClient, ThroughputProperties, exceptions
from common._parity_helpers import (
    run_on_both_backends_async, run_target_operation_async,
    skip_unless_emulator, skip_unless_rust_binding,
)
from common.parity_provisioning import create_owned_database

pytestmark = [skip_unless_emulator(), skip_unless_rust_binding(), pytest.mark.asyncio]


def _normalize_throughput(throughput_properties):
    """Compare the public fields and complete offer properties for the same database."""
    return {
        "offer_throughput": throughput_properties.offer_throughput,
        "auto_scale_max_throughput": throughput_properties.auto_scale_max_throughput,
        "auto_scale_increment_percent": throughput_properties.auto_scale_increment_percent,
        "properties": throughput_properties.properties,
    }


def _database_with_throughput(offer_throughput):
    """Create a throwaway database with the given throughput and delete it after.

    Setup runs on the sync client on purpose: it is only scaffolding, the call
    under test is the async one inside each test, and a sync fixture avoids
    holding an event loop open across the fixture boundary.
    """
    client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])
    database_id = "parity_get_db_tp_a_" + uuid.uuid4().hex[:8]
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
        return _normalize_throughput(await run_target_operation_async(client, database.get_throughput))

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
        return _normalize_throughput(await run_target_operation_async(client, database.get_throughput))

    comparison = await run_on_both_backends_async(
        _do, description="async database get_throughput, autoscale"
    )
    comparison.print_report()
    comparison.assert_functional_parity()
    assert comparison.core_python.return_value["auto_scale_max_throughput"] == 5000
    assert comparison.core_python.return_value["auto_scale_increment_percent"] == 2
    assert comparison.core_python.return_value["offer_throughput"] is None


async def test_get_throughput_without_provisioned_throughput_async(database_without_throughput):
    """Both implementations report a missing database offer as a typed 404."""

    async def _do(client):
        """Attempt to read throughput on a database that owns no offer."""
        database = client.get_database_client(database_without_throughput)
        return _normalize_throughput(await run_target_operation_async(client, database.get_throughput))

    comparison = await run_on_both_backends_async(
        _do, description="async database get_throughput, no throughput"
    )
    comparison.print_report()

    assert isinstance(comparison.rust.raised, exceptions.CosmosResourceNotFoundError), (
        "rust should report a missing offer as a typed 404, got {!r}".format(comparison.rust.raised)
    )
    assert comparison.rust.raised.status_code == 404
    assert isinstance(comparison.core_python.raised, exceptions.CosmosResourceNotFoundError)
    assert comparison.core_python.raised.status_code == 404
    comparison.assert_functional_parity()


@pytest.mark.parametrize("warm", [False, True])
async def test_get_throughput_preserves_inputs_and_callback_result_async(fixed_throughput_database, warm):
    async def read(client):
        database = client.get_database_client(fixed_throughput_database)
        if warm:
            await database.read()
        options = {"initialHeaders": {"x-ms-client-request-id": "database-throughput-parity"}}
        original = deepcopy(options)
        callbacks = []

        def hook(headers, offers):
            callbacks.append((dict(headers), deepcopy(list(offers))))
            headers.clear()
            offers[0]["content"]["offerThroughput"] = 999

        result = await run_target_operation_async(
            client, lambda: database.get_throughput(request_options=options, response_hook=hook)
        )
        assert options == original
        assert len(callbacks) == 1
        assert result.offer_throughput == 1000
        assert callbacks[0][1][0]["content"]["offerThroughput"] == 1000
        headers = result.get_response_headers()
        assert float(headers["x-ms-request-charge"]) > 0
        assert dict(headers) == callbacks[0][0]
        await database.read()
        assert result.get_response_headers() == headers
        return _normalize_throughput(result)

    comparison = await run_on_both_backends_async(
        read, description=f"async database throughput ownership, warm properties={warm}",
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
async def test_rust_database_read_rejects_unsupported_inputs_async(monkeypatch, options):
    from azure.cosmos.aio import CosmosClient as AsyncCosmosClient

    async with AsyncCosmosClient(
        os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust",
    ) as client:
        database = client.get_database_client("not-requested")

        def unexpected_request(*args, **kwargs):
            pytest.fail("unsupported input must be rejected before metadata or legacy execution")

        monkeypatch.setattr(database, "_get_properties", unexpected_request)
        monkeypatch.setattr(client.client_connection, "QueryOffers", unexpected_request)
        with pytest.raises(NotImplementedError, match="legacy Python path"):
            await run_target_operation_async(
                client, lambda: database.get_throughput(**options), expect_rust=False,
            )
