# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import unittest
from unittest.mock import MagicMock, patch

from opentelemetry import trace as trace_api
from opentelemetry.attributes import BoundedAttributes
from opentelemetry.context import Context
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import INVALID_SPAN_CONTEXT, SpanContext, TraceFlags

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

    def test_on_start_propagates_to_child_with_none_parent_context(self):
        """Regression: child spans start with parent_context=None and must still
        inherit main_agent context from the active parent.

        Child LLM/chat spans are created with parent_context=None and rely on
        get_current_span(None) resolving the active invoke_agent span. Propagation
        must not be gated on parent_context being non-None.
        """
        span = MagicMock()
        parent_span = MagicMock()
        parent_span.get_span_context.return_value = SpanContext(
            trace_id=1, span_id=2, is_remote=False, trace_flags=TraceFlags(1)
        )
        parent_span.attributes = {
            "microsoft.gen_ai.main_agent.name": "MainAgent",
            "microsoft.gen_ai.main_agent.id": "agent-123",
        }

        with patch(
            "azure.monitor.opentelemetry.exporter._gen_ai._processor.get_current_span",
            return_value=parent_span,
        ) as get_current_span_mock:
            self.processor.on_start(span, parent_context=None)

        # get_current_span(None) is used to resolve the active parent.
        get_current_span_mock.assert_called_once_with(None)
        span.set_attribute.assert_any_call("microsoft.gen_ai.main_agent.name", "MainAgent")
        span.set_attribute.assert_any_call("microsoft.gen_ai.main_agent.id", "agent-123")

    def test_on_start_propagation_cascades_through_subtree(self):
        """main_agent context should cascade to every span in the subtree.

        Because on_start copies the parent's microsoft.gen_ai.main_agent.* onto the
        child, a grandchild resolving its (already-attributed) parent inherits the
        same main-agent identity, keeping the whole subtree attributed to the root.
        """
        # Level 1: child resolves the root invoke_agent span (self-attributed).
        root_span = MagicMock()
        root_span.get_span_context.return_value = SpanContext(
            trace_id=1, span_id=1, is_remote=False, trace_flags=TraceFlags(1)
        )
        root_span.attributes = {
            "microsoft.gen_ai.main_agent.name": "MainAgent",
            "microsoft.gen_ai.main_agent.id": "agent-123",
        }

        child_span = MagicMock()
        child_attrs = {}
        child_span.set_attribute.side_effect = lambda k, v: child_attrs.__setitem__(k, v)

        with patch(
            "azure.monitor.opentelemetry.exporter._gen_ai._processor.get_current_span",
            return_value=root_span,
        ):
            self.processor.on_start(child_span, parent_context=None)

        self.assertEqual(child_attrs["microsoft.gen_ai.main_agent.name"], "MainAgent")
        self.assertEqual(child_attrs["microsoft.gen_ai.main_agent.id"], "agent-123")

        # Level 2: grandchild resolves the now-attributed child span and inherits
        # the same main-agent identity.
        child_span.attributes = child_attrs
        grandchild_span = MagicMock()
        grandchild_attrs = {}
        grandchild_span.set_attribute.side_effect = lambda k, v: grandchild_attrs.__setitem__(k, v)

        with patch(
            "azure.monitor.opentelemetry.exporter._gen_ai._processor.get_current_span",
            return_value=child_span,
        ):
            self.processor.on_start(grandchild_span, parent_context=None)

        self.assertEqual(grandchild_attrs["microsoft.gen_ai.main_agent.name"], "MainAgent")
        self.assertEqual(grandchild_attrs["microsoft.gen_ai.main_agent.id"], "agent-123")


