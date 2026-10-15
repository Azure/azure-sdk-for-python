# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for A2AAgentServerHost routes and request context."""

from typing import cast
from unittest.mock import patch

import pytest
from a2a.helpers import new_text_message
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler, RequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentInterface
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from azure.ai.agentserver.a2a import A2AAgentServerHost
from azure.ai.agentserver.a2a._version import VERSION
from azure.ai.agentserver.core import get_request_context
from azure.ai.agentserver.invocations import InvocationAgentServerHost

_RPC_PATH = "/a2a"
_CARD_PATH = "/a2a/.well-known/agent-card.json"


class _NoOpExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        del context, event_queue
        raise NotImplementedError

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        del context, event_queue
        raise NotImplementedError


class _StreamingExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        del context
        await event_queue.enqueue_event(new_text_message("streamed"))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        del context, event_queue
        raise NotImplementedError


def _agent_card() -> AgentCard:
    return AgentCard(
        name="hello",
        description="test agent",
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


def _request_handler(card: AgentCard) -> RequestHandler:
    return DefaultRequestHandler(
        agent_executor=_NoOpExecutor(),
        task_store=InMemoryTaskStore(),
        agent_card=card,
    )


def _host(**kwargs) -> A2AAgentServerHost:
    card = _agent_card()
    return A2AAgentServerHost(
        agent_card=card,
        request_handler=_request_handler(card),
        configure_observability=None,
        **kwargs,
    )


def test_registers_only_canonical_a2a_routes():
    host = _host()

    paths = [getattr(route, "path", None) for route in host.routes]

    assert paths == [_RPC_PATH, _CARD_PATH, "/readiness"]
    assert "/.well-known/agent-card.json" not in paths
    assert "/a2a/extendedAgentCard" not in paths


@pytest.mark.asyncio
async def test_serves_canonical_agent_card_route(client_factory):
    host = _host()

    async with client_factory(host) as client:
        response = await client.get(_CARD_PATH)

    assert response.status_code == 200
    assert response.json()["name"] == "hello"


@pytest.mark.asyncio
async def test_jsonrpc_route_does_not_redirect_trailing_slash(client_factory):
    host = _host()

    async with client_factory(host) as client:
        response = await client.post(_RPC_PATH, json={})

    assert response.status_code == 200
    assert response.headers.get("location") is None


@pytest.mark.asyncio
async def test_send_streaming_message_returns_sse(client_factory):
    card = _agent_card()
    card.capabilities.streaming = True
    host = A2AAgentServerHost(
        agent_card=card,
        request_handler=DefaultRequestHandler(
            agent_executor=_StreamingExecutor(),
            task_store=InMemoryTaskStore(),
            agent_card=card,
        ),
        configure_observability=None,
    )

    async with client_factory(host) as client:
        response = await client.post(
            _RPC_PATH,
            headers={"A2A-Version": "1.0"},
            json={
                "jsonrpc": "2.0",
                "id": "stream",
                "method": "SendStreamingMessage",
                "params": {
                    "message": {
                        "messageId": "m1",
                        "role": "ROLE_USER",
                        "parts": [{"text": "hello"}],
                    }
                },
            },
        )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "data:" in response.text


@pytest.mark.asyncio
async def test_binds_and_resets_platform_request_context(client_factory):
    async def inspect_context(_request: Request) -> JSONResponse:
        context = get_request_context()
        return JSONResponse(
            {
                "call_id": context.call_id,
                "user_id": context.user_id,
                "session_id": context.session_id,
                "outbound_headers": context.platform_headers(),
            }
        )

    with patch(
        "azure.ai.agentserver.a2a._host.create_jsonrpc_routes",
        return_value=[Route(_RPC_PATH, inspect_context, methods=["POST"])],
    ):
        host = _host()

    async with client_factory(host) as client:
        response = await client.post(
            _RPC_PATH,
            json={},
            headers={
                "x-agent-foundry-call-id": "call-123",
                "x-agent-user-id": "user-456",
                "x-agent-session-id": "session-789",
            },
        )

    assert response.json() == {
        "call_id": "call-123",
        "user_id": "user-456",
        "session_id": None,
        "outbound_headers": {"x-agent-foundry-call-id": "call-123"},
    }
    assert get_request_context().call_id is None
    assert get_request_context().user_id is None
    assert get_request_context().session_id is None


@pytest.mark.asyncio
async def test_platform_context_is_limited_to_a2a_routes(client_factory):
    async def inspect_context(_request: Request) -> JSONResponse:
        context = get_request_context()
        return JSONResponse({"call_id": context.call_id, "user_id": context.user_id})

    host = _host(routes=[Route("/inspect", inspect_context, methods=["GET"])])

    async with client_factory(host) as client:
        response = await client.get(
            "/inspect",
            headers={
                "x-agent-foundry-call-id": "must-not-bind",
                "x-agent-user-id": "must-not-bind",
            },
        )

    assert response.json() == {"call_id": None, "user_id": None}


def test_disables_v0_3_compatibility():
    card = _agent_card()
    handler = _request_handler(card)

    with patch(
        "azure.ai.agentserver.a2a._host.create_jsonrpc_routes",
        return_value=[Route(_RPC_PATH, lambda _request: JSONResponse({}), methods=["POST"])],
    ) as create_routes:
        A2AAgentServerHost(
            agent_card=card,
            request_handler=handler,
            configure_observability=None,
        )

    assert create_routes.call_args.kwargs["enable_v0_3_compat"] is False


def test_exposes_native_card_handler_and_server_version():
    card = _agent_card()
    handler = _request_handler(card)
    host = A2AAgentServerHost(
        agent_card=card,
        request_handler=handler,
        configure_observability=None,
    )

    assert host.agent_card is card
    assert host.request_handler is handler
    assert "azure-ai-agentserver-a2a" in host._build_server_version()
    assert VERSION in host._build_server_version()


@pytest.mark.asyncio
async def test_composes_with_invocations_on_one_server(client_factory):
    class MultiProtocolHost(A2AAgentServerHost, InvocationAgentServerHost):
        pass

    card = _agent_card()
    host = MultiProtocolHost(
        agent_card=card,
        request_handler=_request_handler(card),
        configure_observability=None,
    )

    @host.invoke_handler
    async def handle_invocation(_request: Request) -> JSONResponse:
        return JSONResponse({"protocol": "invocations"})

    async with client_factory(host) as client:
        a2a_response = await client.get(_CARD_PATH)
        invocation_response = await client.post("/invocations", json={})

    assert a2a_response.status_code == 200
    assert invocation_response.status_code == 200
    assert invocation_response.json() == {"protocol": "invocations"}


def test_native_route_factories_receive_canonical_paths():
    card = _agent_card()
    handler = _request_handler(card)

    with (
        patch(
            "azure.ai.agentserver.a2a._host.create_jsonrpc_routes",
            return_value=[Route(_RPC_PATH, lambda _request: JSONResponse({}), methods=["POST"])],
        ) as create_rpc_routes,
        patch(
            "azure.ai.agentserver.a2a._host.create_agent_card_routes",
            return_value=[Route(_CARD_PATH, lambda _request: JSONResponse({}), methods=["GET"])],
        ) as create_card_routes,
    ):
        A2AAgentServerHost(
            agent_card=card,
            request_handler=handler,
            configure_observability=None,
        )

    assert create_rpc_routes.call_args.kwargs["rpc_url"] == _RPC_PATH
    assert create_card_routes.call_args.kwargs["card_url"] == _CARD_PATH
