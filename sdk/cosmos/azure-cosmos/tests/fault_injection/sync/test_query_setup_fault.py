# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""A metadata error leaves the public sync query iterator retryable."""

import os
import time
import uuid

import pytest

from azure.core.exceptions import AzureError
from azure.cosmos import CosmosClient
from common._parity_helpers import _binding_operation_count, _rust_fallback_count
from fault_injection._delayed_create import assert_route, emit
from fault_injection._query_resume import (
    PAGE_BUDGET,
    QUERY,
    assert_complete,
    capture_query_calls,
    set_rule,
)
from fault_injection._query_setup import (
    assert_guard_failure,
    assert_setup_failure,
    setup_rules,
)

pytestmark = pytest.mark.cosmosEmulator


@pytest.mark.timeout(90)
@pytest.mark.parametrize(
    "inject", [True, False], ids=["cold-metadata-failure", "no-injection"]
)
def test_query_setup_error_retries_same_iterator(owned_target, monkeypatch, inject):
    database_id, observer = owned_target
    partition = uuid.uuid4().hex
    items = [
        {
            "id": f"{partition}-{i}",
            "pk": partition,
            "name": f"order-{i}",
            "state": "confirmed",
        }
        for i in range(3)
    ]
    for item in items:
        observer.create_item(item)
    metadata_id, guard_id = "setup-" + uuid.uuid4().hex, "guard-" + uuid.uuid4().hex
    with CosmosClient(
        os.environ["ACCOUNT_HOST"],
        os.environ["ACCOUNT_KEY"],
        _backend="rust",
        consistency_level="Session",
        retry_throttle_total=0,
        _fault_injection_rules=setup_rules(metadata_id, guard_id, observer.id, inject),
    ) as client:
        # Acquire the driver only; do not warm this client's container metadata.
        handle = client._adapter._ensure_driver_handle()
        container = client.get_database_client(database_id).get_container_client(
            observer.id
        )
        assert client._adapter._debug_fault_injection_rule_hit_count(metadata_id) == 0
        assert client._adapter._debug_fault_injection_rule_hit_count(guard_id) == 0
        calls, hooks = capture_query_calls(monkeypatch), []
        pages = container.query_items(
            QUERY,
            partition_key=partition,
            max_item_count=1,
            timeout=PAGE_BUDGET,
            response_hook=lambda headers, body: hooks.append(dict(headers)),
        ).by_page()
        assert not calls and pages.state.cursor is None
        before = (_binding_operation_count(), _rust_fallback_count())
        error, first = None, None
        start = time.perf_counter()
        try:
            try:
                first = list(next(pages))
            except (AzureError, TimeoutError) as caught:
                error = caught
        finally:
            set_rule(handle, metadata_id, False)
            set_rule(handle, guard_id, False)
        elapsed = time.perf_counter() - start
        after = (_binding_operation_count(), _rust_fallback_count())
        metadata_hits = client._adapter._debug_fault_injection_rule_hit_count(
            metadata_id
        )
        guard_hits = client._adapter._debug_fault_injection_rule_hit_count(guard_id)
        emit(
            "query_setup",
            surface="sync",
            database_id=database_id,
            inject=inject,
            error_type=None if error is None else type(error).__name__,
            status=None if error is None else getattr(error, "status_code", None),
            sub_status=None if error is None else getattr(error, "sub_status", None),
            metadata_hits=metadata_hits,
            guard_hits=guard_hits,
            hook_count=len(hooks),
            iterator_failed=pages.state.failed,
            can_retry_setup=(
                None
                if pages.state.cursor is None
                else pages.state.cursor.can_retry_setup
            ),
            continuation_present=pages.continuation_token is not None,
            elapsed=elapsed,
            binding_delta=after[0] - before[0],
            fallback_delta=after[1] - before[1],
        )
        assert_route(before, after, "rust")
        assert len(calls) == 1
        cursor = calls[0][1]
        if inject:
            assert first is None
            assert_setup_failure(
                error, pages, cursor, hooks, metadata_hits, guard_hits, elapsed
            )
            first = list(next(pages))
            recovered = (_binding_operation_count(), _rust_fallback_count())
            assert_route(after, recovered, "rust")
            assert len(calls) == 2 and calls[-1][1] is cursor
        else:
            assert error is None and metadata_hits == guard_hits == 0
        assert len(first) == 1 and first[0]["id"] == items[0]["id"]
        assert len(hooks) == 1 and pages.state.cursor is cursor
        assert not pages.state.failed and not cursor.can_retry_setup
        remainder = [row for page in pages for row in page]
        assert_complete(first, remainder, items)
        assert pages.state.cursor is None
        assert all(call[1] is cursor for call in calls)
        completed = (_binding_operation_count(), _rust_fallback_count())
        assert completed[0] - before[0] == len(calls) and completed[1] == before[1]
        assert (
            client._adapter._debug_fault_injection_rule_hit_count(metadata_id)
            == metadata_hits
        )
        assert client._adapter._debug_fault_injection_rule_hit_count(guard_id) == 0
        emit(
            "query_setup_recovered",
            surface="sync",
            database_id=database_id,
            inject=inject,
            same_cursor=True,
            returned_ids=[row["id"] for row in first + remainder],
            expected_ids=[item["id"] for item in items],
            binding_delta=completed[0] - before[0],
            native_calls=len(calls),
            fallback_delta=completed[1] - before[1],
        )
        # A warmed, separate iterator proves the guard really matches QueryItem.
        set_rule(handle, guard_id, True)
        guard_error = None
        guard_pages = container.query_items(
            QUERY,
            partition_key=partition,
            max_item_count=1,
            timeout=PAGE_BUDGET,
        ).by_page()
        try:
            try:
                list(next(guard_pages))
            except (AzureError, TimeoutError) as caught:
                guard_error = caught
        finally:
            set_rule(handle, guard_id, False)
        guard_hits = client._adapter._debug_fault_injection_rule_hit_count(guard_id)
        assert_guard_failure(guard_error, guard_hits)
        guard_after = (_binding_operation_count(), _rust_fallback_count())
        assert_route(completed, guard_after, "rust")
        assert (
            client._adapter._debug_fault_injection_rule_hit_count(metadata_id)
            == metadata_hits
        )
        assert guard_pages.state.failed and guard_pages.state.cursor is None
        emit(
            "query_setup_guard",
            surface="sync",
            database_id=database_id,
            hits=guard_hits,
            status=guard_error.status_code,
            sub_status=guard_error.sub_status,
            binding_delta=guard_after[0] - completed[0],
            fallback_delta=guard_after[1] - completed[1],
        )
        for item in items:
            stored = observer.read_item(item["id"], partition_key=partition)
            assert {field: stored[field] for field in item} == item
        emit(
            "query_setup_stored_state",
            surface="sync",
            database_id=database_id,
            fields=items,
        )
