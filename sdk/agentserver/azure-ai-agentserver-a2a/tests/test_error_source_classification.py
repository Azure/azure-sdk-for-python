# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for A2A transport-level error source classification."""

from collections.abc import Awaitable, Callable
from typing import cast
from unittest.mock import patch

import pytest
from a2a.server.request_handlers import RequestHandler
from a2a.types import AgentCapabilities, AgentCard, AgentInterface
from azure.ai.agentserver.core._platform_headers import (
    ERROR_DETAIL,
    ERROR_SOURCE,
    PLATFORM_ERROR_TAG,
)
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from azure.ai.agentserver.a2a import A2AAgentServerHost

_RPC_PATH = "/a2a"


def _agent_card() -> AgentCard:
    return AgentCard(
        name="error-test",
        description="error classification test agent",
        version="1.0.0",
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        capabilities=AgentCapabilities(),
        supported_interfaces=[
            AgentInterface(
                protocol_binding="JSONRPC",
                protocol_version="1.0",
                url="http://localhost:8088/a2a",
            )
        ],
        skills=[],
    )


def _host(endpoint: Callable[[Request], Awaitable[Response]]) -> A2AAgentServerHost:
    with patch(
        "azure.ai.agentserver.a2a._host.create_jsonrpc_routes",
        return_value=[Route(_RPC_PATH, endpoint, methods=["POST"])],
    ):
        return A2AAgentServerHost(
            agent_card=_agent_card(),
            request_handler=cast(RequestHandler, object()),
            configure_observability=None,
        )


@pytest.mark.asyncio
async def test_success_has_no_error_source(client_factory):
    async def endpoint(_request: Request) -> JSONResponse:
        return JSONResponse({"ok": True})

    async with client_factory(_host(endpoint)) as client:
        response = await client.post(_RPC_PATH)

    assert response.status_code == 200
    assert ERROR_SOURCE not in response.headers
    assert ERROR_DETAIL not in response.headers


@pytest.mark.asyncio
async def test_client_transport_error_is_classified_as_user(client_factory):
    async def endpoint(_request: Request) -> JSONResponse:
        return JSONResponse({"detail": "invalid request"}, status_code=400)

    async with client_factory(_host(endpoint)) as client:
        response = await client.post(_RPC_PATH)

    assert response.status_code == 400
    assert response.headers[ERROR_SOURCE] == "user"
    assert ERROR_DETAIL not in response.headers


@pytest.mark.asyncio
async def test_server_transport_error_is_classified_as_upstream(client_factory):
    async def endpoint(_request: Request) -> JSONResponse:
        return JSONResponse({"detail": "handler failed"}, status_code=500)

    async with client_factory(_host(endpoint)) as client:
        response = await client.post(_RPC_PATH)

    assert response.status_code == 500
    assert response.headers[ERROR_SOURCE] == "upstream"
    assert ERROR_DETAIL not in response.headers


@pytest.mark.asyncio
async def test_unhandled_exception_is_classified_as_upstream(client_factory):
    async def endpoint(_request: Request) -> JSONResponse:
        raise RuntimeError("handler failed")

    async with client_factory(_host(endpoint)) as client:
        response = await client.post(_RPC_PATH)

    assert response.status_code == 500
    assert response.headers[ERROR_SOURCE] == "upstream"
    assert ERROR_DETAIL not in response.headers


@pytest.mark.asyncio
async def test_platform_exception_includes_error_detail(client_factory):
    async def endpoint(_request: Request) -> JSONResponse:
        error = RuntimeError("storage unavailable")
        setattr(error, PLATFORM_ERROR_TAG, True)
        raise error

    async with client_factory(_host(endpoint)) as client:
        response = await client.post(_RPC_PATH)

    assert response.status_code == 500
    assert response.headers[ERROR_SOURCE] == "platform"
    assert "storage unavailable" in response.headers[ERROR_DETAIL]
