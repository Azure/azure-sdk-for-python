# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Reading and replacing a single container's provisioned throughput.

The throughput counterpart to
:class:`~azure.cosmos._helpers.item_helper.ItemHelper`, for containers. The
public proxy methods ``ContainerProxy.get_throughput`` and
``ContainerProxy.replace_throughput`` (sync and async) each gather their
arguments and call one function here; the function does the engine work and
hands back a finished ``ThroughputProperties``.

The container's request-unit budget lives in a separate account-level *offer*
record rather than on the container (see
:mod:`~azure.cosmos._helpers._throughput_setup`), so both operations first read
that offer, and replace then edits the record and writes it back. That
read-modify-write is why the replace functions drive two operations, not one.

Why this module exists (public methods must not know which engine runs): without
it, ``get_throughput`` / ``replace_throughput`` on the proxy would read
``client_connection._backend`` and branch inline -- try the rust engine, else
fall back to the legacy ``QueryOffers`` / ``ReplaceOffer`` calls -- inside the
customer-facing method, putting engine-selection code in the public API surface.
Instead, each function coerces the client's backend selection to a concrete
backend (``coerce_backend`` -> the rust backend or the explicit ``LegacyBackend``,
never ``None``) and drives the work through
:meth:`~azure.cosmos._backend.base.CosmosBackend.run_operation`, so the proxy
method is a thin delegate that names no engine.
"""
from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, Mapping, Optional, Union

from .._backend.contracts import LegacyOperation
from .._backend.legacy import coerce_backend
from .._base import _deserialize_throughput, _replace_throughput
from .._constants import _Constants as Constants
from .._cosmos_responses import CosmosDict
from .._offer_rust_routing import (
    can_use_rust_backend_for_read_offer,
    can_use_rust_backend_for_replace_throughput,
    parse_read_offer_response,
    parse_replace_offer_response,
    prepare_read_offer_request,
    prepare_read_offer_request_async,
    prepare_replace_offer_request,
    prepare_replace_offer_request_async,
)
from ..offer import ThroughputProperties
from ._throughput_setup import gather_rust_call_inputs, offer_query

def get_container_throughput(
    *,
    client_connection: Any,
    container_link: str,
    get_properties: Callable[[], Mapping[str, Any]],
    response_hook: Optional[Callable[[Mapping[str, Any], list[dict[str, Any]]], None]],
    kwargs: Mapping[str, Any],
) -> ThroughputProperties:
    """Read container throughput without exposing backend selection to the public proxy."""
    properties = get_properties()
    query_spec = offer_query(properties["_self"])
    container_rid = properties["_rid"]
    legacy_options: Dict[str, Any] = {Constants.ContainerRID: container_rid}
    selected_backend, rust_options, rust_kwargs = gather_rust_call_inputs(client_connection, container_rid, kwargs)
    backend = coerce_backend(selected_backend)
    offers = backend.run_operation(
        build_prepared=lambda: prepare_read_offer_request(
            client_connection=client_connection,
            container_link=container_link,
            offer_query=query_spec,
            options=rust_options,
        ),
        legacy_operation=LegacyOperation(
            op="read_offer",
            invoke=lambda: list(client_connection.QueryOffers(query_spec, legacy_options, **kwargs)),
        ),
        parse_response=lambda response: parse_read_offer_response(
            response, client_connection=client_connection
        ),
        rust_eligible=can_use_rust_backend_for_read_offer(
            backend=selected_backend,
            options=rust_options,
            kwargs=rust_kwargs,
        ),
    )

    if response_hook:
        response_hook(client_connection.last_response_headers, offers)
    return _deserialize_throughput(throughput=offers)


async def get_container_throughput_async(
    *,
    client_connection: Any,
    container_link: str,
    get_properties: Callable[[], Awaitable[Mapping[str, Any]]],
    response_hook: Optional[Callable[[Mapping[str, Any], list[dict[str, Any]]], None]],
    kwargs: Mapping[str, Any],
) -> ThroughputProperties:
    """Async twin of :func:`get_throughput`."""
    from ..aio._backend.legacy import coerce_async_backend

    properties = await get_properties()
    query_spec = offer_query(properties["_self"])
    container_rid = properties["_rid"]
    legacy_options: Dict[str, Any] = {Constants.ContainerRID: container_rid}
    selected_backend, rust_options, rust_kwargs = gather_rust_call_inputs(client_connection, container_rid, kwargs)
    backend = coerce_async_backend(selected_backend)

    async def run_legacy_read() -> list[dict[str, Any]]:
        """Drain the legacy offer query into a list.

        ``QueryOffers`` yields asynchronously, so the fallback leg has to
        materialise it here to hand back the same list shape the Rust leg
        produces.
        """
        return [
            offer async for offer in client_connection.QueryOffers(
                query_spec, legacy_options, **kwargs
            )
        ]

    offers = await backend.run_operation(
        build_prepared=lambda: prepare_read_offer_request_async(
            client_connection=client_connection,
            container_link=container_link,
            offer_query=query_spec,
            options=rust_options,
        ),
        legacy_operation=LegacyOperation(op="read_offer", invoke=run_legacy_read),
        parse_response=lambda response: parse_read_offer_response(
            response, client_connection=client_connection
        ),
        rust_eligible=can_use_rust_backend_for_read_offer(
            backend=selected_backend,
            options=rust_options,
            kwargs=rust_kwargs,
        ),
    )

    if response_hook:
        response_hook(client_connection.last_response_headers, offers)
    return _deserialize_throughput(throughput=offers)


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
    through the same coerced backend, so the public method never picks an engine.
    """
    properties = get_properties()
    query_spec = offer_query(properties["_self"])
    container_rid = properties["_rid"]
    legacy_options: Dict[str, Any] = {Constants.ContainerRID: container_rid}
    selected_backend, rust_options, rust_kwargs = gather_rust_call_inputs(client_connection, container_rid, kwargs)
    backend = coerce_backend(selected_backend)
    rust_eligible = can_use_rust_backend_for_replace_throughput(
        backend=selected_backend,
        options=rust_options,
        kwargs=rust_kwargs,
    )
    offers = backend.run_operation(
        build_prepared=lambda: prepare_read_offer_request(
            client_connection=client_connection,
            container_link=container_link,
            offer_query=query_spec,
            options=rust_options,
        ),
        legacy_operation=LegacyOperation(
            op="read_offer",
            invoke=lambda: list(client_connection.QueryOffers(query_spec, legacy_options, **kwargs)),
        ),
        parse_response=lambda response: parse_read_offer_response(
            response, client_connection=client_connection
        ),
        rust_eligible=rust_eligible,
    )
    new_offer = offers[0].copy()
    _replace_throughput(throughput=throughput, new_throughput_properties=new_offer)
    updated_offer = backend.run_operation(
        build_prepared=lambda: prepare_replace_offer_request(
                client_connection=client_connection,
                container_link=container_link,
                offer=new_offer,
                options=rust_options,
        ),
        legacy_operation=LegacyOperation(
            op="replace_offer",
            invoke=lambda: client_connection.ReplaceOffer(
                offer_link=new_offer["_self"],
                offer=new_offer,
                **kwargs,
            ),
        ),
        parse_response=lambda response: parse_replace_offer_response(
            response, client_connection=client_connection
        ),
        rust_eligible=rust_eligible,
    )
    if response_hook:
        response_hook(client_connection.last_response_headers, updated_offer)
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
    """Async twin of :func:`replace_throughput`."""
    from ..aio._backend.legacy import coerce_async_backend

    properties = await get_properties()
    query_spec = offer_query(properties["_self"])
    container_rid = properties["_rid"]
    legacy_options: Dict[str, Any] = {Constants.ContainerRID: container_rid}
    selected_backend, rust_options, rust_kwargs = gather_rust_call_inputs(client_connection, container_rid, kwargs)
    backend = coerce_async_backend(selected_backend)
    rust_eligible = can_use_rust_backend_for_replace_throughput(
        backend=selected_backend,
        options=rust_options,
        kwargs=rust_kwargs,
    )

    async def run_legacy_read() -> list[dict[str, Any]]:
        """Drain the legacy offer query into a list.

        ``QueryOffers`` yields asynchronously, so the fallback leg has to
        materialise it here to hand back the same list shape the Rust leg
        produces.
        """
        return [
            offer async for offer in client_connection.QueryOffers(
                query_spec, legacy_options, **kwargs
            )
        ]

    offers = await backend.run_operation(
        build_prepared=lambda: prepare_read_offer_request_async(
            client_connection=client_connection,
            container_link=container_link,
            offer_query=query_spec,
            options=rust_options,
        ),
        legacy_operation=LegacyOperation(op="read_offer", invoke=run_legacy_read),
        parse_response=lambda response: parse_read_offer_response(
            response, client_connection=client_connection
        ),
        rust_eligible=rust_eligible,
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
        build_prepared=lambda: prepare_replace_offer_request_async(
                client_connection=client_connection,
                container_link=container_link,
                offer=new_offer,
                options=rust_options,
        ),
        legacy_operation=LegacyOperation(op="replace_offer", invoke=run_legacy_replace),
        parse_response=lambda response: parse_replace_offer_response(
            response, client_connection=client_connection
        ),
        rust_eligible=rust_eligible,
    )
    if response_hook:
        response_hook(client_connection.last_response_headers, updated_offer)
    return ThroughputProperties(
        offer_throughput=updated_offer["content"]["offerThroughput"],
        properties=updated_offer,
    )
