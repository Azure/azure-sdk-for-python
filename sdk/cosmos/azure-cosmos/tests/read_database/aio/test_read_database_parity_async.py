# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Live async parity tests for ``DatabaseProxy.read``.

Async twin of ``tests/read_database/sync/test_read_database_parity.py``, which
carries the full explanation of what these scenarios cover and why. Same three
scenarios, same comparison across both engines.

Worth running separately rather than trusting the sync results: the async path
builds its request through a different wrapper (the async engine awaits the
request builder), so it is genuinely different code, not the same code with
``await`` in front of it.
"""
from __future__ import annotations

import os
import uuid

import pytest

from common._parity_helpers import (
    run_on_both_backends_async,
    run_target_operation_async,
    skip_unless_emulator,
    skip_unless_rust_binding,
)
from azure.cosmos import CosmosClient


pytestmark = [skip_unless_emulator(), skip_unless_rust_binding()]


@pytest.fixture(scope="module")
def readable_database_id():
    database_id = "parity_read_db_async_" + uuid.uuid4().hex[:12]
    client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])
    client.create_database(database_id)
    try:
        yield database_id
    finally:
        try:
            client.delete_database(database_id)
        finally:
            client.close()


@pytest.mark.asyncio
async def test_read_database_baseline_properties_async(readable_database_id):
    """Both async backends return the same stable database properties."""

    async def _call(client):
        database = client.get_database_client(readable_database_id)
        properties = await run_target_operation_async(client, database.read)
        return {
            key: properties.get(key)
            for key in ("id", "_rid", "_self", "_etag", "_colls", "_users")
        }

    comparison = await run_on_both_backends_async(
        _call,
        description="async read_database baseline properties",
    )
    comparison.assert_functional_parity()


@pytest.mark.asyncio
async def test_read_database_options_and_response_hook_async(readable_database_id):
    """Async initial headers, ignored session tokens and hooks retain parity."""

    async def _call(client):
        hook_calls = []
        database = client.get_database_client(readable_database_id)
        with pytest.warns(DeprecationWarning, match="session_token"):
            properties = await run_target_operation_async(
                client,
                lambda: database.read(
                    initial_headers={"x-ms-cosmos-throughput-bucket": "1"},
                    session_token="ignored",
                    response_hook=lambda headers, body: hook_calls.append(
                        (dict(headers), dict(body))
                    ),
                ),
            )
        return {
            "database_id_matches": properties["id"] == readable_database_id,
            "hook_count": len(hook_calls),
            "hook_database_id_matches": hook_calls[0][1]["id"] == readable_database_id,
            "request_charge_present": "x-ms-request-charge" in {
                key.lower() for key in hook_calls[0][0]
            },
        }

    comparison = await run_on_both_backends_async(
        _call,
        description="async read_database options and response hook",
        request_kwargs={
            "initial_headers": {"x-ms-cosmos-throughput-bucket": "1"},
            "session_token": "ignored",
            "response_hook": "<callable>",
        },
    )
    comparison.assert_functional_parity()


@pytest.mark.asyncio
async def test_read_database_missing_maps_404_async():
    """An async missing database raises the same typed 404 exception."""
    database_id = "parity_missing_read_db_async_" + uuid.uuid4().hex

    async def _call(client):
        database = client.get_database_client(database_id)
        return await run_target_operation_async(client, database.read)

    comparison = await run_on_both_backends_async(
        _call,
        description="async read_database missing 404",
    )
    comparison.assert_functional_exception_parity()
