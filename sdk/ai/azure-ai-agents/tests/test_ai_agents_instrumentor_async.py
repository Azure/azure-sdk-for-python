# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable
import os
import json
import jsonref
import time
import pytest
from typing import Any, Callable, Dict, List, Optional, Set
from azure.ai.agents.models import (
    AgentsResponseFormatMode,
    AgentsResponseFormat,
    AsyncAgentEventHandler,
    AsyncFunctionTool,
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
    ToolApproval,
    AsyncToolSet,
    Tool,
)
from azure.ai.agents.telemetry._ai_agents_instrumentor import _AIAgentsInstrumentorPreview
from azure.ai.agents.telemetry import AIAgentsInstrumentor, _utils
from azure.core.settings import settings
from gen_ai_trace_verifier import GenAiTraceVerifier
from azure.ai.agents.aio import AgentsClient

from devtools_testutils.aio import recorded_by_proxy_async

from test_agents_client_base import agentClientPreparer
from test_ai_instrumentor_base import TestAiAgentsInstrumentorBase, MessageCreationMode, CONTENT_TRACING_ENV_VARIABLE

settings.tracing_implementation = "OpenTelemetry"
_utils._span_impl_type = settings.tracing_implementation()


class TestAiAgentsInstrumentor(TestAiAgentsInstrumentorBase):
    """Tests for AI agents instrumentor."""

    def create_client(self, **kwargs):
        """helper function: create client and using environment variables"""
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
        # Note: The proper way to invoke the same test over and over again with different parameter values is to use @pytest.mark.parametrize. However,
        # this does not work together with @recorded_by_proxy. So we call the helper function 4 times instead in a single recorded test.
        await self._agent_chat_with_tracing_content_recording_enabled(
            message_creation_mode=MessageCreationMode.MESSAGE_CREATE_STR, **kwargs
        )
        await self._agent_chat_with_tracing_content_recording_enabled(
            message_creation_mode=MessageCreationMode.MESSAGE_CREATE_INPUT_TEXT_BLOCK, **kwargs
        )
        await self._agent_chat_with_tracing_content_recording_enabled(
            message_creation_mode=MessageCreationMode.THREAD_CREATE_STR, **kwargs
        )
        await self._agent_chat_with_tracing_content_recording_enabled(
            message_creation_mode=MessageCreationMode.THREAD_CREATE_INPUT_TEXT_BLOCK, **kwargs
        )

    async def _agent_chat_with_tracing_content_recording_enabled(
        self, message_creation_mode: MessageCreationMode, **kwargs
    ):
        self.cleanup()
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "True"})
        self.setup_telemetry()
        assert True == AIAgentsInstrumentor().is_content_recording_enabled()
        assert True == AIAgentsInstrumentor().is_instrumented()

        client = self.create_client(**kwargs)
        agent = await client.create_agent(model="gpt-4o-mini", name="my-agent", instructions="You are helpful agent")
        user_content = "Hello, tell me a joke"

        # Test 4 different patterns of thread & message creation
        if message_creation_mode == MessageCreationMode.MESSAGE_CREATE_STR:
            thread = await client.threads.create()
            await client.messages.create(thread_id=thread.id, role="user", content=user_content)
        elif message_creation_mode == MessageCreationMode.MESSAGE_CREATE_INPUT_TEXT_BLOCK:
            thread = await client.threads.create()
            await client.messages.create(
                thread_id=thread.id, role="user", content=[MessageInputTextBlock(text=user_content)]
            )
        elif message_creation_mode == MessageCreationMode.THREAD_CREATE_STR:
            thread = await client.threads.create(messages=[ThreadMessageOptions(role="user", content=user_content)])
        elif message_creation_mode == MessageCreationMode.THREAD_CREATE_INPUT_TEXT_BLOCK:
            thread = await client.threads.create(
                messages=[ThreadMessageOptions(role="user", content=[MessageInputTextBlock(text=user_content)])]
            )
        else:
            assert False, f"Unknown message creation mode: {message_creation_mode}"

        run = await client.runs.create(thread_id=thread.id, agent_id=agent.id)

        while run.status in ["queued", "in_progress", "requires_action"]:
            # wait for a second
            time.sleep(self._sleep_time())
            run = await client.runs.get(thread_id=thread.id, run_id=run.id)
            print("Run status:", run.status)
        print("Run completed with status:", run.status)

        # delete agent and close client
        await client.delete_agent(agent.id)
        print("Deleted agent")
        messages = [m async for m in client.messages.list(thread_id=thread.id)]
        assert len(messages) > 1
        await client.close()

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
    @recorded_by_proxy_async
    async def test_agent_chat_with_tracing_content_recording_disabled(self, **kwargs):
        client = self.create_client(**kwargs)
        agent = await client.create_agent(model="gpt-4o-mini", name="my-agent", instructions="You are helpful agent")
        thread = await client.threads.create()
        await client.messages.create(thread_id=thread.id, role="user", content="Hello, tell me a joke")
        run = await client.runs.create(thread_id=thread.id, agent_id=agent.id)

        while run.status in ["queued", "in_progress", "requires_action"]:
            # wait for a second
            time.sleep(self._sleep_time())
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
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True
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
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

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

        functions = AsyncFunctionTool(user_functions)
        toolset = AsyncToolSet()
        toolset.add(functions)
        return toolset

    @pytest.mark.usefixtures("instrument_with_content")
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_agent_streaming_with_toolset_with_tracing_content_recording_enabled(self, **kwargs):
        """Test running functions with streaming and tracing content recording."""
        await self._do_test_run_steps_with_toolset_with_tracing_content_recording(
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

    async def _do_test_run_steps_with_toolset_with_tracing_content_recording(
        self,
        model: str,
        message: str,
        use_stream: bool,
        recording_enabled: bool,
        tool_message_attribute_content: str,
        event_contents: List[str],
        instructions: str = "You are helpful agent",
        toolset: Optional[AsyncToolSet] = None,
        tool: Optional[Tool] = None,
        have_submit_tools=False,
        run_step_events: List[List[Dict[str, Any]]] = None,
        has_annotations: bool = False,
        **kwargs,
    ):
        """The helper method to check the recordings."""
        client = self.create_client(**kwargs)
        if toolset is None == tool is None:
            raise ValueError("Please provide at lease one of toolset or tool, but not both.")
        elif toolset is not None:
            agent = await client.create_agent(model=model, name="my-agent", instructions=instructions, toolset=toolset)

            # workaround for https://github.com/Azure/azure-sdk-for-python/issues/40086
            client.enable_auto_function_calls(toolset)
        elif tool is not None:
            agent = await client.create_agent(
                model=model,
                name="my-agent",
                instructions=instructions,
                tools=tool.definitions,
                tool_resources=tool.resources,
            )

        thread = await client.threads.create()
        await client.messages.create(thread_id=thread.id, role="user", content=message)

        if use_stream:
            event_handler = MyEventHandler()
            async with await client.runs.stream(
                thread_id=thread.id, agent_id=agent.id, event_handler=event_handler
            ) as stream:
                await stream.until_done()
            run_id = event_handler.run_id
        else:
            run = await client.runs.create_and_process(
                thread_id=thread.id, agent_id=agent.id, polling_interval=self._sleep_time()
            )
            assert run.status != RunStatus.FAILED, run.last_error
            run_id = run.id

        # delete agent and close client
        await client.delete_agent(agent.id)
        print("Deleted agent")
        messages = [m async for m in client.messages.list(thread_id=thread.id)]
        assert len(messages) > 1
        steps = [step async for step in client.run_steps.list(thread_id=thread.id, run_id=run_id)]
        assert len(steps) >= 1
        await client.close()

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

    @pytest.mark.usefixtures("instrument_without_content")
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_agent_streaming_with_toolset_with_tracing_content_recording_disabled(self, **kwargs):
        await self._do_test_run_steps_with_toolset_with_tracing_content_recording(
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

    @pytest.mark.usefixtures("instrument_with_content")
    @agentClientPreparer()
    @recorded_by_proxy_async
    async def test_telemetry_steps_with_fn_tool(self, **kwargs):
        """Test running functions with streaming and tracing content recording."""
        await self._do_test_run_steps_with_toolset_with_tracing_content_recording(
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
    @recorded_by_proxy_async
    async def test_telemetry_steps_with_openapi_tool(self, **kwargs):
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
        await self._do_test_run_steps_with_toolset_with_tracing_content_recording(
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
    @recorded_by_proxy_async
    async def test_telemetry_steps_with_mcp_tool(self, **kwargs):
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
        async with self.create_client(**kwargs, by_endpoint=True) as agents_client:
            agent = await agents_client.create_agent(
                model=model,
                name="my-agent",
                instructions=instructions,
                tools=mcp_tool.definitions,
            )
            thread = await agents_client.threads.create()
            try:
                await agents_client.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=message,
                )
                mcp_tool.update_headers("SuperSecret", "123456")
                run = await agents_client.runs.create(
                    thread_id=thread.id, agent_id=agent.id, tool_resources=mcp_tool.resources
                )
                was_approved = False
                while run.status in [RunStatus.QUEUED, RunStatus.IN_PROGRESS, RunStatus.REQUIRES_ACTION]:
                    time.sleep(self._sleep_time())
                    run = await agents_client.runs.get(thread_id=thread.id, run_id=run.id)

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
                            await agents_client.runs.submit_tool_outputs(
                                thread_id=thread.id, run_id=run.id, tool_approvals=tool_approvals
                            )
                assert was_approved, "The run was never approved."
                assert run.status != RunStatus.FAILED, run.last_error

                is_activity_step_found = False
                is_tool_call_step_found = False
                async for run_step in agents_client.run_steps.list(thread_id=thread.id, run_id=run.id):
                    if isinstance(run_step.step_details, RunStepActivityDetails):
                        is_activity_step_found = True
                    if isinstance(run_step.step_details, RunStepToolCallDetails):
                        for tool_call in run_step.step_details.tool_calls:
                            if isinstance(tool_call, RunStepMcpToolCall):
                                is_tool_call_step_found = True
                                break
                assert is_activity_step_found, "RunStepMcpToolCall was not found."
                assert is_tool_call_step_found, "No RunStepMcpToolCall"
                messages = [msg async for msg in agents_client.messages.list(thread_id=thread.id)]
                assert len(messages) > 1
            finally:
                await agents_client.threads.delete(thread.id)
                await agents_client.delete_agent(agent.id)

        self.exporter.force_flush()
        # Check the actual telemetry.
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
    @recorded_by_proxy_async
    async def test_telemetry_steps_with_deep_research_tool(self, **kwargs):
        """Test running functions with streaming and tracing content recording."""
        await self._do_test_run_steps_with_toolset_with_tracing_content_recording(
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
