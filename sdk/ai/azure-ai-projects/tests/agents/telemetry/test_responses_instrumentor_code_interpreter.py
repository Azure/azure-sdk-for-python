# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Tests for ResponsesInstrumentor with Code Interpreter tool.
"""
import os
import pytest
from io import BytesIO
from azure.ai.projects.telemetry import AIProjectInstrumentor, _utils
from azure.ai.projects.telemetry._utils import (
    OPERATION_NAME_INVOKE_AGENT,
    SPAN_NAME_INVOKE_AGENT,
    _set_use_message_events,
    RESPONSES_PROVIDER,
)
from azure.core.settings import settings
from gen_ai_trace_verifier import GenAiTraceVerifier
from devtools_testutils import recorded_by_proxy, RecordedTransport
from azure.ai.projects.models import (
    PromptAgentDefinition,
    CodeInterpreterTool,
    CodeInterpreterContainerAuto,
)

from test_base import servicePreparer
from test_ai_instrumentor_base import (
    TestAiAgentsInstrumentorBase,
    CONTENT_TRACING_ENV_VARIABLE,
)

settings.tracing_implementation = "OpenTelemetry"
_utils._span_impl_type = settings.tracing_implementation()


@pytest.mark.skip(
    reason="Skipped until re-enabled and recorded on Foundry endpoint that supports the new versioning schema"
)
class TestResponsesInstrumentorCodeInterpreter(TestAiAgentsInstrumentorBase):
    """
    Test suite for Code Interpreter agent telemetry instrumentation.

    This class tests OpenTelemetry trace generation when using Code Interpreter tool
    with both content recording enabled and disabled, in both streaming and non-streaming modes.
    """

    # ========================================
    # Sync Code Interpreter Agent Tests - Non-Streaming
    # ========================================

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_sync_code_interpreter_non_streaming_with_content_recording(self, **kwargs):
        """Test synchronous Code Interpreter agent with content recording enabled."""
        self.cleanup()
        _set_use_message_events(True)
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "True",
                "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True",
            }
        )
        self.setup_telemetry()
        assert AIProjectInstrumentor().is_content_recording_enabled()
        assert AIProjectInstrumentor().is_instrumented()

        project_client = self.create_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")
        assert deployment_name is not None

        with project_client:
            openai_client = project_client.get_openai_client()

            # Create CSV data document
            csv_data = """sector,name,operating_profit
