# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Any, Callable, Tuple, Optional, Dict, List, Set
from opentelemetry import trace
from opentelemetry.sdk.trace import Span, TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from memory_trace_exporter import MemoryTraceExporter
from gen_ai_trace_verifier import GenAiTraceVerifier
from azure.ai.projects.telemetry import trace_function
from pytest import raises as pytest_raises


class EmptyClass:
    pass


# Dummy helper functions with decorators
@trace_function("basic_datatypes_positional")
def basic_datatypes_positional(a: int, b: str, c: bool) -> str:
    return f"{a} - {b} - {c}"


@trace_function("basic_datatypes_named")
def basic_datatypes_named(a: int, b: str, c: bool) -> str:
    return f"{a} - {b} - {c}"


@trace_function("no_arguments_no_return")
def no_arguments_no_return() -> None:
    pass


@trace_function("complex_datatypes_positional")
def complex_datatypes_positional(a: List[int], b: Dict[str, int], c: Tuple[int, int]) -> str:
    print(f"Type of b: {type(b)}")  # Print the type of the second argument
    return f"{a} - {b} - {c}"


@trace_function("complex_datatypes_named")
def complex_datatypes_named(a: List[int], b: Dict[str, int], c: Tuple[int, int]) -> str:
    return f"{a} - {b} - {c}"


@trace_function("none_argument")
def none_argument(a: Optional[int]) -> str:
    return f"{a}"


@trace_function("none_return_value")
def none_return_value() -> None:
    return None


@trace_function("list_argument_return_value")
def list_argument_return_value(a: List[int]) -> List[int]:
    return a


@trace_function("dict_argument_return_value")
def dict_argument_return_value(a: Dict[str, int]) -> Dict[str, int]:
    return a


@trace_function("tuple_argument_return_value")
def tuple_argument_return_value(a: Tuple[int, int]) -> Tuple[int, int]:
    return a


@trace_function("set_argument_return_value")
def set_argument_return_value(a: Set[int]) -> Set[int]:
    return a


@trace_function("raise_exception")
def raise_exception() -> None:
    raise ValueError("Test exception")


@trace_function()
def empty_class_argument(a: EmptyClass) -> EmptyClass:
    return a


@trace_function()
def empty_class_return_value() -> EmptyClass:
    return EmptyClass()


@trace_function()
def list_with_empty_class(a: list) -> list:
    return a


@trace_function()
def dict_with_empty_class(a: dict) -> dict:
    return a


@trace_function()
def tuple_with_empty_class(a: tuple) -> tuple:
    return a


@trace_function()
def set_with_empty_class(a: set) -> set:
    return a


@trace_function()
def nested_collections(a: list) -> list:
    return a


