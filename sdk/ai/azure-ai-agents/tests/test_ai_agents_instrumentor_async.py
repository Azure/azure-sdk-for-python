# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable
import pytest
import os
import json
import time
import pytest
import functools
from typing import Set, Callable, Any
from azure.ai.agents.models import (
    AgentsResponseFormatMode,
    AgentsResponseFormat,
    AsyncAgentEventHandler,
    AsyncFunctionTool,
    MessageDeltaChunk,
    MessageDeltaTextContent,
    RunStep,
    ThreadMessage,
    ThreadRun,
    AsyncToolSet,
)
from azure.ai.agents.telemetry._ai_agents_instrumentor import _AIAgentsInstrumentorPreview
from azure.ai.agents.telemetry import AIAgentsInstrumentor, _utils
from azure.core.settings import settings
from memory_trace_exporter import MemoryTraceExporter
from gen_ai_trace_verifier import GenAiTraceVerifier
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from azure.ai.agents.aio import AgentsClient

from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import (
    AzureRecordedTestCase,
    EnvironmentVariableLoader,
)

agentClientPreparer = functools.partial(
    EnvironmentVariableLoader,
    "azure_ai_agents",
    # TODO: uncomment this endpoint when re running with 1DP
    # azure_ai_agents_tests_project_endpoint="https://aiservices-id.services.ai.azure.com/api/projects/project-name",
    # TODO: remove this endpoint when re running with 1DP
    azure_ai_agents_tests_project_endpoint="https://Sanitized.api.azureml.ms/agents/v1.0/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/00000/providers/Microsoft.MachineLearningServices/workspaces/00000/",
    azure_ai_agents_tests_data_path="azureml://subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/rg-resour-cegr-oupfoo1/workspaces/abcd-abcdabcdabcda-abcdefghijklm/datastores/workspaceblobstore/paths/LocalUpload/000000000000/product_info_1.md",
)

CONTENT_TRACING_ENV_VARIABLE = "AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED"
settings.tracing_implementation = "OpenTelemetry"
_utils._span_impl_type = settings.tracing_implementation()


