# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for A2A transport-level error source classification."""

from collections.abc import AsyncIterator, Awaitable, Callable
from typing import cast
from unittest.mock import patch

import pytest
from a2a.server.request_handlers import RequestHandler
from a2a.types import AgentCapabilities, AgentCard, AgentInterface
from azure.ai.agentserver.core._platform_headers import (
    ERROR_DETAIL,
    ERROR_SOURCE,
    PLATFORM_ERROR_TAG,
    REQUEST_ID,
    SERVER_VERSION,
)
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse
from starlette.routing import Route

from azure.ai.agentserver.a2a import A2AAgentServerHost

_RPC_PATH = "/a2a"
_RPC_PATHS = [_RPC_PATH, "/invocations/a2a"]
_CARD_PATHS = ["/a2a/.well-known/agent-card.json", "/invocations/a2a/.well-known/agent-card.json"]


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


def _assert_shared_headers(response, request_id: str) -> None:
    assert response.headers[REQUEST_ID] == request_id
    assert len(response.headers.get_list(REQUEST_ID)) == 1
    assert len(response.headers.get_list(SERVER_VERSION)) == 1
    assert "azure-ai-agentserver-core/" in response.headers[SERVER_VERSION]
    assert "azure-ai-agentserver-a2a/" in response.headers[SERVER_VERSION]


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
@pytest.mark.parametrize("path", _RPC_PATHS)
async def test_unhandled_exception_is_classified_as_upstream(client_factory, path):
    async def endpoint(_request: Request) -> JSONResponse:
        raise RuntimeError("handler failed")

    async with client_factory(_host(endpoint)) as client:
        response = await client.post(path, headers={REQUEST_ID: "request-error"})

    assert response.status_code == 500
    assert response.headers[ERROR_SOURCE] == "upstream"
    assert ERROR_DETAIL not in response.headers
    _assert_shared_headers(response, "request-error")


@pytest.mark.asyncio
@pytest.mark.parametrize("path", _RPC_PATHS)
async def test_platform_exception_includes_error_detail(client_factory, path):
    async def endpoint(_request: Request) -> JSONResponse:
        error = RuntimeError("storage unavailable")
        setattr(error, PLATFORM_ERROR_TAG, True)
        raise error

    async with client_factory(_host(endpoint)) as client:
        response = await client.post(path, headers={REQUEST_ID: "request-platform-error"})

    assert response.status_code == 500
    assert response.headers[ERROR_SOURCE] == "platform"
    assert "storage unavailable" in response.headers[ERROR_DETAIL]
    _assert_shared_headers(response, "request-platform-error")


@pytest.mark.asyncio
@pytest.mark.parametrize("path", _RPC_PATHS)
async def test_exception_response_preserves_trace_request_id(client_factory, path):
    async def endpoint(_request: Request) -> JSONResponse:
        raise RuntimeError("handler failed")

    trace_id = "0123456789abcdef0123456789abcdef"
    async with client_factory(_host(endpoint)) as client:
        response = await client.post(
            path,
            headers={
                REQUEST_ID: "client-request",
                "traceparent": f"00-{trace_id}-0123456789abcdef-01",
            },
            json={"jsonrpc": "2.0", "id": "request", "method": "GetTask", "params": {"id": "task"}},
        )

    assert response.status_code == 500
    _assert_shared_headers(response, trace_id)


@pytest.mark.asyncio
@pytest.mark.parametrize("path", _RPC_PATHS)
async def test_method_not_allowed_keeps_error_classification(client_factory, path):
    async def endpoint(_request: Request) -> JSONResponse:
        return JSONResponse({"ok": True})

    async with client_factory(_host(endpoint)) as client:
        response = await client.get(path, headers={REQUEST_ID: "request-method"})

    assert response.status_code == 405
    assert response.headers[ERROR_SOURCE] == "user"
    _assert_shared_headers(response, "request-method")


@pytest.mark.asyncio
@pytest.mark.parametrize("path", _CARD_PATHS)
async def test_agent_card_exception_has_shared_headers(client_factory, path):
    async def card_modifier(_card: AgentCard) -> AgentCard:
        raise RuntimeError("card modifier failed")

    host = A2AAgentServerHost(
        agent_card=_agent_card(),
        request_handler=cast(RequestHandler, object()),
        card_modifier=card_modifier,
        configure_observability=None,
    )
    async with client_factory(host) as client:
        response = await client.get(
            path,
            headers={REQUEST_ID: "request-card"},
        )

    assert response.status_code == 500
    assert response.headers[ERROR_SOURCE] == "upstream"
    _assert_shared_headers(response, "request-card")


@pytest.mark.asyncio
@pytest.mark.parametrize("path", _CARD_PATHS)
async def test_agent_card_method_error_has_shared_headers(client_factory, path):
    async def endpoint(_request: Request) -> JSONResponse:
        return JSONResponse({"ok": True})

    async with client_factory(_host(endpoint)) as client:
        response = await client.post(path, headers={REQUEST_ID: "card-method"})
    assert response.status_code == 405
    assert response.headers[ERROR_SOURCE] == "user"
    _assert_shared_headers(response, "card-method")


@pytest.mark.asyncio
async def test_stream_exception_after_headers_is_not_converted(client_factory):
    async def generate() -> AsyncIterator[bytes]:
        yield b"started"
        raise RuntimeError("stream failed")

    async def endpoint(_request: Request) -> StreamingResponse:
        return StreamingResponse(generate())

    async with client_factory(_host(endpoint)) as client:
        with pytest.raises(RuntimeError, match="stream failed"):
            await client.post(_RPC_PATH)
