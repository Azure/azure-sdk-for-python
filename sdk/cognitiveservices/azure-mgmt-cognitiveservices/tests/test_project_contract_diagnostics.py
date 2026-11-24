# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Mocked response handling checks; these are not evidence of live service compatibility."""

import json
import logging
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.core.credentials import AccessToken
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.core.pipeline.transport import AsyncHttpTransport, HttpResponse, HttpTransport
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
from azure.mgmt.cognitiveservices.aio import CognitiveServicesManagementClient as AsyncClient

import project_test_helpers as helpers
from project_test_helpers import (
    DEFAULT_API_VERSION,
    LOGGER,
    ResponseDiagnostics,
    cleanup_failed,
    configuration,
    project_body,
)
import test_project_lifecycle as lifecycle

SUBSCRIPTION = "00000000-0000-0000-0000-000000000000"
REQUEST_ID = "11111111-2222-3333-4444-555555555555"


class ProjectResponse(HttpResponse):
    def __init__(self, request, status=201):
        super().__init__(request, None)
        self.status_code = status
        self.headers = {
            "content-type": "application/json",
            "Azure-AsyncOperation": "https://private.example/operations/project?sig=secret",
            "Location": "https://private.example/operations/project?sig=secret",
            "Retry-After": "1",
            "x-ms-request-id": REQUEST_ID,
            "x-ms-correlation-request-id": "sensitive-value",
            "Authorization": "Bearer secret",
        }
        self.content_type = "application/json"
        self.reason = "Created"

    def body(self):
        return json.dumps({"properties": {"provisioningState": "Creating"}, "secret": "body-secret"}).encode()

    def read(self):
        return self.body()

    def json(self):
        return json.loads(self.body())


class AsyncProjectResponse(ProjectResponse):
    async def read(self):
        return self.body()


def _credential(async_client=False):
    credential = SimpleNamespace(get_token=MagicMock(return_value=AccessToken("fake-token", 2527537086)))
    if async_client:
        credential.get_token = AsyncMock(return_value=AccessToken("fake-token", 2527537086))
    return credential


def _assert_rejected_with_diagnostics(error, diagnostics, caplog):
    assert error.value.status_code == 201
    initial = diagnostics.responses[0]
    assert initial["method"] == "PUT"
    assert initial["status"] == 201
    assert initial["api_version"] == initial["request_api_version"] == DEFAULT_API_VERSION
    assert initial["headers"]["x-ms-request-id"] == REQUEST_ID
    assert initial["headers"]["azure-asyncoperation"] == "<present; URL redacted>"
    assert initial["headers"]["location"] == "<present; URL redacted>"
    assert initial["headers"]["retry-after"] == "1"
    assert initial["headers"]["x-ms-correlation-request-id"] == "<redacted>"
    assert REQUEST_ID in caplog.text
    for sensitive in ("secret", "private.example", "sensitive-value", "Authorization", "fake-token"):
        assert sensitive not in caplog.text


def test_sync_rejects_201_after_diagnostic_hook(caplog):
    caplog.set_level(logging.INFO, logger=LOGGER.name)
    transport = MagicMock(spec=HttpTransport)
    transport.send.side_effect = lambda request, **kwargs: ProjectResponse(request)
    diagnostics = ResponseDiagnostics(DEFAULT_API_VERSION, "create")
    with CognitiveServicesManagementClient(
        _credential(), SUBSCRIPTION, api_version=DEFAULT_API_VERSION, transport=transport, logging_enable=False
    ) as client:
        with pytest.raises(HttpResponseError) as error:
            client.projects.begin_create(
                "group", "account", "project", project_body("eastus", "test"), raw_response_hook=diagnostics
            )
    _assert_rejected_with_diagnostics(error, diagnostics, caplog)


