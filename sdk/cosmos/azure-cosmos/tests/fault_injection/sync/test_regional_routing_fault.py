# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Adapted from test_fault_injection_transport.TestFaultInjectionTransport.test_swr_mrr_succeeds.

Keep create/read destination checks and the two-second read window.
Add field checks, attempted-destination evidence, and a forbidden-write control.
"""
import os
import time
import uuid

import pytest

from azure.core.exceptions import ServiceResponseError
from azure.cosmos import CosmosClient, exceptions
from common._parity_helpers import _binding_operation_count, _rust_fallback_count
from fault_injection._delayed_create import assert_route, emit
from fault_injection._regional_routing import (
    READ_REGION, WRITE_REGION, READ_SECONDS, REGIONAL_ROUTING_CASES, TIMEOUT, assert_destination, assert_fields,
    assert_guard, capture_native, emulator_endpoints, isolate,
    load_account, rules, topology, wait_topology,
)

pytestmark = pytest.mark.cosmosEmulator


@pytest.mark.timeout(180)
@pytest.mark.parametrize("case", REGIONAL_ROUTING_CASES)
def test_swr_mrr_succeeds_rust(request, regional_target, monkeypatch, case):
    if isolate(request, regional_target):
        return
    database_id, observer = regional_target
    endpoint, key = os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"]
    write_endpoint, read_endpoint = emulator_endpoints(endpoint)
    account = topology(load_account(endpoint, key), write_endpoint, read_endpoint, case != "routing")
    rule_id = "forbidden-write-" + uuid.uuid4().hex
    item_id = uuid.uuid4().hex
    item = {"id": item_id, "pk": item_id, "name": "sample document", "key": "value"}
    records = []
    capture_native(monkeypatch, records)
    with CosmosClient(
        write_endpoint, key, _backend="rust", consistency_level="Session",
        preferred_locations=[READ_REGION, WRITE_REGION], timeout=TIMEOUT,
        _fault_injection_rules=rules(rule_id, observer.id, account, case != "guard-disabled"),
    ) as client:
        container = client.get_database_client(database_id).get_container_client(observer.id)
        wait_topology(client, rule_id, case != "routing")
        assert client._adapter._debug_fault_injection_rule_hit_count(rule_id) == 0
        container.read()
        records.clear()
        before = (_binding_operation_count(), _rust_fallback_count())
        error, created = None, None
        try:
            created = container.create_item(item, timeout=TIMEOUT)
        except (exceptions.CosmosHttpResponseError, ServiceResponseError) as caught:
            error = caught
        assert_route(before, (_binding_operation_count(), _rust_fallback_count()), "rust")
        hits = client._adapter._debug_fault_injection_rule_hit_count(rule_id)
        emit("regional_create", surface="sync", backend="rust", case=case, hits=hits, attempts=records,
             error_type=None if error is None else type(error).__name__, error=str(error))
        if case == "guard":
            with pytest.raises(exceptions.CosmosResourceNotFoundError) as absent:
                observer.read_item(item_id, partition_key=item_id)
            assert absent.value.status_code == 404
            emit("regional_stored_state", case=case, status=404)
            assert_guard(error, records, read_endpoint, hits, rule_id)
            return
        assert error is None, f"Create unexpectedly failed: {error}"
        assert hits == 0
        destination = write_endpoint if case == "routing" else read_endpoint
        assert_destination(records, destination, 201)
        assert_fields(created, item)
        assert_fields(observer.read_item(item_id, partition_key=item_id), item)
        reads = 0
        start = time.perf_counter()
        while time.perf_counter() - start < READ_SECONDS:
            records.clear()
            before = (_binding_operation_count(), _rust_fallback_count())
            read = container.read_item(item_id, partition_key=item_id, timeout=TIMEOUT)
            assert_route(before, (_binding_operation_count(), _rust_fallback_count()), "rust")
            assert_destination(records, read_endpoint, 200)
            assert_fields(read, item)
            reads += 1
            time.sleep(0.02)  # Routing coverage, not a throughput/throttling workload.
        assert reads > 0, "No reads were exercised"
        emit("regional_reads", surface="sync", backend="rust", case=case, count=reads,
             elapsed=time.perf_counter() - start, expected_fields=item)
