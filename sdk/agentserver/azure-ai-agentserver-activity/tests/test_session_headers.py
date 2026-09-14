# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for session resolution and required response headers."""

import pytest
from starlette.responses import JSONResponse

from azure.ai.agentserver.activity import ActivityAgentServerHost


@pytest.mark.asyncio
async def test_session_resolution_prefers_query_param(asgi_client):
    async def handle(_request):
        return JSONResponse({"ok": True})

    app = ActivityAgentServerHost(request_handler=handle, configure_observability=None)
    async with asgi_client(app) as client:
        resp = await client.post(
            "/activity/messages?agent_session_id=query-session",
            json={"type": "message", "text": "hello", "conversation": {"id": "conv-1"}},
            headers={"Authorization": "Bearer test-token", "x-agent-session-id": "header-session"},
        )

    assert resp.status_code == 200
    assert resp.headers["x-agent-session-id"] == "query-session"


@pytest.mark.asyncio
async def test_session_resolution_uses_header_when_query_missing(asgi_client):
    async def handle(_request):
        return JSONResponse({"ok": True})

    app = ActivityAgentServerHost(request_handler=handle, configure_observability=None)
    async with asgi_client(app) as client:
        resp = await client.post(
            "/activity/messages",
            json={"type": "message", "text": "hello", "conversation": {"id": "conv-2"}},
            headers={"Authorization": "Bearer test-token", "x-agent-session-id": "header-session"},
        )

    assert resp.status_code == 200
    assert resp.headers["x-agent-session-id"] == "header-session"
