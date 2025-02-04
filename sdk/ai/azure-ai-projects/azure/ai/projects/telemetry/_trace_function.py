# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import asyncio
from typing import Any, Callable, Tuple, Optional, Dict, List

try:
    # pylint: disable = no-name-in-module
    from opentelemetry import trace as opentelemetry_trace
    tracer = opentelemetry_trace.get_tracer(__name__)
    _tracing_library_available = True
except ModuleNotFoundError:
    _tracing_library_available = False

if _tracing_library_available:
    def trace_function(span_name: Optional[str] = None):
        """
        A decorator for tracing function calls using OpenTelemetry.

        This decorator handles various data types for function parameters and return values, 
        and records them as attributes in the trace span. The supported data types include:
        - Basic data types: str, int, float, bool
        - Collections: list, dict, tuple, set

        Special handling for collections:
        - If a collection (list, dict, tuple, set) contains nested collections, the entire collection 
        is converted to a string before being recorded as an attribute.
        - Sets and dictionaries are always converted to strings to ensure compatibility with span attributes.

        Object types are omitted, and the corresponding parameter is not traced.

        Parameters:
        - span_name (Optional[str]): The name of the span. If not provided, the function name is used.

        Returns:
        - Callable: The decorated function with tracing enabled.

        Example usage:
        @trace_function("example_span")
        def example_function(a, b, c):
            return a + b + c
        """
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
                            if isinstance(sanitized_result, (list, dict, tuple, set)):
                                if any(isinstance(i, (list, dict, tuple, set)) for i in sanitized_result):
                                    sanitized_result = str(sanitized_result)  
                            span.set_attributes({"code.function.return.value": sanitized_result})
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
                            if isinstance(sanitized_result, (list, dict, tuple, set)):
                                if any(isinstance(i, (list, dict, tuple, set)) for i in sanitized_result):
                                    sanitized_result = str(sanitized_result)  
                            span.set_attributes({"code.function.return.value": sanitized_result})
                        return result
                    except Exception as e:
                        span.record_exception(e)
                        raise

            # Determine if the function is async
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            return sync_wrapper

        return decorator
else:
    # Define a no-op decorator if OpenTelemetry is not available
    def trace_function(span_name: Optional[str] = None):
        """
        A no-op decorator for tracing function calls when OpenTelemetry is not available.

        Parameters:
        - span_name (Optional[str]): The name of the span. If not provided, the function name is used.

        Returns:
        - Callable: The original function without tracing.
        """
        def decorator(func: Callable) -> Callable:
            return func

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

        sanitized_value = sanitize_for_attributes(value)
        # Check if the collection has nested collections
        if isinstance(sanitized_value, (list, dict, tuple, set)):
            if any(isinstance(i, (list, dict, tuple, set)) for i in sanitized_value):
                sanitized_value = str(sanitized_value)
        if sanitized_value is not None:
            sanitized_params["code.function.parameter." + name] = sanitized_value

    return sanitized_params


def sanitize_for_attributes(value: Any, is_recursive: bool = False) -> Any:
    """
    Sanitize a value to be used as an attribute.

    :param value: The value to sanitize.
    :return: The sanitized value or None if the value is not a supported type.
    """
    if isinstance(value, (str, int, float, bool)):
        return value
    elif isinstance(value, list):
        return [sanitize_for_attributes(item, True) for item in value if isinstance(item, (str, int, float, bool, list, dict, tuple, set))]
    elif isinstance(value, dict):
        retval = {k: sanitize_for_attributes(v, True) for k, v in value.items() if isinstance(v, (str, int, float, bool, list, dict, tuple, set))}
        # dict to compatible with span attribute, so return it as a string
        if is_recursive:
            return retval
        else:
            return str(retval)
    elif isinstance(value, tuple):
        return tuple(sanitize_for_attributes(item, True) for item in value if isinstance(item, (str, int, float, bool, list, dict, tuple, set)))
    elif isinstance(value, set):
        retval = {sanitize_for_attributes(item, True) for item in value if isinstance(item, (str, int, float, bool, list, dict, tuple, set))}
        if is_recursive:
            return retval
        else:
            return str(retval)
    return None