TRANSPORTATION,Contoso shipping,850000
TRANSPORTATION,Contoso rail,920000
TRANSPORTATION,Contoso air,1100000
"""

            # Create vector store is not needed for code interpreter, but we need to upload file
            csv_file = BytesIO(csv_data.encode("utf-8"))
            csv_file.name = "transportation_data.csv"

            # Upload file for code interpreter
            file = openai_client.files.create(purpose="assistants", file=csv_file)
            assert file.id is not None

            # Create agent with Code Interpreter tool
            agent = project_client.agents.create_version(
                agent_name="MyAgent",
                definition=PromptAgentDefinition(
                    model=deployment_name,
                    instructions="You are a helpful assistant that can execute Python code to analyze data.",
                    tools=[CodeInterpreterTool(container=CodeInterpreterContainerAuto(file_ids=[file.id]))],
                ),
            )

            try:
                conversation = openai_client.conversations.create()

                # Ask question that triggers code interpreter
                response = openai_client.responses.create(
                    conversation=conversation.id,
                    input="Calculate the average operating profit from the transportation data",
                    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
                )

                # Explicitly call and iterate through conversation items
                items = openai_client.conversations.items.list(conversation_id=conversation.id)
                for item in items:
                    pass

                # Check spans
                self.exporter.force_flush()
                spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_INVOKE_AGENT} {agent.name}")
                assert len(spans) == 1, "Should have one response span"

                # Validate response span
                span = spans[0]
                assert span.attributes is not None
                response_id = span.attributes.get("gen_ai.response.id")
                assert response_id is not None

                expected_attributes = [
                    ("az.namespace", "Microsoft.CognitiveServices"),
                    ("gen_ai.operation.name", OPERATION_NAME_INVOKE_AGENT),
                    ("gen_ai.provider.name", RESPONSES_PROVIDER),
                    ("server.address", ""),
                    ("gen_ai.conversation.id", conversation.id),
                    ("gen_ai.agent.name", agent.name),
                    ("gen_ai.response.model", deployment_name),
                    ("gen_ai.response.id", response_id),
                    ("gen_ai.usage.input_tokens", "+"),
                    ("gen_ai.usage.output_tokens", "+"),
                ]
                assert GenAiTraceVerifier().check_span_attributes(span, expected_attributes)

                # Comprehensive event validation - verify content IS present
                from collections.abc import Mapping
                import json

                found_code_interpreter_call = False
                found_text_response = False

                for event in span.events:
                    if event.name == "gen_ai.input.messages":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)
                        for entry in data:
                            if entry.get("role") == "user":
                                parts = entry.get("parts")
                                for part in parts:
                                    if part.get("type") == "text":
                                        assert "content" in part and isinstance(
                                            part["content"], str
                                        ), "Text content should be present when content recording is enabled"

                    elif event.name == "gen_ai.output.messages":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)

                        for entry in data:
                            parts = entry.get("parts")
                            if parts:
                                for part in parts:
                                    if part.get("type") == "tool_call":
                                        tool_content = part.get("content")
                                        if tool_content and tool_content.get("type") == "code_interpreter_call":
                                            found_code_interpreter_call = True
                                            assert "id" in tool_content, "code_interpreter_call should have id"
                                            # With content recording, code should be present
                                            assert (
                                                "code" in tool_content
                                            ), "code should be present when content recording is enabled"
                                    elif part.get("type") == "text":
                                        found_text_response = True
                                        assert (
                                            "content" in part
                                        ), "text content should be present when content recording is enabled"

                assert found_code_interpreter_call, "Should have found code_interpreter_call in output"
                assert found_text_response, "Should have found text response in output"

                # Check list_conversation_items span
                list_spans = self.exporter.get_spans_by_name("list_conversation_items")
                assert len(list_spans) == 1, "Should have one list_conversation_items span"
                list_span = list_spans[0]

                found_code_interpreter_in_items = False
                for event in list_span.events:
                    if event.name == "gen_ai.conversation.item":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)

                        for entry in data:
                            parts = entry.get("parts")
                            if parts:
                                for part in parts:
                                    if part.get("type") == "text":
                                        assert "content" in part, "text content should be present in conversation items"
                                    elif part.get("type") == "tool_call":
                                        tool_content = part.get("content")
                                        if tool_content and tool_content.get("type") == "code_interpreter_call":
                                            found_code_interpreter_in_items = True
                                            assert (
                                                "id" in tool_content
                                            ), "code_interpreter_call should have id in conversation items"
                                            code_interpreter = tool_content.get("code_interpreter")
                                            if code_interpreter:
                                                assert (
                                                    "code" in code_interpreter
                                                ), "code should be present when content recording is enabled"
                                                assert (
                                                    "status" in code_interpreter
                                                ), "status should be present in code_interpreter"
                    else:
                        assert False, f"Unexpected event name in list_conversation_items span: {event.name}"

                assert found_code_interpreter_in_items, "Should have found code_interpreter_call in conversation items"

                # Cleanup
                openai_client.conversations.delete(conversation_id=conversation.id)
                openai_client.files.delete(file.id)

            finally:
                project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_sync_code_interpreter_non_streaming_without_content_recording(self, **kwargs):
        """Test synchronous Code Interpreter agent with content recording disabled."""
        self.cleanup()
        _set_use_message_events(True)
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "False",
                "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True",
            }
        )
        self.setup_telemetry()
        assert not AIProjectInstrumentor().is_content_recording_enabled()
        assert AIProjectInstrumentor().is_instrumented()

        project_client = self.create_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")
        assert deployment_name is not None

        with project_client:
            openai_client = project_client.get_openai_client()

            # Create CSV data document
            csv_data = """sector,name,operating_profit
