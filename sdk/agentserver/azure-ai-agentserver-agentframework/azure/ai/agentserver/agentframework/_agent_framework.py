# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=logging-fstring-interpolation,no-name-in-module,no-member,do-not-import-asyncio
from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, AsyncGenerator, Awaitable, Optional, Protocol, Union, List

from agent_framework import AgentProtocol, AIFunction
from agent_framework.azure import AzureAIClient  # pylint: disable=no-name-in-module
from opentelemetry import trace

from ..core.tools._exceptions import OAuthConsentRequiredError
from azure.ai.agentserver.core import AgentRunContext, FoundryCBAgent
from azure.ai.agentserver.core.constants import Constants as AdapterConstants
from azure.ai.agentserver.core.logger import APPINSIGHT_CONNSTR_ENV_NAME, get_logger
from azure.ai.agentserver.core.models import (
    CreateResponse,
    Response as OpenAIResponse,
    ResponseStreamEvent,
)
from azure.ai.agentserver.core.models.projects import ResponseErrorEvent, ResponseFailedEvent

from .models.agent_framework_input_converters import AgentFrameworkInputConverter
from .models.agent_framework_output_non_streaming_converter import (
    AgentFrameworkOutputNonStreamingConverter,
)
from .models.agent_framework_output_streaming_converter import AgentFrameworkOutputStreamingConverter
from .models.constants import Constants

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential

logger = get_logger()


class AgentFactory(Protocol):
    """Protocol for agent factory functions.

    An agent factory is a callable that takes a list of tools and returns
    an AgentProtocol, either synchronously or asynchronously.
    """

    def __call__(self, tools: List[AIFunction]) -> Union[AgentProtocol, Awaitable[AgentProtocol]]:
        """Create an AgentProtocol using the provided tools.

        :param tools: The list of AIFunction tools available to the agent.
        :type tools: List[AIFunction]
        :return: An Agent Framework agent, or an awaitable that resolves to one.
        :rtype: Union[AgentProtocol, Awaitable[AgentProtocol]]
        """
        ...


class AgentFrameworkCBAgent(FoundryCBAgent):
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
                 **kwargs: Any):
        """Initialize the AgentFrameworkCBAgent with an AgentProtocol or a factory function.

        :param agent: The Agent Framework agent to adapt, or a callable that takes ToolClient
            and returns AgentProtocol (sync or async).
        :type agent: Union[AgentProtocol, AgentFactory]
        :param credentials: Azure credentials for authentication.
        :type credentials: Optional[AsyncTokenCredential]
        """
        super().__init__(credentials=credentials, **kwargs)  # pylint: disable=unexpected-keyword-arg
        self._agent: AgentProtocol = agent

    @property
    def agent(self) -> "Optional[AgentProtocol]":
        """Get the resolved agent. This property provides backward compatibility.

        :return: The resolved AgentProtocol if available, None otherwise.
        :rtype: Optional[AgentProtocol]
        """
        return self._agent

    def _resolve_stream_timeout(self, request_body: CreateResponse) -> float:
        """Resolve idle timeout for streaming updates.

        Order of precedence:
        1) request_body.stream_timeout_s (if provided)
        2) env var Constants.AGENTS_ADAPTER_STREAM_TIMEOUT_S
        3) Constants.DEFAULT_STREAM_TIMEOUT_S

        :param request_body: The CreateResponse request body.
        :type request_body: CreateResponse

        :return: The resolved stream timeout in seconds.
        :rtype: float
        """
        override = request_body.get("stream_timeout_s", None)
        if override is not None:
            return float(override)
        env_val = os.getenv(Constants.AGENTS_ADAPTER_STREAM_TIMEOUT_S)
        return float(env_val) if env_val is not None else float(Constants.DEFAULT_STREAM_TIMEOUT_S)

    def init_tracing(self):
        try:
            exporter = os.environ.get(AdapterConstants.OTEL_EXPORTER_ENDPOINT)
            app_insights_conn_str = os.environ.get(APPINSIGHT_CONNSTR_ENV_NAME)
            project_endpoint = os.environ.get(AdapterConstants.AZURE_AI_PROJECT_ENDPOINT)

            if exporter or app_insights_conn_str:
                from agent_framework.observability import setup_observability

                setup_observability(
                    enable_sensitive_data=True,
                    otlp_endpoint=exporter,
                    applicationinsights_connection_string=app_insights_conn_str,
                )
            elif project_endpoint:
                self.setup_tracing_with_azure_ai_client(project_endpoint)
        except Exception as e:
            logger.warning(f"Failed to initialize tracing: {e}", exc_info=True)
        self.tracer = trace.get_tracer(__name__)

    def setup_tracing_with_azure_ai_client(self, project_endpoint: str):
        async def setup_async():
            async with AzureAIClient(
                project_endpoint=project_endpoint, async_credential=self.credentials
                ) as agent_client:
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
        try:
            logger.info(f"Starting agent_run with stream={context.stream}")
            request_input = context.request.get("input")

            input_converter = AgentFrameworkInputConverter()
            message = input_converter.transform_input(request_input)
            logger.debug(f"Transformed input message type: {type(message)}")

            # Use split converters
            if context.stream:
                logger.info("Running agent in streaming mode")
                streaming_converter = AgentFrameworkOutputStreamingConverter(context)

                async def stream_updates():
                    try:
                        update_count = 0
                        try:
                            updates = self.agent.run_stream(message)
                            async for event in streaming_converter.convert(updates):
                                update_count += 1
                                yield event

                            logger.info("Streaming completed with %d updates", update_count)
                        except OAuthConsentRequiredError as e:
                            logger.info("OAuth consent required during streaming updates")
                            if update_count == 0:
                                async for event in self.respond_with_oauth_consent_astream(context, e):
                                    yield event
                            else:
                                # If we've already emitted events, we cannot safely restart a new
                                # OAuth-consent stream (it would reset sequence numbers).
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

                            # Emit well-formed error events instead of terminating the stream.
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
                        # No request-scoped resources to clean up here today.
                        # Keep this block as a hook for future request-scoped cleanup.
                        pass

                return stream_updates()

            # Non-streaming path
            logger.info("Running agent in non-streaming mode")
            non_streaming_converter = AgentFrameworkOutputNonStreamingConverter(context)
            result = await self.agent.run(message)
            logger.debug(f"Agent run completed, result type: {type(result)}")
            transformed_result = non_streaming_converter.transform_output_for_response(result)
            logger.info("Agent run and transformation completed successfully")
            return transformed_result
        except OAuthConsentRequiredError as e:
            logger.info("OAuth consent required during agent run")
            if context.stream:
                # Yield OAuth consent response events
                # Capture e in the closure by passing it as a default argument
                async def oauth_consent_stream(error=e):
                    async for event in self.respond_with_oauth_consent_astream(context, error):
                        yield event
                return oauth_consent_stream()
            return await self.respond_with_oauth_consent(context, e)
        finally:
            pass
