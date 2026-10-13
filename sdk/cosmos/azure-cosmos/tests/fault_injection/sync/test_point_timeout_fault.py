# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""F12 point-read operation timeout through the synchronous Python/Rust boundary."""
import os
import time
import uuid

import pytest

from azure.core.exceptions import ServiceResponseError
from azure.cosmos import CosmosClient, exceptions
from common._parity_helpers import _binding_operation_count, _rust_fallback_count
from fault_injection._delayed_create import assert_control, assert_route, emit
from fault_injection._point_timeout import (
    OPERATION_TIMEOUT, assert_point_timeout, assert_read_budget, assert_read_elapsed,
    capture_read_budget, read_timeout_rule,
)

pytestmark = pytest.mark.cosmosEmulator


@pytest.mark.timeout(90)
@pytest.mark.parametrize("inject", [True, False], ids=["delayed-read", "no-injection"])
def test_point_read_operation_timeout(owned_target, monkeypatch, inject):
    database_id, observer = owned_target
    item_id = uuid.uuid4().hex
    item = {"id": item_id, "pk": item_id, "name": "order-17", "state": "confirmed"}
    observer.create_item(item)
    rule_id = "read-timeout-" + uuid.uuid4().hex
    with CosmosClient(
        os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"],
        _backend="rust", consistency_level="Session",
        _fault_injection_rules=[read_timeout_rule(rule_id, observer.id, inject)],
    ) as client:
        container = client.get_database_client(database_id).get_container_client(observer.id)
        container.read(timeout=30)
        # Warm the driver's partition-key metadata as well as the Python container cache.
        client._adapter.get_container_metadata(container.container_link, deadline=time.monotonic() + 30)
        assert client._adapter._debug_fault_injection_rule_hit_count(rule_id) == 0
        budgets = capture_read_budget(monkeypatch)
        before = (_binding_operation_count(), _rust_fallback_count())
        error, returned = None, None
        start = time.perf_counter()
        try:
            returned = container.read_item(item_id, partition_key=item_id, timeout=OPERATION_TIMEOUT)
        except (exceptions.CosmosClientTimeoutError, exceptions.CosmosHttpResponseError,
                ServiceResponseError, TimeoutError) as caught:
            error = caught
        elapsed = time.perf_counter() - start
        after = (_binding_operation_count(), _rust_fallback_count())
        hits = client._adapter._debug_fault_injection_rule_hit_count(rule_id)
        emit("point_timeout", surface="sync", backend="rust", inject=inject, database_id=database_id,
             rule_id=rule_id, elapsed=elapsed, hits=hits, native_budgets=budgets,
             error_type=None if error is None else type(error).__name__,
             error_message=None if error is None else str(error),
             binding_delta=after[0] - before[0], fallback_delta=after[1] - before[1])
        assert_route(before, after, "rust")
        assert_read_budget(budgets)
        stored = observer.read_item(item_id, partition_key=item_id)
        assert {field: stored[field] for field in item} == item, "Stored customer fields changed"
        emit("stored_state", surface="sync", inject=inject, item_id=item_id,
             fields={field: stored[field] for field in item})
        if inject:
            assert returned is None
            assert_point_timeout(error, elapsed, hits)
        else:
            assert error is None, "The no-injection read timed out"
            assert_read_elapsed(elapsed)
            assert_control(returned, stored, item, hits)
