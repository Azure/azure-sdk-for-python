# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Responses protocol host for Azure AI Hosted Agents.

Provides the Responses API endpoints and handler decorators
as a :class:`~azure.ai.agentserver.core.AgentServerHost` subclass.
"""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import logging
import types
from collections.abc import AsyncIterable, Awaitable, Generator
from typing import Any, AsyncIterator, Callable, Optional, Union

from starlette.routing import Route

from azure.ai.agentserver.core import AgentServerHost, build_server_version

from .._options import ResponsesServerOptions
from .._response_context import ResponseContext
from .._version import VERSION as _RESPONSES_VERSION
from ..models._generated import CreateResponse, ResponseStreamEvent
from ..store._base import ResponseProviderProtocol, ResponseStreamProviderProtocol
from ..store._memory import InMemoryResponseProvider
from ._endpoint_handler import _ResponseEndpointHandler
from ._orchestrator import _ResponseOrchestrator
from ._runtime_state import _RuntimeState

CreateHandlerFn = Callable[
    [CreateResponse, ResponseContext, asyncio.Event],
    Union[
        AsyncIterable[Union[ResponseStreamEvent, dict[str, Any]]],
        Generator[Union[ResponseStreamEvent, dict[str, Any]], Any, None],
        Awaitable[AsyncIterable[Union[ResponseStreamEvent, dict[str, Any]]]],
    ],
]
"""Type alias for the user-registered create-response handler function.

The handler receives:
- ``request``: The parsed :class:`CreateResponse` model.
- ``context``: The :class:`ResponseContext` for the current request.
- ``cancellation_signal``: An :class:`asyncio.Event` set when cancellation is requested.

