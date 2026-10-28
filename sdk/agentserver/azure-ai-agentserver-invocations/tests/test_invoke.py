# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the POST /invocations invoke dispatch."""
import json
import uuid
from importlib.metadata import requires

import pytest
import httpx
from opentelemetry import context as otel_context
from packaging.requirements import Requirement
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse

from azure.ai.agentserver.core import (
    FoundryAgentRequestContext,
    get_request_context,
    reset_request_context,
    set_request_context,
)
from azure.ai.agentserver.invocations import InvocationAgentServerHost
from azure.ai.agentserver.invocations import _invocation


def test_original_subject_core_dependency_floor():
    requirements = (Requirement(value) for value in requires("azure-ai-agentserver-invocations") or [])
    core = next(value for value in requirements if value.name == "azure-ai-agentserver-core")
    assert "2.3.0" in core.specifier
    assert "2.3.0b2" not in core.specifier
    assert "2.3.0b1" not in core.specifier
    assert "2.1.0" not in core.specifier
    assert callable(FoundryAgentRequestContext.model_attribution_headers)


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", ["invoke", "get", "cancel"])
@pytest.mark.parametrize("fields", [
    [("x-ms-original-subject", "malformed")],
    [("x-ms-original-subject", 'oid="one", oid="two"')],
    [("x-ms-original-subject", 'unknown="value"')],
    [("x-ms-original-subject", 'oid="one";parameter')],
    [("x-ms-original-subject", 'oid="one"'), ("x-ms-original-subject", 'tid="two"')],
])
async def test_malformed_original_subject_preserves_ambient_context(operation, fields):
    app = InvocationAgentServerHost(configure_observability=None)

    async def unexpected_dispatch(_request):
        pytest.fail("Malformed attribution must not reach a handler.")

    app.invoke_handler(unexpected_dispatch)
    request = Request({
        "type": "http",
        "method": "POST" if operation != "get" else "GET",
        "path": "/invocations",
        "path_params": {"invocation_id": "invocation-test"},
        "query_string": b"",
        "headers": [(name.encode(), value.encode()) for name, value in fields],
    })
    outer = FoundryAgentRequestContext(call_id="outer-call")
    token = set_request_context(outer)
    baggage = otel_context.get_current()
    invocation_id = _invocation._invocation_id_var.get()
    session_id = _invocation._session_id_var.get()
    try:
        if operation == "invoke":
            response = await app._create_invocation_endpoint(request)
        else:
            response = await app._traced_invocation_endpoint(request, operation, unexpected_dispatch)
        assert response.status_code == 400
        assert response.headers["x-platform-error-source"] == "platform"
        assert response.headers["x-platform-error-detail"] == "invalid_original_subject"
        assert get_request_context() is outer
        assert otel_context.get_current() == baggage
        assert _invocation._invocation_id_var.get() == invocation_id
        assert _invocation._session_id_var.get() == session_id
    finally:
        reset_request_context(token)


@pytest.mark.asyncio
@pytest.mark.parametrize("stream", [False, True])
async def test_invoke_original_subject_is_available_during_body_iteration(stream):
    app = InvocationAgentServerHost()

    @app.invoke_handler
    async def handler(_request):
        if stream:
            async def body():
                yield json.dumps(get_request_context().model_attribution_headers())
            return StreamingResponse(body(), media_type="application/json")
        return JSONResponse(get_request_context().model_attribution_headers())

    subject = {
        "x-ms-original-subject": 'oid="original-oid", tid="original-tid", idtype="app"',
    }
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.post("/invocations", headers={**subject, "x-agent-user-id": "state-key"})
        assert response.status_code == 200
        assert response.json() == subject
        response = await client.post("/invocations")
        assert response.status_code == 200
        assert response.json() == {}
    assert get_request_context().original_subject is None


# ---------------------------------------------------------------------------
# Echo body
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_invoke_echo_body(echo_client):
    """POST /invocations echoes the request body."""
    resp = await echo_client.post("/invocations", content=b"hello world")
    assert resp.status_code == 200
    assert resp.content == b"hello world"


# ---------------------------------------------------------------------------
# Headers
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_invoke_returns_invocation_id_header(echo_client):
    """Response includes x-agent-invocation-id header."""
    resp = await echo_client.post("/invocations", content=b"test")
    assert "x-agent-invocation-id" in resp.headers
    # Should be a valid UUID
    uuid.UUID(resp.headers["x-agent-invocation-id"])


@pytest.mark.asyncio
async def test_invoke_returns_session_id_header(echo_client):
    """Response includes x-agent-session-id header on POST /invocations."""
    resp = await echo_client.post("/invocations", content=b"test")
    assert "x-agent-session-id" in resp.headers
    # Should be a valid UUID (auto-generated)
    uuid.UUID(resp.headers["x-agent-session-id"])


@pytest.mark.asyncio
async def test_invoke_unique_invocation_ids(echo_client):
    """Each invoke gets a unique invocation ID."""
    ids = set()
    for _ in range(5):
        resp = await echo_client.post("/invocations", content=b"test")
        ids.add(resp.headers["x-agent-invocation-id"])
    assert len(ids) == 5


@pytest.mark.asyncio
async def test_invoke_accepts_custom_invocation_id(echo_client):
    """If the request sends x-agent-invocation-id, the server echoes it."""
    custom_id = str(uuid.uuid4())
    resp = await echo_client.post(
        "/invocations",
        content=b"test",
        headers={"x-agent-invocation-id": custom_id},
    )
    assert resp.headers["x-agent-invocation-id"] == custom_id


# ---------------------------------------------------------------------------
# Streaming
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_streaming_returns_chunks(streaming_client):
    """Streaming handler returns 3 JSON chunks."""
    resp = await streaming_client.post("/invocations", content=b"")
    assert resp.status_code == 200
    lines = resp.text.strip().split("\n")
    assert len(lines) == 3
    for i, line in enumerate(lines):
        assert json.loads(line) == {"chunk": i}


@pytest.mark.asyncio
async def test_streaming_has_invocation_id_header(streaming_client):
    """Streaming response includes invocation ID header."""
    resp = await streaming_client.post("/invocations", content=b"")
    assert "x-agent-invocation-id" in resp.headers
    uuid.UUID(resp.headers["x-agent-invocation-id"])


# ---------------------------------------------------------------------------
# Empty body
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_invoke_empty_body(echo_client):
    """Empty body doesn't crash the server."""
    resp = await echo_client.post("/invocations", content=b"")
    assert resp.status_code == 200
    assert resp.content == b""


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_invoke_error_returns_500(failing_client):
    """Handler exception returns 500 with generic message."""
    resp = await failing_client.post("/invocations", content=b"test")
    assert resp.status_code == 500
    body = resp.json()
    assert body["error"]["code"] == "internal_error"
    assert body["error"]["message"] == "Internal server error"


@pytest.mark.asyncio
async def test_invoke_error_has_invocation_id(failing_client):
    """Error response still includes invocation ID header."""
    resp = await failing_client.post("/invocations", content=b"test")
    assert "x-agent-invocation-id" in resp.headers


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_error_hides_details_by_default(failing_client):
    """Exception message is hidden in error responses."""
    resp = await failing_client.post("/invocations", content=b"")
    body = resp.json()
    assert "something went wrong" not in body["error"]["message"]
