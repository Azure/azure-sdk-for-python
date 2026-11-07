# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""Live ``query_databases`` per-page response hook behavior on the Rust backend."""
from __future__ import annotations

import os
import uuid
from collections.abc import Mapping

import pytest

from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from common._rust_checks import run_on_rust


def _rust_client():
    return CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")


@pytest.fixture(scope="module")
def database_ids():
    ids = ["rust_query_db_hook_{}_{}".format(index, uuid.uuid4().hex[:12]) for index in range(3)]
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


def test_response_hook_runs_lazily_per_page_with_isolated_headers_rust(database_ids):
    """The hook is not called until iteration, then once per page with that page's headers.

    Each page's headers carry the same activity id as ``last_response_headers``
    at that point, a positive request charge and the SDK diagnostics header.
    Changes the hook makes to its headers do not leak into
    ``last_response_headers``. Request options are accepted.
    """
    client = _rust_client()
    try:
        hook_calls = []

        def hook(headers):
            hook_calls.append(dict(headers))
            headers["x-hook-mutation"] = "isolated"

        iterable = client.query_databases(
            query="SELECT * FROM root r WHERE r.id IN (@id0, @id1, @id2)",
            parameters=[
                {"name": "@id{}".format(index), "value": database_id}
                for index, database_id in enumerate(database_ids)
            ],
            max_item_count=1,
            initial_headers={"x-query-databases-test": "sync"},
            response_hook=hook,
            throughput_bucket=1,
            timeout=10,
        )
        assert hook_calls == []

        def target():
            rows = []
            page_count = 0
            for page in iterable.by_page():
                page_count += 1
                assert len(hook_calls) == page_count
                headers = hook_calls[-1]
                assert isinstance(headers, Mapping)
                last_headers = client.client_connection.last_response_headers
                assert headers["x-ms-activity-id"] == last_headers["x-ms-activity-id"]
                assert "x-hook-mutation" not in last_headers
                assert float(headers["x-ms-request-charge"]) > 0
                assert headers["x-ms-cosmos-sdk-diagnostics"]
                rows.extend(page)
            return rows, page_count

        rows, page_count = run_on_rust(client, target)
    finally:
        client.close()
    assert sorted(row["id"] for row in rows) == sorted(database_ids)
    assert len(hook_calls) == page_count
    assert len({headers["x-ms-activity-id"] for headers in hook_calls}) == page_count
    assert page_count >= 3