@pytest.mark.asyncio
async def test_async_rejects_201_after_diagnostic_hook(caplog):
    caplog.set_level(logging.INFO, logger=LOGGER.name)
    transport = MagicMock(spec=AsyncHttpTransport)
    transport.send = AsyncMock(side_effect=lambda request, **kwargs: AsyncProjectResponse(request))
    diagnostics = ResponseDiagnostics(DEFAULT_API_VERSION, "create")
    async with AsyncClient(
        _credential(async_client=True),
        SUBSCRIPTION,
        api_version=DEFAULT_API_VERSION,
        transport=transport,
        logging_enable=False,
    ) as client:
        with pytest.raises(HttpResponseError) as error:
            await client.projects.begin_create(
                "group", "account", "project", project_body("eastus", "test"), raw_response_hook=diagnostics
            )
    _assert_rejected_with_diagnostics(error, diagnostics, caplog)


@pytest.mark.parametrize("original_error", [True, False])
def test_cleanup_failure_preserves_original_error(original_error, caplog):
    error = HttpResponseError("body-secret")
    if original_error:
        cleanup_failed(error, original_error=True)
    else:
        with pytest.raises(HttpResponseError) as raised:
            cleanup_failed(error, original_error=False)
        assert raised.value is error
    assert "Project cleanup failed" in caplog.text
    assert "body-secret" not in caplog.text


def test_playback_requires_recorded_project_variables():
    with pytest.raises(pytest.fail.Exception, match="Re-record"):
        configuration(SimpleNamespace(is_live=False), {})


def test_api_version_live_uses_sdk_default_or_override_and_playback_uses_recording(monkeypatch):
    monkeypatch.delenv("AZURE_COGNITIVE_SERVICES_API_VERSION", raising=False)
    live, playback = SimpleNamespace(is_live=True), SimpleNamespace(is_live=False)
    assert helpers.api_version(live, None) == DEFAULT_API_VERSION
    monkeypatch.setenv("AZURE_COGNITIVE_SERVICES_API_VERSION", "2026-11-01")
    assert helpers.api_version(live, None) == "2026-11-01"
    # Playback ignores the override and the SDK default so recorded URLs still match.
    assert helpers.api_version(playback, {"api_version": "2025-01-01-preview"}) == "2025-01-01-preview"
    with pytest.raises(pytest.fail.Exception, match="re-record"):
        helpers.api_version(playback, {})


def test_generated_project_name_is_sanitized(monkeypatch):
    for key, value in {
        "AZURE_SUBSCRIPTION_ID": SUBSCRIPTION,
        "AZURE_RESOURCE_GROUP": "group",
        "AZURE_COGNITIVE_SERVICES_ACCOUNT": "account",
        "AZURE_COGNITIVE_SERVICES_LOCATION": "eastus",
    }.items():
        monkeypatch.setenv(key, value)
    sanitizer = MagicMock()
    query_sanitizer = MagicMock()
    monkeypatch.setattr(helpers, "add_general_string_sanitizer", sanitizer)
    monkeypatch.setattr(helpers, "add_general_regex_sanitizer", query_sanitizer)
    test_case = SimpleNamespace(is_live=True, get_resource_name=lambda _: "sdkproj")

    _, _, _, name = configuration(test_case, None)

    sanitizer.assert_called_once_with(target=name, value=helpers.SANITIZED_PROJECT_NAME, function_scoped=True)
    query_sanitizer.assert_called_once_with(
        regex=r'[?&](?:c|s|h)=([^&"]+)',
        value="sanitized",
        group_for_replace="1",
        function_scoped=True,
    )
    assert (
        configuration(
            SimpleNamespace(is_live=False), {"project_name": helpers.SANITIZED_PROJECT_NAME, "location": "eastus"}
        )[-1]
        == helpers.SANITIZED_PROJECT_NAME
    )
    with pytest.raises(pytest.fail.Exception, match="sanitized project_name"):
        configuration(SimpleNamespace(is_live=False), {"project_name": name, "location": "eastus"})


