# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import pytest

from azure.core.exceptions import ServiceResponseError
from azure.cosmos import exceptions
from azure.cosmos._backend.client_config import _prepare_fault_injection_rules
from fault_injection._throttle_retry import (
    OPERATION_TIMEOUT, assert_throttle_failure, assert_throttle_wait_failure, throttle_rule,
)


@pytest.mark.parametrize("inject", [True, False])
def test_throttle_rule_preserves_scope_and_persistent_failure_rust(inject):
    prepared, = _prepare_fault_injection_rules([throttle_rule("rule", "owned-container", inject)])
    assert prepared.id == "rule"
    assert prepared.container_id == "owned-container"
    assert prepared.operation_type == "ReadItem"
    assert prepared.status_code == 429
    assert prepared.error_type is None
    assert prepared.delay_ms == 0
    assert prepared.probability == (1.0 if inject else 0.0)
    assert prepared.hit_limit is None
    assert prepared.enabled is True


@pytest.mark.parametrize("error", [
    None, exceptions.CosmosClientTimeoutError(), TimeoutError("raw or outer deadline"),
    exceptions.CosmosHttpResponseError(408), exceptions.CosmosHttpResponseError(503),
    ServiceResponseError("response failure"),
])
def test_throttle_failure_rejects_success_deadline_transport_and_wrong_http_status_rust(error):
    with pytest.raises(AssertionError):
        assert_throttle_failure(error, 1.0, 6, 5)


@pytest.mark.parametrize("retry_limit,hits", [(0, 1), (2, 3), (3, 4), (5, 6)])
def test_throttle_count_includes_initial_attempt_rust(retry_limit, hits):
    assert_throttle_failure(exceptions.CosmosHttpResponseError(429), 1.0, hits, retry_limit)


@pytest.mark.parametrize("retry_limit,hits", [
    (0, 0), (0, 2), (0, 6), (0, 10), (2, 1), (2, 2), (2, 4), (2, 6),
    (5, 0), (5, 1), (5, 5), (5, 7), (5, 10),
])
def test_throttle_failure_rejects_missing_extra_and_off_by_one_attempts_rust(retry_limit, hits):
    with pytest.raises(AssertionError, match="exactly the configured"):
        assert_throttle_failure(exceptions.CosmosHttpResponseError(429), 1.0, hits, retry_limit)


@pytest.mark.parametrize("elapsed", [-1, OPERATION_TIMEOUT, OPERATION_TIMEOUT + 1, float("nan"), float("inf")])
def test_throttle_failure_rejects_operation_expiry_or_invalid_elapsed_rust(elapsed):
    with pytest.raises(AssertionError, match="before the operation budget"):
        assert_throttle_failure(exceptions.CosmosHttpResponseError(429), elapsed, 6, 5)


@pytest.mark.parametrize("inject", [True, False])
def test_wait_rule_uses_response_header_not_injected_delay_rust(inject):
    prepared, = _prepare_fault_injection_rules([throttle_rule("rule", "owned", inject, wait_budget=True)])
    assert dict(prepared.response_headers) == {"x-ms-retry-after-ms": "1000"}
    assert prepared.delay_ms == 0
    assert prepared.hit_limit is None
    assert prepared.probability == (1.0 if inject else 0.0)


@pytest.mark.parametrize("retries,elapsed", [(3, 16.02), (5, 5.02)])
def test_throttle_wait_accepts_driver_final_retry_and_count_limited_wait_rust(retries, elapsed):
    assert_throttle_wait_failure(
        exceptions.CosmosHttpResponseError(429), elapsed, retries + 1, retries, max_retries=5,
    )


@pytest.mark.parametrize("retries,elapsed,hits", [
    (3, 0.002, 4), (3, 2.0, 3), (3, 2.5, 4), (3, 3.02, 4), (3, 4.0, 5),
    (3, 16.02, 3), (3, 16.02, 5), (3, 15.8, 4), (3, 16.4, 4), (3, 29.0, 4),
    (3, OPERATION_TIMEOUT, 4), (3, float("nan"), 4), (3, float("inf"), 4),
    (5, 0.005, 6), (5, 2.0, 3), (5, 4.8, 6), (5, 5.4, 6), (5, 10.0, 6),
    (5, 16.02, 6), (5, float("nan"), 6),
])
def test_throttle_wait_rejects_wrong_count_legacy_timing_and_incorrect_driver_wait_rust(retries, elapsed, hits):
    with pytest.raises(AssertionError):
        assert_throttle_wait_failure(
            exceptions.CosmosHttpResponseError(429), elapsed, hits, retries, max_retries=5,
        )


@pytest.mark.parametrize("error", [
    None, exceptions.CosmosClientTimeoutError(), exceptions.CosmosHttpResponseError(408),
    exceptions.CosmosHttpResponseError(503), ServiceResponseError("response failure"),
])
def test_driver_final_wait_still_requires_terminal_throttling_rust(error):
    with pytest.raises(AssertionError):
        assert_throttle_wait_failure(error, 16.02, 4, 3, max_retries=5)


def test_final_wait_uses_operation_budget_not_fixed_sixteen_seconds_rust(monkeypatch):
    from fault_injection import _throttle_retry

    monkeypatch.setattr(_throttle_retry, "OPERATION_TIMEOUT", 10.0)
    assert_throttle_wait_failure(exceptions.CosmosHttpResponseError(429), 6.02, 4, 3, max_retries=5)
    with pytest.raises(AssertionError):
        assert_throttle_wait_failure(exceptions.CosmosHttpResponseError(429), 3.02, 4, 3, max_retries=5)


def test_unmodified_legacy_policy_retains_three_waits_as_characterization_rust():
    from azure.cosmos._resource_throttle_retry_policy import ResourceThrottleRetryPolicy

    policy = ResourceThrottleRetryPolicy(5, 0, 2.5)
    error = exceptions.CosmosHttpResponseError(status_code=429)
    # CosmosHttpResponseError normally receives headers from a response.
    error.headers = {"x-ms-retry-after-ms": "1000"}
    assert [policy.ShouldRetry(error) for _ in range(4)] == [True, True, True, False]
    assert policy.cumulative_wait_time_in_milliseconds == 3000
