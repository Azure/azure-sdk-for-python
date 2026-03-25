# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the POST /invocations invoke dispatch."""
import json
import uuid

import pytest


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
