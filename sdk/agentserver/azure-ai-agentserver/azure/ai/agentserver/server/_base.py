# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import contextlib
import inspect
import os
import uuid
from abc import abstractmethod
from typing import Any, AsyncGenerator, Optional, Union

import uvicorn
from opentelemetry import trace
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse
from starlette.routing import Route

from .._constants import Constants
from .._logger import configure_logging, get_logger
from .._types import InvokeRequest
from ..validation._openapi_validator import OpenApiValidator

logger = get_logger()


class AgentServer:
    """Generic agent server base with pluggable protocol heads.

    Subclass and implement :meth:`invoke` to handle ``/invocations`` requests.
    Optionally override :meth:`get_invocation` and :meth:`cancel_invocation`
    for long-running invocation support.

    :param openapi_spec: Optional OpenAPI spec dict for request/response validation.
    :type openapi_spec: Optional[dict[str, Any]]
    """

    def __init__(self, openapi_spec: Optional[dict[str, Any]] = None) -> None:
        configure_logging()
        self._openapi_spec = openapi_spec
        self._validator: Optional[OpenApiValidator] = (
            OpenApiValidator(openapi_spec) if openapi_spec else None
        )
        self._tracer = trace.get_tracer("azure.ai.agentserver")
        self._build_app()

    # ------------------------------------------------------------------
    # Abstract / overridable protocol methods
    # ------------------------------------------------------------------

    @abstractmethod
    async def invoke(
        self,
        request: InvokeRequest,
    ) -> Union[bytes, AsyncGenerator[bytes, None]]:
        """Process an invocation.

        Return either:
        - ``bytes`` for a non-streaming response
        - ``AsyncGenerator[bytes, None]`` for a streaming response that yields chunks

        :param request: The invoke request containing body, headers, and invocation_id.
        :type request: InvokeRequest
        :return: Response bytes or an async generator of byte chunks.
        :rtype: Union[bytes, AsyncGenerator[bytes, None]]
        """

    async def get_invocation(self, invocation_id: str) -> bytes:
        """Retrieve a previous invocation result.

        Default implementation raises :class:`NotImplementedError` (returns 404).
        Override to support retrieval.

        :param invocation_id: The invocation ID to look up.
        :type invocation_id: str
        :return: The stored invocation result as bytes.
        :rtype: bytes
        :raises NotImplementedError: When not overridden.
        """
        raise NotImplementedError

    async def cancel_invocation(
        self,
        invocation_id: str,
        body: Optional[bytes] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> bytes:
        """Cancel an invocation.

        Default implementation raises :class:`NotImplementedError` (returns 404).
        Override to support cancellation.

        :param invocation_id: The invocation ID to cancel.
        :type invocation_id: str
        :param body: Optional request body bytes.
        :type body: Optional[bytes]
        :param headers: Optional request headers.
        :type headers: Optional[dict[str, str]]
        :return: Cancellation result as bytes.
        :rtype: bytes
        :raises NotImplementedError: When not overridden.
        """
        raise NotImplementedError

    def get_openapi_spec(self) -> Optional[dict[str, Any]]:
        """Return the OpenAPI spec dict for this agent, or None.

        :return: The registered OpenAPI spec or None.
        :rtype: Optional[dict[str, Any]]
        """
        return self._openapi_spec

    def set_openapi_spec(self, spec: dict[str, Any]) -> None:
        """Register or replace the OpenAPI spec at runtime.

        :param spec: An OpenAPI spec dictionary.
        :type spec: dict[str, Any]
        """
        self._openapi_spec = spec
        self._validator = OpenApiValidator(spec)

    # ------------------------------------------------------------------
    # Run helpers
    # ------------------------------------------------------------------

    def run(self, port: Optional[int] = None) -> None:
        """Start the server synchronously via uvicorn.

        :param port: Port to bind. Defaults to ``DEFAULT_AD_PORT`` env var or 8088.
        :type port: Optional[int]
        """
        resolved_port = self._resolve_port(port)
        logger.info("AgentServer starting on port %s", resolved_port)
        uvicorn.run(self.app, host="0.0.0.0", port=resolved_port)

    async def run_async(self, port: Optional[int] = None) -> None:
        """Start the server asynchronously (awaitable).

        :param port: Port to bind. Defaults to ``DEFAULT_AD_PORT`` env var or 8088.
        :type port: Optional[int]
        """
        resolved_port = self._resolve_port(port)
        logger.info("AgentServer starting on port %s (async)", resolved_port)
        config = uvicorn.Config(self.app, host="0.0.0.0", port=resolved_port)
        server = uvicorn.Server(config)
        await server.serve()

    # ------------------------------------------------------------------
    # Private: app construction
    # ------------------------------------------------------------------

    def _build_app(self) -> None:
        """Construct the Starlette ASGI application with all routes."""

        @contextlib.asynccontextmanager
        async def _lifespan(app: Starlette):  # type: ignore[no-untyped-def]
            logger.info("AgentServer started")
            yield

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

        self.app = Starlette(routes=routes, lifespan=_lifespan)
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # ------------------------------------------------------------------
    # Private: endpoint handlers
    # ------------------------------------------------------------------

    async def _get_openapi_spec_endpoint(self, request: Request) -> Response:
        """GET /invocations/docs/openapi.json — return registered spec or 404.

        :param request: The incoming Starlette request.
        :type request: Request
        :return: JSON response with the spec or 404.
        :rtype: Response
        """
        spec = self.get_openapi_spec()
        if spec is None:
            return JSONResponse({"error": "No OpenAPI spec registered"}, status_code=404)
        return JSONResponse(spec)

    async def _create_invocation_endpoint(self, request: Request) -> Response:
        """POST /invocations — create and process an invocation.

        :param request: The incoming Starlette request.
        :type request: Request
        :return: The invocation result or error response.
        :rtype: Response
        """
        body = await request.body()
        headers = dict(request.headers)
        invocation_id = str(uuid.uuid4())
        invoke_request = InvokeRequest(body=body, headers=headers, invocation_id=invocation_id)

        # Validate request body against OpenAPI spec
        if self._validator is not None:
            content_type = headers.get("content-type", "application/json")
            errors = self._validator.validate_request(body, content_type)
            if errors:
                return JSONResponse(
                    {"error": "Request validation failed", "details": errors},
                    status_code=400,
                )

        with self._tracer.start_as_current_span(
            name="agentserver-invoke",
            kind=trace.SpanKind.SERVER,
        ):
            try:
                result = self.invoke(invoke_request)
                # If invoke() is a coroutine (non-streaming), await it.
                # If it's an async generator (streaming), use it directly.
                if not inspect.isasyncgen(result) and inspect.isawaitable(result):
                    result = await result
            except Exception as exc:
                logger.error("Error processing invocation %s: %s", invocation_id, exc, exc_info=True)
                error_message = str(exc) if os.environ.get(Constants.AGENT_DEBUG_ERRORS) else "Internal server error"
                return JSONResponse(
                    {"error": error_message},
                    status_code=500,
                    headers={"x-agent-invocation-id": invocation_id},
                )

        response_headers = {"x-agent-invocation-id": invocation_id}

        if isinstance(result, bytes):
            # Non-streaming: optionally validate response
            if self._validator is not None:
                content_type = "application/json"
                resp_errors = self._validator.validate_response(result, content_type)
                if resp_errors:
                    logger.warning(
                        "Response validation warnings for invocation %s: %s",
                        invocation_id,
                        resp_errors,
                    )
            return Response(content=result, media_type="application/json", headers=response_headers)

        # Streaming: result is an AsyncGenerator
        return StreamingResponse(result, headers=response_headers)

    async def _get_invocation_endpoint(self, request: Request) -> Response:
        """GET /invocations/{invocation_id} — retrieve an invocation result.

        :param request: The incoming Starlette request.
        :type request: Request
        :return: The stored result or 404.
        :rtype: Response
        """
        invocation_id = request.path_params["invocation_id"]
        try:
            result = await self.get_invocation(invocation_id)
            return Response(content=result)
        except NotImplementedError:
            return JSONResponse(
                {"error": "get_invocation not supported"},
                status_code=404,
            )
        except Exception as exc:
            logger.error("Error in get_invocation %s: %s", invocation_id, exc, exc_info=True)
            error_message = str(exc) if os.environ.get(Constants.AGENT_DEBUG_ERRORS) else "Internal server error"
            return JSONResponse(
                {"error": error_message},
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
        body = await request.body()
        headers = dict(request.headers)
        try:
            result = await self.cancel_invocation(invocation_id, body=body, headers=headers)
            return Response(content=result)
        except NotImplementedError:
            return JSONResponse(
                {"error": "cancel_invocation not supported"},
                status_code=404,
            )
        except Exception as exc:
            logger.error("Error in cancel_invocation %s: %s", invocation_id, exc, exc_info=True)
            error_message = str(exc) if os.environ.get(Constants.AGENT_DEBUG_ERRORS) else "Internal server error"
            return JSONResponse(
                {"error": error_message},
                status_code=500,
            )

    async def _liveness_endpoint(self, request: Request) -> Response:
        """GET /liveness — health check.

        :param request: The incoming Starlette request.
        :type request: Request
        :return: 200 OK response.
        :rtype: Response
        """
        return JSONResponse({"status": "alive"})

    async def _readiness_endpoint(self, request: Request) -> Response:
        """GET /readiness — readiness check.

        :param request: The incoming Starlette request.
        :type request: Request
        :return: 200 OK response.
        :rtype: Response
        """
        return JSONResponse({"status": "ready"})

    # ------------------------------------------------------------------
    # Private: helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_port(port: Optional[int]) -> int:
        """Resolve the server port from argument, env var, or default.

        :param port: Explicitly requested port or None.
        :type port: Optional[int]
        :return: The resolved port number.
        :rtype: int
        """
        if port is not None:
            return port
        env_port = os.environ.get(Constants.DEFAULT_AD_PORT)
        if env_port:
            try:
                return int(env_port)
            except ValueError:
                pass
        return Constants.DEFAULT_PORT
