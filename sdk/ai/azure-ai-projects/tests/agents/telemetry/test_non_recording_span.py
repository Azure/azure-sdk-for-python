# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Tests verifying that instrumentors correctly skip non-recording spans.

When a span is not recording, the instrumentor must not attempt to write
attributes or events to it. These tests use a mock span whose
``is_recording()`` returns False and whose mutation methods raise
``AssertionError`` if called, ensuring the guards work correctly.
"""

import os
import json
import pytest
from unittest.mock import MagicMock, PropertyMock

from azure.ai.projects.telemetry._ai_project_instrumentor import (
    _AIAgentsInstrumentorPreview,
)
from azure.ai.projects.telemetry._responses_instrumentor import (
    _ResponsesInstrumentorPreview,
)


def _make_non_recording_span():
    """Return a mock AbstractSpan wrapping a non-recording OTel span.

    * ``span_instance.is_recording()`` returns ``False``
    * ``span_instance.is_recording`` (the property/method) also returns ``False``
      so the guard correctly skips writes.
    * Any call to ``add_event``, ``set_status``, ``record_exception`` or
      ``set_attribute`` raises ``AssertionError``, catching any code path
      that fails to check ``is_recording()`` properly.
    """
    span_instance = MagicMock()
    span_instance.is_recording = MagicMock(return_value=False)
    span_instance.add_event = MagicMock(side_effect=AssertionError("add_event called on non-recording span"))
    span_instance.set_status = MagicMock(side_effect=AssertionError("set_status called on non-recording span"))
    span_instance.record_exception = MagicMock(
        side_effect=AssertionError("record_exception called on non-recording span")
    )

    span = MagicMock()
    span.span_instance = span_instance
    span.add_attribute = MagicMock(side_effect=AssertionError("add_attribute called on non-recording span"))
    return span


class TestNonRecordingSpanProjectInstrumentor:
    """Verify _AIAgentsInstrumentorPreview skips non-recording spans."""

    def test_add_message_event_skips_non_recording_span(self):
        """_add_message_event should not write to a non-recording span."""
        instrumentor = _AIAgentsInstrumentorPreview()
        span = _make_non_recording_span()

        # This must not raise; the guard should return early.
        instrumentor._add_message_event(span, role="user", content="hello")

    def test_add_instructions_event_skips_non_recording_span(self):
        """_add_instructions_event should not write to a non-recording span."""
        instrumentor = _AIAgentsInstrumentorPreview()
        span = _make_non_recording_span()

        instrumentor._add_instructions_event(span, instructions="Be helpful", additional_instructions=None)

    def test_start_create_agent_span_skips_non_recording_span(self):
        """start_create_agent_span should not write attributes to a non-recording span."""
        instrumentor = _AIAgentsInstrumentorPreview()

        # We need to patch start_span to return our non-recording span
        from unittest.mock import patch

        non_recording_span = _make_non_recording_span()

        with patch(
            "azure.ai.projects.telemetry._ai_project_instrumentor.start_span",
            return_value=non_recording_span,
        ):
            result = instrumentor.start_create_agent_span(
                server_address="test.openai.azure.com",
                port=443,
                model="gpt-4",
                name="test-agent",
                instructions="Be helpful",
            )

        # Should return the span but not have written any attributes/events to it
        assert result is non_recording_span
        non_recording_span.add_attribute.assert_not_called()
        non_recording_span.span_instance.add_event.assert_not_called()


class TestNonRecordingSpanResponsesInstrumentor:
    """Verify _ResponsesInstrumentorPreview skips non-recording spans."""

    def test_set_span_attribute_safe_skips_non_recording_span(self):
        """_set_span_attribute_safe should not write to a non-recording span."""
        instrumentor = _ResponsesInstrumentorPreview()
        span = _make_non_recording_span()

        # This must not raise; the guard should return early.
        instrumentor._set_span_attribute_safe(span, "test.key", "test_value")

    def test_start_responses_span_skips_non_recording_span(self):
        """start_responses_span should not write attributes to a non-recording span."""
        instrumentor = _ResponsesInstrumentorPreview()

        from unittest.mock import patch

        non_recording_span = _make_non_recording_span()

        with patch(
            "azure.ai.projects.telemetry._responses_instrumentor.start_span",
            return_value=non_recording_span,
        ):
            result = instrumentor.start_responses_span(
                server_address="test.openai.azure.com",
                port=443,
                model="gpt-4",
                assistant_name="test-agent",
                conversation_id="conv-123",
                input_text="Hello",
            )

        assert result is non_recording_span
        non_recording_span.add_attribute.assert_not_called()
        non_recording_span.span_instance.add_event.assert_not_called()

    def test_start_create_conversation_span_skips_non_recording_span(self):
        """start_create_conversation_span should not write to a non-recording span."""
        instrumentor = _ResponsesInstrumentorPreview()

        from unittest.mock import patch

        non_recording_span = _make_non_recording_span()

        with patch(
            "azure.ai.projects.telemetry._responses_instrumentor.start_span",
            return_value=non_recording_span,
        ):
            result = instrumentor.start_create_conversation_span(
                server_address="test.openai.azure.com",
                port=443,
            )

        assert result is non_recording_span
        non_recording_span.add_attribute.assert_not_called()
        non_recording_span.span_instance.add_event.assert_not_called()

    def test_start_list_conversation_items_span_skips_non_recording_span(self):
        """start_list_conversation_items_span should not write to a non-recording span."""
        instrumentor = _ResponsesInstrumentorPreview()

        from unittest.mock import patch

        non_recording_span = _make_non_recording_span()

        with patch(
            "azure.ai.projects.telemetry._responses_instrumentor.start_span",
            return_value=non_recording_span,
        ):
            result = instrumentor.start_list_conversation_items_span(
                server_address="test.openai.azure.com",
                port=443,
                conversation_id="conv-123",
            )

        assert result is non_recording_span
        non_recording_span.add_attribute.assert_not_called()
        non_recording_span.span_instance.add_event.assert_not_called()

    def test_add_tool_call_events_skips_non_recording_span(self):
        """_add_tool_call_events should not write to a non-recording span."""
        instrumentor = _ResponsesInstrumentorPreview()
        span = _make_non_recording_span()

        # Create a mock response with function call output
        mock_response = MagicMock()
        mock_output_item = MagicMock()
        mock_output_item.type = "function_call"
        mock_output_item.name = "get_weather"
        mock_output_item.call_id = "call_123"
        mock_output_item.arguments = '{"city": "Seattle"}'
        mock_response.output = [mock_output_item]

        instrumentor._add_tool_call_events(span, mock_response)

    def test_add_conversation_item_event_skips_non_recording_span(self):
        """_add_conversation_item_event should not write to a non-recording span."""
        instrumentor = _ResponsesInstrumentorPreview()
        span = _make_non_recording_span()

        mock_item = MagicMock()
        mock_item.id = "item_123"
        mock_item.type = "message"
        mock_item.role = "user"
        mock_item.content = []

        instrumentor._add_conversation_item_event(span, mock_item)
