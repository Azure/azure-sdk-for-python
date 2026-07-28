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
"""Shared query-routing helpers used by both sync and async client connections.

This module is the single place that decides whether one page of query_items (or
whole-container read_all_items) can be fetched by the Rust backend instead of the
Python HTTP path, and that packages the request and the response so a Rust-served
page looks exactly like a legacy one. Both the sync and async client connections
import from here, so the two paths share one definition and cannot diverge.
It has three jobs: decide if a page is safe for Rust (the ``can_use_*`` gates),
build the page request (``build_query_items_prepared_query`` /
``build_read_all_items_prepared_query``), and finish the response to match
legacy (``finalize_rust_query_page_response``).
Without this file the query fast paths in the client would have nothing to call
and every query page would stay on the Python HTTP path.

The ``can_use_*`` gates are temporary migration code: each ``return False`` case shrinks as
that case is supported on Rust, and the gates go away once the Rust path reaches full parity.
"""
from __future__ import annotations

from typing import Any, AsyncIterator, Callable, Iterator, Mapping, Optional, Union, cast

from azure.core.utils import CaseInsensitiveDict

from . import _base as base
from . import _utils
from . import http_constants
from ._backend.base import (
    OP_QUERY_ITEMS,
    OP_READ_ALL_ITEMS,
    BackendResponse,
    PreparedQuery,
    QueryNotSupportedByBackendError,
    QueryPage,
)
from ._constants import _Constants as Constants
from ._helpers._pk_wire import serialize_partition_key_to_wire
from ._query_advisor import get_query_advice_info
from .partition_key import _build_partition_key_from_properties

_RUST_QUERY_FALLBACK_COUNT = 0


def rust_query_fallback_count() -> int:
    """Return Rust query attempts rejected through typed capability fallback."""
    return _RUST_QUERY_FALLBACK_COUNT


