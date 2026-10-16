# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import base64
import hashlib
import io
import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock

import pytest
from azure.core.exceptions import ResourceNotFoundError
from azure.core.utils import case_insensitive_dict
from azure.mgmt.edgeactions import models
from devtools_testutils import RandomNameResourceGroupPreparer

from edgeactions_test_settings import RESOURCE_GROUP_OPTIONS
from test_edge_actions_mgmt_client_lifecycle_test import (
    HANDLER,
    TestEdgeActionsLifecycle as LifecycleScenarios,
    cleanup_edge_action,
    complete_lro,
    pytestmark as lifecycle_marks,
    version_code,
)

VERSION_URL = (
    "https://management.azure.com/subscriptions/00000000-0000-0000-0000-000000000000"
    "/resourceGroups/rg/providers/Microsoft.Cdn/edgeActions/action/versions/v1"
)
SWAP_URL = VERSION_URL + "/swapDefault"
VERSION_BODY = {
    "id": VERSION_URL.removeprefix("https://management.azure.com"),
    "name": "v1",
    "type": "Microsoft.Cdn/edgeActions/versions",
    "location": "global",
    "properties": {"deploymentType": "file", "isDefaultVersion": "True", "provisioningState": "Succeeded"},
}


def http_response(body=None, status=200, headers=None):
    return SimpleNamespace(
        status_code=status,
        headers=case_insensitive_dict(headers or {}),
        content=json.dumps(body).encode() if body is not None else b"",
        json=lambda: body,
    )


def configure_lro(operation, result=None, responses=None, method="POST"):
    if responses is None:
        response = http_response(result.as_dict() if result is not None else None)
        responses = [("https://management.azure.com/resource", response)]
    poller = operation.return_value
    poller.result.return_value = result
    poller.done.return_value = True
    poller.status.return_value = "Succeeded"

    def begin(*args, **kwargs):
        for index, (url, response) in enumerate(responses):
            request = SimpleNamespace(url=url, method=method if index == 0 else "GET")
            kwargs["raw_response_hook"](SimpleNamespace(http_request=request, http_response=response))
        return poller

    operation.side_effect = begin


@pytest.mark.parametrize("sdk_reads_location", [False, True])
@pytest.mark.parametrize(
    "method,status,url", [("POST", 204, SWAP_URL), ("DELETE", 200, VERSION_URL), ("DELETE", 204, VERSION_URL)]
)
def test_final_location_is_checked_even_when_sdk_returns_none(sdk_reads_location, method, status, url):
    client = Mock()
    operation = Mock()
    status_url = "https://management.azure.com/operations/test"
    location = "https://management.azure.com/operationresults/test"
    final = http_response(status=status)
    responses = [
        (
            url,
            http_response(status=202, headers={"Azure-AsyncOperation": status_url, "Location": location}),
        ),
        (status_url, http_response({"status": "Running"})),
        (status_url, http_response({"status": "Succeeded"})),
    ]
    if sdk_reads_location:
        responses.append((location, final))
    configure_lro(operation, responses=responses, method=method)
    client.send_request.return_value = final
    assert complete_lro(client, operation, result_type=None) is None
    if sdk_reads_location:
        client.send_request.assert_not_called()
    else:
        request = client.send_request.call_args.args[0]
        assert request.method == "GET"
        assert request.url == location


@pytest.mark.parametrize("status", ["Running", "Failed", "Canceled"])
def test_final_location_requires_succeeded_status(status):
    client = Mock()
    operation = Mock()
    status_url = "https://management.azure.com/operations/test"
    location = "https://management.azure.com/operationresults/test"
    configure_lro(
        operation,
        responses=[
            (
                SWAP_URL,
                http_response(status=202, headers={"Azure-AsyncOperation": status_url, "Location": location}),
            ),
            (status_url, http_response({"status": status})),
        ],
    )
    with pytest.raises(AssertionError):
        complete_lro(client, operation, result_type=None)
    client.send_request.assert_not_called()


