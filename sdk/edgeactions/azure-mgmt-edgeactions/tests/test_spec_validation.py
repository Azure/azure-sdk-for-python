# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
from copy import deepcopy
import json

import pytest

import spec_validation
from spec_validation import response_spec

VERSION_URL = (
    "https://management.azure.com/subscriptions/00000000-0000-0000-0000-000000000000"
    "/resourceGroups/rg/providers/Microsoft.Cdn/edgeActions/action/versions/v1?api-version=2026-10-01"
)
RESULT_URL = "https://management.azure.com/operationresults/test?api-version=2026-10-01"
VERSION_BODY = {
    "id": VERSION_URL.split("?")[0].removeprefix("https://management.azure.com"),
    "name": "v1",
    "type": "Microsoft.Cdn/edgeActions/versions",
    "location": "global",
    "properties": {
        "deploymentType": "file",
        "isDefaultVersion": "True",
        "provisioningState": "Succeeded",
        "validationStatus": "Succeeded",
    },
}


def action_url(action):
    return VERSION_URL.replace("?api-version", f"/{action}?api-version")


@pytest.mark.parametrize(
    "method,url,status,body",
    [
        ("GET", VERSION_URL, 200, VERSION_BODY),
        ("POST", action_url("deployVersionCode"), 200, VERSION_BODY),
        ("POST", action_url("deployVersionCode"), 202, None),
        ("POST", action_url("getVersionCode"), 200, {"name": "v1", "content": "aGVsbG8="}),
        ("POST", action_url("swapDefault"), 204, None),
        ("DELETE", VERSION_URL, 200, None),
        ("DELETE", VERSION_URL, 204, None),
    ],
)
def test_documented_response_status_and_body(method, url, status, body):
    spec = response_spec()
    spec.validate_response(spec.operation(method, url), status, body, {})


def test_deployment_final_location_returns_full_version():
    response_spec().validate_location("POST", action_url("deployVersionCode"), RESULT_URL, 200, VERSION_BODY, {})


@pytest.mark.parametrize("status", [200, 201])
def test_explicit_null_status_exception_preserves_response_and_spec(status, caplog):
    spec = response_spec()
    snapshot = deepcopy(spec.snapshot)
    body = deepcopy(VERSION_BODY)
    body["properties"]["validationStatus"] = None
    original = deepcopy(body)
    operation = spec.operation("PUT", VERSION_URL)
    spec.validate_response(operation, status, body, {}, allow_known_null_validation_status=True)
    assert "known version-creation service bug" in caplog.text
    assert body == original
    assert spec.snapshot == snapshot
    with pytest.raises(AssertionError, match="properties.validationStatus violates OpenAPI"):
        spec.validate_response(operation, status, body, {})


@pytest.mark.parametrize(
    "method,url,status",
    [
        ("GET", VERSION_URL, 200),
        ("PATCH", VERSION_URL, 200),
        ("POST", action_url("deployVersionCode"), 200),
        ("DELETE", VERSION_URL, 200),
        ("PUT", VERSION_URL, 202),
        ("PUT", VERSION_URL, 500),
    ],
)
def test_null_status_exception_does_not_relax_other_operations_or_statuses(method, url, status):
    spec = response_spec()
    body = deepcopy(VERSION_BODY)
    body["properties"]["validationStatus"] = None
    with pytest.raises(AssertionError):
        spec.validate_response(spec.operation(method, url), status, body, {}, allow_known_null_validation_status=True)


@pytest.mark.parametrize(
    "field,value",
    [
        ("deploymentType", None),
        ("isDefaultVersion", True),
        ("lastPackageUpdateTime", "not-a-date"),
        ("provisioningState", []),
        ("validationStatus", []),
    ],
)
def test_null_status_exception_keeps_other_property_checks(field, value):
    spec = response_spec()
    body = deepcopy(VERSION_BODY)
    body["properties"]["validationStatus"] = None
    body["properties"][field] = value
    with pytest.raises(AssertionError, match=f"properties.{field} violates OpenAPI"):
        spec.validate_response(
            spec.operation("PUT", VERSION_URL), 201, body, {}, allow_known_null_validation_status=True
        )


def test_null_status_exception_keeps_required_properties():
    spec = response_spec()
    body = deepcopy(VERSION_BODY)
    body["properties"]["validationStatus"] = None
    del body["properties"]["deploymentType"]
    with pytest.raises(AssertionError, match="properties violates OpenAPI required"):
        spec.validate_response(
            spec.operation("PUT", VERSION_URL), 201, body, {}, allow_known_null_validation_status=True
        )