TRANSPORTATION,Contoso shipping,850000
TRANSPORTATION,Contoso rail,920000
TRANSPORTATION,Contoso air,1100000
"""

            csv_file = BytesIO(csv_data.encode("utf-8"))
            csv_file.name = "transportation_data.csv"

            # Upload file for code interpreter
            file = openai_client.files.create(purpose="assistants", file=csv_file)
            assert file.id is not None

            # Create agent with Code Interpreter tool
            agent = project_client.agents.create_version(
                agent_name="MyAgent",
                definition=PromptAgentDefinition(
                    model=deployment_name,
                    instructions="You are a helpful assistant that can execute Python code to analyze data.",
                    tools=[CodeInterpreterTool(container=CodeInterpreterContainerAuto(file_ids=[file.id]))],
                ),
            )

            try:
                conversation = openai_client.conversations.create()

                # Ask question that triggers code interpreter
                response = openai_client.responses.create(
                    conversation=conversation.id,
                    input="Calculate the average operating profit from the transportation data",
                    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
                )

                # Explicitly call and iterate through conversation items
                items = openai_client.conversations.items.list(conversation_id=conversation.id)
                for item in items:
                    pass

                # Check spans
                self.exporter.force_flush()
                spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_INVOKE_AGENT} {agent.name}")
                assert len(spans) == 1, "Should have one response span"

                # Validate response span
                span = spans[0]
                assert span.attributes is not None
                response_id = span.attributes.get("gen_ai.response.id")
                assert response_id is not None

                expected_attributes = [
                    ("az.namespace", "Microsoft.CognitiveServices"),
                    ("gen_ai.operation.name", OPERATION_NAME_INVOKE_AGENT),
                    ("gen_ai.provider.name", RESPONSES_PROVIDER),
                    ("server.address", ""),
                    ("gen_ai.conversation.id", conversation.id),
                    ("gen_ai.agent.name", agent.name),
                    ("gen_ai.response.model", deployment_name),
                    ("gen_ai.response.id", response_id),
                    ("gen_ai.usage.input_tokens", "+"),
                    ("gen_ai.usage.output_tokens", "+"),
                ]
                assert GenAiTraceVerifier().check_span_attributes(span, expected_attributes)

                # Comprehensive event validation - verify content is NOT present
                from collections.abc import Mapping
                import json

                found_code_interpreter_call = False
                found_text_response = False

                for event in span.events:
                    if event.name == "gen_ai.input.messages":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)
                        for entry in data:
                            if entry.get("role") == "user":
                                parts = entry.get("parts")
                                for part in parts:
                                    if part.get("type") == "text":
                                        assert (
                                            "content" not in part
                                        ), "Text content should NOT be present when content recording is disabled"

                    elif event.name == "gen_ai.output.messages":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)

                        for entry in data:
                            parts = entry.get("parts")
                            if parts:
                                for part in parts:
                                    if part.get("type") == "tool_call":
                                        tool_content = part.get("content")
                                        if tool_content and tool_content.get("type") == "code_interpreter_call":
                                            found_code_interpreter_call = True
                                            assert "id" in tool_content, "code_interpreter_call should have id"
                                            # Without content recording, code should NOT be present
                                            assert (
                                                "code" not in tool_content
                                            ), "code should NOT be present when content recording is disabled"
                                    elif part.get("type") == "text":
                                        found_text_response = True
                                        assert (
                                            "content" not in part
                                        ), "text content should NOT be present when content recording is disabled"

                assert found_code_interpreter_call, "Should have found code_interpreter_call in output"
                assert found_text_response, "Should have found text response type in output"

                # Check list_conversation_items span
                list_spans = self.exporter.get_spans_by_name("list_conversation_items")
                assert len(list_spans) == 1, "Should have one list_conversation_items span"
                list_span = list_spans[0]

                found_code_interpreter_in_items = False
                for event in list_span.events:
                    if event.name == "gen_ai.conversation.item":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)

                        for entry in data:
                            parts = entry.get("parts")
                            if parts:
                                for part in parts:
                                    if part.get("type") == "text":
                                        assert (
                                            "content" not in part
                                        ), "text content should NOT be present in conversation items"
                                    elif part.get("type") == "tool_call":
                                        tool_content = part.get("content")
                                        if tool_content and tool_content.get("type") == "code_interpreter_call":
                                            found_code_interpreter_in_items = True
                                            assert (
                                                "id" in tool_content
                                            ), "code_interpreter_call should have id in conversation items"
                                            # Without content recording, code should NOT be present
                                            code_interpreter = tool_content.get("code_interpreter")
                                            if code_interpreter:
                                                assert (
                                                    "code" not in code_interpreter
                                                ), "code should NOT be present when content recording is disabled"
                    else:
                        assert False, f"Unexpected event name in list_conversation_items span: {event.name}"

                assert found_code_interpreter_in_items, "Should have found code_interpreter_call in conversation items"

                # Cleanup
                openai_client.conversations.delete(conversation_id=conversation.id)
                openai_client.files.delete(file.id)

            finally:
                project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

    # ========================================
    # Sync Code Interpreter Agent Tests - Streaming
    # ========================================

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_sync_code_interpreter_streaming_with_content_recording(self, **kwargs):
        """Test synchronous Code Interpreter agent with streaming and content recording enabled."""
        self.cleanup()
        _set_use_message_events(True)
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "True",
                "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True",
            }
        )
        self.setup_telemetry()
        assert AIProjectInstrumentor().is_content_recording_enabled()
        assert AIProjectInstrumentor().is_instrumented()

        project_client = self.create_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")
        assert deployment_name is not None

        with project_client:
            openai_client = project_client.get_openai_client()

            # Create CSV data document
            csv_data = """sector,name,operating_profit
