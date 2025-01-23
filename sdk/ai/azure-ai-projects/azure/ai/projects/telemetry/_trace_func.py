# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import asyncio
from typing import Any, Callable, Tuple
from opentelemetry import trace

tracer = trace.get_tracer(__name__)


def sanitize_for_attributes(value: Any) -> str:
    """
    Convert input value to a flat string representation.

    This function transforms complex data structures (e.g., lists, tuples,
    dictionaries) into a simple string format, ensuring that the attributes
    logged are always in a compatible string format.

    :param value: The value to sanitize, which can be of any type.
    :type value: Any
    :return: The string representation of the input value.
    :rtype: str
    """
    if isinstance(value, (list, tuple)):
        # Convert the entire list or tuple to a flat string representation
        return "[" + ", ".join(sanitize_for_attributes(v) for v in value) + "]"
    if isinstance(value, dict):
        # Create a flat string representation of the dictionary
        return "{" + ", ".join(f"{k}: {sanitize_for_attributes(v)}" for k, v in value.items()) + "}"
    # Convert other values to string representation
    return str(value)


def trace_func(func: Callable) -> Callable:
    """
    Decorator to trace function calls using OpenTelemetry.

    This decorator captures the function's parameters, return values,
    and exceptions, logging them as spans within OpenTelemetry. It
    works with both synchronous and asynchronous functions.

    Note that using the decorator will cause all the information mentioned
    above to be traced always when traces are enabled. The value of the
    AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED is not observed.

    :param func: The function to be decorated.
    :type func: Callable
    :return: The wrapped function with tracing capabilities.
    :rtype: Callable
    """

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs) -> Any:
        """
        Wrapper function for asynchronous functions.

        :param args: Positional arguments passed to the function.
        :type args: Tuple[Any]
        :return: The result of the decorated asynchronous function.
        :rtype: Any
        """
        with tracer.start_as_current_span(func.__name__) as span:
            try:
                # Sanitize parameters and set them as attributes
                span.set_attributes(
                    {
                        "params": sanitize_for_attributes(args),
                        "kwargs": sanitize_for_attributes(kwargs),
                    }
                )
                result = await func(*args, **kwargs)
                span.set_attributes({"return": sanitize_for_attributes(result)})
                return result
            except Exception as e:
                span.record_exception(e)
                raise

    @functools.wraps(func)
    def sync_wrapper(*args: Tuple[Any], **kwargs) -> Any:
        """
        Wrapper function for synchronous functions.

        :param args: Positional arguments passed to the function.
        :type args: Tuple[Any]
        :return: The result of the decorated synchronous function.
        :rtype: Any
        """
        with tracer.start_as_current_span(func.__name__) as span:
            try:
                # Sanitize parameters and set them as attributes
                span.set_attributes(
                    {
                        "params": sanitize_for_attributes(args),
                        "kwargs": sanitize_for_attributes(kwargs),
                    }
                )
                result = func(*args, **kwargs)
                span.set_attributes({"return": sanitize_for_attributes(result)})
                return result
            except Exception as e:
                span.record_exception(e)
                raise

    # Determine if the function is async
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper
