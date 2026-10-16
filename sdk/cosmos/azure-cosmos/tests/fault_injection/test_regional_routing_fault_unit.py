# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Offline guards for F02; these do not establish regional execution."""
import copy
import json

import pytest

from azure.core.exceptions import ServiceResponseError
from azure.cosmos import exceptions
from azure.cosmos._backend.client_config import _prepare_fault_injection_rules
from fault_injection._regional_routing import (
    assert_destination, assert_fields, assert_guard, emulator_endpoints, native_records, rules, topology,
)


@pytest.mark.parametrize("endpoint", [
    "", "https://account.documents.azure.com/", "http://localhost:8081/",
    "https://localhost.example/", "https://user:password@localhost:8081/",
    "https://localhost:8081/dbs", "https://localhost:8081/?x=1", "https://localhost:8081/#x",
])
def test_f02_rejects_non_emulator_endpoint_before_provisioning(endpoint):
    with pytest.raises(ValueError, match="F02 requires"):
        emulator_endpoints(endpoint)


@pytest.mark.parametrize("host", ["localhost", "127.0.0.1"])
def test_f02_uses_two_aliases_on_the_configured_emulator_port(host):
    assert emulator_endpoints(f"https://{host}:8181/") == (
        "https://127.0.0.1:8181/", "https://localhost:8181/")


@pytest.mark.parametrize("guard", [False, True])
def test_topology_preserves_account_fields_without_mutating_the_source(guard):
    original = {"id": "test", "consistencyPolicy": {"defaultConsistencyLevel": "Session"},
                "thinClientReadableLocations": [{"name": "old"}]}
    before = copy.deepcopy(original)
    result = topology(original, "https://127.0.0.1:8081/", "https://localhost:8081/", guard)
    assert original == before
    assert result["consistencyPolicy"] == original["consistencyPolicy"]
    assert result["writableLocations"][0]["name"] == ("West US" if guard else "East US")
    assert [region["name"] for region in result["readableLocations"]] == ["East US", "West US"]
    assert result["enableMultipleWriteLocations"] is False
    assert "thinClientReadableLocations" not in result
    result["consistencyPolicy"]["defaultConsistencyLevel"] = "Eventual"
    assert original == before


@pytest.mark.parametrize("inject", [True, False])
def test_rule_body_and_write_forbidden_contract_survive_preparation(inject):
    configured = rules("guard", "orders", {"id": "account"}, inject)
    metadata, guard = _prepare_fault_injection_rules(configured)
    assert metadata.operation_type == "MetadataReadDatabaseAccount"
    assert metadata.status_code == 200
    assert json.loads(metadata.response_body) == {"id": "account"}
    assert metadata.probability == 1.0
    assert guard.operation_type == "CreateItem"
    assert (guard.status_code, guard.sub_status, guard.region) == (403, 3, "West US")
    assert guard.container_id == "orders"
    assert guard.probability == (1.0 if inject else 0.0)
    assert guard.hit_limit is None


@pytest.mark.parametrize("body", [None, "", {}, [], bytearray(b"{}"), True])
def test_response_body_requires_immutable_bytes(body):
    rule = rules("guard", "orders", {})[0]
    rule["response_body"] = body
    with pytest.raises(ValueError, match="response_body"):
        _prepare_fault_injection_rules([rule])


def test_transport_error_cannot_carry_an_http_response_body():
    with pytest.raises(ValueError, match="response_body"):
        _prepare_fault_injection_rules([{
            "id": "bad", "operation_type": "ReadItem",
            "error_type": "ConnectionError", "response_body": b"{}",
        }])


@pytest.mark.parametrize("records", [
    [], [{"endpoint": "https://127.0.0.1:8081/", "status": 200}],
    [{"endpoint": "https://localhost:8181/", "status": 200}],
    [{"endpoint": "https://localhost:8081/", "status": 429}],
    [{"endpoint": "https://127.0.0.1:8081/", "status": 403},
     {"endpoint": "https://localhost:8081/", "status": 200}],
])
def test_final_success_cannot_hide_wrong_or_missing_attempt_evidence(records):
    with pytest.raises(AssertionError):
        assert_destination(records, "https://localhost:8081/", 200)


def payload():
    return {"activity_id": "operation-id", "request_count": 1, "retained_request_count": 1,
            "requests": [{"pipeline": "data_plane", "endpoint": "https://localhost:8081/",
                          "status": 403, "sub_status": 3,
                          "evaluations": [{"rule_id": "guard", "applied": True}]}]}


@pytest.mark.parametrize("change", [
    {"activity_id": None}, {"request_count": 2}, {"retained_request_count": 0}, {"requests": []},
    {"requests": [{"pipeline": "metadata"}]},
])
def test_missing_truncated_or_metadata_only_diagnostics_fail(change):
    with pytest.raises(AssertionError):
        native_records({**payload(), **change})


def test_guard_requires_rejection_named_application_and_matching_destination():
    error = exceptions.CosmosHttpResponseError(403, message="guard", sub_status=3)
    records = native_records(payload())
    assert_guard(error, records, "https://localhost:8081/", 1, "guard", "rust")
    for error_value, hits, name in [(None, 1, "guard"), (error, 0, "guard"), (error, 1, "other")]:
        with pytest.raises(AssertionError):
            assert_guard(error_value, records, "https://localhost:8081/", hits, name, "rust")


def test_write_forbidden_exhaustion_is_not_silently_accepted_as_403():
    with pytest.raises(AssertionError, match="Guard did not reject"):
        assert_guard(ServiceResponseError("503/20311"), native_records(payload()),
                     "https://localhost:8081/", 1, "guard", "rust")


@pytest.mark.parametrize("actual", [None, {}, {"id": "wrong"}, {"id": "order", "total": 0}])
def test_correct_region_does_not_replace_customer_field_checks(actual):
    with pytest.raises(AssertionError):
        assert_fields(actual, {"id": "order", "total": 125.5})
