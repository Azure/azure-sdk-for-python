# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Fake implementation of AbstractSpan for tests."""
from contextlib import contextmanager
from azure.core.tracing import HttpSpanMixin, SpanKind
from typing import Union, Sequence, Optional, Dict
AttributeValue = Union[
    str,
    bool,
    int,
    float,
    Sequence[str],
    Sequence[bool],
    Sequence[int],
    Sequence[float],
]
Attributes = Optional[Dict[str, AttributeValue]]

class FakeSpan(HttpSpanMixin, object):
    # Keep a fake context of the current one
    CONTEXT = []

    def __init__(self, span=None, name="span"):
        # type: (Optional[Span], Optional[str]) -> None
        """
        If a span is not passed in, creates a new tracer. If the instrumentation key for Azure Exporter is given, will
        configure the azure exporter else will just create a new tracer.

        :param span: The OpenTelemetry span to wrap
        :type span: :class: OpenTelemetry.trace.Span
        :param name: The name of the OpenTelemetry span to create if a new span is needed
        :type name: str
        """
        self._span = span
        self.name = name
        self._kind = SpanKind.UNSPECIFIED
        self.attributes = {}
        self.children = []
        if self.CONTEXT:
            self.CONTEXT[-1].children.append(self)
        self.CONTEXT.append(self)
        self.status = None

    def __str__(self):
        buffer = "Name: {}\n".format(self.name)
        buffer += "Children:\n"
        subchildren = "\n".join(str(child) for child in self.children)
        buffer += "\n".join("\t{}".format(line) for line in subchildren.splitlines())
        return buffer

    @property
    def span_instance(self):
        # type: () -> Span
        """
        :return: The OpenTelemetry span that is being wrapped.
        """
        return self._span

    def span(self, name="span"):
        # type: (Optional[str]) -> OpenCensusSpan
        """
        Create a child span for the current span and append it to the child spans list in the span instance.
        :param name: Name of the child span
        :type name: str
        :return: The OpenCensusSpan that is wrapping the child span instance
        """
        return self.__class__(name=name)

    @property
    def kind(self):
        # type: () -> Optional[SpanKind]
        """Get the span kind of this span."""
        return self._kind


    @kind.setter
    def kind(self, value):
        # type: (SpanKind) -> None
        """Set the span kind of this span."""
        self._kind = value

    def __enter__(self):
        """Start a span."""
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """Finish a span."""
        if exception_value:
            self.status = exception_value.args[0]
        self.CONTEXT.pop()

    def start(self):
        # type: () -> None
        """Set the start time for a span."""
        pass

    def finish(self):
        # type: () -> None
        """Set the end time for a span."""
        self.CONTEXT.pop()

    def to_header(self):
        # type: () -> Dict[str, str]
        """
        Returns a dictionary with the header labels and values.
        :return: A key value pair dictionary
        """
        return {'traceparent': '123456789'}

    def add_attribute(self, key, value):
        # type: (str, Union[str, int]) -> None
        """
        Add attribute (key value pair) to the current span.

        :param key: The key of the key value pair
        :type key: str
        :param value: The value of the key value pair
        :type value: str
        """
        self.attributes[key] = value

    def get_trace_parent(self):
        """Return traceparent string as defined in W3C trace context specification.

        Example:
        Value = 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
        base16(version) = 00
        base16(trace-id) = 4bf92f3577b34da6a3ce929d0e0e4736
        base16(parent-id) = 00f067aa0ba902b7
        base16(trace-flags) = 01  // sampled

        :return: a traceparent string
        :rtype: str
        """
        return self.to_header()['traceparent']

    @classmethod
    def link(cls, traceparent, attributes=None):
        # type: (str, Attributes) -> None
        """
        Links the context to the current tracer.

        :param traceparent: A complete traceparent
        :type traceparent: str
        """
        cls.link_from_headers({
            'traceparent': traceparent
        })

    @classmethod
    def link_from_headers(cls, headers, attributes=None):
        # type: (Dict[str, str], Attributes) -> None
        """
        Given a dictionary, extracts the context and links the context to the current tracer.

        :param headers: A key value pair dictionary
        :type headers: dict
        """
        raise NotImplementedError("This method needs to be implemented")

    @classmethod
    def get_current_span(cls):
        # type: () -> Span
        """
        Get the current span from the execution context. Return None otherwise.
        """
        return cls.CONTEXT[-1]

    @classmethod
    def get_current_tracer(cls):
        # type: () -> Tracer
        """
        Get the current tracer from the execution context. Return None otherwise.
        """
        raise NotImplementedError()

    @classmethod
    @contextmanager
    def change_context(cls, span):
        # type: (Span) -> ContextManager
        """Change the context for the life of this context manager.
        """
        try:
            cls.CONTEXT.append(span)
            yield
        finally:
            cls.CONTEXT.pop()

    @classmethod
    def set_current_span(cls, span):
        # type: (Span) -> None
        """Not supported by OpenTelemetry.
        """
        raise NotImplementedError()

    @classmethod
    def set_current_tracer(cls, tracer):
        # type: (Tracer) -> None
        """
        Set the given tracer as the current tracer in the execution context.
        :param tracer: The tracer to set the current tracer as
        :type tracer: :class: OpenTelemetry.trace.Tracer
        """
        raise NotImplementedError()

    @classmethod
    def with_current_context(cls, func):
        # type: (Callable) -> Callable
        """Passes the current spans to the new context the function will be run in.

        :param func: The function that will be run in the new context
        :return: The target the pass in instead of the function
        """
        return func
