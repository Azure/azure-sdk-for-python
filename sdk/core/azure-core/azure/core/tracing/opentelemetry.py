# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from __future__ import annotations
from typing import Optional, Dict, Sequence, cast, Callable, ContextManager, Type, List
from types import TracebackType

from typing_extensions import Self
from opentelemetry import context as otel_context_module, trace
from opentelemetry.trace import (
    Span,
    NonRecordingSpan,
    SpanKind as OpenTelemetrySpanKind,
    StatusCode as OpenTelemetryStatusCode,
    Link as OpenTelemetryLink,
)
from opentelemetry.trace.propagation import get_current_span as get_current_span_otel
from opentelemetry.propagate import extract, inject

try:
    from opentelemetry.context import _SUPPRESS_HTTP_INSTRUMENTATION_KEY  # type: ignore[attr-defined]
except ImportError:
    _SUPPRESS_HTTP_INSTRUMENTATION_KEY = "suppress_http_instrumentation"

from .._version import VERSION
from ._models import (
    AttributeValue,
    Attributes,
    SpanKind as _SpanKind,
    StatusCode as _StatusCode,
    Link as _Link,
)


_DEFAULT_SCHEMA_URL = "https://opentelemetry.io/schemas/1.23.1"
_DEFAULT_MODULE_NAME = "azure-core"
_SUPPRESSED_SPAN_FLAG = "SUPPRESSED_SPAN_FLAG"
_LAST_UNSUPPRESSED_SPAN = "LAST_UNSUPPRESSED_SPAN"
_ERROR_SPAN_ATTRIBUTE = "error.type"

_KIND_MAPPINGS = {
    _SpanKind.CLIENT: OpenTelemetrySpanKind.CLIENT,
    _SpanKind.CONSUMER: OpenTelemetrySpanKind.CONSUMER,
    _SpanKind.PRODUCER: OpenTelemetrySpanKind.PRODUCER,
    _SpanKind.SERVER: OpenTelemetrySpanKind.SERVER,
    _SpanKind.INTERNAL: OpenTelemetrySpanKind.INTERNAL,
    _SpanKind.UNSPECIFIED: OpenTelemetrySpanKind.INTERNAL,
}

_OTEL_KIND_MAPPINGS = {
    OpenTelemetrySpanKind.CLIENT: _SpanKind.CLIENT,
    OpenTelemetrySpanKind.CONSUMER: _SpanKind.CONSUMER,
    OpenTelemetrySpanKind.PRODUCER: _SpanKind.PRODUCER,
    OpenTelemetrySpanKind.SERVER: _SpanKind.SERVER,
    OpenTelemetrySpanKind.INTERNAL: _SpanKind.INTERNAL,
}

_STATUS_CODE_MAPPINGS = {
    _StatusCode.OK: OpenTelemetryStatusCode.OK,
    _StatusCode.ERROR: OpenTelemetryStatusCode.ERROR,
    _StatusCode.UNSET: OpenTelemetryStatusCode.UNSET,
}


class OpenTelemetrySpan:
    """OpenTelemetry-based tracing span for client libraries.

    :param span: The OpenTelemetry span to wrap.
    :type span: ~opentelemetry.trace.Span
    """

    def __init__(self, *, span: Span) -> None:
        self._span_instance = span
        self._context_tokens: List[object] = []
        self._current_ctxt_manager: Optional[ContextManager[Span]] = None

    @property
    def kind(self) -> Optional[_SpanKind]:
        """Get the span kind of this span.

        :rtype: ~azure.core.tracing.SpanKind
        """
        try:
            value = self.span_instance.kind  # type: ignore[attr-defined]
        except AttributeError:
            return None
        return _OTEL_KIND_MAPPINGS.get(value)

    @property
    def span_instance(self) -> Span:
        """Returns the span the class is wrapping.

        :rtype: ~opentelemetry.trace.Span
        """
        return self._span_instance

    def __enter__(self) -> Self:
        # Determine if span recording should be suppressed.
        if not isinstance(self.span_instance, NonRecordingSpan):
            if self.kind == _SpanKind.INTERNAL:
                # Suppress INTERNAL spans within this context.
                self._context_tokens.append(
                    otel_context_module.attach(otel_context_module.set_value(_SUPPRESSED_SPAN_FLAG, True))
                )

            # Since the span is not suppressed, let's keep a reference to it in the context so that children spans
            # always have access to the last non-suppressed parent span.
            self._context_tokens.append(
                otel_context_module.attach(otel_context_module.set_value(_LAST_UNSUPPRESSED_SPAN, self))
            )

        # Activate the span in the current context.
        self._current_ctxt_manager = trace.use_span(self.span_instance, end_on_exit=True)  # type: ignore[attr-defined]
        if self._current_ctxt_manager:
            self._current_ctxt_manager.__enter__()
        return self

    def __exit__(
        self,
        exception_type: Optional[Type[BaseException]],
        exception_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        """Finish a span's context manager and calls end() on the span.

        :param exception_type: The type of the exception
        :type exception_type: type
        :param exception_value: The value of the exception
        :type exception_value: Exception
        :param traceback: The traceback of the exception
        :type traceback: Traceback
        """
        # Finish the span.
        if exception_type:
            module = exception_type.__module__ if exception_type.__module__ != "builtins" else ""
            error_type = f"{module}.{exception_type.__qualname__}" if module else exception_type.__qualname__
            self.set_attribute(_ERROR_SPAN_ATTRIBUTE, error_type)

        if self._current_ctxt_manager:
            self._current_ctxt_manager.__exit__(exception_type, exception_value, traceback)
            self._current_ctxt_manager = None
        else:
            self.span_instance.end()

        while self._context_tokens:
            token = self._context_tokens.pop()
            otel_context_module.detach(token)

    def _suppress_auto_http_instrumentation(self) -> None:
        """Suppress automatic HTTP instrumentation.

        Since azure-core already instruments HTTP calls, we need to suppress any automatic HTTP
        instrumentation provided by other libraries to prevent duplicate spans. This has no effect if no
        automatic HTTP instrumentation libraries are being used.
        """
        self._context_tokens.append(
            otel_context_module.attach(otel_context_module.set_value(_SUPPRESS_HTTP_INSTRUMENTATION_KEY, True))
        )

    def end(self) -> None:
        """Set the end time for a span."""
        self.span_instance.end()
        while self._context_tokens:
            token = self._context_tokens.pop()
            otel_context_module.detach(token)

    def set_attribute(self, key: str, value: AttributeValue) -> None:
        """Set an attribute (key-value pair) to the current span.

        :param key: The key of the key value pair
        :type key: str
        :param value: The value of the key value pair
        :type value: Union[str, int, bool, float, Sequence[str], Sequence[int], Sequence[bool], Sequence[float]]
        """
        self.span_instance.set_attribute(key, value)

    def set_status(self, status_code: _StatusCode, description: Optional[str] = None) -> None:
        """Set the status of the span.

        :param status_code: The status code of the span
        :type status_code: ~azure.core.tracing.StatusCode
        :param description: A description of the status if needed.
        :type description: str
        """
        otel_status_code = _STATUS_CODE_MAPPINGS.get(status_code, OpenTelemetryStatusCode.UNSET)
        self.span_instance.set_status(otel_status_code, description)

    def add_event(
        self,
        name: str,
        attributes: Optional[Attributes] = None,
        timestamp: Optional[int] = None,
    ) -> None:
        """Add an event to the span.

        :param name: The name of the event
        :type name: str
        :param attributes: Any additional attributes that should be added to the event
        :type attributes: Mapping[str, AttributeValue]
        :param timestamp: The timestamp of the event
        :type timestamp: int
        """
        self.span_instance.add_event(name, attributes=attributes, timestamp=timestamp)


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
        kind: _SpanKind = _SpanKind.INTERNAL,
        attributes: Optional[Attributes] = None,
        links: Optional[Sequence[_Link]] = None,
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
        )
        return OpenTelemetrySpan(span=otel_span)

    def _parse_links(self, links: Optional[Sequence[_Link]]) -> Optional[Sequence[OpenTelemetryLink]]:
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
        :rtype: ~azure.core.tracing.opentelemetry.OpenTelemetrySpan
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
