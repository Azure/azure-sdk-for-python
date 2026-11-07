# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""Live async ``query_databases`` continuation behavior on the Rust backend.

The account is shared; the module creates three databases so at least that
many pages exist, and tolerates any others.
"""
from __future__ import annotations

import os
import uuid

import pytest

from azure.cosmos import CosmosClient as SyncCosmosClient
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from common._rust_checks import run_on_rust_async

pytestmark = [pytest.mark.asyncio]


@pytest.fixture(scope="module")
def database_ids():
    ids = ["rust_query_db_aio_{}_{}".format(index, uuid.uuid4().hex[:12]) for index in range(3)]
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


async def test_continuation_token_replays_second_page_async_rust(database_ids):
    """With one database per page, the token saved after page one fetches the same second page again."""
    assert len(database_ids) == 3
    async with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as client:

        async def target():
            iterable = client.query_databases(query="SELECT * FROM root r", max_item_count=1)
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
