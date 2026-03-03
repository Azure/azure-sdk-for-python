# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Tests for ResponsesInstrumentor with MCP agents.
"""
import os
import pytest
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
from azure.ai.projects.models import PromptAgentDefinition, MCPTool
from openai.types.responses.response_input_param import McpApprovalResponse

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
class TestResponsesInstrumentorMCP(TestAiAgentsInstrumentorBase):
    """Tests for ResponsesInstrumentor with MCP agents."""

    # ========================================
    # Sync MCP Agent Tests - Non-Streaming
    # ========================================

    def _test_sync_mcp_non_streaming_with_content_recording_impl(self, use_events, **kwargs):
        """Implementation for testing synchronous MCP agent with non-streaming and content recording enabled.

        Args:
            use_events: If True, use event-based message tracing. If False, use attribute-based.
                       Note: MCP tests currently only validate event mode regardless of this setting.
        """
        self.cleanup()
        _set_use_message_events(use_events)
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

            # Create MCP tool
            mcp_tool = MCPTool(
                server_label="api-specs",
                server_url="https://gitmcp.io/Azure/azure-rest-api-specs",
                require_approval="always",
            )

            agent = project_client.agents.create_version(
                agent_name="MyAgent",
                definition=PromptAgentDefinition(
                    model=deployment_name,
                    instructions="You are a helpful agent that can use MCP tools to assist users.",
                    tools=[mcp_tool],
                ),
            )

            try:
                conversation = openai_client.conversations.create()

                # First request - triggers MCP tool
                response = openai_client.responses.create(
                    conversation=conversation.id,
                    input="Please summarize the Azure REST API specifications Readme",
                    stream=False,
                    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
                )

                # Collect approval requests
                input_list = []
                for item in response.output:
                    if item.type == "mcp_approval_request":
                        if item.server_label == "api-specs" and item.id:
                            input_list.append(
                                McpApprovalResponse(
                                    type="mcp_approval_response",
                                    approve=True,
                                    approval_request_id=item.id,
                                )
                            )

                # Send approval response
                response2 = openai_client.responses.create(
                    conversation=conversation.id,
                    input=input_list,
                    stream=False,
                    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
                )

                assert response2.output_text is not None

                # Explicitly call and iterate through conversation items
                items = openai_client.conversations.items.list(conversation_id=conversation.id)
                for item in items:
                    pass  # Iterate to consume items

                # Check spans
                self.exporter.force_flush()
                spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_INVOKE_AGENT} {agent.name}")
                assert len(spans) == 2, "Should have two response spans (initial + approval)"

                # Validate first response span (MCP tool trigger)
                span1 = spans[0]
                expected_attributes_1 = [
                    ("az.namespace", "Microsoft.CognitiveServices"),
                    ("gen_ai.operation.name", OPERATION_NAME_INVOKE_AGENT),
                    ("gen_ai.provider.name", RESPONSES_PROVIDER),
                    ("server.address", ""),
                    ("gen_ai.conversation.id", conversation.id),
                    ("gen_ai.agent.name", agent.name),
                    ("gen_ai.response.model", deployment_name),
                    ("gen_ai.response.id", response.id),
                    ("gen_ai.usage.input_tokens", "+"),
                    ("gen_ai.usage.output_tokens", "+"),
                ]

                # Add message attributes when not using events
                if not use_events:
                    expected_attributes_1.extend(
                        [
                            ("gen_ai.input.messages", ""),
                            ("gen_ai.output.messages", ""),
                        ]
                    )

                assert GenAiTraceVerifier().check_span_attributes(span1, expected_attributes_1)

                # Comprehensive event validation for first span - verify content IS present
                # Only validate events when use_events is True
                from collections.abc import Mapping

                if use_events:
                    for event in span1.events:
                        if event.name == "gen_ai.input.messages":
                            attrs = event.attributes
                            assert attrs is not None and isinstance(attrs, Mapping)
                            content = attrs.get("gen_ai.event.content")
                            assert isinstance(content, str) and content.strip() != ""
                            import json

                            data = json.loads(content)
                            assert isinstance(data, list) and len(data) > 0
                            # Validate content fields ARE present
                            for entry in data:
                                if entry.get("role") == "user":
                                    parts = entry.get("parts")
                                    assert isinstance(parts, list) and len(parts) > 0
                                    for part in parts:
                                        if part.get("type") == "text":
                                            assert (
                                                "content" in part
                                                and isinstance(part["content"], str)
                                                and part["content"].strip() != ""
                                            ), "Text content should be present when content recording is enabled"
                        elif event.name == "gen_ai.output.messages":
                            attrs = event.attributes
                            assert attrs is not None and isinstance(attrs, Mapping)
                            content = attrs.get("gen_ai.event.content")
                            assert isinstance(content, str) and content.strip() != ""
                            import json

                            data = json.loads(content)
                            assert isinstance(data, list) and len(data) > 0
                            first = data[0]
                            assert first.get("role") in ("assistant", "tool")
                            parts = first.get("parts")
                            assert isinstance(parts, list) and len(parts) > 0
                            # Check for MCP-specific content
                            for part in parts:
                                if part.get("type") == "tool_call":
                                    tool_content = part.get("content")
                                    assert isinstance(tool_content, dict)
                                    tool_type = tool_content.get("type")
                                    if tool_type in ("mcp_list_tools", "mcp_approval_request"):
                                        assert "id" in tool_content
                                        if tool_type == "mcp_list_tools":
                                            assert (
                                                "server_label" in tool_content
                                            ), "server_label should be present for mcp_list_tools when content recording is enabled"
                                        elif tool_type == "mcp_approval_request":
                                            assert (
                                                "name" in tool_content
                                            ), "name should be present for mcp_approval_request when content recording is enabled"
                                            assert (
                                                "server_label" in tool_content
                                            ), "server_label should be present for mcp_approval_request when content recording is enabled"
                                            assert (
                                                "arguments" in tool_content
                                            ), "arguments should be present for mcp_approval_request when content recording is enabled"

                # Validate second response span (approval response)
                span2 = spans[1]
                expected_attributes_2 = [
                    ("az.namespace", "Microsoft.CognitiveServices"),
                    ("gen_ai.operation.name", OPERATION_NAME_INVOKE_AGENT),
                    ("gen_ai.provider.name", RESPONSES_PROVIDER),
                    ("server.address", ""),
                    ("gen_ai.conversation.id", conversation.id),
                    ("gen_ai.agent.name", agent.name),
                    ("gen_ai.response.model", deployment_name),
                    ("gen_ai.response.id", response2.id),
                    ("gen_ai.usage.input_tokens", "+"),
                    ("gen_ai.usage.output_tokens", "+"),
                ]

                # Add message attributes when not using events
                if not use_events:
                    expected_attributes_2.extend(
                        [
                            ("gen_ai.input.messages", ""),
                            ("gen_ai.output.messages", ""),
                        ]
                    )

                assert GenAiTraceVerifier().check_span_attributes(span2, expected_attributes_2)

                # Validate MCP approval response and call in second span
                # Only validate events when use_events is True
                if use_events:
                    for event in span2.events:
                        if event.name == "gen_ai.input.messages":
                            attrs = event.attributes
                            assert attrs is not None and isinstance(attrs, Mapping)
                            content = attrs.get("gen_ai.event.content")
                            assert isinstance(content, str) and content.strip() != ""
                            import json

                            data = json.loads(content)
                            # Check for MCP approval response content
                            for entry in data:
                                if entry.get("role") == "user":
                                    parts = entry.get("parts")
                                    for part in parts:
                                        if part.get("type") == "mcp":
                                            mcp_content = part.get("content")
                                            assert isinstance(mcp_content, dict)
                                            if mcp_content.get("type") == "mcp_approval_response":
                                                assert "id" in mcp_content
                                                assert (
                                                    "approval_request_id" in mcp_content
                                                ), "approval_request_id should be present when content recording is enabled"
                        elif event.name == "gen_ai.output.messages":
                            attrs = event.attributes
                            assert attrs is not None and isinstance(attrs, Mapping)
                            content = attrs.get("gen_ai.event.content")
                            assert isinstance(content, str) and content.strip() != ""
                            import json

                            data = json.loads(content)
                            # Check for MCP call content
                            for entry in data:
                                parts = entry.get("parts")
                                if parts:
                                    for part in parts:
                                        if part.get("type") == "tool_call":
                                            tool_content = part.get("content")
                                            if tool_content and tool_content.get("type") == "mcp_call":
                                                assert "id" in tool_content
                                                assert (
                                                    "name" in tool_content
                                                ), "name should be present for mcp_call when content recording is enabled"
                                                assert (
                                                    "arguments" in tool_content
                                                ), "arguments should be present for mcp_call when content recording is enabled"
                                                assert (
                                                    "server_label" in tool_content
                                                ), "server_label should be present for mcp_call when content recording is enabled"
                                        elif part.get("type") == "text":
                                            assert (
                                                "content" in part
                                            ), "text content should be present when content recording is enabled"

                # Check list_conversation_items span
                list_spans = self.exporter.get_spans_by_name("list_conversation_items")
                assert len(list_spans) == 1, "Should have one list_conversation_items span"
                list_span = list_spans[0]

                if use_events:
                    for event in list_span.events:
                        if event.name == "gen_ai.conversation.item":
                            attrs = event.attributes
                            assert attrs is not None and isinstance(attrs, Mapping)
                            content = attrs.get("gen_ai.event.content")
                            assert isinstance(content, str) and content.strip() != ""
                            import json

                            data = json.loads(content)
                            # Validate MCP content in conversation items
                            for entry in data:
                                if entry.get("role") == "user":
                                    parts = entry.get("parts")
                                    for part in parts:
                                        if part.get("type") == "text":
                                            assert (
                                                "content" in part
                                            ), "text content should be present in conversation items when content recording is enabled"
                                        elif part.get("type") == "mcp":
                                            mcp_content = part.get("content")
                                            if mcp_content and mcp_content.get("type") == "mcp_approval_response":
                                                assert (
                                                    "approval_request_id" in mcp_content
                                                ), "approval_request_id should be present when content recording is enabled"
                                elif entry.get("role") == "assistant":
                                    parts = entry.get("parts")
                                    for part in parts:
                                        if part.get("type") == "text":
                                            assert (
                                                "content" in part
                                            ), "text content should be present in conversation items when content recording is enabled"
                                        elif part.get("type") == "mcp":
                                            mcp_content = part.get("content")
                                            if mcp_content:
                                                mcp_type = mcp_content.get("type")
                                                if mcp_type in ("mcp_list_tools", "mcp_call", "mcp_approval_request"):
                                                    assert "id" in mcp_content
                                                    if mcp_type == "mcp_call":
                                                        assert (
                                                            "name" in mcp_content
                                                        ), "name should be present for mcp_call in conversation items"
                                                        assert (
                                                            "server_label" in mcp_content
                                                        ), "server_label should be present for mcp_call in conversation items"
                        else:
                            assert False, f"Unexpected event name in list_conversation_items span: {event.name}"

                # Cleanup
                openai_client.conversations.delete(conversation_id=conversation.id)

            finally:
                project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_sync_mcp_non_streaming_with_content_recording_events(self, **kwargs):
        """Test synchronous MCP agent with non-streaming and content recording enabled (event-based messages)."""
        self._test_sync_mcp_non_streaming_with_content_recording_impl(True, **kwargs)

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_sync_mcp_non_streaming_with_content_recording_attributes(self, **kwargs):
        """Test synchronous MCP agent with non-streaming and content recording enabled (attribute-based messages)."""
        self._test_sync_mcp_non_streaming_with_content_recording_impl(False, **kwargs)

    def _test_sync_mcp_non_streaming_without_content_recording_impl(self, use_events, **kwargs):
        """Implementation for testing synchronous MCP agent with non-streaming and content recording disabled.

        Args:
            use_events: If True, use event-based message tracing. If False, use attribute-based.
                       Note: MCP tests currently only validate event mode regardless of this setting.
        """
        self.cleanup()
        _set_use_message_events(use_events)
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

            # Create MCP tool
            mcp_tool = MCPTool(
                server_label="api-specs",
                server_url="https://gitmcp.io/Azure/azure-rest-api-specs",
                require_approval="always",
            )

            agent = project_client.agents.create_version(
                agent_name="MyAgent",
                definition=PromptAgentDefinition(
                    model=deployment_name,
                    instructions="You are a helpful agent that can use MCP tools to assist users.",
                    tools=[mcp_tool],
                ),
            )

            try:
                conversation = openai_client.conversations.create()

                # First request - triggers MCP tool
                response = openai_client.responses.create(
                    conversation=conversation.id,
                    input="Please summarize the Azure REST API specifications Readme",
                    stream=False,
                    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
                )

                # Collect approval requests
                input_list = []
                for item in response.output:
                    if item.type == "mcp_approval_request":
                        if item.server_label == "api-specs" and item.id:
                            input_list.append(
                                McpApprovalResponse(
                                    type="mcp_approval_response",
                                    approve=True,
                                    approval_request_id=item.id,
                                )
                            )

                # Send approval response
                response2 = openai_client.responses.create(
                    conversation=conversation.id,
                    input=input_list,
                    stream=False,
                    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
                )

                assert response2.output_text is not None

                # Explicitly call and iterate through conversation items
                items = openai_client.conversations.items.list(conversation_id=conversation.id)
                for item in items:
                    pass  # Just iterate to consume items

                # Check spans
                self.exporter.force_flush()
                spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_INVOKE_AGENT} {agent.name}")
                assert len(spans) == 2, "Should have two response spans (initial + approval)"

                # Validate first response span (MCP tool trigger)
                span1 = spans[0]
                expected_attributes_1 = [
                    ("az.namespace", "Microsoft.CognitiveServices"),
                    ("gen_ai.operation.name", OPERATION_NAME_INVOKE_AGENT),
                    ("gen_ai.provider.name", RESPONSES_PROVIDER),
                    ("server.address", ""),
                    ("gen_ai.conversation.id", conversation.id),
                    ("gen_ai.agent.name", agent.name),
                    ("gen_ai.response.model", deployment_name),
                    ("gen_ai.response.id", response.id),
                    ("gen_ai.usage.input_tokens", "+"),
                    ("gen_ai.usage.output_tokens", "+"),
                ]

                # Add message attributes when not using events
                if not use_events:
                    expected_attributes_1.extend(
                        [
                            ("gen_ai.input.messages", ""),
                            ("gen_ai.output.messages", ""),
                        ]
                    )

                assert GenAiTraceVerifier().check_span_attributes(span1, expected_attributes_1)

                # Comprehensive event validation for first span - verify content is NOT present
                # Only validate events when use_events is True
                from collections.abc import Mapping

                if use_events:
                    for event in span1.events:
                        if event.name == "gen_ai.input.messages":
                            attrs = event.attributes
                            assert attrs is not None and isinstance(attrs, Mapping)
                            content = attrs.get("gen_ai.event.content")
                            assert isinstance(content, str) and content.strip() != ""
                            import json

                            data = json.loads(content)
                            assert isinstance(data, list) and len(data) > 0
                            # Validate content fields are NOT present
                            for entry in data:
                                if entry.get("role") == "user":
                                    parts = entry.get("parts")
                                    assert isinstance(parts, list) and len(parts) > 0
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
                            import json

                            data = json.loads(content)
                            assert isinstance(data, list) and len(data) > 0
                            first = data[0]
                            assert first.get("role") in ("assistant", "tool")
                            parts = first.get("parts")
                            assert isinstance(parts, list) and len(parts) > 0
                            # Check for MCP-specific content - should have type and id but not detailed fields
                            for part in parts:
                                if part.get("type") == "tool_call":
                                    tool_content = part.get("content")
                                    assert isinstance(tool_content, dict)
                                    tool_type = tool_content.get("type")
                                    if tool_type in ("mcp_list_tools", "mcp_approval_request"):
                                        assert "id" in tool_content
                                        if tool_type == "mcp_list_tools":
                                            # server_label might be present but other details should not
                                            pass
                                        elif tool_type == "mcp_approval_request":
                                            # Should not have name, arguments when content recording is disabled
                                            assert (
                                                "name" not in tool_content
                                            ), "name should NOT be present for mcp_approval_request when content recording is disabled"
                                            assert (
                                                "arguments" not in tool_content
                                            ), "arguments should NOT be present for mcp_approval_request when content recording is disabled"

                # Validate second response span (approval response)
                span2 = spans[1]
                expected_attributes_2 = [
                    ("az.namespace", "Microsoft.CognitiveServices"),
                    ("gen_ai.operation.name", OPERATION_NAME_INVOKE_AGENT),
                    ("gen_ai.provider.name", RESPONSES_PROVIDER),
                    ("server.address", ""),
                    ("gen_ai.conversation.id", conversation.id),
                    ("gen_ai.agent.name", agent.name),
                    ("gen_ai.response.model", deployment_name),
                    ("gen_ai.response.id", response2.id),
                    ("gen_ai.usage.input_tokens", "+"),
                    ("gen_ai.usage.output_tokens", "+"),
                ]

                # Add message attributes when not using events
                if not use_events:
                    expected_attributes_2.extend(
                        [
                            ("gen_ai.input.messages", ""),
                            ("gen_ai.output.messages", ""),
                        ]
                    )

                assert GenAiTraceVerifier().check_span_attributes(span2, expected_attributes_2)

                # Validate MCP approval response and call in second span - content should be minimal
                for event in span2.events:
                    if event.name == "gen_ai.input.messages":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        import json

                        data = json.loads(content)
                        # Check for MCP approval response content - should be minimal
                        for entry in data:
                            if entry.get("role") == "user":
                                parts = entry.get("parts")
                                for part in parts:
                                    if part.get("type") == "mcp":
                                        mcp_content = part.get("content")
                                        assert isinstance(mcp_content, dict)
                                        if mcp_content.get("type") == "mcp_approval_response":
                                            assert "id" in mcp_content
                                            # approval_request_id might not be present when content recording is disabled
                    elif event.name == "gen_ai.output.messages":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        import json

                        data = json.loads(content)
                        # Check for MCP call content - should be minimal
                        for entry in data:
                            parts = entry.get("parts")
                            if parts:
                                for part in parts:
                                    if part.get("type") == "tool_call":
                                        tool_content = part.get("content")
                                        if tool_content and tool_content.get("type") == "mcp_call":
                                            assert "id" in tool_content
                                            assert (
                                                "name" not in tool_content
                                            ), "name should NOT be present for mcp_call when content recording is disabled"
                                            assert (
                                                "arguments" not in tool_content
                                            ), "arguments should NOT be present for mcp_call when content recording is disabled"
                                    elif part.get("type") == "text":
                                        assert (
                                            "content" not in part
                                        ), "text content should NOT be present when content recording is disabled"

                # Check list_conversation_items span
                list_spans = self.exporter.get_spans_by_name("list_conversation_items")
                assert len(list_spans) == 1, "Should have one list_conversation_items span"
                list_span = list_spans[0]

                for event in list_span.events:
                    if event.name == "gen_ai.conversation.item":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        import json

                        data = json.loads(content)
                        # Validate MCP content in conversation items - should be minimal
                        for entry in data:
                            if entry.get("role") == "user":
                                parts = entry.get("parts")
                                for part in parts:
                                    if part.get("type") == "text":
                                        assert (
                                            "content" not in part
                                        ), "text content should NOT be present in conversation items when content recording is disabled"
                                    elif part.get("type") == "mcp":
                                        mcp_content = part.get("content")
                                        if mcp_content and mcp_content.get("type") == "mcp_approval_response":
                                            # Should have id but might not have other details
                                            assert "id" in mcp_content
                            elif entry.get("role") == "assistant":
                                parts = entry.get("parts")
                                for part in parts:
                                    if part.get("type") == "text":
                                        assert (
                                            "content" not in part
                                        ), "text content should NOT be present in conversation items when content recording is disabled"
                                    elif part.get("type") == "mcp":
                                        mcp_content = part.get("content")
                                        if mcp_content:
                                            mcp_type = mcp_content.get("type")
                                            if mcp_type == "mcp_call":
                                                assert "id" in mcp_content
                                                # Should not have name, server_label, arguments when content recording is disabled
                                                assert (
                                                    "name" not in mcp_content
                                                ), "name should NOT be present for mcp_call in conversation items when content recording is disabled"
                    else:
                        assert False, f"Unexpected event name in list_conversation_items span: {event.name}"

                # Cleanup
                openai_client.conversations.delete(conversation_id=conversation.id)

            finally:
                project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_sync_mcp_non_streaming_without_content_recording_events(self, **kwargs):
        """Test synchronous MCP agent with non-streaming and content recording disabled (event-based messages)."""
        self._test_sync_mcp_non_streaming_without_content_recording_impl(True, **kwargs)

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_sync_mcp_non_streaming_without_content_recording_attributes(self, **kwargs):
        """Test synchronous MCP agent with non-streaming and content recording disabled (attribute-based messages)."""
        self._test_sync_mcp_non_streaming_without_content_recording_impl(False, **kwargs)

    # ========================================
    # Sync MCP Agent Tests - Streaming
    # ========================================

    def _test_sync_mcp_streaming_with_content_recording_impl(self, use_events, **kwargs):
        """Implementation for testing synchronous MCP agent with streaming and content recording enabled.

        Args:
            use_events: If True, use event-based message tracing. If False, use attribute-based.
                       Note: MCP tests currently only validate event mode regardless of this setting.
        """
        self.cleanup()
        _set_use_message_events(use_events)
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

            # Create MCP tool
            mcp_tool = MCPTool(
                server_label="api-specs",
                server_url="https://gitmcp.io/Azure/azure-rest-api-specs",
                require_approval="always",
            )

            agent = project_client.agents.create_version(
                agent_name="MyAgent",
                definition=PromptAgentDefinition(
                    model=deployment_name,
                    instructions="You are a helpful agent that can use MCP tools to assist users.",
                    tools=[mcp_tool],
                ),
            )

            try:
                conversation = openai_client.conversations.create()

                # First streaming request - triggers MCP tool
                stream = openai_client.responses.create(
                    conversation=conversation.id,
                    input="Please summarize the Azure REST API specifications Readme",
                    stream=True,
                    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
                )

                # Collect approval requests from stream
                input_list = []
                for event in stream:
                    if hasattr(event, "type") and event.type == "response.output_item.done":
                        if hasattr(event, "item") and hasattr(event.item, "type"):
                            if event.item.type == "mcp_approval_request":
                                if hasattr(event.item, "server_label") and event.item.server_label == "api-specs":
                                    if hasattr(event.item, "id") and event.item.id:
                                        input_list.append(
                                            McpApprovalResponse(
                                                type="mcp_approval_response",
                                                approve=True,
                                                approval_request_id=event.item.id,
                                            )
                                        )

                # Send approval response as streaming
                stream2 = openai_client.responses.create(
                    conversation=conversation.id,
                    input=input_list,
                    stream=True,
                    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
                )

                # Consume second stream
                for event in stream2:
                    pass

                # Explicitly call and iterate through conversation items
                items = openai_client.conversations.items.list(conversation_id=conversation.id)
                for item in items:
                    pass

                # Check spans
                self.exporter.force_flush()
                spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_INVOKE_AGENT} {agent.name}")
                assert len(spans) == 2, "Should have two response spans (initial + approval)"

                # Validate first response span
                span1 = spans[0]
                assert span1.attributes is not None
                response_id_1 = span1.attributes.get("gen_ai.response.id")
                assert response_id_1 is not None

                expected_attributes_1 = [
                    ("az.namespace", "Microsoft.CognitiveServices"),
                    ("gen_ai.operation.name", OPERATION_NAME_INVOKE_AGENT),
                    ("gen_ai.provider.name", RESPONSES_PROVIDER),
                    ("server.address", ""),
                    ("gen_ai.conversation.id", conversation.id),
                    ("gen_ai.agent.name", agent.name),
                    ("gen_ai.response.model", deployment_name),
                    ("gen_ai.response.id", response_id_1),
                    ("gen_ai.usage.input_tokens", "+"),
                    ("gen_ai.usage.output_tokens", "+"),
                ]

                # Add message attributes when not using events
                if not use_events:
                    expected_attributes_1.extend(
                        [
                            ("gen_ai.input.messages", ""),
                            ("gen_ai.output.messages", ""),
                        ]
                    )

                assert GenAiTraceVerifier().check_span_attributes(span1, expected_attributes_1)

                # Comprehensive event validation - verify content IS present
                from collections.abc import Mapping

                for event in span1.events:
                    if event.name == "gen_ai.input.messages":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        import json

                        data = json.loads(content)
                        for entry in data:
                            if entry.get("role") == "user":
                                parts = entry.get("parts")
                                for part in parts:
                                    if part.get("type") == "text":
                                        assert (
                                            "content" in part
                                            and isinstance(part["content"], str)
                                            and part["content"].strip() != ""
                                        ), "Text content should be present when content recording is enabled"
                    elif event.name == "gen_ai.output.messages":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        import json

                        data = json.loads(content)
                        for entry in data:
                            parts = entry.get("parts")
                            if parts:
                                for part in parts:
                                    if part.get("type") == "tool_call":
                                        tool_content = part.get("content")
                                        if tool_content:
                                            tool_type = tool_content.get("type")
                                            if tool_type == "mcp_approval_request":
                                                assert (
                                                    "name" in tool_content
                                                ), "name should be present for mcp_approval_request when content recording is enabled"
                                                assert (
                                                    "arguments" in tool_content
                                                ), "arguments should be present for mcp_approval_request when content recording is enabled"

                # Validate second response span
                span2 = spans[1]
                assert span2.attributes is not None
                response_id_2 = span2.attributes.get("gen_ai.response.id")
                assert response_id_2 is not None

                expected_attributes_2 = [
                    ("az.namespace", "Microsoft.CognitiveServices"),
                    ("gen_ai.operation.name", OPERATION_NAME_INVOKE_AGENT),
                    ("gen_ai.provider.name", RESPONSES_PROVIDER),
                    ("server.address", ""),
                    ("gen_ai.conversation.id", conversation.id),
                    ("gen_ai.agent.name", agent.name),
                    ("gen_ai.response.model", deployment_name),
                    ("gen_ai.response.id", response_id_2),
                    ("gen_ai.usage.input_tokens", "+"),
                    ("gen_ai.usage.output_tokens", "+"),
                ]

                # Add message attributes when not using events
                if not use_events:
                    expected_attributes_2.extend(
                        [
                            ("gen_ai.input.messages", ""),
                            ("gen_ai.output.messages", ""),
                        ]
                    )

                assert GenAiTraceVerifier().check_span_attributes(span2, expected_attributes_2)

                # Validate second span events
                for event in span2.events:
                    if event.name == "gen_ai.output.messages":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        import json

                        data = json.loads(content)
                        for entry in data:
                            parts = entry.get("parts")
                            if parts:
                                for part in parts:
                                    if part.get("type") == "tool_call":
                                        tool_content = part.get("content")
                                        if tool_content and tool_content.get("type") == "mcp_call":
                                            assert (
                                                "name" in tool_content
                                            ), "name should be present for mcp_call when content recording is enabled"
                                            assert (
                                                "arguments" in tool_content
                                            ), "arguments should be present for mcp_call when content recording is enabled"
                                    elif part.get("type") == "text":
                                        assert (
                                            "content" in part
                                        ), "text content should be present when content recording is enabled"

                # Check list_conversation_items span
                list_spans = self.exporter.get_spans_by_name("list_conversation_items")
                assert len(list_spans) == 1
                list_span = list_spans[0]

                for event in list_span.events:
                    if event.name == "gen_ai.conversation.item":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        import json

                        data = json.loads(content)
                        for entry in data:
                            parts = entry.get("parts")
                            if parts:
                                for part in parts:
                                    if part.get("type") == "text":
                                        assert (
                                            "content" in part
                                        ), "text content should be present in conversation items when content recording is enabled"
                                    elif part.get("type") == "mcp":
                                        mcp_content = part.get("content")
                                        if mcp_content and mcp_content.get("type") == "mcp_call":
                                            assert (
                                                "name" in mcp_content
                                            ), "name should be present for mcp_call in conversation items when content recording is enabled"
                    else:
                        assert False, f"Unexpected event name in list_conversation_items span: {event.name}"

                # Cleanup
                openai_client.conversations.delete(conversation_id=conversation.id)

            finally:
                project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_sync_mcp_streaming_with_content_recording_events(self, **kwargs):
        """Test synchronous MCP agent with streaming and content recording enabled (event-based messages)."""
        self._test_sync_mcp_streaming_with_content_recording_impl(True, **kwargs)

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_sync_mcp_streaming_with_content_recording_attributes(self, **kwargs):
        """Test synchronous MCP agent with streaming and content recording enabled (attribute-based messages)."""
        self._test_sync_mcp_streaming_with_content_recording_impl(False, **kwargs)

    def _test_sync_mcp_streaming_without_content_recording_impl(self, use_events, **kwargs):
        """Implementation for testing synchronous MCP agent with streaming and content recording disabled.

        Args:
            use_events: If True, use event-based message tracing. If False, use attribute-based.
                       Note: MCP tests currently only validate event mode regardless of this setting.
        """
        self.cleanup()
        _set_use_message_events(use_events)
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

            # Create MCP tool
            mcp_tool = MCPTool(
                server_label="api-specs",
                server_url="https://gitmcp.io/Azure/azure-rest-api-specs",
                require_approval="always",
            )

            agent = project_client.agents.create_version(
                agent_name="MyAgent",
                definition=PromptAgentDefinition(
                    model=deployment_name,
                    instructions="You are a helpful agent that can use MCP tools to assist users.",
                    tools=[mcp_tool],
                ),
            )

            try:
                conversation = openai_client.conversations.create()

                # First streaming request - triggers MCP tool
                stream = openai_client.responses.create(
                    conversation=conversation.id,
                    input="Please summarize the Azure REST API specifications Readme",
                    stream=True,
                    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
                )

                # Collect approval requests from stream
                input_list = []
                for event in stream:
                    if hasattr(event, "type") and event.type == "response.output_item.done":
                        if hasattr(event, "item") and hasattr(event.item, "type"):
                            if event.item.type == "mcp_approval_request":
                                if hasattr(event.item, "server_label") and event.item.server_label == "api-specs":
                                    if hasattr(event.item, "id") and event.item.id:
                                        input_list.append(
                                            McpApprovalResponse(
                                                type="mcp_approval_response",
                                                approve=True,
                                                approval_request_id=event.item.id,
                                            )
                                        )

                # Send approval response as streaming
                stream2 = openai_client.responses.create(
                    conversation=conversation.id,
                    input=input_list,
                    stream=True,
                    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
                )

                # Consume second stream
                for event in stream2:
                    pass

                # Explicitly call and iterate through conversation items
                items = openai_client.conversations.items.list(conversation_id=conversation.id)
                for item in items:
                    pass

                # Check spans
                self.exporter.force_flush()
                spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_INVOKE_AGENT} {agent.name}")
                assert len(spans) == 2, "Should have two response spans (initial + approval)"

                # Validate first response span
                span1 = spans[0]
                assert span1.attributes is not None
                response_id_1 = span1.attributes.get("gen_ai.response.id")
                assert response_id_1 is not None

                expected_attributes_1 = [
                    ("az.namespace", "Microsoft.CognitiveServices"),
                    ("gen_ai.operation.name", OPERATION_NAME_INVOKE_AGENT),
                    ("gen_ai.provider.name", RESPONSES_PROVIDER),
                    ("server.address", ""),
                    ("gen_ai.conversation.id", conversation.id),
                    ("gen_ai.agent.name", agent.name),
                    ("gen_ai.response.model", deployment_name),
                    ("gen_ai.response.id", response_id_1),
                    ("gen_ai.usage.input_tokens", "+"),
                    ("gen_ai.usage.output_tokens", "+"),
                ]

                # Add message attributes when not using events
                if not use_events:
                    expected_attributes_1.extend(
                        [
                            ("gen_ai.input.messages", ""),
                            ("gen_ai.output.messages", ""),
                        ]
                    )

                assert GenAiTraceVerifier().check_span_attributes(span1, expected_attributes_1)

                # Comprehensive event validation - verify content is NOT present
                from collections.abc import Mapping

                for event in span1.events:
                    if event.name == "gen_ai.input.messages":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        import json

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
                        import json

                        data = json.loads(content)
                        for entry in data:
                            parts = entry.get("parts")
                            if parts:
                                for part in parts:
                                    if part.get("type") == "tool_call":
                                        tool_content = part.get("content")
                                        if tool_content:
                                            tool_type = tool_content.get("type")
                                            if tool_type == "mcp_approval_request":
                                                assert (
                                                    "name" not in tool_content
                                                ), "name should NOT be present for mcp_approval_request when content recording is disabled"
                                                assert (
                                                    "arguments" not in tool_content
                                                ), "arguments should NOT be present for mcp_approval_request when content recording is disabled"

                # Validate second response span
                span2 = spans[1]
                assert span2.attributes is not None
                response_id_2 = span2.attributes.get("gen_ai.response.id")
                assert response_id_2 is not None

                expected_attributes_2 = [
                    ("az.namespace", "Microsoft.CognitiveServices"),
                    ("gen_ai.operation.name", OPERATION_NAME_INVOKE_AGENT),
                    ("gen_ai.provider.name", RESPONSES_PROVIDER),
                    ("server.address", ""),
                    ("gen_ai.conversation.id", conversation.id),
                    ("gen_ai.agent.name", agent.name),
                    ("gen_ai.response.model", deployment_name),
                    ("gen_ai.response.id", response_id_2),
                    ("gen_ai.usage.input_tokens", "+"),
                    ("gen_ai.usage.output_tokens", "+"),
                ]

                # Add message attributes when not using events
                if not use_events:
                    expected_attributes_2.extend(
                        [
                            ("gen_ai.input.messages", ""),
                            ("gen_ai.output.messages", ""),
                        ]
                    )

                assert GenAiTraceVerifier().check_span_attributes(span2, expected_attributes_2)

                # Validate second span events - content should be minimal
                for event in span2.events:
                    if event.name == "gen_ai.output.messages":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        import json

                        data = json.loads(content)
                        for entry in data:
                            parts = entry.get("parts")
                            if parts:
                                for part in parts:
                                    if part.get("type") == "tool_call":
                                        tool_content = part.get("content")
                                        if tool_content and tool_content.get("type") == "mcp_call":
                                            assert (
                                                "name" not in tool_content
                                            ), "name should NOT be present for mcp_call when content recording is disabled"
                                            assert (
                                                "arguments" not in tool_content
                                            ), "arguments should NOT be present for mcp_call when content recording is disabled"
                                    elif part.get("type") == "text":
                                        assert (
                                            "content" not in part
                                        ), "text content should NOT be present when content recording is disabled"

                # Check list_conversation_items span
                list_spans = self.exporter.get_spans_by_name("list_conversation_items")
                assert len(list_spans) == 1
                list_span = list_spans[0]

                for event in list_span.events:
                    if event.name == "gen_ai.conversation.item":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        import json

                        data = json.loads(content)
                        for entry in data:
                            parts = entry.get("parts")
                            if parts:
                                for part in parts:
                                    if part.get("type") == "text":
                                        assert (
                                            "content" not in part
                                        ), "text content should NOT be present in conversation items when content recording is disabled"
                                    elif part.get("type") == "mcp":
                                        mcp_content = part.get("content")
                                        if mcp_content and mcp_content.get("type") == "mcp_call":
                                            assert (
                                                "name" not in mcp_content
                                            ), "name should NOT be present for mcp_call in conversation items when content recording is disabled"
                    else:
                        assert False, f"Unexpected event name in list_conversation_items span: {event.name}"

                # Cleanup
                openai_client.conversations.delete(conversation_id=conversation.id)

            finally:
                project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_sync_mcp_streaming_without_content_recording_events(self, **kwargs):
        """Test synchronous MCP agent with streaming and content recording disabled (event-based messages)."""
        self._test_sync_mcp_streaming_without_content_recording_impl(True, **kwargs)

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_sync_mcp_streaming_without_content_recording_attributes(self, **kwargs):
        """Test synchronous MCP agent with streaming and content recording disabled (attribute-based messages)."""
        self._test_sync_mcp_streaming_without_content_recording_impl(False, **kwargs)
