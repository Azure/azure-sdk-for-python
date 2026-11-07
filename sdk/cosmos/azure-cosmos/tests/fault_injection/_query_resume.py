# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Fault a retained query after delivery, then resume using its public bookmark.

Extends the query contract's mocked last-delivered-bookmark cases with an
installed-emulator QueryItem response. Rules start disabled and are armed only
between public fetches; no transport mock, timer race, or decoded/rewritten token.
Coverage is single-partition ordered SQL with unchanged data, not snapshot
isolation under concurrent writes or cross-backend token compatibility.
"""

import math

from azure.cosmos import exceptions

QUERY = "SELECT * FROM c ORDER BY c.id"
PAGE_BUDGET = 30
FAULT_STATUS = 429
FAULT_SUBSTATUS = 32001


def resume_rule(rule_id, container_id, inject):
    return {
        "id": rule_id,
        "operation_type": "QueryItem",
        "container_id": container_id,
        "status_code": FAULT_STATUS,
        "sub_status": FAULT_SUBSTATUS,
        "probability": 1.0 if inject else 0.0,
        "enabled": False,
        "hit_limit": None,
    }


def capture_query_calls(monkeypatch, *, asynchronous=False):
    """Retain cursor identity for assertions while forwarding every real call."""
    from azure.cosmos import _rust

    name = "fetch_page_with_cursor_async" if asynchronous else "fetch_page_with_cursor"
    original = getattr(_rust, name)
    calls = []

    def observed(handle, prepared, cursor, **kwargs):
        assert prepared.op == "query_items"
        assert isinstance(cursor, _rust._ItemFeedCursor)
        budget = kwargs.get("timeout_seconds")
        assert (
            budget is not None and math.isfinite(budget) and 0 < budget <= PAGE_BUDGET
        )
        calls.append((handle, cursor))
        return original(handle, prepared, cursor, **kwargs)

    monkeypatch.setattr(_rust, name, observed)
    return calls


def assert_failure(error, bookmark, hits, elapsed):
    assert isinstance(
        error, exceptions.CosmosHttpResponseError
    ), "Expected the injected HTTP error"
    assert error.status_code == FAULT_STATUS
    assert error.headers.get("x-ms-substatus") == str(FAULT_SUBSTATUS)
    assert hits == 1, "Expected one faulted attempt with throttle retries disabled"
    assert math.isfinite(elapsed) and 0 <= elapsed < PAGE_BUDGET
    assert isinstance(bookmark, str) and bookmark
    assert (
        error.continuation_token == bookmark
    ), "Error advanced or lost the delivered public bookmark"


def assert_complete(first, remainder, expected):
    """Ordered equality catches gaps, duplicates, replay and changed fields."""
    rows = first + remainder
    fields = tuple(expected[0])
    assert [{field: row[field] for field in fields} for row in rows] == expected


def set_rule(handle, rule_id, enabled):
    from azure.cosmos import _rust

    toggle = getattr(_rust, "_debug_set_fault_injection_rule_enabled", None)
    if toggle is None:
        raise RuntimeError(
            "Rebuild the binding with the internal fault-rule toggle before running query resume tests"
        )
    toggle(handle, rule_id, enabled)