def test_null_status_exception_keeps_header_checks():
    spec = response_spec()
    body = deepcopy(VERSION_BODY)
    body["properties"]["validationStatus"] = None
    with pytest.raises(AssertionError, match="Retry-After must be an integer"):
        spec.validate_response(
            spec.operation("PUT", VERSION_URL),
            201,
            body,
            {"Retry-After": "not-an-integer"},
            allow_known_null_validation_status=True,
        )


def test_version_get_does_not_override_swap_default_final_contract():
    spec = response_spec()
    spec.validate_response(spec.operation("GET", VERSION_URL), 200, VERSION_BODY, {})
    with pytest.raises(AssertionError, match="EdgeActionVersions_SwapDefault: HTTP 200"):
        spec.validate_location("POST", action_url("swapDefault"), VERSION_URL, 200, VERSION_BODY, {})


def test_explicit_swap_exception_preserves_the_pinned_spec(caplog):
    spec = response_spec()
    original = deepcopy(spec.snapshot)
    spec.validate_location(
        "POST",
        action_url("swapDefault"),
        VERSION_URL,
        200,
        VERSION_BODY,
        {},
        allow_known_swap_default_response=True,
    )
    assert "known HTTP-200-with-body service bug" in caplog.text
    assert spec.snapshot == original
    with pytest.raises(AssertionError, match="HTTP 200 is not a documented response"):
        spec.validate_location("POST", action_url("swapDefault"), VERSION_URL, 200, VERSION_BODY, {})


@pytest.mark.parametrize(
    "method,url,status,body",
    [
        ("POST", action_url("swapDefault"), 200, None),
        ("POST", action_url("swapDefault"), 204, VERSION_BODY),
        ("POST", action_url("swapDefault"), 202, None),
        ("POST", action_url("swapDefault"), 500, VERSION_BODY),
        ("DELETE", VERSION_URL, 200, VERSION_BODY),
        ("POST", action_url("deployVersionCode"), 200, {"status": "Succeeded"}),
        ("POST", action_url("getVersionCode"), 200, {"status": "Succeeded"}),
    ],
)
def test_swap_exception_does_not_relax_other_contracts(method, url, status, body):
    with pytest.raises(AssertionError):
        response_spec().validate_location(
            method,
            url,
            RESULT_URL,
            status,
            body,
            {},
            allow_known_swap_default_response=True,
        )


@pytest.mark.parametrize(
    "location", ["http://management.azure.com/result", RESULT_URL.replace("2026-10-01", "invalid")]
)
def test_swap_exception_does_not_relax_location_url_validation(location):
    with pytest.raises(AssertionError, match="HTTPS URL|API version mismatch"):
        response_spec().validate_location(
            "POST",
            action_url("swapDefault"),
            location,
            200,
            VERSION_BODY,
            {},
            allow_known_swap_default_response=True,
        )


@pytest.mark.parametrize("status", ["Accepted", "Running", "Succeeded", "Failed", "Canceled"])
def test_arm_polling_status_envelope(status):
    assert response_spec().validate_status_response(200, {"status": status}) == status


def test_arm_polling_allows_provider_specific_fields():
    body = {"status": "Succeeded", "operationId": "test-operation", "operationType": "Deploy", "error": None}
    assert response_spec().validate_status_response(200, body) == "Succeeded"


@pytest.mark.parametrize("body", [None, [], "Succeeded", {}, {"status": None}, {"status": 0}, {"status": ""}])
def test_arm_polling_requires_a_nonempty_string_status(body):
    with pytest.raises(AssertionError, match="Azure-AsyncOperation"):
        response_spec().validate_status_response(200, body)


@pytest.mark.parametrize("status", [201, 202, 204, 400, 500])
def test_arm_status_monitor_requires_http_200(status):
    with pytest.raises(AssertionError, match="expected HTTP 200"):
        response_spec().validate_status_response(status, {"status": "Succeeded"})


def test_json_null_is_not_an_empty_final_response():
    with pytest.raises(AssertionError, match="does not declare a response body"):
        response_spec().validate_location(
            "POST", action_url("swapDefault"), RESULT_URL, 204, None, {}, body_present=True
        )


@pytest.mark.parametrize("present,error", [(False, "requires a response body"), (True, "violates OpenAPI type")])
def test_missing_or_null_deployment_result_is_rejected(present, error):
    with pytest.raises(AssertionError, match=error):
        response_spec().validate_location(
            "POST", action_url("deployVersionCode"), RESULT_URL, 200, None, {}, body_present=present
        )


@pytest.mark.parametrize(
    "field,value",
    [
        ("deploymentType", 123),
        ("isDefaultVersion", True),
        ("validationStatus", []),
        ("lastPackageUpdateTime", "not-a-date"),
    ],
)
def test_version_final_properties_are_validated_from_spec(field, value):
    body = deepcopy(VERSION_BODY)
    body["properties"][field] = value
    with pytest.raises(AssertionError, match=f"properties.{field} violates OpenAPI"):
        response_spec().validate_location("POST", action_url("deployVersionCode"), RESULT_URL, 200, body, {})


