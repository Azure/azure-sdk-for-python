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

from azure.ai.agentserver.core import (  # pylint: disable=import-error,no-name-in-module
    AgentServerHost,
    build_server_version,
)

from .._options import ResponsesServerOptions
from .._response_context import ResponseContext
from .._version import VERSION as _RESPONSES_VERSION
from ..models._generated import CreateResponse, ResponseStreamEvent
from ..store._base import ResponseProviderProtocol
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


def _serialize_event_payload(payload: Any) -> bytes:
    """Serialize a stream event for the file-backed registry codec.

    Stream payloads are either SDK ``ResponseStreamEvent`` model instances
    (the orchestrator passes generated models) or raw dicts (rehydrated /
    test scaffolds). Both shapes are JSON-encoded via ``as_dict`` when
    available so the registry's deserializer round-trips them as plain
    dicts (the consumer side only reads ``e["sequence_number"]`` /
    ``e["type"]``).
    """
    import json  # pylint: disable=import-outside-toplevel

    if hasattr(payload, "as_dict") and callable(payload.as_dict):
        data = payload.as_dict()
    elif isinstance(payload, dict):
        data = payload
    else:
        data = dict(payload)
    return json.dumps(data, separators=(",", ":"), default=str).encode("utf-8")


def _deserialize_event_payload(blob: bytes) -> Any:
    """Inverse of :func:`_serialize_event_payload`. Returns a plain dict."""
    import json  # pylint: disable=import-outside-toplevel

    return json.loads(blob.decode("utf-8"))


def _stream_cursor(event: Any) -> int:
    """Cursor function for SSE event streams — exposes ``sequence_number``."""
    return int(event["sequence_number"])


def _configure_streams_registry(runtime_options: ResponsesServerOptions) -> None:
    """Pick the registry backing for SSE event streams at compose time.

    - ``durable_background=True`` → file-backed replay under
      ``${AGENTSERVER_DURABLE_ROOT:-~/.durable}/streams/`` (spec 024
      Phase 3a unified storage layout).
    - ``durable_background=False`` → in-memory replay (events live in
      process; replay survives eager eviction within the TTL window).

    The configurator is a process-wide singleton — last call wins for
    streams created after it. In tests with multiple hosts per process,
    the per-test fixtures snapshot/restore the registry's private state.
    """
    from azure.ai.agentserver.core.storage_paths import (  # pylint: disable=import-outside-toplevel,import-error,no-name-in-module
        resolve_durable_subdir,
    )
    from azure.ai.agentserver.core.streaming import (  # pylint: disable=import-outside-toplevel,import-error,no-name-in-module
        streams,
    )

    if runtime_options.durable_background:
        # (Spec 024 Phase 3a) Stream store path resolves via the unified
        # storage-paths helper; legacy ``AGENTSERVER_STREAM_STORE_PATH``
        # env var + per-temp-dir default are deleted.
        stream_dir = resolve_durable_subdir("streams")
        streams.use_file_backed_replay(
            storage_dir=stream_dir,
            cursor_fn=_stream_cursor,
            ttl_seconds=runtime_options.replay_event_ttl_seconds,
            serializer=_serialize_event_payload,
            deserializer=_deserialize_event_payload,
        )
    else:
        streams.use_in_memory_replay(
            cursor_fn=_stream_cursor,
            ttl_seconds=runtime_options.replay_event_ttl_seconds,
        )


