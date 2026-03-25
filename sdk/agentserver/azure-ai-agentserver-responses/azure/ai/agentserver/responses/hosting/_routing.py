# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Response protocol handler for AgentServer.

Provides the Responses API endpoints and registers them with the
``AgentServer`` on construction, following the same pattern as
``InvocationHandler``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional

from starlette.routing import Route

from azure.ai.agentserver.hosting import AgentLogger

from ._endpoint_handler import _ResponseEndpointHandler
from ._orchestrator import _ResponseOrchestrator
from ._runtime_state import _RuntimeState
from .._options import ResponsesServerOptions
from ..store._base import ResponseProviderProtocol, ResponseStreamProviderProtocol
from ..store._memory import InMemoryResponseProvider

if TYPE_CHECKING:
    from azure.ai.agentserver.hosting import AgentServer, TracingHelper

logger = AgentLogger.get()


class ResponseHandler:
    """Response protocol handler that plugs into an ``AgentServer``.

    Creates the Responses API endpoints and registers them with
    the server.  Use the :meth:`create_handler` decorator to wire
    a handler function to the create endpoint.

    This design supports multi-protocol composition -- multiple protocol
    handlers (e.g. ``InvocationHandler``, ``ResponseHandler``) can be
    mounted onto the same ``AgentServer``.

    Usage::

        from azure.ai.agentserver.hosting import AgentServer
        from azure.ai.agentserver.responses.hosting import ResponseHandler

        server = AgentServer()
        responses = ResponseHandler(server)

        @responses.create_handler
        def my_handler(request, context, cancellation_signal):
            async def _events():
                yield event
            return _events()

        server.run()

    :param server: The ``AgentServer`` to register response protocol
        routes with.
    :type server: AgentServer
    :param prefix: Optional URL prefix for all response routes
        (e.g. ``"/v1"``).
    :type prefix: str
    :param options: Optional runtime options for the responses server.
    :type options: ResponsesServerOptions | None
    :param provider: Optional persistence provider for response
        envelopes and input items.
    :type provider: ResponseProviderProtocol | None
    """

    def __init__(
        self,
        server: "AgentServer",
        *,
        prefix: str = "",
        options: ResponsesServerOptions | None = None,
        provider: ResponseProviderProtocol | None = None,
    ) -> None:
        # Extract tracing from server
        self._tracing: Optional["TracingHelper"] = server.tracing

        # Handler slot — populated via @responses.create_handler decorator
        self._create_fn: Optional[Callable] = None

        # Normalize prefix
        normalized_prefix = prefix.strip()
        if normalized_prefix and not normalized_prefix.startswith("/"):
            normalized_prefix = f"/{normalized_prefix}"
        normalized_prefix = normalized_prefix.rstrip("/")

        # Build internal components
        runtime_options = options or ResponsesServerOptions()
        # SSE-specific headers (x-platform-server is handled by hosting middleware)
        sse_headers: dict[str, str] = {
            "connection": "keep-alive",
            "cache-control": "no-cache",
            "x-accel-buffering": "no",
        }

        resolved_provider: ResponseProviderProtocol = provider if provider is not None else InMemoryResponseProvider()
        stream_provider = resolved_provider if isinstance(resolved_provider, ResponseStreamProviderProtocol) else None
        runtime_state = _RuntimeState()
        orchestrator = _ResponseOrchestrator(
            create_async=self._dispatch_create,
            runtime_state=runtime_state,
            runtime_options=runtime_options,
            provider=resolved_provider,
            stream_provider=stream_provider,
        )
        endpoint = _ResponseEndpointHandler(
            orchestrator=orchestrator,
            runtime_state=runtime_state,
            runtime_options=runtime_options,
            response_headers={},
            sse_headers=sse_headers,
            tracing=self._tracing,
            provider=resolved_provider,
            stream_provider=stream_provider,
        )

        # Build and cache routes
        self._routes: list[Route] = [
            Route(
                f"{normalized_prefix}/responses",
                endpoint.handle_create,
                methods=["POST"],
                name="create_response",
            ),
            Route(
                f"{normalized_prefix}/responses/{{response_id}}",
                endpoint.handle_get,
                methods=["GET"],
                name="get_response",
            ),
            Route(
                f"{normalized_prefix}/responses/{{response_id}}",
                endpoint.handle_delete,
                methods=["DELETE"],
                name="delete_response",
            ),
            Route(
                f"{normalized_prefix}/responses/{{response_id}}/cancel",
                endpoint.handle_cancel,
                methods=["POST"],
                name="cancel_response",
            ),
            Route(
                f"{normalized_prefix}/responses/{{response_id}}/input_items",
                endpoint.handle_input_items,
                methods=["GET"],
                name="get_input_items",
            ),
        ]

        # Register routes with the server
        server.register_routes(self._routes)

        # Register shutdown handler with the server
        server.shutdown_handler(endpoint.handle_shutdown)

    # ------------------------------------------------------------------
    # Handler decorator
    # ------------------------------------------------------------------

    def create_handler(self, fn: Callable) -> Callable:
        """Register a function as the create-response handler.

        The function must be decorated with ``@response_handler`` first.

        Usage::

            @responses.create_handler
            @response_handler
            def my_handler(request, context, cancellation_signal):
                async def _events():
                    yield event
                return _events()

        Or equivalently (decorator order does not matter)::

            @response_handler
            @responses.create_handler
            def my_handler(request, context, cancellation_signal):
                ...

        :param fn: A function decorated with ``@response_handler``.
        :type fn: Callable
        :return: The original function (unmodified).
        :rtype: Callable
        """
        self._create_fn = fn
        return fn

    # ------------------------------------------------------------------
    # Dispatch (internal)
    # ------------------------------------------------------------------

    def _dispatch_create(self, request, context, cancellation_signal):  # type: ignore[no-untyped-def]
        """Dispatch to the registered create handler.

        Called by the orchestrator when processing a create request.
        """
        if self._create_fn is None:
            raise NotImplementedError(
                "No create handler registered. Use the @responses.create_handler decorator."
            )
        return self._create_fn(request, context, cancellation_signal)

    # ------------------------------------------------------------------
    # Routes
    # ------------------------------------------------------------------

    @property
    def routes(self) -> list[Route]:
        """Starlette routes for the response protocol.

        :return: A list of Route objects for the response endpoints.
        :rtype: list[Route]
        """
        return self._routes
