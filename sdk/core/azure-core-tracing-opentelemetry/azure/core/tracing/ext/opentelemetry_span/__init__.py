# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Implements azure.core.tracing.AbstractSpan to wrap OpenTelemetry spans."""
from typing import Any, ContextManager, Dict, Optional, Union, Callable, Sequence, cast, List
import warnings

from opentelemetry import context, trace
from opentelemetry.trace import (
    Span,
    Status,
    StatusCode,
    Tracer,
    NonRecordingSpan,
    SpanKind as OpenTelemetrySpanKind,
    Link as OpenTelemetryLink,
)  # type: ignore[attr-defined]
from opentelemetry.propagate import extract, inject  # type: ignore[attr-defined]
from opentelemetry.trace.propagation import get_current_span as get_span_from_context  # type: ignore[attr-defined]

# TODO: Fix import of this private attribute once the location of the suppress instrumentation key is defined.
try:
    from opentelemetry.context import _SUPPRESS_HTTP_INSTRUMENTATION_KEY  # type: ignore[attr-defined]
except ImportError:
    _SUPPRESS_HTTP_INSTRUMENTATION_KEY = "suppress_http_instrumentation"

from azure.core.tracing import SpanKind, HttpSpanMixin, Link as CoreLink  # type: ignore[attr-defined] # pylint: disable=no-name-in-module

from ._schema import OpenTelemetrySchema, OpenTelemetrySchemaVersion as _OpenTelemetrySchemaVersion
from ._version import VERSION

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
Attributes = Dict[str, AttributeValue]

__version__ = VERSION

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

_SPAN_KIND_MAPPINGS = {
    SpanKind.CLIENT: OpenTelemetrySpanKind.CLIENT,
    SpanKind.CONSUMER: OpenTelemetrySpanKind.CONSUMER,
    SpanKind.PRODUCER: OpenTelemetrySpanKind.PRODUCER,
    SpanKind.SERVER: OpenTelemetrySpanKind.SERVER,
    SpanKind.INTERNAL: OpenTelemetrySpanKind.INTERNAL,
    SpanKind.UNSPECIFIED: OpenTelemetrySpanKind.INTERNAL,
}


class _SuppressionContextManager(ContextManager):
    def __init__(self, span: "OpenTelemetrySpan"):
        self._span = span
        self._context_token: Optional[object] = None
        self._current_ctxt_manager: Optional[ContextManager[Span]] = None

    def __enter__(self) -> Any:
        ctx = context.get_current()
        if not isinstance(self._span.span_instance, NonRecordingSpan):
            if self._span.kind in (SpanKind.INTERNAL, SpanKind.CLIENT, SpanKind.PRODUCER):
                # This is a client call that's reported for SDK service method.
                # We're going to suppress all nested spans reported in the context of this call.
                # We're not suppressing anything in the scope of SERVER or CONSUMER spans because
                # those wrap user code which may do HTTP requests and call other SDKs.
                ctx = context.set_value(_SUPPRESSED_SPAN_FLAG, True, ctx)
                # Since core already instruments HTTP calls, we need to suppress any automatic HTTP instrumentation
                # provided by other libraries to prevent duplicate spans. This has no effect if no automatic HTTP
                # instrumentation libraries are being used.
                ctx = context.set_value(_SUPPRESS_HTTP_INSTRUMENTATION_KEY, True, ctx)

            # Since the span is not suppressed, let's keep a reference to it in the context so that children spans
            # always have access to the last non-suppressed parent span.
            ctx = context.set_value(_LAST_UNSUPPRESSED_SPAN, self._span, ctx)
            ctx = trace.set_span_in_context(self._span._span_instance, ctx)
            self._context_token = context.attach(ctx)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._context_token:
            context.detach(self._context_token)
            self._context_token = None


