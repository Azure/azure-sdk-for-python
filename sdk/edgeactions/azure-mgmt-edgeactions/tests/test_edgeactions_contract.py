# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Synthetic EdgeActions HTTP contract tests; these do not assert live service behavior."""

import base64
import inspect
import io
import json
from collections import deque
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest
import pytest_asyncio
from azure.core.credentials import AccessToken
from azure.core.exceptions import HttpResponseError
from azure.core.pipeline.transport import AsyncHttpTransport, HttpTransport
from azure.core.rest import AsyncHttpResponse, HttpResponse
from azure.core.utils import case_insensitive_dict
from azure.mgmt.edgeactions import EdgeActionsMgmtClient, models
from azure.mgmt.edgeactions.aio import EdgeActionsMgmtClient as AsyncEdgeActionsMgmtClient

SUBSCRIPTION = "00000000-0000-0000-0000-000000000000"
RESOURCE_ID = f"/subscriptions/{SUBSCRIPTION}/resourceGroups/rg/providers/Microsoft.Cdn/edgeActions/action"
RESOURCE_URL = f"https://management.azure.com{RESOURCE_ID}"
API_VERSION = "2026-10-01"
VERSION_PROPERTIES = {"deploymentType": "file", "isDefaultVersion": "False", "provisioningState": "Succeeded"}
GROUPS = [
    ("edge_actions", (), "", models.EdgeAction, models.EdgeActionUpdate),
    ("edge_action_versions", ("v1",), "/versions/v1", models.EdgeActionVersion, models.EdgeActionVersionUpdate),
    (
        "edge_action_execution_filters",
        ("filter",),
        "/executionFilters/filter",
        models.EdgeActionExecutionFilter,
        models.EdgeActionExecutionFilterUpdate,
    ),
]


async def resolve(value):
    return await value if inspect.isawaitable(value) else value


def request_body(request):
    content = request.content
    if hasattr(content, "read"):
        content = content.read()
    return json.loads(content)


@pytest_asyncio.fixture(params=[False, True], ids=["sync", "async"])
async def api(request):
    is_async = request.param
    responses = deque()
    requests = []

    def send(http_request, **kwargs):
        requests.append(http_request)
        assert responses, f"Unexpected HTTP request: {http_request.method} {http_request.url}"
        status, body, headers = responses.popleft()
        content = json.dumps(body).encode() if body is not None else b""
        response = Mock(spec=AsyncHttpResponse if is_async else HttpResponse)
        response.request = http_request
        response.status_code = status
        response.headers = case_insensitive_dict({"Content-Type": "application/json", **headers})
        response.reason = "Bad Request" if status == 400 else "OK"
        response.content_type = "application/json"
        response.content = content
        response.url = http_request.url
        response.is_closed = True
        response.is_stream_consumed = True
        response.text.return_value = content.decode()
        response.json.return_value = body
        response.read = AsyncMock(return_value=content) if is_async else Mock(return_value=content)
        response.iter_bytes.return_value = iter([content])
        return response

    transport = AsyncMock(spec=AsyncHttpTransport) if is_async else MagicMock(spec=HttpTransport)
    transport.send.side_effect = send
    credential = Mock(spec=["get_token"])
    token = AccessToken("offline-test-token", 4102444800)
    credential.get_token = AsyncMock(return_value=token) if is_async else Mock(return_value=token)
    client_class = AsyncEdgeActionsMgmtClient if is_async else EdgeActionsMgmtClient
    client = client_class(credential, SUBSCRIPTION, transport=transport, polling_interval=0)

    def respond(body=None, status=200, headers=None):
        responses.append((status, body, headers or {}))

    try:
        yield SimpleNamespace(client=client, respond=respond, requests=requests)
        assert not responses, "Expected HTTP responses were not consumed"
    finally:
        await resolve(client.close())


pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize("group,children,path,model,update_model", GROUPS)
async def test_get_uses_stable_api(api, group, children, path, model, update_model):
    api.respond({"id": RESOURCE_ID + path, "name": "resource", "location": "global"})
    result = await resolve(getattr(api.client, group).get("rg", "action", *children))
    assert isinstance(result, model)
    assert result.id == RESOURCE_ID + path
    assert [(r.method, r.url) for r in api.requests] == [("GET", f"{RESOURCE_URL}{path}?api-version={API_VERSION}")]


@pytest.mark.parametrize("group,children,path,model,update_model", GROUPS)
@pytest.mark.parametrize("operation", ["begin_create", "begin_update"])
@pytest.mark.parametrize("body_format", ["model", "mapping", "stream"])
async def test_resource_request_serialization(api, group, children, path, model, update_model, operation, body_format):
    body = {"tags": {"purpose": "test"}}
    if operation == "begin_create":
        body["location"] = "global"
        if group == "edge_actions":
            body["sku"] = {"name": "Standard", "tier": "Standard"}
        elif group == "edge_action_versions":
            body["properties"] = {"deploymentType": "file", "isDefaultVersion": "False"}
        else:
            body["properties"] = {
                "versionId": RESOURCE_ID + "/versions/v1",
                "executionFilterIdentifierHeaderName": "x-sdk-test",
                "executionFilterIdentifierHeaderValue": "test",
            }
    body_model = model if operation == "begin_create" else update_model
    payload = body_model(body) if body_format == "model" else body
    if body_format == "stream":
        payload = io.BytesIO(json.dumps(body).encode())
    api.respond({"id": RESOURCE_ID + path, "location": "global", **body})
    poller = await resolve(
        getattr(getattr(api.client, group), operation)("rg", "action", *children, payload, polling=False)
    )
    result = await resolve(poller.result())
    assert isinstance(result, model)
    assert result.tags == body["tags"]
    assert len(api.requests) == 1
    request = api.requests[0]
    assert request.method == ("PUT" if operation == "begin_create" else "PATCH")
    assert request.url == f"{RESOURCE_URL}{path}?api-version={API_VERSION}"
    assert request.headers["Content-Type"] == "application/json"
    assert request_body(request) == body


@pytest.mark.parametrize("tags", [{}, {"purpose": "replacement"}], ids=["cleared", "replaced"])
async def test_tag_patch_does_not_add_sku_or_properties(api, tags):
    body = models.EdgeActionUpdate(tags=tags)
    api.respond({"location": "global", "tags": tags})
    poller = await resolve(api.client.edge_actions.begin_update("rg", "action", body, polling=False))
    await resolve(poller.result())
    assert request_body(api.requests[0]) == {"tags": tags}


@pytest.mark.parametrize("body_format", ["model", "mapping"])
async def test_empty_patch_rejection(api, body_format):
    message = "The PATCH request body must contain at least one property."
    api.respond({"Error": {"Code": "400", "Message": message}}, status=400)
    body = models.EdgeActionUpdate() if body_format == "model" else {}
    with pytest.raises(HttpResponseError, match="PATCH request body must contain at least one property") as error:
        poller = await resolve(api.client.edge_actions.begin_update("rg", "action", body))
        await resolve(poller.result())
    assert error.value.status_code == 400
    assert len(api.requests) == 1
    assert request_body(api.requests[0]) == {}


async def test_version_update_preserves_explicit_false_string(api):
    body = models.EdgeActionVersionUpdate(
        properties=models.EdgeActionVersionUpdateProperties(deployment_type="file", is_default_version="False")
    )
    api.respond({"location": "global", "properties": VERSION_PROPERTIES})
    poller = await resolve(api.client.edge_action_versions.begin_update("rg", "action", "v1", body, polling=False))
    result = await resolve(poller.result())
    assert result.properties.is_default_version == "False"
    assert request_body(api.requests[0]) == {"properties": {"deploymentType": "file", "isDefaultVersion": "False"}}


