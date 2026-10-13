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
    READ_REGION, WRITE_REGION, READ_SECONDS, TIMEOUT, assert_destination, assert_fields,
    assert_guard, capture_native, emulator_endpoints, isolate, legacy_transport,
    load_account, rules, topology, wait_topology,
)

pytestmark = pytest.mark.cosmosEmulator


@pytest.mark.timeout(180)
@pytest.mark.parametrize("backend", ["core-python", "rust"])
@pytest.mark.parametrize("case", ["routing", "guard", "guard-disabled"])
def test_swr_mrr_succeeds(request, regional_target, monkeypatch, backend, case):
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
    state = {"hits": 0}
    if backend == "rust":
        settings = {"_fault_injection_rules": rules(rule_id, observer.id, account, case != "guard-disabled")}
        capture_native(monkeypatch, records)
    else:
        transport, state = legacy_transport(account, read_endpoint, observer.id, case != "guard-disabled", records)
        settings = {"transport": transport}
    with CosmosClient(
        write_endpoint, key, _backend=backend, consistency_level="Session",
        preferred_locations=[READ_REGION, WRITE_REGION], timeout=TIMEOUT, **settings,
    ) as client:
        container = client.get_database_client(database_id).get_container_client(observer.id)
        if backend == "rust":
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
        assert_route(before, (_binding_operation_count(), _rust_fallback_count()), backend)
        hits = client._adapter._debug_fault_injection_rule_hit_count(rule_id) if backend == "rust" else state["hits"]
        emit("regional_create", surface="sync", backend=backend, case=case, hits=hits, attempts=records,
             error_type=None if error is None else type(error).__name__, error=str(error))
        if case == "guard":
            with pytest.raises(exceptions.CosmosResourceNotFoundError) as absent:
                observer.read_item(item_id, partition_key=item_id)
            assert absent.value.status_code == 404
            emit("regional_stored_state", case=case, status=404)
            assert_guard(error, records, read_endpoint, hits, rule_id, backend)
            return
        assert error is None, f"Create unexpectedly failed: {error}"
        assert hits == 0
        destination = write_endpoint if case == "routing" else read_endpoint
        assert_destination(records, destination, 201)
        if backend == "core-python":
            assert created.get_response_headers()["_request"].url.startswith(destination)
        assert_fields(created, item)
        assert_fields(observer.read_item(item_id, partition_key=item_id), item)
        reads = 0
        start = time.perf_counter()
        while time.perf_counter() - start < READ_SECONDS:
            records.clear()
            before = (_binding_operation_count(), _rust_fallback_count())
            read = container.read_item(item_id, partition_key=item_id, timeout=TIMEOUT)
            assert_route(before, (_binding_operation_count(), _rust_fallback_count()), backend)
            assert_destination(records, read_endpoint, 200)
            if backend == "core-python":
                assert read.get_response_headers()["_request"].url.startswith(read_endpoint)
            assert_fields(read, item)
            reads += 1
            time.sleep(0.02)  # Routing coverage, not a throughput/throttling workload.
        assert reads > 0, "No reads were exercised"
        emit("regional_reads", surface="sync", backend=backend, case=case, count=reads,
             elapsed=time.perf_counter() - start, expected_fields=item)
