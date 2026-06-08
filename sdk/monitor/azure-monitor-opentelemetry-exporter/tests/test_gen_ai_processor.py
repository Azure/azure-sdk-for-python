# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import unittest
from unittest.mock import MagicMock, patch

from opentelemetry.context import Context
from opentelemetry.trace import INVALID_SPAN_CONTEXT, SpanContext, TraceFlags

from azure.monitor.opentelemetry.exporter._constants import (
    _MAIN_AGENT_ATTRIBUTES,
    _MAIN_AGENT_PREFIX,
    _MAIN_AGENT_SELF_ATTRIBUTES,
)
from azure.monitor.opentelemetry.exporter._gen_ai._processor import (
    _GenAIMainAgentLogRecordProcessor,
    _GenAIMainAgentSpanProcessor,
)


class TestGenAIMainAgentSpanProcessorOnStart(unittest.TestCase):
    def setUp(self):
        self.processor = _GenAIMainAgentSpanProcessor()

    def test_on_start_no_parent_context(self):
        """on_start should no-op when parent_context is None."""
        span = MagicMock()
        self.processor.on_start(span, parent_context=None)
        span.set_attribute.assert_not_called()

    def test_on_start_invalid_parent_span(self):
        """on_start should no-op when parent span context is invalid."""
        span = MagicMock()
        parent_span = MagicMock()
        parent_span.get_span_context.return_value = INVALID_SPAN_CONTEXT
        parent_context = MagicMock(spec=Context)

        with patch(
            "azure.monitor.opentelemetry.exporter._gen_ai._processor.get_current_span",
            return_value=parent_span,
        ):
            self.processor.on_start(span, parent_context=parent_context)

        span.set_attribute.assert_not_called()

    def test_on_start_propagates_primary_source(self):
        """on_start should copy microsoft.gen_ai.main_agent.* from parent (primary source)."""
        span = MagicMock()
        parent_span = MagicMock()
        parent_span.get_span_context.return_value = SpanContext(
            trace_id=1, span_id=2, is_remote=False, trace_flags=TraceFlags(1)
        )
        parent_span.attributes = {
            "microsoft.gen_ai.main_agent.name": "MainAgent",
            "microsoft.gen_ai.main_agent.id": "agent-123",
            "microsoft.gen_ai.main_agent.version": "1.0",
            "microsoft.gen_ai.main_agent.conversation_id": "conv-456",
        }
        parent_context = MagicMock(spec=Context)

        with patch(
            "azure.monitor.opentelemetry.exporter._gen_ai._processor.get_current_span",
            return_value=parent_span,
        ):
            self.processor.on_start(span, parent_context=parent_context)

        span.set_attribute.assert_any_call("microsoft.gen_ai.main_agent.name", "MainAgent")
        span.set_attribute.assert_any_call("microsoft.gen_ai.main_agent.id", "agent-123")
        span.set_attribute.assert_any_call("microsoft.gen_ai.main_agent.version", "1.0")
        span.set_attribute.assert_any_call("microsoft.gen_ai.main_agent.conversation_id", "conv-456")

    def test_on_start_propagates_fallback_source(self):
        """on_start should use gen_ai.agent.* as fallback when primary not present."""
        span = MagicMock()
        parent_span = MagicMock()
        parent_span.get_span_context.return_value = SpanContext(
            trace_id=1, span_id=2, is_remote=False, trace_flags=TraceFlags(1)
        )
        parent_span.attributes = {
            "gen_ai.agent.name": "RootAgent",
            "gen_ai.agent.id": "root-789",
            "gen_ai.agent.version": "2.0",
            "gen_ai.conversation.id": "conv-101",
        }
        parent_context = MagicMock(spec=Context)

        with patch(
            "azure.monitor.opentelemetry.exporter._gen_ai._processor.get_current_span",
            return_value=parent_span,
        ):
            self.processor.on_start(span, parent_context=parent_context)

        span.set_attribute.assert_any_call("microsoft.gen_ai.main_agent.name", "RootAgent")
        span.set_attribute.assert_any_call("microsoft.gen_ai.main_agent.id", "root-789")
        span.set_attribute.assert_any_call("microsoft.gen_ai.main_agent.version", "2.0")
        span.set_attribute.assert_any_call("microsoft.gen_ai.main_agent.conversation_id", "conv-101")

    def test_on_start_primary_takes_precedence_over_fallback(self):
        """on_start should prefer primary source over fallback."""
        span = MagicMock()
        parent_span = MagicMock()
        parent_span.get_span_context.return_value = SpanContext(
            trace_id=1, span_id=2, is_remote=False, trace_flags=TraceFlags(1)
        )
        parent_span.attributes = {
            "microsoft.gen_ai.main_agent.name": "MainAgent",
            "gen_ai.agent.name": "SubAgent",
            "gen_ai.agent.id": "sub-999",
        }
        parent_context = MagicMock(spec=Context)

        with patch(
            "azure.monitor.opentelemetry.exporter._gen_ai._processor.get_current_span",
            return_value=parent_span,
        ):
            self.processor.on_start(span, parent_context=parent_context)

        # Primary source takes precedence for name
        span.set_attribute.assert_any_call("microsoft.gen_ai.main_agent.name", "MainAgent")
        # Fallback used for id (no primary source present)
        span.set_attribute.assert_any_call("microsoft.gen_ai.main_agent.id", "sub-999")

    def test_on_start_no_attributes_on_parent(self):
        """on_start should no-op when parent has no relevant attributes."""
        span = MagicMock()
        parent_span = MagicMock()
        parent_span.get_span_context.return_value = SpanContext(
            trace_id=1, span_id=2, is_remote=False, trace_flags=TraceFlags(1)
        )
        parent_span.attributes = {"http.method": "GET"}
        parent_context = MagicMock(spec=Context)

        with patch(
            "azure.monitor.opentelemetry.exporter._gen_ai._processor.get_current_span",
            return_value=parent_span,
        ):
            self.processor.on_start(span, parent_context=parent_context)

        span.set_attribute.assert_not_called()

    def test_on_start_parent_has_no_attributes_property(self):
        """on_start should no-op when parent span has no attributes."""
        span = MagicMock()
        parent_span = MagicMock(spec=[])  # No attributes at all
        parent_span.get_span_context = MagicMock(
            return_value=SpanContext(trace_id=1, span_id=2, is_remote=False, trace_flags=TraceFlags(1))
        )
        parent_context = MagicMock(spec=Context)

        with patch(
            "azure.monitor.opentelemetry.exporter._gen_ai._processor.get_current_span",
            return_value=parent_span,
        ):
            self.processor.on_start(span, parent_context=parent_context)

        span.set_attribute.assert_not_called()


