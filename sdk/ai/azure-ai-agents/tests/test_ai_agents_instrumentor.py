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
from typing import Any, Callable, Dict, Optional, List, Set
from azure.ai.agents.models import (
    AgentsResponseFormatMode,
    AgentsResponseFormat,
    AgentEventHandler,
    FunctionTool,
    McpTool,
    MessageDeltaChunk,
    MessageDeltaTextContent,
    MessageInputTextBlock,
    OpenApiAnonymousAuthDetails,
    OpenApiTool,
    RequiredMcpToolCall,
    RunStatus,
    RunStep,
    RunStepActivityDetails,
    RunStepMcpToolCall,
    RunStepToolCallDetails,
    SubmitToolApprovalAction,
    ThreadMessage,
    ThreadMessageOptions,
    ThreadRun,
    Tool,
    ToolApproval,
    ToolSet,
)
from azure.ai.agents.telemetry._ai_agents_instrumentor import _AIAgentsInstrumentorPreview
from azure.ai.agents.telemetry import AIAgentsInstrumentor, _utils
from azure.core.settings import settings
from gen_ai_trace_verifier import GenAiTraceVerifier
from azure.ai.agents import AgentsClient

from devtools_testutils import (
    recorded_by_proxy,
)

from test_agents_client_base import agentClientPreparer
from test_ai_instrumentor_base import TestAiAgentsInstrumentorBase, MessageCreationMode, CONTENT_TRACING_ENV_VARIABLE

settings.tracing_implementation = "OpenTelemetry"
_utils._span_impl_type = settings.tracing_implementation()