async def test_execution_filter_update_wire_names(api):
    properties = {
        "versionId": RESOURCE_ID + "/versions/v2",
        "executionFilterIdentifierHeaderName": "x-sdk-test",
        "executionFilterIdentifierHeaderValue": "updated",
    }
    api.respond({"location": "global", "properties": properties})
    body = models.EdgeActionExecutionFilterUpdate(
        properties=models.EdgeActionExecutionFilterUpdateProperties(
            version_id=properties["versionId"],
            execution_filter_identifier_header_name=properties["executionFilterIdentifierHeaderName"],
            execution_filter_identifier_header_value=properties["executionFilterIdentifierHeaderValue"],
        )
    )
    poller = await resolve(
        api.client.edge_action_execution_filters.begin_update("rg", "action", "filter", body, polling=False)
    )
    result = await resolve(poller.result())
    assert result.properties.version_id == properties["versionId"]
    assert request_body(api.requests[0]) == {"properties": properties}


@pytest.mark.parametrize("body_format", ["model", "mapping", "stream"])
async def test_deploy_version_code_preserves_base64_content(api, body_format):
    content = base64.b64encode(b"function handler(event) { return event; }").decode()
    body = {"name": "v1", "content": content}
    payload = models.VersionCode(**body) if body_format == "model" else body
    if body_format == "stream":
        payload = io.BytesIO(json.dumps(body).encode())
    api.respond(VERSION_PROPERTIES)
    poller = await resolve(
        api.client.edge_action_versions.begin_deploy_version_code("rg", "action", "v1", payload, polling=False)
    )
    result = await resolve(poller.result())
    assert isinstance(result, models.EdgeActionVersionProperties)
    assert result.deployment_type == "file"
    assert len(api.requests) == 1
    assert api.requests[0].method == "POST"
    assert api.requests[0].url == f"{RESOURCE_URL}/versions/v1/deployVersionCode?api-version={API_VERSION}"
    assert request_body(api.requests[0]) == body


@pytest.mark.parametrize(
    "operation,route", [("begin_get_version_code", "getVersionCode"), ("begin_swap_default", "swapDefault")]
)
async def test_version_action_routes(api, operation, route):
    api.respond(
        {"name": "v1", "content": "aGVsbG8="} if route == "getVersionCode" else None,
        status=200 if route == "getVersionCode" else 204,
    )
    poller = await resolve(getattr(api.client.edge_action_versions, operation)("rg", "action", "v1", polling=False))
    result = await resolve(poller.result())
    if route == "getVersionCode":
        assert isinstance(result, models.VersionCode)
        assert base64.b64decode(result.content) == b"hello"
    else:
        assert result is None
    assert [(r.method, r.url) for r in api.requests] == [
        ("POST", f"{RESOURCE_URL}/versions/v1/{route}?api-version={API_VERSION}")
    ]


@pytest.mark.parametrize("group,children,path,model,update_model", GROUPS)
@pytest.mark.parametrize("status", [200, 202, 204])
async def test_delete_status_and_polling(api, group, children, path, model, update_model, status):
    url = f"{RESOURCE_URL}{path}?api-version={API_VERSION}"
    api.respond(status=status, headers={"Location": url, "Retry-After": "0"} if status == 202 else {})
    if status == 202:
        api.respond(status=204)
    poller = await resolve(getattr(api.client, group).begin_delete("rg", "action", *children))
    assert await resolve(poller.result()) is None
    assert [(r.method, r.url) for r in api.requests] == (
        [("DELETE", url), ("GET", url)] if status == 202 else [("DELETE", url)]
    )