class TestAiAgentsInstrumentor(AzureRecordedTestCase):
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

    @pytest.mark.usefixtures("instrument_with_content")
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_agent_chat_with_tracing_content_recording_enabled(self, **kwargs):
        client = self.create_client(**kwargs)
        agent = await client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        thread = await client.threads.create()
        message = await client.messages.create(thread_id=thread.id, role="user", content="Hello, tell me a joke")
        run = await client.runs.create(thread_id=thread.id, agent_id=agent.id)

        while run.status in ["queued", "in_progress", "requires_action"]:
            # wait for a second
            time.sleep(1)
            run = await client.runs.get(thread_id=thread.id, run_id=run.id)
            print("Run status:", run.status)
        print("Run completed with status:", run.status)

        # delete agent and close client
        await client.delete_agent(agent.id)
        print("Deleted agent")
        messages = [m async for m in client.messages.list(thread_id=thread.id)]
        assert len(messages) > 1
        await client.close()

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name("create_agent my-agent")
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
            ("gen_ai.response.model", "gpt-4o"),
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
            ("gen_ai.response.model", "gpt-4o"),
            ("gen_ai.usage.input_tokens", "+"),
            ("gen_ai.usage.output_tokens", "+"),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        spans = self.exporter.get_spans_by_name("list_messages")
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

    @pytest.mark.usefixtures("instrument_without_content")
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_agent_chat_with_tracing_content_recording_disabled(self, **kwargs):
        client = self.create_client(**kwargs)
        agent = await client.create_agent(model="gpt-4o", name="my-agent", instructions="You are helpful agent")
        thread = await client.threads.create()
        message = await client.messages.create(thread_id=thread.id, role="user", content="Hello, tell me a joke")
        run = await client.runs.create(thread_id=thread.id, agent_id=agent.id)

        while run.status in ["queued", "in_progress", "requires_action"]:
            # wait for a second
            time.sleep(1)
            run = await client.runs.get(thread_id=thread.id, run_id=run.id)
            print("Run status:", run.status)
        print("Run completed with status:", run.status)

        # delete agent and close client
        await client.delete_agent(agent.id)
        print("Deleted agent")
        message_async = client.messages.list(thread_id=thread.id)
        messages = [m async for m in message_async]
        assert len(messages) > 1
        await client.close()

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name("create_agent my-agent")
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
            ("gen_ai.response.model", "gpt-4o"),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        spans = self.exporter.get_spans_by_name("list_messages")
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

    @pytest.mark.usefixtures("instrument_with_content")
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_agent_streaming_with_toolset_with_tracing_content_recording_enabled(self, **kwargs):
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

        functions = AsyncFunctionTool(user_functions)
        toolset = AsyncToolSet()
        toolset.add(functions)

        client = self.create_client(**kwargs)
        client.enable_auto_function_calls(toolset)

        agent = await client.create_agent(
            model="gpt-4o", name="my-agent", instructions="You are helpful agent", toolset=toolset
        )

        # workaround for https://github.com/Azure/azure-sdk-for-python/issues/40086
        client.enable_auto_function_calls(toolset)

        thread = await client.threads.create()
        message = await client.messages.create(
            thread_id=thread.id, role="user", content="What is the weather in New York?"
        )

        event_handler = MyEventHandler()
        async with await client.runs.stream(
            thread_id=thread.id, agent_id=agent.id, event_handler=event_handler
        ) as stream:
            await stream.until_done()

        # delete agent and close client
        await client.delete_agent(agent.id)
        print("Deleted agent")
        messages = [m async for m in client.messages.list(thread_id=thread.id)]
        assert len(messages) > 1
        steps = [step async for step in client.run_steps.list(thread_id=thread.id, run_id=event_handler.run_id)]
        assert len(steps) >= 1
        await client.close()

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name("list_run_steps")
        assert len(spans) == 1
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
        spans = self.exporter.get_spans_by_name("create_agent my-agent")
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
                    "gen_ai.event.content": '{"content": "What is the weather in New York?", "role": "user"}',
                },
            }
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

        spans = self.exporter.get_spans_by_name("submit_tool_outputs")
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
                    "gen_ai.run_step.start.timestamp": "*",
                    "gen_ai.run_step.end.timestamp": "*",
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

        spans = self.exporter.get_spans_by_name("list_messages")
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

    @pytest.mark.usefixtures("instrument_without_content")
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_agent_streaming_with_toolset_with_tracing_content_recording_disabled(self, **kwargs):
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

        functions = AsyncFunctionTool(user_functions)
        toolset = AsyncToolSet()
        toolset.add(functions)

        client = self.create_client(**kwargs)
        agent = await client.create_agent(
            model="gpt-4o", name="my-agent", instructions="You are helpful agent", toolset=toolset
        )

        # workaround for https://github.com/Azure/azure-sdk-for-python/issues/40086
        client.enable_auto_function_calls(toolset)

        thread = await client.threads.create()
        message = await client.messages.create(
            thread_id=thread.id, role="user", content="What is the weather in New York?"
        )

        async with await client.runs.stream(
            thread_id=thread.id, agent_id=agent.id, event_handler=MyEventHandler()
        ) as stream:
            await stream.until_done()

        # delete agent and close client
        await client.delete_agent(agent.id)
        print("Deleted agent")
        messages = [m async for m in client.messages.list(thread_id=thread.id)]
        assert len(messages) > 1
        await client.close()

        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name("create_agent my-agent")
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

        spans = self.exporter.get_spans_by_name("submit_tool_outputs")
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
                    "gen_ai.run_step.start.timestamp": "*",
                    "gen_ai.run_step.end.timestamp": "*",
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

        spans = self.exporter.get_spans_by_name("list_messages")
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


class MyEventHandler(AsyncAgentEventHandler):

    async def on_message_delta(self, delta: "MessageDeltaChunk") -> None:
        for content_part in delta.delta.content:
            if isinstance(content_part, MessageDeltaTextContent):
                text_value = content_part.text.value if content_part.text else "No text"
                print(f"Text delta received: {text_value}")

    async def on_thread_message(self, message: "ThreadMessage") -> None:
        print(f"ThreadMessage created. ID: {message.id}, Status: {message.status}")

    async def on_thread_run(self, run: "ThreadRun") -> None:
        print(f"ThreadRun status: {run.status}")
        self.run_id = run.id
        if run.status == "failed":
            print(f"Run failed. Error: {run.last_error}")

    async def on_run_step(self, step: "RunStep") -> None:
        print(f"RunStep type: {step.type}, Status: {step.status}")

    async def on_error(self, data: str) -> None:
        print(f"An error occurred. Data: {data}")

    async def on_done(self) -> None:
        print("Stream completed.")

    async def on_unhandled_event(self, event_type: str, event_data: Any) -> None:
        print(f"Unhandled Event Type: {event_type}, Data: {event_data}")
