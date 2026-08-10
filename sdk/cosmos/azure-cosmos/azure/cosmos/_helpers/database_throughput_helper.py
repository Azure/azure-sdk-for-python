# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Reading and replacing the throughput a database's containers share.

A database can provision request units at the database level, and every
container inside it then draws on that one shared budget instead of holding its
own. These functions back ``DatabaseProxy.get_throughput`` and
``DatabaseProxy.replace_throughput`` (sync and async); the container-level
equivalents are in
:mod:`~azure.cosmos._helpers.container_throughput_helper`.

The shape of the work is the same as for a container -- find the account-level
*offer* record for this resource (see
:mod:`~azure.cosmos._helpers._throughput_setup`), then read it, or edit it and
write it back -- but with one difference that matters to a customer: a database
is only required to have an offer if it was created with shared throughput. A
database created without it has no offer at all, so these functions check for
that case explicitly (:func:`_require_offers`) and raise the public
``CosmosResourceNotFoundError`` with a message naming the database, rather than
letting an empty result fail later as something more obscure.

Engine selection is handled exactly as in the container module: the client's
backend selection is coerced to a concrete backend and the work is driven
through :meth:`~azure.cosmos._backend.base.CosmosBackend.run_operation`, so the
public proxy method stays a thin delegate that names no engine.
"""
from __future__ import annotations

from typing import Any, Awaitable, Callable, Mapping, Optional, Union

from .._backend.contracts import LegacyOperation
from .._backend.legacy import coerce_backend
from .._base import _deserialize_throughput, _replace_throughput
from ..exceptions import CosmosResourceNotFoundError
from ..http_constants import StatusCodes as _StatusCodes
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

def _require_offers(offers: list[dict[str, Any]], not_found_message: str) -> None:
    """Raise the public not-found error when a resource has no throughput offer."""
    if not offers:
        raise CosmosResourceNotFoundError(
            status_code=_StatusCodes.NOT_FOUND,
            message=not_found_message,
        )


def get_database_throughput(
    *,
    client_connection: Any,
    database_link: str,
    get_properties: Callable[[], Mapping[str, Any]],
    not_found_message: str,
    response_hook: Optional[Callable[[Mapping[str, Any], list[dict[str, Any]]], None]],
    kwargs: Mapping[str, Any],
) -> ThroughputProperties:
    """Return the provisioned throughput shared by a database's containers."""
    properties = get_properties()
    query_spec = offer_query(properties["_self"])
    selected_backend, rust_options, rust_kwargs = gather_rust_call_inputs(client_connection, None, kwargs)
    backend = coerce_backend(selected_backend)
    offers = backend.run_operation(
        build_prepared=lambda: prepare_read_offer_request(
            client_connection=client_connection,
            container_link=database_link,
            offer_query=query_spec,
            options=rust_options,
        ),
        legacy_operation=LegacyOperation(
            op="read_offer",
            invoke=lambda: list(client_connection.QueryOffers(query_spec, **kwargs)),
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
    _require_offers(offers, not_found_message)

    if response_hook:
        response_hook(client_connection.last_response_headers, offers)
    return _deserialize_throughput(throughput=offers)


async def get_database_throughput_async(
    *,
    client_connection: Any,
    database_link: str,
    get_properties: Callable[[], Awaitable[Mapping[str, Any]]],
    not_found_message: str,
    response_hook: Optional[Callable[[Mapping[str, Any], list[dict[str, Any]]], None]],
    kwargs: Mapping[str, Any],
) -> ThroughputProperties:
    """Return a database's provisioned throughput asynchronously."""
    # Import here to avoid a circular import between the sync and async packages.
    from ..aio._backend.legacy import coerce_async_backend

    properties = await get_properties()
    query_spec = offer_query(properties["_self"])
    selected_backend, rust_options, rust_kwargs = gather_rust_call_inputs(client_connection, None, kwargs)
    backend = coerce_async_backend(selected_backend)

    async def run_legacy_read() -> list[dict[str, Any]]:
        """Drain the legacy offer query into a list.

        ``QueryOffers`` yields asynchronously, so the fallback leg has to
        materialise it here to hand back the same list shape the Rust leg
        produces.
        """
        return [
            offer async for offer in client_connection.QueryOffers(query_spec, **kwargs)
        ]

    offers = await backend.run_operation(
        build_prepared=lambda: prepare_read_offer_request_async(
            client_connection=client_connection,
            container_link=database_link,
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
    _require_offers(offers, not_found_message)

    if response_hook:
        response_hook(client_connection.last_response_headers, offers)
    return _deserialize_throughput(throughput=offers)


def replace_database_throughput(
    *,
    client_connection: Any,
    database_link: str,
    get_properties: Callable[[], Mapping[str, Any]],
    throughput: Union[int, ThroughputProperties],
    not_found_message: str,
    kwargs: Mapping[str, Any],
    read_kwargs: Optional[Mapping[str, Any]] = None,
) -> ThroughputProperties:
    """Set a database's shared throughput and return the updated settings."""
    properties = get_properties()
    query_spec = offer_query(properties["_self"])
    legacy_read_kwargs = dict(kwargs if read_kwargs is None else read_kwargs)
    selected_backend, rust_options, rust_kwargs = gather_rust_call_inputs(client_connection, None, kwargs)
    backend = coerce_backend(selected_backend)
    rust_eligible = can_use_rust_backend_for_replace_throughput(
        backend=selected_backend,
        options=rust_options,
        kwargs=rust_kwargs,
    )
    offers = backend.run_operation(
        build_prepared=lambda: prepare_read_offer_request(
            client_connection=client_connection,
            container_link=database_link,
            offer_query=query_spec,
            options=rust_options,
        ),
        legacy_operation=LegacyOperation(
            op="read_offer",
            invoke=lambda: list(client_connection.QueryOffers(query_spec, **legacy_read_kwargs)),
        ),
        parse_response=lambda response: parse_read_offer_response(
            response, client_connection=client_connection
        ),
        rust_eligible=rust_eligible,
    )
    _require_offers(offers, not_found_message)
    new_offer = offers[0].copy()
    _replace_throughput(throughput=throughput, new_throughput_properties=new_offer)
    updated_offer = backend.run_operation(
        build_prepared=lambda: prepare_replace_offer_request(
            client_connection=client_connection,
            container_link=database_link,
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
    return ThroughputProperties(
        offer_throughput=updated_offer["content"]["offerThroughput"],
        properties=updated_offer,
    )


async def replace_database_throughput_async(
    *,
    client_connection: Any,
    database_link: str,
    get_properties: Callable[[], Awaitable[Mapping[str, Any]]],
    throughput: Union[int, ThroughputProperties],
    not_found_message: str,
    kwargs: Mapping[str, Any],
) -> ThroughputProperties:
    """Set a database's shared throughput asynchronously."""
    # Deferred, not module-level: ``azure.cosmos.aio`` reaches back into
    # ``azure.cosmos`` for ``DatabaseAccount``, so importing it at the top of
    # this module closes a cycle and breaks plain ``import azure.cosmos``.
    from ..aio._backend.legacy import coerce_async_backend

    properties = await get_properties()
    query_spec = offer_query(properties["_self"])
    selected_backend, rust_options, rust_kwargs = gather_rust_call_inputs(client_connection, None, kwargs)
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
            offer async for offer in client_connection.QueryOffers(query_spec, **kwargs)
        ]

    offers = await backend.run_operation(
        build_prepared=lambda: prepare_read_offer_request_async(
            client_connection=client_connection,
            container_link=database_link,
            offer_query=query_spec,
            options=rust_options,
        ),
        legacy_operation=LegacyOperation(op="read_offer", invoke=run_legacy_read),
        parse_response=lambda response: parse_read_offer_response(
            response, client_connection=client_connection
        ),
        rust_eligible=rust_eligible,
    )
    _require_offers(offers, not_found_message)
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
            container_link=database_link,
            offer=new_offer,
            options=rust_options,
        ),
        legacy_operation=LegacyOperation(op="replace_offer", invoke=run_legacy_replace),
        parse_response=lambda response: parse_replace_offer_response(
            response, client_connection=client_connection
        ),
        rust_eligible=rust_eligible,
    )
    return ThroughputProperties(
        offer_throughput=updated_offer["content"]["offerThroughput"],
        properties=updated_offer,
    )
