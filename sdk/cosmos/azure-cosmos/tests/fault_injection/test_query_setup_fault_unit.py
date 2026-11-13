# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from types import SimpleNamespace

import pytest

from azure.cosmos import exceptions
from azure.cosmos._backend.client_config import _prepare_fault_injection_rules
from fault_injection._query_setup import (
    GUARD_SUBSTATUS,
    SETUP_SUBSTATUS,
    assert_guard_failure,
    assert_setup_failure,
    setup_rules,
)


@pytest.mark.parametrize("inject", [True, False])
def test_setup_and_execution_rules_have_independent_controls_rust(inject):
    metadata, guard = _prepare_fault_injection_rules(
        setup_rules("metadata", "guard", "owned", inject)
    )
    assert metadata.id != guard.id
    assert (
        metadata.operation_type == "MetadataReadContainer"
        and guard.operation_type == "QueryItem"
    )
    assert metadata.enabled and metadata.probability == (1 if inject else 0)
    assert guard.enabled is inject and guard.probability == 1
    assert (
        metadata.sub_status == SETUP_SUBSTATUS and guard.sub_status == GUARD_SUBSTATUS
    )
    for rule in (metadata, guard):
        assert rule.container_id == "owned" and rule.status_code == 429
        assert rule.hit_limit is None and rule.delay_ms == 0


def setup_evidence():
    cursor = SimpleNamespace(can_retry_setup=True)
    pages = SimpleNamespace(
        state=SimpleNamespace(cursor=cursor, failed=False), continuation_token=None
    )
    error = exceptions.CosmosHttpResponseError(
        response=SimpleNamespace(
            status_code=429,
            headers={"x-ms-substatus": str(SETUP_SUBSTATUS)},
            reason="synthetic",
        )
    )
    error.continuation_token = None
    return dict(
        error=error,
        pages=pages,
        cursor=cursor,
        hooks=[],
        metadata_hits=1,
        guard_hits=0,
        elapsed=0.1,
    )


def test_setup_failure_accepts_unstarted_retryable_cursor_rust():
    assert_setup_failure(**setup_evidence())


@pytest.mark.parametrize(
    "change",
    [
        "wrong-error",
        "wrong-status",
        "wrong-substatus",
        "missing-metadata",
        "query-started",
        "native-started",
        "failed-iterator",
        "lost-cursor",
        "hook-called",
        "advanced-token",
        "advanced-error-token",
        "timeout",
        "nan",
    ],
)
def test_setup_failure_rejects_false_evidence_rust(change):
    evidence = setup_evidence()
    if change == "wrong-error":
        evidence["error"] = TimeoutError()
    elif change == "wrong-status":
        evidence["error"].status_code = 503
    elif change == "wrong-substatus":
        evidence["error"].sub_status = 0
    elif change == "missing-metadata":
        evidence["metadata_hits"] = 0
    elif change == "query-started":
        evidence["guard_hits"] = 1
    elif change == "native-started":
        evidence["cursor"].can_retry_setup = False
    elif change == "failed-iterator":
        evidence["pages"].state.failed = True
    elif change == "lost-cursor":
        evidence["pages"].state.cursor = None
    elif change == "hook-called":
        evidence["hooks"].append({})
    elif change == "advanced-token":
        evidence["pages"].continuation_token = "q1.invalid"
    elif change == "advanced-error-token":
        evidence["error"].continuation_token = "q1.invalid"
    elif change == "timeout":
        evidence["elapsed"] = 30
    else:
        evidence["elapsed"] = float("nan")
    with pytest.raises(AssertionError):
        assert_setup_failure(**evidence)


@pytest.mark.parametrize(
    "substatus,hits", [(SETUP_SUBSTATUS, 1), (GUARD_SUBSTATUS, 0), (GUARD_SUBSTATUS, 2)]
)
def test_guard_requires_matching_positive_execution_fault_rust(substatus, hits):
    error = exceptions.CosmosHttpResponseError(status_code=429, sub_status=substatus)
    with pytest.raises(AssertionError):
        assert_guard_failure(error, hits)


def test_guard_accepts_one_execution_fault_rust():
    assert_guard_failure(
        exceptions.CosmosHttpResponseError(status_code=429, sub_status=GUARD_SUBSTATUS),
        1,
    )
