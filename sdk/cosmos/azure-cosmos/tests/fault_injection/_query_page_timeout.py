# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Real retained-page timeout, selected from test_crud's paged timeout contract.

The sync/async legacy tests use a Python transport delay. Here the installed
emulator and a Rust QueryItem fault exercise the compiled page boundary instead.
This covers the first fetch and fresh per-page budgets, not failure/resume after
an already delivered page, or multi-partition query execution.
"""
import math

from azure.cosmos.exceptions import CosmosClientTimeoutError
from fault_injection._point_timeout import (
    DELAY_MS, MAX_OPERATION_ELAPSED, MIN_TIMEOUT_ELAPSED, OPERATION_TIMEOUT,
    read_operation_timeout_rule,
)

PAGE_TIMEOUT = OPERATION_TIMEOUT
BETWEEN_PAGES_DELAY = PAGE_TIMEOUT + 0.1


def query_timeout_rule(rule_id, container_id, inject):
    return {**read_operation_timeout_rule(rule_id, container_id, inject), "operation_type": "QueryItem"}


def capture_page_calls(monkeypatch, *, asynchronous=False):
    """Observe the real entry point without substituting a page or a timer."""
    from azure.cosmos import _rust

    name = "fetch_page_with_cursor_async" if asynchronous else "fetch_page_with_cursor"
    original = getattr(_rust, name)
    calls = []

    def observed(*args, **kwargs):
        calls.append({
            "op": args[1].op,
            "timeout_seconds": kwargs.get("timeout_seconds"),
            "cursor_id": id(args[2]),
            "native_cursor": isinstance(args[2], _rust._ItemFeedCursor),
        })
        return original(*args, **kwargs)

    monkeypatch.setattr(_rust, name, observed)
    return calls


def assert_page_call(calls):
    assert len(calls) == 1, "Expected one retained native page fetch"
    call, = calls
    assert call["op"] == "query_items" and call["native_cursor"], "Expected the real query cursor path"
    budget = call["timeout_seconds"]
    assert (
        budget is not None and math.isfinite(budget) and 0 < budget <= PAGE_TIMEOUT
    ), "Python did not forward the remaining page budget"


def assert_page_timeout(error, elapsed, hits):
    assert isinstance(error, CosmosClientTimeoutError), "Expected CosmosClientTimeoutError"
    assert hits > 0, "The intended QueryItem fault did not apply"
    assert (
        math.isfinite(elapsed) and MIN_TIMEOUT_ELAPSED <= elapsed <= MAX_OPERATION_ELAPSED
    ), "The page did not stop within the page budget's scheduling allowance"


def assert_control_page(rows, items, elapsed, hits):
    assert hits == 0, "The no-injection query applied a fault"
    assert math.isfinite(elapsed) and 0 <= elapsed <= MAX_OPERATION_ELAPSED
    assert len(rows) == 1, "Expected one order per page"
    expected = {item["id"]: item for item in items}
    assert rows[0]["id"] in expected
    item = expected[rows[0]["id"]]
    assert {field: rows[0][field] for field in item} == item
