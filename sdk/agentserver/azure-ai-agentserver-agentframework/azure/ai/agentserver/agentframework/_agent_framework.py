# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=logging-fstring-interpolation,no-name-in-module,no-member,do-not-import-asyncio
from __future__ import annotations

import asyncio
import os
from typing import TYPE_CHECKING, Any, AsyncGenerator, Optional, Union

from agent_framework import AgentSession, BaseHistoryProvider, ResponseStream, SupportsAgentRun
from opentelemetry import trace

from azure.ai.agentserver.core import AgentRunContext, FoundryCBAgent
from azure.ai.agentserver.core.constants import Constants as AdapterConstants
from azure.ai.agentserver.core.logger import APPINSIGHT_CONNSTR_ENV_NAME, get_logger, get_project_endpoint
from azure.ai.agentserver.core.models import (
    Response as OpenAIResponse,
    ResponseStreamEvent,
)
from azure.ai.agentserver.core.models.projects import ResponseErrorEvent, ResponseFailedEvent
from azure.ai.agentserver.core.tools import OAuthConsentRequiredError  # pylint: disable=import-error

from .models.agent_framework_output_streaming_converter import AgentFrameworkOutputStreamingConverter
from .models.human_in_the_loop_helper import HumanInTheLoopHelper
from .persistence import AgentSessionRepository
from .persistence._foundry_conversation_history_provider import FoundryConversationHistoryProvider
from .persistence._foundry_conversation_session_repository import FoundryConversationSessionRepository

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential

logger = get_logger()


