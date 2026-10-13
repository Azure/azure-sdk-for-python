# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""F11 response-side failure through the synchronous public point-read API."""
import os
import time
import uuid

import pytest

from azure.core.exceptions import ServiceRequestError, ServiceResponseError
from azure.cosmos import CosmosClient, _rust, exceptions
from common._parity_helpers import _binding_operation_count, _rust_fallback_count
from fault_injection._delayed_create import assert_control, assert_route, emit
from fault_injection._response_failure import OPERATION_TIMEOUT, assert_response_failure, response_failure_rule

pytestmark = pytest.mark.cosmosEmulator


@pytest.mark.timeout(90)
@pytest.mark.parametrize("inject", [True, False], ids=["response-failure", "no-injection"])
def test_point_read_response_failure(owned_target, inject):
    database_id, observer = owned_target
    item_id = uuid.uuid4().hex
    item = {"id": item_id, "pk": item_id, "name": "order-17", "state": "confirmed"}
    observer.create_item(item)
    rule_id = "response-failure-" + uuid.uuid4().hex
    with CosmosClient(
        os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"],
        _backend="rust", consistency_level="Session",
        _fault_injection_rules=[response_failure_rule(rule_id, observer.id, inject)],
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
        emit("response_failure", surface="sync", backend="rust", inject=inject, database_id=database_id,
             rule_id=rule_id, elapsed=elapsed, hits=hits,
             error_type=None if error is None else type(error).__name__,
             error_message=None if error is None else str(error),
             cause_type=None if error is None else type(error.__cause__).__name__,
             binding_delta=after[0] - before[0], fallback_delta=after[1] - before[1])
        assert_route(before, after, "rust")
        stored = observer.read_item(item_id, partition_key=item_id)
        assert {field: stored[field] for field in item} == item, "Stored customer fields changed"
        emit("stored_state", surface="sync", inject=inject, item_id=item_id,
             fields={field: stored[field] for field in item})
        if inject:
            assert returned is None
            assert_response_failure(error, elapsed, hits)
            assert isinstance(error.__cause__, _rust._DriverTransportError), "Native transport cause was lost"
        else:
            assert error is None, "The no-injection read failed"
            assert_control(returned, stored, item, hits)
