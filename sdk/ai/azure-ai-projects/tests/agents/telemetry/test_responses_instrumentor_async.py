# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import pytest
from azure.ai.projects.telemetry import AIProjectInstrumentor, _utils
from azure.core.settings import settings
from gen_ai_trace_verifier import GenAiTraceVerifier

from devtools_testutils.aio import recorded_by_proxy_async

from test_base import servicePreparer
from test_ai_instrumentor_base import TestAiAgentsInstrumentorBase, CONTENT_TRACING_ENV_VARIABLE

settings.tracing_implementation = "OpenTelemetry"
_utils._span_impl_type = settings.tracing_implementation()


class TestResponsesInstrumentor(TestAiAgentsInstrumentorBase):
    """Tests for ResponsesInstrumentor with real endpoints (async)."""

    @pytest.mark.skip(reason="recordings not working for responses API")
    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_async_non_streaming_with_content_recording(self, **kwargs):
        """Test asynchronous non-streaming responses with content recording enabled."""
        self.cleanup()
        os.environ.update(
            {CONTENT_TRACING_ENV_VARIABLE: "True", "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True"}
        )
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = self.test_agents_params["model_deployment_name"]

        async with project_client:
            # Get the OpenAI client from the project client
            client = await project_client.get_openai_client()

            # Create a conversation
            conversation = await client.conversations.create()

            # Create responses and call create method
            result = await client.responses.create(
                model=deployment_name, conversation=conversation.id, input="Write a short poem about AI", stream=False
            )

            # Verify the response exists
            assert hasattr(result, "output")
            assert result.output is not None

        # Check spans
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"responses {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Check span attributes
        expected_attributes = [
            ("az.namespace", "Microsoft.CognitiveServices"),
            ("gen_ai.operation.name", "responses"),
            ("gen_ai.request.model", deployment_name),
            ("gen_ai.provider.name", "azure.openai"),
            ("server.address", ""),
            ("gen_ai.conversation.id", conversation.id),
            ("gen_ai.response.model", deployment_name),
            ("gen_ai.response.id", ""),
            ("gen_ai.usage.input_tokens", "+"),
            ("gen_ai.usage.output_tokens", "+"),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        # Check span events
        expected_events = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "user",
                    "gen_ai.event.content": '{"role": "user", "content": "Write a short poem about AI"}',
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": '{"role": "assistant", "content": "*"}',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.skip(reason="recordings not working for responses API")
    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_async_streaming_with_content_recording(self, **kwargs):
        """Test asynchronous streaming responses with content recording enabled."""
        self.cleanup()
        os.environ.update(
            {CONTENT_TRACING_ENV_VARIABLE: "True", "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True"}
        )
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = self.test_agents_params["model_deployment_name"]

        async with project_client:
            # Get the OpenAI client from the project client
            client = await project_client.get_openai_client()

            # Create a conversation
            conversation = await client.conversations.create()

            # Create streaming responses and call create method
            stream = await client.responses.create(
                model=deployment_name, conversation=conversation.id, input="Write a short poem about AI", stream=True
            )

            # Consume the stream
            accumulated_content = []
            async for chunk in stream:
                if hasattr(chunk, "delta") and isinstance(chunk.delta, str):
                    accumulated_content.append(chunk.delta)
                elif hasattr(chunk, "output") and chunk.output:
                    accumulated_content.append(chunk.output)

            full_content = "".join(accumulated_content)
            assert full_content is not None
            assert len(full_content) > 0

        # Check spans
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"responses {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Check span attributes
        expected_attributes = [
            ("az.namespace", "Microsoft.CognitiveServices"),
            ("gen_ai.operation.name", "responses"),
            ("gen_ai.request.model", deployment_name),
            ("gen_ai.provider.name", "azure.openai"),
            ("server.address", ""),
            ("gen_ai.conversation.id", conversation.id),
            ("gen_ai.response.model", deployment_name),
            ("gen_ai.response.id", ""),
            ("gen_ai.usage.input_tokens", "+"),
            ("gen_ai.usage.output_tokens", "+"),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        # Check span events (should include assistant message for streaming)
        expected_events = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "user",
                    "gen_ai.event.content": '{"role": "user", "content": "Write a short poem about AI"}',
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": '{"role": "assistant", "content": "*"}',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.skip(reason="recordings not working for responses API")
    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_async_conversations_create(self, **kwargs):
        """Test asynchronous conversations.create() method."""
        self.cleanup()
        os.environ.update(
            {CONTENT_TRACING_ENV_VARIABLE: "True", "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True"}
        )
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = self.test_agents_params["model_deployment_name"]

        async with project_client:
            # Get the OpenAI client from the project client
            client = await project_client.get_openai_client()

            # Create a conversation
            conversation = await client.conversations.create()

            # Verify the conversation was created
            assert hasattr(conversation, "id")
            assert conversation.id is not None

        # Check spans - conversations.create should be traced
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name("create_conversation")
        assert len(spans) == 1
        span = spans[0]

        # Check basic span attributes
        expected_attributes = [
            ("az.namespace", "Microsoft.CognitiveServices"),
            ("gen_ai.operation.name", "create_conversation"),
            ("gen_ai.provider.name", "azure.openai"),
            ("server.address", ""),
            ("gen_ai.conversation.id", conversation.id),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

    @pytest.mark.skip(reason="recordings not working for responses API")
    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_async_list_conversation_items_with_content_recording(self, **kwargs):
        """Test asynchronous list_conversation_items with content recording enabled."""
        self.cleanup()
        os.environ.update(
            {CONTENT_TRACING_ENV_VARIABLE: "True", "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True"}
        )
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = self.test_agents_params["model_deployment_name"]

        async with project_client:
            # Get the OpenAI client from the project client
            client = await project_client.get_openai_client()

            # Create a conversation
            conversation = await client.conversations.create()

            # Add some responses to create items
            await client.responses.create(
                model=deployment_name, conversation=conversation.id, input="Hello", stream=False
            )

            # List conversation items
            items = await client.conversations.items.list(conversation_id=conversation.id)
            items_list = []
            async for item in items:
                items_list.append(item)
            assert len(items_list) > 0

        # Check spans
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name("list_conversation_items")
        assert len(spans) == 1
        span = spans[0]

        # Check span attributes
        expected_attributes = [
            ("az.namespace", "Microsoft.CognitiveServices"),
            ("gen_ai.operation.name", "list_conversation_items"),
            ("gen_ai.provider.name", "azure.openai"),
            ("server.address", ""),
            ("gen_ai.conversation.id", conversation.id),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True
