# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=logging-fstring-interpolation,no-name-in-module,no-member,do-not-import-asyncio
from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, AsyncGenerator, Awaitable, Optional, Protocol, Union, List
import inspect

from agent_framework import AgentProtocol, AIFunction, CheckpointStorage, InMemoryCheckpointStorage, WorkflowCheckpoint
from agent_framework.azure import AzureAIClient  # pylint: disable=no-name-in-module
from agent_framework._workflows import get_checkpoint_summary
from opentelemetry import trace

from azure.ai.agentserver.core.client.tools import OAuthConsentRequiredError
from azure.ai.agentserver.core import AgentRunContext, FoundryCBAgent
from azure.ai.agentserver.core.constants import Constants as AdapterConstants
from azure.ai.agentserver.core.logger import APPINSIGHT_CONNSTR_ENV_NAME, get_logger
from azure.ai.agentserver.core.models import (
    CreateResponse,
    Response as OpenAIResponse,
    ResponseStreamEvent,
)

from .models.agent_framework_input_converters import AgentFrameworkInputConverter
from .models.agent_framework_output_non_streaming_converter import (
    AgentFrameworkOutputNonStreamingConverter,
)
from .models.agent_framework_output_streaming_converter import AgentFrameworkOutputStreamingConverter
from .models.human_in_the_loop_helper import HumanInTheLoopHelper
from .models.constants import Constants
from .persistence import AgentThreadRepository, CheckpointRepository
from .tool_client import ToolClient

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential

logger = get_logger()