class TestGenAIMainAgentSpanProcessorOnEnd(unittest.TestCase):
    def setUp(self):
        self.processor = _GenAIMainAgentSpanProcessor()

    def test_on_end_no_attributes(self):
        """on_end should no-op when span has no attributes."""
        span = MagicMock()
        span.attributes = None
        self.processor.on_end(span)

    def test_on_end_cleans_up_parent_ref_even_without_attributes(self):
        """on_end must drop the stored parent reference even on the early-return
        path where span.attributes is None, so the map does not leak entries."""
        span_id = 12345
        parent_span = MagicMock()
        self.processor._parent_spans[span_id] = parent_span

        span = MagicMock()
        span.attributes = None
        span.context.span_id = span_id

        self.processor.on_end(span)

        self.assertNotIn(span_id, self.processor._parent_spans)

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

    def test_on_end_writes_to_immutable_attributes(self):
        """on_end must self-attribute even when span attributes are frozen.

        OTel SDK >= 1.43 sets BoundedAttributes._immutable = True inside
        Span.end() *before* invoking on_end. The processor must temporarily lift
        the freeze to write and restore it afterwards, without raising.
        """
        attributes = BoundedAttributes(
            immutable=False,
            attributes={
                "gen_ai.operation.name": "invoke_agent",
                "gen_ai.agent.name": "RootAgent",
                "gen_ai.agent.id": "agent-001",
                "gen_ai.agent.version": "3.0",
                "gen_ai.conversation.id": "conv-xyz",
            },
        )
        # Simulate the frozen state Span.end() leaves the attributes in.
        attributes._immutable = True

        span = MagicMock()
        span.attributes = attributes
        span._attributes = attributes

        # Must not raise even though the mapping is immutable.
        self.processor.on_end(span)

        self.assertEqual(attributes["microsoft.gen_ai.main_agent.name"], "RootAgent")
        self.assertEqual(attributes["microsoft.gen_ai.main_agent.id"], "agent-001")
        self.assertEqual(attributes["microsoft.gen_ai.main_agent.version"], "3.0")
        self.assertEqual(attributes["microsoft.gen_ai.main_agent.conversation_id"], "conv-xyz")
        # The freeze must be restored so the exported snapshot stays immutable.
        self.assertTrue(attributes._immutable)

    def test_immutable_attributes_reject_direct_write(self):
        """Regression guard: proves the failure the fix guards against.

        A direct write to frozen BoundedAttributes (the pre-fix behavior)
        raises TypeError. This is why on_end must lift the freeze first.
        """
        attributes = BoundedAttributes(immutable=False, attributes={})
        attributes._immutable = True
        with self.assertRaises(TypeError):
            attributes["microsoft.gen_ai.main_agent.name"] = "RootAgent"


