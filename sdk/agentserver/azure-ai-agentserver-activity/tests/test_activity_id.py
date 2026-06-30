# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for activity ID handling (provided value used; missing -> UUID)."""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.responses import JSONResponse

from azure.ai.agentserver.activity import ActivityAgentServerHost


@pytest.mark.asyncio
async def test_provided_activity_id_is_used():
    async def handle(request):  # pylint: disable=unused-argument
        return JSONResponse({"ok": True})

    app = ActivityAgentServerHost(handler=handle, configure_observability=None)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post(
            "/activity/messages",
            json={"type": "message", "text": "hi", "id": "my-activity-123"},
            headers={"Authorization": "Bearer test-token"},
        )

    assert resp.status_code == 200
    assert resp.headers["x-agent-activity-id"] == "my-activity-123"


@pytest.mark.asyncio
async def test_missing_activity_id_generates_uuid():
    async def handle(request):  # pylint: disable=unused-argument
        return JSONResponse({"ok": True})

    app = ActivityAgentServerHost(handler=handle, configure_observability=None)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post(
            "/activity/messages",
            json={"type": "message", "text": "hi"},
            headers={"Authorization": "Bearer test-token"},
        )

    assert resp.status_code == 200
    activity_id = resp.headers["x-agent-activity-id"]
    # Should be a valid UUID
    uuid.UUID(activity_id)
