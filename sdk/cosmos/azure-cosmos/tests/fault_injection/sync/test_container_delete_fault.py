# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Deletion faults with independent container and proof-item observations."""

import os
import time
import uuid

import pytest

from azure.cosmos import CosmosClient, _rust, exceptions
from config.diagnostics import _binding_operation_count, emit, fault_rule_hit_count
from fault_injection._container_create import OPERATION_TIMEOUT
from fault_injection._container_delete import (
    DELETE_FAULT_CASES,
    assert_deletion_outcome,
    assert_stored_target,
    deletion_fault_rules,
    seed_target,
)
from fault_injection._delayed_create import assert_route
from fault_injection._query_resume import set_rule

pytestmark = [pytest.mark.cosmosEmulator, pytest.mark.cosmosSdkFaultInjection]


@pytest.mark.timeout(90)
@pytest.mark.parametrize("phase,fault,retry_limit,hit_limit,inject", DELETE_FAULT_CASES)
def test_container_delete_fault_rust(
    owned_target, phase, fault, retry_limit, hit_limit, inject
):
    database_id, setup_container = owned_target
    container_id = setup_container.id
    properties, proof = seed_target(setup_container)
    rule_id = "container-delete-" + uuid.uuid4().hex
    rules = deletion_fault_rules(rule_id, phase, fault, hit_limit, inject)
    with CosmosClient(
        os.environ["ACCOUNT_HOST"],
        os.environ["ACCOUNT_KEY"],
        _backend="rust",
        retry_throttle_total=retry_limit,
        _fault_injection_rules=rules,
    ) as client:
        database = client.get_database_client(database_id)
        database.read(timeout=30)
        handle = client._adapter._ensure_driver_handle()
        if phase == "delete":
            _rust.get_container_metadata(
                handle, setup_container.container_link, timeout_seconds=30
            )
        for rule in rules:
            assert fault_rule_hit_count(client._adapter, rule["id"]) == 0
        hooks = []
        error, returned = None, None
        before = _binding_operation_count()
        for rule in rules:
            set_rule(handle, rule["id"], True)
        start = time.perf_counter()
        try:
            returned = database.delete_container(
                container_id,
                timeout=30 if fault == "throttle" else OPERATION_TIMEOUT,
                response_hook=lambda headers, body: hooks.append((dict(headers), body)),
            )
        except (
            exceptions.CosmosHttpResponseError,
            exceptions.CosmosClientTimeoutError,
        ) as caught:
            error = caught
        finally:
            for rule in rules:
                set_rule(handle, rule["id"], False)
        elapsed = time.perf_counter() - start
        after = _binding_operation_count()
        hits = fault_rule_hit_count(client._adapter, rule_id)
        if phase == "delete":
            assert fault_rule_hit_count(client._adapter, rules[0]["id"]) == 0
        preserved = inject and (
            fault == "timeout" or (fault == "throttle" and hit_limit is None)
        )
        assert_stored_target(
            database_id, container_id, properties, proof, exists=preserved
        )
        emit(
            "container_delete_fault",
            surface="sync",
            phase=phase,
            fault=fault,
            inject=inject,
            retry_limit=retry_limit,
            hits=hits,
            elapsed=elapsed,
            error_type=None if error is None else type(error).__name__,
            preserved=preserved,
        )
        assert_route(before, after, "rust")
        assert_deletion_outcome(
            fault=fault,
            inject=inject,
            retry_limit=retry_limit,
            hit_limit=hit_limit,
            error=error,
            returned=returned,
            hooks=hooks,
            elapsed=elapsed,
            hits=hits,
        )
        assert fault_rule_hit_count(client._adapter, rule_id) == hits
