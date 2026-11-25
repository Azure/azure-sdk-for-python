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
"""Prepare page requests and process backend pages during migration.

This module checks whether legacy/internal page inputs can use the Rust path,
builds PreparedPageRequest objects, and processes BackendPage results. The
caller chooses the permitted execution path before fetching. These helpers
do not select service-backend regions or replicas.

For example, listing containers under "dbs/checkout/colls" produces a prepared
page request with container_link="dbs/checkout" and no SQL query. The Python
backend later converts it to PreparedRequest for the binding call. A returned
backend page is parsed into a Python body and response headers.

Public Rust item queries, read-all operations, and change feed use their own
page iterators with retained feed cursors. They do not use the item-query and
read-all eligibility checks here, although they reuse response conversion.
Database and container feeds also use this module's builders and checks.

Eligibility checks are migration support, not a reason to discard request
validation when legacy execution is retired.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from copy import deepcopy
import time
from typing import Any, Callable, Mapping, Optional, Union, cast

from azure.core.utils import CaseInsensitiveDict

from . import _base as base
from . import _utils
from . import http_constants
from ._backend.operations import (
    OP_LIST_CONTAINERS,
    OP_LIST_DATABASES,
    OP_QUERY_CONTAINERS,
    OP_QUERY_DATABASES,
    OP_QUERY_ITEMS,
)
from ._backend.contracts import PreparedPageRequest, BackendPage
from ._backend.partition_key_input import BindingPartitionKey
from ._constants import _Constants as Constants
from ._cosmos_responses import CosmosDict
from .exceptions import CosmosClientTimeoutError
from ._helpers._partition_key import normalize_partition_key, parse_customer_partition_key_header
from ._helpers._request_settings import (
    is_supported_operation_timeout,
    overrides_driver_owned_header,
    prepare_service_request_settings,
)
from ._helpers._response_parse import page_to_backend_response, process_backend_response
from ._query_advisor import get_query_advice_info
from .partition_key import _build_partition_key_from_properties

# Telemetry keywords are consumed by the Python page recorder, not the driver.
# Other unrecognized keywords make metadata feeds ineligible for the Rust path.
_MASTER_FEED_ALLOWED_INTERNAL_KWARGS = frozenset(
    {
        Constants.OperationStartTime,
        "logger",
        "logging_enable",
        "tracing_options",
        "tracing_attributes",
    }
)
_DATABASE_FEED_ALLOWED_INTERNAL_KWARGS = _MASTER_FEED_ALLOWED_INTERNAL_KWARGS | {
    Constants.Kwargs.TIMEOUT,
}










def can_use_rust_backend_for_query_page(
    *,
    query_payload: Optional[Union[str, dict[str, Any]]],
    options: Mapping[str, Any],
    kwargs: Mapping[str, Any],
    container_properties: Optional[Mapping[str, Any]],
    is_query_plan: bool,
    resource_type: str,
) -> bool:
    """Check inputs for the legacy/internal item-query page path.

    This is not the public retained-query path. The checks below describe what
    this compatibility path forwards, not everything the Rust driver supports.
    In particular, read_items' legacy internal query shapes and options this
    path does not handle are not eligible for Rust dispatch here.

    Query text is not searched for SQL clauses. Passing these input checks
    does not prove that the Rust driver can execute the query. The caller's
    run_page_operation rejects ineligible Rust requests before execution.
    Preflight and execution errors never switch a Rust query to legacy Python.

    :keyword query_payload: SQL text or query dictionary, or None for a read feed.
    :paramtype query_payload: str or dict[str, Any] or None
    :keyword options: Internal request options to check for supported query settings.
    :paramtype options: Mapping[str, Any]
    :keyword kwargs: Additional internal arguments checked for unsupported range routing.
    :paramtype kwargs: Mapping[str, Any]
    :keyword container_properties: Container metadata used to detect prefix partition keys.
    :paramtype container_properties: Mapping[str, Any] or None
    :keyword bool is_query_plan: Whether this request fetches a query plan rather than results.
    :keyword str resource_type: Resource type of the requested feed.
    :return: Whether the compatibility path can forward the supplied request.
    :rtype: bool
    """
    if (
        query_payload is None
        or is_query_plan
        or resource_type != http_constants.ResourceType.Document
        or any(key in kwargs for key in ("feed_range", "prefix_partition_key_object", "prefix_partition_key_value"))
    ):
        return False
    # These options are not supported by this compatibility page path.
    if (
        Constants.Kwargs.AVAILABILITY_STRATEGY in options
        or overrides_driver_owned_header(options)
        or "fullTextScoreScope" in options
        or options.get("populateQueryAdvice")
    ):
        return False

    has_partition_key = "partitionKey" in options
    partition_key_value = options.get("partitionKey")
    partition_key_wire = BindingPartitionKey("cross_partition")
    if has_partition_key:
        try:
            partition_key_wire = normalize_partition_key(partition_key_value)
        except (TypeError, ValueError):
            return False

    if partition_key_wire.kind in ("cross_partition", "empty_sentinel"):
        # Do not use this cross-partition path when the customer app explicitly
        # disabled it. This checks an option, not the SQL text.
        return options.get("enableCrossPartitionQuery") is not False

    if container_properties is None:
        return False
    partition_key_obj = _build_partition_key_from_properties(container_properties)
    # Prefix detection is shared with the SDK's partition-key implementation.
    return not partition_key_obj._is_prefix_partition_key(partition_key_value)  # pylint: disable=protected-access


def _master_feed_page_is_rust_eligible(
    *,
    options: Mapping[str, Any],
    kwargs: Mapping[str, Any],
    is_query_plan: bool,
    resource_type: str,
    expected_resource_type: str,
    allow_timeout: bool = False,
) -> bool:
    """Share option checks for listing or querying databases and containers.

    The caller supplies the expected resource type. When allow_timeout is True,
    the timeout must be supported and agree between options and keyword arguments.
    Otherwise any non-None timeout is rejected.

    Other checks prevent unsupported options and overrides of headers owned by
    the Rust driver from being silently dropped.

    :keyword options: Internal request options to validate.
    :paramtype options: Mapping[str, Any]
    :keyword kwargs: Additional request arguments to validate.
    :paramtype kwargs: Mapping[str, Any]
    :keyword bool is_query_plan: Whether this is a query-plan request.
    :keyword str resource_type: Actual resource type.
    :keyword str expected_resource_type: Resource type supported by the caller.
    :keyword bool allow_timeout: Whether supported, consistent timeout values are permitted.
    :return: Whether the request passes the metadata-feed compatibility checks.
    :rtype: bool
    """
    if is_query_plan or resource_type != expected_resource_type or options.get("changeFeedState") is not None:
        return False
    allowed_kwargs = _MASTER_FEED_ALLOWED_INTERNAL_KWARGS
    if allow_timeout:
        timeout = options.get(Constants.Kwargs.TIMEOUT)
        if not is_supported_operation_timeout(timeout):
            return False
        # The builder carries the option value. Do not accept a timeout supplied
        # only through internal kwargs or conflicting with the forwarded value.
        if Constants.Kwargs.TIMEOUT in kwargs and kwargs[Constants.Kwargs.TIMEOUT] != timeout:
            return False
        allowed_kwargs = _DATABASE_FEED_ALLOWED_INTERNAL_KWARGS
    elif (
        options.get(Constants.Kwargs.TIMEOUT) is not None
        or kwargs.get(Constants.Kwargs.TIMEOUT) is not None
    ):
        return False
    return not (
        Constants.Kwargs.AVAILABILITY_STRATEGY in options
        or set(kwargs).difference(allowed_kwargs)
        or overrides_driver_owned_header(options)
    )


def _container_feed_page_is_rust_eligible(
    *,
    options: Mapping[str, Any],
    kwargs: Mapping[str, Any],
    is_query_plan: bool,
    resource_type: str,
) -> bool:
    """Apply the shared checks to a container page, allowing an operation timeout.

    :keyword options: Internal request options.
    :paramtype options: Mapping[str, Any]
    :keyword kwargs: Additional request arguments.
    :paramtype kwargs: Mapping[str, Any]
    :keyword bool is_query_plan: Whether this is a query-plan request.
    :keyword str resource_type: Requested resource type.
    :return: Whether a container page can use the Rust path.
    :rtype: bool
    """
    return _master_feed_page_is_rust_eligible(
        options=options,
        kwargs=kwargs,
        is_query_plan=is_query_plan,
        resource_type=resource_type,
        expected_resource_type=http_constants.ResourceType.Collection,
        allow_timeout=True,
    )


def can_use_rust_list_containers(
    *,
    path: str,
    options: Mapping[str, Any],
    kwargs: Mapping[str, Any],
    is_query_plan: bool,
    resource_type: str,
) -> bool:
    """Check the database path and options for a list_containers page.

    :keyword str path: Container-feed path under a database.
    :keyword options: Internal listing options.
    :paramtype options: Mapping[str, Any]
    :keyword kwargs: Additional listing arguments.
    :paramtype kwargs: Mapping[str, Any]
    :keyword bool is_query_plan: Whether this is a query-plan request.
    :keyword str resource_type: Requested resource type.
    :return: Whether the path and options are supported by the Rust listing path.
    :rtype: bool
    """
    if not _database_link_from_colls_path(path):
        return False
    return _master_feed_page_is_rust_eligible(
        options=options,
        kwargs=kwargs,
        is_query_plan=is_query_plan,
        resource_type=resource_type,
        expected_resource_type=http_constants.ResourceType.Collection,
        allow_timeout=True,
    )


def can_use_rust_query_containers(
    *,
    path: str,
    query_payload: Optional[Union[str, dict[str, Any]]],
    options: Mapping[str, Any],
    kwargs: Mapping[str, Any],
    is_query_plan: bool,
    resource_type: str,
) -> bool:
    """Check the query dictionary, database path, and container-page options.

    :keyword str path: Container-feed path under a database.
    :keyword query_payload: Query dictionary, legacy SQL text, or None.
    :paramtype query_payload: str or dict[str, Any] or None
    :keyword options: Internal query options.
    :paramtype options: Mapping[str, Any]
    :keyword kwargs: Additional query arguments.
    :paramtype kwargs: Mapping[str, Any]
    :keyword bool is_query_plan: Whether this is a query-plan request.
    :keyword str resource_type: Requested resource type.
    :return: Whether the Rust path supports the query shape, path, and options.
    :rtype: bool
    """
    if query_payload is None:
        return False
    # Legacy SqlQuery mode uses a plain-text body. This Rust path expects the
    # query dictionary used for application/query+json instead.
    if not isinstance(query_payload, dict):
        return False
    if not _database_link_from_colls_path(path):
        return False
    return _container_feed_page_is_rust_eligible(
        options=options,
        kwargs=kwargs,
        is_query_plan=is_query_plan,
        resource_type=resource_type,
    )


def can_use_rust_list_databases(
    *,
    options: Mapping[str, Any],
    kwargs: Mapping[str, Any],
    is_query_plan: bool,
    resource_type: str,
) -> bool:
    """Apply the shared checks to a list_databases page.

    :keyword options: Internal listing options.
    :paramtype options: Mapping[str, Any]
    :keyword kwargs: Additional listing arguments.
    :paramtype kwargs: Mapping[str, Any]
    :keyword bool is_query_plan: Whether this is a query-plan request.
    :keyword str resource_type: Requested resource type.
    :return: Whether the Rust path supports the database-listing options.
    :rtype: bool
    """
    return _master_feed_page_is_rust_eligible(
        options=options,
        kwargs=kwargs,
        is_query_plan=is_query_plan,
        resource_type=resource_type,
        expected_resource_type=http_constants.ResourceType.Database,
        allow_timeout=True,
    )


def can_use_rust_query_databases(
    *,
    query_payload: Optional[Union[str, dict[str, Any]]],
    options: Mapping[str, Any],
    kwargs: Mapping[str, Any],
    is_query_plan: bool,
    resource_type: str,
) -> bool:
    """Check the query dictionary and options for a query_databases page.

    :keyword query_payload: Query dictionary, legacy SQL text, or None.
    :paramtype query_payload: str or dict[str, Any] or None
    :keyword options: Internal query options.
    :paramtype options: Mapping[str, Any]
    :keyword kwargs: Additional query arguments.
    :paramtype kwargs: Mapping[str, Any]
    :keyword bool is_query_plan: Whether this is a query-plan request.
    :keyword str resource_type: Requested resource type.
    :return: Whether the Rust path supports the database query shape and options.
    :rtype: bool
    """
    if query_payload is None or is_query_plan:
        return False
    # A string here belongs to legacy SqlQuery mode's plain-text body, not the
    # query dictionary expected by this Rust path.
    if not isinstance(query_payload, dict):
        return False
    return _master_feed_page_is_rust_eligible(
        options=options,
        kwargs=kwargs,
        is_query_plan=is_query_plan,
        resource_type=resource_type,
        expected_resource_type=http_constants.ResourceType.Database,
        allow_timeout=True,
    )


def _build_prepared_page_request(
    *,
    op: str,
    container_link: str,
    resource_type: str,
    options: Mapping[str, Any],
    req_headers: Mapping[str, Any],
    query_payload: Optional[Union[str, Mapping[str, Any]]] = None,
) -> PreparedPageRequest:
    """Build a prepared page request from client headers and request options.

    For example, maxItemCount=100 becomes max_item_count=100, not a second
    page-size header. Continuation and partition-key values likewise move to
    their dedicated fields. The Python backend converts this record to a
    prepared request before calling the binding.

    :keyword str op: Backend operation identifier.
    :keyword str container_link: Resource link, or an empty string for account-level feeds.
    :keyword str resource_type: Resource type used when preparing headers and settings.
    :keyword options: Internal request options, including paging and partition-key values.
    :paramtype options: Mapping[str, Any]
    :keyword req_headers: Request headers used as the initial header mapping.
    :paramtype req_headers: Mapping[str, Any]
    :keyword query_payload: SQL text or query dictionary; None for a read feed.
    :paramtype query_payload: str or Mapping[str, Any] or None
    :return: Prepared page request with dedicated paging, query, and partition-key fields.
    :rtype: ~azure.cosmos._backend.contracts.PreparedPageRequest
    """
    if resource_type in ("dbs", "colls"):
        timeout = options.get(Constants.Kwargs.TIMEOUT)
        started = options.get(Constants.OperationStartTime)
        if timeout is not None and started is not None and time.time() - started >= timeout:
            raise CosmosClientTimeoutError()
    header_options = {key: value for key, value in options.items() if key not in ("maxItemCount", "continuation")}
    headers, settings = prepare_service_request_settings(header_options, req_headers, resource_type=resource_type)
    raw_count = headers.pop(http_constants.HttpHeaders.PageSize, None)
    max_item_count = options.get("maxItemCount")
    if max_item_count is None and raw_count is not None:
        try:
            max_item_count = int(raw_count)
        except ValueError as error:
            raise ValueError("x-ms-max-item-count must be an integer.") from error
    raw_continuation = headers.pop(http_constants.HttpHeaders.Continuation, None)
    continuation = options.get("continuation")
    if continuation is None:
        continuation = raw_continuation
    raw_partition_key = headers.pop(http_constants.HttpHeaders.PartitionKey, None)
    partition_key = BindingPartitionKey("cross_partition")
    if resource_type == "docs" and "partitionKey" in options:
        partition_key = normalize_partition_key(options["partitionKey"])
        if partition_key.kind == "empty_sentinel":
            partition_key = BindingPartitionKey("cross_partition")
    elif resource_type == "docs" and raw_partition_key is not None:
        partition_key = parse_customer_partition_key_header(raw_partition_key)
    if query_payload is not None:
        headers.pop(http_constants.HttpHeaders.IsQuery, None)
        settings = replace(settings, query=replace(settings.query, is_query=True))
    return PreparedPageRequest(
        op=op,
        container_link=container_link,
        query=query_payload if isinstance(query_payload, str) else (
            query_payload.get("query") if query_payload is not None else None
        ),
        parameters=tuple(query_payload.get("parameters") or ()) if isinstance(query_payload, Mapping) else (),
        partition_key=partition_key if resource_type == "docs" else BindingPartitionKey("cross_partition"),
        max_item_count=max_item_count,
        continuation=continuation,
        headers=headers,
        settings=settings,
    )


def _extract_container_link_from_docs_path(path: str) -> str:
    """Turn a path such as "dbs/checkout/colls/orders/docs" into its container link.

    :param str path: Resource path with optional boundary slashes and trailing /docs.
    :return: Normalized path with any trailing /docs removed.
    :rtype: str
    """
    normalized_path = base.TrimBeginningAndEndingSlashes(path)
    return normalized_path[: -len("/docs")] if normalized_path.endswith("/docs") else normalized_path


def build_query_items_prepared_page_request(
    *,
    path: str,
    query_payload: Union[str, dict[str, Any]],
    options: Mapping[str, Any],
    req_headers: Mapping[str, Any],
) -> PreparedPageRequest:
    """Build a prepared page request carrying the item query and its parameters.

    :keyword str path: Item-feed path under the container.
    :keyword query_payload: SQL text or a query dictionary containing SQL and parameters.
    :paramtype query_payload: str or dict[str, Any]
    :keyword options: Internal query and paging options.
    :paramtype options: Mapping[str, Any]
    :keyword req_headers: Initial request headers.
    :paramtype req_headers: Mapping[str, Any]
    :return: Prepared item-query page request.
    :rtype: ~azure.cosmos._backend.contracts.PreparedPageRequest
    """
    return _build_prepared_page_request(
        op=OP_QUERY_ITEMS,
        container_link=_extract_container_link_from_docs_path(path),
        resource_type="docs",
        query_payload=query_payload,
        options=options,
        req_headers=req_headers,
    )


def build_list_databases_page(
    *,
    options: Mapping[str, Any],
    req_headers: Mapping[str, Any],
) -> PreparedPageRequest:
    """Build a prepared page request for listing databases, with no SQL query.

    :keyword options: Internal listing options, including an optional content type.
    :paramtype options: Mapping[str, Any]
    :keyword req_headers: Initial request headers.
    :paramtype req_headers: Mapping[str, Any]
    :return: Prepared database-listing page request.
    :rtype: ~azure.cosmos._backend.contracts.PreparedPageRequest
    """
    prepared = _build_prepared_page_request(
        op=OP_LIST_DATABASES,
        container_link="",
        resource_type="dbs",
        options=options,
        req_headers=req_headers,
    )
    if options.get("contentType"):
        prepared = replace(
            prepared,
            settings=replace(
                prepared.settings,
                resource=replace(prepared.settings.resource, content_type=options["contentType"]),
            ),
        )
    return prepared


def build_query_databases_page(
    *,
    query_payload: Union[str, Mapping[str, Any]],
    options: Mapping[str, Any],
    req_headers: Mapping[str, Any],
) -> PreparedPageRequest:
    """Build a prepared page request carrying the database query.

    :keyword query_payload: SQL text or query dictionary.
    :paramtype query_payload: str or Mapping[str, Any]
    :keyword options: Internal query and paging options.
    :paramtype options: Mapping[str, Any]
    :keyword req_headers: Initial request headers.
    :paramtype req_headers: Mapping[str, Any]
    :return: Prepared database-query page request.
    :rtype: ~azure.cosmos._backend.contracts.PreparedPageRequest
    """
    return _build_prepared_page_request(
        op=OP_QUERY_DATABASES,
        container_link="",
        resource_type="dbs",
        query_payload=query_payload,
        options=options,
        req_headers=req_headers,
    )


def _database_link_from_colls_path(path: str) -> str:
    """Turn "dbs/checkout/colls" into "dbs/checkout", or return "" for an invalid path.

    :param str path: Container-feed path, optionally surrounded by slashes.
    :return: Database resource link, or an empty string if the path does not match.
    :rtype: str
    """
    normalized_path = base.TrimBeginningAndEndingSlashes(path)
    if not normalized_path.endswith("/colls"):
        return ""
    database_link = normalized_path[: -len("/colls")]
    parts = database_link.split("/")
    if len(parts) != 2 or parts[0] != "dbs" or not parts[1]:
        return ""
    return database_link


def build_list_containers_page(
    *,
    path: str,
    options: Mapping[str, Any],
    req_headers: Mapping[str, Any],
) -> PreparedPageRequest:
    """Build a prepared page request for listing containers in the named database.

    :keyword str path: Container-feed path under the database.
    :keyword options: Internal listing and paging options.
    :paramtype options: Mapping[str, Any]
    :keyword req_headers: Initial request headers.
    :paramtype req_headers: Mapping[str, Any]
    :return: Prepared container-listing page request.
    :rtype: ~azure.cosmos._backend.contracts.PreparedPageRequest
    """
    return _build_prepared_page_request(
        op=OP_LIST_CONTAINERS,
        container_link=_database_link_from_colls_path(path),
        resource_type="colls",
        options=options,
        req_headers=req_headers,
    )


def build_query_containers_page(
    *,
    path: str,
    query_payload: Union[str, Mapping[str, Any]],
    options: Mapping[str, Any],
    req_headers: Mapping[str, Any],
) -> PreparedPageRequest:
    """Build a prepared page request carrying the container query and database link.

    :keyword str path: Container-feed path under the database.
    :keyword query_payload: SQL text or query dictionary.
    :paramtype query_payload: str or Mapping[str, Any]
    :keyword options: Internal query and paging options.
    :paramtype options: Mapping[str, Any]
    :keyword req_headers: Initial request headers.
    :paramtype req_headers: Mapping[str, Any]
    :return: Prepared container-query page request.
    :rtype: ~azure.cosmos._backend.contracts.PreparedPageRequest
    """
    return _build_prepared_page_request(
        op=OP_QUERY_CONTAINERS,
        container_link=_database_link_from_colls_path(path),
        resource_type="colls",
        query_payload=query_payload,
        options=options,
        req_headers=req_headers,
    )


@dataclass(frozen=True)
class ParsedRustPage:
    """Python record containing a body decoded from BackendPage and processed response headers."""

    body: dict[str, Any]
    headers: CaseInsensitiveDict


def finalize_rust_page_response(
    *,
    client_connection: Any,
    req_headers: Mapping[str, Any],
    parsed: dict[str, Any],
    last_response_headers: CaseInsensitiveDict,
    internal_headers_capture: Optional[dict[str, Any]],
    response_headers: Optional[CaseInsensitiveDict],
    response_hook: Optional[Callable[[Mapping[str, Any], dict[str, Any]], None]],
) -> CaseInsensitiveDict:
    """Update session state and response headers, then call the response hook.

    Shared by item, database, and container pages. Decode index metrics and
    query advice only when their headers are present; keep other headers,
    including diagnostics. Copy headers into the connection and any supplied
    response_headers dictionary. internal_headers_capture records the headers
    before those conversions.

    The response hook receives its own header copy but the same parsed body.
    A hook error is raised to the caller, not used to select legacy fallback.

    :keyword client_connection: Connection whose session and last-response state are updated.
    :paramtype client_connection: Any
    :keyword req_headers: Request headers used when updating session state.
    :paramtype req_headers: Mapping[str, Any]
    :keyword parsed: Decoded response body passed to session handling and the response hook.
    :paramtype parsed: dict[str, Any]
    :keyword last_response_headers: Response headers to process in place.
    :paramtype last_response_headers: ~azure.core.utils.CaseInsensitiveDict
    :keyword internal_headers_capture: Optional destination for headers before conversion.
    :paramtype internal_headers_capture: dict[str, Any] or None
    :keyword response_headers: Optional destination for a copy of the processed headers.
    :paramtype response_headers: ~azure.core.utils.CaseInsensitiveDict or None
    :keyword response_hook: Optional callback receiving copied headers and the decoded body.
    :paramtype response_hook: Callable or None
    :return: Processed response headers.
    :rtype: ~azure.core.utils.CaseInsensitiveDict
    """
    if internal_headers_capture is not None:
        internal_headers_capture.clear()
        internal_headers_capture.update(last_response_headers)
    # The internal connection owns session updates for both execution backends.
    client_connection._UpdateSessionIfRequired(  # pylint: disable=protected-access
        req_headers, parsed, last_response_headers
    )
    if last_response_headers.get(http_constants.HttpHeaders.IndexUtilization) is not None:
        index_metrics_raw = last_response_headers[http_constants.HttpHeaders.IndexUtilization]
        last_response_headers[http_constants.HttpHeaders.IndexUtilization] = (
            _utils.get_index_metrics_info(index_metrics_raw)
        )
    if last_response_headers.get(http_constants.HttpHeaders.QueryAdvice) is not None:
        query_advice_raw = last_response_headers[http_constants.HttpHeaders.QueryAdvice]
        last_response_headers[http_constants.HttpHeaders.QueryAdvice] = (
            get_query_advice_info(query_advice_raw)
        )
    client_connection.last_response_headers = deepcopy(last_response_headers)
    if response_headers is not None:
        response_headers.clear()
        response_headers.update(deepcopy(last_response_headers))
    if response_hook:
        response_hook(deepcopy(last_response_headers), parsed)
    return last_response_headers


def process_query_page(  # pylint: disable=too-many-arguments
    *,
    page: BackendPage,
    client_connection: Any,
    req_headers: Mapping[str, Any],
    internal_headers_capture: Optional[dict[str, Any]],
    response_headers: Optional[CaseInsensitiveDict],
    response_hook: Optional[Callable[[Mapping[str, Any], dict[str, Any]], None]],
) -> ParsedRustPage:
    """Decode a backend page and perform the shared session, header, and hook updates.

    Return the parsed body and processed headers together. The result is Python
    data, not a Rust driver page or a feed cursor.

    :keyword page: Backend page containing response bytes and headers.
    :paramtype page: ~azure.cosmos._backend.contracts.BackendPage
    :keyword client_connection: Connection whose response and session state are updated.
    :paramtype client_connection: Any
    :keyword req_headers: Original request headers used for session processing.
    :paramtype req_headers: Mapping[str, Any]
    :keyword internal_headers_capture: Optional destination for unprocessed response headers.
    :paramtype internal_headers_capture: dict[str, Any] or None
    :keyword response_headers: Optional destination for processed response headers.
    :paramtype response_headers: ~azure.core.utils.CaseInsensitiveDict or None
    :keyword response_hook: Optional callback receiving headers and the decoded body.
    :paramtype response_hook: Callable or None
    :return: Decoded body and processed headers.
    :rtype: ~azure.cosmos._query_rust_routing.ParsedRustPage
    """
    parsed_response = cast(
        CosmosDict,
        process_backend_response(
            page_to_backend_response(page),
            client_connection=None,
            response_hook=None,
        ),
    )
    parsed = cast(dict[str, Any], parsed_response)
    last_response_headers = parsed_response.get_response_headers()
    client_connection.last_response_headers = deepcopy(last_response_headers)
    last_response_headers = finalize_rust_page_response(
        client_connection=client_connection,
        req_headers=req_headers,
        parsed=parsed,
        last_response_headers=last_response_headers,
        internal_headers_capture=internal_headers_capture,
        response_headers=response_headers,
        response_hook=response_hook,
    )
    return ParsedRustPage(body=parsed, headers=last_response_headers)
