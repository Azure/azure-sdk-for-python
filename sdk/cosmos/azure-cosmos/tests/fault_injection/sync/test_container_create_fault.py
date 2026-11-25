# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Creation-specific 429 recovery, exhaustion, and deadline expiry on the emulator."""

import os
import time
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey, exceptions
from config.diagnostics import _binding_operation_count, fault_rule_hit_count
from fault_injection._container_create import (
    CREATE_FAULT_CASES,
    OPERATION_TIMEOUT,
    assert_creation_outcome,
    assert_stored_container,
    creation_fault_rule,
)
from fault_injection._delayed_create import assert_route, emit
from fault_injection._query_resume import set_rule

pytestmark = [pytest.mark.cosmosEmulator, pytest.mark.cosmosSdkFaultInjection]


@pytest.mark.timeout(90)
@pytest.mark.parametrize("fault,retry_limit,hit_limit,inject", CREATE_FAULT_CASES)
@pytest.mark.parametrize(
    "return_properties", [False, True], ids=["proxy", "properties"]
)
def test_container_create_fault_rust(
    owned_target, fault, retry_limit, hit_limit, inject, return_properties
):
    database_id, _ = owned_target
    container_id = "created_" + uuid.uuid4().hex
    rule_id = "container-create-" + uuid.uuid4().hex
    assert_stored_container(database_id, container_id, exists=False)
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
        hooks = []
        error, returned = None, None
        before = _binding_operation_count()
        set_rule(handle, rule_id, True)
        start = time.perf_counter()
        try:
            try:
                returned = database.create_container(
                    id=container_id,
                    partition_key=PartitionKey("/pk"),
                    default_ttl=90,
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
        finally:
            set_rule(handle, rule_id, False)
        elapsed = time.perf_counter() - start
        after = _binding_operation_count()
        hits = fault_rule_hit_count(client._adapter, rule_id)
        persisted = (
            not inject
            or fault == "timeout-after-service"
            or (fault == "throttle" and hit_limit is not None)
        )
        stored = assert_stored_container(database_id, container_id, exists=persisted)
        emit(
            "container_create_fault",
            surface="sync",
            database_id=database_id,
            container_id=container_id,
            fault=fault,
            inject=inject,
            return_properties=return_properties,
            retry_limit=retry_limit,
            hits=hits,
            elapsed=elapsed,
            error_type=None if error is None else type(error).__name__,
            persisted=stored is not None,
        )
        assert_route(before, after, "rust")
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
        )
        assert fault_rule_hit_count(client._adapter, rule_id) == hits
