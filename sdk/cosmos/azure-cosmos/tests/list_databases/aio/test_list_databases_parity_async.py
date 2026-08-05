# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Live async parity tests for ``CosmosClient.list_databases``."""
from __future__ import annotations

import os
import uuid
import warnings
from collections.abc import Mapping

import pytest

from azure.cosmos import CosmosClient as SyncCosmosClient
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from common._parity_helpers import (
    run_on_both_backends_async,
    run_target_operation_async,
    skip_unless_emulator,
    skip_unless_rust_binding,
)


pytestmark = [skip_unless_emulator(), skip_unless_rust_binding()]


@pytest.fixture(scope="module")
def database_ids():
    ids = ["parity_list_db_aio_{}_{}".format(index, uuid.uuid4().hex[:12]) for index in range(3)]
    client = SyncCosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])
    try:
        for database_id in ids:
            client.create_database(database_id)
        yield tuple(ids)
    finally:
        for database_id in ids:
            try:
                client.delete_database(database_id)
            except CosmosResourceNotFoundError:
                pass
        client.close()


@pytest.mark.asyncio
async def test_list_databases_baseline_properties_async(database_ids):
    """Both async backends return the created databases with the normal property shape."""

    async def _do(client):
        async def _target():
            rows = [row async for row in client.list_databases()]
            selected = [row for row in rows if row.get("id") in database_ids]
            return {
                "ids": sorted(row["id"] for row in selected),
                "all_properties_present": all(
                    {"id", "_rid", "_self", "_etag", "_ts"}.issubset(row) for row in selected
                ),
            }

        return await run_target_operation_async(client, _target)

    comparison = await run_on_both_backends_async(_do, description="async list_databases baseline")
    comparison.assert_functional_parity()
    assert comparison.rust.return_value["ids"] == sorted(database_ids)
    assert comparison.rust.return_value["all_properties_present"]


@pytest.mark.asyncio
async def test_list_databases_continuation_replay_async(database_ids):
    """Async one-item paging exposes a continuation token that can be replayed."""
    assert len(database_ids) == 3

    async def _do(client):
        async def _target():
            iterable = client.list_databases(max_item_count=1)
            pager = iterable.by_page()
            first_page = [item async for item in await pager.__anext__()]
            continuation = pager.continuation_token
            second_page = [item async for item in await pager.__anext__()]
            replay_page = [
                item async for item in await iterable.by_page(continuation).__anext__()
            ]
            return {
                "first_page_size": len(first_page),
                "second_page_size": len(second_page),
                "token_present": continuation is not None,
                "second_id": second_page[0]["id"],
                "replay_id": replay_page[0]["id"],
            }

        return await run_target_operation_async(client, _target)

    comparison = await run_on_both_backends_async(
        _do, description="async list_databases continuation replay"
    )
    comparison.assert_functional_parity()
    result = comparison.rust.return_value
    assert result["first_page_size"] == 1
    assert result["second_page_size"] == 1
    assert result["token_present"]
    assert result["second_id"] == result["replay_id"]


@pytest.mark.asyncio
async def test_list_databases_options_hook_and_ignored_session_token_async(database_ids):
    """Async request options preserve the ignored-session-token warning contract."""

    async def _do(client):
        async def _target():
            hook_calls = []
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                rows = [
                    row
                    async for row in client.list_databases(
                        max_item_count=2,
                        initial_headers={"x-list-databases-test": "aio"},
                        response_hook=lambda headers: hook_calls.append(headers),
                        session_token="ignored-session-token",
                        throughput_bucket=1,
                    )
                ]
            return {
                "target_ids": sorted(row["id"] for row in rows if row.get("id") in database_ids),
                "hook_count": len(hook_calls),
                "hook_received_mapping": bool(hook_calls) and isinstance(hook_calls[0], Mapping),
                "warning_categories": [warning.category.__name__ for warning in caught],
                "warning_mentions_session_token": any(
                    "session_token" in str(warning.message) for warning in caught
                ),
            }

        return await run_target_operation_async(client, _target)

    comparison = await run_on_both_backends_async(
        _do, description="async list_databases options"
    )
    comparison.assert_functional_parity()
    result = comparison.rust.return_value
    assert result["target_ids"] == sorted(database_ids)
    assert result["hook_count"] == 1
    assert result["hook_received_mapping"]
    assert result["warning_categories"] == ["DeprecationWarning"]
    assert result["warning_mentions_session_token"]
