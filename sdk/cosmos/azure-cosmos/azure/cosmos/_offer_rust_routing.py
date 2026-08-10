# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""Shared Rust-routing helpers for the offer/throughput read and replace (sync + aio).

Every Cosmos container has one "offer" record that holds how much throughput
(RU/s) the container is provisioned for. Two public methods touch it:

- ``get_throughput`` (and its deprecated alias ``read_offer``) *reads* that record.
- ``replace_throughput`` *changes* it: read the current offer, apply the new RU/s
  (or autoscale setting), and PUT it back. This is a read-modify-write, so it uses
  the read helpers below plus the replace helpers.

On the legacy (core-python) path both are done by hand over the account's
``/offers`` feed. This module lets a Rust-backed client run the exact same work on
the Rust driver instead, and -- key point -- return offer records with the
identical shape, so the code that turns them into ``ThroughputProperties`` is
unchanged and the customer sees the same RU/s number and autoscale ceiling either
way.

Both the sync and async entry points call into this one module so they build the
identical request and parse the identical response. Without it, each entry point would
carry its own copy of the can-use / build / parse logic; the two could diverge, and a
customer's throughput read or change could behave differently depending on which
entry point (sync vs async) they used.

"""
from __future__ import annotations

from typing import Any, Mapping, cast

from . import _base as base
from . import _runtime_constants as runtime_constants
from . import documents
from . import http_constants
from ._backend.operations import OP_READ_OFFER, OP_REPLACE_OFFER
from ._backend.contracts import PreparedRequest
from ._constants import _Constants as Constants
from ._helpers._body_wire import serialize_body_to_bytes
from ._helpers._request_headers import DRIVER_OWNED_REQUEST_HEADERS
from ._helpers._response_parse import parse_backend_response
from ._request_object import RequestObject

_OFFERS_PATH = "/offers"


def can_use_rust_backend_for_read_offer(
    *,
    backend: Any,
    options: Mapping[str, Any],
    kwargs: Mapping[str, Any],
) -> bool:
    """Return True when ``read_offer`` / ``get_throughput`` can use the Rust backend.

    True only when this client uses the Rust backend and the remaining call shape is
    supported by the Rust route. The Rust binding now exposes an offer entry point (``read_offer`` /
    ``read_offer_async``), so a Rust-backed client's throughput read runs the offer
    query on the driver and returns the same offer records as legacy. Any extra
    kwarg -- which legacy forwards into ``QueryOffers`` -- keeps the call on legacy
    until that option is explicitly supported on the Rust path. This per-call gate is
    temporary migration code: it shrinks as options are supported and goes away once the
    whole operation is supported on Rust.

    :param backend: The client's Rust backend, or ``None`` for core-python.
    :type backend: Any
    :param options: Normalized request options for this call.
    :type options: Mapping[str, Any]
    :param kwargs: The caller's remaining arguments (any unsupported option keeps the
        call on legacy).
    :type kwargs: Mapping[str, Any]
    :rtype: bool
    """
    if backend is None:
        return False
    # Rust offer path does not yet support the socket read timeout or the
    # client-side availability strategy that legacy QueryOffers applies.
    if options.get(Constants.Kwargs.READ_TIMEOUT) is not None:
        return False
    if options.get(Constants.Kwargs.AVAILABILITY_STRATEGY) is not None:
        return False
    # Extra kwargs -> stay on legacy (Rust can't honor those options yet).
    return len(kwargs) == 0


def build_read_offer_prepared_request(
    *,
    container_link: str,
    offer_query: Mapping[str, Any],
    req_headers: Mapping[str, Any],
    options: Mapping[str, Any],
) -> PreparedRequest:
    """Build the PreparedRequest the binding's ``read_offer`` entry point consumes.

    The body is a query that picks out this container's one throughput record from
    the account's list of offers. Headers are copied from the legacy request
    preparation path so rust execution preserves parity for routing/session/timeout
    behavior and internal request metadata.

    :param container_link: The container's link, used as request context.
    :type container_link: str
    :param offer_query: The offer query spec (``{"query": ..., "parameters": ...}``).
    :type offer_query: Mapping[str, Any]
    :param req_headers: Legacy-prepared request headers for this call.
    :type req_headers: Mapping[str, Any]
    :param options: Normalized request options for this call.
    :type options: Mapping[str, Any]
    :rtype: ~azure.cosmos._backend.base.PreparedRequest
    """
    normalized_container_link = base.TrimBeginningAndEndingSlashes(container_link)
    body_bytes = serialize_body_to_bytes(dict(offer_query))
    headers = _build_prepared_headers_for_rust_offer_dispatch(options=options, req_headers=req_headers)
    return PreparedRequest(
        op=OP_READ_OFFER,
        container_link=normalized_container_link,
        body_bytes=body_bytes,
        partition_key_header="[]",
        headers=headers,
        item_id=None,
    )


def _build_prepared_headers_for_rust_offer_dispatch(
    *,
    options: Mapping[str, Any],
    req_headers: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the offer ``PreparedRequest.headers`` from the legacy header map.

    ``req_headers`` is a complete set of legacy wire headers (``_base.GetHeaders``
    built it), so it carries the standard headers the rust driver writes for
    itself -- the authorization signature, the timestamp, the content type.
    Those are stripped here; see ``DRIVER_OWNED_REQUEST_HEADERS`` for why sending
    them is redundant at best. The query/feed path strips the same set before its
    own dispatch, so the two rust entry points hand the binding the same shape.

    What remains is the ``x-ms-*`` headers the driver genuinely acts on, plus the
    two request options that live outside the header map: the excluded-location
    list and the overall-timeout sentinel.

    :param options: Normalized request options for this call.
    :type options: Mapping[str, Any]
    :param req_headers: Legacy-prepared request headers for this call.
    :type req_headers: Mapping[str, Any]
    :returns: The headers map to place on the ``PreparedRequest``.
    :rtype: dict[str, Any]
    """
    prepared_headers = {
        name: value
        for name, value in req_headers.items()
        if not (isinstance(name, str) and name.lower() in DRIVER_OWNED_REQUEST_HEADERS)
    }
    excluded_locations = options.get(Constants.Kwargs.EXCLUDED_LOCATIONS)
    if excluded_locations is not None:
        prepared_headers[Constants.Kwargs.EXCLUDED_LOCATIONS] = excluded_locations
    timeout_seconds = options.get(Constants.Kwargs.TIMEOUT)
    if timeout_seconds is not None:
        prepared_headers[Constants.OVERALL_TIMEOUT_SECONDS] = timeout_seconds
    return prepared_headers