class AgentFactory(Protocol):
    """Protocol for agent factory functions.

    An agent factory is a callable that takes a ToolClient and returns
    an AgentProtocol, either synchronously or asynchronously.
    """

    def __call__(self, tools: List[AIFunction]) -> Union[AgentProtocol, Awaitable[AgentProtocol]]:
        """Create an AgentProtocol using the provided ToolClient.

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

    def __init__(self, agent: Union[AgentProtocol, AgentFactory],
                 credentials: "Optional[AsyncTokenCredential]" = None,
                 *,
                 thread_repository: AgentThreadRepository = None,
                 checkpoint_repository: CheckpointRepository = None,
                 **kwargs: Any,
                ):
        """Initialize the AgentFrameworkCBAgent with an AgentProtocol or a factory function.

        :param agent: The Agent Framework agent to adapt, or a callable that takes ToolClient
            and returns AgentProtocol (sync or async).
        :type agent: Union[AgentProtocol, AgentFactory]
        :param credentials: Azure credentials for authentication.
        :type credentials: Optional[AsyncTokenCredential]
        :param thread_repository: An optional AgentThreadRepository instance for managing thread messages.
        :type thread_repository: Optional[AgentThreadRepository]
        """
        super().__init__(credentials=credentials, **kwargs)  # pylint: disable=unexpected-keyword-arg
        self._agent_or_factory: Union[AgentProtocol, AgentFactory] = agent
        self._resolved_agent: "Optional[AgentProtocol]" = None
        self._hitl_helper = HumanInTheLoopHelper()
        self._checkpoint_repository = checkpoint_repository
        self._thread_repository = thread_repository

        # If agent is already instantiated, use it directly
        if isinstance(agent, AgentProtocol):
            self._resolved_agent = agent
            logger.info(f"Initialized AgentFrameworkCBAgent with agent: {type(agent).__name__}")
        else:
            logger.info("Initialized AgentFrameworkCBAgent with agent factory")

    @property
    def agent(self) -> "Optional[AgentProtocol]":
        """Get the resolved agent. This property provides backward compatibility.

        :return: The resolved AgentProtocol if available, None otherwise.
        :rtype: Optional[AgentProtocol]
        """
        return self._resolved_agent

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

    async def _resolve_agent(self, context: AgentRunContext):
        """Resolve the agent if it's a factory function (for single-use/first-time resolution).
        Creates a ToolClient and calls the factory function with it.
        This is used for the initial resolution.

        :param context: The agent run context containing tools and user information.
        :type context: AgentRunContext
        """
        if callable(self._agent_or_factory):
            logger.debug("Resolving agent from factory function")

            # Create ToolClient with credentials
            tool_client = self.get_tool_client(tools=context.get_tools(), user_info=context.get_user_info()) # pylint: disable=no-member
            tool_client_wrapper = ToolClient(tool_client)
            tools = await tool_client_wrapper.list_tools()

            result = self._agent_or_factory(tools)
            if inspect.iscoroutine(result):
                self._resolved_agent = await result
            else:
                self._resolved_agent = result

            logger.debug("Agent resolved successfully")
        else:
            # Should not reach here, but just in case
            self._resolved_agent = self._agent_or_factory

    async def _resolve_agent_for_request(self, context: AgentRunContext):

        logger.debug("Resolving fresh agent from factory function for request")

        # Create ToolClient with credentials
        tool_client = self.get_tool_client(tools=context.get_tools(), user_info=context.get_user_info()) # pylint: disable=no-member
        tool_client_wrapper = ToolClient(tool_client)
        tools = await tool_client_wrapper.list_tools()

        result = self._agent_or_factory(tools)
        if inspect.iscoroutine(result):
            agent = await result
        else:
            agent = result

        logger.debug("Fresh agent resolved successfully for request")
        return agent, tool_client_wrapper

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
        # Resolve agent - always resolve if it's a factory function to get fresh agent each time
        # For factories, get a new agent instance per request to avoid concurrency issues
        tool_client = None
        try:
            if callable(self._agent_or_factory):
                agent, tool_client = await self._resolve_agent_for_request(context)
            elif self._resolved_agent is None:
                await self._resolve_agent(context)
                agent = self._resolved_agent
            else:
                agent = self._resolved_agent

            logger.info(f"Starting agent_run with stream={context.stream}")
            request_input = context.request.get("input")

            agent_thread = None
            checkpoint_storage = None
            last_checkpoint = None
            if self._thread_repository:
                agent_thread = await self._thread_repository.get(context.conversation_id)
                if agent_thread:
                    logger.info(f"Loaded agent thread for conversation: {context.conversation_id}")
                else:
                    agent_thread = agent.get_new_thread()
            
            if self._checkpoint_repository:
                checkpoint_storage = await self._checkpoint_repository.get_or_create(context.conversation_id)
                last_checkpoint = await self.get_latest_checkpoint(checkpoint_storage)
                if last_checkpoint:
                    summary = get_checkpoint_summary(last_checkpoint)
                    if summary.status == "completed":
                        logger.warning("Last checkpoint is completed. Will not resume from it.")
                        last_checkpoint = None  # Do not resume from completed checkpoints
                if last_checkpoint:
                    logger.info(f"Loading checkpoint ID: {last_checkpoint.checkpoint_id}")
                    await self.load_checkpoint(agent, last_checkpoint, checkpoint_storage)


            input_converter = AgentFrameworkInputConverter(hitl_helper=self._hitl_helper)
            message = await input_converter.transform_input(
                request_input,
                agent_thread=agent_thread,
                checkpoint=last_checkpoint)
            logger.debug(f"Transformed input message type: {type(message)}")

            # Use split converters
            if context.stream:
                logger.info("Running agent in streaming mode")
                streaming_converter = AgentFrameworkOutputStreamingConverter(context, hitl_helper=self._hitl_helper)

                async def stream_updates():
                    try:
                        update_count = 0
                        updates = agent.run_stream(
                            message,
                            thread=agent_thread,
                            checkpoint_storage=checkpoint_storage,
                            checkpoint_id=last_checkpoint.checkpoint_id if last_checkpoint else None,
                        )
                        async for event in streaming_converter.convert(updates):
                            update_count += 1
                            yield event
                        
                        if agent_thread and self._thread_repository:
                            await self._thread_repository.set(context.conversation_id, agent_thread, checkpoint_storage)
                            logger.info(f"Saved agent thread for conversation: {context.conversation_id}")
                            
                        logger.info("Streaming completed with %d updates", update_count)
                    finally:
                        # Close tool_client if it was created for this request
                        if tool_client is not None:
                            try:
                                await tool_client.close()
                                logger.debug("Closed tool_client after streaming completed")
                            except Exception as ex:  # pylint: disable=broad-exception-caught
                                logger.warning(f"Error closing tool_client in stream: {ex}")

                return stream_updates()

            # Non-streaming path
            logger.info("Running agent in non-streaming mode")
            non_streaming_converter = AgentFrameworkOutputNonStreamingConverter(context, hitl_helper=self._hitl_helper)
            result = await agent.run(message,
                        thread=agent_thread,
                        checkpoint_storage=checkpoint_storage,
                        checkpoint_id=last_checkpoint.checkpoint_id if last_checkpoint else None,
                        )

            if agent_thread and self._thread_repository:
                await self._thread_repository.set(context.conversation_id, agent_thread, checkpoint_storage)
                logger.info(f"Saved agent thread for conversation: {context.conversation_id}")
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
            # Close tool_client if it was created for this request (non-streaming only, streaming handles in generator)
            if not context.stream and tool_client is not None:
                try:
                    await tool_client.close()
                    logger.debug("Closed tool_client after request processing")
                except Exception as ex:  # pylint: disable=broad-exception-caught
                    logger.warning(f"Error closing tool_client: {ex}")

    async def get_latest_checkpoint(self,
                checkpoint_storage: CheckpointStorage) -> Optional[Any]:
        """Load the latest checkpoint from the given storage.

        :param checkpoint_storage: The checkpoint storage to load from.
        :type checkpoint_storage: CheckpointStorage

        :return: The latest checkpoint if available, None otherwise.
        :rtype: Optional[Any]
        """
        checkpoints = await checkpoint_storage.list_checkpoints()
        if checkpoints:
            latest_checkpoint = max(checkpoints, key=lambda cp: cp.timestamp)
            logger.info(f"Got latest checkpoint with ID: {latest_checkpoint.checkpoint_id}")
            return latest_checkpoint
        return None

    async def load_checkpoint(self, agent: AgentProtocol,
                              checkpoint: WorkflowCheckpoint,
                              checkpoint_storage: CheckpointStorage) -> None:
        """Load the checkpoint data from the given WorkflowCheckpoint.

        :param checkpoint: The WorkflowCheckpoint to load data from.
        :type checkpoint: WorkflowCheckpoint
        """
        if checkpoint:
            res = await agent.run(checkpoint_id=checkpoint.checkpoint_id,
                                  checkpoint_storage=checkpoint_storage)
            logger.info(f"Loaded checkpoint with ID: {checkpoint.checkpoint_id}")
            logger.info(f"Result: {res}")