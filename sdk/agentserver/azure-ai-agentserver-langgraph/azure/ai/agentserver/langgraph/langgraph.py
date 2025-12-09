# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=logging-fstring-interpolation,broad-exception-caught,no-member
# mypy: disable-error-code="assignment,arg-type"
import os
import re
from typing import TYPE_CHECKING, Any, Awaitable, Protocol, Union, Optional, List

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import StructuredTool
from langgraph.graph.state import CompiledStateGraph

from azure.ai.agentserver.core.client.tools import OAuthConsentRequiredError
from azure.ai.agentserver.core.constants import Constants
from azure.ai.agentserver.core.logger import get_logger
from azure.ai.agentserver.core.server.base import FoundryCBAgent
from azure.ai.agentserver.core.server.common.agent_run_context import AgentRunContext

from .models import (
    LanggraphMessageStateConverter,
    LanggraphStateConverter,
)
from .models.utils import is_state_schema_valid
from .tool_client import ToolClient

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential

logger = get_logger()


class GraphFactory(Protocol):
    """Protocol for graph factory functions.

    A graph factory is a callable that takes a ToolClient and returns
    a CompiledStateGraph, either synchronously or asynchronously.
    """

    def __call__(self, tools: List[StructuredTool]) -> Union[CompiledStateGraph, Awaitable[CompiledStateGraph]]:
        """Create a CompiledStateGraph using the provided ToolClient.

        :param tools: The list of StructuredTool instances.
        :type tools: List[StructuredTool]
        :return: A compiled LangGraph state graph, or an awaitable that resolves to one.
        :rtype: Union[CompiledStateGraph, Awaitable[CompiledStateGraph]]
        """
        ...


