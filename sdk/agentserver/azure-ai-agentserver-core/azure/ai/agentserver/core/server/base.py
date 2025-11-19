# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=broad-exception-caught,unused-argument,logging-fstring-interpolation,too-many-statements,too-many-return-statements
# mypy: ignore-errors
import inspect
import json
import os
import time
import traceback
from abc import abstractmethod
from typing import Any, AsyncGenerator, Generator, Optional, Union

import uvicorn
from azure.identity.aio import DefaultAzureCredential as AsyncDefaultTokenCredential
from opentelemetry import context as otel_context, trace
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse
from starlette.routing import Route
from starlette.types import ASGIApp
from  ..models import projects as project_models
from ..constants import Constants
from ..logger import APPINSIGHT_CONNSTR_ENV_NAME, get_logger, request_context
from ..models import (
    Response as OpenAIResponse,
    ResponseStreamEvent,
)
from .common.agent_run_context import AgentRunContext

from ..client.tools.aio._client import AzureAIToolClient
from ..client.tools._utils._model_base import ToolDefinition, UserInfo

logger = get_logger()
DEBUG_ERRORS = os.environ.get(Constants.AGENT_DEBUG_ERRORS, "false").lower() == "true"

class AgentRunContextMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, agent: Optional['FoundryCBAgent'] = None):
        super().__init__(app)
        self.agent = agent

    async def dispatch(self, request: Request, call_next):
        user_info: Optional[UserInfo] = None
        if request.url.path in ("/runs", "/responses"):
            try:
                user_info = self.set_user_info_to_context_var(request)
                self.set_request_id_to_context_var(request)
                payload = await request.json()
            except Exception as e:
                logger.error(f"Invalid JSON payload: {e}")
                return JSONResponse({"error": f"Invalid JSON payload: {e}"}, status_code=400)
            try:
                agent_tools = self.agent.tools if self.agent else []
                request.state.agent_run_context = AgentRunContext(payload, user_info=user_info, agent_tools=agent_tools)
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

    def set_user_info_to_context_var(self, request) -> Optional[UserInfo]:
        user_info: Optional[UserInfo] = None
        try:
            object_id_header = request.headers.get("x-aml-oid", None)
            tenant_id_header = request.headers.get("x-aml-tid", None)
            if not object_id_header and not tenant_id_header:
                return None
            user_info = UserInfo(
                objectId=object_id_header,
                tenantId=tenant_id_header
            )

        except Exception as e:
            logger.error(f"Failed to parse X-User-Info header: {e}", exc_info=True)
        if user_info:
            ctx = request_context.get() or {}
            for key, value in user_info.to_dict().items():
                ctx[f"azure.ai.agentserver.user.{key}"] = str(value)
            request_context.set(ctx)
        return user_info