@pytest.mark.parametrize("sdk_reads_location", [False, True])
def test_known_swap_default_location_body_is_exempted(sdk_reads_location, caplog):
    client = Mock()
    operation = Mock()
    status_url = "https://management.azure.com/operations/test"
    final = http_response(VERSION_BODY)
    responses = [
        (SWAP_URL, http_response(status=202, headers={"Azure-AsyncOperation": status_url, "Location": VERSION_URL})),
        (status_url, http_response({"status": "Running"})),
        (status_url, http_response({"status": "Succeeded"})),
    ]
    if sdk_reads_location:
        responses.append((VERSION_URL, final))
    configure_lro(operation, responses=responses)
    client.send_request.return_value = final
    assert complete_lro(client, operation, result_type=None) is None
    assert "known HTTP-200-with-body service bug" in caplog.text
    assert client.send_request.call_count == (0 if sdk_reads_location else 1)


@pytest.mark.parametrize(
    "method,url,status",
    [("POST", SWAP_URL, 204), ("POST", SWAP_URL, 400), ("DELETE", VERSION_URL, 200), ("DELETE", VERSION_URL, 204)],
)
def test_swap_exception_does_not_allow_other_no_content_violations(method, url, status):
    client = Mock()
    operation = Mock()
    status_url = "https://management.azure.com/operations/test"
    location = VERSION_URL
    configure_lro(
        operation,
        responses=[
            (
                url,
                http_response(status=202, headers={"Azure-AsyncOperation": status_url, "Location": location}),
            ),
            (status_url, http_response({"status": "Succeeded"})),
            (location, http_response(VERSION_BODY, status=status)),
        ],
        method=method,
    )
    with pytest.raises(AssertionError, match="documented response|does not declare a response body"):
        complete_lro(client, operation, result_type=None)


@pytest.mark.parametrize("initial_status", [201, 202])
@pytest.mark.parametrize("body", [None, [], {}, {"status": None}, {"status": ""}, {"status": 123}])
def test_polling_response_schema_is_checked(initial_status, body):
    client = Mock()
    operation = Mock()
    status_url = "https://management.azure.com/operations/test"
    configure_lro(
        operation,
        result=models.EdgeActionVersion(VERSION_BODY),
        method="PUT" if initial_status == 201 else "POST",
        responses=[
            (
                VERSION_URL if initial_status == 201 else VERSION_URL + "/deployVersionCode",
                http_response(
                    VERSION_BODY if initial_status == 201 else None,
                    status=initial_status,
                    headers={"Azure-AsyncOperation": status_url},
                ),
            ),
            (status_url, http_response(body)),
            (status_url, http_response({"status": "Succeeded"})),
            (VERSION_URL, http_response(VERSION_BODY)),
        ],
    )
    with pytest.raises(AssertionError, match="Azure-AsyncOperation"):
        complete_lro(client, operation, result_type=models.EdgeActionVersion)
    client.send_request.assert_not_called()


def test_created_location_is_not_an_accepted_operation_result(monkeypatch):
    client = Mock()
    operation = Mock()
    status_url = "https://management.azure.com/operations/test"
    result = models.EdgeActionVersion(VERSION_BODY)
    spec = Mock()
    spec.validate_status_response.side_effect = lambda status, body: body["status"]
    monkeypatch.setattr("test_edge_actions_mgmt_client_lifecycle_test.response_spec", lambda: spec)
    configure_lro(
        operation,
        result=result,
        method="PUT",
        responses=[
            (
                VERSION_URL,
                http_response(
                    VERSION_BODY, status=201, headers={"Azure-AsyncOperation": status_url, "Location": VERSION_URL}
                ),
            ),
            (status_url, http_response({"status": "Running"})),
            (status_url, http_response({"status": "Succeeded"})),
            (VERSION_URL, http_response(VERSION_BODY)),
        ],
    )
    assert complete_lro(client, operation, result_type=models.EdgeActionVersion) is result
    assert spec.validate_status_response.call_count == 2
    spec.validate_location.assert_not_called()
    client.send_request.assert_not_called()


