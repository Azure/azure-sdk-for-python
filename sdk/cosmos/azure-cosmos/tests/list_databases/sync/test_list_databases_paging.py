# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""Live ``list_databases`` results and paging on the Rust backend.

The account is shared, so assertions only concern the databases this module
creates and tolerate any others.
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
    ids = ["rust_list_db_{}_{}".format(index, uuid.uuid4().hex[:12]) for index in range(3)]
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


@pytest.fixture
def client():
    rust_client = _rust_client()
    try:
        yield rust_client
    finally:
        rust_client.close()


def test_listed_databases_include_created_ones_with_system_properties_rust(client, database_ids):
    """Every created database is listed with its id, _rid, _self, _etag and _ts properties."""
    snapshots = []

    def target():
        rows = []
        page_count = 0
        for page in client.list_databases(
            max_item_count=2,
            timeout=10,
            throughput_bucket=1,
            initial_headers={"x-list-databases-test": "sync"},
            response_hook=lambda headers: snapshots.append(dict(headers)),
        ).by_page():
            rows.extend(page)
            page_count += 1
            assert len(snapshots) == page_count
            assert (
                snapshots[-1]["x-ms-activity-id"] == client.client_connection.last_response_headers["x-ms-activity-id"]
            )
        assert page_count >= 2
        return rows

    rows = run_on_rust(client, target)
    assert_live_page_headers(snapshots)
    selected = [row for row in rows if row.get("id") in database_ids]
    assert sorted(row["id"] for row in selected) == sorted(database_ids)
    for row in selected:
        assert {"id", "_rid", "_self", "_etag", "_ts"}.issubset(row)


def test_continuation_token_replays_second_page_rust(client, database_ids):
    """With one database per page, the token saved after page one fetches the same second page again."""
    assert len(database_ids) == 3

    def target():
        iterable = client.list_databases(max_item_count=1)
        pager = iterable.by_page()
        first_page = list(next(pager))
        continuation = pager.continuation_token
        second_page = list(next(pager))
        replay_page = list(next(iterable.by_page(continuation)))
        return first_page, continuation, second_page, replay_page

    first_page, continuation, second_page, replay_page = run_on_rust(client, target)
    assert len(first_page) == 1
    assert len(second_page) == 1
    assert continuation is not None
    assert replay_page[0]["id"] == second_page[0]["id"]
