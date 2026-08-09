# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Live sync parity tests for ``CosmosClient.query_databases``."""
from __future__ import annotations

import os
import uuid
import warnings
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


def test_query_databases_options_hook_and_ignored_session_token(database_ids):
    """Request options work while the irrelevant session token keeps its warning contract."""

    def _do(client):
        """Run with all options set and capture hook calls and deprecation warnings."""

        def _target():
            """Execute the full-options query and return diagnostic counters."""
            hook_calls = []
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                rows = list(
                    client.query_databases(
                        query="SELECT * FROM root r",
                        max_item_count=2,
                        initial_headers={"x-query-databases-test": "sync"},
                        response_hook=lambda headers: hook_calls.append(headers),
                        session_token="ignored-session-token",
                        throughput_bucket=1,
                    )
                )
            return {
                "target_ids": sorted(row["id"] for row in rows if row.get("id") in database_ids),
                "hook_count": len(hook_calls),
                "hook_received_mapping": bool(hook_calls) and isinstance(hook_calls[0], Mapping),
                # ResourceWarning entries are garbage-collector noise that can
                # land in this capture from unrelated objects, so they are
                # filtered out to keep the comparison about this call.
                "warning_categories": [
                    warning.category.__name__
                    for warning in caught
                    if not issubclass(warning.category, ResourceWarning)
                ],
                "warning_mentions_session_token": any(
                    "session_token" in str(warning.message) for warning in caught
                ),
            }

        return run_target_operation(client, _target)

    comparison = run_on_both_backends(_do, description="query_databases options")
    comparison.assert_functional_parity()
    result = comparison.rust.return_value
    assert result["target_ids"] == sorted(database_ids)
    assert result["hook_count"] >= 1
    assert result["hook_received_mapping"]
    assert result["warning_categories"] == ["UserWarning"]
    assert result["warning_mentions_session_token"]
