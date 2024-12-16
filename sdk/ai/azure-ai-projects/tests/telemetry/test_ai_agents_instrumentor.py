# pylint: disable=too-many-lines
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable# cSpell:disable
import pytest
import os
import json
import time
import pytest
import functools
from typing import Set, Callable, Any
from azure.ai.projects.telemetry.agents._ai_agents_instrumentor import _AIAgentsInstrumentorPreview
from azure.ai.projects.models import AgentsApiResponseFormatMode, AgentsApiResponseFormat

from azure.ai.projects.models import AgentEventHandler

from azure.ai.projects.telemetry.agents import AIAgentsInstrumentor
from azure.core.settings import settings
from memory_trace_exporter import MemoryTraceExporter
from gen_ai_trace_verifier import GenAiTraceVerifier
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

from azure.ai.projects import AIProjectClient
from devtools_testutils import (
    AzureRecordedTestCase,
    EnvironmentVariableLoader,
    recorded_by_proxy,
)

from azure.ai.projects.models import (
    FunctionTool,
    MessageDeltaChunk,
    MessageDeltaTextContent,
    RunStep,
    ThreadMessage,
    ThreadRun,
    ToolSet,
)

agentClientPreparer = functools.partial(
    EnvironmentVariableLoader,
    "azure_ai_projects",
    azure_ai_projects_connection_string="https://foo.bar.some-domain.ms;00000000-0000-0000-0000-000000000000;rg-resour-cegr-oupfoo1;abcd-abcdabcdabcda-abcdefghijklm",
    azure_ai_projects_data_path="azureml://subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/rg-resour-cegr-oupfoo1/workspaces/abcd-abcdabcdabcda-abcdefghijklm/datastores/workspaceblobstore/paths/LocalUpload/000000000000/product_info_1.md",
)
"""
agentClientPreparer = functools.partial(
    EnvironmentVariableLoader,
    'azure_ai_project',
    azure_ai_project_host_name="https://foo.bar.some-domain.ms",
    azure_ai_project_subscription_id="00000000-0000-0000-0000-000000000000",
    azure_ai_project_resource_group_name="rg-resour-cegr-oupfoo1",
    azure_ai_project_workspace_name="abcd-abcdabcdabcda-abcdefghijklm",
)
"""

CONTENT_TRACING_ENV_VARIABLE = "AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED"
content_tracing_initial_value = os.getenv(CONTENT_TRACING_ENV_VARIABLE)


