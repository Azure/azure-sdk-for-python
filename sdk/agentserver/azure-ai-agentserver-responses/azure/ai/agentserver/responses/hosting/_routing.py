# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Starlette hosting integration for the Responses server package."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from ._endpoint_handler import _ResponseEndpointHandler
from ._observability import build_platform_server_header
from .._options import ResponsesServerOptions
from ._orchestrator import _ResponseOrchestrator
from ._runtime_state import _RuntimeState
from .._version import VERSION

if TYPE_CHECKING:
    from starlette.applications import Starlette

    from .._handlers import ResponseHandler


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
    handler: "ResponseHandler",
    *,
    prefix: str = "",
    options: ResponsesServerOptions | None = None,
) -> None:
    if app is None:
        raise ValueError("app is required")
    if handler is None:
        raise ValueError(
            "No ResponseHandler implementation is registered. Provide a handler before calling map_responses_server()."
        )
    create_async = getattr(handler, "create_async", None)
    if not callable(create_async):
        raise TypeError("handler must define create_async(request, context, cancellation_signal)")

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

    runtime_state = _RuntimeState()
    orchestrator = _ResponseOrchestrator(
        create_async=create_async,
        runtime_state=runtime_state,
        runtime_options=runtime_options,
    )
    endpoint = _ResponseEndpointHandler(
        orchestrator=orchestrator,
        runtime_state=runtime_state,
        runtime_options=runtime_options,
        response_headers=response_headers,
        sse_headers=sse_headers,
        sdk_name=_SDK_NAME,
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