def _prepare_offer_query_headers(
    *,
    client_connection: Any,
    options: Mapping[str, Any],
) -> dict[str, Any]:
    """Build service headers for a throughput offer query."""
    headers = dict(getattr(client_connection, "default_headers", {}))
    query_compatibility_mode = getattr(client_connection, "_query_compatibility_mode", None)
    if query_compatibility_mode in ("Default", "Query"):
        headers[http_constants.HttpHeaders.ContentType] = runtime_constants.MediaTypes.QueryJson
    elif query_compatibility_mode in ("SqlQuery",):
        headers[http_constants.HttpHeaders.ContentType] = runtime_constants.MediaTypes.SQL
    return base.GetHeaders(
        client_connection,
        headers,
        "post",
        _OFFERS_PATH,
        "",
        http_constants.ResourceType.Offer,
        documents._OperationType.SqlQuery,
        options,
    )


def prepare_read_offer_request(
    *,
    client_connection: Any,
    container_link: str,
    offer_query: Mapping[str, Any],
    options: Mapping[str, Any],
) -> PreparedRequest:
    """Prepare a throughput-read request without executing a backend."""
    req_headers = _prepare_offer_query_headers(client_connection=client_connection, options=options)
    request_params = RequestObject(
        http_constants.ResourceType.Offer,
        documents._OperationType.SqlQuery,
        req_headers,
        options.get("partitionKey", None),
    )
    base.set_session_token_header(
        client_connection, req_headers, _OFFERS_PATH, request_params, options
    )
    return build_read_offer_prepared_request(
        container_link=container_link,
        offer_query=offer_query,
        req_headers=req_headers,
        options=options,
    )


