# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Offline contracts for the shared Rust fault-rule adapters used by service tests."""

import pytest
from azure.core.exceptions import ServiceResponseError

from azure.cosmos.documents import _OperationType as OperationType
from azure.cosmos.exceptions import CosmosHttpResponseError
from common.fault_rule_adapters import FaultInjectionTransport, _RegionFaultRules


@pytest.mark.parametrize(
    "error, outcome",
    [
        (CosmosHttpResponseError(status_code=503), {"status_code": 503}),
        ("region_down", {"error_type": "ConnectionError"}),
        (ServiceResponseError("injected"), {"error_type": "ResponseTimeout"}),
    ],
)
@pytest.mark.parametrize("region", ["West US", "", None])
def test_document_fault_rules_preserve_outcome_and_region_rust(error, outcome, region):
    adapter = _RegionFaultRules(error, region)
    rules = adapter.rules()
    assert [{key: value for key, value in rule.items() if key != "id"} for rule in rules] == [
        {"operation_type": operation, "region": region or None, **outcome}
        for operation in (
            "ReadItem",
            "QueryItem",
            "ChangeFeedItem",
            "CreateItem",
            "UpsertItem",
            "ReplaceItem",
            "DeleteItem",
            "BatchItem",
        )
    ]
    batches = [rules, adapter.faults, _RegionFaultRules(error, region).rules()]
    ids = [rule["id"] for batch in batches for rule in batch]
    assert len(set(ids)) == len(ids)
    rules[0]["region"] = "changed"
    assert all(rule["region"] == (region or None) for rule in adapter.faults)


@pytest.mark.parametrize("mutation", ["remove", "add"])
def test_document_live_rule_mutation_keeps_driver_gap_skip_rust(mutation):
    adapter = _RegionFaultRules("region_down", "West US")
    verb = "removed from" if mutation == "remove" else "added to"
    with pytest.raises(pytest.skip.Exception) as caught:
        if mutation == "remove":
            adapter.faults = []
        else:
            adapter.add_fault(lambda request: True, "region_down")
    assert str(caught.value) == (
        f"driver-gap: fault rules cannot be {verb} a client after it is created."
    )
    assert all(rule["error_type"] == "ConnectionError" for rule in adapter.rules())


@pytest.mark.parametrize(
    "operation, expected",
    [
        (OperationType.Read, ["ReadItem"]),
        (OperationType.SqlQuery, ["QueryItem"]),
        (OperationType.ReadFeed, ["QueryItem", "ChangeFeedItem"]),
        (OperationType.Create, ["CreateItem"]),
        (OperationType.Upsert, ["UpsertItem"]),
        (OperationType.Replace, ["ReplaceItem"]),
        (OperationType.Delete, ["DeleteItem"]),
        (OperationType.Patch, ["PatchItem"]),
        (OperationType.Batch, ["BatchItem"]),
    ],
)
def test_availability_predicates_are_probed_once_and_preserve_rule_fields_rust(operation, expected):
    adapter = FaultInjectionTransport()
    calls = []

    def predicate(request):
        calls.append(("predicate", request))
        return (
            adapter.predicate_is_document_operation(request)
            and adapter.predicate_is_operation_type(request, operation)
            and adapter.predicate_targets_region(request, "https://west.example")
        )

    def error(request):
        calls.append(("error", request))
        return adapter.error_after_delay(125, CosmosHttpResponseError(status_code=503, sub_status=1002))

    adapter.add_fault(predicate, error)
    rules = adapter.rules({"https://west.example": "West US"})
    assert [rule["operation_type"] for rule in rules] == expected
    assert [{key: value for key, value in rule.items() if key != "id"} for rule in rules] == [
        {"operation_type": op, "region": "West US", "delay_ms": 125, "status_code": 503, "sub_status": 1002}
        for op in expected
    ]
    adapter.rules({"https://west.example": "West US"})
    assert [call[0] for call in calls] == ["predicate", "error"]
    assert calls[0][1] is calls[1][1]


def _add_read_fault(adapter, error, uri="https://west.example"):
    adapter.add_fault(
        lambda request: (
            adapter.predicate_is_operation_type(request, OperationType.Read)
            and adapter.predicate_targets_region(request, uri)
        ),
        lambda request: adapter.error_after_delay(0, error),
    )


def test_availability_faults_and_ids_are_isolated_between_instances_and_calls_rust():
    adapter = FaultInjectionTransport()
    other = FaultInjectionTransport()
    _add_read_fault(adapter, ServiceResponseError("injected"))
    _add_read_fault(adapter, CosmosHttpResponseError(status_code=429), "https://east.example")
    regions = {"https://west.example": "West US", "https://east.example": "East US"}
    rules = adapter.rules(regions)
    assert [{key: value for key, value in rule.items() if key != "id"} for rule in rules] == [
        {"operation_type": "ReadItem", "region": "West US", "delay_ms": 0, "error_type": "ResponseTimeout"},
        {"operation_type": "ReadItem", "region": "East US", "delay_ms": 0, "status_code": 429, "sub_status": 0},
    ]
    assert other.rules(regions) == []
    _add_read_fault(other, CosmosHttpResponseError(status_code=500))
    repeated = adapter.rules(regions) + other.rules(regions)
    ids = [rule["id"] for rule in rules + repeated]
    assert len(set(ids)) == len(ids)
    adapter.faults.clear()
    assert adapter.rules(regions) == []
    assert len(rules) == 2
    assert len(other.rules(regions)) == 1


def test_availability_unsupported_error_and_missing_region_do_not_silently_drop_faults_rust():
    adapter = FaultInjectionTransport()
    _add_read_fault(adapter, ValueError("unsupported"))
    with pytest.raises(TypeError, match="unsupported injected error"):
        adapter.rules({"https://west.example": "West US"})
    adapter.faults.clear()
    _add_read_fault(adapter, CosmosHttpResponseError(status_code=503))
    with pytest.raises(KeyError, match="https://west.example"):
        adapter.rules({})


def test_availability_topology_transformation_keeps_driver_gap_skip_rust():
    adapter = FaultInjectionTransport()
    predicate = adapter.predicate_is_database_account_call
    transformation = adapter.transform_topology_ppaf_enabled
    adapter.add_response_transformation(predicate, transformation)
    assert adapter.response_transformations == [(predicate, transformation)]
    assert FaultInjectionTransport().response_transformations == []
    with pytest.raises(pytest.skip.Exception) as caught:
        adapter.response_transformations[0][1]({})
    assert str(caught.value) == (
        "driver-gap: fault rules cannot change the account details the client reads, so these tests "
        "cannot turn on per-partition automatic failover (PPAF)."
    )
