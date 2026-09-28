# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Reading and replacing a single container's provisioned throughput.

The throughput counterpart to
:class:`~azure.cosmos._helpers._item_operations.ItemHelper`, for containers. The
public proxy methods ``ContainerProxy.get_throughput`` and
``ContainerProxy.replace_throughput`` (sync and async) each gather their
arguments and call one function here; it uses the selected Python backend and
hands back a finished ``ThroughputProperties``.

The container's request-unit budget lives in a separate account-level *offer*
record rather than on the container (see
:mod:`~azure.cosmos._helpers._throughput_setup`), so both operations first read
that offer, and replace then edits the record and writes it back. That
read-modify-write is why the replace functions drive two operations, not one.

These helpers keep migration-path decisions out of public proxy methods.
Each uses the Python backend already stored by the client and supplies
OperationRouting to run_operation. Reads reject unsupported Rust inputs before
metadata requests. An empty lookup or a container-recreation error can refresh
metadata once and repeat the read on the same Rust path if the container changed.
Replacement retains its separate migration policy.
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, Mapping, Optional, Union

from azure.cosmos._backend.capabilities import GET_CONTAINER_THROUGHPUT, OperationRouting, REPLACE_THROUGHPUT
from azure.cosmos._backend.constants import is_rust_backend

from .._base import _replace_throughput
from .. import exceptions
from ..http_constants import HttpHeaders, StatusCodes, SubStatusCodes
from .._constants import _Constants as Constants
from .._cosmos_responses import CosmosDict
from .._offer_rust_routing import (
    offer_response_headers,
    can_use_rust_backend_for_read_offer,
    can_use_rust_backend_for_replace_throughput,
    process_read_offer_response,
    process_replace_offer_response,
    build_read_offer_from_connection,
    build_replace_offer_from_connection,
)
from ..offer import ThroughputProperties
from ._throughput_setup import gather_rust_call_inputs, offer_query
from ._throughput_read import prepare_read_kwargs, finish_read, legacy_read_kwargs, read_routing


def _finish_container_read(
    offers: list[dict[str, Any]],
    client_connection: Any,
    properties: Mapping[str, Any],
    response_hook: Optional[Callable[[Mapping[str, Any], list[dict[str, Any]]], None]],
) -> ThroughputProperties:
    if not offers:
        raise exceptions.CosmosResourceNotFoundError(
            status_code=StatusCodes.NOT_FOUND,
            message="Could not find ThroughputProperties for container " + properties["_self"],
            response=exceptions._InternalCosmosException(
                status_code=StatusCodes.NOT_FOUND,
                headers={HttpHeaders.SubStatus: SubStatusCodes.THROUGHPUT_OFFER_NOT_FOUND},
            ),
        )
    return finish_read(offers, client_connection, response_hook)


def get_container_throughput(
    *,
    client_connection: Any,
    container_link: str,
    get_properties: Callable[[], Mapping[str, Any]],
    refresh_properties: Callable[[], Mapping[str, Any]],
    response_hook: Optional[Callable[[Mapping[str, Any], list[dict[str, Any]]], None]],
    kwargs: Mapping[str, Any],
) -> ThroughputProperties:
    """Read container throughput without exposing backend selection to the public proxy."""
    kwargs = prepare_read_kwargs(kwargs, response_hook)
    backend, rust_options, rust_kwargs = gather_rust_call_inputs(
        client_connection, None, kwargs
    )
    routing = read_routing(
        backend, rust_options,
        supported=can_use_rust_backend_for_read_offer(
            backend=backend, options=rust_options, kwargs=rust_kwargs,
        ),
        capability=GET_CONTAINER_THROUGHPUT,
    )
    legacy_kwargs = legacy_read_kwargs(rust_options, rust_kwargs, kwargs)
    properties = get_properties()
    offers: list[dict[str, Any]] = []
    for attempt in range(2):
        query_spec = offer_query(properties["_self"])
        rust_options[Constants.ContainerRID] = properties["_rid"]
        recovery_error = None
        try:
            offers = backend.run_operation(
                build_request=lambda: build_read_offer_from_connection(
                    client_connection=client_connection,
                    container_link=container_link,
                    offer_query=query_spec,
                    options=rust_options,
                ),
                routing=routing,
                legacy_call=lambda: list(client_connection.QueryOffers(query_spec, **legacy_kwargs)),
                process_response=lambda response: process_read_offer_response(
                    response, client_connection=client_connection
                ),
            )
        except exceptions.CosmosHttpResponseError as error:
            if attempt or not is_rust_backend(backend) or not exceptions._container_recreate_exception(error):
                raise
            recovery_error = error
        else:
            if offers or attempt or not is_rust_backend(backend):
                break
        # An account-level offer query cannot refresh the owning container.
        refreshed = refresh_properties()
        if refreshed["_rid"] == properties["_rid"]:
            if recovery_error is not None:
                raise recovery_error
            break
        properties = refreshed

    return _finish_container_read(offers, client_connection, properties, response_hook)


