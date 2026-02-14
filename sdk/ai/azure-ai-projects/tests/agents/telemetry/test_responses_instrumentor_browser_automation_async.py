# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Async tests for ResponsesInstrumentor with browser automation agents.
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
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import RecordedTransport
from azure.ai.projects.models import PromptAgentDefinition

from test_base import servicePreparer
from test_ai_instrumentor_base import (
    TestAiAgentsInstrumentorBase,
    CONTENT_TRACING_ENV_VARIABLE,
)

import json

settings.tracing_implementation = "OpenTelemetry"
_utils._span_impl_type = settings.tracing_implementation()


@pytest.mark.skip(
    reason="Skipped until re-enabled and recorded on Foundry endpoint that supports the new versioning schema"
)
class TestResponsesInstrumentorBrowserAutomationAsync(TestAiAgentsInstrumentorBase):
    """Async tests for ResponsesInstrumentor with browser automation agents."""

    # ========================================
    # Async Browser Automation Tests - Non-Streaming
    # ========================================

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_async_browser_automation_non_streaming_with_content_recording(self, **kwargs):
        """Test asynchronous browser automation agent with non-streaming and content recording enabled."""
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

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")
        browser_automation_connection_id = kwargs.get("browser_automation_project_connection_id")
        assert deployment_name is not None
        if browser_automation_connection_id is None:
            pytest.skip("browser_automation_project_connection_id not configured")

        async with project_client:
            openai_client = project_client.get_openai_client()

            from azure.ai.projects.models import (
                BrowserAutomationPreviewTool,
                BrowserAutomationToolParameters,
                BrowserAutomationToolConnectionParameters,
            )

            tool = BrowserAutomationPreviewTool(
                browser_automation_preview=BrowserAutomationToolParameters(
                    connection=BrowserAutomationToolConnectionParameters(
                        project_connection_id=browser_automation_connection_id,
                    )
                )
            )

            agent = await project_client.agents.create_version(
                agent_name="MyAgent",
                definition=PromptAgentDefinition(
                    model=deployment_name,
                    instructions="""You are an Agent helping with browser automation tasks.""",
                    tools=[tool],
                ),
            )

            try:
                conversation = await openai_client.conversations.create()
                response = await openai_client.responses.create(
                    conversation=conversation.id,
                    tool_choice="required",
                    input="""
                          Your task is to get the latests news story from Microsoft website.
                          Go to the website https://news.microsoft.com and click the "What's new today" link at the top of the page to open the latest
                          news stories and provide a summary of the most recent one.
                          """,
                    stream=False,
                    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
                )

                assert response.output is not None
                assert len(response.output) > 0

                self.exporter.force_flush()
                spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_INVOKE_AGENT} {agent.name}")
                assert len(spans) == 1
                span = spans[0]

                expected_attributes = [
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
                assert GenAiTraceVerifier().check_span_attributes(span, expected_attributes)

                tool_call_events = [e for e in span.events if e.name == "gen_ai.output.messages"]
                assert len(tool_call_events) > 0
                found_browser_tool = False
                for event in tool_call_events:
                    if event.attributes and "gen_ai.event.content" in event.attributes:
                        content = event.attributes["gen_ai.event.content"]
                        if isinstance(content, str) and "browser_automation_preview_call" in content:
                            found_browser_tool = True
                            assert "arguments" in content or "query" in content
                assert found_browser_tool

                # Comprehensive event content validation - verify content IS present
                from collections.abc import Mapping

                for event in span.events:
                    if event.name == "gen_ai.input.messages":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)
                        assert isinstance(data, list) and len(data) > 0
                        # Check that content fields ARE present with content recording ON
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
                        data = json.loads(content)
                        assert isinstance(data, list) and len(data) > 0

                await openai_client.conversations.delete(conversation_id=conversation.id)
            finally:
                await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_async_browser_automation_non_streaming_without_content_recording(self, **kwargs):
        """Test asynchronous browser automation agent with non-streaming and content recording disabled."""
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

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")
        browser_automation_connection_id = kwargs.get("browser_automation_project_connection_id")
        assert deployment_name is not None
        if browser_automation_connection_id is None:
            pytest.skip("browser_automation_project_connection_id not configured")

        async with project_client:
            openai_client = project_client.get_openai_client()

            from azure.ai.projects.models import (
                BrowserAutomationPreviewTool,
                BrowserAutomationToolParameters,
                BrowserAutomationToolConnectionParameters,
            )

            tool = BrowserAutomationPreviewTool(
                browser_automation_preview=BrowserAutomationToolParameters(
                    connection=BrowserAutomationToolConnectionParameters(
                        project_connection_id=browser_automation_connection_id,
                    )
                )
            )

            agent = await project_client.agents.create_version(
                agent_name="MyAgent",
                definition=PromptAgentDefinition(
                    model=deployment_name,
                    instructions="""You are an Agent helping with browser automation tasks.""",
                    tools=[tool],
                ),
            )

            try:
                conversation = await openai_client.conversations.create()
                response = await openai_client.responses.create(
                    conversation=conversation.id,
                    tool_choice="required",
                    input="""
                          Your task is to get the latests news story from Microsoft website.
                          Go to the website https://news.microsoft.com and click the "What's new today" link at the top of the page to open the latest
                          news stories and provide a summary of the most recent one.
                          """,
                    stream=False,
                    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
                )

                self.exporter.force_flush()
                spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_INVOKE_AGENT} {agent.name}")
                assert len(spans) == 1
                span = spans[0]

                expected_attributes = [
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
                assert GenAiTraceVerifier().check_span_attributes(span, expected_attributes)

                tool_call_events = [e for e in span.events if e.name == "gen_ai.output.messages"]
                for event in tool_call_events:
                    if event.attributes and "gen_ai.event.content" in event.attributes:
                        content = event.attributes["gen_ai.event.content"]
                        if isinstance(content, str) and "browser_automation_preview_call" in content:
                            assert '"id"' in content

                # Comprehensive event content validation - verify content is NOT present
                from collections.abc import Mapping

                for event in span.events:
                    if event.name == "gen_ai.input.messages":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)
                        assert isinstance(data, list) and len(data) > 0
                        # Check that content fields are NOT present with content recording OFF
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
                        data = json.loads(content)
                        assert isinstance(data, list) and len(data) > 0

                await openai_client.conversations.delete(conversation_id=conversation.id)
            finally:
                await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

    # ========================================
    # Async Browser Automation Tests - Streaming
    # ========================================

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_async_browser_automation_streaming_with_content_recording(self, **kwargs):
        """Test asynchronous browser automation agent with streaming and content recording enabled."""
        self.cleanup()
        _set_use_message_events(True)
        os.environ.update(
            {CONTENT_TRACING_ENV_VARIABLE: "True", "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True"}
        )
        self.setup_telemetry()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")
        browser_automation_connection_id = kwargs.get("browser_automation_project_connection_id")
        assert deployment_name is not None
        if browser_automation_connection_id is None:
            pytest.skip("browser_automation_project_connection_id not configured")

        async with project_client:
            openai_client = project_client.get_openai_client()

            from azure.ai.projects.models import (
                BrowserAutomationPreviewTool,
                BrowserAutomationToolParameters,
                BrowserAutomationToolConnectionParameters,
            )

            tool = BrowserAutomationPreviewTool(
                browser_automation_preview=BrowserAutomationToolParameters(
                    connection=BrowserAutomationToolConnectionParameters(
                        project_connection_id=browser_automation_connection_id
                    )
                )
            )
            agent = await project_client.agents.create_version(
                agent_name="MyAgent",
                definition=PromptAgentDefinition(
                    model=deployment_name, instructions="""Browser automation helper.""", tools=[tool]
                ),
            )

            try:
                conversation = await openai_client.conversations.create()
                stream = await openai_client.responses.create(
                    conversation=conversation.id,
                    tool_choice="required",
                    input="""
                          Your task is to get the latests news story from Microsoft website.
                          Go to the website https://news.microsoft.com and click the "What's new today" link at the top of the page to open the latest
                          news stories and provide a summary of the most recent one.
                          """,
                    stream=True,
                    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
                )
                async for _ in stream:
                    pass

                self.exporter.force_flush()
                spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_INVOKE_AGENT} {agent.name}")
                assert len(spans) == 1
                span = spans[0]

                # Get response ID from span
                assert span.attributes is not None, "Span should have attributes"
                response_id = span.attributes.get("gen_ai.response.id")
                assert response_id is not None, "Response ID should be present in span"

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

                tool_call_events = [e for e in span.events if e.name == "gen_ai.output.messages"]
                assert len(tool_call_events) > 0

                # Strict event content checks for response generation span
                from collections.abc import Mapping

                for event in span.events:
                    if event.name == "gen_ai.input.messages":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)
                        assert isinstance(data, list) and len(data) > 0
                        first = data[0]
                        assert first.get("role") in ("user", "tool")
                        assert isinstance(first.get("parts"), list) and len(first["parts"]) > 0
                        # Validate content fields ARE present when content recording is enabled
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
                    if event.name == "gen_ai.output.messages":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)
                        assert isinstance(data, list) and len(data) > 0
                        first = data[0]
                        assert first.get("role") in ("assistant", "tool")
                        assert isinstance(first.get("parts"), list) and len(first["parts"]) > 0

                await openai_client.conversations.delete(conversation_id=conversation.id)
            finally:
                await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_async_browser_automation_streaming_without_content_recording(self, **kwargs):
        """Test asynchronous browser automation agent with streaming and content recording disabled."""
        self.cleanup()
        _set_use_message_events(True)
        os.environ.update(
            {CONTENT_TRACING_ENV_VARIABLE: "False", "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True"}
        )
        self.setup_telemetry()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")
        browser_automation_connection_id = kwargs.get("browser_automation_project_connection_id")
        assert deployment_name is not None
        if browser_automation_connection_id is None:
            pytest.skip("browser_automation_project_connection_id not configured")

        async with project_client:
            openai_client = project_client.get_openai_client()

            from azure.ai.projects.models import (
                BrowserAutomationPreviewTool,
                BrowserAutomationToolParameters,
                BrowserAutomationToolConnectionParameters,
            )

            tool = BrowserAutomationPreviewTool(
                browser_automation_preview=BrowserAutomationToolParameters(
                    connection=BrowserAutomationToolConnectionParameters(
                        project_connection_id=browser_automation_connection_id
                    )
                )
            )
            agent = await project_client.agents.create_version(
                agent_name="MyAgent",
                definition=PromptAgentDefinition(model=deployment_name, instructions="Browser helper.", tools=[tool]),
            )

            try:
                conversation = await openai_client.conversations.create()
                stream = await openai_client.responses.create(
                    conversation=conversation.id,
                    tool_choice="required",
                    input="""
                          Your task is to get the latests news story from Microsoft website.
                          Go to the website https://news.microsoft.com and click the "What's new today" link at the top of the page to open the latest
                          news stories and provide a summary of the most recent one.
                          """,
                    stream=True,
                    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
                )
                async for _ in stream:
                    pass

                self.exporter.force_flush()
                spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_INVOKE_AGENT} {agent.name}")
                assert len(spans) == 1
                span = spans[0]

                # Get response ID from span
                assert span.attributes is not None, "Span should have attributes"
                response_id = span.attributes.get("gen_ai.response.id")
                assert response_id is not None, "Response ID should be present in span"

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

                # Strict event content checks for response generation span - verify content recording is OFF
                from collections.abc import Mapping

                for event in span.events:
                    if event.name == "gen_ai.input.messages":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)
                        assert isinstance(data, list) and len(data) > 0
                        first = data[0]
                        assert first.get("role") in ("user", "tool")
                        assert isinstance(first.get("parts"), list) and len(first["parts"]) > 0
                        # Validate content fields are NOT present when content recording is disabled
                        for entry in data:
                            if entry.get("role") == "user":
                                parts = entry.get("parts")
                                for part in parts:
                                    if part.get("type") == "text":
                                        assert (
                                            "content" not in part
                                        ), "Text content should NOT be present when content recording is disabled"
                    if event.name == "gen_ai.output.messages":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)
                        assert isinstance(data, list) and len(data) > 0
                        first = data[0]
                        assert first.get("role") in ("assistant", "tool")
                        assert isinstance(first.get("parts"), list) and len(first["parts"]) > 0

                await openai_client.conversations.delete(conversation_id=conversation.id)
            finally:
                await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
