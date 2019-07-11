# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

from azure.core.tracing import AbstractSpan
from opencensus.trace import execution_context
from opencensus.trace import tracer as tracer_module, Span
from opencensus.trace.propagation import trace_context_http_header_format
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.trace.tracers.noop_tracer import NoopTracer

try:
    from opencensus.ext.azure.trace_exporter import AzureExporter
except:
    AzureExporter = False

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import Any, Dict, Union


class OpencensusSpanWrapper(AbstractSpan):
    """Wraps a given Opencensus Span so that it implements azure.core.tracing.AbstractSpan"""

    def __init__(self, span=None, name="parent_span"):
        # type: (Span, str) -> None
        """
        If a span is not passed in, creates a new tracer. If the instrumentation key for Azure Exporter is given, will
        configure the azure exporter else will just create a new tracer.

        :param span: The opencensus span to wrap
        :param name: The name of the opencensus span to create if a new span is needed
        """
        super(OpencensusSpanWrapper, self).__init__(span, name)
        tracer = self.get_current_tracer()
        span = span or tracer.span(name=name)
        self._span_instance = span

    @property
    def span_instance(self):
        # type: () -> Span
        """
        :return: The openencensus span that is being wrapped.
        """
        return self._span_instance

    def span(self, name="child_span"):
        # type: (str) -> OpencensusSpanWrapper
        """
        Create a child span for the current span and append it to the child spans list in the span instance.
        :param name: Name of the child span
        :return: The OpencensusWrapper that is wrapping the child span instance
        """
        return self.__class__(self.span_instance.span(name=name))

    def start(self):
        # type: () -> None
        """Set the start time for a span."""
        self.span_instance.start()

    def finish(self):
        # type: () -> None
        """Set the end time for a span."""
        self.span_instance.finish()

    def to_header(self):
        # type: (Dict[str, str]) -> str
        """
        Returns a dictionary with the header labels and values.
        :param headers: A key value pair dictionary
        :return: A key value pair dictionary
        """
        tracer_from_context = self.get_current_tracer()
        temp_headers = {}
        if tracer_from_context is not None:
            ctx = tracer_from_context.span_context
            temp_headers = tracer_from_context.propagator.to_headers(ctx)
        return temp_headers

    @classmethod
    def from_header(cls, headers):
        # type: (Dict[str, str]) -> Any
        """
        Given a dictionary returns a new tracer with the span context extracted from that dictionary.
        :param headers: A key value pair dictionary
        :return: A tracer initialized with the span context extraction from headers.
        """
        ctx = trace_context_http_header_format.TraceContextPropagator().from_headers(
            headers
        )
        return tracer_module.Tracer(span_context=ctx)

    @classmethod
    def get_current_span(cls):
        # type: () -> Span
        """
        Get the current span from the execution context. Return None otherwise.
        """
        return execution_context.get_current_span()

    @classmethod
    def get_current_tracer(cls):
        # type: () -> tracer_module.Tracer
        """
        Get the current tracer from the execution context. Return None otherwise.
        """
        return execution_context.get_opencensus_tracer()

    @classmethod
    def set_current_span(cls, span):
        # type: (Span) -> None
        """
        Set the given span as the current span in the execution context.
        """
        return execution_context.set_current_span(span)

    @classmethod
    def set_current_tracer(cls, tracer):
        # type: (tracer_module.Tracer) -> None
        """
        Set the given tracer as the current tracer in the execution context.
        """
        return execution_context.set_opencensus_tracer(tracer)
