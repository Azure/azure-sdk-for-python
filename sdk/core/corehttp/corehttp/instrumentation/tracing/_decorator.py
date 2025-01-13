# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""The decorator to apply if you want the given method traced."""
import functools
from typing import Awaitable, Any, TypeVar, overload, Optional, Mapping, Callable, TYPE_CHECKING
from typing_extensions import ParamSpec

from ._models import SpanKind, TracingOptions
from ._tracer import default_tracer_manager
from ...settings import settings

if TYPE_CHECKING:
    from .opentelemetry_tracer import OpenTelemetryTracer
    from .opentelemetry_span import OpenTelemetrySpan


P = ParamSpec("P")
T = TypeVar("T")


@overload
def distributed_trace(__func: Callable[P, T]) -> Callable[P, T]:
    pass


@overload
def distributed_trace(
    *,
    name_of_span: Optional[str] = None,
    kind: Optional[SpanKind] = None,
    tracing_attributes: Optional[Mapping[str, Any]] = None,
    tracer: Optional["OpenTelemetryTracer"] = None,
    pre_hook: Optional[Callable[["OpenTelemetrySpan", Any, Any], Any]] = None,
    post_hook: Optional[Callable[["OpenTelemetrySpan", Any], Any]] = None,
    **kwargs: Any,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    pass


def distributed_trace(
    __func: Optional[Callable[P, T]] = None,  # pylint: disable=unused-argument
    *,
    name_of_span: Optional[str] = None,
    kind: Optional[SpanKind] = None,
    tracer: Optional["OpenTelemetryTracer"] = None,
    pre_hook: Optional[Callable[["OpenTelemetrySpan", Any, Any], Any]] = None,
    post_hook: Optional[Callable[["OpenTelemetrySpan", Any], Any]] = None,
    **kwargs: Any,
) -> Any:
    """Decorator to apply to an SDK method to have it traced automatically.

    Span will use the method's qualified name or "name_of_span".

    Note:

    This decorator SHOULD NOT be used by application developers. It's intended to be called by client libraries only.
    Application developers should use OpenTelemetry directly to instrument their applications.

    :param callable __func: A function to decorate
    :keyword name_of_span: The span name to replace func name if necessary
    :paramtype name_of_span: str
    :keyword kind: The kind of the span. INTERNAL by default.
    :paramtype kind: ~corehttp.instrumentation.tracing.SpanKind
    :keyword tracer: The tracer to use. If not provided, a default tracer will be used.
    :paramtype tracer: ~corehttp.instrumentation.tracing.Tracer
    :keyword pre_hook: A hook to run before the span is created. This hook can modify the span attributes.
    :paramtype pre_hook: Callable[["OpenTelemetrySpan", Any, Any], Any]
    :keyword post_hook: A hook to run after the span is created. This hook can modify the span attributes.
    :paramtype post_hook: Callable[["OpenTelemetrySpan", Any], Any]
    :return: The decorated function
    :rtype: Any
    """
    if kind is None:
        kind = SpanKind.INTERNAL

    def decorator(func: Callable[P, T]) -> Callable[P, T]:

        @functools.wraps(func)
        def wrapper_use_tracer(*args: Any, **kwargs: Any) -> T:
            # Assume this will be popped in DistributedTracingPolicy.
            tracing_options: TracingOptions = kwargs.get("tracing_options", {})

            # User can explicitly disable tracing for this call
            user_enabled = tracing_options.get("enabled")
            if user_enabled is False:
                return func(*args, **kwargs)

            # If tracing is disabled globally and user didn't explicitly enable it, don't trace.
            if not settings.tracing_enabled and user_enabled is None:
                return func(*args, **kwargs)

            method_tracer = tracer or default_tracer_manager.tracer
            if not method_tracer:
                return func(*args, **kwargs)

            name = name_of_span or func.__qualname__
            with method_tracer.start_span(
                name=name,
                kind=kind,
                attributes=tracing_options.get("attributes"),
                record_exception=tracing_options.get("record_exception", True),
            ) as span:
                if pre_hook:
                    pre_hook(span, *args, **kwargs)

                result = func(*args, **kwargs)

                if post_hook:
                    post_hook(span, result)

                return result

        return wrapper_use_tracer

    return decorator if __func is None else decorator(__func)


@overload
def distributed_trace_async(__func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
    pass


@overload
def distributed_trace_async(
    *,
    name_of_span: Optional[str] = None,
    kind: Optional[SpanKind] = None,
    tracer: Optional["OpenTelemetryTracer"] = None,
    pre_hook: Optional[Callable[["OpenTelemetrySpan", Any, Any], Any]] = None,
    post_hook: Optional[Callable[["OpenTelemetrySpan", Any], Any]] = None,
    **kwargs: Any,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    pass


def distributed_trace_async(  # pylint: disable=unused-argument
    __func: Optional[Callable[P, Awaitable[T]]] = None,
    *,
    name_of_span: Optional[str] = None,
    kind: Optional[SpanKind] = None,
    tracer: Optional["OpenTelemetryTracer"] = None,
    pre_hook: Optional[Callable[["OpenTelemetrySpan", Any, Any], Any]] = None,
    post_hook: Optional[Callable[["OpenTelemetrySpan", Any], Any]] = None,
    **kwargs: Any,
) -> Any:
    """Decorator to apply to an SDK method to have it traced automatically.

    Span will use the method's qualified name or "name_of_span".

    Note:

    This decorator SHOULD NOT be used by application developers. It's intended to be called by client libraries only.
    Application developers should use OpenTelemetry directly to instrument their applications.

    :param callable __func: A function to decorate
    :keyword name_of_span: The span name to replace func name if necessary
    :paramtype name_of_span: str
    :keyword kind: The kind of the span. INTERNAL by default.
    :paramtype kind: ~corehttp.instrumentation.tracing.SpanKind
    :keyword tracer: The tracer to use. If not provided, a default tracer will be used.
    :paramtype tracer: ~corehttp.instrumentation.tracing.Tracer
    :keyword pre_hook: A hook to run before the span is created. This hook can modify the span attributes.
    :paramtype pre_hook: Callable[["OpenTelemetrySpan", Any, Any], Any]
    :keyword post_hook: A hook to run after the span is created. This hook can modify the span attributes.
    :paramtype post_hook: Callable[["OpenTelemetrySpan", Any], Any]
    :return: The decorated function
    :rtype: Any
    """
    if kind is None:
        kind = SpanKind.INTERNAL

    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:

        @functools.wraps(func)
        async def wrapper_use_tracer(*args: Any, **kwargs: Any) -> T:
            # Assume this will be popped in DistributedTracingPolicy.
            tracing_options: TracingOptions = kwargs.get("tracing_options", {})

            # User can explicitly disable tracing for this call
            user_enabled = tracing_options.get("enabled")
            if user_enabled is False:
                return await func(*args, **kwargs)

            # If tracing is disabled globally and user didn't explicitly enable it, don't trace.
            if not settings.tracing_enabled and user_enabled is None:
                return await func(*args, **kwargs)

            method_tracer = tracer or default_tracer_manager.tracer
            if not method_tracer:
                return await func(*args, **kwargs)

            name = name_of_span or func.__qualname__
            with method_tracer.start_span(
                name=name,
                kind=kind,
                attributes=tracing_options.get("attributes"),
                record_exception=tracing_options.get("record_exception", True),
            ) as span:
                if pre_hook:
                    pre_hook(span, *args, **kwargs)

                result = await func(*args, **kwargs)

                if post_hook:
                    post_hook(span, result)

                return result

        return wrapper_use_tracer

    return decorator if __func is None else decorator(__func)
