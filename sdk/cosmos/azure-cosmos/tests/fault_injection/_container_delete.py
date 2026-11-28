# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Fault metadata resolution or deletion and independently observe stored state."""

import math
import os

import pytest

from azure.cosmos import exceptions
from config.clients import create_fault_setup_client
from fault_injection._container_create import (
    CREATE_FAULT_CASES,
    MAX_OPERATION_ELAPSED,
    MIN_TIMEOUT_ELAPSED,
    creation_fault_rule,
)
from fault_injection._throttle_retry import assert_throttle_failure

DELETE_FAULT_CASES = [
    pytest.param(phase, *case.values, id=f"{phase}-{case.id}")
    for phase in ("metadata", "delete")
    for case in CREATE_FAULT_CASES
    if phase == "delete" or case.values[0] != "timeout-after-service"
]


def deletion_fault_rules(rule_id, phase, fault, hit_limit, inject):
    rule = creation_fault_rule(rule_id, fault, hit_limit, inject)
    if phase == "metadata":
        rule["operation_type"] = "MetadataReadContainer"
        return [rule]
    # All must reach DELETE, not an unexpected metadata GET after warming.
    guard = {
        "id": rule_id + "-metadata-guard",
        "operation_type": "MetadataReadContainer",
        "status_code": 500,
        "probability": 1.0,
        "enabled": False,
    }
    return [guard, rule]


def seed_target(container):
    proof = {"id": "proof", "pk": "A", "amount": 42}
    container.create_item(proof)
    return container.read(), proof


def assert_stored_target(database_id, container_id, properties, proof, *, exists):
    """Use a separate runtime without fault rules or the deleting client's cache."""
    with create_fault_setup_client(
        os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"]
    ) as observer:
        container = observer.get_database_client(database_id).get_container_client(
            container_id
        )
        if exists:
            stored = container.read()
            for field in ("_rid", "_etag", "partitionKey"):
                assert stored[field] == properties[field]
            item = container.read_item(proof["id"], partition_key=proof["pk"])
            assert {key: item[key] for key in proof} == proof
        else:
            with pytest.raises(exceptions.CosmosResourceNotFoundError) as absent:
                container.read()
            assert absent.value.status_code == 404
            with pytest.raises(exceptions.CosmosResourceNotFoundError) as absent:
                container.read_item(proof["id"], partition_key=proof["pk"])
            assert absent.value.status_code == 404


def assert_deletion_outcome(
    *, fault, inject, retry_limit, hit_limit, error, returned, hooks, elapsed, hits
):
    if inject and fault != "throttle":
        assert isinstance(error, exceptions.CosmosClientTimeoutError)
        assert MIN_TIMEOUT_ELAPSED <= elapsed <= MAX_OPERATION_ELAPSED
        if fault == "timeout-after-service":
            # Cancellation can precede recording the delayed response's hit.
            # The independent observer, not this counter, establishes deletion.
            assert hits <= 1
        else:
            assert hits == 1
    elif inject and hit_limit is None:
        assert_throttle_failure(error, elapsed, hits, retry_limit)
    else:
        assert error is None, "Container deletion did not succeed"
        assert hits == (hit_limit if inject else 0)
        assert math.isfinite(elapsed) and 0 <= elapsed < (
            30 if fault == "throttle" else MAX_OPERATION_ELAPSED
        )
        assert returned is None
        assert len(hooks) == 1
        headers, body = hooks[0]
        assert headers["x-ms-activity-id"]
        assert body is None
        return
    assert returned is None
    assert not hooks
