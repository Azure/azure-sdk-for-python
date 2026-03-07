# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Shared fixtures for azure-ai-agentserver tests."""
import json

import pytest
import pytest_asyncio
import httpx

from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from azure.ai.agentserver import AgentServer


# ---------------------------------------------------------------------------
# Agent factory functions (decorator pattern)
# ---------------------------------------------------------------------------


def _make_echo_agent(**kwargs) -> AgentServer:
    """Create an echo agent that returns the request body as-is."""
    server = AgentServer(**kwargs)

    @server.invoke_handler
    async def handle(request: Request) -> Response:
        body = await request.body()
        return Response(content=body, media_type="application/octet-stream")

    return server


def _make_streaming_agent(**kwargs) -> AgentServer:
    """Create an agent that returns a multi-chunk streaming response."""
    server = AgentServer(**kwargs)

    @server.invoke_handler
    async def handle(request: Request) -> StreamingResponse:
        async def generate():
            for i in range(3):
                yield json.dumps({"chunk": i}).encode() + b"\n"

        return StreamingResponse(generate())

    return server


def _make_async_storage_agent(**kwargs) -> AgentServer:
    """Create an agent with get/cancel support via in-memory storage."""
    store: dict[str, bytes] = {}
    server = AgentServer(**kwargs)
    server._store = store  # expose for test access

    @server.invoke_handler
    async def invoke(request: Request) -> Response:
        body = await request.body()
        invocation_id = request.state.invocation_id
        result = json.dumps({"echo": body.decode()}).encode()
        store[invocation_id] = result
        return Response(content=result, media_type="application/json")

    @server.get_invocation_handler
    async def get_invocation(request: Request) -> Response:
        invocation_id = request.state.invocation_id
        if invocation_id in store:
            return Response(content=store[invocation_id], media_type="application/json")
        return JSONResponse({"error": "not found"}, status_code=404)

    @server.cancel_invocation_handler
    async def cancel_invocation(request: Request) -> Response:
        invocation_id = request.state.invocation_id
        if invocation_id in store:
            del store[invocation_id]
            return JSONResponse({"status": "cancelled"})
        return JSONResponse({"error": "not found"}, status_code=404)

    return server


SAMPLE_OPENAPI_SPEC: dict = {
    "openapi": "3.0.0",
    "info": {"title": "Test", "version": "1.0"},
    "paths": {
        "/invocations": {
            "post": {
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                },
                                "required": ["name"],
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "greeting": {"type": "string"},
                                    },
                                    "required": ["greeting"],
                                }
                            }
                        }
                    }
                },
            }
        }
    },
}


def _make_validated_agent() -> AgentServer:
    """Create an agent with OpenAPI validation that returns a greeting."""
    server = AgentServer(openapi_spec=SAMPLE_OPENAPI_SPEC, enable_request_validation=True)

    @server.invoke_handler
    async def handle(request: Request) -> Response:
        data = await request.json()
        return JSONResponse({"greeting": f"Hello, {data['name']}!"})

    return server


def _make_failing_agent(**kwargs) -> AgentServer:
    """Create an agent whose invoke handler always raises."""
    server = AgentServer(**kwargs)

    @server.invoke_handler
    async def handle(request: Request) -> Response:
        raise ValueError("something went wrong")

    return server


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def echo_client():
    """httpx.AsyncClient wired to an echo agent's ASGI app."""
    server = _make_echo_agent()
    transport = httpx.ASGITransport(app=server.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest_asyncio.fixture
async def streaming_client():
    """httpx.AsyncClient wired to a streaming agent's ASGI app."""
    server = _make_streaming_agent()
    transport = httpx.ASGITransport(app=server.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.fixture
def async_storage_server():
    """An async storage agent instance."""
    return _make_async_storage_agent()


@pytest_asyncio.fixture
async def async_storage_client(async_storage_server):
    """httpx.AsyncClient wired to an async storage agent's ASGI app."""
    transport = httpx.ASGITransport(app=async_storage_server.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest_asyncio.fixture
async def validated_client():
    """httpx.AsyncClient wired to a validated agent's ASGI app."""
    server = _make_validated_agent()
    transport = httpx.ASGITransport(app=server.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest_asyncio.fixture
async def no_spec_client():
    """httpx.AsyncClient wired to an echo agent (no OpenAPI spec)."""
    server = _make_echo_agent()
    transport = httpx.ASGITransport(app=server.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest_asyncio.fixture
async def failing_client():
    """httpx.AsyncClient wired to a failing agent's ASGI app."""
    server = _make_failing_agent()
    transport = httpx.ASGITransport(app=server.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
