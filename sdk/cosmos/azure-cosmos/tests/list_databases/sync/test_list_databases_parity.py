# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Live sync parity tests for ``CosmosClient.list_databases``."""
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
    """Create database IDs that must appear in every backend result."""
    ids = ["parity_list_db_{}_{}".format(index, uuid.uuid4().hex[:12]) for index in range(3)]
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


def test_list_databases_baseline_properties(database_ids):
    """Both backends return the created databases with the normal property shape."""

    def _do(client):
        def _target():
            rows = list(client.list_databases())
            selected = [row for row in rows if row.get("id") in database_ids]
            return {
                "ids": sorted(row["id"] for row in selected),
                "all_properties_present": all(
                    {"id", "_rid", "_self", "_etag", "_ts"}.issubset(row) for row in selected
                ),
            }

        return run_target_operation(client, _target)

    comparison = run_on_both_backends(_do, description="list_databases baseline")
    comparison.assert_functional_parity()
    assert comparison.rust.return_value["ids"] == sorted(database_ids)
    assert comparison.rust.return_value["all_properties_present"]


def test_list_databases_continuation_replay(database_ids):
    """A one-item page exposes a continuation token that resumes deterministically."""
    assert len(database_ids) == 3

    def _do(client):
        def _target():
            iterable = client.list_databases(max_item_count=1)
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

    comparison = run_on_both_backends(_do, description="list_databases continuation replay")
    comparison.assert_functional_parity()
    result = comparison.rust.return_value
    assert result["first_page_size"] == 1
    assert result["second_page_size"] == 1
    assert result["token_present"]
    assert result["second_id"] == result["replay_id"]


def test_list_databases_options_and_page_hooks(database_ids):
    """Supported options preserve lazy per-page metadata on both backends."""

    def _do(client):
        def _target():
            hook_calls = []
            iterable = client.list_databases(
                max_item_count=2,
                initial_headers={"x-list-databases-test": "sync"},
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
                "target_ids": sorted(row["id"] for row in rows if row.get("id") in database_ids),
                "hook_count": len(hook_calls),
                "page_count": page_count,
                "distinct_page_headers": len({headers["x-ms-activity-id"] for headers in hook_calls}),
            }

        return run_target_operation(client, _target)

    comparison = run_on_both_backends(_do, description="list_databases options")
    comparison.assert_functional_parity()
    result = comparison.rust.return_value
    assert result["target_ids"] == sorted(database_ids)
    assert result["hook_count"] == result["page_count"] == result["distinct_page_headers"]
    assert result["page_count"] >= 2
