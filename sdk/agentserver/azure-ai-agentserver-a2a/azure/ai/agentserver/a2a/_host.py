# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""A2A protocol host for Azure AI Hosted Agents."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Optional

from a2a.server.request_handlers import RequestHandler
from a2a.server.routes import (
    ServerCallContextBuilder,
    create_agent_card_routes,
    create_jsonrpc_routes,
)
from a2a.types import AgentCard
from starlette.datastructures import Headers
from starlette.routing import Route
from starlette.types import ASGIApp, Receive, Scope, Send

from azure.ai.agentserver.core import (
    AgentServerHost,
    FoundryAgentRequestContext,
    build_server_version,
    reset_request_context,
    set_request_context,
)
from azure.ai.agentserver.core._platform_headers import (  # pylint: disable=import-error,no-name-in-module
    FOUNDRY_CALL_ID,
    USER_ID,
)

from ._version import VERSION as _A2A_VERSION

_A2A_RPC_PATH = "/invocations/a2a"
_A2A_AGENT_CARD_PATH = "/invocations/a2a/.well-known/agent-card.json"
_SESSION_ID_HEADER = "x-agent-session-id"
_A2A_PATHS = frozenset((_A2A_RPC_PATH, _A2A_AGENT_CARD_PATH))


class _A2APlatformContextMiddleware:
    """Bind Foundry platform headers while a native A2A route is executing."""

    def __init__(self, app: ASGIApp) -> None:
        self._app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope.get("path") not in _A2A_PATHS:
            await self._app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        token = set_request_context(
            FoundryAgentRequestContext(
                call_id=headers.get(FOUNDRY_CALL_ID),
                user_id=headers.get(USER_ID),
                session_id=headers.get(_SESSION_ID_HEADER),
            )
        )
        try:
            await self._app(scope, receive, send)
        finally:
            reset_request_context(token)


def _get_a2a_routes(
    agent_card: AgentCard,
    request_handler: RequestHandler,
    *,
    card_modifier: Optional[Callable[[AgentCard], Awaitable[AgentCard]]] = None,
    context_builder: Optional[ServerCallContextBuilder] = None,
) -> list[Route]:
    return [
        *create_jsonrpc_routes(
            request_handler=request_handler,
            rpc_url=_A2A_RPC_PATH,
            context_builder=context_builder,
            enable_v0_3_compat=False,
        ),
        *create_agent_card_routes(
            agent_card=agent_card,
            card_modifier=card_modifier,
            card_url=_A2A_AGENT_CARD_PATH,
        ),
    ]


class A2AAgentServerHost(AgentServerHost):
    """Host a native A2A SDK handler in an Azure AI Hosted Agent container.

    The host registers the native SDK's JSON-RPC and public agent-card routes
    at Foundry's canonical container paths. It also supplies the shared Agent
    Server readiness endpoint, lifecycle, telemetry, and request-scoped
    Foundry identity context.

    :param agent_card: Native A2A v1.0 agent card to serve to Foundry.
    :type agent_card: ~a2a.types.AgentCard
    :param request_handler: Native A2A v1.0 request handler.
    :type request_handler: ~a2a.server.request_handlers.RequestHandler
    :param card_modifier: Optional async callback applied before serving the agent card.
    :type card_modifier: Optional[Callable[[AgentCard], Awaitable[AgentCard]]]
    :param context_builder: Optional native A2A server call-context builder.
    :type context_builder: Optional[~a2a.server.routes.ServerCallContextBuilder]
    """

    def __init__(
        self,
        *,
        agent_card: AgentCard,
        request_handler: RequestHandler,
        card_modifier: Optional[Callable[[AgentCard], Awaitable[AgentCard]]] = None,
        context_builder: Optional[ServerCallContextBuilder] = None,
        **kwargs: Any,
    ) -> None:
        self._agent_card = agent_card
        self._request_handler = request_handler
        a2a_routes = _get_a2a_routes(
            agent_card,
            request_handler,
            card_modifier=card_modifier,
            context_builder=context_builder,
        )
        existing_routes = list(kwargs.pop("routes", None) or [])

        super().__init__(routes=existing_routes + a2a_routes, **kwargs)
        self.add_middleware(_A2APlatformContextMiddleware)
        self.register_server_version(build_server_version("azure-ai-agentserver-a2a", _A2A_VERSION))

    @property
    def agent_card(self) -> AgentCard:
        """Return the native A2A agent card hosted by this server.

        :return: The native A2A agent card.
        :rtype: ~a2a.types.AgentCard
        """
        return self._agent_card

    @property
    def request_handler(self) -> RequestHandler:
        """Return the native A2A request handler hosted by this server.

        :return: The native A2A request handler.
        :rtype: ~a2a.server.request_handlers.RequestHandler
        """
        return self._request_handler
