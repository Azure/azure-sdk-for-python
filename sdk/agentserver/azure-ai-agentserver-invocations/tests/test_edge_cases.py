# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Edge-case tests for InvocationAgentServerHost + InvocationAgentServerHost."""
import asyncio
import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse

from azure.ai.agentserver.invocations import InvocationAgentServerHost

from conftest import SAMPLE_OPENAPI_SPEC


# ---------------------------------------------------------------------------
# Factory helpers for edge cases
# ---------------------------------------------------------------------------


def _make_custom_header_agent() -> InvocationAgentServerHost:
    """Agent whose handler sets its own x-agent-invocation-id (should be overwritten)."""
    app = InvocationAgentServerHost()

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        resp = Response(content=b"ok")
        resp.headers["x-agent-invocation-id"] = "custom-id-from-handler"
        return resp

    return app


def _make_empty_streaming_agent() -> InvocationAgentServerHost:
    """Agent that returns an empty streaming response."""
    app = InvocationAgentServerHost()

    @app.invoke_handler
    async def handle(request: Request) -> StreamingResponse:
        async def generate():
            return
            yield  # noqa: E501 — make it a generator

        return StreamingResponse(generate(), media_type="text/plain")

    return app


def _make_large_payload_agent() -> InvocationAgentServerHost:
    """Agent that echoes large payloads."""
    app = InvocationAgentServerHost()

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        body = await request.body()
        return Response(content=body, media_type="application/octet-stream")

    return app


# ---------------------------------------------------------------------------
# Method not allowed tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_invocations_returns_405():
    """GET /invocations returns 405 Method Not Allowed."""
    app = InvocationAgentServerHost()

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.get("/invocations")
    assert resp.status_code == 405


@pytest.mark.asyncio
async def test_put_invocations_returns_405():
    """PUT /invocations returns 405 Method Not Allowed."""
    app = InvocationAgentServerHost()

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.put("/invocations", content=b"test")
    assert resp.status_code == 405


@pytest.mark.asyncio
async def test_delete_invocation_returns_405():
    """DELETE /invocations/{id} returns 405 Method Not Allowed."""
    app = InvocationAgentServerHost()

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.delete("/invocations/some-id")
    assert resp.status_code == 405


@pytest.mark.asyncio
async def test_post_openapi_json_returns_405():
    """POST /invocations/docs/openapi.json returns 405."""
    app = InvocationAgentServerHost(openapi_spec=SAMPLE_OPENAPI_SPEC)

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations/docs/openapi.json", content=b"{}")
    assert resp.status_code == 405


# ---------------------------------------------------------------------------
# Response header tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_custom_invocation_id_overwritten():
    """Handler-set x-agent-invocation-id is overwritten by the server."""
    server = _make_custom_header_agent()
    transport = ASGITransport(app=server)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations", content=b"test")
    # Server overwrites handler's value with a generated UUID
    inv_id = resp.headers["x-agent-invocation-id"]
    assert inv_id != "custom-id-from-handler"
    uuid.UUID(inv_id)  # Should be a valid UUID


@pytest.mark.asyncio
async def test_invocation_id_auto_injected(echo_client):
    """Invocation ID is auto-injected when not provided."""
    resp = await echo_client.post("/invocations", content=b"test")
    assert "x-agent-invocation-id" in resp.headers


@pytest.mark.asyncio
async def test_invocation_id_accepted_from_request(echo_client):
    """Server accepts invocation ID from request header."""
    custom_id = str(uuid.uuid4())
    resp = await echo_client.post(
        "/invocations",
        content=b"test",
        headers={"x-agent-invocation-id": custom_id},
    )
    assert resp.headers["x-agent-invocation-id"] == custom_id


@pytest.mark.asyncio
async def test_invocation_id_generated_when_empty(echo_client):
    """When empty invocation ID is sent, server generates one."""
    resp = await echo_client.post(
        "/invocations",
        content=b"test",
        headers={"x-agent-invocation-id": ""},
    )
    inv_id = resp.headers["x-agent-invocation-id"]
    uuid.UUID(inv_id)  # Should be a valid UUID


# ---------------------------------------------------------------------------
# Payload edge cases
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_large_payload():
    """Large payload (1MB) is handled correctly."""
    server = _make_large_payload_agent()
    transport = ASGITransport(app=server)
    payload = b"x" * (1024 * 1024)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations", content=payload)
    assert resp.status_code == 200
    assert len(resp.content) == 1024 * 1024


@pytest.mark.asyncio
async def test_unicode_payload(echo_client):
    """Unicode payload is preserved."""
    text = "Hello, 世界! 🌍"
    resp = await echo_client.post("/invocations", content=text.encode("utf-8"))
    assert resp.status_code == 200
    assert resp.content.decode("utf-8") == text


@pytest.mark.asyncio
async def test_binary_payload(echo_client):
    """Binary payload with non-UTF-8 bytes is handled."""
    binary = bytes(range(256))
    resp = await echo_client.post("/invocations", content=binary)
    assert resp.status_code == 200
    assert resp.content == binary


# ---------------------------------------------------------------------------
# Streaming edge cases
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_empty_streaming():
    """Empty streaming response doesn't crash."""
    server = _make_empty_streaming_agent()
    transport = ASGITransport(app=server)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations", content=b"test")
    assert resp.status_code == 200
    assert resp.content == b""


@pytest.mark.asyncio
async def test_streaming_has_invocation_id():
    """Streaming response has x-agent-invocation-id header."""
    app = InvocationAgentServerHost()

    @app.invoke_handler
    async def handle(request: Request) -> StreamingResponse:
        async def generate():
            yield b"chunk1"

        return StreamingResponse(generate(), media_type="text/plain")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations", content=b"test")
    assert "x-agent-invocation-id" in resp.headers


# ---------------------------------------------------------------------------
# Invocation lifecycle
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_multiple_gets(async_storage_client):
    """Multiple GETs for the same invocation return the same result."""
    resp = await async_storage_client.post("/invocations", content=b"multi-get")
    inv_id = resp.headers["x-agent-invocation-id"]

    for _ in range(3):
        get_resp = await async_storage_client.get(f"/invocations/{inv_id}")
        assert get_resp.status_code == 200
        assert get_resp.content == b"multi-get"


@pytest.mark.asyncio
async def test_double_cancel(async_storage_client):
    """Cancelling twice: second cancel returns 404."""
    resp = await async_storage_client.post("/invocations", content=b"cancel-twice")
    inv_id = resp.headers["x-agent-invocation-id"]

    cancel1 = await async_storage_client.post(f"/invocations/{inv_id}/cancel")
    assert cancel1.status_code == 200

    cancel2 = await async_storage_client.post(f"/invocations/{inv_id}/cancel")
    assert cancel2.status_code == 404


@pytest.mark.asyncio
async def test_invoke_cancel_get(async_storage_client):
    """Invoke → cancel → get returns 404."""
    resp = await async_storage_client.post("/invocations", content=b"icg")
    inv_id = resp.headers["x-agent-invocation-id"]

    await async_storage_client.post(f"/invocations/{inv_id}/cancel")
    get_resp = await async_storage_client.get(f"/invocations/{inv_id}")
    assert get_resp.status_code == 404


# ---------------------------------------------------------------------------
# Concurrency
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_concurrent_invocations_get_unique_ids():
    """10 concurrent POSTs each get unique invocation IDs."""
    app = InvocationAgentServerHost()

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        tasks = [client.post("/invocations", content=b"test") for _ in range(10)]
        responses = await asyncio.gather(*tasks)

    ids = {r.headers["x-agent-invocation-id"] for r in responses}
    assert len(ids) == 10
