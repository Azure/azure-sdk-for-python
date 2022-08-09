# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Implements azure.core.tracing.AbstractSpan to wrap OpenTelemetry spans."""

import warnings
from opentelemetry import trace
from opentelemetry.trace import Span, Tracer, SpanKind as OpenTelemetrySpanKind, Link as OpenTelemetryLink
from opentelemetry.context import attach, detach, get_current
from opentelemetry.propagate import extract, inject
from opentelemetry.trace.propagation import get_current_span as get_span_from_context

from azure.core.tracing import SpanKind, HttpSpanMixin  # pylint: disable=no-name-in-module

from ._version import VERSION

try:
    from typing import TYPE_CHECKING, ContextManager
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import Any, Mapping, Dict, Optional, Union, Callable, Sequence

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


class OpenTelemetrySpan(HttpSpanMixin, object):
    """OpenTelemetry plugin for Azure client libraries.

    :param span: The OpenTelemetry span to wrap, or nothing to create a new one.
    :type span: ~OpenTelemetry.trace.Span
    :param name: The name of the OpenTelemetry span to create if a new span is needed
    :type name: str
    :keyword SpanKind kind: The span kind of this span.
    :keyword links: The list of links to be added to the span.
    :paramtype links: list[~azure.core.tracing.Link]
    """

    def __init__(self, span=None, name="span", **kwargs):
        # type: (Optional[Span], Optional[str], Any) -> None
        current_tracer = self.get_current_tracer()

        ## kind
        value = kwargs.pop('kind', None)
        kind = (
            OpenTelemetrySpanKind.CLIENT if value == SpanKind.CLIENT else
            OpenTelemetrySpanKind.PRODUCER if value == SpanKind.PRODUCER else
            OpenTelemetrySpanKind.SERVER if value == SpanKind.SERVER else
            OpenTelemetrySpanKind.CONSUMER if value == SpanKind.CONSUMER else
            OpenTelemetrySpanKind.INTERNAL if value == SpanKind.INTERNAL else
            OpenTelemetrySpanKind.INTERNAL if value == SpanKind.UNSPECIFIED else
            None
        ) # type: SpanKind
        if value and kind is None:
            raise ValueError("Kind {} is not supported in OpenTelemetry".format(value))

        links = kwargs.pop('links', None)
        if links:
            try:
                ot_links = []
                for link in links:
                    ctx = extract(link.headers)
                    span_ctx = get_span_from_context(ctx).get_span_context()
                    ot_links.append(OpenTelemetryLink(span_ctx, link.attributes))
                kwargs.setdefault('links', ot_links)
            except AttributeError:
                # we will just send the links as is if it's not ~azure.core.tracing.Link without any validation
                # assuming user knows what they are doing.
                kwargs.setdefault('links', links)
        self._span_instance = span or current_tracer.start_span(name=name, kind=kind, **kwargs)
        # spell-checker:ignore ctxt
        self._current_ctxt_manager = None

    @property
    def span_instance(self):
        # type: () -> Span
        """
        :return: The OpenTelemetry span that is being wrapped.
        """
        return self._span_instance

    def span(self, name="span", **kwargs):
        # type: (Optional[str], Any) -> OpenTelemetrySpan
        """
        Create a child span for the current span and append it to the child spans list in the span instance.
        :param name: Name of the child span
        :type name: str
        :keyword SpanKind kind: The span kind of this span.
        :keyword links: The list of links to be added to the span.
        :paramtype links: list[Link]
        :return: The OpenTelemetrySpan that is wrapping the child span instance
        """
        return self.__class__(name=name, **kwargs)

    @property
    def kind(self):
        # type: () -> Optional[SpanKind]
        """Get the span kind of this span."""
        value = self.span_instance.kind
        return (
            SpanKind.CLIENT if value == OpenTelemetrySpanKind.CLIENT else
            SpanKind.PRODUCER if value == OpenTelemetrySpanKind.PRODUCER else
            SpanKind.SERVER if value == OpenTelemetrySpanKind.SERVER else
            SpanKind.CONSUMER if value == OpenTelemetrySpanKind.CONSUMER else
            SpanKind.INTERNAL if value == OpenTelemetrySpanKind.INTERNAL else
            None
        )


    @kind.setter
    def kind(self, value):
        # type: (SpanKind) -> None
        """Set the span kind of this span."""
        kind = (
            OpenTelemetrySpanKind.CLIENT if value == SpanKind.CLIENT else
            OpenTelemetrySpanKind.PRODUCER if value == SpanKind.PRODUCER else
            OpenTelemetrySpanKind.SERVER if value == SpanKind.SERVER else
            OpenTelemetrySpanKind.CONSUMER if value == SpanKind.CONSUMER else
            OpenTelemetrySpanKind.INTERNAL if value == SpanKind.INTERNAL else
            OpenTelemetrySpanKind.INTERNAL if value == SpanKind.UNSPECIFIED else
            None
        )
        if kind is None:
            raise ValueError("Kind {} is not supported in OpenTelemetry".format(value))
        try:
            self._span_instance._kind = kind # pylint: disable=protected-access
        except AttributeError:
            warnings.warn(
                """Kind must be set while creating the span for OpenTelemetry. It might be possible
                that one of the packages you are using doesn't follow the latest Opentelemtry Spec.
                Try updating the azure packages to the latest versions."""
            )

    def __enter__(self):
        """Start a span."""
        self._current_ctxt_manager = trace.use_span(self._span_instance, end_on_exit=True)
        self._current_ctxt_manager.__enter__() # pylint: disable=no-member
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """Finish a span."""
        if self._current_ctxt_manager:
            self._current_ctxt_manager.__exit__(exception_type, exception_value, traceback) # pylint: disable=no-member
            self._current_ctxt_manager = None

    def start(self):
        # Spans are automatically started at their creation with OpenTelemetry
        pass

    def finish(self):
        # type: () -> None
        """Set the end time for a span."""
        self.span_instance.end()

    def to_header(self): # pylint: disable=no-self-use
        # type: () -> Dict[str, str]
        """
        Returns a dictionary with the header labels and values.
        :return: A key value pair dictionary
        """
        temp_headers = {} # type: Dict[str, str]
        inject(temp_headers)
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
        # type: () -> str
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
        }, attributes)

    @classmethod
    def link_from_headers(cls, headers, attributes=None):
        # type: (Dict[str, str], Attributes) -> None
        """
        Given a dictionary, extracts the context and links the context to the current tracer.

        :param headers: A key value pair dictionary
        :type headers: dict
        """
        ctx = extract(headers)
        span_ctx = get_span_from_context(ctx).get_span_context()
        current_span = cls.get_current_span()
        try:
            current_span._links.append(OpenTelemetryLink(span_ctx, attributes)) # pylint: disable=protected-access
        except AttributeError:
            warnings.warn(
                """Link must be added while creating the span for OpenTelemetry. It might be possible
                that one of the packages you are using doesn't follow the latest Opentelemtry Spec.
                Try updating the azure packages to the latest versions."""
            )

    @classmethod
    def get_current_span(cls):
        # type: () -> Span
        """
        Get the current span from the execution context. Return None otherwise.
        """
        return get_span_from_context()

    @classmethod
    def get_current_tracer(cls):
        # type: () -> Tracer
        """
        Get the current tracer from the execution context. Return None otherwise.
        """
        return trace.get_tracer(__name__, __version__)

    @classmethod
    def change_context(cls, span):
        # type: (Span) -> ContextManager
        """Change the context for the life of this context manager.
        """
        return trace.use_span(span, end_on_exit=False)

    @classmethod
    def set_current_span(cls, span):
        # type: (Span) -> None
        """Not supported by OpenTelemetry.
        """
        raise NotImplementedError(
            "set_current_span is not supported by OpenTelemetry plugin. Use change_context instead."
        )

    @classmethod
    def set_current_tracer(cls, _):
        # type: (Tracer) -> None
        """
        Set the given tracer as the current tracer in the execution context.
        :param tracer: The tracer to set the current tracer as
        :type tracer: :class: OpenTelemetry.trace.Tracer
        """
        # Do nothing, if you're able to get two tracer with OpenTelemetry that's a surprise!

    @classmethod
    def with_current_context(cls, func):
        # type: (Callable) -> Callable
        """Passes the current spans to the new context the function will be run in.

        :param func: The function that will be run in the new context
        :return: The target the pass in instead of the function
        """
        # returns the current Context object
        context = get_current()

        def call_with_current_context(*args, **kwargs):
            try:
                token = attach(context)
                return func(*args, **kwargs)
            finally:
                detach(token)

        return call_with_current_context
