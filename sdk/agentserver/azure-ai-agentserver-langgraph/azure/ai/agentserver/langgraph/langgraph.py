# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=logging-fstring-interpolation,broad-exception-caught,no-member
# mypy: disable-error-code="assignment,arg-type"
import os
import re
from typing import Optional, TYPE_CHECKING, Union

from langgraph.graph.state import CompiledStateGraph

from azure.ai.agentserver.core.constants import Constants
from azure.ai.agentserver.core.logger import get_logger
from azure.ai.agentserver.core.server.base import FoundryCBAgent
from azure.ai.agentserver.core.server.common.agent_run_context import AgentRunContext
from azure.ai.agentserver.core.tools import OAuthConsentRequiredError
from ._context import LanggraphRunContext
from .models.response_api_converter import GraphInputArguments, ResponseAPIConverter
from .models.response_api_default_converter import ResponseAPIDefaultConverter
from .models.utils import is_state_schema_valid
from .tools._context import FoundryToolContext
from .tools._resolver import FoundryLangChainToolResolver

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential

logger = get_logger()


class LangGraphAdapter(FoundryCBAgent):
    """
    Adapter for LangGraph Agent.
    """

    def __init__(
        self,
        graph: CompiledStateGraph,
        credentials: "Optional[AsyncTokenCredential]" = None,
        converter: "Optional[ResponseAPIConverter]" = None,
    ) -> None:
        """
        Initialize the LangGraphAdapter with a CompiledStateGraph or a function that returns one.

        :param graph: The LangGraph StateGraph to adapt, or a callable that takes ToolClient
            and returns CompiledStateGraph (sync or async).
        :type graph: Union[CompiledStateGraph, GraphFactory]
        :param credentials: Azure credentials for authentication.
        :type credentials: Optional[AsyncTokenCredential]
        :param converter: custom response converter.
        :type converter: Optional[ResponseAPIConverter]
        """
        super().__init__(credentials=credentials) # pylint: disable=unexpected-keyword-arg
        self._graph = graph
        self._tool_resolver = FoundryLangChainToolResolver()
        self.azure_ai_tracer = None

        if not converter:
            if is_state_schema_valid(self._graph.builder.state_schema):
                self.converter = ResponseAPIDefaultConverter(graph=self._graph)
            else:
                raise ValueError("converter is required for non-MessagesState graph.")
        else:
            self.converter = converter

    async def agent_run(self, context: AgentRunContext):
        # Resolve graph - always resolve if it's a factory function to get fresh graph each time
        # For factories, get a new graph instance per request to avoid concurrency issues
        try:
            input_arguments = await self.converter.convert_request(context)
            self.ensure_runnable_config(context, input_arguments)

            lg_run_context = await self.setup_lg_run_context()
            if not context.stream:
                response = await self.agent_run_non_stream(input_arguments, context, lg_run_context)
                return response

            # For streaming, pass tool_client to be closed after streaming completes
            return self.agent_run_astream(input_arguments, context, lg_run_context)
        except OAuthConsentRequiredError as e:
            if not context.stream:
                response = await self.respond_with_oauth_consent(context, e)
                return response
            return self.respond_with_oauth_consent_astream(context, e)
        except Exception:
            raise

    async def setup_lg_run_context(self):
        resolved = await self._tool_resolver.resolve_from_registry()
        return LanggraphRunContext(FoundryToolContext(resolved))

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

    async def agent_run_non_stream(self, input_arguments: GraphInputArguments, context: AgentRunContext,
                                   lg_run_context: LanggraphRunContext):
        """
        Run the agent with non-streaming response.

        :param input_arguments: The input data to run the agent with.
        :type input_arguments: GraphInputArguments
        :param context: The context for the agent run.
        :type context: AgentRunContext
        :param lg_run_context: The tool context for the agent run.
        :type lg_run_context: FoundryToolContext

        :return: The response of the agent run.
        :rtype: dict
        """

        try:
            result = await self._graph.ainvoke(**input_arguments, context=lg_run_context)
            output = self.converter.convert_response_non_stream(result, context)
            return output
        except Exception as e:
            logger.error(f"Error during agent run: {e}", exc_info=True)
            raise e

    async def agent_run_astream(self,
                                input_arguments: GraphInputArguments,
                                context: AgentRunContext,
                                lg_run_context: LanggraphRunContext):
        """
        Run the agent with streaming response.

        :param input_arguments: The input data to run the agent with.
        :type input_arguments: GraphInputArguments
        :param context: The context for the agent run.
        :type context: AgentRunContext
        :param lg_run_context: The tool context for the agent run.
        :type lg_run_context: FoundryToolContext

        :return: An async generator yielding the response stream events.
        :rtype: AsyncGenerator[dict]
        """
        try:
            logger.info(f"Starting streaming agent run {context.response_id}")
            stream = self._graph.astream(**input_arguments, context=lg_run_context)
            async for output_event in self.converter.convert_response_stream(stream, context):
                yield output_event
        except Exception as e:
            logger.error(f"Error during streaming agent run: {e}", exc_info=True)
            raise e

    def ensure_runnable_config(self, context: AgentRunContext, input_arguments: GraphInputArguments):
        """
        Ensure the RunnableConfig is set in the input arguments.

        :param context: The context for the agent run.
        :type context: AgentRunContext
        :param input_arguments: The input arguments for the agent run.
        :type input_arguments: GraphInputArguments
        """
        config = input_arguments.get("config", {})
        configurable = config.get("configurable", {})
        configurable["thread_id"] = context.conversation_id
        config["configurable"] = configurable

        callbacks = config.get("callbacks", [])
        if self.azure_ai_tracer and self.azure_ai_tracer not in callbacks:
            callbacks.append(self.azure_ai_tracer)
            config["callbacks"] = callbacks
        input_arguments["config"] = config

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
