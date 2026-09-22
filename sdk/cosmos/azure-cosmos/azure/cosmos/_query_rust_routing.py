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
"""Compatibility page-routing helpers used by sync and async client connections.

Public Rust ``query_items``, ``read_all_items`` and change feed use independent
retained pagers, not the query/feed eligibility gates below. Those gates remain
for legacy/internal connection paths; the master-resource feeds still use this
module directly. Shared request/response adapters are also reused by the retained
pagers.

It has three jobs: decide whether a page is safe for Rust (the ``can_use_*``
gates), build the page request (``build_query_items_prepared_query``,
``build_read_all_items_prepared_query``, or
``build_list_databases_prepared_query``), and finish the response to match
legacy (``finalize_rust_page_response``).

The ``can_use_*`` gates are temporary migration code: each ``return False`` case shrinks as
that case is supported on Rust, and the gates go away once the Rust path reaches full parity.
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

# Internal keywords the four master-resource feeds -- list/query databases and
# list/query containers -- recognize. Anything else in ``kwargs`` means the caller
# asked for something these pages do not carry. All four feeds reject such calls.
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
    """Return True when one query page can safely route through the Rust backend.

    This compatibility gate is not used by the public retained Rust query pager.
    Backend selection for these legacy/internal calls is handled
    separately by ``run_page_operation``. It says no whenever anything does not
    fit: no query, the query-plan step, a non-document query, or the internal
    read_items query leg (a confirmed driver panic -- see the
    ``Constants.ReadItemsQueryLeg`` check below). It also says no when the
    caller used a feed_range, a prefix partition key, a custom read timeout, an
    availability strategy, full-text score scope, or query advice -- none of which
    ``PreparedPageRequest`` has a field for, so the Rust path cannot represent them yet.

    Unlike those, the query *text* is deliberately not inspected here. This gate
    used to regex-scan the SQL for clauses (``ORDER BY`` / ``GROUP BY`` / ...) the
    Rust driver could not run across partitions and route those queries around it;
    that made Python's regex the thing deciding what the driver could do, which is
    fragile (a clause could appear in a string literal, or an unsupported shape the
    patterns never anticipated could slip through) and duplicates a decision the
    driver is the actual authority on. The query shape is instead always handed to
    the driver once the structural checks below pass. If its query plan requires
    an unsupported merge operation, the binding returns a typed capability error
    and this module falls back before exposing an error to the caller.
    """
    if query_payload is None or is_query_plan:
        return False
    if resource_type != http_constants.ResourceType.Document:
        return False
    # read_items builds an internal per-partition "id IN (...)" query for each
    # chunk of its batch and marks those queries with this flag. The rust query
    # path cannot serve that shape yet (it panics resolving the partition
    # topology for it), so keep read_items' query legs on legacy while its
    # point-read legs still use rust. Normal query_items calls never set this.
    # This is a confirmed-crash gate (not a capability guess), so it stays.
    if options.get(Constants.ReadItemsQueryLeg):
        return False
    if "feed_range" in kwargs:
        return False
    if "prefix_partition_key_object" in kwargs or "prefix_partition_key_value" in kwargs:
        return False
    # The rust query-page fast path currently does not honor these request-level
    # controls the same way as the legacy path, so keep those requests on legacy.
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
        # Honor explicit "cross partition disabled" requests by keeping them on
        # the legacy path, which raises the same BAD_REQUEST the service returns
        # today for unsupported cross-partition execution. This is a plain
        # request-shape flag, not a parse of the query text.
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
    """Return True when one read_all_items page can safely route through Rust.

    Same idea as the query_items gate, for a whole-container read: it says no when
    the caller is reading a change feed, reading one specific partition range, or
    used a custom read timeout, an availability strategy, query metrics, or a
    feed_range. Otherwise the whole-container read can be served by Rust.
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
    """Return True when one page of ``client.list_databases()`` can run on Rust.

    Same idea as the two container gates above, for the account's list of
    databases. It says no when the caller asked for something the Rust page does
    not serve yet: a query-plan request, a feed of something other than
    databases, a change feed, a per-call read timeout or unsupported overall timeout, an
    availability strategy, an internal keyword this path does not recognize, or
    an override of a header the driver writes itself.

    Without this gate unsupported internal call shapes could reach Rust.
    Rejection does not always imply a lost legacy feature: availability
    strategies were accepted but not applied to legacy database metadata requests.
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
    """Return whether Rust supports this container feed page."""
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
    """Return whether Rust supports this ``list_containers`` page."""
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
    """Return whether Rust supports this ``query_containers`` page."""
    if query_payload is None:
        return False
    # Same reason as the database query gate: the legacy-only SqlQuery mode
    # leaves the payload a bare string and posts it as ``text/plain``, while the
    # driver always posts ``application/query+json``. Different bytes on the
    # wire, so reject that case on a Rust backend.
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
    """Return whether Rust supports this ``list_databases`` page."""
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
    """Return whether Rust supports this ``query_databases`` page."""
    if query_payload is None or is_query_plan:
        return False
    # By the time the query reaches here it has been normalized: the default
    # query mode always yields a dict, and the legacy-only SqlQuery mode leaves
    # it a bare string that legacy posts as ``text/plain``. The driver always
    # posts ``application/query+json``, so a string here means the two paths
    # would put different bytes on the wire. Reject that case on a Rust backend.
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


def _build_feed_request(
    *,
    op: str,
    container_link: str,
    resource_type: str,
    options: Mapping[str, Any],
    req_headers: Mapping[str, Any],
    query_payload: Optional[Union[str, Mapping[str, Any]]] = None,
) -> PreparedPageRequest:
    """Build a page from unsigned defaults/options, with one paging authority."""
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
    """Return the container link from a document-feed path."""
    normalized_path = base.TrimBeginningAndEndingSlashes(path)
    return normalized_path[: -len("/docs")] if normalized_path.endswith("/docs") else normalized_path


def build_query_items_prepared_query(
    *,
    path: str,
    query_payload: Union[str, dict[str, Any]],
    options: Mapping[str, Any],
    req_headers: Mapping[str, Any],
) -> PreparedPageRequest:
    """Build an item query directly from unsigned defaults and service options."""
    return _build_feed_request(
        op=OP_QUERY_ITEMS,
        container_link=_extract_container_link_from_docs_path(path),
        resource_type="docs",
        query_payload=query_payload,
        options=options,
        req_headers=req_headers,
    )


def build_read_all_items_prepared_query(
    *,
    path: str,
    options: Mapping[str, Any],
    req_headers: Mapping[str, Any],
) -> PreparedPageRequest:
    """Build the PreparedPageRequest for one read_all_items page dispatch.

    Python carries the requested scope without constructing SQL. The binding uses
    native read-feed for a logical partition and the legacy-compatible internal
    query for a whole-container read.
    """
    return _build_feed_request(
        op=OP_READ_ALL_ITEMS,
        container_link=_extract_container_link_from_docs_path(path),
        resource_type="docs",
        options=options,
        req_headers=req_headers,
    )


def build_list_databases_prepared_query(
    *,
    options: Mapping[str, Any],
    req_headers: Mapping[str, Any],
) -> PreparedPageRequest:
    """Build the Rust request for one page of ``list_databases``."""
    return _build_feed_request(
        op=OP_LIST_DATABASES,
        container_link="",
        resource_type="dbs",
        options=options,
        req_headers=req_headers,
    )


def build_query_databases_prepared_query(
    *,
    query_payload: Union[str, Mapping[str, Any]],
    options: Mapping[str, Any],
    req_headers: Mapping[str, Any],
) -> PreparedPageRequest:
    """Build the Rust request for one page of ``query_databases``."""
    return _build_feed_request(
        op=OP_QUERY_DATABASES,
        container_link="",
        resource_type="dbs",
        query_payload=query_payload,
        options=options,
        req_headers=req_headers,
    )


def _database_link_from_colls_path(path: str) -> str:
    """Return the database link from a container-feed path, or ``""``."""
    normalized_path = base.TrimBeginningAndEndingSlashes(path)
    if not normalized_path.endswith("/colls"):
        return ""
    database_link = normalized_path[: -len("/colls")]
    parts = database_link.split("/")
    if len(parts) != 2 or parts[0] != "dbs" or not parts[1]:
        return ""
    return database_link


def build_list_containers_prepared_query(
    *,
    path: str,
    options: Mapping[str, Any],
    req_headers: Mapping[str, Any],
) -> PreparedPageRequest:
    """Build the Rust request for one page of ``list_containers``."""
    return _build_feed_request(
        op=OP_LIST_CONTAINERS,
        container_link=_database_link_from_colls_path(path),
        resource_type="colls",
        options=options,
        req_headers=req_headers,
    )


def build_query_containers_prepared_query(
    *,
    path: str,
    query_payload: Union[str, Mapping[str, Any]],
    options: Mapping[str, Any],
    req_headers: Mapping[str, Any],
) -> PreparedPageRequest:
    """Build the Rust request for one page of ``query_containers``."""
    return _build_feed_request(
        op=OP_QUERY_CONTAINERS,
        container_link=_database_link_from_colls_path(path),
        resource_type="colls",
        query_payload=query_payload,
        options=options,
        req_headers=req_headers,
    )


def page_to_backend_response(page: BackendPage) -> BackendResponse:
    """Adapt a page reply for the existing response/error parser."""
    return BackendResponse(
        status_code=page.status_code,
        sub_status=page.sub_status,
        headers=page.headers,
        body=page.body,
        diagnostics=page.diagnostics,
    )


@dataclass(frozen=True)
class ParsedRustPage:
    """One parsed Rust page and its finalized response headers."""

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
    """Finalize a Rust feed page while retaining SDK diagnostics.

    Shared by item, database, and container queries and read feeds.

    Updates the session token, rewrites the index-metrics and query-advice headers
    into their readable form, fills the caller's response headers, and fires the
    response hook. The SDK-created diagnostics header is an intentional vNext
    addition on all Rust response paths. For a native read-feed, index-metrics and
    query-advice headers are simply absent, so those rewrite branches are no-ops.
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
    """Parse one backend page and apply legacy response side effects."""
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
