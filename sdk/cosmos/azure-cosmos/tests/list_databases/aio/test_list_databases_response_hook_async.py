# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""Live async ``list_databases`` per-page response hook behavior on the Rust backend.

The account is shared, so result assertions only concern the databases this
module creates and tolerate any others.
"""
from __future__ import annotations

import os
import uuid
from collections.abc import Mapping

import pytest

from azure.cosmos import CosmosClient as SyncCosmosClient
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from common._rust_checks import run_on_rust_async

pytestmark = [pytest.mark.asyncio]


@pytest.fixture(scope="module")
def database_ids():
    ids = ["rust_list_db_aio_hook_{}_{}".format(index, uuid.uuid4().hex[:12]) for index in range(3)]
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


async def test_response_hook_runs_lazily_per_page_with_matching_headers_async_rust(database_ids):
    """The hook is not called until iteration, then once per page with that page's headers.

    Each page's headers carry the same activity id as ``last_response_headers``
    at that point, a positive request charge and the SDK diagnostics header.
    Request options (initial headers, throughput bucket, timeout) are accepted.
    """
    async with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as client:
        hook_calls = []
        iterable = client.list_databases(
            max_item_count=2,
            initial_headers={"x-list-databases-test": "aio"},
            response_hook=hook_calls.append,
            throughput_bucket=1,
            timeout=10,
        )
        assert hook_calls == []

        async def target():
            rows = []
            page_count = 0
            async for page in iterable.by_page():
                page_count += 1
                assert len(hook_calls) == page_count
                headers = hook_calls[-1]
                assert isinstance(headers, Mapping)
                last_headers = client.client_connection.last_response_headers
                assert headers["x-ms-activity-id"] == last_headers["x-ms-activity-id"]
                assert float(headers["x-ms-request-charge"]) > 0
                assert headers["x-ms-cosmos-sdk-diagnostics"]
                rows.extend([row async for row in page])
            return rows, page_count

        rows, page_count = await run_on_rust_async(client, target)
    assert sorted(row["id"] for row in rows if row.get("id") in database_ids) == sorted(database_ids)
    assert len(hook_calls) == page_count
    assert len({headers["x-ms-activity-id"] for headers in hook_calls}) == page_count
    assert page_count >= 2
