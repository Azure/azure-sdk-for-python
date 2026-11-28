# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

import azure.cosmos
from azure.cosmos import exceptions
from azure.cosmos._backend.client_config import _prepare_fault_injection_rules
from fault_injection._query_resume import (
    FAULT_STATUS,
    FAULT_SUBSTATUS,
    PAGE_BUDGET,
    assert_complete,
    assert_failure,
    capture_query_calls,
    resume_rule,
)


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize(
    "budget,accepted",
    [
        pytest.param((1000.003 + PAGE_BUDGET) - 1000.003, True, id="deadline-roundoff"),
        pytest.param(PAGE_BUDGET, True, id="full-budget"),
        pytest.param(PAGE_BUDGET - 1, True, id="remaining-budget"),
        pytest.param(None, False, id="missing"),
        pytest.param(0, False, id="expired"),
        pytest.param(-1, False, id="negative"),
        pytest.param(float("nan"), False, id="nan"),
        pytest.param(float("inf"), False, id="infinite"),
        pytest.param(PAGE_BUDGET + 0.001, False, id="over-budget"),
    ],
)
def test_query_capture_validates_budget_without_rewriting_it_rust(
    monkeypatch, asynchronous, budget, accepted
):
    name = "fetch_page_with_cursor_async" if asynchronous else "fetch_page_with_cursor"
    native = Mock()
    binding = SimpleNamespace(_ItemFeedCursor=SimpleNamespace, **{name: native})
    monkeypatch.setattr(azure.cosmos, "_rust", binding, raising=False)
    calls = capture_query_calls(monkeypatch, asynchronous=asynchronous)
    handle, prepared, cursor = (
        object(),
        SimpleNamespace(op="query_items"),
        SimpleNamespace(),
    )
    observed = getattr(binding, name)
    if accepted:
        assert (
            observed(handle, prepared, cursor, timeout_seconds=budget)
            is native.return_value
        )
        native.assert_called_once_with(handle, prepared, cursor, timeout_seconds=budget)
        assert calls == [(handle, cursor)]
    else:
        with pytest.raises(
            AssertionError, match="Unexpected query timeout budget"
        ) as error:
            observed(handle, prepared, cursor, timeout_seconds=budget)
        assert repr(budget) in str(error.value)
        native.assert_not_called()
        assert not calls


@pytest.mark.parametrize("inject", [True, False])
def test_resume_rule_is_disabled_until_after_delivery_rust(inject):
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
def test_resume_failure_rejects_wrong_error_progress_or_fault_count_rust(
    error, hits, elapsed
):
    with pytest.raises(AssertionError):
        assert_failure(error, "service-saved", hits, elapsed)


def test_resume_failure_accepts_exact_public_bookmark_rust():
    assert_failure(failure(), "service-saved", 1, 0.1)


@pytest.mark.parametrize("ids", [[0, 1, 2], [1], [2], [1, 1, 2], [2, 1]])
def test_resume_result_rejects_replay_gaps_duplicates_or_reordering_rust(ids):
    expected = [{"id": i, "state": "confirmed"} for i in range(3)]
    with pytest.raises(AssertionError):
        assert_complete(expected[:1], [expected[i] for i in ids], expected)


def test_resume_result_accepts_exact_rows_and_rejects_changed_fields_rust():
    expected = [{"id": i, "state": "confirmed"} for i in range(3)]
    assert_complete(expected[:1], expected[1:], expected)
    with pytest.raises(AssertionError):
        assert_complete(
            expected[:1], [dict(expected[1], state="changed"), expected[2]], expected
        )
