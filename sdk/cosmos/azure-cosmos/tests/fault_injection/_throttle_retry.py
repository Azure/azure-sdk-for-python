# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""F07: Public throttle limits control a persistently throttled Rust-backed order read.

Select retry_throttle_total, its precedence over retry_total, and the cumulative
waiting budget with a fixed Retry-After header from the paired retry_policy
tests. Waiting follows the driver's accepted forced-final retry behavior.
This does not claim wait-option precedence, connection retry, or query coverage.
"""
import math

import pytest

from azure.cosmos.exceptions import CosmosHttpResponseError

OPERATION_TIMEOUT = 30.0  # Also determines the driver's forced-final retry delay.

THROTTLE_RETRY_CASES = [
    pytest.param({"retry_throttle_total": 0}, 0, id="zero-retries"),
    pytest.param({"retry_throttle_total": 5}, 5, id="five-retries"),
    # Expected retries are fixed independently of the SDK's configuration resolver.
    pytest.param({"retry_total": 5}, 5, id="alias-only"),
    pytest.param({"retry_total": 5, "retry_throttle_total": 2}, 2, id="specific-over-alias"),
    pytest.param({"retry_total": 5, "retry_throttle_total": 0}, 0, id="zero-over-alias"),
    pytest.param({"retry_total": 5, "retry_throttle_total": None}, 5, id="none-uses-alias"),
    pytest.param(
        {"retry_throttle_total": 5, "throttle_retry_wait_threshold_seconds": 2.5}, 3, id="wait-budget-limits-retries",
    ),
    pytest.param(
        {"retry_throttle_total": 5, "throttle_retry_wait_threshold_seconds": 10.0}, 5, id="wait-budget-allows-retries",
    ),
]


def throttle_rule(rule_id, container_id, inject, *, wait_budget=False):
    rule = {
        "id": rule_id,  # Identify the rule whose applications we count.
        "operation_type": "ReadItem",  # Do not throttle setup or metadata requests.
        "container_id": container_id,  # Match only the unique test-owned container.
        "status_code": 429,  # Synthetic HTTP throttling response, not a transport exception.
        "delay_ms": 0,  # Add no artificial delay before returning the response.
        "probability": 1.0 if inject else 0.0,  # The fresh-client control never injects.
        "hit_limit": None,  # Retry recovery must not occur by exhausting the rule.
    }
    if wait_budget:
        # Ask the retry policy to wait; do not delay the synthetic response.
        rule["response_headers"] = {"x-ms-retry-after-ms": "1000"}
    return rule


def assert_throttle_failure(error, elapsed, hits, retry_limit):
    assert isinstance(error, CosmosHttpResponseError), "Expected CosmosHttpResponseError, not success or another error"
    assert error.status_code == 429, "Expected the terminal throttling response"
    assert hits == retry_limit + 1, "Expected the initial attempt plus exactly the configured throttle retries"
    assert (
        math.isfinite(elapsed) and 0 <= elapsed < OPERATION_TIMEOUT
    ), "Throttle retries must exhaust before the operation budget expires"


def assert_throttle_wait_failure(error, elapsed, hits, expected_retries, *, max_retries):
    assert_throttle_failure(error, elapsed, hits, expected_retries)
    expected_wait = float(expected_retries)
    if expected_retries < max_retries:
        # The wait budget stops ordinary one-second retries before the count cap.
        # The last retry instead waits for half the remaining operation budget.
        ordinary_wait = float(expected_retries - 1)
        expected_wait = ordinary_wait + (OPERATION_TIMEOUT - ordinary_wait) / 2
    assert expected_wait - 0.1 <= elapsed < expected_wait + 0.4, (
        f"Expected driver throttle waiting near {expected_wait:.1f}s with bounded scheduling overhead; "
        f"observed {elapsed:.3f}s, {hits} attempts, maximum {max_retries} retries"
    )
