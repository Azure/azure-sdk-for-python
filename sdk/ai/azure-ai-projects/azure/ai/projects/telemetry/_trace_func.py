# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import asyncio
from typing import Any, Callable, Tuple, Optional, Dict, List
from opentelemetry import trace as opentelemetry_trace

tracer = opentelemetry_trace.get_tracer(__name__)


def trace_function(span_name: Optional[str] = None):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            """
            Wrapper function for asynchronous functions.

            :param args: Positional arguments passed to the function.
            :type args: Tuple[Any]
            :return: The result of the decorated asynchronous function.
            :rtype: Any
            """
            name = span_name if span_name else func.__name__
            with tracer.start_as_current_span(name) as span:
                try:
                    # Sanitize parameters and set them as attributes
                    sanitized_params = sanitize_parameters(func, *args, **kwargs)
                    span.set_attributes(sanitized_params)
                    result = await func(*args, **kwargs)
                    sanitized_result = sanitize_for_attributes(result)
                    if sanitized_result is not None:
                        span.set_attributes({"return": sanitized_result})
                    return result
                except Exception as e:
                    span.record_exception(e)
                    raise

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            """
            Wrapper function for synchronous functions.

            :param args: Positional arguments passed to the function.
            :type args: Tuple[Any]
            :return: The result of the decorated synchronous function.
            :rtype: Any
            """
            name = span_name if span_name else func.__name__
            with tracer.start_as_current_span(name) as span:
                try:
                    # Sanitize parameters and set them as attributes
                    sanitized_params = sanitize_parameters(func, *args, **kwargs)
                    span.set_attributes(sanitized_params)
                    result = func(*args, **kwargs)
                    sanitized_result = sanitize_for_attributes(result)
                    if sanitized_result is not None:
                        span.set_attributes({"return": sanitized_result})
                    return result
                except Exception as e:
                    span.record_exception(e)
                    raise

        # Determine if the function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def sanitize_parameters(func, *args, **kwargs) -> Dict[str, Any]:
    """
    Sanitize function parameters to include only built-in data types.

    :param func: The function being decorated.
    :param args: Positional arguments passed to the function.
    :param kwargs: Keyword arguments passed to the function.
    :return: A dictionary of sanitized parameters.
    """
    import inspect

    params = inspect.signature(func).parameters
    sanitized_params = {}

    for i, (name, param) in enumerate(params.items()):
        if param.default == inspect.Parameter.empty and i < len(args):
            value = args[i]
        else:
            value = kwargs.get(name, param.default)

        if isinstance(value, (str, int, bool, float)):
            sanitized_params[name] = value
        elif isinstance(value, (list, dict, tuple, set)):
            if all(isinstance(item, (str, int, bool, float)) for item in value):
                sanitized_params[name] = value

    return sanitized_params


def sanitize_for_attributes(value: Any) -> Any:
    """
    Sanitize a value to be used as an attribute.

    :param value: The value to sanitize.
    :return: The sanitized value or None if the value is not a supported type.
    """
    if isinstance(value, (str, int, float, bool)):
        return value
    elif isinstance(value, list):
        return [sanitize_for_attributes(item) for item in value if isinstance(item, (str, int, float, bool))]
    elif isinstance(value, dict):
        return {k: sanitize_for_attributes(v) for k, v in value.items() if isinstance(v, (str, int, float, bool))}
    elif isinstance(value, tuple):
        return tuple(sanitize_for_attributes(item) for item in value if isinstance(item, (str, int, float, bool)))
    elif isinstance(value, set):
        return {sanitize_for_attributes(item) for item in value if isinstance(item, (str, int, float, bool))}
    return None