class OpenTelemetrySpan(HttpSpanMixin, object):
    """OpenTelemetry plugin for Azure client libraries.

    :param span: The OpenTelemetry span to wrap, or nothing to create a new one.
    :type span: ~OpenTelemetry.trace.Span
    :param name: The name of the OpenTelemetry span to create if a new span is needed
    :type name: str
    :keyword kind: The span kind of this span.
    :paramtype kind: ~azure.core.tracing.SpanKind
    :keyword links: The list of links to be added to the span.
    :paramtype links: list[~azure.core.tracing.Link]
    :keyword context: Context headers of parent span that should be used when creating a new span.
    :paramtype context: Dict[str, str]
    :keyword schema_version: The OpenTelemetry schema version to use for the span.
    :paramtype schema_version: str
    """

    def __init__(
        self,
        span: Optional[Span] = None,
        name: Optional[str] = "span",
        *,
        kind: Optional["SpanKind"] = None,
        links: Optional[List["CoreLink"]] = None,
        **kwargs: Any,
    ) -> None:
        self._current_ctxt_manager: Optional[_SuppressionContextManager] = None
        self._schema_version = kwargs.pop("schema_version", _OpenTelemetrySchemaVersion.V1_19_0)
        self._attribute_mappings = OpenTelemetrySchema.get_attribute_mappings(self._schema_version)

        if span:
            self._span_instance = span
            return

        ## kind
        span_kind = kind
        otel_kind = _SPAN_KIND_MAPPINGS.get(span_kind)

        if span_kind and otel_kind is None:
            raise ValueError("Kind {} is not supported in OpenTelemetry".format(span_kind))

        if otel_kind == OpenTelemetrySpanKind.INTERNAL and context.get_value(_SUPPRESSED_SPAN_FLAG):
            # Nested internal calls should be suppressed per the Azure SDK guidelines.
            self._span_instance = NonRecordingSpan(context=self.get_current_span().get_span_context())
            return

        current_tracer = trace.get_tracer(
            __name__,
            __version__,
            schema_url=OpenTelemetrySchema.get_schema_url(self._schema_version),
        )

        if links:
            try:
                ot_links = []
                for link in links:
                    ctx = extract(link.headers)
                    span_ctx = get_span_from_context(ctx).get_span_context()
                    ot_links.append(OpenTelemetryLink(span_ctx, link.attributes))
                kwargs.setdefault("links", ot_links)
            except AttributeError:
                # We will just send the links as is if it's not ~azure.core.tracing.Link without any validation
                # assuming user knows what they are doing.
                kwargs.setdefault("links", links)

        parent_context = kwargs.pop("context", None)
        if parent_context:
            # Create OpenTelemetry Context object from dict.
            kwargs["context"] = extract(parent_context)

        self._span_instance = current_tracer.start_span(name=name, kind=otel_kind, **kwargs)  # type: ignore

    @property
    def span_instance(self) -> Span:
        """The OpenTelemetry span that is being wrapped.

        :rtype: ~openTelemetry.trace.Span
        """
        return self._span_instance

    def span(
        self,
        name: str = "span",
        *,
        kind: Optional["SpanKind"] = None,
        links: Optional[List["CoreLink"]] = None,
        **kwargs: Any,
    ) -> "OpenTelemetrySpan":
        """Create a child span for the current span and return it.

        :param name: Name of the child span
        :type name: str
        :keyword kind: The span kind of this span.
        :paramtype kind: ~azure.core.tracing.SpanKind
        :keyword links: The list of links to be added to the span.
        :paramtype links: list[Link]
        :return: The OpenTelemetrySpan that is wrapping the child span instance.
        :rtype: ~azure.core.tracing.ext.opentelemetry_span.OpenTelemetrySpan
        """
        return self.__class__(name=name, kind=kind, links=links, **kwargs)

    @property
    def kind(self) -> Optional[SpanKind]:
        """Get the span kind of this span."""
        try:
            value = self.span_instance.kind  # type: ignore[attr-defined]
        except AttributeError:
            return None
        return _OTEL_KIND_MAPPINGS.get(value)

    @kind.setter
    def kind(self, value: SpanKind) -> None:
        """Set the span kind of this span.

        :param value: The span kind to set.
        :type value: ~azure.core.tracing.SpanKind
        """
        kind = _SPAN_KIND_MAPPINGS.get(value)
        if kind is None:
            raise ValueError("Kind {} is not supported in OpenTelemetry".format(value))
        try:
            self._span_instance._kind = kind  # type: ignore[attr-defined] # pylint: disable=protected-access
        except AttributeError:
            warnings.warn(
                """Kind must be set while creating the span for OpenTelemetry. It might be possible
                that one of the packages you are using doesn't follow the latest Opentelemetry Spec.
                Try updating the azure packages to the latest versions."""
            )

    def __enter__(self) -> "OpenTelemetrySpan":
        self._current_ctxt_manager = _SuppressionContextManager(self)
        self._current_ctxt_manager.__enter__()
        return self

    def __exit__(self, exception_type, exception_value, traceback) -> None:
        # Finish the span.
        if exception_type:
            module = exception_type.__module__ if exception_type.__module__ != "builtins" else ""
            error_type = f"{module}.{exception_type.__qualname__}" if module else exception_type.__qualname__
            self.add_attribute(_ERROR_SPAN_ATTRIBUTE, error_type)

            self.span_instance.set_status(
                Status(
                    status_code=StatusCode.ERROR,
                    description=f"{error_type}: {exception_value}",
                )
            )

        self.finish()

        # end the context manager.
        if self._current_ctxt_manager:
            self._current_ctxt_manager.__exit__(exception_type, exception_value, traceback)
            self._current_ctxt_manager = None

    def start(self) -> None:
        # Spans are automatically started at their creation with OpenTelemetry.
        pass

    def finish(self) -> None:
        """Set the end time for a span."""
        self.span_instance.end()

    def to_header(self) -> Dict[str, str]:
        """Returns a dictionary with the context header labels and values.

        These are generally the W3C Trace Context headers (i.e. "traceparent" and "tracestate").

        :return: A key value pair dictionary
        :rtype: dict[str, str]
        """
        temp_headers: Dict[str, str] = {}
        inject(temp_headers)
        return temp_headers

    def add_attribute(self, key: str, value: Union[str, int]) -> None:
        """Add attribute (key value pair) to the current span.

        :param key: The key of the key value pair
        :type key: str
        :param value: The value of the key value pair
        :type value: Union[str, int]
        """
        key = self._attribute_mappings.get(key, key)
        self.span_instance.set_attribute(key, value)

    def get_trace_parent(self) -> str:
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
    def link(cls, traceparent: str, attributes: Optional[Attributes] = None) -> None:
        """Links the context to the current tracer.

        :param traceparent: A complete traceparent
        :type traceparent: str
        :param attributes: Attributes to be added to the link
        :type attributes: dict or None
        """
        cls.link_from_headers({"traceparent": traceparent}, attributes)

    @classmethod
    def link_from_headers(cls, headers: Dict[str, str], attributes: Optional[Attributes] = None) -> None:
        """Given a dictionary, extracts the context and links the context to the current tracer.

        :param headers: A key value pair dictionary
        :type headers: dict
        :param attributes: Attributes to be added to the link
        :type attributes: dict or None
        """
        ctx = extract(headers)
        span_ctx = get_span_from_context(ctx).get_span_context()
        current_span = cls.get_current_span()
        try:
            current_span._links.append(OpenTelemetryLink(span_ctx, attributes))  # type: ignore # pylint: disable=protected-access
        except AttributeError:
            warnings.warn(
                """Link must be added while creating the span for OpenTelemetry. It might be possible
                that one of the packages you are using doesn't follow the latest Opentelemetry Spec.
                Try updating the azure packages to the latest versions."""
            )

    @classmethod
    def get_current_span(cls) -> Span:
        """Get the current span from the execution context.

        :return: The current span
        :rtype: ~opentelemetry.trace.Span
        """
        span = get_span_from_context()
        last_unsuppressed_parent = context.get_value(_LAST_UNSUPPRESSED_SPAN)
        if isinstance(span, NonRecordingSpan) and last_unsuppressed_parent:
            return cast(OpenTelemetrySpan, last_unsuppressed_parent).span_instance
        return span

    @classmethod
    def get_current_tracer(cls) -> Tracer:
        """Get the current tracer from the execution context.

        :return: The current tracer
        :rtype: ~opentelemetry.trace.Tracer
        """
        return trace.get_tracer(__name__, __version__)

    @classmethod
    def change_context(cls, span: Union[Span, "OpenTelemetrySpan"]) -> ContextManager:
        """Change the context for the life of this context manager.

        :param span: The span to use as the current span
        :type span: ~opentelemetry.trace.Span
        :return: A context manager to use for the duration of the span
        :rtype: contextmanager
        """

        if isinstance(span, Span):
            return trace.use_span(span, end_on_exit=False)

        return _SuppressionContextManager(span)

    @classmethod
    def set_current_span(cls, span: Span) -> None:  # pylint: disable=docstring-missing-return,docstring-missing-rtype
        """Not supported by OpenTelemetry.

        :param span: The span to set as the current span
        :type span: ~opentelemetry.trace.Span
        :raises: NotImplementedError
        """
        raise NotImplementedError(
            "set_current_span is not supported by OpenTelemetry plugin. Use change_context instead."
        )

    @classmethod
    def set_current_tracer(cls, tracer: Tracer) -> None:  # pylint: disable=unused-argument
        """Not supported by OpenTelemetry.

        :param tracer: The tracer to set the current tracer as
        :type tracer: ~opentelemetry.trace.Tracer
        """
        # Do nothing, if you're able to get two tracer with OpenTelemetry that's a surprise!
        return

    @classmethod
    def with_current_context(cls, func: Callable) -> Callable:
        """Passes the current spans to the new context the function will be run in.

        :param func: The function that will be run in the new context
        :type func: callable
        :return: The target the pass in instead of the function
        :rtype: callable
        """
        # returns the current Context object
        current_context = context.get_current()

        def call_with_current_context(*args, **kwargs):
            token = None
            try:
                token = context.attach(current_context)
                return func(*args, **kwargs)
            finally:
                if token is not None:
                    context.detach(token)

        return call_with_current_context
