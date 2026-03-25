# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Starlette hosting integration for the Responses server package."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Callable

from ._endpoint_handler import _ResponseEndpointHandler
from ._observability import build_platform_server_header
from .._options import ResponsesServerOptions
from ._orchestrator import _ResponseOrchestrator
from ._runtime_state import _RuntimeState
from ..store._base import ResponseProviderProtocol, ResponseStreamProviderProtocol
from ..store._memory import InMemoryResponseProvider
from .._version import VERSION

if TYPE_CHECKING:
    from starlette.applications import Starlette


_SDK_NAME = "azure-ai-agentserver-responses"
_SDK_VERSION = VERSION


def _runtime_marker() -> str:
    return f"python/{sys.version_info.major}.{sys.version_info.minor}"


def _platform_header(options: ResponsesServerOptions) -> str:
    return build_platform_server_header(
        sdk_name=_SDK_NAME,
        version=_SDK_VERSION,
        runtime=_runtime_marker(),
        extra=options.additional_server_identity,
    )


def map_responses_server(
    app: "Starlette",
    handler: Callable,
    *,
    prefix: str = "",
    options: ResponsesServerOptions | None = None,
    provider: ResponseProviderProtocol | None = None,
) -> None:
    if app is None:
        raise ValueError("app is required")
    if handler is None:
        raise ValueError(
            "No response handler registered. Decorate a function with @response_handler "
            "and pass it to map_responses_server()."
        )
    if not getattr(handler, "_is_response_handler", False):
        raise TypeError(
            "handler must be a function decorated with @response_handler"
        )
    create_async = handler

    normalized_prefix = prefix.strip()
    if normalized_prefix and not normalized_prefix.startswith("/"):
        normalized_prefix = f"/{normalized_prefix}"
    normalized_prefix = normalized_prefix.rstrip("/")

    runtime_options = options or ResponsesServerOptions()
    response_headers = {"x-platform-server": _platform_header(runtime_options)}
    sse_headers = {
        **response_headers,
        "connection": "keep-alive",
        "cache-control": "no-cache",
        "x-accel-buffering": "no",
    }

    resolved_provider: ResponseProviderProtocol = provider if provider is not None else InMemoryResponseProvider()
    stream_provider = resolved_provider if isinstance(resolved_provider, ResponseStreamProviderProtocol) else None
    runtime_state = _RuntimeState()
    orchestrator = _ResponseOrchestrator(
        create_async=create_async,
        runtime_state=runtime_state,
        runtime_options=runtime_options,
        provider=resolved_provider,
        stream_provider=stream_provider,
    )
    endpoint = _ResponseEndpointHandler(
        orchestrator=orchestrator,
        runtime_state=runtime_state,
        runtime_options=runtime_options,
        response_headers=response_headers,
        sse_headers=sse_headers,
        sdk_name=_SDK_NAME,
        provider=resolved_provider,
        stream_provider=stream_provider,
    )

    app.add_route(f"{normalized_prefix}/responses", endpoint.handle_create, methods=["POST"])
    app.add_route(f"{normalized_prefix}/responses/{{response_id}}", endpoint.handle_get, methods=["GET"])
    app.add_route(f"{normalized_prefix}/responses/{{response_id}}", endpoint.handle_delete, methods=["DELETE"])
    app.add_route(f"{normalized_prefix}/responses/{{response_id}}/cancel", endpoint.handle_cancel, methods=["POST"])
    app.add_route(
        f"{normalized_prefix}/responses/{{response_id}}/input_items",
        endpoint.handle_input_items,
        methods=["GET"],
    )
    app.router.lifespan_context = endpoint.lifespan_context(app.router.lifespan_context)
