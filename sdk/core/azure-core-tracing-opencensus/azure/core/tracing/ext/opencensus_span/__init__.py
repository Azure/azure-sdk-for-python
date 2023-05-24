# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Implements azure.core.tracing.AbstractSpan to wrap opencensus spans."""
import warnings

from opencensus.trace import Span, execution_context
from opencensus.trace.tracer import Tracer
from opencensus.trace.span import SpanKind as OpenCensusSpanKind
from opencensus.trace.link import Link
from opencensus.trace.propagation import trace_context_http_header_format
from opencensus.trace import config_integration as _config_integration

from azure.core.tracing import SpanKind, HttpSpanMixin  # pylint: disable=no-name-in-module

from ._version import VERSION

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import Dict, Optional, Union, Callable, Sequence, Any

    from azure.core.pipeline.transport import HttpRequest, HttpResponse

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


__version__ = VERSION

_config_integration.trace_integrations(["threading"])


class OpenCensusSpan(HttpSpanMixin, object):
    """Wraps a given OpenCensus Span so that it implements azure.core.tracing.AbstractSpan"""

    def __init__(self, span=None, name="span", **kwargs):
        # type: (Optional[Span], Optional[str], Any) -> None
        """
        If a span is not passed in, creates a new tracer. If the instrumentation key for Azure Exporter is given, will
        configure the azure exporter else will just create a new tracer.

        :param span: The OpenCensus span to wrap
        :type span: :class: opencensus.trace.Span
        :param name: The name of the OpenCensus span to create if a new span is needed
        :type name: str
        :keyword SpanKind kind: The span kind of this span.
        :keyword links: The list of links to be added to the span.
        :paramtype links: list[~azure.core.tracing.Link]
        """
        tracer = self.get_current_tracer()
        value = kwargs.pop("kind", None)
        kind = (
            OpenCensusSpanKind.CLIENT
            if value == SpanKind.CLIENT
            else OpenCensusSpanKind.CLIENT
            if value == SpanKind.PRODUCER
            else OpenCensusSpanKind.SERVER  # No producer in opencensus
            if value == SpanKind.SERVER
            else OpenCensusSpanKind.CLIENT
            if value == SpanKind.CONSUMER
            else OpenCensusSpanKind.UNSPECIFIED  # No consumer in opencensus
            if value == SpanKind.INTERNAL
            else OpenCensusSpanKind.UNSPECIFIED  # No internal in opencensus
            if value == SpanKind.UNSPECIFIED
            else None
        )  # type: SpanKind
        if value and kind is None:
            raise ValueError("Kind {} is not supported in OpenCensus".format(value))

        links = kwargs.pop("links", None)
        self._span_instance = span or tracer.start_span(name=name)
        if kind is not None:
            self._span_instance.span_kind = kind

        if links:
            try:
                for link in links:
                    ctx = trace_context_http_header_format.TraceContextPropagator().from_headers(link.headers)
                    self._span_instance.add_link(
                        Link(trace_id=ctx.trace_id, span_id=ctx.span_id, attributes=link.attributes)
                    )
            except AttributeError:
                # we will just send the links as is if it's not ~azure.core.tracing.Link without any validation
                # assuming user knows what they are doing.
                self._span_instance.links = links

    @property
    def span_instance(self):
        # type: () -> Span
        """
        :return: The OpenCensus span that is being wrapped.
        """
        return self._span_instance

    def span(self, name="span", **kwargs):
        # type: (Optional[str], Any) -> OpenCensusSpan
        """
        Create a child span for the current span and append it to the child spans list in the span instance.
        :param name: Name of the child span
        :type name: str
        :keyword SpanKind kind: The span kind of this span.
        :keyword links: The list of links to be added to the span.
        :paramtype links: list[~azure.core.tracing.Link]
        :return: The OpenCensusSpan that is wrapping the child span instance
        """
        return self.__class__(name=name, **kwargs)

    @property
    def kind(self):
        # type: () -> Optional[SpanKind]
        """Get the span kind of this span."""
        value = self.span_instance.span_kind
        return (
            SpanKind.CLIENT
            if value == OpenCensusSpanKind.CLIENT
            else SpanKind.SERVER
            if value == OpenCensusSpanKind.SERVER
            else SpanKind.UNSPECIFIED
            if value == OpenCensusSpanKind.UNSPECIFIED
            else None
        )

    _KIND_MAPPING = {
        SpanKind.CLIENT: OpenCensusSpanKind.CLIENT,
        SpanKind.PRODUCER: OpenCensusSpanKind.CLIENT,  # No producer in opencensus
        SpanKind.SERVER: OpenCensusSpanKind.SERVER,
        SpanKind.CONSUMER: OpenCensusSpanKind.CLIENT,  # No consumer in opencensus
        SpanKind.INTERNAL: OpenCensusSpanKind.UNSPECIFIED,  # No internal in opencensus
        SpanKind.UNSPECIFIED: OpenCensusSpanKind.UNSPECIFIED,
    }

    @kind.setter
    def kind(self, value):
        # type: (SpanKind) -> None
        """Set the span kind of this span."""
        kind = self._KIND_MAPPING.get(value)
        if kind is None:
            raise ValueError("Kind {} is not supported in OpenCensus".format(value))
        self.span_instance.span_kind = kind

    def __enter__(self):
        """Start a span."""
        self.span_instance.__enter__()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """Finish a span."""
        self.span_instance.__exit__(exception_type, exception_value, traceback)

    def start(self):
        # type: () -> None
        """Set the start time for a span."""
        self.__enter__()

    def finish(self):
        # type: () -> None
        """Set the end time for a span."""
        self.__exit__(None, None, None)

    def to_header(self):
        # type: () -> Dict[str, str]
        """
        Returns a dictionary with the header labels and values.
        :return: A key value pair dictionary
        """
        tracer_from_context = self.get_current_tracer()
        temp_headers = {}  # type: Dict[str, str]
        if tracer_from_context is not None:
            ctx = tracer_from_context.span_context
            try:
                temp_headers = tracer_from_context.propagator.to_headers(ctx)
            except AttributeError:
                pass
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
        self.span_instance.add_attribute(key, value)

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
        return self.to_header()["traceparent"]

    @classmethod
    def link(cls, traceparent, attributes=None):
        # type: (str, Attributes) -> None
        """
        Links the context to the current tracer.

        :param traceparent: A complete traceparent
        :type traceparent: str
        """
        cls.link_from_headers({"traceparent": traceparent}, attributes)

    @classmethod
    def link_from_headers(cls, headers, attributes=None):
        # type: (Dict[str, str], Attributes) -> None
        """
        Given a dictionary, extracts the context and links the context to the current tracer.

        :param headers: A key value pair dictionary
        :type headers: dict
        """
        ctx = trace_context_http_header_format.TraceContextPropagator().from_headers(headers)
        current_span = cls.get_current_span()
        current_span.add_link(Link(trace_id=ctx.trace_id, span_id=ctx.span_id, attributes=attributes))

    @classmethod
    def get_current_span(cls):
        # type: () -> Span
        """
        Get the current span from the execution context. Return None otherwise.
        """
        return execution_context.get_current_span()

    @classmethod
    def get_current_tracer(cls):
        # type: () -> Tracer
        """
        Get the current tracer from the execution context. Return None otherwise.
        """
        return execution_context.get_opencensus_tracer()

    @classmethod
    def set_current_span(cls, span):
        # type: (Span) -> None
        """
        Set the given span as the current span in the execution context.

        :param span: The span to set the current span as
        :type span: :class: opencensus.trace.Span
        """
        warnings.warn("set_current_span is deprecated, use change_context instead", DeprecationWarning)
        return execution_context.set_current_span(span)

    @classmethod
    def change_context(cls, span):
        # type: (Span) -> ContextManager
        """Change the context for the life of this context manager."""
        original_span = cls.get_current_span()
        try:
            execution_context.set_current_span(span)
            yield
        finally:
            execution_context.set_current_span(original_span)

    @classmethod
    def set_current_tracer(cls, tracer):
        # type: (Tracer) -> None
        """
        Set the given tracer as the current tracer in the execution context.
        :param tracer: The tracer to set the current tracer as
        :type tracer: :class: opencensus.trace.Tracer
        """
        return execution_context.set_opencensus_tracer(tracer)

    @classmethod
    def with_current_context(cls, func):
        # type: (Callable) -> Callable
        """Passes the current spans to the new context the function will be run in.

        :param func: The function that will be run in the new context
        :return: The target the pass in instead of the function
        """
        try:
            import opencensus.ext.threading  # pylint: disable=unused-import
        except ImportError:
            raise ValueError("In order to trace threads with Opencensus, please install opencensus-ext-threading")
        # Noop, once opencensus-ext-threading is installed threads get context for free.
        return func
