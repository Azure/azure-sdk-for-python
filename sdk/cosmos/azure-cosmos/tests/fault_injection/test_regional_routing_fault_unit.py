# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Offline guards for F02; these do not establish regional execution."""
import copy
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from azure.core.exceptions import ServiceResponseError
from azure.cosmos import exceptions
from azure.cosmos._backend.client_config import _prepare_fault_injection_rules
from fault_injection import _regional_routing
from fault_injection._regional_routing import (
    REGIONAL_ROUTING_CASES, assert_destination, assert_fields, assert_guard,
    emulator_endpoints, native_records, rules, topology,
)


@pytest.mark.parametrize("exit_code", [1, 2])
def test_worker_failure_preserves_child_output_in_assertion_rust(monkeypatch, exit_code):
    node_name = "test_swr_mrr_succeeds_rust[guard-rust]"
    request = SimpleNamespace(
        config=SimpleNamespace(getoption=lambda option: False),
        node=SimpleNamespace(path=Path(__file__).resolve(), name=node_name),
    )
    run = Mock(return_value=SimpleNamespace(
        returncode=exit_code,
        stdout="FAILED: child operation assertion",
        stderr="Traceback: child setup exception",
    ))
    monkeypatch.setattr(_regional_routing.subprocess, "run", run)
    with pytest.raises(AssertionError) as failure:
        _regional_routing.isolate(request, ("fault_create_test", SimpleNamespace(id="orders_test")))
    message = str(failure.value)
    assert f"Isolated F02 worker failed with exit {exit_code}" in message
    assert node_name in message
    assert "--- worker stdout ---\nFAILED: child operation assertion" in message
    assert "--- worker stderr ---\nTraceback: child setup exception" in message
    run.assert_called_once()


def test_worker_success_and_child_branch_remain_unchanged_rust(monkeypatch):
    run = Mock(return_value=SimpleNamespace(returncode=0, stdout="", stderr=""))
    monkeypatch.setattr(_regional_routing.subprocess, "run", run)
    request = SimpleNamespace(
        config=SimpleNamespace(getoption=lambda option: False),
        node=SimpleNamespace(path=Path(__file__).resolve(), name="test_worker"),
    )
    target = ("fault_create_test", SimpleNamespace(id="orders_test"))
    assert _regional_routing.isolate(request, target) is True
    run.assert_called_once()
    run.reset_mock()
    request.config.getoption = lambda option: True
    assert _regional_routing.isolate(request, target) is False
    run.assert_not_called()


def test_regional_cases_only_select_enabled_rust_scenarios_rust():
    assert [(case.values, case.id) for case in REGIONAL_ROUTING_CASES] == [
        (("routing",), "routing-rust"),
        (("guard",), "guard-rust"),
        (("guard-disabled",), "guard-disabled-rust"),
    ]
    assert all(not case.marks for case in REGIONAL_ROUTING_CASES)


@pytest.mark.parametrize("endpoint", [
    "", "https://account.documents.azure.com/", "http://localhost:8081/",
    "https://localhost.example/", "https://user:password@localhost:8081/",
    "https://localhost:8081/dbs", "https://localhost:8081/?x=1", "https://localhost:8081/#x",
])
def test_f02_rejects_non_emulator_endpoint_before_provisioning_rust(endpoint):
    with pytest.raises(ValueError, match="F02 requires"):
        emulator_endpoints(endpoint)


@pytest.mark.parametrize("host", ["localhost", "127.0.0.1"])
def test_f02_uses_two_aliases_on_the_configured_emulator_port_rust(host):
    assert emulator_endpoints(f"https://{host}:8181/") == (
        "https://127.0.0.1:8181/", "https://localhost:8181/")


@pytest.mark.parametrize("guard", [False, True])
def test_topology_preserves_account_fields_without_mutating_the_source_rust(guard):
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
def test_rule_body_and_write_forbidden_contract_survive_preparation_rust(inject):
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
def test_response_body_requires_immutable_bytes_rust(body):
    rule = rules("guard", "orders", {})[0]
    rule["response_body"] = body
    with pytest.raises(ValueError, match="response_body"):
        _prepare_fault_injection_rules([rule])


