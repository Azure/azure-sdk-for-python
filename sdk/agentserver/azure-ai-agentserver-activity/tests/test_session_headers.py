# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for session resolution and required response headers."""

from importlib.metadata import requires

import pytest
from packaging.requirements import Requirement
from starlette.responses import JSONResponse

from azure.ai.agentserver.activity import ActivityAgentServerHost
from azure.ai.agentserver.core import FoundryAgentRequestContext, get_request_context


def test_original_subject_core_dependency_floor():
    requirements = (Requirement(value) for value in requires("azure-ai-agentserver-activity") or [])
    core = next(value for value in requirements if value.name == "azure-ai-agentserver-core")
    assert "2.3.0b2" in core.specifier
    assert "2.3.0b1" not in core.specifier
    assert "2.0.0b8" not in core.specifier
    assert callable(FoundryAgentRequestContext.model_attribution_headers)


@pytest.mark.asyncio
@pytest.mark.parametrize("value", ["malformed", 'oid="one", oid="two"', 'unknown="value"'])
async def test_malformed_original_subject_is_classified_before_handler(value, asgi_client):
    handled = []

    async def handle(_request):
        handled.append(True)
        return JSONResponse(get_request_context().model_attribution_headers())

    app = ActivityAgentServerHost(request_handler=handle, configure_observability=None)
    payload = {"type": "message", "conversation": {"id": "conversation"}}
    async with asgi_client(app) as client:
        response = await client.post(
            "/activity/messages", json=payload,
            headers={"x-ms-original-subject": value, "Authorization": "Bearer test-token"},
        )
        assert response.status_code == 400
        assert response.headers["x-platform-error-source"] == "platform"
        assert response.headers["x-platform-error-detail"] == "invalid_original_subject"
        assert not handled
        response = await client.post(
            "/activity/messages", json=payload, headers={"Authorization": "Bearer test-token"},
        )
        assert response.status_code == 200
        assert response.json() == {}
    assert get_request_context().original_subject is None


@pytest.mark.asyncio
async def test_original_subject_comes_from_headers_not_activity_payload(asgi_client):
    async def handle(_request):
        return JSONResponse(get_request_context().model_attribution_headers())

    app = ActivityAgentServerHost(request_handler=handle, configure_observability=None)
    subject = {
        "x-ms-original-subject": 'oid="platform-original-oid", tid="platform-original-tid", idtype="user"',
    }
    payload = {
        "type": "message",
        "from": {"aadObjectId": "payload-spoof"},
        "channelData": {"tenant": {"id": "payload-spoof"}},
        "conversation": {"id": "conversation"},
    }
    async with asgi_client(app) as client:
        response = await client.post(
            "/activity/messages", json=payload,
            headers={**subject, "Authorization": "Bearer bot-token", "x-agent-user-id": "state-key"},
        )
        assert response.status_code == 200
        assert response.json() == subject
        response = await client.post(
            "/activity/messages", json=payload, headers={"Authorization": "Bearer bot-token"},
        )
        assert response.status_code == 200
        assert response.json() == {}
    assert get_request_context().original_subject is None


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
