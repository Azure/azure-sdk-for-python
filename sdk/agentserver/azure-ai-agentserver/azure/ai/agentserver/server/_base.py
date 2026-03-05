# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import asyncio  # pylint: disable=do-not-import-asyncio
import contextlib
import os
import uuid
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator  # pylint: disable=import-error
from typing import Any, Optional

from hypercorn.asyncio import serve as _hypercorn_serve
from hypercorn.config import Config as HypercornConfig
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse
from starlette.routing import Route

from .._access_log import AccessLogHelper
from .._constants import Constants
from .._errors import error_response
from .._logger import get_logger
from .._metrics import MetricsHelper
from .._tracing import TracingHelper, extract_w3c_carrier
from ..validation._openapi_validator import OpenApiValidator
from ._config import (
    resolve_graceful_shutdown_timeout,
    resolve_request_timeout,
    resolve_max_concurrent_requests,
    resolve_max_request_body_size,
    resolve_port,
)
from ._middleware import (
    AccessLogMiddleware,
    MaxBodySizeMiddleware,
    MaxConcurrentRequestsMiddleware,
    MetricsMiddleware,
)

logger = get_logger()


class AgentServer(ABC):
    """Generic agent server base with pluggable protocol heads.

    Subclass and implement :meth:`invoke` to handle ``/invocations`` requests.
    Optionally override :meth:`get_invocation` and :meth:`cancel_invocation`
    for additional protocol support.

    Developer receives raw Starlette ``Request`` objects and returns raw
    Starlette ``Response`` objects, giving full control over content types,
    streaming, headers, and status codes.

    :param openapi_spec: Optional OpenAPI spec dict for request validation.
    :type openapi_spec: Optional[dict[str, Any]]
    :param enable_tracing: Enable OpenTelemetry tracing.  When *None* (default)
        the ``AGENT_ENABLE_TRACING`` env var is consulted (``"true"`` to enable).
        Requires ``opentelemetry-api`` — install with
        ``pip install azure-ai-agentserver[tracing]``.
    :type enable_tracing: Optional[bool]
    :param timeout_graceful_shutdown: Seconds to wait for in-flight requests to
        complete after receiving SIGTERM / shutdown signal.  When *None* (default)
        the ``AGENT_GRACEFUL_SHUTDOWN_TIMEOUT`` env var is consulted; if that is
        also unset the default is 30 seconds.  Set to ``0`` to disable the
        drain period.
    :type timeout_graceful_shutdown: Optional[int]
    :param max_request_body_size: Maximum allowed request body size in bytes.
        When *None* (default) the ``AGENT_MAX_REQUEST_BODY_SIZE`` env var is
        consulted; if that is also unset the default is 100 MB (104857600).
        Set to ``0`` to disable the limit.  Requests exceeding this limit
        receive a ``413 Payload Too Large`` response.
    :type max_request_body_size: Optional[int]
    :param request_timeout: Maximum seconds an ``invoke()`` call may run before
        being cancelled.  When *None* (default) the ``AGENT_REQUEST_TIMEOUT``
        env var is consulted; if that is also unset the default is 300 seconds
        (5 minutes).  Set to ``0`` to disable the timeout.
    :type request_timeout: Optional[int]
    :param max_concurrent_requests: Maximum number of HTTP requests that may be
        processed simultaneously.  When *None* (default) the
        ``AGENT_MAX_CONCURRENT_REQUESTS`` env var is consulted; if that is also
        unset the default is ``0`` (disabled — no concurrency limit).  When
        the limit is reached, additional requests receive a
        ``429 Too Many Requests`` response.
    :type max_concurrent_requests: Optional[int]
    :param enable_metrics: Enable Prometheus metrics endpoint at ``/metrics``.
        When *None* (default) the ``AGENT_ENABLE_METRICS`` env var is consulted
        (``"true"`` to enable).  Requires ``prometheus_client`` — install with
        ``pip install azure-ai-agentserver[metrics]``.
    :type enable_metrics: Optional[bool]
    :param enable_access_log: Enable structured per-request access logging to
        the ``azure.ai.agentserver.access`` logger.  When *None* (default)
        the ``AGENT_ENABLE_ACCESS_LOG`` env var is consulted (``"true"`` to
        enable).  Uses JSON format if ``python-json-logger`` is installed,
        otherwise falls back to ``key=value`` pairs.
    :type enable_access_log: Optional[bool]
    """

    def __init__(
        self,
        openapi_spec: Optional[dict[str, Any]] = None,
        enable_tracing: Optional[bool] = None,
        timeout_graceful_shutdown: Optional[int] = None,
        max_request_body_size: Optional[int] = None,
        request_timeout: Optional[int] = None,
        max_concurrent_requests: Optional[int] = None,
        enable_metrics: Optional[bool] = None,
        enable_access_log: Optional[bool] = None,
    ) -> None:
        self._openapi_spec = openapi_spec
        self._validator: Optional[OpenApiValidator] = (
            OpenApiValidator(openapi_spec) if openapi_spec else None
        )
        self._tracing = TracingHelper(enabled=enable_tracing)
        self._metrics = MetricsHelper(enabled=enable_metrics)
        self._access_log = AccessLogHelper(enabled=enable_access_log)
        self._timeout_graceful_shutdown = resolve_graceful_shutdown_timeout(
            timeout_graceful_shutdown
        )
        self._max_request_body_size = resolve_max_request_body_size(
            max_request_body_size
        )
        self._request_timeout = resolve_request_timeout(request_timeout)
        self._max_concurrent_requests = resolve_max_concurrent_requests(
            max_concurrent_requests
        )
        self.app: Starlette
        self._build_app()

    # ------------------------------------------------------------------
    # Abstract / overridable protocol methods
    # ------------------------------------------------------------------

    @abstractmethod
    async def invoke(self, request: Request) -> Response:
        """Process an invocation.

        The invocation ID is available via ``request.state.invocation_id``.
        Return any Starlette ``Response`` — ``JSONResponse``, ``Response``,
        ``StreamingResponse``, etc. The server auto-injects the
        ``x-agent-invocation-id`` response header if not already set.

        :param request: The raw Starlette request.
        :type request: starlette.requests.Request
        :return: Any Starlette response.
        :rtype: starlette.responses.Response
        """

    async def get_invocation(self, request: Request) -> Response:  # pylint: disable=unused-argument
        """Retrieve a previous invocation result.

        The invocation ID is available via ``request.state.invocation_id``
        (extracted from the URL path parameter).

        Default implementation returns 404. Override to support retrieval.

        :param request: The raw Starlette request.
        :type request: starlette.requests.Request
        :return: Any Starlette response.
        :rtype: starlette.responses.Response
        """
        return error_response("not_supported", "get_invocation not supported", status_code=404)

    async def cancel_invocation(self, request: Request) -> Response:  # pylint: disable=unused-argument
        """Cancel an invocation.

        The invocation ID is available via ``request.state.invocation_id``
        (extracted from the URL path parameter).

        Default implementation returns 404. Override to support cancellation.

        :param request: The raw Starlette request.
        :type request: starlette.requests.Request
        :return: Any Starlette response.
        :rtype: starlette.responses.Response
        """
        return error_response("not_supported", "cancel_invocation not supported", status_code=404)

    async def on_shutdown(self) -> None:
        """Called during server shutdown after in-flight requests have drained.

        Override to checkpoint state, flush buffers, close connections, or
        release external resources before the process exits.

        The callback is bounded by ``timeout_graceful_shutdown`` seconds.
        If it does not complete in time, a warning is logged and shutdown
        proceeds.

        Default implementation is a no-op.
        """

    def get_openapi_spec(self) -> Optional[dict[str, Any]]:
        """Return the OpenAPI spec dict for this agent, or None.

        :return: The registered OpenAPI spec or None.
        :rtype: Optional[dict[str, Any]]
        """
        return self._openapi_spec

    # ------------------------------------------------------------------
    # Run helpers
    # ------------------------------------------------------------------

    def _build_hypercorn_config(self, host: str, port: int) -> HypercornConfig:
        """Create a Hypercorn config with resolved host, port and timeouts.

        :param host: Network interface to bind.
        :type host: str
        :param port: Port to bind.
        :type port: int
        :return: Configured Hypercorn config.
        :rtype: HypercornConfig
        """
        config = HypercornConfig()
        config.bind = [f"{host}:{port}"]
        config.graceful_timeout = float(self._timeout_graceful_shutdown)
        return config

    def run(self, host: str = "127.0.0.1", port: Optional[int] = None) -> None:
        """Start the server synchronously.

        Uses Hypercorn as the ASGI server, which supports HTTP/1.1 and HTTP/2.

        :param host: Network interface to bind. Defaults to ``127.0.0.1``.
            Use ``"0.0.0.0"`` to listen on all interfaces.
        :type host: str
        :param port: Port to bind. Defaults to ``AGENT_SERVER_PORT`` env var or 8088.
        :type port: Optional[int]
        """
        resolved_port = resolve_port(port)
        logger.info("AgentServer starting on %s:%s", host, resolved_port)
        config = self._build_hypercorn_config(host, resolved_port)
        asyncio.run(_hypercorn_serve(self.app, config))  # type: ignore[arg-type]  # Starlette is ASGI-compatible

    async def run_async(self, host: str = "127.0.0.1", port: Optional[int] = None) -> None:
        """Start the server asynchronously (awaitable).

        Uses Hypercorn as the ASGI server, which supports HTTP/1.1 and HTTP/2.

        :param host: Network interface to bind. Defaults to ``127.0.0.1``.
            Use ``"0.0.0.0"`` to listen on all interfaces.
        :type host: str
        :param port: Port to bind. Defaults to ``AGENT_SERVER_PORT`` env var or 8088.
        :type port: Optional[int]
        """
        resolved_port = resolve_port(port)
        logger.info("AgentServer starting on %s:%s (async)", host, resolved_port)
        config = self._build_hypercorn_config(host, resolved_port)
        await _hypercorn_serve(self.app, config)  # type: ignore[arg-type]  # Starlette is ASGI-compatible

    # ------------------------------------------------------------------
    # Private: app construction
    # ------------------------------------------------------------------

    def _build_app(self) -> None:
        """Construct the Starlette ASGI application with all routes."""

        @contextlib.asynccontextmanager
        async def _lifespan(_app: Starlette) -> AsyncGenerator[None, None]:  # noqa: RUF029
            logger.info("AgentServer started")
            yield

            # --- SHUTDOWN: runs once when the server is stopping ---
            logger.info(
                "AgentServer shutting down (graceful timeout=%ss)",
                self._timeout_graceful_shutdown,
            )
            try:
                await asyncio.wait_for(
                    self.on_shutdown(),
                    timeout=self._timeout_graceful_shutdown or None,
                )
            except asyncio.TimeoutError:
                logger.warning(
                    "on_shutdown did not complete within %ss timeout",
                    self._timeout_graceful_shutdown,
                )
            except Exception:  # pylint: disable=broad-exception-caught
                logger.exception("Error in on_shutdown")

        routes = [
            Route(
                "/invocations/docs/openapi.json",
                self._get_openapi_spec_endpoint,
                methods=["GET"],
                name="get_openapi_spec",
            ),
            Route(
                "/invocations",
                self._create_invocation_endpoint,
                methods=["POST"],
                name="create_invocation",
            ),
            Route(
                "/invocations/{invocation_id}",
                self._get_invocation_endpoint,
                methods=["GET"],
                name="get_invocation",
            ),
            Route(
                "/invocations/{invocation_id}/cancel",
                self._cancel_invocation_endpoint,
                methods=["POST"],
                name="cancel_invocation",
            ),
            Route("/liveness", self._liveness_endpoint, methods=["GET"], name="liveness"),
            Route("/readiness", self._readiness_endpoint, methods=["GET"], name="readiness"),
        ]

        if self._metrics.enabled:
            routes.append(
                Route("/metrics", self._metrics_endpoint, methods=["GET"], name="metrics")
            )

        self.app = Starlette(routes=routes, lifespan=_lifespan)
        if self._max_request_body_size > 0:
            self.app.add_middleware(
                MaxBodySizeMiddleware,
                max_body_size=self._max_request_body_size,
            )
        if self._max_concurrent_requests > 0:
            self.app.add_middleware(
                MaxConcurrentRequestsMiddleware,
                max_concurrent=self._max_concurrent_requests,
            )
        # Observability middleware (innermost — only measures requests that
        # pass body-size and concurrency gates).
        if self._access_log.enabled:
            self.app.add_middleware(AccessLogMiddleware, access_log=self._access_log)
        if self._metrics.enabled:
            self.app.add_middleware(MetricsMiddleware, metrics=self._metrics)
        # CORS must be added last so it wraps outermost — this ensures
        # error responses from inner middleware (413, 429) also carry
        # Access-Control-Allow-Origin headers for browser clients.
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=False,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # ------------------------------------------------------------------
    # Private: endpoint handlers
    # ------------------------------------------------------------------

    async def _get_openapi_spec_endpoint(self, request: Request) -> Response:  # pylint: disable=unused-argument
        """GET /invocations/docs/openapi.json — return registered spec or 404.

        :param request: The incoming Starlette request.
        :type request: Request
        :return: JSON response with the spec or 404.
        :rtype: Response
        """
        spec = self.get_openapi_spec()
        if spec is None:
            return error_response("not_found", "No OpenAPI spec registered", status_code=404)
        return JSONResponse(spec)

    async def _create_invocation_endpoint(self, request: Request) -> Response:
        """POST /invocations — create and process an invocation.

        :param request: The incoming Starlette request.
        :type request: Request
        :return: The invocation result or error response.
        :rtype: Response
        """
        invocation_id = str(uuid.uuid4())
        request.state.invocation_id = invocation_id

        # Validate request body against OpenAPI spec
        if self._validator is not None:
            content_type = request.headers.get("content-type", "application/json")
            body = await request.body()
            errors = self._validator.validate_request(body, content_type)
            if errors:
                return error_response(
                    "invalid_payload",
                    "Request validation failed",
                    status_code=400,
                    details=[
                        {"code": "validation_error", "message": e}
                        for e in errors
                    ],
                )

        carrier = extract_w3c_carrier(request.headers)

        # Use manual span management so that streaming responses keep the
        # span open until the last chunk is yielded (or an error occurs).
        otel_span = self._tracing.start_span(
            "AgentServer.invoke",
            attributes={"invocation.id": invocation_id},
            carrier=carrier,
        )
        try:
            invoke_awaitable = self.invoke(request)
            timeout = self._request_timeout or None  # 0 → None (no limit)
            response = await asyncio.wait_for(invoke_awaitable, timeout=timeout)
        except asyncio.TimeoutError:
            self._tracing.end_span(otel_span)
            logger.error(
                "Invocation %s timed out after %ss",
                invocation_id,
                self._request_timeout,
            )
            return error_response(
                "request_timeout",
                f"Invocation timed out after {self._request_timeout}s",
                status_code=504,
                headers={Constants.INVOCATION_ID_HEADER: invocation_id},
            )
        except Exception as exc:  # pylint: disable=broad-exception-caught
            self._tracing.end_span(otel_span, exc=exc)
            logger.error("Error processing invocation %s: %s", invocation_id, exc, exc_info=True)
            message = str(exc) if os.environ.get(Constants.AGENT_DEBUG_ERRORS) else "Internal server error"
            return error_response(
                "internal_error",
                message,
                status_code=500,
                headers={Constants.INVOCATION_ID_HEADER: invocation_id},
            )

        # For streaming responses, wrap the body iterator so the span stays
        # open until all chunks are sent and captures any streaming errors.
        if isinstance(response, StreamingResponse):
            response.body_iterator = self._tracing.trace_stream(response.body_iterator, otel_span)
        else:
            self._tracing.end_span(otel_span)

        # Auto-inject invocation_id header if developer didn't set it
        if Constants.INVOCATION_ID_HEADER not in response.headers:
            response.headers[Constants.INVOCATION_ID_HEADER] = invocation_id

        return response

    async def _get_invocation_endpoint(self, request: Request) -> Response:
        """GET /invocations/{invocation_id} — retrieve an invocation result.

        :param request: The incoming Starlette request.
        :type request: Request
        :return: The stored result or 404.
        :rtype: Response
        """
        invocation_id = request.path_params["invocation_id"]
        request.state.invocation_id = invocation_id
        carrier = extract_w3c_carrier(request.headers)
        with self._tracing.span(
            "AgentServer.get_invocation",
            attributes={"invocation.id": invocation_id},
            carrier=carrier,
        ) as _otel_span:
            try:
                return await self.get_invocation(request)
            except Exception as exc:  # pylint: disable=broad-exception-caught
                self._tracing.record_error(_otel_span, exc)
                logger.error("Error in get_invocation %s: %s", invocation_id, exc, exc_info=True)
                message = str(exc) if os.environ.get(Constants.AGENT_DEBUG_ERRORS) else "Internal server error"
                return error_response(
                    "internal_error",
                    message,
                    status_code=500,
                )

    async def _cancel_invocation_endpoint(self, request: Request) -> Response:
        """POST /invocations/{invocation_id}/cancel — cancel an invocation.

        :param request: The incoming Starlette request.
        :type request: Request
        :return: The cancellation result or 404.
        :rtype: Response
        """
        invocation_id = request.path_params["invocation_id"]
        request.state.invocation_id = invocation_id
        carrier = extract_w3c_carrier(request.headers)
        with self._tracing.span(
            "AgentServer.cancel_invocation",
            attributes={"invocation.id": invocation_id},
            carrier=carrier,
        ) as _otel_span:
            try:
                return await self.cancel_invocation(request)
            except Exception as exc:  # pylint: disable=broad-exception-caught
                self._tracing.record_error(_otel_span, exc)
                logger.error("Error in cancel_invocation %s: %s", invocation_id, exc, exc_info=True)
                message = str(exc) if os.environ.get(Constants.AGENT_DEBUG_ERRORS) else "Internal server error"
                return error_response(
                    "internal_error",
                    message,
                    status_code=500,
                )

    async def _liveness_endpoint(self, request: Request) -> Response:  # pylint: disable=unused-argument
        """GET /liveness — health check.

        :param request: The incoming Starlette request.
        :type request: Request
        :return: 200 OK response.
        :rtype: Response
        """
        return JSONResponse({"status": "alive"})

    async def _readiness_endpoint(self, request: Request) -> Response:  # pylint: disable=unused-argument
        """GET /readiness — readiness check.

        :param request: The incoming Starlette request.
        :type request: Request
        :return: 200 OK response.
        :rtype: Response
        """
        return JSONResponse({"status": "ready"})

    async def _metrics_endpoint(self, request: Request) -> Response:  # pylint: disable=unused-argument
        """GET /metrics — Prometheus text exposition format.

        :param request: The incoming Starlette request.
        :type request: Request
        :return: Prometheus metrics in text format.
        :rtype: Response
        """
        data = self._metrics.render()
        return Response(
            content=data,
            media_type="text/plain; version=0.0.4; charset=utf-8",
        )