def test_transport_error_cannot_carry_an_http_response_body_rust():
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
def test_final_success_cannot_hide_wrong_or_missing_attempt_evidence_rust(records):
    with pytest.raises(AssertionError):
        assert_destination(records, "https://localhost:8081/", 200)


def payload():
    return {"activity_id": "operation-id", "request_count": 1, "retained_request_count": 1,
            "requests": [{"pipeline": "data_plane", "endpoint": "https://localhost:8081/",
                          "status": 403, "sub_status": 3,
                          "evaluations": [{"rule_id": "guard", "applied": True}]}]}


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("operation", ["create_item", "read_item"])
@pytest.mark.parametrize("fails", [False, True])
async def test_attempt_capture_excludes_independent_rust_verification_rust(
    monkeypatch, asynchronous, operation, fails,
):
    if asynchronous:
        from azure.cosmos.aio._backend import binding_adapter as module
    else:
        from azure.cosmos._backend import binding_adapter as module

    class TransportError(Exception):
        pass

    error = TransportError("controlled transport failure")
    error._cosmos_fault_diagnostics = payload()
    measured_handle, verification_handle = object(), object()
    response = object()

    def execute(handle, request, **kwargs):
        if fails:
            raise error
        return (response, payload()) if kwargs.get("include_fault_diagnostics") else response

    binding = (AsyncMock if asynchronous else Mock)(side_effect=execute)
    monkeypatch.setattr(module, "_binding_function_for_op", Mock(return_value=binding))
    monkeypatch.setattr(module, "_DRIVER_TRANSPORT_ERROR", TransportError)
    records = []
    _regional_routing.capture_native(
        monkeypatch, records, asynchronous, driver_handle=measured_handle,
    )
    selected = module._binding_function_for_op(operation)

    async def call(handle):
        if asynchronous:
            return await selected(handle, "request")
        return selected(handle, "request")

    for handle in (verification_handle, measured_handle):
        if fails:
            with pytest.raises(TransportError) as caught:
                await call(handle)
            assert caught.value is error
        else:
            assert await call(handle) is response
        if handle is verification_handle:
            assert records == []
            assert binding.call_args.kwargs == {}
        else:
            assert records == payload()["requests"]
            assert binding.call_args.kwargs == {"include_fault_diagnostics": True}
    assert module._binding_function_for_op("patch_item") is binding


@pytest.mark.parametrize("change", [
    {"activity_id": None}, {"request_count": 2}, {"retained_request_count": 0}, {"requests": []},
    {"requests": [{"pipeline": "metadata"}]},
])
def test_missing_truncated_or_metadata_only_diagnostics_fail_rust(change):
    with pytest.raises(AssertionError):
        native_records({**payload(), **change})


def test_guard_requires_rejection_named_application_and_matching_destination_rust():
    error = exceptions.CosmosHttpResponseError(403, message="guard", sub_status=3)
    records = native_records(payload())
    assert_guard(error, records, "https://localhost:8081/", 1, "guard")
    for error_value, hits, name in [(None, 1, "guard"), (error, 0, "guard"), (error, 1, "other")]:
        with pytest.raises(AssertionError):
            assert_guard(error_value, records, "https://localhost:8081/", hits, name)


def test_write_forbidden_exhaustion_is_not_silently_accepted_as_403_rust():
    with pytest.raises(AssertionError, match="Guard did not reject"):
        assert_guard(ServiceResponseError("503/20311"), native_records(payload()),
                     "https://localhost:8081/", 1, "guard")


@pytest.mark.parametrize("actual", [None, {}, {"id": "wrong"}, {"id": "order", "total": 0}])
def test_correct_region_does_not_replace_customer_field_checks_rust(actual):
    with pytest.raises(AssertionError):
        assert_fields(actual, {"id": "order", "total": 125.5})
