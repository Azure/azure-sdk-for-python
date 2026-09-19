# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Pure response decoding, explicit header publication and isolated success hooks."""

from __future__ import annotations
import json
from dataclasses import replace
from azure.core.utils import CaseInsensitiveDict
from copy import deepcopy
from typing import Any, Callable, Mapping, Optional
from ._exceptions import (
    extract_message_from_body,
    is_success_status,
    map_backend_response_to_exception,
)
from ._item_context import ClientLastResponseHeaders
from ._wire_encoding import format_ru_charge
from .._backend.contracts import BackendResponse
from .._cosmos_responses import CosmosDict
from .._operation_deadline import remaining_timeout

# Matches ``http_constants.HttpHeaders.RequestCharge``; inlined to avoid
# an extra import for a single string.
_REQUEST_CHARGE_HEADER = "x-ms-request-charge"
_DIAGNOSTICS_HEADER = "x-ms-cosmos-sdk-diagnostics"


def with_response_header_snapshot(
    response_hook: Optional[Callable[[Mapping[str, Any], Any], None]],
    *,
    copy_body: bool = False,
) -> Optional[Callable[[Mapping[str, Any], Any], None]]:
    """Give the response hook copied headers and, when requested, a copied body."""
    if response_hook is None:
        return None

    def on_response(headers: Mapping[str, Any], body: Any) -> None:
        response_hook(
            CaseInsensitiveDict(headers), deepcopy(body) if copy_body else body
        )

    return on_response


def process_database_read_response(
    response: BackendResponse,
    *,
    client_connection: Any,
    response_hook: Optional[Callable[[Mapping[str, Any], Any], None]] = None,
) -> CosmosDict:
    """Preserve the legacy database-read hook's None body on a 304 response."""

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
    client_connection: Any,
    response_hook: Optional[Callable[[Mapping[str, Any], None], None]] = None,
) -> None:
    """Parse errors and headers while preserving the no-body deletion contract."""
    result = process_backend_response(response, client_connection=client_connection)
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
    :param client_connection: When supplied, its
        ``last_response_headers`` attribute is updated with the parsed
        headers. ``None`` skips that side effect (used by tests).
    :type client_connection: Optional[Any]
    :param response_state: Narrow client-owned header state for connection-free
        callers. The connection argument remains for unmigrated families.
    :type response_state: Optional[ClientLastResponseHeaders]
    :param response_hook: Optional callable invoked once after parsing and
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
    headers = _take_response_headers(response)
    apply_request_charge_format(headers)
    apply_response_diagnostics(headers, response.diagnostics)

    if client_connection is not None:
        client_connection.last_response_headers = deepcopy(headers)
    if response_state is not None:
        response_state.last_response_headers = deepcopy(headers)

    parsed = parse_response_body(replace(response, headers=headers))
    cosmos_dict = CosmosDict(parsed, response_headers=headers)
    if response_hook is not None:
        response_hook(deepcopy(headers), parsed)
    return cosmos_dict


def build_response_headers(response: BackendResponse) -> CaseInsensitiveDict:
    """Build normalized headers without mutating the response's header mapping."""
    headers = CaseInsensitiveDict(response.headers or {})
    apply_request_charge_format(headers)
    apply_response_diagnostics(headers, response.diagnostics)
    return headers


def parse_backend_response(response: BackendResponse) -> CosmosDict:
    """Decode a response without updating client state or invoking callbacks."""
    headers = build_response_headers(response)
    return CosmosDict(parse_response_body(replace(response, headers=headers)), response_headers=headers)


def parse_response_body(response: BackendResponse) -> Any:
    """Decode the success body or raise its mapped service/JSON error."""
    # Accept conditional-read 304 separately from 2xx. An empty body becomes
    # {}; a nonempty body still goes through JSON decoding below.
    is_not_modified = response.status_code == 304

    if not is_not_modified and not is_success_status(response.status_code):
        message = extract_message_from_body(response.body)
        raise map_backend_response_to_exception(response, message=message)

    if not response.body:
        # ``no_response=True`` returns an empty CosmosDict, not None.
        # This also handles an empty 304 body without synthesizing an ETag.
        parsed: Any = {}
    else:
        parsed = json.loads(response.body)

    return parsed


def _take_response_headers(response: BackendResponse) -> CaseInsensitiveDict:
    """Snapshot headers before normalization or publication to customer code."""
    return CaseInsensitiveDict(deepcopy(response.headers or {}))


def apply_request_charge_format(headers: CaseInsensitiveDict) -> None:
    """Ensure the request-charge header is a string in the wire format.

    No-op when the header is absent or already a string. The Rust path
    may surface the charge as a numeric type; this bridges the two
    representations so byte equality holds.
    """
    raw = headers.get(_REQUEST_CHARGE_HEADER)
    if raw is None or isinstance(raw, str):
        return
    headers[_REQUEST_CHARGE_HEADER] = format_ru_charge(float(raw))


def apply_response_diagnostics(headers: CaseInsensitiveDict, diagnostics: Any) -> None:
    """Add a supplied diagnostic value to this header mapping; skip None."""
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
    """Invoke a success hook outside retries with independent nested snapshots."""
    remaining_timeout(deadline)
    if response_hook is not None:
        headers = result.get_response_headers()
        body = CosmosDict(
            deepcopy(dict(result)) if len(result) else {},
            response_headers=CaseInsensitiveDict(headers),
        )
        response_hook(CaseInsensitiveDict(headers), body)
    return result
