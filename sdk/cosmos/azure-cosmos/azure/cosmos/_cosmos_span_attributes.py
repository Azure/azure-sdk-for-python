# The MIT License (MIT)
# Copyright (c) 2024 Microsoft Corporation

"""Decorator to add Cosmos DB semantic convention attributes to OpenTelemetry spans."""

import functools
import re
from typing import Any, Callable, Mapping, Optional, TypeVar, cast
from azure.core.settings import settings
from azure.core.tracing import AbstractSpan
from ._cosmos_responses import CosmosDict, CosmosList
from ._constants import _Constants
from .http_constants import HttpHeaders

__all__ = ["cosmos_span_attributes", "sanitize_query"]

F = TypeVar("F", bound=Callable[..., Any])


def sanitize_query(query: str, parameters: Optional[list]) -> str:
    """
    Sanitize query text according to OpenTelemetry semantic conventions.

    Per the spec: https://github.com/devopsleague/opentelemetry-semantic-conventions/blob/main/docs/database/database-spans.md#sanitization-of-dbquerytext

    - If the query uses parameterized placeholders (e.g., @param), it's safe to log as-is
    - Otherwise, replace all literal values with '?' placeholder

    :param query: The SQL query text
    :type query: str
    :param parameters: Optional list of query parameters
    :type parameters: Optional[list]
    :return: Sanitized query text
    :rtype: str
    """
    if not query:
        return query

    # If query uses parameters, it's already safe (values are in parameters, not query text)
    if parameters:
        return query

    # Sanitize literal values in non-parameterized queries
    # Replace string literals (single quotes)
    sanitized = re.sub(r"'[^']*'", "'?'", query)

    # Replace numeric literals (integers and floats)
    # Match numbers not preceded by @ (to avoid matching @param names)
    sanitized = re.sub(r'(?<!@)\b\d+(\.\d+)?\b', '?', sanitized)

    # Replace boolean literals
    sanitized = re.sub(r'\b(true|false)\b', '?', sanitized, flags=re.IGNORECASE)

    # Replace null literals
    sanitized = re.sub(r'\b(null)\b', '?', sanitized, flags=re.IGNORECASE)

    return sanitized


