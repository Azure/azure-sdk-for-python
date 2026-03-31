# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Tracing test helpers for Cosmos DB tests.

This module provides helpers for testing tracing functionality using Azure Core's
tracing abstractions, avoiding direct dependencies on OpenTelemetry.
"""

from contextlib import contextmanager
from typing import List, Dict, Any, Optional
from azure.core.tracing import HttpSpanMixin, SpanKind


class MockSpan(HttpSpanMixin, object):
    """Mock span implementation for testing that captures attributes."""

    # Keep track of all created spans
    _all_spans = []
    # Keep a fake context of the current span stack
    CONTEXT = []

    def __init__(self, name="span", kind=None):
        """Initialize a mock span.

        :param name: Name of the span
        :type name: str
        :param kind: Kind of span
        :type kind: SpanKind
        """
        self.name = name
        self._kind = kind or SpanKind.UNSPECIFIED
        self.attributes = {}
        self.children = []
        self.status = None
        self._finished = False

        # Track this span globally
        MockSpan._all_spans.append(self)

        # Add to parent's children if there's a parent
        if self.CONTEXT:
            self.CONTEXT[-1].children.append(self)

    def __enter__(self):
        """Start a span."""
        self.CONTEXT.append(self)
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """Finish a span."""
        if exception_value:
            self.status = str(exception_value)
        self._finished = True
        if self.CONTEXT and self.CONTEXT[-1] == self:
            self.CONTEXT.pop()

    @property
    def span_instance(self):
        """Return the span instance."""
        return self

    @property
    def kind(self):
        """Get the span kind."""
        return self._kind

    @kind.setter
    def kind(self, value):
        """Set the span kind."""
        self._kind = value

    def span(self, name="span"):
        """Create a child span.

        :param name: Name of the child span
        :type name: str
        :return: Child span
        :rtype: MockSpan
        """
        return self.__class__(name=name)

    def start(self):
        """Start the span."""
        pass

    def finish(self):
        """Finish the span."""
        self._finished = True
        if self.CONTEXT and self.CONTEXT[-1] == self:
            self.CONTEXT.pop()

    def add_attribute(self, key, value):
        """Add an attribute to the span.

        :param key: Attribute key
        :type key: str
        :param value: Attribute value
        :type value: Any
        """
        self.attributes[key] = value

    def to_header(self):
        """Return a traceparent header.

        :return: Dictionary with traceparent header
        :rtype: Dict[str, str]
        """
        return {"traceparent": f"00-12345-{self.name}-01"}

    def get_trace_parent(self):
        """Return traceparent string.

        :return: Traceparent string
        :rtype: str
        """
        return self.to_header()["traceparent"]

    @classmethod
    def get_current_span(cls):
        """Get the current span from context.

        :return: Current span or None
        :rtype: Optional[MockSpan]
        """
        return cls.CONTEXT[-1] if cls.CONTEXT else None

    @classmethod
    @contextmanager
    def change_context(cls, span):
        """Change the context for the life of this context manager.

        :param span: Span to set as current
        :type span: MockSpan
        """
        try:
            cls.CONTEXT.append(span)
            yield
        finally:
            cls.CONTEXT.pop()

    @classmethod
    def clear_all_spans(cls):
        """Clear all tracked spans."""
        cls._all_spans = []
        cls.CONTEXT = []

    @classmethod
    def get_all_spans(cls):
        """Get all tracked spans.

        :return: List of all spans
        :rtype: List[MockSpan]
        """
        return cls._all_spans

    @classmethod
    def get_finished_spans(cls):
        """Get all finished spans.

        :return: List of finished spans
        :rtype: List[MockSpan]
        """
        return [s for s in cls._all_spans if s._finished]


class TracingTestHelper:
    """Helper class for tracing tests."""

    def __init__(self):
        """Initialize the tracing test helper."""
        self.spans = []

    def clear(self):
        """Clear all captured spans."""
        MockSpan.clear_all_spans()
        self.spans = []

    def get_spans(self):
        """Get all spans as dictionaries.

        :return: List of span dictionaries
        :rtype: List[Dict[str, Any]]
        """
        all_spans = MockSpan.get_all_spans()
        return [
            {
                "name": span.name,
                "attributes": dict(span.attributes),
                "kind": span.kind,
                "status": span.status
            }
            for span in all_spans
        ]

    def get_finished_spans(self):
        """Get all finished spans as dictionaries.

        :return: List of finished span dictionaries
        :rtype: List[Dict[str, Any]]
        """
        finished_spans = MockSpan.get_finished_spans()
        return [
            {
                "name": span.name,
                "attributes": dict(span.attributes),
                "kind": span.kind,
                "status": span.status
            }
            for span in finished_spans
        ]


def setup_tracing():
    """Set up tracing for tests.

    :return: Tracing test helper instance
    :rtype: TracingTestHelper
    """
    from azure.core.settings import settings

    # Set MockSpan as the tracing implementation
    settings.tracing_implementation = MockSpan

    helper = TracingTestHelper()
    helper.clear()
    return helper


def cleanup_tracing():
    """Clean up tracing after tests."""
    from azure.core.settings import settings

    MockSpan.clear_all_spans()
    settings.tracing_implementation = None