class FoundryCBAgent:
    _cached_tools_endpoint: Optional[str] = None
    _cached_agent_name: Optional[str] = None

    def __init__(self, credentials: Optional["AsyncTokenCredential"] = None, **kwargs: Any) -> None:
        self.credentials = credentials or AsyncDefaultTokenCredential()
        self.tools = kwargs.get("tools", [])

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

                    resp = await self.agent_run(context)

                    if inspect.isgenerator(resp):
                        # Prefetch first event to allow 500 status if generation fails immediately
                        try:
                            first_event = next(resp)
                        except Exception as e:  # noqa: BLE001
                            err_msg = _format_error(e)
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
                                err_msg = _format_error(e)
                                logger.error("Error in non-async generator: %s\n%s", e, traceback.format_exc())
                                payload = {"error": err_msg}
                                yield f"event: error\ndata: {json.dumps(payload)}\n\n"
                                error_sent = True
                            finally:
                                logger.info("End of processing CreateResponse request.")
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
                            err_msg = _format_error(e)
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
                                err_msg = _format_error(e)
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

    @staticmethod
    def _configure_endpoint() -> tuple[str, Optional[str]]:
        """Configure and return the tools endpoint and agent name from environment variables.

        :return: A tuple of (tools_endpoint, agent_name).
        :rtype: tuple[str, Optional[str]]
        """
        if not FoundryCBAgent._cached_tools_endpoint:
            project_endpoint_format: str = "https://{account_name}.services.ai.azure.com/api/projects/{project_name}"
            workspace_endpoint = os.getenv(Constants.AZURE_AI_WORKSPACE_ENDPOINT)
            tools_endpoint = os.getenv(Constants.AZURE_AI_TOOLS_ENDPOINT)
            project_endpoint = os.getenv(Constants.AZURE_AI_PROJECT_ENDPOINT)

            if not tools_endpoint:
                # project endpoint corrupted could have been an overridden enviornment variable
                # try to reconstruct tools endpoint from workspace endpoint
                # Robustly reconstruct project_endpoint from workspace_endpoint if needed.

                if workspace_endpoint:
                    # Expected format:
                    # "https://<region>.api.azureml.ms/subscriptions/<subscription>/resourceGroups/<region>/
                    # providers/Microsoft.MachineLearningServices/workspaces/<account_name>@<project_name>@AML"
                    from urllib.parse import urlparse
                    parsed_url = urlparse(workspace_endpoint)
                    path_parts = [p for p in parsed_url.path.split('/') if p]
                    # Find the 'workspaces' part and extract account_name@project_name@AML
                    try:
                        workspaces_idx = path_parts.index("workspaces")
                        if workspaces_idx + 1 >= len(path_parts):
                            raise ValueError(
                                f"Workspace endpoint path does not contain workspace info "
                                f"after 'workspaces': {workspace_endpoint}"
                            )
                        workspace_info = path_parts[workspaces_idx + 1]
                        workspace_parts = workspace_info.split('@')
                        if len(workspace_parts) < 2:
                            raise ValueError(
                                f"Workspace info '{workspace_info}' does not contain both account_name "
                                f"and project_name separated by '@'."
                            )
                        account_name = workspace_parts[0]
                        project_name = workspace_parts[1]
                        # Documented expected format for PROJECT_ENDPOINT_FORMAT:
                        # "https://<account_name>.api.azureml.ms/api/projects/{project_name}"
                        project_endpoint = project_endpoint_format.format(
                            account_name=account_name, project_name=project_name
                        )
                    except (ValueError, IndexError) as e:
                        raise ValueError(
                            f"Failed to reconstruct project endpoint from workspace endpoint "
                            f"'{workspace_endpoint}': {e}"
                        ) from e
                    # should never reach here
                    logger.info("Reconstructed tools endpoint from project endpoint %s", project_endpoint)
                    tools_endpoint = project_endpoint

                tools_endpoint = project_endpoint

            if not tools_endpoint:
                raise ValueError(
                    "Project endpoint needed for Azure AI tools endpoint is not found. "
                )
            FoundryCBAgent._cached_tools_endpoint = tools_endpoint

            agent_name = os.getenv(Constants.AGENT_NAME)
            if agent_name is None:
                if os.getenv("CONTAINER_APP_NAME"):
                    raise ValueError(
                        "Agent name needed for Azure AI hosted agents is not found. "
                    )
                agent_name = "$default"
            FoundryCBAgent._cached_agent_name = agent_name

        return FoundryCBAgent._cached_tools_endpoint, FoundryCBAgent._cached_agent_name

    def get_tool_client(
            self, tools: Optional[list[ToolDefinition]], user_info: Optional[UserInfo]
        ) -> AzureAIToolClient:
        logger.debug("Creating AzureAIToolClient with tools: %s", tools)
        if not self.credentials:
            raise ValueError("Credentials are required to create Tool Client.")

        tools_endpoint, agent_name = self._configure_endpoint()

        return AzureAIToolClient(
            endpoint=tools_endpoint,
            credential=self.credentials,
            tools=tools,
            user=user_info,
            agent_name=agent_name,
        )


def _event_to_sse_chunk(event: ResponseStreamEvent) -> str:
    event_data = json.dumps(event.as_dict())
    if event.type:
        return f"event: {event.type}\ndata: {event_data}\n\n"
    return f"data: {event_data}\n\n"


def _format_error(exc: Exception) -> str:
    message = str(exc)
    if message:
        return message
    if DEBUG_ERRORS:
        return repr(exc)
    return f"{type(exc)}: Internal error"


def _to_response(result: Union[Response, dict]) -> Response:
    return result if isinstance(result, Response) else JSONResponse(result)
