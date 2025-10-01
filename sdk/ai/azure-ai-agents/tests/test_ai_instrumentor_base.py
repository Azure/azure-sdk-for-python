# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from enum import IntEnum
from typing import Any, Dict, List, Optional
import json
import os
import pytest

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

from azure.ai.agents.telemetry import AIAgentsInstrumentor

from azure.ai.agents.models import DeepResearchTool

from gen_ai_trace_verifier import GenAiTraceVerifier
from memory_trace_exporter import MemoryTraceExporter
from test_agents_client_base import TestAgentClientBase

CONTENT_TRACING_ENV_VARIABLE = "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"


# We test different ways to create a thread & message, to cover all tracing code paths
class MessageCreationMode(IntEnum):
    MESSAGE_CREATE_STR = (
        1  # Test calls `client.messages.create(content="...", ...)` to create the messages in a dedicated call
    )
    MESSAGE_CREATE_INPUT_TEXT_BLOCK = 2  # Test calls `client.messages.create(content=[MessageInputTextBlock(...)], ...)` to create the message in a dedicated call
    THREAD_CREATE_STR = 3  # Test calls `client.threads.create(messages=[ThreadMessageOptions(...)])`.
    THREAD_CREATE_INPUT_TEXT_BLOCK = (
        4  # Test calls `client.threads.create(messages=[ThreadMessageOptions(content=[MessageInputTextBlock(...)])])`.
    )


class TestAiAgentsInstrumentorBase(TestAgentClientBase):
    """The utility methods, used by AI Instrumentor test."""

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

    def _get_deep_research_tool(self, **kwargs):
        """Get deep research tool."""
        bing_conn_id = kwargs.pop("azure_ai_agents_tests_bing_connection_id")
        deep_research_model = kwargs.pop("azure_ai_agents_tests_deep_research_model")

        # Create DeepResearchTool
        return DeepResearchTool(
            bing_grounding_connection_id=bing_conn_id,
            deep_research_model=deep_research_model,
        )

    def _check_spans(
        self,
        model: str,
        recording_enabled: bool,
        instructions: str,
        message: str,
        have_submit_tools: bool,
        use_stream: bool,
        tool_message_attribute_content: str,
        event_contents: List[str],
        run_step_events: Optional[List[List[Dict[str, Any]]]] = None,
        has_annotations: bool = False,
    ):
        """Check the spans for correctness."""
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
                expected_attributes.extend([("gen_ai.thread.run.status", ""), ("gen_ai.response.model", model)])

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
        assert len(spans) >= 2
        span = spans[0]
        expected_attributes = [
            ("gen_ai.system", "az.ai.agents"),
            ("gen_ai.operation.name", "list_messages"),
            ("server.address", ""),
            ("gen_ai.thread.id", ""),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        if recording_enabled:
            if has_annotations:
                content = '{"content": {"text": {"value": "*", "annotations": "*"}}, "role": "assistant"}'
            else:
                content = '{"content": {"text": {"value": "*"}}, "role": "assistant"}'
        else:
            content = '{"role": "assistant"}'
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

        span = spans[-1]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        content = (
            f'{{"content": {{"text": {{"value": "{message}"}}}}, "role": "user"}}'
            if recording_enabled
            else '{"role": "user"}'
        )
        expected_events = [
            {
                "name": "gen_ai.user.message",
                "attributes": {
                    "gen_ai.system": "az.ai.agents",
                    "gen_ai.thread.id": "*",
                    "gen_ai.message.id": "*",
                    "gen_ai.event.content": content,
                },
            },
        ]
        events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
        assert events_match == True

        spans = self.exporter.get_spans_by_name("list_run_steps")
        if run_step_events:
            expected_attributes = [
                ("gen_ai.system", "az.ai.agents"),
                ("gen_ai.operation.name", "list_run_steps"),
                ("server.address", ""),
                ("gen_ai.thread.id", ""),
                ("gen_ai.thread.run.id", ""),
            ]
            if len(spans) < 5:
                assert len(spans) == len(run_step_events)
                zip_obj = zip(spans, run_step_events)
            else:
                assert len(run_step_events) == 5
                # If it is deep research there may be multiple run steps.
                zip_obj = zip(spans[:3] + spans[-2:], run_step_events)
            for span, expected_span_events in zip_obj:
                attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
                assert attributes_match == True
                events_match = GenAiTraceVerifier().check_span_events(span, expected_span_events)
                assert events_match == True
        else:
            assert spans == []

    def get_expected_fn_spans(self, recording_enabled: bool) -> List[List[Dict[str, Any]]]:
        """Get the expected run steps for functions."""
        expected_spans = [
            [
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
        ]
        expected_event_content = (
            '{"tool_calls": [{"id": "*", "type": "function", "function": {"name": "fetch_weather", "arguments": {"location": "New York"}}}]}'
            if recording_enabled
            else '{"tool_calls": [{"id": "*", "type": "function"}]}'
        )
        expected_spans.append(
            [
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
                        "gen_ai.event.content": expected_event_content,
                    },
                },
            ]
        )
        return expected_spans

    def get_expected_openapi_spans(self):
        expected_spans = [
            [
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
        ]
        expected_spans.append(
            [
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
                        "gen_ai.event.content": '{"tool_calls": [{"id": "*", "type": "openapi", "function": {"name": "get_weather_GetCurrentWeather", "arguments": "*", "output": "*"}}]}',
                    },
                },
            ]
        )
        return expected_spans

    def get_expected_mcp_spans(self):
        """Get spans for the MCP tool call."""
        expected_event_content = json.dumps(
            {
                "tool_calls": [
                    {
                        "id": "*",
                        "type": "mcp",
                        "arguments": json.dumps({"query": "Readme", "page": 1}),
                        "name": "search_azure_rest_api_code",
                        "output": "*",
                        "server_label": "github",
                    }
                ]
            }
        )

        expected_spans = [
            [
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
        ]
        expected_spans.append(
            [
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
                        "gen_ai.event.content": expected_event_content,
                    },
                },
            ]
        )
        expected_spans.append([])
        return expected_spans

    def get_expected_deep_research_spans(self):
        expected_event_content = json.dumps(
            {
                "tool_calls": [
                    {
                        "id": "*",
                        "type": "deep_research",
                        "deep_research": {"input": "*", "output": "*"},
                    }
                ]
            }
        )

        expected_spans = [
            [
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
                        "gen_ai.usage.input_tokens": 0,
                        "gen_ai.usage.output_tokens": 0,
                    },
                },
            ]
        ] * 4
        expected_spans.append(
            [
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
                        "gen_ai.event.content": expected_event_content,
                    },
                },
            ]
        )
        return expected_spans
