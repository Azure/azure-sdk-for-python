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
from azure.identity.aio import (
    DefaultAzureCredential as AsyncDefaultTokenCredential,
    get_bearer_token_provider,
)

from ._context import AgentServerContext
from ._response_metadata import (
    attach_foundry_metadata_to_response,
    build_foundry_agents_metadata_headers,
    try_attach_foundry_metadata_to_event,
)
from .common.agent_run_context import AgentRunContext
from ..constants import Constants
from ..logger import APPINSIGHT_CONNSTR_ENV_NAME, get_logger, get_project_endpoint, request_context
from ..models import Response as OpenAIResponse, ResponseStreamEvent, projects as project_models
from ..tools import UserInfoContextMiddleware, create_tool_runtime
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
        self._project_endpoint = get_project_endpoint(logger=logger) or project_endpoint
        AgentServerContext(create_tool_runtime(self._project_endpoint, self.credentials))
        self._port: Optional[int] = None

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

                    # Save input to conversation if store=True
                    if self._should_store(context):
                        logger.debug("Storing input to conversation.")
                        await self._save_input_to_conversation(context)

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
                    if not ex:
                        attach_foundry_metadata_to_response(result)
                        # Save output to conversation if store=True
                        if self._should_store(context):
                            logger.debug("Storing output to conversation.")
                            await self._save_output_to_conversation(context, result)
                    return JSONResponse(result.as_dict(), headers=self.create_response_headers())

                async def gen_async(ex):
                    ctx = TraceContextTextMapPropagator().extract(carrier=context_carrier)
                    prev_ctx = otel_context.get_current()
                    otel_context.attach(ctx)
                    seq = 0
                    output_events = []  # Collect events for saving to conversation
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
                                try_attach_foundry_metadata_to_event(event)
                                seq += 1
                                output_events.append(event)
                                yield _event_to_sse_chunk(event)
                        logger.info("End of processing CreateResponse request.")
                        # Save output to conversation if store=True
                        if self._should_store(context):
                            logger.debug("Storing output to conversation.")
                            await self._save_output_events_to_conversation(context, output_events)
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
                        otel_context.attach(prev_ctx)

                return StreamingResponse(
                    gen_async(ex),
                    media_type="text/event-stream",
                    headers=self.create_response_headers(),
                )

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
        async def on_startup():
            import logging

            # Log server started successfully
            port = getattr(self, '_port', 'unknown')
            logger.info(f"FoundryCBAgent server started successfully on port {port}")

            # Attach App Insights handler to uvicorn loggers
            for handler in logger.handlers:
                if handler.name == "appinsights_handler":
                    for logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
                        uv_logger = logging.getLogger(logger_name)
                        uv_logger.addHandler(handler)
                        uv_logger.setLevel(logger.level)
                        uv_logger.propagate = False

        self.tracer = None

    def _should_store(self, context: AgentRunContext) -> bool:
        """Determine whether conversation artifacts should be persisted.

        :param context: Agent run context that contains the incoming request payload.
        :type context: AgentRunContext
        :return: ``True`` when storage is requested and the conversation is scoped to a project.
        :rtype: bool
        """
        return context.request.get("store", False) and context.conversation_id and self._project_endpoint

    def _items_are_equal(self, item1: dict, item2: dict) -> bool:
        """Compare two conversation items for equality based on type and content.

        :param item1: First conversation item.
        :type item1: dict
        :param item2: Second conversation item.
        :type item2: dict
        :return: ``True`` when both the metadata and content match.
        :rtype: bool
        """
        if item1.get("type") != item2.get("type"):
            return False
        if item1.get("role") != item2.get("role"):
            return False
        # Compare content - handle both string and structured content
        content1 = item1.get("content")
        content2 = item2.get("content")
        if isinstance(content1, str) and isinstance(content2, str):
            return content1 == content2
        if isinstance(content1, list) and isinstance(content2, list):
            # For structured content, compare text parts
            text1 = "".join(p.get("text", "") for p in content1 if isinstance(p, dict))
            text2 = "".join(p.get("text", "") for p in content2 if isinstance(p, dict))
            return text1 == text2
        return content1 == content2

    async def _create_openai_client(self) -> "AsyncOpenAI":
        """Create an AsyncOpenAI client for conversation operations.

        :return: Configured AsyncOpenAI client scoped to the Foundry project endpoint.
        :rtype: AsyncOpenAI
        """
        from openai import AsyncOpenAI

        token_provider = get_bearer_token_provider(
            self.credentials, "https://ai.azure.com/.default"
        )
        token = await token_provider()
        return AsyncOpenAI(
            base_url=f"{self._project_endpoint}/openai",
            api_key=token,
            default_query={"api-version": "2025-11-15-preview"},
        )

    async def _save_input_to_conversation(self, context: AgentRunContext) -> None:
        """Persist request input items when storage is enabled on the request.

        :param context: Agent run context containing the request payload and conversation metadata.
        :type context: AgentRunContext
        :return: None
        :rtype: None
        """
        try:
            conversation_id = context.conversation_id
            input_items = context.request.get("input", [])
            if not input_items:
                return

            # Handle string input as a single item
            if isinstance(input_items, str):
                input_items = [input_items]

            # Convert input items to the format expected by the API
            items_to_save = []
            for item in input_items:
                if isinstance(item, str):
                    items_to_save.append({"type": "message", "role": "user", "content": item})
                elif isinstance(item, dict):
                    items_to_save.append(item)
                elif hasattr(item, 'as_dict'):
                    items_to_save.append(item.as_dict())
                else:
                    items_to_save.append({"type": "message", "role": "user", "content": str(item)})

            if not items_to_save:
                return

            openai_client = await self._create_openai_client()

            # Check for duplicates by comparing the last N historical items with current N items
            try:
                historical_items = []
                async for item in openai_client.conversations.items.list(conversation_id):
                    historical_items.append(item)
                # API returns items in reverse order (newest first), so reverse to get chronological order
                historical_items.reverse()

                n = len(items_to_save)
                if len(historical_items) >= n:
                    # Get last N historical items (in chronological order)
                    last_n_historical = historical_items[-n:]
                    # Compare as a whole - all N items must match in order
                    all_match = True
                    for i in range(n):
                        hist_dict = last_n_historical[i].model_dump() \
                                if hasattr(last_n_historical[i], 'model_dump') \
                                else dict(last_n_historical[i])
                        if not self._items_are_equal(hist_dict, items_to_save[i]):
                            all_match = False
                            break
                    if all_match:
                        logger.debug(f"All {n} input items already exist in " +
                                     f"conversation {conversation_id}, skipping save")
                        return
            except Exception as e:
                logger.debug(f"Could not check for duplicates: {e}")

            await openai_client.conversations.items.create(
                conversation_id=conversation_id,
                items=items_to_save,
            )
            logger.debug(f"Saved {len(items_to_save)} input items to conversation {conversation_id}")
        except Exception as e:
            logger.warning(f"Failed to save input items to conversation: {e}", exc_info=True)

    async def _save_output_to_conversation(
            self, context: AgentRunContext, response: project_models.Response) -> None:
        """
        Save output items from a non-streaming response to the conversation.
        
        :param context: The agent run context containing conversation information.
        :type context: AgentRunContext
        :param response: The response object containing output items to save.
        :type response: project_models.Response
        :return: None
        :rtype: None
        """
        try:
            conversation_id = context.conversation_id
            output_items = response.get("output", [])
            if not output_items:
                return

            # Convert output items to the format expected by the API
            items_to_save = []
            for item in output_items:
                if isinstance(item, dict):
                    items_to_save.append(item)
                elif hasattr(item, 'as_dict'):
                    items_to_save.append(item.as_dict())
                else:
                    items_to_save.append(dict(item))

            openai_client = await self._create_openai_client()
            await openai_client.conversations.items.create(
                conversation_id=conversation_id,
                items=items_to_save,
            )
            logger.debug(f"Saved {len(items_to_save)} output items to conversation {conversation_id}")
        except Exception as e:
            logger.warning(f"Failed to save output items to conversation: {e}", exc_info=True)

    async def _save_output_events_to_conversation(self, context: AgentRunContext, events: list) -> None:
        """Persist streaming output events for later retrieval.

        :param context: Agent run context containing conversation identifiers.
        :type context: AgentRunContext
        :param events: Response stream events captured during execution.
        :type events: list
        :return: None
        :rtype: None
        """
        try:
            conversation_id = context.conversation_id
            # Extract completed items from ResponseOutputItemDoneEvent
            items_to_save = []
            for event in events:
                if hasattr(event, 'type') and event.type == 'response.output_item.done':
                    item = getattr(event, 'item', None)
                    if item:
                        if isinstance(item, dict):
                            items_to_save.append(item)
                        elif hasattr(item, 'as_dict'):
                            items_to_save.append(item.as_dict())
                        else:
                            items_to_save.append(dict(item))

            if not items_to_save:
                return

            openai_client = await self._create_openai_client()
            await openai_client.conversations.items.create(
                conversation_id=conversation_id,
                items=items_to_save,
            )
            logger.debug(f"Saved {len(items_to_save)} output items to conversation {conversation_id}")
        except Exception as e:
            logger.warning(f"Failed to save output items to conversation: {e}", exc_info=True)

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
            "output": []
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
            "output": []
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
        self._port = port
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
        self._port = port
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

    def create_response_headers(self) -> dict[str, str]:
        headers = {}
        headers.update(build_foundry_agents_metadata_headers())
        return headers


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