async def get_container_throughput_async(
    *,
    client_connection: Any,
    container_link: str,
    get_properties: Callable[[], Awaitable[Mapping[str, Any]]],
    refresh_properties: Callable[[], Awaitable[Mapping[str, Any]]],
    response_hook: Optional[Callable[[Mapping[str, Any], list[dict[str, Any]]], None]],
    kwargs: Mapping[str, Any],
) -> ThroughputProperties:
    """Read container throughput, awaiting metadata and Python backend execution."""
    kwargs = prepare_read_kwargs(kwargs, response_hook)
    backend, rust_options, rust_kwargs = gather_rust_call_inputs(
        client_connection, None, kwargs
    )
    routing = read_routing(
        backend, rust_options,
        supported=can_use_rust_backend_for_read_offer(
            backend=backend, options=rust_options, kwargs=rust_kwargs,
        ),
        capability=GET_CONTAINER_THROUGHPUT,
    )
    legacy_kwargs = legacy_read_kwargs(rust_options, rust_kwargs, kwargs)
    properties = await get_properties()
    offers: list[dict[str, Any]] = []
    for attempt in range(2):
        query_spec = offer_query(properties["_self"])
        rust_options[Constants.ContainerRID] = properties["_rid"]

        async def run_legacy_read() -> list[dict[str, Any]]:
            return [offer async for offer in client_connection.QueryOffers(query_spec, **legacy_kwargs)]

        recovery_error = None
        try:
            offers = await backend.run_operation(
                build_request=lambda: build_read_offer_from_connection(
                    client_connection=client_connection,
                    container_link=container_link,
                    offer_query=query_spec,
                    options=rust_options,
                ),
                routing=routing,
                legacy_call=run_legacy_read,
                process_response=lambda response: process_read_offer_response(
                    response, client_connection=client_connection
                ),
            )
        except exceptions.CosmosHttpResponseError as error:
            if attempt or not is_rust_backend(backend) or not exceptions._container_recreate_exception(error):
                raise
            recovery_error = error
        else:
            if offers or attempt or not is_rust_backend(backend):
                break
        refreshed = await refresh_properties()
        if refreshed["_rid"] == properties["_rid"]:
            if recovery_error is not None:
                raise recovery_error
            break
        properties = refreshed

    return _finish_container_read(offers, client_connection, properties, response_hook)


