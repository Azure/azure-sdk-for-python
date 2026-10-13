# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import pytest

from azure.core.exceptions import ServiceRequestError, ServiceResponseError
from azure.cosmos import exceptions
from azure.cosmos._backend.client_config import _prepare_fault_injection_rules
from fault_injection._response_failure import OPERATION_TIMEOUT, assert_response_failure, response_failure_rule


@pytest.mark.parametrize("inject", [True, False])
def test_response_fault_is_scoped_transport_error_without_delay(inject):
    rule = response_failure_rule("rule", "owned-container", inject)
    prepared, = _prepare_fault_injection_rules([rule])
    assert prepared.id == "rule"
    assert prepared.container_id == "owned-container"
    assert prepared.operation_type == "ReadItem"
    assert prepared.error_type == "ResponseTimeout"
    assert prepared.status_code is None
    assert prepared.sub_status == 0
    assert prepared.response_body == b""
    assert prepared.delay_ms == 0
    assert prepared.probability == (1.0 if inject else 0.0)
    assert prepared.hit_limit is None
    assert prepared.enabled is True
    assert "status_code" not in rule


@pytest.mark.parametrize("error", [
    None, exceptions.CosmosClientTimeoutError(), TimeoutError("raw or outer deadline"),
    exceptions.CosmosHttpResponseError(408), exceptions.CosmosHttpResponseError(503),
    ServiceRequestError("failed before sending"), RuntimeError("raw binding error"),
])
def test_response_failure_rejects_success_deadline_http_and_wrong_transport_error(error):
    with pytest.raises(AssertionError, match="Expected ServiceResponseError"):
        assert_response_failure(error, 1.0, 1)


@pytest.mark.parametrize("hits", [0, -1])
def test_response_failure_requires_applied_fault(hits):
    with pytest.raises(AssertionError, match="did not apply"):
        assert_response_failure(ServiceResponseError("injected"), 1.0, hits)


@pytest.mark.parametrize("elapsed", [-1, OPERATION_TIMEOUT, OPERATION_TIMEOUT + 1, float("nan"), float("inf")])
def test_response_failure_rejects_expired_or_invalid_budget(elapsed):
    with pytest.raises(AssertionError, match="before the operation budget"):
        assert_response_failure(ServiceResponseError("injected"), elapsed, 1)


@pytest.mark.parametrize("hits", [1, 3])
def test_response_failure_accepts_transport_error_without_inventing_retry_count(hits):
    assert_response_failure(ServiceResponseError("injected"), 1.0, hits)
