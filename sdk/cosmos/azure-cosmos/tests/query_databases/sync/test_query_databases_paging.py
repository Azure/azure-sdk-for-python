# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""Live ``query_databases`` continuation behavior on the Rust backend.

The account is shared; the query selects only the three databases this module
creates.
"""

from __future__ import annotations

import os
import uuid

import pytest

from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from common._rust_checks import assert_live_page_headers, run_on_rust

pytestmark = [pytest.mark.cosmosEmulator]


def _rust_client():
    return CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")


@pytest.fixture(scope="module")
def database_ids():
    ids = ["rust_query_db_{}_{}".format(index, uuid.uuid4().hex[:12]) for index in range(3)]
    client = _rust_client()
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


def test_continuation_token_replays_second_page_rust(database_ids):
    """With one database per page, the token saved after page one fetches the same second page again."""
    assert len(database_ids) == 3
    client = _rust_client()
    try:
        snapshots = []

        def consume(page):
            rows = list(page)
            assert (
                snapshots[-1]["x-ms-activity-id"] == client.client_connection.last_response_headers["x-ms-activity-id"]
            )
            return rows

        def target():
            iterable = client.query_databases(
                query="SELECT * FROM root r WHERE r.id IN (@id0, @id1, @id2)",
                parameters=[
                    {"name": "@id{}".format(index), "value": database_id}
                    for index, database_id in enumerate(database_ids)
                ],
                max_item_count=1,
                timeout=10,
                throughput_bucket=1,
                initial_headers={"x-query-databases-test": "sync"},
                response_hook=lambda headers: snapshots.append(dict(headers)),
            )
            pager = iterable.by_page()
            first_page = consume(next(pager))
            continuation = pager.continuation_token
            second_page = consume(next(pager))
            remaining_pages = [consume(page) for page in pager]
            rows = first_page + second_page + [row for page in remaining_pages for row in page]
            assert sorted(row["id"] for row in rows) == sorted(database_ids)
            assert len(snapshots) == 2 + len(remaining_pages) >= 3
            assert_live_page_headers(snapshots)
            replay_page = list(next(iterable.by_page(continuation)))
            return first_page, continuation, second_page, replay_page

        first_page, continuation, second_page, replay_page = run_on_rust(client, target)
    finally:
        client.close()
    assert len(first_page) == 1
    assert len(second_page) == 1
    assert continuation is not None
    assert replay_page[0]["id"] == second_page[0]["id"]
