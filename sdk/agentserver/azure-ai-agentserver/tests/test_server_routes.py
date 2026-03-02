# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for route registration and basic endpoint behavior."""
import uuid

import pytest


@pytest.mark.asyncio
async def test_post_invocations_returns_200(echo_client):
    """POST /invocations with valid body returns 200."""
    resp = await echo_client.post("/invocations", content=b'{"hello":"world"}')
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_post_invocations_returns_invocation_id_header(echo_client):
    """Response includes x-agent-invocation-id header in UUID format."""
    resp = await echo_client.post("/invocations", content=b'{"hello":"world"}')
    invocation_id = resp.headers.get("x-agent-invocation-id")
    assert invocation_id is not None
    # Validate UUID format
    uuid.UUID(invocation_id)


@pytest.mark.asyncio
async def test_get_openapi_spec_returns_404_when_not_set(echo_client):
    """GET /invocations/docs/openapi.json returns 404 if no spec registered."""
    resp = await echo_client.get("/invocations/docs/openapi.json")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_openapi_spec_returns_spec(validated_client):
    """GET /invocations/docs/openapi.json returns registered spec as JSON."""
    resp = await validated_client.get("/invocations/docs/openapi.json")
    assert resp.status_code == 200
    data = resp.json()
    assert data["openapi"] == "3.0.0"
    assert "/invocations" in data["paths"]


@pytest.mark.asyncio
async def test_get_invocation_returns_404_default(echo_client):
    """GET /invocations/{id} returns 404 when not overridden."""
    resp = await echo_client.get(f"/invocations/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_cancel_invocation_returns_404_default(echo_client):
    """POST /invocations/{id}/cancel returns 404 when not overridden."""
    resp = await echo_client.post(f"/invocations/{uuid.uuid4()}/cancel")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_unknown_route_returns_404(echo_client):
    """GET /unknown returns 404."""
    resp = await echo_client.get("/unknown")
    assert resp.status_code == 404
