# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Get-or-create faults with independent service-state verification."""

import os
import time
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey, exceptions
from config.diagnostics import _binding_operation_count, emit, fault_rule_hit_count
from fault_injection._container_create import (
    OPERATION_TIMEOUT,
    assert_creation_outcome,
    assert_stored_container,
    creation_fault_rule,
)
from fault_injection._container_get_or_create import (
    GET_OR_CREATE_FAULT_CASES,
    assert_workflow_calls,
    capture_workflow_calls,
    prepare_target,
)

pytestmark = [pytest.mark.cosmosEmulator, pytest.mark.cosmosSdkFaultInjection]


@pytest.mark.timeout(90)
@pytest.mark.parametrize(
    "phase,existing,fault,retry_limit,hit_limit,inject", GET_OR_CREATE_FAULT_CASES
)
@pytest.mark.parametrize(
    "return_properties", [False, True], ids=["proxy", "properties"]
)
def test_container_get_or_create_fault_rust(
    owned_target,
    monkeypatch,
    phase,
    existing,
    fault,
    retry_limit,
    hit_limit,
    inject,
    return_properties,
):
    database_id, _ = owned_target
    container_id = "get_or_create_" + uuid.uuid4().hex
    original = prepare_target(database_id, container_id, existing)
    rule_id = "container-get-or-create-" + uuid.uuid4().hex
    with CosmosClient(
        os.environ["ACCOUNT_HOST"],
        os.environ["ACCOUNT_KEY"],
        _backend="rust",
        retry_throttle_total=retry_limit,
        _fault_injection_rules=[creation_fault_rule(rule_id, fault, hit_limit, inject)],
    ) as client:
        database = client.get_database_client(database_id)
        database.read(timeout=30)
        handle = client._adapter._ensure_driver_handle()
        assert fault_rule_hit_count(client._adapter, rule_id) == 0
        calls = capture_workflow_calls(monkeypatch, client, handle, rule_id, phase)
        hooks = []
        error, returned = None, None
        before = _binding_operation_count()
        start = time.perf_counter()
        try:
            returned = database.create_container_if_not_exists(
                container_id,
                PartitionKey("/different" if existing else "/pk"),
                default_ttl=30 if existing else 90,
                return_properties=return_properties,
                timeout=30 if fault == "throttle" else OPERATION_TIMEOUT,
                response_hook=lambda headers, body: hooks.append(
                    (dict(headers), dict(body))
                ),
            )
        except (
            exceptions.CosmosHttpResponseError,
            exceptions.CosmosClientTimeoutError,
        ) as caught:
            error = caught
        elapsed = time.perf_counter() - start
        after = _binding_operation_count()
        hits = fault_rule_hit_count(client._adapter, rule_id)
        persisted = (
            existing
            or not inject
            or fault == "timeout-after-service"
            or (fault == "throttle" and hit_limit is not None)
        )
        stored = assert_stored_container(database_id, container_id, exists=persisted)
        emit(
            "container_get_or_create_fault",
            surface="sync",
            phase=phase,
            existing=existing,
            fault=fault,
            inject=inject,
            return_properties=return_properties,
            retry_limit=retry_limit,
            hits=hits,
            elapsed=elapsed,
            error_type=None if error is None else type(error).__name__,
            persisted=stored is not None,
        )
        assert_workflow_calls(
            calls,
            before,
            after,
            phase=phase,
            existing=existing,
            fault=fault,
            inject=inject,
            hit_limit=hit_limit,
        )
        assert_creation_outcome(
            fault=fault,
            inject=inject,
            retry_limit=retry_limit,
            hit_limit=hit_limit,
            error=error,
            returned=returned,
            hooks=hooks,
            elapsed=elapsed,
            hits=hits,
            stored=stored,
            return_properties=return_properties,
            existing_properties=original,
        )
        assert fault_rule_hit_count(client._adapter, rule_id) == hits
