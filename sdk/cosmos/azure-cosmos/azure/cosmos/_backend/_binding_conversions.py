# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Convert Python wrapper requests and Python/Rust binding responses.

The binding adapts Python wrapper calls to the Rust driver. It receives
PreparedRequest objects and returns tuples containing status, sub-status,
headers, body bytes, and diagnostics. Both synchronous and asynchronous
Python wrappers use these conversions.
"""
from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Mapping, Optional
from dataclasses import replace

from azure.core.utils import CaseInsensitiveDict

from .contracts import (
    BackendResponse, ContainerMetadata, PreparedClientConfig,
    PreparedPageRequest, PreparedRequest, BackendPage, QueryScope,
)
from .errors import BindingProtocolError
from ._immutable import json_mapping
from .operations import (
    OP_LIST_CONTAINERS, OP_LIST_DATABASES, OP_READ_ALL_ITEMS,
    OP_QUERY_ITEMS_CHANGE_FEED, OP_QUERY_ITEMS, OP_READ_ITEMS,
)
from ..exceptions import CosmosHttpResponseError
from .._operation_deadline import remaining_timeout

if TYPE_CHECKING:
    from .._rust import _DriverHandle


_PARAMETERLESS_FEED_OPS = frozenset({OP_READ_ALL_ITEMS, OP_READ_ITEMS, OP_LIST_DATABASES, OP_LIST_CONTAINERS})


def build_binding_request_from_page(prepared: PreparedPageRequest) -> PreparedRequest:
    """Convert a prepared page request into the prepared request for the binding.

    PreparedPageRequest -> body bytes and request headers -> PreparedRequest.
    The feed cursor, when present, is passed separately to the binding function.

    Reuse query_body when the Python wrapper has converted the SQL and parameters
    to JSON bytes. Listing requests need no body; change-feed requests use their
    own settings instead of SQL. Copy headers and put supplied page-size and
    continuation values in typed query settings, removing their corresponding
    headers from the copy except for the change-feed continuation header.
    The original prepared page request is not changed.

    :param prepared: Page inputs, including query settings and any retained cursor.
    :type prepared: ~azure.cosmos._backend.contracts.PreparedPageRequest
    :return: Binding request with serialized body and page settings.
    :rtype: ~azure.cosmos._backend.contracts.PreparedRequest
    """
    if prepared.op == OP_QUERY_ITEMS_CHANGE_FEED:
        body = json.dumps(
            prepared.change_feed, separators=(",", ":"), default=json_mapping
        ).encode("utf-8")
    elif prepared.op in _PARAMETERLESS_FEED_OPS:
        body = b""
    elif prepared.query_body is not None:
        body = prepared.query_body
    else:
        if prepared.query is None:
            raise ValueError("{} requires PreparedPageRequest.query.".format(prepared.op))
        payload: dict[str, Any] = {"query": prepared.query}
        if prepared.parameters:
            payload["parameters"] = list(prepared.parameters)
        body = json.dumps(
            payload, separators=(",", ":"), default=json_mapping
        ).encode("utf-8")
    headers = dict(prepared.headers)
    query_settings = prepared.settings.query
    if prepared.continuation is not None:
        if prepared.op != OP_QUERY_ITEMS_CHANGE_FEED:
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
        read_many_items=prepared.read_many_items,
    )


def page_binding_call_arguments(
    driver_handle: _DriverHandle,
    request: PreparedRequest,
    prepared: PreparedPageRequest,
    deadline: Optional[float],
) -> tuple[tuple[Any, ...], dict[str, Optional[float]]]:
    """Build page binding call arguments without invoking the function.

    Stateless paging passes (driver_handle, request). Retained paging also
    passes prepared.cursor. A supplied deadline contributes only its remaining
    seconds, not a fresh operation budget.

    :param driver_handle: Owning handle for the driver executing the page fetch.
    :type driver_handle: ~azure.cosmos._rust._DriverHandle
    :param request: Converted binding request.
    :type request: ~azure.cosmos._backend.contracts.PreparedRequest
    :param prepared: Original page request carrying any retained cursor.
    :type prepared: ~azure.cosmos._backend.contracts.PreparedPageRequest
    :param deadline: Absolute monotonic deadline, or None for no deadline.
    :type deadline: float or None
    :return: Positional arguments and timeout keyword arguments for the binding.
    :rtype: tuple[tuple[typing.Any, ...], dict[str, typing.Optional[float]]]
    """
    args: tuple[Any, ...] = (driver_handle, request)
    if prepared.cursor is not None:
        args += (prepared.cursor,)
    kwargs = (
        {"timeout_seconds": remaining_timeout(deadline)}
        if prepared.cursor is not None or deadline is not None
        else {}
    )
    return args, kwargs


def build_backend_page(prepared: PreparedPageRequest, response: BackendResponse) -> BackendPage:
    """Convert a backend response into a backend page.

    Copy the continuation token from response headers. For retained item
    queries, read-many, and read-all operations, also copy has_more and
    continuation_supported from the feed cursor.
    Other page paths leave has_more as None and apply their own completion rules.

    :param prepared: Page inputs and optional cursor supplying progress.
    :type prepared: ~azure.cosmos._backend.contracts.PreparedPageRequest
    :param response: Converted binding response.
    :type response: ~azure.cosmos._backend.contracts.BackendResponse
    :return: Response body and page continuation metadata.
    :rtype: ~azure.cosmos._backend.contracts.BackendPage
    """
    cursor = prepared.cursor if prepared.op in (OP_QUERY_ITEMS, OP_READ_ITEMS, OP_READ_ALL_ITEMS) else None
    return BackendPage(
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
    """Check the binding's container ID and partition-key definition.

    This returns container properties, not a service response, and does not
    change the client's saved response headers.

    :param raw: Binding tuple of resource ID, partition-key paths, kind, and system-key flag.
    :type raw: typing.Any
    :return: Validated container metadata.
    :rtype: ~azure.cosmos._backend.contracts.ContainerMetadata
    """
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


def response_exception_from_binding(error: BaseException) -> CosmosHttpResponseError:
    """Convert a binding response error to a public Cosmos exception.

    Used for driver initialization, metadata lookups, and item operations.
    Keep its headers on the exception without replacing the client's saved
    response headers.

    :param error: Binding exception containing a five-element response tuple in its arguments.
    :type error: BaseException
    :return: Public exception with normalized headers and response diagnostics.
    :rtype: ~azure.cosmos.exceptions.CosmosHttpResponseError
    """
    from .._helpers._exceptions import error_message_from_body, map_backend_response_to_exception
    from .._helpers._response_parse import apply_response_diagnostics, apply_request_charge_format

    if len(error.args) != 1 or not isinstance(error.args[0], tuple) or len(error.args[0]) != 5:
        raise BindingProtocolError("The binding returned an invalid response error")
    response = build_backend_response(*error.args[0])
    if response.status_code < 400:
        raise BindingProtocolError("The binding returned a failure with a non-error status")
    headers = CaseInsensitiveDict(response.headers or {})
    apply_request_charge_format(headers)
    apply_response_diagnostics(headers, response.diagnostics)
    response = replace(response, headers=headers)
    return map_backend_response_to_exception(
        response, message=error_message_from_body(response.body, response.status_code)
    )


def normalize_response_headers(
    headers: Optional[Mapping[str, Any]],
) -> Optional[CaseInsensitiveDict]:
    """Wrap the binding's response-header dict in a ``CaseInsensitiveDict``.

    Copy entries into a new mapping. Names that differ only in case can collapse
    to one entry, with the later assignment winning. ``None`` or empty input
    returns ``None``. This cannot recover service headers omitted by the driver.

    :param headers: Response headers to copy, or None.
    :type headers: typing.Mapping[str, typing.Any] or None
    :return: Case-insensitive copy, or None for absent or empty headers.
    :rtype: ~azure.core.utils.CaseInsensitiveDict or None
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
    """Build arguments for the binding's ``acquire_driver_handle`` function.

    A token credential is the fourth argument, with None in the master-key
    position. A master key uses the three-argument form. Supplying both raises
    here; supplying neither is rejected by the binding.

    :param endpoint: Cosmos account endpoint URL.
    :type endpoint: str
    :param master_key: Account key, or None when using a token credential.
    :type master_key: str or None
    :param client_config: Prepared client settings, or None for defaults.
    :type client_config: ~azure.cosmos._backend.contracts.PreparedClientConfig or None
    :param token_credential: Token credential retained for driver authentication, or None.
    :type token_credential: typing.Any
    :return: Positional arguments for acquiring a driver handle.
    :rtype: tuple[typing.Any, ...]
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

    The binding returns five elements:
    ``(status, sub_status, headers, body, diagnostics_or_none)``. The default
    diagnostics argument also allows tests to supply only four values. It does
    not make an older binding compatible with current prepared requests.

    :param status_code: HTTP status convertible to an integer.
    :type status_code: typing.Any
    :param sub_status: Cosmos sub-status convertible to an integer.
    :type sub_status: typing.Any
    :param headers: Binding response headers, or None.
    :type headers: typing.Mapping[str, typing.Any] or None
    :param body: Response body convertible to bytes; false values produce an empty body.
    :type body: typing.Any
    :param diagnostics: Driver diagnostics, or None when absent.
    :type diagnostics: typing.Any
    :return: Normalized backend response.
    :rtype: ~azure.cosmos._backend.contracts.BackendResponse
    """
    return BackendResponse(
        status_code=int(status_code),
        sub_status=int(sub_status),
        headers=normalize_response_headers(headers),
        body=bytes(body) if body else b"",
        diagnostics=diagnostics,
    )