# Pytest unit tests
class TestFunctionTraceDecorator:
    def setup_memory_trace_exporter(self) -> MemoryTraceExporter:
        trace.set_tracer_provider(TracerProvider())
        tracer = trace.get_tracer(__name__)
        memoryExporter = MemoryTraceExporter()
        span_processor = SimpleSpanProcessor(memoryExporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        return span_processor, memoryExporter

    def test_basic_datatypes_positional_arguments(self):
        processor, exporter = self.setup_memory_trace_exporter()
        result = basic_datatypes_positional(1, "test", True)
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

    def test_basic_datatypes_named_arguments(self):
        processor, exporter = self.setup_memory_trace_exporter()
        result = basic_datatypes_named(b="test", a=1, c=True)
        assert result == "1 - test - True"
        processor.force_flush()
        spans = exporter.get_spans_by_name("basic_datatypes_named")
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

    def test_no_arguments_no_return_value(self):
        processor, exporter = self.setup_memory_trace_exporter()
        result = no_arguments_no_return()
        assert result is None
        processor.force_flush()
        spans = exporter.get_spans_by_name("no_arguments_no_return")
        assert len(spans) == 1
        span = spans[0]
        assert GenAiTraceVerifier().check_decorator_span_attributes(span, [])

    def test_complex_datatypes_positional_arguments(self):
        processor, exporter = self.setup_memory_trace_exporter()
        result = complex_datatypes_positional([1, 2], {"key": 3}, (4, 5))
        assert result == "[1, 2] - {'key': 3} - (4, 5)"
        processor.force_flush()
        spans = exporter.get_spans_by_name("complex_datatypes_positional")
        assert len(spans) == 1
        span = spans[0]
        assert GenAiTraceVerifier().check_decorator_span_attributes(
            span,
            [
                ("code.function.parameter.a", [1, 2]),
                ("code.function.parameter.b", "{'key': 3}"),
                ("code.function.parameter.c", (4, 5)),
                ("code.function.return.value", "[1, 2] - {'key': 3} - (4, 5)"),
            ],
        )

    def test_complex_datatypes_named_arguments(self):
        processor, exporter = self.setup_memory_trace_exporter()
        result = complex_datatypes_named(a=[1, 2], b={"key": 3}, c=(4, 5))
        assert result == "[1, 2] - {'key': 3} - (4, 5)"
        processor.force_flush()
        spans = exporter.get_spans_by_name("complex_datatypes_named")
        assert len(spans) == 1
        span = spans[0]
        assert GenAiTraceVerifier().check_decorator_span_attributes(
            span,
            [
                ("code.function.parameter.a", [1, 2]),
                ("code.function.parameter.b", "{'key': 3}"),
                ("code.function.parameter.c", (4, 5)),
                ("code.function.return.value", "[1, 2] - {'key': 3} - (4, 5)"),
            ],
        )

    def test_none_argument(self):
        processor, exporter = self.setup_memory_trace_exporter()
        result = none_argument(None)
        assert result == "None"
        processor.force_flush()
        spans = exporter.get_spans_by_name("none_argument")
        assert len(spans) == 1
        span = spans[0]
        assert GenAiTraceVerifier().check_decorator_span_attributes(span, [("code.function.return.value", "None")])

    def test_none_return_value(self):
        processor, exporter = self.setup_memory_trace_exporter()
        result = none_return_value()
        assert result is None
        processor.force_flush()
        spans = exporter.get_spans_by_name("none_return_value")
        assert len(spans) == 1
        span = spans[0]
        assert GenAiTraceVerifier().check_decorator_span_attributes(span, [])

    def test_list_argument_return_value(self):
        processor, exporter = self.setup_memory_trace_exporter()
        result = list_argument_return_value([1, 2, 3])
        assert result == [1, 2, 3]
        processor.force_flush()
        spans = exporter.get_spans_by_name("list_argument_return_value")
        assert len(spans) == 1
        span = spans[0]
        assert GenAiTraceVerifier().check_decorator_span_attributes(
            span, [("code.function.parameter.a", [1, 2, 3]), ("code.function.return.value", [1, 2, 3])]
        )

    def test_dict_argument_return_value(self):
        processor, exporter = self.setup_memory_trace_exporter()
        result = dict_argument_return_value({"key": 1})
        assert result == {"key": 1}
        processor.force_flush()
        spans = exporter.get_spans_by_name("dict_argument_return_value")
        assert len(spans) == 1
        span = spans[0]
        assert GenAiTraceVerifier().check_decorator_span_attributes(
            span, [("code.function.parameter.a", "{'key': 1}"), ("code.function.return.value", "{'key': 1}")]
        )

    def test_tuple_argument_return_value(self):
        processor, exporter = self.setup_memory_trace_exporter()
        result = tuple_argument_return_value((1, 2))
        assert result == (1, 2)
        processor.force_flush()
        spans = exporter.get_spans_by_name("tuple_argument_return_value")
        assert len(spans) == 1
        span = spans[0]
        assert GenAiTraceVerifier().check_decorator_span_attributes(
            span, [("code.function.parameter.a", (1, 2)), ("code.function.return.value", (1, 2))]
        )

    def test_set_argument_return_value(self):
        processor, exporter = self.setup_memory_trace_exporter()
        result = set_argument_return_value({1, 2, 3})
        assert result == {1, 2, 3}
        processor.force_flush()
        spans = exporter.get_spans_by_name("set_argument_return_value")
        assert len(spans) == 1
        span = spans[0]
        assert GenAiTraceVerifier().check_decorator_span_attributes(
            span, [("code.function.parameter.a", "{1, 2, 3}"), ("code.function.return.value", "{1, 2, 3}")]
        )

    def test_exception(self):
        processor, exporter = self.setup_memory_trace_exporter()
        try:
            raise_exception()
            assert False
        except Exception as e:
            processor.force_flush()
            spans = exporter.get_spans_by_name("raise_exception")
            assert len(spans) == 1
            span: Span = spans[0]
            assert span.status.is_ok == False
            assert span.status.description == "ValueError: Test exception"
            assert GenAiTraceVerifier().check_decorator_span_attributes(
                span, [("error.type", e.__class__.__qualname__)]
            )

    def test_object_argument_and_return_value(self):
        processor, exporter = self.setup_memory_trace_exporter()
        empty_instance = EmptyClass()
        result = empty_class_argument(empty_instance)
        assert result == empty_instance
        processor.force_flush()
        spans = exporter.get_spans_by_name("empty_class_argument")
        assert len(spans) == 1
        span = spans[0]
        assert GenAiTraceVerifier().check_decorator_span_attributes(span, [])

    def test_list_with_object(self):
        processor, exporter = self.setup_memory_trace_exporter()
        empty_instance = EmptyClass()
        result = list_with_empty_class([empty_instance, 1, 2, 3])
        assert result == [empty_instance, 1, 2, 3]
        processor.force_flush()
        spans = exporter.get_spans_by_name("list_with_empty_class")
        assert len(spans) == 1
        span = spans[0]
        assert GenAiTraceVerifier().check_decorator_span_attributes(
            span, [("code.function.parameter.a", [1, 2, 3]), ("code.function.return.value", [1, 2, 3])]
        )

    def test_dict_with_object(self):
        processor, exporter = self.setup_memory_trace_exporter()
        empty_instance = EmptyClass()
        result = dict_with_empty_class({"key1": empty_instance, "key2": 1})
        assert result == {"key1": empty_instance, "key2": 1}
        processor.force_flush()
        spans = exporter.get_spans_by_name("dict_with_empty_class")
        assert len(spans) == 1
        span = spans[0]
        assert GenAiTraceVerifier().check_decorator_span_attributes(
            span, [("code.function.parameter.a", "{'key2': 1}"), ("code.function.return.value", "{'key2': 1}")]
        )

    def test_tuple_with_object(self):
        processor, exporter = self.setup_memory_trace_exporter()
        empty_instance = EmptyClass()
        result = tuple_with_empty_class((empty_instance, 1, 2, 3))
        assert result == (empty_instance, 1, 2, 3)
        processor.force_flush()
        spans = exporter.get_spans_by_name("tuple_with_empty_class")
        assert len(spans) == 1
        span = spans[0]
        assert GenAiTraceVerifier().check_decorator_span_attributes(
            span, [("code.function.parameter.a", (1, 2, 3)), ("code.function.return.value", (1, 2, 3))]
        )

    def test_set_with_object(self):
        processor, exporter = self.setup_memory_trace_exporter()
        empty_instance = EmptyClass()
        result = set_with_empty_class({empty_instance, 1, 2, 3})
        assert result == {empty_instance, 1, 2, 3}
        processor.force_flush()
        spans = exporter.get_spans_by_name("set_with_empty_class")
        assert len(spans) == 1
        span = spans[0]
        assert GenAiTraceVerifier().check_decorator_span_attributes(
            span, [("code.function.parameter.a", "{1, 2, 3}"), ("code.function.return.value", "{1, 2, 3}")]
        )

    def test_nested_collections(self):
        processor, exporter = self.setup_memory_trace_exporter()
        nested_instance = [1, [2, 3], {"key": [4, 5]}, (6, {7, 8})]
        result = nested_collections(nested_instance)
        assert result == nested_instance
        processor.force_flush()
        spans = exporter.get_spans_by_name("nested_collections")
        assert len(spans) == 1
        span = spans[0]
        assert GenAiTraceVerifier().check_decorator_span_attributes(
            span,
            [("code.function.parameter.a", str(nested_instance)), ("code.function.return.value", str(nested_instance))],
        )
