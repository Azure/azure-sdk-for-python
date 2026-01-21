# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=broad-exception-caught,unused-argument,logging-fstring-interpolation,too-many-statements,too-many-return-statements
# mypy: ignore-errors
import asyncio  # pylint: disable=C4763
import inspect
import json
import os
import time
from abc import abstractmethod
from typing import Any, AsyncGenerator, Generator, Optional, Union

import uvicorn
from opentelemetry import context as otel_context, trace
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from starlette.applications import Starlette
from starlette.concurrency import iterate_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse
from starlette.routing import Route
from starlette.types import ASGIApp

from azure.core.credentials import TokenCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.identity.aio import DefaultAzureCredential as AsyncDefaultTokenCredential

from ._context import AgentServerContext
from ..models import projects as project_models
from ..constants import Constants
from ..logger import APPINSIGHT_CONNSTR_ENV_NAME, get_logger, get_project_endpoint, request_context
from ..models import (
    Response as OpenAIResponse,
    ResponseStreamEvent,
)
from .common.agent_run_context import AgentRunContext

from ..tools import DefaultFoundryToolRuntime, UserInfoContextMiddleware
from ..utils._credential import AsyncTokenCredentialAdapter

logger = get_logger()
DEBUG_ERRORS = os.environ.get(Constants.AGENT_DEBUG_ERRORS, "false").lower() == "true"
KEEP_ALIVE_INTERVAL = 15.0  # seconds

class AgentRunContextMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, agent: Optional['FoundryCBAgent'] = None):
        super().__init__(app)
        self.agent = agent

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
            ctx["azure.ai.agentserver.x-request-id"] = request_id
            request_context.set(ctx)

    def set_run_context_to_context_var(self, run_context):
        agent_id, agent_name = "", ""
        agent_obj = run_context.get_agent_id_object()
        if agent_obj:
            agent_name = getattr(agent_obj, "name", "")
            agent_version = getattr(agent_obj, "version", "")
            agent_id = f"{agent_name}:{agent_version}"

        res = {
            "azure.ai.agentserver.response_id": run_context.response_id or "",
            "azure.ai.agentserver.conversation_id": run_context.conversation_id or "",
            "azure.ai.agentserver.streaming": str(run_context.stream or False),
            "gen_ai.agent.id": agent_id,
            "gen_ai.agent.name": agent_name,
            "gen_ai.provider.name": "AzureAI Hosted Agents",
            "gen_ai.response.id": run_context.response_id or "",
        }
        ctx = request_context.get() or {}
        ctx.update(res)
        request_context.set(ctx)


