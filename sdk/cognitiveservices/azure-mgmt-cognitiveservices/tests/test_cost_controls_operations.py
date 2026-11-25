# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Unit tests for Cost Control request serialization and response handling."""

import json
import time
from copy import deepcopy
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from azure.core import MatchConditions
from azure.core.credentials import AccessToken
from azure.core.exceptions import HttpResponseError
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient, models

SUBSCRIPTION_ID = "00000000-0000-0000-0000-000000000000"
ACCOUNT_ID = (
    f"/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/rg/providers/" "Microsoft.CognitiveServices/accounts/acct"
)
API_VERSION = "2026-11-15-preview"
BUDGET_PROPERTIES = {
    "provider": "Microsoft.CognitiveServices",
    "category": "Cost",
    "amount": 125,
    "timeGrain": "Monthly",
    "timePeriod": {"startDate": "2026-11-01T00:00:00Z", "endDate": "2026-12-01T00:00:00Z"},
    "grouping": [{"name": "agent", "type": "AdditionalInfoKey"}],
    "filter": {"additionalInfo": {"name": "project", "operator": "In", "values": ["project"]}},
    "notifications": {
        "budget-alert": {
            "eventGridConnectionId": f"{ACCOUNT_ID}/connections/event-grid",
            "thresholdType": "Percentage",
            "threshold": 80,
            "enabled": True,
            "operator": "GreaterThanOrEqualTo",
        }
    },
    "providerProperties": {
        "actions": {
            "budget-block": {
                "type": "Block",
                "thresholdType": "Absolute",
                "threshold": 125,
                "operator": "GreaterThanOrEqualTo",
            }
        }
    },
}

PATCH_CASES = [
    pytest.param({}, id="omitted-properties"),
    pytest.param({"properties": None}, id="clear-properties-null"),
    pytest.param({"properties": {}}, id="clear-properties-empty"),
    pytest.param({"properties": {"filter": None}}, id="clear-filter"),
    pytest.param({"properties": {"grouping": []}}, id="reset-grouping"),
    pytest.param({"properties": {"notifications": None}}, id="clear-notifications"),
    pytest.param({"properties": {"notifications": {}}}, id="preserve-notifications"),
    pytest.param({"properties": {"notifications": {"budget-alert": None}}}, id="delete-notification"),
    pytest.param({"properties": {"notifications": {"budget-alert": {"enabled": False}}}}, id="disable-notification"),
    pytest.param({"properties": {"providerProperties": None}}, id="clear-provider-properties"),
    pytest.param({"properties": {"providerProperties": {}}}, id="preserve-provider-properties"),
    pytest.param({"properties": {"providerProperties": {"actions": None}}}, id="clear-actions"),
    pytest.param({"properties": {"providerProperties": {"actions": {}}}}, id="preserve-actions"),
    pytest.param({"properties": {"providerProperties": {"actions": {"budget-block": None}}}}, id="delete-action"),
    pytest.param(
        {"properties": {"providerProperties": {"actions": {"budget-block": {"threshold": 100}}}}},
        id="update-action-threshold",
    ),
    pytest.param({"properties": {"timePeriod": {"endDate": "2027-01-01T00:00:00Z"}}}, id="extend-validity"),
]


def _cost_control_case(scope):
    parent_id = ACCOUNT_ID if scope == "account" else f"{ACCOUNT_ID}/projects/project"
    resource_type = "Microsoft.CognitiveServices/accounts"
    if scope == "project":
        resource_type += "/projects"
    return SimpleNamespace(
        operations_name=f"{scope}_cost_controls",
        parent_args=("rg", "acct") if scope == "account" else ("rg", "acct", "project"),
        parent_id=parent_id,
        model_type=models.AccountCostControl if scope == "account" else models.ProjectCostControl,
        response={
            "id": f"{parent_id}/costControls/monthly-budget",
            "name": "monthly-budget",
            "type": f"{resource_type}/costControls",
            "etag": '"body-etag"',
            "properties": deepcopy(BUDGET_PROPERTIES),
        },
    )


@pytest.fixture(params=["account", "project"])
def cost_control_case(request):
    return _cost_control_case(request.param)


class _FakeCredential:
    def get_token(self, *scopes, **kwargs):  # pylint: disable=unused-argument
        return AccessToken("fake-token", int(time.time()) + 3600)


class _FakeHttpResponse:
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

    def read(self, *args, **kwargs):  # pylint: disable=unused-argument
        return self.content

    def iter_bytes(self, *args, **kwargs):  # pylint: disable=unused-argument
        return iter([self.content])

    def iter_raw(self, *args, **kwargs):  # pylint: disable=unused-argument
        return iter([self.content])


def _make_client(status_code=200, body=None, headers=None):
    client = CognitiveServicesManagementClient(
        credential=_FakeCredential(),
        subscription_id=SUBSCRIPTION_ID,
    )

    def send(request, **kwargs):  # pylint: disable=unused-argument
        response = _FakeHttpResponse(request, status_code, body, headers)
        return SimpleNamespace(http_request=request, http_response=response, context={})

    client._client._pipeline.run = MagicMock(side_effect=send)  # pylint: disable=protected-access
    return client


def _request(client):
    return client._client._pipeline.run.call_args.args[0]  # pylint: disable=protected-access


