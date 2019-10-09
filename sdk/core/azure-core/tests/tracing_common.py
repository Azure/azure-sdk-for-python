# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Fake implementation of AbstractSpan for tests."""
from azure.core.tracing import HttpSpanMixin, SpanKind


class FakeSpan(HttpSpanMixin, object):

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
        self._name = name
        self._kind = SpanKind.UNSPECIFIED

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
        pass

    def start(self):
        # type: () -> None
        """Set the start time for a span."""
        pass

    def finish(self):
        # type: () -> None
        """Set the end time for a span."""
        pass

    def to_header(self):
        # type: () -> Dict[str, str]
        """
        Returns a dictionary with the header labels and values.
        :return: A key value pair dictionary
        """
        temp_headers = {} # type: Dict[str, str]
        # FIXME
        return temp_headers

    def add_attribute(self, key, value):
        # type: (str, Union[str, int]) -> None
        """
        Add attribute (key value pair) to the current span.

        :param key: The key of the key value pair
        :type key: str
        :param value: The value of the key value pair
        :type value: str
        """
        self.span_instance.set_attribute(key, value)

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
    def link(cls, traceparent):
        # type: (str) -> None
        """
        Links the context to the current tracer.

        :param traceparent: A complete traceparent
        :type traceparent: str
        """
        cls.link_from_headers({
            'traceparent': traceparent
        })

    @classmethod
    def link_from_headers(cls, headers):
        # type: (Dict[str, str]) -> None
        """
        Given a dictionary, extracts the context and links the context to the current tracer.

        :param headers: A key value pair dictionary
        :type headers: dict
        """
        ctx = extract(_get_headers_from_http_request_headers, headers)
        current_span = cls.get_current_span()
        current_span.add_link(ctx)

    @classmethod
    def get_current_span(cls):
        # type: () -> Span
        """
        Get the current span from the execution context. Return None otherwise.
        """
        return cls.get_current_tracer().get_current_span()

    @classmethod
    def get_current_tracer(cls):
        # type: () -> Tracer
        """
        Get the current tracer from the execution context. Return None otherwise.
        """
        return tracer()

    @classmethod
    def change_context(cls, span):
        # type: (Span) -> ContextManager
        """Change the context for the life of this context manager.
        """
        return cls.get_current_tracer().use_span(span, end_on_exit=False)

    @classmethod
    def set_current_span(cls, span):
        # type: (Span) -> None
        """Not supported by OpenTelemetry.
        """
        raise NotImplementedError("set_current_span is not supported by OpenTelemetry plugin. Use ChangeContext instead.")

    @classmethod
    def set_current_tracer(cls, tracer):
        # type: (Tracer) -> None
        """
        Set the given tracer as the current tracer in the execution context.
        :param tracer: The tracer to set the current tracer as
        :type tracer: :class: OpenTelemetry.trace.Tracer
        """
        # Do nothing, if you're able to get two tracer with OpenTelemetry that's a surprise!
        pass

    @classmethod
    def with_current_context(cls, func):
        # type: (Callable) -> Callable
        """Passes the current spans to the new context the function will be run in.

        :param func: The function that will be run in the new context
        :return: The target the pass in instead of the function
        """
        return Context.with_current_context(func)