class FoundryCBAgent:
    def __init__(self,
                 credentials: Optional[Union[AsyncTokenCredential, TokenCredential]] = None,
                 project_endpoint: Optional[str] = None) -> None:
        self.credentials = AsyncTokenCredentialAdapter(credentials) if credentials else AsyncDefaultTokenCredential()
        project_endpoint = get_project_endpoint() or project_endpoint
        if not project_endpoint:
            raise ValueError("Project endpoint is required.")
        AgentServerContext(DefaultFoundryToolRuntime(project_endpoint, self.credentials))

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
                    logger.info("Start processing CreateResponse request.")

                    context_carrier = {}
                    TraceContextTextMapPropagator().inject(context_carrier)

                    ex = None
                    resp = await self.agent_run(context)
                except Exception as e:
                    # TODO: extract status code from exception
                    logger.error(f"Error processing CreateResponse request: {e}", exc_info=True)
                    ex = e

                if not context.stream:
                    logger.info("End of processing CreateResponse request.")
                    result = resp if not ex else project_models.ResponseError(
                        code=project_models.ResponseErrorCode.SERVER_ERROR,
                        message=_format_error(ex))
                    return JSONResponse(result.as_dict())

                async def gen_async(ex):
                    ctx = TraceContextTextMapPropagator().extract(carrier=context_carrier)
                    token = otel_context.attach(ctx)
                    seq = 0
                    try:
                        if ex:
                            return
                        it = iterate_in_threadpool(resp) if inspect.isgenerator(resp) else resp
                        # Wrap iterator with keep-alive mechanism
                        async for event in _iter_with_keep_alive(it):
                            if event is None:
                                # Keep-alive signal
                                yield _keep_alive_comment()
                            else:
                                seq += 1
                                yield _event_to_sse_chunk(event)
                        logger.info("End of processing CreateResponse request.")
                    except Exception as e:  # noqa: BLE001
                        logger.error("Error in async generator: %s", e, exc_info=True)
                        ex = e
                    finally:
                        if ex:
                            err = project_models.ResponseErrorEvent(
                                sequence_number=seq + 1,
                                code=project_models.ResponseErrorCode.SERVER_ERROR,
                                message=_format_error(ex),
                                param="")
                            yield _event_to_sse_chunk(err)
                        otel_context.detach(token)

                return StreamingResponse(gen_async(ex), media_type="text/event-stream")

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
        UserInfoContextMiddleware.install(self.app)
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.app.add_middleware(AgentRunContextMiddleware, agent=self)

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

    async def respond_with_oauth_consent(self, context, error) -> project_models.Response:
        """Generate a response indicating that OAuth consent is required.

        :param context: The agent run context.
        :type context: AgentRunContext
        :param error: The OAuthConsentRequiredError instance.
        :type error: OAuthConsentRequiredError
        :return: A Response indicating the need for OAuth consent.
        :rtype: project_models.Response
        """
        output = [
            project_models.OAuthConsentRequestItemResource(
                id=context.id_generator.generate_oauthreq_id(),
                consent_link=error.consent_url,
                server_label="server_label"
            )
        ]
        agent_id = context.get_agent_id_object()
        conversation = context.get_conversation_object()
        response =  project_models.Response({
            "object": "response",
            "id": context.response_id,
            "agent": agent_id,
            "conversation": conversation,
            "metadata": context.request.get("metadata"),
            "created_at": int(time.time()),
            "output": output,
        })
        return response

    async def respond_with_oauth_consent_astream(self, context, error) -> AsyncGenerator[ResponseStreamEvent, None]:
        """Generate a response stream indicating that OAuth consent is required.

        :param context: The agent run context.
        :type context: AgentRunContext
        :param error: The OAuthConsentRequiredError instance.
        :type error: OAuthConsentRequiredError
        :return: An async generator yielding ResponseStreamEvent instances.
        :rtype: AsyncGenerator[ResponseStreamEvent, None]
        """
        sequence_number = 0
        agent_id = context.get_agent_id_object()
        conversation = context.get_conversation_object()

        response = project_models.Response({
            "object": "response",
            "id": context.response_id,
            "agent": agent_id,
            "conversation": conversation,
            "metadata": context.request.get("metadata"),
            "status": "in_progress",
            "created_at": int(time.time()),
        })
        yield project_models.ResponseCreatedEvent(sequence_number=sequence_number, response=response)
        sequence_number += 1

        response = project_models.Response({
            "object": "response",
            "id": context.response_id,
            "agent": agent_id,
            "conversation": conversation,
            "metadata": context.request.get("metadata"),
            "status": "in_progress",
            "created_at": int(time.time()),
        })
        yield project_models.ResponseInProgressEvent(sequence_number=sequence_number, response=response)

        sequence_number += 1
        output_index = 0
        oauth_id = context.id_generator.generate_oauthreq_id()
        item = project_models.OAuthConsentRequestItemResource({
            "id": oauth_id,
            "type": "oauth_consent_request",
            "consent_link": error.consent_url,
            "server_label": "server_label",
        })
        yield project_models.ResponseOutputItemAddedEvent(sequence_number=sequence_number,
                                                          output_index=output_index, item=item)
        sequence_number += 1
        yield project_models.ResponseStreamEvent({
            "sequence_number": sequence_number,
            "output_index": output_index,
            "id": oauth_id,
            "type": "response.oauth_consent_requested",
            "consent_link": error.consent_url,
            "server_label": "server_label",
        })

        sequence_number += 1
        yield project_models.ResponseOutputItemDoneEvent(sequence_number=sequence_number,
                                                         output_index=output_index, item=item)
        sequence_number += 1
        output = [
            project_models.OAuthConsentRequestItemResource(
                id= oauth_id,
                consent_link=error.consent_url,
                server_label="server_label"
            )
        ]

        response =  project_models.Response({
            "object": "response",
            "id": context.response_id,
            "agent": agent_id,
            "conversation": conversation,
            "metadata": context.request.get("metadata"),
            "created_at": int(time.time()),
            "status": "completed",
            "output": output,
        })
        yield project_models.ResponseCompletedEvent(sequence_number=sequence_number, response=response)

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
        app_insights_conn_str = os.environ.get(APPINSIGHT_CONNSTR_ENV_NAME)
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
            "service.name": "azure.ai.agentserver",
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


def _keep_alive_comment() -> str:
    """Generate a keep-alive SSE comment to maintain connection.

    :return: The keep-alive comment string.
    :rtype: str
    """
    return ": keep-alive\n\n"


async def _iter_with_keep_alive(
    it: AsyncGenerator[ResponseStreamEvent, None]
) -> AsyncGenerator[Optional[ResponseStreamEvent], None]:
    """Wrap an async iterator with keep-alive mechanism.

    If no event is received within KEEP_ALIVE_INTERVAL seconds,
    yields None as a signal to send a keep-alive comment.
    The original iterator is protected with asyncio.shield to ensure
    it continues running even when timeout occurs.

    :param it: The async generator to wrap.
    :type it: AsyncGenerator[ResponseStreamEvent, None]
    :return: An async generator that yields events or None for keep-alive.
    :rtype: AsyncGenerator[Optional[ResponseStreamEvent], None]
    """
    it_anext = it.__anext__
    pending_task: Optional[asyncio.Task] = None

    while True:
        try:
            # If there's a pending task from previous timeout, wait for it first
            if pending_task is not None:
                event = await pending_task
                pending_task = None
                yield event
                continue

            # Create a task for the next event
            next_event_task = asyncio.create_task(it_anext())

            try:
                # Shield the task and wait with timeout
                event = await asyncio.wait_for(
                    asyncio.shield(next_event_task),
                    timeout=KEEP_ALIVE_INTERVAL
                )
                yield event
            except asyncio.TimeoutError:
                # Timeout occurred, but task continues due to shield
                # Save task to check in next iteration
                pending_task = next_event_task
                yield None

        except StopAsyncIteration:
            # Iterator exhausted
            break


def _format_error(exc: Exception) -> str:
    message = str(exc)
    if message:
        return message
    if DEBUG_ERRORS:
        return repr(exc)
    return f"{type(exc)}: Internal error"


def _to_response(result: Union[Response, dict]) -> Response:
    return result if isinstance(result, Response) else JSONResponse(result)
