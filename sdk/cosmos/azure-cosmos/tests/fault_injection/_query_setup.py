# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Cold query setup recovery through the compiled binding and installed emulator.

Complements the mocked initial-setup recovery contract with a metadata fault.
An active QueryItem guard must stay untouched until setup succeeds; its later
positive control proves that zero hits did not come from an unmatched guard.
This is not metadata-region routing, split recovery, or automatic retry coverage.
"""

import math

from azure.cosmos import exceptions
from fault_injection._query_resume import PAGE_BUDGET

SETUP_SUBSTATUS = 32002
GUARD_SUBSTATUS = 32003


def setup_rules(metadata_id, guard_id, container_id, inject):
    common = {
        "container_id": container_id,
        "status_code": 429,
        "hit_limit": None,
    }
    return [
        {
            **common,
            "id": metadata_id,
            "operation_type": "MetadataReadContainer",
            "sub_status": SETUP_SUBSTATUS,
            "enabled": True,
            "probability": 1.0 if inject else 0.0,
        },
        {
            **common,
            "id": guard_id,
            "operation_type": "QueryItem",
            "sub_status": GUARD_SUBSTATUS,
            "enabled": inject,
            "probability": 1.0,
        },
    ]


def assert_setup_failure(
    error, pages, cursor, hooks, metadata_hits, guard_hits, elapsed
):
    assert isinstance(
        error, exceptions.CosmosHttpResponseError
    ), "Expected metadata HTTP error"
    assert error.status_code == 429 and error.sub_status == SETUP_SUBSTATUS
    assert error.headers.get("x-ms-substatus") == str(SETUP_SUBSTATUS)
    assert (
        metadata_hits == 1
    ), "Expected one metadata fault with throttle retries disabled"
    assert guard_hits == 0, "Query execution occurred before setup completed"
    assert math.isfinite(elapsed) and 0 <= elapsed < PAGE_BUDGET
    assert (
        not hooks
        and pages.continuation_token is None
        and error.continuation_token is None
    )
    assert pages.state.cursor is cursor and not pages.state.failed
    assert (
        cursor.can_retry_setup
    ), "Native execution started or the cursor was invalidated"


def assert_guard_failure(error, hits):
    assert isinstance(
        error, exceptions.CosmosHttpResponseError
    ), "Query guard did not intercept execution"
    assert error.status_code == 429 and error.sub_status == GUARD_SUBSTATUS
    assert hits == 1, "Query guard must demonstrably match the recovered container"