TRANSPORTATION,Contoso shipping,850000
TRANSPORTATION,Contoso rail,920000
TRANSPORTATION,Contoso air,1100000
"""

            csv_file = BytesIO(csv_data.encode("utf-8"))
            csv_file.name = "transportation_data.csv"

            # Upload file for code interpreter
            file = openai_client.files.create(purpose="assistants", file=csv_file)
            assert file.id is not None

            # Create agent with Code Interpreter tool
            agent = project_client.agents.create_version(
                agent_name="MyAgent",
                definition=PromptAgentDefinition(
                    model=deployment_name,
                    instructions="You are a helpful assistant that can execute Python code to analyze data.",
                    tools=[CodeInterpreterTool(container=CodeInterpreterContainerAuto(file_ids=[file.id]))],
                ),
            )

            try:
                conversation = openai_client.conversations.create()

                # Ask question that triggers code interpreter with streaming
                stream = openai_client.responses.create(
                    conversation=conversation.id,
                    input="Calculate the average operating profit from the transportation data",
                    stream=True,
                    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
                )

                # Consume the stream
                for event in stream:
                    pass

                # Explicitly call and iterate through conversation items
                items = openai_client.conversations.items.list(conversation_id=conversation.id)
                for item in items:
                    pass

                # Check spans
                self.exporter.force_flush()
                spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_INVOKE_AGENT} {agent.name}")
                assert len(spans) == 1, "Should have one response span"

                # Validate response span
                span = spans[0]
                assert span.attributes is not None
                response_id = span.attributes.get("gen_ai.response.id")
                assert response_id is not None

                expected_attributes = [
                    ("az.namespace", "Microsoft.CognitiveServices"),
                    ("gen_ai.operation.name", OPERATION_NAME_INVOKE_AGENT),
                    ("gen_ai.provider.name", RESPONSES_PROVIDER),
                    ("server.address", ""),
                    ("gen_ai.conversation.id", conversation.id),
                    ("gen_ai.agent.name", agent.name),
                    ("gen_ai.response.model", deployment_name),
                    ("gen_ai.response.id", response_id),
                    ("gen_ai.usage.input_tokens", "+"),
                    ("gen_ai.usage.output_tokens", "+"),
                ]
                assert GenAiTraceVerifier().check_span_attributes(span, expected_attributes)

                # Comprehensive event validation - verify content IS present
                from collections.abc import Mapping
                import json

                found_code_interpreter_call = False
                found_text_response = False

                for event in span.events:
                    if event.name == "gen_ai.input.messages":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)
                        for entry in data:
                            if entry.get("role") == "user":
                                parts = entry.get("parts")
                                for part in parts:
                                    if part.get("type") == "text":
                                        assert "content" in part and isinstance(
                                            part["content"], str
                                        ), "Text content should be present when content recording is enabled"

                    elif event.name == "gen_ai.output.messages":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)

                        for entry in data:
                            parts = entry.get("parts")
                            if parts:
                                for part in parts:
                                    if part.get("type") == "tool_call":
                                        tool_content = part.get("content")
                                        if tool_content and tool_content.get("type") == "code_interpreter_call":
                                            found_code_interpreter_call = True
                                            assert "id" in tool_content, "code_interpreter_call should have id"
                                            assert (
                                                "code" in tool_content
                                            ), "code should be present when content recording is enabled"
                                    elif part.get("type") == "text":
                                        found_text_response = True
                                        assert (
                                            "content" in part
                                        ), "text content should be present when content recording is enabled"

                assert found_code_interpreter_call, "Should have found code_interpreter_call in output"
                assert found_text_response, "Should have found text response in output"

                # Check list_conversation_items span
                list_spans = self.exporter.get_spans_by_name("list_conversation_items")
                assert len(list_spans) == 1, "Should have one list_conversation_items span"
                list_span = list_spans[0]

                found_code_interpreter_in_items = False
                for event in list_span.events:
                    if event.name == "gen_ai.conversation.item":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)

                        for entry in data:
                            parts = entry.get("parts")
                            if parts:
                                for part in parts:
                                    if part.get("type") == "text":
                                        assert "content" in part, "text content should be present in conversation items"
                                    elif part.get("type") == "tool_call":
                                        tool_content = part.get("content")
                                        if tool_content and tool_content.get("type") == "code_interpreter_call":
                                            found_code_interpreter_in_items = True
                                            assert (
                                                "id" in tool_content
                                            ), "code_interpreter_call should have id in conversation items"
                                            code_interpreter = tool_content.get("code_interpreter")
                                            if code_interpreter:
                                                assert (
                                                    "code" in code_interpreter
                                                ), "code should be present when content recording is enabled"
                                                assert (
                                                    "status" in code_interpreter
                                                ), "status should be present in code_interpreter"
                    else:
                        assert False, f"Unexpected event name in list_conversation_items span: {event.name}"

                assert found_code_interpreter_in_items, "Should have found code_interpreter_call in conversation items"

                # Cleanup
                openai_client.conversations.delete(conversation_id=conversation.id)
                openai_client.files.delete(file.id)

            finally:
                project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_sync_code_interpreter_streaming_without_content_recording(self, **kwargs):
        """Test synchronous Code Interpreter agent with streaming and content recording disabled."""
        self.cleanup()
        _set_use_message_events(True)
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "False",
                "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True",
            }
        )
        self.setup_telemetry()
        assert not AIProjectInstrumentor().is_content_recording_enabled()
        assert AIProjectInstrumentor().is_instrumented()

        project_client = self.create_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")
        assert deployment_name is not None

        with project_client:
            openai_client = project_client.get_openai_client()

            # Create CSV data document
            csv_data = """sector,name,operating_profit