def test_no_content_action_rejects_literal_json_null_from_location():
    client = Mock()
    operation = Mock()
    location = "https://management.azure.com/operationresults/test"
    final = http_response(status=204)
    final.content = b"null"
    configure_lro(
        operation,
        responses=[
            (SWAP_URL, http_response(status=202, headers={"Location": location})),
            (location, final),
        ],
    )
    with pytest.raises(AssertionError, match="does not declare a response body"):
        complete_lro(client, operation, result_type=None)


def test_accepted_operation_requires_a_polling_header():
    client = Mock()
    operation = Mock()
    configure_lro(
        operation,
        responses=[
            (SWAP_URL, http_response(status=202)),
        ],
    )
    with pytest.raises(AssertionError, match="polling header"):
        complete_lro(client, operation, result_type=None)
    client.send_request.assert_not_called()


@pytest.mark.parametrize("header", ["Azure-AsyncOperation", "Location"])
def test_polling_headers_must_be_absolute_https_urls(header):
    client = Mock()
    operation = Mock()
    configure_lro(
        operation, responses=[(SWAP_URL, http_response(status=202, headers={header: "http://example.com/result"}))]
    )
    with pytest.raises(AssertionError, match="must be an HTTPS URL"):
        complete_lro(client, operation, result_type=None)
    client.send_request.assert_not_called()


@pytest.mark.parametrize("header", ["Azure-AsyncOperation", "Location"])
def test_accepted_operation_supports_either_polling_header(header):
    client = Mock()
    operation = Mock()
    url = "https://management.azure.com/operations/test"
    responses = [(SWAP_URL, http_response(status=202, headers={header: url}))]
    if header == "Azure-AsyncOperation":
        responses.extend(
            [
                (url, http_response({"status": "Accepted"})),
                (url, http_response({"status": "Running"})),
                (url, http_response({"status": "Succeeded"})),
            ]
        )
    else:
        responses.extend([(url, http_response(status=202)), (url, http_response(status=204))])
    configure_lro(operation, responses=responses)
    assert complete_lro(client, operation, result_type=None) is None
    client.send_request.assert_not_called()


@pytest.mark.parametrize(
    "body",
    [
        {"status": "Succeeded"},
        {"name": "wrong", "content": "aGVsbG8="},
    ],
)
def test_final_location_body_must_match_the_expected_result(body):
    client = Mock()
    operation = Mock()
    status_url = "https://management.azure.com/operations/test"
    location = "https://management.azure.com/operationresults/test"
    configure_lro(
        operation,
        result=models.VersionCode(name="v1", content="aGVsbG8="),
        responses=[
            (
                VERSION_URL + "/getVersionCode",
                http_response(status=202, headers={"Azure-AsyncOperation": status_url, "Location": location}),
            ),
            (status_url, http_response({"status": "Succeeded"})),
            (location, http_response(body)),
        ],
    )
    with pytest.raises(AssertionError):
        complete_lro(client, operation, result_type=models.VersionCode)


def test_final_location_cannot_precede_status_completion():
    client = Mock()
    operation = Mock()
    status_url = "https://management.azure.com/operations/test"
    location = "https://management.azure.com/operationresults/test"
    configure_lro(
        operation,
        responses=[
            (
                SWAP_URL,
                http_response(status=202, headers={"Azure-AsyncOperation": status_url, "Location": location}),
            ),
            (location, http_response(status=204)),
            (status_url, http_response({"status": "Succeeded"})),
        ],
    )
    with pytest.raises(AssertionError, match="after the operation reports Succeeded"):
        complete_lro(client, operation, result_type=None)