class TestAiAgentsInstrumentor(TestAiAgentsInstrumentorBase):
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
        # Note: The proper way to invoke the same test over and over again with different parameter values is to use @pytest.mark.parametrize. However,
        # this does not work together with @recorded_by_proxy. So we call the helper function 4 times instead in a single recorded test.
        self._agent_chat_with_tracing_content_recording_enabled(
            message_creation_mode=MessageCreationMode.MESSAGE_CREATE_STR, **kwargs
        )
        self._agent_chat_with_tracing_content_recording_enabled(
            message_creation_mode=MessageCreationMode.MESSAGE_CREATE_INPUT_TEXT_BLOCK, **kwargs
        )
        self._agent_chat_with_tracing_content_recording_enabled(
            message_creation_mode=MessageCreationMode.THREAD_CREATE_STR, **kwargs
        )
        self._agent_chat_with_tracing_content_recording_enabled(
            message_creation_mode=MessageCreationMode.THREAD_CREATE_INPUT_TEXT_BLOCK, **kwargs
        )

    def _agent_chat_with_tracing_content_recording_enabled(self, message_creation_mode: MessageCreationMode, **kwargs):
        self.cleanup()
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "True"})
        self.setup_telemetry()
        assert True == AIAgentsInstrumentor().is_content_recording_enabled()
        assert True == AIAgentsInstrumentor().is_instrumented()

        client = self.create_client(**kwargs)
        agent = client.create_agent(model="gpt-4o-mini", name="my-agent", instructions="You are helpful agent")
        user_content = "Hello, tell me a joke"

        # Test 4 different patterns of thread & message creation
        if message_creation_mode == MessageCreationMode.MESSAGE_CREATE_STR:
            thread = client.threads.create()
            client.messages.create(thread_id=thread.id, role="user", content=user_content)
        elif message_creation_mode == MessageCreationMode.MESSAGE_CREATE_INPUT_TEXT_BLOCK:
            thread = client.threads.create()
            client.messages.create(thread_id=thread.id, role="user", content=[MessageInputTextBlock(text=user_content)])
        elif message_creation_mode == MessageCreationMode.THREAD_CREATE_STR:
            thread = client.threads.create(messages=[ThreadMessageOptions(role="user", content=user_content)])
        elif message_creation_mode == MessageCreationMode.THREAD_CREATE_INPUT_TEXT_BLOCK:
            thread = client.threads.create(
                messages=[ThreadMessageOptions(role="user", content=[MessageInputTextBlock(text=user_content)])]
            )
        else:
            assert False, f"Unknown message creation mode: {message_creation_mode}"

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

        # ------------------------- Validate "create_agent" span ---------------------------------
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

        # ------------------------- Validate "create_thread" span ---------------------------------
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

        if message_creation_mode in (
            MessageCreationMode.THREAD_CREATE_STR,
            MessageCreationMode.THREAD_CREATE_INPUT_TEXT_BLOCK,
        ):
            expected_events = [
                {
                    "name": "gen_ai.user.message",
                    "attributes": {
                        "gen_ai.system": "az.ai.agents",
                        "gen_ai.event.content": '{"content": "Hello, tell me a joke", "role": "user"}',
                    },
                }
            ]
            events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
            assert events_match == True

        # ------------------------- Validate "create_message" span ---------------------------------
        if message_creation_mode in (
            MessageCreationMode.MESSAGE_CREATE_STR,
            MessageCreationMode.MESSAGE_CREATE_INPUT_TEXT_BLOCK,
        ):
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

        # ------------------------- Validate "start_thread_run" span ---------------------------------
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

        # ------------------------- Validate "get_thread_run" span ---------------------------------
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

        # ------------------------- Validate "list_messages" span ---------------------------------
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
                '{"content": {"text": {"value": "*"}}, "role": "assistant"}',
            ],
            have_submit_tools=True,
            run_step_events=self.get_expected_fn_spans(True),
            **kwargs,
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
            toolset=self._get_function_toolset(),
            model="gpt-4o",
            use_stream=True,
            message="What is the weather in New York?",
            recording_enabled=False,
            tool_message_attribute_content='{\\"weather\\": \\"Sunny\\"}',
            event_contents=['{"tool_calls": [{"id": "*", "type": "function"}]}', '{"role": "assistant"}'],
            have_submit_tools=True,
            run_step_events=self.get_expected_fn_spans(False),
            **kwargs,
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
            toolset=self._get_function_toolset(),
            model="gpt-4o",
            use_stream=True,
            message="What is the weather in New York?",
            recording_enabled=True,
            tool_message_attribute_content='{\\"weather\\": \\"Sunny\\"}',
            event_contents=[
                '{"tool_calls": [{"id": "*", "type": "function", "function": {"name": "fetch_weather", "arguments": {"location": "New York"}}}]}',
                '{"content": {"text": {"value": "*"}}, "role": "assistant"}',
            ],
            have_submit_tools=True,
            run_step_events=self.get_expected_fn_spans(True),
            **kwargs,
        )

    def _do_test_run_steps_with_toolset_with_tracing_content_recording(
        self,
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
        run_step_events: List[List[Dict[str, Any]]] = None,
        has_annotations: bool = False,
        **kwargs,
    ) -> None:
        """The helper method to check the recordings."""
        client = self.create_client(**kwargs)
        if toolset is None == tool is None:
            raise ValueError("Please provide at lease one of toolset or tool, but not both.")
        elif toolset is not None:
            agent = client.create_agent(model=model, name="my-agent", instructions=instructions, toolset=toolset)

            # workaround for https://github.com/Azure/azure-sdk-for-python/issues/40086
            client.enable_auto_function_calls(toolset)
        elif tool is not None:
            agent = client.create_agent(
                model=model,
                name="my-agent",
                instructions=instructions,
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
            run = client.runs.create_and_process(
                thread_id=thread.id, agent_id=agent.id, polling_interval=self._sleep_time()
            )
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
        self._check_spans(
            model=model,
            recording_enabled=recording_enabled,
            instructions=instructions,
            message=message,
            have_submit_tools=have_submit_tools,
            use_stream=use_stream,
            tool_message_attribute_content=tool_message_attribute_content,
            event_contents=event_contents,
            run_step_events=run_step_events,
            has_annotations=has_annotations,
        )

    @pytest.mark.usefixtures("instrument_with_content")
    @agentClientPreparer()
    @recorded_by_proxy
    def test_telemetry_steps_with_fn_tool(self, **kwargs):
        """Test running functions with streaming and tracing content recording."""
        self._do_test_run_steps_with_toolset_with_tracing_content_recording(
            toolset=self._get_function_toolset(),
            model="gpt-4o",
            use_stream=False,
            message="What is the weather in New York?",
            recording_enabled=True,
            tool_message_attribute_content='{\\"weather\\": \\"Sunny\\"}',
            event_contents=[
                '{"tool_calls": [{"id": "*", "type": "function", "function": {"name": "fetch_weather", "arguments": {"location": "New York"}}}]}',
                '{"content": {"text": {"value": "*"}}, "role": "assistant"}',
            ],
            have_submit_tools=True,
            run_step_events=self.get_expected_fn_spans(True),
            **kwargs,
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
            tool=openapi_tool,
            model="gpt-4o",
            use_stream=False,
            message="What is the weather in New York, NY?",
            recording_enabled=True,
            tool_message_attribute_content="",
            event_contents=[],
            run_step_events=self.get_expected_openapi_spans(),
            **kwargs,
        )

    @pytest.mark.usefixtures("instrument_with_content")
    @agentClientPreparer()
    @recorded_by_proxy
    def test_telemetry_steps_with_mcp_tool(self, **kwargs):
        """Test run steps with OpenAPI."""
        mcp_tool = McpTool(
            server_label="github",
            server_url="https://gitmcp.io/Azure/azure-rest-api-specs",
            allowed_tools=["search_azure_rest_api_code"],  # Optional: specify allowed tools
        )
        model = "gpt-4o"
        instructions = "You are a helpful agent that can use MCP tools to assist users. Use the available MCP tools to answer questions and perform tasks."
        recording_enabled = True
        message = "Please summarize the Azure REST API specifications Readme"
        with self.create_client(**kwargs, by_endpoint=True) as agents_client:
            agent = agents_client.create_agent(
                model=model,
                name="my-agent",
                instructions=instructions,
                tools=mcp_tool.definitions,
            )
            thread = agents_client.threads.create()
            try:
                agents_client.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=message,
                )
                mcp_tool.update_headers("SuperSecret", "123456")
                run = agents_client.runs.create(
                    thread_id=thread.id, agent_id=agent.id, tool_resources=mcp_tool.resources
                )
                was_approved = False
                while run.status in [RunStatus.QUEUED, RunStatus.IN_PROGRESS, RunStatus.REQUIRES_ACTION]:
                    time.sleep(self._sleep_time())
                    run = agents_client.runs.get(thread_id=thread.id, run_id=run.id)

                    if run.status == RunStatus.REQUIRES_ACTION and isinstance(
                        run.required_action, SubmitToolApprovalAction
                    ):
                        tool_calls = run.required_action.submit_tool_approval.tool_calls
                        assert tool_calls, "No tool calls to approve."

                        tool_approvals = []
                        for tool_call in tool_calls:
                            if isinstance(tool_call, RequiredMcpToolCall):
                                tool_approvals.append(
                                    ToolApproval(
                                        tool_call_id=tool_call.id,
                                        approve=True,
                                        headers=mcp_tool.headers,
                                    )
                                )

                        if tool_approvals:
                            was_approved = True
                            agents_client.runs.submit_tool_outputs(
                                thread_id=thread.id, run_id=run.id, tool_approvals=tool_approvals
                            )
                assert was_approved, "The run was never approved."
                assert run.status != RunStatus.FAILED, run.last_error

                is_activity_step_found = False
                is_tool_call_step_found = False
                for run_step in agents_client.run_steps.list(thread_id=thread.id, run_id=run.id):
                    if isinstance(run_step.step_details, RunStepActivityDetails):
                        is_activity_step_found = True
                    if isinstance(run_step.step_details, RunStepToolCallDetails):
                        for tool_call in run_step.step_details.tool_calls:
                            if isinstance(tool_call, RunStepMcpToolCall):
                                is_tool_call_step_found = True
                                break
                assert is_activity_step_found, "RunStepMcpToolCall was not found."
                assert is_tool_call_step_found, "No RunStepMcpToolCall"
                messages = list(agents_client.messages.list(thread_id=thread.id))
                assert len(messages) > 1
            finally:
                agents_client.threads.delete(thread.id)
                agents_client.delete_agent(agent.id)

        self.exporter.force_flush()
        # Check the actual telemetry
        self._check_spans(
            model=model,
            recording_enabled=recording_enabled,
            instructions=instructions,
            message=message,
            have_submit_tools=True,
            use_stream=False,
            tool_message_attribute_content="",
            event_contents=[],
            run_step_events=self.get_expected_mcp_spans(),
        )

    @pytest.mark.usefixtures("instrument_with_content")
    @agentClientPreparer()
    @recorded_by_proxy
    def test_telemetry_steps_with_deep_research_tool(self, **kwargs):
        """Test running functions with streaming and tracing content recording."""

        self._do_test_run_steps_with_toolset_with_tracing_content_recording(
            tool=self._get_deep_research_tool(**kwargs),
            model="gpt-4o",
            use_stream=False,
            instructions="You are a helpful agent that assists in researching scientific topics.",
            message="Research the benefits of renewable energy sources. Keep the response brief.",
            recording_enabled=True,
            tool_message_attribute_content="",
            event_contents=[],
            have_submit_tools=False,
            run_step_events=self.get_expected_deep_research_spans(),
            has_annotations=True,
            **kwargs,
        )


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
