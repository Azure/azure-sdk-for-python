# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Conversions between the Rust binding's plain values and our typed objects.

The binding speaks in tuples and plain dicts. These helpers convert in both
directions -- arguments on the way in, responses on the way out -- providing
shared conversions for the synchronous and asynchronous backends.
"""
from __future__ import annotations

import json
from typing import Any, Mapping, Optional
from dataclasses import replace

from azure.core.utils import CaseInsensitiveDict

from .contracts import (
    BackendResponse, ContainerMetadata, PreparedClientConfig,
    PreparedQuery, PreparedRequest, QueryPage, QueryScope,
)
from .errors import BindingProtocolError
from .operations import (
    OP_LIST_CONTAINERS, OP_LIST_DATABASES, OP_READ_ALL_ITEMS,
    OP_QUERY_ITEMS_CHANGE_FEED, OP_QUERY_ITEMS,
)
from ..exceptions import CosmosHttpResponseError
from .._operation_deadline import remaining_timeout


_PARAMETERLESS_FEED_OPS = frozenset({OP_READ_ALL_ITEMS, OP_LIST_DATABASES, OP_LIST_CONTAINERS})


def build_binding_request_from_page(prepared: PreparedQuery) -> PreparedRequest:
    """Adapt sync/async page requests to the binding's request object.

    Reuse the pager's serialized service query body when available. Retained
    query scope travels separately. Only headers and typed page settings change
    between fetches; change-feed and parameterless-feed bodies keep their shape.
    """
    if prepared.op == OP_QUERY_ITEMS_CHANGE_FEED:
        body = json.dumps(prepared.change_feed, separators=(",", ":")).encode("utf-8")
    elif prepared.op in _PARAMETERLESS_FEED_OPS:
        body = b""
    elif prepared.query_body is not None:
        body = prepared.query_body
    else:
        if prepared.query is None:
            raise ValueError("{} requires PreparedQuery.query.".format(prepared.op))
        payload: dict[str, Any] = {"query": prepared.query}
        if prepared.parameters:
            payload["parameters"] = list(prepared.parameters)
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    headers = dict(prepared.headers)
    query_settings = prepared.settings.query
    if prepared.continuation is not None:
        headers.pop("x-ms-continuation", None)
        query_settings = replace(query_settings, continuation=prepared.continuation)
    if prepared.max_item_count is not None:
        headers.pop("x-ms-max-item-count", None)
        query_settings = replace(query_settings, max_item_count=prepared.max_item_count)
    query_scope = None
    if prepared.op == OP_QUERY_ITEMS and prepared.cursor is not None:
        query_scope = prepared.query_scope or QueryScope()
    return PreparedRequest(
        op=prepared.op,
        container_link=prepared.container_link,
        body_bytes=body,
        partition_key=prepared.partition_key,
        headers=headers,
        settings=replace(prepared.settings, query=query_settings),
        query_scope=query_scope,
    )


def page_dispatch_arguments(
    driver_handle: str,
    request: PreparedRequest,
    prepared: PreparedQuery,
    deadline: Optional[float],
) -> tuple[tuple[Any, ...], dict[str, Optional[float]]]:
    """Compute the remaining budget immediately before sync or async dispatch."""
    args: tuple[Any, ...] = (driver_handle, request)
    if prepared.cursor is not None:
        args += (prepared.cursor,)
    kwargs = (
        {"timeout_seconds": remaining_timeout(deadline)}
        if prepared.cursor is not None or deadline is not None
        else {}
    )
    return args, kwargs


def build_query_page(prepared: PreparedQuery, response: BackendResponse) -> QueryPage:
    """Attach continuation and retained-query cursor state to one response."""
    cursor = prepared.cursor if prepared.op == OP_QUERY_ITEMS else None
    return QueryPage(
        status_code=response.status_code,
        continuation=response.headers.get("x-ms-continuation") if response.headers else None,
        sub_status=response.sub_status,
        headers=response.headers,
        body=response.body,
        diagnostics=response.diagnostics,
        has_more=cursor.has_more if cursor is not None else None,
        continuation_supported=cursor.continuation_supported if cursor is not None else True,
    )


def build_container_metadata(raw: Any) -> ContainerMetadata:
    """Validate the native metadata contract once, without JSON or response state."""
    if not isinstance(raw, tuple) or len(raw) != 4:
        raise BindingProtocolError("The binding returned invalid container metadata")
    rid, paths, kind, system_key = raw
    if not isinstance(rid, str) or not rid:
        raise BindingProtocolError("Container metadata requires a non-empty rid")
    if not isinstance(paths, tuple) or any(not isinstance(path, str) or not path for path in paths):
        raise BindingProtocolError("Container metadata requires a tuple of non-empty paths")
    if kind not in (None, "Hash", "MultiHash", "Range") or bool(paths) != (kind is not None):
        raise BindingProtocolError("Container metadata contains an invalid partition-key definition")
    if system_key is not None and not isinstance(system_key, bool):
        raise BindingProtocolError("Container metadata system_key must be bool or None")
    return ContainerMetadata(rid, paths, kind, system_key)


def metadata_exception_from_binding(error: BaseException) -> CosmosHttpResponseError:
    """Convert an actual metadata failure without publishing response headers."""
    from .._helpers._exceptions import extract_message_from_body, map_backend_response_to_exception
    from .._helpers._response_parse import apply_response_diagnostics, apply_request_charge_format

    if len(error.args) != 1 or not isinstance(error.args[0], tuple) or len(error.args[0]) != 5:
        raise BindingProtocolError("The binding returned an invalid metadata error")
    response = build_backend_response(*error.args[0])
    if response.status_code < 400:
        raise BindingProtocolError("The binding returned a non-error metadata failure")
    headers = CaseInsensitiveDict(response.headers or {})
    apply_request_charge_format(headers)
    apply_response_diagnostics(headers, response.diagnostics)
    response = replace(response, headers=headers)
    return map_backend_response_to_exception(response, message=extract_message_from_body(response.body))


# ---------------------------------------------------------------------------
# Response-header normalisation (binding dict -> CaseInsensitiveDict)
# ---------------------------------------------------------------------------
#
# Convert the binding's header mapping to case-insensitive lookup. Its values
# come from native response conversion and may include synthesized headers;
# this conversion does not establish parity with raw HTTP or legacy headers.


def normalize_response_headers(
    headers: Optional[Mapping[str, Any]],
) -> Optional[CaseInsensitiveDict]:
    """Wrap the binding's response-header dict in a ``CaseInsensitiveDict``.

    Copy entries into a new mapping. Names that differ only in case can collapse
    to one entry, with the later assignment winning. ``None`` or empty input
    returns ``None``.
    """
    if not headers:
        return None
    result = CaseInsensitiveDict()
    for raw_key, value in headers.items():
        result[raw_key] = value
    return result


def acquire_driver_handle_args(
    endpoint: str,
    master_key: Optional[str],
    client_config: Optional[PreparedClientConfig],
    token_credential: Optional[Any],
) -> tuple[Any, ...]:
    """Build the positional args for the Rust ``acquire_driver_handle`` call.

    A token credential rides as the 4th argument; master-key auth uses the
    3-argument form. ``credentials.resolve_credential`` is contracted to set
    exactly one of the two. Shared by both backends so the call shape lives in
    one place.

    This helper rejects both credentials being set. If neither is supplied, it
    still builds the three-argument form; the native acquisition function rejects
    the missing credential.
    """
    if master_key is not None and token_credential is not None:
        raise ValueError(
            "acquire_driver_handle_args received both master_key and token_credential; "
            "exactly one must be set (credentials.resolve_credential is "
            "responsible for this)."
        )
    if token_credential is not None:
        return (endpoint, None, client_config, token_credential)
    return (endpoint, master_key, client_config)


def build_backend_response(
    status_code: Any,
    sub_status: Any,
    headers: Optional[Mapping[str, Any]],
    body: Any,
    diagnostics: Any = None,
) -> BackendResponse:
    """Wrap the binding's response tuple as a ``BackendResponse``.

    The native response serializer returns five elements:
    ``(status, sub_status, headers, body, diagnostics_or_none)``. The default
    diagnostics argument also accepts four-element test doubles; it does not
    establish compatibility with an older binding's request protocol.
    """
    return BackendResponse(
        status_code=int(status_code),
        sub_status=int(sub_status),
        headers=normalize_response_headers(headers),
        body=bytes(body) if body else b"",
        diagnostics=diagnostics,
    )
