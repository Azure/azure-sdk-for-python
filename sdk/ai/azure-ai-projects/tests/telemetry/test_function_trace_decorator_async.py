# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
from opentelemetry import trace
from opentelemetry.sdk.trace import Span, TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from memory_trace_exporter import MemoryTraceExporter
from gen_ai_trace_verifier import GenAiTraceVerifier
from azure.ai.projects.telemetry import trace_function
import pytest


# Dummy helper functions with decorators
@trace_function("basic_datatypes_positional")
async def basic_datatypes_positional(a: int, b: str, c: bool) -> str:
    await asyncio.sleep(1)
    return f"{a} - {b} - {c}"


# Pytest unit tests
class TestFunctionTraceDecoratorAsync:
    def setup_memory_trace_exporter(self) -> MemoryTraceExporter:
        trace.set_tracer_provider(TracerProvider())
        tracer = trace.get_tracer(__name__)
        memoryExporter = MemoryTraceExporter()
        span_processor = SimpleSpanProcessor(memoryExporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        return span_processor, memoryExporter

    @pytest.mark.asyncio
    async def test_basic_datatypes_positional_arguments(self):
        processor, exporter = self.setup_memory_trace_exporter()
        result = await basic_datatypes_positional(1, "test", True)
        assert result == "1 - test - True"
        processor.force_flush()
        spans = exporter.get_spans_by_name("basic_datatypes_positional")
        assert len(spans) == 1
        span = spans[0]

        assert GenAiTraceVerifier().check_decorator_span_attributes(
            span,
            [
                ("code.function.parameter.a", 1),
                ("code.function.parameter.b", "test"),
                ("code.function.parameter.c", True),
                ("code.function.return.value", "1 - test - True"),
            ],
        )
