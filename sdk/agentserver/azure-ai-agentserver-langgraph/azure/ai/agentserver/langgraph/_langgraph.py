# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import re
from typing import TYPE_CHECKING, Any, List, Optional, cast

from langgraph.graph.state import CompiledStateGraph

from azure.ai.agentserver.core.constants import Constants
from azure.ai.agentserver.core.logger import get_logger
from azure.ai.agentserver.core.server._base import FoundryCBAgent
from azure.ai.agentserver.core import AgentRunContext
from azure.ai.agentserver.core.tools import OAuthConsentRequiredError  # pylint:disable=import-error,no-name-in-module
from ._context import LanggraphRunContext
from .models._response_api_converter import GraphInputArguments, ResponseAPIConverter
from .models._response_api_default_converter import ResponseAPIDefaultConverter
from .models._utils import is_state_schema_valid
from .tools._context import FoundryToolContext
from .tools._resolver import FoundryLangChainToolResolver

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential
    from azure.core.credentials_async import AsyncTokenCredential

logger = get_logger()


class LangGraphAdapter(FoundryCBAgent):
    """
    Adapter for LangGraph Agent.
    """

    def __init__(
        self,
        graph: CompiledStateGraph,
        credentials: "Optional[AsyncTokenCredential | TokenCredential]" = None,
        converter: "Optional[ResponseAPIConverter]" = None,
    ) -> None:
        """
        Initialize the LangGraphAdapter with a CompiledStateGraph or a function that returns one.

        :param graph: The LangGraph StateGraph to adapt, or a callable that takes ToolClient
            and returns CompiledStateGraph (sync or async).
        :type graph: Union[CompiledStateGraph, GraphFactory]
        :param credentials: Azure credentials for authentication.
        :type credentials: Optional[AsyncTokenCredential | TokenCredential]
        :param converter: custom response converter.
        :type converter: Optional[ResponseAPIConverter]
        """
        super().__init__(credentials=credentials)  # pylint: disable=unexpected-keyword-arg
        self._graph = graph
        self._tool_resolver = FoundryLangChainToolResolver()
        self.azure_ai_tracer = None
        self.converter: ResponseAPIConverter

        if not converter:
            if is_state_schema_valid(self._graph.builder.state_schema):
                self.converter = ResponseAPIDefaultConverter(graph=self._graph)
            else:
                raise ValueError("converter is required for non-MessagesState graph.")
        else:
            self.converter = converter

    async def agent_run(self, context: AgentRunContext):
        """Execute a LangGraph-backed agent run.

        :param context: The agent run context supplied by Agent Server.
        :type context: AgentRunContext

        :return: A response object or an async response stream.
        :rtype: Any
        """
        # Resolve graph - always resolve if it's a factory function to get fresh graph each time
        # For factories, get a new graph instance per request to avoid concurrency issues
        try:
            lg_run_context = await self.setup_lg_run_context(context)
            input_arguments = await self.converter.convert_request(lg_run_context)
            self.ensure_runnable_config(input_arguments, lg_run_context)

            if not context.stream:
                response = await self.agent_run_non_stream(input_arguments)
                return response

            return self.agent_run_astream(input_arguments)
        except OAuthConsentRequiredError as e:
            if not context.stream:
                response = await self.respond_with_oauth_consent(context, e)
                return response
            return self.respond_with_oauth_consent_astream(context, e)

    async def setup_lg_run_context(self, agent_run_context: AgentRunContext) -> LanggraphRunContext:
        """Build the LangGraph run context for the current request.

        :param agent_run_context: The agent run context from the server layer.
        :type agent_run_context: AgentRunContext

        :return: The run context used by the adapter and tools.
        :rtype: LanggraphRunContext
        """
        resolved = await self._tool_resolver.resolve_from_registry()
        return LanggraphRunContext(
            agent_run_context,
            FoundryToolContext(resolved))

    def init_tracing_internal(self, exporter_endpoint=None, app_insights_conn_str=None):
        """Initialize LangSmith and Azure AI tracing hooks for the adapter.

        :param exporter_endpoint: Optional OTLP exporter endpoint.
        :type exporter_endpoint: Optional[str]
        :param app_insights_conn_str: Optional Application Insights connection string.
        :type app_insights_conn_str: Optional[str]
        """
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
            except Exception as error:  # pylint: disable=broad-except
                logger.error("Failed to initialize AzureAIOpenTelemetryTracer, ignore: %s", error)

    def setup_otlp_exporter(self, endpoint, provider):
        """Normalize the OTLP endpoint before delegating exporter setup.

        :param endpoint: The configured exporter endpoint.
        :type endpoint: str
        :param provider: The tracer provider receiving the exporter.
        :type provider: Any

        :return: The configured exporter registration result.
        :rtype: Any
        """
        endpoint = self.format_otlp_endpoint(endpoint)
        return super().setup_otlp_exporter(endpoint, provider)

    def get_trace_attributes(self):
        """Return base tracing attributes for LangGraph spans.

        :return: The trace attributes for this adapter.
        :rtype: dict
        """
        attrs = super().get_trace_attributes()
        attrs["service.namespace"] = "azure.ai.agentserver.langgraph"
        return attrs

    async def agent_run_non_stream(self, input_arguments: GraphInputArguments):
        """
        Run the agent with non-streaming response.

        :param input_arguments: The input data to run the agent with.
        :type input_arguments: GraphInputArguments

        :return: The response of the agent run.
        :rtype: dict
        """
        try:
            result = await self._ainvoke_graph(input_arguments)
            output = await self.converter.convert_response_non_stream(result, input_arguments["context"])
            return output
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error during agent run: %s", e, exc_info=True)
            raise e

    async def agent_run_astream(self,
                                input_arguments: GraphInputArguments):
        """
        Run the agent with streaming response.

        :param input_arguments: The input data to run the agent with.
        :type input_arguments: GraphInputArguments

        :return: An async generator yielding the response stream events.
        :rtype: AsyncGenerator[dict]
        """
        try:
            logger.info("Starting streaming agent run %s", input_arguments["context"].agent_run.response_id)
            stream = self._astream_graph(input_arguments)
            async for output_event in self.converter.convert_response_stream(
                stream,
                input_arguments["context"],
            ):
                yield output_event
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error during streaming agent run: %s", e, exc_info=True)
            raise e

    async def _ainvoke_graph(self, input_arguments: GraphInputArguments) -> Any:
        """Invoke the compiled graph with the LangGraph-supported arguments only.

        :param input_arguments: The adapter-level graph invocation arguments.
        :type input_arguments: GraphInputArguments

        :return: The graph execution result.
        :rtype: Any
        """
        invoke_kwargs = input_arguments.get("invoke_kwargs", {})
        return await self._graph.ainvoke(
            input_arguments["input"],
            config=input_arguments["config"],
            stream_mode=input_arguments["stream_mode"],
            **invoke_kwargs,
        )

    def _astream_graph(self, input_arguments: GraphInputArguments):
        """Stream the compiled graph with the LangGraph-supported arguments only.

        :param input_arguments: The adapter-level graph invocation arguments.
        :type input_arguments: GraphInputArguments

        :return: The async graph event iterator.
        :rtype: AsyncIterator[Any]
        """
        invoke_kwargs = input_arguments.get("invoke_kwargs", {})
        return self._graph.astream(
            input_arguments["input"],
            config=input_arguments["config"],
            stream_mode=input_arguments["stream_mode"],
            **invoke_kwargs,
        )

    def ensure_runnable_config(self, input_arguments: GraphInputArguments, context: LanggraphRunContext):
        """
        Ensure the RunnableConfig is set in the input arguments.

        :param input_arguments: The input arguments for the agent run.
        :type input_arguments: GraphInputArguments
        :param context: The Langgraph run context.
        :type context: LanggraphRunContext
        """
        config = input_arguments.get("config", {})
        configurable = config.get("configurable", {})
        thread_id = input_arguments["context"].agent_run.conversation_id
        if thread_id:
            configurable["thread_id"] = thread_id
        else:
            configurable["thread_id"] = f"langgraph-{input_arguments['context'].agent_run.response_id}"
            logger.debug("Conversation ID not provided, generate one: thread_id=%s", configurable["thread_id"])
        config["configurable"] = configurable
        context.attach_to_config(config)

        callbacks = cast(List[object], config.get("callbacks") or [])
        if self.azure_ai_tracer and self.azure_ai_tracer not in callbacks:
            callbacks.append(self.azure_ai_tracer)
            config["callbacks"] = callbacks
        input_arguments["config"] = config

    def format_otlp_endpoint(self, endpoint: str) -> str:
        """Ensure the OTLP endpoint includes the traces ingestion path.

        :param endpoint: The configured exporter endpoint.
        :type endpoint: str

        :return: The normalized traces endpoint.
        :rtype: str
        """
        m = re.match(r"^(https?://[^/]+)", endpoint)
        if m:
            return f"{m.group(1)}/v1/traces"
        return endpoint

    def get_agent_identifier(self) -> str:
        """Resolve the agent identifier used by tracing integrations.

        :return: The configured agent name or identifier.
        :rtype: str
        """
        agent_name = os.getenv(Constants.AGENT_NAME)
        if agent_name:
            return agent_name
        agent_id = os.getenv(Constants.AGENT_ID)
        if agent_id:
            return agent_id
        return "HostedAgent-LangGraph"