def cosmos_span_attributes(
    __func: Optional[Callable] = None,
    *,
    name_of_span: Optional[str] = None,
    kind: Optional[Any] = None,
    tracing_attributes: Optional[Mapping[str, Any]] = None,
    operation_type: Optional[str] = None,
    **kwargs: Any,
) -> Any:
    """
    Decorator that adds Cosmos DB semantic convention attributes to the current OpenTelemetry span.

    The operation name (db.operation.name) is automatically derived from the function name.
    The operation_type (db.cosmosdb.operation_type) should be provided from the spec table values.

    This decorator should be used in conjunction with @distributed_trace to enrich
    the trace span with Cosmos-specific attributes following the OpenTelemetry semantic conventions.

    :param __func: The function to decorate
    :type __func: Optional[Callable]
    :keyword name_of_span: Not used, for signature compatibility
    :paramtype name_of_span: Optional[str]
    :keyword kind: Not used, for signature compatibility
    :paramtype kind: Optional[Any]
    :keyword tracing_attributes: Not used, for signature compatibility
    :paramtype tracing_attributes: Optional[Mapping[str, Any]]
    :keyword operation_type: The Cosmos DB operation type from the spec table (e.g., "create", "read", "query")
    :paramtype operation_type: Optional[str]
    :return: The decorated function
    :rtype: Any

    Example usage::

        @distributed_trace
        @cosmos_span_attributes(operation_type=Constants.OpenTelemetryOperationTypes.CREATE)
        def create_item(self, body, **kwargs):
            # ... implementation
            return result
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **func_kwargs: Any) -> Any:
            # Auto-derive method name from the function name
            method_name = func.__name__

            # Extract query and parameters BEFORE the function runs (for telemetry)
            query_for_telemetry = func_kwargs.get('query')
            parameters_for_telemetry = func_kwargs.get('parameters')

            # Execute the function (the parent @distributed_trace will create the span)
            try:
                result = func(*args, **func_kwargs)

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

        return cast(F, wrapper)

    return decorator if __func is None else decorator(__func)


def _add_cosmos_error_telemetry(error: Exception) -> None:
    """
    Add Cosmos DB-specific error telemetry to the current span.

    :param error: The exception that occurred
    :type error: Exception
    """
    try:
        # Get the tracing implementation
        span_impl_type = settings.tracing_implementation()

        if span_impl_type is None:
            return

        # Get the current span
        try:
            raw_span = span_impl_type.get_current_span()
        except Exception:
            return

        if raw_span is None:
            return

        # Skip if NonRecordingSpan
        if hasattr(raw_span, 'is_recording'):
            if not raw_span.is_recording():
                return

        # Wrap the span
        span: AbstractSpan = span_impl_type(span=raw_span)

        # Always add db.system for Cosmos DB
        span.add_attribute(_Constants.OpenTelemetryAttributes.DB_SYSTEM, "cosmosdb")

        # Add error attributes
        if hasattr(error, "status_code"):
            span.add_attribute(_Constants.OpenTelemetryAttributes.DB_COSMOSDB_STATUS_CODE, error.status_code)

        if hasattr(error, "sub_status_code"):
            span.add_attribute(_Constants.OpenTelemetryAttributes.DB_COSMOSDB_SUB_STATUS_CODE, error.sub_status_code)

        if hasattr(error, "headers") and error.headers:
            _extract_headers(span, error.headers)

    except Exception:
        pass


def _add_cosmos_telemetry(
    method_name: Optional[str],
    operation_type: Optional[str],
    args: tuple,
    kwargs: dict,
    result: Any
) -> None:
    """
    Add Cosmos DB-specific telemetry attributes to the current span.

    :param method_name: The actual method name from the function (e.g., "create_item")
    :type method_name: Optional[str]
    :param operation_type: The Cosmos DB operation type from spec (e.g., "create")
    :type operation_type: Optional[str]
    :param args: Function arguments
    :type args: tuple
    :param kwargs: Function keyword arguments
    :type kwargs: dict
    :param result: The function result
    :type result: Any
    """
    try:
        # Get the tracing implementation from azure-core settings
        span_impl_type = settings.tracing_implementation()

        if span_impl_type is None:
            return

        # Get the current span
        try:
            raw_span = span_impl_type.get_current_span()
        except Exception:
            return

        # Skip if no span
        if raw_span is None:
            return

        # Skip if NonRecordingSpan
        if hasattr(raw_span, 'is_recording'):
            is_recording = raw_span.is_recording()
            if not is_recording:
                return

        # Wrap the raw span in the AbstractSpan implementation
        span: AbstractSpan = span_impl_type(span=raw_span)

        # Add Cosmos DB attributes
        _add_cosmos_attributes(span, method_name, operation_type, args, kwargs)
        _add_response_attributes(span, result)

    except Exception:
        # Silently fail - telemetry should never break functionality
        pass


def _add_cosmos_attributes(
    span: AbstractSpan,
    method_name: Optional[str],
    operation_type: Optional[str],
    args: tuple,
    kwargs: dict
) -> None:
    """Add Cosmos DB client-level attributes to the span per OpenTelemetry semantic conventions."""
    try:
        # Required: db.system
        span.add_attribute(_Constants.OpenTelemetryAttributes.DB_SYSTEM, "cosmosdb")

        # db.operation.name: The actual method name (e.g., "create_item")
        # Per spec: "capture the value as provided by the application"
        if method_name:
            span.add_attribute(_Constants.OpenTelemetryAttributes.DB_OPERATION_NAME, method_name)

        # db.cosmosdb.operation_type: Standardized value from spec table (e.g., "create")
        if operation_type:
            span.add_attribute(_Constants.OpenTelemetryAttributes.DB_COSMOSDB_OPERATION_TYPE, operation_type)

        # Extract container and database info from self (first arg)
        if args and hasattr(args[0], "id"):
            instance = args[0]

            # Required: db.collection.name (container name)
            container_name = instance.id
            span.add_attribute(_Constants.OpenTelemetryAttributes.DB_COLLECTION_NAME, container_name)

            # Required: db.namespace (database name)
            # Extract database name from container_link: /dbs/{db}/colls/{container}
            if hasattr(instance, "container_link"):
                container_link = instance.container_link
                if "dbs/" in container_link and "/colls/" in container_link:
                    parts = container_link.split("/")
                    try:
                        db_index = parts.index("dbs")
                        if db_index + 1 < len(parts):
                            db_name = parts[db_index + 1]
                            span.add_attribute(_Constants.OpenTelemetryAttributes.DB_NAMESPACE, db_name)
                    except (ValueError, IndexError):
                        pass

            # Extract connection mode and client ID from client_connection
            if hasattr(instance, "client_connection"):
                client_conn = instance.client_connection

                # db.cosmosdb.connection_mode
                if hasattr(client_conn, "connection_policy"):
                    policy = client_conn.connection_policy
                    if hasattr(policy, "ConnectionMode"):
                        # 0 = Gateway, 1 = Direct
                        mode = "direct" if policy.ConnectionMode == 1 else "gateway"
                        span.add_attribute(_Constants.OpenTelemetryAttributes.DB_COSMOSDB_CONNECTION_MODE, mode)

                # db.cosmosdb.client_id
                if hasattr(client_conn, "client_id"):
                    span.add_attribute(_Constants.OpenTelemetryAttributes.DB_COSMOSDB_CLIENT_ID, str(client_conn.client_id))

        # db.query.text for query operations
        query_text = None
        parameters = None

        if "query" in kwargs:
            query = kwargs["query"]
            if isinstance(query, str):
                query_text = query
            elif isinstance(query, dict) and "query" in query:
                query_text = query["query"]
                parameters = query.get("parameters")

        # Also check for parameters passed separately
        if "parameters" in kwargs:
            parameters = kwargs["parameters"]

        if query_text:
            # Sanitize query text per semantic conventions
            sanitized_query = sanitize_query(query_text, parameters)
            span.add_attribute(_Constants.OpenTelemetryAttributes.DB_QUERY_TEXT, sanitized_query)

            # Note: Query parameter VALUES are opt-in per semantic conventions
            # Since we don't have a standard configuration mechanism for this,
            # we do NOT log parameter values to avoid exposing sensitive data


    except Exception:
        pass


def _add_response_attributes(span: AbstractSpan, result: Any) -> None:
    """Add Cosmos DB attributes from the response."""
    try:
        if result is None:
            return

        headers = None

        # Handle CosmosDict responses (single item operations)
        if isinstance(result, CosmosDict):
            headers = result.get_response_headers()
        # Handle CosmosList responses (query operations)
        elif isinstance(result, CosmosList):
            headers = result.get_response_headers()
            span.add_attribute(_Constants.OpenTelemetryAttributes.DB_COSMOSDB_ITEM_COUNT, len(result))
        # Handle other types with get_response_headers method
        elif hasattr(result, "get_response_headers"):
            headers = result.get_response_headers()

        if headers:
            _extract_headers(span, headers)

    except Exception:
        pass


def _extract_headers(span: AbstractSpan, headers: dict) -> None:
    """Extract Cosmos DB client-level telemetry from response headers per OpenTelemetry semantic conventions."""
    try:
        # db.cosmosdb.request_charge - Request Units consumed
        if HttpHeaders.RequestCharge in headers:
            charge = float(headers[HttpHeaders.RequestCharge])
            span.add_attribute(_Constants.OpenTelemetryAttributes.DB_COSMOSDB_REQUEST_CHARGE, charge)  # type: ignore[arg-type]

        # db.cosmosdb.request_diagnostics_id - Request correlation ID
        if HttpHeaders.ActivityId in headers:
            activity_id = headers[HttpHeaders.ActivityId]
            span.add_attribute(_Constants.OpenTelemetryAttributes.DB_COSMOSDB_REQUEST_DIAGNOSTICS_ID, activity_id)

        # db.cosmosdb.sub_status_code - Cosmos-specific error details
        if HttpHeaders.SubStatus in headers:
            sub_status = int(headers[HttpHeaders.SubStatus])
            span.add_attribute(_Constants.OpenTelemetryAttributes.DB_COSMOSDB_SUB_STATUS_CODE, sub_status)

        # db.cosmosdb.item_count - Number of items in response
        if HttpHeaders.ItemCount in headers:
            item_count = int(headers[HttpHeaders.ItemCount])
            span.add_attribute(_Constants.OpenTelemetryAttributes.DB_COSMOSDB_ITEM_COUNT, item_count)

        # db.cosmosdb.request_content_length - Size of request body
        if HttpHeaders.ContentLength in headers:
            try:
                request_length = int(headers[HttpHeaders.ContentLength])
                span.add_attribute(_Constants.OpenTelemetryAttributes.DB_COSMOSDB_REQUEST_CONTENT_LENGTH, request_length)
            except (ValueError, TypeError):
                pass

        # db.cosmosdb.regions_contacted - Regions contacted for hedging/multi-region scenarios
        for key in ["x-ms-regions-contacted", "x-ms-cosmos-regions-contacted"]:
            if key in headers:
                regions_header = headers[key]
                if isinstance(regions_header, str):
                    span.add_attribute(_Constants.OpenTelemetryAttributes.DB_COSMOSDB_REGIONS_CONTACTED, regions_header)
                break

    except Exception:
        pass