class TestGenAIMainAgentSpanProcessorOnEnd(unittest.TestCase):
    def setUp(self):
        self.processor = _GenAIMainAgentSpanProcessor()

    def test_on_end_no_attributes(self):
        """on_end should no-op when span has no attributes."""
        span = MagicMock()
        span.attributes = None
        self.processor.on_end(span)

    def test_on_end_not_invoke_agent(self):
        """on_end should no-op when gen_ai.operation.name is not invoke_agent."""
        span = MagicMock()
        span.attributes = {"gen_ai.operation.name": "chat"}
        span._attributes = {}
        self.processor.on_end(span)
        self.assertEqual(span._attributes, {})

    def test_on_end_no_operation_name(self):
        """on_end should no-op when gen_ai.operation.name is missing."""
        span = MagicMock()
        span.attributes = {"gen_ai.agent.name": "Agent1"}
        span._attributes = {}
        self.processor.on_end(span)
        self.assertEqual(span._attributes, {})

    def test_on_end_already_has_main_agent_attributes(self):
        """on_end should no-op when span already has microsoft.gen_ai.main_agent.* attrs."""
        span = MagicMock()
        span.attributes = {
            "gen_ai.operation.name": "invoke_agent",
            "microsoft.gen_ai.main_agent.name": "AlreadySet",
            "gen_ai.agent.name": "Agent1",
        }
        span._attributes = dict(span.attributes)
        self.processor.on_end(span)
        # Should not have been changed
        self.assertEqual(span._attributes.get("microsoft.gen_ai.main_agent.name"), "AlreadySet")

    def test_on_end_self_attributes_invoke_agent(self):
        """on_end should self-attribute root invoke_agent spans."""
        span = MagicMock()
        span.attributes = {
            "gen_ai.operation.name": "invoke_agent",
            "gen_ai.agent.name": "RootAgent",
            "gen_ai.agent.id": "agent-001",
            "gen_ai.agent.version": "3.0",
            "gen_ai.conversation.id": "conv-xyz",
        }
        span._attributes = dict(span.attributes)
        self.processor.on_end(span)
        self.assertEqual(span._attributes["microsoft.gen_ai.main_agent.name"], "RootAgent")
        self.assertEqual(span._attributes["microsoft.gen_ai.main_agent.id"], "agent-001")
        self.assertEqual(span._attributes["microsoft.gen_ai.main_agent.version"], "3.0")
        self.assertEqual(span._attributes["microsoft.gen_ai.main_agent.conversation_id"], "conv-xyz")

    def test_on_end_partial_self_attribution(self):
        """on_end should only copy attributes that exist on the span."""
        span = MagicMock()
        span.attributes = {
            "gen_ai.operation.name": "invoke_agent",
            "gen_ai.agent.name": "PartialAgent",
        }
        span._attributes = dict(span.attributes)
        self.processor.on_end(span)
        self.assertEqual(span._attributes["microsoft.gen_ai.main_agent.name"], "PartialAgent")
        self.assertNotIn("microsoft.gen_ai.main_agent.id", span._attributes)
        self.assertNotIn("microsoft.gen_ai.main_agent.version", span._attributes)
        self.assertNotIn("microsoft.gen_ai.main_agent.conversation_id", span._attributes)


class TestGenAIMainAgentLogRecordProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = _GenAIMainAgentLogRecordProcessor()

    def test_on_emit_no_current_span(self):
        """on_emit should no-op when there is no valid current span."""
        log_record = MagicMock()
        invalid_span = MagicMock()
        invalid_span.get_span_context.return_value = INVALID_SPAN_CONTEXT

        with patch(
            "azure.monitor.opentelemetry.exporter._gen_ai._processor.get_current_span",
            return_value=invalid_span,
        ):
            self.processor.on_emit(log_record)

    def test_on_emit_span_has_no_main_agent_attributes(self):
        """on_emit should no-op when span has no microsoft.gen_ai.main_agent.* attributes."""
        log_record = MagicMock()
        current_span = MagicMock()
        current_span.get_span_context.return_value = SpanContext(
            trace_id=1, span_id=2, is_remote=False, trace_flags=TraceFlags(1)
        )
        current_span.attributes = {"http.method": "GET"}

        with patch(
            "azure.monitor.opentelemetry.exporter._gen_ai._processor.get_current_span",
            return_value=current_span,
        ):
            self.processor.on_emit(log_record)

    def test_on_emit_copies_main_agent_attributes_to_log_record(self):
        """on_emit should copy microsoft.gen_ai.main_agent.* from span to log record."""
        log_record = MagicMock()
        log_record.log_record = MagicMock()
        log_record.log_record.attributes = {}

        current_span = MagicMock()
        current_span.get_span_context.return_value = SpanContext(
            trace_id=1, span_id=2, is_remote=False, trace_flags=TraceFlags(1)
        )
        current_span.attributes = {
            "microsoft.gen_ai.main_agent.name": "MainAgent",
            "microsoft.gen_ai.main_agent.id": "agent-123",
            "microsoft.gen_ai.main_agent.version": "1.0",
            "microsoft.gen_ai.main_agent.conversation_id": "conv-456",
            "other.attribute": "should_not_be_copied",
        }

        with patch(
            "azure.monitor.opentelemetry.exporter._gen_ai._processor.get_current_span",
            return_value=current_span,
        ):
            self.processor.on_emit(log_record)

        self.assertEqual(log_record.log_record.attributes["microsoft.gen_ai.main_agent.name"], "MainAgent")
        self.assertEqual(log_record.log_record.attributes["microsoft.gen_ai.main_agent.id"], "agent-123")
        self.assertEqual(log_record.log_record.attributes["microsoft.gen_ai.main_agent.version"], "1.0")
        self.assertEqual(log_record.log_record.attributes["microsoft.gen_ai.main_agent.conversation_id"], "conv-456")
        self.assertNotIn("other.attribute", log_record.log_record.attributes)

    def test_on_emit_creates_attributes_dict_if_none(self):
        """on_emit should initialize attributes dict if None."""
        log_record = MagicMock()
        log_record.log_record = MagicMock()
        log_record.log_record.attributes = None

        current_span = MagicMock()
        current_span.get_span_context.return_value = SpanContext(
            trace_id=1, span_id=2, is_remote=False, trace_flags=TraceFlags(1)
        )
        current_span.attributes = {
            "microsoft.gen_ai.main_agent.name": "TestAgent",
        }

        with patch(
            "azure.monitor.opentelemetry.exporter._gen_ai._processor.get_current_span",
            return_value=current_span,
        ):
            self.processor.on_emit(log_record)

        self.assertEqual(log_record.log_record.attributes["microsoft.gen_ai.main_agent.name"], "TestAgent")

    def test_on_emit_does_not_overwrite_existing_log_record_attributes(self):
        """on_emit should not overwrite existing microsoft.gen_ai.main_agent.* on the log record."""
        log_record = MagicMock()
        log_record.log_record = MagicMock()
        log_record.log_record.attributes = {
            "microsoft.gen_ai.main_agent.name": "ExistingAgent",
        }

        current_span = MagicMock()
        current_span.get_span_context.return_value = SpanContext(
            trace_id=1, span_id=2, is_remote=False, trace_flags=TraceFlags(1)
        )
        current_span.attributes = {
            "microsoft.gen_ai.main_agent.name": "SpanAgent",
            "microsoft.gen_ai.main_agent.id": "span-id-123",
        }

        with patch(
            "azure.monitor.opentelemetry.exporter._gen_ai._processor.get_current_span",
            return_value=current_span,
        ):
            self.processor.on_emit(log_record)

        # Existing value should not be overwritten
        self.assertEqual(log_record.log_record.attributes["microsoft.gen_ai.main_agent.name"], "ExistingAgent")
        # Missing value should be populated
        self.assertEqual(log_record.log_record.attributes["microsoft.gen_ai.main_agent.id"], "span-id-123")

    def test_on_emit_span_has_no_attributes(self):
        """on_emit should no-op when span has no attributes property."""
        log_record = MagicMock()
        current_span = MagicMock(spec=[])
        current_span.get_span_context = MagicMock(
            return_value=SpanContext(trace_id=1, span_id=2, is_remote=False, trace_flags=TraceFlags(1))
        )

        with patch(
            "azure.monitor.opentelemetry.exporter._gen_ai._processor.get_current_span",
            return_value=current_span,
        ):
            self.processor.on_emit(log_record)


if __name__ == "__main__":
    unittest.main()
