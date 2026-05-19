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
    to the child span (with fallback to gen_ai.agent.* on the parent).

    In OnEnd, self-attributes root invoke_agent spans that have no main_agent context.
    """

    def on_start(self, span: Span, parent_context: Optional[Context] = None) -> None:  # type: ignore
        if parent_context is None:
            return
        parent_span = get_current_span(parent_context)
        parent_span_context = parent_span.get_span_context()
        if not parent_span_context.is_valid:
            return

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
        attributes = span.attributes
        if attributes is None:
            return

        # Only apply to spans with gen_ai.operation.name = "invoke_agent"
        if attributes.get("gen_ai.operation.name") != "invoke_agent":
            return

        # If span already has any microsoft.gen_ai.main_agent.* attribute, return
        for key in attributes:
            if key.startswith(_MAIN_AGENT_PREFIX):
                return

        # Self-attribute from the span's own gen_ai attributes
        for target, source in _MAIN_AGENT_SELF_ATTRIBUTES:
            value = attributes.get(source)
            if value is not None:
                span._attributes[target] = value  # type: ignore

    def shutdown(self):
        pass

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
