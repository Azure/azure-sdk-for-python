# The MIT License (MIT)
# Copyright (c) 2014 Microsoft Corporation
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Distributed tracing policy for Azure Cosmos DB SDK."""

import json
import logging
import sys
import time
import urllib.parse
from typing import Any, Optional, Tuple, Dict, Type, TypeVar, Union, TYPE_CHECKING
from types import TracebackType

from azure.core.pipeline import PipelineRequest, PipelineResponse
from azure.core.pipeline.transport import HttpResponse as LegacyHttpResponse, HttpRequest as LegacyHttpRequest
from azure.core.rest import HttpResponse, HttpRequest
from azure.core.pipeline.policies._distributed_tracing import DistributedTracingPolicy
from azure.core.settings import settings
from azure.core.tracing import SpanKind
from azure.core.exceptions import ServiceRequestError, ServiceResponseError  # type: ignore

from .exceptions import CosmosHttpResponseError  # type: ignore
from ._constants import _CosmosTracingConstants
from .http_constants import HttpHeaders

if TYPE_CHECKING:
    from azure.core.tracing._abstract_span import (
        AbstractSpan,
    )





# request.context keys
_SPAN_REQUEST_CONTEXT_KEY = "cosmos_distributed_tracing.span_entry"
_START_TIME_REQUEST_CONTEXT_KEY = "cosmos_distributed_tracing.start_time"

HTTPResponseType = TypeVar("HTTPResponseType", HttpResponse, LegacyHttpResponse)
HTTPRequestType = TypeVar("HTTPRequestType", HttpRequest, LegacyHttpRequest)
ExcInfo = Tuple[Type[BaseException], BaseException, TracebackType]
OptExcInfo = Union[ExcInfo, Tuple[None, None, None]]

logger = logging.getLogger("azure.cosmos._cosmos_distributed_tracing")

# Required / recommended attribute sets for validation/consumers
REQUIRED_ATTRIBUTES = [
    _CosmosTracingConstants.DB_SYSTEM_NAME,
    _CosmosTracingConstants.DB_OPERATION_NAME,
]

CONDITIONALLY_REQUIRED_ATTRIBUTES = [
    _CosmosTracingConstants.AZURE_COSMOS_CONNECTION_MODE,
    _CosmosTracingConstants.AZURE_COSMOS_CONSISTENCY_LEVEL,
    _CosmosTracingConstants.AZURE_COSMOS_OPERATION_CONTACTED_REGIONS,
    _CosmosTracingConstants.AZURE_COSMOS_OPERATION_REQUEST_CHARGE,
    _CosmosTracingConstants.AZURE_COSMOS_RESPONSE_SUB_STATUS_CODE,
    _CosmosTracingConstants.DB_COLLECTION_NAME,
    _CosmosTracingConstants.DB_NAMESPACE,
    _CosmosTracingConstants.DB_RESPONSE_RETURNED_ROWS,
    _CosmosTracingConstants.DB_RESPONSE_STATUS_CODE,
    _CosmosTracingConstants.ERROR_TYPE,
    _CosmosTracingConstants.SERVER_PORT,
]

RECOMMENDED_ATTRIBUTES = [
    _CosmosTracingConstants.AZURE_CLIENT_ID,
    _CosmosTracingConstants.AZURE_COSMOS_REQUEST_BODY_SIZE,
    _CosmosTracingConstants.AZURE_RESOURCE_PROVIDER_NAMESPACE,
    _CosmosTracingConstants.DB_OPERATION_BATCH_SIZE,
    _CosmosTracingConstants.DB_QUERY_TEXT,
    _CosmosTracingConstants.DB_STORED_PROCEDURE_NAME,
    _CosmosTracingConstants.SERVER_ADDRESS,
    _CosmosTracingConstants.USER_AGENT_ORIGINAL,
]

OPT_IN_ATTRIBUTES = [
    _CosmosTracingConstants.DB_QUERY_PARAMETER_KEY,
]

# Mappping of operation names to output correct values.
OPERATION_NAME_MAPPING = {
    # Batch operations
    "execute_batch": "execute_batch",
    "ExecuteBatch": "execute_batch",

    # Bulk operations
    "execute_bulk": "execute_bulk",
    "ExecuteBulk": "execute_bulk",
    "bulk_create_item": "bulk_create_item",
    "BulkCreateItem": "bulk_create_item",
    "bulk_upsert_item": "bulk_upsert_item",
    "BulkUpsertItem": "bulk_upsert_item",

    # Change feed operations
    "query_change_feed": "query_change_feed",
    "QueryChangeFeed": "query_change_feed",

    # Conflicts operations
    "delete_conflict": "delete_conflict",
    "DeleteConflict": "delete_conflict",
    "query_conflicts": "query_conflicts",
    "QueryConflicts": "query_conflicts",
    "read_all_conflicts": "read_all_conflicts",
    "ReadAllConflicts": "read_all_conflicts",
    "read_conflict": "read_conflict",
    "ReadConflict": "read_conflict",

    # Container operations
    "create_container": "create_container",
    "CreateContainer": "create_container",
    "create_container_if_not_exists": "create_container_if_not_exists",
    "CreateContainerIfNotExists": "create_container_if_not_exists",
    "delete_container": "delete_container",
    "DeleteContainer": "delete_container",
    "query_containers": "query_containers",
    "QueryContainers": "query_containers",
    "read_all_containers": "read_all_containers",
    "ReadAllContainers": "read_all_containers",
    "read_container": "read_container",
    "ReadContainer": "read_container",
    "read_container_throughput": "read_container_throughput",
    "ReadContainerThroughput": "read_container_throughput",
    "replace_container": "replace_container",
    "ReplaceContainer": "replace_container",
    "replace_container_throughput": "replace_container_throughput",
    "ReplaceContainerThroughput": "replace_container_throughput",

    # Database operations
    "create_database": "create_database",
    "CreateDatabase": "create_database",
    "create_database_if_not_exists": "create_database_if_not_exists",
    "CreateDatabaseIfNotExists": "create_database_if_not_exists",
    "delete_database": "delete_database",
    "DeleteDatabase": "delete_database",
    "query_databases": "query_databases",
    "QueryDatabases": "query_databases",
    "read_all_databases": "read_all_databases",
    "ReadAllDatabases": "read_all_databases",
    "read_database": "read_database",
    "ReadDatabase": "read_database",
    "read_database_throughput": "read_database_throughput",
    "ReadDatabaseThroughput": "read_database_throughput",
    "replace_database_throughput": "replace_database_throughput",
    "ReplaceDatabaseThroughput": "replace_database_throughput",

    # Encryption key operations
    "create_client_encryption_key": "create_client_encryption_key",
    "CreateClientEncryptionKey": "create_client_encryption_key",
    "query_client_encryption_keys": "query_client_encryption_keys",
    "QueryClientEncryptionKeys": "query_client_encryption_keys",
    "read_all_client_encryption_keys": "read_all_client_encryption_keys",
    "ReadAllClientEncryptionKeys": "read_all_client_encryption_keys",
    "read_client_encryption_key": "read_client_encryption_key",
    "ReadClientEncryptionKey": "read_client_encryption_key",
    "replace_client_encryption_key": "replace_client_encryption_key",
    "ReplaceClientEncryptionKey": "replace_client_encryption_key",

    # Item operations
    "create_item": "create_item",
    "CreateItem": "create_item",
    "delete_all_items_by_partition_key": "delete_all_items_by_partition_key",
    "DeleteAllItemsByPartitionKey": "delete_all_items_by_partition_key",
    "delete_item": "delete_item",
    "DeleteItem": "delete_item",
    "patch_item": "patch_item",
    "PatchItem": "patch_item",
    "query_items": "query_items",
    "QueryItems": "query_items",
    "SqlQuery": "query_items",
    "read_all_items": "read_all_items",
    "ReadAllItems": "read_all_items",
    "read_all_items_of_logical_partition": "read_all_items_of_logical_partition",
    "ReadAllItemsOfLogicalPartition": "read_all_items_of_logical_partition",
    "read_many_items": "read_many_items",
    "ReadManyItems": "read_many_items",
    "read_item": "read_item",
    "ReadItem": "read_item",
    "replace_item": "replace_item",
    "ReplaceItem": "replace_item",
    "upsert_item": "upsert_item",
    "UpsertItem": "upsert_item",

    # Permission operations
    "create_permission": "create_permission",
    "CreatePermission": "create_permission",
    "delete_permission": "delete_permission",
    "DeletePermission": "delete_permission",
    "query_permissions": "query_permissions",
    "QueryPermissions": "query_permissions",
    "read_all_permissions": "read_all_permissions",
    "ReadAllPermissions": "read_all_permissions",
    "read_permission": "read_permission",
    "ReadPermission": "read_permission",
    "replace_permission": "replace_permission",
    "ReplacePermission": "replace_permission",
    "upsert_permission": "upsert_permission",
    "UpsertPermission": "upsert_permission",

    # Stored procedure operations
    "create_stored_procedure": "create_stored_procedure",
    "CreateStoredProcedure": "create_stored_procedure",
    "delete_stored_procedure": "delete_stored_procedure",
    "DeleteStoredProcedure": "delete_stored_procedure",
    "execute_stored_procedure": "execute_stored_procedure",
    "ExecuteStoredProcedure": "execute_stored_procedure",
    "query_stored_procedures": "query_stored_procedures",
    "QueryStoredProcedures": "query_stored_procedures",
    "read_all_stored_procedures": "read_all_stored_procedures",
    "ReadAllStoredProcedures": "read_all_stored_procedures",
    "read_stored_procedure": "read_stored_procedure",
    "ReadStoredProcedure": "read_stored_procedure",
    "replace_stored_procedure": "replace_stored_procedure",
    "ReplaceStoredProcedure": "replace_stored_procedure",

    # Trigger operations
    "create_trigger": "create_trigger",
    "CreateTrigger": "create_trigger",
    "delete_trigger": "delete_trigger",
    "DeleteTrigger": "delete_trigger",
    "query_triggers": "query_triggers",
    "QueryTriggers": "query_triggers",
    "read_all_triggers": "read_all_triggers",
    "ReadAllTriggers": "read_all_triggers",
    "read_trigger": "read_trigger",
    "ReadTrigger": "read_trigger",
    "replace_trigger": "replace_trigger",
    "ReplaceTrigger": "replace_trigger",

    # User operations
    "create_user": "create_user",
    "CreateUser": "create_user",
    "delete_user": "delete_user",
    "DeleteUser": "delete_user",
    "query_users": "query_users",
    "QueryUsers": "query_users",
    "read_all_users": "read_all_users",
    "ReadAllUsers": "read_all_users",
    "read_user": "read_user",
    "ReadUser": "read_user",
    "replace_user": "replace_user",
    "ReplaceUser": "replace_user",
    "upsert_user": "upsert_user",
    "UpsertUser": "upsert_user",

    # User-defined function operations
    "create_user_defined_function": "create_user_defined_function",
    "CreateUserDefinedFunction": "create_user_defined_function",
    "delete_user_defined_function": "delete_user_defined_function",
    "DeleteUserDefinedFunction": "delete_user_defined_function",
    "query_user_defined_functions": "query_user_defined_functions",
    "QueryUserDefinedFunctions": "query_user_defined_functions",
    "read_all_user_defined_functions": "read_all_user_defined_functions",
    "ReadAllUserDefinedFunctions": "read_all_user_defined_functions",
    "read_user_defined_function": "read_user_defined_function",
    "ReadUserDefinedFunction": "read_user_defined_function",
}


def _safe_set_attribute(span: "AbstractSpan", key: str, value: Optional[Any]) -> None:
    """
    Best-effort set attribute on span when OpenTelemetry is present and span is recording.
    Only called for db.* and azure.cosmosdb.* keys.
    """
    if value:
        span.add_attribute(key, value)


def _extract_db_names_from_url(url: Optional[Union[str]]) -> Tuple[Optional[str], Optional[str]]:
    database_name: Optional[str] = None
    collection_name: Optional[str] = None
    if not url:
        return database_name, collection_name
    try:
        path = urllib.parse.urlparse(str(url)).path
        parts = [p for p in path.split("/") if p]
        # find db name after 'dbs'
        if "dbs" in parts:
            idx = parts.index("dbs")
            if idx + 1 < len(parts):
                database_name = parts[idx + 1]
        # find collection/container name
        for token in ("colls", "containers"):
            if token in parts:
                idx = parts.index(token)
                if idx + 1 < len(parts):
                    collection_name = parts[idx + 1]
                    break
    except (ValueError, AttributeError) as ex:
        logger.debug("Failed to extract db/collection from url %s: %s", url, ex, exc_info=True)
    except Exception as ex:  # defensive fallback
        logger.debug("Unexpected error extracting db names: %s", ex, exc_info=True)
    return database_name, collection_name


def _extract_stored_procedure_from_url(url: Optional[Any]) -> Optional[str]:
    if not url:
        return None
    try:
        path = urllib.parse.urlparse(str(url)).path
        parts = [p for p in path.split("/") if p]
        if "sprocs" in parts:
            idx = parts.index("sprocs")
            if idx + 1 < len(parts):
                return parts[idx + 1]
    except (ValueError, AttributeError) as ex:
        logger.debug("Failed to extract stored proc from url %s: %s", url, ex, exc_info=True)
    except Exception as ex:
        logger.debug("Unexpected error extracting stored proc: %s", ex, exc_info=True)
    return None


def _extract_contacted_regions_from_headers(headers: Dict) -> Optional[str]:
    """
    Stub for contacted regions extraction.

    At the moment, contacted regions are not surfaced by the client/backend.
    Probe known header names for future visibility, but always return None.
    """
    return None


def _extract_query_and_parameters(http_request: Any) -> Tuple[Optional[str], Dict[str, Any]]:
    query_text: Optional[str] = None
    params: Dict[str, Any] = {}
    try:
        body = getattr(http_request, "body", None) or getattr(http_request, "data", None) or getattr(http_request,
                                                                                                     "json", None)
        if body is None:
            return query_text, params

        s: Optional[str] = None
        if isinstance(body, (bytes, bytearray)):
            try:
                s = body.decode("utf-8")
            except Exception:
                s = None
        elif isinstance(body, str):
            s = body
        elif isinstance(body, dict):
            try:
                s = json.dumps(body)
            except Exception:
                s = None
        else:
            try:
                s = str(body)
            except Exception:
                s = None

        if s:
            # Attempt to parse JSON body with common Cosmos query shapes
            try:
                obj = json.loads(s)
                # common field names used by SDK: 'query', 'queryText', 'parameters'
                if isinstance(obj, dict):
                    if "query" in obj:
                        query_text = obj.get("query")
                    elif "queryText" in obj:
                        query_text = obj.get("queryText")
                    # parameters may be list of {name, value}
                    p = obj.get("parameters") or obj.get("params") or obj.get("parametersList")
                    if isinstance(p, list):
                        for entry in p:
                            if isinstance(entry, dict) and "name" in entry:
                                key = entry.get("name")
                                if isinstance(key, str) and key.startswith("@"):
                                    params[key] = entry.get("value")
                                else:
                                    params[str(key)] = entry.get("value")
                    # fallback parse a single 'parameters' dict
                    if isinstance(p, dict):
                        for k, v in p.items():
                            params[str(k)] = v
                # if body is a string SQL, treat as query
                elif isinstance(obj, str):
                    query_text = obj
            except Exception:
                # not JSON; treat entire body as query text if looks like SQL
                trimmed = s.strip()
                if trimmed.upper().startswith("SELECT") or trimmed.upper().startswith(
                        "FROM") or "WHERE" in trimmed.upper():
                    query_text = trimmed
    except Exception as ex:
        logger.debug("Error extracting query and parameters: %s", ex, exc_info=True)
    return query_text, params


class CosmosDistributedTracingPolicy(DistributedTracingPolicy):
    """
    Cosmos-specific distributed tracing policy.

    - Overrides on_request/on_response/on_exception and does not call parent implementations.
    - Uses only header names defined on `HttpHeaders`.
    - Records `azure.cosmosdb.response.sub_status_code` when available.
    - Degrades gracefully when OpenTelemetry or optional exceptions are unavailable.
    """

    def __init__(self, tracing_attributes: dict = {}, **kwargs: Any) -> None:
        user_attrs = tracing_attributes if tracing_attributes else kwargs.pop("tracing_attributes", {})
        required_attrs = {_CosmosTracingConstants.DB_SYSTEM_NAME: _CosmosTracingConstants.DB_SYSTEM_VALUE,
                          _CosmosTracingConstants.DB_OPERATION_NAME: None}
        merged_attrs = {**required_attrs, **user_attrs}
        kwargs["tracing_attributes"] = merged_attrs
        super().__init__(**kwargs)

    def _safe_set_opt_in_attribute(self, span: "AbstractSpan", key: str, value: Optional[Any]) -> None:
        """
        Set opt-in attributes on the span if they are part of the OPT_IN_ATTRIBUTES list.
        """
        span.add_attribute(key, value)

    def on_request(self, request: PipelineRequest[HTTPRequestType]) -> None:
        ctxt = request.context.options
        raw_headers = request.http_request.headers or {}
        request_headers = {str(k).lower(): str(v) for k, v in raw_headers.items()}

        span_impl_type = settings.tracing_implementation()
        if span_impl_type is None:
            return

        namer = ctxt.pop("network_span_namer", self._network_span_namer)
        span_name = namer(request.http_request)
        span: "AbstractSpan" = span_impl_type(name=span_name, kind=SpanKind.CLIENT)

        for attr, value in self._tracing_attributes.items():
            if attr == _CosmosTracingConstants.DB_OPERATION_NAME and value is None:
                op_name = None
                parent_span = span.get_current_span()
                parent_name = getattr(parent_span, "name", None)
                if parent_name:
                    op_name = parent_name.rsplit(".", 1)[-1]
                op_name = op_name or request_headers.get(HttpHeaders.ThinClientProxyOperationType.lower())
                if op_name:
                    value = OPERATION_NAME_MAPPING.get(op_name)
            if attr not in OPT_IN_ATTRIBUTES:
                _safe_set_attribute(span, attr, value)

        # Extract and set additional trace attributes
        # Connection mode
        # Python always uses gateway mode
        _safe_set_attribute(span, _CosmosTracingConstants.AZURE_COSMOS_CONNECTION_MODE,
                            "Gateway")
        # Consistency level
        _safe_set_attribute(span, _CosmosTracingConstants.AZURE_COSMOS_CONSISTENCY_LEVEL,
                            request_headers.get(HttpHeaders.ConsistencyLevel.lower()))
        # Collection and namespace from URL
        db_name, coll_name = _extract_db_names_from_url(request.http_request.url)
        _safe_set_attribute(span, _CosmosTracingConstants.DB_COLLECTION_NAME, coll_name)
        _safe_set_attribute(span, _CosmosTracingConstants.DB_NAMESPACE, db_name)
        # Server address and port
        parsed_url = urllib.parse.urlparse(str(request.http_request.url))
        _safe_set_attribute(span, _CosmosTracingConstants.SERVER_ADDRESS, parsed_url.hostname)
        _safe_set_attribute(span, _CosmosTracingConstants.SERVER_PORT, parsed_url.port)
        # Client ID (if available)
        _safe_set_attribute(span, _CosmosTracingConstants.AZURE_CLIENT_ID, getattr(request.context.options,
                                                                                   "client_id", None))
        # Resource provider namespace (if available)
        _safe_set_attribute(span, _CosmosTracingConstants.AZURE_RESOURCE_PROVIDER_NAMESPACE,
                            getattr(request.context.options, "resource_provider_namespace", None))
        # User agent
        _safe_set_attribute(span, _CosmosTracingConstants.USER_AGENT_ORIGINAL,
                            request_headers.get(HttpHeaders.UserAgent.lower()))
        # Request body size
        body = getattr(request.http_request, "body", None)
        if body is not None:
            _safe_set_attribute(span, _CosmosTracingConstants.AZURE_COSMOS_REQUEST_BODY_SIZE,
                                len(body) if isinstance(body, (bytes, bytearray)) else len(str(body)))
        # Query text and batch size
        query_text, params = _extract_query_and_parameters(request.http_request)
        _safe_set_attribute(span, _CosmosTracingConstants.DB_QUERY_TEXT, query_text)
        if isinstance(body, dict) and "batch" in body:
            _safe_set_attribute(span, _CosmosTracingConstants.DB_OPERATION_BATCH_SIZE, len(body["batch"]))

        # Stored procedure name
        _safe_set_attribute(span, _CosmosTracingConstants.DB_STORED_PROCEDURE_NAME,
                            _extract_stored_procedure_from_url(request.http_request.url))
        # Opt in attributes
        if _CosmosTracingConstants.DB_QUERY_PARAMETER_KEY in self._tracing_attributes:
            for param_key, param_value in params.items():
                self._safe_set_opt_in_attribute(
                    span,
                    f"{_CosmosTracingConstants.DB_QUERY_PARAMETER_KEY}.{param_key.lstrip('@')}",
                    param_value
                )

        span.start()
        request.context[_START_TIME_REQUEST_CONTEXT_KEY] = time.time_ns()
        request.http_request.headers.update(span.to_header())
        request.context[self.TRACING_CONTEXT] = span


    def end_span(
            self,
            request: PipelineRequest[HTTPRequestType],
            response: Optional[HTTPResponseType] = None,
            exc_info: Optional[OptExcInfo] = None,
    ) -> None:
        ctx = request.context
        http_request: Union[HttpRequest, LegacyHttpRequest] = request.http_request
        if self.TRACING_CONTEXT not in ctx:
            return
        span: "AbstractSpan" = ctx[self.TRACING_CONTEXT]
        if not span:
            return

        if hasattr(span, "set_http_attributes"):
            span.set_http_attributes(http_request, response=response)

        if response:
            headers = dict(response.headers)
            _safe_set_attribute(span, _CosmosTracingConstants.DB_RESPONSE_STATUS_CODE, response.status_code)
            _safe_set_attribute(span, _CosmosTracingConstants.AZURE_COSMOS_RESPONSE_SUB_STATUS_CODE,
                                headers.get(HttpHeaders.SubStatus.lower()))
            _safe_set_attribute(span, _CosmosTracingConstants.AZURE_COSMOS_OPERATION_REQUEST_CHARGE,
                                float(headers.get(HttpHeaders.RequestCharge.lower(), 0)))
            _safe_set_attribute(span, _CosmosTracingConstants.DB_RESPONSE_RETURNED_ROWS,
                                int(headers.get(HttpHeaders.ItemCount.lower(), 0)))
            _safe_set_attribute(span, _CosmosTracingConstants.AZURE_COSMOS_CONSISTENCY_LEVEL,
                                headers.get(HttpHeaders.ConsistencyLevel.lower()))
            _safe_set_attribute(span, _CosmosTracingConstants.AZURE_COSMOS_OPERATION_CONTACTED_REGIONS,
                                _extract_contacted_regions_from_headers(headers))
            # Recommended attributes from response headers if available
            _safe_set_attribute(span, _CosmosTracingConstants.AZURE_CLIENT_ID, headers.get("x-ms-client-id"))
            _safe_set_attribute(span, _CosmosTracingConstants.USER_AGENT_ORIGINAL,
                                headers.get(HttpHeaders.UserAgent.lower()))


        if exc_info:
            _, exc_val, _ = exc_info
            if exc_val:
                _safe_set_attribute(span, _CosmosTracingConstants.DB_RESPONSE_STATUS_CODE,
                                    getattr(exc_val, "status_code", None))
                _safe_set_attribute(span, _CosmosTracingConstants.AZURE_COSMOS_RESPONSE_SUB_STATUS_CODE,
                                    getattr(exc_val, "sub_status", None))
                _safe_set_attribute(span, _CosmosTracingConstants.ERROR_TYPE, type(exc_val).__name__)

            start_ns = ctx.get(_START_TIME_REQUEST_CONTEXT_KEY)
            if start_ns:
                start_ns = float(start_ns)
                duration_ms = (time.time_ns() - start_ns) / 1_000_000.0
                _safe_set_attribute(span, "azure.cosmosdb.operation.duration_ms", duration_ms)
            span.__exit__(*exc_info)
        else:
            start_ns = ctx.get(_START_TIME_REQUEST_CONTEXT_KEY)
            if start_ns:
                start_ns = float(start_ns)
                duration_ms = (time.time_ns() - start_ns) / 1_000_000.0
                _safe_set_attribute(span, "azure.cosmosdb.operation.duration_ms", duration_ms)
            span.finish()

    def on_response(
        self, request: PipelineRequest[HTTPRequestType], response: PipelineResponse[HTTPRequestType, HTTPResponseType]
    ) -> None:
        self.end_span(request, response=response.http_response if response else None)


    def on_exception(self, request: PipelineRequest[HTTPRequestType]) -> None:
        exc_info: OptExcInfo = (None, None, None)
        try:
            exc_info = sys.exc_info()
        except Exception as ex:
            logger.debug("Failed to obtain sys.exc_info(): %s", ex, exc_info=True)
        self.end_span(request, exc_info=exc_info)

