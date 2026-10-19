# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from types import SimpleNamespace

import pytest

from azure.cosmos import exceptions
from azure.cosmos._backend.client_config import _prepare_fault_injection_rules
from fault_injection._query_resume import (
    FAULT_STATUS,
    FAULT_SUBSTATUS,
    assert_complete,
    assert_failure,
    resume_rule,
)


@pytest.mark.parametrize("inject", [True, False])
def test_resume_rule_is_disabled_until_after_delivery(inject):
    (rule,) = _prepare_fault_injection_rules([resume_rule("unique", "owned", inject)])
    assert rule.operation_type == "QueryItem" and rule.container_id == "owned"
    assert rule.enabled is False and rule.hit_limit is None
    assert rule.probability == (1.0 if inject else 0.0)
    assert rule.status_code == FAULT_STATUS and rule.sub_status == FAULT_SUBSTATUS
    assert rule.delay_ms == 0


def failure(token="service-saved", status=FAULT_STATUS, substatus=FAULT_SUBSTATUS):
    error = exceptions.CosmosHttpResponseError(
        response=SimpleNamespace(
            status_code=status,
            headers={"x-ms-substatus": str(substatus)},
            reason="injected",
        ),
        message="injected",
    )
    error.continuation_token = token
    return error


@pytest.mark.parametrize(
    "error,hits,elapsed",
    [
        (None, 1, 0.1),
        (TimeoutError(), 1, 0.1),
        (failure(token="service-advanced"), 1, 0.1),
        (failure(status=503), 1, 0.1),
        (failure(substatus=0), 1, 0.1),
        (failure(), 0, 0.1),
        (failure(), 2, 0.1),
        (failure(), 1, 30),
        (failure(), 1, float("nan")),
    ],
)
def test_resume_failure_rejects_wrong_error_progress_or_fault_count(
    error, hits, elapsed
):
    with pytest.raises(AssertionError):
        assert_failure(error, "service-saved", hits, elapsed)


def test_resume_failure_accepts_exact_public_bookmark():
    assert_failure(failure(), "service-saved", 1, 0.1)


@pytest.mark.parametrize("ids", [[0, 1, 2], [1], [2], [1, 1, 2], [2, 1]])
def test_resume_result_rejects_replay_gaps_duplicates_or_reordering(ids):
    expected = [{"id": i, "state": "confirmed"} for i in range(3)]
    with pytest.raises(AssertionError):
        assert_complete(expected[:1], [expected[i] for i in ids], expected)


def test_resume_result_accepts_exact_rows_and_rejects_changed_fields():
    expected = [{"id": i, "state": "confirmed"} for i in range(3)]
    assert_complete(expected[:1], expected[1:], expected)
    with pytest.raises(AssertionError):
        assert_complete(
            expected[:1], [dict(expected[1], state="changed"), expected[2]], expected
        )
