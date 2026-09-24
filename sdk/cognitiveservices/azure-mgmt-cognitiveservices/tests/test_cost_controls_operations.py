# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Unit tests for Cost Control request serialization and response handling."""

import json
import time
from types import SimpleNamespace
from unittest.mock import MagicMock

from azure.core import MatchConditions
from azure.core.credentials import AccessToken
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient, models


SUBSCRIPTION_ID = "00000000-0000-0000-0000-000000000000"
RESOURCE_ID = (
    f"/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/rg/providers/"
    "Microsoft.CognitiveServices/accounts/acct/costControls/monthly-budget"
)

THRESHOLDS = [
    models.CostControlThreshold(type="percentage", value=80, action="alert"),
    models.CostControlThreshold(type="absolute", value=100, action="block"),
]
RULE = models.CostControlRule(
    name="project-budget",
    counter_key=[models.CostControlDimension(type="project")],
    unit="usd",
    amount=125,
    period="month",
    recurring=True,
    match=models.CostControlMatch(
        project_ids=[
            "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.CognitiveServices/accounts/acct/projects/project"
        ]
    ),
    thresholds=THRESHOLDS,
)
COST_CONTROL = models.CostControl(properties=models.CostControlProperties(display_name="Monthly budget", rules=[RULE]))
COST_CONTROL_RESPONSE = {
    "id": RESOURCE_ID,
    "name": "monthly-budget",
    "type": "Microsoft.CognitiveServices/accounts/costControls",
    "etag": '"body-etag"',
    "properties": {
        "displayName": "Monthly budget",
        "rules": [
            {
                "name": "project-budget",
                "counterKey": [{"type": "project"}],
                "unit": "usd",
                "amount": 125,
                "period": "month",
                "recurring": True,
                "match": {
                    "foundry.project.id": [
                        "/subscriptions/sub/resourceGroups/rg/providers/"
                        "Microsoft.CognitiveServices/accounts/acct/projects/project"
                    ]
                },
                "thresholds": [
                    {"type": "percentage", "value": 80, "action": "alert"},
                    {"type": "absolute", "value": 100, "action": "block"},
                ],
            }
        ],
    },
}


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


def test_create_serializes_thresholds_and_if_none_match():
    client = _make_client(201, COST_CONTROL_RESPONSE, {"ETag": '"response-etag"'})

    result = client.cost_controls.create_or_update(
        "rg",
        "acct",
        "monthly-budget",
        COST_CONTROL,
        etag="*",
        match_condition=MatchConditions.IfMissing,
    )

    request = _request(client)
    body = _json_body(request)
    assert request.method == "PUT"
    assert request.headers["If-None-Match"] == "*"
    assert body["properties"]["rules"][0]["thresholds"] == [
        {"type": "percentage", "value": 80, "action": "alert"},
        {"type": "absolute", "value": 100, "action": "block"},
    ]
    assert body["properties"]["rules"][0]["match"]["foundry.project.id"]
    assert result.properties.rules[0].thresholds[1].action == "block"


def test_get_deserializes_cost_control_and_etag_header():
    client = _make_client(200, COST_CONTROL_RESPONSE, {"ETag": '"response-etag"'})

    result, response_headers = client.cost_controls.get(
        "rg",
        "acct",
        "monthly-budget",
        cls=lambda _, model, headers: (model, headers),
    )

    request = _request(client)
    assert request.method == "GET"
    assert request.url.endswith("/costControls/monthly-budget?api-version=2026-09-15-preview")
    assert result.etag == '"body-etag"'
    assert response_headers["ETag"] == '"response-etag"'


def test_update_sends_if_match_and_replacement_rules():
    client = _make_client(200, COST_CONTROL_RESPONSE, {"ETag": '"updated-etag"'})
    patch = models.CostControlPatch(properties=models.CostControlPatchProperties(rules=[RULE]))

    client.cost_controls.update(
        "rg",
        "acct",
        "monthly-budget",
        patch,
        etag='"body-etag"',
        match_condition=MatchConditions.IfNotModified,
    )

    request = _request(client)
    assert request.method == "PATCH"
    assert request.headers["If-Match"] == '"body-etag"'
    assert _json_body(request)["properties"]["rules"][0]["name"] == "project-budget"


def test_list_deserializes_cost_controls():
    client = _make_client(200, {"value": [COST_CONTROL_RESPONSE], "nextLink": None})

    result = list(client.cost_controls.list("rg", "acct"))

    request = _request(client)
    assert request.method == "GET"
    assert request.url.endswith("/costControls?api-version=2026-09-15-preview")
    assert [cost_control.name for cost_control in result] == ["monthly-budget"]


def test_delete_sends_if_match():
    client = _make_client(204)

    result = client.cost_controls.delete(
        "rg",
        "acct",
        "monthly-budget",
        etag='"body-etag"',
        match_condition=MatchConditions.IfNotModified,
    )

    request = _request(client)
    assert result is None
    assert request.method == "DELETE"
    assert request.headers["If-Match"] == '"body-etag"'


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
