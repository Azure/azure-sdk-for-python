# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Live async parity tests for ``DatabaseProxy.read``.

Async twin of ``tests/read_database/sync/test_read_database_parity.py``, which
carries the full explanation of what these scenarios cover and why. Same
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
from azure.core import MatchConditions

from common._parity_helpers import (
    run_on_both_backends_async,
    run_target_operation_async,
    skip_unless_emulator,
    skip_unless_rust_binding,
)
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosResourceNotFoundError


pytestmark = [skip_unless_emulator(), skip_unless_rust_binding()]


@pytest.fixture(scope="module")
def readable_database_id():
    database_id = "parity_read_db_async_" + uuid.uuid4().hex[:12]
    with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"]) as client:
        try:
            client.create_database(database_id)
            yield database_id
        finally:
            try:
                client.delete_database(database_id)
            except CosmosResourceNotFoundError:
                pass  # A failed create may not have reached the service.


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
    assert comparison.core_python.raised is None
    assert comparison.rust.raised is None
    comparison.assert_functional_parity()


@pytest.mark.asyncio
async def test_read_database_options_and_response_hook_async(readable_database_id):
    """Async supported options and isolated hooks retain parity."""

    async def _call(client):
        hook_calls = []
        database = client.get_database_client(readable_database_id)
        def hook(headers, body):
            assert "X-MS-REQUEST-CHARGE" in headers
            hook_calls.append((headers, dict(body)))
            headers["x-test-hook-only"] = "not-sdk-state"

        properties = await run_target_operation_async(
            client,
            lambda: database.read(
                initial_headers={"x-ms-cosmos-throughput-bucket": "1"},
                timeout=10,
                response_hook=hook,
            ),
        )
        assert len(hook_calls) == 1
        assert "x-test-hook-only" not in properties.get_response_headers()
        assert "x-test-hook-only" not in client.client_connection.last_response_headers
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
            "timeout": 10,
            "response_hook": "<callable>",
        },
    )
    assert comparison.core_python.raised is None
    assert comparison.rust.raised is None
    comparison.assert_functional_parity()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "condition, empty_body",
    [(MatchConditions.IfNotModified, False), (MatchConditions.IfModified, True),
     (MatchConditions.IfPresent, False)],
)
async def test_read_database_conditional_read_async(readable_database_id, condition, empty_body):
    async def _call(client):
        database = client.get_database_client(readable_database_id)
        original = await database.read()
        hook_calls = []
        properties = await run_target_operation_async(
            client,
            lambda: database.read(
                etag="unused" if condition == MatchConditions.IfPresent else original["_etag"],
                match_condition=condition,
                response_hook=lambda headers, body: hook_calls.append((headers, body)),
            ),
        )
        assert len(hook_calls) == 1
        assert hook_calls[0][1] == (None if empty_body else properties)
        assert properties == ({} if empty_body else original)
        return {"body": dict(properties), "etag": properties.get_response_headers()["etag"]}

    comparison = await run_on_both_backends_async(_call, description=f"async read_database conditional {condition.name}")
    assert comparison.core_python.raised is None
    assert comparison.rust.raised is None
    comparison.assert_functional_parity()


@pytest.mark.asyncio
async def test_read_database_preserves_service_behavior_for_stale_if_match_async(readable_database_id):
    """The service does not enforce If-Match on this GET; do not invent a 412."""
    async def _call(client):
        database = client.get_database_client(readable_database_id)
        return await run_target_operation_async(
            client, lambda: database.read(etag='"stale-version"', match_condition=MatchConditions.IfNotModified),
        )

    comparison = await run_on_both_backends_async(_call, description="async read_database stale If-Match")
    assert comparison.core_python.raised is None
    assert comparison.rust.raised is None
    assert comparison.core_python.return_value["id"] == readable_database_id
    assert comparison.rust.return_value["id"] == readable_database_id
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
