# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cspell:ignore otel
from typing import ContextManager, Optional, Type, List, Any
from types import TracebackType

from typing_extensions import Self
from opentelemetry import context as otel_context_module, trace
from opentelemetry.trace import (
    Span,
    NonRecordingSpan,
    SpanKind as OpenTelemetrySpanKind,
    StatusCode as OpenTelemetryStatusCode,
)  # type: ignore[attr-defined]

try:
    from opentelemetry.context import _SUPPRESS_HTTP_INSTRUMENTATION_KEY  # type: ignore[attr-defined]
except ImportError:
    _SUPPRESS_HTTP_INSTRUMENTATION_KEY = "suppress_http_instrumentation"

from ._models import Attributes, AttributeValue, SpanKind, StatusCode


_SUPPRESSED_SPAN_FLAG = "SUPPRESSED_SPAN_FLAG"
_LAST_UNSUPPRESSED_SPAN = "LAST_UNSUPPRESSED_SPAN"
_ERROR_SPAN_ATTRIBUTE = "error.type"

_OTEL_KIND_MAPPINGS = {
    OpenTelemetrySpanKind.CLIENT: SpanKind.CLIENT,
    OpenTelemetrySpanKind.CONSUMER: SpanKind.CONSUMER,
    OpenTelemetrySpanKind.PRODUCER: SpanKind.PRODUCER,
    OpenTelemetrySpanKind.SERVER: SpanKind.SERVER,
    OpenTelemetrySpanKind.INTERNAL: SpanKind.INTERNAL,
}

_STATUS_CODE_MAPPINGS = {
    StatusCode.OK: OpenTelemetryStatusCode.OK,
    StatusCode.ERROR: OpenTelemetryStatusCode.ERROR,
    StatusCode.UNSET: OpenTelemetryStatusCode.UNSET,
}


class OpenTelemetrySpan:
    """OpenTelemetry-based tracing span for client libraries.

    :param span: The OpenTelemetry span to wrap.
    :type span: ~opentelemetry.trace.Span
    """

    def __init__(self, *, span: Span, **kwargs: Any):
        self._span_instance = span
        self._context_tokens: List[object] = []
        self._current_ctxt_manager: Optional[ContextManager[Span]] = None
        self._record_exception = kwargs.get("_record_exception", True)

    @property
    def kind(self) -> Optional[SpanKind]:
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
            if self.kind == SpanKind.CLIENT:
                # Since azure-core already instruments HTTP calls, we need to suppress any automatic HTTP
                # instrumentation provided by other libraries to prevent duplicate spans. This has no effect if no
                # automatic HTTP instrumentation libraries are being used.
                self._context_tokens.append(
                    otel_context_module.attach(otel_context_module.set_value(_SUPPRESS_HTTP_INSTRUMENTATION_KEY, True))
                )
            elif self.kind == SpanKind.INTERNAL:
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
        self._current_ctxt_manager = trace.use_span(
            self.span_instance, record_exception=self._record_exception, end_on_exit=True  # type: ignore[attr-defined]
        )
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
            if self._record_exception and exception_value:
                self.span_instance.record_exception(exception_value)
            self.end()

        for token in self._context_tokens:
            otel_context_module.detach(token)
            self._context_tokens.remove(token)

    def end(self) -> None:
        """Set the end time for a span."""
        self.span_instance.end()
        for token in self._context_tokens:
            otel_context_module.detach(token)
            self._context_tokens.remove(token)

    def set_attribute(self, key: str, value: AttributeValue) -> None:
        """Set an attribute (key-value pair) to the current span.

        :param key: The key of the key value pair
        :type key: str
        :param value: The value of the key value pair
        :type value: Union[str, int, bool, float, Sequence[str], Sequence[int], Sequence[bool], Sequence[float]]
        """
        self.span_instance.set_attribute(key, value)

    def set_status(self, status_code: StatusCode, description: Optional[str] = None) -> None:
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
