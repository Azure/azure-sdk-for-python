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
validation when legacy execution is retired. Terminology follows
docs/V5/VOCABULARY.md.
"""
from __future__ import annotations

from ._backend.partition_key_input import BindingPartitionKey

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
    OP_READ_ALL_ITEMS,
)
from ._backend.contracts import BackendResponse, PreparedPageRequest, BackendPage
from ._constants import _Constants as Constants
from ._cosmos_responses import CosmosDict
from .exceptions import CosmosClientTimeoutError
from ._helpers._partition_key import normalize_partition_key, parse_customer_partition_key_header
from ._helpers._request_settings import (
    is_supported_operation_timeout,
    overrides_driver_owned_header,
    prepare_service_request_settings,
)
from ._helpers._response_parse import process_backend_response
from ._query_advisor import get_query_advice_info
from .partition_key import _build_partition_key_from_properties

# List/query database and container pages only forward the internal keywords
# listed here. Other keywords make the input ineligible for the Rust path.
_MASTER_FEED_ALLOWED_INTERNAL_KWARGS = frozenset({
    Constants.OperationStartTime,
})
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
    In particular, they keep read_items' internal queries on the legacy path
    and reject options this path does not handle.

    Query text is not searched for SQL clauses. Passing these input checks
    does not prove that the Rust driver can execute the query. The caller's
    run_page_operation decides any permitted fallback before execution;
    an execution error is not permission to repeat the query through legacy.
    """
    if query_payload is None or is_query_plan:
        return False
    if resource_type != http_constants.ResourceType.Document:
        return False
    # read_items marks its internal "id IN (...)" queries with this flag.
    # Keep that existing legacy path; its individual item reads are separate.
    if options.get(Constants.ReadItemsQueryLeg):
        return False
    if "feed_range" in kwargs:
        return False
    if "prefix_partition_key_object" in kwargs or "prefix_partition_key_value" in kwargs:
        return False
    # These options are not supported by this compatibility page path.
    if options.get("read_timeout") is not None:
        return False
    if Constants.Kwargs.AVAILABILITY_STRATEGY in options:
        return False
    if overrides_driver_owned_header(options):
        return False
    if "fullTextScoreScope" in options:
        return False
    if options.get("populateQueryAdvice"):
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
        if options.get("enableCrossPartitionQuery") is False:
            return False
        return True

    if container_properties is None:
        return False
    partition_key_obj = _build_partition_key_from_properties(container_properties)
    if partition_key_obj._is_prefix_partition_key(partition_key_value):
        return False
    return True


