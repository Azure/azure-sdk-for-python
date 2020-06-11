# Copyright 2017, OpenCensus Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from opencensus.trace import execution_context
from opencensus.trace import print_exporter
from opencensus.trace import samplers
from opencensus.trace.propagation import trace_context_http_header_format
from opencensus.trace.span_context import SpanContext
from opencensus.trace.tracers import context_tracer
from opencensus.trace.tracers import noop_tracer


class Tracer(object):
    """The Tracer is for tracing a request for web applications.

    :type span_context: :class:`~opencensus.trace.span_context.SpanContext`
    :param span_context: SpanContext encapsulates the current context within
                         the request's trace.

    :type sampler: :class:`~opencensus.trace.samplers.base.Sampler`
    :param sampler: Instances of Sampler objects. Defaults to
                    :class:`.ProbabilitySampler`. Other options include
                    :class:`.AlwaysOnSampler` and :class:`.AlwaysOffSampler`.

    :type exporter: :class:`~opencensus.trace.base_exporter.exporter`
    :param exporter: Instances of exporter objects. Default to
                     :class:`.Printexporter`. The rest options are
                     :class:`.Fileexporter`, :class:`.Printexporter`,
                     :class:`.Loggingexporter`, :class:`.Zipkinexporter`,
                     :class:`.GoogleCloudexporter`
    """
    def __init__(
            self,
            span_context=None,
            sampler=None,
            exporter=None,
            propagator=None):
        if span_context is None:
            span_context = SpanContext()

        if sampler is None:
            sampler = samplers.ProbabilitySampler()

        if exporter is None:
            exporter = print_exporter.PrintExporter()

        if propagator is None:
            propagator = \
                trace_context_http_header_format.TraceContextPropagator()

        self.span_context = span_context
        self.sampler = sampler
        self.exporter = exporter
        self.propagator = propagator
        self.tracer = self.get_tracer()
        self.store_tracer()

    def should_sample(self):
        """Determine whether to sample this request or not.
        If the context enables tracing, return True.
        Else follow the decision of the sampler.

        :rtype: bool
        :returns: Whether to trace the request or not.
        """
        return self.sampler.should_sample(self.span_context)

    def get_tracer(self):
        """Return a tracer according to the sampling decision."""
        sampled = self.should_sample()

        if sampled:
            self.span_context.trace_options.set_enabled(True)
            return context_tracer.ContextTracer(
                exporter=self.exporter,
                span_context=self.span_context)
        return noop_tracer.NoopTracer()

    def store_tracer(self):
        """Add the current tracer to thread_local"""
        execution_context.set_opencensus_tracer(self)

    def finish(self):
        """End all spans."""
        self.tracer.finish()

    def span(self, name='span'):
        """Create a new span with the trace using the context information.

        :type name: str
        :param name: The name of the span.

        :rtype: :class:`~opencensus.trace.span.Span`
        :returns: The Span object.
        """
        return self.tracer.span(name)

    def start_span(self, name='span'):
        return self.tracer.start_span(name)

    def end_span(self):
        """End a span. Update the span_id in SpanContext to the current span's
        parent span id; Update the current span; Send the span to exporter.
        """
        self.tracer.end_span()

    def current_span(self):
        """Return the current span."""
        return self.tracer.current_span()

    def add_attribute_to_current_span(self, attribute_key, attribute_value):
        """Add attribute to current span.

        :type attribute_key: str
        :param attribute_key: Attribute key.

        :type attribute_value:str
        :param attribute_value: Attribute value.
        """
        self.tracer.add_attribute_to_current_span(
            attribute_key, attribute_value)

    def trace_decorator(self):
        """Decorator to trace a function."""

        def decorator(func):

            def wrapper(*args, **kwargs):
                self.tracer.start_span(name=func.__name__)
                return_value = func(*args, **kwargs)
                self.tracer.end_span()
                return return_value

            return wrapper

        return decorator
