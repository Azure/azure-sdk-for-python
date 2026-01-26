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
    # ResponseTextFormatConfigurationText,
)

from devtools_testutils.aio import recorded_by_proxy_async

from test_base import servicePreparer
from test_ai_instrumentor_base import (
    TestAiAgentsInstrumentorBase,
    MessageCreationMode,
    CONTENT_TRACING_ENV_VARIABLE,
)

from azure.ai.projects.telemetry._utils import (
    AZ_NAMESPACE,
    AZ_NAMESPACE_VALUE,
    GEN_AI_AGENT_ID,
    GEN_AI_AGENT_NAME,
    GEN_AI_AGENT_VERSION,
    GEN_AI_CONVERSATION_ID,
    GEN_AI_EVENT_CONTENT,
    GEN_AI_OPERATION_NAME,
    GEN_AI_PROVIDER_NAME,
    GEN_AI_REQUEST_MODEL,
    GEN_AI_RESPONSE_FINISH_REASONS,
    GEN_AI_RESPONSE_ID,
    GEN_AI_RESPONSE_MODEL,
    GEN_AI_SYSTEM,
    GEN_AI_USAGE_INPUT_TOKENS,
    GEN_AI_USAGE_OUTPUT_TOKENS,
    SERVER_ADDRESS,
    GEN_AI_AGENT_TYPE,
    GEN_AI_SYSTEM_INSTRUCTION_EVENT,
    GEN_AI_AGENT_WORKFLOW_EVENT,
    GEN_AI_CONVERSATION_ITEM_TYPE,
    AZURE_AI_AGENTS_SYSTEM,
    AZURE_AI_AGENTS_PROVIDER,
    AGENT_TYPE_PROMPT,
    AGENT_TYPE_WORKFLOW,
)

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
        model = kwargs.get("azure_ai_model_deployment_name")

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
            (GEN_AI_PROVIDER_NAME, AZURE_AI_AGENTS_PROVIDER),
            (GEN_AI_OPERATION_NAME, "create_agent"),
            (SERVER_ADDRESS, ""),
            (GEN_AI_REQUEST_MODEL, model),
            # ("gen_ai.request.temperature", "0.7"),
            # ("gen_ai.request.top_p", "0.9"),
            # ("gen_ai.request.response_format", "text"),
            # ("gen_ai.request.reasoning.effort", "medium"),
            # ("gen_ai.request.reasoning.summary", "auto"),
            (GEN_AI_AGENT_NAME, "myagent"),
            (GEN_AI_AGENT_ID, "myagent:" + str(version)),
            (GEN_AI_AGENT_VERSION, str(version)),
            (GEN_AI_AGENT_TYPE, AGENT_TYPE_PROMPT),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        expected_events = [
            {
                "name": GEN_AI_SYSTEM_INSTRUCTION_EVENT,
                "attributes": {
                    GEN_AI_PROVIDER_NAME: AZURE_AI_AGENTS_PROVIDER,
                    GEN_AI_EVENT_CONTENT: '[{"type": "text", "content": "You are a helpful AI assistant. Always be polite and provide accurate information."}]',
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
        model = kwargs.get("azure_ai_model_deployment_name")

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
            (GEN_AI_PROVIDER_NAME, AZURE_AI_AGENTS_PROVIDER),
            (GEN_AI_OPERATION_NAME, "create_agent"),
            (SERVER_ADDRESS, ""),
            (GEN_AI_REQUEST_MODEL, model),
            # ("gen_ai.request.temperature", "0.7"),
            # ("gen_ai.request.top_p", "0.9"),
            # ("gen_ai.request.response_format", "text"),
            # ("gen_ai.request.reasoning.effort", "medium"),
            # ("gen_ai.request.reasoning.summary", "auto"),
            (GEN_AI_AGENT_NAME, "myagent"),
            (GEN_AI_AGENT_ID, "myagent:" + str(version)),
            (GEN_AI_AGENT_VERSION, str(version)),
            (GEN_AI_AGENT_TYPE, AGENT_TYPE_PROMPT),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        expected_events = [
            {
                "name": GEN_AI_SYSTEM_INSTRUCTION_EVENT,
                "attributes": {
                    GEN_AI_PROVIDER_NAME: AZURE_AI_AGENTS_PROVIDER,
                    GEN_AI_EVENT_CONTENT: "[]",
                },
            }
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_workflow_agent_creation_with_tracing_content_recording_enabled(self, **kwargs):
        """Test workflow agent creation with content recording enabled (async)."""
        self.cleanup()
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "True"})
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        from azure.ai.projects.models import WorkflowAgentDefinition

        project_client = self.create_async_client(operation_group="tracing", **kwargs)

        async with project_client:
            workflow_yaml = """
kind: workflow
trigger:
  kind: OnConversationStart
  id: test_workflow
  actions:
    - kind: SetVariable
      id: set_variable
      variable: Local.TestVar
      value: "test"
"""

            agent = await project_client.agents.create_version(
                agent_name="test-workflow-agent-async",
                definition=WorkflowAgentDefinition(workflow=workflow_yaml),
            )
            version = agent.version

            # delete agent
            await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

        # ------------------------- Validate "create_agent" span ---------------------------------
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name("create_agent test-workflow-agent-async")
        assert len(spans) == 1
        span = spans[0]
        expected_attributes = [
            (GEN_AI_PROVIDER_NAME, AZURE_AI_AGENTS_PROVIDER),
            (GEN_AI_OPERATION_NAME, "create_agent"),
            (SERVER_ADDRESS, ""),
            (GEN_AI_AGENT_NAME, "test-workflow-agent-async"),
            (GEN_AI_AGENT_ID, "test-workflow-agent-async:" + str(version)),
            (GEN_AI_AGENT_VERSION, str(version)),
            (GEN_AI_AGENT_TYPE, AGENT_TYPE_WORKFLOW),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        # Verify workflow event with standard content format
        events = span.events
        assert len(events) == 1
        workflow_event = events[0]
        assert workflow_event.name == GEN_AI_AGENT_WORKFLOW_EVENT

        import json

        event_content = json.loads(workflow_event.attributes[GEN_AI_EVENT_CONTENT])
        # New optimized format: direct array with "content" field for workflow YAML
        assert isinstance(event_content, list)
        assert len(event_content) == 1
        assert event_content[0]["type"] == "workflow"
        assert "content" in event_content[0]
        assert "kind: workflow" in event_content[0]["content"]

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_workflow_agent_creation_with_tracing_content_recording_disabled(self, **kwargs):
        """Test workflow agent creation with content recording disabled (async)."""
        self.cleanup()
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "False"})
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        from azure.ai.projects.models import WorkflowAgentDefinition

        project_client = self.create_async_client(operation_group="agents", **kwargs)

        async with project_client:
            workflow_yaml = """
kind: workflow
trigger:
  kind: OnConversationStart
  id: test_workflow
  actions:
    - kind: SetVariable
      id: set_variable
      variable: Local.TestVar
      value: "test"
"""

            agent = await project_client.agents.create_version(
                agent_name="test-workflow-agent-async",
                definition=WorkflowAgentDefinition(workflow=workflow_yaml),
            )
            version = agent.version

            # delete agent
            await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

        # ------------------------- Validate "create_agent" span ---------------------------------
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name("create_agent test-workflow-agent-async")
        assert len(spans) == 1
        span = spans[0]
        expected_attributes = [
            (GEN_AI_PROVIDER_NAME, AZURE_AI_AGENTS_PROVIDER),
            (GEN_AI_OPERATION_NAME, "create_agent"),
            (SERVER_ADDRESS, ""),
            (GEN_AI_AGENT_NAME, "test-workflow-agent-async"),
            (GEN_AI_AGENT_ID, "test-workflow-agent-async:" + str(version)),
            (GEN_AI_AGENT_VERSION, str(version)),
            (GEN_AI_AGENT_TYPE, AGENT_TYPE_WORKFLOW),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        # Verify workflow event is present but content is empty when content recording is disabled
        events = span.events
        assert len(events) == 1
        workflow_event = events[0]
        assert workflow_event.name == GEN_AI_AGENT_WORKFLOW_EVENT

        import json

        event_content = json.loads(workflow_event.attributes[GEN_AI_EVENT_CONTENT])
        # When content recording is disabled, event should be an empty array
        assert isinstance(event_content, list)
        assert len(event_content) == 0

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_agent_with_structured_output_with_instructions_content_recording_enabled(self, **kwargs):
        """Test agent creation with structured output and instructions, content recording enabled (async)."""
        self.cleanup()
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "True"})
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        from azure.ai.projects.models import TextResponseFormatJsonSchema

        project_client = self.create_async_client(operation_group="tracing", **kwargs)

        async with project_client:
            model = kwargs.get("azure_ai_model_deployment_name")

            # Define a JSON schema for structured output
            test_schema = {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "number"},
                },
                "required": ["name", "age"],
            }

            agent_definition = PromptAgentDefinition(
                model=model,
                instructions="You are a helpful assistant that extracts person information.",
                text=PromptAgentDefinitionText(
                    format=TextResponseFormatJsonSchema(
                        name="PersonInfo",
                        schema=test_schema,
                    )
                ),
            )

            agent = await project_client.agents.create_version(
                agent_name="structured-agent-async", definition=agent_definition
            )
            version = agent.version

            await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

        # Validate span
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name("create_agent structured-agent-async")
        assert len(spans) == 1
        span = spans[0]

        expected_attributes = [
            (GEN_AI_PROVIDER_NAME, AZURE_AI_AGENTS_PROVIDER),
            (GEN_AI_OPERATION_NAME, "create_agent"),
            (SERVER_ADDRESS, ""),
            (GEN_AI_REQUEST_MODEL, model),
            ("gen_ai.request.response_format", "json_schema"),
            (GEN_AI_AGENT_NAME, "structured-agent-async"),
            (GEN_AI_AGENT_ID, "structured-agent-async:" + str(version)),
            (GEN_AI_AGENT_VERSION, str(version)),
            (GEN_AI_AGENT_TYPE, AGENT_TYPE_PROMPT),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        # Verify event contains both instructions and schema
        events = span.events
        assert len(events) == 1
        instruction_event = events[0]
        assert instruction_event.name == GEN_AI_SYSTEM_INSTRUCTION_EVENT

        import json

        event_content = json.loads(instruction_event.attributes[GEN_AI_EVENT_CONTENT])
        assert isinstance(event_content, list)
        assert len(event_content) == 2  # Both instructions and schema

        # Check instructions content
        assert event_content[0]["type"] == "text"
        assert "helpful assistant" in event_content[0]["content"]

        # Check schema content
        assert event_content[1]["type"] == "response_schema"
        schema_str = event_content[1]["content"]
        schema_obj = json.loads(schema_str)
        assert schema_obj["type"] == "object"
        assert "name" in schema_obj["properties"]
        assert "age" in schema_obj["properties"]

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_agent_with_structured_output_with_instructions_content_recording_disabled(self, **kwargs):
        """Test agent creation with structured output and instructions, content recording disabled (async)."""
        self.cleanup()
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "False"})
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        from azure.ai.projects.models import TextResponseFormatJsonSchema

        project_client = self.create_async_client(operation_group="agents", **kwargs)

        async with project_client:
            model = kwargs.get("azure_ai_model_deployment_name")

            test_schema = {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "number"},
                },
                "required": ["name", "age"],
            }

            agent_definition = PromptAgentDefinition(
                model=model,
                instructions="You are a helpful assistant that extracts person information.",
                text=PromptAgentDefinitionText(
                    format=TextResponseFormatJsonSchema(
                        name="PersonInfo",
                        schema=test_schema,
                    )
                ),
            )

            agent = await project_client.agents.create_version(
                agent_name="structured-agent-async", definition=agent_definition
            )
            version = agent.version

            await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

        # Validate span
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name("create_agent structured-agent-async")
        assert len(spans) == 1
        span = spans[0]

        expected_attributes = [
            (GEN_AI_PROVIDER_NAME, AZURE_AI_AGENTS_PROVIDER),
            (GEN_AI_OPERATION_NAME, "create_agent"),
            (SERVER_ADDRESS, ""),
            (GEN_AI_REQUEST_MODEL, model),
            ("gen_ai.request.response_format", "json_schema"),
            (GEN_AI_AGENT_NAME, "structured-agent-async"),
            (GEN_AI_AGENT_ID, "structured-agent-async:" + str(version)),
            (GEN_AI_AGENT_VERSION, str(version)),
            (GEN_AI_AGENT_TYPE, AGENT_TYPE_PROMPT),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        # When content recording is disabled, event should be empty
        events = span.events
        assert len(events) == 1
        instruction_event = events[0]
        assert instruction_event.name == GEN_AI_SYSTEM_INSTRUCTION_EVENT

        import json

        event_content = json.loads(instruction_event.attributes[GEN_AI_EVENT_CONTENT])
        assert isinstance(event_content, list)
        assert len(event_content) == 0  # Empty when content recording disabled

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_agent_with_structured_output_without_instructions_content_recording_enabled(self, **kwargs):
        """Test agent creation with structured output but NO instructions, content recording enabled (async)."""
        self.cleanup()
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "True"})
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        from azure.ai.projects.models import TextResponseFormatJsonSchema

        project_client = self.create_async_client(operation_group="tracing", **kwargs)

        async with project_client:
            model = kwargs.get("azure_ai_model_deployment_name")

            test_schema = {
                "type": "object",
                "properties": {
                    "result": {"type": "string"},
                },
                "required": ["result"],
            }

            agent_definition = PromptAgentDefinition(
                model=model,
                # No instructions provided
                text=PromptAgentDefinitionText(
                    format=TextResponseFormatJsonSchema(
                        name="Result",
                        schema=test_schema,
                    )
                ),
            )

            agent = await project_client.agents.create_version(
                agent_name="no-instructions-agent-async", definition=agent_definition
            )
            version = agent.version

            await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

        # Validate span
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name("create_agent no-instructions-agent-async")
        assert len(spans) == 1
        span = spans[0]

        expected_attributes = [
            (GEN_AI_PROVIDER_NAME, AZURE_AI_AGENTS_PROVIDER),
            (GEN_AI_OPERATION_NAME, "create_agent"),
            (SERVER_ADDRESS, ""),
            (GEN_AI_REQUEST_MODEL, model),
            ("gen_ai.request.response_format", "json_schema"),
            (GEN_AI_AGENT_NAME, "no-instructions-agent-async"),
            (GEN_AI_AGENT_ID, "no-instructions-agent-async:" + str(version)),
            (GEN_AI_AGENT_VERSION, str(version)),
            (GEN_AI_AGENT_TYPE, AGENT_TYPE_PROMPT),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        # Event should be created with just the schema (no instructions)
        events = span.events
        assert len(events) == 1
        instruction_event = events[0]
        assert instruction_event.name == GEN_AI_SYSTEM_INSTRUCTION_EVENT

        import json

        event_content = json.loads(instruction_event.attributes[GEN_AI_EVENT_CONTENT])
        assert isinstance(event_content, list)
        assert len(event_content) == 1  # Only schema, no instructions

        # Check schema content
        assert event_content[0]["type"] == "response_schema"
        schema_str = event_content[0]["content"]
        schema_obj = json.loads(schema_str)
        assert schema_obj["type"] == "object"
        assert "result" in schema_obj["properties"]

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_agent_with_structured_output_without_instructions_content_recording_disabled(self, **kwargs):
        """Test agent creation with structured output but NO instructions, content recording disabled (async)."""
        self.cleanup()
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "False"})
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        from azure.ai.projects.models import TextResponseFormatJsonSchema

        project_client = self.create_async_client(operation_group="agents", **kwargs)

        async with project_client:
            model = kwargs.get("azure_ai_model_deployment_name")

            test_schema = {
                "type": "object",
                "properties": {
                    "result": {"type": "string"},
                },
                "required": ["result"],
            }

            agent_definition = PromptAgentDefinition(
                model=model,
                # No instructions provided
                text=PromptAgentDefinitionText(
                    format=TextResponseFormatJsonSchema(
                        name="Result",
                        schema=test_schema,
                    )
                ),
            )

            agent = await project_client.agents.create_version(
                agent_name="no-instructions-agent-async", definition=agent_definition
            )
            version = agent.version

            await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

        # Validate span
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name("create_agent no-instructions-agent-async")
        assert len(spans) == 1
        span = spans[0]

        expected_attributes = [
            (GEN_AI_PROVIDER_NAME, AZURE_AI_AGENTS_PROVIDER),
            (GEN_AI_OPERATION_NAME, "create_agent"),
            (SERVER_ADDRESS, ""),
            (GEN_AI_REQUEST_MODEL, model),
            ("gen_ai.request.response_format", "json_schema"),
            (GEN_AI_AGENT_NAME, "no-instructions-agent-async"),
            (GEN_AI_AGENT_ID, "no-instructions-agent-async:" + str(version)),
            (GEN_AI_AGENT_VERSION, str(version)),
            (GEN_AI_AGENT_TYPE, AGENT_TYPE_PROMPT),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        # Event should be created with empty content due to content recording disabled
        events = span.events
        assert len(events) == 1
        instruction_event = events[0]
        assert instruction_event.name == GEN_AI_SYSTEM_INSTRUCTION_EVENT

        import json

        event_content = json.loads(instruction_event.attributes[GEN_AI_EVENT_CONTENT])
        assert isinstance(event_content, list)
        assert len(event_content) == 0  # Empty because content recording is disabled