TRANSPORTATION,Contoso shipping,850000
TRANSPORTATION,Contoso rail,920000
TRANSPORTATION,Contoso air,1100000
"""

            csv_file = BytesIO(csv_data.encode("utf-8"))
            csv_file.name = "transportation_data.csv"

            # Upload file for code interpreter
            file = openai_client.files.create(purpose="assistants", file=csv_file)
            assert file.id is not None

            # Create agent with Code Interpreter tool
            agent = project_client.agents.create_version(
                agent_name="MyAgent",
                definition=PromptAgentDefinition(
                    model=deployment_name,
                    instructions="You are a helpful assistant that can execute Python code to analyze data.",
                    tools=[CodeInterpreterTool(container=CodeInterpreterContainerAuto(file_ids=[file.id]))],
                ),
            )

            try:
                conversation = openai_client.conversations.create()

                # Ask question that triggers code interpreter with streaming
                stream = openai_client.responses.create(
                    conversation=conversation.id,
                    input="Calculate the average operating profit from the transportation data",
                    stream=True,
                    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
                )

                # Consume the stream
                for event in stream:
                    pass

                # Explicitly call and iterate through conversation items
                items = openai_client.conversations.items.list(conversation_id=conversation.id)
                for item in items:
                    pass

                # Check spans
                self.exporter.force_flush()
                spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_INVOKE_AGENT} {agent.name}")
                assert len(spans) == 1, "Should have one response span"

                # Validate response span
                span = spans[0]
                assert span.attributes is not None
                response_id = span.attributes.get("gen_ai.response.id")
                assert response_id is not None

                expected_attributes = [
                    ("az.namespace", "Microsoft.CognitiveServices"),
                    ("gen_ai.operation.name", OPERATION_NAME_INVOKE_AGENT),
                    ("gen_ai.provider.name", RESPONSES_PROVIDER),
                    ("server.address", ""),
                    ("gen_ai.conversation.id", conversation.id),
                    ("gen_ai.agent.name", agent.name),
                    ("gen_ai.response.model", deployment_name),
                    ("gen_ai.response.id", response_id),
                    ("gen_ai.usage.input_tokens", "+"),
                    ("gen_ai.usage.output_tokens", "+"),
                ]
                assert GenAiTraceVerifier().check_span_attributes(span, expected_attributes)

                # Comprehensive event validation - verify content is NOT present
                from collections.abc import Mapping
                import json

                found_code_interpreter_call = False
                found_text_response = False

                for event in span.events:
                    if event.name == "gen_ai.input.messages":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)
                        for entry in data:
                            if entry.get("role") == "user":
                                parts = entry.get("parts")
                                for part in parts:
                                    if part.get("type") == "text":
                                        assert (
                                            "content" not in part
                                        ), "Text content should NOT be present when content recording is disabled"

                    elif event.name == "gen_ai.output.messages":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)

                        for entry in data:
                            parts = entry.get("parts")
                            if parts:
                                for part in parts:
                                    if part.get("type") == "tool_call":
                                        tool_content = part.get("content")
                                        if tool_content and tool_content.get("type") == "code_interpreter_call":
                                            found_code_interpreter_call = True
                                            assert "id" in tool_content, "code_interpreter_call should have id"
                                            assert (
                                                "code" not in tool_content
                                            ), "code should NOT be present when content recording is disabled"
                                    elif part.get("type") == "text":
                                        found_text_response = True
                                        assert (
                                            "content" not in part
                                        ), "text content should NOT be present when content recording is disabled"

                assert found_code_interpreter_call, "Should have found code_interpreter_call in output"
                assert found_text_response, "Should have found text response type in output"

                # Check list_conversation_items span
                list_spans = self.exporter.get_spans_by_name("list_conversation_items")
                assert len(list_spans) == 1, "Should have one list_conversation_items span"
                list_span = list_spans[0]

                found_code_interpreter_in_items = False
                for event in list_span.events:
                    if event.name == "gen_ai.conversation.item":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)

                        for entry in data:
                            parts = entry.get("parts")
                            if parts:
                                for part in parts:
                                    if part.get("type") == "text":
                                        assert (
                                            "content" not in part
                                        ), "text content should NOT be present in conversation items"
                                    elif part.get("type") == "tool_call":
                                        tool_content = part.get("content")
                                        if tool_content and tool_content.get("type") == "code_interpreter_call":
                                            found_code_interpreter_in_items = True
                                            assert (
                                                "id" in tool_content
                                            ), "code_interpreter_call should have id in conversation items"
                                            code_interpreter = tool_content.get("code_interpreter")
                                            if code_interpreter:
                                                assert (
                                                    "code" not in code_interpreter
                                                ), "code should NOT be present when content recording is disabled"
                    else:
                        assert False, f"Unexpected event name in list_conversation_items span: {event.name}"

                assert found_code_interpreter_in_items, "Should have found code_interpreter_call in conversation items"

                # Cleanup
                openai_client.conversations.delete(conversation_id=conversation.id)
                openai_client.files.delete(file.id)

            finally:
                project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
