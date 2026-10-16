# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import pytest

from azure.core.exceptions import ServiceResponseError
from azure.cosmos import exceptions
from azure.cosmos._backend.client_config import _prepare_fault_injection_rules
from fault_injection._query_page_timeout import (
    BETWEEN_PAGES_DELAY, DELAY_MS, PAGE_TIMEOUT, assert_page_call, assert_page_timeout, query_timeout_rule,
)


@pytest.mark.parametrize("inject", [True, False])
def test_query_timeout_rule_targets_execution_not_metadata_or_point_reads(inject):
    prepared, = _prepare_fault_injection_rules([query_timeout_rule("rule", "owned-container", inject)])
    assert prepared.id == "rule" and prepared.container_id == "owned-container"
    assert prepared.operation_type == "QueryItem"
    assert prepared.status_code == 503 and prepared.error_type is None
    assert prepared.delay_ms == DELAY_MS == 5000
    assert prepared.probability == (1.0 if inject else 0.0)
    assert prepared.hit_limit is None and prepared.enabled is True
    assert 0 < PAGE_TIMEOUT < BETWEEN_PAGES_DELAY < DELAY_MS / 1000


@pytest.mark.parametrize("error,elapsed,hits", [
    (None, 1, 1),
    (TimeoutError(), 1, 1),
    (exceptions.CosmosHttpResponseError(408), 1, 1),
    (ServiceResponseError("timeout"), 1, 1),
    (exceptions.CosmosClientTimeoutError(), 0, 1),
    (exceptions.CosmosClientTimeoutError(), 5, 1),
    (exceptions.CosmosClientTimeoutError(), float("nan"), 1),
    (exceptions.CosmosClientTimeoutError(), float("inf"), 1),
    (exceptions.CosmosClientTimeoutError(), 1, 0),
])
def test_query_page_timeout_rejects_false_positive(error, elapsed, hits):
    with pytest.raises(AssertionError):
        assert_page_timeout(error, elapsed, hits)


def test_query_page_timeout_accepts_applied_bounded_timeout():
    assert_page_timeout(exceptions.CosmosClientTimeoutError(), 1, 1)


@pytest.mark.parametrize("budget", [None, 0, -1, 1.01, float("nan"), float("inf")])
def test_query_page_requires_valid_remaining_budget(budget):
    with pytest.raises(AssertionError, match="remaining page budget"):
        assert_page_call([{"op": "query_items", "native_cursor": True, "timeout_seconds": budget}])


@pytest.mark.parametrize("op,native_cursor", [("read_all_items", True), ("query_items", False)])
def test_query_page_requires_real_retained_query_path(op, native_cursor):
    with pytest.raises(AssertionError, match="real query cursor"):
        assert_page_call([{"op": op, "native_cursor": native_cursor, "timeout_seconds": 0.99}])


@pytest.mark.parametrize("count", [0, 2])
def test_query_page_requires_exactly_one_native_call(count):
    call = {"op": "query_items", "native_cursor": True, "timeout_seconds": 0.99}
    with pytest.raises(AssertionError, match="one retained native"):
        assert_page_call([call] * count)


def test_query_page_accepts_remaining_native_budget():
    assert_page_call([{"op": "query_items", "native_cursor": True, "timeout_seconds": 0.99}])
