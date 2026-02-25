# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for the trace_function decorator with asynchronous functions."""
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
class TestTraceFunctionDecoratorAsync:
    """Tests for trace_function decorator with asynchronous functions."""

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

    @pytest.mark.asyncio
    async def test_async_basic_function_with_primitives(self, setup_telemetry):
        """Test decorator with an async function that has primitive type parameters."""

        @trace_function()
        async def add_numbers_async(a: int, b: int) -> int:
            return a + b

        result = await add_numbers_async(5, 3)
        assert result == 8

        spans = self.exporter.get_spans_by_name("add_numbers_async")
        assert len(spans) == 1
        span = spans[0]

        expected_attributes = [
            ("code.function.parameter.a", 5),
            ("code.function.parameter.b", 3),
            ("code.function.return.value", 8),
        ]
        attributes_match = GenAiTraceVerifier().check_decorator_span_attributes(span, expected_attributes)
        assert attributes_match is True

    @pytest.mark.asyncio
    async def test_async_function_with_string_parameters(self, setup_telemetry):
        """Test decorator with async function and string parameters."""

        @trace_function()
        async def greet_async(name: str, greeting: str = "Hello") -> str:
            return f"{greeting}, {name}!"

        result = await greet_async("Bob", "Good morning")
        assert result == "Good morning, Bob!"

        spans = self.exporter.get_spans_by_name("greet_async")
        assert len(spans) == 1
        span = spans[0]

        expected_attributes = [
            ("code.function.parameter.name", "Bob"),
            ("code.function.parameter.greeting", "Good morning"),
            ("code.function.return.value", "Good morning, Bob!"),
        ]
        attributes_match = GenAiTraceVerifier().check_decorator_span_attributes(span, expected_attributes)
        assert attributes_match is True

    @pytest.mark.asyncio
    async def test_async_function_with_list_parameter(self, setup_telemetry):
        """Test decorator with async function and list parameters."""

        @trace_function()
        async def sum_list_async(numbers: list) -> int:
            return sum(numbers)

        result = await sum_list_async([10, 20, 30, 40])
        assert result == 100

        spans = self.exporter.get_spans_by_name("sum_list_async")
        assert len(spans) == 1
        span = spans[0]

        expected_attributes = [
            ("code.function.parameter.numbers", [10, 20, 30, 40]),
            ("code.function.return.value", 100),
        ]
        attributes_match = GenAiTraceVerifier().check_decorator_span_attributes(span, expected_attributes)
        assert attributes_match is True

    @pytest.mark.asyncio
    async def test_async_function_with_dict_parameter(self, setup_telemetry):
        """Test decorator with async function and dict parameters."""

        @trace_function()
        async def get_value_async(data: dict, key: str) -> str:
            return data.get(key, "not found")

        result = await get_value_async({"city": "Seattle", "state": "WA"}, "city")
        assert result == "Seattle"

        spans = self.exporter.get_spans_by_name("get_value_async")
        assert len(spans) == 1
        span = spans[0]

        expected_dict_str = str({"city": "Seattle", "state": "WA"})
        expected_attributes = [
            ("code.function.parameter.data", expected_dict_str),
            ("code.function.parameter.key", "city"),
            ("code.function.return.value", "Seattle"),
        ]
        attributes_match = GenAiTraceVerifier().check_decorator_span_attributes(span, expected_attributes)
        assert attributes_match is True

    @pytest.mark.asyncio
    async def test_async_function_with_nested_collections(self, setup_telemetry):
        """Test decorator with async function and nested collections."""

        @trace_function()
        async def process_nested_async(data: list) -> int:
            total = 0
            for sublist in data:
                total += sum(sublist)
            return total

        nested_data = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        result = await process_nested_async(nested_data)
        assert result == 45

        spans = self.exporter.get_spans_by_name("process_nested_async")
        assert len(spans) == 1
        span = spans[0]

        expected_data_str = str(nested_data)
        expected_attributes = [
            ("code.function.parameter.data", expected_data_str),
            ("code.function.return.value", 45),
        ]
        attributes_match = GenAiTraceVerifier().check_decorator_span_attributes(span, expected_attributes)
        assert attributes_match is True

    @pytest.mark.asyncio
    async def test_async_function_with_custom_span_name(self, setup_telemetry):
        """Test decorator with custom span name on async function."""

        @trace_function(span_name="async_custom_operation")
        async def calculate_async(x: int, y: int) -> int:
            return x * y

        result = await calculate_async(6, 9)
        assert result == 54

        spans = self.exporter.get_spans_by_name("async_custom_operation")
        assert len(spans) == 1
        span = spans[0]

        expected_attributes = [
            ("code.function.parameter.x", 6),
            ("code.function.parameter.y", 9),
            ("code.function.return.value", 54),
        ]
        attributes_match = GenAiTraceVerifier().check_decorator_span_attributes(span, expected_attributes)
        assert attributes_match is True

    @pytest.mark.asyncio
    async def test_async_function_with_no_return_value(self, setup_telemetry):
        """Test decorator with async function that returns None."""

        @trace_function()
        async def log_message_async(message: str) -> None:
            pass  # Just a placeholder

        result = await log_message_async("Async test message")
        assert result is None

        spans = self.exporter.get_spans_by_name("log_message_async")
        assert len(spans) == 1
        span = spans[0]

        expected_attributes = [
            ("code.function.parameter.message", "Async test message"),
        ]
        attributes_match = GenAiTraceVerifier().check_decorator_span_attributes(span, expected_attributes)
        assert attributes_match is True

    @pytest.mark.asyncio
    async def test_async_function_with_boolean_parameters(self, setup_telemetry):
        """Test decorator with async function and boolean parameters."""

        @trace_function()
        async def check_status_async(is_active: bool, is_verified: bool) -> str:
            if is_active and is_verified:
                return "approved"
            elif is_active:
                return "pending"
            return "inactive"

        result = await check_status_async(True, True)
        assert result == "approved"

        spans = self.exporter.get_spans_by_name("check_status_async")
        assert len(spans) == 1
        span = spans[0]

        expected_attributes = [
            ("code.function.parameter.is_active", True),
            ("code.function.parameter.is_verified", True),
            ("code.function.return.value", "approved"),
        ]
        attributes_match = GenAiTraceVerifier().check_decorator_span_attributes(span, expected_attributes)
        assert attributes_match is True

    @pytest.mark.asyncio
    async def test_async_function_with_float_parameters(self, setup_telemetry):
        """Test decorator with async function and float parameters."""

        @trace_function()
        async def calculate_area_async(width: float, height: float) -> float:
            return width * height

        result = await calculate_area_async(12.5, 8.3)
        assert abs(result - 103.75) < 0.01

        spans = self.exporter.get_spans_by_name("calculate_area_async")
        assert len(spans) == 1
        span = spans[0]

        expected_attributes = [
            ("code.function.parameter.width", 12.5),
            ("code.function.parameter.height", 8.3),
            ("code.function.return.value", result),
        ]
        attributes_match = GenAiTraceVerifier().check_decorator_span_attributes(span, expected_attributes)
        assert attributes_match is True

    @pytest.mark.asyncio
    async def test_async_function_with_tuple_parameter(self, setup_telemetry):
        """Test decorator with async function and tuple parameters."""

        @trace_function()
        async def get_coordinates_async(point: tuple) -> str:
            return f"Position: ({point[0]}, {point[1]}, {point[2]})"

        result = await get_coordinates_async((10, 20, 30))
        assert result == "Position: (10, 20, 30)"

        spans = self.exporter.get_spans_by_name("get_coordinates_async")
        assert len(spans) == 1
        span = spans[0]

        expected_attributes = [
            ("code.function.parameter.point", (10, 20, 30)),
            ("code.function.return.value", "Position: (10, 20, 30)"),
        ]
        attributes_match = GenAiTraceVerifier().check_decorator_span_attributes(span, expected_attributes)
        assert attributes_match is True

    @pytest.mark.asyncio
    async def test_async_function_with_set_parameter(self, setup_telemetry):
        """Test decorator with async function and set parameters."""

        @trace_function()
        async def count_unique_async(items: set) -> int:
            return len(items)

        result = await count_unique_async({10, 20, 30, 40, 50})
        assert result == 5

        spans = self.exporter.get_spans_by_name("count_unique_async")
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
        assert items_value == {10, 20, 30, 40, 50}
        assert span.attributes["code.function.return.value"] == 5

    @pytest.mark.asyncio
    async def test_async_function_with_exception(self, setup_telemetry):
        """Test decorator records exception information in async functions."""

        @trace_function()
        async def divide_async(a: int, b: int) -> float:
            return a / b

        with pytest.raises(ZeroDivisionError):
            await divide_async(100, 0)

        spans = self.exporter.get_spans_by_name("divide_async")
        assert len(spans) == 1
        span = spans[0]

        expected_attributes = [
            ("code.function.parameter.a", 100),
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

    @pytest.mark.asyncio
    async def test_async_function_with_mixed_parameters(self, setup_telemetry):
        """Test decorator with async function and mixed parameter types."""

        @trace_function()
        async def process_data_async(name: str, count: int, active: bool, scores: list) -> dict:
            return {
                "name": name.upper(),
                "count": count * 2,
                "active": active,
                "total": sum(scores),
            }

        result = await process_data_async("async_test", 3, False, [100, 200, 300])
        assert result["name"] == "ASYNC_TEST"
        assert result["count"] == 6
        assert result["total"] == 600

        spans = self.exporter.get_spans_by_name("process_data_async")
        assert len(spans) == 1
        span = spans[0]

        expected_result_str = str(result)
        expected_attributes = [
            ("code.function.parameter.name", "async_test"),
            ("code.function.parameter.count", 3),
            ("code.function.parameter.active", False),
            ("code.function.parameter.scores", [100, 200, 300]),
            ("code.function.return.value", expected_result_str),
        ]
        attributes_match = GenAiTraceVerifier().check_decorator_span_attributes(span, expected_attributes)
        assert attributes_match is True

    @pytest.mark.asyncio
    async def test_async_function_with_default_parameters(self, setup_telemetry):
        """Test decorator with async function using default parameters."""

        @trace_function()
        async def create_user_async(name: str, role: str = "user", active: bool = True) -> dict:
            return {"name": name, "role": role, "active": active}

        result = await create_user_async("Charlie")
        assert result["name"] == "Charlie"
        assert result["role"] == "user"
        assert result["active"] is True

        spans = self.exporter.get_spans_by_name("create_user_async")
        assert len(spans) == 1
        span = spans[0]

        expected_result_str = str(result)
        expected_attributes = [
            ("code.function.parameter.name", "Charlie"),
            ("code.function.parameter.role", "user"),
            ("code.function.parameter.active", True),
            ("code.function.return.value", expected_result_str),
        ]
        attributes_match = GenAiTraceVerifier().check_decorator_span_attributes(span, expected_attributes)
        assert attributes_match is True

    @pytest.mark.asyncio
    async def test_async_function_list_return_value(self, setup_telemetry):
        """Test decorator with async function returning a list."""

        @trace_function()
        async def get_range_async(start: int, end: int) -> list:
            return list(range(start, end))

        result = await get_range_async(1, 6)
        assert result == [1, 2, 3, 4, 5]

        spans = self.exporter.get_spans_by_name("get_range_async")
        assert len(spans) == 1
        span = spans[0]

        expected_attributes = [
            ("code.function.parameter.start", 1),
            ("code.function.parameter.end", 6),
            ("code.function.return.value", [1, 2, 3, 4, 5]),
        ]
        attributes_match = GenAiTraceVerifier().check_decorator_span_attributes(span, expected_attributes)
        assert attributes_match is True
