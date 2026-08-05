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


@pytest.mark.asyncio
async def test_platform_error_detail_strips_control_characters(asgi_client):
    """CR/LF in exception text must not reach the error-detail header (no response splitting)."""

    async def handle(_request):
        exc = RuntimeError("bad\r\nInjected-Header: evil")
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
    detail = resp.headers[ERROR_DETAIL]
    assert "\r" not in detail and "\n" not in detail
    assert "injected-header" not in resp.headers


@pytest.mark.asyncio
async def test_platform_error_detail_drops_non_latin1(asgi_client):
    """Non-ASCII code points are dropped so Starlette can latin-1 encode the header."""

    async def handle(_request):
        exc = RuntimeError("caf\u00e9 \U0001f600 failure")  # accented + emoji
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
    detail = resp.headers[ERROR_DETAIL]
    detail.encode("latin-1")  # must not raise
    assert "\U0001f600" not in detail


@pytest.mark.asyncio
async def test_handler_error_status_is_classified_upstream(asgi_client):
    """A handler that returns a 4xx/5xx directly (without raising) is still classified."""
    from starlette.responses import JSONResponse

    async def handle(_request):
        return JSONResponse({"error": "bad gateway"}, status_code=502)

    app = ActivityAgentServerHost(request_handler=handle, configure_observability=None)
    async with asgi_client(app) as client:
        resp = await client.post(
            "/activity/messages",
            json={"type": "message", "text": "hello"},
            headers={"Authorization": "Bearer test-token", "x-agent-session-id": "session-123"},
        )

    assert resp.status_code == 502
    assert resp.headers[ERROR_SOURCE] == "upstream"


@pytest.mark.asyncio
async def test_handler_success_status_is_not_classified(asgi_client):
    """A successful (2xx) handler response carries no error-source header."""
    from starlette.responses import JSONResponse

    async def handle(_request):
        return JSONResponse({"ok": True})

    app = ActivityAgentServerHost(request_handler=handle, configure_observability=None)
    async with asgi_client(app) as client:
        resp = await client.post(
            "/activity/messages",
            json={"type": "message", "text": "hello"},
            headers={"Authorization": "Bearer test-token", "x-agent-session-id": "session-123"},
        )

    assert resp.status_code == 200
    assert ERROR_SOURCE not in resp.headers


@pytest.mark.asyncio
async def test_malformed_request_is_classified_user(asgi_client):
    """A caller validation error (non-object / missing body) is classified as user."""

    async def handle(_request):
        from starlette.responses import JSONResponse

        return JSONResponse({"ok": True})

    app = ActivityAgentServerHost(request_handler=handle, configure_observability=None)
    async with asgi_client(app) as client:
        resp = await client.post(
            "/activity/messages",
            json=["not", "an", "object"],
            headers={"Authorization": "Bearer test-token"},
        )

    assert resp.status_code == 400
    assert resp.headers[ERROR_SOURCE] == "user"

