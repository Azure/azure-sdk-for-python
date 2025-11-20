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
    ResponseTextFormatConfigurationText,
)
from devtools_testutils import (
    recorded_by_proxy,
)

from test_base import servicePreparer
from test_ai_instrumentor_base import TestAiAgentsInstrumentorBase, MessageCreationMode, CONTENT_TRACING_ENV_VARIABLE

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

            model = self.test_agents_params["model_deployment_name"]
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
            ("gen_ai.agent.type", "prompt"),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        expected_events = [
            {
                "name": "gen_ai.system.instruction",
                "attributes": {
                    "gen_ai.system": "az.ai.agents",
                    "gen_ai.event.content": '{"content": [{"type": "text", "text": "You are a helpful AI assistant. Be polite and provide accurate information."}]}',
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

            model = self.test_agents_params["model_deployment_name"]
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
            ("gen_ai.agent.type", "prompt"),
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
            ("gen_ai.system", "az.ai.agents"),
            ("gen_ai.provider.name", "azure.ai.agents"),
            ("gen_ai.operation.name", "create_agent"),
            ("server.address", ""),
            ("gen_ai.agent.name", "test-workflow-agent"),
            ("gen_ai.agent.id", "test-workflow-agent:" + str(version)),
            ("gen_ai.agent.version", str(version)),
            ("gen_ai.agent.type", "workflow"),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        # Verify workflow event with standard content format
        events = span.events
        assert len(events) == 1
        workflow_event = events[0]
        assert workflow_event.name == "gen_ai.agent.workflow"

        import json

        event_content = json.loads(workflow_event.attributes["gen_ai.event.content"])
        assert "content" in event_content
        assert len(event_content["content"]) == 1
        assert event_content["content"][0]["type"] == "workflow"
        assert "workflow" in event_content["content"][0]
        assert "kind: workflow" in event_content["content"][0]["workflow"]

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
            ("gen_ai.system", "az.ai.agents"),
            ("gen_ai.provider.name", "azure.ai.agents"),
            ("gen_ai.operation.name", "create_agent"),
            ("server.address", ""),
            ("gen_ai.agent.name", "test-workflow-agent"),
            ("gen_ai.agent.id", "test-workflow-agent:" + str(version)),
            ("gen_ai.agent.version", str(version)),
            ("gen_ai.agent.type", "workflow"),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        # Verify no workflow event when content recording is disabled
        events = span.events
        assert len(events) == 0
