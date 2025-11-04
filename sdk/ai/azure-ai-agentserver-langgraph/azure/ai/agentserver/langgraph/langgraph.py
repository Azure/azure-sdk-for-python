# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import re
from typing import Optional

from azure.ai.agentserver.core.constants import Constants
from azure.ai.agentserver.core.logger import get_logger
from azure.ai.agentserver.core.server.base import FoundryCBAgent
from azure.ai.agentserver.core.server.common.agent_run_context import AgentRunContext
from langchain_core.runnables import RunnableConfig

from langgraph.graph.state import CompiledStateGraph

from .models import (
    LanggraphMessageStateConverter,
    LanggraphStateConverter,
)
from .models.utils import is_state_schema_valid

logger = get_logger()


class LangGraphAdapter(FoundryCBAgent):
    """
    Adapter for LangGraph Agent.
    """

    def __init__(self, graph: CompiledStateGraph, state_converter: Optional[LanggraphStateConverter] = None):
        """
        Initialize the LangGraphAdapter with a CompiledStateGraph.

        Args:
            graph (StateGraph): The LangGraph StateGraph to adapt.
            state_converter: custom state converter. Required if graph state is not MessagesState.
        """
        super().__init__()
        self.graph = graph
        self.azure_ai_tracer = None
        if not state_converter:
            if is_state_schema_valid(self.graph.builder.state_schema):
                self.state_converter = LanggraphMessageStateConverter()
            else:
                raise ValueError("state_converter is required for non-MessagesState graph.")
        else:
            self.state_converter = state_converter

    async def agent_run(self, context: AgentRunContext):
        input_data = self.state_converter.request_to_state(context)
        logger.debug(f"Converted input data: {input_data}")
        if not context.stream:
            response = await self.agent_run_non_stream(input_data, context)
            return response
        else:
            return self.agent_run_astream(input_data, context)

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
        attrs["service.namespace"] = "azure.ai.agentshosting.langgraph"
        return attrs

    async def agent_run_non_stream(self, input_data: dict, context: AgentRunContext):
        """
        Run the agent with non-streaming response.

        Args:
            context (AgentRunContext): The context for the agent run.

        Returns:
            RunObject: The result of the agent run.
        """

        try:
            config = self.create_runnable_config(context)
            stream_mode = self.state_converter.get_stream_mode(context)
            result = await self.graph.ainvoke(input_data, config=config, stream_mode=stream_mode)
            output = self.state_converter.state_to_response(result, context)
            return output
        except Exception as e:
            logger.error(f"Error during agent run: {e}")
            raise e

    async def agent_run_astream(self, input_data: dict, context: AgentRunContext):
        """
        Run the agent with streaming response.

        Args:
            request_body (CreateResponse): The request body to run the agent with.

        Returns:
            StreamingResponse: The streaming response of the agent run.
        """
        try:
            logger.info(f"Starting streaming agent run {context.response_id}")
            config = self.create_runnable_config(context)
            stream_mode = self.state_converter.get_stream_mode(context)
            stream = self.graph.astream(input=input_data, config=config, stream_mode=stream_mode)
            async for result in self.state_converter.state_to_response_stream(stream, context):
                yield result
        except Exception as e:
            logger.error(f"Error during streaming agent run: {e}")
            raise e

    def create_runnable_config(self, context: AgentRunContext) -> RunnableConfig:
        """
        Create a RunnableConfig from the converted request data.
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
        return "AgentsHosting-LangGraph"
