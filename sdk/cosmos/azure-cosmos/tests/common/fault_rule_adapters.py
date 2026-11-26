# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Test-only adapters from legacy fault scenarios to Rust fault-rule mappings."""

import uuid

import pytest
from azure.core.exceptions import ServiceResponseError

from azure.cosmos.documents import _OperationType as OperationType
from azure.cosmos.exceptions import CosmosHttpResponseError

#: Rust driver labels for the document operations the original transport predicate matched.
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
_REGION_DOWN = "region_down"

_GAP_10_PPAF_SKIP = (
    "driver-gap: Rust fault injection cannot transform the database-account response to enable "
    "PPAF (known gap 10: custom transports are excluded)."
)

#: Rust fault-rule labels for the legacy operation types the transport predicates matched.
# The retry-safe patch scenario runs server-side (PatchItem); read_all_items is a Rust query.
_RUST_OPERATION_TYPES = {
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


class _RustFaultInjection(object):
    """Rust stand-in for FaultInjectionTransport with one region-targeted document fault.

    Known gap 10: Closed by design: client-level proxy configuration, custom CA, client certificate, and transport
    options are excluded. Faults become Rust
    ``_fault_injection_rules`` fixed when the client is built, so the original's later
    ``faults = []`` / ``add_fault`` on the live client cannot change that client's rules.
    """

    def __init__(self, error, region):
        self.error = error
        self.region = region or None

    def rules(self):
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
        pytest.skip("driver-gap: Rust fault injection rules cannot be removed from a live client (known gap 10).")

    def add_fault(self, predicate, error):
        pytest.skip("driver-gap: Rust fault injection rules cannot be added to a live client (known gap 10).")


class FaultInjectionTransport(object):
    """Rust stand-in for the legacy FaultInjectionTransport.

    Known gap 10: Closed by design: client-level proxy configuration, custom CA, client certificate, and transport
    options are excluded. The predicate and error lambdas
    are evaluated once against a probe to record the operation type, target region, delay and error, which
    become Rust ``_fault_injection_rules`` fixed when the client is built.
    """

    class _Probe(object):
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
        probe = self._Probe()
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
        pytest.skip(_GAP_10_PPAF_SKIP)

    def rules(self, region_by_uri):
        rules = []
        suffix = uuid.uuid4().hex
        for index, (probe, fault) in enumerate(self.faults):
            if isinstance(fault.error, CosmosHttpResponseError):
                outcome = {"status_code": fault.error.status_code, "sub_status": fault.error.sub_status or 0}
            elif isinstance(fault.error, ServiceResponseError):
                # A failed response without an HTTP status maps to Rust's transport-level response failure.
                outcome = {"error_type": "ResponseTimeout"}
            else:
                raise TypeError("unsupported injected error {!r}".format(fault.error))
            for operation_type in _RUST_OPERATION_TYPES[probe.operation_type]:
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
