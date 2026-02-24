# The MIT License (MIT)
# Copyright (c) 2024 Microsoft Corporation

"""Async decorator to add Cosmos DB semantic convention attributes to OpenTelemetry spans."""

from .._cosmos_span_attributes import _add_cosmos_telemetry, _add_cosmos_error_telemetry
import functools
from typing import Any, Callable, Mapping, Optional, TypeVar, cast

__all__ = ["cosmos_span_attributes_async"]

F = TypeVar("F", bound=Callable[..., Any])


def cosmos_span_attributes_async(
    __func: Optional[Callable] = None,
    *,
    name_of_span: Optional[str] = None,
    kind: Optional[Any] = None,
    tracing_attributes: Optional[Mapping[str, Any]] = None,
    operation_type: Optional[str] = None,
    **kwargs: Any,
) -> Any:
    """
    Async decorator that adds Cosmos DB semantic convention attributes to the current OpenTelemetry span.

    The operation name (db.operation.name) is automatically derived from the function name.
    The operation_type (db.cosmosdb.operation_type) should be provided from the spec table values.

    This decorator should be used in conjunction with @distributed_trace_async to enrich
    the trace span with Cosmos-specific attributes following the OpenTelemetry semantic conventions.

    :param __func: The async function to decorate
    :type __func: Optional[Callable]
    :keyword operation_type: The Cosmos DB operation type from the spec table (e.g., "create", "read")
    :paramtype operation_type: Optional[str]
    :return: The decorated async function
    :rtype: Any

    Example usage::

        @distributed_trace_async
        @cosmos_span_attributes_async(operation_type=Constants.OpenTelemetryOperationTypes.CREATE)
        async def create_item(self, body, **kwargs):
            # ... implementation
            return result
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **func_kwargs: Any) -> Any:
            # Auto-derive method name from the function name
            method_name = func.__name__

            # Extract query and parameters BEFORE the function runs (for telemetry)
            query_for_telemetry = func_kwargs.get('query')
            parameters_for_telemetry = func_kwargs.get('parameters')

            # Handle dict-style query with embedded parameters
            if isinstance(query_for_telemetry, dict):
                if 'query' in query_for_telemetry:
                    actual_query = query_for_telemetry['query']
                    if parameters_for_telemetry is None:
                        parameters_for_telemetry = query_for_telemetry.get('parameters')
                    query_for_telemetry = actual_query

            # Execute the async function (the parent @distributed_trace_async will create the span)
            try:
                result = await func(*args, **func_kwargs)

                # Add Cosmos-specific attributes (only if span exists)
                # Create a copy of kwargs with the query/parameters we saved
                telemetry_kwargs = dict(func_kwargs)
                if query_for_telemetry is not None:
                    telemetry_kwargs['query'] = query_for_telemetry
                if parameters_for_telemetry is not None:
                    telemetry_kwargs['parameters'] = parameters_for_telemetry

                _add_cosmos_telemetry(method_name, operation_type, args, telemetry_kwargs, result)

                return result
            except Exception as error:
                # Add error attributes if we have a span
                _add_cosmos_error_telemetry(error)
                raise

        return cast(F, async_wrapper)

    return decorator if __func is None else decorator(__func)
