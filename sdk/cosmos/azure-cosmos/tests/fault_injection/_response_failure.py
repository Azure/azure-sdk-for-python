# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""F11 point-read response failure, distinct from F12's operation deadline.

Select the ServiceResponseError contract from the paired service_retry_policies
tests. This does not claim their multi-region retry-count or write coverage.
"""
import math

from azure.core.exceptions import ServiceResponseError

OPERATION_TIMEOUT = 30.0  # Leave room for normal retries; expiry must not satisfy this test.


def response_failure_rule(rule_id, container_id, inject):
    return {
        "id": rule_id,  # Identify the rule whose application count we inspect.
        "operation_type": "ReadItem",  # Leave setup and metadata requests unaffected.
        "container_id": container_id,  # Match only the unique test-owned container.
        "error_type": "ResponseTimeout",  # Transport failure, not an HTTP response or operation deadline.
        "delay_ms": 0,  # Do not manufacture an expired operation budget with a delay.
        "probability": 1.0 if inject else 0.0,  # Fresh-client control never applies the fault.
        "hit_limit": None,  # Do not let retries escape by exhausting the rule.
    }


def assert_response_failure(error, elapsed, hits):
    assert isinstance(error, ServiceResponseError), "Expected ServiceResponseError, not success or another error"
    assert hits > 0, "The intended ReadItem response fault did not apply"
    assert (
        math.isfinite(elapsed) and 0 <= elapsed < OPERATION_TIMEOUT
    ), "Response failure must surface before the operation budget expires"