class TestGenAIMainAgentSpanProcessorSDKPropagation(unittest.TestCase):
    """Real-SDK propagation tests using a TracerProvider + InMemorySpanExporter.

    These exercise the full on_start/on_end flow against real OTel SDK spans
    (with frozen attributes on end), catching timing and immutability issues
    that mock-based tests cannot detect.
    """

    def setUp(self):
        self.exporter = InMemorySpanExporter()
        self.provider = TracerProvider()
        # Main-agent processor FIRST so on_start enriches before export.
        self.provider.add_span_processor(_GenAIMainAgentSpanProcessor())
        self.provider.add_span_processor(SimpleSpanProcessor(self.exporter))
        self.tracer = self.provider.get_tracer("test")

    def tearDown(self):
        self.provider.shutdown()

    def _get_exported_spans(self):
        return {s.name: s for s in self.exporter.get_finished_spans()}

    def test_invoke_agent_propagates_to_chat_span(self):
        """invoke_agent (with gen_ai.agent.*) -> chat child:
        child must have microsoft.gen_ai.main_agent.* attrs."""
        root_ctx = trace_api.set_span_in_context(trace_api.INVALID_SPAN)
        agent_span = self.tracer.start_span("invoke_agent TravelBot", context=root_ctx)
        agent_span.set_attribute("gen_ai.operation.name", "invoke_agent")
        agent_span.set_attribute("gen_ai.agent.name", "TravelBot")
        agent_span.set_attribute("gen_ai.agent.id", "agent-1")
        agent_span.set_attribute("gen_ai.agent.version", "2.0")
        agent_span.set_attribute("gen_ai.conversation.id", "conv-1")

        chat_ctx = trace_api.set_span_in_context(agent_span)
        chat_span = self.tracer.start_span("chat gpt-4", context=chat_ctx)
        chat_span.end()
        agent_span.end()

        spans = self._get_exported_spans()
        chat = spans["chat gpt-4"]
        self.assertEqual(chat.attributes.get("microsoft.gen_ai.main_agent.name"), "TravelBot")
        self.assertEqual(chat.attributes.get("microsoft.gen_ai.main_agent.id"), "agent-1")
        self.assertEqual(chat.attributes.get("microsoft.gen_ai.main_agent.version"), "2.0")
        self.assertEqual(chat.attributes.get("microsoft.gen_ai.main_agent.conversation_id"), "conv-1")

    def test_invoke_agent_propagates_to_tool_span(self):
        """invoke_agent -> execute_tool child:
        tool span must have microsoft.gen_ai.main_agent.* attrs."""
        root_ctx = trace_api.set_span_in_context(trace_api.INVALID_SPAN)
        agent_span = self.tracer.start_span("invoke_agent TravelBot", context=root_ctx)
        agent_span.set_attribute("gen_ai.operation.name", "invoke_agent")
        agent_span.set_attribute("gen_ai.agent.name", "TravelBot")
        agent_span.set_attribute("gen_ai.agent.id", "agent-1")

        tool_ctx = trace_api.set_span_in_context(agent_span)
        tool_span = self.tracer.start_span("execute_tool get_weather", context=tool_ctx)
        tool_span.end()
        agent_span.end()

        spans = self._get_exported_spans()
        tool = spans["execute_tool get_weather"]
        self.assertEqual(tool.attributes.get("microsoft.gen_ai.main_agent.name"), "TravelBot")
        self.assertEqual(tool.attributes.get("microsoft.gen_ai.main_agent.id"), "agent-1")

    def test_propagation_cascades_through_nested_subtree(self):
        """invoke_agent -> wrapper -> inner -> chat:
        main_agent attrs must propagate through the entire chain."""
        root_ctx = trace_api.set_span_in_context(trace_api.INVALID_SPAN)
        agent_span = self.tracer.start_span("invoke_agent TravelBot", context=root_ctx)
        agent_span.set_attribute("gen_ai.operation.name", "invoke_agent")
        agent_span.set_attribute("gen_ai.agent.name", "TravelBot")
        agent_span.set_attribute("gen_ai.agent.id", "agent-1")

        wrapper = self.tracer.start_span("wrapper", context=trace_api.set_span_in_context(agent_span))
        inner = self.tracer.start_span("inner", context=trace_api.set_span_in_context(wrapper))
        chat = self.tracer.start_span("chat gpt-4", context=trace_api.set_span_in_context(inner))
        chat.end()
        inner.end()
        wrapper.end()
        agent_span.end()

        spans = self._get_exported_spans()
        for name in ("wrapper", "inner", "chat gpt-4"):
            self.assertEqual(
                spans[name].attributes.get("microsoft.gen_ai.main_agent.name"),
                "TravelBot",
                f"{name} should inherit main_agent.name",
            )
            self.assertEqual(spans[name].attributes.get("microsoft.gen_ai.main_agent.id"), "agent-1")

    def test_multi_agent_preserves_main_agent_over_sub_agent(self):
        """main_agent -> sub_agent -> chat:
        sub_agent has its own gen_ai.agent.* but the MAIN agent's
        microsoft.gen_ai.main_agent.* must be preserved on the grandchild."""
        root_ctx = trace_api.set_span_in_context(trace_api.INVALID_SPAN)
        main_agent = self.tracer.start_span("invoke_agent MainAgent", context=root_ctx)
        main_agent.set_attribute("gen_ai.operation.name", "invoke_agent")
        main_agent.set_attribute("gen_ai.agent.name", "MainAgent")
        main_agent.set_attribute("gen_ai.agent.id", "main-1")

        sub_agent = self.tracer.start_span("invoke_agent SubAgent", context=trace_api.set_span_in_context(main_agent))
        sub_agent.set_attribute("gen_ai.operation.name", "invoke_agent")
        sub_agent.set_attribute("gen_ai.agent.name", "SubAgent")
        sub_agent.set_attribute("gen_ai.agent.id", "sub-1")

        chat = self.tracer.start_span("chat gpt-4", context=trace_api.set_span_in_context(sub_agent))
        chat.end()
        sub_agent.end()
        main_agent.end()

        spans = self._get_exported_spans()
        # The grandchild is attributed to the MAIN agent, not the sub-agent.
        self.assertEqual(spans["chat gpt-4"].attributes.get("microsoft.gen_ai.main_agent.name"), "MainAgent")
        self.assertEqual(spans["chat gpt-4"].attributes.get("microsoft.gen_ai.main_agent.id"), "main-1")

    def test_propagation_to_sibling_spans(self):
        """invoke_agent -> [chat, tool]: both siblings get main_agent attrs."""
        root_ctx = trace_api.set_span_in_context(trace_api.INVALID_SPAN)
        agent_span = self.tracer.start_span("invoke_agent TravelBot", context=root_ctx)
        agent_span.set_attribute("gen_ai.operation.name", "invoke_agent")
        agent_span.set_attribute("gen_ai.agent.name", "TravelBot")
        agent_span.set_attribute("gen_ai.agent.id", "agent-1")

        agent_ctx = trace_api.set_span_in_context(agent_span)
        chat = self.tracer.start_span("chat gpt-4", context=agent_ctx)
        chat.end()
        tool = self.tracer.start_span("execute_tool get_weather", context=agent_ctx)
        tool.end()
        agent_span.end()

        spans = self._get_exported_spans()
        for name in ("chat gpt-4", "execute_tool get_weather"):
            self.assertEqual(spans[name].attributes.get("microsoft.gen_ai.main_agent.name"), "TravelBot")
            self.assertEqual(spans[name].attributes.get("microsoft.gen_ai.main_agent.id"), "agent-1")

    def test_non_agent_parent_does_not_propagate(self):
        """A chat span without gen_ai.agent.* on the parent should not inject main_agent attrs."""
        root_ctx = trace_api.set_span_in_context(trace_api.INVALID_SPAN)
        parent = self.tracer.start_span("chat gpt-4", context=root_ctx)
        parent.set_attribute("gen_ai.operation.name", "chat")

        child = self.tracer.start_span("chat child", context=trace_api.set_span_in_context(parent))
        child.end()
        parent.end()

        spans = self._get_exported_spans()
        for key in spans["chat child"].attributes:
            self.assertFalse(key.startswith("microsoft.gen_ai.main_agent."))

    def test_attrs_set_after_child_creation_recovered_on_end(self):
        """If agent attributes are set AFTER creating the child span, on_start
        cannot propagate them -- but on_end fallback re-reads from the (now
        enriched) parent and fills in the gap."""
        root_ctx = trace_api.set_span_in_context(trace_api.INVALID_SPAN)
        agent_span = self.tracer.start_span("invoke_agent TravelBot", context=root_ctx)
        agent_span.set_attribute("gen_ai.operation.name", "invoke_agent")

        # Create the child BEFORE the parent's agent attributes are set.
        chat_span = self.tracer.start_span("chat gpt-4", context=trace_api.set_span_in_context(agent_span))

        # Now populate the parent's agent attributes (missed by on_start).
        agent_span.set_attribute("gen_ai.agent.name", "TravelBot")
        agent_span.set_attribute("gen_ai.agent.id", "agent-1")

        chat_span.end()
        agent_span.end()

        spans = self._get_exported_spans()
        self.assertEqual(
            spans["chat gpt-4"].attributes.get("microsoft.gen_ai.main_agent.name"),
            "TravelBot",
            "on_end fallback should recover propagation from the parent",
        )
        self.assertEqual(spans["chat gpt-4"].attributes.get("microsoft.gen_ai.main_agent.id"), "agent-1")

    def test_root_invoke_agent_self_promotes_on_end(self):
        """A root invoke_agent span with no parent must self-promote its
        gen_ai.agent.* to microsoft.gen_ai.main_agent.* on end."""
        root_ctx = trace_api.set_span_in_context(trace_api.INVALID_SPAN)
        agent = self.tracer.start_span("invoke_agent TravelBot", context=root_ctx)
        agent.set_attribute("gen_ai.operation.name", "invoke_agent")
        agent.set_attribute("gen_ai.agent.name", "TravelBot")
        agent.set_attribute("gen_ai.agent.id", "agent-1")
        agent.set_attribute("gen_ai.agent.version", "2.0")
        agent.set_attribute("gen_ai.conversation.id", "conv-1")
        agent.end()

        spans = self._get_exported_spans()
        exported = spans["invoke_agent TravelBot"]
        self.assertEqual(exported.attributes.get("microsoft.gen_ai.main_agent.name"), "TravelBot")
        self.assertEqual(exported.attributes.get("microsoft.gen_ai.main_agent.id"), "agent-1")
        self.assertEqual(exported.attributes.get("microsoft.gen_ai.main_agent.version"), "2.0")
        self.assertEqual(exported.attributes.get("microsoft.gen_ai.main_agent.conversation_id"), "conv-1")

    def test_self_promotion_only_for_invoke_agent(self):
        """Non-invoke_agent root spans must NOT self-promote."""
        root_ctx = trace_api.set_span_in_context(trace_api.INVALID_SPAN)
        chat = self.tracer.start_span("chat gpt-4", context=root_ctx)
        chat.set_attribute("gen_ai.operation.name", "chat")
        chat.set_attribute("gen_ai.agent.name", "SomeAgent")
        chat.end()

        spans = self._get_exported_spans()
        for key in spans["chat gpt-4"].attributes:
            self.assertFalse(key.startswith("microsoft.gen_ai.main_agent."))


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
