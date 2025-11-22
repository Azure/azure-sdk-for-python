# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import json
import pytest
from typing import Optional, Tuple
from azure.ai.projects.telemetry import AIProjectInstrumentor, _utils
from azure.core.settings import settings
from gen_ai_trace_verifier import GenAiTraceVerifier
from openai import OpenAI
from devtools_testutils import recorded_by_proxy
from azure.ai.projects.models import PromptAgentDefinition, FunctionTool

from test_base import servicePreparer, recorded_by_proxy_httpx
from test_ai_instrumentor_base import TestAiAgentsInstrumentorBase, CONTENT_TRACING_ENV_VARIABLE

settings.tracing_implementation = "OpenTelemetry"
_utils._span_impl_type = settings.tracing_implementation()

# Environment variable for binary data tracing
BINARY_DATA_TRACING_ENV_VARIABLE = "AZURE_TRACING_GEN_AI_INCLUDE_BINARY_DATA"

# Base64-encoded test image (PNG format) for testing binary data capture.
# This is a small png image with letters ABC in black on white background.
TEST_IMAGE_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAHgAAABDCAYAAABX2cG8AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAFiUAABYlAUlSJPAAAAPBSURBVHhe7ZFbbgMxDANz"
    "/0u3KNAA24Et60FtGscD8CdLkVL8+DpszYM/HPbiPPDmnAfenPPAm3MeeHO2e+DH4/FHn852/wAf+NMfervL+bDUp7HdxXzQmT6FLS/lY1p6F7J7+51vBP+Mlf4j3HEkDz7Xm8E/"
    "wqP/Avey5MHnKhBdSAH/iGc3f6NeCXfxyIPPlYQLeZeqws5rL3+nXgF38MiL35mAS0UWq8DOUS+/z3ydsHulDLkpJ1ywsmgE9s066bG8atg5kgJNygAuq17cgn1WJ32WVwX7KCXa"
    "tAtcmuqEXVYffZZXAbsoNfrEX7j4SF2wx+qiz/JWYc8tnfxBAZefqQv2rLroXfkzML+z60pLOg+w1AE7rB76LG8W5nd2kZYGHvE8hL91Hcl8q4M+y5uF+V09I+QtPOJ6CH/ndxXM"
    "n3XQY3mzMLujw0LexEN4DL+NPFWYPcrnd8tbgdnq/BXyNh4zOojfZ74szGU2v818VZjd0bFC2sZDZsfQY3kzMPeazd9HHhXM7+hYIW3kMdZB9K38EZjpkRrmd/WskDbymNVB9Hpm"
    "PDBvpQ7Y0dWzQtbKYzwH0e+dW8E8S12wp7PLQtbKY7wHcSYyO4NZljpgR2fXClkrj4kcxLnoPGGOVyqYq8yOImnmMZ6D6J8pAzOiqsI8RWYWSTOPUSsK57PKwpxKVhVJM49RKwrn"
    "K8rAjGyOgnIzD+lQFM7PMuiZKQrnMxkqys08pEsROOuZp5+KwNnovJJyMw/xyIJezwzhbGSec6qMV1Fq5hGqQ5gZzeZcZPYHzkYzOBeZVVNq5hHKQ5gbyeeMd+4K5yMZnIvMqik1"
    "8wjlIcyN5HPGO3eF85EMzkVm1aSbeUDHEcz39tDvmSGcj2RwLjKrJt3MA7qOYIeni96VfwTnIxmci84rSbdy+a4D2OHponflH8H5aAZno/MqUq1cvHt5dq066bO8Izj7qgwFqUYu"
    "fcfi7LN66Zn5CGei84QZlawsqTYufMfS7LN66Zn5rtBPZWBGJStLuI3L3rkwe2f9/D7yPKFvpArMUmRGCDdx0TuX/YHdo35+p4ffLFVhHtVNuIEL3rHkFXaP+vn96eFvlpQwm+ok"
    "lM7FupebsernjlF1wI6ROgilcqGupapwR6+6Yd9KCkIpXEC1hBruuNLdsD8jL37nL5mSu+GfMdKr4T4ZefC53hD+Gd4/5G64Y0QefK7DLfABV/Lgcx1uh49JefE7D2/JeeDNOQ+8"
    "OeeBN+c88OacB96c88Cbcx54c84Db8554M35BqSHAPxoJdj6AAAAAElFTkSuQmCC"
)


