# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Shared assertions for the copied delayed-create scenario and its control."""
import json
import math

from azure.cosmos.exceptions import CosmosHttpResponseError

DELAY_MS = 10000
OPERATION_TIMEOUT = 90


def create_rule(rule_id, container_id, inject):
    return {
        "id": rule_id,  # Identifies the rule whose application count we inspect.
        "operation_type": "CreateItem",  # Do not inject faults into setup, metadata, or independent reads.
        "container_id": container_id,  # URL-substring match; use a unique owned container.
        "status_code": 502,  # Fabricated failure returned instead of sending the write.
        "delay_ms": DELAY_MS,  # Delay each affected attempt by ten seconds.
        "probability": 1.0 if inject else 0.0,  # The control never applies the rule or its delay.
        "hit_limit": None,  # Keep failing retries; this is not a transient-recovery test.
    }


def assert_failure(error, elapsed, hits):
    assert isinstance(error, CosmosHttpResponseError), "Expected a Cosmos HTTP failure, not success"
    assert error.status_code == 502, "Expected the injected 502"
    assert math.isfinite(elapsed) and elapsed > DELAY_MS / 1000, "Injected delay was not preserved"
    assert hits > 0, "The intended fault did not apply"


def assert_control(returned, stored, item, hits):
    assert hits == 0, "The no-injection control applied a fault"
    for result in (returned, stored):
        assert isinstance(result, dict), "Expected an item response"
        assert {field: result[field] for field in item} == item, "Customer fields changed"


def assert_route(before, after, backend):
    assert after[0] - before[0] == (1 if backend == "rust" else 0), "Wrong binding operation count"
    assert after[1] == before[1], "The Rust operation fell back to Python"


def emit(kind, **fields):
    print("FAULT_EVIDENCE " + json.dumps({"kind": kind, **fields}, sort_keys=True), flush=True)
