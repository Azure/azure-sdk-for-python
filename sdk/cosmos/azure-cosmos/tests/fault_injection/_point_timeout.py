# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""F12: an overall point-read budget expires while a Rust fault is delayed.

Use the installed/pipeline emulator, not the Rust in-memory emulator. This
selects the public timeout contract from test_crud.test_timeout_for_point_operation;
it does not simulate an interruptible network wait with a Python transport sleep.
"""
import math

from azure.cosmos.exceptions import CosmosClientTimeoutError

OPERATION_TIMEOUT = 1.0
DELAY_MS = 5000
MIN_TIMEOUT_ELAPSED = 0.9  # Allow 100 ms of clock/timer precision, not immediate failure.
MAX_OPERATION_ELAPSED = 2.0  # One second of scheduling allowance, still below the fault delay.


def read_operation_timeout_rule(rule_id, container_id, inject):
    return {
        "id": rule_id,  # Identify the rule whose applications we count.
        "operation_type": "ReadItem",  # Do not delay setup or metadata resolution.
        "container_id": container_id,  # Match only the unique test-owned container.
        "status_code": 503,  # This response must not arrive before the operation expires.
        "delay_ms": DELAY_MS,  # Keep the attempt waiting beyond the one-second budget.
        "probability": 1.0 if inject else 0.0,  # The fresh-client control never injects.
        "hit_limit": None,  # A retry cannot escape by exhausting the rule.
    }


def database_read_operation_timeout_rule(rule_id, inject):
    """Activate only around one database read on an initialized, dedicated client."""
    rule = read_operation_timeout_rule(rule_id, None, inject)
    rule.update(operation_type="All", enabled=False)
    return rule


def capture_read_budget(monkeypatch, *, asynchronous=False, operation="read_item"):
    """Observe the real binding call without replacing its execution or timer."""
    from azure.cosmos import _rust

    name = operation + "_async" if asynchronous else operation
    original = getattr(_rust, name)
    budgets = []

    def observed(*args, **kwargs):
        budgets.append(kwargs.get("timeout_seconds"))
        return original(*args, **kwargs)

    monkeypatch.setattr(_rust, name, observed)
    return budgets


def assert_read_budget(budgets):
    assert len(budgets) == 1, "Expected one native read call"
    budget = budgets[0]
    assert (
        budget is not None and math.isfinite(budget) and 0 < budget <= OPERATION_TIMEOUT
    ), "Python did not forward the remaining operation budget"


def assert_point_timeout(error, elapsed, hits):
    assert isinstance(
        error, CosmosClientTimeoutError
    ), "Expected CosmosClientTimeoutError, not success or another error"
    assert hits > 0, "The intended read fault did not apply"
    assert (
        math.isfinite(elapsed)
        and MIN_TIMEOUT_ELAPSED <= elapsed <= MAX_OPERATION_ELAPSED
    ), "The read did not stop within the operation budget's scheduling allowance"


def assert_read_elapsed(elapsed):
    assert math.isfinite(elapsed) and 0 <= elapsed <= MAX_OPERATION_ELAPSED, "The control read exceeded its budget allowance"
