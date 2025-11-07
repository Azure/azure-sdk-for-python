# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=broad-exception-caught,unused-argument,logging-fstring-interpolation,too-many-statements,too-many-return-statements
import inspect
import json
import os
import traceback
from abc import abstractmethod
from typing import Any, AsyncGenerator, Generator, Union

import uvicorn
from opentelemetry import context as otel_context, trace
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse
from starlette.routing import Route
from starlette.types import ASGIApp

from ..constants import Constants
from ..logger import get_logger, request_context
from ..models import (
    Response as OpenAIResponse,
    ResponseStreamEvent,
)
from .common.agent_run_context import AgentRunContext

logger = get_logger()
DEBUG_ERRORS = os.environ.get(Constants.AGENT_DEBUG_ERRORS, "false").lower() == "true"


class AgentRunContextMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        if request.url.path in ("/runs", "/responses"):
            try:
                self.set_request_id_to_context_var(request)
                payload = await request.json()
            except Exception as e:
                logger.error(f"Invalid JSON payload: {e}")
                return JSONResponse({"error": f"Invalid JSON payload: {e}"}, status_code=400)
            try:
                request.state.agent_run_context = AgentRunContext(payload)
                self.set_run_context_to_context_var(request.state.agent_run_context)
            except Exception as e:
                logger.error(f"Context build failed: {e}.", exc_info=True)
                return JSONResponse({"error": f"Context build failed: {e}"}, status_code=500)
        return await call_next(request)

    def set_request_id_to_context_var(self, request):
        request_id = request.headers.get("X-Request-Id", None)
        if request_id:
            ctx = request_context.get() or {}
            ctx["azure.ai.agentshosting.x-request-id"] = request_id
            request_context.set(ctx)

    def set_run_context_to_context_var(self, run_context):
        agent_id, agent_name = "", ""
        agent_obj = run_context.get_agent_id_object()
        if agent_obj:
            agent_name = getattr(agent_obj, "name", "")
            agent_version = getattr(agent_obj, "version", "")
            agent_id = f"{agent_name}:{agent_version}"

        res = {
            "azure.ai.agentshosting.response_id": run_context.response_id or "",
            "azure.ai.agentshosting.conversation_id": run_context.conversation_id or "",
            "azure.ai.agentshosting.streaming": str(run_context.stream or False),
            "gen_ai.agent.id": agent_id,
            "gen_ai.agent.name": agent_name,
            "gen_ai.provider.name": "AzureAI Hosted Agents",
            "gen_ai.response.id": run_context.response_id or "",
        }
        ctx = request_context.get() or {}
        ctx.update(res)
        request_context.set(ctx)


