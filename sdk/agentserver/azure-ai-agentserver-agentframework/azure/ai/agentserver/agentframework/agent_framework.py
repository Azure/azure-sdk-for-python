# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=logging-fstring-interpolation
from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import os
from typing import Any, AsyncGenerator, Union

from agent_framework import AgentProtocol
from agent_framework.azure import AzureAIAgentClient  # pylint: disable=no-name-in-module
from opentelemetry import trace

from azure.ai.agentserver.core import AgentRunContext, FoundryCBAgent
from azure.ai.agentserver.core.constants import Constants as AdapterConstants
from azure.ai.agentserver.core.logger import get_logger
from azure.ai.agentserver.core.models import (
    CreateResponse,
    Response as OpenAIResponse,
    ResponseStreamEvent,
)
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

from .models.agent_framework_input_converters import AgentFrameworkInputConverter
from .models.agent_framework_output_non_streaming_converter import (
    AgentFrameworkOutputNonStreamingConverter,
)
from .models.agent_framework_output_streaming_converter import AgentFrameworkOutputStreamingConverter
from .models.constants import Constants

logger = get_logger()


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

    def __init__(self, agent: AgentProtocol):
        super().__init__()
        self.agent = agent
        logger.info(f"Initialized AgentFrameworkCBAgent with agent: {type(agent).__name__}")

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
        exporter = os.environ.get(AdapterConstants.OTEL_EXPORTER_ENDPOINT)
        app_insights_conn_str = os.environ.get(AdapterConstants.APPLICATION_INSIGHTS_CONNECTION_STRING)
        project_endpoint = os.environ.get(AdapterConstants.AZURE_AI_PROJECT_ENDPOINT)

        if project_endpoint:
            project_client = AIProjectClient(endpoint=project_endpoint, credential=DefaultAzureCredential())
            agent_client = AzureAIAgentClient(project_client=project_client)
            agent_client.setup_azure_ai_observability()
        elif exporter or app_insights_conn_str:
            os.environ["WORKFLOW_ENABLE_OTEL"] = "true"
            from agent_framework.observability import setup_observability

            setup_observability(
                enable_sensitive_data=True,
                otlp_endpoint=exporter,
                applicationinsights_connection_string=app_insights_conn_str,
            )
        self.tracer = trace.get_tracer(__name__)

    async def agent_run(
        self, context: AgentRunContext
    ) -> Union[
        OpenAIResponse,
        AsyncGenerator[ResponseStreamEvent, Any],
    ]:
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
                update_count = 0
                timeout_s = self._resolve_stream_timeout(context.request)
                logger.info("Starting streaming with idle-timeout=%.2fs", timeout_s)
                for ev in streaming_converter.initial_events():
                    yield ev

                # Iterate with per-update timeout; terminate if idle too long
                aiter = self.agent.run_stream(message).__aiter__()
                while True:
                    try:
                        update = await asyncio.wait_for(aiter.__anext__(), timeout=timeout_s)
                    except StopAsyncIteration:
                        logger.debug("Agent streaming iterator finished (StopAsyncIteration)")
                        break
                    except asyncio.TimeoutError:
                        logger.warning("Streaming idle timeout reached (%.1fs); terminating stream.", timeout_s)
                        for ev in streaming_converter.completion_events():
                            yield ev
                        return
                    update_count += 1
                    transformed = streaming_converter.transform_output_for_streaming(update)
                    for event in transformed:
                        yield event
                for ev in streaming_converter.completion_events():
                    yield ev
                logger.info("Streaming completed with %d updates", update_count)

            return stream_updates()

        # Non-streaming path
        logger.info("Running agent in non-streaming mode")
        non_streaming_converter = AgentFrameworkOutputNonStreamingConverter(context)
        result = await self.agent.run(message)
        logger.debug(f"Agent run completed, result type: {type(result)}")
        transformed_result = non_streaming_converter.transform_output_for_response(result)
        logger.info("Agent run and transformation completed successfully")
        return transformed_result
