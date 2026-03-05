# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""ASGI middleware for AgentServer request handling."""
from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import time
from typing import TYPE_CHECKING, Any

from starlette.types import ASGIApp, Receive, Scope, Send

from .._errors import error_response

if TYPE_CHECKING:
    from .._access_log import AccessLogHelper
    from .._metrics import MetricsHelper

#: Paths exempt from concurrency, body-size limits, and access logging
#: (health probes must remain reachable even when all request slots are
#: occupied, and they generate too much noise for observability).
_HEALTH_PATHS = frozenset(("/liveness", "/readiness"))


class MaxBodySizeMiddleware:
    """ASGI middleware that rejects requests whose body exceeds a configured limit.

    Checks the ``Content-Length`` header and rejects requests that declare a
    body larger than the configured maximum.  Chunked transfers without a
    ``Content-Length`` header are allowed through — the application layer is
    responsible for bounding those reads.
    """

    def __init__(self, app: ASGIApp, max_body_size: int) -> None:
        self.app = app
        self.max_body_size = max_body_size

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope.get("path", "") in _HEALTH_PATHS:
            await self.app(scope, receive, send)
            return

        # Fast reject via Content-Length header
        headers = dict(scope.get("headers", []))
        content_length_raw = headers.get(b"content-length")
        if content_length_raw is not None:
            try:
                content_length = int(content_length_raw)
            except ValueError:
                content_length = 0
            if content_length > self.max_body_size:
                response = error_response(
                    "payload_too_large",
                    f"Payload Too Large (max {self.max_body_size} bytes)",
                    status_code=413,
                )
                await response(scope, receive, send)
                return

        await self.app(scope, receive, send)


class MaxConcurrentRequestsMiddleware:
    """ASGI middleware that limits the number of concurrent HTTP requests.

    When the limit is reached, additional requests receive a
    ``429 Too Many Requests`` response.
    """

    def __init__(self, app: ASGIApp, max_concurrent: int) -> None:
        self.app = app
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope.get("path", "") in _HEALTH_PATHS:
            await self.app(scope, receive, send)
            return

        if self._semaphore.locked():
            response = error_response(
                "too_many_requests",
                f"Too Many Requests (max {self.max_concurrent} concurrent)",
                status_code=429,
            )
            await response(scope, receive, send)
            return

        async with self._semaphore:
            await self.app(scope, receive, send)


class MetricsMiddleware:
    """ASGI middleware that records Prometheus metrics for every request.

    Captures request count, duration, in-flight gauge, and body sizes.
    Skips health-probe paths to avoid noisy data.
    """

    def __init__(self, app: ASGIApp, metrics: MetricsHelper) -> None:
        self.app = app
        self._metrics = metrics

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope.get("path", "") in _HEALTH_PATHS:
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "UNKNOWN")
        path = scope.get("path", "/")
        headers = dict(scope.get("headers", []))

        # Request body size from Content-Length (best-effort)
        request_size = 0
        cl_raw = headers.get(b"content-length")
        if cl_raw is not None:
            try:
                request_size = int(cl_raw)
            except ValueError:
                pass

        self._metrics.inc_in_flight()
        start = time.perf_counter()
        status_code = 0
        response_size = 0

        async def send_wrapper(message: Any) -> None:
            nonlocal status_code, response_size
            if message["type"] == "http.response.start":
                status_code = message.get("status", 0)
                for hdr_name, hdr_val in message.get("headers", []):
                    if hdr_name == b"content-length":
                        try:
                            response_size = int(hdr_val)
                        except ValueError:
                            pass
                        break
            elif message["type"] == "http.response.body":
                body = message.get("body", b"")
                if body:
                    response_size += len(body)
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            duration = time.perf_counter() - start
            self._metrics.dec_in_flight()
            self._metrics.record_request(
                method=method,
                path=path,
                status=status_code,
                duration=duration,
                request_size=request_size,
                response_size=response_size,
            )


class AccessLogMiddleware:
    """ASGI middleware that emits structured access log entries.

    One log entry per completed HTTP request.  Health-probe paths are excluded
    to reduce noise in production environments.
    """

    def __init__(self, app: ASGIApp, access_log: AccessLogHelper) -> None:
        self.app = app
        self._access_log = access_log

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope.get("path", "") in _HEALTH_PATHS:
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "UNKNOWN")
        path = scope.get("path", "/")
        http_version = scope.get("http_version", "1.1")
        protocol = f"HTTP/{http_version}"
        headers = dict(scope.get("headers", []))

        # Request body size from Content-Length
        request_size = 0
        cl_raw = headers.get(b"content-length")
        if cl_raw is not None:
            try:
                request_size = int(cl_raw)
            except ValueError:
                pass

        # Client IP
        client = scope.get("client")
        client_ip = client[0] if client else ""

        # User-Agent
        user_agent = ""
        ua_raw = headers.get(b"user-agent")
        if ua_raw is not None:
            user_agent = ua_raw.decode("latin-1", errors="replace")

        start = time.perf_counter()
        status_code = 0
        response_size = 0
        invocation_id = ""

        async def send_wrapper(message: Any) -> None:
            nonlocal status_code, response_size, invocation_id
            if message["type"] == "http.response.start":
                status_code = message.get("status", 0)
                for hdr_name, hdr_val in message.get("headers", []):
                    if hdr_name == b"content-length":
                        try:
                            response_size = int(hdr_val)
                        except ValueError:
                            pass
                    elif hdr_name == b"x-agent-invocation-id":
                        invocation_id = hdr_val.decode("latin-1", errors="replace")
            elif message["type"] == "http.response.body":
                body = message.get("body", b"")
                if body:
                    response_size += len(body)
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            self._access_log.log_request(
                method=method,
                path=path,
                status=status_code,
                duration_ms=duration_ms,
                request_size=request_size,
                response_size=response_size,
                invocation_id=invocation_id,
                client_ip=client_ip,
                user_agent=user_agent,
                protocol=protocol,
            )