def test_package_collection_handles_multiple_conftest_files():
    env = os.environ.copy()
    env["AZURE_TEST_RUN_LIVE"] = "false"
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        cwd=Path(__file__).resolve().parents[1],
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "test_edge_actions_mgmt_client_lifecycle_test.py::TestEdgeActionsLifecycle" in result.stdout


def test_resource_group_prefix_is_applied_once(monkeypatch):
    monkeypatch.delenv("AZURE_RESOURCEGROUP_NAME", raising=False)
    preparer = RandomNameResourceGroupPreparer(**RESOURCE_GROUP_OPTIONS)
    name = preparer._prefix_name(preparer.random_name)
    assert name.startswith("rgpy-pythonsdk-edgeaction-test-")
    assert len(name) == 45
    assert preparer.moniker == "pythonsdk-edgeaction-test-rgname"


def test_lifecycle_supports_playback_without_source_edits():
    marks = lifecycle_marks if isinstance(lifecycle_marks, (list, tuple)) else [lifecycle_marks]
    assert all(mark.name != "live_test_only" for mark in marks)
    assert any(mark.name == "usefixtures" and "add_sanitizers" in mark.args for mark in marks)


def test_action_names_are_repeatable_and_distinct_between_scenarios(monkeypatch):
    scenario = LifecycleScenarios()
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "edgeactions::tag_updates (call)")
    name = scenario.get_resource_name("eapython")
    assert name.startswith("eapython")
    assert name != "eapython"
    assert scenario.get_resource_name("eapython") == name

    monkeypatch.setenv("PYTEST_CURRENT_TEST", "edgeactions::file_versions (call)")
    assert scenario.get_resource_name("eapython") != name


@pytest.mark.parametrize("deployment_type", ["file", "zip"])
def test_version_code_is_replayable(deployment_type):
    encoded = version_code(deployment_type)
    assert encoded == version_code(deployment_type)
    decoded = base64.b64decode(encoded)
    if deployment_type == "zip":
        with zipfile.ZipFile(io.BytesIO(decoded)) as archive:
            assert archive.namelist() == ["handler.js"]
            assert archive.read("handler.js") == HANDLER
            assert archive.getinfo("handler.js").date_time == (1980, 1, 1, 0, 0, 0)
    else:
        assert decoded == HANDLER


@pytest.mark.parametrize("create_system", [0, 3], ids=["windows", "unix"])
def test_zip_payload_matches_recording_across_platforms(monkeypatch, create_system):
    class PlatformZipInfo(zipfile.ZipInfo):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.create_system = create_system

    monkeypatch.setattr(zipfile, "ZipInfo", PlatformZipInfo)
    payload = base64.b64decode(version_code("zip"))
    # Fingerprint of the synthetic ZIP request in the existing service recording.
    assert hashlib.sha256(payload).hexdigest() == "1513a84ea0182336e1a0e7d7ab1c8472bd276c47628fd41c6272e43407d3a5c6"


def make_version(name, is_default):
    return models.EdgeActionVersion(
        {"name": name, "location": "global", "properties": {"deploymentType": "file", "isDefaultVersion": is_default}}
    )


@pytest.mark.parametrize("default_name", ["v1", "v2"])
def test_cleanup_uses_current_default_and_deletes_parent_last(default_name):
    client = Mock()
    for group in (client.edge_actions, client.edge_action_versions, client.edge_action_execution_filters):
        configure_lro(group.begin_delete)
    client.edge_action_execution_filters.list_by_edge_action.return_value = [
        models.EdgeActionExecutionFilter({"name": "filter", "location": "global"})
    ]
    client.edge_action_versions.list_by_edge_action.return_value = [
        make_version(name, "True" if name == default_name else "False") for name in ("v1", "v2")
    ]
    cleanup_edge_action(client, "rg", "action")
    non_default = "v2" if default_name == "v1" else "v1"
    deletes = [(item[0], item.args) for item in client.mock_calls if item[0].endswith("begin_delete")]
    assert deletes == [
        ("edge_action_execution_filters.begin_delete", ("rg", "action", "filter")),
        ("edge_action_versions.begin_delete", ("rg", "action", non_default)),
        ("edge_action_versions.begin_delete", ("rg", "action", default_name)),
        ("edge_actions.begin_delete", ("rg", "action")),
    ]
    client.edge_actions.begin_delete.return_value.result.assert_called_once_with()


