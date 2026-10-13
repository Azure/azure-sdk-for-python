# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import asyncio

import pytest

from azure.cosmos import exceptions
from azure.cosmos._backend.client_config import _prepare_fault_injection_rules
from fault_injection._async_cancellation import assert_cancelled, cancellation_rule


@pytest.mark.parametrize("inject", [True, False])
def test_cancellation_rule_is_scoped_delayed_and_consumed_once(inject):
    rule, = _prepare_fault_injection_rules([cancellation_rule("cancel", "owned", inject)])
    assert rule.id == "cancel" and rule.container_id == "owned"
    assert rule.operation_type == "ReadItem" and rule.status_code == 503
    assert rule.delay_ms == 5000 and rule.hit_limit == 1
    assert rule.probability == (1.0 if inject else 0.0)


@pytest.mark.parametrize("status", ["created", "scheduled", "running", "completed"])
def test_python_cancellation_alone_is_not_native_cessation(status):
    with pytest.raises(AssertionError, match="native operation"):
        assert_cancelled(asyncio.CancelledError(), status, 0.02)


@pytest.mark.parametrize("error", [None, TimeoutError(), exceptions.CosmosClientTimeoutError(),
                                  exceptions.CosmosHttpResponseError(503)])
def test_cancellation_rejects_wrong_outcome(error):
    with pytest.raises(AssertionError, match="CancelledError"):
        assert_cancelled(error, "dropped", 0.02)


@pytest.mark.parametrize("elapsed", [-1, 1, 5, float("inf"), float("nan")])
def test_cancellation_rejects_late_or_invalid_completion(elapsed):
    with pytest.raises(AssertionError, match="prompt"):
        assert_cancelled(asyncio.CancelledError(), "dropped", elapsed)


def test_cancellation_accepts_dropped_native_future():
    assert_cancelled(asyncio.CancelledError(), "dropped", 0.02)
