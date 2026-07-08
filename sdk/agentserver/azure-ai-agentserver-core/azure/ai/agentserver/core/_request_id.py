# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Request ID middleware for Azure AI Agent Server hosts.

A pure-ASGI middleware that sets the ``x-request-id`` response header on
every HTTP response.  The value is resolved in priority order:

1. Current OTEL trace ID.
2. Incoming ``x-request-id`` request header (client-provided correlation ID).
3. A new UUID as fallback.

The resolved value is also stored in ``scope["state"]["agentserver.request_id"]``
for use by downstream handlers (e.g., error body enrichment in protocol
packages).
"""

from __future__ import annotations

import uuid
from typing import Any, MutableMapping

from starlette.types import ASGIApp, Receive, Scope, Send

from ._middleware import _extract_header, _get_trace_id

# Key used to store the resolved request ID in ASGI scope state.
REQUEST_ID_STATE_KEY = "agentserver.request_id"


class RequestIdMiddleware:
    """Pure-ASGI middleware that sets ``x-request-id`` on every HTTP response.

    The resolved request ID is stored in ``scope["state"]`` under
    :data:`REQUEST_ID_STATE_KEY` so that protocol-specific code (e.g. the
    Responses package) can read it for error body enrichment.

    Unlike ``BaseHTTPMiddleware``, this passes the ``receive`` callable
    through to the inner application untouched, preserving
    ``request.is_disconnected()`` behaviour.

    :param app: The inner ASGI application.
    :type app: ASGIApp
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        raw_headers: list[tuple[bytes, bytes]] = scope.get("headers", [])
        request_id = _resolve_request_id(raw_headers)

        # Store in scope state for downstream access.
        state = scope.get("state")
        if not isinstance(state, MutableMapping):
            state = {}
            scope["state"] = state
        state[REQUEST_ID_STATE_KEY] = request_id

        async def _send_with_request_id(message: MutableMapping[str, Any]) -> None:
            if message["type"] == "http.response.start":
                # Filter any existing x-request-id to avoid duplicates, then add ours.
                headers = [
                    (name, value)
                    for name, value in message.get("headers", [])
                    if name.lower() != b"x-request-id"
                ]
                headers.append((b"x-request-id", request_id.encode()))
                message = {**message, "headers": headers}
            await send(message)

        await self.app(scope, receive, _send_with_request_id)


def _resolve_request_id(raw_headers: list[tuple[bytes, bytes]]) -> str:
    """Resolve the request ID from available sources.

    Priority:
    1. OTEL trace ID from current activity.
    2. Incoming ``x-request-id`` request header.
    3. New UUID fallback.

    :param raw_headers: Raw ASGI header tuples.
    :type raw_headers: list[tuple[bytes, bytes]]
    :return: The resolved request ID string.
    :rtype: str
    """
    # Priority 1: OTEL trace ID
    trace_id = _get_trace_id(raw_headers)
    if trace_id and trace_id != "0" * 32:
        return trace_id

    # Priority 2: Incoming x-request-id header
    incoming = _extract_header(raw_headers, b"x-request-id")
    if incoming:
        return incoming

    # Priority 3: New UUID
    return uuid.uuid4().hex
