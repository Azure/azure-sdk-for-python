# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import azure.ai.inference as sdk
from azure.ai.inference.tracing import AIInferenceInstrumentor

from model_inference_test_base import (
    ModelClientTestBase,
    ServicePreparerChatCompletions,
)

from azure.core.settings import settings
from devtools_testutils.aio import recorded_by_proxy_async
from memory_trace_exporter import MemoryTraceExporter
from gen_ai_trace_verifier import GenAiTraceVerifier
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

CONTENT_TRACING_ENV_VARIABLE = "AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED"
content_tracing_initial_value = os.getenv(CONTENT_TRACING_ENV_VARIABLE)


# The test class name needs to start with "Test" to get collected by pytest
class TestClientTracingAsync(ModelClientTestBase):

    @classmethod
    def teardown_class(cls):
        if content_tracing_initial_value is not None:
            os.environ[CONTENT_TRACING_ENV_VARIABLE] = content_tracing_initial_value

    # **********************************************************************************
    #
    #                            TRACING TESTS - CHAT COMPLETIONS
    #
    # **********************************************************************************

    def setup_memory_trace_exporter(self) -> MemoryTraceExporter:
        # Setup Azure Core settings to use OpenTelemetry tracing
        settings.tracing_implementation = "OpenTelemetry"
        trace.set_tracer_provider(TracerProvider())
        _ = trace.get_tracer(__name__)
        memoryExporter = MemoryTraceExporter()
        span_processor = SimpleSpanProcessor(memoryExporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        return span_processor, memoryExporter

    def modify_env_var(self, name, new_value):
        current_value = os.getenv(name)
        os.environ[name] = new_value
        return current_value

    @ServicePreparerChatCompletions()
    @recorded_by_proxy_async
    async def test_chat_completion_async_tracing_content_recording_disabled(self, **kwargs):
        # Make sure code is not instrumented due to a previous test exception
        try:
            AIInferenceInstrumentor().uninstrument()
        except RuntimeError as e:
            pass
        self.modify_env_var(CONTENT_TRACING_ENV_VARIABLE, "False")
        client = self._create_async_chat_client(**kwargs)
        model = kwargs.pop("azure_ai_chat_model").lower()
        processor, exporter = self.setup_memory_trace_exporter()
        AIInferenceInstrumentor().instrument()
        _ = await client.complete(
            messages=[
                sdk.models.SystemMessage(content="You are a helpful assistant."),
                sdk.models.UserMessage(content="What is the capital of France?"),
            ],
        )
        processor.force_flush()
        spans = exporter.get_spans_by_name_starts_with("chat ")
        if len(spans) == 0:
            spans = exporter.get_spans_by_name("chat")
        assert len(spans) == 1
        span = spans[0]
        expected_attributes = [
            ("gen_ai.operation.name", "chat"),
            ("gen_ai.system", "az.ai.inference"),
            ("gen_ai.request.model", "chat"),
            ("server.address", ""),
            ("gen_ai.response.id", ""),
            ("gen_ai.response.model", model),
            ("gen_ai.usage.input_tokens", "+"),
            ("gen_ai.usage.output_tokens", "+"),
            ("gen_ai.response.finish_reasons", ("stop",)),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        expected_events = [
            {
                "name": "gen_ai.choice",
                "attributes": {
                    "gen_ai.system": "az.ai.inference",
                    "gen_ai.event.content": '{"finish_reason": "stop", "index": 0}',
                },
            }
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True
        AIInferenceInstrumentor().uninstrument()