class ResponsesAgentServerHost(AgentServerHost):
    """Responses protocol host for Azure AI Hosted Agents.

    A :class:`~azure.ai.agentserver.core.AgentServerHost` subclass that adds
    the Responses API endpoints.  Use the :meth:`response_handler` decorator
    to wire a handler function to the create endpoint.

    For multi-protocol agents, compose via cooperative inheritance::

        class MyHost(InvocationAgentServerHost, ResponsesAgentServerHost):
            pass

    Usage::

        from azure.ai.agentserver.responses import ResponsesAgentServerHost

        app = ResponsesAgentServerHost()

        @app.response_handler
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
        # Handler slot — populated via @app.response_handler decorator
        self._create_fn: Optional[CreateHandlerFn] = None
        # Acceptance hook — populated via @app.response_acceptor decorator
        self._acceptance_hook: Optional[Any] = None

        # Normalize prefix
        normalized_prefix = prefix.strip()
        if normalized_prefix and not normalized_prefix.startswith("/"):
            normalized_prefix = f"/{normalized_prefix}"
        normalized_prefix = normalized_prefix.rstrip("/")

        # Build internal components
        runtime_options = options or ResponsesServerOptions()

        # Server version string — the responses segment is built once and
        # registered on the host.  The full x-platform-server value is
        # assembled lazily by _build_server_version() (joining all
        # registered segments) and is also used as the Foundry storage
        # User-Agent via callback so both headers are always identical.
        _responses_version = build_server_version("azure-ai-agentserver-responses", _RESPONSES_VERSION)

        # Resolve AgentConfig — used for Foundry auto-activation and
        # merging platform env-vars (SSE keep-alive) into runtime options.
        from azure.ai.agentserver.core._config import (
            AgentConfig,
        )  # pylint: disable=import-error,no-name-in-module

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
                    store = FoundryStorageProvider(
                        DefaultAzureCredential(),
                        settings,
                        get_server_version=self._build_server_version,
                    )

        # (Spec 024 Phase 3a) When no explicit store is supplied, default
        # to a file-backed store under ``${AGENTSERVER_DURABLE_ROOT:-~/.durable}/responses/``.
        # The legacy ``AGENTSERVER_RESPONSE_STORE_PATH`` env var is
        # deleted — operators control the location via the unified
        # ``AGENTSERVER_DURABLE_ROOT``. This enables cross-process
        # recovery in local-dev / crash-harness tests without standing
        # up Foundry. Note: this implements Phase 3b's "file-backed
        # response default" together with Phase 3a's rename because the
        # two are inseparable (the default path depends on the unified
        # root resolution).
        if store is None:
            from azure.ai.agentserver.core.storage_paths import (  # pylint: disable=import-outside-toplevel,import-error,no-name-in-module
                resolve_durable_subdir,
            )

            from ..store._file import (
                FileResponseStore,
            )  # pylint: disable=import-outside-toplevel

            store = FileResponseStore(storage_dir=resolve_durable_subdir("responses"))

        resolved_provider: ResponseProviderProtocol = store if store is not None else InMemoryResponseProvider()

        # Composition guard: when ``durable_background=True`` AND the
        # caller EXPLICITLY supplied a non-persistent ``store=`` argument,
        # refuse to start. The operator chose a store that contradicts
        # their durable_background opt-in and we won't silently degrade.
        #
        # The default path (``store=None`` → ``FileResponseStore`` under
        # ``${AGENTSERVER_DURABLE_ROOT}/responses/``) is now persistent
        # and never triggers this guard. Pre-Phase-3a the default was
        # ``InMemoryResponseProvider`` and operators had to set
        # ``AGENTSERVER_RESPONSE_STORE_PATH`` to upgrade — that env var
        # is now deleted in favour of the unified default.
        if runtime_options.durable_background and store is not None and isinstance(store, InMemoryResponseProvider):
            raise ValueError(
                "ResponsesAgentServerHost refused to start: "
                "``durable_background=True`` was configured with an "
                "explicit ``store=`` argument "
                f"({type(store).__name__}) that does not persist across "
                "process crashes — durable_background cannot honour its "
                "recovery promise. Either (a) supply a persistent store "
                "(FileResponseStore, FoundryStorageProvider, etc.), "
                "(b) omit ``store=`` to use the default file-backed store "
                "under ``${AGENTSERVER_DURABLE_ROOT}/responses/``, or "
                "(c) set ``durable_background=False`` to opt out of "
                "crash recovery."
            )

        # Configure the process-wide streams registry. A single configurator
        # call at compose time picks the backing used for every response's
        # SSE event stream. The handler-emitted events are serialized to
        # ``as_dict()`` form so the registry's default JSON codec accepts
        # them; the cursor function exposes ``sequence_number`` as the
        # reconnection cursor for ``subscribe(after=N)`` / ``Last-Event-ID``.
        _configure_streams_registry(runtime_options)

        runtime_state = _RuntimeState()
        orchestrator = _ResponseOrchestrator(
            create_fn=self._dispatch_create,
            runtime_state=runtime_state,
            runtime_options=runtime_options,
            provider=resolved_provider,
            acceptance_hook=self._acceptance_hook,
        )
        endpoint = _ResponseEndpointHandler(
            orchestrator=orchestrator,
            runtime_state=runtime_state,
            runtime_options=runtime_options,
            response_headers={},
            sse_headers=sse_headers,
            host=self,
            provider=resolved_provider,
        )
        # Wire the endpoint's shutdown flag into the orchestrator so the
        # exception/cancellation handlers can detect "we're inside the
        # graceful-shutdown grace window" before the durable task's
        # ctx.shutdown event propagates. Without this, an upstream-client
        # exception triggered by SIGTERM-via-killpg (e.g. an LLM SDK
        # subprocess in the server's process group dying instantly)
        # would be misclassified as a regular handler failure and bake
        # a "failed" terminal into the durable task — instead of leaving
        # the task in_progress for next-lifetime recovery as the spec /
        # user-facing durability contract requires.
        orchestrator._shutdown_event = endpoint._shutdown_requested  # pylint: disable=protected-access

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

        # Register the responses protocol version (and any additional version
        # from the handler developer) on the host so the x-platform-server
        # header includes this package's version.
        self.register_server_version(_responses_version)

        # Allow handler developers to append their own version segment.
        if runtime_options.additional_server_version:
            self.register_server_version(runtime_options.additional_server_version)

        # Register shutdown handler on self (inherited from AgentServerHost)
        self.shutdown_handler(endpoint.handle_shutdown)

        # (Spec 014) Register a pre-shutdown callback that runs from the
        # SIGTERM signal handler — BEFORE Hypercorn's graceful drain
        # begins. This sets the endpoint's ``_shutdown_requested`` event
        # immediately so foreground responses' disconnect-poll loop
        # detects shutdown and signals the handler to exit cleanly,
        # avoiding the case where Hypercorn waits a long
        # ``graceful_shutdown_timeout`` for the handler to complete
        # naturally — which would deliver the wrong terminal status
        # (completed instead of failed) to a Row 3 Path B test scenario.
        self.register_pre_shutdown_callback(endpoint._shutdown_requested.set)

        # Stash endpoint reference for request_shutdown() access.
        self._endpoint = endpoint

        # --- Responses startup configuration logging ---
        logger.info(
            "Responses protocol: storage_provider=%s, default_model=%s, "
            "default_fetch_history_count=%s, shutdown_grace_period=%ss",
            type(resolved_provider).__name__,
            runtime_options.default_model or "(not set)",
            runtime_options.default_fetch_history_count,
            runtime_options.shutdown_grace_period_seconds,
        )

    # ------------------------------------------------------------------
    # Shutdown notification
    # ------------------------------------------------------------------

    def request_shutdown(self) -> None:
        """Signal that shutdown is imminent.

        Sets the internal shutdown flag immediately so that in-flight
        foreground requests observe the cancellation signal without waiting
        for the ASGI lifespan shutdown phase (which only fires after all
        requests drain).

        Call this from a process signal handler (SIGTERM) or before
        triggering the ASGI server's shutdown to avoid deadlocking
        foreground handlers that await the cancellation signal.
        """
        self._endpoint._shutdown_requested.set()

    # ------------------------------------------------------------------
    # Handler decorator
    # ------------------------------------------------------------------

    def response_handler(self, fn: CreateHandlerFn) -> CreateHandlerFn:
        """Register a function as the create-response handler.

        The handler function must accept exactly three positional parameters:
        ``(request, context, cancellation_signal)`` and return an
        ``AsyncIterable`` of response stream events.

        Usage::

            @app.response_handler
            def my_handler(request, context, cancellation_signal):
                yield event

        :param fn: A callable accepting (request, context, cancellation_signal).
        :type fn: CreateHandlerFn
        :return: The original function (unmodified).
        :rtype: CreateHandlerFn
        """
        self._create_fn = fn
        return fn

    def response_acceptor(self, fn: Any) -> Any:
        """Register a function as the acceptance hook for steerable conversations.

        The acceptance hook is called when a new turn is queued on an
        already-active steerable conversation. It generates the "queued"
        response returned to the HTTP caller.

        Usage::

            @app.response_acceptor
            def my_acceptor(request, context):
                return {"status": "queued", "id": context.response_id}

        :param fn: A callable accepting (request, context) and returning a dict.
        :type fn: Callable
        :return: The original function (unmodified).
        :rtype: Callable
        """
        self._acceptance_hook = fn
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
            raise NotImplementedError("No create handler registered. Use the @app.response_handler decorator.")
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
