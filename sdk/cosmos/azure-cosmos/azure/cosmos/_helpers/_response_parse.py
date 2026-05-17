# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Turn a ``BackendResponse`` into the same ``CosmosDict`` v4 returned.

The five wire-prep helpers prepare a request; this module is the other
side of the seam — it converts the backend's response back into the
shape customer code expects:

* On success, build a ``CosmosDict`` from the JSON body plus the
  response headers, then invoke any ``response_hook`` the caller
  supplied (D1, D2, D3, D4).
* On failure, raise the right typed exception via the exception-mapping helper
  (``map_backend_response_to_exception``). The exception carries the
  same ``status_code``, ``sub_status``, ``headers``, and ``response``
  surface customer code reads today.
* In both paths, write the response headers onto
  ``client_connection.last_response_headers`` so the existing
  ``client.client_connection.last_response_headers`` access pattern
  keeps working.

The function is pure with one explicit side effect: assigning to
``client_connection.last_response_headers``. That side effect is
documented and matches the legacy behaviour byte-for-byte.

This module is the parser the helper runs whenever a backend returns
a real ``BackendResponse`` (today: only ``RustBackend``). The
"core-python" selection bypasses this module entirely — it forwards
straight to legacy ``client_connection.CreateItem``, which produces
its own ``CosmosDict``. Tests in ``tests/test_response_parse_unit.py``
exercise every branch in isolation.
"""
from __future__ import annotations

import json
from typing import Any, Callable, Mapping, Optional

from azure.core.utils import CaseInsensitiveDict

from .._backend.base import BackendResponse
from .._cosmos_responses import CosmosDict
from ._exceptions import (
    extract_message_from_body,
    is_success_status,
    map_backend_response_to_exception,
)
from ._format_ru import format_ru_charge


# Header name the request charge lives under. Kept as a constant so
# the RU-formatting branch below is self-explanatory. The value
# matches ``http_constants.HttpHeaders.RequestCharge``; reproducing
# it here as a literal avoids an extra import for a single string.
_REQUEST_CHARGE_HEADER = "x-ms-request-charge"


def parse_backend_response(
    response: BackendResponse,
    *,
    client_connection: Optional[Any] = None,
    response_hook: Optional[Callable[[Mapping[str, Any], Any], None]] = None,
) -> CosmosDict:
    """Translate a ``BackendResponse`` into the ``CosmosDict`` customer code expects.

    Behaviour matches the legacy code path in
    ``CosmosClientConnection.CreateItem`` and friends:

    * 2xx with a JSON body: ``json.loads`` the body, build a
      ``CosmosDict(parsed, response_headers=headers)`` (D1),
      stash ``headers`` on ``client_connection.last_response_headers``
      (D2), invoke ``response_hook(headers, parsed)`` exactly once
      (D4), return.
    * 2xx with an empty body (``no_response=True`` â→ 204): build an
      empty ``CosmosDict({}, response_headers=headers)`` (D3) so
      customer code that does ``if result: ...`` flips to the
      empty-dict branch instead of crashing on ``json.loads(b"")``.
    * Non-2xx: raise the right typed exception via the exception-mapping helper's
      ``map_backend_response_to_exception``. The exception carries
      ``status_code``, ``sub_status``, ``headers``, and ``response``
      so existing ``except CosmosHttpResponseError as e:`` blocks
      that read those attributes keep working.

    :param response: The ``BackendResponse`` produced by either
        backend. The function assumes the bytes the response carries
        are valid UTF-8 JSON (or empty); a non-JSON 2xx body raises
        ``json.JSONDecodeError``, which is the same failure mode the
        legacy path produces.
    :type response: BackendResponse
    :param client_connection: The ``CosmosClientConnection`` whose
        ``last_response_headers`` attribute should be updated. May be
        ``None`` for tests that do not exercise that side effect; in
        that case the function does not touch it.
    :type client_connection: Optional[Any]
    :param response_hook: Optional callable the caller registered.
        Invoked exactly once on success with ``(headers, parsed_body)``,
        the same signature the legacy SDK uses. Not invoked on
        failure (the legacy path also does not invoke it on failure).
    :type response_hook: Optional[Callable[[Mapping[str, Any], Any], None]]
    :returns: A ``CosmosDict`` whose dict content is the parsed JSON
        body (empty dict for a no-body 2xx) and whose
        ``response_headers`` attribute is the response's
        ``CaseInsensitiveDict``.
    :rtype: CosmosDict
    :raises CosmosHttpResponseError: For any non-2xx response. The
        specific subclass (``CosmosResourceExistsError`` for 409,
        ``CosmosResourceNotFoundError`` for 404, etc.) is chosen by
        ``map_backend_response_to_exception``.
    """
    # Normalise headers up front so every branch below sees a
    # CaseInsensitiveDict regardless of what the backend handed in.
    # CaseInsensitiveDict is what the legacy ``last_response_headers``
    # consumer expects; preserving the type here means customer code
    # doing ``headers["X-MS-Request-Charge"]`` (mixed case) works.
    headers = _normalise_headers(response)

    # Normalise the request-charge header to a string for consistency
    # between backends. The core-python path already gets a string from
    # the wire; the Rust path may surface the charge as a typed float
    # in BackendResponse.headers. If we find a non-string value at the
    # request-charge slot, format it via the D5 helper so byte equality
    # with the core-python path holds.
    _normalise_request_charge_header(headers)

    # Side effect 1 of 1: keep ``client_connection.last_response_headers``
    # current. The legacy path does the same thing inside CreateItem.
    if client_connection is not None:
        client_connection.last_response_headers = headers

    # Failure path: raise the right typed exception.
    if not is_success_status(response.status_code):
        message = extract_message_from_body(response.body)
        raise map_backend_response_to_exception(response, message=message)

    # Success path: build a CosmosDict.
    if not response.body:
        # D3: no_response=True returns an empty CosmosDict({}), not
        # None and not an exception. ``json.loads(b"")`` would have
        # raised JSONDecodeError; explicitly returning the empty dict
        # is the contract.
        parsed: Any = {}
    else:
        # D1: the common case. The legacy code uses json.loads with
        # the default parser (no special hook); match it.
        parsed = json.loads(response.body)

    cosmos_dict = CosmosDict(parsed, response_headers=headers)

    # D4: response_hook fires exactly once on success, with the
    # headers map and the parsed body. The signature
    # (headers, parsed) is the one the legacy SDK uses.
    if response_hook is not None:
        response_hook(headers, parsed)

    return cosmos_dict


def _normalise_headers(response: BackendResponse) -> CaseInsensitiveDict:
    """Return the response headers as a fresh ``CaseInsensitiveDict``.

    Always returns a *new* dict instance so that subsequent in-place
    mutation by the parser (e.g. normalising the request-charge
    header) cannot leak back into the caller's ``BackendResponse``.
    The caller writes the returned dict onto
    ``client_connection.last_response_headers``; isolating that slot
    from the backend's data is what guarantees a backend that re-uses
    its own header dict across calls is safe.
    """
    if response.headers is None:
        return CaseInsensitiveDict()
    # Copy unconditionally — even when the response handed us a
    # ``CaseInsensitiveDict`` already, returning it directly would
    # mean the parser's ``headers[_REQUEST_CHARGE_HEADER] = ...``
    # write at the bottom of this module mutates the backend's data.
    return CaseInsensitiveDict(response.headers)


def _normalise_request_charge_header(headers: CaseInsensitiveDict) -> None:
    """Make sure the request-charge header is a string in the wire format.

    Mutates ``headers`` in place. No-op when the header is absent or
    already a string. The shape (one lookup, one conditional write)
    is intentionally minimal — every Cosmos response runs through
    here, so any extra branch lands on the hottest path in the SDK.
    """
    raw = headers.get(_REQUEST_CHARGE_HEADER)
    if raw is None or isinstance(raw, str):
        return
    # The Rust path may surface the charge as a typed numeric value;
    # the core-python path always has a string (the original wire
    # value). Bridge the two by formatting the numeric to a string the
    # same way the server would have.
    headers[_REQUEST_CHARGE_HEADER] = format_ru_charge(float(raw))