class TestAiAgentsInstrumentor(AzureRecordedTestCase):
    """Tests for AI agents instrumentor."""

    @classmethod
    def teardown_class(cls):
        if content_tracing_initial_value is not None:
            os.environ[CONTENT_TRACING_ENV_VARIABLE] = content_tracing_initial_value

    # helper function: create client and using environment variables
    def create_client(self, **kwargs):
        # fetch environment variables
        connection_string = kwargs.pop("azure_ai_projects_connection_string")
        credential = self.get_credential(AIProjectClient, is_async=False)

        # create and return client
        client = AIProjectClient.from_connection_string(
            credential=credential,
            conn_str=connection_string,
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
            (AgentsApiResponseFormatMode.AUTO, "auto"),
            (AgentsApiResponseFormat(type="test"), "test"),
        ],
    )
    def test_convert_api_response_format(self, fmt, expected):
        """Test conversion of AgentsApiResponseFormatOption to string"""
        actual = _AIAgentsInstrumentorPreview.agent_api_response_to_str(fmt)
        assert actual == expected

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

    @pytest.mark.skip
    @agentClientPreparer()
    @recorded_by_proxy
    def test_instrumentation(self, **kwargs):
        # Make sure code is not instrumented due to a previous test exception
        AIAgentsInstrumentor().uninstrument()
        with self.create_client(**kwargs) as client:
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

    @pytest.mark.skip
    @agentClientPreparer()
    @recorded_by_proxy
    def test_instrumenting_twice_does_not_cause_exception(self, **kwargs):
        # Make sure code is not instrumented due to a previous test exception
        AIAgentsInstrumentor().uninstrument()
        with self.create_client(**kwargs) as client:
            exception_caught = False
            try:
                AIAgentsInstrumentor().instrument()
                AIAgentsInstrumentor().instrument()
            except RuntimeError as e:
                exception_caught = True
                print(e)
            AIAgentsInstrumentor().uninstrument()
            assert exception_caught == False

    @pytest.mark.skip
    @agentClientPreparer()
    @recorded_by_proxy
    def test_uninstrumenting_uninstrumented_does_not_cause_exception(self, **kwargs):
        # Make sure code is not instrumented due to a previous test exception
        AIAgentsInstrumentor().uninstrument()
        with self.create_client(**kwargs) as client:
            exception_caught = False
            try:
                AIAgentsInstrumentor().uninstrument()
            except RuntimeError as e:
                exception_caught = True
                print(e)
            assert exception_caught == False

    @pytest.mark.skip
    @agentClientPreparer()
    @recorded_by_proxy
    def test_uninstrumenting_twice_does_not_cause_exception(self, **kwargs):
        # Make sure code is not instrumented due to a previous test exception
        AIAgentsInstrumentor().uninstrument()
        with self.create_client(**kwargs) as client:
            exception_caught = False
            uninstrumented_once = False
            try:
                AIAgentsInstrumentor().instrument()
                AIAgentsInstrumentor().uninstrument()
                AIAgentsInstrumentor().uninstrument()
            except RuntimeError as e:
                exception_caught = True
                print(e)
            assert exception_caught == False

    @pytest.mark.skip
    @agentClientPreparer()
    @recorded_by_proxy
    def test_is_content_recording_enabled(self, **kwargs):
        # Make sure code is not instrumented due to a previous test exception
        AIAgentsInstrumentor().uninstrument()
        self.modify_env_var(CONTENT_TRACING_ENV_VARIABLE, "False")
        with self.create_client(**kwargs) as client:
            exception_caught = False
            uninstrumented_once = False
            try:
                # From environment variable instrumenting from uninstrumented
                AIAgentsInstrumentor().instrument()
                self.modify_env_var(CONTENT_TRACING_ENV_VARIABLE, "False")
                AIAgentsInstrumentor().instrument()
                content_recording_enabled = AIAgentsInstrumentor().is_content_recording_enabled()
                assert content_recording_enabled == False
                AIAgentsInstrumentor().uninstrument()
                self.modify_env_var(CONTENT_TRACING_ENV_VARIABLE, "True")
                AIAgentsInstrumentor().instrument()
                content_recording_enabled = AIAgentsInstrumentor().is_content_recording_enabled()
                assert content_recording_enabled == True
                AIAgentsInstrumentor().uninstrument()
                self.modify_env_var(CONTENT_TRACING_ENV_VARIABLE, "invalid")
                AIAgentsInstrumentor().instrument()
                content_recording_enabled = AIAgentsInstrumentor().is_content_recording_enabled()
                assert content_recording_enabled == False

                # From environment variable instrumenting from instrumented
                self.modify_env_var(CONTENT_TRACING_ENV_VARIABLE, "True")
                AIAgentsInstrumentor().instrument()
                content_recording_enabled = AIAgentsInstrumentor().is_content_recording_enabled()
                assert content_recording_enabled == True
                self.modify_env_var(CONTENT_TRACING_ENV_VARIABLE, "True")
                AIAgentsInstrumentor().instrument()
                content_recording_enabled = AIAgentsInstrumentor().is_content_recording_enabled()
                assert content_recording_enabled == True
                self.modify_env_var(CONTENT_TRACING_ENV_VARIABLE, "invalid")
                AIAgentsInstrumentor().instrument()
                content_recording_enabled = AIAgentsInstrumentor().is_content_recording_enabled()
                assert content_recording_enabled == False

                # From parameter instrumenting from uninstrumented
                AIAgentsInstrumentor().uninstrument()
                self.modify_env_var(CONTENT_TRACING_ENV_VARIABLE, "True")
                AIAgentsInstrumentor().instrument(enable_content_recording=False)
                content_recording_enabled = AIAgentsInstrumentor().is_content_recording_enabled()
                assert content_recording_enabled == False
                AIAgentsInstrumentor().uninstrument()
                self.modify_env_var(CONTENT_TRACING_ENV_VARIABLE, "False")
                AIAgentsInstrumentor().instrument(enable_content_recording=True)
                content_recording_enabled = AIAgentsInstrumentor().is_content_recording_enabled()
                assert content_recording_enabled == True

                # From parameter instrumenting from instrumented
                self.modify_env_var(CONTENT_TRACING_ENV_VARIABLE, "True")
                AIAgentsInstrumentor().instrument(enable_content_recording=False)
                content_recording_enabled = AIAgentsInstrumentor().is_content_recording_enabled()
                assert content_recording_enabled == False
                self.modify_env_var(CONTENT_TRACING_ENV_VARIABLE, "False")
                AIAgentsInstrumentor().instrument(enable_content_recording=True)
                content_recording_enabled = AIAgentsInstrumentor().is_content_recording_enabled()
                assert content_recording_enabled == True
            except RuntimeError as e:
                exception_caught = True
                print(e)
            assert exception_caught == False

    @pytest.mark.skip
    @agentClientPreparer()
    @recorded_by_proxy
    def test_agent_chat_with_tracing_content_recording_enabled(self, **kwargs):
        # Make sure code is not instrumented due to a previous test exception
        try:
            AIAgentsInstrumentor().uninstrument()
        except RuntimeError as e:
            pass
        self.modify_env_var(CONTENT_TRACING_ENV_VARIABLE, "True")

        processor, exporter = self.setup_memory_trace_exporter()
        AIAgentsInstrumentor().instrument()

        client = self.create_client(**kwargs)
        agent = client.agents.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        thread = client.agents.create_thread()
        message = client.agents.create_message(thread_id=thread.id, role="user", content="Hello, tell me a joke")
        run = client.agents.create_run(thread_id=thread.id, assistant_id=agent.id)

        while run.status in ["queued", "in_progress", "requires_action"]:
            # wait for a second
            time.sleep(1)
            run = client.agents.get_run(thread_id=thread.id, run_id=run.id)
            print("Run status:", run.status)
        print("Run completed with status:", run.status)

        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        messages = client.agents.list_messages(thread_id=thread.id)
        client.close()

        processor.force_flush()
        spans = exporter.get_spans_by_name("create_agent my-agent")
        assert len(spans) == 1
        span = spans[0]
        expected_attributes = [
            ("gen_ai.system", "az.ai.agents"),
            ("gen_ai.operation.name", "create_agent"),
            ("server.address", ""),
            ("gen_ai.request.model", "gpt-4o"),
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

        spans = exporter.get_spans_by_name("create_thread")
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

        spans = exporter.get_spans_by_name("create_message")
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

        spans = exporter.get_spans_by_name("start_thread_run")
        assert len(spans) == 1
        span = spans[0]
        expected_attributes = [
            ("gen_ai.system", "az.ai.agents"),
            ("gen_ai.operation.name", "start_thread_run"),
            ("server.address", ""),
            ("gen_ai.thread.id", ""),
            ("gen_ai.agent.id", ""),
            ("gen_ai.thread.run.status", "queued"),
            ("gen_ai.response.model", "gpt-4o"),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        spans = exporter.get_spans_by_name("list_messages")
        assert len(spans) == 1
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
                    "gen_ai.event.content": '{"content": {"text": {"value": "*"}}, "role": "assistant"}',
                },
            },
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

        AIAgentsInstrumentor().uninstrument()

    @pytest.mark.skip
    @agentClientPreparer()
    @recorded_by_proxy
    def test_agent_chat_with_tracing_content_recording_disabled(self, **kwargs):
        # Make sure code is not instrumented due to a previous test exception
        try:
            AIAgentsInstrumentor().uninstrument()
        except RuntimeError as e:
            pass
        self.modify_env_var(CONTENT_TRACING_ENV_VARIABLE, "False")

        processor, exporter = self.setup_memory_trace_exporter()
        AIAgentsInstrumentor().instrument()

        client = self.create_client(**kwargs)
        agent = client.agents.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        thread = client.agents.create_thread()
        message = client.agents.create_message(thread_id=thread.id, role="user", content="Hello, tell me a joke")
        run = client.agents.create_run(thread_id=thread.id, assistant_id=agent.id)

        while run.status in ["queued", "in_progress", "requires_action"]:
            # wait for a second
            time.sleep(1)
            run = client.agents.get_run(thread_id=thread.id, run_id=run.id)
            print("Run status:", run.status)
        print("Run completed with status:", run.status)

        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        messages = client.agents.list_messages(thread_id=thread.id)
        client.close()

        processor.force_flush()
        spans = exporter.get_spans_by_name("create_agent my-agent")
        assert len(spans) == 1
        span = spans[0]
        expected_attributes = [
            ("gen_ai.system", "az.ai.agents"),
            ("gen_ai.operation.name", "create_agent"),
            ("server.address", ""),
            ("gen_ai.request.model", "gpt-4o"),
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

        spans = exporter.get_spans_by_name("create_thread")
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

        spans = exporter.get_spans_by_name("create_message")
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

        spans = exporter.get_spans_by_name("start_thread_run")
        assert len(spans) == 1
        span = spans[0]
        expected_attributes = [
            ("gen_ai.system", "az.ai.agents"),
            ("gen_ai.operation.name", "start_thread_run"),
            ("server.address", ""),
            ("gen_ai.thread.id", ""),
            ("gen_ai.agent.id", ""),
            ("gen_ai.thread.run.status", "queued"),
            ("gen_ai.response.model", "gpt-4o"),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        spans = exporter.get_spans_by_name("list_messages")
        assert len(spans) == 1
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
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

        AIAgentsInstrumentor().uninstrument()

    @pytest.mark.skip
    @agentClientPreparer()
    @recorded_by_proxy
    def test_agent_streaming_with_toolset_with_tracing_content_recording_enabled(self, **kwargs):
        # Make sure code is not instrumented due to a previous test exception
        try:
            AIAgentsInstrumentor().uninstrument()
        except RuntimeError as e:
            pass
        self.modify_env_var(CONTENT_TRACING_ENV_VARIABLE, "True")

        processor, exporter = self.setup_memory_trace_exporter()
        AIAgentsInstrumentor().instrument()

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

        client = self.create_client(**kwargs)
        agent = client.agents.create_agent(
            model="gpt-4o", name="my-agent", instructions="You are helpful agent", toolset=toolset
        )
        thread = client.agents.create_thread()
        message = client.agents.create_message(
            thread_id=thread.id, role="user", content="What is the weather in New York?"
        )

        with client.agents.create_stream(
            thread_id=thread.id, assistant_id=agent.id, event_handler=MyEventHandler()
        ) as stream:
            stream.until_done()

        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        messages = client.agents.list_messages(thread_id=thread.id)
        client.close()

        processor.force_flush()
        spans = exporter.get_spans_by_name("create_agent my-agent")
        assert len(spans) == 1
        span = spans[0]
        expected_attributes = [
            ("gen_ai.system", "az.ai.agents"),
            ("gen_ai.operation.name", "create_agent"),
            ("server.address", ""),
            ("gen_ai.request.model", "gpt-4o"),
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

        spans = exporter.get_spans_by_name("create_thread")
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

        spans = exporter.get_spans_by_name("create_message")
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
                    "gen_ai.event.content": '{"content": "What is the weather in New York?", "role": "user"}',
                },
            }
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

        spans = exporter.get_spans_by_name("submit_tool_outputs")
        assert len(spans) == 1
        span = spans[0]
        expected_attributes = [
            ("gen_ai.system", "az.ai.agents"),
            ("gen_ai.operation.name", "submit_tool_outputs"),
            ("server.address", ""),
            ("gen_ai.thread.id", ""),
            ("gen_ai.thread.run.id", ""),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        spans = exporter.get_spans_by_name("process_thread_run")
        assert len(spans) == 1
        span = spans[0]
        expected_attributes = [
            ("gen_ai.system", "az.ai.agents"),
            ("gen_ai.operation.name", "process_thread_run"),
            ("server.address", ""),
            ("gen_ai.thread.id", ""),
            ("gen_ai.agent.id", ""),
            ("gen_ai.thread.run.status", "completed"),
            ("gen_ai.response.model", "gpt-4o"),
            ("gen_ai.usage.input_tokens", "+"),
            ("gen_ai.usage.output_tokens", "+"),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        expected_events = [
            {
                "name": "gen_ai.tool.message",
                "attributes": {"gen_ai.event.content": '{"content": "{\\"weather\\": \\"Sunny\\"}", "id": "*"}'},
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.system": "az.ai.agents",
                    "gen_ai.thread.id": "*",
                    "gen_ai.agent.id": "*",
                    "gen_ai.thread.run.id": "*",
                    "gen_ai.message.status": "completed",
                    "gen_ai.usage.input_tokens": "+",
                    "gen_ai.usage.output_tokens": "+",
                    "gen_ai.event.content": '{"tool_calls": [{"id": "*", "type": "function", "function": {"name": "fetch_weather", "arguments": {"location": "New York"}}}]}',
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
                    "gen_ai.message.status": "completed",
                    "gen_ai.usage.input_tokens": "+",
                    "gen_ai.usage.output_tokens": "+",
                    "gen_ai.event.content": '{"content": {"text": {"value": "*"}}, "role": "assistant"}',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

        spans = exporter.get_spans_by_name("list_messages")
        assert len(spans) == 1
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
                    "gen_ai.event.content": '{"content": {"text": {"value": "*"}}, "role": "assistant"}',
                },
            },
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.system": "az.ai.agents",
                    "gen_ai.thread.id": "*",
                    "gen_ai.message.id": "*",
                    "gen_ai.event.content": '{"content": {"text": {"value": "What is the weather in New York?"}}, "role": "user"}',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

        AIAgentsInstrumentor().uninstrument()

    @pytest.mark.skip
    @agentClientPreparer()
    @recorded_by_proxy
    def test_agent_streaming_with_toolset_with_tracing_content_recording_disabled(self, **kwargs):
        # Make sure code is not instrumented due to a previous test exception
        try:
            AIAgentsInstrumentor().uninstrument()
        except RuntimeError as e:
            pass
        self.modify_env_var(CONTENT_TRACING_ENV_VARIABLE, "False")

        processor, exporter = self.setup_memory_trace_exporter()
        AIAgentsInstrumentor().instrument()

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

        client = self.create_client(**kwargs)
        agent = client.agents.create_agent(
            model="gpt-4o", name="my-agent", instructions="You are helpful agent", toolset=toolset
        )
        thread = client.agents.create_thread()
        message = client.agents.create_message(
            thread_id=thread.id, role="user", content="What is the weather in New York?"
        )

        with client.agents.create_stream(
            thread_id=thread.id, assistant_id=agent.id, event_handler=MyEventHandler()
        ) as stream:
            stream.until_done()

        # delete agent and close client
        client.agents.delete_agent(agent.id)
        print("Deleted agent")
        messages = client.agents.list_messages(thread_id=thread.id)
        client.close()

        processor.force_flush()
        spans = exporter.get_spans_by_name("create_agent my-agent")
        assert len(spans) == 1
        span = spans[0]
        expected_attributes = [
            ("gen_ai.system", "az.ai.agents"),
            ("gen_ai.operation.name", "create_agent"),
            ("server.address", ""),
            ("gen_ai.request.model", "gpt-4o"),
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

        spans = exporter.get_spans_by_name("create_thread")
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

        spans = exporter.get_spans_by_name("create_message")
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

        spans = exporter.get_spans_by_name("submit_tool_outputs")
        assert len(spans) == 1
        span = spans[0]
        expected_attributes = [
            ("gen_ai.system", "az.ai.agents"),
            ("gen_ai.operation.name", "submit_tool_outputs"),
            ("server.address", ""),
            ("gen_ai.thread.id", ""),
            ("gen_ai.thread.run.id", ""),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        spans = exporter.get_spans_by_name("process_thread_run")
        assert len(spans) == 1
        span = spans[0]
        expected_attributes = [
            ("gen_ai.system", "az.ai.agents"),
            ("gen_ai.operation.name", "process_thread_run"),
            ("server.address", ""),
            ("gen_ai.thread.id", ""),
            ("gen_ai.agent.id", ""),
            ("gen_ai.thread.run.status", "completed"),
            ("gen_ai.response.model", "gpt-4o"),
            ("gen_ai.usage.input_tokens", "+"),
            ("gen_ai.usage.output_tokens", "+"),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        expected_events = [
            {
                "name": "gen_ai.tool.message",
                "attributes": {"gen_ai.event.content": '{"content": "", "id": "*"}'},
            },
            {
                "name": "gen_ai.assistant.message",
                "attributes": {
                    "gen_ai.system": "az.ai.agents",
                    "gen_ai.thread.id": "*",
                    "gen_ai.agent.id": "*",
                    "gen_ai.thread.run.id": "*",
                    "gen_ai.message.status": "completed",
                    "gen_ai.usage.input_tokens": "+",
                    "gen_ai.usage.output_tokens": "+",
                    "gen_ai.event.content": '{"tool_calls": [{"id": "*", "type": "function"}]}',
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
                    "gen_ai.message.status": "completed",
                    "gen_ai.usage.input_tokens": "+",
                    "gen_ai.usage.output_tokens": "+",
                    "gen_ai.event.content": '{"role": "assistant"}',
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

        spans = exporter.get_spans_by_name("list_messages")
        assert len(spans) == 1
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
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

        AIAgentsInstrumentor().uninstrument()


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
