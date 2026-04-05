# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for multi-modality payloads with InvocationAgentServerHost + InvocationAgentServerHost."""
import json

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from azure.ai.agentserver.invocations import InvocationAgentServerHost



# ---------------------------------------------------------------------------
# Helper: content-type echo agent
# ---------------------------------------------------------------------------

def _make_content_type_echo_agent() -> InvocationAgentServerHost:
    """Agent that echoes body and returns the content-type it received."""
    app = InvocationAgentServerHost()

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        body = await request.body()
        ct = request.headers.get("content-type", "unknown")
        return Response(
            content=body,
            media_type=ct,
            headers={"x-received-content-type": ct},
        )

    return app


def _make_status_code_agent() -> InvocationAgentServerHost:
    """Agent that returns a custom HTTP status code from query param."""
    app = InvocationAgentServerHost()

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        status = int(request.query_params.get("status", "200"))
        body = await request.body()
        return Response(content=body, status_code=status)

    return app


def _make_sse_agent() -> InvocationAgentServerHost:
    """Agent that returns SSE-formatted streaming response."""
    app = InvocationAgentServerHost()

    @app.invoke_handler
    async def handle(request: Request) -> StreamingResponse:
        async def generate():
            for i in range(3):
                yield f"data: {json.dumps({'event': i})}\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    return app


# ---------------------------------------------------------------------------
# Various content types
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_png_content_type():
    """PNG content type is accepted and echoed."""
    server = _make_content_type_echo_agent()
    transport = ASGITransport(app=server)
    fake_png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post(
            "/invocations",
            content=fake_png,
            headers={"content-type": "image/png"},
        )
    assert resp.status_code == 200
    assert resp.headers["x-received-content-type"] == "image/png"
    assert resp.content == fake_png


@pytest.mark.asyncio
async def test_jpeg_content_type():
    """JPEG content type is accepted."""
    server = _make_content_type_echo_agent()
    transport = ASGITransport(app=server)
    fake_jpeg = b"\xff\xd8\xff\xe0" + b"\x00" * 100
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post(
            "/invocations",
            content=fake_jpeg,
            headers={"content-type": "image/jpeg"},
        )
    assert resp.status_code == 200
    assert resp.headers["x-received-content-type"] == "image/jpeg"


@pytest.mark.asyncio
async def test_wav_content_type():
    """WAV audio content type is accepted."""
    server = _make_content_type_echo_agent()
    transport = ASGITransport(app=server)
    fake_wav = b"RIFF" + b"\x00" * 100
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post(
            "/invocations",
            content=fake_wav,
            headers={"content-type": "audio/wav"},
        )
    assert resp.status_code == 200
    assert resp.headers["x-received-content-type"] == "audio/wav"


@pytest.mark.asyncio
async def test_pdf_content_type():
    """PDF content type is accepted."""
    server = _make_content_type_echo_agent()
    transport = ASGITransport(app=server)
    fake_pdf = b"%PDF-1.4" + b"\x00" * 100
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post(
            "/invocations",
            content=fake_pdf,
            headers={"content-type": "application/pdf"},
        )
    assert resp.status_code == 200
    assert resp.headers["x-received-content-type"] == "application/pdf"


@pytest.mark.asyncio
async def test_octet_stream_content_type():
    """application/octet-stream is accepted."""
    server = _make_content_type_echo_agent()
    transport = ASGITransport(app=server)
    binary = bytes(range(256))
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post(
            "/invocations",
            content=binary,
            headers={"content-type": "application/octet-stream"},
        )
    assert resp.status_code == 200
    assert resp.content == binary


@pytest.mark.asyncio
async def test_text_plain_content_type():
    """text/plain content type is accepted."""
    server = _make_content_type_echo_agent()
    transport = ASGITransport(app=server)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post(
            "/invocations",
            content=b"Hello, world!",
            headers={"content-type": "text/plain"},
        )
    assert resp.status_code == 200
    assert resp.content == b"Hello, world!"


# ---------------------------------------------------------------------------
# Custom HTTP status codes
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_custom_status_200():
    """Handler returning 200."""
    server = _make_status_code_agent()
    transport = ASGITransport(app=server)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations?status=200", content=b"ok")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_custom_status_201():
    """Handler returning 201."""
    server = _make_status_code_agent()
    transport = ASGITransport(app=server)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations?status=201", content=b"created")
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_custom_status_202():
    """Handler returning 202."""
    server = _make_status_code_agent()
    transport = ASGITransport(app=server)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations?status=202", content=b"accepted")
    assert resp.status_code == 202


# ---------------------------------------------------------------------------
# Query strings
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_query_string_passed_to_handler():
    """Query string params are accessible in the handler."""
    app = InvocationAgentServerHost()

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        name = request.query_params.get("name", "unknown")
        return JSONResponse({"name": name})

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations?name=Alice", content=b"")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Alice"


# ---------------------------------------------------------------------------
# SSE streaming
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_sse_streaming():
    """SSE-formatted streaming response works."""
    server = _make_sse_agent()
    transport = ASGITransport(app=server)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations", content=b"")
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers.get("content-type", "")
    lines = [line for line in resp.text.split("\n") if line.startswith("data:")]
    assert len(lines) == 3


# ---------------------------------------------------------------------------
# Large binary payloads
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_large_binary_payload():
    """Large binary payload (512KB) is handled correctly."""
    server = _make_content_type_echo_agent()
    transport = ASGITransport(app=server)
    payload = bytes(range(256)) * 2048  # 512KB
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post(
            "/invocations",
            content=payload,
            headers={"content-type": "application/octet-stream"},
        )
    assert resp.status_code == 200
    assert len(resp.content) == len(payload)


# ---------------------------------------------------------------------------
# Health endpoint (updated from /healthy to /readiness)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_health_endpoint_returns_200():
    """GET /readiness returns 200 with healthy status."""
    app = InvocationAgentServerHost()

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.get("/readiness")
    assert resp.status_code == 200
    assert resp.json() == {"status": "healthy"}