def can_use_rust_backend_for_query_page(
    *,
    backend: Any,
    query_payload: Optional[Union[str, dict[str, Any]]],
    options: Mapping[str, Any],
    kwargs: Mapping[str, Any],
    container_properties: Optional[Mapping[str, Any]],
    is_query_plan: bool,
    resource_type: str,
) -> bool:
    """Return True when one query page can safely route through the Rust backend.

    This is the gate for query_items. It says no (keep the page on the Python HTTP
    path) whenever anything does not fit: no Rust backend, no query, the query-plan
    step, a non-document query, the internal read_items query leg (a confirmed
    driver panic -- see the ``Constants.ReadItemsQueryLeg`` check below), or the
    caller used a feed_range, a prefix partition key, a custom read timeout, an
    availability strategy, full-text score scope, or query advice -- none of which
    ``PreparedQuery`` has a field for, so the Rust path cannot represent them yet.

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
    if backend is None or query_payload is None or is_query_plan:
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
    if "fullTextScoreScope" in options:
        return False
    if options.get("populateQueryAdvice"):
        return False

    has_partition_key = "partitionKey" in options
    partition_key_value = options.get("partitionKey")
    partition_key_wire = "[]"
    if has_partition_key:
        try:
            partition_key_wire = serialize_partition_key_to_wire(partition_key_value)
        except (TypeError, ValueError):
            return False

    if partition_key_wire == "[]":
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
    backend: Any,
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
    if backend is None or is_query_plan:
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
    if "populateQueryMetrics" in options:
        return False
    if "feed_range" in kwargs:
        return False
    return True


def _build_prepared_headers_for_rust_feed_dispatch(
    *,
    options: Mapping[str, Any],
    req_headers: Mapping[str, Any],
) -> dict[str, Any]:
    prepared_headers = dict(req_headers)
    excluded_locations = options.get(Constants.Kwargs.EXCLUDED_LOCATIONS)
    if excluded_locations is not None:
        prepared_headers[Constants.Kwargs.EXCLUDED_LOCATIONS] = excluded_locations
    timeout_value = options.get(Constants.Kwargs.TIMEOUT)
    if timeout_value is not None:
        prepared_headers[Constants.OVERALL_TIMEOUT_SECONDS] = timeout_value
    return prepared_headers


def _resolve_partition_key_header_for_feed_dispatch(
    *,
    options: Mapping[str, Any],
    req_headers: Mapping[str, Any],
) -> str:
    partition_key_header = req_headers.get(http_constants.HttpHeaders.PartitionKey)
    if isinstance(partition_key_header, str):
        return partition_key_header
    if "partitionKey" in options:
        return serialize_partition_key_to_wire(options.get("partitionKey"))
    return "[]"


def _extract_container_link_from_docs_path(path: str) -> str:
    normalized_path = base.TrimBeginningAndEndingSlashes(path)
    return normalized_path[: -len("/docs")] if normalized_path.endswith("/docs") else normalized_path


def build_query_items_prepared_query(
    *,
    path: str,
    query_payload: Union[str, dict[str, Any]],
    options: Mapping[str, Any],
    req_headers: Mapping[str, Any],
) -> PreparedQuery:
    """Build the PreparedQuery for one query-items page dispatch.

    Assembles the request object the binding reads: it copies the request headers,
    carries the excluded-locations and timeout values, works out the container link
    from the request path, turns the query JSON into bytes, and sets the
    partition_key_header to ["pk"] for one partition or [] for the whole container.
    That header string is exactly what the Rust side decodes to pick the query scope,
    so both ends agree on it.
    """
    prepared_headers = _build_prepared_headers_for_rust_feed_dispatch(
        options=options,
        req_headers=req_headers,
    )
    partition_key_header = _resolve_partition_key_header_for_feed_dispatch(
        options=options,
        req_headers=req_headers,
    )
    query_text = query_payload if isinstance(query_payload, str) else query_payload.get("query")
    parameters = () if isinstance(query_payload, str) else tuple(query_payload.get("parameters") or ())
    return PreparedQuery(
        op=OP_QUERY_ITEMS,
        container_link=_extract_container_link_from_docs_path(path),
        query=query_text,
        parameters=parameters,
        partition_key_header=partition_key_header,
        max_item_count=options.get("maxItemCount"),
        continuation=options.get("continuation"),
        headers=prepared_headers,
    )


def build_read_all_items_prepared_query(
    *,
    path: str,
    options: Mapping[str, Any],
    req_headers: Mapping[str, Any],
) -> PreparedQuery:
    """Build the PreparedQuery for one read_all_items page dispatch.

    Python carries the requested scope without constructing SQL. The binding uses
    native read-feed for a logical partition and the legacy-compatible internal
    query for a whole-container read.
    """
    return PreparedQuery(
        op=OP_READ_ALL_ITEMS,
        container_link=_extract_container_link_from_docs_path(path),
        partition_key_header=_resolve_partition_key_header_for_feed_dispatch(
            options=options,
            req_headers=req_headers,
        ),
        max_item_count=options.get("maxItemCount"),
        continuation=options.get("continuation"),
        headers=_build_prepared_headers_for_rust_feed_dispatch(
            options=options,
            req_headers=req_headers,
        ),
    )


def query_page_to_backend_response(page: QueryPage) -> BackendResponse:
    """Adapt a page reply for the existing response/error parser."""
    return BackendResponse(
        status_code=page.status_code,
        sub_status=page.sub_status,
        headers=page.headers,
        body=page.body,
        diagnostics=page.diagnostics,
    )


def run_query_page_on_rust_backend(backend: Any, prepared: PreparedQuery) -> Optional[QueryPage]:
    """Fetch one page through the sync page boundary."""
    try:
        pages: Iterator[QueryPage] = backend.execute_pages(prepared)
        return next(pages, None)
    except QueryNotSupportedByBackendError:
        global _RUST_QUERY_FALLBACK_COUNT  # pylint: disable=global-statement
        _RUST_QUERY_FALLBACK_COUNT += 1
        return None


async def run_query_page_on_rust_backend_async(
    backend: Any, prepared: PreparedQuery
) -> Optional[QueryPage]:
    """Fetch one page through the async page boundary."""
    try:
        pages: AsyncIterator[QueryPage] = backend.execute_pages(prepared)
        return await pages.__anext__()
    except StopAsyncIteration:
        return None
    except QueryNotSupportedByBackendError:
        global _RUST_QUERY_FALLBACK_COUNT  # pylint: disable=global-statement
        _RUST_QUERY_FALLBACK_COUNT += 1
        return None


def finalize_rust_query_page_response(
    *,
    client_connection: Any,
    req_headers: Mapping[str, Any],
    parsed: dict[str, Any],
    internal_headers_capture: Optional[dict[str, Any]],
    response_headers: Optional[CaseInsensitiveDict],
    response_hook: Optional[Callable[[Mapping[str, Any], dict[str, Any]], None]],
) -> CaseInsensitiveDict:
    """Apply legacy-parity post-processing after a Rust feed-page parse.

    Shared by both query_items and read_all_items: read_all_items is served through
    the same query-page machinery (its rows come back in a query-shaped page), so the
    "query" in this name refers to that page shape, not to a SQL query specifically.

    Does the same finishing work the legacy path already does, so a Rust-served page
    is indistinguishable from a legacy one: it updates the session token, rewrites
    the index-metrics and query-advice headers into their readable form, drops the
    internal diagnostics header, fills the caller's response headers, and fires the
    response hook. For read_all_items (a native read-feed) the index-metrics and
    query-advice headers are simply absent, so those rewrite branches are no-ops.
    """
    last_response_headers = cast(CaseInsensitiveDict, client_connection.last_response_headers)
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
    # Keep response headers/hook parity with legacy query behavior.
    last_response_headers.pop("x-ms-cosmos-sdk-diagnostics", None)
    if response_headers is not None:
        response_headers.clear()
        response_headers.update(last_response_headers)
    if response_hook:
        response_hook(last_response_headers, parsed)
    return last_response_headers
