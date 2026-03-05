# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for invoke dispatch (streaming and non-streaming)."""
import json
import uuid

import pytest


@pytest.mark.asyncio
async def test_invoke_echoes_body(echo_client):
    """POST /invocations body is passed to invoke() and echoed back."""
    payload = b'{"message":"ping"}'
    resp = await echo_client.post("/invocations", content=payload)
    assert resp.status_code == 200
    assert resp.content == payload


@pytest.mark.asyncio
async def test_invoke_receives_headers(echo_client):
    """request.headers contains sent HTTP headers."""
    # EchoAgent echoes body; we just confirm the request succeeds with custom headers.
    resp = await echo_client.post(
        "/invocations",
        content=b"{}",
        headers={"X-Custom-Header": "test-value", "Content-Type": "application/json"},
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_invoke_receives_invocation_id(echo_client):
    """Response x-agent-invocation-id is a non-empty UUID string."""
    resp = await echo_client.post("/invocations", content=b"{}")
    invocation_id = resp.headers["x-agent-invocation-id"]
    assert invocation_id
    uuid.UUID(invocation_id)  # raises if not valid UUID


@pytest.mark.asyncio
async def test_invoke_invocation_id_unique(echo_client):
    """Two consecutive POST /invocations return different x-agent-invocation-id values."""
    resp1 = await echo_client.post("/invocations", content=b"{}")
    resp2 = await echo_client.post("/invocations", content=b"{}")
    id1 = resp1.headers["x-agent-invocation-id"]
    id2 = resp2.headers["x-agent-invocation-id"]
    assert id1 != id2


@pytest.mark.asyncio
async def test_invoke_streaming_returns_chunked(streaming_client):
    """Streaming agent returns a StreamingResponse."""
    resp = await streaming_client.post("/invocations", content=b"{}")
    assert resp.status_code == 200
    # The response should contain all chunks
    assert len(resp.content) > 0


@pytest.mark.asyncio
async def test_invoke_streaming_yields_all_chunks(streaming_client):
    """All chunks from the async generator are received by the client."""
    resp = await streaming_client.post("/invocations", content=b"{}")
    lines = resp.content.decode().strip().split("\n")
    chunks = [json.loads(line) for line in lines]
    assert len(chunks) == 3
    assert chunks[0]["chunk"] == 0
    assert chunks[1]["chunk"] == 1
    assert chunks[2]["chunk"] == 2


@pytest.mark.asyncio
async def test_invoke_streaming_has_invocation_id_header(streaming_client):
    """Streaming response also includes x-agent-invocation-id header."""
    resp = await streaming_client.post("/invocations", content=b"{}")
    invocation_id = resp.headers.get("x-agent-invocation-id")
    assert invocation_id is not None
    uuid.UUID(invocation_id)


@pytest.mark.asyncio
async def test_invoke_empty_body(echo_client):
    """POST /invocations with empty body doesn't crash."""
    resp = await echo_client.post("/invocations", content=b"")
    assert resp.status_code == 200
    assert resp.content == b""


@pytest.mark.asyncio
async def test_invoke_error_returns_500(failing_client):
    """When invoke() raises, server returns 500 with generic error message and invocation id."""
    resp = await failing_client.post("/invocations", content=b'{"key":"value"}')
    assert resp.status_code == 500
    data = resp.json()
    assert data["error"]["code"] == "internal_error"
    assert data["error"]["message"] == "Internal server error"
    assert resp.headers.get("x-agent-invocation-id") is not None


@pytest.mark.asyncio
async def test_invoke_error_hides_details_by_default(failing_client):
    """Without AGENT_DEBUG_ERRORS, the actual exception message is hidden."""
    resp = await failing_client.post("/invocations", content=b'{}')
    assert resp.status_code == 500
    assert resp.json()["error"]["message"] == "Internal server error"


@pytest.mark.asyncio
async def test_invoke_error_exposes_details_with_debug(monkeypatch, failing_client):
    """With AGENT_DEBUG_ERRORS set, the actual exception message is returned."""
    monkeypatch.setenv("AGENT_DEBUG_ERRORS", "1")
    resp = await failing_client.post("/invocations", content=b'{}')
    assert resp.status_code == 500
    assert resp.json()["error"]["message"] == "something went wrong"