def test_project_identity_uses_sanitized_id_in_playback():
    expected_id = (
        "/subscriptions/sub/resourceGroups/group/providers/Microsoft.CognitiveServices/accounts/acct/projects/p"
    )
    project = SimpleNamespace(
        id="Sanitized",
        name="p",
        type=helpers.RESOURCE_TYPE,
        location="eastus",
        properties=SimpleNamespace(
            provisioning_state="Succeeded", display_name="SDK contract test", description="test"
        ),
    )
    helpers.assert_project(project, expected_id, "eastus", "test", is_live=False)
    with pytest.raises(AssertionError):
        helpers.assert_project(project, expected_id, "eastus", "test", is_live=True)
    project.id = expected_id
    helpers.assert_project(project, expected_id, "eastus", "test", is_live=True)


@pytest.mark.parametrize("cleanup_error", [False, True])
def test_sync_lifecycle_cleans_up_rejected_create(monkeypatch, cleanup_error):
    monkeypatch.setattr("devtools_testutils.proxy_testcase.is_live_and_not_recording", lambda: True)
    monkeypatch.setattr(lifecycle, "configuration", lambda *_: ("group", "account", "eastus", "sdkproj-unit"))
    monkeypatch.setattr(lifecycle, "api_version", lambda *_: DEFAULT_API_VERSION)
    test_case = lifecycle.TestProjectLifecycle()
    client = MagicMock()
    client.__enter__.return_value = client
    client.projects.get.side_effect = ResourceNotFoundError("preflight")
    original = HttpResponseError("original rejection")
    client.projects.begin_create.side_effect = original
    if cleanup_error:
        client.projects.begin_delete.side_effect = HttpResponseError("cleanup rejection")
    monkeypatch.setattr(test_case, "create_mgmt_client", lambda *args, **kwargs: client)
    monkeypatch.setattr(test_case, "get_settings_value", lambda _: SUBSCRIPTION)

    with pytest.raises(HttpResponseError) as raised:
        test_case.test_project_lifecycle()

    assert raised.value is original
    assert client.projects.begin_delete.call_args.args == ("group", "account", "sdkproj-unit")
    client.projects.begin_delete.assert_called_once()
    if not cleanup_error:
        client.projects.begin_delete.return_value.result.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("cleanup_error", [False, True])
async def test_async_lifecycle_cleans_up_rejected_create(monkeypatch, cleanup_error):
    monkeypatch.setattr("devtools_testutils.aio.proxy_testcase_async.is_live_and_not_recording", lambda: True)
    monkeypatch.setattr(lifecycle, "configuration", lambda *_: ("group", "account", "eastus", "sdkproj-unit"))
    monkeypatch.setattr(lifecycle, "api_version", lambda *_: DEFAULT_API_VERSION)
    test_case = lifecycle.TestProjectLifecycleAsync()
    client = MagicMock()
    client.__aenter__.return_value = client
    client.projects.get = AsyncMock(side_effect=ResourceNotFoundError("preflight"))
    original = HttpResponseError("original rejection")
    client.projects.begin_create = AsyncMock(side_effect=original)
    poller = SimpleNamespace(result=AsyncMock())
    client.projects.begin_delete = AsyncMock(return_value=poller)
    if cleanup_error:
        client.projects.begin_delete.side_effect = HttpResponseError("cleanup rejection")
    credential = SimpleNamespace(close=AsyncMock())
    monkeypatch.setattr(test_case, "get_credential", lambda *args, **kwargs: credential)
    monkeypatch.setattr(test_case, "create_client_from_credential", lambda *args, **kwargs: client)
    monkeypatch.setattr(test_case, "get_settings_value", lambda _: SUBSCRIPTION)

    with pytest.raises(HttpResponseError) as raised:
        await test_case.test_project_lifecycle()

    assert raised.value is original
    assert client.projects.begin_delete.call_args.args == ("group", "account", "sdkproj-unit")
    client.projects.begin_delete.assert_awaited_once()
    credential.close.assert_awaited_once()
    if not cleanup_error:
        poller.result.assert_awaited_once()
