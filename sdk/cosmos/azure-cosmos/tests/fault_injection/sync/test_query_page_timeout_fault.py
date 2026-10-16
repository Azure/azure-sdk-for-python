# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Public sync query-page timeout against the installed/pipeline emulator."""
import os
import time
import uuid

import pytest

from azure.core.exceptions import ServiceResponseError
from azure.cosmos import CosmosClient, exceptions
from common._parity_helpers import _binding_operation_count, _rust_fallback_count
from fault_injection._delayed_create import assert_route, emit
from fault_injection._query_page_timeout import (
    BETWEEN_PAGES_DELAY, PAGE_TIMEOUT, assert_control_page, assert_page_call,
    assert_page_timeout, capture_page_calls, query_timeout_rule,
)

pytestmark = pytest.mark.cosmosEmulator


@pytest.mark.timeout(90)
@pytest.mark.parametrize("inject", [True, False], ids=["delayed-page", "no-injection"])
def test_query_page_timeout(owned_target, monkeypatch, inject):
    database_id, observer = owned_target
    partition = uuid.uuid4().hex
    items = [
        {"id": partition + "-" + str(index), "pk": partition, "name": "order-" + str(index), "state": "confirmed"}
        for index in range(2)
    ]
    for item in items:
        observer.create_item(item)
    rule_id = "query-timeout-" + uuid.uuid4().hex
    with CosmosClient(
        os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"],
        _backend="rust", consistency_level="Session",
        _fault_injection_rules=[query_timeout_rule(rule_id, observer.id, inject)],
    ) as client:
        container = client.get_database_client(database_id).get_container_client(observer.id)
        container.read(timeout=30)
        client._adapter.get_container_metadata(container.container_link, deadline=time.monotonic() + 30)
        assert client._adapter._debug_fault_injection_rule_hit_count(rule_id) == 0
        calls = capture_page_calls(monkeypatch)
        hooks = []
        before = (_binding_operation_count(), _rust_fallback_count())
        pages = container.query_items(
            "SELECT * FROM c", partition_key=partition, max_item_count=1, timeout=PAGE_TIMEOUT,
            response_hook=lambda headers, body: hooks.append(dict(headers)),
        ).by_page()
        assert not calls and pages.state.cursor is None
        assert (_binding_operation_count(), _rust_fallback_count()) == before
        error, rows = None, None
        start = time.perf_counter()
        try:
            rows = list(next(pages))
        except (exceptions.CosmosClientTimeoutError, exceptions.CosmosHttpResponseError,
                ServiceResponseError, TimeoutError) as caught:
            error = caught
        elapsed = time.perf_counter() - start
        after = (_binding_operation_count(), _rust_fallback_count())
        hits = client._adapter._debug_fault_injection_rule_hit_count(rule_id)
        emit("query_page_timeout", surface="sync", database_id=database_id, inject=inject,
             rule_id=rule_id, elapsed=elapsed, hits=hits, native_calls=list(calls),
             error_type=None if error is None else type(error).__name__,
             error_message=None if error is None else str(error),
             delivered_count=0 if rows is None else len(rows), hook_count=len(hooks),
             cursor_released=pages.state.cursor is None,
             binding_delta=after[0] - before[0], fallback_delta=after[1] - before[1])
        assert_route(before, after, "rust")
        assert_page_call(calls)
        if inject:
            assert_page_timeout(error, elapsed, hits)
            assert rows is None and not hooks
            assert pages.state.failed and pages.state.cursor is None
            assert pages.continuation_token is None and error.continuation_token is None
            with pytest.raises(RuntimeError, match="Query pager failed"):
                next(pages)
            assert len(calls) == 1
            assert (_binding_operation_count(), _rust_fallback_count()) == after
            assert client._adapter._debug_fault_injection_rule_hit_count(rule_id) == hits
            emit("failed_query_reuse", surface="sync", database_id=database_id,
                 error_type="RuntimeError", additional_binding_calls=0, cursor_released=True)
        else:
            assert error is None
            assert_control_page(rows, items, elapsed, hits)
            assert len(hooks) == 1 and pages.state.cursor is not None
            time.sleep(BETWEEN_PAGES_DELAY)
            second_start = time.perf_counter()
            assert second_start - (start + elapsed) > PAGE_TIMEOUT
            second = list(next(pages))
            second_elapsed = time.perf_counter() - second_start
            second_after = (_binding_operation_count(), _rust_fallback_count())
            assert_route(after, second_after, "rust")
            assert len(calls) == 2
            assert_page_call(calls[1:])
            assert calls[0]["cursor_id"] == calls[1]["cursor_id"]
            assert_control_page(second, items, second_elapsed,
                                client._adapter._debug_fault_injection_rule_hit_count(rule_id))
            assert {row["id"] for row in rows + second} == {item["id"] for item in items}
            assert len(hooks) == 2
            with pytest.raises(StopIteration):
                next(pages)
            assert pages.state.cursor is None
            completion_after = (_binding_operation_count(), _rust_fallback_count())
            assert completion_after[0] - second_after[0] == len(calls) - 2
            assert completion_after[1] == second_after[1]
            for call in calls[2:]:
                assert_page_call([call])
                assert call["cursor_id"] == calls[0]["cursor_id"]
            emit("query_page_budget_reset", surface="sync", database_id=database_id,
                 pause_seconds=second_start - (start + elapsed), elapsed=second_elapsed,
                 native_calls=list(calls[:2]), completion_native_calls=list(calls[2:]),
                 completion_binding_delta=completion_after[0] - second_after[0],
                 delivered_ids=[row["id"] for row in rows + second],
                 cursor_released=True, binding_delta=second_after[0] - after[0],
                 fallback_delta=second_after[1] - after[1])
        for item in items:
            stored = observer.read_item(item["id"], partition_key=partition)
            assert {field: stored[field] for field in item} == item
            emit("stored_state", surface="sync", database_id=database_id, inject=inject,
                 item_id=item["id"], fields={field: stored[field] for field in item})
