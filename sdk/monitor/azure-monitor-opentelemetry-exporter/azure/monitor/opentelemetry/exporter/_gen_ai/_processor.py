# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Optional

from opentelemetry.context import Context
from opentelemetry.sdk._logs import LogRecordProcessor, ReadWriteLogRecord
from opentelemetry.sdk.trace import ReadableSpan, SpanProcessor
from opentelemetry.trace import get_current_span, Span

from azure.monitor.opentelemetry.exporter._constants import (
    _MAIN_AGENT_ATTRIBUTES,
    _MAIN_AGENT_PREFIX,
    _MAIN_AGENT_SELF_ATTRIBUTES,
)


# pylint: disable=protected-access
class _GenAIMainAgentSpanProcessor(SpanProcessor):
    """Propagates main-agent context in GenAI multi-agent systems.

    In OnStart, copies microsoft.gen_ai.main_agent.* attributes from the parent span
    to the child span (with fallback to gen_ai.agent.* on the parent), so the whole
    subtree under an invoke_agent span is attributed to the main agent. A reference to
    the parent span is also stored so OnEnd can retry propagation for children whose
    parent attributes were not yet populated at OnStart time.

    In OnEnd, self-attributes root invoke_agent spans (whose parent is invalid, so
    OnStart could not propagate) from their own gen_ai.agent.* attributes, and, for any
    span still lacking main_agent context, retries propagation from the (now potentially
    populated) parent span.
    """

    def __init__(self) -> None:
        # child span-id -> parent Span, used for OnEnd fallback propagation
        self._parent_spans: dict = {}

    def on_start(self, span: Span, parent_context: Optional[Context] = None) -> None:  # type: ignore
        # parent_context is typically None for child spans; get_current_span(None)
        # resolves the parent from the active context. A root span yields an
        # invalid parent span context, in which case there is nothing to propagate.
        parent_span = get_current_span(parent_context)
        if not parent_span.get_span_context().is_valid:
            return

        # Store parent reference so on_end can retry propagation for children whose
        # parent attributes are populated only after the child was created.
        span_context = span.get_span_context()
        if span_context.is_valid:
            self._parent_spans[span_context.span_id] = parent_span

        parent_attributes = getattr(parent_span, "attributes", None)
        if parent_attributes is None:
            return

        for target, primary_source, fallback_source in _MAIN_AGENT_ATTRIBUTES:
            value = parent_attributes.get(primary_source)
            if value is None:
                value = parent_attributes.get(fallback_source)
            if value is not None:
                span.set_attribute(target, value)

    def on_end(self, span: ReadableSpan) -> None:
        # Retrieve and drop the stored parent reference first, before any early
        # return below, so cleanup is guaranteed for every ended span.
        parent_span = None
        span_context = span.context
        if span_context is not None:
            parent_span = self._parent_spans.pop(span_context.span_id, None)

        attributes = span.attributes
        if attributes is None:
            return

        # If span already has any microsoft.gen_ai.main_agent.* attribute, return
        for key in attributes:
            if key.startswith(_MAIN_AGENT_PREFIX):
                return

        # Access the internal mutable attributes mapping. on_end receives a
        # ReadableSpan which has no set_attribute, so we write to the underlying
        # BoundedAttributes mapping directly.
        mutable = getattr(span, "_attributes", None)
        if mutable is None:
            return

        # Build the attributes to write before touching the (now frozen) span.
        updates = {}

        # Self-attribution: root invoke_agent spans copy their own
        # gen_ai.agent.* -> microsoft.gen_ai.main_agent.*
        if attributes.get("gen_ai.operation.name") == "invoke_agent":
            for target, source in _MAIN_AGENT_SELF_ATTRIBUTES:
                value = attributes.get(source)
                if value is not None:
                    updates[target] = value

        # Fallback propagation: re-read from the parent span whose attributes
        # may have been populated after this child was created (timing gap that
        # on_start missed, e.g. child LLM/chat spans under an invoke_agent span).
        # Parent values take precedence so nested spans are attributed to the
        # main (top-level) agent rather than an intermediate sub-agent.
        if parent_span is not None:
            parent_attributes = getattr(parent_span, "attributes", None)
            if parent_attributes is not None:
                for target, primary_source, fallback_source in _MAIN_AGENT_ATTRIBUTES:
                    value = parent_attributes.get(primary_source)
                    if value is None:
                        value = parent_attributes.get(fallback_source)
                    if value is not None:
                        updates[target] = value

        if not updates:
            return

        # OTel SDK >= 1.43 freezes span attributes (_immutable = True) inside
        # end() *before* invoking on_end. Writing then raises TypeError.
        # Temporarily lift the freeze for our own synchronous writes and always
        # restore it so the exported ReadableSpan snapshot stays frozen.
        was_immutable = getattr(mutable, "_immutable", False)
        if was_immutable:
            mutable._immutable = False  # type: ignore # pylint: disable=protected-access
            try:
                for target, value in updates.items():
                    mutable[target] = value
            finally:
                mutable._immutable = True  # type: ignore # pylint: disable=protected-access
        else:
            for target, value in updates.items():
                mutable[target] = value

    def shutdown(self):
        self._parent_spans.clear()

    def force_flush(self, timeout_millis: int = 30000):
        return True


class _GenAIMainAgentLogRecordProcessor(LogRecordProcessor):
    """Copies microsoft.gen_ai.main_agent.* attributes from the current span onto log records."""

    def on_emit(self, log_record: ReadWriteLogRecord) -> None:  # type: ignore # pylint: disable=arguments-renamed
        current_span = get_current_span()
        span_context = current_span.get_span_context()
        if not span_context.is_valid:
            return

        span_attributes = getattr(current_span, "attributes", None)
        if span_attributes is None:
            return

        # Collect all microsoft.gen_ai.main_agent.* attributes from the current span
        main_agent_attrs = {key: value for key, value in span_attributes.items() if key.startswith(_MAIN_AGENT_PREFIX)}

        if not main_agent_attrs:
            return

        # Copy them onto the log record without overwriting any existing log-level values
        if hasattr(log_record, "log_record") and log_record.log_record is not None:
            if log_record.log_record.attributes is None:
                log_record.log_record.attributes = {}
            for key, value in main_agent_attrs.items():
                if key not in log_record.log_record.attributes:
                    log_record.log_record.attributes[key] = value  # type: ignore[index]
        elif hasattr(log_record, "attributes"):
            if log_record.attributes is None:  # type: ignore[union-attr]
                log_record.attributes = {}  # type: ignore[union-attr]
            for key, value in main_agent_attrs.items():
                if key not in log_record.attributes:  # type: ignore[operator]
                    log_record.attributes[key] = value  # type: ignore[index]

    def emit(self, log_record: ReadWriteLogRecord) -> None:  # pylint: disable=arguments-renamed
        self.on_emit(log_record)

    def shutdown(self):
        pass

    def force_flush(self, timeout_millis: int = 30000):
        return True
