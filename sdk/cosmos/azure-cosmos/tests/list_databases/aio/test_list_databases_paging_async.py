# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""Live async ``list_databases`` results and paging on the Rust backend.

The account is shared, so assertions only concern the databases this module
creates and tolerate any others.
"""
from __future__ import annotations

import os
import uuid

import pytest

from azure.cosmos import CosmosClient as SyncCosmosClient
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from common._rust_checks import assert_live_page_headers, run_on_rust_async

pytestmark = [pytest.mark.asyncio, pytest.mark.cosmosEmulator]


def _rust_client():
    return CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")


@pytest.fixture(scope="module")
def database_ids():
    ids = ["rust_list_db_aio_{}_{}".format(index, uuid.uuid4().hex[:12]) for index in range(3)]
    client = SyncCosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")
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


async def test_listed_databases_include_created_ones_with_system_properties_async_rust(database_ids):
    """Every created database is listed with its id, _rid, _self, _etag and _ts properties."""
    async with _rust_client() as client:
        snapshots = []

        async def target():
            rows = []
            page_count = 0
            async for page in client.list_databases(
                max_item_count=2,
                timeout=10,
                throughput_bucket=1,
                initial_headers={"x-list-databases-test": "async"},
                response_hook=lambda headers: snapshots.append(dict(headers)),
            ).by_page():
                rows.extend([row async for row in page])
                page_count += 1
                assert len(snapshots) == page_count
                assert (
                    snapshots[-1]["x-ms-activity-id"]
                    == client.client_connection.last_response_headers["x-ms-activity-id"]
                )
            assert page_count >= 2
            return rows

        rows = await run_on_rust_async(client, target)
    assert_live_page_headers(snapshots)
    selected = [row for row in rows if row.get("id") in database_ids]
    assert sorted(row["id"] for row in selected) == sorted(database_ids)
    for row in selected:
        assert {"id", "_rid", "_self", "_etag", "_ts"}.issubset(row)


async def test_continuation_token_replays_second_page_async_rust(database_ids):
    """With one database per page, the token saved after page one fetches the same second page again."""
    assert len(database_ids) == 3
    async with _rust_client() as client:

        async def target():
            iterable = client.list_databases(max_item_count=1)
            pager = iterable.by_page()
            first_page = [item async for item in await pager.__anext__()]
            continuation = pager.continuation_token
            second_page = [item async for item in await pager.__anext__()]
            replay_page = [item async for item in await iterable.by_page(continuation).__anext__()]
            return first_page, continuation, second_page, replay_page

        first_page, continuation, second_page, replay_page = await run_on_rust_async(client, target)
    assert len(first_page) == 1
    assert len(second_page) == 1
    assert continuation is not None
    assert replay_page[0]["id"] == second_page[0]["id"]
