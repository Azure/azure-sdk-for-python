# pylint: disable=too-many-lines
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json
import os
import azure.ai.inference as sdk
from azure.ai.inference.tracing import AIInferenceInstrumentor

from model_inference_test_base import (
    ModelClientTestBase,
    ServicePreparerChatCompletions,
)
from azure.core.settings import settings
from devtools_testutils import recorded_by_proxy
from memory_trace_exporter import MemoryTraceExporter
from gen_ai_trace_verifier import GenAiTraceVerifier
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

CONTENT_TRACING_ENV_VARIABLE = "AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED"
content_tracing_initial_value = os.getenv(CONTENT_TRACING_ENV_VARIABLE)


# The test class name needs to start with "Test" to get collected by pytest
class TestClientTracing(ModelClientTestBase):

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
        tracer = trace.get_tracer(__name__)
        memoryExporter = MemoryTraceExporter()
        span_processor = SimpleSpanProcessor(memoryExporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        return span_processor, memoryExporter

    def modify_env_var(self, name, new_value):
        current_value = os.getenv(name)
        os.environ[name] = new_value
        return current_value

    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_instrumentation(self, **kwargs):
        # Make sure code is not instrumented due to a previous test exception
        try:
            AIInferenceInstrumentor().uninstrument()
        except RuntimeError as e:
            pass
        client = self._create_chat_client(**kwargs)
        exception_caught = False
        try:
            assert AIInferenceInstrumentor().is_instrumented() == False
            AIInferenceInstrumentor().instrument()
            assert AIInferenceInstrumentor().is_instrumented() == True
            AIInferenceInstrumentor().uninstrument()
            assert AIInferenceInstrumentor().is_instrumented() == False
        except RuntimeError as e:
            exception_caught = True
            print(e)
        client.close()
        assert exception_caught == False

    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_instrumenting_twice_does_not_cause_exception(self, **kwargs):
        # Make sure code is not instrumented due to a previous test exception
        try:
            AIInferenceInstrumentor().uninstrument()
        except RuntimeError as e:
            pass
        client = self._create_chat_client(**kwargs)
        exception_caught = False
        try:
            AIInferenceInstrumentor().instrument()
            AIInferenceInstrumentor().instrument()
        except RuntimeError as e:
            exception_caught = True
            print(e)
        AIInferenceInstrumentor().uninstrument()
        client.close()
        assert exception_caught == False

    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_uninstrumenting_uninstrumented_does_not_cause_exception(self, **kwargs):
        # Make sure code is not instrumented due to a previous test exception
        try:
            AIInferenceInstrumentor().uninstrument()
        except RuntimeError as e:
            pass
        client = self._create_chat_client(**kwargs)
        exception_caught = False
        try:
            AIInferenceInstrumentor().uninstrument()
        except RuntimeError as e:
            exception_caught = True
            print(e)
        client.close()
        assert exception_caught == False

    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_uninstrumenting_twice_does_not_cause_exception(self, **kwargs):
        # Make sure code is not instrumented due to a previous test exception
        try:
            AIInferenceInstrumentor().uninstrument()
        except RuntimeError as e:
            pass
        client = self._create_chat_client(**kwargs)
        exception_caught = False
        uninstrumented_once = False
        try:
            AIInferenceInstrumentor().instrument()
            AIInferenceInstrumentor().uninstrument()
            AIInferenceInstrumentor().uninstrument()
        except RuntimeError as e:
            exception_caught = True
            print(e)
        client.close()
        assert exception_caught == False

    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_is_content_recording_enabled(self, **kwargs):
        # Make sure code is not instrumented due to a previous test exception
        try:
            AIInferenceInstrumentor().uninstrument()
        except RuntimeError as e:
            pass
        self.modify_env_var(CONTENT_TRACING_ENV_VARIABLE, "False")
        client = self._create_chat_client(**kwargs)
        exception_caught = False
        uninstrumented_once = False
        try:
            # From environment variable instrumenting from uninstrumented
            AIInferenceInstrumentor().instrument()
            self.modify_env_var(CONTENT_TRACING_ENV_VARIABLE, "False")
            AIInferenceInstrumentor().instrument()
            content_recording_enabled = AIInferenceInstrumentor().is_content_recording_enabled()
            assert content_recording_enabled == False
            AIInferenceInstrumentor().uninstrument()
            self.modify_env_var(CONTENT_TRACING_ENV_VARIABLE, "True")
            AIInferenceInstrumentor().instrument()
            content_recording_enabled = AIInferenceInstrumentor().is_content_recording_enabled()
            assert content_recording_enabled == True
            AIInferenceInstrumentor().uninstrument()
            self.modify_env_var(CONTENT_TRACING_ENV_VARIABLE, "invalid")
            AIInferenceInstrumentor().instrument()
            content_recording_enabled = AIInferenceInstrumentor().is_content_recording_enabled()
            assert content_recording_enabled == False

            # From environment variable instrumenting from instrumented
            self.modify_env_var(CONTENT_TRACING_ENV_VARIABLE, "True")
            AIInferenceInstrumentor().instrument()
            content_recording_enabled = AIInferenceInstrumentor().is_content_recording_enabled()
            assert content_recording_enabled == True
            self.modify_env_var(CONTENT_TRACING_ENV_VARIABLE, "True")
            AIInferenceInstrumentor().instrument()
            content_recording_enabled = AIInferenceInstrumentor().is_content_recording_enabled()
            assert content_recording_enabled == True
            self.modify_env_var(CONTENT_TRACING_ENV_VARIABLE, "invalid")
            AIInferenceInstrumentor().instrument()
            content_recording_enabled = AIInferenceInstrumentor().is_content_recording_enabled()
            assert content_recording_enabled == False

            # From parameter instrumenting from uninstrumented
            AIInferenceInstrumentor().uninstrument()
            self.modify_env_var(CONTENT_TRACING_ENV_VARIABLE, "True")
            AIInferenceInstrumentor().instrument(enable_content_recording=False)
            content_recording_enabled = AIInferenceInstrumentor().is_content_recording_enabled()
            assert content_recording_enabled == False
            AIInferenceInstrumentor().uninstrument()
            self.modify_env_var(CONTENT_TRACING_ENV_VARIABLE, "False")
            AIInferenceInstrumentor().instrument(enable_content_recording=True)
            content_recording_enabled = AIInferenceInstrumentor().is_content_recording_enabled()
            assert content_recording_enabled == True

            # From parameter instrumenting from instrumented
            self.modify_env_var(CONTENT_TRACING_ENV_VARIABLE, "True")
            AIInferenceInstrumentor().instrument(enable_content_recording=False)
            content_recording_enabled = AIInferenceInstrumentor().is_content_recording_enabled()
            assert content_recording_enabled == False
            self.modify_env_var(CONTENT_TRACING_ENV_VARIABLE, "False")
            AIInferenceInstrumentor().instrument(enable_content_recording=True)
            content_recording_enabled = AIInferenceInstrumentor().is_content_recording_enabled()
            assert content_recording_enabled == True
        except RuntimeError as e:
            exception_caught = True
            print(e)
        client.close()
        assert exception_caught == False

    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_chat_completion_tracing_content_recording_disabled(self, **kwargs):
        # Make sure code is not instrumented due to a previous test exception
        try:
            AIInferenceInstrumentor().uninstrument()
        except RuntimeError as e:
            pass
        self.modify_env_var(CONTENT_TRACING_ENV_VARIABLE, "False")
        client = self._create_chat_client(**kwargs)
        model = kwargs.pop("azure_ai_chat_model").lower()
        processor, exporter = self.setup_memory_trace_exporter()
        AIInferenceInstrumentor().instrument()
        response = client.complete(
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

    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_chat_completion_tracing_content_recording_enabled(self, **kwargs):
        # Make sure code is not instrumented due to a previous test exception
        try:
            AIInferenceInstrumentor().uninstrument()
        except RuntimeError as e:
            pass
        self.modify_env_var(CONTENT_TRACING_ENV_VARIABLE, "True")
        client = self._create_chat_client(**kwargs)
        model = kwargs.pop("azure_ai_chat_model").lower()
        processor, exporter = self.setup_memory_trace_exporter()
        AIInferenceInstrumentor().instrument()
        response = client.complete(
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
                "name": "gen_ai.system.message",
                "attributes": {
                    "gen_ai.system": "az.ai.inference",
                    "gen_ai.event.content": '{"role": "system", "content": "You are a helpful assistant."}',
                },
            },
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.system": "az.ai.inference",
                    "gen_ai.event.content": '{"role": "user", "content": "What is the capital of France?"}',
                },
            },
            {
                "name": "gen_ai.choice",
                "attributes": {
                    "gen_ai.system": "az.ai.inference",
                    "gen_ai.event.content": '{"message": {"content": "*"}, "finish_reason": "stop", "index": 0}',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True
        AIInferenceInstrumentor().uninstrument()

    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_chat_completion_tracing_content_unicode(self, **kwargs):
        # Make sure code is not instrumented due to a previous test exception
        try:
            AIInferenceInstrumentor().uninstrument()
        except RuntimeError as e:
            pass
        self.modify_env_var(CONTENT_TRACING_ENV_VARIABLE, "True")
        client = self._create_chat_client(**kwargs)
        processor, exporter = self.setup_memory_trace_exporter()
        AIInferenceInstrumentor().instrument()
        response = client.complete(
            messages=[
                sdk.models.SystemMessage(content="You are a helpful assistant."),
                sdk.models.UserMessage(content="将“hello world”翻译成中文和乌克兰语"),
            ],
        )
        processor.force_flush()
        spans = exporter.get_spans_by_name_starts_with("chat")
        assert len(spans) == 1
        expected_events = [
            {
                "name": "gen_ai.system.message",
                "attributes": {
                    "gen_ai.system": "az.ai.inference",
                    "gen_ai.event.content": '{"role": "system", "content": "You are a helpful assistant."}',
                },
            },
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.system": "az.ai.inference",
                    "gen_ai.event.content": '{"role": "user", "content": "将“hello world”翻译成中文和乌克兰语"}',
                },
            },
            {
                "name": "gen_ai.choice",
                "attributes": {
                    "gen_ai.system": "az.ai.inference",
                    "gen_ai.event.content": '{"message": {"content": "*"}, "finish_reason": "stop", "index": 0}',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(spans[0], expected_events)
        assert events_match == True

        completion_event_content = json.loads(spans[0].events[2].attributes["gen_ai.event.content"])
        assert False == completion_event_content["message"]["content"].isascii()
        assert response.choices[0].message.content == completion_event_content["message"]["content"]
        AIInferenceInstrumentor().uninstrument()

    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_chat_completion_streaming_tracing_content_recording_disabled(self, **kwargs):
        # Make sure code is not instrumented due to a previous test exception
        try:
            AIInferenceInstrumentor().uninstrument()
        except RuntimeError as e:
            pass
        self.modify_env_var(CONTENT_TRACING_ENV_VARIABLE, "False")
        client = self._create_chat_client(**kwargs)
        model = kwargs.pop("azure_ai_chat_model").lower()
        processor, exporter = self.setup_memory_trace_exporter()
        AIInferenceInstrumentor().instrument()
        response = client.complete(
            messages=[
                sdk.models.SystemMessage(content="You are a helpful assistant."),
                sdk.models.UserMessage(content="What is the capital of France?"),
            ],
            stream=True,
        )
        response_content = ""
        for update in response:
            if update.choices and update.choices[0].delta.content:
                response_content = response_content + update.choices[0].delta.content
        client.close()

        processor.force_flush()
        spans = exporter.get_spans_by_name_starts_with("chat")
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

    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_chat_completion_streaming_tracing_content_recording_enabled(self, **kwargs):
        # Make sure code is not instrumented due to a previous test exception
        try:
            AIInferenceInstrumentor().uninstrument()
        except RuntimeError as e:
            pass
        self.modify_env_var(CONTENT_TRACING_ENV_VARIABLE, "True")
        client = self._create_chat_client(**kwargs)
        model = kwargs.pop("azure_ai_chat_model").lower()
        processor, exporter = self.setup_memory_trace_exporter()
        AIInferenceInstrumentor().instrument()
        response = client.complete(
            messages=[
                sdk.models.SystemMessage(content="You are a helpful assistant."),
                sdk.models.UserMessage(content="What is the capital of France?"),
            ],
            stream=True,
        )
        response_content = ""
        for update in response:
            if update.choices and update.choices[0].delta.content:
                response_content = response_content + update.choices[0].delta.content
        client.close()

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
                "name": "gen_ai.system.message",
                "attributes": {
                    "gen_ai.system": "az.ai.inference",
                    "gen_ai.event.content": '{"role": "system", "content": "You are a helpful assistant."}',
                },
            },
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.system": "az.ai.inference",
                    "gen_ai.event.content": '{"role": "user", "content": "What is the capital of France?"}',
                },
            },
            {
                "name": "gen_ai.choice",
                "attributes": {
                    "gen_ai.system": "az.ai.inference",
                    "gen_ai.event.content": '{"message": {"content": "*"}, "finish_reason": "stop", "index": 0}',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True
        AIInferenceInstrumentor().uninstrument()

    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_chat_completion_with_function_call_tracing_content_recording_enabled(self, **kwargs):
        # Make sure code is not instrumented due to a previous test exception
        try:
            AIInferenceInstrumentor().uninstrument()
        except RuntimeError as e:
            pass
        import json
        from azure.ai.inference.models import (
            CompletionsFinishReason,
            ToolMessage,
            AssistantMessage,
            ChatCompletionsToolCall,
            ChatCompletionsToolDefinition,
            FunctionDefinition,
        )
        from azure.ai.inference import ChatCompletionsClient

        self.modify_env_var(CONTENT_TRACING_ENV_VARIABLE, "True")
        client = self._create_chat_client(**kwargs)
        model = kwargs.pop("azure_ai_chat_model").lower()
        processor, exporter = self.setup_memory_trace_exporter()
        AIInferenceInstrumentor().instrument()

        def get_weather(city: str) -> str:
            if city == "Seattle":
                return "Nice weather"
            elif city == "New York City":
                return "Good weather"
            else:
                return "Unavailable"

        weather_description = ChatCompletionsToolDefinition(
            function=FunctionDefinition(
                name="get_weather",
                description="Returns description of the weather in the specified city",
                parameters={
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "The name of the city for which weather info is requested",
                        },
                    },
                    "required": ["city"],
                },
            )
        )
        messages = [
            sdk.models.SystemMessage(content="You are a helpful assistant."),
            sdk.models.UserMessage(content="What is the weather in Seattle?"),
        ]

        response = client.complete(messages=messages, tools=[weather_description])

        if response.choices[0].finish_reason == CompletionsFinishReason.TOOL_CALLS:
            # Append the previous model response to the chat history
            messages.append(AssistantMessage(tool_calls=response.choices[0].message.tool_calls))
            # The tool should be of type function call.
            if response.choices[0].message.tool_calls is not None and len(response.choices[0].message.tool_calls) > 0:
                for tool_call in response.choices[0].message.tool_calls:
                    if type(tool_call) is ChatCompletionsToolCall:
                        function_args = json.loads(tool_call.function.arguments.replace("'", '"'))
                        print(f"Calling function `{tool_call.function.name}` with arguments {function_args}")
                        callable_func = locals()[tool_call.function.name]
                        function_response = callable_func(**function_args)
                        print(f"Function response = {function_response}")
                        # Provide the tool response to the model, by appending it to the chat history
                        messages.append(ToolMessage(tool_call_id=tool_call.id, content=function_response))
                # With the additional tools information on hand, get another response from the model
                response = client.complete(messages=messages, tools=[weather_description])
        processor.force_flush()
        spans = exporter.get_spans_by_name_starts_with("chat")
        assert len(spans) == 2
        expected_attributes = [
            ("gen_ai.operation.name", "chat"),
            ("gen_ai.system", "az.ai.inference"),
            ("gen_ai.request.model", "chat"),
            ("server.address", ""),
            ("gen_ai.response.id", ""),
            ("gen_ai.response.model", model),
            ("gen_ai.usage.input_tokens", "+"),
            ("gen_ai.usage.output_tokens", "+"),
            ("gen_ai.response.finish_reasons", ("tool_calls",)),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(spans[0], expected_attributes)
        assert attributes_match == True
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
        attributes_match = GenAiTraceVerifier().check_span_attributes(spans[1], expected_attributes)
        assert attributes_match == True

        expected_events = [
            {
                "name": "gen_ai.system.message",
                "timestamp": "*",
                "attributes": {
                    "gen_ai.system": "az.ai.inference",
                    "gen_ai.event.content": '{"role": "system", "content": "You are a helpful assistant."}',
                },
            },
            {
                "name": "gen_ai.user.message",
                "timestamp": "*",
                "attributes": {
                    "gen_ai.system": "az.ai.inference",
                    "gen_ai.event.content": '{"role": "user", "content": "What is the weather in Seattle?"}',
                },
            },
            {
                "name": "gen_ai.choice",
                "timestamp": "*",
                "attributes": {
                    "gen_ai.system": "az.ai.inference",
                    "gen_ai.event.content": '{"message": {"content": "", "tool_calls": [{"function": {"arguments": "{\\"city\\":\\"Seattle\\"}", "call_id": null, "name": "get_weather"}, "id": "*", "type": "function"}]}, "finish_reason": "tool_calls", "index": 0}',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(spans[0], expected_events)
        assert events_match == True

        expected_events = [
            {
                "name": "gen_ai.system.message",
                "timestamp": "*",
                "attributes": {
                    "gen_ai.system": "az.ai.inference",
                    "gen_ai.event.content": '{"role": "system", "content": "You are a helpful assistant."}',
                },
            },
            {
                "name": "gen_ai.user.message",
                "timestamp": "*",
                "attributes": {
                    "gen_ai.system": "az.ai.inference",
                    "gen_ai.event.content": '{"role": "user", "content": "What is the weather in Seattle?"}',
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "timestamp": "*",
                "attributes": {
                    "gen_ai.system": "az.ai.inference",
                    "gen_ai.event.content": '{"role": "assistant", "tool_calls": [{"function": {"arguments": "{\\"city\\": \\"Seattle\\"}", "call_id": null, "name": "get_weather"}, "id": "*", "type": "function"}]}',
                },
            },
            {
                "name": "gen_ai.tool.message",
                "timestamp": "*",
                "attributes": {
                    "gen_ai.system": "az.ai.inference",
                    "gen_ai.event.content": '{"role": "tool", "tool_call_id": "*", "content": "Nice weather"}',
                },
            },
            {
                "name": "gen_ai.choice",
                "timestamp": "*",
                "attributes": {
                    "gen_ai.system": "az.ai.inference",
                    "gen_ai.event.content": '{"message": {"content": "*"}, "finish_reason": "stop", "index": 0}',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(spans[1], expected_events)
        assert events_match == True

        AIInferenceInstrumentor().uninstrument()

    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_chat_completion_with_function_call_tracing_content_recording_disabled(self, **kwargs):
        # Make sure code is not instrumented due to a previous test exception
        try:
            AIInferenceInstrumentor().uninstrument()
        except RuntimeError as e:
            pass
        import json
        from azure.ai.inference.models import (
            CompletionsFinishReason,
            ToolMessage,
            AssistantMessage,
            ChatCompletionsToolCall,
            ChatCompletionsToolDefinition,
            FunctionDefinition,
        )
        from azure.ai.inference import ChatCompletionsClient

        self.modify_env_var(CONTENT_TRACING_ENV_VARIABLE, "False")
        client = self._create_chat_client(**kwargs)
        model = kwargs.pop("azure_ai_chat_model").lower()
        processor, exporter = self.setup_memory_trace_exporter()
        AIInferenceInstrumentor().instrument()

        def get_weather(city: str) -> str:
            if city == "Seattle":
                return "Nice weather"
            elif city == "New York City":
                return "Good weather"
            else:
                return "Unavailable"

        weather_description = ChatCompletionsToolDefinition(
            function=FunctionDefinition(
                name="get_weather",
                description="Returns description of the weather in the specified city",
                parameters={
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "The name of the city for which weather info is requested",
                        },
                    },
                    "required": ["city"],
                },
            )
        )
        messages = [
            sdk.models.SystemMessage(content="You are a helpful assistant."),
            sdk.models.UserMessage(content="What is the weather in Seattle?"),
        ]

        response = client.complete(messages=messages, tools=[weather_description])

        if response.choices[0].finish_reason == CompletionsFinishReason.TOOL_CALLS:
            # Append the previous model response to the chat history
            messages.append(AssistantMessage(tool_calls=response.choices[0].message.tool_calls))
            # The tool should be of type function call.
            if response.choices[0].message.tool_calls is not None and len(response.choices[0].message.tool_calls) > 0:
                for tool_call in response.choices[0].message.tool_calls:
                    if type(tool_call) is ChatCompletionsToolCall:
                        function_args = json.loads(tool_call.function.arguments.replace("'", '"'))
                        print(f"Calling function `{tool_call.function.name}` with arguments {function_args}")
                        callable_func = locals()[tool_call.function.name]
                        function_response = callable_func(**function_args)
                        print(f"Function response = {function_response}")
                        # Provide the tool response to the model, by appending it to the chat history
                        messages.append(ToolMessage(tool_call_id=tool_call.id, content=function_response))
                # With the additional tools information on hand, get another response from the model
                response = client.complete(messages=messages, tools=[weather_description])
        processor.force_flush()
        spans = exporter.get_spans_by_name_starts_with("chat ")
        if len(spans) == 0:
            spans = exporter.get_spans_by_name("chat")
        assert len(spans) == 2
        expected_attributes = [
            ("gen_ai.operation.name", "chat"),
            ("gen_ai.system", "az.ai.inference"),
            ("gen_ai.request.model", "chat"),
            ("server.address", ""),
            ("gen_ai.response.id", ""),
            ("gen_ai.response.model", model),
            ("gen_ai.usage.input_tokens", "+"),
            ("gen_ai.usage.output_tokens", "+"),
            ("gen_ai.response.finish_reasons", ("tool_calls",)),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(spans[0], expected_attributes)
        assert attributes_match == True
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
        attributes_match = GenAiTraceVerifier().check_span_attributes(spans[1], expected_attributes)
        assert attributes_match == True

        expected_events = [
            {
                "name": "gen_ai.choice",
                "timestamp": "*",
                "attributes": {
                    "gen_ai.system": "az.ai.inference",
                    "gen_ai.event.content": '{"finish_reason": "tool_calls", "index": 0, "message": {"tool_calls": [{"function": {"call_id": null}, "id": "*", "type": "function"}]}}',
                },
            }
        ]
        events_match = GenAiTraceVerifier().check_span_events(spans[0], expected_events)
        assert events_match == True

        expected_events = [
            {
                "name": "gen_ai.choice",
                "timestamp": "*",
                "attributes": {
                    "gen_ai.system": "az.ai.inference",
                    "gen_ai.event.content": '{"finish_reason": "stop", "index": 0}',
                },
            }
        ]
        events_match = GenAiTraceVerifier().check_span_events(spans[1], expected_events)
        assert events_match == True

        AIInferenceInstrumentor().uninstrument()

    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_chat_completion_with_function_call_streaming_tracing_content_recording_enabled(self, **kwargs):
        # Make sure code is not instrumented due to a previous test exception
        try:
            AIInferenceInstrumentor().uninstrument()
        except RuntimeError as e:
            pass
        import json
        from azure.ai.inference.models import (
            FunctionCall,
            ToolMessage,
            AssistantMessage,
            ChatCompletionsToolCall,
            ChatCompletionsToolDefinition,
            FunctionDefinition,
        )
        from azure.ai.inference import ChatCompletionsClient

        self.modify_env_var(CONTENT_TRACING_ENV_VARIABLE, "True")
        client = self._create_chat_client(**kwargs)
        model = kwargs.pop("azure_ai_chat_model").lower()
        processor, exporter = self.setup_memory_trace_exporter()
        AIInferenceInstrumentor().instrument()

        def get_weather(city: str) -> str:
            if city == "Seattle":
                return "Nice weather"
            elif city == "New York City":
                return "Good weather"
            else:
                return "Unavailable"

        weather_description = ChatCompletionsToolDefinition(
            function=FunctionDefinition(
                name="get_weather",
                description="Returns description of the weather in the specified city",
                parameters={
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "The name of the city for which weather info is requested",
                        },
                    },
                    "required": ["city"],
                },
            )
        )
        messages = [
            sdk.models.SystemMessage(content="You are a helpful AI assistant."),
            sdk.models.UserMessage(content="What is the weather in Seattle?"),
        ]

        response = client.complete(messages=messages, tools=[weather_description], stream=True)

        # At this point we expect a function tool call in the model response
        tool_call_id: str = ""
        function_name: str = ""
        function_args: str = ""
        for update in response:
            if update.choices[0].delta.tool_calls is not None:
                if update.choices[0].delta.tool_calls[0].function.name is not None:
                    function_name = update.choices[0].delta.tool_calls[0].function.name
                if update.choices[0].delta.tool_calls[0].id is not None:
                    tool_call_id = update.choices[0].delta.tool_calls[0].id
                function_args += update.choices[0].delta.tool_calls[0].function.arguments or ""

        # Append the previous model response to the chat history
        messages.append(
            AssistantMessage(
                tool_calls=[
                    ChatCompletionsToolCall(
                        id=tool_call_id, function=FunctionCall(name=function_name, arguments=function_args)
                    )
                ]
            )
        )

        # Make the function call
        callable_func = locals()[function_name]
        function_args_mapping = json.loads(function_args.replace("'", '"'))
        function_response = callable_func(**function_args_mapping)

        # Append the function response as a tool message to the chat history
        messages.append(ToolMessage(tool_call_id=tool_call_id, content=function_response))

        # With the additional tools information on hand, get another streaming response from the model
        response = client.complete(messages=messages, tools=[weather_description], stream=True)

        content = ""
        for update in response:
            content = content + update.choices[0].delta.content

        processor.force_flush()
        spans = exporter.get_spans_by_name_starts_with("chat ")
        if len(spans) == 0:
            spans = exporter.get_spans_by_name("chat")
        assert len(spans) == 2
        expected_attributes = [
            ("gen_ai.operation.name", "chat"),
            ("gen_ai.system", "az.ai.inference"),
            ("gen_ai.request.model", "chat"),
            ("server.address", ""),
            ("gen_ai.response.id", ""),
            ("gen_ai.response.model", model),
            ("gen_ai.usage.input_tokens", "+"),
            ("gen_ai.usage.output_tokens", "+"),
            ("gen_ai.response.finish_reasons", ("tool_calls",)),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(spans[0], expected_attributes)
        assert attributes_match == True
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
        attributes_match = GenAiTraceVerifier().check_span_attributes(spans[1], expected_attributes)
        assert attributes_match == True

        expected_events = [
            {
                "name": "gen_ai.system.message",
                "timestamp": "*",
                "attributes": {
                    "gen_ai.system": "az.ai.inference",
                    "gen_ai.event.content": '{"role": "system", "content": "You are a helpful AI assistant."}',
                },
            },
            {
                "name": "gen_ai.user.message",
                "timestamp": "*",
                "attributes": {
                    "gen_ai.system": "az.ai.inference",
                    "gen_ai.event.content": '{"role": "user", "content": "What is the weather in Seattle?"}',
                },
            },
            {
                "name": "gen_ai.choice",
                "timestamp": "*",
                "attributes": {
                    "gen_ai.system": "az.ai.inference",
                    "gen_ai.event.content": '{"finish_reason": "tool_calls", "message": {"tool_calls": [{"id": "*", "type": "function", "function": {"name": "get_weather", "arguments": "{\\"city\\": \\"Seattle\\"}"}}]}, "index": 0}',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(spans[0], expected_events)
        assert events_match == True

        expected_events = [
            {
                "name": "gen_ai.system.message",
                "timestamp": "*",
                "attributes": {
                    "gen_ai.system": "az.ai.inference",
                    "gen_ai.event.content": '{"role": "system", "content": "You are a helpful AI assistant."}',
                },
            },
            {
                "name": "gen_ai.user.message",
                "timestamp": "*",
                "attributes": {
                    "gen_ai.system": "az.ai.inference",
                    "gen_ai.event.content": '{"role": "user", "content": "What is the weather in Seattle?"}',
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "timestamp": "*",
                "attributes": {
                    "gen_ai.system": "az.ai.inference",
                    "gen_ai.event.content": '{"role": "assistant", "tool_calls": [{"id": "*", "function": {"name": "get_weather", "arguments": "{\\"city\\": \\"Seattle\\"}"}, "type": "function"}]}',
                },
            },
            {
                "name": "gen_ai.tool.message",
                "timestamp": "*",
                "attributes": {
                    "gen_ai.system": "az.ai.inference",
                    "gen_ai.event.content": '{"role": "tool", "tool_call_id": "*", "content": "Nice weather"}',
                },
            },
            {
                "name": "gen_ai.choice",
                "timestamp": "*",
                "attributes": {
                    "gen_ai.system": "az.ai.inference",
                    "gen_ai.event.content": '{"message": {"content": "*"}, "finish_reason": "stop", "index": 0}',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(spans[1], expected_events)
        assert events_match == True

        AIInferenceInstrumentor().uninstrument()

    @ServicePreparerChatCompletions()
    @recorded_by_proxy
    def test_chat_completion_with_function_call_streaming_tracing_content_recording_disabled(self, **kwargs):
        # Make sure code is not instrumented due to a previous test exception
        try:
            AIInferenceInstrumentor().uninstrument()
        except RuntimeError as e:
            pass
        import json
        from azure.ai.inference.models import (
            FunctionCall,
            ToolMessage,
            AssistantMessage,
            ChatCompletionsToolCall,
            ChatCompletionsToolDefinition,
            FunctionDefinition,
        )
        from azure.ai.inference import ChatCompletionsClient

        self.modify_env_var(CONTENT_TRACING_ENV_VARIABLE, "False")
        client = self._create_chat_client(**kwargs)
        model = kwargs.pop("azure_ai_chat_model").lower()
        processor, exporter = self.setup_memory_trace_exporter()
        AIInferenceInstrumentor().instrument()

        def get_weather(city: str) -> str:
            if city == "Seattle":
                return "Nice weather"
            elif city == "New York City":
                return "Good weather"
            else:
                return "Unavailable"

        weather_description = ChatCompletionsToolDefinition(
            function=FunctionDefinition(
                name="get_weather",
                description="Returns description of the weather in the specified city",
                parameters={
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "The name of the city for which weather info is requested",
                        },
                    },
                    "required": ["city"],
                },
            )
        )
        messages = [
            sdk.models.SystemMessage(content="You are a helpful assistant."),
            sdk.models.UserMessage(content="What is the weather in Seattle?"),
        ]

        response = client.complete(messages=messages, tools=[weather_description], stream=True)

        # At this point we expect a function tool call in the model response
        tool_call_id: str = ""
        function_name: str = ""
        function_args: str = ""
        for update in response:
            if update.choices[0].delta.tool_calls is not None:
                if update.choices[0].delta.tool_calls[0].function.name is not None:
                    function_name = update.choices[0].delta.tool_calls[0].function.name
                if update.choices[0].delta.tool_calls[0].id is not None:
                    tool_call_id = update.choices[0].delta.tool_calls[0].id
                function_args += update.choices[0].delta.tool_calls[0].function.arguments or ""

        # Append the previous model response to the chat history
        messages.append(
            AssistantMessage(
                tool_calls=[
                    ChatCompletionsToolCall(
                        id=tool_call_id, function=FunctionCall(name=function_name, arguments=function_args)
                    )
                ]
            )
        )

        # Make the function call
        callable_func = locals()[function_name]
        function_args_mapping = json.loads(function_args.replace("'", '"'))
        function_response = callable_func(**function_args_mapping)

        # Append the function response as a tool message to the chat history
        messages.append(ToolMessage(tool_call_id=tool_call_id, content=function_response))

        # With the additional tools information on hand, get another streaming response from the model
        response = client.complete(messages=messages, tools=[weather_description], stream=True)

        content = ""
        for update in response:
            content = content + update.choices[0].delta.content

        processor.force_flush()
        spans = exporter.get_spans_by_name_starts_with("chat ")
        if len(spans) == 0:
            spans = exporter.get_spans_by_name("chat")
        assert len(spans) == 2
        expected_attributes = [
            ("gen_ai.operation.name", "chat"),
            ("gen_ai.system", "az.ai.inference"),
            ("gen_ai.request.model", "chat"),
            ("server.address", ""),
            ("gen_ai.response.id", ""),
            ("gen_ai.response.model", model),
            ("gen_ai.usage.input_tokens", "+"),
            ("gen_ai.usage.output_tokens", "+"),
            ("gen_ai.response.finish_reasons", ("tool_calls",)),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(spans[0], expected_attributes)
        assert attributes_match == True
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
        attributes_match = GenAiTraceVerifier().check_span_attributes(spans[1], expected_attributes)
        assert attributes_match == True

        expected_events = [
            {
                "name": "gen_ai.choice",
                "timestamp": "*",
                "attributes": {
                    "gen_ai.system": "az.ai.inference",
                    "gen_ai.event.content": '{"finish_reason": "tool_calls", "message": {"tool_calls": [{"id": "*", "type": "function"}]}, "index": 0}',
                },
            }
        ]
        events_match = GenAiTraceVerifier().check_span_events(spans[0], expected_events)
        assert events_match == True

        expected_events = [
            {
                "name": "gen_ai.choice",
                "timestamp": "*",
                "attributes": {
                    "gen_ai.system": "az.ai.inference",
                    "gen_ai.event.content": '{"finish_reason": "stop", "index": 0}',
                },
            }
        ]
        events_match = GenAiTraceVerifier().check_span_events(spans[1], expected_events)
        assert events_match == True

        AIInferenceInstrumentor().uninstrument()
