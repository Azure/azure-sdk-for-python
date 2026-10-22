# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for activity ID handling (provided value used; missing -> UUID)."""

import uuid

import pytest
from starlette.responses import JSONResponse

from azure.ai.agentserver.activity import ActivityAgentServerHost


@pytest.mark.asyncio
async def test_provided_activity_id_is_used(asgi_client):
    async def handle(_request):
        return JSONResponse({"ok": True})

    app = ActivityAgentServerHost(request_handler=handle, configure_observability=None)
    async with asgi_client(app) as client:
        resp = await client.post(
            "/activity/messages",
            json={"type": "message", "text": "hi", "id": "my-activity-123"},
            headers={"Authorization": "Bearer test-token"},
        )

    assert resp.status_code == 200
    assert resp.headers["x-agent-activity-id"] == "my-activity-123"


@pytest.mark.asyncio
async def test_missing_activity_id_generates_uuid(asgi_client):
    async def handle(_request):
        return JSONResponse({"ok": True})

    app = ActivityAgentServerHost(request_handler=handle, configure_observability=None)
    async with asgi_client(app) as client:
        resp = await client.post(
            "/activity/messages",
            json={"type": "message", "text": "hi"},
            headers={"Authorization": "Bearer test-token"},
        )

    assert resp.status_code == 200
    activity_id = resp.headers["x-agent-activity-id"]
    # Should be a valid UUID
    uuid.UUID(activity_id)


@pytest.mark.asyncio
async def test_oversized_activity_id_falls_back_to_uuid(asgi_client):
    async def handle(_request):
        return JSONResponse({"ok": True})

    app = ActivityAgentServerHost(request_handler=handle, configure_observability=None)
    async with asgi_client(app) as client:
        resp = await client.post(
            "/activity/messages",
            json={"type": "message", "text": "hi", "id": "x" * 300},
            headers={"Authorization": "Bearer test-token"},
        )

    assert resp.status_code == 200
    activity_id = resp.headers["x-agent-activity-id"]
    assert len(activity_id) < 300
    uuid.UUID(activity_id)  # fallback UUID


@pytest.mark.asyncio
async def test_malformed_activity_id_falls_back_to_uuid(asgi_client):
    async def handle(_request):
        return JSONResponse({"ok": True})

    app = ActivityAgentServerHost(request_handler=handle, configure_observability=None)
    async with asgi_client(app) as client:
        resp = await client.post(
            "/activity/messages",
            json={"type": "message", "text": "hi", "id": "id with spaces & <script>"},
            headers={"Authorization": "Bearer test-token"},
        )

    assert resp.status_code == 200
    activity_id = resp.headers["x-agent-activity-id"]
    assert "<script>" not in activity_id
    uuid.UUID(activity_id)  # fallback UUID


@pytest.mark.asyncio
async def test_trailing_newline_activity_id_falls_back_to_uuid(asgi_client):
    """An id ending in a newline must be rejected (header-injection defense)."""

    async def handle(_request):
        return JSONResponse({"ok": True})

    app = ActivityAgentServerHost(request_handler=handle, configure_observability=None)
    async with asgi_client(app) as client:
        resp = await client.post(
            "/activity/messages",
            json={"type": "message", "text": "hi", "id": "valid-id\n"},
            headers={"Authorization": "Bearer test-token"},
        )

    assert resp.status_code == 200
    activity_id = resp.headers["x-agent-activity-id"]
    assert "\n" not in activity_id
    uuid.UUID(activity_id)  # fallback UUID


def test_scrub_for_log_strips_control_characters():
    """Untrusted values are stripped of CR/LF/tab so they cannot forge log lines."""
    from azure.ai.agentserver.activity._activity import _scrub_for_log

    assert _scrub_for_log("normal value") == "normal value"
    assert _scrub_for_log("evil\r\nInjected: line") == "evilInjected: line"
    assert _scrub_for_log("tab\there") == "tabhere"
    assert "\n" not in _scrub_for_log("a\nb")
    assert _scrub_for_log("") == ""

