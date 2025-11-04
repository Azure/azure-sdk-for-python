# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable
import os
import pytest
from azure.ai.projects.telemetry import AIProjectInstrumentor, _utils
from azure.core.settings import settings
from gen_ai_trace_verifier import GenAiTraceVerifier
from azure.ai.projects.models import PromptAgentDefinition, PromptAgentDefinitionText
from azure.ai.projects.models import (
    Reasoning,
    FunctionTool,
    ResponseTextFormatConfigurationText,
)

from devtools_testutils.aio import recorded_by_proxy_async

from test_base import servicePreparer
from test_ai_instrumentor_base import TestAiAgentsInstrumentorBase, MessageCreationMode, CONTENT_TRACING_ENV_VARIABLE

settings.tracing_implementation = "OpenTelemetry"
_utils._span_impl_type = settings.tracing_implementation()


class TestAiAgentsInstrumentor(TestAiAgentsInstrumentorBase):
    """Tests for AI agents instrumentor."""

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_create_agent_with_tracing_content_recording_enabled(self, **kwargs):
        self.cleanup()
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "True"})
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        model = self.test_agents_params["model_deployment_name"]

        async with project_client:
            agent_definition = PromptAgentDefinition(
                # Required parameter
                model=model,
                # Optional parameters
                instructions="You are a helpful AI assistant. Always be polite and provide accurate information.",
                # temperature=0.7,
                # top_p=0.9,
                # # Reasoning configuration
                # reasoning=Reasoning(
                #     effort="medium",
                #     summary="auto",
                # ),
                # # Tools that the model can use
                # tools=[
                #     # Function tool for custom functions
                #     FunctionTool(
                #         name="get_weather",
                #         description="Get the current weather for a location",
                #         parameters={
                #             "type": "object",
                #             "properties": {
                #                 "location": {
                #                     "type": "string",
                #                     "description": "The city and state, e.g. San Francisco, CA",
                #                 },
                #                 "unit": {
                #                     "type": "string",
                #                     "enum": ["celsius", "fahrenheit"],
                #                     "description": "The temperature unit",
                #                 },
                #             },
                #             "required": ["location"],
                #         },
                #         strict=True,  # Enforce strict parameter validation
                #     ),
                # ],
                # # Text response configuration
                # text=PromptAgentDefinitionText(format=ResponseTextFormatConfigurationText()),
            )

            agent = await project_client.agents.create_version(agent_name="myagent", definition=agent_definition)
            version = agent.version
            await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

        # ------------------------- Validate "create_agent" span ---------------------------------
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name("create_agent myagent")
        assert len(spans) == 1
        span = spans[0]
        expected_attributes = [
            ("gen_ai.system", "az.ai.agents"),
            ("gen_ai.provider.name", "azure.ai.agents"),
            ("gen_ai.operation.name", "create_agent"),
            ("server.address", ""),
            ("gen_ai.request.model", model),
            # ("gen_ai.request.temperature", "0.7"),
            # ("gen_ai.request.top_p", "0.9"),
            # ("gen_ai.request.response_format", "text"),
            # ("gen_ai.request.reasoning.effort", "medium"),
            # ("gen_ai.request.reasoning.summary", "auto"),
            ("gen_ai.agent.name", "myagent"),
            ("gen_ai.agent.id", "myagent:" + str(version)),
            ("gen_ai.agent.version", str(version)),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        expected_events = [
            {
                "name": "gen_ai.system.instruction",
                "attributes": {
                    "gen_ai.system": "az.ai.agents",
                    "gen_ai.event.content": '{"text": "You are a helpful AI assistant. Always be polite and provide accurate information."}',
                },
            }
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_agent_creation_with_tracing_content_recording_disabled(self, **kwargs):
        self.cleanup()
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "False"})
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        project_client = self.create_async_client(operation_group="agents", **kwargs)
        model = self.test_agents_params["model_deployment_name"]

        async with project_client:
            agent_definition = PromptAgentDefinition(
                # Required parameter
                model=model,
                # Optional parameters
                instructions="You are a helpful AI assistant. Always be polite and provide accurate information.",
                # temperature=0.7,
                # top_p=0.9,
                # # Reasoning configuration
                # reasoning=Reasoning(
                #     effort="medium",
                #     summary="auto",
                # ),
                # # Tools that the model can use
                # tools=[
                #     # Function tool for custom functions
                #     FunctionTool(
                #         name="get_weather",
                #         description="Get the current weather for a location",
                #         parameters={
                #             "type": "object",
                #             "properties": {
                #                 "location": {
                #                     "type": "string",
                #                     "description": "The city and state, e.g. San Francisco, CA",
                #                 },
                #                 "unit": {
                #                     "type": "string",
                #                     "enum": ["celsius", "fahrenheit"],
                #                     "description": "The temperature unit",
                #                 },
                #             },
                #             "required": ["location"],
                #         },
                #         strict=True,  # Enforce strict parameter validation
                #     ),
                # ],
                # # Text response configuration
                # text=PromptAgentDefinitionText(format=ResponseTextFormatConfigurationText()),
            )

            agent = await project_client.agents.create_version(agent_name="myagent", definition=agent_definition)
            version = agent.version
            await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

        # ------------------------- Validate "create_agent" span ---------------------------------
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name("create_agent myagent")
        assert len(spans) == 1
        span = spans[0]
        expected_attributes = [
            ("gen_ai.system", "az.ai.agents"),
            ("gen_ai.provider.name", "azure.ai.agents"),
            ("gen_ai.operation.name", "create_agent"),
            ("server.address", ""),
            ("gen_ai.request.model", model),
            # ("gen_ai.request.temperature", "0.7"),
            # ("gen_ai.request.top_p", "0.9"),
            # ("gen_ai.request.response_format", "text"),
            # ("gen_ai.request.reasoning.effort", "medium"),
            # ("gen_ai.request.reasoning.summary", "auto"),
            ("gen_ai.agent.name", "myagent"),
            ("gen_ai.agent.id", "myagent:" + str(version)),
            ("gen_ai.agent.version", str(version)),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        expected_events = [
            {
                "name": "gen_ai.system.instruction",
                "attributes": {
                    "gen_ai.system": "az.ai.agents",
                    "gen_ai.event.content": "{}",
                },
            }
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True
