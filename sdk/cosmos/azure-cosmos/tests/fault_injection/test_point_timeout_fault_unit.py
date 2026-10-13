# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import pytest

from azure.core.exceptions import ServiceResponseError
from azure.cosmos import exceptions
from azure.cosmos._backend.client_config import _prepare_fault_injection_rules
from fault_injection._point_timeout import (
    DELAY_MS, MAX_OPERATION_ELAPSED, MIN_TIMEOUT_ELAPSED, OPERATION_TIMEOUT,
    assert_point_timeout, assert_read_budget, assert_read_elapsed, read_timeout_rule,
)


@pytest.mark.parametrize("inject", [True, False])
def test_point_timeout_rule_preserves_scope_delay_and_control(inject):
    prepared, = _prepare_fault_injection_rules([read_timeout_rule("rule", "owned-container", inject)])
    assert prepared.id == "rule"
    assert prepared.container_id == "owned-container"
    assert prepared.operation_type == "ReadItem"
    assert prepared.status_code == 503
    assert prepared.error_type is None
    assert prepared.delay_ms == DELAY_MS == 5000
    assert prepared.probability == (1.0 if inject else 0.0)
    assert prepared.hit_limit is None
    assert prepared.enabled is True
    assert 0 < MIN_TIMEOUT_ELAPSED <= OPERATION_TIMEOUT < MAX_OPERATION_ELAPSED < DELAY_MS / 1000


@pytest.mark.parametrize("error", [
    None, TimeoutError("raw binding or outer timeout"), exceptions.CosmosHttpResponseError(503),
    exceptions.CosmosHttpResponseError(408), ServiceResponseError("408/20008 ClientOperationTimeout"),
    RuntimeError("unexpected error"),
])
def test_point_timeout_rejects_success_and_wrong_exception(error):
    with pytest.raises(AssertionError, match="Expected CosmosClientTimeoutError"):
        assert_point_timeout(error, 1.0, 1)


@pytest.mark.parametrize("elapsed", [0, 0.89, 2.01, 5, float("nan"), float("inf"), -1])
def test_point_timeout_rejects_early_late_and_invalid_elapsed(elapsed):
    with pytest.raises(AssertionError, match="scheduling allowance"):
        assert_point_timeout(exceptions.CosmosClientTimeoutError(), elapsed, 1)


@pytest.mark.parametrize("hits", [0, -1])
def test_point_timeout_requires_applied_fault(hits):
    with pytest.raises(AssertionError, match="did not apply"):
        assert_point_timeout(exceptions.CosmosClientTimeoutError(), 1.0, hits)


@pytest.mark.parametrize("elapsed", [MIN_TIMEOUT_ELAPSED, OPERATION_TIMEOUT, MAX_OPERATION_ELAPSED])
def test_point_timeout_accepts_bounded_expiry(elapsed):
    assert_point_timeout(exceptions.CosmosClientTimeoutError(), elapsed, 1)


@pytest.mark.parametrize("budgets", [[], [None], [0], [-1], [1.01], [float("nan")], [float("inf")], [0.5, 0.5]])
def test_point_timeout_requires_one_remaining_native_budget(budgets):
    with pytest.raises(AssertionError):
        assert_read_budget(budgets)


@pytest.mark.parametrize("budget", [0.001, 0.9, OPERATION_TIMEOUT])
def test_point_timeout_accepts_remaining_native_budget(budget):
    assert_read_budget([budget])


@pytest.mark.parametrize("elapsed", [-1, 2.01, 5, float("nan"), float("inf")])
def test_control_rejects_unbounded_or_invalid_elapsed(elapsed):
    with pytest.raises(AssertionError, match="control read"):
        assert_read_elapsed(elapsed)


@pytest.mark.parametrize("elapsed", [0, 0.1, MAX_OPERATION_ELAPSED])
def test_control_accepts_bounded_elapsed(elapsed):
    assert_read_elapsed(elapsed)
