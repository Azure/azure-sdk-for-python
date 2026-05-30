# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for x-request-id header on invocations responses.

The ``RequestIdMiddleware`` is wired in ``AgentServerHost`` (core) and
inherited by ``InvocationAgentServerHost``.  These tests verify the
header appears on invocations endpoints.

Note: Error body enrichment (``additionalInfo.request_id``) is a
Responses-only feature and is NOT applied to invocations error responses.
"""
import uuid

import pytest


# ---------------------------------------------------------------------------
# Header presence — success responses
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_invoke_returns_request_id_header(echo_client):
    """POST /invocations success response includes x-request-id."""
    resp = await echo_client.post("/invocations", content=b"hello")
    assert "x-request-id" in resp.headers
    assert resp.headers["x-request-id"]  # non-empty


@pytest.mark.asyncio
async def test_request_id_is_stable_per_request(echo_client):
    """Each request gets a unique x-request-id."""
    ids = set()
    for _ in range(5):
        resp = await echo_client.post("/invocations", content=b"x")
        ids.add(resp.headers["x-request-id"])
    assert len(ids) == 5


@pytest.mark.asyncio
async def test_request_id_echoes_incoming_header(echo_client):
    """When the client sends x-request-id, the same value is returned."""
    custom_id = uuid.uuid4().hex
    resp = await echo_client.post(
        "/invocations",
        content=b"test",
        headers={"x-request-id": custom_id},
    )
    assert resp.headers["x-request-id"] == custom_id


@pytest.mark.asyncio
async def test_readiness_returns_request_id(echo_client):
    """GET /readiness also gets x-request-id (middleware applies to all routes)."""
    resp = await echo_client.get("/readiness")
    assert resp.status_code == 200
    assert "x-request-id" in resp.headers


# ---------------------------------------------------------------------------
# Error responses — header present, but NO body enrichment
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_error_response_has_request_id_header(failing_client):
    """500 error response includes x-request-id header."""
    resp = await failing_client.post("/invocations", content=b"boom")
    assert resp.status_code == 500
    assert "x-request-id" in resp.headers
    assert resp.headers["x-request-id"]


@pytest.mark.asyncio
async def test_error_response_no_additional_info_enrichment(failing_client):
    """Invocations error bodies do NOT get additionalInfo.request_id (Responses-only)."""
    resp = await failing_client.post("/invocations", content=b"boom")
    assert resp.status_code == 500

    body = resp.json()
    error = body.get("error", {})
    # core's create_error_response doesn't include additionalInfo
    assert "additionalInfo" not in error
