# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Focused SDK contract tests for account and project connection creation."""

import json
import re
import time
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from azure.core.credentials import AccessToken
from azure.core.exceptions import HttpResponseError
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
from azure.mgmt.cognitiveservices.aio import CognitiveServicesManagementClient as AsyncCognitiveServicesManagementClient

from connection_test_utils import (
    API_VERSION,
    SANITIZED_CONNECTION_NAME,
    TEST_CREDENTIAL,
    add_connection_sanitizers,
    connection_resource,
    log_create_failure,
)

SUBSCRIPTION_ID = "00000000-0000-0000-0000-000000000000"
PARENT_ARGS = {
    "account_connections": ("resource-group", "cognitive-account"),
    "project_connections": ("resource-group", "cognitive-account", "foundry-project"),
}


class _FakeCredential:
    def get_token(self, *scopes, **kwargs):  # pylint: disable=unused-argument
        return AccessToken("fake-token", int(time.time()) + 3600)


class _FakeAsyncCredential:
    async def get_token(self, *scopes, **kwargs):  # pylint: disable=unused-argument
        return AccessToken("fake-token", int(time.time()) + 3600)


class _FakeHttpResponse:
    def __init__(self, request, status_code):
        self.request = request
        self.status_code = status_code
        self.headers = {
            "x-ms-request-id": "d7a11ed8-d78a-4a56-a4dc-5a35ee16e626",
            "azure-asyncoperation": "https://management.azure.com/poll?secret=do-not-log",
            "authorization": "Bearer do-not-log",
        }
        self.reason = "Created"
        self.content_type = "application/json"

    @property
    def content(self):
        return json.dumps({"error": {"code": "UnexpectedStatus", "message": "Created"}}).encode("utf-8")

    def text(self, *args, **kwargs):  # pylint: disable=unused-argument
        return self.content.decode("utf-8")

    def json(self):
        return json.loads(self.content)

    def read(self, *args, **kwargs):  # pylint: disable=unused-argument
        return self.content

    def iter_bytes(self, *args, **kwargs):  # pylint: disable=unused-argument
        return iter([self.content])

    def iter_raw(self, *args, **kwargs):  # pylint: disable=unused-argument
        return iter([self.content])


def _make_sync_client():
    client = CognitiveServicesManagementClient(
        credential=_FakeCredential(),
        subscription_id=SUBSCRIPTION_ID,
        api_version=API_VERSION,
    )

    def send(request, **kwargs):  # pylint: disable=unused-argument
        response = _FakeHttpResponse(request, 201)
        return SimpleNamespace(http_request=request, http_response=response, context={})

    client._client._pipeline.run = MagicMock(side_effect=send)  # pylint: disable=protected-access
    return client


def _make_async_client():
    client = AsyncCognitiveServicesManagementClient(
        credential=_FakeAsyncCredential(),
        subscription_id=SUBSCRIPTION_ID,
        api_version=API_VERSION,
    )

    def send(request, **kwargs):  # pylint: disable=unused-argument
        response = _FakeHttpResponse(request, 201)
        return SimpleNamespace(http_request=request, http_response=response, context={})

    client._client._pipeline.run = AsyncMock(side_effect=send)  # pylint: disable=protected-access
    return client


def _assert_request(client, operations_name, connection_name):
    request = client._client._pipeline.run.call_args.args[0]  # pylint: disable=protected-access
    body = json.loads(request.content)

    assert request.method == "PUT"
    assert request.url.endswith(f"/connections/{connection_name}?api-version={API_VERSION}")
    assert body["properties"]["category"] == "CustomKeys"
    assert body["properties"]["authType"] == "CustomKeys"
    assert body["properties"]["credentials"]["keys"] == {"test-key": TEST_CREDENTIAL}
    if operations_name == "project_connections":
        assert "/projects/foundry-project/" in request.url


@pytest.mark.parametrize("operations_name", ["account_connections", "project_connections"])
def test_sync_connection_create_rejects_201_and_serializes_custom_keys(operations_name):
    client = _make_sync_client()
    connection_name = "sdkconnection"
    try:
        with pytest.raises(HttpResponseError) as error:
            getattr(client, operations_name).create(
                *PARENT_ARGS[operations_name],
                connection_name,
                connection_resource("initial"),
            )

        assert error.value.response.status_code == 201
        _assert_request(client, operations_name, connection_name)
    finally:
        client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("operations_name", ["account_connections", "project_connections"])
async def test_async_connection_create_rejects_201_and_serializes_custom_keys(operations_name):
    client = _make_async_client()
    connection_name = "sdkconnection"
    try:
        with pytest.raises(HttpResponseError) as error:
            await getattr(client, operations_name).create(
                *PARENT_ARGS[operations_name],
                connection_name,
                connection_resource("initial"),
            )

        assert error.value.response.status_code == 201
        _assert_request(client, operations_name, connection_name)
    finally:
        await client.close()


def test_create_failure_diagnostics_only_log_allowlisted_metadata(caplog):
    response = _FakeHttpResponse(None, 201)
    error = HttpResponseError(response=response)

    with caplog.at_level("ERROR"):
        log_create_failure(error, API_VERSION)

    assert "status=201" in caplog.text
    assert f"api_version={API_VERSION}" in caplog.text
    assert "d7a11ed8-d78a-4a56-a4dc-5a35ee16e626" in caplog.text
    assert "'azure-asyncoperation': True" in caplog.text
    assert "do-not-log" not in caplog.text


def test_list_name_sanitizer_preserves_test_connection_and_redacts_other_names():
    connection_name = "sdkconn-test"
    with (
        patch("connection_test_utils.add_general_string_sanitizer"),
        patch("connection_test_utils.add_header_regex_sanitizer"),
        patch("connection_test_utils.add_body_key_sanitizer") as body_sanitizer,
    ):
        add_connection_sanitizers(connection_name)

    name_rule = next(
        call.kwargs for call in body_sanitizer.call_args_list if call.kwargs["json_path"] == "$..value[*].name"
    )
    regex = name_rule["regex"]
    assert re.fullmatch(regex, "existing-connection")
    assert not re.fullmatch(regex, connection_name)
    assert not re.fullmatch(regex, SANITIZED_CONNECTION_NAME)
    assert re.fullmatch(regex, f"{connection_name}-other")
