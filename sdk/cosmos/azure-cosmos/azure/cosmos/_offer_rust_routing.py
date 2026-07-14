# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""Shared Rust-routing helpers for the offer/throughput read (sync + aio).

``read_offer`` (the deprecated alias) and ``get_throughput`` read a container's
provisioned throughput. On the legacy path this is a query over the account's
``/offers`` feed, filtered to the one offer whose ``resource`` link is this
container, then deserialized into ``ThroughputProperties``.

Both the sync and async ``get_throughput`` methods call into this one module so
the two paths build the identical request and return the identical offer records.
Without it, each surface would carry its own copy of the can-use / build / parse
logic; the two could drift, and the Rust path could hand back offer records that
differ from the legacy path -- which would show customers a different RU/s number
or autoscale ceiling depending on which surface they used.

"""
from __future__ import annotations

from typing import Any, Mapping, Optional, cast

from . import _base as base
from . import _runtime_constants as runtime_constants
from . import documents
from . import http_constants
from ._backend.base import OP_READ_OFFER, PreparedRequest
from ._constants import _Constants as Constants
from ._helpers._body_wire import serialize_body_to_bytes
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
    mirrored by the Rust route. The Rust binding now exposes an offer entry point (``read_offer`` /
    ``read_offer_async``), so a Rust-backed client's throughput read runs the offer
    query on the driver and returns the same offer records as legacy. Any extra
    kwarg -- which legacy forwards into ``QueryOffers`` -- keeps the call on legacy
    until that knob is explicitly mirrored on the Rust path. This per-call gate is
    migration scaffolding: it shrinks as knobs are mirrored and goes away once the
    surface is fully mirrored.

    :param backend: The client's Rust backend, or ``None`` for core-python.
    :type backend: Any
    :param options: Normalized request options for this call.
    :type options: Mapping[str, Any]
    :param kwargs: The caller's remaining arguments (any unmirrored knob keeps the
        call on legacy).
    :type kwargs: Mapping[str, Any]
    :rtype: bool
    """
    if backend is None:
        return False
    # Rust offer path does not yet mirror socket read timeout or client-side
    # availability strategy shaping used by legacy QueryOffers.
    if options.get(Constants.Kwargs.READ_TIMEOUT) is not None:
        return False
    if options.get(Constants.Kwargs.AVAILABILITY_STRATEGY) is not None:
        return False
    # Extra kwargs -> stay on legacy (Rust can't honor those knobs yet).
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
    prepared_headers = dict(req_headers)
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


def try_read_offer_with_rust_backend(
    *,
    client_connection: Any,
    container_link: str,
    offer_query: Mapping[str, Any],
    options: Mapping[str, Any],
) -> Optional[list[dict[str, Any]]]:
    """Execute ``read_offer`` through Rust, or return None to use legacy fallback.

    Builds the offer request, runs it on the Rust backend, and turns the
    response into the offer records the caller expects. Returns None (so the caller
    falls back to legacy) when there is no backend or the backend declines the call.

    :param client_connection: The connection whose backend runs the request.
    :type client_connection: Any
    :param container_link: The container's link.
    :type container_link: str
    :param offer_query: The offer query spec.
    :type offer_query: Mapping[str, Any]
    :param options: Normalized request options for this call.
    :type options: Mapping[str, Any]
    :rtype: Optional[list[dict[str, Any]]]
    """
    backend = getattr(client_connection, "_backend", None)
    if backend is None:
        return None
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
    prepared = build_read_offer_prepared_request(
        container_link=container_link,
        offer_query=offer_query,
        req_headers=req_headers,
        options=options,
    )
    backend_response = backend.execute(prepared)
    if backend_response is None:
        return None
    parsed = parse_backend_response(
        backend_response,
        client_connection=client_connection,
        response_hook=None,
    )
    return parse_read_offer_payload(cast(Mapping[str, Any], parsed))


async def try_read_offer_with_rust_backend_async(
    *,
    client_connection: Any,
    container_link: str,
    offer_query: Mapping[str, Any],
    options: Mapping[str, Any],
) -> Optional[list[dict[str, Any]]]:
    """Async sibling of ``try_read_offer_with_rust_backend``.

    :param client_connection: The connection whose backend runs the request.
    :type client_connection: Any
    :param container_link: The container's link.
    :type container_link: str
    :param offer_query: The offer query spec.
    :type offer_query: Mapping[str, Any]
    :param options: Normalized request options for this call.
    :type options: Mapping[str, Any]
    :rtype: Optional[list[dict[str, Any]]]
    """
    backend = getattr(client_connection, "_backend", None)
    if backend is None:
        return None
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
    prepared = build_read_offer_prepared_request(
        container_link=container_link,
        offer_query=offer_query,
        req_headers=req_headers,
        options=options,
    )
    backend_response = await backend.execute(prepared)
    if backend_response is None:
        return None
    parsed = parse_backend_response(
        backend_response,
        client_connection=client_connection,
        response_hook=None,
    )
    return parse_read_offer_payload(cast(Mapping[str, Any], parsed))
