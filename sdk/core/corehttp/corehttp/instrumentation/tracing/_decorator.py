# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""The decorator to apply if you want the given method traced."""
from contextvars import ContextVar
import functools
from typing import Awaitable, Any, TypeVar, overload, Optional, Callable, TYPE_CHECKING
from typing_extensions import ParamSpec

from ._models import SpanKind
from ._tracer import get_tracer
from ...settings import settings

if TYPE_CHECKING:
    from ._models import TracingOptions


P = ParamSpec("P")
T = TypeVar("T")


# This context variable is used to determine if we are already in the span context of a decorated function.
_in_span_context = ContextVar("in_span_context", default=False)


@overload
def distributed_trace(__func: Callable[P, T]) -> Callable[P, T]:
    pass


@overload
def distributed_trace(**kwargs: Any) -> Callable[[Callable[P, T]], Callable[P, T]]:
    pass


def distributed_trace(__func: Optional[Callable[P, T]] = None, **kwargs: Any) -> Any:  # pylint: disable=unused-argument
    """Decorator to apply to an SDK method to have it traced automatically.

    Span will use the method's qualified name.

    Note: This decorator SHOULD NOT be used by application developers. It's intended to be called by client
    libraries only. Application developers should use OpenTelemetry directly to instrument their applications.

    :param callable __func: A function to decorate

    :return: The decorated function
    :rtype: Any
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:

        @functools.wraps(func)
        def wrapper_use_tracer(*args: Any, **kwargs: Any) -> T:
            # If we are already in the span context of a decorated function, don't trace.
            if _in_span_context.get():
                return func(*args, **kwargs)

            # This will be popped in the pipeline or transport runner.
            tracing_options: TracingOptions = kwargs.get("tracing_options", {})

            # User can explicitly disable tracing for this call
            user_enabled = tracing_options.get("enabled")
            if user_enabled is False:
                return func(*args, **kwargs)

            # If tracing is disabled globally and user didn't explicitly enable it, don't trace.
            if not settings.tracing_enabled and user_enabled is None:
                return func(*args, **kwargs)

            config = {}
            if args and hasattr(args[0], "_instrumentation_config"):
                config = args[0]._instrumentation_config  # pylint: disable=protected-access

            method_tracer = get_tracer(
                library_name=config.get("library_name"),
                library_version=config.get("library_version"),
                schema_url=config.get("schema_url"),
                attributes=config.get("attributes"),
            )
            if not method_tracer:
                return func(*args, **kwargs)

            name = func.__qualname__
            span_suppression_token = _in_span_context.set(True)
            try:
                with method_tracer.start_as_current_span(
                    name=name,
                    kind=SpanKind.INTERNAL,
                    attributes=tracing_options.get("attributes"),
                ) as span:
                    try:
                        return func(*args, **kwargs)
                    except Exception as err:  # pylint: disable=broad-except
                        ex_type = type(err)
                        module = ex_type.__module__ if ex_type.__module__ != "builtins" else ""
                        error_type = f"{module}.{ex_type.__qualname__}" if module else ex_type.__qualname__
                        span.set_attribute("error.type", error_type)
                        raise
            finally:
                _in_span_context.reset(span_suppression_token)

        return wrapper_use_tracer

    return decorator if __func is None else decorator(__func)


@overload
def distributed_trace_async(__func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
    pass


@overload
def distributed_trace_async(**kwargs: Any) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    pass


def distributed_trace_async(  # pylint: disable=unused-argument
    __func: Optional[Callable[P, Awaitable[T]]] = None,
    **kwargs: Any,
) -> Any:
    """Decorator to apply to an SDK method to have it traced automatically.

    Span will use the method's qualified name.

    Note: This decorator SHOULD NOT be used by application developers. It's intended to be called by client
    libraries only. Application developers should use OpenTelemetry directly to instrument their applications.

    :param callable __func: A function to decorate

    :return: The decorated function
    :rtype: Any
    """

    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:

        @functools.wraps(func)
        async def wrapper_use_tracer(*args: Any, **kwargs: Any) -> T:
            # If we are already in the span context of a decorated function, don't trace.
            if _in_span_context.get():
                return await func(*args, **kwargs)

            # This will be popped in the pipeline or transport runner.
            tracing_options: TracingOptions = kwargs.get("tracing_options", {})

            # User can explicitly disable tracing for this call
            user_enabled = tracing_options.get("enabled")
            if user_enabled is False:
                return await func(*args, **kwargs)

            # If tracing is disabled globally and user didn't explicitly enable it, don't trace.
            if not settings.tracing_enabled and user_enabled is None:
                return await func(*args, **kwargs)

            config = {}
            if args and hasattr(args[0], "_instrumentation_config"):
                config = args[0]._instrumentation_config  # pylint: disable=protected-access

            method_tracer = get_tracer(
                library_name=config.get("library_name"),
                library_version=config.get("library_version"),
                schema_url=config.get("schema_url"),
                attributes=config.get("attributes"),
            )
            if not method_tracer:
                return await func(*args, **kwargs)

            name = func.__qualname__
            span_suppression_token = _in_span_context.set(True)
            try:
                with method_tracer.start_as_current_span(
                    name=name,
                    kind=SpanKind.INTERNAL,
                    attributes=tracing_options.get("attributes"),
                ) as span:
                    try:
                        return await func(*args, **kwargs)
                    except Exception as err:  # pylint: disable=broad-except
                        ex_type = type(err)
                        module = ex_type.__module__ if ex_type.__module__ != "builtins" else ""
                        error_type = f"{module}.{ex_type.__qualname__}" if module else ex_type.__qualname__
                        span.set_attribute("error.type", error_type)
                        raise
            finally:
                _in_span_context.reset(span_suppression_token)

        return wrapper_use_tracer

    return decorator if __func is None else decorator(__func)
