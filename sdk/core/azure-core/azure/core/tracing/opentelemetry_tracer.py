# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from __future__ import annotations
from typing import Optional, Dict, Sequence, cast, Callable

from opentelemetry import context as otel_context_module, trace
from opentelemetry.trace import (
    NonRecordingSpan,
    SpanKind as OpenTelemetrySpanKind,
    Link as OpenTelemetryLink,
)
from opentelemetry.trace.propagation import get_current_span as get_current_span_otel
from opentelemetry.propagate import extract, inject

from .._version import VERSION
from ._models import SpanKind, Link, Attributes
from .opentelemetry_span import OpenTelemetrySpan


_DEFAULT_SCHEMA_URL = "https://opentelemetry.io/schemas/1.23.1"
_DEFAULT_MODULE_NAME = "azure-core"
_SUPPRESSED_SPAN_FLAG = "SUPPRESSED_SPAN_FLAG"
_LAST_UNSUPPRESSED_SPAN = "LAST_UNSUPPRESSED_SPAN"

_KIND_MAPPINGS = {
    SpanKind.CLIENT: OpenTelemetrySpanKind.CLIENT,
    SpanKind.CONSUMER: OpenTelemetrySpanKind.CONSUMER,
    SpanKind.PRODUCER: OpenTelemetrySpanKind.PRODUCER,
    SpanKind.SERVER: OpenTelemetrySpanKind.SERVER,
    SpanKind.INTERNAL: OpenTelemetrySpanKind.INTERNAL,
    SpanKind.UNSPECIFIED: OpenTelemetrySpanKind.INTERNAL,
}


class OpenTelemetryTracer:
    """A tracer that uses OpenTelemetry to trace operations.

    :keyword library_name: The name of the library to use in the tracer.
    :paramtype library_name: str
    :keyword library_version: The version of the library to use in the tracer.
    :paramtype library_version: str
    :keyword schema_url: Specifies the Schema URL of the emitted spans.
    :paramtype schema_url: str
    :keyword attributes: Attributes to add to the emitted spans.
    """

    def __init__(
        self,
        *,
        library_name: Optional[str] = None,
        library_version: Optional[str] = None,
        schema_url: Optional[str] = None,
        attributes: Optional[Attributes] = None,
    ) -> None:
        self._tracer = trace.get_tracer(
            instrumenting_module_name=library_name or _DEFAULT_MODULE_NAME,
            instrumenting_library_version=library_version or VERSION,
            schema_url=schema_url or _DEFAULT_SCHEMA_URL,
            attributes=attributes,
        )

    def start_span(
        self,
        name: str,
        *,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: Optional[Attributes] = None,
        links: Optional[Sequence[Link]] = None,
        record_exception: bool = True,
    ) -> OpenTelemetrySpan:
        """Starts a span without setting it as the current span in the context.

        The span can be used as a context manager. Upon entering the context manager, the span will be set as the
        current span in the context. On exiting the context manager, the span's end() method will be called.

        :param name: The name of the span
        :type name: str
        :keyword kind: The kind of the span. INTERNAL by default.
        :paramtype kind: ~azure.core.tracing.SpanKind
        :keyword attributes: Attributes to add to the span.
        :paramtype attributes: M
        :keyword links: Links to add to the span.
        :paramtype links: list[~azure.core.tracing.Link]
        :keyword record_exception: Whether to record any exceptions raised within the operation's context as error
            events on the span. Default is True.
        :paramtype record_exception: bool
        :return: The span that was started
        :rtype: ~azure.core.tracing.Span
        """
        otel_kind = _KIND_MAPPINGS.get(kind, OpenTelemetrySpanKind.INTERNAL)
        otel_links = self._parse_links(links)

        if otel_kind == OpenTelemetrySpanKind.INTERNAL and otel_context_module.get_value(_SUPPRESSED_SPAN_FLAG):
            current_span = OpenTelemetryTracer.get_current_span()
            return OpenTelemetrySpan(span=NonRecordingSpan(context=current_span.span_instance.get_span_context()))

        otel_span = self._tracer.start_span(
            name,
            kind=otel_kind,
            attributes=attributes,
            links=otel_links,
            record_exception=record_exception,
        )
        return OpenTelemetrySpan(span=otel_span, _record_exception=record_exception)

    def _parse_links(self, links: Optional[Sequence[Link]]) -> Optional[Sequence[OpenTelemetryLink]]:
        if not links:
            return None

        try:
            otel_links = []
            for link in links:
                ctx = extract(link.headers)
                span_ctx = get_current_span_otel(ctx).get_span_context()
                otel_links.append(OpenTelemetryLink(span_ctx, link.attributes))
            return otel_links
        except AttributeError:
            # We will just send the links as is if it's not ~azure.core.tracing.Link without
            # any validation assuming the user knows what they are doing.
            return cast(Sequence[OpenTelemetryLink], links)

    @classmethod
    def get_current_span(cls) -> OpenTelemetrySpan:
        """Returns the current span in the context.

        If the current span is a NonRecordingSpan and the last unsuppressed parent span is available, it will return
        the last unsuppressed parent span.

        :return: The current span
        :rtype: ~azure.core.tracing.opentelemetry_span.OpenTelemetrySpan
        """
        otel_span = get_current_span_otel()
        last_unsuppressed_parent = otel_context_module.get_value(_LAST_UNSUPPRESSED_SPAN)
        if isinstance(otel_span, NonRecordingSpan) and last_unsuppressed_parent:
            return cast(OpenTelemetrySpan, last_unsuppressed_parent)
        return OpenTelemetrySpan(span=otel_span)

    @classmethod
    def with_current_context(cls, func: Callable) -> Callable:
        """Passes the current spans to the new context the function will be run in.

        :param func: The function that will be run in the new context
        :type func: callable
        :return: The wrapped function
        :rtype: callable
        """
        current_context = otel_context_module.get_current()

        def call_with_current_context(*args, **kwargs):
            token = None
            try:
                token = otel_context_module.attach(current_context)
                return func(*args, **kwargs)
            finally:
                if token is not None:
                    otel_context_module.detach(token)

        return call_with_current_context

    @classmethod
    def get_trace_context(cls) -> Dict[str, str]:
        """Returns the Trace Context header values associated with the span.

        These are generally the W3C Trace Context headers (i.e. "traceparent" and "tracestate").

        :return: A key value pair dictionary
        :rtype: dict[str, str]
        """
        trace_context: Dict[str, str] = {}
        inject(trace_context)
        return trace_context
