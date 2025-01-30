# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""The decorator to apply if you want the given method traced."""
import functools
from typing import Awaitable, Any, TypeVar, overload, Optional, Callable
from typing_extensions import ParamSpec

from ._models import SpanKind, TracingOptions
from ._tracer import TracerProvider, default_tracer_provider
from ...settings import settings


P = ParamSpec("P")
T = TypeVar("T")


@overload
def distributed_trace(__func: Callable[P, T]) -> Callable[P, T]:
    pass


@overload
def distributed_trace(
    *,
    tracer_provider: Optional[TracerProvider] = None,
    **kwargs: Any,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    pass


def distributed_trace(
    __func: Optional[Callable[P, T]] = None,  # pylint: disable=unused-argument
    *,
    tracer_provider: Optional[TracerProvider] = None,
    **kwargs: Any,
) -> Any:
    """Decorator to apply to an SDK method to have it traced automatically.

    Span will use the method's qualified name.
    Note:

    This decorator SHOULD NOT be used by application developers. It's intended to be called by client libraries only.
    Application developers should use OpenTelemetry directly to instrument their applications.

    :param callable __func: A function to decorate
    :keyword tracer_provider: The tracer provider to use. If not provided, a default tracer provider will be used.
    :paramtype tracer_provider: ~corehttp.instrumentation.tracing.TracerProvider

    :return: The decorated function
    :rtype: Any
    """

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

            method_tracer = tracer_provider.get_tracer() if tracer_provider else default_tracer_provider.get_tracer()
            if not method_tracer:
                return func(*args, **kwargs)

            name = func.__qualname__
            with method_tracer.start_span(
                name=name,
                kind=SpanKind.INTERNAL,
                attributes=tracing_options.get("attributes"),
                record_exception=tracing_options.get("record_exception", True),
            ):
                return func(*args, **kwargs)

        return wrapper_use_tracer

    return decorator if __func is None else decorator(__func)


@overload
def distributed_trace_async(__func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
    pass


@overload
def distributed_trace_async(
    *,
    tracer_provider: Optional[TracerProvider] = None,
    **kwargs: Any,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    pass


def distributed_trace_async(  # pylint: disable=unused-argument
    __func: Optional[Callable[P, Awaitable[T]]] = None,
    *,
    tracer_provider: Optional[TracerProvider] = None,
    **kwargs: Any,
) -> Any:
    """Decorator to apply to an SDK method to have it traced automatically.

    Span will use the method's qualified name.

    Note:

    This decorator SHOULD NOT be used by application developers. It's intended to be called by client libraries only.
    Application developers should use OpenTelemetry directly to instrument their applications.

    :param callable __func: A function to decorate
    :keyword tracer_provider: The tracer provider to use. If not provided, a default tracer provider will be used.
    :paramtype tracer_provider: ~corehttp.instrumentation.tracing.TracerProvider
    :return: The decorated function
    :rtype: Any
    """

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

            method_tracer = tracer_provider.get_tracer() if tracer_provider else default_tracer_provider.get_tracer()
            if not method_tracer:
                return await func(*args, **kwargs)

            name = func.__qualname__
            with method_tracer.start_span(
                name=name,
                kind=SpanKind.INTERNAL,
                attributes=tracing_options.get("attributes"),
                record_exception=tracing_options.get("record_exception", True),
            ):
                return await func(*args, **kwargs)

        return wrapper_use_tracer

    return decorator if __func is None else decorator(__func)