async def prepare_read_offer_request_async(
    *,
    client_connection: Any,
    container_link: str,
    offer_query: Mapping[str, Any],
    options: Mapping[str, Any],
) -> PreparedRequest:
    """Async twin of :func:`prepare_read_offer_request`."""
    req_headers = _prepare_offer_query_headers(client_connection=client_connection, options=options)
    request_params = RequestObject(
        http_constants.ResourceType.Offer,
        documents._OperationType.SqlQuery,
        req_headers,
        options.get("partitionKey", None),
    )
    await base.set_session_token_header_async(
        client_connection, req_headers, _OFFERS_PATH, request_params, options
    )
    return build_read_offer_prepared_request(
        container_link=container_link,
        offer_query=offer_query,
        req_headers=req_headers,
        options=options,
    )


def parse_read_offer_response(backend_response: Any, *, client_connection: Any) -> list[dict[str, Any]]:
    """Parse a backend response into the legacy offer-list shape."""
    parsed = parse_backend_response(
        backend_response,
        client_connection=client_connection,
        response_hook=None,
    )
    return parse_read_offer_payload(cast(Mapping[str, Any], parsed))


def parse_read_offer_payload(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Convert the Rust payload ``{"Offers":[...]}`` to a plain list of offer records.

    An "offer record" is the raw dict the Cosmos service returns to describe a
    container's throughput -- it holds the current RU/s and any autoscale settings.
    ``get_throughput`` later reads those numbers out of this list to build the
    ``ThroughputProperties`` object the customer gets back.

    The legacy (core-python) path fetches the same records with the client's
    ``QueryOffers`` method; this function just produces that same list of records from
    the Rust response instead. Because the list is identical in shape, the code that
    turns it into ``ThroughputProperties`` is unchanged and both paths return the same
    throughput to the customer.

    :param payload: The parsed Rust response body.
    :type payload: Mapping[str, Any]
    :rtype: list[dict[str, Any]]
    :raises ValueError: when the payload is not shaped as expected.
    """
    # Response side: unwrap the {"Offers":[...]} the Rust path sends back so rows match legacy.
    raw_offers = payload.get("Offers")
    if not isinstance(raw_offers, list):
        raise ValueError(
            "read_offer Rust payload must include a list field 'Offers'."
        )
    offers: list[dict[str, Any]] = []
    for index, offer in enumerate(raw_offers):
        if not isinstance(offer, Mapping):
            raise ValueError(
                "read_offer Rust payload entry at index {} must be an object.".format(index)
            )
        offers.append(dict(offer))
    return offers

def can_use_rust_backend_for_replace_throughput(
    *,
    backend: Any,
    options: Mapping[str, Any],
    kwargs: Mapping[str, Any],
) -> bool:
    """Return True when ``replace_throughput`` can use the Rust backend.

    ``replace_throughput`` is a two-step read-modify-write on the container's offer:
    it first reads the offer (the same query ``get_throughput`` runs) and then PUTs
    the mutated offer back. Both steps use the offer entry points on the Rust
    driver, and both honor exactly the same options, so this gate matches the read gate
    (``can_use_rust_backend_for_read_offer``): Rust-backed client, no socket read
    timeout, no client-side availability strategy, and no extra kwargs. Any unsupported
    option keeps the whole call on legacy so nothing a customer passed is silently
    dropped.

    :param backend: The client's Rust backend, or ``None`` for core-python.
    :type backend: Any
    :param options: Normalized request options for this call.
    :type options: Mapping[str, Any]
    :param kwargs: The caller's remaining arguments (any unsupported option keeps the
        call on legacy).
    :type kwargs: Mapping[str, Any]
    :rtype: bool
    """
    return can_use_rust_backend_for_read_offer(backend=backend, options=options, kwargs=kwargs)


def build_replace_offer_prepared_request(
    *,
    container_link: str,
    offer: Mapping[str, Any],
    offer_id: str,
    req_headers: Mapping[str, Any],
    options: Mapping[str, Any],
) -> PreparedRequest:
    """Build the PreparedRequest the binding's ``replace_offer`` entry point consumes.

    The body is the full, already-mutated offer document (the same document the
    legacy ``ReplaceOffer`` PUTs). The offer RID travels in ``item_id`` -- that is
    which offer the driver overwrites (it PUTs to ``/offers/{rid}``). Headers are
    copied from the legacy request-preparation path so Rust execution preserves
    parity for routing/session/timeout behavior and internal request metadata.

    :param container_link: The container's link, used as request context.
    :type container_link: str
    :param offer: The mutated offer document to send as the request body.
    :type offer: Mapping[str, Any]
    :param offer_id: The offer's RID (resolved from the offer's ``_self`` link).
    :type offer_id: str
    :param req_headers: Legacy-prepared request headers for this call.
    :type req_headers: Mapping[str, Any]
    :param options: Normalized request options for this call.
    :type options: Mapping[str, Any]
    :rtype: ~azure.cosmos._backend.base.PreparedRequest
    """
    normalized_container_link = base.TrimBeginningAndEndingSlashes(container_link)
    body_bytes = serialize_body_to_bytes(dict(offer))
    headers = _build_prepared_headers_for_rust_offer_dispatch(options=options, req_headers=req_headers)
    return PreparedRequest(
        op=OP_REPLACE_OFFER,
        container_link=normalized_container_link,
        body_bytes=body_bytes,
        partition_key_header="[]",
        headers=headers,
        item_id=offer_id,
    )


def _prepare_offer_replace_headers(
    *,
    client_connection: Any,
    offer_link: str,
    offer_id: str,
    options: Mapping[str, Any],
) -> dict[str, Any]:
    """Build service headers for a throughput offer replacement."""
    headers = dict(getattr(client_connection, "default_headers", {}))
    return base.GetHeaders(
        client_connection,
        headers,
        "put",
        base.GetPathFromLink(offer_link),
        offer_id,
        http_constants.ResourceType.Offer,
        documents._OperationType.Replace,
        options,
    )


def prepare_replace_offer_request(
    *,
    client_connection: Any,
    container_link: str,
    offer: Mapping[str, Any],
    options: Mapping[str, Any],
) -> PreparedRequest:
    """Prepare an offer replacement without executing a backend."""
    offer_link = offer["_self"]
    offer_id = base.GetResourceIdOrFullNameFromLink(offer_link)
    req_headers = _prepare_offer_replace_headers(
        client_connection=client_connection,
        offer_link=offer_link,
        offer_id=offer_id,
        options=options,
    )
    request_params = RequestObject(
        http_constants.ResourceType.Offer,
        documents._OperationType.Replace,
        req_headers,
        options.get("partitionKey", None),
    )
    base.set_session_token_header(
        client_connection, req_headers, base.GetPathFromLink(offer_link), request_params, options
    )
    return build_replace_offer_prepared_request(
        container_link=container_link,
        offer=offer,
        offer_id=offer_id,
        req_headers=req_headers,
        options=options,
    )


async def prepare_replace_offer_request_async(
    *,
    client_connection: Any,
    container_link: str,
    offer: Mapping[str, Any],
    options: Mapping[str, Any],
) -> PreparedRequest:
    """Async twin of :func:`prepare_replace_offer_request`."""
    offer_link = offer["_self"]
    offer_id = base.GetResourceIdOrFullNameFromLink(offer_link)
    req_headers = _prepare_offer_replace_headers(
        client_connection=client_connection,
        offer_link=offer_link,
        offer_id=offer_id,
        options=options,
    )
    request_params = RequestObject(
        http_constants.ResourceType.Offer,
        documents._OperationType.Replace,
        req_headers,
        options.get("partitionKey", None),
    )
    await base.set_session_token_header_async(
        client_connection, req_headers, base.GetPathFromLink(offer_link), request_params, options
    )
    return build_replace_offer_prepared_request(
        container_link=container_link,
        offer=offer,
        offer_id=offer_id,
        req_headers=req_headers,
        options=options,
    )


def parse_replace_offer_response(backend_response: Any, *, client_connection: Any) -> Any:
    """Parse an offer replacement response."""
    return parse_backend_response(
        backend_response,
        client_connection=client_connection,
        response_hook=None,
    )
