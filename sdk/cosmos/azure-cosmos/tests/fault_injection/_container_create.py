# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Container creation faults before sending and after a successful service response."""

import math
import os

import pytest

from azure.cosmos import exceptions
from config.clients import create_fault_setup_client
from fault_injection._throttle_retry import assert_throttle_failure

OPERATION_TIMEOUT = 10.0
DELAY_MS = 30000
MAX_OPERATION_ELAPSED = OPERATION_TIMEOUT + 2.0
MIN_TIMEOUT_ELAPSED = OPERATION_TIMEOUT - 0.1

CREATE_FAULT_CASES = [
    pytest.param("throttle", 0, None, True, id="429-no-retries"),
    pytest.param("throttle", 2, None, True, id="429-exhausted"),
    pytest.param("throttle", 2, 1, True, id="429-recovered"),
    pytest.param("throttle", 2, None, False, id="429-control"),
    pytest.param("timeout", 0, None, True, id="deadline-expired"),
    pytest.param("timeout-after-service", 0, 1, True, id="deadline-after-commit"),
    pytest.param("timeout", 0, None, False, id="deadline-control"),
]


def creation_fault_rule(rule_id, fault, hit_limit, inject):
    # No CreateContainer selector exists. Arm All only for creation on a
    # warmed, dedicated client; the independent observer has no fault rules.
    rule = {
        "id": rule_id,
        "operation_type": "All",
        "delay_ms": 0 if fault == "throttle" else DELAY_MS,
        "probability": 1.0 if inject else 0.0,
        "hit_limit": hit_limit,
        "enabled": False,
    }
    if fault == "timeout-after-service":
        rule["error_type"] = "ResponseTimeoutAfterService"
    else:
        rule["status_code"] = 429 if fault == "throttle" else 503
        rule["response_headers"] = {"x-ms-retry-after-ms": "100"}
    return rule


def assert_stored_container(database_id, container_id, *, exists):
    """Read through another Rust client, never through the faulted client's cache."""
    with create_fault_setup_client(
        os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"]
    ) as observer:
        container = observer.get_database_client(database_id).get_container_client(
            container_id
        )
        if not exists:
            with pytest.raises(exceptions.CosmosResourceNotFoundError) as absent:
                container.read()
            assert absent.value.status_code == 404
            return None
        properties = container.read()
        assert properties["id"] == container_id
        assert properties["partitionKey"]["paths"] == ["/pk"]
        assert properties["defaultTtl"] == 90
        return properties


def assert_creation_outcome(
    *,
    fault,
    inject,
    retry_limit,
    hit_limit,
    error,
    returned,
    hooks,
    elapsed,
    hits,
    stored,
    return_properties,
    existing_properties=None,
):
    if existing_properties is not None:
        assert stored == existing_properties, "An existing container must not change"
    if inject and fault != "throttle":
        assert isinstance(error, exceptions.CosmosClientTimeoutError)
        assert MIN_TIMEOUT_ELAPSED <= elapsed <= MAX_OPERATION_ELAPSED
        if fault == "timeout-after-service":
            # The post-service delay may be cancelled before its hit is counted.
            # Independently read properties establish persistence, not the counter.
            assert hits <= 1
            assert stored is not None
        else:
            assert hits == 1, "The delayed attempt must expire without a second attempt"
    elif inject and hit_limit is None:
        assert_throttle_failure(error, elapsed, hits, retry_limit)
    else:
        assert error is None, "Container creation did not succeed"
        assert hits == (hit_limit if inject else 0)
        assert math.isfinite(elapsed) and 0 <= elapsed < (
            MAX_OPERATION_ELAPSED if fault != "throttle" else 30
        )
        proxy, properties = returned if return_properties else (returned, None)
        assert proxy.id == stored["id"]
        assert len(hooks) == 1
        for result in ([properties] if return_properties else []) + [hooks[0][1]]:
            for field in ("id", "_rid", "partitionKey", "defaultTtl"):
                assert result[field] == stored[field]
        return
    assert returned is None and not hooks
    if fault != "timeout-after-service" and existing_properties is None:
        assert (
            stored is None
        ), "A synthetic pre-send failure must not create a container"