@pytest.mark.parametrize("body", [{"status": "Succeeded"}, {"deploymentType": "file", "isDefaultVersion": "True"}])
def test_status_document_or_properties_only_is_not_a_version_result(body):
    with pytest.raises(AssertionError, match="violates OpenAPI required"):
        response_spec().validate_location("POST", action_url("deployVersionCode"), RESULT_URL, 200, body, {})


def test_required_nested_version_property_is_checked():
    body = deepcopy(VERSION_BODY)
    del body["properties"]["deploymentType"]
    with pytest.raises(AssertionError, match="properties violates OpenAPI required"):
        response_spec().validate_location("POST", action_url("deployVersionCode"), RESULT_URL, 200, body, {})


def test_location_202_is_not_a_completed_result():
    with pytest.raises(AssertionError, match="did not return a completed response"):
        response_spec().validate_location("POST", action_url("deployVersionCode"), RESULT_URL, 202, None, {})


def test_unknown_operation_is_not_silently_accepted():
    with pytest.raises(AssertionError, match="No initiating operation"):
        response_spec().validate_location("POST", "https://management.azure.com/unknown", RESULT_URL, 200, {}, {})


def test_declared_retry_after_header_type_is_checked():
    spec = response_spec()
    operation = spec.operation("POST", action_url("deployVersionCode"))
    spec.validate_response(operation, 202, None, {"Retry-After": "10"})
    with pytest.raises(AssertionError, match="Retry-After must be an integer"):
        spec.validate_response(operation, 202, None, {"Retry-After": "not-an-integer"})


def test_declared_async_operation_header_uri_format_is_checked():
    spec = response_spec()
    operation = spec.operation("POST", action_url("deployVersionCode"))
    with pytest.raises(AssertionError, match="violates OpenAPI format"):
        spec.validate_response(operation, 202, None, {"Azure-AsyncOperation": "not a URI"})


@pytest.mark.parametrize("location", ["http://management.azure.com/result", "https:/result"])
def test_final_location_requires_an_absolute_https_url(location):
    with pytest.raises(AssertionError, match="must be an HTTPS URL"):
        response_spec().validate_location("POST", action_url("deployVersionCode"), location, 200, VERSION_BODY, {})


def test_location_requires_an_initiating_lro_not_a_standalone_get():
    with pytest.raises(AssertionError, match="requires a long-running operation"):
        response_spec().validate_location("GET", VERSION_URL, RESULT_URL, 200, VERSION_BODY, {})


def test_operation_route_and_method_are_case_insensitive():
    spec = response_spec()
    assert spec.operation("get", VERSION_URL.upper()) == spec.operation("GET", VERSION_URL)


def test_unknown_http_method_is_not_matched():
    assert response_spec().operation("OPTIONS", VERSION_URL) is None


@pytest.mark.parametrize("target", ["request", "location"])
def test_response_spec_rejects_a_different_api_version(target):
    request_url = action_url("deployVersionCode")
    location = RESULT_URL
    if target == "request":
        request_url = request_url.replace("2026-10-01", "2025-12-01-preview")
    else:
        location = location.replace("2026-10-01", "2025-12-01-preview")
    with pytest.raises(AssertionError, match="API version mismatch"):
        response_spec().validate_location("POST", request_url, location, 200, VERSION_BODY, {})


@pytest.mark.parametrize(
    "field,value",
    [("commit", "0" * 40), ("repository", "Azure/incorrect-repository"), ("url", "https://example.com/incorrect-spec")],
)
def test_snapshot_must_match_pinned_generation_source(monkeypatch, tmp_path, field, value):
    snapshot = deepcopy(response_spec().snapshot)
    snapshot["source"][field] = value
    path = tmp_path / "response_spec.json"
    path.write_text(json.dumps(snapshot), encoding="utf-8")
    monkeypatch.setattr(spec_validation, "SNAPSHOT", path)
    with pytest.raises(AssertionError):
        response_spec.__wrapped__()


def test_snapshot_source_url_must_match_the_repository_and_commit(monkeypatch, tmp_path):
    snapshot = deepcopy(response_spec().snapshot)
    snapshot["source"]["url"] = snapshot["source"]["url"].replace("raw.githubusercontent.com", "example.com")
    path = tmp_path / "response_spec.json"
    path.write_text(json.dumps(snapshot), encoding="utf-8")
    monkeypatch.setattr(spec_validation, "SNAPSHOT", path)
    with pytest.raises(AssertionError, match="source URL mismatch"):
        response_spec.__wrapped__()
