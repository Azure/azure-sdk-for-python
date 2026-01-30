# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable# cSpell:disable
import pytest
import os
from typing import Optional
from azure.ai.projects.telemetry import AIProjectInstrumentor, _utils
from azure.core.settings import settings
from gen_ai_trace_verifier import GenAiTraceVerifier
from azure.ai.projects.models import PromptAgentDefinition, PromptAgentDefinitionText

from azure.ai.projects.models import (
    Reasoning,
    FunctionTool,
    # ResponseTextFormatConfigurationText,
)
from devtools_testutils import (
    recorded_by_proxy,
)

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

    @pytest.fixture(scope="function")
    def instrument_with_content(self):
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "True"})
        self.setup_telemetry()
        yield
        self.cleanup()

    @pytest.fixture(scope="function")
    def instrument_without_content(self):
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "False"})
        self.setup_telemetry()
        yield
        self.cleanup()

    def test_instrumentation(self, **kwargs):
        # Make sure code is not instrumented due to a previous test exception
        AIProjectInstrumentor().uninstrument()
        exception_caught = False
        try:
            assert AIProjectInstrumentor().is_instrumented() == False
            AIProjectInstrumentor().instrument()
            assert AIProjectInstrumentor().is_instrumented() == True
            AIProjectInstrumentor().uninstrument()
            assert AIProjectInstrumentor().is_instrumented() == False
        except RuntimeError as e:
            exception_caught = True
            print(e)
        assert exception_caught == False

    def test_instrumenting_twice_does_not_cause_exception(self, **kwargs):
        # Make sure code is not instrumented due to a previous test exception
        AIProjectInstrumentor().uninstrument()
        exception_caught = False
        try:
            AIProjectInstrumentor().instrument()
            AIProjectInstrumentor().instrument()
        except RuntimeError as e:
            exception_caught = True
            print(e)
        AIProjectInstrumentor().uninstrument()
        assert exception_caught == False

    def test_uninstrumenting_uninstrumented_does_not_cause_exception(self, **kwargs):
        # Make sure code is not instrumented due to a previous test exception
        AIProjectInstrumentor().uninstrument()
        exception_caught = False
        try:
            AIProjectInstrumentor().uninstrument()
        except RuntimeError as e:
            exception_caught = True
            print(e)
        assert exception_caught == False

    def test_uninstrumenting_twice_does_not_cause_exception(self, **kwargs):
        # Make sure code is not instrumented due to a previous test exception
        AIProjectInstrumentor().uninstrument()
        exception_caught = False
        try:
            AIProjectInstrumentor().instrument()
            AIProjectInstrumentor().uninstrument()
            AIProjectInstrumentor().uninstrument()
        except RuntimeError as e:
            exception_caught = True
            print(e)
        assert exception_caught == False

    @pytest.mark.parametrize(
        "env1, env2, expected",
        [
            (None, None, False),
            (None, False, False),
            (None, True, False),
            (False, None, False),
            (False, False, False),
            (False, True, False),
            (True, None, True),
            (True, False, True),
            (True, True, True),
        ],
    )
    def test_content_recording_verify_old_env_variable_ignored(
        self, env1: Optional[bool], env2: Optional[bool], expected: bool
    ):
        """
        Test content recording enablement with both old and new environment variables.
        This test verifies the behavior of content recording when both the current
        and legacy environment variables are set to different combinations of values.
        The method tests all possible combinations of None, True, and False for both
        environment variables to ensure the old one is no longer having impact, since
        support for it has been dropped.
        Args:
            env1: Value for the current content tracing environment variable.
                  Can be None (unset), True, or False.
            env2: Value for the old/legacy content tracing environment variable.
                  Can be None (unset), True, or False.
            expected: The expected result of is_content_recording_enabled() given
                      the environment variable combination.
        The test ensures that only if one or both of the environment variables are
        defined and set to "true" content recording is enabled.
        """

        OLD_CONTENT_TRACING_ENV_VARIABLE = "AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED"  # Deprecated, undocumented.

        def set_env_var(var_name, value):
            if value is None:
                os.environ.pop(var_name, None)
            else:
                os.environ[var_name] = "true" if value else "false"

        set_env_var(CONTENT_TRACING_ENV_VARIABLE, env1)
        set_env_var(OLD_CONTENT_TRACING_ENV_VARIABLE, env2)

        self.setup_telemetry()
        try:
            assert AIProjectInstrumentor().is_content_recording_enabled() == expected
        finally:
            self.cleanup()  # This also undefines CONTENT_TRACING_ENV_VARIABLE
            os.environ.pop(OLD_CONTENT_TRACING_ENV_VARIABLE, None)

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy
    def test_agent_creation_with_tracing_content_recording_enabled(self, **kwargs):
        self.cleanup()
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "True"})
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:

            model = kwargs.get("azure_ai_model_deployment_name")
            print(f"Using model deployment: {model}")

            agent_definition = PromptAgentDefinition(
                # Required parameter
                model=model,
                # Optional parameters
                instructions="You are a helpful AI assistant. Be polite and provide accurate information.",
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
                #                 "location": {"type": "string", "description": "The city and state, e.g. San Francisco, CA"},
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

            agent = project_client.agents.create_version(agent_name="myagent", definition=agent_definition)
            version = agent.version

            # delete agent and close client
            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print("Deleted agent")

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
                    GEN_AI_EVENT_CONTENT: '[{"type": "text", "content": "You are a helpful AI assistant. Be polite and provide accurate information."}]',
                },
            }
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy
    def test_agent_creation_with_tracing_content_recording_disabled(self, **kwargs):
        self.cleanup()
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "False"})
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="agents", **kwargs) as project_client:

            model = kwargs.get("azure_ai_model_deployment_name")
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
                #                 "location": {"type": "string", "description": "The city and state, e.g. San Francisco, CA"},
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
                # Text response configuration
                # text=PromptAgentDefinitionText(format=ResponseTextFormatConfigurationText()),
            )

            agent = project_client.agents.create_version(agent_name="myagent", definition=agent_definition)
            version = agent.version

            # delete agent and close client
            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print("Deleted agent")

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
    @recorded_by_proxy
    def test_workflow_agent_creation_with_tracing_content_recording_enabled(self, **kwargs):
        """Test workflow agent creation with content recording enabled."""
        self.cleanup()
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "True"})
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        from azure.ai.projects.models import WorkflowAgentDefinition

        with self.create_client(operation_group="tracing", **kwargs) as project_client:

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

            agent = project_client.agents.create_version(
                agent_name="test-workflow-agent",
                definition=WorkflowAgentDefinition(workflow=workflow_yaml),
            )
            version = agent.version

            # delete agent
            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print("Deleted workflow agent")

        # ------------------------- Validate "create_agent" span ---------------------------------
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name("create_agent test-workflow-agent")
        assert len(spans) == 1
        span = spans[0]
        expected_attributes = [
            (GEN_AI_PROVIDER_NAME, AZURE_AI_AGENTS_PROVIDER),
            (GEN_AI_OPERATION_NAME, "create_agent"),
            (SERVER_ADDRESS, ""),
            (GEN_AI_AGENT_NAME, "test-workflow-agent"),
            (GEN_AI_AGENT_ID, "test-workflow-agent:" + str(version)),
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
    @recorded_by_proxy
    def test_workflow_agent_creation_with_tracing_content_recording_disabled(self, **kwargs):
        """Test workflow agent creation with content recording disabled."""
        self.cleanup()
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "False"})
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        from azure.ai.projects.models import WorkflowAgentDefinition

        with self.create_client(operation_group="agents", **kwargs) as project_client:

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

            agent = project_client.agents.create_version(
                agent_name="test-workflow-agent",
                definition=WorkflowAgentDefinition(workflow=workflow_yaml),
            )
            version = agent.version

            # delete agent
            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print("Deleted workflow agent")

        # ------------------------- Validate "create_agent" span ---------------------------------
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name("create_agent test-workflow-agent")
        assert len(spans) == 1
        span = spans[0]
        expected_attributes = [
            (GEN_AI_PROVIDER_NAME, AZURE_AI_AGENTS_PROVIDER),
            (GEN_AI_OPERATION_NAME, "create_agent"),
            (SERVER_ADDRESS, ""),
            (GEN_AI_AGENT_NAME, "test-workflow-agent"),
            (GEN_AI_AGENT_ID, "test-workflow-agent:" + str(version)),
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
    @recorded_by_proxy
    def test_agent_with_structured_output_with_instructions_content_recording_enabled(self, **kwargs):
        """Test agent creation with structured output and instructions, content recording enabled."""
        self.cleanup()
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "True"})
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        from azure.ai.projects.models import TextResponseFormatJsonSchema

        with self.create_client(operation_group="tracing", **kwargs) as project_client:

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

            agent = project_client.agents.create_version(agent_name="structured-agent", definition=agent_definition)
            version = agent.version

            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

        # Validate span
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name("create_agent structured-agent")
        assert len(spans) == 1
        span = spans[0]

        expected_attributes = [
            (GEN_AI_PROVIDER_NAME, AZURE_AI_AGENTS_PROVIDER),
            (GEN_AI_OPERATION_NAME, "create_agent"),
            (SERVER_ADDRESS, ""),
            (GEN_AI_REQUEST_MODEL, model),
            ("gen_ai.request.response_format", "json_schema"),
            (GEN_AI_AGENT_NAME, "structured-agent"),
            (GEN_AI_AGENT_ID, "structured-agent:" + str(version)),
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
    @recorded_by_proxy
    def test_agent_with_structured_output_with_instructions_content_recording_disabled(self, **kwargs):
        """Test agent creation with structured output and instructions, content recording disabled."""
        self.cleanup()
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "False"})
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        from azure.ai.projects.models import TextResponseFormatJsonSchema

        with self.create_client(operation_group="agents", **kwargs) as project_client:

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

            agent = project_client.agents.create_version(agent_name="structured-agent", definition=agent_definition)
            version = agent.version

            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

        # Validate span
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name("create_agent structured-agent")
        assert len(spans) == 1
        span = spans[0]

        expected_attributes = [
            (GEN_AI_PROVIDER_NAME, AZURE_AI_AGENTS_PROVIDER),
            (GEN_AI_OPERATION_NAME, "create_agent"),
            (SERVER_ADDRESS, ""),
            (GEN_AI_REQUEST_MODEL, model),
            ("gen_ai.request.response_format", "json_schema"),
            (GEN_AI_AGENT_NAME, "structured-agent"),
            (GEN_AI_AGENT_ID, "structured-agent:" + str(version)),
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
    @recorded_by_proxy
    def test_agent_with_structured_output_without_instructions_content_recording_enabled(self, **kwargs):
        """Test agent creation with structured output but NO instructions, content recording enabled."""
        self.cleanup()
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "True"})
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        from azure.ai.projects.models import TextResponseFormatJsonSchema

        with self.create_client(operation_group="tracing", **kwargs) as project_client:

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

            agent = project_client.agents.create_version(
                agent_name="no-instructions-agent", definition=agent_definition
            )
            version = agent.version

            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

        # Validate span
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name("create_agent no-instructions-agent")
        assert len(spans) == 1
        span = spans[0]

        expected_attributes = [
            (GEN_AI_PROVIDER_NAME, AZURE_AI_AGENTS_PROVIDER),
            (GEN_AI_OPERATION_NAME, "create_agent"),
            (SERVER_ADDRESS, ""),
            (GEN_AI_REQUEST_MODEL, model),
            ("gen_ai.request.response_format", "json_schema"),
            (GEN_AI_AGENT_NAME, "no-instructions-agent"),
            (GEN_AI_AGENT_ID, "no-instructions-agent:" + str(version)),
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
    @recorded_by_proxy
    def test_agent_with_structured_output_without_instructions_content_recording_disabled(self, **kwargs):
        """Test agent creation with structured output but NO instructions, content recording disabled."""
        self.cleanup()
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "False"})
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        from azure.ai.projects.models import TextResponseFormatJsonSchema

        with self.create_client(operation_group="agents", **kwargs) as project_client:

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

            agent = project_client.agents.create_version(
                agent_name="no-instructions-agent", definition=agent_definition
            )
            version = agent.version

            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

        # Validate span
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name("create_agent no-instructions-agent")
        assert len(spans) == 1
        span = spans[0]

        expected_attributes = [
            (GEN_AI_PROVIDER_NAME, AZURE_AI_AGENTS_PROVIDER),
            (GEN_AI_OPERATION_NAME, "create_agent"),
            (SERVER_ADDRESS, ""),
            (GEN_AI_REQUEST_MODEL, model),
            ("gen_ai.request.response_format", "json_schema"),
            (GEN_AI_AGENT_NAME, "no-instructions-agent"),
            (GEN_AI_AGENT_ID, "no-instructions-agent:" + str(version)),
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
