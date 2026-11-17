# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for basic server route registration with InvocationAgentServerHost + InvocationAgentServerHost."""
import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.requests import Request
from starlette.responses import Response

from azure.ai.agentserver.invocations import InvocationAgentServerHost

from conftest import SAMPLE_OPENAPI_SPEC


# ---------------------------------------------------------------------------
# POST /invocations returns 200
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_post_invocations_returns_200(echo_client):
    """POST /invocations returns 200 OK."""
    resp = await echo_client.post("/invocations", content=b"test")
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# POST /invocations returns invocation-id header (UUID)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_post_invocations_returns_uuid_invocation_id(echo_client):
    """POST /invocations returns a valid UUID in x-agent-invocation-id."""
    resp = await echo_client.post("/invocations", content=b"test")
    inv_id = resp.headers["x-agent-invocation-id"]
    parsed = uuid.UUID(inv_id)
    assert str(parsed) == inv_id


# ---------------------------------------------------------------------------
# GET openapi spec returns 404 when not set
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_openapi_spec_returns_404_when_not_set(no_spec_client):
    """GET /invocations/docs/openapi.json returns 404 when no spec registered."""
    resp = await no_spec_client.get("/invocations/docs/openapi.json")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET openapi spec returns spec when registered
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_openapi_spec_returns_spec_when_registered():
    """GET /invocations/docs/openapi.json returns the spec when registered."""
    app = InvocationAgentServerHost(openapi_spec=SAMPLE_OPENAPI_SPEC)

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.get("/invocations/docs/openapi.json")
    assert resp.status_code == 200
    assert resp.json() == SAMPLE_OPENAPI_SPEC


# ---------------------------------------------------------------------------
# GET asyncapi specs return 404 when not set
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_asyncapi_json_returns_404_when_not_set(no_spec_client):
    """GET /invocations/docs/asyncapi.json returns 404 when no spec registered."""
    resp = await no_spec_client.get("/invocations/docs/asyncapi.json")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_asyncapi_yaml_returns_404_when_not_set(no_spec_client):
    """GET /invocations/docs/asyncapi.yaml returns 404 when no spec registered."""
    resp = await no_spec_client.get("/invocations/docs/asyncapi.yaml")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET asyncapi specs return spec when registered
# ---------------------------------------------------------------------------

SAMPLE_ASYNCAPI_SPEC_JSON = {
    "asyncapi": "3.0.0",
    "info": {"title": "Test Agent", "version": "1.0.0"},
    "channels": {},
    "operations": {},
}

SAMPLE_ASYNCAPI_SPEC_YAML = (
    "asyncapi: 3.0.0\n"
    "info:\n"
    "  title: Test Agent\n"
    "  version: 1.0.0\n"
    "channels: {}\n"
    "operations: {}\n"
)


@pytest.mark.asyncio
async def test_get_asyncapi_json_returns_spec_when_registered():
    """GET /invocations/docs/asyncapi.json returns the spec when registered."""
    app = InvocationAgentServerHost(asyncapi_spec_json=SAMPLE_ASYNCAPI_SPEC_JSON)

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.get("/invocations/docs/asyncapi.json")
    assert resp.status_code == 200
    assert resp.json() == SAMPLE_ASYNCAPI_SPEC_JSON


@pytest.mark.asyncio
async def test_get_asyncapi_yaml_returns_spec_when_registered():
    """GET /invocations/docs/asyncapi.yaml returns the spec verbatim with YAML media type."""
    app = InvocationAgentServerHost(asyncapi_spec_yaml=SAMPLE_ASYNCAPI_SPEC_YAML)

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.get("/invocations/docs/asyncapi.yaml")
    assert resp.status_code == 200
    assert resp.text == SAMPLE_ASYNCAPI_SPEC_YAML
    assert resp.headers["content-type"].startswith("application/yaml")


@pytest.mark.asyncio
async def test_asyncapi_representations_are_independent():
    """Registering only JSON leaves YAML as 404 and vice versa (no format conversion)."""
    json_only = InvocationAgentServerHost(asyncapi_spec_json=SAMPLE_ASYNCAPI_SPEC_JSON)

    @json_only.invoke_handler
    async def handle_json_only(request: Request) -> Response:
        return Response(content=b"ok")

    transport = ASGITransport(app=json_only)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        assert (await client.get("/invocations/docs/asyncapi.json")).status_code == 200
        assert (await client.get("/invocations/docs/asyncapi.yaml")).status_code == 404

    yaml_only = InvocationAgentServerHost(asyncapi_spec_yaml=SAMPLE_ASYNCAPI_SPEC_YAML)

    @yaml_only.invoke_handler
    async def handle_yaml_only(request: Request) -> Response:
        return Response(content=b"ok")

    transport = ASGITransport(app=yaml_only)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        assert (await client.get("/invocations/docs/asyncapi.yaml")).status_code == 200
        assert (await client.get("/invocations/docs/asyncapi.json")).status_code == 404


def test_asyncapi_json_rejects_non_dict():
    """Constructor rejects non-dict asyncapi_spec_json to avoid silent misuse."""
    with pytest.raises(TypeError, match="asyncapi_spec_json must be dict"):
        InvocationAgentServerHost(asyncapi_spec_json="not a dict")  # type: ignore[arg-type]


def test_asyncapi_yaml_rejects_non_str():
    """Constructor rejects non-str asyncapi_spec_yaml to avoid stringified dict leaking to client."""
    with pytest.raises(TypeError, match="asyncapi_spec_yaml must be str"):
        InvocationAgentServerHost(asyncapi_spec_yaml={"not": "a string"})  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# GET /invocations/{id} returns 404 default
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_invocation_returns_404_default(echo_client):
    """GET /invocations/{id} returns 404 when no get handler registered."""
    resp = await echo_client.get("/invocations/some-id")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# POST /invocations/{id}/cancel returns 404 default
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_cancel_invocation_returns_404_default(echo_client):
    """POST /invocations/{id}/cancel returns 404 when no cancel handler."""
    resp = await echo_client.post("/invocations/some-id/cancel")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Unknown route returns 404
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_unknown_route_returns_404(echo_client):
    """Unknown route returns 404."""
    resp = await echo_client.get("/nonexistent")
    assert resp.status_code == 404
