# The MIT License (MIT)
# Copyright (c) 2024 Microsoft Corporation

"""Decorator to add Cosmos DB semantic convention attributes to aio client spans."""

import functools
import inspect
from typing import Any, Awaitable, Callable, Mapping, Optional, cast

from .._cosmos_span_attributes import (
    _add_cosmos_error_telemetry,
    _add_cosmos_telemetry,
    sanitize_query,
)

__all__ = ["cosmos_span_attributes_async", "sanitize_query"]


def _build_telemetry_kwargs(func_kwargs: Mapping[str, Any]) -> dict[str, Any]:
    """Copy kwargs and normalize query metadata for telemetry.

    :param Mapping[str, Any] func_kwargs: The keyword arguments passed to the decorated method.
    :returns: A copied kwargs mapping with normalized query and parameters values for telemetry.
    :rtype: dict[str, Any]
    """
    query_for_telemetry = func_kwargs.get("query")
    parameters_for_telemetry = func_kwargs.get("parameters")

    if isinstance(query_for_telemetry, dict) and "query" in query_for_telemetry:
        if parameters_for_telemetry is None:
            parameters_for_telemetry = query_for_telemetry.get("parameters")
        query_for_telemetry = query_for_telemetry["query"]

    telemetry_kwargs = dict(func_kwargs)
    if query_for_telemetry is not None:
        telemetry_kwargs["query"] = query_for_telemetry
    if parameters_for_telemetry is not None:
        telemetry_kwargs["parameters"] = parameters_for_telemetry
    return telemetry_kwargs


def _add_success_telemetry(
    operation_name: str,
    args: tuple[Any, ...],
    func_kwargs: Mapping[str, Any],
    result: Any,
) -> None:
    """Add success telemetry for the decorated aio method.

    :param operation_name: The semantic db.operation.name value.
    :type operation_name: str
    :param args: Positional arguments passed to the decorated method.
    :type args: tuple[Any, ...]
    :param func_kwargs: Keyword arguments passed to the decorated method.
    :type func_kwargs: Mapping[str, Any]
    :param result: The method result.
    :type result: Any
    """
    _add_cosmos_telemetry(
        operation_name,
        args,
        _build_telemetry_kwargs(func_kwargs),
        result,
    )


def _add_error_telemetry(error: Exception) -> None:
    """Add error telemetry for the decorated aio method.

    :param Exception error: The raised exception.
    """
    _add_cosmos_error_telemetry(error)


def cosmos_span_attributes_async(
    __func: Optional[Callable[..., Any]] = None,
    *,
    name_of_span: Optional[str] = None,
    kind: Optional[Any] = None,
    tracing_attributes: Optional[Mapping[str, Any]] = None,
    operation_name: Optional[str] = None,
    **kwargs: Any,
) -> Any:
    """
    Decorator that adds Cosmos DB semantic convention attributes to the current OpenTelemetry span.

    The operation name (db.operation.name) defaults to the function name unless
    an explicit operation_name override is provided.

    This decorator is intended for aio client methods and supports two shapes:

    * ``async def`` methods used with ``@distributed_trace_async``
    * synchronous pager-factory methods used with ``@distributed_trace`` that return
      async iterables consumed via ``async for``

    Preserving the original callable shape is required so async-pager factory methods continue
    to return async iterables directly instead of coroutines.

    :param __func: The function to decorate.
    :type __func: Optional[Callable]
    :keyword name_of_span: Unused compatibility argument.
    :paramtype name_of_span: Optional[str]
    :keyword kind: Unused compatibility argument.
    :paramtype kind: Optional[Any]
    :keyword tracing_attributes: Unused compatibility argument.
    :paramtype tracing_attributes: Optional[Mapping[str, Any]]
    :keyword operation_name: Explicit db.operation.name override.
    :paramtype operation_name: Optional[str]
    :return: The decorated function.
    :rtype: Any

    Example usage::

        @distributed_trace_async
        @cosmos_span_attributes_async(operation_name=Constants.OpenTelemetryOperationNames.CREATE_ITEM)
        async def create_item(self, body, **kwargs):
            # ... implementation
            return result
    """
    del name_of_span, kind, tracing_attributes, kwargs

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        resolved_operation_name = operation_name or func.__name__

        if inspect.iscoroutinefunction(func):
            coroutine_func = cast(Callable[..., Awaitable[Any]], func)

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    result = await coroutine_func(*args, **kwargs)
                    _add_success_telemetry(resolved_operation_name, args, kwargs, result)
                    return result
                except Exception as error:
                    _add_error_telemetry(error)
                    raise

            return async_wrapper

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                result = func(*args, **kwargs)
                _add_success_telemetry(resolved_operation_name, args, kwargs, result)
                return result
            except Exception as error:
                _add_error_telemetry(error)
                raise

        return sync_wrapper

    return decorator if __func is None else decorator(__func)
