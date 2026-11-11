# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Async unit tests for Cost Control request serialization and response handling."""

import json
import time
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from azure.core import MatchConditions
from azure.core.credentials import AccessToken
from azure.core.exceptions import HttpResponseError
from azure.mgmt.cognitiveservices import models
from azure.mgmt.cognitiveservices.aio import CognitiveServicesManagementClient

from test_cost_controls_operations import (
    API_VERSION,
    BUDGET_PROPERTIES,
    PATCH_CASES,
    SUBSCRIPTION_ID,
    _cost_control_case,
)


@pytest.fixture(params=["account", "project"])
def cost_control_case(request):
    return _cost_control_case(request.param)


class _FakeAsyncCredential:
    async def get_token(self, *scopes, **kwargs):  # pylint: disable=unused-argument
        return AccessToken("fake-token", int(time.time()) + 3600)


class _FakeAsyncHttpResponse:
    def __init__(self, request, status_code, body=None, headers=None):
        self.request = request
        self.status_code = status_code
        self._body = body
        self.headers = headers or {}
        self.reason = "reason"
        self.content_type = "application/json"

    @property
    def content(self):
        return json.dumps(self._body).encode("utf-8") if self._body is not None else b""

    def text(self, *args, **kwargs):  # pylint: disable=unused-argument
        return self.content.decode("utf-8")

    def json(self):
        return self._body

    async def read(self, *args, **kwargs):  # pylint: disable=unused-argument
        return self.content

    def iter_bytes(self, *args, **kwargs):  # pylint: disable=unused-argument
        return iter([self.content])

    def iter_raw(self, *args, **kwargs):  # pylint: disable=unused-argument
        return iter([self.content])


def _make_client(status_code=200, body=None, headers=None):
    client = CognitiveServicesManagementClient(
        credential=_FakeAsyncCredential(),
        subscription_id=SUBSCRIPTION_ID,
    )

    def send(request, **kwargs):  # pylint: disable=unused-argument
        response = _FakeAsyncHttpResponse(request, status_code, body, headers)
        return SimpleNamespace(http_request=request, http_response=response, context={})

    client._client._pipeline.run = AsyncMock(side_effect=send)  # pylint: disable=protected-access
    return client


def _request(client):
    return client._client._pipeline.run.call_args.args[0]  # pylint: disable=protected-access


def _json_body(request):
    content = request.content
    if isinstance(content, bytes):
        content = content.decode("utf-8")
    return json.loads(content)


@pytest.mark.asyncio
async def test_create_serializes_budget_and_if_none_match(cost_control_case):
    client = _make_client(201, cost_control_case.response, {"ETag": '"response-etag"'})
    budget = cost_control_case.model_type(properties=models.CostControlProperties(deepcopy(BUDGET_PROPERTIES)))

    result = await getattr(client, cost_control_case.operations_name).create_or_update(
        *cost_control_case.parent_args,
        "monthly-budget",
        budget,
        etag="*",
        match_condition=MatchConditions.IfMissing,
    )

    request = _request(client)
    body = _json_body(request)
    assert request.method == "PUT"
    assert request.url.endswith(f"{cost_control_case.parent_id}/costControls/monthly-budget?api-version={API_VERSION}")
    assert request.headers["If-None-Match"] == "*"
    assert body == {"properties": BUDGET_PROPERTIES}
    assert isinstance(result, cost_control_case.model_type)
    assert result.properties.notifications["budget-alert"].threshold == 80
    assert result.properties.provider_properties.actions["budget-block"].type == "Block"


@pytest.mark.asyncio
async def test_get_deserializes_cost_control_and_etag_header(cost_control_case):
    client = _make_client(200, cost_control_case.response, {"ETag": '"response-etag"'})

    result, response_headers = await getattr(client, cost_control_case.operations_name).get(
        *cost_control_case.parent_args,
        "monthly-budget",
        cls=lambda _, model, headers: (model, headers),
    )

    request = _request(client)
    assert request.method == "GET"
    assert request.url.endswith(f"{cost_control_case.parent_id}/costControls/monthly-budget?api-version={API_VERSION}")
    assert isinstance(result, cost_control_case.model_type)
    assert result.properties.amount == 125
    assert result.etag == '"body-etag"'
    assert response_headers["ETag"] == '"response-etag"'


