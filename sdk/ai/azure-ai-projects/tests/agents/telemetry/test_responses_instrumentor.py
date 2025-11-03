# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import pytest
from typing import Optional, Tuple
from azure.ai.projects.telemetry import AIProjectInstrumentor, _utils
from azure.core.settings import settings
from gen_ai_trace_verifier import GenAiTraceVerifier
from openai import OpenAI
from devtools_testutils import recorded_by_proxy

from test_base import servicePreparer
from test_ai_instrumentor_base import TestAiAgentsInstrumentorBase, CONTENT_TRACING_ENV_VARIABLE

settings.tracing_implementation = "OpenTelemetry"
_utils._span_impl_type = settings.tracing_implementation()


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

    @pytest.mark.skip(reason="recordings not working for responses API")
    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy
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
    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy
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
                    "gen_ai.event.content": '{"role": "user"}',
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.provider.name": "azure.openai",
                    "gen_ai.message.role": "assistant",
                    "gen_ai.event.content": '{"role": "assistant"}',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.skip(reason="recordings not working for responses API")
    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy
    def test_sync_streaming_with_content_recording(self, **kwargs):
        """Test synchronous streaming responses with content recording enabled."""
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
    @recorded_by_proxy
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

    @pytest.mark.skip(reason="recordings not working for responses API")
    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy
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

    @pytest.mark.skip(reason="recordings not working for responses API")
    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy
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

    @pytest.mark.skip(reason="recordings not working for responses API")
    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy
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