@pytest.mark.parametrize("states", [("True", "True"), ("True", None)])
def test_cleanup_rejects_ambiguous_default_state(states):
    client = Mock()
    client.edge_action_execution_filters.list_by_edge_action.return_value = []
    client.edge_action_versions.list_by_edge_action.return_value = [
        make_version(f"v{index}", state) for index, state in enumerate(states)
    ]
    with pytest.raises(AssertionError):
        cleanup_edge_action(client, "rg", "action")
    client.edge_action_versions.begin_delete.assert_not_called()
    client.edge_actions.begin_delete.assert_not_called()


def test_existing_action_is_not_overwritten(monkeypatch):
    scenario = LifecycleScenarios()
    client = MagicMock()
    client.__enter__.return_value = client
    monkeypatch.setattr(scenario, "create_mgmt_client", Mock(return_value=client))
    monkeypatch.setattr(scenario, "get_resource_name", Mock(return_value="existing"))
    with pytest.raises(pytest.fail.Exception, match="Refusing to overwrite existing EdgeAction"):
        with scenario.edge_action("rg"):
            pytest.fail("An existing resource must not be yielded to the scenario")
    client.edge_actions.begin_create.assert_not_called()
    client.edge_actions.begin_delete.assert_not_called()


@pytest.mark.parametrize("failure_during_create", [False, True], ids=["scenario-failure", "create-failure"])
def test_failure_still_cleans_owned_action(monkeypatch, failure_during_create):
    scenario = LifecycleScenarios()
    client = MagicMock()
    client.__enter__.return_value = client
    client.edge_actions.get.side_effect = [ResourceNotFoundError("Not found"), models.EdgeAction(location="global")]
    configure_lro(
        client.edge_actions.begin_create,
        models.EdgeAction(
            {
                "id": "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Cdn/edgeActions/owned",
                "name": "owned",
                "type": "Microsoft.Cdn/edgeActions",
                "location": "global",
                "sku": {"name": "Standard", "tier": "Standard"},
                "tags": {"purpose": "initial", "remove-me": "initial"},
                "properties": {"provisioningState": "Succeeded", "attachments": []},
            }
        ),
    )
    configure_lro(client.edge_actions.begin_delete)
    if failure_during_create:
        client.edge_actions.begin_create.return_value.result.side_effect = ValueError("Scenario failure")
    client.edge_action_execution_filters.list_by_edge_action.return_value = []
    client.edge_action_versions.list_by_edge_action.return_value = []
    monkeypatch.setattr(scenario, "create_mgmt_client", Mock(return_value=client))
    monkeypatch.setattr(scenario, "get_resource_name", Mock(return_value="owned"))
    with pytest.raises(ValueError, match="Scenario failure"):
        with scenario.edge_action("rg"):
            raise ValueError("Scenario failure")
    client.edge_actions.begin_delete.assert_called_once()
    assert client.edge_actions.begin_delete.call_args.args == ("rg", "owned")
    client.edge_actions.begin_delete.return_value.result.assert_called_once_with()


def test_cleanup_of_absent_action_does_not_delete_resources():
    client = Mock()
    client.edge_actions.get.side_effect = ResourceNotFoundError("Not found")
    cleanup_edge_action(client, "rg", "absent")
    client.edge_action_execution_filters.list_by_edge_action.assert_not_called()
    client.edge_action_versions.list_by_edge_action.assert_not_called()
    client.edge_actions.begin_delete.assert_not_called()