@pytest.mark.asyncio
async def test_update_sends_if_match_and_partial_budget(cost_control_case):
    client = _make_client(200, cost_control_case.response, {"ETag": '"updated-etag"'})
    patch = models.CostControlPatch(properties=models.CostControlPatchProperties(amount=150))

    await getattr(client, cost_control_case.operations_name).update(
        *cost_control_case.parent_args,
        "monthly-budget",
        patch,
        etag='"body-etag"',
        match_condition=MatchConditions.IfNotModified,
    )

    request = _request(client)
    assert request.method == "PATCH"
    assert request.headers["If-Match"] == '"body-etag"'
    assert _json_body(request) == {"properties": {"amount": 150}}


@pytest.mark.asyncio
async def test_list_deserializes_cost_controls(cost_control_case):
    client = _make_client(200, {"value": [cost_control_case.response], "nextLink": None})
    operations = getattr(client, cost_control_case.operations_name)

    result = [cost_control async for cost_control in operations.list(*cost_control_case.parent_args)]

    request = _request(client)
    assert request.method == "GET"
    assert request.url.endswith(f"{cost_control_case.parent_id}/costControls?api-version={API_VERSION}")
    assert [cost_control.name for cost_control in result] == ["monthly-budget"]


@pytest.mark.asyncio
async def test_delete_sends_if_match(cost_control_case):
    client = _make_client(204)

    result = await getattr(client, cost_control_case.operations_name).delete(
        *cost_control_case.parent_args,
        "monthly-budget",
        etag='"body-etag"',
        match_condition=MatchConditions.IfNotModified,
    )

    request = _request(client)
    assert result is None
    assert request.method == "DELETE"
    assert request.headers["If-Match"] == '"body-etag"'


@pytest.mark.asyncio
@pytest.mark.parametrize("payload", PATCH_CASES)
async def test_update_preserves_patch_payload(cost_control_case, payload):
    client = _make_client(200, cost_control_case.response)

    await getattr(client, cost_control_case.operations_name).update(
        *cost_control_case.parent_args,
        "monthly-budget",
        models.CostControlPatch(deepcopy(payload)),
    )

    request = _request(client)
    assert request.method == "PATCH"
    assert request.url.endswith(f"{cost_control_case.parent_id}/costControls/monthly-budget?api-version={API_VERSION}")
    assert _json_body(request) == payload


@pytest.mark.asyncio
async def test_check_existence_uses_head_and_returns_etag(cost_control_case):
    client = _make_client(200, headers={"ETag": '"head-etag"'})
    operations = getattr(client, cost_control_case.operations_name)

    assert await operations.check_existence(*cost_control_case.parent_args, "monthly-budget") is True
    response_headers = await operations.check_existence(
        *cost_control_case.parent_args, "monthly-budget", cls=lambda _, model, headers: headers
    )

    request = _request(client)
    assert request.method == "HEAD"
    assert request.url.endswith(f"{cost_control_case.parent_id}/costControls/monthly-budget?api-version={API_VERSION}")
    assert response_headers["ETag"] == '"head-etag"'


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status_code,error_code",
    [(400, "BadRequest"), (403, "FeatureNotRegistered"), (412, "PreconditionFailed")],
)
async def test_update_propagates_service_errors(cost_control_case, status_code, error_code):
    client = _make_client(status_code, {"error": {"code": error_code, "message": "Update rejected"}})

    with pytest.raises(HttpResponseError) as error:
        await getattr(client, cost_control_case.operations_name).update(
            *cost_control_case.parent_args,
            "monthly-budget",
            models.CostControlPatch(properties=models.CostControlPatchProperties(amount=150)),
            etag='"stale-etag"',
            match_condition=MatchConditions.IfNotModified,
        )

    assert error.value.status_code == status_code
    assert error.value.error.code == error_code


@pytest.mark.asyncio
async def test_account_update_serializes_explicit_null_cost_control_connections():
    client = _make_client(
        200,
        {
            "id": "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.CognitiveServices/accounts/acct",
            "name": "acct",
            "type": "Microsoft.CognitiveServices/accounts",
            "location": "eastus",
            "properties": {"costControlConnections": None},
        },
    )

    await client.accounts.begin_update(
        "rg",
        "acct",
        {"properties": {"costControlConnections": None}},
        polling=False,
    )

    request = _request(client)
    assert request.method == "PATCH"
    assert _json_body(request)["properties"]["costControlConnections"] is None
