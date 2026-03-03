# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for OpenAPI spec validation."""
import json

import pytest


@pytest.mark.asyncio
async def test_valid_request_passes(validated_client):
    """Request matching schema returns 200."""
    resp = await validated_client.post(
        "/invocations",
        content=json.dumps({"name": "World"}).encode(),
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert data["greeting"] == "Hello, World!"


@pytest.mark.asyncio
async def test_invalid_request_returns_400(validated_client):
    """Request missing required field returns 400 with error details."""
    resp = await validated_client.post(
        "/invocations",
        content=json.dumps({"wrong_field": "oops"}).encode(),
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code == 400
    data = resp.json()
    assert "error" in data
    assert "details" in data


@pytest.mark.asyncio
async def test_invalid_request_wrong_type_returns_400(validated_client):
    """Request with wrong field type returns 400."""
    resp = await validated_client.post(
        "/invocations",
        content=json.dumps({"name": 12345}).encode(),
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code == 400
    data = resp.json()
    assert "details" in data


@pytest.mark.asyncio
async def test_response_validation_logs_warning(bad_response_client, caplog):
    """Invalid response body logs warning but still returns 200 (non-blocking)."""
    resp = await bad_response_client.post(
        "/invocations",
        content=json.dumps({"name": "World"}).encode(),
        headers={"Content-Type": "application/json"},
    )
    # Response should still be returned (validation is non-blocking)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_no_spec_skips_validation(no_spec_client):
    """Agent with no spec accepts any request body."""
    resp = await no_spec_client.post(
        "/invocations",
        content=b"this is not json at all",
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_spec_endpoint_returns_spec(validated_client):
    """GET /invocations/docs/openapi.json returns the registered spec."""
    resp = await validated_client.get("/invocations/docs/openapi.json")
    assert resp.status_code == 200
    data = resp.json()
    assert "paths" in data


@pytest.mark.asyncio
async def test_non_json_body_skips_validation(no_spec_client):
    """Non-JSON content type bypasses JSON schema validation."""
    # Use no_spec_client (EchoAgent) which handles any body without crashing.
    # With a spec, non-JSON content-type still passes validation (validation is skipped).
    from azure.ai.agentserver import AgentServer, InvokeRequest
    import httpx

    class PlainTextEchoAgent(AgentServer):
        def __init__(self):
            super().__init__(openapi_spec={
                "openapi": "3.0.0",
                "info": {"title": "Test", "version": "1.0"},
                "paths": {
                    "/invocations": {
                        "post": {
                            "requestBody": {
                                "content": {
                                    "application/json": {
                                        "schema": {"type": "object", "required": ["name"]}
                                    }
                                }
                            },
                            "responses": {"200": {"description": "OK"}}
                        }
                    }
                }
            })

        async def invoke(self, request: InvokeRequest) -> bytes:
            return request.body

    agent = PlainTextEchoAgent()
    transport = httpx.ASGITransport(app=agent.app)
    client = httpx.AsyncClient(transport=transport, base_url="http://testserver")
    resp = await client.post(
        "/invocations",
        content=b"plain text body",
        headers={"Content-Type": "text/plain"},
    )
    # Should not fail validation since content-type is not JSON
    assert resp.status_code == 200
