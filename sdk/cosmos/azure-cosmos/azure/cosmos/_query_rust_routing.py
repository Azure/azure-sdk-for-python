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
import from here, so the two paths share one source of truth and cannot drift.
It has three jobs: decide if a page is safe for Rust (the ``can_use_*`` gates),
build the request the binding reads (``build_query_items_prepared_request`` /
``build_read_all_items_prepared_request``), and finish the response to match
legacy (``finalize_rust_query_page_response``).
Without this file the query fast paths in the client would have nothing to call
and every query page would stay on the Python HTTP path.

The ``can_use_*`` gates are migration scaffolding: each ``return False`` case shrinks as
that case lands on Rust, and the gates go away once the Rust path reaches full parity.
"""
from __future__ import annotations

import re
from typing import Any, Callable, Mapping, Optional, Union, cast

from azure.core.utils import CaseInsensitiveDict

from . import _base as base
from . import _utils
from . import http_constants
from ._backend.base import OP_QUERY_ITEMS, OP_READ_ALL_ITEMS, PreparedRequest
from ._constants import _Constants as Constants
from ._helpers._body_wire import serialize_body_to_bytes
from ._helpers._pk_wire import serialize_partition_key_to_wire
from ._query_advisor import get_query_advice_info
from .partition_key import _build_partition_key_from_properties


# Operations the Rust driver cannot run across partitions today: they need work
# that combines results from every partition (sorting, grouping, de-duplicating,
# counting/summing, cutting to N rows, full-text/hybrid ranking). A cross-partition
# query that uses any of these must stay on the legacy path, which does that
# combining itself. Single-partition queries are unaffected.
_UNSUPPORTED_CROSS_PARTITION_QUERY_PATTERNS = (
    re.compile(r"\bORDER\s+BY\b", re.IGNORECASE),
    re.compile(r"\bGROUP\s+BY\b", re.IGNORECASE),
    re.compile(r"\bDISTINCT\b", re.IGNORECASE),
    re.compile(r"\bTOP\s+\d+\b", re.IGNORECASE),
    re.compile(r"\bOFFSET\b", re.IGNORECASE),
    re.compile(r"\bLIMIT\b", re.IGNORECASE),
    re.compile(r"\b(COUNT|SUM|AVG|MIN|MAX|COUNTIF|DCOUNT)\s*\(", re.IGNORECASE),
    re.compile(r"\b(FULLTEXTCONTAINS|FULLTEXTSCORE|RRF|WEIGHTEDRANKFUSION)\s*\(", re.IGNORECASE),
)


def _extract_query_text(query_payload: Union[str, dict[str, Any]]) -> Optional[str]:
    """Pull the SQL text out of the query payload (a plain string or a {"query": ...} dict).

    Returns None when there is no query string; the shape check needs the raw text to scan it.
    """
    if isinstance(query_payload, str):
        return query_payload
    if isinstance(query_payload, dict):
        query_text = query_payload.get("query")
        if isinstance(query_text, str):
            return query_text
    return None


def _is_rust_supported_cross_partition_query_shape(query_payload: Union[str, dict[str, Any]]) -> bool:
    """True only when the query text uses none of the operations listed in
    ``_UNSUPPORTED_CROSS_PARTITION_QUERY_PATTERNS``.

    Without this, a cross-partition query that needs the server to combine results across
    partitions could route to Rust and return wrong or partial results.
    """
    query_text = _extract_query_text(query_payload)
    if not isinstance(query_text, str):
        return False
    for pattern in _UNSUPPORTED_CROSS_PARTITION_QUERY_PATTERNS:
        if pattern.search(query_text):
            return False
    return True


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
    step, a non-document query, or the caller used a feed_range, a prefix partition
    key, a custom read timeout, an availability strategy, full-text score scope, or
    query advice. If those pass, it looks at the partition key: a real partition_key
    means a single-partition query (allowed), while an empty key means a
    cross-partition query, which is allowed only when the caller did not turn
    cross-partition off and the query text uses none of the operations the Rust
    driver cannot run across partitions.
    """
    if backend is None or query_payload is None or is_query_plan:
        return False
    if resource_type != http_constants.ResourceType.Document:
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
        # today for unsupported cross-partition execution.
        if options.get("enableCrossPartitionQuery") is False:
            return False
        return _is_rust_supported_cross_partition_query_shape(query_payload)

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


def build_query_items_prepared_request(
    *,
    path: str,
    query_payload: Union[str, dict[str, Any]],
    options: Mapping[str, Any],
    req_headers: Mapping[str, Any],
) -> PreparedRequest:
    """Build the PreparedRequest for one query-items page dispatch.

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
    return PreparedRequest(
        op=OP_QUERY_ITEMS,
        container_link=_extract_container_link_from_docs_path(path),
        body_bytes=serialize_body_to_bytes(query_payload),
        partition_key_header=partition_key_header,
        headers=prepared_headers,
        item_id=None,
    )


def build_read_all_items_prepared_request(
    *,
    path: str,
    options: Mapping[str, Any],
    req_headers: Mapping[str, Any],
) -> PreparedRequest:
    """Build the PreparedRequest for one read_all_items page dispatch.

    Builds the native read-feed request the Rust side reads for partition-targeted
    read_all_items. Note the binding currently only reaches this for a partition-
    targeted scope (a PartitionKey header present); whole-container read_all_items is
    served through the query-page path instead, because the driver does not yet
    support cross-partition read-feed fan-out. Preserves parity-sensitive request
    metadata (partition key targeting, timeout, excluded locations, forwarded headers).
    """
    return PreparedRequest(
        op=OP_READ_ALL_ITEMS,
        container_link=_extract_container_link_from_docs_path(path),
        body_bytes=b"",
        partition_key_header=_resolve_partition_key_header_for_feed_dispatch(
            options=options,
            req_headers=req_headers,
        ),
        headers=_build_prepared_headers_for_rust_feed_dispatch(
            options=options,
            req_headers=req_headers,
        ),
        item_id=None,
    )


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
