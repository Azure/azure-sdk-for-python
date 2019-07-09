# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

from azure.core.tracing.abstract_span import AbstractSpan
from opencensus.trace import execution_context
from opencensus.trace import tracer as tracer_module, Span
from opencensus.trace.propagation import trace_context_http_header_format
from opencensus.trace.samplers import ProbabilitySampler


class OpencensusWrapper(AbstractSpan):
    def __init__(self, span=None, name="parent_span"):
        # type: (Any) -> None
        tracer = self.get_current_tracer()
        self.was_created_by_azure_sdk = False
        if span is None:
            instrumentation_key = self._get_environ("APPINSIGHTS_INSTRUMENTATIONKEY")
            prob = self._get_environ("AZURE_TRACING_SAMPLER") or 0.001
            if tracer is None:
                if instrumentation_key is not None:
                    from opencensus.ext.azure.trace_exporter import AzureExporter

                    tracer = tracer_module.Tracer(
                        exporter=AzureExporter(instrumentation_key=instrumentation_key),
                        sampler=ProbabilitySampler(prob),
                    )
                else:
                    tracer = tracer_module.Tracer(sampler=ProbabilitySampler(prob))
                self.was_created_by_azure_sdk = True
            span = tracer.span(name=name)

        self.tracer = tracer
        self.span_instance = span

    def _get_environ(self, key):
        # type: (str) -> str
        if key in os.environ:
            return os.environ[key]
        return None

    def span(self, name="child_span"):
        # type: (str) -> OpencensusWrapper
        child = self.span_instance.span(name=name)
        wrapped_child = OpencensusWrapper(child)
        return wrapped_child

    def start(self):
        # type: () -> None
        self.span_instance.start()

    def finish(self):
        # type: () -> None
        self.span_instance.finish()
        if self.was_created_by_azure_sdk:
            self.end_tracer(self.tracer)

    def to_header(self, headers):
        # type: (Dict[str, str]) -> str
        tracer_from_context = self.get_current_tracer()
        temp_headers = {}
        if tracer_from_context is not None:
            ctx = tracer_from_context.span_context
            temp_headers = tracer_from_context.propagator.to_headers(ctx)
        return temp_headers

    def from_header(self, headers):
        # type: (Dict[str, str]) -> Any
        ctx = trace_context_http_header_format.TraceContextPropagator().from_headers(headers)
        return tracer_module.Tracer(span_context=ctx)

    @classmethod
    def end_tracer(cls, tracer):
        # type: (Tracer) -> None
        if tracer is not None:
            tracer.end_span()

    @classmethod
    def get_current_span(cls):
        # type: () -> Span
        return execution_context.get_current_span()

    @classmethod
    def get_current_tracer(cls):
        # type: () -> Tracer
        return execution_context.get_opencensus_tracer()

    @classmethod
    def set_current_span(cls, span):
        # type: (Span) -> None
        return execution_context.set_current_span(span)

    @classmethod
    def set_current_tracer(cls, tracer):
        # type: (Tracer) -> None
        return execution_context.set_opencensus_tracer(tracer)
