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
from azure.ai.projects.models import PromptAgentDefinition, PromptAgentDefinitionTextOptions
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
    AGENTS_PROVIDER,
    AGENT_TYPE_PROMPT,
    AGENT_TYPE_WORKFLOW,
    _set_use_message_events,
)

settings.tracing_implementation = "OpenTelemetry"
_utils._span_impl_type = settings.tracing_implementation()


@pytest.mark.skip(
    reason="Skipped until re-enabled and recorded on Foundry endpoint that supports the new versioning schema"
)
class TestAiAgentsInstrumentor(TestAiAgentsInstrumentorBase):
    """Tests for AI agents instrumentor."""

    async def _test_create_agent_with_tracing_content_recording_enabled_impl(self, use_events: bool, **kwargs):
        """Implementation for agent creation with content recording enabled test (async).

        :param use_events: If True, use events for messages. If False, use attributes.
        :type use_events: bool
        """
        self.cleanup()
        _set_use_message_events(use_events)
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "True"})
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        model = kwargs.get("azure_ai_model_deployment_name")

        async with project_client:
            agent_definition = PromptAgentDefinition(
                model=model,
                instructions="You are a helpful AI assistant. Always be polite and provide accurate information.",
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
            (GEN_AI_PROVIDER_NAME, AGENTS_PROVIDER),
            (GEN_AI_OPERATION_NAME, "create_agent"),
            (SERVER_ADDRESS, ""),
            (GEN_AI_REQUEST_MODEL, model),
            (GEN_AI_AGENT_NAME, "myagent"),
            (GEN_AI_AGENT_ID, "myagent:" + str(version)),
            (GEN_AI_AGENT_VERSION, str(version)),
            (GEN_AI_AGENT_TYPE, AGENT_TYPE_PROMPT),
        ]

        # When using attributes, add the system instructions attribute to expected list
        if not use_events:
            from azure.ai.projects.telemetry._utils import GEN_AI_SYSTEM_MESSAGE
            import json

            # The system message should be a JSON array of content objects

            expected_system_message = json.dumps(
                [
                    {
                        "type": "text",
                        "content": "You are a helpful AI assistant. Always be polite and provide accurate information.",
                    }
                ],
                ensure_ascii=False,
            )
            expected_attributes.append((GEN_AI_SYSTEM_MESSAGE, expected_system_message))

        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        if use_events:
            expected_events = [
                {
                    "name": GEN_AI_SYSTEM_INSTRUCTION_EVENT,
                    "attributes": {
                        GEN_AI_PROVIDER_NAME: AGENTS_PROVIDER,
                        GEN_AI_EVENT_CONTENT: '[{"type": "text", "content": "You are a helpful AI assistant. Always be polite and provide accurate information."}]',
                    },
                }
            ]
            events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
            assert events_match == True
        else:
            # When using attributes, check for gen_ai.system.instructions attribute
            from azure.ai.projects.telemetry._utils import GEN_AI_SYSTEM_MESSAGE
            import json

            assert span.attributes is not None
            assert GEN_AI_SYSTEM_MESSAGE in span.attributes

            system_message_json = span.attributes[GEN_AI_SYSTEM_MESSAGE]
            system_message = json.loads(system_message_json)

            # Verify structure
            assert isinstance(system_message, list)
            assert len(system_message) == 1
            assert system_message[0]["type"] == "text"
            assert (
                system_message[0]["content"]
                == "You are a helpful AI assistant. Always be polite and provide accurate information."
            )

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_create_agent_with_tracing_content_recording_enabled(self, **kwargs):
        """Test agent creation with content recording enabled using events (async)."""
        await self._test_create_agent_with_tracing_content_recording_enabled_impl(use_events=True, **kwargs)

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_create_agent_with_tracing_content_recording_enabled_with_attributes(self, **kwargs):
        """Test agent creation with content recording enabled using attributes (async)."""
        await self._test_create_agent_with_tracing_content_recording_enabled_impl(use_events=False, **kwargs)

    async def _test_agent_creation_with_tracing_content_recording_disabled_impl(self, use_events: bool, **kwargs):
        """Implementation for agent creation with content recording disabled test (async).

        :param use_events: If True, use events for messages. If False, use attributes.
        :type use_events: bool
        """
        import json

        self.cleanup()
        _set_use_message_events(use_events)
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "False"})
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        project_client = self.create_async_client(operation_group="agents", **kwargs)
        model = kwargs.get("azure_ai_model_deployment_name")

        async with project_client:
            agent_definition = PromptAgentDefinition(
                model=model,
                instructions="You are a helpful AI assistant. Always be polite and provide accurate information.",
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
            (GEN_AI_PROVIDER_NAME, AGENTS_PROVIDER),
            (GEN_AI_OPERATION_NAME, "create_agent"),
            (SERVER_ADDRESS, ""),
            (GEN_AI_REQUEST_MODEL, model),
            (GEN_AI_AGENT_NAME, "myagent"),
            (GEN_AI_AGENT_ID, "myagent:" + str(version)),
            (GEN_AI_AGENT_VERSION, str(version)),
            (GEN_AI_AGENT_TYPE, AGENT_TYPE_PROMPT),
        ]

        # When using attributes, add empty system message attribute
        if not use_events:
            from azure.ai.projects.telemetry._utils import GEN_AI_SYSTEM_MESSAGE

            # The system message should have type indicator without content when content recording is disabled

            expected_system_message = json.dumps([{"type": "text"}], ensure_ascii=False)
            expected_attributes.append((GEN_AI_SYSTEM_MESSAGE, expected_system_message))

        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        if use_events:
            expected_events = [
                {
                    "name": GEN_AI_SYSTEM_INSTRUCTION_EVENT,
                    "attributes": {
                        GEN_AI_PROVIDER_NAME: AGENTS_PROVIDER,
                        GEN_AI_EVENT_CONTENT: json.dumps([{"type": "text"}]),
                    },
                }
            ]
            events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
            assert events_match == True
        else:
            # When using attributes and content recording disabled, verify empty structure
            from azure.ai.projects.telemetry._utils import GEN_AI_SYSTEM_MESSAGE
            import json

            assert span.attributes is not None
            assert GEN_AI_SYSTEM_MESSAGE in span.attributes

            system_message_json = span.attributes[GEN_AI_SYSTEM_MESSAGE]
            system_message = json.loads(system_message_json)
            # Should have type indicator when content recording is disabled
            assert isinstance(system_message, list)
            assert len(system_message) == 1
            assert system_message[0]["type"] == "text"
            assert "content" not in system_message[0]

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_agent_creation_with_tracing_content_recording_disabled(self, **kwargs):
        """Test agent creation with content recording disabled using events (async)."""
        await self._test_agent_creation_with_tracing_content_recording_disabled_impl(use_events=True, **kwargs)

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_agent_creation_with_tracing_content_recording_disabled_with_attributes(self, **kwargs):
        """Test agent creation with content recording disabled using attributes (async)."""
        await self._test_agent_creation_with_tracing_content_recording_disabled_impl(use_events=False, **kwargs)

    async def _test_workflow_agent_creation_impl(self, use_events: bool, content_recording_enabled: bool, **kwargs):
        """Implementation for workflow agent creation test (async).

        :param use_events: If True, use events for messages. If False, use attributes.
        :type use_events: bool
        :param content_recording_enabled: Whether content recording is enabled.
        :type content_recording_enabled: bool
        """
        self.cleanup()
        _set_use_message_events(use_events)
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "True" if content_recording_enabled else "False"})
        self.setup_telemetry()
        assert content_recording_enabled == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        from azure.ai.projects.models import WorkflowAgentDefinition

        operation_group = "tracing" if content_recording_enabled else "agents"
        project_client = self.create_async_client(operation_group=operation_group, **kwargs)

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

            await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

        # ------------------------- Validate "create_agent" span ---------------------------------
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name("create_agent test-workflow-agent-async")
        assert len(spans) == 1
        span = spans[0]
        expected_attributes = [
            (GEN_AI_PROVIDER_NAME, AGENTS_PROVIDER),
            (GEN_AI_OPERATION_NAME, "create_agent"),
            (SERVER_ADDRESS, ""),
            (GEN_AI_AGENT_NAME, "test-workflow-agent-async"),
            (GEN_AI_AGENT_ID, "test-workflow-agent-async:" + str(version)),
            (GEN_AI_AGENT_VERSION, str(version)),
            (GEN_AI_AGENT_TYPE, AGENT_TYPE_WORKFLOW),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        if use_events:
            # Verify workflow event
            events = span.events
            assert len(events) == 1
            workflow_event = events[0]
            assert workflow_event.name == GEN_AI_AGENT_WORKFLOW_EVENT

            import json

            event_content = json.loads(workflow_event.attributes[GEN_AI_EVENT_CONTENT])
            assert isinstance(event_content, list)

            if content_recording_enabled:
                assert len(event_content) == 1
                assert event_content[0]["type"] == "workflow"
                assert "content" in event_content[0]
                assert "kind: workflow" in event_content[0]["content"]
            else:
                # When content recording is disabled, event should be empty
                assert len(event_content) == 0
        else:
            # When using attributes, workflow events are still sent as events (not attributes)
            events = span.events
            assert len(events) == 1
            workflow_event = events[0]
            assert workflow_event.name == GEN_AI_AGENT_WORKFLOW_EVENT

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_workflow_agent_creation_with_tracing_content_recording_enabled(self, **kwargs):
        """Test workflow agent creation with content recording enabled using events (async)."""
        await self._test_workflow_agent_creation_impl(use_events=True, content_recording_enabled=True, **kwargs)

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_workflow_agent_creation_with_tracing_content_recording_enabled_with_attributes(self, **kwargs):
        """Test workflow agent creation with content recording enabled using attributes (async)."""
        await self._test_workflow_agent_creation_impl(use_events=False, content_recording_enabled=True, **kwargs)

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_workflow_agent_creation_with_tracing_content_recording_disabled(self, **kwargs):
        """Test workflow agent creation with content recording disabled using events (async)."""
        await self._test_workflow_agent_creation_impl(use_events=True, content_recording_enabled=False, **kwargs)

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_workflow_agent_creation_with_tracing_content_recording_disabled_with_attributes(self, **kwargs):
        """Test workflow agent creation with content recording disabled using attributes (async)."""
        await self._test_workflow_agent_creation_impl(use_events=False, content_recording_enabled=False, **kwargs)

    async def _test_agent_with_structured_output_with_instructions_impl(
        self, use_events: bool, content_recording_enabled: bool, **kwargs
    ):
        """Implementation for structured output with instructions test (async).

        :param use_events: If True, use events for messages. If False, use attributes.
        :type use_events: bool
        :param content_recording_enabled: Whether content recording is enabled.
        :type content_recording_enabled: bool
        """
        import json

        self.cleanup()
        _set_use_message_events(use_events)
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "True" if content_recording_enabled else "False"})
        self.setup_telemetry()
        assert content_recording_enabled == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        from azure.ai.projects.models import TextResponseFormatJsonSchema

        operation_group = "tracing" if content_recording_enabled else "agents"
        project_client = self.create_async_client(operation_group=operation_group, **kwargs)

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
                text=PromptAgentDefinitionTextOptions(
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
            (GEN_AI_PROVIDER_NAME, AGENTS_PROVIDER),
            (GEN_AI_OPERATION_NAME, "create_agent"),
            (SERVER_ADDRESS, ""),
            (GEN_AI_REQUEST_MODEL, model),
            ("gen_ai.request.response_format", "json_schema"),
            (GEN_AI_AGENT_NAME, "structured-agent-async"),
            (GEN_AI_AGENT_ID, "structured-agent-async:" + str(version)),
            (GEN_AI_AGENT_VERSION, str(version)),
            (GEN_AI_AGENT_TYPE, AGENT_TYPE_PROMPT),
        ]

        # Add attribute expectation when using attributes mode
        if not use_events:
            from azure.ai.projects.telemetry._utils import GEN_AI_SYSTEM_MESSAGE

            if content_recording_enabled:
                expected_system_message = json.dumps(
                    [
                        {
                            "type": "text",
                            "content": "You are a helpful assistant that extracts person information.",
                        },
                        {"type": "response_schema", "content": json.dumps(test_schema)},
                    ]
                )
            else:
                expected_system_message = json.dumps([{"type": "text"}, {"type": "response_schema"}])
            expected_attributes.append((GEN_AI_SYSTEM_MESSAGE, expected_system_message))

        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        if use_events:
            # Verify event
            events = span.events
            assert len(events) == 1
            instruction_event = events[0]
            assert instruction_event.name == GEN_AI_SYSTEM_INSTRUCTION_EVENT

            event_content = json.loads(instruction_event.attributes[GEN_AI_EVENT_CONTENT])
            assert isinstance(event_content, list)

            if content_recording_enabled:
                assert len(event_content) == 2  # Both instructions and schema
                assert event_content[0]["type"] == "text"
                assert "helpful assistant" in event_content[0]["content"]
                assert event_content[1]["type"] == "response_schema"
                schema_obj = json.loads(event_content[1]["content"])
                assert schema_obj["type"] == "object"
                assert "name" in schema_obj["properties"]
            else:
                # Type indicators without content when content recording disabled
                assert len(event_content) == 2
                assert event_content[0]["type"] == "text"
                assert "content" not in event_content[0]
                assert event_content[1]["type"] == "response_schema"
                assert "content" not in event_content[1]
        else:
            # Validate attribute
            attribute_value = None
            for attr_key, attr_val in span.attributes.items():
                if attr_key == GEN_AI_SYSTEM_MESSAGE:
                    attribute_value = attr_val
                    break
            assert attribute_value is not None

            system_message = json.loads(attribute_value)
            assert isinstance(system_message, list)

            if content_recording_enabled:
                assert len(system_message) == 2
                assert system_message[0]["type"] == "text"
                assert "helpful assistant" in system_message[0]["content"]
                assert system_message[1]["type"] == "response_schema"
                schema_obj = json.loads(system_message[1]["content"])
                assert schema_obj["type"] == "object"
            else:
                # When content recording disabled, type indicators without content
                assert len(system_message) == 2
                assert system_message[0]["type"] == "text"
                assert "content" not in system_message[0]
                assert system_message[1]["type"] == "response_schema"
                assert "content" not in system_message[1]

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_agent_with_structured_output_with_instructions_content_recording_enabled(self, **kwargs):
        """Test agent creation with structured output and instructions, content recording enabled using events (async)."""
        await self._test_agent_with_structured_output_with_instructions_impl(
            use_events=True, content_recording_enabled=True, **kwargs
        )

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_agent_with_structured_output_with_instructions_content_recording_enabled_with_attributes(
        self, **kwargs
    ):
        """Test agent creation with structured output and instructions, content recording enabled using attributes (async)."""
        await self._test_agent_with_structured_output_with_instructions_impl(
            use_events=False, content_recording_enabled=True, **kwargs
        )

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_agent_with_structured_output_with_instructions_content_recording_disabled(self, **kwargs):
        """Test agent creation with structured output and instructions, content recording disabled using events (async)."""
        await self._test_agent_with_structured_output_with_instructions_impl(
            use_events=True, content_recording_enabled=False, **kwargs
        )

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_agent_with_structured_output_with_instructions_content_recording_disabled_with_attributes(
        self, **kwargs
    ):
        """Test agent creation with structured output and instructions, content recording disabled using attributes (async)."""
        await self._test_agent_with_structured_output_with_instructions_impl(
            use_events=False, content_recording_enabled=False, **kwargs
        )

    async def _test_agent_with_structured_output_without_instructions_impl(
        self, use_events: bool, content_recording_enabled: bool, **kwargs
    ):
        """Implementation for structured output without instructions test (async).

        :param use_events: If True, use events for messages. If False, use attributes.
        :type use_events: bool
        :param content_recording_enabled: Whether content recording is enabled.
        :type content_recording_enabled: bool
        """
        import json

        self.cleanup()
        _set_use_message_events(use_events)
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "True" if content_recording_enabled else "False"})
        self.setup_telemetry()
        assert content_recording_enabled == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        from azure.ai.projects.models import TextResponseFormatJsonSchema

        operation_group = "tracing" if content_recording_enabled else "agents"
        project_client = self.create_async_client(operation_group=operation_group, **kwargs)

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
                text=PromptAgentDefinitionTextOptions(
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
            (GEN_AI_PROVIDER_NAME, AGENTS_PROVIDER),
            (GEN_AI_OPERATION_NAME, "create_agent"),
            (SERVER_ADDRESS, ""),
            (GEN_AI_REQUEST_MODEL, model),
            ("gen_ai.request.response_format", "json_schema"),
            (GEN_AI_AGENT_NAME, "no-instructions-agent-async"),
            (GEN_AI_AGENT_ID, "no-instructions-agent-async:" + str(version)),
            (GEN_AI_AGENT_VERSION, str(version)),
            (GEN_AI_AGENT_TYPE, AGENT_TYPE_PROMPT),
        ]

        # Add attribute expectation when using attributes mode
        if not use_events:
            from azure.ai.projects.telemetry._utils import GEN_AI_SYSTEM_MESSAGE

            if content_recording_enabled:
                expected_system_message = json.dumps([{"type": "response_schema", "content": json.dumps(test_schema)}])
            else:
                expected_system_message = json.dumps([{"type": "response_schema"}])
            expected_attributes.append((GEN_AI_SYSTEM_MESSAGE, expected_system_message))

        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        if use_events:
            # Verify event
            events = span.events
            assert len(events) == 1
            instruction_event = events[0]
            assert instruction_event.name == GEN_AI_SYSTEM_INSTRUCTION_EVENT

            event_content = json.loads(instruction_event.attributes[GEN_AI_EVENT_CONTENT])
            assert isinstance(event_content, list)

            if content_recording_enabled:
                assert len(event_content) == 1  # Only schema, no instructions
                assert event_content[0]["type"] == "response_schema"
                schema_obj = json.loads(event_content[0]["content"])
                assert schema_obj["type"] == "object"
                assert "result" in schema_obj["properties"]
            else:
                # Type indicator without content when content recording disabled
                assert len(event_content) == 1
                assert event_content[0]["type"] == "response_schema"
                assert "content" not in event_content[0]
        else:
            # Validate attribute
            attribute_value = None
            for attr_key, attr_val in span.attributes.items():
                if attr_key == GEN_AI_SYSTEM_MESSAGE:
                    attribute_value = attr_val
                    break
            assert attribute_value is not None

            system_message = json.loads(attribute_value)
            assert isinstance(system_message, list)

            if content_recording_enabled:
                assert len(system_message) == 1  # Only schema
                assert system_message[0]["type"] == "response_schema"
                schema_obj = json.loads(system_message[0]["content"])
                assert schema_obj["type"] == "object"
                assert "result" in schema_obj["properties"]
            else:
                # When content recording disabled, type indicator without content
                assert len(system_message) == 1
                assert system_message[0]["type"] == "response_schema"
                assert "content" not in system_message[0]

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_agent_with_structured_output_without_instructions_content_recording_enabled(self, **kwargs):
        """Test agent creation with structured output but NO instructions, content recording enabled using events (async)."""
        await self._test_agent_with_structured_output_without_instructions_impl(
            use_events=True, content_recording_enabled=True, **kwargs
        )

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_agent_with_structured_output_without_instructions_content_recording_enabled_with_attributes(
        self, **kwargs
    ):
        """Test agent creation with structured output but NO instructions, content recording enabled using attributes (async)."""
        await self._test_agent_with_structured_output_without_instructions_impl(
            use_events=False, content_recording_enabled=True, **kwargs
        )

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_agent_with_structured_output_without_instructions_content_recording_disabled(self, **kwargs):
        """Test agent creation with structured output but NO instructions, content recording disabled using events (async)."""
        await self._test_agent_with_structured_output_without_instructions_impl(
            use_events=True, content_recording_enabled=False, **kwargs
        )

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_agent_with_structured_output_without_instructions_content_recording_disabled_with_attributes(
        self, **kwargs
    ):
        """Test agent creation with structured output but NO instructions, content recording disabled using attributes (async)."""
        await self._test_agent_with_structured_output_without_instructions_impl(
            use_events=False, content_recording_enabled=False, **kwargs
        )
