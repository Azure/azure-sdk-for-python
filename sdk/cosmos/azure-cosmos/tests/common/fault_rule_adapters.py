# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Helpers that turn the fault scenarios used by the tests into fault rules passed to the client when it is created."""

import uuid

import pytest
from azure.core.exceptions import ServiceResponseError

from azure.cosmos.documents import _OperationType as OperationType
from azure.cosmos.exceptions import CosmosHttpResponseError

#: The item operations that _RegionFaultRules adds a fault for.
_DOCUMENT_OPERATION_TYPES = (
    "ReadItem",
    "QueryItem",
    "ChangeFeedItem",
    "CreateItem",
    "UpsertItem",
    "ReplaceItem",
    "DeleteItem",
    "BatchItem",
)
#: Pass this instead of an error to make the whole region unreachable (a connection error).
_REGION_DOWN = "region_down"

_PPAF_SKIP_REASON = (
    "driver-gap: fault rules cannot change the account details the client reads, so these tests "
    "cannot turn on per-partition automatic failover (PPAF)."
)

#: Fault rule operation names for each operation type the tests use.
# Patch has its own PatchItem rule. read_all_items is sent as a query.
_FAULT_RULE_OPERATIONS = {
    OperationType.Read: ("ReadItem",),
    OperationType.SqlQuery: ("QueryItem",),
    OperationType.ReadFeed: ("QueryItem", "ChangeFeedItem"),
    OperationType.Create: ("CreateItem",),
    OperationType.Upsert: ("UpsertItem",),
    OperationType.Replace: ("ReplaceItem",),
    OperationType.Delete: ("DeleteItem",),
    OperationType.Patch: ("PatchItem",),
    OperationType.Batch: ("BatchItem",),
}


class _RegionFaultRules(object):
    """Builds fault rules that make every item operation in one region fail with the same error.

    The rules are passed to the client when it is created and cannot be changed afterwards,
    so tests that remove or add faults on a running client are skipped.
    """

    def __init__(self, error, region):
        self.error = error
        self.region = region or None

    def rules(self):
        """Returns one fault rule per item operation, using the stored error and region."""
        suffix = uuid.uuid4().hex
        if isinstance(self.error, CosmosHttpResponseError):
            fault = {"status_code": self.error.status_code}
        elif self.error == _REGION_DOWN:
            fault = {"error_type": "ConnectionError"}
        else:
            fault = {"error_type": "ResponseTimeout"}
        return [
            dict(id="{}-{}".format(op, suffix), operation_type=op, region=self.region, **fault)
            for op in _DOCUMENT_OPERATION_TYPES
        ]

    @property
    def faults(self):
        return self.rules()

    @faults.setter
    def faults(self, value):
        pytest.skip("driver-gap: fault rules cannot be removed from a client after it is created.")

    def add_fault(self, predicate, error):
        pytest.skip("driver-gap: fault rules cannot be added to a client after it is created.")


class FaultInjectionTransport(object):
    """Keeps the method names of the original fault injection transport so the tests read the same.

    Tests still call add_fault with a predicate and an error. Each predicate is run once against
    a fake request to record the operation type and target region. rules() then turns the
    recorded faults into fault rules passed to the client when it is created.
    """

    class _FakeRequest(object):
        def __init__(self):
            self.operation_type = None
            self.target_uri = None

    class _DelayedError(object):
        def __init__(self, delay_ms, error):
            self.delay_ms = delay_ms
            self.error = error

    def __init__(self):
        self.faults = []
        self.response_transformations = []

    def add_fault(self, predicate, error_lambda):
        probe = self._FakeRequest()
        predicate(probe)
        self.faults.append((probe, error_lambda(probe)))

    def add_response_transformation(self, predicate, transformation):
        self.response_transformations.append((predicate, transformation))

    @staticmethod
    def predicate_is_document_operation(r):
        return True

    @staticmethod
    def predicate_is_operation_type(r, operation_type):
        r.operation_type = operation_type
        return True

    @staticmethod
    def predicate_targets_region(r, uri):
        r.target_uri = uri
        return True

    @staticmethod
    def predicate_is_database_account_call(r):
        return True

    @staticmethod
    def error_after_delay(delay_ms, error):
        return FaultInjectionTransport._DelayedError(delay_ms, error)

    @staticmethod
    def transform_topology_ppaf_enabled(inner):
        pytest.skip(_PPAF_SKIP_REASON)

    def rules(self, region_by_uri):
        """Returns one fault rule per recorded fault and operation.

        region_by_uri maps each endpoint URL used in the tests to its region name.
        """
        rules = []
        suffix = uuid.uuid4().hex
        for index, (probe, fault) in enumerate(self.faults):
            if isinstance(fault.error, CosmosHttpResponseError):
                outcome = {"status_code": fault.error.status_code, "sub_status": fault.error.sub_status or 0}
            elif isinstance(fault.error, ServiceResponseError):
                # An error with no HTTP status code becomes a response timeout.
                outcome = {"error_type": "ResponseTimeout"}
            else:
                raise TypeError("unsupported injected error {!r}".format(fault.error))
            for operation_type in _FAULT_RULE_OPERATIONS[probe.operation_type]:
                rules.append(
                    dict(
                        id="{}-{}-{}".format(operation_type, index, suffix),
                        operation_type=operation_type,
                        region=region_by_uri[probe.target_uri],
                        delay_ms=fault.delay_ms,
                        **outcome
                    )
                )
        return rules