class AgentFrameworkAgent(FoundryCBAgent):
    """
    Adapter class for integrating Agent Framework agents with the FoundryCB agent interface.

    This class wraps an Agent Framework `SupportsAgentRun` instance and provides a unified interface
    for running agents in both streaming and non-streaming modes. It handles input and output
    conversion between the Agent Framework and the expected formats for FoundryCB agents.

    Parameters:
        agent (SupportsAgentRun): An instance of an Agent Framework agent to be adapted.

    Usage:
        - Instantiate with an Agent Framework agent.
        - Call `agent_run` with a `CreateResponse` request body to execute the agent.
        - Supports both streaming and non-streaming responses based on the `stream` flag.
    """

    def __init__(
        self,
        credentials: "Optional[AsyncTokenCredential]" = None,
        session_repository: Optional[AgentSessionRepository] = None,
        project_endpoint: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Initialize the AgentFrameworkAgent with a SupportsAgentRun-compatible agent adapter.

        :param credentials: Azure credentials for authentication.
        :type credentials: Optional[AsyncTokenCredential]
        :param session_repository: An optional AgentSessionRepository instance for managing session messages.
        :type session_repository: Optional[AgentSessionRepository]
        :param project_endpoint: The endpoint of the Azure AI Project.
        :type project_endpoint: Optional[str]
        """
        super().__init__(credentials=credentials, **kwargs)  # pylint: disable=unexpected-keyword-arg
        self.project_endpoint = get_project_endpoint(logger=logger) or project_endpoint
        self._session_repository = session_repository
        self._hitl_helper = HumanInTheLoopHelper()

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

            if exporters and self._configure_otel_providers(exporters):
                logger.info("Observability setup completed with provided exporters.")
            elif app_insights_conn_str and self._setup_tracing_with_connection_string(app_insights_conn_str):
                logger.info("Observability setup completed with APPINSIGHTS connection string.")
            elif project_endpoint:
                self._setup_tracing_with_project_client(project_endpoint)
        except Exception as e: # pylint: disable=broad-exception-caught
            logger.warning(f"Failed to initialize tracing: {e}", exc_info=True)
        self.tracer = trace.get_tracer(__name__)

    def _create_application_insights_exporter(self, connection_string):
        try:
            from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

            return AzureMonitorTraceExporter.from_connection_string(connection_string)
        except Exception as e: # pylint: disable=broad-exception-caught
            logger.error(f"Failed to create Application Insights exporter: {e}", exc_info=True)
            return None

    def _setup_tracing_with_connection_string(self, connection_string: str) -> bool:
        try:
            from azure.monitor.opentelemetry import configure_azure_monitor

            configure_azure_monitor(connection_string=connection_string)
            return True
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.warning(f"Failed to set up Azure Monitor from APPINSIGHTS connection string: {e}", exc_info=True)
            return False

    def _create_otlp_exporter(self, endpoint, protocol=None):
        try:
            if protocol and protocol.lower() in ("http", "http/protobuf", "http/json"):
                from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

                return OTLPSpanExporter(endpoint=endpoint)

            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

            return OTLPSpanExporter(endpoint=endpoint)
        except Exception as e: # pylint: disable=broad-exception-caught
            logger.error(f"Failed to create OTLP exporter: {e}", exc_info=True)
            return None

    def _configure_otel_providers(self, exporters) -> bool:
        try:
            from agent_framework.observability import configure_otel_providers
        except ImportError as e:
            logger.warning(f"Failed to import configure_otel_providers: {e}")
            return False
        configure_otel_providers(
            enable_sensitive_data=True,
            exporters=exporters,
        )
        return True

    def _setup_tracing_with_project_client(self, project_endpoint: str):
        if not self.credentials:
            logger.warning(
                "Skipping Azure Monitor setup through the project client because credentials are not configured."
            )
            return

        async def setup_async():
            from azure.ai.projects.aio import AIProjectClient
            from azure.monitor.opentelemetry import configure_azure_monitor

            async with AIProjectClient(project_endpoint, self.credentials) as project_client:
                connection_string = await project_client.telemetry.get_application_insights_connection_string()
            configure_azure_monitor(connection_string=connection_string)

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

    async def _load_agent_session(
        self,
        context: AgentRunContext,
        agent: SupportsAgentRun,
    ) -> Optional[AgentSession]:
        """Load the agent session for a given conversation ID.

        :param context: The agent run context.
        :type context: AgentRunContext
        :param agent: The agent instance.
        :type agent: SupportsAgentRun

        :return: The loaded AgentSession if available, None otherwise.
        :rtype: Optional[AgentSession]
        """
        if self._session_repository and context.conversation_id:
            self._ensure_foundry_history_provider(agent)
            conversation_id = context.conversation_id
            agent_session = await self._session_repository.get(conversation_id)
            if agent_session:
                logger.info(f"Loaded agent session for conversation: {conversation_id}")
                return agent_session
            return agent.create_session()
        return None

    async def _save_agent_session(self, context: AgentRunContext, agent_session: AgentSession) -> None:
        """Save the agent session for a given conversation ID.

        :param context: The agent run context.
        :type context: AgentRunContext
        :param agent_session: The agent session to save.
        :type agent_session: AgentSession

        :return: None
        :rtype: None
        """
        if agent_session and self._session_repository and (conversation_id := context.conversation_id):
            await self._session_repository.set(conversation_id, agent_session)
            logger.info(f"Saved agent session for conversation: {conversation_id}")

    def _run_streaming_updates(
        self,
        context: AgentRunContext,
        stream: ResponseStream[Any, Any],
        agent_session: Optional[AgentSession] = None,
    ) -> AsyncGenerator[ResponseStreamEvent, Any]:
        """
        Execute a streaming run with shared OAuth/error handling.

        :param context: The agent run context.
        :type context: AgentRunContext
        :param stream: ResponseStream from an agent streaming run.
        :type stream: ResponseStream[Any, Any]
        :param agent_session: The agent session to use during streaming updates.
        :type agent_session: Optional[AgentSession]

        :return: An async generator yielding streaming events.
        :rtype: AsyncGenerator[ResponseStreamEvent, Any]
        """
        logger.info("Running agent in streaming mode")
        streaming_converter = AgentFrameworkOutputStreamingConverter(
            context,
            hitl_helper=self._hitl_helper,
        )

        async def stream_updates():
            try:
                update_count = 0
                try:
                    async for event in streaming_converter.convert(stream):
                        update_count += 1
                        yield event

                    # Trigger the result hooks (e.g. _run_after_providers) which
                    # populate the session with messages. Without this call the
                    # session remains empty because result hooks only execute
                    # inside get_final_response().
                    await stream.get_final_response()
                    await self._save_agent_session(context, agent_session)
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
                            response=streaming_converter._build_response(  # pylint: disable=protected-access
                                status="failed"
                            ),
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
                        response=streaming_converter._build_response(  # pylint: disable=protected-access
                            status="failed"
                        ),
                    )
            finally:
                # No request-scoped resources to clean up today, but keep hook for future use.
                pass

        return stream_updates()

    def _create_foundry_conversation_session_repository(
        self,
        project_endpoint: str,
        credential: AsyncTokenCredential,
    ) -> FoundryConversationSessionRepository:
        """Helper method to create a FoundryConversationSessionRepository instance.

        :param project_endpoint: The endpoint of the Azure AI Project.
        :type project_endpoint: str
        :param credential: The credential for authenticating with the Azure AI Project.
        :type credential: AsyncTokenCredential

        :return: An instance of FoundryConversationSessionRepository.
        :rtype: FoundryConversationSessionRepository
        """
        return FoundryConversationSessionRepository(
            project_endpoint=project_endpoint,
            credential=credential,
        )

    def _ensure_foundry_history_provider(self, agent: SupportsAgentRun) -> None:
        if not isinstance(self._session_repository, FoundryConversationSessionRepository):
            return

        context_providers = getattr(agent, "context_providers", None)
        if not isinstance(context_providers, list):
            logger.warning(
                "Agent does not expose mutable context_providers; FoundryConversationHistoryProvider was not attached."
            )
            return

        if any(isinstance(provider, FoundryConversationHistoryProvider) for provider in context_providers):
            return

        context_providers.append(self._session_repository.history_provider)

    def _get_history_provider(self, agent: SupportsAgentRun) -> Optional[BaseHistoryProvider]:
        """
        Return the first BaseHistoryProvider attached to the agent, if any.

        :param agent: The agent instance to check for history providers.
        :type agent: SupportsAgentRun
        :return: The first BaseHistoryProvider found, or None if none are attached.
        :rtype: Optional[BaseHistoryProvider]
        """
        for provider in getattr(agent, "context_providers", None) or []:
            if isinstance(provider, BaseHistoryProvider):
                return provider
        return None

    def _try_setup_default_conversation_repository(self) -> None:
        """Set up the default FoundryConversationSessionRepository if no session repository was provided.

        :return: None
        :rtype: None
        """
        if not self._session_repository and self._project_endpoint and self.credentials:
            logger.warning("No session repository provided. FoundryConversationSessionRepository will be used.")
            self._session_repository = self._create_foundry_conversation_session_repository(
                self._project_endpoint, self.credentials
            )