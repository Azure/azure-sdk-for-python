# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Live async parity tests for ``CosmosClient.create_database``."""
from __future__ import annotations

import os
import uuid

import pytest

from common._parity_helpers import (
    run_on_both_backends_async,
    skip_unless_emulator,
    skip_unless_rust_binding,
)

from azure.cosmos import ThroughputProperties
from azure.cosmos.aio import CosmosClient


pytestmark = [skip_unless_emulator(), skip_unless_rust_binding()]


def _database_id(label):
    return "parity_create_db_{}_{}".format(label, uuid.uuid4().hex[:12])


async def _cleanup(database_ids):
    async with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"]) as client:
        for database_id in database_ids:
            try:
                await client.delete_database(database_id)
            except Exception:  # pylint: disable=broad-except
                pass


async def _run_case(label, call):
    database_ids = []

    async def _do(client):
        database_id = _database_id(label)
        database_ids.append(database_id)
        return await call(client, database_id)

    try:
        return await run_on_both_backends_async(_do, description=label)
    finally:
        await _cleanup(database_ids)


@pytest.mark.asyncio
async def test_create_database_baseline_properties_async():
    """Minimal create returns the same customer-visible database document."""

    async def _call(client, database_id):
        _proxy, properties = await client.create_database(database_id, return_properties=True)
        return dict(properties)

    comparison = await _run_case("async create_database baseline", _call)
    comparison.assert_functional_parity()


@pytest.mark.asyncio
async def test_create_database_manual_throughput_async():
    """Manual database throughput is created and read back identically."""

    async def _call(client, database_id):
        database = await client.create_database(database_id, offer_throughput=1000)
        throughput = await database.get_throughput()
        return {"id": database.id, "offer_throughput": throughput.offer_throughput}

    comparison = await _run_case("async create_database manual throughput", _call)
    comparison.assert_functional_parity()


@pytest.mark.asyncio
async def test_create_database_autoscale_zero_increment_async():
    """Autoscale max throughput and an explicit zero increment survive the request."""

    async def _call(client, database_id):
        database = await client.create_database(
            database_id,
            offer_throughput=ThroughputProperties(
                auto_scale_max_throughput=5000,
                auto_scale_increment_percent=0,
            ),
        )
        throughput = await database.get_throughput()
        return {
            "id": database.id,
            "auto_scale_max_throughput": throughput.auto_scale_max_throughput,
            "auto_scale_increment_percent": throughput.auto_scale_increment_percent,
        }

    comparison = await _run_case("async create_database autoscale increment zero", _call)
    comparison.assert_functional_parity()


@pytest.mark.asyncio
async def test_create_database_options_and_response_hook_async():
    """Throughput bucket, initial headers and response hook work on both backends."""

    async def _call(client, database_id):
        hook_calls = []
        _proxy, properties = await client.create_database(
            database_id,
            throughput_bucket=1,
            initial_headers={"x-ms-cosmos-throughput-bucket": "1"},
            return_properties=True,
            response_hook=lambda headers, body: hook_calls.append(
                (dict(headers), dict(body))
            ),
        )
        return {
            "database_id_matches": properties["id"] == database_id,
            "hook_count": len(hook_calls),
            "hook_database_id_matches": hook_calls[0][1]["id"] == database_id,
            "request_charge_present": "x-ms-request-charge" in {
                key.lower() for key in hook_calls[0][0]
            },
        }

    comparison = await _run_case("async create_database options and response hook", _call)
    comparison.assert_functional_parity()


@pytest.mark.asyncio
async def test_create_database_duplicate_maps_409_async():
    """Creating the same database twice raises the same typed 409 exception."""

    async def _call(client, database_id):
        await client.create_database(database_id)
        return await client.create_database(database_id)

    comparison = await _run_case("async create_database duplicate 409", _call)
    comparison.assert_functional_exception_parity()
