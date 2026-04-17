# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Inbound request logging middleware for Azure AI Agent Server hosts.

A pure-ASGI middleware that logs every inbound HTTP request at INFO level
(start) and at INFO or WARNING level (completion, depending on status code).

Behaviour:
- Logs method + path (no query string) on start.
- Logs method + path + status code + duration on completion.
- Correlation headers (``x-request-id``, ``x-ms-client-request-id``) are
  included when present.
- OTel trace ID is included when an active trace exists.
- Status >= 400 → WARNING; otherwise → INFO.
- Unhandled exceptions → forced status 500, WARNING.
"""

from __future__ import annotations

import logging
import time
from typing import Any, MutableMapping

from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger("azure.ai.agentserver")


def _extract_header(headers: list[tuple[bytes, bytes]], name: bytes) -> str | None:
    """Extract a header value from raw ASGI headers.

    :param headers: Raw ASGI header tuples.
    :type headers: list[tuple[bytes, bytes]]
    :param name: Lower-case header name to look up.
    :type name: bytes
    :return: Decoded header value, or ``None`` if not found.
    :rtype: str | None
    """
    for key, value in headers:
        if key == name:
            return value.decode("latin-1")
    return None


def _get_trace_id() -> str | None:
    """Return the current OTel trace ID hex string, or ``None``.

    :return: Hex-encoded trace ID from the current OTel span, or ``None``.
    :rtype: str | None
    """
    try:
        from opentelemetry import trace as _trace  # pylint: disable=import-outside-toplevel

        span = _trace.get_current_span()
        ctx = span.get_span_context()
        if ctx and ctx.trace_id:
            return format(ctx.trace_id, "032x")
    except Exception:  # pylint: disable=broad-exception-caught
        pass
    return None


class InboundRequestLoggingMiddleware:
    """Pure-ASGI middleware that logs inbound HTTP requests.

    Unlike ``BaseHTTPMiddleware``, this passes the ``receive`` callable
    through to the inner application untouched, preserving
    ``request.is_disconnected()`` behaviour.

    Wired automatically by :class:`AgentServerHost` so that all protocol
    hosts (responses, invocations, etc.) get consistent inbound logging.

    :param app: The inner ASGI application.
    :type app: ASGIApp
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method: str = scope.get("method", "?")
        path: str = scope.get("path", "/")
        raw_headers: list[tuple[bytes, bytes]] = scope.get("headers", [])

        request_id = _extract_header(raw_headers, b"x-request-id")
        client_request_id = _extract_header(raw_headers, b"x-ms-client-request-id")
        trace_id = _get_trace_id()

        extra_parts: list[str] = []
        if request_id:
            extra_parts.append(f"x-request-id={request_id}")
        if client_request_id:
            extra_parts.append(f"x-ms-client-request-id={client_request_id}")
        if trace_id:
            extra_parts.append(f"trace_id={trace_id}")
        extra_str = f" [{', '.join(extra_parts)}]" if extra_parts else ""

        logger.info("Inbound %s %s started%s", method, path, extra_str)

        status_code: int | None = None
        start = time.monotonic()

        async def _send_wrapper(message: MutableMapping[str, Any]) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message.get("status", 0)
            await send(message)

        try:
            await self.app(scope, receive, _send_wrapper)
        except Exception:
            elapsed_ms = (time.monotonic() - start) * 1000
            logger.warning(
                "Inbound %s %s failed with status 500 in %.1fms%s",
                method, path, elapsed_ms, extra_str,
            )
            raise

        elapsed_ms = (time.monotonic() - start) * 1000

        if status_code is not None and status_code >= 400:
            logger.warning(
                "Inbound %s %s completed with status %d in %.1fms%s",
                method, path, status_code, elapsed_ms, extra_str,
            )
        else:
            logger.info(
                "Inbound %s %s completed with status %s in %.1fms%s",
                method, path, status_code, elapsed_ms, extra_str,
            )
