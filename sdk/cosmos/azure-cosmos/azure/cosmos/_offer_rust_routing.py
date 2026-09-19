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
"""Offer compatibility routing and response conversion; builders are pure."""

from __future__ import annotations

from typing import Any, Mapping, cast
from copy import deepcopy
from azure.core.utils import CaseInsensitiveDict

from ._backend.constants import is_rust_backend
from ._backend.contracts import PreparedRequest
from ._constants import _Constants as Constants
from ._cosmos_responses import CosmosDict, CosmosList
from ._helpers._request_settings import overrides_driver_owned_header
from ._helpers._request_offer import build_read_offer_request, build_replace_offer_request
from ._helpers._response_parse import process_backend_response


def can_use_rust_backend_for_read_offer(*, backend: Any, options: Mapping[str, Any], kwargs: Mapping[str, Any]) -> bool:
    """Keep unsupported transport options and customer overrides on legacy."""
    if not is_rust_backend(backend):
        return False
    if options.get(Constants.Kwargs.READ_TIMEOUT) is not None:
        return False
    if options.get(Constants.Kwargs.AVAILABILITY_STRATEGY) is not None:
        return False
    if overrides_driver_owned_header(options):
        return False
    return len(kwargs) == 0


def build_read_offer_from_connection(
    *,
    client_connection: Any,
    container_link: str,
    offer_query: Mapping[str, Any],
    options: Mapping[str, Any],
) -> PreparedRequest:
    """Adapt connection defaults to the value-only offer-query builder."""
    return build_read_offer_request(
        resource_link=container_link,
        offer_query=offer_query,
        request_options=options,
        default_headers=client_connection.default_headers,
    )




def process_read_offer_response(backend_response: Any, *, client_connection: Any) -> list[dict[str, Any]]:
    """Parse a backend response into the legacy offer-list shape."""
    parsed = process_backend_response(
        backend_response,
        client_connection=client_connection,
        response_hook=None,
    )
    return CosmosList(
        parse_read_offer_payload(cast(Mapping[str, Any], parsed)),
        response_headers=parsed.get_response_headers(),
    )


def offer_response_headers(result: Any, client_connection: Any) -> CaseInsensitiveDict:
    """Use operation-owned headers; retain the legacy plain-list fallback."""
    if isinstance(result, (CosmosDict, CosmosList)):
        return deepcopy(result.get_response_headers())
    return CaseInsensitiveDict(deepcopy(client_connection.last_response_headers))


def parse_read_offer_payload(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return offer records consumed by the shared throughput deserializer."""
    raw_offers = payload.get("Offers")
    if not isinstance(raw_offers, list):
        raise ValueError("read_offer Rust payload must include a list field 'Offers'.")
    offers: list[dict[str, Any]] = []
    for index, offer in enumerate(raw_offers):
        if not isinstance(offer, Mapping):
            raise ValueError("read_offer Rust payload entry at index {} must be an object.".format(index))
        offers.append(dict(offer))
    return offers


def can_use_rust_backend_for_replace_throughput(
    *,
    backend: Any,
    options: Mapping[str, Any],
    kwargs: Mapping[str, Any],
) -> bool:
    """Keep both steps of the read-modify-write on the same eligible backend."""
    return can_use_rust_backend_for_read_offer(backend=backend, options=options, kwargs=kwargs)


def build_replace_offer_from_connection(
    *,
    client_connection: Any,
    container_link: str,
    offer: Mapping[str, Any],
    options: Mapping[str, Any],
) -> PreparedRequest:
    """Adapt connection defaults to the value-only offer-replacement builder."""
    return build_replace_offer_request(
        resource_link=container_link,
        offer_body=offer,
        request_options=options,
        default_headers=client_connection.default_headers,
    )




def process_replace_offer_response(backend_response: Any, *, client_connection: Any) -> Any:
    """Parse an offer replacement response."""
    return process_backend_response(
        backend_response,
        client_connection=client_connection,
        response_hook=None,
    )
