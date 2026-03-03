# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import json
import pytest
from azure.ai.projects.telemetry import AIProjectInstrumentor, _utils
from azure.ai.projects.telemetry._utils import (
    OPERATION_NAME_CHAT,
    OPERATION_NAME_INVOKE_AGENT,
    SPAN_NAME_CHAT,
    SPAN_NAME_INVOKE_AGENT,
    _set_use_message_events,
    _set_use_simple_tool_format,
    RESPONSES_PROVIDER,
)
from azure.ai.projects.models import FunctionTool, PromptAgentDefinition
from azure.core.settings import settings
from gen_ai_trace_verifier import GenAiTraceVerifier
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import RecordedTransport
from test_base import servicePreparer
from test_ai_instrumentor_base import (
    TestAiAgentsInstrumentorBase,
    CONTENT_TRACING_ENV_VARIABLE,
)

BINARY_DATA_TRACING_ENV_VARIABLE = "AZURE_TRACING_GEN_AI_INCLUDE_BINARY_DATA"

# Base64 encoded small test image (1x1 PNG)
TEST_IMAGE_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

settings.tracing_implementation = "OpenTelemetry"
_utils._span_impl_type = settings.tracing_implementation()


@pytest.mark.skip(
    reason="Skipped until re-enabled and recorded on Foundry endpoint that supports the new versioning schema"
)
class TestResponsesInstrumentor(TestAiAgentsInstrumentorBase):
    """Tests for ResponsesInstrumentor with real endpoints (async)."""

    async def _test_async_non_streaming_with_content_recording_impl(self, use_events, **kwargs):
        """Implementation for testing asynchronous non-streaming responses with content recording.

        Args:
            use_events: If True, use event-based message tracing. If False, use attribute-based.
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
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")

        async with project_client:
            # Get the OpenAI client from the project client
            client = project_client.get_openai_client()

            # Create a conversation
            conversation = await client.conversations.create()

            # Create responses and call create method
            result = await client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input="Write a short poem about AI",
                stream=False,
            )

            # Verify the response exists
            assert hasattr(result, "output")
            assert result.output is not None

        # Check spans
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_CHAT} {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Check span attributes
        expected_attributes = [
            ("az.namespace", "Microsoft.CognitiveServices"),
            ("gen_ai.operation.name", OPERATION_NAME_CHAT),
            ("gen_ai.request.model", deployment_name),
            ("gen_ai.provider.name", RESPONSES_PROVIDER),
            ("server.address", ""),
            ("gen_ai.conversation.id", conversation.id),
            ("gen_ai.response.model", deployment_name),
            ("gen_ai.response.id", ""),
            ("gen_ai.usage.input_tokens", "+"),
            ("gen_ai.usage.output_tokens", "+"),
        ]
        if not use_events:
            expected_attributes.extend(
                [
                    ("gen_ai.input.messages", ""),
                    ("gen_ai.output.messages", ""),
                ]
            )
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        # Check span events (only in events mode)
        if use_events:
            expected_events = [
                {
                    "name": "gen_ai.input.messages",
                    "attributes": {
                        "gen_ai.provider.name": RESPONSES_PROVIDER,
                        # "gen_ai.message.role": "user",  # Commented out - now in event content
                        "gen_ai.event.content": '[{"role": "user", "parts": [{"type": "text", "content": "Write a short poem about AI"}]}]',
                    },
                },
                {
                    "name": "gen_ai.output.messages",
                    "attributes": {
                        "gen_ai.provider.name": RESPONSES_PROVIDER,
                        # "gen_ai.message.role": "assistant",  # Commented out - now in event content
                        "gen_ai.event.content": '[{"role": "assistant", "parts": [{"type": "text", "content": "*"}], "finish_reason": "*"}]',
                    },
                },
            ]
            events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
            assert events_match == True

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_async_non_streaming_with_content_recording_events(self, **kwargs):
        """Test asynchronous non-streaming responses with content recording enabled (event-based messages)."""
        await self._test_async_non_streaming_with_content_recording_impl(True, **kwargs)

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_async_non_streaming_with_content_recording_attributes(self, **kwargs):
        """Test asynchronous non-streaming responses with content recording enabled (attribute-based messages)."""
        await self._test_async_non_streaming_with_content_recording_impl(False, **kwargs)

    async def _test_async_streaming_with_content_recording_impl(self, use_events, **kwargs):
        """Implementation for testing asynchronous streaming responses with content recording.

        Args:
            use_events: If True, use event-based message tracing. If False, use attribute-based.
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
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")

        async with project_client:
            # Get the OpenAI client from the project client
            client = project_client.get_openai_client()

            # Create a conversation
            conversation = await client.conversations.create()

            # Create streaming responses and call create method
            stream = await client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input="Write a short poem about AI",
                stream=True,
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
        spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_CHAT} {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Check span attributes
        expected_attributes = [
            ("az.namespace", "Microsoft.CognitiveServices"),
            ("gen_ai.operation.name", OPERATION_NAME_CHAT),
            ("gen_ai.request.model", deployment_name),
            ("gen_ai.provider.name", RESPONSES_PROVIDER),
            ("server.address", ""),
            ("gen_ai.conversation.id", conversation.id),
            ("gen_ai.response.model", deployment_name),
            ("gen_ai.response.id", ""),
            ("gen_ai.usage.input_tokens", "+"),
            ("gen_ai.usage.output_tokens", "+"),
        ]
        if not use_events:
            expected_attributes.extend(
                [
                    ("gen_ai.input.messages", ""),
                    ("gen_ai.output.messages", ""),
                ]
            )
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        # Check span events (only in events mode)
        if use_events:
            expected_events = [
                {
                    "name": "gen_ai.input.messages",
                    "attributes": {
                        "gen_ai.provider.name": RESPONSES_PROVIDER,
                        # "gen_ai.message.role": "user",  # Commented out - now in event content
                        "gen_ai.event.content": '[{"role": "user", "parts": [{"type": "text", "content": "Write a short poem about AI"}]}]',
                    },
                },
                {
                    "name": "gen_ai.output.messages",
                    "attributes": {
                        "gen_ai.provider.name": RESPONSES_PROVIDER,
                        # "gen_ai.message.role": "assistant",  # Commented out - now in event content
                        "gen_ai.event.content": '[{"role": "assistant", "parts": [{"type": "text", "content": "*"}], "finish_reason": "*"}]',
                    },
                },
            ]
            events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
            assert events_match == True

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_async_streaming_with_content_recording_events(self, **kwargs):
        """Test asynchronous streaming responses with content recording enabled (event-based messages)."""
        await self._test_async_streaming_with_content_recording_impl(True, **kwargs)

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_async_streaming_with_content_recording_attributes(self, **kwargs):
        """Test asynchronous streaming responses with content recording enabled (attribute-based messages)."""
        await self._test_async_streaming_with_content_recording_impl(False, **kwargs)

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_async_conversations_create(self, **kwargs):
        """Test asynchronous conversations.create() method."""
        self.cleanup()
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "True",
                "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True",
            }
        )
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")

        async with project_client:
            # Get the OpenAI client from the project client
            client = project_client.get_openai_client()

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
            ("gen_ai.provider.name", RESPONSES_PROVIDER),
            ("server.address", ""),
            ("gen_ai.conversation.id", conversation.id),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_async_list_conversation_items_with_content_recording(self, **kwargs):
        """Test asynchronous list_conversation_items with content recording enabled."""
        self.cleanup()
        _set_use_message_events(True)  # Use event-based mode for this test
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "True",
                "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True",
            }
        )
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")

        async with project_client:
            # Get the OpenAI client from the project client
            client = project_client.get_openai_client()

            # Create a conversation
            conversation = await client.conversations.create()

            # Add some responses to create items
            await client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input="Hello",
                stream=False,
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
            ("gen_ai.provider.name", RESPONSES_PROVIDER),
            ("server.address", ""),
            ("gen_ai.conversation.id", conversation.id),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        # Check span events - should have assistant and user message events with content (API returns newest first)
        expected_events = [
            {
                "name": "gen_ai.conversation.item",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    "gen_ai.conversation.item.id": "*",
                    "gen_ai.event.content": '[{"role": "assistant", "parts": [{"type": "text", "content": "*"}]}]',
                },
            },
            {
                "name": "gen_ai.conversation.item",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    "gen_ai.conversation.item.id": "*",
                    "gen_ai.event.content": '[{"role": "user", "parts": [{"type": "text", "content": "Hello"}]}]',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    async def _test_async_function_tool_with_content_recording_streaming_impl(
        self, use_events, use_simple_tool_call_format=False, **kwargs
    ):
        """Implementation for testing asynchronous function tool usage with content recording (streaming).

        Args:
            use_events: If True, use event-based message tracing. If False, use attribute-based.
            use_simple_tool_call_format: If True, use simple OTEL-compliant tool call format.
        """
        from openai.types.responses.response_input_param import FunctionCallOutput

        self.cleanup()
        _set_use_message_events(use_events)
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "True",
                "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True",
            }
        )
        self.setup_telemetry()
        _set_use_simple_tool_format(use_simple_tool_call_format)
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)

        async with project_client:
            # Get the OpenAI client from the project client
            client = project_client.get_openai_client()
            deployment_name = kwargs.get("azure_ai_model_deployment_name")

            # Define a function tool
            func_tool = FunctionTool(
                name="get_weather",
                parameters={
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city name, e.g. San Francisco",
                        },
                    },
                    "required": ["location"],
                    "additionalProperties": False,
                },
                description="Get the current weather for a location.",
                strict=True,
            )

            # Create agent with function tool
            agent = await project_client.agents.create_version(
                agent_name="WeatherAgent",
                definition=PromptAgentDefinition(
                    model=deployment_name,
                    instructions="You are a helpful assistant that can use function tools.",
                    tools=[func_tool],
                ),
            )

            # Create a conversation
            conversation = await client.conversations.create()

            # First request - should trigger function call
            stream = await client.responses.create(
                conversation=conversation.id,
                input="What's the weather in Seattle?",
                extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
                stream=True,
            )
            # Consume the stream and collect function calls
            # In streaming, we get events, not direct output items
            function_calls_dict = {}
            first_response_id = None
            async for chunk in stream:
                # Capture the response ID from ResponseCreatedEvent or ResponseCompletedEvent
                if chunk.type == "response.created" and hasattr(chunk, "response"):
                    first_response_id = chunk.response.id
                elif chunk.type == "response.completed" and hasattr(chunk, "response"):
                    if first_response_id is None:
                        first_response_id = chunk.response.id

                # Collect complete function calls from ResponseOutputItemDoneEvent
                if chunk.type == "response.output_item.done" and hasattr(chunk, "item"):
                    item = chunk.item
                    if hasattr(item, "type") and item.type == "function_call":
                        call_id = item.call_id
                        function_calls_dict[call_id] = item

            # Process function calls and prepare input for second request
            input_list = []
            for item in function_calls_dict.values():
                # Mock function result
                weather_result = {"temperature": "72°F", "condition": "sunny"}
                output = FunctionCallOutput(
                    type="function_call_output",
                    call_id=item.call_id,
                    output=json.dumps(weather_result),
                )
                input_list.append(output)

            # Second request - provide function results (using conversation, not previous_response_id)
            stream2 = await client.responses.create(
                conversation=conversation.id,
                input=input_list,
                extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
                stream=True,
            )
            # Consume the second stream
            accumulated_content = []
            async for chunk in stream2:
                if hasattr(chunk, "delta") and isinstance(chunk.delta, str):
                    accumulated_content.append(chunk.delta)
                elif hasattr(chunk, "output") and chunk.output:
                    accumulated_content.append(str(chunk.output))
            full_content = "".join(accumulated_content)
            assert full_content is not None
            assert len(full_content) > 0

            # Cleanup
            await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

        # Check spans - should have 2 responses spans
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_INVOKE_AGENT} {agent.name}")
        assert len(spans) == 2

        # Validate first span (user message + tool call)
        span1 = spans[0]
        expected_attributes_1 = [
            ("az.namespace", "Microsoft.CognitiveServices"),
            ("gen_ai.operation.name", OPERATION_NAME_INVOKE_AGENT),
            ("gen_ai.agent.name", agent.name),
            ("gen_ai.provider.name", RESPONSES_PROVIDER),
            ("server.address", ""),
            ("gen_ai.conversation.id", conversation.id),
            ("gen_ai.response.model", deployment_name),
            ("gen_ai.response.id", ""),
            ("gen_ai.usage.input_tokens", "+"),
            ("gen_ai.usage.output_tokens", "+"),
        ]
        if not use_events:
            expected_attributes_1.extend(
                [
                    ("gen_ai.input.messages", ""),
                    ("gen_ai.output.messages", ""),
                ]
            )
        attributes_match = GenAiTraceVerifier().check_span_attributes(span1, expected_attributes_1)
        assert attributes_match == True

        # Check events for first span - user message and assistant tool call (only in events mode)
        if use_events:
            # Tool call format depends on use_simple_tool_call_format flag
            if use_simple_tool_call_format:
                tool_call_content = '[{"role": "assistant", "parts": [{"type": "tool_call", "id": "*", "name": "get_weather", "arguments": "*"}]}]'
            else:
                tool_call_content = '[{"role": "assistant", "parts": [{"type": "tool_call", "content": {"type": "function_call", "id": "*", "function": {"name": "get_weather", "arguments": "*"}}}]}]'

            expected_events_1 = [
                {
                    "name": "gen_ai.input.messages",
                    "attributes": {
                        "gen_ai.provider.name": RESPONSES_PROVIDER,
                        "gen_ai.event.content": '[{"role": "user", "parts": [{"type": "text", "content": "What\'s the weather in Seattle?"}]}]',
                    },
                },
                {
                    "name": "gen_ai.output.messages",
                    "attributes": {
                        "gen_ai.provider.name": RESPONSES_PROVIDER,
                        "gen_ai.event.content": tool_call_content,
                    },
                },
            ]
            events_match = GenAiTraceVerifier().check_span_events(span1, expected_events_1)
            assert events_match == True

        # Validate second span (tool output + final response)
        span2 = spans[1]
        expected_attributes_2 = [
            ("az.namespace", "Microsoft.CognitiveServices"),
            ("gen_ai.operation.name", OPERATION_NAME_INVOKE_AGENT),
            ("gen_ai.agent.name", agent.name),
            ("gen_ai.provider.name", RESPONSES_PROVIDER),
            ("server.address", ""),
            ("gen_ai.conversation.id", conversation.id),
            ("gen_ai.response.model", deployment_name),
            ("gen_ai.response.id", ""),
            ("gen_ai.usage.input_tokens", "+"),
            ("gen_ai.usage.output_tokens", "+"),
        ]
        if not use_events:
            # Span2 has both input messages (tool output) and output messages (assistant response)
            expected_attributes_2.extend(
                [
                    ("gen_ai.input.messages", ""),
                    ("gen_ai.output.messages", ""),
                ]
            )
        attributes_match = GenAiTraceVerifier().check_span_attributes(span2, expected_attributes_2)
        assert attributes_match == True

        # Check events for second span - tool output and assistant response (only in events mode)
        if use_events:
            # Tool output format depends on use_simple_tool_call_format flag
            if use_simple_tool_call_format:
                tool_output_content = '[{"role": "tool", "parts": [{"type": "tool_call_response", "id": "*", "result": {"temperature": "72°F", "condition": "sunny"}}]}]'
            else:
                tool_output_content = '[{"role": "tool", "parts": [{"type": "tool_call_output", "content": {"type": "function_call_output", "id": "*", "output": {"temperature": "72°F", "condition": "sunny"}}}]}]'

            expected_events_2 = [
                {
                    "name": "gen_ai.input.messages",
                    "attributes": {
                        "gen_ai.provider.name": RESPONSES_PROVIDER,
                        "gen_ai.event.content": tool_output_content,
                    },
                },
                {
                    "name": "gen_ai.output.messages",
                    "attributes": {
                        "gen_ai.provider.name": RESPONSES_PROVIDER,
                        "gen_ai.event.content": '[{"role": "assistant", "parts": [{"type": "text", "content": "*"}], "finish_reason": "*"}]',
                    },
                },
            ]
            events_match = GenAiTraceVerifier().check_span_events(span2, expected_events_2)
            assert events_match == True

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_async_function_tool_with_content_recording_streaming_events(self, **kwargs):
        """Test asynchronous function tool usage with content recording enabled (streaming, event-based messages)."""
        await self._test_async_function_tool_with_content_recording_streaming_impl(True, **kwargs)

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_async_function_tool_with_content_recording_streaming_attributes(self, **kwargs):
        """Test asynchronous function tool usage with content recording enabled (streaming, attribute-based messages)."""
        await self._test_async_function_tool_with_content_recording_streaming_impl(False, **kwargs)

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_async_function_tool_with_content_recording_streaming_simple_format_events(self, **kwargs):
        """Test async function tool with content recording, streaming, simple OTEL format (event mode)."""
        await self._test_async_function_tool_with_content_recording_streaming_impl(
            True, use_simple_tool_call_format=True, **kwargs
        )

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_async_function_tool_with_content_recording_streaming_simple_format_attributes(self, **kwargs):
        """Test async function tool with content recording, streaming, simple OTEL format (attribute mode)."""
        await self._test_async_function_tool_with_content_recording_streaming_impl(
            False, use_simple_tool_call_format=True, **kwargs
        )

    async def _test_async_function_tool_without_content_recording_streaming_impl(
        self, use_events, use_simple_tool_call_format=False, **kwargs
    ):
        """Implementation for testing asynchronous function tool usage without content recording (streaming).

        Args:
            use_events: If True, use event-based message tracing. If False, use attribute-based.
            use_simple_tool_call_format: If True, use simple OTEL-compliant tool call format.
        """
        from openai.types.responses.response_input_param import FunctionCallOutput

        self.cleanup()
        _set_use_message_events(use_events)
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "False",
                "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True",
            }
        )
        self.setup_telemetry()
        _set_use_simple_tool_format(use_simple_tool_call_format)
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)

        async with project_client:
            # Get the OpenAI client from the project client
            client = project_client.get_openai_client()
            deployment_name = kwargs.get("azure_ai_model_deployment_name")

            # Define a function tool
            func_tool = FunctionTool(
                name="get_weather",
                parameters={
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city name, e.g. San Francisco",
                        },
                    },
                    "required": ["location"],
                    "additionalProperties": False,
                },
                description="Get the current weather for a location.",
                strict=True,
            )

            # Create agent with function tool
            agent = await project_client.agents.create_version(
                agent_name="WeatherAgent",
                definition=PromptAgentDefinition(
                    model=deployment_name,
                    instructions="You are a helpful assistant that can use function tools.",
                    tools=[func_tool],
                ),
            )

            # Create a conversation
            conversation = await client.conversations.create()

            # First request - should trigger function call
            stream = await client.responses.create(
                conversation=conversation.id,
                input="What\\'s the weather in Seattle?",
                extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
                stream=True,
            )
            # Consume the stream and collect function calls
            # In streaming, we get events, not direct output items
            function_calls_dict = {}
            first_response_id = None
            async for chunk in stream:
                # Capture the response ID from ResponseCreatedEvent or ResponseCompletedEvent
                if chunk.type == "response.created" and hasattr(chunk, "response"):
                    first_response_id = chunk.response.id
                elif chunk.type == "response.completed" and hasattr(chunk, "response"):
                    if first_response_id is None:
                        first_response_id = chunk.response.id

                # Collect complete function calls from ResponseOutputItemDoneEvent
                if chunk.type == "response.output_item.done" and hasattr(chunk, "item"):
                    item = chunk.item
                    if hasattr(item, "type") and item.type == "function_call":
                        call_id = item.call_id
                        function_calls_dict[call_id] = item

            # Process function calls and prepare input for second request
            # Respond to ALL function calls (streaming may not populate name attribute reliably)
            input_list = []
            for item in function_calls_dict.values():
                # Mock function result
                weather_result = {"temperature": "72°F", "condition": "sunny"}
                output = FunctionCallOutput(
                    type="function_call_output",
                    call_id=item.call_id,
                    output=json.dumps(weather_result),
                )
                input_list.append(output)

            # Second request - provide function results (using conversation, not previous_response_id)
            stream2 = await client.responses.create(
                conversation=conversation.id,
                input=input_list,
                extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
                stream=True,
            )
            # Consume the second stream
            async for chunk in stream2:
                pass  # Just consume the stream

            # Cleanup
            await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

        # Check spans - should have 2 responses spans
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_INVOKE_AGENT} {agent.name}")
        assert len(spans) == 2

        # Validate first span (user message + tool call) - no content
        span1 = spans[0]
        expected_attributes_1 = [
            ("az.namespace", "Microsoft.CognitiveServices"),
            ("gen_ai.operation.name", OPERATION_NAME_INVOKE_AGENT),
            ("gen_ai.agent.name", agent.name),
            ("gen_ai.provider.name", RESPONSES_PROVIDER),
            ("server.address", ""),
            ("gen_ai.conversation.id", conversation.id),
            ("gen_ai.response.model", deployment_name),
            ("gen_ai.response.id", ""),
            ("gen_ai.usage.input_tokens", "+"),
            ("gen_ai.usage.output_tokens", "+"),
        ]
        if not use_events:
            expected_attributes_1.extend(
                [
                    ("gen_ai.input.messages", ""),
                    ("gen_ai.output.messages", ""),
                ]
            )
        attributes_match = GenAiTraceVerifier().check_span_attributes(span1, expected_attributes_1)
        assert attributes_match == True

        # Check events for first span - tool call ID included but no function details (only in events mode)
        if use_events:
            # Tool call format depends on use_simple_tool_call_format flag
            if use_simple_tool_call_format:
                tool_call_content = '[{"role": "assistant", "parts": [{"type": "tool_call", "id": "*"}]}]'
            else:
                tool_call_content = '[{"role": "assistant", "parts": [{"type": "tool_call", "content": {"type": "function_call", "id": "*"}}]}]'

            expected_events_1 = [
                {
                    "name": "gen_ai.input.messages",
                    "attributes": {
                        "gen_ai.provider.name": RESPONSES_PROVIDER,
                        "gen_ai.event.content": '[{"role": "user", "parts": [{"type": "text"}]}]',
                    },
                },
                {
                    "name": "gen_ai.output.messages",
                    "attributes": {
                        "gen_ai.provider.name": RESPONSES_PROVIDER,
                        "gen_ai.event.content": tool_call_content,
                    },
                },
            ]
            events_match = GenAiTraceVerifier().check_span_events(span1, expected_events_1)
            assert events_match == True

        # Validate second span (tool output + final response) - no content
        span2 = spans[1]
        expected_attributes_2 = [
            ("az.namespace", "Microsoft.CognitiveServices"),
            ("gen_ai.operation.name", OPERATION_NAME_INVOKE_AGENT),
            ("gen_ai.agent.name", agent.name),
            ("gen_ai.provider.name", RESPONSES_PROVIDER),
            ("server.address", ""),
            ("gen_ai.conversation.id", conversation.id),
            ("gen_ai.response.model", deployment_name),
            ("gen_ai.response.id", ""),
            ("gen_ai.usage.input_tokens", "+"),
            ("gen_ai.usage.output_tokens", "+"),
        ]
        if not use_events:
            # Span2 has both input messages (tool output) and output messages (assistant response)
            expected_attributes_2.extend(
                [
                    ("gen_ai.input.messages", ""),
                    ("gen_ai.output.messages", ""),
                ]
            )
        attributes_match = GenAiTraceVerifier().check_span_attributes(span2, expected_attributes_2)
        assert attributes_match == True

        # Check events for second span - tool output metadata and response (only in events mode)
        if use_events:
            # Tool output format depends on use_simple_tool_call_format flag
            if use_simple_tool_call_format:
                tool_output_content = '[{"role": "tool", "parts": [{"type": "tool_call_response", "id": "*"}]}]'
            else:
                tool_output_content = '[{"role": "tool", "parts": [{"type": "tool_call_output", "content": {"type": "function_call_output", "id": "*"}}]}]'

            expected_events_2 = [
                {
                    "name": "gen_ai.input.messages",
                    "attributes": {
                        "gen_ai.provider.name": RESPONSES_PROVIDER,
                        "gen_ai.event.content": tool_output_content,
                    },
                },
                {
                    "name": "gen_ai.output.messages",
                    "attributes": {
                        "gen_ai.provider.name": RESPONSES_PROVIDER,
                        "gen_ai.event.content": '[{"role": "assistant", "parts": [{"type": "text"}], "finish_reason": "*"}]',
                    },
                },
            ]
            events_match = GenAiTraceVerifier().check_span_events(span2, expected_events_2)
            assert events_match == True

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_async_function_tool_without_content_recording_streaming_events(self, **kwargs):
        """Test asynchronous function tool usage without content recording (streaming, event-based messages)."""
        await self._test_async_function_tool_without_content_recording_streaming_impl(True, **kwargs)

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_async_function_tool_without_content_recording_streaming_attributes(self, **kwargs):
        """Test asynchronous function tool usage without content recording (streaming, attribute-based messages)."""
        await self._test_async_function_tool_without_content_recording_streaming_impl(False, **kwargs)

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_async_function_tool_without_content_recording_streaming_simple_format_events(self, **kwargs):
        """Test async function tool without content recording, streaming, simple OTEL format (event mode)."""
        await self._test_async_function_tool_without_content_recording_streaming_impl(
            True, use_simple_tool_call_format=True, **kwargs
        )

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_async_function_tool_without_content_recording_streaming_simple_format_attributes(self, **kwargs):
        """Test async function tool without content recording, streaming, simple OTEL format (attribute mode)."""
        await self._test_async_function_tool_without_content_recording_streaming_impl(
            False, use_simple_tool_call_format=True, **kwargs
        )

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_async_multiple_text_inputs_with_content_recording_non_streaming(self, **kwargs):
        """Test asynchronous non-streaming responses with multiple text inputs and content recording enabled."""
        self.cleanup()
        _set_use_message_events(True)  # Use event-based mode for this test
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "True",
                "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True",
            }
        )
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        async with self.create_async_client(operation_group="tracing", **kwargs) as project_client:
            # Get the OpenAI client from the project client
            client = project_client.get_openai_client()
            deployment_name = kwargs.get("azure_ai_model_deployment_name")

            # Create a conversation
            conversation = await client.conversations.create()

            # Create responses with multiple text inputs as a list
            input_list = [
                {"role": "user", "content": [{"type": "input_text", "text": "Hello"}]},
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": "Write a haiku about Python"}],
                },
            ]

            result = await client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input=input_list,
                stream=False,
            )

            # Verify the response exists
            assert hasattr(result, "output")
            assert result.output is not None

        # Check spans
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_CHAT} {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Check span attributes
        expected_attributes = [
            ("az.namespace", "Microsoft.CognitiveServices"),
            ("gen_ai.operation.name", OPERATION_NAME_CHAT),
            ("gen_ai.request.model", deployment_name),
            ("gen_ai.provider.name", RESPONSES_PROVIDER),
            ("server.address", ""),
            ("gen_ai.conversation.id", conversation.id),
            ("gen_ai.response.model", deployment_name),
            ("gen_ai.response.id", ""),
            ("gen_ai.usage.input_tokens", "+"),
            ("gen_ai.usage.output_tokens", "+"),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        # Check span events - should have 2 user messages and 1 assistant message
        expected_events = [
            {
                "name": "gen_ai.input.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "user",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "user", "parts": [{"type": "text", "content": "Hello"}]}]',
                },
            },
            {
                "name": "gen_ai.input.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "user",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "user", "parts": [{"type": "text", "content": "Write a haiku about Python"}]}]',
                },
            },
            {
                "name": "gen_ai.output.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "assistant",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "assistant", "parts": [{"type": "text", "content": "*"}], "finish_reason": "*"}]',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_async_multiple_text_inputs_with_content_recording_streaming(self, **kwargs):
        """Test asynchronous streaming responses with multiple text inputs and content recording enabled."""
        self.cleanup()
        _set_use_message_events(True)  # Use event-based mode for this test
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "True",
                "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True",
            }
        )
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        async with self.create_async_client(operation_group="tracing", **kwargs) as project_client:
            # Get the OpenAI client from the project client
            client = project_client.get_openai_client()
            deployment_name = kwargs.get("azure_ai_model_deployment_name")

            # Create a conversation
            conversation = await client.conversations.create()

            # Create responses with multiple text inputs as a list
            input_list = [
                {"role": "user", "content": [{"type": "input_text", "text": "Hello"}]},
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": "Write a haiku about Python"}],
                },
            ]

            stream = await client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input=input_list,
                stream=True,
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
        spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_CHAT} {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Check span attributes
        expected_attributes = [
            ("az.namespace", "Microsoft.CognitiveServices"),
            ("gen_ai.operation.name", OPERATION_NAME_CHAT),
            ("gen_ai.request.model", deployment_name),
            ("gen_ai.provider.name", RESPONSES_PROVIDER),
            ("server.address", ""),
            ("gen_ai.conversation.id", conversation.id),
            ("gen_ai.response.model", deployment_name),
            ("gen_ai.response.id", ""),
            ("gen_ai.usage.input_tokens", "+"),
            ("gen_ai.usage.output_tokens", "+"),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        # Check span events - should have 2 user messages and 1 assistant message
        expected_events = [
            {
                "name": "gen_ai.input.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "user",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "user", "parts": [{"type": "text", "content": "Hello"}]}]',
                },
            },
            {
                "name": "gen_ai.input.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "user",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "user", "parts": [{"type": "text", "content": "Write a haiku about Python"}]}]',
                },
            },
            {
                "name": "gen_ai.output.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "assistant",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "assistant", "parts": [{"type": "text", "content": "*"}], "finish_reason": "*"}]',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_async_multiple_text_inputs_without_content_recording_non_streaming(self, **kwargs):
        """Test asynchronous non-streaming responses with multiple text inputs and content recording disabled."""
        self.cleanup()
        _set_use_message_events(True)  # Use event-based mode for this test
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "False",
                "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True",
            }
        )
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        async with self.create_async_client(operation_group="tracing", **kwargs) as project_client:
            # Get the OpenAI client from the project client
            client = project_client.get_openai_client()
            deployment_name = kwargs.get("azure_ai_model_deployment_name")

            # Create a conversation
            conversation = await client.conversations.create()

            # Create responses with multiple text inputs as a list
            input_list = [
                {"role": "user", "content": [{"type": "input_text", "text": "Hello"}]},
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": "Write a haiku about Python"}],
                },
            ]

            result = await client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input=input_list,
                stream=False,
            )

            # Verify the response exists
            assert hasattr(result, "output")
            assert result.output is not None

        # Check spans
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_CHAT} {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Check span attributes
        expected_attributes = [
            ("az.namespace", "Microsoft.CognitiveServices"),
            ("gen_ai.operation.name", OPERATION_NAME_CHAT),
            ("gen_ai.request.model", deployment_name),
            ("gen_ai.provider.name", RESPONSES_PROVIDER),
            ("server.address", ""),
            ("gen_ai.conversation.id", conversation.id),
            ("gen_ai.response.model", deployment_name),
            ("gen_ai.response.id", ""),
            ("gen_ai.usage.input_tokens", "+"),
            ("gen_ai.usage.output_tokens", "+"),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        # Check span events - should have 2 user messages and 1 assistant message, role included but no content
        expected_events = [
            {
                "name": "gen_ai.input.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "user",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "user", "parts": [{"type": "text"}]}]',
                },
            },
            {
                "name": "gen_ai.input.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "user",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "user", "parts": [{"type": "text"}]}]',
                },
            },
            {
                "name": "gen_ai.output.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "assistant",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "assistant", "parts": [{"type": "text"}], "finish_reason": "*"}]',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    # ========================================
    # Binary Data Tracing Tests (Image Only)
    # ========================================

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_async_image_only_content_off_binary_off_non_streaming(self, **kwargs):
        """Test image only with content recording OFF and binary data OFF (non-streaming)."""
        self.cleanup()
        _set_use_message_events(True)  # Use event-based mode for this test
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "False",
                BINARY_DATA_TRACING_ENV_VARIABLE: "False",
            }
        )
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")

        async with project_client:
            client = project_client.get_openai_client()
            conversation = await client.conversations.create()

            # Send only an image (no text)
            result = await client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_image",
                                "image_url": f"data:image/png;base64,{TEST_IMAGE_BASE64}",
                            }
                        ],
                    }
                ],
                stream=False,
            )

            assert hasattr(result, "output")
            assert result.output is not None

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_CHAT} {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Content recording OFF: event content should have role, parts with type only, and finish_reason
        expected_events = [
            {
                "name": "gen_ai.input.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "user",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "user", "parts": [{"type": "image"}]}]',
                },
            },
            {
                "name": "gen_ai.output.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "assistant",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "assistant", "parts": [{"type": "text"}], "finish_reason": "*"}]',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_async_image_only_content_off_binary_on_non_streaming(self, **kwargs):
        """Test image only with content recording OFF and binary data ON (non-streaming)."""
        self.cleanup()
        _set_use_message_events(True)  # Use event-based mode for this test
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "False",
                BINARY_DATA_TRACING_ENV_VARIABLE: "True",
            }
        )
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")

        async with project_client:
            client = project_client.get_openai_client()
            conversation = await client.conversations.create()

            result = await client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_image",
                                "image_url": f"data:image/png;base64,{TEST_IMAGE_BASE64}",
                            }
                        ],
                    }
                ],
                stream=False,
            )

            assert hasattr(result, "output")
            assert result.output is not None

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_CHAT} {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Content recording OFF: event content should have role, parts with type only, and finish_reason (binary flag doesn't matter)
        expected_events = [
            {
                "name": "gen_ai.input.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "user",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "user", "parts": [{"type": "image"}]}]',
                },
            },
            {
                "name": "gen_ai.output.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "assistant",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "assistant", "parts": [{"type": "text"}], "finish_reason": "*"}]',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_async_image_only_content_on_binary_off_non_streaming(self, **kwargs):
        """Test image only with content recording ON and binary data OFF (non-streaming)."""
        self.cleanup()
        _set_use_message_events(True)  # Use event-based mode for this test
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "True",
                BINARY_DATA_TRACING_ENV_VARIABLE: "False",
            }
        )
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")

        async with project_client:
            client = project_client.get_openai_client()
            conversation = await client.conversations.create()

            result = await client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_image",
                                "image_url": f"data:image/png;base64,{TEST_IMAGE_BASE64}",
                            }
                        ],
                    }
                ],
                stream=False,
            )

            assert hasattr(result, "output")
            assert result.output is not None

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_CHAT} {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Content recording ON, binary OFF: should have image type but no image_url
        expected_events = [
            {
                "name": "gen_ai.input.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "user",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role":"user","parts":[{"type":"image"}]}]',
                },
            },
            {
                "name": "gen_ai.output.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "assistant",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "assistant", "parts": [{"type": "text", "content": "*"}], "finish_reason": "*"}]',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_async_image_only_content_on_binary_on_non_streaming(self, **kwargs):
        """Test image only with content recording ON and binary data ON (non-streaming)."""
        self.cleanup()
        _set_use_message_events(True)  # Use event-based mode for this test
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "True",
                BINARY_DATA_TRACING_ENV_VARIABLE: "True",
            }
        )
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")

        async with project_client:
            client = project_client.get_openai_client()
            conversation = await client.conversations.create()

            result = await client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_image",
                                "image_url": f"data:image/png;base64,{TEST_IMAGE_BASE64}",
                            }
                        ],
                    }
                ],
                stream=False,
            )

            assert hasattr(result, "output")
            assert result.output is not None

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_CHAT} {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Content recording ON, binary ON: should have image type AND image_url with base64 data
        expected_events = [
            {
                "name": "gen_ai.input.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "user",  # Commented out - now in event content
                    "gen_ai.event.content": f'[{{"role":"user","parts":[{{"type":"image","content":"data:image/png;base64,{TEST_IMAGE_BASE64}"}}]}}]',
                },
            },
            {
                "name": "gen_ai.output.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "assistant",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "assistant", "parts": [{"type": "text", "content": "*"}], "finish_reason": "*"}]',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    # ========================================
    # Binary Data Tracing Tests (Text + Image)
    # ========================================

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_async_text_and_image_content_off_binary_off_non_streaming(self, **kwargs):
        """Test text + image with content recording OFF and binary data OFF (non-streaming)."""
        self.cleanup()
        _set_use_message_events(True)  # Use event-based mode for this test
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "False",
                BINARY_DATA_TRACING_ENV_VARIABLE: "False",
            }
        )
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")

        async with project_client:
            client = project_client.get_openai_client()
            conversation = await client.conversations.create()

            # Send text + image
            result = await client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": "What is shown in this image?",
                            },
                            {
                                "type": "input_image",
                                "image_url": f"data:image/png;base64,{TEST_IMAGE_BASE64}",
                            },
                        ],
                    }
                ],
                stream=False,
            )

            assert hasattr(result, "output")
            assert result.output is not None

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_CHAT} {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Content recording OFF: event content should have role, parts with type only, and finish_reason
        expected_events = [
            {
                "name": "gen_ai.input.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "user",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "user", "parts": [{"type": "text"}, {"type": "image"}]}]',
                },
            },
            {
                "name": "gen_ai.output.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "assistant",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "assistant", "parts": [{"type": "text"}], "finish_reason": "*"}]',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_async_text_and_image_content_off_binary_on_non_streaming(self, **kwargs):
        """Test text + image with content recording OFF and binary data ON (non-streaming)."""
        self.cleanup()
        _set_use_message_events(True)  # Use event-based mode for this test
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "False",
                BINARY_DATA_TRACING_ENV_VARIABLE: "True",
            }
        )
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")

        async with project_client:
            client = project_client.get_openai_client()
            conversation = await client.conversations.create()

            result = await client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": "What is shown in this image?",
                            },
                            {
                                "type": "input_image",
                                "image_url": f"data:image/png;base64,{TEST_IMAGE_BASE64}",
                            },
                        ],
                    }
                ],
                stream=False,
            )

            assert hasattr(result, "output")
            assert result.output is not None

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_CHAT} {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Content recording OFF: event content should have role, parts with type only, and finish_reason (binary flag doesn't matter)
        expected_events = [
            {
                "name": "gen_ai.input.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "user",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "user", "parts": [{"type": "text"}, {"type": "image"}]}]',
                },
            },
            {
                "name": "gen_ai.output.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "assistant",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "assistant", "parts": [{"type": "text"}], "finish_reason": "*"}]',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_async_text_and_image_content_on_binary_off_non_streaming(self, **kwargs):
        """Test text + image with content recording ON and binary data OFF (non-streaming)."""
        self.cleanup()
        _set_use_message_events(True)  # Use event-based mode for this test
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "True",
                BINARY_DATA_TRACING_ENV_VARIABLE: "False",
            }
        )
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")

        async with project_client:
            client = project_client.get_openai_client()
            conversation = await client.conversations.create()

            result = await client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": "What is shown in this image?",
                            },
                            {
                                "type": "input_image",
                                "image_url": f"data:image/png;base64,{TEST_IMAGE_BASE64}",
                            },
                        ],
                    }
                ],
                stream=False,
            )

            assert hasattr(result, "output")
            assert result.output is not None

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_CHAT} {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Content recording ON, binary OFF: should have text and image type but no image_url
        expected_events = [
            {
                "name": "gen_ai.input.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "user",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role":"user","parts":[{"type":"text","content":"What is shown in this image?"},{"type":"image"}]}]',
                },
            },
            {
                "name": "gen_ai.output.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "assistant",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "assistant", "parts": [{"type": "text", "content": "*"}], "finish_reason": "*"}]',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_async_text_and_image_content_on_binary_on_non_streaming(self, **kwargs):
        """Test text + image with content recording ON and binary data ON (non-streaming)."""
        self.cleanup()
        _set_use_message_events(True)  # Use event-based mode for this test
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "True",
                BINARY_DATA_TRACING_ENV_VARIABLE: "True",
            }
        )
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")

        async with project_client:
            client = project_client.get_openai_client()
            conversation = await client.conversations.create()

            result = await client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": "What is shown in this image?",
                            },
                            {
                                "type": "input_image",
                                "image_url": f"data:image/png;base64,{TEST_IMAGE_BASE64}",
                            },
                        ],
                    }
                ],
                stream=False,
            )

            assert hasattr(result, "output")
            assert result.output is not None

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_CHAT} {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Content recording ON, binary ON: should have text and image with full base64 data
        expected_events = [
            {
                "name": "gen_ai.input.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "user",  # Commented out - now in event content
                    "gen_ai.event.content": f'[{{"role":"user","parts":[{{"type":"text","content":"What is shown in this image?"}},{{"type":"image","content":"data:image/png;base64,{TEST_IMAGE_BASE64}"}}]}}]',
                },
            },
            {
                "name": "gen_ai.output.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "assistant",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "assistant", "parts": [{"type": "text", "content": "*"}], "finish_reason": "*"}]',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    # ========================================
    # Binary Data Tracing Tests - Streaming (Image Only)
    # ========================================

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_async_image_only_content_off_binary_off_streaming(self, **kwargs):
        """Test image only with content recording OFF and binary data OFF (streaming)."""
        self.cleanup()
        _set_use_message_events(True)  # Use event-based mode for this test
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "False",
                BINARY_DATA_TRACING_ENV_VARIABLE: "False",
            }
        )
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")

        async with project_client:
            client = project_client.get_openai_client()
            conversation = await client.conversations.create()

            stream = await client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_image",
                                "image_url": f"data:image/png;base64,{TEST_IMAGE_BASE64}",
                            }
                        ],
                    }
                ],
                stream=True,
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

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_CHAT} {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Content recording OFF: event content should have role, parts with type only, and finish_reason
        expected_events = [
            {
                "name": "gen_ai.input.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "user",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "user", "parts": [{"type": "image"}]}]',
                },
            },
            {
                "name": "gen_ai.output.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "assistant",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "assistant", "parts": [{"type": "text"}], "finish_reason": "*"}]',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_async_image_only_content_off_binary_on_streaming(self, **kwargs):
        """Test image only with content recording OFF and binary data ON (streaming)."""
        self.cleanup()
        _set_use_message_events(True)  # Use event-based mode for this test
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "False",
                BINARY_DATA_TRACING_ENV_VARIABLE: "True",
            }
        )
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")

        async with project_client:
            client = project_client.get_openai_client()
            conversation = await client.conversations.create()

            stream = await client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_image",
                                "image_url": f"data:image/png;base64,{TEST_IMAGE_BASE64}",
                            }
                        ],
                    }
                ],
                stream=True,
            )

            accumulated_content = []
            async for chunk in stream:
                if hasattr(chunk, "delta") and isinstance(chunk.delta, str):
                    accumulated_content.append(chunk.delta)
                elif hasattr(chunk, "output") and chunk.output:
                    accumulated_content.append(chunk.output)

            full_content = "".join(accumulated_content)
            assert full_content is not None
            assert len(full_content) > 0

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_CHAT} {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Content recording OFF: event content should have role, parts with type only, and finish_reason
        expected_events = [
            {
                "name": "gen_ai.input.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "user",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "user", "parts": [{"type": "image"}]}]',
                },
            },
            {
                "name": "gen_ai.output.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "assistant",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "assistant", "parts": [{"type": "text"}], "finish_reason": "*"}]',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_async_image_only_content_on_binary_off_streaming(self, **kwargs):
        """Test image only with content recording ON and binary data OFF (streaming)."""
        self.cleanup()
        _set_use_message_events(True)  # Use event-based mode for this test
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "True",
                BINARY_DATA_TRACING_ENV_VARIABLE: "False",
            }
        )
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")

        async with project_client:
            client = project_client.get_openai_client()
            conversation = await client.conversations.create()

            stream = await client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_image",
                                "image_url": f"data:image/png;base64,{TEST_IMAGE_BASE64}",
                            }
                        ],
                    }
                ],
                stream=True,
            )

            accumulated_content = []
            async for chunk in stream:
                if hasattr(chunk, "delta") and isinstance(chunk.delta, str):
                    accumulated_content.append(chunk.delta)
                elif hasattr(chunk, "output") and chunk.output:
                    accumulated_content.append(chunk.output)

            full_content = "".join(accumulated_content)
            assert full_content is not None
            assert len(full_content) > 0

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_CHAT} {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Content recording ON, binary OFF: should have image type but no image_url
        expected_events = [
            {
                "name": "gen_ai.input.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "user",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role":"user","parts":[{"type":"image"}]}]',
                },
            },
            {
                "name": "gen_ai.output.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "assistant",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "assistant", "parts": [{"type": "text", "content": "*"}], "finish_reason": "*"}]',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_async_image_only_content_on_binary_on_streaming(self, **kwargs):
        """Test image only with content recording ON and binary data ON (streaming)."""
        self.cleanup()
        _set_use_message_events(True)  # Use event-based mode for this test
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "True",
                BINARY_DATA_TRACING_ENV_VARIABLE: "True",
            }
        )
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")

        async with project_client:
            client = project_client.get_openai_client()
            conversation = await client.conversations.create()

            stream = await client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_image",
                                "image_url": f"data:image/png;base64,{TEST_IMAGE_BASE64}",
                            }
                        ],
                    }
                ],
                stream=True,
            )

            accumulated_content = []
            async for chunk in stream:
                if hasattr(chunk, "delta") and isinstance(chunk.delta, str):
                    accumulated_content.append(chunk.delta)
                elif hasattr(chunk, "output") and chunk.output:
                    accumulated_content.append(chunk.output)

            full_content = "".join(accumulated_content)
            assert full_content is not None
            assert len(full_content) > 0

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_CHAT} {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Content recording ON, binary ON: should have image type AND image_url with base64 data
        expected_events = [
            {
                "name": "gen_ai.input.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "user",  # Commented out - now in event content
                    "gen_ai.event.content": f'[{{"role":"user","parts":[{{"type":"image","content":"data:image/png;base64,{TEST_IMAGE_BASE64}"}}]}}]',
                },
            },
            {
                "name": "gen_ai.output.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "assistant",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "assistant", "parts": [{"type": "text", "content": "*"}], "finish_reason": "*"}]',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    # ========================================
    # Binary Data Tracing Tests - Streaming (Text + Image)
    # ========================================

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_async_text_and_image_content_off_binary_off_streaming(self, **kwargs):
        """Test text + image with content recording OFF and binary data OFF (streaming)."""
        self.cleanup()
        _set_use_message_events(True)  # Use event-based mode for this test
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "False",
                BINARY_DATA_TRACING_ENV_VARIABLE: "False",
            }
        )
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")

        async with project_client:
            client = project_client.get_openai_client()
            conversation = await client.conversations.create()

            stream = await client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": "What is shown in this image?",
                            },
                            {
                                "type": "input_image",
                                "image_url": f"data:image/png;base64,{TEST_IMAGE_BASE64}",
                            },
                        ],
                    }
                ],
                stream=True,
            )

            accumulated_content = []
            async for chunk in stream:
                if hasattr(chunk, "delta") and isinstance(chunk.delta, str):
                    accumulated_content.append(chunk.delta)
                elif hasattr(chunk, "output") and chunk.output:
                    accumulated_content.append(chunk.output)

            full_content = "".join(accumulated_content)
            assert full_content is not None
            assert len(full_content) > 0

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_CHAT} {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Content recording OFF: event content should have role, parts with type only, and finish_reason
        expected_events = [
            {
                "name": "gen_ai.input.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "user",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "user", "parts": [{"type": "text"}, {"type": "image"}]}]',
                },
            },
            {
                "name": "gen_ai.output.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "assistant",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "assistant", "parts": [{"type": "text"}], "finish_reason": "*"}]',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_async_text_and_image_content_off_binary_on_streaming(self, **kwargs):
        """Test text + image with content recording OFF and binary data ON (streaming)."""
        self.cleanup()
        _set_use_message_events(True)  # Use event-based mode for this test
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "False",
                BINARY_DATA_TRACING_ENV_VARIABLE: "True",
            }
        )
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")

        async with project_client:
            client = project_client.get_openai_client()
            conversation = await client.conversations.create()

            stream = await client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": "What is shown in this image?",
                            },
                            {
                                "type": "input_image",
                                "image_url": f"data:image/png;base64,{TEST_IMAGE_BASE64}",
                            },
                        ],
                    }
                ],
                stream=True,
            )

            accumulated_content = []
            async for chunk in stream:
                if hasattr(chunk, "delta") and isinstance(chunk.delta, str):
                    accumulated_content.append(chunk.delta)
                elif hasattr(chunk, "output") and chunk.output:
                    accumulated_content.append(chunk.output)

            full_content = "".join(accumulated_content)
            assert full_content is not None
            assert len(full_content) > 0

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_CHAT} {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Content recording OFF: event content should have role, parts with type only, and finish_reason
        expected_events = [
            {
                "name": "gen_ai.input.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "user",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "user", "parts": [{"type": "text"}, {"type": "image"}]}]',
                },
            },
            {
                "name": "gen_ai.output.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "assistant",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "assistant", "parts": [{"type": "text"}], "finish_reason": "*"}]',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_async_text_and_image_content_on_binary_off_streaming(self, **kwargs):
        """Test text + image with content recording ON and binary data OFF (streaming)."""
        self.cleanup()
        _set_use_message_events(True)  # Use event-based mode for this test
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "True",
                BINARY_DATA_TRACING_ENV_VARIABLE: "False",
            }
        )
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")

        async with project_client:
            client = project_client.get_openai_client()
            conversation = await client.conversations.create()

            stream = await client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": "What is shown in this image?",
                            },
                            {
                                "type": "input_image",
                                "image_url": f"data:image/png;base64,{TEST_IMAGE_BASE64}",
                            },
                        ],
                    }
                ],
                stream=True,
            )

            accumulated_content = []
            async for chunk in stream:
                if hasattr(chunk, "delta") and isinstance(chunk.delta, str):
                    accumulated_content.append(chunk.delta)
                elif hasattr(chunk, "output") and chunk.output:
                    accumulated_content.append(chunk.output)

            full_content = "".join(accumulated_content)
            assert full_content is not None
            assert len(full_content) > 0

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_CHAT} {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Content recording ON, binary OFF: should have text and image type but no image_url
        expected_events = [
            {
                "name": "gen_ai.input.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "user",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role":"user","parts":[{"type":"text","content":"What is shown in this image?"},{"type":"image"}]}]',
                },
            },
            {
                "name": "gen_ai.output.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "assistant",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "assistant", "parts": [{"type": "text", "content": "*"}], "finish_reason": "*"}]',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_async_text_and_image_content_on_binary_on_streaming(self, **kwargs):
        """Test text + image with content recording ON and binary data ON (streaming)."""
        self.cleanup()
        _set_use_message_events(True)  # Use event-based mode for this test
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "True",
                BINARY_DATA_TRACING_ENV_VARIABLE: "True",
            }
        )
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")

        async with project_client:
            client = project_client.get_openai_client()
            conversation = await client.conversations.create()

            stream = await client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": "What is shown in this image?",
                            },
                            {
                                "type": "input_image",
                                "image_url": f"data:image/png;base64,{TEST_IMAGE_BASE64}",
                            },
                        ],
                    }
                ],
                stream=True,
            )

            accumulated_content = []
            async for chunk in stream:
                if hasattr(chunk, "delta") and isinstance(chunk.delta, str):
                    accumulated_content.append(chunk.delta)
                elif hasattr(chunk, "output") and chunk.output:
                    accumulated_content.append(chunk.output)

            full_content = "".join(accumulated_content)
            assert full_content is not None
            assert len(full_content) > 0

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_CHAT} {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Content recording ON, binary ON: should have text and image with full base64 data
        expected_events = [
            {
                "name": "gen_ai.input.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "user",  # Commented out - now in event content
                    "gen_ai.event.content": f'[{{"role":"user","parts":[{{"type":"text","content":"What is shown in this image?"}},{{"type":"image","content":"data:image/png;base64,{TEST_IMAGE_BASE64}"}}]}}]',
                },
            },
            {
                "name": "gen_ai.output.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "assistant",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "assistant", "parts": [{"type": "text", "content": "*"}], "finish_reason": "*"}]',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_async_multiple_text_inputs_without_content_recording_streaming(self, **kwargs):
        """Test asynchronous streaming responses with multiple text inputs and content recording disabled."""
        self.cleanup()
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "False",
                "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True",
            }
        )
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        async with self.create_async_client(operation_group="tracing", **kwargs) as project_client:
            # Get the OpenAI client from the project client
            client = project_client.get_openai_client()
            deployment_name = kwargs.get("azure_ai_model_deployment_name")

            # Create a conversation
            conversation = await client.conversations.create()

            # Create responses with multiple text inputs as a list
            input_list = [
                {"role": "user", "content": [{"type": "input_text", "text": "Hello"}]},
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": "Write a haiku about Python"}],
                },
            ]

            stream = await client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input=input_list,
                stream=True,
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
        spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_CHAT} {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Check span attributes
        expected_attributes = [
            ("az.namespace", "Microsoft.CognitiveServices"),
            ("gen_ai.operation.name", OPERATION_NAME_CHAT),
            ("gen_ai.request.model", deployment_name),
            ("gen_ai.provider.name", RESPONSES_PROVIDER),
            ("server.address", ""),
            ("gen_ai.conversation.id", conversation.id),
            ("gen_ai.response.model", deployment_name),
            ("gen_ai.response.id", ""),
            ("gen_ai.usage.input_tokens", "+"),
            ("gen_ai.usage.output_tokens", "+"),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        # Check span events - should have 2 user messages and 1 assistant message with role and finish_reason
        expected_events = [
            {
                "name": "gen_ai.input.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "user",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "user", "parts": [{"type": "text"}]}]',
                },
            },
            {
                "name": "gen_ai.input.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "user",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "user", "parts": [{"type": "text"}]}]',
                },
            },
            {
                "name": "gen_ai.output.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "assistant",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "assistant", "parts": [{"type": "text"}], "finish_reason": "*"}]',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    # ========================================
    # responses.stream() Method Tests (Async)
    # ========================================

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_async_responses_stream_method_with_content_recording(self, **kwargs):
        """Test async responses.stream() method with content recording enabled."""
        self.cleanup()
        _set_use_message_events(True)  # Use event-based mode for this test
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "True",
                "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True",
            }
        )
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        async with self.create_async_client(operation_group="tracing", **kwargs) as project_client:
            client = project_client.get_openai_client()
            deployment_name = kwargs.get("azure_ai_model_deployment_name")

            conversation = await client.conversations.create()

            # Use async responses.stream() method
            async with client.responses.stream(
                conversation=conversation.id,
                model=deployment_name,
                input="Write a short haiku about testing",
            ) as stream:
                # Iterate through events
                async for event in stream:
                    pass  # Process events

                # Get final response
                final_response = await stream.get_final_response()
                assert final_response is not None

        # Check spans
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_CHAT} {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Check span attributes
        expected_attributes = [
            ("az.namespace", "Microsoft.CognitiveServices"),
            ("gen_ai.operation.name", OPERATION_NAME_CHAT),
            ("gen_ai.request.model", deployment_name),
            ("gen_ai.provider.name", RESPONSES_PROVIDER),
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
                "name": "gen_ai.input.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "user",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "user", "parts": [{"type": "text", "content": "Write a short haiku about testing"}]}]',
                },
            },
            {
                "name": "gen_ai.output.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "assistant",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "assistant", "parts": [{"type": "text", "content": "*"}], "finish_reason": "*"}]',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_async_responses_stream_method_without_content_recording(self, **kwargs):
        """Test async responses.stream() method without content recording."""
        self.cleanup()
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "False",
                "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True",
            }
        )
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        async with self.create_async_client(operation_group="tracing", **kwargs) as project_client:
            client = project_client.get_openai_client()
            deployment_name = kwargs.get("azure_ai_model_deployment_name")

            conversation = await client.conversations.create()

            # Use async responses.stream() method
            async with client.responses.stream(
                conversation=conversation.id,
                model=deployment_name,
                input="Write a short haiku about testing",
            ) as stream:
                # Iterate through events
                async for event in stream:
                    pass  # Process events

                # Get final response
                final_response = await stream.get_final_response()
                assert final_response is not None

        # Check spans
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_CHAT} {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Check span attributes
        expected_attributes = [
            ("az.namespace", "Microsoft.CognitiveServices"),
            ("gen_ai.operation.name", OPERATION_NAME_CHAT),
            ("gen_ai.request.model", deployment_name),
            ("gen_ai.provider.name", RESPONSES_PROVIDER),
            ("server.address", ""),
            ("gen_ai.conversation.id", conversation.id),
            ("gen_ai.response.model", deployment_name),
            ("gen_ai.response.id", ""),
            ("gen_ai.usage.input_tokens", "+"),
            ("gen_ai.usage.output_tokens", "+"),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        # Check span events - should have events with role and finish_reason
        expected_events = [
            {
                "name": "gen_ai.input.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "user",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "user", "parts": [{"type": "text"}]}]',
                },
            },
            {
                "name": "gen_ai.output.messages",
                "attributes": {
                    "gen_ai.provider.name": RESPONSES_PROVIDER,
                    # "gen_ai.message.role": "assistant",  # Commented out - now in event content
                    "gen_ai.event.content": '[{"role": "assistant", "parts": [{"type": "text"}], "finish_reason": "*"}]',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    async def _test_async_responses_stream_method_with_tools_with_content_recording_impl(
        self, use_events, use_simple_tool_call_format=False, **kwargs
    ):
        """Implementation for testing async responses.stream() method with function tools and content recording.

        Args:
            use_events: If True, use event-based message tracing. If False, use attribute-based.
            use_simple_tool_call_format: If True, use simple OTEL-compliant tool call format.
        """
        from openai.types.responses.response_input_param import FunctionCallOutput

        self.cleanup()
        _set_use_message_events(use_events)
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "True",
                "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True",
            }
        )
        self.setup_telemetry()
        _set_use_simple_tool_format(use_simple_tool_call_format)
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        async with self.create_async_client(operation_group="tracing", **kwargs) as project_client:
            client = project_client.get_openai_client()
            deployment_name = kwargs.get("azure_ai_model_deployment_name")

            # Define a function tool
            function_tool = FunctionTool(
                name="get_weather",
                description="Get the current weather for a location.",
                parameters={
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city name, e.g. San Francisco",
                        },
                    },
                    "required": ["location"],
                    "additionalProperties": False,
                },
                strict=True,
            )

            conversation = await client.conversations.create()

            # First request - should trigger function call
            function_calls = []
            async with client.responses.stream(
                conversation=conversation.id,
                model=deployment_name,
                input="What's the weather in Boston?",
                tools=[function_tool],
            ) as stream:
                async for event in stream:
                    pass  # Process events

                final_response = await stream.get_final_response()

                # Extract function calls
                if hasattr(final_response, "output") and final_response.output:
                    for item in final_response.output:
                        if hasattr(item, "type") and item.type == "function_call":
                            function_calls.append(item)

            assert len(function_calls) > 0

            # Prepare function output
            input_list = []
            for func_call in function_calls:
                weather_result = {"temperature": "65°F", "condition": "cloudy"}
                output = FunctionCallOutput(
                    type="function_call_output",
                    call_id=func_call.call_id,
                    output=json.dumps(weather_result),
                )
                input_list.append(output)

            # Second request - provide function results
            async with client.responses.stream(
                conversation=conversation.id,
                model=deployment_name,
                input=input_list,
                tools=[function_tool],
            ) as stream:
                async for event in stream:
                    pass  # Process events

                final_response = await stream.get_final_response()
                assert final_response is not None

        # Check spans - should have 2 responses spans
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_CHAT} {deployment_name}")
        assert len(spans) == 2

        # Validate first span (user message + tool call)
        span1 = spans[0]
        expected_attributes_1 = [
            ("az.namespace", "Microsoft.CognitiveServices"),
            ("gen_ai.operation.name", OPERATION_NAME_CHAT),
            ("gen_ai.request.model", deployment_name),
            ("gen_ai.provider.name", RESPONSES_PROVIDER),
            ("server.address", ""),
            ("gen_ai.conversation.id", conversation.id),
            ("gen_ai.response.model", deployment_name),
            ("gen_ai.response.id", ""),
            ("gen_ai.usage.input_tokens", "+"),
            ("gen_ai.usage.output_tokens", "+"),
        ]
        if not use_events:
            expected_attributes_1.extend(
                [
                    ("gen_ai.input.messages", ""),
                    ("gen_ai.output.messages", ""),
                ]
            )
        attributes_match = GenAiTraceVerifier().check_span_attributes(span1, expected_attributes_1)
        assert attributes_match == True

        # Check events for first span - tool call format depends on use_simple_tool_call_format flag (only in events mode)
        if use_events:
            if use_simple_tool_call_format:
                tool_call_content = '[{"role": "assistant", "parts": [{"type": "tool_call", "id": "*", "name": "get_weather", "arguments": "*"}]}]'
            else:
                tool_call_content = '[{"role": "assistant", "parts": [{"type": "tool_call", "content": {"type": "function_call", "id": "*", "function": {"name": "get_weather", "arguments": "*"}}}]}]'

            expected_events_1 = [
                {
                    "name": "gen_ai.input.messages",
                    "attributes": {
                        "gen_ai.provider.name": RESPONSES_PROVIDER,
                        "gen_ai.event.content": '[{"role": "user", "parts": [{"type": "text", "content": "What\'s the weather in Boston?"}]}]',
                    },
                },
                {
                    "name": "gen_ai.output.messages",
                    "attributes": {
                        "gen_ai.provider.name": RESPONSES_PROVIDER,
                        "gen_ai.event.content": tool_call_content,
                    },
                },
            ]
            events_match = GenAiTraceVerifier().check_span_events(span1, expected_events_1)
            assert events_match == True

        # Validate second span (tool output + final response)
        span2 = spans[1]
        expected_attributes_2 = [
            ("az.namespace", "Microsoft.CognitiveServices"),
            ("gen_ai.operation.name", OPERATION_NAME_CHAT),
            ("gen_ai.request.model", deployment_name),
            ("gen_ai.provider.name", RESPONSES_PROVIDER),
            ("server.address", ""),
            ("gen_ai.conversation.id", conversation.id),
            ("gen_ai.response.model", deployment_name),
            ("gen_ai.response.id", ""),
            ("gen_ai.usage.input_tokens", "+"),
            ("gen_ai.usage.output_tokens", "+"),
        ]
        if not use_events:
            expected_attributes_2.extend(
                [
                    ("gen_ai.input.messages", ""),
                    ("gen_ai.output.messages", ""),
                ]
            )
        attributes_match = GenAiTraceVerifier().check_span_attributes(span2, expected_attributes_2)
        assert attributes_match == True

        # Check events for second span (only in events mode)
        if use_events:
            # Tool output format depends on use_simple_tool_call_format flag
            if use_simple_tool_call_format:
                tool_output_content = '[{"role": "tool", "parts": [{"type": "tool_call_response", "id": "*", "result": {"temperature": "65°F", "condition": "cloudy"}}]}]'
            else:
                tool_output_content = '[{"role": "tool", "parts": [{"type": "tool_call_output", "content": {"type": "function_call_output", "id": "*", "output": {"temperature": "65°F", "condition": "cloudy"}}}]}]'

            expected_events_2 = [
                {
                    "name": "gen_ai.input.messages",
                    "attributes": {
                        "gen_ai.provider.name": RESPONSES_PROVIDER,
                        "gen_ai.event.content": tool_output_content,
                    },
                },
                {
                    "name": "gen_ai.output.messages",
                    "attributes": {
                        "gen_ai.provider.name": RESPONSES_PROVIDER,
                        "gen_ai.event.content": '[{"role": "assistant", "parts": [{"type": "text", "content": "*"}], "finish_reason": "*"}]',
                    },
                },
            ]
            events_match = GenAiTraceVerifier().check_span_events(span2, expected_events_2)
            assert events_match == True

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_async_responses_stream_method_with_tools_with_content_recording_events(self, **kwargs):
        """Test async responses.stream() with tools and content recording (event-based messages)."""
        await self._test_async_responses_stream_method_with_tools_with_content_recording_impl(True, **kwargs)

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_async_responses_stream_method_with_tools_with_content_recording_attributes(self, **kwargs):
        """Test async responses.stream() with tools and content recording (attribute-based messages)."""
        await self._test_async_responses_stream_method_with_tools_with_content_recording_impl(False, **kwargs)

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_async_responses_stream_method_with_tools_with_content_recording_simple_format_events(self, **kwargs):
        """Test async responses.stream() with tools, content recording, simple OTEL format (event mode)."""
        await self._test_async_responses_stream_method_with_tools_with_content_recording_impl(
            True, use_simple_tool_call_format=True, **kwargs
        )

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_async_responses_stream_method_with_tools_with_content_recording_simple_format_attributes(
        self, **kwargs
    ):
        """Test async responses.stream() with tools, content recording, simple OTEL format (attribute mode)."""
        await self._test_async_responses_stream_method_with_tools_with_content_recording_impl(
            False, use_simple_tool_call_format=True, **kwargs
        )

    async def _test_async_responses_stream_method_with_tools_without_content_recording_impl(
        self, use_events, use_simple_tool_call_format=False, **kwargs
    ):
        """Implementation for testing async responses.stream() method with function tools without content recording.

        Args:
            use_events: If True, use event-based message tracing. If False, use attribute-based.
            use_simple_tool_call_format: If True, use simple OTEL-compliant tool call format.
        """
        from openai.types.responses.response_input_param import FunctionCallOutput

        self.cleanup()
        _set_use_message_events(use_events)
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "False",
                "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True",
            }
        )
        self.setup_telemetry()
        _set_use_simple_tool_format(use_simple_tool_call_format)
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        async with self.create_async_client(operation_group="tracing", **kwargs) as project_client:
            client = project_client.get_openai_client()
            deployment_name = kwargs.get("azure_ai_model_deployment_name")

            # Define a function tool
            function_tool = FunctionTool(
                name="get_weather",
                description="Get the current weather for a location.",
                parameters={
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city name, e.g. San Francisco",
                        },
                    },
                    "required": ["location"],
                    "additionalProperties": False,
                },
                strict=True,
            )

            conversation = await client.conversations.create()

            # First request - should trigger function call
            function_calls = []
            async with client.responses.stream(
                conversation=conversation.id,
                model=deployment_name,
                input="What\\'s the weather in Boston?",
                tools=[function_tool],
            ) as stream:
                async for event in stream:
                    pass  # Process events

                final_response = await stream.get_final_response()

                # Extract function calls
                if hasattr(final_response, "output") and final_response.output:
                    for item in final_response.output:
                        if hasattr(item, "type") and item.type == "function_call":
                            function_calls.append(item)

            assert len(function_calls) > 0

            # Prepare function output
            input_list = []
            for func_call in function_calls:
                weather_result = {"temperature": "65°F", "condition": "cloudy"}
                output = FunctionCallOutput(
                    type="function_call_output",
                    call_id=func_call.call_id,
                    output=json.dumps(weather_result),
                )
                input_list.append(output)

            # Second request - provide function results
            async with client.responses.stream(
                conversation=conversation.id,
                model=deployment_name,
                input=input_list,
                tools=[function_tool],
            ) as stream:
                async for event in stream:
                    pass  # Process events

                final_response = await stream.get_final_response()
                assert final_response is not None

        # Check spans - should have 2 responses spans
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_CHAT} {deployment_name}")
        assert len(spans) == 2

        # Validate first span
        span1 = spans[0]
        expected_attributes_1 = [
            ("az.namespace", "Microsoft.CognitiveServices"),
            ("gen_ai.operation.name", OPERATION_NAME_CHAT),
            ("gen_ai.request.model", deployment_name),
            ("gen_ai.provider.name", RESPONSES_PROVIDER),
            ("server.address", ""),
            ("gen_ai.conversation.id", conversation.id),
            ("gen_ai.response.model", deployment_name),
            ("gen_ai.response.id", ""),
            ("gen_ai.usage.input_tokens", "+"),
            ("gen_ai.usage.output_tokens", "+"),
        ]
        if not use_events:
            expected_attributes_1.extend(
                [
                    ("gen_ai.input.messages", ""),
                    ("gen_ai.output.messages", ""),
                ]
            )
        attributes_match = GenAiTraceVerifier().check_span_attributes(span1, expected_attributes_1)
        assert attributes_match == True

        # Check events for first span - tool call format depends on use_simple_tool_call_format flag (only in events mode)
        if use_events:
            if use_simple_tool_call_format:
                tool_call_content = '[{"role": "assistant", "parts": [{"type": "tool_call", "id": "*"}]}]'
            else:
                tool_call_content = '[{"role": "assistant", "parts": [{"type": "tool_call", "content": {"type": "function_call", "id": "*"}}]}]'

            expected_events_1 = [
                {
                    "name": "gen_ai.input.messages",
                    "attributes": {
                        "gen_ai.provider.name": RESPONSES_PROVIDER,
                        "gen_ai.event.content": '[{"role": "user", "parts": [{"type": "text"}]}]',
                    },
                },
                {
                    "name": "gen_ai.output.messages",
                    "attributes": {
                        "gen_ai.provider.name": RESPONSES_PROVIDER,
                        "gen_ai.event.content": tool_call_content,
                    },
                },
            ]
            events_match = GenAiTraceVerifier().check_span_events(span1, expected_events_1)
            assert events_match == True

        # Validate second span
        span2 = spans[1]
        expected_attributes_2 = [
            ("az.namespace", "Microsoft.CognitiveServices"),
            ("gen_ai.operation.name", OPERATION_NAME_CHAT),
            ("gen_ai.request.model", deployment_name),
            ("gen_ai.provider.name", RESPONSES_PROVIDER),
            ("server.address", ""),
            ("gen_ai.conversation.id", conversation.id),
            ("gen_ai.response.model", deployment_name),
            ("gen_ai.response.id", ""),
            ("gen_ai.usage.input_tokens", "+"),
            ("gen_ai.usage.output_tokens", "+"),
        ]
        if not use_events:
            expected_attributes_2.extend(
                [
                    ("gen_ai.input.messages", ""),
                    ("gen_ai.output.messages", ""),
                ]
            )
        attributes_match = GenAiTraceVerifier().check_span_attributes(span2, expected_attributes_2)
        assert attributes_match == True

        # Check events for second span (only in events mode)
        if use_events:
            # Tool output format depends on use_simple_tool_call_format flag
            if use_simple_tool_call_format:
                tool_output_content = '[{"role": "tool", "parts": [{"type": "tool_call_response", "id": "*"}]}]'
            else:
                tool_output_content = '[{"role": "tool", "parts": [{"type": "tool_call_output", "content": {"type": "function_call_output", "id": "*"}}]}]'

            expected_events_2 = [
                {
                    "name": "gen_ai.input.messages",
                    "attributes": {
                        "gen_ai.provider.name": RESPONSES_PROVIDER,
                        "gen_ai.event.content": tool_output_content,
                    },
                },
                {
                    "name": "gen_ai.output.messages",
                    "attributes": {
                        "gen_ai.provider.name": RESPONSES_PROVIDER,
                        "gen_ai.event.content": '[{"role": "assistant", "parts": [{"type": "text"}], "finish_reason": "*"}]',
                    },
                },
            ]
            events_match = GenAiTraceVerifier().check_span_events(span2, expected_events_2)
            assert events_match == True

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_async_responses_stream_method_with_tools_without_content_recording_events(self, **kwargs):
        """Test async responses.stream() with tools, without content recording (event-based messages)."""
        await self._test_async_responses_stream_method_with_tools_without_content_recording_impl(True, **kwargs)

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_async_responses_stream_method_with_tools_without_content_recording_attributes(self, **kwargs):
        """Test async responses.stream() with tools, without content recording (attribute-based messages)."""
        await self._test_async_responses_stream_method_with_tools_without_content_recording_impl(False, **kwargs)

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_async_responses_stream_method_with_tools_without_content_recording_simple_format_events(
        self, **kwargs
    ):
        """Test async responses.stream() with tools, without content recording, simple OTEL format (event mode)."""
        await self._test_async_responses_stream_method_with_tools_without_content_recording_impl(
            True, use_simple_tool_call_format=True, **kwargs
        )

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_async_responses_stream_method_with_tools_without_content_recording_simple_format_attributes(
        self, **kwargs
    ):
        """Test async responses.stream() with tools, without content recording, simple OTEL format (attribute mode)."""
        await self._test_async_responses_stream_method_with_tools_without_content_recording_impl(
            False, use_simple_tool_call_format=True, **kwargs
        )

    # ========================================
    # Workflow Agent Tracing Tests (Async)
    # ========================================

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_async_workflow_agent_non_streaming_with_content_recording(self, **kwargs):
        """Test async workflow agent with non-streaming and content recording enabled."""
        from azure.ai.projects.models import WorkflowAgentDefinition

        self.cleanup()
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "True",
                "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True",
            }
        )
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")

        async with project_client:
            # Create a simple workflow agent
            workflow_yaml = """
kind: workflow
trigger:
  kind: OnConversationStart
  id: test_workflow
  actions:
    - kind: SetVariable
      id: set_result
      variable: Local.Result
      value: "Workflow completed"
"""
            workflow_agent = await project_client.agents.create_version(
                agent_name="test-workflow",
                definition=WorkflowAgentDefinition(workflow=workflow_yaml),
            )

            openai_client = project_client.get_openai_client()
            conversation = await openai_client.conversations.create()

            response = await openai_client.responses.create(
                conversation=conversation.id,
                extra_body={"agent_reference": {"name": workflow_agent.name, "type": "agent_reference"}},
                input="Test workflow",
                stream=False,
            )

            # List conversation items to verify workflow actions in conversation
            items = await openai_client.conversations.items.list(conversation_id=conversation.id)
            # Must iterate to create the span
            items_list = []
            async for item in items:
                items_list.append(item)

            await openai_client.conversations.delete(conversation_id=conversation.id)
            await project_client.agents.delete_version(
                agent_name=workflow_agent.name, agent_version=workflow_agent.version
            )

        # Verify workflow action events
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_INVOKE_AGENT} {workflow_agent.name}")
        assert len(spans) >= 1
        span = spans[0]

        # Check for workflow action events
        workflow_events = [e for e in span.events if e.name == "gen_ai.workflow.action"]
        assert len(workflow_events) > 0

        # Verify workflow event content structure
        for event in workflow_events:
            content_str = event.attributes.get("gen_ai.event.content", "[]")
            content = json.loads(content_str)
            assert isinstance(content, list)
            assert len(content) == 1
            assert content[0]["role"] == "workflow"
            assert "parts" in content[0]
            assert len(content[0]["parts"]) == 1
            part = content[0]["parts"][0]
            assert part["type"] == "workflow_action"
            assert "content" in part
            assert "status" in part["content"]

        # Verify conversation items listing span
        list_spans = self.exporter.get_spans_by_name("list_conversation_items")
        assert len(list_spans) >= 1
        list_span = list_spans[0]

        # Check for conversation item events in list items span
        list_item_events = [e for e in list_span.events if e.name == "gen_ai.conversation.item"]
        assert len(list_item_events) > 0

        # Verify conversation item event content structure - check for workflow items
        found_workflow_item = False
        for event in list_item_events:
            content_str = event.attributes.get("gen_ai.event.content", "[]")
            content = json.loads(content_str)
            assert isinstance(content, list)
            for item in content:
                if item.get("role") == "workflow":
                    found_workflow_item = True
                    assert "parts" in item
                    assert len(item["parts"]) >= 1
                    part = item["parts"][0]
                    assert part["type"] == "workflow_action"
                    assert "content" in part
                    assert "status" in part["content"]
                    # With content recording ON, action_id and previous_action_id should be present
                    assert (
                        "action_id" in part["content"]
                    ), "action_id should be present when content recording is enabled"
                    assert (
                        "previous_action_id" in part["content"]
                    ), "previous_action_id should be present when content recording is enabled"
        assert found_workflow_item, "Should have found workflow items in conversation items"

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_async_workflow_agent_non_streaming_without_content_recording(self, **kwargs):
        """Test async workflow agent with non-streaming and content recording disabled."""
        from azure.ai.projects.models import WorkflowAgentDefinition

        self.cleanup()
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "False",
                "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True",
            }
        )
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")

        async with project_client:
            workflow_yaml = """
kind: workflow
trigger:
  kind: OnConversationStart
  id: test_workflow
  actions:
    - kind: SetVariable
      id: set_result
      variable: Local.Result
      value: "Workflow completed"
"""
            workflow_agent = await project_client.agents.create_version(
                agent_name="test-workflow",
                definition=WorkflowAgentDefinition(workflow=workflow_yaml),
            )

            openai_client = project_client.get_openai_client()
            conversation = await openai_client.conversations.create()

            response = await openai_client.responses.create(
                conversation=conversation.id,
                extra_body={"agent_reference": {"name": workflow_agent.name, "type": "agent_reference"}},
                input="Test workflow",
                stream=False,
            )

            # List conversation items to verify workflow actions in conversation
            items = await openai_client.conversations.items.list(conversation_id=conversation.id)
            # Must iterate to create the span
            items_list = []
            async for item in items:
                items_list.append(item)

            await openai_client.conversations.delete(conversation_id=conversation.id)
            await project_client.agents.delete_version(
                agent_name=workflow_agent.name, agent_version=workflow_agent.version
            )

        # Verify workflow action events (content recording off)
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_INVOKE_AGENT} {workflow_agent.name}")
        assert len(spans) >= 1
        span = spans[0]

        # Check for workflow action events - should still exist but with limited content
        workflow_events = [e for e in span.events if e.name == "gen_ai.workflow.action"]
        assert len(workflow_events) > 0

        # Verify workflow event content structure (no action_id/previous_action_id when content off)
        for event in workflow_events:
            content_str = event.attributes.get("gen_ai.event.content", "[]")
            content = json.loads(content_str)
            assert isinstance(content, list)
            assert len(content) == 1
            assert content[0]["role"] == "workflow"
            assert "parts" in content[0]
            assert len(content[0]["parts"]) == 1
            part = content[0]["parts"][0]
            assert part["type"] == "workflow_action"
            assert "content" in part
            assert "status" in part["content"]
            # action_id and previous_action_id should NOT be present when content recording is off
            assert (
                "action_id" not in part["content"]
            ), "action_id should not be present when content recording is disabled"
            assert (
                "previous_action_id" not in part["content"]
            ), "previous_action_id should not be present when content recording is disabled"

        # Verify conversation items listing span
        list_spans = self.exporter.get_spans_by_name("list_conversation_items")
        assert len(list_spans) >= 1
        list_span = list_spans[0]

        # Check for conversation item events in list items span
        list_item_events = [e for e in list_span.events if e.name == "gen_ai.conversation.item"]
        assert len(list_item_events) > 0

        # Verify conversation item event content structure (content recording OFF)
        found_workflow_item = False
        for event in list_item_events:
            content_str = event.attributes.get("gen_ai.event.content", "[]")
            content = json.loads(content_str)
            assert isinstance(content, list)
            for item in content:
                if item.get("role") == "workflow":
                    found_workflow_item = True
                    assert "parts" in item
                    assert len(item["parts"]) >= 1
                    part = item["parts"][0]
                    assert part["type"] == "workflow_action"
                    assert "content" in part
                    assert "status" in part["content"]
                    # action_id and previous_action_id should NOT be present when content recording is off
                    assert (
                        "action_id" not in part["content"]
                    ), "action_id should not be present when content recording is disabled"
                    assert (
                        "previous_action_id" not in part["content"]
                    ), "previous_action_id should not be present when content recording is disabled"
        assert found_workflow_item, "Should have found workflow items in conversation items"

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_async_workflow_agent_streaming_with_content_recording(self, **kwargs):
        """Test async workflow agent with streaming and content recording enabled."""
        from azure.ai.projects.models import WorkflowAgentDefinition

        self.cleanup()
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "True",
                "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True",
            }
        )
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")

        async with project_client:
            workflow_yaml = """
kind: workflow
trigger:
  kind: OnConversationStart
  id: test_workflow
  actions:
    - kind: SetVariable
      id: set_result
      variable: Local.Result
      value: "Workflow completed"
"""
            workflow_agent = await project_client.agents.create_version(
                agent_name="test-workflow",
                definition=WorkflowAgentDefinition(workflow=workflow_yaml),
            )

            openai_client = project_client.get_openai_client()
            conversation = await openai_client.conversations.create()

            stream = await openai_client.responses.create(
                conversation=conversation.id,
                extra_body={"agent_reference": {"name": workflow_agent.name, "type": "agent_reference"}},
                input="Test workflow",
                stream=True,
            )

            # Consume the stream
            async for _ in stream:
                pass

            # List conversation items to verify workflow actions in conversation
            items = await openai_client.conversations.items.list(conversation_id=conversation.id)
            # Must iterate to create the span
            items_list = []
            async for item in items:
                items_list.append(item)
            print(f"\n=== Async streaming test: Found {len(items_list)} conversation items ===")

            await openai_client.conversations.delete(conversation_id=conversation.id)
            await project_client.agents.delete_version(
                agent_name=workflow_agent.name, agent_version=workflow_agent.version
            )

        # Verify workflow action events in streaming mode
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_INVOKE_AGENT} {workflow_agent.name}")
        assert len(spans) >= 1
        span = spans[0]

        # Check for workflow action events
        workflow_events = [e for e in span.events if e.name == "gen_ai.workflow.action"]
        assert len(workflow_events) > 0

        # Verify workflow event content structure
        for event in workflow_events:
            content_str = event.attributes.get("gen_ai.event.content", "[]")
            content = json.loads(content_str)
            assert isinstance(content, list)
            assert len(content) == 1
            assert content[0]["role"] == "workflow"
            assert "parts" in content[0]
            assert len(content[0]["parts"]) == 1
            part = content[0]["parts"][0]
            assert part["type"] == "workflow_action"
            assert "content" in part
            assert "status" in part["content"]

        # Verify conversation items listing span
        list_spans = self.exporter.get_spans_by_name("list_conversation_items")
        assert len(list_spans) >= 1
        list_span = list_spans[0]

        # Check for conversation item events in list items span
        list_item_events = [e for e in list_span.events if e.name == "gen_ai.conversation.item"]
        assert len(list_item_events) > 0

        # Verify conversation item event content structure - check for workflow items
        found_workflow_item = False
        for event in list_item_events:
            content_str = event.attributes.get("gen_ai.event.content", "[]")
            content = json.loads(content_str)
            assert isinstance(content, list)
            for item in content:
                if item.get("role") == "workflow":
                    found_workflow_item = True
                    assert "parts" in item
                    assert len(item["parts"]) >= 1
                    part = item["parts"][0]
                    assert part["type"] == "workflow_action"
                    assert "content" in part
                    assert "status" in part["content"]
                    # With content recording ON, action_id and previous_action_id should be present
                    assert (
                        "action_id" in part["content"]
                    ), "action_id should be present when content recording is enabled"
                    assert (
                        "previous_action_id" in part["content"]
                    ), "previous_action_id should be present when content recording is enabled"
        assert found_workflow_item, "Should have found workflow items in conversation items"

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_async_workflow_agent_streaming_without_content_recording(self, **kwargs):
        """Test async workflow agent with streaming and content recording disabled."""
        from azure.ai.projects.models import WorkflowAgentDefinition

        self.cleanup()
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "False",
                "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True",
            }
        )
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")

        async with project_client:
            workflow_yaml = """
kind: workflow
trigger:
  kind: OnConversationStart
  id: test_workflow
  actions:
    - kind: SetVariable
      id: set_result
      variable: Local.Result
      value: "Workflow completed"
"""
            workflow_agent = await project_client.agents.create_version(
                agent_name="test-workflow",
                definition=WorkflowAgentDefinition(workflow=workflow_yaml),
            )

            openai_client = project_client.get_openai_client()
            conversation = await openai_client.conversations.create()

            stream = await openai_client.responses.create(
                conversation=conversation.id,
                extra_body={"agent_reference": {"name": workflow_agent.name, "type": "agent_reference"}},
                input="Test workflow",
                stream=True,
            )

            # Consume the stream
            async for _ in stream:
                pass

            # List conversation items to verify workflow actions in conversation
            items = await openai_client.conversations.items.list(conversation_id=conversation.id)
            # Must iterate to create the span
            items_list = []
            async for item in items:
                items_list.append(item)
            print(f"\n=== Async streaming test (no content recording): Found {len(items_list)} conversation items ===")

            await openai_client.conversations.delete(conversation_id=conversation.id)
            await project_client.agents.delete_version(
                agent_name=workflow_agent.name, agent_version=workflow_agent.version
            )

        # Verify workflow action events (content recording off)
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_INVOKE_AGENT} {workflow_agent.name}")
        assert len(spans) >= 1
        span = spans[0]

        # Check for workflow action events - should still exist but with limited content
        workflow_events = [e for e in span.events if e.name == "gen_ai.workflow.action"]
        assert len(workflow_events) > 0

        # Verify workflow event content structure (no action_id/previous_action_id when content off)
        for event in workflow_events:
            content_str = event.attributes.get("gen_ai.event.content", "[]")
            content = json.loads(content_str)
            assert isinstance(content, list)
            assert len(content) == 1
            assert content[0]["role"] == "workflow"
            assert "parts" in content[0]
            assert len(content[0]["parts"]) == 1
            part = content[0]["parts"][0]
            assert part["type"] == "workflow_action"
            assert "content" in part
            assert "status" in part["content"]
            # action_id and previous_action_id should NOT be present when content recording is off
            assert (
                "action_id" not in part["content"]
            ), "action_id should not be present when content recording is disabled"
            assert (
                "previous_action_id" not in part["content"]
            ), "previous_action_id should not be present when content recording is disabled"

        # Verify conversation items listing span
        list_spans = self.exporter.get_spans_by_name("list_conversation_items")
        assert len(list_spans) >= 1
        list_span = list_spans[0]

        # Check for conversation item events in list items span
        list_item_events = [e for e in list_span.events if e.name == "gen_ai.conversation.item"]
        assert len(list_item_events) > 0

        # Verify conversation item event content structure (content recording OFF)
        found_workflow_item = False
        for event in list_item_events:
            content_str = event.attributes.get("gen_ai.event.content", "[]")
            content = json.loads(content_str)
            assert isinstance(content, list)
            for item in content:
                if item.get("role") == "workflow":
                    found_workflow_item = True
                    assert "parts" in item
                    assert len(item["parts"]) >= 1
                    part = item["parts"][0]
                    assert part["type"] == "workflow_action"
                    assert "content" in part
                    assert "status" in part["content"]
                    # action_id and previous_action_id should NOT be present when content recording is off
                    assert (
                        "action_id" not in part["content"]
                    ), "action_id should not be present when content recording is disabled"
                    assert (
                        "previous_action_id" not in part["content"]
                    ), "previous_action_id should not be present when content recording is disabled"
        assert found_workflow_item, "Should have found workflow items in conversation items"

    async def _test_async_prompt_agent_with_responses_non_streaming_impl(
        self, use_events, use_simple_tool_call_format=False, **kwargs
    ):
        """Implementation for testing async prompt agent with responses API (non-streaming).

        Args:
            use_events: If True, use event-based message tracing. If False, use attribute-based.
            use_simple_tool_call_format: If True, use simple OTEL-compliant tool call format.
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
        _set_use_simple_tool_format(use_simple_tool_call_format)
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")

        async with project_client:
            client = project_client.get_openai_client()

            # Create a simple prompt agent
            agent = await project_client.agents.create_version(
                agent_name="PromptTestAgent",
                definition=PromptAgentDefinition(
                    model=deployment_name,
                    instructions="You are a helpful assistant that answers general questions.",
                ),
            )

            # Create a conversation
            conversation = await client.conversations.create()

            # Create response with agent name and id
            response = await client.responses.create(
                conversation=conversation.id,
                extra_body={"agent_reference": {"name": agent.name, "id": agent.id, "type": "agent_reference"}},
                input="What is the capital of France?",
            )

            assert hasattr(response, "output_text")
            assert response.output_text is not None
            assert len(response.output_text) > 0

            # Cleanup
            await client.conversations.delete(conversation_id=conversation.id)
            await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

        # Verify traces contain agent name and id
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_INVOKE_AGENT} {agent.name}")
        assert len(spans) >= 1

        # Validate span attributes
        span = spans[0]
        expected_attributes = [
            ("az.namespace", "Microsoft.CognitiveServices"),
            ("gen_ai.operation.name", OPERATION_NAME_INVOKE_AGENT),
            ("gen_ai.agent.name", agent.name),
            ("gen_ai.agent.id", agent.id),
            ("gen_ai.provider.name", RESPONSES_PROVIDER),
            ("server.address", ""),
            ("gen_ai.conversation.id", conversation.id),
            ("gen_ai.response.model", deployment_name),
            ("gen_ai.response.id", ""),
            ("gen_ai.usage.input_tokens", "+"),
            ("gen_ai.usage.output_tokens", "+"),
        ]
        if not use_events:
            expected_attributes.extend(
                [
                    ("gen_ai.input.messages", ""),
                    ("gen_ai.output.messages", ""),
                ]
            )
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        # Check events (only in events mode)
        if use_events:
            expected_events = [
                {
                    "name": "gen_ai.input.messages",
                    "attributes": {
                        "gen_ai.provider.name": RESPONSES_PROVIDER,
                        "gen_ai.event.content": '[{"role": "user", "parts": [{"type": "text", "content": "What is the capital of France?"}]}]',
                    },
                },
                {
                    "name": "gen_ai.output.messages",
                    "attributes": {
                        "gen_ai.provider.name": RESPONSES_PROVIDER,
                        "gen_ai.event.content": '[{"role": "assistant", "parts": [{"type": "text", "content": "*"}], "finish_reason": "*"}]',
                    },
                },
            ]
            events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
            assert events_match == True

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_async_prompt_agent_with_responses_non_streaming_events(self, **kwargs):
        """Test async prompt agent with responses (non-streaming, event-based messages)."""
        await self._test_async_prompt_agent_with_responses_non_streaming_impl(True, **kwargs)

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_async_prompt_agent_with_responses_non_streaming_attributes(self, **kwargs):
        """Test async prompt agent with responses (non-streaming, attribute-based messages)."""
        await self._test_async_prompt_agent_with_responses_non_streaming_impl(False, **kwargs)

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_async_prompt_agent_with_responses_non_streaming_simple_format_events(self, **kwargs):
        """Test async prompt agent with responses (non-streaming, simple OTEL format, event mode)."""
        await self._test_async_prompt_agent_with_responses_non_streaming_impl(
            True, use_simple_tool_call_format=True, **kwargs
        )

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_async_prompt_agent_with_responses_non_streaming_simple_format_attributes(self, **kwargs):
        """Test async prompt agent with responses (non-streaming, simple OTEL format, attribute mode)."""
        await self._test_async_prompt_agent_with_responses_non_streaming_impl(
            False, use_simple_tool_call_format=True, **kwargs
        )

    async def _test_async_prompt_agent_with_responses_streaming_impl(
        self, use_events, use_simple_tool_call_format=False, **kwargs
    ):
        """Implementation for testing async prompt agent with responses API (streaming).

        Args:
            use_events: If True, use event-based message tracing. If False, use attribute-based.
            use_simple_tool_call_format: If True, use simple OTEL-compliant tool call format.
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
        _set_use_simple_tool_format(use_simple_tool_call_format)
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")

        async with project_client:
            client = project_client.get_openai_client()

            # Create a simple prompt agent
            agent = await project_client.agents.create_version(
                agent_name="PromptTestAgentStreaming",
                definition=PromptAgentDefinition(
                    model=deployment_name,
                    instructions="You are a helpful assistant that answers general questions.",
                ),
            )

            # Create a conversation
            conversation = await client.conversations.create()

            # Create streaming response with agent name and id
            stream = await client.responses.create(
                conversation=conversation.id,
                extra_body={"agent_reference": {"name": agent.name, "id": agent.id, "type": "agent_reference"}},
                input="What is the capital of France?",
                stream=True,
            )

            # Consume the stream
            accumulated_content = []
            async for chunk in stream:
                if hasattr(chunk, "delta") and isinstance(chunk.delta, str):
                    accumulated_content.append(chunk.delta)
                elif hasattr(chunk, "output") and chunk.output:
                    accumulated_content.append(str(chunk.output))

            full_content = "".join(accumulated_content)
            assert full_content is not None
            assert len(full_content) > 0

            # Cleanup
            await client.conversations.delete(conversation_id=conversation.id)
            await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

        # Verify traces contain agent name and id
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_INVOKE_AGENT} {agent.name}")
        assert len(spans) >= 1

        # Validate span attributes
        span = spans[0]
        expected_attributes = [
            ("az.namespace", "Microsoft.CognitiveServices"),
            ("gen_ai.operation.name", OPERATION_NAME_INVOKE_AGENT),
            ("gen_ai.agent.name", agent.name),
            ("gen_ai.agent.id", agent.id),
            ("gen_ai.provider.name", RESPONSES_PROVIDER),
            ("server.address", ""),
            ("gen_ai.conversation.id", conversation.id),
            ("gen_ai.response.model", deployment_name),
            ("gen_ai.response.id", ""),
            ("gen_ai.usage.input_tokens", "+"),
            ("gen_ai.usage.output_tokens", "+"),
        ]
        if not use_events:
            expected_attributes.extend(
                [
                    ("gen_ai.input.messages", ""),
                    ("gen_ai.output.messages", ""),
                ]
            )
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        # Check events (only in events mode)
        if use_events:
            expected_events = [
                {
                    "name": "gen_ai.input.messages",
                    "attributes": {
                        "gen_ai.provider.name": RESPONSES_PROVIDER,
                        "gen_ai.event.content": '[{"role": "user", "parts": [{"type": "text", "content": "What is the capital of France?"}]}]',
                    },
                },
                {
                    "name": "gen_ai.output.messages",
                    "attributes": {
                        "gen_ai.provider.name": RESPONSES_PROVIDER,
                        "gen_ai.event.content": '[{"role": "assistant", "parts": [{"type": "text", "content": "*"}], "finish_reason": "*"}]',
                    },
                },
            ]
            events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
            assert events_match == True

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_async_prompt_agent_with_responses_streaming_events(self, **kwargs):
        """Test async prompt agent with responses (streaming, event-based messages)."""
        await self._test_async_prompt_agent_with_responses_streaming_impl(True, **kwargs)

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_async_prompt_agent_with_responses_streaming_attributes(self, **kwargs):
        """Test async prompt agent with responses (streaming, attribute-based messages)."""
        await self._test_async_prompt_agent_with_responses_streaming_impl(False, **kwargs)

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_async_prompt_agent_with_responses_streaming_simple_format_events(self, **kwargs):
        """Test async prompt agent with responses (streaming, simple OTEL format, event mode)."""
        await self._test_async_prompt_agent_with_responses_streaming_impl(
            True, use_simple_tool_call_format=True, **kwargs
        )

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_async_prompt_agent_with_responses_streaming_simple_format_attributes(self, **kwargs):
        """Test async prompt agent with responses (streaming, simple OTEL format, attribute mode)."""
        await self._test_async_prompt_agent_with_responses_streaming_impl(
            False, use_simple_tool_call_format=True, **kwargs
        )
