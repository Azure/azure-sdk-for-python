# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Shared fixtures for azure-ai-agentserver tests."""
import json
from typing import AsyncGenerator, Optional

import pytest
import httpx

from azure.ai.agentserver import AgentServer, InvokeRequest


# ---------------------------------------------------------------------------
# Test agent implementations
# ---------------------------------------------------------------------------


class EchoAgent(AgentServer):
    """Echoes the request body back as-is."""

    async def invoke(self, request: InvokeRequest) -> bytes:
        return request.body


class StreamingAgent(AgentServer):
    """Returns a multi-chunk streaming response."""

    async def invoke(self, request: InvokeRequest) -> AsyncGenerator[bytes, None]:
        for i in range(3):
            yield json.dumps({"chunk": i}).encode() + b"\n"


class AsyncStorageAgent(AgentServer):
    """Supports get_invocation and cancel_invocation via in-memory storage."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._store: dict[str, bytes] = {}

    async def invoke(self, request: InvokeRequest) -> bytes:
        result = json.dumps({"echo": request.body.decode()}).encode()
        self._store[request.invocation_id] = result
        return result

    async def get_invocation(self, invocation_id: str) -> bytes:
        if invocation_id in self._store:
            return self._store[invocation_id]
        raise NotImplementedError

    async def cancel_invocation(
        self,
        invocation_id: str,
        body: Optional[bytes] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> bytes:
        if invocation_id in self._store:
            del self._store[invocation_id]
            return json.dumps({"status": "cancelled"}).encode()
        raise NotImplementedError


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

    async def invoke(self, request: InvokeRequest) -> bytes:
        data = json.loads(request.body)
        return json.dumps({"greeting": f"Hello, {data['name']}!"}).encode()


class BadResponseAgent(AgentServer):
    """Agent with OpenAPI validation that returns a non-conforming response."""

    def __init__(self):
        super().__init__(openapi_spec=SAMPLE_OPENAPI_SPEC)

    async def invoke(self, request: InvokeRequest) -> bytes:
        # Returns a response missing the required 'greeting' field
        return json.dumps({"wrong_field": "oops"}).encode()


class FailingAgent(AgentServer):
    """Agent whose invoke() always raises an exception."""

    async def invoke(self, request: InvokeRequest) -> bytes:
        raise ValueError("something went wrong")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
async def echo_client():
    """httpx.AsyncClient wired to EchoAgent's ASGI app."""
    agent = EchoAgent()
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.fixture
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


@pytest.fixture
async def async_storage_client(async_storage_agent):
    """httpx.AsyncClient wired to AsyncStorageAgent's ASGI app."""
    transport = httpx.ASGITransport(app=async_storage_agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.fixture
async def validated_client():
    """httpx.AsyncClient wired to ValidatedAgent's ASGI app."""
    agent = ValidatedAgent()
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.fixture
async def bad_response_client():
    """httpx.AsyncClient wired to BadResponseAgent's ASGI app."""
    agent = BadResponseAgent()
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.fixture
async def no_spec_client():
    """httpx.AsyncClient wired to EchoAgent (no OpenAPI spec)."""
    agent = EchoAgent()
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.fixture
async def failing_client():
    """httpx.AsyncClient wired to FailingAgent's ASGI app."""
    agent = FailingAgent()
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