def _json_body(request):
    content = request.content
    if isinstance(content, bytes):
        content = content.decode("utf-8")
    return json.loads(content)


def test_create_serializes_budget_and_if_none_match(cost_control_case):
    client = _make_client(201, cost_control_case.response, {"ETag": '"response-etag"'})
    budget = cost_control_case.model_type(properties=models.CostControlProperties(deepcopy(BUDGET_PROPERTIES)))

    result = getattr(client, cost_control_case.operations_name).create_or_update(
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
    assert result.properties.time_period.start_date == datetime(2026, 11, 1, tzinfo=timezone.utc)


def test_get_deserializes_cost_control_and_etag_header(cost_control_case):
    client = _make_client(200, cost_control_case.response, {"ETag": '"response-etag"'})

    result, response_headers = getattr(client, cost_control_case.operations_name).get(
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


def test_update_sends_if_match_and_partial_budget(cost_control_case):
    client = _make_client(200, cost_control_case.response, {"ETag": '"updated-etag"'})
    patch = models.CostControlPatch(properties=models.CostControlPatchProperties(amount=150))

    getattr(client, cost_control_case.operations_name).update(
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


def test_list_deserializes_cost_controls(cost_control_case):
    client = _make_client(200, {"value": [cost_control_case.response], "nextLink": None})

    result = list(getattr(client, cost_control_case.operations_name).list(*cost_control_case.parent_args))

    request = _request(client)
    assert request.method == "GET"
    assert request.url.endswith(f"{cost_control_case.parent_id}/costControls?api-version={API_VERSION}")
    assert [cost_control.name for cost_control in result] == ["monthly-budget"]


def test_delete_sends_if_match(cost_control_case):
    client = _make_client(204)

    result = getattr(client, cost_control_case.operations_name).delete(
        *cost_control_case.parent_args,
        "monthly-budget",
        etag='"body-etag"',
        match_condition=MatchConditions.IfNotModified,
    )

    request = _request(client)
    assert result is None
    assert request.method == "DELETE"
    assert request.headers["If-Match"] == '"body-etag"'


@pytest.mark.parametrize("payload", PATCH_CASES)
def test_update_preserves_patch_payload(cost_control_case, payload):
    client = _make_client(200, cost_control_case.response)

    getattr(client, cost_control_case.operations_name).update(
        *cost_control_case.parent_args,
        "monthly-budget",
        models.CostControlPatch(deepcopy(payload)),
    )

    request = _request(client)
    assert request.method == "PATCH"
    assert request.url.endswith(f"{cost_control_case.parent_id}/costControls/monthly-budget?api-version={API_VERSION}")
    assert _json_body(request) == payload


def test_create_serializes_token_budget_and_conjunctive_filter(cost_control_case):
    properties = deepcopy(BUDGET_PROPERTIES)
    properties.update(
        category="Tokens",
        amount=10000,
        timeGrain="Daily",
        filter={
            "and": [
                {"additionalInfo": {"name": "project", "operator": "In", "values": ["project"]}},
                {"additionalInfo": {"name": "tokenType", "operator": "In", "values": ["input", "output"]}},
            ]
        },
    )
    response = deepcopy(cost_control_case.response)
    response["properties"] = properties
    client = _make_client(201, response)

    result = getattr(client, cost_control_case.operations_name).create_or_update(
        *cost_control_case.parent_args,
        "monthly-budget",
        cost_control_case.model_type(properties=models.CostControlProperties(properties)),
    )

    assert _json_body(_request(client)) == {"properties": properties}
    assert result.properties.category == "Tokens"
    assert result.properties.time_grain == "Daily"


def test_check_existence_uses_head_and_returns_etag(cost_control_case):
    client = _make_client(200, headers={"ETag": '"head-etag"'})
    operations = getattr(client, cost_control_case.operations_name)

    assert operations.check_existence(*cost_control_case.parent_args, "monthly-budget") is True
    response_headers = operations.check_existence(
        *cost_control_case.parent_args, "monthly-budget", cls=lambda _, model, headers: headers
    )

    request = _request(client)
    assert request.method == "HEAD"
    assert request.url.endswith(f"{cost_control_case.parent_id}/costControls/monthly-budget?api-version={API_VERSION}")
    assert response_headers["ETag"] == '"head-etag"'


@pytest.mark.parametrize(
    "status_code,error_code",
    [(400, "BadRequest"), (403, "FeatureNotRegistered"), (412, "PreconditionFailed")],
)
def test_update_propagates_service_errors(cost_control_case, status_code, error_code):
    client = _make_client(status_code, {"error": {"code": error_code, "message": "Update rejected"}})

    with pytest.raises(HttpResponseError) as error:
        getattr(client, cost_control_case.operations_name).update(
            *cost_control_case.parent_args,
            "monthly-budget",
            models.CostControlPatch(properties=models.CostControlPatchProperties(amount=150)),
            etag='"stale-etag"',
            match_condition=MatchConditions.IfNotModified,
        )

    assert error.value.status_code == status_code
    assert error.value.error.code == error_code


def test_account_update_serializes_explicit_null_cost_control_connections():
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

    client.accounts.begin_update(
        "rg",
        "acct",
        {"properties": {"costControlConnections": None}},
        polling=False,
    )

    request = _request(client)
    assert request.method == "PATCH"
    assert _json_body(request)["properties"]["costControlConnections"] is None