It must return one of:
- A ``TextResponse`` for text-only responses (it implements ``AsyncIterable``).
- An ``AsyncIterable`` (async generator) of :class:`ResponseStreamEvent` instances.
- A synchronous ``Generator`` of :class:`ResponseStreamEvent` instances.
"""

logger = logging.getLogger("azure.ai.agentserver")


async def _sync_to_async_gen(sync_gen: types.GeneratorType) -> AsyncIterator:
    """Wrap a synchronous generator into an async generator.

    :param sync_gen: A synchronous generator to wrap.
    :type sync_gen: types.GeneratorType
    :return: An async iterator yielding items from the synchronous generator.
    :rtype: AsyncIterator
    """
    for item in sync_gen:
        yield item


class ResponsesAgentServerHost(AgentServerHost):
    """Responses protocol host for Azure AI Hosted Agents.

    A :class:`~azure.ai.agentserver.core.AgentServerHost` subclass that adds
    the Responses API endpoints.  Use the :meth:`create_handler` decorator
    to wire a handler function to the create endpoint.

    For multi-protocol agents, compose via cooperative inheritance::

        class MyHost(InvocationAgentServerHost, ResponsesAgentServerHost):
            pass

    Usage::

        from azure.ai.agentserver.responses import ResponsesAgentServerHost

        app = ResponsesAgentServerHost()

        @app.create_handler
        def my_handler(request, context, cancellation_signal):
            yield event

        app.run()

    :param prefix: Optional URL prefix for all response routes
        (e.g. ``"/v1"``).
    :type prefix: str
    :param options: Optional runtime options for the responses server.
    :type options: ResponsesServerOptions | None
    :param store: Optional persistence provider for response
        envelopes and input items.
    :type store: ResponseProviderProtocol | None
    """

    _INSTRUMENTATION_SCOPE = "Azure.AI.AgentServer.Responses"

    def __init__(
        self,
        *,
        prefix: str = "",
        options: ResponsesServerOptions | None = None,
        store: ResponseProviderProtocol | None = None,
        **kwargs: Any,
    ) -> None:
        # Handler slot — populated via @app.create_handler decorator
        self._create_fn: Optional[CreateHandlerFn] = None

        # Normalize prefix
        normalized_prefix = prefix.strip()
        if normalized_prefix and not normalized_prefix.startswith("/"):
            normalized_prefix = f"/{normalized_prefix}"
        normalized_prefix = normalized_prefix.rstrip("/")

        # Build internal components
        runtime_options = options or ResponsesServerOptions()

        # Resolve AgentConfig — used for Foundry auto-activation and
        # merging platform env-vars (SSE keep-alive) into runtime options.
        from azure.ai.agentserver.core._config import AgentConfig

        config = AgentConfig.from_env()

        # Merge SSE keep-alive from AgentConfig when the user hasn't
        # explicitly set one via the options constructor.  AgentConfig
        # defaults to 0 (disabled) per spec; a positive value means the
        # platform env var SSE_KEEPALIVE_INTERVAL was explicitly set.
        if runtime_options.sse_keep_alive_interval_seconds is None and config.sse_keepalive_interval > 0:
            runtime_options.sse_keep_alive_interval_seconds = config.sse_keepalive_interval

        # SSE-specific headers (x-platform-server is handled by hosting middleware)
        sse_headers: dict[str, str] = {
            "connection": "keep-alive",
            "cache-control": "no-cache",
            "x-accel-buffering": "no",
        }

        if store is None:
            if config.is_hosted:
                from ..store._foundry_provider import FoundryStorageProvider
                from ..store._foundry_settings import FoundryStorageSettings

                try:
                    from azure.identity.aio import DefaultAzureCredential
                except ImportError:
                    logger.warning("azure-identity not installed; Foundry auto-activation disabled")
                else:
                    settings = FoundryStorageSettings.from_endpoint(config.project_endpoint)
                    store = FoundryStorageProvider(DefaultAzureCredential(), settings)

        resolved_provider: ResponseProviderProtocol = store if store is not None else InMemoryResponseProvider()
        stream_provider = resolved_provider if isinstance(resolved_provider, ResponseStreamProviderProtocol) else None
        runtime_state = _RuntimeState()
        orchestrator = _ResponseOrchestrator(
            create_fn=self._dispatch_create,
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
            host=self,
            provider=resolved_provider,
            stream_provider=stream_provider,
        )

        # Build response protocol routes
        response_routes: list[Route] = [
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

        # Merge with any routes from sibling mixins via cooperative init
        existing = list(kwargs.pop("routes", None) or [])
        super().__init__(routes=existing + response_routes, **kwargs)

        # Register the responses protocol version on the host so the
        # x-platform-server header includes this package's version.
        self.register_server_version(build_server_version("azure-ai-agentserver-responses", _RESPONSES_VERSION))

        # Allow handler developers to append their own version segment.
        if runtime_options.additional_server_version:
            self.register_server_version(runtime_options.additional_server_version)

        # Register shutdown handler on self (inherited from AgentServerHost)
        self.shutdown_handler(endpoint.handle_shutdown)

    # ------------------------------------------------------------------
    # Handler decorator
    # ------------------------------------------------------------------

    def create_handler(self, fn: CreateHandlerFn) -> CreateHandlerFn:
        """Register a function as the create-response handler.

        The handler function must accept exactly three positional parameters:
        ``(request, context, cancellation_signal)`` and return an
        ``AsyncIterable`` of response stream events.

        Usage::

            @app.create_handler
            def my_handler(request, context, cancellation_signal):
                yield event

        :param fn: A callable accepting (request, context, cancellation_signal).
        :type fn: CreateHandlerFn
        :return: The original function (unmodified).
        :rtype: CreateHandlerFn
        """
        self._create_fn = fn
        return fn

    # ------------------------------------------------------------------
    # Dispatch (internal)
    # ------------------------------------------------------------------

    def _dispatch_create(
        self,
        request: CreateResponse,
        context: ResponseContext,
        cancellation_signal: asyncio.Event,
    ) -> AsyncIterator[ResponseStreamEvent]:
        """Dispatch to the registered create handler.

        Called by the orchestrator when processing a create request.
        Handles all handler return signatures:

        - Sync generator → wrapped into async generator.
        - AsyncIterable (e.g. ``TextResponse``) → converted to ``AsyncIterator``.
        - Coroutine (``async def`` that ``return`` s a value) → awaited, then the
          result is recursively normalised.
        - Async generator → returned as-is.

        :param request: The parsed create-response request.
        :type request: CreateResponse
        :param context: The response context for the request.
        :type context: ResponseContext
        :param cancellation_signal: The cancellation signal for the request.
        :type cancellation_signal: asyncio.Event
        :returns: The result from the registered create handler callable.
        :rtype: AsyncIterator[ResponseStreamEvent]
        """
        if self._create_fn is None:
            raise NotImplementedError("No create handler registered. Use the @app.create_handler decorator.")
        result = self._create_fn(request, context, cancellation_signal)
        return self._normalize_handler_result(result)

    def _normalize_handler_result(self, result: Any) -> AsyncIterator[ResponseStreamEvent]:
        """Convert a handler result into an AsyncIterator.

        Supports sync generators, async generators, coroutines (async def
        that returns), and AsyncIterables (e.g. TextResponse).

        :param result: The handler result to normalize.
        :type result: Any
        :return: An async iterator of response stream events.
        :rtype: AsyncIterator[ResponseStreamEvent]
        """
        if isinstance(result, types.GeneratorType):
            return _sync_to_async_gen(result)
        # Coroutine: async def handler that returns (rather than yields).
        # Await it and normalise the inner result.
        if asyncio.iscoroutine(result):
            return self._await_and_normalize(result)
        # If the handler returned an AsyncIterable (e.g. TextResponse), convert
        # to an AsyncIterator so the orchestrator can __anext__() uniformly.
        if hasattr(result, "__aiter__") and not hasattr(result, "__anext__"):
            return result.__aiter__()  # type: ignore[union-attr, return-value]
        return result  # type: ignore[return-value]

    async def _await_and_normalize(self, coro: Any) -> AsyncIterator[ResponseStreamEvent]:  # type: ignore[misc]
        """Await a coroutine and yield events from its normalised result.

        :param coro: A coroutine to await.
        :type coro: Any
        :return: An async iterator of response stream events from the awaited result.
        :rtype: AsyncIterator[ResponseStreamEvent]
        """
        inner = await coro
        async for event in self._normalize_handler_result(inner):
            yield event