def can_use_rust_backend_for_read_all_items_page(
    *,
    options: Mapping[str, Any],
    kwargs: Mapping[str, Any],
    is_query_plan: bool,
    resource_type: str,
    partition_key_range_id: Optional[str],
) -> bool:
    """Check inputs for the legacy/internal whole-container read path.

    This is separate from the public retained read-all page iterator. Reject
    query-plan requests, change feed, a selected partition range, and options
    this compatibility path cannot forward.
    """
    if is_query_plan:
        return False
    if resource_type != http_constants.ResourceType.Document:
        return False
    if partition_key_range_id is not None:
        return False
    if options.get("changeFeedState") is not None:
        return False
    if options.get("read_timeout") is not None:
        return False
    if Constants.Kwargs.AVAILABILITY_STRATEGY in options:
        return False
    if overrides_driver_owned_header(options):
        return False
    if "populateQueryMetrics" in options:
        return False
    if "feed_range" in kwargs:
        return False
    return True


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
    """
    if is_query_plan:
        return False
    if resource_type != expected_resource_type:
        return False
    if options.get("changeFeedState") is not None:
        return False
    if options.get(Constants.Kwargs.READ_TIMEOUT) is not None:
        return False
    if kwargs.get(Constants.Kwargs.READ_TIMEOUT) is not None:
        return False
    allowed_kwargs = _MASTER_FEED_ALLOWED_INTERNAL_KWARGS
    if allow_timeout:
        timeout = options.get(Constants.Kwargs.TIMEOUT)
        if not is_supported_operation_timeout(timeout):
            return False
        # The builder carries the option value. Do not accept an unforwarded or
        # conflicting timeout supplied only through internal kwargs.
        if Constants.Kwargs.TIMEOUT in kwargs and kwargs[Constants.Kwargs.TIMEOUT] != timeout:
            return False
        allowed_kwargs = _DATABASE_FEED_ALLOWED_INTERNAL_KWARGS
    elif (
        options.get(Constants.Kwargs.TIMEOUT) is not None
        or kwargs.get(Constants.Kwargs.TIMEOUT) is not None
    ):
        return False
    if Constants.Kwargs.AVAILABILITY_STRATEGY in options:
        return False
    if set(kwargs).difference(allowed_kwargs):
        return False
    if overrides_driver_owned_header(options):
        return False
    return True


def _container_feed_page_is_rust_eligible(
    *,
    options: Mapping[str, Any],
    kwargs: Mapping[str, Any],
    is_query_plan: bool,
    resource_type: str,
) -> bool:
    """Apply the shared checks to a container page, allowing an operation timeout."""
    return _master_feed_page_is_rust_eligible(
        options=options,
        kwargs=kwargs,
        is_query_plan=is_query_plan,
        resource_type=resource_type,
        expected_resource_type=http_constants.ResourceType.Collection,
        allow_timeout=True,
    )


def can_use_rust_backend_for_list_containers_page(
    *,
    path: str,
    options: Mapping[str, Any],
    kwargs: Mapping[str, Any],
    is_query_plan: bool,
    resource_type: str,
) -> bool:
    """Check the database path and options for a list_containers page."""
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


def can_use_rust_backend_for_query_containers_page(
    *,
    path: str,
    query_payload: Optional[Union[str, dict[str, Any]]],
    options: Mapping[str, Any],
    kwargs: Mapping[str, Any],
    is_query_plan: bool,
    resource_type: str,
) -> bool:
    """Check the query dictionary, database path, and container-page options."""
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


def can_use_rust_backend_for_list_databases_page(
    *,
    options: Mapping[str, Any],
    kwargs: Mapping[str, Any],
    is_query_plan: bool,
    resource_type: str,
) -> bool:
    """Apply the shared checks to a list_databases page."""
    return _master_feed_page_is_rust_eligible(
        options=options,
        kwargs=kwargs,
        is_query_plan=is_query_plan,
        resource_type=resource_type,
        expected_resource_type=http_constants.ResourceType.Database,
        allow_timeout=True,
    )


def can_use_rust_backend_for_query_databases_page(
    *,
    query_payload: Optional[Union[str, dict[str, Any]]],
    options: Mapping[str, Any],
    kwargs: Mapping[str, Any],
    is_query_plan: bool,
    resource_type: str,
) -> bool:
    """Check the query dictionary and options for a query_databases page."""
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
    """Turn a path such as "dbs/checkout/colls/orders/docs" into its container link."""
    normalized_path = base.TrimBeginningAndEndingSlashes(path)
    return normalized_path[: -len("/docs")] if normalized_path.endswith("/docs") else normalized_path


def build_query_items_prepared_page_request(
    *,
    path: str,
    query_payload: Union[str, dict[str, Any]],
    options: Mapping[str, Any],
    req_headers: Mapping[str, Any],
) -> PreparedPageRequest:
    """Build a prepared page request carrying the item query and its parameters."""
    return _build_prepared_page_request(
        op=OP_QUERY_ITEMS,
        container_link=_extract_container_link_from_docs_path(path),
        resource_type="docs",
        query_payload=query_payload,
        options=options,
        req_headers=req_headers,
    )


def build_read_all_items_prepared_page_request(
    *,
    path: str,
    options: Mapping[str, Any],
    req_headers: Mapping[str, Any],
) -> PreparedPageRequest:
    """Build a prepared page request for read_all_items without constructing SQL.

    The partition-key field carries the requested scope. Choosing the Rust
    driver operation happens later through the binding, not in this builder.
    """
    return _build_prepared_page_request(
        op=OP_READ_ALL_ITEMS,
        container_link=_extract_container_link_from_docs_path(path),
        resource_type="docs",
        options=options,
        req_headers=req_headers,
    )


def build_list_databases_prepared_page_request(
    *,
    options: Mapping[str, Any],
    req_headers: Mapping[str, Any],
) -> PreparedPageRequest:
    """Build a prepared page request for listing databases, with no SQL query."""
    return _build_prepared_page_request(
        op=OP_LIST_DATABASES,
        container_link="",
        resource_type="dbs",
        options=options,
        req_headers=req_headers,
    )


def build_query_databases_prepared_page_request(
    *,
    query_payload: Union[str, Mapping[str, Any]],
    options: Mapping[str, Any],
    req_headers: Mapping[str, Any],
) -> PreparedPageRequest:
    """Build a prepared page request carrying the database query."""
    return _build_prepared_page_request(
        op=OP_QUERY_DATABASES,
        container_link="",
        resource_type="dbs",
        query_payload=query_payload,
        options=options,
        req_headers=req_headers,
    )


def _database_link_from_colls_path(path: str) -> str:
    """Turn "dbs/checkout/colls" into "dbs/checkout", or return "" for an invalid path."""
    normalized_path = base.TrimBeginningAndEndingSlashes(path)
    if not normalized_path.endswith("/colls"):
        return ""
    database_link = normalized_path[: -len("/colls")]
    parts = database_link.split("/")
    if len(parts) != 2 or parts[0] != "dbs" or not parts[1]:
        return ""
    return database_link


def build_list_containers_prepared_page_request(
    *,
    path: str,
    options: Mapping[str, Any],
    req_headers: Mapping[str, Any],
) -> PreparedPageRequest:
    """Build a prepared page request for listing containers in the named database."""
    return _build_prepared_page_request(
        op=OP_LIST_CONTAINERS,
        container_link=_database_link_from_colls_path(path),
        resource_type="colls",
        options=options,
        req_headers=req_headers,
    )


def build_query_containers_prepared_page_request(
    *,
    path: str,
    query_payload: Union[str, Mapping[str, Any]],
    options: Mapping[str, Any],
    req_headers: Mapping[str, Any],
) -> PreparedPageRequest:
    """Build a prepared page request carrying the container query and database link."""
    return _build_prepared_page_request(
        op=OP_QUERY_CONTAINERS,
        container_link=_database_link_from_colls_path(path),
        resource_type="colls",
        query_payload=query_payload,
        options=options,
        req_headers=req_headers,
    )


def page_to_backend_response(page: BackendPage) -> BackendResponse:
    """Represent a backend page's response fields as BackendResponse for body parsing.

    Reuse the headers and body bytes without decoding them. Page-only
    continuation information is not included.
    """
    return BackendResponse(
        status_code=page.status_code,
        sub_status=page.sub_status,
        headers=page.headers,
        body=page.body,
        diagnostics=page.diagnostics,
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
    """
    if internal_headers_capture is not None:
        internal_headers_capture.clear()
        internal_headers_capture.update(last_response_headers)
    client_connection._UpdateSessionIfRequired(req_headers, parsed, last_response_headers)
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
