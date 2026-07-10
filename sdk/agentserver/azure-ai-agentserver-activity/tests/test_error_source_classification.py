# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for x-platform-error-source classification in activity endpoints."""

import pytest
from azure.ai.agentserver.core._platform_headers import ERROR_DETAIL, ERROR_SOURCE, PLATFORM_ERROR_TAG

from azure.ai.agentserver.activity import ActivityAgentServerHost


@pytest.mark.asyncio
async def test_upstream_handler_error_is_classified_upstream(asgi_client):
    async def handle(_request):
        raise RuntimeError("handler bug")

    app = ActivityAgentServerHost(request_handler=handle, configure_observability=None)
    async with asgi_client(app) as client:
        resp = await client.post(
            "/activity/messages",
            json={"type": "message", "text": "hello"},
            headers={"Authorization": "Bearer test-token", "x-agent-session-id": "session-123"},
        )

    assert resp.status_code == 500
    assert resp.headers[ERROR_SOURCE] == "upstream"
    assert ERROR_DETAIL not in resp.headers


@pytest.mark.asyncio
async def test_platform_tagged_error_is_classified_platform_with_detail(asgi_client):
    async def handle(_request):
        exc = RuntimeError("platform storage failure")
        setattr(exc, PLATFORM_ERROR_TAG, True)
        raise exc

    app = ActivityAgentServerHost(request_handler=handle, configure_observability=None)
    async with asgi_client(app) as client:
        resp = await client.post(
            "/activity/messages",
            json={"type": "message", "text": "hello"},
            headers={"Authorization": "Bearer test-token", "x-agent-session-id": "session-123"},
        )

    assert resp.status_code == 500
    assert resp.headers[ERROR_SOURCE] == "platform"
    assert "platform storage failure" in resp.headers[ERROR_DETAIL]
