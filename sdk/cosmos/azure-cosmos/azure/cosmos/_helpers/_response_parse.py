# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Parse backend responses, publish response headers, and invoke response hooks.

parse_backend_response only builds the result. process_backend_response can
also update client-owned headers and call a hook. Neither performs a binding
call; a parsing or callback failure is not permission for legacy fallback.
"""

from __future__ import annotations
import inspect
import json
from copy import deepcopy
from dataclasses import replace
from functools import partial
from typing import Any, Callable, Mapping, Optional

from azure.core.utils import CaseInsensitiveDict
from ._exceptions import (
    error_message_from_body,
    is_success_status,
    map_backend_response_to_exception,
)
from ._client_context import ClientLastResponseHeaders
from ._wire_encoding import format_ru_charge
from .._backend.contracts import BackendPage, BackendResponse
from .._cosmos_responses import CosmosDict
from .._operation_deadline import remaining_timeout

# Matches ``http_constants.HttpHeaders.RequestCharge``; inlined to avoid
# an extra import for a single string.
_REQUEST_CHARGE_HEADER = "x-ms-request-charge"
_DIAGNOSTICS_HEADER = "x-ms-cosmos-sdk-diagnostics"


def page_to_backend_response(page: BackendPage) -> BackendResponse:
    """Expose a page's response fields to the shared body and error parser.

    :param BackendPage page: Backend page carrying status, headers, body, and diagnostics.
    :return: A response containing the page's response fields.
    :rtype: ~azure.cosmos._backend.contracts.BackendResponse
    """
    return BackendResponse(
        status_code=page.status_code,
        sub_status=page.sub_status,
        headers=page.headers,
        body=page.body,
        diagnostics=page.diagnostics,
    )


def validate_response_hook_is_synchronous(response_hook: Any, operation: str) -> None:
    """Reject declared async hooks before an operation dispatches.

    :param Any response_hook: The customer callback, or None.
    :param str operation: Public operation name used in the error.
    :raises TypeError: The callback is an async function or callable object.
    :rtype: None
    """
    if response_hook is None:
        return
    hook = response_hook
    while isinstance(hook, partial):
        hook = hook.func
    if any(
        inspect.iscoroutinefunction(candidate) or inspect.isasyncgenfunction(candidate)
        for candidate in (hook, getattr(hook, "__call__", None))
    ):
        raise TypeError(f"{operation} response_hook must be synchronous; async hooks are not supported.")


def with_response_header_snapshot(
    response_hook: Optional[Callable[[Mapping[str, Any], Any], None]],
    *,
    copy_body: bool = False,
) -> Optional[Callable[[Mapping[str, Any], Any], None]]:
    """Give the response hook copied headers and, when requested, a copied body.

    :param callable or None response_hook: Callback accepting response headers and a parsed body.
    :keyword bool copy_body: Whether to deep-copy the body before invoking the callback.
    :return: A snapshotting callback, or None when no callback was supplied.
    :rtype: callable or None
    """
    if response_hook is None:
        return None

    def on_response(headers: Mapping[str, Any], body: Any) -> None:
        response_hook(
            CaseInsensitiveDict(headers), deepcopy(body) if copy_body else body
        )

    return on_response


def process_create_response(
    response: BackendResponse,
    *,
    client_connection: Any,
) -> CosmosDict:
    """A not-modified read response is not a successful creation.

    :param BackendResponse response: Creation response to validate and parse.
    :keyword Any client_connection: Connection whose last response headers are updated.
    :return: Parsed creation properties with response headers.
    :rtype: ~azure.cosmos.CosmosDict
    """
    if response.status_code == 304:
        raise map_backend_response_to_exception(response, message="Container creation returned HTTP 304, not success.")
    return process_backend_response(response, client_connection=client_connection)


def process_database_read_response(
    response: BackendResponse,
    *,
    client_connection: Any,
    response_hook: Optional[Callable[[Mapping[str, Any], Any], None]] = None,
) -> CosmosDict:
    """Preserve the legacy database-read hook's None body on a 304 response.

    :param BackendResponse response: Database read response to parse.
    :keyword Any client_connection: Connection whose last response headers are updated.
    :keyword callable or None response_hook: Callback receiving copied headers and the body, or None for HTTP 304.
    :return: Parsed database properties with response headers.
    :rtype: ~azure.cosmos.CosmosDict
    """

    def on_response(headers: Mapping[str, Any], body: Any) -> None:
        if response_hook is not None:
            response_hook(headers, None if response.status_code == 304 else body)

    return process_backend_response(
        response,
        client_connection=client_connection,
        response_hook=on_response if response_hook is not None else None,
    )


def process_delete_response(
    response: BackendResponse,
    *,
    client_connection: Optional[Any] = None,
    response_state: Optional[ClientLastResponseHeaders] = None,
    response_hook: Optional[Callable[[Mapping[str, Any], None], None]] = None,
) -> None:
    """Parse errors and headers while preserving the no-body deletion contract.

    :param BackendResponse response: Deletion response to validate and parse.
    :keyword Any client_connection: Optional connection whose last response headers are updated.
    :keyword ClientLastResponseHeaders or None response_state: Optional client-owned header state to update.
    :keyword callable or None response_hook: Callback receiving response headers and a None body.
    :return: None.
    :rtype: None
    """
    result = process_backend_response(response, client_connection=client_connection, response_state=response_state)
    if response_hook is not None:
        response_hook(result.get_response_headers(), None)


def process_backend_response(
    response: BackendResponse,
    *,
    client_connection: Optional[Any] = None,
    response_state: Optional[ClientLastResponseHeaders] = None,
    response_hook: Optional[Callable[[Mapping[str, Any], Any], None]] = None,
) -> CosmosDict:
    """Translate a ``BackendResponse`` into a ``CosmosDict``.

    :param response: The ``BackendResponse``. The bytes are assumed to
        contain JSON (or be empty). Invalid JSON/encoding errors propagate
        from ``json.loads``.
    :type response: BackendResponse
    :keyword client_connection: When supplied, its
        ``last_response_headers`` attribute is updated with the parsed
        headers. ``None`` skips updating a connection; production callers can
        supply ``response_state`` instead or leave client header state unchanged.
    :type client_connection: Optional[Any]
    :keyword response_state: Narrow client-owned header state for connection-free
        callers. The connection argument remains for unmigrated families.
    :type response_state: Optional[ClientLastResponseHeaders]
    :keyword response_hook: Optional callable invoked once after parsing and
        result construction with ``(headers, parsed_body)``. Its exceptions
        propagate. Headers are copied independently for the hook and client
        diagnostic state; body isolation is the caller's responsibility.
    :type response_hook: Optional[Callable[[Mapping[str, Any], Any], None]]
    :returns: A ``CosmosDict`` whose content is the parsed JSON (or
        ``{}`` for an accepted empty response) with response headers available
        through ``get_response_headers()``.
    :rtype: CosmosDict
    :raises CosmosHttpResponseError: For statuses outside 2xx other than 304. The
        typed subclass is chosen by ``map_backend_response_to_exception``.
    """
    headers = _copy_response_headers(response.headers or {})
    apply_request_charge_format(headers)
    apply_response_diagnostics(headers, response.diagnostics)

    if client_connection is not None:
        client_connection.last_response_headers = _copy_response_headers(headers)
    if response_state is not None:
        response_state.last_response_headers = _copy_response_headers(headers)

    parsed = parse_response_body(replace(response, headers=headers))
    cosmos_dict = CosmosDict(parsed, response_headers=headers)
    if response_hook is not None:
        response_hook(_copy_response_headers(headers), parsed)
    return cosmos_dict


def build_response_headers(response: BackendResponse) -> CaseInsensitiveDict:
    """Build normalized headers without mutating the response's header mapping.

    :param BackendResponse response: Response supplying headers and diagnostics.
    :return: Case-insensitive headers with formatted charge and diagnostics values.
    :rtype: ~azure.core.utils.CaseInsensitiveDict
    """
    headers = CaseInsensitiveDict(response.headers or {})
    apply_request_charge_format(headers)
    apply_response_diagnostics(headers, response.diagnostics)
    return headers


def parse_backend_response(response: BackendResponse) -> CosmosDict:
    """Decode a response without updating client state or invoking callbacks.

    :param BackendResponse response: Backend response to validate and decode.
    :return: Parsed body carrying normalized response headers.
    :rtype: ~azure.cosmos.CosmosDict
    """
    headers = build_response_headers(response)
    return CosmosDict(parse_response_body(replace(response, headers=headers)), response_headers=headers)


def parse_response_body(response: BackendResponse) -> Any:
    """Decode the success body or raise its mapped service/JSON error.

    :param BackendResponse response: Response supplying status and UTF-8 JSON bytes.
    :return: Decoded JSON, or an empty dictionary for an accepted empty response.
    :rtype: Any
    """
    # Accept conditional-read 304 separately from 2xx. An empty body becomes
    # {}; a nonempty body still goes through JSON decoding below.
    is_not_modified = response.status_code == 304

    if not is_not_modified and not is_success_status(response.status_code):
        message = error_message_from_body(response.body, response.status_code)
        raise map_backend_response_to_exception(response, message=message)

    if not response.body:
        # ``no_response=True`` returns an empty CosmosDict, not None.
        # This also handles an empty 304 body without synthesizing an ETag.
        parsed: Any = {}
    else:
        # Lossy recovery, when selected, has already run in the Rust driver.
        parsed = json.loads(response.body.decode("utf-8"))

    return parsed


def _copy_response_headers(headers: Mapping[str, Any]) -> CaseInsensitiveDict:
    """Reuse string header values while copying mutable backend-response values.

    :param Mapping[str, Any] headers: Headers to snapshot.
    :return: Case-insensitive headers isolated from mutable source values.
    :rtype: ~azure.core.utils.CaseInsensitiveDict
    """
    snapshot = CaseInsensitiveDict()
    for key, value in headers.items():
        # A str subclass can carry mutable attributes and must still be copied.
        snapshot[key] = value if type(value) is str else deepcopy(value)  # pylint: disable=unidiomatic-typecheck
    return snapshot


def apply_request_charge_format(headers: CaseInsensitiveDict) -> None:
    """Ensure the request-charge header is a string in the wire format.

    No-op when the header is absent or already a string. The Rust path
    may surface the charge as a numeric type; for example, 1 becomes "1.0".

    :param CaseInsensitiveDict headers: Header mapping updated in place.
    :return: None.
    :rtype: None
    """
    raw = headers.get(_REQUEST_CHARGE_HEADER)
    if raw is None or isinstance(raw, str):
        return
    headers[_REQUEST_CHARGE_HEADER] = format_ru_charge(float(raw))


def apply_response_diagnostics(headers: CaseInsensitiveDict, diagnostics: Any) -> None:
    """Add a supplied diagnostic value to this header mapping; skip None.

    :param CaseInsensitiveDict headers: Header mapping updated in place.
    :param Any diagnostics: Diagnostic value to stringify, or None to leave headers unchanged.
    :return: None.
    :rtype: None
    """
    if diagnostics is None:
        return
    if isinstance(diagnostics, str):
        headers[_DIAGNOSTICS_HEADER] = diagnostics
        return
    headers[_DIAGNOSTICS_HEADER] = str(diagnostics)


def complete_item_response(
    result: CosmosDict,
    response_hook: Optional[Callable[[Mapping[str, Any], CosmosDict], None]],
    deadline: Optional[float],
) -> CosmosDict:
    """Invoke a success hook outside retries with independent nested snapshots.

    :param CosmosDict result: Parsed item result returned unchanged.
    :param callable or None response_hook: Callback receiving isolated header and body snapshots.
    :param float or None deadline: Monotonic deadline checked before invoking the callback.
    :return: The original item result.
    :rtype: ~azure.cosmos.CosmosDict
    """
    remaining_timeout(deadline)
    if response_hook is not None:
        headers = result.get_response_headers()
        body = CosmosDict(
            deepcopy(dict(result)) if len(result) else {},
            response_headers=CaseInsensitiveDict(headers),
        )
        response_hook(CaseInsensitiveDict(headers), body)
    return result