class FoundryCBAgent:
    def __init__(self):
        async def runs_endpoint(request):
            # Set up tracing context and span
            context = request.state.agent_run_context
            ctx = request_context.get()
            with self.tracer.start_as_current_span(
                name=f"HostedAgents-{context.response_id}",
                attributes=ctx,
                kind=trace.SpanKind.SERVER,
            ):
                try:
                    logger.info("Start processing CreateResponse request:")

                    context_carrier = {}
                    TraceContextTextMapPropagator().inject(context_carrier)

                    resp = await self.agent_run(context)

                    if inspect.isgenerator(resp):
                        # Prefetch first event to allow 500 status if generation fails immediately
                        try:
                            first_event = next(resp)
                        except Exception as e:  # noqa: BLE001
                            err_msg = str(e) if DEBUG_ERRORS else "Internal error"
                            logger.error("Generator initialization failed: %s\n%s", e, traceback.format_exc())
                            return JSONResponse({"error": err_msg}, status_code=500)

                        def gen():
                            ctx = TraceContextTextMapPropagator().extract(carrier=context_carrier)
                            token = otel_context.attach(ctx)
                            error_sent = False
                            try:
                                # yield prefetched first event
                                yield _event_to_sse_chunk(first_event)
                                for event in resp:
                                    yield _event_to_sse_chunk(event)
                            except Exception as e:  # noqa: BLE001
                                err_msg = str(e) if DEBUG_ERRORS else "Internal error"
                                logger.error("Error in non-async generator: %s\n%s", e, traceback.format_exc())
                                payload = {"error": err_msg}
                                yield f"event: error\ndata: {json.dumps(payload)}\n\n"
                                yield "data: [DONE]\n\n"
                                error_sent = True
                            finally:
                                logger.info("End of processing CreateResponse request:")
                                otel_context.detach(token)
                                if not error_sent:
                                    yield "data: [DONE]\n\n"

                        return StreamingResponse(gen(), media_type="text/event-stream")
                    if inspect.isasyncgen(resp):
                        # Prefetch first async event to allow early 500
                        try:
                            first_event = await resp.__anext__()
                        except StopAsyncIteration:
                            # No items produced; treat as empty successful stream
                            def empty_gen():
                                yield "data: [DONE]\n\n"

                            return StreamingResponse(empty_gen(), media_type="text/event-stream")
                        except Exception as e:  # noqa: BLE001
                            err_msg = str(e) if DEBUG_ERRORS else "Internal error"
                            logger.error("Async generator initialization failed: %s\n%s", e, traceback.format_exc())
                            return JSONResponse({"error": err_msg}, status_code=500)

                        async def gen_async():
                            ctx = TraceContextTextMapPropagator().extract(carrier=context_carrier)
                            token = otel_context.attach(ctx)
                            error_sent = False
                            try:
                                # yield prefetched first event
                                yield _event_to_sse_chunk(first_event)
                                async for event in resp:
                                    yield _event_to_sse_chunk(event)
                            except Exception as e:  # noqa: BLE001
                                err_msg = str(e) if DEBUG_ERRORS else "Internal error"
                                logger.error("Error in async generator: %s\n%s", e, traceback.format_exc())
                                payload = {"error": err_msg}
                                yield f"event: error\ndata: {json.dumps(payload)}\n\n"
                                yield "data: [DONE]\n\n"
                                error_sent = True
                            finally:
                                logger.info("End of processing CreateResponse request.")
                                otel_context.detach(token)
                                if not error_sent:
                                    yield "data: [DONE]\n\n"

                        return StreamingResponse(gen_async(), media_type="text/event-stream")
                    logger.info("End of processing CreateResponse request.")
                    return JSONResponse(resp.as_dict())
                except Exception as e:
                    # TODO: extract status code from exception
                    logger.error(f"Error processing CreateResponse request: {traceback.format_exc()}")
                    return JSONResponse({"error": str(e)}, status_code=500)

        async def liveness_endpoint(request):
            result = await self.agent_liveness(request)
            return _to_response(result)

        async def readiness_endpoint(request):
            result = await self.agent_readiness(request)
            return _to_response(result)

        routes = [
            Route("/runs", runs_endpoint, methods=["POST"], name="agent_run"),
            Route("/responses", runs_endpoint, methods=["POST"], name="agent_response"),
            Route("/liveness", liveness_endpoint, methods=["GET"], name="agent_liveness"),
            Route("/readiness", readiness_endpoint, methods=["GET"], name="agent_readiness"),
        ]

        self.app = Starlette(routes=routes)
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.app.add_middleware(AgentRunContextMiddleware)

        @self.app.on_event("startup")
        async def attach_appinsights_logger():
            import logging

            for handler in logger.handlers:
                if handler.name == "appinsights_handler":
                    for logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
                        uv_logger = logging.getLogger(logger_name)
                        uv_logger.addHandler(handler)
                        uv_logger.setLevel(logger.level)
                        uv_logger.propagate = False

        self.tracer = None

    @abstractmethod
    async def agent_run(
        self, context: AgentRunContext
    ) -> Union[OpenAIResponse, Generator[ResponseStreamEvent, Any, Any], AsyncGenerator[ResponseStreamEvent, Any]]:
        raise NotImplementedError

    async def agent_liveness(self, request) -> Union[Response, dict]:
        return Response(status_code=200)

    async def agent_readiness(self, request) -> Union[Response, dict]:
        return {"status": "ready"}

    async def run_async(
        self,
        port: int = int(os.environ.get("DEFAULT_AD_PORT", 8088)),
    ) -> None:
        """
        Awaitable server starter for use **inside** an existing event loop.

        :param port: Port to listen on.
        :type port: int
        """
        self.init_tracing()
        config = uvicorn.Config(self.app, host="0.0.0.0", port=port, loop="asyncio")
        server = uvicorn.Server(config)
        logger.info(f"Starting FoundryCBAgent server async on port {port}")
        await server.serve()

    def run(self, port: int = int(os.environ.get("DEFAULT_AD_PORT", 8088))) -> None:
        """
        Start a Starlette server on localhost:<port> exposing:
          POST  /runs
          POST  /responses
          GET   /liveness
          GET   /readiness

        :param port: Port to listen on.
        :type port: int
        """
        self.init_tracing()
        logger.info(f"Starting FoundryCBAgent server on port {port}")
        uvicorn.run(self.app, host="0.0.0.0", port=port)

    def init_tracing(self):
        exporter = os.environ.get(Constants.OTEL_EXPORTER_ENDPOINT)
        app_insights_conn_str = os.environ.get(Constants.APPLICATION_INSIGHTS_CONNECTION_STRING)
        if exporter or app_insights_conn_str:
            from opentelemetry.sdk.resources import Resource
            from opentelemetry.sdk.trace import TracerProvider

            resource = Resource.create(self.get_trace_attributes())
            provider = TracerProvider(resource=resource)
            if exporter:
                self.setup_otlp_exporter(exporter, provider)
            if app_insights_conn_str:
                self.setup_application_insights_exporter(app_insights_conn_str, provider)
            trace.set_tracer_provider(provider)
            self.init_tracing_internal(exporter_endpoint=exporter, app_insights_conn_str=app_insights_conn_str)
        self.tracer = trace.get_tracer(__name__)

    def get_trace_attributes(self):
        return {
            "service.name": "azure.ai.agentshosting",
        }

    def init_tracing_internal(self, exporter_endpoint=None, app_insights_conn_str=None):
        pass

    def setup_application_insights_exporter(self, connection_string, provider):
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

        exporter_instance = AzureMonitorTraceExporter.from_connection_string(connection_string)
        processor = BatchSpanProcessor(exporter_instance)
        provider.add_span_processor(processor)
        logger.info("Tracing setup with Application Insights exporter.")

    def setup_otlp_exporter(self, endpoint, provider):
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        exporter_instance = OTLPSpanExporter(endpoint=endpoint)
        processor = BatchSpanProcessor(exporter_instance)
        provider.add_span_processor(processor)
        logger.info(f"Tracing setup with OTLP exporter: {endpoint}")


def _event_to_sse_chunk(event: ResponseStreamEvent) -> str:
    event_data = json.dumps(event.as_dict())
    if event.type:
        return f"event: {event.type}\ndata: {event_data}\n\n"
    return f"data: {event_data}\n\n"


def _to_response(result: Union[Response, dict]) -> Response:
    return result if isinstance(result, Response) else JSONResponse(result)