class TestResponsesInstrumentor(TestAiAgentsInstrumentorBase):
    """Tests for ResponsesInstrumentor with real endpoints."""

    def _get_openai_client_and_deployment(self, **kwargs) -> Tuple[OpenAI, str]:
        """Create OpenAI client through AI Projects client"""
        # Create AI Projects client using the standard test infrastructure
        project_client = self.create_client(operation_group="tracing", **kwargs)

        # Get the OpenAI client from the project client
        openai_client = project_client.get_openai_client()

        # Get the model deployment name from test parameters
        model_deployment_name = self.test_agents_params["model_deployment_name"]

        return openai_client, model_deployment_name

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
        "env_value, expected",
        [
            (None, False),
            ("false", False),
            ("False", False),
            ("true", True),
            ("True", True),
        ],
    )
    def test_content_recording_environment_variable(self, env_value: Optional[str], expected: bool):
        def set_env_var(var_name, value):
            if value is None:
                os.environ.pop(var_name, None)
            else:
                os.environ[var_name] = str(value).lower()

        set_env_var(CONTENT_TRACING_ENV_VARIABLE, env_value)
        self.setup_telemetry()
        try:
            assert expected == AIProjectInstrumentor().is_content_recording_enabled()
        finally:
            self.cleanup()

    @pytest.mark.parametrize(
        "env_value, expected_enabled, expected_instrumented",
        [
            (None, True, True),  # Default: enabled and instrumented
            ("true", True, True),  # Explicitly enabled
            ("True", True, True),  # Case insensitive
            ("TRUE", True, True),  # Case insensitive
            ("false", False, False),  # Explicitly disabled
            ("False", False, False),  # Case insensitive
            ("random", False, False),  # Invalid value treated as false
            ("0", False, False),  # Numeric false
            ("1", False, False),  # Numeric true but not "true"
        ],
    )
    def test_instrumentation_environment_variable(
        self, env_value: Optional[str], expected_enabled: bool, expected_instrumented: bool
    ):
        def set_env_var(var_name, value):
            if value is None:
                os.environ.pop(var_name, None)
            else:
                os.environ[var_name] = str(value).lower()

        # Set the instrumentation environment variable
        set_env_var("AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API", env_value)

        # Clean up any existing instrumentation
        AIProjectInstrumentor().uninstrument()

        try:
            # Set up telemetry (which calls instrument())
            self.setup_telemetry()

            # Check if overall instrumentation is enabled (AIProjectInstrumentor always instruments agents)
            # The environment variable only affects whether responses API calls are traced
            assert True == AIProjectInstrumentor().is_instrumented()

            # The real test is whether responses API calls would be traced
            # This is controlled by the _is_instrumentation_enabled() method
            instrumentor = AIProjectInstrumentor()
            if hasattr(instrumentor, "_responses_impl") and instrumentor._responses_impl:
                responses_enabled = instrumentor._responses_impl._is_instrumentation_enabled()
                assert expected_enabled == responses_enabled

        finally:
            self.cleanup()

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_httpx
    def test_sync_non_streaming_with_content_recording(self, **kwargs):
        """Test synchronous non-streaming responses with content recording enabled."""
        self.cleanup()
        os.environ.update(
            {CONTENT_TRACING_ENV_VARIABLE: "True", "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True"}
        )
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            # Get the OpenAI client from the project client
            client = project_client.get_openai_client()
            deployment_name = self.test_agents_params["model_deployment_name"]

            # Create a conversation
            conversation = client.conversations.create()

            # Create responses and call create method
            result = client.responses.create(
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
                    "gen_ai.event.content": '{"content": [{"type": "text", "text": "Write a short poem about AI"}]}',
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": '{"content": [{"type": "text", "text": "*"}]}',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_httpx
    def test_sync_non_streaming_without_content_recording(self, **kwargs):
        """Test synchronous non-streaming responses with content recording disabled."""
        self.cleanup()
        os.environ.update(
            {CONTENT_TRACING_ENV_VARIABLE: "False", "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True"}
        )
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            # Get the OpenAI client from the project client
            client = project_client.get_openai_client()
            deployment_name = self.test_agents_params["model_deployment_name"]

            # Create a conversation
            conversation = client.conversations.create()

            # Create responses and call create method
            result = client.responses.create(
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

        # Check span events (should not contain content)
        expected_events = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "user",
                    "gen_ai.event.content": "{}",
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": "{}",
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_httpx
    def test_sync_streaming_with_content_recording(self, **kwargs):
        """Test synchronous streaming responses with content recording enabled."""
        from openai.types.responses.response_input_param import FunctionCallOutput

        self.cleanup()
        os.environ.update(
            {CONTENT_TRACING_ENV_VARIABLE: "True", "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True"}
        )
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            # Get the OpenAI client from the project client
            client = project_client.get_openai_client()
            deployment_name = self.test_agents_params["model_deployment_name"]

            # Create a conversation
            conversation = client.conversations.create()

            # Create streaming responses and call create method
            stream = client.responses.create(
                model=deployment_name, conversation=conversation.id, input="Write a short poem about AI", stream=True
            )

            # Consume the stream
            accumulated_content = []
            for chunk in stream:
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
                    "gen_ai.event.content": '{"content": [{"type": "text", "text": "Write a short poem about AI"}]}',
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": '{"content": [{"type": "text", "text": "*"}]}',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_httpx
    def test_sync_conversations_create(self, **kwargs):
        """Test synchronous conversations.create() method."""
        self.cleanup()
        os.environ.update(
            {CONTENT_TRACING_ENV_VARIABLE: "True", "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True"}
        )
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            # Get the OpenAI client from the project client
            client = project_client.get_openai_client()
            deployment_name = self.test_agents_params["model_deployment_name"]

            # Create a conversation
            conversation = client.conversations.create()

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
            ("gen_ai.operation.name", "create_conversation"),
            ("gen_ai.provider.name", "azure.openai"),
            ("server.address", ""),
            ("gen_ai.conversation.id", conversation.id),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_httpx
    def test_sync_list_conversation_items_with_content_recording(self, **kwargs):
        """Test synchronous list_conversation_items with content recording enabled."""
        self.cleanup()
        os.environ.update(
            {CONTENT_TRACING_ENV_VARIABLE: "True", "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True"}
        )
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            # Get the OpenAI client from the project client
            client = project_client.get_openai_client()
            deployment_name = self.test_agents_params["model_deployment_name"]

            # Create a conversation
            conversation = client.conversations.create()

            # Add some responses to create items
            client.responses.create(model=deployment_name, conversation=conversation.id, input="Hello", stream=False)

            # List conversation items
            items = client.conversations.items.list(conversation_id=conversation.id)
            items_list = list(items)
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

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_httpx
    def test_sync_list_conversation_items_without_content_recording(self, **kwargs):
        """Test synchronous list_conversation_items with content recording disabled."""
        self.cleanup()
        os.environ.update(
            {CONTENT_TRACING_ENV_VARIABLE: "False", "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True"}
        )
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            # Get the OpenAI client from the project client
            client = project_client.get_openai_client()
            deployment_name = self.test_agents_params["model_deployment_name"]

            # Create a conversation
            conversation = client.conversations.create()

            # Add some responses to create items
            client.responses.create(model=deployment_name, conversation=conversation.id, input="Hello", stream=False)

            # List conversation items
            items = client.conversations.items.list(conversation_id=conversation.id)
            items_list = list(items)
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

    def test_no_instrumentation_no_spans(self):
        """Test that no spans are created when instrumentation is disabled."""
        # Make sure instrumentation is disabled
        AIProjectInstrumentor().uninstrument()

        # Set up only the exporter without instrumentation
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor
        from memory_trace_exporter import MemoryTraceExporter

        trace._TRACER_PROVIDER = TracerProvider()
        exporter = MemoryTraceExporter()
        span_processor = SimpleSpanProcessor(exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)

        try:
            # Verify no instrumentation
            assert AIProjectInstrumentor().is_instrumented() == False

            # Note: We can't easily test this without mock objects because
            # we need a real client, but the client creation itself might
            # require authentication that we don't want to require for this test

            # For now, just verify the instrumentation state
            assert AIProjectInstrumentor().is_instrumented() == False

            # Check no spans were created
            exporter.force_flush()
            all_spans = exporter.get_spans()
            assert len(all_spans) == 0

        finally:
            exporter.shutdown()
            trace._TRACER_PROVIDER = None

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_httpx
    def test_sync_non_streaming_without_conversation(self, **kwargs):
        """Test synchronous non-streaming responses without conversation parameter."""
        self.cleanup()
        os.environ.update(
            {CONTENT_TRACING_ENV_VARIABLE: "True", "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True"}
        )
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        project_client = self.create_client(operation_group="tracing", **kwargs)
        deployment_name = self.test_agents_params["model_deployment_name"]

        with project_client:
            # Get the OpenAI client from the project client
            client = project_client.get_openai_client()

            # Create responses without conversation parameter
            result = client.responses.create(model=deployment_name, input="Write a short poem about AI")

            # Verify the response exists
            assert hasattr(result, "output")
            assert result.output is not None

        # Check spans
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"responses {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Check span attributes - should NOT have conversation.id
        expected_attributes = [
            ("az.namespace", "Microsoft.CognitiveServices"),
            ("gen_ai.operation.name", "responses"),
            ("gen_ai.request.model", deployment_name),
            ("gen_ai.provider.name", "azure.openai"),
            ("server.address", ""),
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
                    "gen_ai.event.content": '{"content": [{"type": "text", "text": "Write a short poem about AI"}]}',
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": '{"content": [{"type": "text", "text": "*"}]}',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.skip(reason="recordings not working for responses API")
    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy
    def test_sync_function_tool_with_content_recording_non_streaming(self, **kwargs):
        """Test synchronous function tool usage with content recording enabled (non-streaming)."""
        from openai.types.responses.response_input_param import FunctionCallOutput

        self.cleanup()
        os.environ.update(
            {CONTENT_TRACING_ENV_VARIABLE: "True", "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True"}
        )
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            # Get the OpenAI client from the project client
            client = project_client.get_openai_client()
            deployment_name = self.test_agents_params["model_deployment_name"]

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
            agent = project_client.agents.create_version(
                agent_name="WeatherAgent",
                definition=PromptAgentDefinition(
                    model=deployment_name,
                    instructions="You are a helpful assistant that can use function tools.",
                    tools=[func_tool],
                ),
            )

            # Create a conversation
            conversation = client.conversations.create()

            # First request - should trigger function call
            response = client.responses.create(
                conversation=conversation.id,
                input="What's the weather in Seattle?",
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
                stream=False,
            )
            function_calls = [item for item in response.output if item.type == "function_call"]

            # Process function calls and prepare input for second request
            input_list = []
            for item in function_calls:
                if item.name == "get_weather":
                    # Mock function result
                    weather_result = {"temperature": "72°F", "condition": "sunny"}
                    input_list.append(
                        FunctionCallOutput(
                            type="function_call_output",
                            call_id=item.call_id,
                            output=json.dumps(weather_result),
                        )
                    )

            # Second request - provide function results
            response2 = client.responses.create(
                conversation=conversation.id,
                input=input_list,
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
                stream=False,
            )
            assert hasattr(response2, "output")
            assert response2.output is not None

            # Cleanup
            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

        # Check spans - should have 2 responses spans
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"responses {agent.name}")
        assert len(spans) == 2

        # Validate first span (user message + tool call)
        span1 = spans[0]
        expected_attributes_1 = [
            ("az.namespace", "Microsoft.CognitiveServices"),
            ("gen_ai.operation.name", "responses"),
            ("gen_ai.request.assistant_name", agent.name),
            ("gen_ai.provider.name", "azure.openai"),
            ("server.address", ""),
            ("gen_ai.conversation.id", conversation.id),
            ("gen_ai.response.model", deployment_name),
            ("gen_ai.response.id", ""),
            ("gen_ai.usage.input_tokens", "+"),
            ("gen_ai.usage.output_tokens", "+"),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span1, expected_attributes_1)
        assert attributes_match == True

        # Check events for first span - user message and assistant tool call
        expected_events_1 = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "user",
                    "gen_ai.event.content": '{"content": [{"type": "text", "text": "What\'s the weather in Seattle?"}]}',
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": '{"content": [{"type": "tool_call", "tool_call": {"type": "function", "id": "*", "function": {"name": "get_weather", "arguments": "*"}}}]}',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span1, expected_events_1)
        assert events_match == True

        # Validate second span (tool output + final response)
        span2 = spans[1]
        expected_attributes_2 = [
            ("az.namespace", "Microsoft.CognitiveServices"),
            ("gen_ai.operation.name", "responses"),
            ("gen_ai.request.assistant_name", agent.name),
            ("gen_ai.provider.name", "azure.openai"),
            ("server.address", ""),
            ("gen_ai.conversation.id", conversation.id),
            ("gen_ai.response.model", deployment_name),
            ("gen_ai.response.id", ""),
            ("gen_ai.usage.input_tokens", "+"),
            ("gen_ai.usage.output_tokens", "+"),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span2, expected_attributes_2)
        assert attributes_match == True

        # Check events for second span - tool output and assistant response
        expected_events_2 = [
            {
                "name": "gen_ai.tool.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "tool",
                    "gen_ai.event.content": '{"content": [{"type": "tool_call_output", "tool_call_output": {"type": "function", "id": "*", "output": {"temperature": "72°F", "condition": "sunny"}}}]}',
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": '{"content": [{"type": "text", "text": "*"}]}',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span2, expected_events_2)
        assert events_match == True

    @pytest.mark.skip(reason="recordings not working for responses API")
    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy
    def test_sync_function_tool_with_content_recording_streaming(self, **kwargs):
        """Test synchronous function tool usage with content recording enabled (streaming)."""
        from openai.types.responses.response_input_param import FunctionCallOutput

        self.cleanup()
        os.environ.update(
            {CONTENT_TRACING_ENV_VARIABLE: "True", "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True"}
        )
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            # Get the OpenAI client from the project client
            client = project_client.get_openai_client()
            deployment_name = self.test_agents_params["model_deployment_name"]

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
            agent = project_client.agents.create_version(
                agent_name="WeatherAgent",
                definition=PromptAgentDefinition(
                    model=deployment_name,
                    instructions="You are a helpful assistant that can use function tools.",
                    tools=[func_tool],
                ),
            )

            # Create a conversation
            conversation = client.conversations.create()

            # First request - should trigger function call
            stream = client.responses.create(
                conversation=conversation.id,
                input="What's the weather in Seattle?",
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
                stream=True,
            )
            # Consume the stream and collect function calls
            # In streaming, we get events, not direct output items
            function_calls_dict = {}
            first_response_id = None
            for chunk in stream:
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
            stream2 = client.responses.create(
                conversation=conversation.id,
                input=input_list,
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
                stream=True,
            )
            # Consume the second stream
            accumulated_content = []
            for chunk in stream2:
                if hasattr(chunk, "delta") and isinstance(chunk.delta, str):
                    accumulated_content.append(chunk.delta)
                elif hasattr(chunk, "output") and chunk.output:
                    accumulated_content.append(str(chunk.output))
            full_content = "".join(accumulated_content)
            assert full_content is not None
            assert len(full_content) > 0

            # Cleanup
            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

        # Check spans - should have 2 responses spans
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"responses {agent.name}")
        assert len(spans) == 2

        # Validate first span (user message + tool call)
        span1 = spans[0]
        expected_attributes_1 = [
            ("az.namespace", "Microsoft.CognitiveServices"),
            ("gen_ai.operation.name", "responses"),
            ("gen_ai.request.assistant_name", agent.name),
            ("gen_ai.provider.name", "azure.openai"),
            ("server.address", ""),
            ("gen_ai.conversation.id", conversation.id),
            ("gen_ai.response.model", deployment_name),
            ("gen_ai.response.id", ""),
            ("gen_ai.usage.input_tokens", "+"),
            ("gen_ai.usage.output_tokens", "+"),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span1, expected_attributes_1)
        assert attributes_match == True

        # Check events for first span - user message and assistant tool call
        expected_events_1 = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "user",
                    "gen_ai.event.content": '{"content": [{"type": "text", "text": "What\'s the weather in Seattle?"}]}',
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": '{"content": [{"type": "tool_call", "tool_call": {"type": "function", "id": "*", "function": {"name": "get_weather", "arguments": "*"}}}]}',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span1, expected_events_1)
        assert events_match == True

        # Validate second span (tool output + final response)
        span2 = spans[1]
        expected_attributes_2 = [
            ("az.namespace", "Microsoft.CognitiveServices"),
            ("gen_ai.operation.name", "responses"),
            ("gen_ai.request.assistant_name", agent.name),
            ("gen_ai.provider.name", "azure.openai"),
            ("server.address", ""),
            ("gen_ai.conversation.id", conversation.id),
            ("gen_ai.response.model", deployment_name),
            ("gen_ai.response.id", ""),
            ("gen_ai.usage.input_tokens", "+"),
            ("gen_ai.usage.output_tokens", "+"),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span2, expected_attributes_2)
        assert attributes_match == True

        # Check events for second span - tool output and assistant response
        expected_events_2 = [
            {
                "name": "gen_ai.tool.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "tool",
                    "gen_ai.event.content": '{"content": [{"type": "tool_call_output", "tool_call_output": {"type": "function", "id": "*", "output": {"temperature": "72°F", "condition": "sunny"}}}]}',
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": '{"content": [{"type": "text", "text": "*"}]}',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span2, expected_events_2)
        assert events_match == True

    @pytest.mark.skip(reason="recordings not working for responses API")
    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy
    def test_sync_function_tool_without_content_recording_non_streaming(self, **kwargs):
        """Test synchronous function tool usage without content recording (non-streaming)."""
        from openai.types.responses.response_input_param import FunctionCallOutput

        self.cleanup()
        os.environ.update(
            {CONTENT_TRACING_ENV_VARIABLE: "False", "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True"}
        )
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            # Get the OpenAI client from the project client
            client = project_client.get_openai_client()
            deployment_name = self.test_agents_params["model_deployment_name"]

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
            agent = project_client.agents.create_version(
                agent_name="WeatherAgent",
                definition=PromptAgentDefinition(
                    model=deployment_name,
                    instructions="You are a helpful assistant that can use function tools.",
                    tools=[func_tool],
                ),
            )

            # Create a conversation
            conversation = client.conversations.create()

            # First request - should trigger function call
            response = client.responses.create(
                conversation=conversation.id,
                input="What's the weather in Seattle?",
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
                stream=False,
            )
            function_calls = [item for item in response.output if item.type == "function_call"]

            # Process function calls and prepare input for second request
            input_list = []
            for item in function_calls:
                if item.name == "get_weather":
                    # Mock function result
                    weather_result = {"temperature": "72°F", "condition": "sunny"}
                    input_list.append(
                        FunctionCallOutput(
                            type="function_call_output",
                            call_id=item.call_id,
                            output=json.dumps(weather_result),
                        )
                    )

            # Second request - provide function results
            response2 = client.responses.create(
                conversation=conversation.id,
                input=input_list,
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
                stream=False,
            )
            assert hasattr(response2, "output")

            # Cleanup
            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

        # Check spans - should have 2 responses spans
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"responses {agent.name}")
        assert len(spans) == 2

        # Validate first span (user message + tool call) - no content
        span1 = spans[0]
        expected_attributes_1 = [
            ("az.namespace", "Microsoft.CognitiveServices"),
            ("gen_ai.operation.name", "responses"),
            ("gen_ai.request.assistant_name", agent.name),
            ("gen_ai.provider.name", "azure.openai"),
            ("server.address", ""),
            ("gen_ai.conversation.id", conversation.id),
            ("gen_ai.response.model", deployment_name),
            ("gen_ai.response.id", ""),
            ("gen_ai.usage.input_tokens", "+"),
            ("gen_ai.usage.output_tokens", "+"),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span1, expected_attributes_1)
        assert attributes_match == True

        # Check events for first span - tool call ID included but no function details
        expected_events_1 = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "user",
                    "gen_ai.event.content": "{}",
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": '{"content": [{"type": "tool_call", "tool_call": {"type": "function", "id": "*"}}]}',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span1, expected_events_1)
        assert events_match == True

        # Validate second span (tool output + final response) - no content
        span2 = spans[1]
        expected_attributes_2 = [
            ("az.namespace", "Microsoft.CognitiveServices"),
            ("gen_ai.operation.name", "responses"),
            ("gen_ai.request.assistant_name", agent.name),
            ("gen_ai.provider.name", "azure.openai"),
            ("server.address", ""),
            ("gen_ai.conversation.id", conversation.id),
            ("gen_ai.response.model", deployment_name),
            ("gen_ai.response.id", ""),
            ("gen_ai.usage.input_tokens", "+"),
            ("gen_ai.usage.output_tokens", "+"),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span2, expected_attributes_2)
        assert attributes_match == True

        # Check events for second span - empty content bodies
        expected_events_2 = [
            {
                "name": "gen_ai.tool.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "tool",
                    "gen_ai.event.content": "{}",
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": "{}",
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span2, expected_events_2)
        assert events_match == True

    @pytest.mark.skip(reason="recordings not working for responses API")
    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy
    def test_sync_function_tool_without_content_recording_streaming(self, **kwargs):
        """Test synchronous function tool usage without content recording (streaming)."""
        from openai.types.responses.response_input_param import FunctionCallOutput

        self.cleanup()
        os.environ.update(
            {CONTENT_TRACING_ENV_VARIABLE: "False", "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True"}
        )
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            # Get the OpenAI client from the project client
            client = project_client.get_openai_client()
            deployment_name = self.test_agents_params["model_deployment_name"]

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
            agent = project_client.agents.create_version(
                agent_name="WeatherAgent",
                definition=PromptAgentDefinition(
                    model=deployment_name,
                    instructions="You are a helpful assistant that can use function tools.",
                    tools=[func_tool],
                ),
            )

            # Create a conversation
            conversation = client.conversations.create()

            # First request - should trigger function call
            stream = client.responses.create(
                conversation=conversation.id,
                input="What's the weather in Seattle?",
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
                stream=True,
            )
            # Consume the stream and collect function calls
            # In streaming, we get events, not direct output items
            function_calls_dict = {}
            first_response_id = None
            for chunk in stream:
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
            stream2 = client.responses.create(
                conversation=conversation.id,
                input=input_list,
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
                stream=True,
            )
            # Consume the second stream
            for chunk in stream2:
                pass  # Just consume the stream

            # Cleanup
            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

        # Check spans - should have 2 responses spans
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"responses {agent.name}")
        assert len(spans) == 2

        # Validate first span (user message + tool call) - no content
        span1 = spans[0]
        expected_attributes_1 = [
            ("az.namespace", "Microsoft.CognitiveServices"),
            ("gen_ai.operation.name", "responses"),
            ("gen_ai.request.assistant_name", agent.name),
            ("gen_ai.provider.name", "azure.openai"),
            ("server.address", ""),
            ("gen_ai.conversation.id", conversation.id),
            ("gen_ai.response.model", deployment_name),
            ("gen_ai.response.id", ""),
            ("gen_ai.usage.input_tokens", "+"),
            ("gen_ai.usage.output_tokens", "+"),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span1, expected_attributes_1)
        assert attributes_match == True

        # Check events for first span - tool call ID included but no function details
        expected_events_1 = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "user",
                    "gen_ai.event.content": "{}",
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": '{"content": [{"type": "tool_call", "tool_call": {"type": "function", "id": "*"}}]}',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span1, expected_events_1)
        assert events_match == True

        # Validate second span (tool output + final response) - no content
        span2 = spans[1]
        expected_attributes_2 = [
            ("az.namespace", "Microsoft.CognitiveServices"),
            ("gen_ai.operation.name", "responses"),
            ("gen_ai.request.assistant_name", agent.name),
            ("gen_ai.provider.name", "azure.openai"),
            ("server.address", ""),
            ("gen_ai.conversation.id", conversation.id),
            ("gen_ai.response.model", deployment_name),
            ("gen_ai.response.id", ""),
            ("gen_ai.usage.input_tokens", "+"),
            ("gen_ai.usage.output_tokens", "+"),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span2, expected_attributes_2)
        assert attributes_match == True

        # Check events for second span - empty content bodies
        expected_events_2 = [
            {
                "name": "gen_ai.tool.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "tool",
                    "gen_ai.event.content": "{}",
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": "{}",
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span2, expected_events_2)
        assert events_match == True

    @pytest.mark.skip(reason="recordings not working for responses API")
    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy
    def test_sync_function_tool_list_conversation_items_with_content_recording(self, **kwargs):
        """Test listing conversation items after function tool usage with content recording enabled."""
        from openai.types.responses.response_input_param import FunctionCallOutput

        self.cleanup()
        os.environ.update(
            {CONTENT_TRACING_ENV_VARIABLE: "True", "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True"}
        )
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            # Get the OpenAI client from the project client
            client = project_client.get_openai_client()
            deployment_name = self.test_agents_params["model_deployment_name"]

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
            agent = project_client.agents.create_version(
                agent_name="WeatherAgent",
                definition=PromptAgentDefinition(
                    model=deployment_name,
                    instructions="You are a helpful assistant that can use function tools.",
                    tools=[func_tool],
                ),
            )

            # Create a conversation
            conversation = client.conversations.create()

            # First request - should trigger function call
            response = client.responses.create(
                conversation=conversation.id,
                input="What's the weather in Seattle?",
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
                stream=False,
            )

            # Process function calls
            input_list = []
            for item in response.output:
                if item.type == "function_call" and item.name == "get_weather":
                    weather_result = {"temperature": "72°F", "condition": "sunny"}
                    input_list.append(
                        FunctionCallOutput(
                            type="function_call_output",
                            call_id=item.call_id,
                            output=json.dumps(weather_result),
                        )
                    )

            # Second request - provide function results
            response2 = client.responses.create(
                conversation=conversation.id,
                input=input_list,
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
                stream=False,
            )

            # List conversation items
            items = client.conversations.items.list(conversation_id=conversation.id)
            items_list = list(items)
            assert len(items_list) > 0

            # Cleanup
            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

        # Check spans
        self.exporter.force_flush()

        # Check list_conversation_items span
        list_spans = self.exporter.get_spans_by_name("list_conversation_items")
        assert len(list_spans) == 1
        list_span = list_spans[0]

        # Check span attributes
        expected_attributes = [
            ("az.namespace", "Microsoft.CognitiveServices"),
            ("gen_ai.operation.name", "list_conversation_items"),
            ("gen_ai.provider.name", "azure.openai"),
            ("server.address", ""),
            ("gen_ai.conversation.id", conversation.id),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(list_span, expected_attributes)
        assert attributes_match == True

        # Check events - should include user message, function_call, function_call_output, and assistant response
        # The order might vary, so we check that all expected event types are present
        events = list_span.events
        event_names = [event.name for event in events]

        # Should have: user message, assistant message (with tool call), tool message (output), assistant message (final)
        assert "gen_ai.user.message" in event_names
        assert "gen_ai.assistant.message" in event_names
        assert "gen_ai.tool.message" in event_names

        # Find and validate the tool message event
        tool_events = [e for e in events if e.name == "gen_ai.tool.message"]
        assert len(tool_events) >= 1
        tool_event = tool_events[0]

        # Check that tool event has correct role and provider attributes
        tool_event_attrs = dict(tool_event.attributes)
        assert "gen_ai.provider.name" in tool_event_attrs
        assert tool_event_attrs["gen_ai.provider.name"] == "azure.openai"
        assert "gen_ai.conversation.item.role" in tool_event_attrs
        assert tool_event_attrs["gen_ai.conversation.item.role"] == "tool"

        # Check that content contains tool_call_output
        assert "gen_ai.event.content" in tool_event_attrs
        content = tool_event_attrs["gen_ai.event.content"]
        assert "tool_call_output" in content
        assert "temperature" in content
        assert "72°F" in content

    @pytest.mark.skip(reason="recordings not working for responses API")
    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy
    def test_sync_function_tool_list_conversation_items_without_content_recording(self, **kwargs):
        """Test listing conversation items after function tool usage without content recording."""
        from openai.types.responses.response_input_param import FunctionCallOutput

        self.cleanup()
        os.environ.update(
            {CONTENT_TRACING_ENV_VARIABLE: "False", "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True"}
        )
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            # Get the OpenAI client from the project client
            client = project_client.get_openai_client()
            deployment_name = self.test_agents_params["model_deployment_name"]

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
            agent = project_client.agents.create_version(
                agent_name="WeatherAgent",
                definition=PromptAgentDefinition(
                    model=deployment_name,
                    instructions="You are a helpful assistant that can use function tools.",
                    tools=[func_tool],
                ),
            )

            # Create a conversation
            conversation = client.conversations.create()

            # First request - should trigger function call
            response = client.responses.create(
                conversation=conversation.id,
                input="What's the weather in Seattle?",
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
                stream=False,
            )

            # Process function calls
            input_list = []
            for item in response.output:
                if item.type == "function_call" and item.name == "get_weather":
                    weather_result = {"temperature": "72°F", "condition": "sunny"}
                    input_list.append(
                        FunctionCallOutput(
                            type="function_call_output",
                            call_id=item.call_id,
                            output=json.dumps(weather_result),
                        )
                    )

            # Second request - provide function results
            response2 = client.responses.create(
                conversation=conversation.id,
                input=input_list,
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
                stream=False,
            )

            # List conversation items
            items = client.conversations.items.list(conversation_id=conversation.id)
            items_list = list(items)
            assert len(items_list) > 0

            # Cleanup
            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

        # Check spans
        self.exporter.force_flush()

        # Check list_conversation_items span
        list_spans = self.exporter.get_spans_by_name("list_conversation_items")
        assert len(list_spans) == 1
        list_span = list_spans[0]

        # Check span attributes
        expected_attributes = [
            ("az.namespace", "Microsoft.CognitiveServices"),
            ("gen_ai.operation.name", "list_conversation_items"),
            ("gen_ai.provider.name", "azure.openai"),
            ("server.address", ""),
            ("gen_ai.conversation.id", conversation.id),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(list_span, expected_attributes)
        assert attributes_match == True

        # Check events - should have event names but empty content
        events = list_span.events
        event_names = [event.name for event in events]

        # Should have the event types present
        assert "gen_ai.user.message" in event_names
        assert "gen_ai.assistant.message" in event_names
        assert "gen_ai.tool.message" in event_names

        # Find and validate the tool message event has correct role, provider, and basic content (no details)
        tool_events = [e for e in events if e.name == "gen_ai.tool.message"]
        assert len(tool_events) >= 1
        tool_event = tool_events[0]

        # Check that tool event has correct role and provider attributes
        tool_event_attrs = dict(tool_event.attributes)
        assert "gen_ai.provider.name" in tool_event_attrs
        assert tool_event_attrs["gen_ai.provider.name"] == "azure.openai"
        assert "gen_ai.conversation.item.role" in tool_event_attrs
        assert tool_event_attrs["gen_ai.conversation.item.role"] == "tool"

        # Check that content is empty when content recording is disabled
        assert "gen_ai.event.content" in tool_event_attrs
        content = tool_event_attrs["gen_ai.event.content"]
        assert content == "{}"  # Should be empty JSON object

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_httpx
    def test_sync_multiple_text_inputs_with_content_recording_non_streaming(self, **kwargs):
        """Test synchronous non-streaming responses with multiple text inputs and content recording enabled."""
        self.cleanup()
        os.environ.update(
            {CONTENT_TRACING_ENV_VARIABLE: "True", "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True"}
        )
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            # Get the OpenAI client from the project client
            client = project_client.get_openai_client()
            deployment_name = self.test_agents_params["model_deployment_name"]

            # Create a conversation
            conversation = client.conversations.create()

            # Create responses with multiple text inputs as a list
            input_list = [
                {"role": "user", "content": [{"type": "input_text", "text": "Hello"}]},
                {"role": "user", "content": [{"type": "input_text", "text": "Write a haiku about Python"}]},
            ]

            result = client.responses.create(
                model=deployment_name, conversation=conversation.id, input=input_list, stream=False
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

        # Check span events - should have 2 user messages and 1 assistant message
        expected_events = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "user",
                    "gen_ai.event.content": '{"content": [{"type": "text", "text": "Hello"}]}',
                },
            },
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "user",
                    "gen_ai.event.content": '{"content": [{"type": "text", "text": "Write a haiku about Python"}]}',
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": '{"content": [{"type": "text", "text": "*"}]}',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_httpx
    def test_sync_multiple_text_inputs_with_content_recording_streaming(self, **kwargs):
        """Test synchronous streaming responses with multiple text inputs and content recording enabled."""
        self.cleanup()
        os.environ.update(
            {CONTENT_TRACING_ENV_VARIABLE: "True", "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True"}
        )
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            # Get the OpenAI client from the project client
            client = project_client.get_openai_client()
            deployment_name = self.test_agents_params["model_deployment_name"]

            # Create a conversation
            conversation = client.conversations.create()

            # Create responses with multiple text inputs as a list
            input_list = [
                {"role": "user", "content": [{"type": "input_text", "text": "Hello"}]},
                {"role": "user", "content": [{"type": "input_text", "text": "Write a haiku about Python"}]},
            ]

            stream = client.responses.create(
                model=deployment_name, conversation=conversation.id, input=input_list, stream=True
            )

            # Consume the stream
            accumulated_content = []
            for chunk in stream:
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

        # Check span events - should have 2 user messages and 1 assistant message
        expected_events = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "user",
                    "gen_ai.event.content": '{"content": [{"type": "text", "text": "Hello"}]}',
                },
            },
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "user",
                    "gen_ai.event.content": '{"content": [{"type": "text", "text": "Write a haiku about Python"}]}',
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": '{"content": [{"type": "text", "text": "*"}]}',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_httpx
    def test_sync_multiple_text_inputs_without_content_recording_non_streaming(self, **kwargs):
        """Test synchronous non-streaming responses with multiple text inputs and content recording disabled."""
        self.cleanup()
        os.environ.update(
            {CONTENT_TRACING_ENV_VARIABLE: "False", "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True"}
        )
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            # Get the OpenAI client from the project client
            client = project_client.get_openai_client()
            deployment_name = self.test_agents_params["model_deployment_name"]

            # Create a conversation
            conversation = client.conversations.create()

            # Create responses with multiple text inputs as a list
            input_list = [
                {"role": "user", "content": [{"type": "input_text", "text": "Hello"}]},
                {"role": "user", "content": [{"type": "input_text", "text": "Write a haiku about Python"}]},
            ]

            result = client.responses.create(
                model=deployment_name, conversation=conversation.id, input=input_list, stream=False
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

        # Check span events - should have 2 user messages and 1 assistant message, all with empty content
        expected_events = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "user",
                    "gen_ai.event.content": "{}",
                },
            },
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "user",
                    "gen_ai.event.content": "{}",
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": "{}",
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_httpx
    def test_sync_multiple_text_inputs_without_content_recording_streaming(self, **kwargs):
        """Test synchronous streaming responses with multiple text inputs and content recording disabled."""
        self.cleanup()
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "False"})
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            # Get the OpenAI client from the project client
            client = project_client.get_openai_client()
            deployment_name = self.test_agents_params["model_deployment_name"]

            # Create a conversation
            conversation = client.conversations.create()

            # Create responses with multiple text inputs as a list
            input_list = [
                {"role": "user", "content": [{"type": "input_text", "text": "Hello"}]},
                {"role": "user", "content": [{"type": "input_text", "text": "Write a haiku about Python"}]},
            ]

            stream = client.responses.create(
                model=deployment_name, conversation=conversation.id, input=input_list, stream=True
            )

            # Consume the stream
            accumulated_content = []
            for chunk in stream:
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

        # Check span events - should have 2 user messages and 1 assistant message, all with empty content
        expected_events = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "user",
                    "gen_ai.event.content": "{}",
                },
            },
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "user",
                    "gen_ai.event.content": "{}",
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": "{}",
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_httpx
    def test_image_only_content_off_binary_off_non_streaming(self, **kwargs):
        """Test image only with content recording OFF and binary data OFF (non-streaming)."""
        self.cleanup()
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "False", BINARY_DATA_TRACING_ENV_VARIABLE: "False"})
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            client = project_client.get_openai_client()
            deployment_name = self.test_agents_params["model_deployment_name"]

            conversation = client.conversations.create()

            # Send only an image (no text)
            result = client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input=[
                    {
                        "role": "user",
                        "content": [{"type": "input_image", "image_url": f"data:image/png;base64,{TEST_IMAGE_BASE64}"}],
                    }
                ],
                stream=False,
            )

            assert hasattr(result, "output")
            assert result.output is not None

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"responses {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Content recording OFF: event content should be empty
        expected_events = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "user",
                    "gen_ai.event.content": "{}",
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": "{}",
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_httpx
    def test_image_only_content_off_binary_on_non_streaming(self, **kwargs):
        """Test image only with content recording OFF and binary data ON (non-streaming)."""
        self.cleanup()
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "False", BINARY_DATA_TRACING_ENV_VARIABLE: "True"})
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            client = project_client.get_openai_client()
            deployment_name = self.test_agents_params["model_deployment_name"]

            conversation = client.conversations.create()

            result = client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input=[
                    {
                        "role": "user",
                        "content": [{"type": "input_image", "image_url": f"data:image/png;base64,{TEST_IMAGE_BASE64}"}],
                    }
                ],
                stream=False,
            )

            assert hasattr(result, "output")
            assert result.output is not None

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"responses {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Content recording OFF: event content should be empty (binary flag doesn't matter)
        expected_events = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "user",
                    "gen_ai.event.content": "{}",
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": "{}",
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_httpx
    def test_image_only_content_on_binary_off_non_streaming(self, **kwargs):
        """Test image only with content recording ON and binary data OFF (non-streaming)."""
        self.cleanup()
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "True", BINARY_DATA_TRACING_ENV_VARIABLE: "False"})
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            client = project_client.get_openai_client()
            deployment_name = self.test_agents_params["model_deployment_name"]

            conversation = client.conversations.create()

            result = client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input=[
                    {
                        "role": "user",
                        "content": [{"type": "input_image", "image_url": f"data:image/png;base64,{TEST_IMAGE_BASE64}"}],
                    }
                ],
                stream=False,
            )

            assert hasattr(result, "output")
            assert result.output is not None

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"responses {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Content recording ON, binary OFF: should have image type but no image_url
        expected_events = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "user",
                    "gen_ai.event.content": '{"content":[{"type":"image"}]}',
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": "*",
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_httpx
    def test_image_only_content_on_binary_on_non_streaming(self, **kwargs):
        """Test image only with content recording ON and binary data ON (non-streaming)."""
        self.cleanup()
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "True", BINARY_DATA_TRACING_ENV_VARIABLE: "True"})
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            client = project_client.get_openai_client()
            deployment_name = self.test_agents_params["model_deployment_name"]

            conversation = client.conversations.create()

            result = client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input=[
                    {
                        "role": "user",
                        "content": [{"type": "input_image", "image_url": f"data:image/png;base64,{TEST_IMAGE_BASE64}"}],
                    }
                ],
                stream=False,
            )

            assert hasattr(result, "output")
            assert result.output is not None

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"responses {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Content recording ON, binary ON: should have image type AND image_url with base64 data
        expected_events = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "user",
                    "gen_ai.event.content": f'{{"content":[{{"type":"image","image_url":"data:image/png;base64,{TEST_IMAGE_BASE64}"}}]}}',
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": "*",
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
    @recorded_by_proxy_httpx
    def test_text_and_image_content_off_binary_off_non_streaming(self, **kwargs):
        """Test text + image with content recording OFF and binary data OFF (non-streaming)."""
        self.cleanup()
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "False", BINARY_DATA_TRACING_ENV_VARIABLE: "False"})
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            client = project_client.get_openai_client()
            deployment_name = self.test_agents_params["model_deployment_name"]

            conversation = client.conversations.create()

            # Send text + image
            result = client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": "What is shown in this image?"},
                            {"type": "input_image", "image_url": f"data:image/png;base64,{TEST_IMAGE_BASE64}"},
                        ],
                    }
                ],
                stream=False,
            )

            assert hasattr(result, "output")
            assert result.output is not None

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"responses {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Content recording OFF: event content should be empty
        expected_events = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "user",
                    "gen_ai.event.content": "{}",
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": "{}",
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_httpx
    def test_text_and_image_content_off_binary_on_non_streaming(self, **kwargs):
        """Test text + image with content recording OFF and binary data ON (non-streaming)."""
        self.cleanup()
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "False", BINARY_DATA_TRACING_ENV_VARIABLE: "True"})
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            client = project_client.get_openai_client()
            deployment_name = self.test_agents_params["model_deployment_name"]

            conversation = client.conversations.create()

            result = client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": "What is shown in this image?"},
                            {"type": "input_image", "image_url": f"data:image/png;base64,{TEST_IMAGE_BASE64}"},
                        ],
                    }
                ],
                stream=False,
            )

            assert hasattr(result, "output")
            assert result.output is not None

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"responses {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Content recording OFF: event content should be empty (binary flag doesn't matter)
        expected_events = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "user",
                    "gen_ai.event.content": "{}",
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": "{}",
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_httpx
    def test_text_and_image_content_on_binary_off_non_streaming(self, **kwargs):
        """Test text + image with content recording ON and binary data OFF (non-streaming)."""
        self.cleanup()
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "True", BINARY_DATA_TRACING_ENV_VARIABLE: "False"})
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            client = project_client.get_openai_client()
            deployment_name = self.test_agents_params["model_deployment_name"]

            conversation = client.conversations.create()

            result = client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": "What is shown in this image?"},
                            {"type": "input_image", "image_url": f"data:image/png;base64,{TEST_IMAGE_BASE64}"},
                        ],
                    }
                ],
                stream=False,
            )

            assert hasattr(result, "output")
            assert result.output is not None

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"responses {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Content recording ON, binary OFF: should have text and image type but no image_url
        expected_events = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "user",
                    "gen_ai.event.content": '{"content":[{"type":"text","text":"What is shown in this image?"},{"type":"image"}]}',
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": "*",
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_httpx
    def test_text_and_image_content_on_binary_on_non_streaming(self, **kwargs):
        """Test text + image with content recording ON and binary data ON (non-streaming)."""
        self.cleanup()
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "True", BINARY_DATA_TRACING_ENV_VARIABLE: "True"})
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            client = project_client.get_openai_client()
            deployment_name = self.test_agents_params["model_deployment_name"]

            conversation = client.conversations.create()

            result = client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": "What is shown in this image?"},
                            {"type": "input_image", "image_url": f"data:image/png;base64,{TEST_IMAGE_BASE64}"},
                        ],
                    }
                ],
                stream=False,
            )

            assert hasattr(result, "output")
            assert result.output is not None

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"responses {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Content recording ON, binary ON: should have text and image with full base64 data
        expected_events = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "user",
                    "gen_ai.event.content": f'{{"content":[{{"type":"text","text":"What is shown in this image?"}},{{"type":"image","image_url":"data:image/png;base64,{TEST_IMAGE_BASE64}"}}]}}',
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": "*",
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
    @recorded_by_proxy_httpx
    def test_image_only_content_off_binary_off_streaming(self, **kwargs):
        """Test image only with content recording OFF and binary data OFF (streaming)."""
        self.cleanup()
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "False", BINARY_DATA_TRACING_ENV_VARIABLE: "False"})
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            client = project_client.get_openai_client()
            deployment_name = self.test_agents_params["model_deployment_name"]

            conversation = client.conversations.create()

            stream = client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input=[
                    {
                        "role": "user",
                        "content": [{"type": "input_image", "image_url": f"data:image/png;base64,{TEST_IMAGE_BASE64}"}],
                    }
                ],
                stream=True,
            )

            # Consume the stream
            accumulated_content = []
            for chunk in stream:
                if hasattr(chunk, "delta") and isinstance(chunk.delta, str):
                    accumulated_content.append(chunk.delta)
                elif hasattr(chunk, "output") and chunk.output:
                    accumulated_content.append(chunk.output)

            full_content = "".join(accumulated_content)
            assert full_content is not None
            assert len(full_content) > 0

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"responses {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Content recording OFF: event content should be empty
        expected_events = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "user",
                    "gen_ai.event.content": "{}",
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": "{}",
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_httpx
    def test_image_only_content_off_binary_on_streaming(self, **kwargs):
        """Test image only with content recording OFF and binary data ON (streaming)."""
        self.cleanup()
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "False", BINARY_DATA_TRACING_ENV_VARIABLE: "True"})
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            client = project_client.get_openai_client()
            deployment_name = self.test_agents_params["model_deployment_name"]

            conversation = client.conversations.create()

            stream = client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input=[
                    {
                        "role": "user",
                        "content": [{"type": "input_image", "image_url": f"data:image/png;base64,{TEST_IMAGE_BASE64}"}],
                    }
                ],
                stream=True,
            )

            accumulated_content = []
            for chunk in stream:
                if hasattr(chunk, "delta") and isinstance(chunk.delta, str):
                    accumulated_content.append(chunk.delta)
                elif hasattr(chunk, "output") and chunk.output:
                    accumulated_content.append(chunk.output)

            full_content = "".join(accumulated_content)
            assert full_content is not None
            assert len(full_content) > 0

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"responses {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Content recording OFF: event content should be empty
        expected_events = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "user",
                    "gen_ai.event.content": "{}",
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": "{}",
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_httpx
    def test_image_only_content_on_binary_off_streaming(self, **kwargs):
        """Test image only with content recording ON and binary data OFF (streaming)."""
        self.cleanup()
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "True", BINARY_DATA_TRACING_ENV_VARIABLE: "False"})
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            client = project_client.get_openai_client()
            deployment_name = self.test_agents_params["model_deployment_name"]

            conversation = client.conversations.create()

            stream = client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input=[
                    {
                        "role": "user",
                        "content": [{"type": "input_image", "image_url": f"data:image/png;base64,{TEST_IMAGE_BASE64}"}],
                    }
                ],
                stream=True,
            )

            accumulated_content = []
            for chunk in stream:
                if hasattr(chunk, "delta") and isinstance(chunk.delta, str):
                    accumulated_content.append(chunk.delta)
                elif hasattr(chunk, "output") and chunk.output:
                    accumulated_content.append(chunk.output)

            full_content = "".join(accumulated_content)
            assert full_content is not None
            assert len(full_content) > 0

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"responses {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Content recording ON, binary OFF: should have image type but no image_url
        expected_events = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "user",
                    "gen_ai.event.content": '{"content":[{"type":"image"}]}',
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": "*",
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_httpx
    def test_image_only_content_on_binary_on_streaming(self, **kwargs):
        """Test image only with content recording ON and binary data ON (streaming)."""
        self.cleanup()
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "True", BINARY_DATA_TRACING_ENV_VARIABLE: "True"})
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            client = project_client.get_openai_client()
            deployment_name = self.test_agents_params["model_deployment_name"]

            conversation = client.conversations.create()

            stream = client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input=[
                    {
                        "role": "user",
                        "content": [{"type": "input_image", "image_url": f"data:image/png;base64,{TEST_IMAGE_BASE64}"}],
                    }
                ],
                stream=True,
            )

            accumulated_content = []
            for chunk in stream:
                if hasattr(chunk, "delta") and isinstance(chunk.delta, str):
                    accumulated_content.append(chunk.delta)
                elif hasattr(chunk, "output") and chunk.output:
                    accumulated_content.append(chunk.output)

            full_content = "".join(accumulated_content)
            assert full_content is not None
            assert len(full_content) > 0

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"responses {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Content recording ON, binary ON: should have image type AND image_url with base64 data
        expected_events = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "user",
                    "gen_ai.event.content": f'{{"content":[{{"type":"image","image_url":"data:image/png;base64,{TEST_IMAGE_BASE64}"}}]}}',
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": "*",
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
    @recorded_by_proxy_httpx
    def test_text_and_image_content_off_binary_off_streaming(self, **kwargs):
        """Test text + image with content recording OFF and binary data OFF (streaming)."""
        self.cleanup()
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "False", BINARY_DATA_TRACING_ENV_VARIABLE: "False"})
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            client = project_client.get_openai_client()
            deployment_name = self.test_agents_params["model_deployment_name"]

            conversation = client.conversations.create()

            stream = client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": "What is shown in this image?"},
                            {"type": "input_image", "image_url": f"data:image/png;base64,{TEST_IMAGE_BASE64}"},
                        ],
                    }
                ],
                stream=True,
            )

            accumulated_content = []
            for chunk in stream:
                if hasattr(chunk, "delta") and isinstance(chunk.delta, str):
                    accumulated_content.append(chunk.delta)
                elif hasattr(chunk, "output") and chunk.output:
                    accumulated_content.append(chunk.output)

            full_content = "".join(accumulated_content)
            assert full_content is not None
            assert len(full_content) > 0

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"responses {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Content recording OFF: event content should be empty
        expected_events = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "user",
                    "gen_ai.event.content": "{}",
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": "{}",
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_httpx
    def test_text_and_image_content_off_binary_on_streaming(self, **kwargs):
        """Test text + image with content recording OFF and binary data ON (streaming)."""
        self.cleanup()
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "False", BINARY_DATA_TRACING_ENV_VARIABLE: "True"})
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            client = project_client.get_openai_client()
            deployment_name = self.test_agents_params["model_deployment_name"]

            conversation = client.conversations.create()

            stream = client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": "What is shown in this image?"},
                            {"type": "input_image", "image_url": f"data:image/png;base64,{TEST_IMAGE_BASE64}"},
                        ],
                    }
                ],
                stream=True,
            )

            accumulated_content = []
            for chunk in stream:
                if hasattr(chunk, "delta") and isinstance(chunk.delta, str):
                    accumulated_content.append(chunk.delta)
                elif hasattr(chunk, "output") and chunk.output:
                    accumulated_content.append(chunk.output)

            full_content = "".join(accumulated_content)
            assert full_content is not None
            assert len(full_content) > 0

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"responses {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Content recording OFF: event content should be empty
        expected_events = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "user",
                    "gen_ai.event.content": "{}",
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": "{}",
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_httpx
    def test_text_and_image_content_on_binary_off_streaming(self, **kwargs):
        """Test text + image with content recording ON and binary data OFF (streaming)."""
        self.cleanup()
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "True", BINARY_DATA_TRACING_ENV_VARIABLE: "False"})
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            client = project_client.get_openai_client()
            deployment_name = self.test_agents_params["model_deployment_name"]

            conversation = client.conversations.create()

            stream = client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": "What is shown in this image?"},
                            {"type": "input_image", "image_url": f"data:image/png;base64,{TEST_IMAGE_BASE64}"},
                        ],
                    }
                ],
                stream=True,
            )

            accumulated_content = []
            for chunk in stream:
                if hasattr(chunk, "delta") and isinstance(chunk.delta, str):
                    accumulated_content.append(chunk.delta)
                elif hasattr(chunk, "output") and chunk.output:
                    accumulated_content.append(chunk.output)

            full_content = "".join(accumulated_content)
            assert full_content is not None
            assert len(full_content) > 0

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"responses {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Content recording ON, binary OFF: should have text and image type but no image_url
        expected_events = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "user",
                    "gen_ai.event.content": '{"content":[{"type":"text","text":"What is shown in this image?"},{"type":"image"}]}',
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": "*",
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_httpx
    def test_text_and_image_content_on_binary_on_streaming(self, **kwargs):
        """Test text + image with content recording ON and binary data ON (streaming)."""
        self.cleanup()
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "True", BINARY_DATA_TRACING_ENV_VARIABLE: "True"})
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            client = project_client.get_openai_client()
            deployment_name = self.test_agents_params["model_deployment_name"]

            conversation = client.conversations.create()

            stream = client.responses.create(
                model=deployment_name,
                conversation=conversation.id,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": "What is shown in this image?"},
                            {"type": "input_image", "image_url": f"data:image/png;base64,{TEST_IMAGE_BASE64}"},
                        ],
                    }
                ],
                stream=True,
            )

            accumulated_content = []
            for chunk in stream:
                if hasattr(chunk, "delta") and isinstance(chunk.delta, str):
                    accumulated_content.append(chunk.delta)
                elif hasattr(chunk, "output") and chunk.output:
                    accumulated_content.append(chunk.output)

            full_content = "".join(accumulated_content)
            assert full_content is not None
            assert len(full_content) > 0

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"responses {deployment_name}")
        assert len(spans) == 1
        span = spans[0]

        # Content recording ON, binary ON: should have text and image with full base64 data
        expected_events = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "user",
                    "gen_ai.event.content": f'{{"content":[{{"type":"text","text":"What is shown in this image?"}},{{"type":"image","image_url":"data:image/png;base64,{TEST_IMAGE_BASE64}"}}]}}',
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": "*",
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    # ========================================
    # responses.stream() Method Tests
    # ========================================

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_httpx
    def test_responses_stream_method_with_content_recording(self, **kwargs):
        """Test sync responses.stream() method with content recording enabled."""
        os.environ["AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API"] = "True"
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            client = project_client.get_openai_client()
            deployment_name = self.test_agents_params["model_deployment_name"]

            conversation = client.conversations.create()

            # Use responses.stream() method
            with client.responses.stream(
                conversation=conversation.id, model=deployment_name, input="Write a short haiku about testing"
            ) as stream:
                # Iterate through events
                for event in stream:
                    pass  # Process events

                # Get final response
                final_response = stream.get_final_response()
                assert final_response is not None

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
                    "gen_ai.event.content": '{"content": [{"type": "text", "text": "Write a short haiku about testing"}]}',
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": '{"content": [{"type": "text", "text": "*"}]}',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_httpx
    def test_responses_stream_method_without_content_recording(self, **kwargs):
        """Test sync responses.stream() method without content recording."""
        os.environ["AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API"] = "True"
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            client = project_client.get_openai_client()
            deployment_name = self.test_agents_params["model_deployment_name"]

            conversation = client.conversations.create()

            # Use responses.stream() method
            with client.responses.stream(
                conversation=conversation.id, model=deployment_name, input="Write a short haiku about testing"
            ) as stream:
                # Iterate through events
                for event in stream:
                    pass  # Process events

                # Get final response
                final_response = stream.get_final_response()
                assert final_response is not None

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

        # Check span events - should have events with empty content
        expected_events = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "user",
                    "gen_ai.event.content": "{}",
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": "{}",
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_httpx
    def test_responses_stream_method_with_tools_with_content_recording(self, **kwargs):
        """Test sync responses.stream() method with function tools and content recording enabled."""
        from openai.types.responses.response_input_param import FunctionCallOutput

        os.environ["AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API"] = "True"
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            client = project_client.get_openai_client()
            deployment_name = self.test_agents_params["model_deployment_name"]

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

            conversation = client.conversations.create()

            # First request - should trigger function call
            function_calls = []
            with client.responses.stream(
                conversation=conversation.id,
                model=deployment_name,
                input="What's the weather in Boston?",
                tools=[function_tool],
            ) as stream:
                for event in stream:
                    pass  # Process events

                final_response = stream.get_final_response()

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
            with client.responses.stream(
                conversation=conversation.id, model=deployment_name, input=input_list, tools=[function_tool]
            ) as stream:
                for event in stream:
                    pass  # Process events

                final_response = stream.get_final_response()
                assert final_response is not None

        # Check spans - should have 2 responses spans
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"responses {deployment_name}")
        assert len(spans) == 2

        # Validate first span (user message + tool call)
        span1 = spans[0]
        expected_attributes_1 = [
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
        attributes_match = GenAiTraceVerifier().check_span_attributes(span1, expected_attributes_1)
        assert attributes_match == True

        # Check events for first span
        expected_events_1 = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "user",
                    "gen_ai.event.content": '{"content": [{"type": "text", "text": "What\'s the weather in Boston?"}]}',
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": '{"content": [{"type": "tool_call", "tool_call": {"type": "function", "id": "*", "function": {"name": "get_weather", "arguments": "*"}}}]}',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span1, expected_events_1)
        assert events_match == True

        # Validate second span (tool output + final response)
        span2 = spans[1]
        expected_events_2 = [
            {
                "name": "gen_ai.tool.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "tool",
                    "gen_ai.event.content": '{"content": [{"type": "tool_call_output", "tool_call_output": {"type": "function", "id": "*", "output": {"temperature": "65°F", "condition": "cloudy"}}}]}',
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": '{"content": [{"type": "text", "text": "*"}]}',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span2, expected_events_2)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_httpx
    def test_responses_stream_method_with_tools_without_content_recording(self, **kwargs):
        """Test sync responses.stream() method with function tools without content recording."""
        from openai.types.responses.response_input_param import FunctionCallOutput

        self.cleanup()
        os.environ.update(
            {CONTENT_TRACING_ENV_VARIABLE: "False", "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True"}
        )
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            client = project_client.get_openai_client()
            deployment_name = self.test_agents_params["model_deployment_name"]

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

            conversation = client.conversations.create()

            # First request - should trigger function call
            function_calls = []
            with client.responses.stream(
                conversation=conversation.id,
                model=deployment_name,
                input="What's the weather in Boston?",
                tools=[function_tool],
            ) as stream:
                for event in stream:
                    pass  # Process events

                final_response = stream.get_final_response()

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
            with client.responses.stream(
                conversation=conversation.id, model=deployment_name, input=input_list, tools=[function_tool]
            ) as stream:
                for event in stream:
                    pass  # Process events

                final_response = stream.get_final_response()
                assert final_response is not None

        # Check spans - should have 2 responses spans
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"responses {deployment_name}")
        assert len(spans) == 2

        # Validate first span - should have events with tool call structure but no details
        span1 = spans[0]
        expected_events_1 = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "user",
                    "gen_ai.event.content": "{}",
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": '{"content": [{"type": "tool_call", "tool_call": {"type": "function", "id": "*"}}]}',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span1, expected_events_1)
        assert events_match == True

        # Validate second span - empty content
        span2 = spans[1]
        expected_events_2 = [
            {
                "name": "gen_ai.tool.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "tool",
                    "gen_ai.event.content": "{}",
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": "{}",
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span2, expected_events_2)
        assert events_match == True

    # ========================================
    # Workflow Agent Tracing Tests
    # ========================================

    @pytest.mark.skip(reason="recordings not working for responses API")
    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy
    def test_workflow_agent_non_streaming_with_content_recording(self, **kwargs):
        """Test workflow agent with non-streaming and content recording enabled."""
        from azure.ai.projects.models import WorkflowAgentDefinition, AgentReference, PromptAgentDefinition

        self.cleanup()
        os.environ.update(
            {CONTENT_TRACING_ENV_VARIABLE: "True", "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True"}
        )
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            deployment_name = self.test_agents_params["model_deployment_name"]
            openai_client = project_client.get_openai_client()

            # Create Teacher Agent
            teacher_agent = project_client.agents.create_version(
                agent_name="teacher-agent",
                definition=PromptAgentDefinition(
                    model=deployment_name,
                    instructions="""You are a teacher that create pre-school math question for student and check answer. 
                                    If the answer is correct, you stop the conversation by saying [COMPLETE]. 
                                    If the answer is wrong, you ask student to fix it.""",
                ),
            )

            # Create Student Agent
            student_agent = project_client.agents.create_version(
                agent_name="student-agent",
                definition=PromptAgentDefinition(
                    model=deployment_name,
                    instructions="""You are a student who answers questions from the teacher. 
                                    When the teacher gives you a question, you answer it.""",
                ),
            )

            # Create Multi-Agent Workflow
            workflow_yaml = f"""
kind: workflow
trigger:
  kind: OnConversationStart
  id: my_workflow
  actions:
    - kind: SetVariable
      id: set_variable_input_task
      variable: Local.LatestMessage
      value: "=UserMessage(System.LastMessageText)"

    - kind: CreateConversation
      id: create_student_conversation
      conversationId: Local.StudentConversationId

    - kind: CreateConversation
      id: create_teacher_conversation
      conversationId: Local.TeacherConversationId

    - kind: InvokeAzureAgent
      id: student_agent
      description: The student node
      conversationId: "=Local.StudentConversationId"
      agent:
        name: {student_agent.name}
      input:
        messages: "=Local.LatestMessage"
      output:
        messages: Local.LatestMessage

    - kind: InvokeAzureAgent
      id: teacher_agent
      description: The teacher node
      conversationId: "=Local.TeacherConversationId"
      agent:
        name: {teacher_agent.name}
      input:
        messages: "=Local.LatestMessage"
      output:
        messages: Local.LatestMessage

    - kind: SetVariable
      id: set_variable_turncount
      variable: Local.TurnCount
      value: "=Local.TurnCount + 1"

    - kind: ConditionGroup
      id: completion_check
      conditions:
        - condition: '=!IsBlank(Find("[COMPLETE]", Upper(Last(Local.LatestMessage).Text)))'
          id: check_done
          actions:
            - kind: EndConversation
              id: end_workflow

        - condition: "=Local.TurnCount >= 4"
          id: check_turn_count_exceeded
          actions:
            - kind: SendActivity
              id: send_activity_tired
              activity: "Let's try again later...I am tired."

      elseActions:
        - kind: GotoAction
          id: goto_student_agent
          actionId: student_agent
"""

            workflow_agent = project_client.agents.create_version(
                agent_name="student-teacherworkflow",
                definition=WorkflowAgentDefinition(workflow=workflow_yaml),
            )

            conversation = openai_client.conversations.create()

            response = openai_client.responses.create(
                conversation=conversation.id,
                extra_body={"agent": AgentReference(name=workflow_agent.name).as_dict()},
                input="1 + 1 = ?",
                stream=False,
            )

            # Verify we got workflow actions in the response
            workflow_action_count = sum(
                1 for item in response.output if hasattr(item, "type") and item.type == "workflow_action"
            )
            assert workflow_action_count > 0, f"Expected workflow actions in response, got {workflow_action_count}"

            # List conversation items to verify workflow actions in conversation
            items = openai_client.conversations.items.list(conversation_id=conversation.id)
            # Must iterate to create the span
            _ = list(items)

            openai_client.conversations.delete(conversation_id=conversation.id)
            project_client.agents.delete_version(agent_name=workflow_agent.name, agent_version=workflow_agent.version)
            project_client.agents.delete_version(agent_name=student_agent.name, agent_version=student_agent.version)
            project_client.agents.delete_version(agent_name=teacher_agent.name, agent_version=teacher_agent.version)

        # Verify workflow action events
        self.exporter.force_flush()
        # Workflow agents use agent name in span, not deployment name
        spans = self.exporter.get_spans_by_name(f"responses {workflow_agent.name}")
        assert len(spans) >= 1
        span = spans[0]

        # Check for workflow action events
        workflow_events = [e for e in span.events if e.name == "gen_ai.workflow.action"]
        assert len(workflow_events) > 0

        # Verify workflow event content structure
        for event in workflow_events:
            content_str = event.attributes.get("gen_ai.event.content", "{}")
            content = json.loads(content_str)
            assert "content" in content
            assert isinstance(content["content"], list)
            assert len(content["content"]) > 0
            assert content["content"][0]["type"] == "workflow_action"
            assert "status" in content["content"][0]

        # Verify conversation items listing span also has workflow actions
        list_spans = self.exporter.get_spans_by_name("list_conversation_items")
        assert len(list_spans) >= 1
        list_span = list_spans[0]

        # Check for workflow action events in list items span
        list_workflow_events = [e for e in list_span.events if e.name == "gen_ai.workflow.action"]
        assert len(list_workflow_events) > 0

        # Verify workflow event content structure in list items
        for event in list_workflow_events:
            content_str = event.attributes.get("gen_ai.event.content", "{}")
            content = json.loads(content_str)
            assert "content" in content
            assert isinstance(content["content"], list)
            assert len(content["content"]) > 0
            assert content["content"][0]["type"] == "workflow_action"
            assert "status" in content["content"][0]
            # With content recording ON, action_id should be present
            assert "action_id" in content["content"][0]

    @pytest.mark.skip(reason="recordings not working for responses API")
    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy
    def test_workflow_agent_non_streaming_without_content_recording(self, **kwargs):
        """Test workflow agent with non-streaming and content recording disabled."""
        from azure.ai.projects.models import WorkflowAgentDefinition, AgentReference

        self.cleanup()
        os.environ.update(
            {CONTENT_TRACING_ENV_VARIABLE: "False", "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True"}
        )
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            deployment_name = self.test_agents_params["model_deployment_name"]
            openai_client = project_client.get_openai_client()

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
            workflow_agent = project_client.agents.create_version(
                agent_name="test-workflow",
                definition=WorkflowAgentDefinition(workflow=workflow_yaml),
            )

            conversation = openai_client.conversations.create()

            response = openai_client.responses.create(
                conversation=conversation.id,
                extra_body={"agent": AgentReference(name=workflow_agent.name).as_dict()},
                input="Test workflow",
                stream=False,
            )

            # List conversation items to verify workflow actions in conversation
            items = openai_client.conversations.items.list(conversation_id=conversation.id)
            # Must iterate to create the span
            _ = list(items)

            openai_client.conversations.delete(conversation_id=conversation.id)
            project_client.agents.delete_version(agent_name=workflow_agent.name, agent_version=workflow_agent.version)

        # Verify workflow action events (content recording off)
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"responses {workflow_agent.name}")
        assert len(spans) >= 1
        span = spans[0]

        # Check for workflow action events - should still exist but with limited content
        workflow_events = [e for e in span.events if e.name == "gen_ai.workflow.action"]
        assert len(workflow_events) > 0

        # Verify workflow event content structure (no action_id/previous_action_id when content off)
        for event in workflow_events:
            content_str = event.attributes.get("gen_ai.event.content", "{}")
            content = json.loads(content_str)
            assert "content" in content
            assert isinstance(content["content"], list)
            assert len(content["content"]) > 0
            assert content["content"][0]["type"] == "workflow_action"
            assert "status" in content["content"][0]
            # action_id and previous_action_id should NOT be present when content recording is off
            assert "action_id" not in content["content"][0]
            assert "previous_action_id" not in content["content"][0]

        # Verify conversation items listing span also has workflow actions
        list_spans = self.exporter.get_spans_by_name("list_conversation_items")
        assert len(list_spans) >= 1
        list_span = list_spans[0]

        # Check for workflow action events in list items span
        list_workflow_events = [e for e in list_span.events if e.name == "gen_ai.workflow.action"]
        assert len(list_workflow_events) > 0

        # Verify workflow event content structure in list items (content recording OFF)
        for event in list_workflow_events:
            content_str = event.attributes.get("gen_ai.event.content", "{}")
            content = json.loads(content_str)
            assert "content" in content
            assert isinstance(content["content"], list)
            assert len(content["content"]) > 0
            assert content["content"][0]["type"] == "workflow_action"
            assert "status" in content["content"][0]
            # action_id and previous_action_id should NOT be present when content recording is off
            assert "action_id" not in content["content"][0]
            assert "previous_action_id" not in content["content"][0]

    @pytest.mark.skip(reason="recordings not working for responses API")
    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy
    def test_workflow_agent_streaming_with_content_recording(self, **kwargs):
        """Test workflow agent with streaming and content recording enabled."""
        from azure.ai.projects.models import (
            WorkflowAgentDefinition,
            AgentReference,
            PromptAgentDefinition,
            ResponseStreamEventType,
        )

        self.cleanup()
        os.environ.update(
            {CONTENT_TRACING_ENV_VARIABLE: "True", "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True"}
        )
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            deployment_name = self.test_agents_params["model_deployment_name"]
            openai_client = project_client.get_openai_client()

            # Create Teacher Agent
            teacher_agent = project_client.agents.create_version(
                agent_name="teacher-agent",
                definition=PromptAgentDefinition(
                    model=deployment_name,
                    instructions="""You are a teacher that create pre-school math question for student and check answer. 
                                    If the answer is correct, you stop the conversation by saying [COMPLETE]. 
                                    If the answer is wrong, you ask student to fix it.""",
                ),
            )

            # Create Student Agent
            student_agent = project_client.agents.create_version(
                agent_name="student-agent",
                definition=PromptAgentDefinition(
                    model=deployment_name,
                    instructions="""You are a student who answers questions from the teacher. 
                                    When the teacher gives you a question, you answer it.""",
                ),
            )

            # Create Multi-Agent Workflow
            workflow_yaml = f"""
kind: workflow
trigger:
  kind: OnConversationStart
  id: my_workflow
  actions:
    - kind: SetVariable
      id: set_variable_input_task
      variable: Local.LatestMessage
      value: "=UserMessage(System.LastMessageText)"

    - kind: CreateConversation
      id: create_student_conversation
      conversationId: Local.StudentConversationId

    - kind: CreateConversation
      id: create_teacher_conversation
      conversationId: Local.TeacherConversationId

    - kind: InvokeAzureAgent
      id: student_agent
      description: The student node
      conversationId: "=Local.StudentConversationId"
      agent:
        name: {student_agent.name}
      input:
        messages: "=Local.LatestMessage"
      output:
        messages: Local.LatestMessage

    - kind: InvokeAzureAgent
      id: teacher_agent
      description: The teacher node
      conversationId: "=Local.TeacherConversationId"
      agent:
        name: {teacher_agent.name}
      input:
        messages: "=Local.LatestMessage"
      output:
        messages: Local.LatestMessage

    - kind: SetVariable
      id: set_variable_turncount
      variable: Local.TurnCount
      value: "=Local.TurnCount + 1"

    - kind: ConditionGroup
      id: completion_check
      conditions:
        - condition: '=!IsBlank(Find("[COMPLETE]", Upper(Last(Local.LatestMessage).Text)))'
          id: check_done
          actions:
            - kind: EndConversation
              id: end_workflow

        - condition: "=Local.TurnCount >= 4"
          id: check_turn_count_exceeded
          actions:
            - kind: SendActivity
              id: send_activity_tired
              activity: "Let's try again later...I am tired."

      elseActions:
        - kind: GotoAction
          id: goto_student_agent
          actionId: student_agent
"""

            workflow_agent = project_client.agents.create_version(
                agent_name="student-teacherworkflow",
                definition=WorkflowAgentDefinition(workflow=workflow_yaml),
            )

            conversation = openai_client.conversations.create()

            stream = openai_client.responses.create(
                conversation=conversation.id,
                extra_body={"agent": AgentReference(name=workflow_agent.name).as_dict()},
                input="1 + 1 = ?",
                stream=True,
            )

            # Consume the stream and track workflow actions
            workflow_action_count = 0
            for event in stream:
                if (
                    event.type == ResponseStreamEventType.RESPONSE_OUTPUT_ITEM_ADDED
                    and event.item.type == "workflow_action"
                ):
                    workflow_action_count += 1

            # Verify we got workflow actions during streaming
            assert workflow_action_count > 0, f"Expected workflow actions during streaming, got {workflow_action_count}"

            # List conversation items to verify workflow actions in conversation
            items = openai_client.conversations.items.list(conversation_id=conversation.id)
            # Must iterate to create the span
            items_list = list(items)
            print(f"\n=== Streaming test: Found {len(items_list)} conversation items ===")

            openai_client.conversations.delete(conversation_id=conversation.id)
            project_client.agents.delete_version(agent_name=workflow_agent.name, agent_version=workflow_agent.version)
            project_client.agents.delete_version(agent_name=student_agent.name, agent_version=student_agent.version)
            project_client.agents.delete_version(agent_name=teacher_agent.name, agent_version=teacher_agent.version)

        # Verify workflow action events in streaming mode
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"responses {workflow_agent.name}")
        assert len(spans) >= 1
        span = spans[0]

        # Check for workflow action events
        workflow_events = [e for e in span.events if e.name == "gen_ai.workflow.action"]
        assert len(workflow_events) > 0

        # Verify workflow event content structure
        for event in workflow_events:
            content_str = event.attributes.get("gen_ai.event.content", "{}")
            content = json.loads(content_str)
            assert "content" in content
            assert isinstance(content["content"], list)
            assert len(content["content"]) > 0
            assert content["content"][0]["type"] == "workflow_action"
            assert "status" in content["content"][0]

        # Verify conversation items listing span also has workflow actions
        list_spans = self.exporter.get_spans_by_name("list_conversation_items")
        assert len(list_spans) >= 1
        list_span = list_spans[0]

        # Check for workflow action events in list items span
        list_workflow_events = [e for e in list_span.events if e.name == "gen_ai.workflow.action"]
        assert len(list_workflow_events) > 0

        # Verify workflow event content structure in list items
        for event in list_workflow_events:
            content_str = event.attributes.get("gen_ai.event.content", "{}")
            content = json.loads(content_str)
            assert "content" in content
            assert isinstance(content["content"], list)
            assert len(content["content"]) > 0
            assert content["content"][0]["type"] == "workflow_action"
            assert "status" in content["content"][0]
            # With content recording ON, action_id should be present
            assert "action_id" in content["content"][0]

    @pytest.mark.skip(reason="recordings not working for responses API")
    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy
    def test_workflow_agent_streaming_without_content_recording(self, **kwargs):
        """Test workflow agent with streaming and content recording disabled."""
        from azure.ai.projects.models import WorkflowAgentDefinition, AgentReference

        self.cleanup()
        os.environ.update(
            {CONTENT_TRACING_ENV_VARIABLE: "False", "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True"}
        )
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:
            deployment_name = self.test_agents_params["model_deployment_name"]
            openai_client = project_client.get_openai_client()

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
            workflow_agent = project_client.agents.create_version(
                agent_name="test-workflow",
                definition=WorkflowAgentDefinition(workflow=workflow_yaml),
            )

            conversation = openai_client.conversations.create()

            stream = openai_client.responses.create(
                conversation=conversation.id,
                extra_body={"agent": AgentReference(name=workflow_agent.name).as_dict()},
                input="Test workflow",
                stream=True,
            )

            # Consume the stream
            for _ in stream:
                pass

            # List conversation items to verify workflow actions in conversation
            items = openai_client.conversations.items.list(conversation_id=conversation.id)
            # Must iterate to create the span
            items_list = list(items)
            print(f"\n=== Streaming test (no content recording): Found {len(items_list)} conversation items ===")

            openai_client.conversations.delete(conversation_id=conversation.id)
            project_client.agents.delete_version(agent_name=workflow_agent.name, agent_version=workflow_agent.version)

        # Verify workflow action events (content recording off)
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name(f"responses {workflow_agent.name}")
        assert len(spans) >= 1
        span = spans[0]

        # Check for workflow action events - should still exist but with limited content
        workflow_events = [e for e in span.events if e.name == "gen_ai.workflow.action"]
        assert len(workflow_events) > 0

        # Verify workflow event content structure (no action_id/previous_action_id when content off)
        for event in workflow_events:
            content_str = event.attributes.get("gen_ai.event.content", "{}")
            content = json.loads(content_str)
            assert "content" in content
            assert isinstance(content["content"], list)
            assert len(content["content"]) > 0
            assert content["content"][0]["type"] == "workflow_action"
            assert "status" in content["content"][0]
            # action_id and previous_action_id should NOT be present when content recording is off
            assert "action_id" not in content["content"][0]
            assert "previous_action_id" not in content["content"][0]

        # Verify conversation items listing span also has workflow actions
        list_spans = self.exporter.get_spans_by_name("list_conversation_items")
        assert len(list_spans) >= 1
        list_span = list_spans[0]

        # Check for workflow action events in list items span
        list_workflow_events = [e for e in list_span.events if e.name == "gen_ai.workflow.action"]
        assert len(list_workflow_events) > 0

        # Verify workflow event content structure in list items (content recording OFF)
        for event in list_workflow_events:
            content_str = event.attributes.get("gen_ai.event.content", "{}")
            content = json.loads(content_str)
            assert "content" in content
            assert isinstance(content["content"], list)
            assert len(content["content"]) > 0
            assert content["content"][0]["type"] == "workflow_action"
            assert "status" in content["content"][0]
            # action_id and previous_action_id should NOT be present when content recording is off
            assert "action_id" not in content["content"][0]
            assert "previous_action_id" not in content["content"][0]
