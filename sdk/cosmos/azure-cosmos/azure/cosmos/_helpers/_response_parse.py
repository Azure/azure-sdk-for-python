# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Turn a ``BackendResponse`` into the ``CosmosDict`` customer code expects.

- 2xx with JSON body: build ``CosmosDict(parsed, response_headers)``
  and invoke ``response_hook(headers, parsed)`` exactly once.
- 2xx with empty body (``no_response=True`` / 204): build an empty
  ``CosmosDict({}, response_headers)`` so customer code keeps working.
- **304 Not Modified** (conditional ``read_item`` whose
  ``If-None-Match`` etag matched the current server version): treated
  as non-error success. The body is empty; the response headers
  carry the current etag (equal to what the customer sent in). The
  SDK returns an empty ``CosmosDict({}, response_headers)`` so
  customer code can check ``len(result)`` or compare
  ``result.get_response_headers()["etag"]``.
- Non-2xx (and non-304): raise the typed exception subclass for the
  status code via ``map_backend_response_to_exception``.

In all paths the headers are also written to
``client_connection.last_response_headers`` (the one documented side
effect, matching the legacy behaviour). When the Rust backend provides
diagnostics, they are surfaced through the synthetic header
``x-ms-cosmos-sdk-diagnostics`` on the same header map.

This module is used when a backend returns a real ``BackendResponse``
(today: ``RustBackend``). The "core-python" path bypasses it entirely
and goes straight to the legacy client-connection methods
(``CreateItem`` / ``ReadItem`` / ``DeleteItem``).
"""
from __future__ import annotations

import json
from typing import Any, Callable, Mapping, Optional

from azure.core.utils import CaseInsensitiveDict

from .._backend.contracts import BackendResponse
from .._cosmos_responses import CosmosDict
from ._exceptions import (
    extract_message_from_body,
    is_success_status,
    map_backend_response_to_exception,
)
from ._format_ru import format_ru_charge


# Matches ``http_constants.HttpHeaders.RequestCharge``; inlined to avoid
# an extra import for a single string.
_REQUEST_CHARGE_HEADER = "x-ms-request-charge"
_DIAGNOSTICS_HEADER = "x-ms-cosmos-sdk-diagnostics"


def parse_backend_response(
    response: BackendResponse,
    *,
    client_connection: Optional[Any] = None,
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
    headers = _normalise_headers(response)
    _normalise_request_charge_header(headers)
    _attach_diagnostics_header(headers, response.diagnostics)

    if client_connection is not None:
        client_connection.last_response_headers = headers

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

    cosmos_dict = CosmosDict(parsed, response_headers=headers)

    if response_hook is not None:
        response_hook(headers, parsed)

    return cosmos_dict


def _normalise_headers(response: BackendResponse) -> CaseInsensitiveDict:
    """Return the response headers as a ``CaseInsensitiveDict``.

    The Rust backend already hands back a freshly-built
    ``CaseInsensitiveDict`` (``build_backend_response`` ->
    ``normalize_response_headers``) that belongs to this single-use
    ``BackendResponse`` and is shared with nothing else. In that common
    hot-path case we reuse it directly instead of copying it into a
    *second* dict: the response is built and consumed in one place (the
    backend ``execute`` -> ``parse_backend_response`` hand-off in
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


def _normalise_request_charge_header(headers: CaseInsensitiveDict) -> None:
    """Ensure the request-charge header is a string in the wire format.

    No-op when the header is absent or already a string. The Rust path
    may surface the charge as a numeric type; this bridges the two
    representations so byte equality holds.
    """
    raw = headers.get(_REQUEST_CHARGE_HEADER)
    if raw is None or isinstance(raw, str):
        return
    headers[_REQUEST_CHARGE_HEADER] = format_ru_charge(float(raw))


def _attach_diagnostics_header(headers: CaseInsensitiveDict, diagnostics: Any) -> None:
    """Expose backend diagnostics through response headers for parity paths."""
    if diagnostics is None:
        return
    if isinstance(diagnostics, str):
        headers[_DIAGNOSTICS_HEADER] = diagnostics
        return
    headers[_DIAGNOSTICS_HEADER] = str(diagnostics)
