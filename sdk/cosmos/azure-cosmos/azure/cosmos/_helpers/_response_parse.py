# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Pure response decoding, explicit header publication and isolated success hooks."""

from __future__ import annotations
import json
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
        be valid UTF-8 JSON (or empty); a non-JSON 2xx body raises
        ``json.JSONDecodeError`` (matching the legacy behaviour).
    :type response: BackendResponse
    :param client_connection: When supplied, its
        ``last_response_headers`` attribute is updated with the parsed
        headers. ``None`` skips that side effect (used by tests).
    :type client_connection: Optional[Any]
    :param response_state: Narrow client-owned header state for connection-free
        item callers. The connection argument remains for unmigrated families.
    :type response_state: Optional[ClientLastResponseHeaders]
    :param response_hook: Optional callable invoked exactly once on
        success with ``(headers, parsed_body)``. Not invoked on failure.
    :type response_hook: Optional[Callable[[Mapping[str, Any], Any], None]]
    :returns: A ``CosmosDict`` whose content is the parsed JSON (or
        ``{}`` for no-body 2xx) and whose ``response_headers``
        attribute is a ``CaseInsensitiveDict``.
    :rtype: CosmosDict
    :raises CosmosHttpResponseError: For any non-2xx response. The
        typed subclass is chosen by ``map_backend_response_to_exception``.
    """
    headers = _take_response_headers(response)
    apply_request_charge_format(headers)
    apply_response_diagnostics(headers, response.diagnostics)

    if client_connection is not None:
        client_connection.last_response_headers = headers
    if response_state is not None:
        response_state.last_response_headers = headers

    parsed = parse_response_body(response)
    cosmos_dict = CosmosDict(parsed, response_headers=headers)
    if response_hook is not None:
        response_hook(headers, parsed)
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
    return CosmosDict(parse_response_body(response), response_headers=headers)


def parse_response_body(response: BackendResponse) -> Any:
    """Decode the success body or raise its mapped service/JSON error."""
    # 304 Not Modified is the conditional-GET success signal on
    # read_item (see module docstring). It is < 400 but not in the
    # 2xx range, so is_success_status rejects it; handle it as a
    # non-error empty body before that check. The service guarantees
    # an empty body for 304, so falling into the no-body branch below
    # is safe.
    is_not_modified = response.status_code == 304

    if not is_not_modified and not is_success_status(response.status_code):
        message = extract_message_from_body(response.body)
        raise map_backend_response_to_exception(response, message=message)

    if not response.body:
        # ``no_response=True`` returns an empty CosmosDict, not None.
        # 304 lands here too: empty body, headers carry the current
        # etag (equal to the customer's ``If-None-Match``).
        parsed: Any = {}
    else:
        parsed = json.loads(response.body)

    return parsed


def _take_response_headers(response: BackendResponse) -> CaseInsensitiveDict:
    """Return the response headers as a ``CaseInsensitiveDict``.

    The Rust backend already hands back a freshly-built
    ``CaseInsensitiveDict`` (``build_backend_response`` ->
    ``normalize_response_headers``) that belongs to this single-use
    ``BackendResponse`` and is shared with nothing else. In that common
    hot-path case we reuse it directly instead of copying it into a
    *second* dict: the response is built and consumed in one place (the
    backend ``execute`` -> ``process_backend_response`` hand-off in
    ``item_helper``, sync and async), so the later in-place
    request-charge fix cannot leak anywhere observable. Skipping the
    second construction removes a full per-response header copy from
    every point operation -- on the hottest path in the SDK.

    Only when the headers arrive in some other shape -- a plain mapping
    or ``None`` from a test fixture or a future backend -- do we build a
    fresh ``CaseInsensitiveDict`` so the parser's mutation cannot leak
    back into a caller-owned dict.
    """
    headers = response.headers
    if headers is None:
        return CaseInsensitiveDict()
    if isinstance(headers, CaseInsensitiveDict):
        return headers
    return CaseInsensitiveDict(headers)


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
    """Expose the SDK's additive diagnostic summary on every Rust response path."""
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
