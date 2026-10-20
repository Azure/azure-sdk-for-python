# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Adapted from test_fault_injection_transport.TestFaultInjectionTransport.test_throws_injected_error.

Preserve the delayed 502 assertion; replace only the injection mechanism on Rust.
The fresh-client no-injection control additionally checks returned and stored fields.
The immediate-502 Rust rule case is retained here alongside the delayed scenario.
"""
import os
import time
import uuid

import pytest

from azure.cosmos import CosmosClient, exceptions
from common._parity_helpers import _binding_operation_count, _rust_fallback_count
from fault_injection._delayed_create import (
    OPERATION_TIMEOUT, assert_control, assert_failure, assert_route, create_rule, emit,
)

pytestmark = pytest.mark.cosmosEmulator


@pytest.mark.timeout(180)
@pytest.mark.parametrize("inject", [True, False], ids=["delayed-502-rust", "no-injection-rust"])
def test_throws_injected_error_rust(owned_target, inject):
    database_id, owned_container = owned_target
    item_id = uuid.uuid4().hex
    item = {"id": item_id, "pk": item_id, "name": "sample document", "key": "value"}
    rule_id = "create-502-" + uuid.uuid4().hex
    with CosmosClient(
        os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"],
        _backend="rust", consistency_level="Session",
        _fault_injection_rules=[create_rule(rule_id, owned_container.id, inject)],
    ) as client:
        container = client.get_database_client(database_id).get_container_client(owned_container.id)
        container.read()
        assert client._adapter._debug_fault_injection_rule_hit_count(rule_id) == 0
        before = (_binding_operation_count(), _rust_fallback_count())
        start = time.perf_counter()
        error = None
        returned = None
        try:
            returned = container.create_item(body=item, timeout=OPERATION_TIMEOUT)
        except exceptions.CosmosHttpResponseError as caught:
            error = caught
        elapsed = time.perf_counter() - start
        after = (_binding_operation_count(), _rust_fallback_count())
        hits = client._adapter._debug_fault_injection_rule_hit_count(rule_id)
        emit("operation", surface="sync", backend="rust", inject=inject, rule_id=rule_id,
             database_id=database_id, item=item,
             elapsed=elapsed, hits=hits, status=None if error is None else error.status_code,
             binding_delta=after[0] - before[0], fallback_delta=after[1] - before[1])
        assert_route(before, after, "rust")
        if inject:
            assert_failure(error, elapsed, hits)
            with pytest.raises(exceptions.CosmosResourceNotFoundError) as absent:
                owned_container.read_item(item_id, partition_key=item_id)
            assert absent.value.status_code == 404
            emit("stored_state", surface="sync", backend="rust", inject=True, item_id=item_id, status=404)
        else:
            assert error is None, "The no-injection create failed"
            stored = owned_container.read_item(item_id, partition_key=item_id)
            assert_control(returned, stored, item, hits)
            with pytest.raises(AssertionError, match="Expected a Cosmos HTTP failure"):
                assert_failure(error, elapsed, hits)
            emit("stored_state", surface="sync", backend="rust", inject=False,
                 item_id=item_id, fields={field: stored[field] for field in item})


@pytest.mark.timeout(180)
def test_create_item_502_fault_rule_rust(owned_target):
    """Recreate the 502 transport fault through the Rust driver's fault layer."""
    database_id, owned_container = owned_target
    rule_id = "python-create-item-502-" + uuid.uuid4().hex
    with CosmosClient(
        os.environ["ACCOUNT_HOST"],
        os.environ["ACCOUNT_KEY"],
        consistency_level="Session",
        _backend="rust",
        _fault_injection_rules=[
            {
                "id": rule_id,
                "operation_type": "CreateItem",
                "container_id": owned_container.id,
                "status_code": 502,
            }
        ],
    ) as client:
        container = client.get_database_client(database_id).get_container_client(owned_container.id)
        item_id = str(uuid.uuid4())
        with pytest.raises(exceptions.CosmosHttpResponseError) as error:
            container.create_item(
                {
                    "id": item_id,
                    "pk": item_id,
                    "name": "sample document",
                    "key": "value",
                }
            )

        assert error.value.status_code == 502
        assert client._adapter._debug_fault_injection_rule_hit_count(rule_id) > 0
