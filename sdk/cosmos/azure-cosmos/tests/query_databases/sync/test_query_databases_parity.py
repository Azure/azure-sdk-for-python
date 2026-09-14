# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Live sync parity tests for ``CosmosClient.query_databases``."""
from __future__ import annotations

import os
import uuid
from collections.abc import Mapping

import pytest

from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from common._parity_helpers import (
    run_on_both_backends,
    run_target_operation,
    skip_unless_emulator,
    skip_unless_rust_binding,
)


pytestmark = [skip_unless_emulator(), skip_unless_rust_binding()]


@pytest.fixture(scope="module")
def database_ids():
    """Three databases shared across all sync query-databases parity tests."""
    ids = ["parity_query_db_{}_{}".format(index, uuid.uuid4().hex[:12]) for index in range(3)]
    client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])
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


def test_query_databases_parameterized_filter(database_ids):
    """A parameterized filter returns exactly the one database it names."""
    target_id = database_ids[0]

    def _do(client):
        """Run the parameterized query and collect ids plus system-property presence."""

        def _target():
            """Execute the query against the active client backend."""
            rows = list(
                client.query_databases(
                    query="SELECT * FROM root r WHERE r.id = @id",
                    parameters=[{"name": "@id", "value": target_id}],
                )
            )
            return {
                "ids": sorted(row["id"] for row in rows),
                "all_properties_present": all(
                    {"id", "_rid", "_self", "_etag", "_ts"}.issubset(row) for row in rows
                ),
            }

        return run_target_operation(client, _target)

    comparison = run_on_both_backends(_do, description="query_databases parameterized filter")
    comparison.assert_functional_parity()
    assert comparison.rust.return_value["ids"] == [target_id]
    assert comparison.rust.return_value["all_properties_present"]


def test_query_databases_no_match_returns_empty(database_ids):
    """A filter that matches nothing returns an empty result on both backends."""

    def _do(client):
        """Run the no-match query and return the row count."""

        def _target():
            """Execute the query against the active client backend."""
            rows = list(
                client.query_databases(
                    query="SELECT * FROM root r WHERE r.id = @id",
                    parameters=[{"name": "@id", "value": "no-such-database-{}".format(uuid.uuid4().hex)}],
                )
            )
            return {"count": len(rows)}

        return run_target_operation(client, _target)

    comparison = run_on_both_backends(_do, description="query_databases no match")
    comparison.assert_functional_parity()
    assert comparison.rust.return_value["count"] == 0


def test_query_databases_continuation_replay(database_ids):
    """A one-item page exposes a continuation token that resumes deterministically."""
    assert len(database_ids) == 3

    def _do(client):
        """Page through results and verify the continuation token replays the second page."""

        def _target():
            """Fetch two pages then replay the second page via the saved token."""
            iterable = client.query_databases(query="SELECT * FROM root r", max_item_count=1)
            pager = iterable.by_page()
            first_page = list(next(pager))
            continuation = pager.continuation_token
            second_page = list(next(pager))
            replay_page = list(next(iterable.by_page(continuation)))
            return {
                "first_page_size": len(first_page),
                "second_page_size": len(second_page),
                "token_present": continuation is not None,
                "second_id": second_page[0]["id"],
                "replay_id": replay_page[0]["id"],
            }

        return run_target_operation(client, _target)

    comparison = run_on_both_backends(_do, description="query_databases continuation replay")
    comparison.assert_functional_parity()
    result = comparison.rust.return_value
    assert result["first_page_size"] == 1
    assert result["second_page_size"] == 1
    assert result["token_present"]
    assert result["second_id"] == result["replay_id"]


def test_query_databases_options_and_page_hooks(database_ids):
    """Supported options and hooks apply to each fetched query page."""

    def _do(client):
        """Capture actual page headers without invoking the hook eagerly."""

        def _target():
            hook_calls = []
            iterable = client.query_databases(
                query="SELECT * FROM root r WHERE r.id IN (@id0, @id1, @id2)",
                parameters=[
                    {"name": "@id{}".format(index), "value": database_id}
                    for index, database_id in enumerate(database_ids)
                ],
                max_item_count=1,
                initial_headers={"x-query-databases-test": "sync"},
                response_hook=hook_calls.append,
                throughput_bucket=1,
                timeout=10,
            )
            assert hook_calls == []
            rows = []
            page_count = 0
            for page in iterable.by_page():
                page_count += 1
                assert len(hook_calls) == page_count
                headers = hook_calls[-1]
                assert isinstance(headers, Mapping)
                assert headers["x-ms-activity-id"] == client.client_connection.last_response_headers["x-ms-activity-id"]
                assert float(headers["x-ms-request-charge"]) > 0
                if client.client_connection._backend.name == "rust":
                    assert headers["x-ms-cosmos-sdk-diagnostics"]
                rows.extend(page)
            return {
                "target_ids": sorted(row["id"] for row in rows),
                "hook_count": len(hook_calls),
                "page_count": page_count,
                "distinct_page_headers": len({headers["x-ms-activity-id"] for headers in hook_calls}),
            }

        return run_target_operation(client, _target)

    comparison = run_on_both_backends(_do, description="query_databases options")
    comparison.assert_functional_parity()
    result = comparison.rust.return_value
    assert result["target_ids"] == sorted(database_ids)
    assert result["hook_count"] == result["page_count"] == result["distinct_page_headers"]
    assert result["page_count"] >= 3
