# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable# cSpell:disable
import pytest
import os
import json
import jsonref
import time
from typing import Set, Callable, Any, Optional, List
from azure.ai.agents.models import (
    AgentsResponseFormatMode,
    AgentsResponseFormat,
    AgentEventHandler,
    FunctionTool,
    MessageDeltaChunk,
    MessageDeltaTextContent,
    OpenApiAnonymousAuthDetails,
    OpenApiTool,
    RunStatus,
    RunStep,
    ThreadMessage,
    ThreadRun,
    Tool,
    ToolSet,
)
from azure.ai.agents.telemetry._ai_agents_instrumentor import _AIAgentsInstrumentorPreview
from azure.ai.agents.telemetry import AIAgentsInstrumentor, _utils
from azure.core.settings import settings
from memory_trace_exporter import MemoryTraceExporter
from gen_ai_trace_verifier import GenAiTraceVerifier
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from azure.ai.agents import AgentsClient

from devtools_testutils import (
    recorded_by_proxy,
)

from test_agents_client_base import (
    TestAgentClientBase,
    agentClientPreparer,
)

CONTENT_TRACING_ENV_VARIABLE = "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"
settings.tracing_implementation = "OpenTelemetry"
_utils._span_impl_type = settings.tracing_implementation()


class TestAiAgentsInstrumentor(TestAgentClientBase):
    """Tests for AI agents instrumentor."""

    @pytest.fixture(scope="function")
    def instrument_with_content(self):
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "True"})
        self.setup_telemetry()
        yield
        self.cleanup()

    @pytest.fixture(scope="function")
    def instrument_without_content(self):
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "False"})
        self.setup_telemetry()
        yield
        self.cleanup()

    def setup_telemetry(self):
        trace._TRACER_PROVIDER = TracerProvider()
        self.exporter = MemoryTraceExporter()
        span_processor = SimpleSpanProcessor(self.exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        AIAgentsInstrumentor().instrument()

    def cleanup(self):
        self.exporter.shutdown()
        AIAgentsInstrumentor().uninstrument()
        trace._TRACER_PROVIDER = None
        os.environ.pop(CONTENT_TRACING_ENV_VARIABLE, None)

    # helper function: create client and using environment variables
    def create_client(self, **kwargs):
        # fetch environment variables
        endpoint = kwargs.pop("azure_ai_agents_tests_project_endpoint")
        credential = self.get_credential(AgentsClient, is_async=False)

        # create and return client
        client = AgentsClient(
            endpoint=endpoint,
            credential=credential,
        )

        return client

    def test_convert_api_response_format_exception(self):
        """Test that the exception is raised if agent_api_response_to_str is given wrong type."""
        with pytest.raises(ValueError) as cm:
            _AIAgentsInstrumentorPreview.agent_api_response_to_str(42)
        assert "Unknown response format <class 'int'>" in cm.value.args[0]

    @pytest.mark.parametrize(
        "fmt,expected",
        [
            (None, None),
            ("neep", "neep"),
            (AgentsResponseFormatMode.AUTO, "auto"),
            (AgentsResponseFormat(type="test"), "test"),
        ],
    )
    def test_convert_api_response_format(self, fmt, expected):
        """Test conversion of AgentsResponseFormatOption to string"""
        actual = _AIAgentsInstrumentorPreview.agent_api_response_to_str(fmt)
        assert actual == expected

    def test_instrumentation(self, **kwargs):
        # Make sure code is not instrumented due to a previous test exception
        AIAgentsInstrumentor().uninstrument()
        exception_caught = False
        try:
            assert AIAgentsInstrumentor().is_instrumented() == False
            AIAgentsInstrumentor().instrument()
            assert AIAgentsInstrumentor().is_instrumented() == True
            AIAgentsInstrumentor().uninstrument()
            assert AIAgentsInstrumentor().is_instrumented() == False
        except RuntimeError as e:
            exception_caught = True
            print(e)
        assert exception_caught == False

    def test_instrumenting_twice_does_not_cause_exception(self, **kwargs):
        # Make sure code is not instrumented due to a previous test exception
        AIAgentsInstrumentor().uninstrument()
        exception_caught = False
        try:
            AIAgentsInstrumentor().instrument()
            AIAgentsInstrumentor().instrument()
        except RuntimeError as e:
            exception_caught = True
            print(e)
        AIAgentsInstrumentor().uninstrument()
        assert exception_caught == False

    def test_uninstrumenting_uninstrumented_does_not_cause_exception(self, **kwargs):
        # Make sure code is not instrumented due to a previous test exception
        AIAgentsInstrumentor().uninstrument()
        exception_caught = False
        try:
            AIAgentsInstrumentor().uninstrument()
        except RuntimeError as e:
            exception_caught = True
            print(e)
        assert exception_caught == False

    def test_uninstrumenting_twice_does_not_cause_exception(self, **kwargs):
        # Make sure code is not instrumented due to a previous test exception
        AIAgentsInstrumentor().uninstrument()
        exception_caught = False
        try:
            AIAgentsInstrumentor().instrument()
            AIAgentsInstrumentor().uninstrument()
            AIAgentsInstrumentor().uninstrument()
        except RuntimeError as e:
            exception_caught = True
            print(e)
        assert exception_caught == False

    @pytest.mark.parametrize(
        "env1, env2, expected",
        [
            (None, None, False),
            (None, False, False),
            (None, True, True),
            (False, None, False),
            (False, False, False),
            (False, True, False),
            (True, None, True),
            (True, False, False),
            (True, True, True),
        ],
    )
    def test_content_recording_enabled_with_old_and_new_environment_variables(
        self, env1: Optional[bool], env2: Optional[bool], expected: bool
    ):
        """
        Test content recording enablement with both old and new environment variables.
        This test verifies the behavior of content recording when both the current
        and legacy environment variables are set to different combinations of values.
        The method tests all possible combinations of None, True, and False for both
        environment variables to ensure backward compatibility and proper precedence.
        Args:
            env1: Value for the current content tracing environment variable.
                  Can be None (unset), True, or False.
            env2: Value for the old/legacy content tracing environment variable.
                  Can be None (unset), True, or False.
            expected: The expected result of is_content_recording_enabled() given
                      the environment variable combination.
        The test ensures that only if one or both of the environment variables are
        defined and set to "true" content recording is enabled.
        """

        OLD_CONTENT_TRACING_ENV_VARIABLE = "AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED"  # Deprecated, undocumented.

        def set_env_var(var_name, value):
            if value is None:
                os.environ.pop(var_name, None)
            else:
                os.environ[var_name] = "true" if value else "false"

        set_env_var(CONTENT_TRACING_ENV_VARIABLE, env1)
        set_env_var(OLD_CONTENT_TRACING_ENV_VARIABLE, env2)

        self.setup_telemetry()
        try:
            assert AIAgentsInstrumentor().is_content_recording_enabled() == expected
        finally:
            self.cleanup()  # This also undefines CONTENT_TRACING_ENV_VARIABLE
            os.environ.pop(OLD_CONTENT_TRACING_ENV_VARIABLE, None)

    @pytest.mark.usefixtures("instrument_with_content")
    @agentClientPreparer()
    @recorded_by_proxy
    def test_agent_chat_with_tracing_content_recording_enabled(self, **kwargs):
        assert True == AIAgentsInstrumentor().is_content_recording_enabled()
        assert True == AIAgentsInstrumentor().is_instrumented()

        client = self.create_client(**kwargs)
        agent = client.create_agent(model="gpt-4o-mini", name="my-agent", instructions="You are helpful agent")
        thread = client.threads.create()
        client.messages.create(thread_id=thread.id, role="user", content="Hello, tell me a joke")
        run = client.runs.create(thread_id=thread.id, agent_id=agent.id)

        while run.status in ["queued", "in_progress", "requires_action"]:
            # wait for a second
            time.sleep(self._sleep_time())
            run = client.runs.get(thread_id=thread.id, run_id=run.id)
            print("Run status:", run.status)
        print("Run completed with status:", run.status)

        # delete agent and close client
        client.delete_agent(agent.id)
        print("Deleted agent")
        messages = list(client.messages.list(thread_id=thread.id))
        assert len(messages) > 1
        client.close()

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name("create_agent my-agent")
        assert len(spans) == 1
        span = spans[0]
        expected_attributes = [
            ("gen_ai.system", "az.ai.agents"),
            ("gen_ai.operation.name", "create_agent"),
            ("server.address", ""),
            ("gen_ai.request.model", "gpt-4o-mini"),
            ("gen_ai.agent.name", "my-agent"),
            ("gen_ai.agent.id", ""),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        expected_events = [
            {
                "name": "gen_ai.system.message",
                "attributes": {
                    "gen_ai.system": "az.ai.agents",
                    "gen_ai.event.content": '{"content": "You are helpful agent"}',
                },
            }
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

        spans = self.exporter.get_spans_by_name("create_thread")
        assert len(spans) == 1
        span = spans[0]
        expected_attributes = [
            ("gen_ai.system", "az.ai.agents"),
            ("gen_ai.operation.name", "create_thread"),
            ("server.address", ""),
            ("gen_ai.thread.id", ""),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        spans = self.exporter.get_spans_by_name("create_message")
        assert len(spans) == 1
        span = spans[0]
        expected_attributes = [
            ("gen_ai.system", "az.ai.agents"),
            ("gen_ai.operation.name", "create_message"),
            ("server.address", ""),
            ("gen_ai.thread.id", ""),
            ("gen_ai.message.id", ""),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        expected_events = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.system": "az.ai.agents",
                    "gen_ai.thread.id": "*",
                    "gen_ai.event.content": '{"content": "Hello, tell me a joke", "role": "user"}',
                },
            }
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

        spans = self.exporter.get_spans_by_name("start_thread_run")
        assert len(spans) == 1
        span = spans[0]
        expected_attributes = [
            ("gen_ai.system", "az.ai.agents"),
            ("gen_ai.operation.name", "start_thread_run"),
            ("server.address", ""),
            ("gen_ai.thread.id", ""),
            ("gen_ai.thread.run.id", ""),
            ("gen_ai.agent.id", ""),
            ("gen_ai.thread.run.id", ""),
            ("gen_ai.thread.run.status", "queued"),
            ("gen_ai.response.model", "gpt-4o-mini"),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        spans = self.exporter.get_spans_by_name("get_thread_run")
        assert len(spans) >= 1
        span = spans[-1]
        expected_attributes = [
            ("gen_ai.system", "az.ai.agents"),
            ("gen_ai.operation.name", "get_thread_run"),
            ("server.address", ""),
            ("gen_ai.thread.id", ""),
            ("gen_ai.thread.run.id", ""),
            ("gen_ai.agent.id", ""),
            ("gen_ai.thread.run.status", "completed"),
            ("gen_ai.response.model", "gpt-4o-mini"),
            ("gen_ai.usage.input_tokens", "+"),
            ("gen_ai.usage.output_tokens", "+"),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        spans = self.exporter.get_spans_by_name("list_messages")
        assert len(spans) == 2
        span = spans[0]
        expected_attributes = [
            ("gen_ai.system", "az.ai.agents"),
            ("gen_ai.operation.name", "list_messages"),
            ("server.address", ""),
            ("gen_ai.thread.id", ""),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True
        expected_events = [
            {
                "name": "gen_ai.assistant.message",
                "timestamp": "*",
                "attributes": {
                    "gen_ai.system": "az.ai.agents",
                    "gen_ai.thread.id": "*",
                    "gen_ai.agent.id": "*",
                    "gen_ai.thread.run.id": "*",
                    "gen_ai.message.id": "*",
                    # "gen_ai.message.status": "completed", - there is not status over-the wire
                    "gen_ai.event.content": '{"content": {"text": {"value": "*"}}, "role": "assistant"}',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

        span = spans[1]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True
        expected_events = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.system": "az.ai.agents",
                    "gen_ai.thread.id": "*",
                    "gen_ai.message.id": "*",
                    "gen_ai.event.content": '{"content": {"text": {"value": "Hello, tell me a joke"}}, "role": "user"}',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_without_content")
    @agentClientPreparer()
    @recorded_by_proxy
    def test_agent_chat_with_tracing_content_recording_disabled(self, **kwargs):
        assert False == AIAgentsInstrumentor().is_content_recording_enabled()

        client = self.create_client(**kwargs)
        agent = client.create_agent(model="gpt-4o-mini", name="my-agent", instructions="You are helpful agent")
        thread = client.threads.create()
        client.messages.create(thread_id=thread.id, role="user", content="Hello, tell me a joke")
        run = client.runs.create(thread_id=thread.id, agent_id=agent.id)

        while run.status in ["queued", "in_progress", "requires_action"]:
            # wait for a second
            time.sleep(self._sleep_time())
            run = client.runs.get(thread_id=thread.id, run_id=run.id)
            print("Run status:", run.status)
        print("Run completed with status:", run.status)

        # delete agent and close client
        client.delete_agent(agent.id)
        print("Deleted agent")
        messages = list(client.messages.list(thread_id=thread.id))
        assert len(messages) > 1
        client.close()

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name("create_agent my-agent")
        assert len(spans) == 1
        span = spans[0]
        expected_attributes = [
            ("gen_ai.system", "az.ai.agents"),
            ("gen_ai.operation.name", "create_agent"),
            ("server.address", ""),
            ("gen_ai.request.model", "gpt-4o-mini"),
            ("gen_ai.agent.name", "my-agent"),
            ("gen_ai.agent.id", ""),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        expected_events = [
            {
                "name": "gen_ai.system.message",
                "attributes": {
                    "gen_ai.system": "az.ai.agents",
                    "gen_ai.event.content": "{}",
                },
            }
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

        spans = self.exporter.get_spans_by_name("create_thread")
        assert len(spans) == 1
        span = spans[0]
        expected_attributes = [
            ("gen_ai.system", "az.ai.agents"),
            ("gen_ai.operation.name", "create_thread"),
            ("server.address", ""),
            ("gen_ai.thread.id", ""),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        spans = self.exporter.get_spans_by_name("create_message")
        assert len(spans) == 1
        span = spans[0]
        expected_attributes = [
            ("gen_ai.system", "az.ai.agents"),
            ("gen_ai.operation.name", "create_message"),
            ("server.address", ""),
            ("gen_ai.thread.id", ""),
            ("gen_ai.message.id", ""),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        expected_events = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.system": "az.ai.agents",
                    "gen_ai.thread.id": "*",
                    "gen_ai.event.content": '{"role": "user"}',
                },
            }
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

        spans = self.exporter.get_spans_by_name("start_thread_run")
        assert len(spans) == 1
        span = spans[0]
        expected_attributes = [
            ("gen_ai.system", "az.ai.agents"),
            ("gen_ai.operation.name", "start_thread_run"),
            ("server.address", ""),
            ("gen_ai.thread.id", ""),
            ("gen_ai.thread.run.id", ""),
            ("gen_ai.agent.id", ""),
            ("gen_ai.thread.run.id", ""),
            ("gen_ai.thread.run.status", "queued"),
            ("gen_ai.response.model", "gpt-4o-mini"),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        spans = self.exporter.get_spans_by_name("list_messages")
        assert len(spans) == 2
        span = spans[0]
        expected_attributes = [
            ("gen_ai.system", "az.ai.agents"),
            ("gen_ai.operation.name", "list_messages"),
            ("server.address", ""),
            ("gen_ai.thread.id", ""),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True
        expected_events = [
            {
                "name": "gen_ai.assistant.message",
                "timestamp": "*",
                "attributes": {
                    "gen_ai.system": "az.ai.agents",
                    "gen_ai.thread.id": "*",
                    "gen_ai.agent.id": "*",
                    "gen_ai.thread.run.id": "*",
                    "gen_ai.message.id": "*",
                    "gen_ai.event.content": '{"role": "assistant"}',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

        span = spans[1]
        expected_events = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.system": "az.ai.agents",
                    "gen_ai.thread.id": "*",
                    "gen_ai.message.id": "*",
                    "gen_ai.event.content": '{"role": "user"}',
                },
            },
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_with_content")
    @agentClientPreparer()
    @recorded_by_proxy
    def test_agent_streaming_with_toolset_with_tracing_content_recording_enabled(self, **kwargs):
        self._do_test_run_steps_with_toolset_with_tracing_content_recording(
            expected_event_content='{"tool_calls": [{"id": "*", "type": "function", "function": {"name": "fetch_weather", "arguments": {"location": "New York"}}}]}',
            toolset=self._get_function_toolset(),
            model="gpt-4o",
            use_stream=True,
            message="What is the weather in New York?",
            recording_enabled=True,
            tool_message_attribute_content='{\\"weather\\": \\"Sunny\\"}',
            event_contents=[
                '{"tool_calls": [{"id": "*", "type": "function", "function": {"name": "fetch_weather", "arguments": {"location": "New York"}}}]}',
                '{"content": {"text": {"value": "*"}}, "role": "assistant"}'
            ],
            have_submit_tools=True,
            **kwargs
        )

    @pytest.mark.usefixtures("instrument_with_content")
    @agentClientPreparer()
    @recorded_by_proxy
    def test_agent_streaming_with_toolset_with_tracing_content_recording_enabled_unicode(self, **kwargs):
        def fetch_weather(location: str) -> str:
            """
            Fetches the weather information for the specified location.

            :param location (str): The location to fetch weather for.
            :return: Weather information as a JSON string.
            :rtype: str
            """
            # In a real-world scenario, you'd integrate with a weather API.
            # Here, we'll mock the response.
            mock_weather_data = {"New York": "Sunny", "London": "Cloudy", "Sofia": "Ð”ÑŠÐ¶Ð´Ð¾Ð²Ð½Ð¾"}
            weather = mock_weather_data.get(location, f"Weather data not available for this location: {location}")
            weather_json = json.dumps({"weather": weather}, ensure_ascii=False)
            return weather_json

        user_functions: Set[Callable[..., Any]] = {
            fetch_weather,
        }

        functions = FunctionTool(user_functions)
        toolset = ToolSet()
        toolset.add(functions)

        client = self.create_client(**kwargs)
        agent = client.create_agent(
            model="gpt-4o",
            name="my-agent",
            instructions="You are helpful agent. Translate user message to English before executing tools.",
            toolset=toolset,
        )

        # workaround for https://github.com/Azure/azure-sdk-for-python/issues/40086
        client.enable_auto_function_calls(toolset)

        thread = client.threads.create()
        client.messages.create(thread_id=thread.id, role="user", content="Ð’Ñ€ÐµÐ¼ÐµÑ‚Ð¾ Ð² Ð¡Ð¾Ñ„Ð¸Ñ�?")

        with client.runs.stream(thread_id=thread.id, agent_id=agent.id, event_handler=MyEventHandler()) as stream:
            stream.until_done()

        # delete agent and close client
        client.delete_agent(agent.id)
        print("Deleted agent")
        messages = list(client.messages.list(thread_id=thread.id))
        assert len(messages) > 1
        client.close()

        self.exporter.force_flush()

        spans = self.exporter.get_spans_by_name("create_message")
        assert len(spans) == 1
        span = spans[0]

        expected_events = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.system": "az.ai.agents",
                    "gen_ai.thread.id": "*",
                    "gen_ai.event.content": '{"content": "Ð’Ñ€ÐµÐ¼ÐµÑ‚Ð¾ Ð² Ð¡Ð¾Ñ„Ð¸Ñ�?", "role": "user"}',
                },
            }
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

        spans = self.exporter.get_spans_by_name("process_thread_run")
        assert len(spans) == 1
        span = spans[0]
        expected_events = [
            {
                "name": "gen_ai.tool.message",
                "attributes": {
                    "gen_ai.event.content": '{"content": "{\\"weather\\": \\"Ð”ÑŠÐ¶Ð´Ð¾Ð²Ð½Ð¾\\"}", "id": "*"}'
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.system": "az.ai.agents",
                    "gen_ai.thread.id": "*",
                    "gen_ai.agent.id": "*",
                    "gen_ai.thread.run.id": "*",
                    "gen_ai.message.status": "completed",
                    "gen_ai.run_step.start.timestamp": "*",
                    "gen_ai.run_step.end.timestamp": "*",
                    "gen_ai.usage.input_tokens": "+",
                    "gen_ai.usage.output_tokens": "+",
                    "gen_ai.event.content": '{"tool_calls": [{"id": "*", "type": "function", "function": {"name": "fetch_weather", "arguments": {"location": "Sofia"}}}]}',
                },
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.system": "az.ai.agents",
                    "gen_ai.thread.id": "*",
                    "gen_ai.agent.id": "*",
                    "gen_ai.thread.run.id": "*",
                    "gen_ai.message.id": "*",
                    "gen_ai.message.status": "*",  # In some cases the message may be "in progress"
                    "gen_ai.usage.input_tokens": "+",
                    "gen_ai.usage.output_tokens": "+",
                    "gen_ai.event.content": '{"content": {"text": {"value": "*"}}, "role": "assistant"}',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

    @pytest.mark.usefixtures("instrument_without_content")
    @agentClientPreparer()
    @recorded_by_proxy
    def test_agent_streaming_with_toolset_with_tracing_content_recording_disabled(self, **kwargs):
        self._do_test_run_steps_with_toolset_with_tracing_content_recording(
            expected_event_content='{"tool_calls": [{"id": "*", "type": "function"}]}',
            toolset=self._get_function_toolset(),
            model="gpt-4o",
            use_stream=True,
            message="What is the weather in New York?",
            recording_enabled=False,
            tool_message_attribute_content='{\\"weather\\": \\"Sunny\\"}',
            event_contents=[
                '{"tool_calls": [{"id": "*", "type": "function"}]}',
                '{"role": "assistant"}'
            ],
            have_submit_tools=True,
            **kwargs
        )

    def _get_function_toolset(self):
        """Get a function toolset."""
        def fetch_weather(location: str) -> str:
            """
            Fetches the weather information for the specified location.

            :param location (str): The location to fetch weather for.
            :return: Weather information as a JSON string.
            :rtype: str
            """
            # In a real-world scenario, you'd integrate with a weather API.
            # Here, we'll mock the response.
            mock_weather_data = {"New York": "Sunny", "London": "Cloudy", "Tokyo": "Rainy"}
            weather = mock_weather_data.get(location, "Weather data not available for this location.")
            weather_json = json.dumps({"weather": weather})
            return weather_json

        user_functions: Set[Callable[..., Any]] = {
            fetch_weather,
        }

        functions = FunctionTool(user_functions)
        toolset = ToolSet()
        toolset.add(functions)
        return toolset

    @pytest.mark.usefixtures("instrument_with_content")
    @agentClientPreparer()
    @recorded_by_proxy
    def test_agent_streaming_run_steps_with_toolset_with_tracing_content_recording_enabled(self, **kwargs):
        """Test running functions with streaming and tracing content recording."""
        self._do_test_run_steps_with_toolset_with_tracing_content_recording(
            expected_event_content='{"tool_calls": [{"id": "*", "type": "function", "function": {"name": "fetch_weather", "arguments": {"location": "New York"}}}]}',
            toolset=self._get_function_toolset(),
            model="gpt-4o",
            use_stream=True,
            message="What is the weather in New York?",
            recording_enabled=True,
            tool_message_attribute_content='{\\"weather\\": \\"Sunny\\"}',
            event_contents=[
                '{"tool_calls": [{"id": "*", "type": "function", "function": {"name": "fetch_weather", "arguments": {"location": "New York"}}}]}',
                '{"content": {"text": {"value": "*"}}, "role": "assistant"}'
            ],
            have_submit_tools=True,
            **kwargs
        )

    def _do_test_run_steps_with_toolset_with_tracing_content_recording(
            self,
            expected_event_content: str,
            model: str,
            use_stream: bool,
            message: str,
            recording_enabled: bool,
            tool_message_attribute_content: str,
            event_contents: List[str],
            instructions: str = "You are helpful agent",
            test_run_steps=True,
            toolset: Optional[ToolSet] = None,
            tool: Optional[Tool] = None,
            have_submit_tools: bool = False,
            **kwargs
        ) -> None:
        """The helper method to check the recordings."""
        client = self.create_client(**kwargs)
        if toolset is None == tool is None:
            raise ValueError("Please provide at lease one of toolset or tool, but not both.")
        elif toolset is not None:
            agent = client.create_agent(
                model=model, name="my-agent", instructions=instructions, toolset=toolset
            )
    
            # workaround for https://github.com/Azure/azure-sdk-for-python/issues/40086
            client.enable_auto_function_calls(toolset)
        elif tool is not None:
            agent = client.create_agent(
                model=model, name="my-agent", instructions=instructions,
                tools=tool.definitions,
                tool_resources=tool.resources,
            )
            

        thread = client.threads.create()
        client.messages.create(thread_id=thread.id, role="user", content=message)

        if use_stream:
            event_handler = MyEventHandler()
            with client.runs.stream(thread_id=thread.id, agent_id=agent.id, event_handler=event_handler) as stream:
                stream.until_done()
            run_id = event_handler.run_id
        else:
            run = client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id, polling_interval=self._sleep_time())
            assert run.status != RunStatus.FAILED, run.last_error
            run_id = run.id
            

        # delete agent and close client
        client.delete_agent(agent.id)
        print("Deleted agent")
        messages = list(client.messages.list(thread_id=thread.id))
        assert len(messages) > 1
        if test_run_steps:
            steps = list(client.run_steps.list(thread_id=thread.id, run_id=run_id))
            assert len(steps) >= 1
        client.close()
        
        self.exporter.force_flush()
        
        spans = self.exporter.get_spans_by_name("create_agent my-agent")
        assert len(spans) == 1
        span = spans[0]
        expected_attributes = [
            ("gen_ai.system", "az.ai.agents"),
            ("gen_ai.operation.name", "create_agent"),
            ("server.address", ""),
            ("gen_ai.request.model", model),
            ("gen_ai.agent.name", "my-agent"),
            ("gen_ai.agent.id", ""),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True
        
        content = f'{{"content": "{instructions}"}}' if recording_enabled else "{}"
        expected_events = [
            {
                "name": "gen_ai.system.message",
                "attributes": {
                    "gen_ai.system": "az.ai.agents",
                    "gen_ai.event.content": content,
                },
            }
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True
        
        spans = self.exporter.get_spans_by_name("create_thread")
        assert len(spans) == 1
        span = spans[0]
        expected_attributes = [
            ("gen_ai.system", "az.ai.agents"),
            ("gen_ai.operation.name", "create_thread"),
            ("server.address", ""),
            ("gen_ai.thread.id", ""),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        spans = self.exporter.get_spans_by_name("create_message")
        assert len(spans) == 1
        span = spans[0]
        expected_attributes = [
            ("gen_ai.system", "az.ai.agents"),
            ("gen_ai.operation.name", "create_message"),
            ("server.address", ""),
            ("gen_ai.thread.id", ""),
            ("gen_ai.message.id", ""),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        content = f'{{"content": "{message}", "role": "user"}}' if recording_enabled else '{"role": "user"}'
        expected_events = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.system": "az.ai.agents",
                    "gen_ai.thread.id": "*",
                    "gen_ai.event.content": content,
                },
            }
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

        spans = self.exporter.get_spans_by_name("submit_tool_outputs")
        if have_submit_tools:
            assert len(spans) == 1
            span = spans[0]
            expected_attributes = [
                ("gen_ai.system", "az.ai.agents"),
                ("gen_ai.operation.name", "submit_tool_outputs"),
                ("server.address", ""),
                ("gen_ai.thread.id", ""),
                ("gen_ai.thread.run.id", ""),
            ]
            if not use_stream:
                expected_attributes.extend([
                    ('gen_ai.thread.run.status', ''),
                    ('gen_ai.response.model', model)
                ])
                
            attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
            assert attributes_match == True
        else:
            assert len(spans) == 0

        if use_stream:
            spans = self.exporter.get_spans_by_name("process_thread_run")
            assert len(spans) == 1
            span = spans[0]
            expected_attributes = [
                ("gen_ai.system", "az.ai.agents"),
                ("gen_ai.operation.name", "process_thread_run"),
                ("server.address", ""),
                ("gen_ai.thread.id", ""),
                ("gen_ai.agent.id", ""),
                ("gen_ai.thread.run.id", ""),
                ("gen_ai.message.id", ""),
                ("gen_ai.thread.run.status", "completed"),
                ("gen_ai.response.model", model),
                ("gen_ai.usage.input_tokens", "+"),
                ("gen_ai.usage.output_tokens", "+"),
            ]
            attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
            assert attributes_match == True
    
            tool_attr = tool_message_attribute_content if recording_enabled else ""
            expected_events = [
                {
                    "name": "gen_ai.tool.message",
                    "attributes": {"gen_ai.event.content": f'{{"content": "{tool_attr}", "id": "*"}}'},
                },
                {
                    "name": "gen_ai.assistant.message",
                    "attributes": {
                        "gen_ai.system": "az.ai.agents",
                        "gen_ai.thread.id": "*",
                        "gen_ai.agent.id": "*",
                        "gen_ai.thread.run.id": "*",
                        "gen_ai.message.status": "completed",
                        "gen_ai.run_step.start.timestamp": "*",
                        "gen_ai.run_step.end.timestamp": "*",
                        "gen_ai.usage.input_tokens": "+",
                        "gen_ai.usage.output_tokens": "+",
                        "gen_ai.event.content": event_contents[0],
                    },
                },
                {
                    "name": "gen_ai.assistant.message",
                    "attributes": {
                        "gen_ai.system": "az.ai.agents",
                        "gen_ai.thread.id": "*",
                        "gen_ai.agent.id": "*",
                        "gen_ai.thread.run.id": "*",
                        "gen_ai.message.id": "*",
                        "gen_ai.message.status": "*",  # In some cases the message may be "in progress"
                        "gen_ai.usage.input_tokens": "+",
                        "gen_ai.usage.output_tokens": "+",
                        "gen_ai.event.content": event_contents[1],
                    },
                },
            ]
            events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
            assert events_match == True
        
        spans = self.exporter.get_spans_by_name("list_messages")
        assert len(spans) == 2
        span = spans[0]
        expected_attributes = [
            ("gen_ai.system", "az.ai.agents"),
            ("gen_ai.operation.name", "list_messages"),
            ("server.address", ""),
            ("gen_ai.thread.id", ""),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True
        
        content = '{"content": {"text": {"value": "*"}}, "role": "assistant"}' if recording_enabled else '{"role": "assistant"}'
        expected_events = [
            {
                "name": "gen_ai.assistant.message",
                "timestamp": "*",
                "attributes": {
                    "gen_ai.system": "az.ai.agents",
                    "gen_ai.thread.id": "*",
                    "gen_ai.agent.id": "*",
                    "gen_ai.thread.run.id": "*",
                    "gen_ai.message.id": "*",
                    "gen_ai.event.content": content,
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

        span = spans[1]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True
        
        content = f'{{"content": {{"text": {{"value": "{message}"}}}}, "role": "user"}}'  if recording_enabled else '{"role": "user"}'
        expected_events = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.system": "az.ai.agents",
                    "gen_ai.thread.id": "*",
                    "gen_ai.message.id": "*",
                    "gen_ai.event.content": content
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True
        
        spans = self.exporter.get_spans_by_name("list_run_steps")
        if test_run_steps:
            assert len(spans) == 2
            span = spans[0]
            expected_attributes = [
                ("gen_ai.system", "az.ai.agents"),
                ("gen_ai.operation.name", "list_run_steps"),
                ("server.address", ""),
                ("gen_ai.thread.id", ""),
                ("gen_ai.thread.run.id", ""),
            ]
            attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
            assert attributes_match == True
            
            expected_events = [
                {
                    "name": "gen_ai.run_step.message_creation",
                    "attributes": {
                        "gen_ai.system": "az.ai.agents",
                        "gen_ai.thread.id": "*",
                        "gen_ai.agent.id": "*",
                        "gen_ai.thread.run.id": "*",
                        "gen_ai.message.id": "*",
                        "gen_ai.run_step.status": "completed",
                        "gen_ai.run_step.start.timestamp": "*",
                        "gen_ai.run_step.end.timestamp": "*",
                        "gen_ai.usage.input_tokens": "+",
                        "gen_ai.usage.output_tokens": "+",
                    },
                },
            ]
            events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
            assert events_match == True
    
            span = spans[1]
            attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
            assert attributes_match == True
            expected_events = [
                {
                    "name": "gen_ai.run_step.tool_calls",
                    "attributes": {
                        "gen_ai.system": "az.ai.agents",
                        "gen_ai.thread.id": "*",
                        "gen_ai.agent.id": "*",
                        "gen_ai.thread.run.id": "*",
                        "gen_ai.run_step.status": "completed",
                        "gen_ai.run_step.start.timestamp": "*",
                        "gen_ai.run_step.end.timestamp": "*",
                        "gen_ai.usage.input_tokens": "+",
                        "gen_ai.usage.output_tokens": "+",
                        "gen_ai.event.content": expected_event_content
                    },
                },
            ]
            events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
            assert events_match == True
        else:
            assert spans == []

    @pytest.mark.usefixtures("instrument_with_content")
    @agentClientPreparer()
    @recorded_by_proxy
    def test_telemetry_steps_with_fn_tool(self, **kwargs):
        """Test running functions with streaming and tracing content recording."""
        self._do_test_run_steps_with_toolset_with_tracing_content_recording(
            expected_event_content='{"tool_calls": [{"id": "*", "type": "function", "function": {"name": "fetch_weather", "arguments": {"location": "New York"}}}]}',
            toolset=self._get_function_toolset(),
            model="gpt-4o",
            use_stream=False,
            message="What is the weather in New York?",
            recording_enabled=True,
            tool_message_attribute_content='{\\"weather\\": \\"Sunny\\"}',
            event_contents=[
                '{"tool_calls": [{"id": "*", "type": "function", "function": {"name": "fetch_weather", "arguments": {"location": "New York"}}}]}',
                '{"content": {"text": {"value": "*"}}, "role": "assistant"}'
            ],
            have_submit_tools=True,
            **kwargs
        )

    @pytest.mark.usefixtures("instrument_with_content")
    @agentClientPreparer()
    @recorded_by_proxy
    def test_telemetry_steps_with_openapi_tool(self, **kwargs):
        """Test run steps with OpenAPI."""
        weather_asset_file_path = os.path.join(os.path.dirname(__file__), "assets", "weather_openapi.json")
        auth = OpenApiAnonymousAuthDetails()
        with open(weather_asset_file_path, "r") as f:
            openapi_weather = jsonref.load(f)
        openapi_tool = OpenApiTool(
            name="get_weather",
            spec=openapi_weather,
            description="Retrieve weather information for a location",
            auth=auth,
        )
        self._do_test_run_steps_with_toolset_with_tracing_content_recording(
            expected_event_content='{"tool_calls": [{"id": "*", "type": "openapi", "function": {"name": "get_weather_GetCurrentWeather", "arguments": "*", "output": "*"}}]}',
            tool=openapi_tool,
            model="gpt-4o",
            use_stream=False,
            message="What is the weather in New York, NY?",
            recording_enabled=True,
            tool_message_attribute_content='',
            event_contents=[],
            **kwargs)


class MyEventHandler(AgentEventHandler):

    def on_message_delta(self, delta: "MessageDeltaChunk") -> None:
        for content_part in delta.delta.content:
            if isinstance(content_part, MessageDeltaTextContent):
                text_value = content_part.text.value if content_part.text else "No text"
                print(f"Text delta received: {text_value}")

    def on_thread_message(self, message: "ThreadMessage") -> None:
        print(f"ThreadMessage created. ID: {message.id}, Status: {message.status}")

    def on_thread_run(self, run: "ThreadRun") -> None:
        print(f"ThreadRun status: {run.status}")
        self.run_id = run.id
        if run.status == "failed":
            print(f"Run failed. Error: {run.last_error}")

    def on_run_step(self, step: "RunStep") -> None:
        print(f"RunStep type: {step.type}, Status: {step.status}")

    def on_error(self, data: str) -> None:
        print(f"An error occurred. Data: {data}")

    def on_done(self) -> None:
        print("Stream completed.")

    def on_unhandled_event(self, event_type: str, event_data: Any) -> None:
        print(f"Unhandled Event Type: {event_type}, Data: {event_data}")
