# The MIT License (MIT)
# Copyright (c) 2024 Microsoft Corporation

"""Decorator to add Cosmos DB semantic convention attributes to spans."""

import functools
import os
import re
from typing import Any, Callable, Mapping, Optional, Sequence, TypeVar, Union, cast
from urllib.parse import urlparse

from azure.core.settings import settings
from azure.core.tracing import AbstractSpan

from ._cosmos_responses import CosmosDict, CosmosList
from ._constants import _Constants
from .http_constants import HttpHeaders

__all__ = ["cosmos_span_attributes", "sanitize_query"]

F = TypeVar("F", bound=Callable[..., Any])
_NUMERIC_LITERAL_PATTERN = re.compile(r"(?<![@\w.])-?(?:\d+(?:\.\d+)?|\.\d+)(?:[eE][+-]?\d+)?\b")
_TRUE_VALUES = {"1", "true", "yes", "on"}
_FALSE_VALUES = {"0", "false", "no", "off"}


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


def sanitize_query(query: str, parameters: Optional[list]) -> str:
    """
    Sanitize query text according to OpenTelemetry semantic conventions.

    Per the official database semantic conventions:
    https://opentelemetry.io/docs/specs/semconv/db/database-spans/#sanitization-of-dbquerytext

    - Preserve parameterized placeholders (for example, @param)
    - Do not sanitize parameterized query text when explicit query parameters are provided
    - Replace inline literal values with '?' placeholders for non-parameterized queries

    :param query: The SQL query text
    :type query: str
    :param parameters: Optional list of query parameters
    :type parameters: Optional[list]
    :return: Sanitized query text
    :rtype: str
    """
    if not query:
        return query

    if parameters:
        return query

    # Sanitize literal values in non-parameterized queries
    # Replace string literals, including escaped quotes and doubled single quotes.
    sanitized = re.sub(r"'(?:\\.|''|[^'])*'", "'?'", query)

    # Replace numeric literals (integers, floats, and scientific notation),
    # including negative values. Match numbers not preceded by @ or identifier characters.
    sanitized = _NUMERIC_LITERAL_PATTERN.sub("?", sanitized)

    # Replace boolean literals
    sanitized = re.sub(r'\b(true|false)\b', '?', sanitized, flags=re.IGNORECASE)

    # Replace null literals
    sanitized = re.sub(r'\b(null)\b', '?', sanitized, flags=re.IGNORECASE)

    return sanitized


def _get_env_bool(name: str) -> Optional[bool]:
    value = os.environ.get(name)
    if value is None:
        return None

    normalized = value.strip().lower()
    if normalized in _TRUE_VALUES:
        return True
    if normalized in _FALSE_VALUES:
        return False
    return None


def _should_emit_query_text() -> bool:
    explicit_opt_in = _get_env_bool(_Constants.OTEL_ENABLE_QUERY_TEXT)
    return explicit_opt_in is True


def _wrap_span(span_impl_type: Any, raw_span: Any) -> AbstractSpan:
    if hasattr(raw_span, "add_attribute"):
        return cast(AbstractSpan, raw_span)

    try:
        return cast(AbstractSpan, span_impl_type(span=raw_span))
    except TypeError:
        return cast(AbstractSpan, span_impl_type(raw_span))


