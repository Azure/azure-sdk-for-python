# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from opentelemetry import trace
import functools
import asyncio
from typing import Callable, Any

tracer = trace.get_tracer(__name__)

def sanitize_for_attributes(value) -> str:
    """
    Convert input value to a flat string representation.
  
    This function transforms complex data structures (e.g., lists, tuples,
    dictionaries) into a simple string format, ensuring that the attributes
    logged in OpenTelemetry are always in a compatible string format.

    :param value: The value to sanitize, which can be of any type.
    :return: The string representation of the input value.
    :rtype: str
    """
    if isinstance(value, (list, tuple)):
        # Convert the entire list or tuple to a flat string representation  
        return "[" + ", ".join(sanitize_for_attributes(v) for v in value) + "]"
    elif isinstance(value, dict):
        # Create a flat string representation of the dictionary
        return "{" + ", ".join(f"{k}: {sanitize_for_attributes(v)}" for k, v in value.items()) + "}"
    else:
        # Convert other values to string representation
        return str(value)

def trace_func(func) -> Callable:
    """  
    Decorator to trace function calls using OpenTelemetry.  
  
    This decorator captures the function's parameters, return values,   
    and exceptions, logging them as spans within OpenTelemetry. It   
    works with both synchronous and asynchronous functions.  
  
    :param func: The function to be decorated.
    :return: The wrapped function with tracing capabilities.
    :rtype: Callable
    """
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs) -> Any:
        """
        Wrapper function for asynchronous functions.
  
        :param args: Positional arguments passed to the function.
        :param kwargs: Keyword arguments passed to the function.
        :return: The result of the decorated asynchronous function.
        :rtype: Any
        """
        with tracer.start_as_current_span(func.__name__) as span:
            try:
                # Sanitize parameters and set them as attributes
                span.set_attributes({"params": sanitize_for_attributes(args),"kwargs": sanitize_for_attributes(kwargs),})
                result = await func(*args, **kwargs)
                span.set_attributes({"return": sanitize_for_attributes(result)})
                return result
            except Exception as e:
                span.record_exception(e)
                raise

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs) -> Any:
        """
        Wrapper function for synchronous functions.

        :param args: Positional arguments passed to the function.
        :param kwargs: Keyword arguments passed to the function.
        :return: The result of the decorated synchronous function.
        :rtype: Any
        """
        with tracer.start_as_current_span(func.__name__) as span:
            try:
                # Sanitize parameters and set them as attributes
                span.set_attributes({"params": sanitize_for_attributes(args),"kwargs": sanitize_for_attributes(kwargs),})
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
