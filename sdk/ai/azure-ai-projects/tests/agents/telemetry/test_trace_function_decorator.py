# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for the trace_function decorator with synchronous functions."""
import pytest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from azure.ai.projects.telemetry._trace_function import trace_function
from gen_ai_trace_verifier import GenAiTraceVerifier
from memory_trace_exporter import MemoryTraceExporter


@pytest.mark.skip(
    reason="Skipped until re-enabled and recorded on Foundry endpoint that supports the new versioning schema"
)
class TestTraceFunctionDecorator:
    """Tests for trace_function decorator with synchronous functions."""

    @pytest.fixture(scope="function")
    def setup_telemetry(self):
        """Setup telemetry for tests."""
        tracer_provider = TracerProvider()
        trace._TRACER_PROVIDER = tracer_provider
        self.exporter = MemoryTraceExporter()
        span_processor = SimpleSpanProcessor(self.exporter)
        tracer_provider.add_span_processor(span_processor)
        yield
        self.exporter.shutdown()
        trace._TRACER_PROVIDER = None

    def test_basic_function_with_primitives(self, setup_telemetry):
        """Test decorator with a function that has primitive type parameters and return value."""

        @trace_function()
        def add_numbers(a: int, b: int) -> int:
            return a + b

        result = add_numbers(5, 3)
        assert result == 8

        spans = self.exporter.get_spans_by_name("add_numbers")
        assert len(spans) == 1
        span = spans[0]

        # Verify parameters are traced
        expected_attributes = [
            ("code.function.parameter.a", 5),
            ("code.function.parameter.b", 3),
            ("code.function.return.value", 8),
        ]
        attributes_match = GenAiTraceVerifier().check_decorator_span_attributes(span, expected_attributes)
        assert attributes_match is True

    def test_function_with_string_parameters(self, setup_telemetry):
        """Test decorator with string parameters."""

        @trace_function()
        def greet(name: str, greeting: str = "Hello") -> str:
            return f"{greeting}, {name}!"

        result = greet("Alice", "Hi")
        assert result == "Hi, Alice!"

        spans = self.exporter.get_spans_by_name("greet")
        assert len(spans) == 1
        span = spans[0]

        expected_attributes = [
            ("code.function.parameter.name", "Alice"),
            ("code.function.parameter.greeting", "Hi"),
            ("code.function.return.value", "Hi, Alice!"),
        ]
        attributes_match = GenAiTraceVerifier().check_decorator_span_attributes(span, expected_attributes)
        assert attributes_match is True

    def test_function_with_list_parameter(self, setup_telemetry):
        """Test decorator with list parameters."""

        @trace_function()
        def sum_list(numbers: list) -> int:
            return sum(numbers)

        result = sum_list([1, 2, 3, 4, 5])
        assert result == 15

        spans = self.exporter.get_spans_by_name("sum_list")
        assert len(spans) == 1
        span = spans[0]

        expected_attributes = [
            ("code.function.parameter.numbers", [1, 2, 3, 4, 5]),
            ("code.function.return.value", 15),
        ]
        attributes_match = GenAiTraceVerifier().check_decorator_span_attributes(span, expected_attributes)
        assert attributes_match is True

    def test_function_with_dict_parameter(self, setup_telemetry):
        """Test decorator with dict parameters (converted to string)."""

        @trace_function()
        def get_value(data: dict, key: str) -> str:
            return data.get(key, "not found")

        result = get_value({"name": "Alice", "age": 30}, "name")
        assert result == "Alice"

        spans = self.exporter.get_spans_by_name("get_value")
        assert len(spans) == 1
        span = spans[0]

        # Dict parameters are converted to strings
        expected_dict_str = str({"name": "Alice", "age": 30})
        expected_attributes = [
            ("code.function.parameter.data", expected_dict_str),
            ("code.function.parameter.key", "name"),
            ("code.function.return.value", "Alice"),
        ]
        attributes_match = GenAiTraceVerifier().check_decorator_span_attributes(span, expected_attributes)
        assert attributes_match is True

    def test_function_with_nested_collections(self, setup_telemetry):
        """Test decorator with nested collections (converted to string)."""

        @trace_function()
        def process_nested(data: list) -> int:
            return len(data)

        nested_data = [[1, 2], [3, 4], [5, 6]]
        result = process_nested(nested_data)
        assert result == 3

        spans = self.exporter.get_spans_by_name("process_nested")
        assert len(spans) == 1
        span = spans[0]

        # Nested collections are converted to strings
        expected_data_str = str(nested_data)
        expected_attributes = [
            ("code.function.parameter.data", expected_data_str),
            ("code.function.return.value", 3),
        ]
        attributes_match = GenAiTraceVerifier().check_decorator_span_attributes(span, expected_attributes)
        assert attributes_match is True

    def test_function_with_custom_span_name(self, setup_telemetry):
        """Test decorator with custom span name."""

        @trace_function(span_name="custom_operation")
        def calculate(x: int, y: int) -> int:
            return x * y

        result = calculate(4, 7)
        assert result == 28

        spans = self.exporter.get_spans_by_name("custom_operation")
        assert len(spans) == 1
        span = spans[0]

        expected_attributes = [
            ("code.function.parameter.x", 4),
            ("code.function.parameter.y", 7),
            ("code.function.return.value", 28),
        ]
        attributes_match = GenAiTraceVerifier().check_decorator_span_attributes(span, expected_attributes)
        assert attributes_match is True

    def test_function_with_no_return_value(self, setup_telemetry):
        """Test decorator with a function that returns None."""

        @trace_function()
        def log_message(message: str) -> None:
            pass  # Just a placeholder

        result = log_message("Test message")
        assert result is None

        spans = self.exporter.get_spans_by_name("log_message")
        assert len(spans) == 1
        span = spans[0]

        # Only parameter should be traced, no return value attribute
        expected_attributes = [
            ("code.function.parameter.message", "Test message"),
        ]
        attributes_match = GenAiTraceVerifier().check_decorator_span_attributes(span, expected_attributes)
        assert attributes_match is True

    def test_function_with_boolean_parameters(self, setup_telemetry):
        """Test decorator with boolean parameters."""

        @trace_function()
        def check_status(is_active: bool, is_verified: bool) -> str:
            if is_active and is_verified:
                return "approved"
            return "pending"

        result = check_status(True, False)
        assert result == "pending"

        spans = self.exporter.get_spans_by_name("check_status")
        assert len(spans) == 1
        span = spans[0]

        expected_attributes = [
            ("code.function.parameter.is_active", True),
            ("code.function.parameter.is_verified", False),
            ("code.function.return.value", "pending"),
        ]
        attributes_match = GenAiTraceVerifier().check_decorator_span_attributes(span, expected_attributes)
        assert attributes_match is True

    def test_function_with_float_parameters(self, setup_telemetry):
        """Test decorator with float parameters."""

        @trace_function()
        def calculate_average(a: float, b: float, c: float) -> float:
            return (a + b + c) / 3

        result = calculate_average(10.5, 20.3, 15.2)
        assert abs(result - 15.333333333333334) < 0.0001

        spans = self.exporter.get_spans_by_name("calculate_average")
        assert len(spans) == 1
        span = spans[0]

        expected_attributes = [
            ("code.function.parameter.a", 10.5),
            ("code.function.parameter.b", 20.3),
            ("code.function.parameter.c", 15.2),
            ("code.function.return.value", result),
        ]
        attributes_match = GenAiTraceVerifier().check_decorator_span_attributes(span, expected_attributes)
        assert attributes_match is True

    def test_function_with_tuple_parameter(self, setup_telemetry):
        """Test decorator with tuple parameters."""

        @trace_function()
        def get_coordinates(point: tuple) -> str:
            return f"x={point[0]}, y={point[1]}"

        result = get_coordinates((10, 20))
        assert result == "x=10, y=20"

        spans = self.exporter.get_spans_by_name("get_coordinates")
        assert len(spans) == 1
        span = spans[0]

        expected_attributes = [
            ("code.function.parameter.point", (10, 20)),
            ("code.function.return.value", "x=10, y=20"),
        ]
        attributes_match = GenAiTraceVerifier().check_decorator_span_attributes(span, expected_attributes)
        assert attributes_match is True

    def test_function_with_set_parameter(self, setup_telemetry):
        """Test decorator with set parameters (converted to string)."""

        @trace_function()
        def count_unique(items: set) -> int:
            return len(items)

        result = count_unique({1, 2, 3, 4, 5})
        assert result == 5

        spans = self.exporter.get_spans_by_name("count_unique")
        assert len(spans) == 1
        span = spans[0]

        # Sets are converted to strings, but we need to compare the actual set values
        # since set string representation order is non-deterministic
        assert span.attributes is not None
        assert "code.function.parameter.items" in span.attributes
        assert "code.function.return.value" in span.attributes

        # Convert the string back to a set for comparison
        import ast

        items_str = span.attributes["code.function.parameter.items"]
        assert isinstance(items_str, str)
        items_value = ast.literal_eval(items_str)
        assert items_value == {1, 2, 3, 4, 5}
        assert span.attributes["code.function.return.value"] == 5

    def test_function_with_exception(self, setup_telemetry):
        """Test decorator records exception information."""

        @trace_function()
        def divide(a: int, b: int) -> float:
            return a / b

        with pytest.raises(ZeroDivisionError):
            divide(10, 0)

        spans = self.exporter.get_spans_by_name("divide")
        assert len(spans) == 1
        span = spans[0]

        # Check that parameters were traced
        expected_attributes = [
            ("code.function.parameter.a", 10),
            ("code.function.parameter.b", 0),
            ("error.type", "ZeroDivisionError"),
        ]
        attributes_match = GenAiTraceVerifier().check_decorator_span_attributes(span, expected_attributes)
        assert attributes_match is True

        # Verify exception was recorded as an event
        assert len(span.events) > 0
        exception_event = None
        for event in span.events:
            if event.name == "exception":
                exception_event = event
                break
        assert exception_event is not None

    def test_function_with_mixed_parameters(self, setup_telemetry):
        """Test decorator with mixed parameter types."""

        @trace_function()
        def process_data(name: str, count: int, active: bool, scores: list) -> dict:
            return {
                "name": name,
                "count": count,
                "active": active,
                "average": sum(scores) / len(scores) if scores else 0,
            }

        result = process_data("test", 5, True, [90, 85, 95])
        assert result["name"] == "test"
        assert result["average"] == 90

        spans = self.exporter.get_spans_by_name("process_data")
        assert len(spans) == 1
        span = spans[0]

        expected_result_str = str(result)
        expected_attributes = [
            ("code.function.parameter.name", "test"),
            ("code.function.parameter.count", 5),
            ("code.function.parameter.active", True),
            ("code.function.parameter.scores", [90, 85, 95]),
            ("code.function.return.value", expected_result_str),
        ]
        attributes_match = GenAiTraceVerifier().check_decorator_span_attributes(span, expected_attributes)
        assert attributes_match is True
