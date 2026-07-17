# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for ActivityAgentServerHost routes and endpoint behavior."""

import pytest
from starlette.responses import JSONResponse, Response

from azure.ai.agentserver.activity import ActivityAgentServerHost


@pytest.mark.asyncio
async def test_post_activity_returns_200(asgi_client):
    async def handle(request) -> Response:
        activity = request.state.activity
        return JSONResponse({"ok": True, "type": activity.get("type")})

    app = ActivityAgentServerHost(request_handler=handle, configure_observability=None)
    async with asgi_client(app) as client:
        resp = await client.post(
            "/activity/messages",
            json={"type": "message", "text": "hi"},
            headers={"Authorization": "Bearer test-token", "x-agent-session-id": "session-123"},
        )

    assert resp.status_code == 200
    assert resp.json()["ok"] is True
    assert "x-agent-activity-id" in resp.headers
    assert "x-agent-session-id" in resp.headers


@pytest.mark.asyncio
async def test_server_version_registers_activity_segment():
    """The host advertises the activity package in its server version segments."""
    from azure.ai.agentserver.activity._version import VERSION

    async def handle(_request):
        return None

    app = ActivityAgentServerHost(request_handler=handle, configure_observability=None)
    server_version = app._build_server_version()
    assert "azure-ai-agentserver-activity" in server_version
    assert VERSION in server_version


@pytest.mark.asyncio
async def test_post_activity_requires_json_object(asgi_client):
    async def handle(_request):
        return None

    app = ActivityAgentServerHost(request_handler=handle, configure_observability=None)
    async with asgi_client(app) as client:
        resp = await client.post(
            "/activity/messages",
            json=["not", "object"],
            headers={"Authorization": "Bearer test-token", "x-agent-session-id": "session-123"},
        )

    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_default_non_invoke_flow_returns_202_when_handler_returns_none(asgi_client):
    async def handle(_request):
        return Response(status_code=202)

    app = ActivityAgentServerHost(request_handler=handle, configure_observability=None)
    async with asgi_client(app) as client:
        resp = await client.post(
            "/activity/messages",
            json={"type": "message", "text": "hello"},
            headers={"Authorization": "Bearer test-token", "x-agent-session-id": "session-123"},
        )

    assert resp.status_code == 202


@pytest.mark.asyncio
async def test_invoke_response_path_returns_200_with_body(asgi_client):
    async def handle(_request):
        return JSONResponse({"status": 200, "body": {"message": "approved"}})

    app = ActivityAgentServerHost(request_handler=handle, configure_observability=None)
    async with asgi_client(app) as client:
        resp = await client.post(
            "/activity/messages",
            json={"type": "invoke", "name": "adaptiveCard/action", "value": {"verb": "approve"}},
            headers={"Authorization": "Bearer test-token", "x-agent-session-id": "session-123"},
        )

    assert resp.status_code == 200
    assert resp.json() == {"status": 200, "body": {"message": "approved"}}
