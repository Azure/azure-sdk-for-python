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
"""Shared page-routing helpers used by both sync and async client connections.

This module is the single place that decides whether one page of ``query_items``,
whole-container ``read_all_items``, or account-level ``list_databases`` can use
the Rust backend instead of the Python HTTP path. It packages requests and
responses so a Rust-served page looks exactly like a legacy one. Both the sync
and async client connections import from here, so the two paths share one
definition and cannot diverge.

It has three jobs: decide whether a page is safe for Rust (the ``can_use_*``
gates), build the page request (``build_query_items_prepared_query``,
``build_read_all_items_prepared_query``, or
``build_list_databases_prepared_query``), and finish the response to match
legacy (``finalize_rust_page_response``).

The ``can_use_*`` gates are temporary migration code: each ``return False`` case shrinks as
that case is supported on Rust, and the gates go away once the Rust path reaches full parity.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Optional, Union, cast

from azure.core.utils import CaseInsensitiveDict

from . import _base as base
from . import _utils
from . import http_constants
from ._backend.base import (
    OP_LIST_DATABASES,
    OP_LIST_CONTAINERS,
    OP_QUERY_CONTAINERS,
    OP_QUERY_DATABASES,
    OP_QUERY_ITEMS,
    OP_READ_ALL_ITEMS,
    BackendResponse,
    PreparedQuery,
    QueryPage,
)
from ._constants import _Constants as Constants
from ._cosmos_responses import CosmosDict
from ._helpers._pk_wire import serialize_partition_key_to_wire
from ._helpers._request_prep import overrides_driver_owned_header
from ._helpers._response_parse import parse_backend_response
from ._query_advisor import get_query_advice_info
from .partition_key import _build_partition_key_from_properties

# Internal keywords the four master-resource feeds -- list/query databases and
# list/query containers -- recognize. Anything else in ``kwargs`` means the caller
# asked for something these pages do not carry, so the request stays on the legacy
# path.
_MASTER_FEED_ALLOWED_INTERNAL_KWARGS = frozenset({
    Constants.OperationStartTime,
})
_RUST_DRIVER_OWNED_REQUEST_HEADERS = frozenset({
    "accept",
    "authorization",
    "cache-control",
    # A query page carries ``Content-Type: application/query+json``. The driver
    # writes that itself for every query operation, so ours is redundant; the
    # Rust wire layer drops it and, under COSMOS_WIRE_STRICT, rejects it as an
    # untranslated option key. Dropping it here keeps the wire bytes identical
    # and lets strict mode run.
    "content-type",
    "user-agent",
    "x-ms-date",
    "x-ms-version",
})
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

    This is the request-shape gate for query_items. Backend selection is handled
    separately by ``run_page_operation``. It says no whenever anything does not
    fit: no query, the query-plan step, a non-document query, or the internal
    read_items query leg (a confirmed driver panic -- see the
    ``Constants.ReadItemsQueryLeg`` check below). It also says no when the
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
) -> bool:
    """Return True when one page of ``client.list_databases()`` can run on Rust.

    Same idea as the two container gates above, for the account's list of
    databases. It says no when the caller asked for something the Rust page does
    not serve yet: a query-plan request, a feed of something other than
    databases, a change feed, a per-call read timeout or overall timeout, an
    availability strategy, an internal keyword this path does not recognize, or
    an override of a header the driver writes itself.

    Without this gate every ``list_databases`` call would go to Rust, including
    those shapes, and a customer who passed one would silently get behavior that
    differs from the legacy path.
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
    if (
        options.get(Constants.Kwargs.TIMEOUT) is not None
        or kwargs.get(Constants.Kwargs.TIMEOUT) is not None
    ):
        return False
    if Constants.Kwargs.AVAILABILITY_STRATEGY in options:
        return False
    if set(kwargs).difference(_MASTER_FEED_ALLOWED_INTERNAL_KWARGS):
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
    return _container_feed_page_is_rust_eligible(
        options=options,
        kwargs=kwargs,
        is_query_plan=is_query_plan,
        resource_type=resource_type,
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
    # wire, so keep that case on legacy.
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
    # would put different bytes on the wire. Keep that case on legacy.
    if not isinstance(query_payload, dict):
        return False
    return _master_feed_page_is_rust_eligible(
        options=options,
        kwargs=kwargs,
        is_query_plan=is_query_plan,
        resource_type=resource_type,
        expected_resource_type=http_constants.ResourceType.Database,
    )


def _build_prepared_headers_for_rust_feed_dispatch(
    *,
    options: Mapping[str, Any],
    req_headers: Mapping[str, Any],
) -> dict[str, Any]:
    """Choose which of the already-built HTTP headers to hand to the Rust page.

    Two kinds are dropped. The driver writes its own authorization, date, and
    version headers, so ours would be ignored or conflict. Page size and
    continuation are already carried as typed fields on ``PreparedQuery``, so
    sending them as headers too would state the same thing twice. Excluded
    locations and the overall timeout are added instead of dropped, because the
    driver takes those as request options rather than as headers.

    Shared by all three paged operations. Without it each would filter its own
    headers and the three could drift apart.
    """
    typed_paging_headers = set()
    if options.get("maxItemCount") is not None:
        typed_paging_headers.add(http_constants.HttpHeaders.PageSize)
    if options.get("continuation") is not None:
        typed_paging_headers.add(http_constants.HttpHeaders.Continuation)
    excluded_headers = _RUST_DRIVER_OWNED_REQUEST_HEADERS.union(typed_paging_headers)
    prepared_headers = {
        name: value
        for name, value in req_headers.items()
        if not (
            isinstance(name, str)
            and name.lower() in excluded_headers
        )
    }
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
    """Return the serialized partition key used to scope the page."""
    partition_key_header = req_headers.get(http_constants.HttpHeaders.PartitionKey)
    if isinstance(partition_key_header, str):
        return partition_key_header
    if "partitionKey" in options:
        return serialize_partition_key_to_wire(options.get("partitionKey"))
    return "[]"


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


def _build_prepared_headers_for_database_feed_dispatch(
    *,
    options: Mapping[str, Any],
    req_headers: Mapping[str, Any],
) -> dict[str, Any]:
    """Return headers for a database or container feed request."""
    prepared_headers = _build_prepared_headers_for_rust_feed_dispatch(
        options=options,
        req_headers=req_headers,
    )
    initial_headers = options.get("initialHeaders")
    if isinstance(initial_headers, Mapping):
        customer_headers_for_binding = {
            name: value
            for name, value in initial_headers.items()
            if not (
                isinstance(name, str)
                and (
                    name.lower().startswith("x-ms-")
                    or name.lower() in {"if-match", "if-none-match", "prefer"}
                )
            )
        }
        if customer_headers_for_binding:
            for name in customer_headers_for_binding:
                prepared_headers.pop(name, None)
            prepared_headers["initialHeaders"] = customer_headers_for_binding
    return prepared_headers


def build_list_databases_prepared_query(
    *,
    options: Mapping[str, Any],
    req_headers: Mapping[str, Any],
) -> PreparedQuery:
    """Build the Rust request for one page of ``list_databases``."""
    return PreparedQuery(
        op=OP_LIST_DATABASES,
        container_link="",
        max_item_count=options.get("maxItemCount"),
        continuation=options.get("continuation"),
        headers=_build_prepared_headers_for_database_feed_dispatch(
            options=options,
            req_headers=req_headers,
        ),
    )


def build_query_databases_prepared_query(
    *,
    query_payload: Mapping[str, Any],
    options: Mapping[str, Any],
    req_headers: Mapping[str, Any],
) -> PreparedQuery:
    """Build the Rust request for one page of ``query_databases``."""
    return PreparedQuery(
        op=OP_QUERY_DATABASES,
        container_link="",
        query=query_payload.get("query"),
        parameters=tuple(query_payload.get("parameters") or ()),
        max_item_count=options.get("maxItemCount"),
        continuation=options.get("continuation"),
        headers=_build_prepared_headers_for_database_feed_dispatch(
            options=options,
            req_headers=req_headers,
        ),
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
) -> PreparedQuery:
    """Build the Rust request for one page of ``list_containers``."""
    return PreparedQuery(
        op=OP_LIST_CONTAINERS,
        container_link=_database_link_from_colls_path(path),
        max_item_count=options.get("maxItemCount"),
        continuation=options.get("continuation"),
        headers=_build_prepared_headers_for_database_feed_dispatch(
            options=options,
            req_headers=req_headers,
        ),
    )


def build_query_containers_prepared_query(
    *,
    path: str,
    query_payload: Mapping[str, Any],
    options: Mapping[str, Any],
    req_headers: Mapping[str, Any],
) -> PreparedQuery:
    """Build the Rust request for one page of ``query_containers``."""
    return PreparedQuery(
        op=OP_QUERY_CONTAINERS,
        container_link=_database_link_from_colls_path(path),
        query=query_payload.get("query"),
        parameters=tuple(query_payload.get("parameters") or ()),
        max_item_count=options.get("maxItemCount"),
        continuation=options.get("continuation"),
        headers=_build_prepared_headers_for_database_feed_dispatch(
            options=options,
            req_headers=req_headers,
        ),
    )


def page_to_backend_response(page: QueryPage) -> BackendResponse:
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
    """Apply legacy-parity post-processing after a Rust feed-page parse.

    Shared by query_items, read_all_items, and list_databases because all three
    operations use the same one-page backend boundary.

    Does the same finishing work the legacy path already does, so a Rust-served page
    is indistinguishable from a legacy one: it updates the session token, rewrites
    the index-metrics and query-advice headers into their readable form, drops the
    internal diagnostics header, fills the caller's response headers, and fires the
    response hook. For read_all_items (a native read-feed) the index-metrics and
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
    # Keep response headers/hook parity with legacy query behavior.
    last_response_headers.pop("x-ms-cosmos-sdk-diagnostics", None)
    if response_headers is not None:
        response_headers.clear()
        response_headers.update(last_response_headers)
    if response_hook:
        response_hook(last_response_headers, parsed)
    return last_response_headers


def parse_and_finalize_rust_page(  # pylint: disable=too-many-arguments
    *,
    page: QueryPage,
    client_connection: Any,
    req_headers: Mapping[str, Any],
    internal_headers_capture: Optional[dict[str, Any]],
    response_headers: Optional[CaseInsensitiveDict],
    response_hook: Optional[Callable[[Mapping[str, Any], dict[str, Any]], None]],
) -> ParsedRustPage:
    """Parse one backend page and apply legacy response side effects."""
    parsed_response = cast(
        CosmosDict,
        parse_backend_response(
            page_to_backend_response(page),
            client_connection=None,
            response_hook=None,
        ),
    )
    parsed = cast(dict[str, Any], parsed_response)
    last_response_headers = parsed_response.get_response_headers()
    client_connection.last_response_headers = last_response_headers
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
