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
# Test agent implementations
# ---------------------------------------------------------------------------


class EchoAgent(AgentServer):
    """Echoes the request body back as-is."""

    async def invoke(self, request: Request) -> Response:
        body = await request.body()
        return Response(content=body, media_type="application/octet-stream")


class StreamingAgent(AgentServer):
    """Returns a multi-chunk streaming response."""

    async def invoke(self, request: Request) -> StreamingResponse:
        async def generate():
            for i in range(3):
                yield json.dumps({"chunk": i}).encode() + b"\n"

        return StreamingResponse(generate())


class AsyncStorageAgent(AgentServer):
    """Supports get_invocation and cancel_invocation via in-memory storage."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._store: dict[str, bytes] = {}

    async def invoke(self, request: Request) -> Response:
        body = await request.body()
        invocation_id = request.state.invocation_id
        result = json.dumps({"echo": body.decode()}).encode()
        self._store[invocation_id] = result
        return Response(content=result, media_type="application/json")

    async def get_invocation(self, request: Request) -> Response:
        invocation_id = request.state.invocation_id
        if invocation_id in self._store:
            return Response(content=self._store[invocation_id], media_type="application/json")
        return JSONResponse({"error": "not found"}, status_code=404)

    async def cancel_invocation(self, request: Request) -> Response:
        invocation_id = request.state.invocation_id
        if invocation_id in self._store:
            del self._store[invocation_id]
            return JSONResponse({"status": "cancelled"})
        return JSONResponse({"error": "not found"}, status_code=404)


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


class ValidatedAgent(AgentServer):
    """Agent with OpenAPI validation that returns a greeting."""

    def __init__(self):
        super().__init__(openapi_spec=SAMPLE_OPENAPI_SPEC)

    async def invoke(self, request: Request) -> Response:
        data = await request.json()
        return JSONResponse({"greeting": f"Hello, {data['name']}!"})


class FailingAgent(AgentServer):
    """Agent whose invoke() always raises an exception."""

    async def invoke(self, request: Request) -> Response:
        raise ValueError("something went wrong")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def echo_client():
    """httpx.AsyncClient wired to EchoAgent's ASGI app."""
    agent = EchoAgent()
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest_asyncio.fixture
async def streaming_client():
    """httpx.AsyncClient wired to StreamingAgent's ASGI app."""
    agent = StreamingAgent()
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.fixture
def async_storage_agent():
    """An AsyncStorageAgent instance."""
    return AsyncStorageAgent()


@pytest_asyncio.fixture
async def async_storage_client(async_storage_agent):
    """httpx.AsyncClient wired to AsyncStorageAgent's ASGI app."""
    transport = httpx.ASGITransport(app=async_storage_agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest_asyncio.fixture
async def validated_client():
    """httpx.AsyncClient wired to ValidatedAgent's ASGI app."""
    agent = ValidatedAgent()
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest_asyncio.fixture
async def no_spec_client():
    """httpx.AsyncClient wired to EchoAgent (no OpenAPI spec)."""
    agent = EchoAgent()
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest_asyncio.fixture
async def failing_client():
    """httpx.AsyncClient wired to FailingAgent's ASGI app."""
    agent = FailingAgent()
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
