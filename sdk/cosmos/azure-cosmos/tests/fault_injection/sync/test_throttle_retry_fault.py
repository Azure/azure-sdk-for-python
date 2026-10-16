# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""F07 throttle retry counts, alias precedence, and waiting budgets through synchronous reads."""
import os
import time
import uuid

import pytest

from azure.core.exceptions import ServiceRequestError, ServiceResponseError
from azure.cosmos import CosmosClient, exceptions
from common._parity_helpers import _binding_operation_count, _rust_fallback_count
from fault_injection._delayed_create import assert_control, assert_route, emit
from fault_injection._throttle_retry import (
    OPERATION_TIMEOUT, THROTTLE_RETRY_CASES, assert_throttle_failure, assert_throttle_wait_failure, throttle_rule,
)

pytestmark = pytest.mark.cosmosEmulator


@pytest.mark.timeout(90)
@pytest.mark.parametrize("retry_settings,retry_limit", THROTTLE_RETRY_CASES)
@pytest.mark.parametrize("inject", [True, False], ids=["persistent-429", "no-injection"])
def test_point_read_throttle_retry_limit(owned_target, retry_settings, retry_limit, inject):
    database_id, observer = owned_target
    item_id = uuid.uuid4().hex
    item = {"id": item_id, "pk": item_id, "name": "order-17", "state": "confirmed"}
    observer.create_item(item)
    rule_id = "throttle-read-" + uuid.uuid4().hex
    wait_budget = "retry_throttle_backoff_max" in retry_settings
    rule = throttle_rule(rule_id, observer.id, inject, wait_budget=wait_budget)
    with CosmosClient(
        os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"],
        _backend="rust", consistency_level="Session",
        _fault_injection_rules=[rule],
        **retry_settings,  # Pass omitted, zero, and None settings unchanged to the public API.
    ) as client:
        container = client.get_database_client(database_id).get_container_client(observer.id)
        container.read(timeout=30)
        client._adapter.get_container_metadata(container.container_link, deadline=time.monotonic() + 30)
        assert client._adapter._debug_fault_injection_rule_hit_count(rule_id) == 0
        before = (_binding_operation_count(), _rust_fallback_count())
        error, returned = None, None
        start = time.perf_counter()
        try:
            returned = container.read_item(item_id, partition_key=item_id, timeout=OPERATION_TIMEOUT)
        except (exceptions.CosmosClientTimeoutError, exceptions.CosmosHttpResponseError,
                ServiceRequestError, ServiceResponseError, TimeoutError) as caught:
            error = caught
        elapsed = time.perf_counter() - start
        after = (_binding_operation_count(), _rust_fallback_count())
        hits = client._adapter._debug_fault_injection_rule_hit_count(rule_id)
        emit("throttle_retry", surface="sync", backend="rust", inject=inject, database_id=database_id,
             rule_id=rule_id, retry_settings=retry_settings, retry_limit=retry_limit, elapsed=elapsed, hits=hits,
             response_headers=rule.get("response_headers", {}),
             error_type=None if error is None else type(error).__name__,
             status=error.status_code if isinstance(error, exceptions.CosmosHttpResponseError) else None,
             error_message=None if error is None else str(error),
             binding_delta=after[0] - before[0], fallback_delta=after[1] - before[1])
        assert_route(before, after, "rust")
        stored = observer.read_item(item_id, partition_key=item_id)
        assert {field: stored[field] for field in item} == item, "Stored customer fields changed"
        emit("stored_state", surface="sync", inject=inject, retry_limit=retry_limit, item_id=item_id,
             fields={field: stored[field] for field in item})
        if inject:
            assert returned is None
            if wait_budget:
                assert_throttle_wait_failure(error, elapsed, hits, retry_limit)
            else:
                assert_throttle_failure(error, elapsed, hits, retry_limit)
        else:
            assert error is None, "The no-injection read failed"
            assert_control(returned, stored, item, hits)
