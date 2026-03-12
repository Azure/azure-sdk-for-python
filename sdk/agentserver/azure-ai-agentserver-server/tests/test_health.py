# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for health check endpoints."""
import pytest


@pytest.mark.asyncio
async def test_liveness_returns_200(echo_client):
    """GET /liveness returns 200."""
    resp = await echo_client.get("/liveness")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "alive"


@pytest.mark.asyncio
async def test_readiness_returns_200(echo_client):
    """GET /readiness returns 200."""
    resp = await echo_client.get("/readiness")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ready"