def replace_container_throughput(
    *,
    client_connection: Any,
    container_link: str,
    get_properties: Callable[[], Mapping[str, Any]],
    throughput: Union[int, ThroughputProperties],
    response_hook: Optional[Callable[[Mapping[str, Any], CosmosDict], None]],
    kwargs: Mapping[str, Any],
) -> ThroughputProperties:
    """Replace container throughput without backend logic in the public proxy.

    Read-modify-write: run one ``read_offer`` to get the current offer, apply the
    new RU/s to a copy, then run one ``replace_offer`` to write it back. Both go
    through the same selected Python backend; the public method does not select it.
    """
    properties = get_properties()
    query_spec = offer_query(properties["_self"])
    container_rid = properties["_rid"]
    legacy_options: Dict[str, Any] = {Constants.ContainerRID: container_rid}
    selected_backend, rust_options, rust_kwargs = gather_rust_call_inputs(
        client_connection, container_rid, kwargs
    )
    backend = selected_backend
    rust_eligible = can_use_rust_backend_for_replace_throughput(
        backend=selected_backend,
        options=rust_options,
        kwargs=rust_kwargs,
    )
    offers = backend.run_operation(
        build_request=lambda: build_read_offer_from_connection(
            client_connection=client_connection,
            container_link=container_link,
            offer_query=query_spec,
            options=rust_options,
        ),
        routing=OperationRouting(
            "read_offer", rust_eligible, capability=REPLACE_THROUGHPUT
        ),
        legacy_call=lambda: list(
            client_connection.QueryOffers(query_spec, legacy_options, **kwargs)
        ),
        process_response=lambda response: process_read_offer_response(
            response, client_connection=client_connection
        ),
    )
    new_offer = offers[0].copy()
    _replace_throughput(throughput=throughput, new_throughput_properties=new_offer)
    updated_offer = backend.run_operation(
        build_request=lambda: build_replace_offer_from_connection(
            client_connection=client_connection,
            container_link=container_link,
            offer=new_offer,
            options=rust_options,
        ),
        routing=OperationRouting(
            "replace_offer", rust_eligible, capability=REPLACE_THROUGHPUT
        ),
        legacy_call=lambda: client_connection.ReplaceOffer(
            offer_link=new_offer["_self"],
            offer=new_offer,
            **kwargs,
        ),
        process_response=lambda response: process_replace_offer_response(
            response, client_connection=client_connection
        ),
    )
    if response_hook:
        response_hook(offer_response_headers(updated_offer, client_connection), updated_offer)
    return ThroughputProperties(
        offer_throughput=updated_offer["content"]["offerThroughput"],
        properties=updated_offer,
    )


async def replace_container_throughput_async(
    *,
    client_connection: Any,
    container_link: str,
    get_properties: Callable[[], Awaitable[Mapping[str, Any]]],
    throughput: Union[int, ThroughputProperties],
    response_hook: Optional[Callable[[Mapping[str, Any], CosmosDict], None]],
    kwargs: Mapping[str, Any],
) -> ThroughputProperties:
    """Replace throughput, awaiting the offer read and replacement on the same path."""
    properties = await get_properties()
    query_spec = offer_query(properties["_self"])
    container_rid = properties["_rid"]
    legacy_options: Dict[str, Any] = {Constants.ContainerRID: container_rid}
    selected_backend, rust_options, rust_kwargs = gather_rust_call_inputs(
        client_connection, container_rid, kwargs
    )
    backend = selected_backend
    rust_eligible = can_use_rust_backend_for_replace_throughput(
        backend=selected_backend,
        options=rust_options,
        kwargs=rust_kwargs,
    )

    async def run_legacy_read() -> list[dict[str, Any]]:
        """Drain the legacy offer query into a list.

        On the legacy path, await iteration of QueryOffers to produce the same
        list result shape expected from the Rust path.
        """
        return [
            offer
            async for offer in client_connection.QueryOffers(
                query_spec, legacy_options, **kwargs
            )
        ]

    offers = await backend.run_operation(
        build_request=lambda: build_read_offer_from_connection(
            client_connection=client_connection,
            container_link=container_link,
            offer_query=query_spec,
            options=rust_options,
        ),
        routing=OperationRouting(
            "read_offer", rust_eligible, capability=REPLACE_THROUGHPUT
        ),
        legacy_call=run_legacy_read,
        process_response=lambda response: process_read_offer_response(
            response, client_connection=client_connection
        ),
    )
    new_offer = offers[0].copy()
    _replace_throughput(throughput=throughput, new_throughput_properties=new_offer)

    async def run_legacy_replace() -> Any:
        """Replace the offer through the legacy client connection."""
        return await client_connection.ReplaceOffer(
            offer_link=new_offer["_self"],
            offer=new_offer,
            **kwargs,
        )

    updated_offer = await backend.run_operation(
        build_request=lambda: build_replace_offer_from_connection(
            client_connection=client_connection,
            container_link=container_link,
            offer=new_offer,
            options=rust_options,
        ),
        routing=OperationRouting(
            "replace_offer", rust_eligible, capability=REPLACE_THROUGHPUT
        ),
        legacy_call=run_legacy_replace,
        process_response=lambda response: process_replace_offer_response(
            response, client_connection=client_connection
        ),
    )
    if response_hook:
        response_hook(offer_response_headers(updated_offer, client_connection), updated_offer)
    return ThroughputProperties(
        offer_throughput=updated_offer["content"]["offerThroughput"],
        properties=updated_offer,
    )
