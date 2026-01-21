# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=logging-fstring-interpolation,no-name-in-module,no-member,do-not-import-asyncio
from __future__ import annotations

import os
from typing import Any, AsyncGenerator, Optional, TYPE_CHECKING, Union, Callable

from agent_framework import AgentProtocol, AgentThread, WorkflowAgent
from agent_framework.azure import AzureAIClient  # pylint: disable=no-name-in-module
from opentelemetry import trace

from azure.ai.agentserver.core import AgentRunContext, FoundryCBAgent
from azure.ai.agentserver.core.constants import Constants as AdapterConstants
from azure.ai.agentserver.core.logger import APPINSIGHT_CONNSTR_ENV_NAME, get_logger
from azure.ai.agentserver.core.models import (
    Response as OpenAIResponse,
    ResponseStreamEvent,
)
from azure.ai.agentserver.core.models.projects import ResponseErrorEvent, ResponseFailedEvent
from azure.ai.agentserver.core.tools import OAuthConsentRequiredError

from .models.agent_framework_output_streaming_converter import AgentFrameworkOutputStreamingConverter
from .models.human_in_the_loop_helper import HumanInTheLoopHelper
from .persistence import AgentThreadRepository

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential

logger = get_logger()


class AgentFrameworkAgent(FoundryCBAgent):
    """
    Adapter class for integrating Agent Framework agents with the FoundryCB agent interface.

    This class wraps an Agent Framework `AgentProtocol` instance and provides a unified interface
    for running agents in both streaming and non-streaming modes. It handles input and output
    conversion between the Agent Framework and the expected formats for FoundryCB agents.

    Parameters:
        agent (AgentProtocol): An instance of an Agent Framework agent to be adapted.

    Usage:
        - Instantiate with an Agent Framework agent.
        - Call `agent_run` with a `CreateResponse` request body to execute the agent.
        - Supports both streaming and non-streaming responses based on the `stream` flag.
    """

    def __init__(self, agent: AgentProtocol,
                 credentials: "Optional[AsyncTokenCredential]" = None,
                 *,
                 thread_repository: Optional[AgentThreadRepository] = None,
                 **kwargs: Any,
                ):
        """Initialize the AgentFrameworkAgent with an AgentProtocol.

        :param agent: The Agent Framework agent to adapt.
        :type agent: AgentProtocol
        :param credentials: Azure credentials for authentication.
        :type credentials: Optional[AsyncTokenCredential]
        :param thread_repository: An optional AgentThreadRepository instance for managing thread messages.
        :type thread_repository: Optional[AgentThreadRepository]
        """
        super().__init__(credentials=credentials, **kwargs)  # pylint: disable=unexpected-keyword-arg
        self._agent: AgentProtocol = agent
        self._thread_repository = thread_repository
        self._hitl_helper = HumanInTheLoopHelper()

    @property
    def agent(self) -> "AgentProtocol":
        """Get the resolved agent. This property provides backward compatibility.

        :return: The resolved AgentProtocol if available, None otherwise.
        :rtype: AgentProtocol
        """
        return self._agent

    def init_tracing(self):
        try:
            otel_exporter_endpoint = os.environ.get(AdapterConstants.OTEL_EXPORTER_ENDPOINT)
            otel_exporter_protocol = os.environ.get(AdapterConstants.OTEL_EXPORTER_OTLP_PROTOCOL)
            app_insights_conn_str = os.environ.get(APPINSIGHT_CONNSTR_ENV_NAME)
            project_endpoint = os.environ.get(AdapterConstants.AZURE_AI_PROJECT_ENDPOINT)

            exporters = []
            if otel_exporter_endpoint:
                otel_exporter = self._create_otlp_exporter(otel_exporter_endpoint, protocol=otel_exporter_protocol)
                if otel_exporter:
                    exporters.append(otel_exporter)
            if app_insights_conn_str:
                appinsight_exporter = self._create_application_insights_exporter(app_insights_conn_str)
                if appinsight_exporter:
                    exporters.append(appinsight_exporter)

            if exporters and self._setup_observability(exporters):
                logger.info("Observability setup completed with provided exporters.")
            elif project_endpoint:
                self._setup_tracing_with_azure_ai_client(project_endpoint)
        except Exception as e:
            logger.warning(f"Failed to initialize tracing: {e}", exc_info=True)
        self.tracer = trace.get_tracer(__name__)

    def _create_application_insights_exporter(self, connection_string):
        try:
            from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

            return AzureMonitorTraceExporter.from_connection_string(connection_string)
        except Exception as e:
            logger.error(f"Failed to create Application Insights exporter: {e}", exc_info=True)
            return None

    def _create_otlp_exporter(self, endpoint, protocol=None):
        try:
            if protocol and protocol.lower() in ("http", "http/protobuf", "http/json"):
                from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

                return OTLPSpanExporter(endpoint=endpoint)
            else:
                from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

                return OTLPSpanExporter(endpoint=endpoint)
        except Exception as e:
            logger.error(f"Failed to create OTLP exporter: {e}", exc_info=True)
            return None

    def _setup_observability(self, exporters) -> bool:
        setup_function = self._try_import_configure_otel_providers()
        if not setup_function: # fallback to early version with setup_observability
            setup_function = self._try_import_setup_observability()
        if setup_function:
            setup_function(
                enable_sensitive_data=True,
                exporters=exporters,
            )
            return True
        return False

    def _try_import_setup_observability(self):
        try:
            from agent_framework.observability import setup_observability
            return setup_observability
        except ImportError as e:
            logger.warning(f"Failed to import setup_observability: {e}")
            return None

    def _try_import_configure_otel_providers(self):
        try:
            from agent_framework.observability import configure_otel_providers
            return configure_otel_providers
        except ImportError as e:
            logger.warning(f"Failed to import configure_otel_providers: {e}")
            return None

    def _setup_tracing_with_azure_ai_client(self, project_endpoint: str):
        async def setup_async():
            async with AzureAIClient(
                project_endpoint=project_endpoint,
                async_credential=self.credentials,
                credential=self.credentials, # Af breaking change, keep both for compatibility
                ) as agent_client:
                try:
                    await agent_client.configure_azure_monitor()
                except AttributeError:
                    await agent_client.setup_azure_ai_observability()

        import asyncio

        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is already running, schedule as a task
            asyncio.create_task(setup_async())
        else:
            # Run in new event loop
            loop.run_until_complete(setup_async())

    async def agent_run(  # pylint: disable=too-many-statements
        self, context: AgentRunContext
    ) -> Union[
        OpenAIResponse,
        AsyncGenerator[ResponseStreamEvent, Any],
    ]:
        raise NotImplementedError("This method is implemented in the base class.")

    async def _load_agent_thread(self, context: AgentRunContext, agent: Union[AgentProtocol, WorkflowAgent]) -> Optional[AgentThread]:
        """Load the agent thread for a given conversation ID.

        :param context: The agent run context.
        :type context: AgentRunContext
        :param agent: The agent instance.
        :type agent: AgentProtocol | WorkflowAgent

        :return: The loaded AgentThread if available, None otherwise.
        :rtype: Optional[AgentThread]
        """
        if self._thread_repository:
            agent_thread = await self._thread_repository.get(context.conversation_id)
            if agent_thread:
                logger.info(f"Loaded agent thread for conversation: {context.conversation_id}")
                return agent_thread
            return agent.get_new_thread()
        return None

    async def _save_agent_thread(self, context: AgentRunContext, agent_thread: AgentThread) -> None:
        """Save the agent thread for a given conversation ID.

        :param context: The agent run context.
        :type context: AgentRunContext
        :param agent_thread: The agent thread to save.
        :type agent_thread: AgentThread
        """
        if agent_thread and self._thread_repository:
            await self._thread_repository.set(context.conversation_id, agent_thread)
            logger.info(f"Saved agent thread for conversation: {context.conversation_id}")

    def _run_streaming_updates(
        self,
        *,
        context: AgentRunContext,
        run_stream: Callable[[], AsyncGenerator[Any, None]],
        agent_thread: Optional[AgentThread] = None,
    ) -> AsyncGenerator[ResponseStreamEvent, Any]:
        """Execute a streaming run with shared OAuth/error handling."""
        logger.info("Running agent in streaming mode")
        streaming_converter = AgentFrameworkOutputStreamingConverter(context, hitl_helper=self._hitl_helper)

        async def stream_updates():
            try:
                update_count = 0
                try:
                    updates = run_stream()
                    async for event in streaming_converter.convert(updates):
                        update_count += 1
                        yield event

                    await self._save_agent_thread(context, agent_thread)
                    logger.info("Streaming completed with %d updates", update_count)
                except OAuthConsentRequiredError as e:
                    logger.info("OAuth consent required during streaming updates")
                    if update_count == 0:
                        async for event in self.respond_with_oauth_consent_astream(context, e):
                            yield event
                    else:
                        yield ResponseErrorEvent(
                            sequence_number=streaming_converter.next_sequence(),
                            code="server_error",
                            message=f"OAuth consent required: {e.consent_url}",
                            param="agent_run",
                        )
                        yield ResponseFailedEvent(
                            sequence_number=streaming_converter.next_sequence(),
                            response=streaming_converter._build_response(status="failed"),  # pylint: disable=protected-access
                        )
                except Exception as e:  # pylint: disable=broad-exception-caught
                    logger.error("Unhandled exception during streaming updates: %s", e, exc_info=True)
                    yield ResponseErrorEvent(
                        sequence_number=streaming_converter.next_sequence(),
                        code="server_error",
                        message=str(e),
                        param="agent_run",
                    )
                    yield ResponseFailedEvent(
                        sequence_number=streaming_converter.next_sequence(),
                        response=streaming_converter._build_response(status="failed"),  # pylint: disable=protected-access
                    )
            finally:
                # No request-scoped resources to clean up today, but keep hook for future use.
                pass

        return stream_updates()