def cosmos_span_attributes(
    __func: Optional[Callable] = None,
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

    This decorator should be used in conjunction with @distributed_trace to enrich
    the trace span with Cosmos-specific attributes following the OpenTelemetry semantic conventions.

    :param __func: The function to decorate
    :type __func: Optional[Callable]
    :keyword name_of_span: Unused compatibility argument.
    :paramtype name_of_span: Optional[str]
    :keyword kind: Unused compatibility argument.
    :paramtype kind: Optional[Any]
    :keyword tracing_attributes: Unused compatibility argument.
    :paramtype tracing_attributes: Optional[Mapping[str, Any]]
    :keyword operation_name: Explicit db.operation.name override.
    :paramtype operation_name: Optional[str]
    :return: The decorated function
    :rtype: Any

    Example usage::

        @distributed_trace
        @cosmos_span_attributes(operation_name=Constants.OpenTelemetryOperationNames.CREATE_ITEM)
        def create_item(self, body, **kwargs):
            # ... implementation
            return result
    """
    del name_of_span, kind, tracing_attributes, kwargs

    def decorator(func: F) -> F:
        resolved_operation_name = operation_name or func.__name__

        @functools.wraps(func)
        def wrapper(*args: Any, **func_kwargs: Any) -> Any:
            # Execute the function (the parent @distributed_trace will create the span)
            try:
                result = func(*args, **func_kwargs)

                # Add Cosmos-specific attributes (only if span exists)
                _add_cosmos_telemetry(
                    resolved_operation_name,
                    args,
                    _build_telemetry_kwargs(func_kwargs),
                    result,
                )

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
        except AttributeError:
            return

        if raw_span is None:
            return

        # Skip if NonRecordingSpan. If the span is not recording, return before
        # doing any Cosmos-specific enrichment work.
        if hasattr(raw_span, "is_recording"):
            if not raw_span.is_recording():
                return

        span = _wrap_span(span_impl_type, raw_span)

        span.add_attribute(
            _Constants.OpenTelemetryAttributes.DB_SYSTEM_NAME,
            _Constants.OpenTelemetryValues.DB_SYSTEM_NAME_VALUE,
        )

        if hasattr(error, "status_code"):
            status_code = str(getattr(error, "status_code"))
            span.add_attribute(_Constants.OpenTelemetryAttributes.DB_RESPONSE_STATUS_CODE, status_code)
            span.add_attribute(_Constants.OpenTelemetryAttributes.ERROR_TYPE, status_code)
        else:
            span.add_attribute(_Constants.OpenTelemetryAttributes.ERROR_TYPE, type(error).__name__)

        if hasattr(error, "sub_status_code"):
            span.add_attribute(
                _Constants.OpenTelemetryAttributes.AZURE_COSMOSDB_RESPONSE_SUB_STATUS_CODE,
                error.sub_status_code,
            )

        if hasattr(error, "headers") and error.headers:
            _extract_headers(span, error.headers)

    except (AttributeError, TypeError, ValueError):
        pass


def _add_cosmos_telemetry(
    operation_name: Optional[str],
    args: tuple,
    kwargs: dict,
    result: Any,
) -> None:
    """
    Add Cosmos DB-specific telemetry attributes to the current span.

    :param operation_name: The semantic db.operation.name value.
    :type operation_name: Optional[str]
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
        except AttributeError:
            return

        # Skip if no span
        if raw_span is None:
            return

        # Skip if NonRecordingSpan. This avoids all downstream enrichment work,
        # including query metadata extraction and regex-based query sanitization.
        if hasattr(raw_span, "is_recording"):
            is_recording = raw_span.is_recording()
            if not is_recording:
                return

        span = _wrap_span(span_impl_type, raw_span)

        # Add Cosmos DB attributes
        _add_cosmos_attributes(span, operation_name, args, kwargs)
        _add_response_attributes(span, result)

    except (AttributeError, TypeError, ValueError):
        # Silently fail - telemetry should never break functionality
        pass


def _add_cosmos_attributes(
    span: AbstractSpan,
    operation_name: Optional[str],
    args: tuple,
    kwargs: dict,
) -> None:
    """
    Add Cosmos DB client-level attributes to the span.

    :param span: The span to enrich.
    :type span: ~azure.core.tracing.AbstractSpan
    :param operation_name: The semantic db.operation.name value.
    :type operation_name: Optional[str]
    :param args: Positional arguments passed to the wrapped method.
    :type args: tuple
    :param kwargs: Keyword arguments passed to the wrapped method.
    :type kwargs: dict
    """
    try:
        span.add_attribute(
            _Constants.OpenTelemetryAttributes.DB_SYSTEM_NAME,
            _Constants.OpenTelemetryValues.DB_SYSTEM_NAME_VALUE,
        )

        if operation_name:
            span.add_attribute(_Constants.OpenTelemetryAttributes.DB_OPERATION_NAME, operation_name)

        instance = args[0] if args else None
        if instance is not None:
            _add_instance_attributes(span, instance)

        _add_request_attributes(span, operation_name, args, kwargs)

        query_text, parameters = _extract_query_metadata(kwargs)

        if query_text and _should_emit_query_text():
            # Parameterized query text is emitted unchanged per the DB semantic conventions.
            # Non-parameterized query text is sanitized to replace inline literals.
            emitted_query = sanitize_query(query_text, parameters)
            span.add_attribute(_Constants.OpenTelemetryAttributes.DB_QUERY_TEXT, emitted_query)


    except (AttributeError, TypeError, ValueError):
        pass


def _add_response_attributes(span: AbstractSpan, result: Any) -> None:
    """
    Add Cosmos DB attributes from the response.

    :param span: The span to enrich.
    :type span: ~azure.core.tracing.AbstractSpan
    :param result: The SDK response object.
    :type result: Any
    """
    try:
        headers = None

        if result is not None and hasattr(result, "status_code"):
            span.add_attribute(
                _Constants.OpenTelemetryAttributes.DB_RESPONSE_STATUS_CODE,
                str(getattr(result, "status_code")),
            )

        if isinstance(result, CosmosDict):
            # Successful CosmosDict/CosmosList responses currently expose headers but not a public HTTP status code.
            # Once status_code is surfaced on these response types, emit it here, for example:
            # span.add_attribute(
            #     _Constants.OpenTelemetryAttributes.DB_RESPONSE_STATUS_CODE,
            #     str(result.status_code),
            # )
            headers = result.get_response_headers()
        elif isinstance(result, CosmosList):
            headers = result.get_response_headers()
            span.add_attribute(_Constants.OpenTelemetryAttributes.DB_RESPONSE_RETURNED_ROWS, len(result))
        elif hasattr(result, "get_response_headers"):
            headers = result.get_response_headers()

        if isinstance(headers, list):
            headers = headers[-1] if headers else None

        if headers:
            _extract_headers(span, headers)

    except (AttributeError, TypeError, ValueError):
        pass


def _extract_query_metadata(kwargs: Mapping[str, Any]) -> tuple[Optional[str], Optional[list]]:
    """
    Extract query text and parameters from Cosmos kwargs.

    :param kwargs: Keyword arguments passed to the wrapped Cosmos method.
    :type kwargs: Mapping[str, Any]
    :return: A tuple of query text and query parameters.
    :rtype: tuple[Optional[str], Optional[list]]
    """
    query_text = None
    parameters = None
    query = kwargs.get("query")

    if isinstance(query, str):
        query_text = query
    elif isinstance(query, Mapping):
        query_value = query.get("query")
        if isinstance(query_value, str):
            query_text = query_value
        parameters_value = query.get("parameters")
        if isinstance(parameters_value, list):
            parameters = parameters_value

    parameters_kwarg = kwargs.get("parameters")
    if isinstance(parameters_kwarg, list):
        parameters = parameters_kwarg

    return query_text, parameters


def _add_request_attributes(
    span: AbstractSpan,
    operation_name: Optional[str],
    args: tuple[Any, ...],
    kwargs: Mapping[str, Any],
) -> None:
    consistency_level = kwargs.get("consistencyLevel") or kwargs.get("consistency_level")
    if isinstance(consistency_level, (str, int)):
        typed_consistency_level = cast(Union[str, int], consistency_level)
        span.add_attribute(_Constants.OpenTelemetryAttributes.AZURE_COSMOSDB_CONSISTENCY_LEVEL, typed_consistency_level)

    if operation_name != _Constants.OpenTelemetryOperationNames.EXECUTE_BATCH:
        return

    batch_operations = kwargs.get("batch_operations")
    if batch_operations is None and len(args) > 1:
        batch_operations = args[1]

    if isinstance(batch_operations, Sequence) and not isinstance(batch_operations, (str, bytes)):
        batch_size = len(batch_operations)
        if batch_size > 1:
            span.add_attribute(_Constants.OpenTelemetryAttributes.DB_OPERATION_BATCH_SIZE, batch_size)


def _add_instance_attributes(span: AbstractSpan, instance: Any) -> None:
    """
    Add container- and client-related attributes from the wrapped instance.

    :param span: The span to enrich.
    :type span: ~azure.core.tracing.AbstractSpan
    :param instance: The wrapped SDK instance.
    :type instance: Any
    """
    _add_client_connection_attributes(span, instance)

    if hasattr(instance, "container_link") and hasattr(instance, "id"):
        span.add_attribute(_Constants.OpenTelemetryAttributes.DB_COLLECTION_NAME, instance.id)
        _add_namespace_from_link(span, instance.container_link)
        return

    if (
        hasattr(instance, "database_link")
        and not hasattr(instance, "user_link")
        and not hasattr(instance, "permission_link")
    ):
        if hasattr(instance, "id"):
            span.add_attribute(_Constants.OpenTelemetryAttributes.DB_NAMESPACE, instance.id)
        else:
            _add_namespace_from_link(span, instance.database_link)
        return

    if hasattr(instance, "database_link"):
        _add_namespace_from_link(span, instance.database_link)


def _add_namespace_from_link(span: AbstractSpan, resource_link: str) -> None:
    if "dbs/" not in resource_link:
        return

    parts = resource_link.split("/")
    try:
        db_index = parts.index("dbs")
        if db_index + 1 < len(parts):
            span.add_attribute(_Constants.OpenTelemetryAttributes.DB_NAMESPACE, parts[db_index + 1])
    except (ValueError, IndexError):
        pass


def _add_client_connection_attributes(span: AbstractSpan, instance: Any) -> None:
    """
    Add client-connection-specific Cosmos DB attributes.

    :param span: The span to enrich.
    :type span: ~azure.core.tracing.AbstractSpan
    :param instance: The wrapped SDK instance.
    :type instance: Any
    """
    if not hasattr(instance, "client_connection"):
        return

    client_conn = instance.client_connection
    if hasattr(client_conn, "connection_policy"):
        policy = client_conn.connection_policy
        if hasattr(policy, "ConnectionMode"):
            mode = (
                _Constants.OpenTelemetryValues.CONNECTION_MODE_DIRECT
                if policy.ConnectionMode == 1
                else _Constants.OpenTelemetryValues.CONNECTION_MODE_GATEWAY
            )
            if mode != _Constants.OpenTelemetryValues.CONNECTION_MODE_GATEWAY:
                span.add_attribute(_Constants.OpenTelemetryAttributes.AZURE_COSMOSDB_CONNECTION_MODE, mode)

    if hasattr(client_conn, "client_id"):
        span.add_attribute(
            _Constants.OpenTelemetryAttributes.AZURE_CLIENT_ID,
            str(client_conn.client_id),
        )

    default_headers = getattr(client_conn, "default_headers", None)
    consistency_level = None
    if isinstance(default_headers, Mapping):
        consistency_level = default_headers.get(HttpHeaders.ConsistencyLevel)
    if isinstance(consistency_level, (str, int)):
        typed_consistency_level = cast(Union[str, int], consistency_level)
        span.add_attribute(_Constants.OpenTelemetryAttributes.AZURE_COSMOSDB_CONSISTENCY_LEVEL, typed_consistency_level)

    span.add_attribute(
        _Constants.OpenTelemetryAttributes.AZURE_RESOURCE_PROVIDER_NAMESPACE,
        _Constants.OpenTelemetryValues.AZURE_RESOURCE_PROVIDER_NAMESPACE_VALUE,
    )

    if hasattr(client_conn, "url_connection"):
        parsed = urlparse(str(client_conn.url_connection))
        if parsed.hostname is not None:
            hostname = cast(str, parsed.hostname)
            span.add_attribute(_Constants.OpenTelemetryAttributes.SERVER_ADDRESS, hostname)
        if parsed.port is not None and parsed.port != 443:
            port = cast(int, parsed.port)
            span.add_attribute(_Constants.OpenTelemetryAttributes.SERVER_PORT, port)

    user_agent = getattr(client_conn, "_user_agent", None)
    if isinstance(user_agent, (str, int)):
        typed_user_agent = cast(Union[str, int], user_agent)
        span.add_attribute(_Constants.OpenTelemetryAttributes.USER_AGENT_ORIGINAL, typed_user_agent)


def _extract_headers(span: AbstractSpan, headers: Mapping[str, Any]) -> None:
    """
    Extract Cosmos DB client-level telemetry from response headers.

    :param span: The span to enrich.
    :type span: ~azure.core.tracing.AbstractSpan
    :param headers: Response headers.
    :type headers: Mapping[str, Any]
    """
    try:
        if HttpHeaders.RequestCharge in headers:
            charge = float(headers[HttpHeaders.RequestCharge])
            span.add_attribute(
                _Constants.OpenTelemetryAttributes.AZURE_COSMOSDB_OPERATION_REQUEST_CHARGE,
                cast(Any, charge),
            )

        if HttpHeaders.SubStatus in headers:
            sub_status = int(headers[HttpHeaders.SubStatus])
            span.add_attribute(_Constants.OpenTelemetryAttributes.AZURE_COSMOSDB_RESPONSE_SUB_STATUS_CODE, sub_status)

        if HttpHeaders.ItemCount in headers:
            item_count = int(headers[HttpHeaders.ItemCount])
            span.add_attribute(_Constants.OpenTelemetryAttributes.DB_RESPONSE_RETURNED_ROWS, item_count)

        # Python SDK does not currently expose a verified/public contacted-regions
        # response contract for this telemetry path. If that becomes supported,
        # add extraction here using the public response surface.

    except (AttributeError, TypeError, ValueError):
        pass