@pytest.mark.parametrize("group,children,path,model,update_model", GROUPS)
@pytest.mark.parametrize("operation", ["begin_create", "begin_update"])
async def test_resource_lro_polls_and_deserializes_final_result(
    api, group, children, path, model, update_model, operation
):
    url = f"{RESOURCE_URL}{path}?api-version={API_VERSION}"
    polling_url = f"https://management.azure.com/subscriptions/{SUBSCRIPTION}/operations/test?api-version={API_VERSION}"
    api.respond(
        {"properties": {"provisioningState": "Provisioning"}},
        status=201 if operation == "begin_create" else 202,
        headers={"Azure-AsyncOperation": polling_url, "Retry-After": "0"},
    )
    api.respond({"status": "Succeeded"})
    api.respond({"id": RESOURCE_ID + path, "name": "completed", "location": "global"})
    body = {"location": "global"} if operation == "begin_create" else {"tags": {"purpose": "updated"}}
    poller = await resolve(getattr(getattr(api.client, group), operation)("rg", "action", *children, body))
    result = await resolve(poller.result())
    assert isinstance(result, model)
    assert result.name == "completed"
    assert [(r.method, r.url) for r in api.requests] == [
        ("PUT" if operation == "begin_create" else "PATCH", url),
        ("GET", polling_url),
        ("GET", url),
    ]


async def test_failed_lro_surfaces_service_error(api):
    polling_url = f"https://management.azure.com/subscriptions/{SUBSCRIPTION}/operations/test?api-version={API_VERSION}"
    api.respond(status=202, headers={"Azure-AsyncOperation": polling_url, "Retry-After": "0"})
    api.respond({"status": "Failed", "error": {"code": "DeploymentFailed", "message": "Code validation failed"}})
    with pytest.raises(HttpResponseError, match="Code validation failed"):
        poller = await resolve(
            api.client.edge_action_versions.begin_deploy_version_code(
                "rg", "action", "v1", models.VersionCode(name="v1", content="aGVsbG8=")
            )
        )
        await resolve(poller.result())
    assert [request.method for request in api.requests] == ["POST", "GET"]


@pytest.mark.parametrize("body", [{"sku": None}, {"sku": {"name": "Standard", "tier": "Standard"}}, {"tags": None}])
async def test_patch_service_rejections_are_not_swallowed(api, body):
    api.respond({"error": {"code": "InvalidRequest", "message": "Rejected update"}}, status=400)
    with pytest.raises(HttpResponseError, match="Rejected update") as error:
        poller = await resolve(api.client.edge_actions.begin_update("rg", "action", body))
        await resolve(poller.result())
    assert error.value.status_code == 400
    assert len(api.requests) == 1
    assert request_body(api.requests[0]) == body


@pytest.mark.parametrize(
    "group,operation,args,path",
    [
        ("edge_actions", "list_by_resource_group", ("rg",), RESOURCE_URL.rsplit("/", 1)[0]),
        (
            "edge_actions",
            "list_by_subscription",
            (),
            f"https://management.azure.com/subscriptions/{SUBSCRIPTION}/providers/Microsoft.Cdn/edgeActions",
        ),
        ("edge_action_versions", "list_by_edge_action", ("rg", "action"), RESOURCE_URL + "/versions"),
        ("edge_action_execution_filters", "list_by_edge_action", ("rg", "action"), RESOURCE_URL + "/executionFilters"),
    ],
)
async def test_list_follows_next_link(api, group, operation, args, path):
    next_link = f"{path}?api-version={API_VERSION}&$skiptoken=next"
    api.respond({"value": [{"name": "first", "location": "global"}], "nextLink": next_link})
    api.respond({"value": [{"name": "second", "location": "global"}]})
    pages = getattr(getattr(api.client, group), operation)(*args)
    items = [item async for item in pages] if hasattr(pages, "__aiter__") else list(pages)
    assert [item.name for item in items] == ["first", "second"]
    assert len(api.requests) == 2
    assert all(request.method == "GET" for request in api.requests)
    assert api.requests[0].url == f"{path}?api-version={API_VERSION}"
    assert "$skiptoken=next" in api.requests[1].url
    assert f"api-version={API_VERSION}" in api.requests[1].url