class LangGraphAdapter(FoundryCBAgent):
    """
    Adapter for LangGraph Agent.
    """

    def __init__(
        self,
        graph: Union[CompiledStateGraph, GraphFactory],
        credentials: "Optional[AsyncTokenCredential]" = None,
        state_converter: "Optional[LanggraphStateConverter]" = None,
        **kwargs: Any
    ) -> None:
        """
        Initialize the LangGraphAdapter with a CompiledStateGraph or a function that returns one.

        :param graph: The LangGraph StateGraph to adapt, or a callable that takes ToolClient
            and returns CompiledStateGraph (sync or async).
        :type graph: Union[CompiledStateGraph, GraphFactory]
        :param credentials: Azure credentials for authentication.
        :type credentials: Optional[AsyncTokenCredential]
        :param state_converter: custom state converter. Required if graph state is not MessagesState.
        :type state_converter: Optional[LanggraphStateConverter]
        """
        super().__init__(credentials=credentials, **kwargs) # pylint: disable=unexpected-keyword-arg
        self._graph_or_factory: Union[CompiledStateGraph, GraphFactory] = graph
        self._resolved_graph: "Optional[CompiledStateGraph]" = None
        self.azure_ai_tracer = None

        # If graph is already compiled, validate and set up state converter
        if isinstance(graph, CompiledStateGraph):
            self._resolved_graph = graph
            if not state_converter:
                if is_state_schema_valid(self._resolved_graph.builder.state_schema):
                    self.state_converter = LanggraphMessageStateConverter()
                else:
                    raise ValueError("state_converter is required for non-MessagesState graph.")
            else:
                self.state_converter = state_converter
        else:
            # Defer validation until graph is resolved
            self.state_converter = state_converter

    @property
    def graph(self) -> "Optional[CompiledStateGraph]":
        """
        Get the resolved graph. This property provides backward compatibility.

        :return: The resolved CompiledStateGraph if available, None otherwise.
        :rtype: Optional[CompiledStateGraph]
        """
        return self._resolved_graph

    async def agent_run(self, context: AgentRunContext):
        # Resolve graph - always resolve if it's a factory function to get fresh graph each time
        # For factories, get a new graph instance per request to avoid concurrency issues
        tool_client = None
        try:
            if callable(self._graph_or_factory):
                graph, tool_client = await self._resolve_graph_for_request(context)
            elif self._resolved_graph is None:
                await self._resolve_graph(context)
                graph = self._resolved_graph
            else:
                graph = self._resolved_graph

            input_data = self.state_converter.request_to_state(context)
            logger.debug(f"Converted input data: {input_data}")
            if not context.stream:
                try:
                    response = await self.agent_run_non_stream(input_data, context, graph)
                    return response
                finally:
                    # Close tool_client for non-streaming requests
                    if tool_client is not None:
                        try:
                            await tool_client.close()
                            logger.debug("Closed tool_client after non-streaming request")
                        except Exception as e:
                            logger.warning(f"Error closing tool_client: {e}")

            # For streaming, pass tool_client to be closed after streaming completes
            return self.agent_run_astream(input_data, context, graph, tool_client)
        except OAuthConsentRequiredError as e:
            # Clean up tool_client if OAuth error occurs before streaming starts
            if tool_client is not None:
                await tool_client.close()

            if not context.stream:
                response = await self.respond_with_oauth_consent(context, e)
                return response
            return self.respond_with_oauth_consent_astream(context, e)
        except Exception:
            # Clean up tool_client if error occurs before streaming starts
            if tool_client is not None:
                await tool_client.close()
            raise

    async def _resolve_graph(self, context: AgentRunContext):
        """Resolve the graph if it's a factory function (for single-use/first-time resolution).
        Creates a ToolClient and calls the factory function with it.
        This is used for the initial resolution to set up state_converter.

        :param context: The context for the agent run.
        :type context: AgentRunContext
        """
        if callable(self._graph_or_factory):
            logger.debug("Resolving graph from factory function")


            # Create ToolClient with credentials
            tool_client = self.get_tool_client(tools = context.get_tools(), user_info = context.get_user_info()) # pylint: disable=no-member
            tool_client_wrapper = ToolClient(tool_client)
            tools = await tool_client_wrapper.list_tools()
            # Call the factory function with ToolClient
            # Support both sync and async factories
            import inspect
            result = self._graph_or_factory(tools)
            if inspect.iscoroutine(result):
                self._resolved_graph = await result
            else:
                self._resolved_graph = result

            # Validate and set up state converter if not already set from initialization
            if not self.state_converter and self._resolved_graph is not None:
                if is_state_schema_valid(self._resolved_graph.builder.state_schema):
                    self.state_converter = LanggraphMessageStateConverter()
                else:
                    raise ValueError("state_converter is required for non-MessagesState graph.")

            logger.debug("Graph resolved successfully")
        else:
            # Should not reach here, but just in case
            self._resolved_graph = self._graph_or_factory

    async def _resolve_graph_for_request(self, context: AgentRunContext):
        """
        Resolve a fresh graph instance for a single request to avoid concurrency issues.
        Creates a ToolClient and calls the factory function with it.
        This method returns a new graph instance and the tool_client for cleanup.

        :param context: The context for the agent run.
        :type context: AgentRunContext
        :return: A tuple of (compiled graph instance, tool_client wrapper).
        :rtype: tuple[CompiledStateGraph, ToolClient]
        """
        logger.debug("Resolving fresh graph from factory function for request")

        # Create ToolClient with credentials
        tool_client = self.get_tool_client(tools = context.get_tools(), user_info = context.get_user_info()) # pylint: disable=no-member
        tool_client_wrapper = ToolClient(tool_client)
        tools = await tool_client_wrapper.list_tools()
        # Call the factory function with ToolClient
        # Support both sync and async factories
        import inspect
        result = self._graph_or_factory(tools)  # type: ignore[operator]
        if inspect.iscoroutine(result):
            graph = await result
        else:
            graph = result

        # Ensure state converter is set up (use existing one or create new)
        if not self.state_converter:
            if is_state_schema_valid(graph.builder.state_schema):
                self.state_converter = LanggraphMessageStateConverter()
            else:
                raise ValueError("state_converter is required for non-MessagesState graph.")

        logger.debug("Fresh graph resolved successfully for request")
        return graph, tool_client_wrapper

    def init_tracing_internal(self, exporter_endpoint=None, app_insights_conn_str=None):
        # set env vars for langsmith
        os.environ["LANGSMITH_OTEL_ENABLED"] = "true"
        os.environ["LANGSMITH_TRACING"] = "true"
        os.environ["LANGSMITH_OTEL_ONLY"] = "true"
        if app_insights_conn_str:
            # setup azure ai telemetry callbacks
            try:
                from langchain_azure_ai.callbacks.tracers import AzureAIOpenTelemetryTracer

                self.azure_ai_tracer = AzureAIOpenTelemetryTracer(
                    connection_string=app_insights_conn_str,
                    enable_content_recording=True,
                    name=self.get_agent_identifier(),
                )
                logger.info("AzureAIOpenTelemetryTracer initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to import AzureAIOpenTelemetryTracer, ignore: {e}")

    def setup_otlp_exporter(self, endpoint, provider):
        endpoint = self.format_otlp_endpoint(endpoint)
        return super().setup_otlp_exporter(endpoint, provider)

    def get_trace_attributes(self):
        attrs = super().get_trace_attributes()
        attrs["service.namespace"] = "azure.ai.agentserver.langgraph"
        return attrs

    async def agent_run_non_stream(self, input_data: dict, context: AgentRunContext, graph: CompiledStateGraph):
        """
        Run the agent with non-streaming response.

        :param input_data: The input data to run the agent with.
        :type input_data: dict
        :param context: The context for the agent run.
        :type context: AgentRunContext
        :param graph: The compiled graph instance to use for this request.
        :type graph: CompiledStateGraph

        :return: The response of the agent run.
        :rtype: dict
        """

        try:
            config = self.create_runnable_config(context)
            stream_mode = self.state_converter.get_stream_mode(context)
            result = await graph.ainvoke(input_data, config=config, stream_mode=stream_mode)
            output = self.state_converter.state_to_response(result, context)
            return output
        except Exception as e:
            logger.error(f"Error during agent run: {e}", exc_info=True)
            raise e

    async def agent_run_astream(
        self,
        input_data: dict,
        context: AgentRunContext,
        graph: CompiledStateGraph,
        tool_client: "Optional[ToolClient]" = None
    ):
        """
        Run the agent with streaming response.

        :param input_data: The input data to run the agent with.
        :type input_data: dict
        :param context: The context for the agent run.
        :type context: AgentRunContext
        :param graph: The compiled graph instance to use for this request.
        :type graph: CompiledStateGraph
        :param tool_client: Optional ToolClient to close after streaming completes.
        :type tool_client: Optional[ToolClient]

        :return: An async generator yielding the response stream events.
        :rtype: AsyncGenerator[dict]
        """
        try:
            logger.info(f"Starting streaming agent run {context.response_id}")
            config = self.create_runnable_config(context)
            stream_mode = self.state_converter.get_stream_mode(context)
            stream = graph.astream(input=input_data, config=config, stream_mode=stream_mode)
            async for result in self.state_converter.state_to_response_stream(stream, context):
                yield result
        except Exception as e:
            logger.error(f"Error during streaming agent run: {e}", exc_info=True)
            raise e
        finally:
            # Close tool_client if provided
            if tool_client is not None:
                try:
                    await tool_client.close()
                    logger.debug("Closed tool_client after streaming completed")
                except Exception as e:
                    logger.warning(f"Error closing tool_client in stream: {e}")

    def create_runnable_config(self, context: AgentRunContext) -> RunnableConfig:
        """
        Create a RunnableConfig from the converted request data.

        :param context: The context for the agent run.
        :type context: AgentRunContext

        :return: The RunnableConfig for the agent run.
        :rtype: RunnableConfig
        """
        config = RunnableConfig(
            configurable={
                "thread_id": context.conversation_id,
            },
            callbacks=[self.azure_ai_tracer] if self.azure_ai_tracer else None,
        )
        return config

    def format_otlp_endpoint(self, endpoint: str) -> str:
        m = re.match(r"^(https?://[^/]+)", endpoint)
        if m:
            return f"{m.group(1)}/v1/traces"
        return endpoint

    def get_agent_identifier(self) -> str:
        agent_name = os.getenv(Constants.AGENT_NAME)
        if agent_name:
            return agent_name
        agent_id = os.getenv(Constants.AGENT_ID)
        if agent_id:
            return agent_id
        return "HostedAgent-LangGraph"
