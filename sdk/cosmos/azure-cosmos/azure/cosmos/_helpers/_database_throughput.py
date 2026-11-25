# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Reading and replacing the throughput a database's containers share.

For a database provisioned with shared throughput, these functions read or
replace that shared request-unit budget. They implement ``DatabaseProxy.get_throughput`` and
``DatabaseProxy.replace_throughput`` (sync and async); the container-level
equivalents are in
:mod:`~azure.cosmos._helpers._container_throughput`.

The shape of the work is the same as for a container -- find the account-level
*offer* record for this resource (see
:mod:`~azure.cosmos._helpers._throughput_setup`), then read it, or edit it and
write it back -- but with one difference that matters to a customer: a database
is only required to have an offer if it was created with shared throughput. A
database created without it has no offer at all, so these functions check for
that case explicitly (:func:`_require_offers`) and raise the public
``CosmosResourceNotFoundError`` with a message naming the database, rather than
letting an empty result fail later as something more obscure.

Execution-path selection follows the container module: the Python backend
stored by the client drives the work through
:meth:`~azure.cosmos._backend.cosmos_backend.CosmosBackend.run_operation`, so the public
proxy method stays a thin delegate that names no backend.
"""

from __future__ import annotations

from copy import deepcopy
import time
from typing import Any, Awaitable, Callable, Mapping, Optional, Union

from azure.cosmos._backend.capabilities import (
    GET_DATABASE_THROUGHPUT,
    OperationRouting,
    REPLACE_THROUGHPUT,
)

from .._base import _replace_throughput
from .._cosmos_responses import CosmosDict
from ..exceptions import CosmosResourceNotFoundError
from ..http_constants import StatusCodes as _StatusCodes
from ..offer import ThroughputProperties
from .._operation_deadline import remaining_timeout, run_with_deadline
from ._throughput_rust_routing import (
    can_use_rust_backend_for_get_throughput,
    can_use_rust_replace_throughput,
    process_get_throughput_response,
    process_replace_throughput_response,
    build_get_throughput_from_connection,
    build_replace_throughput_from_connection,
)
from ._throughput_read import prepare_throughput_kwargs, finish_read, legacy_throughput_kwargs, read_routing
from ._throughput_setup import gather_rust_call_inputs, offer_query
from ._throughput_replace import finish_replacement, validate_replacement_throughput


def _read_routing(
    backend: Any,
    options: Mapping[str, Any],
    kwargs: Mapping[str, Any],
) -> OperationRouting:
    return read_routing(
        backend, options,
        supported=can_use_rust_backend_for_get_throughput(
            backend=backend,
            options=options,
            kwargs=kwargs,
        ),
        capability=GET_DATABASE_THROUGHPUT,
    )


def _require_offers(offers: list[dict[str, Any]], not_found_message: str) -> None:
    """Raise the public not-found error when a resource has no throughput offer.

    :param list[dict] offers: Offer-query results to check for emptiness.
    :param str not_found_message: Message included in the public not-found exception.
    :return: None.
    :rtype: None
    """
    if not offers:
        raise CosmosResourceNotFoundError(
            status_code=_StatusCodes.NOT_FOUND,
            message=not_found_message,
        )


def _read_database_offers(
    *,
    client_connection: Any,
    database_link: str,
    get_properties: Callable[..., Mapping[str, Any]],
    backend: Any,
    rust_options: Mapping[str, Any],
    routing: OperationRouting,
    legacy_kwargs: Callable[[], dict[str, Any]],
    deadline: Optional[float],
) -> list[dict[str, Any]]:
    """Resolve database metadata and query its offers within the caller's budget.

    :keyword Any client_connection: Connection supplying default headers and legacy execution.
    :keyword str database_link: Name-based database resource link.
    :keyword callable get_properties: Metadata reader accepting an optional deadline.
    :keyword Any backend: Already-selected execution backend.
    :keyword Mapping[str, Any] rust_options: Internal offer-query options.
    :keyword OperationRouting routing: Validated routing for the offer query.
    :keyword callable legacy_kwargs: Factory supplying legacy options with remaining time.
    :keyword float or None deadline: Shared monotonic workflow deadline.
    :return: Offer records, possibly empty, with the query's response headers.
    :rtype: list[dict[str, Any]]
    """
    remaining_timeout(deadline)
    properties = get_properties() if deadline is None else get_properties(deadline=deadline)
    remaining_timeout(deadline)
    query_spec = offer_query(properties["_self"])
    offers = backend.run_operation(
        build_request=lambda: build_get_throughput_from_connection(
            client_connection=client_connection,
            container_link=database_link,
            offer_query=query_spec,
            options=rust_options,
        ),
        routing=routing,
        legacy_call=lambda: list(
            client_connection.QueryOffers(
                query_spec,
                **legacy_kwargs(),
            )
        ),
        process_response=lambda response: process_get_throughput_response(
            response, client_connection=client_connection
        ),
        deadline=deadline,
    )
    remaining_timeout(deadline)
    return offers


async def _read_database_offers_async(
    *,
    client_connection: Any,
    database_link: str,
    get_properties: Callable[..., Awaitable[Mapping[str, Any]]],
    backend: Any,
    rust_options: Mapping[str, Any],
    routing: OperationRouting,
    legacy_kwargs: Callable[[], dict[str, Any]],
    deadline: Optional[float],
) -> list[dict[str, Any]]:
    """Await database metadata and offer lookup within the caller's budget.

    :keyword Any client_connection: Connection supplying default headers and legacy execution.
    :keyword str database_link: Name-based database resource link.
    :keyword callable get_properties: Async metadata reader accepting an optional deadline.
    :keyword Any backend: Already-selected async execution backend.
    :keyword Mapping[str, Any] rust_options: Internal offer-query options.
    :keyword OperationRouting routing: Validated routing for the offer query.
    :keyword callable legacy_kwargs: Factory supplying legacy options with remaining time.
    :keyword float or None deadline: Shared monotonic workflow deadline.
    :return: Offer records, possibly empty, with the query's response headers on the Rust path.
    :rtype: list[dict[str, Any]]
    """
    remaining_timeout(deadline)
    properties = await run_with_deadline(
        lambda: get_properties() if deadline is None else get_properties(deadline=deadline), deadline,
    )
    remaining_timeout(deadline)
    query_spec = offer_query(properties["_self"])

    async def run_legacy_read() -> list[dict[str, Any]]:
        """Drain the legacy offer query into a list.

        On the legacy path, await iteration of QueryOffers to produce the same
        list result shape expected from the Rust path.

        :return: All offer records produced by the legacy query.
        :rtype: list[dict[str, Any]]
        """
        return [
            offer async for offer in client_connection.QueryOffers(
                query_spec,
                **legacy_kwargs(),
            )
        ]

    offers = await run_with_deadline(
        lambda: backend.run_operation(
            build_request=lambda: build_get_throughput_from_connection(
                client_connection=client_connection,
                container_link=database_link,
                offer_query=query_spec,
                options=rust_options,
            ),
            routing=routing,
            legacy_call=run_legacy_read,
            process_response=lambda response: process_get_throughput_response(
                response, client_connection=client_connection
            ),
            deadline=deadline,
        ),
        deadline,
    )
    remaining_timeout(deadline)
    return offers


def get_database_throughput(
    *,
    client_connection: Any,
    database_link: str,
    get_properties: Callable[..., Mapping[str, Any]],
    not_found_message: str,
    response_hook: Optional[Callable[[Mapping[str, Any], list[dict[str, Any]]], None]],
    kwargs: Mapping[str, Any],
) -> ThroughputProperties:
    """Return the provisioned throughput shared by a database's containers.

    :keyword Any client_connection: Connection supplying the backend, options, and response state.
    :keyword str database_link: Name-based database resource link.
    :keyword callable get_properties: Metadata reader accepting an optional deadline.
    :keyword str not_found_message: Error message when the database has no throughput offer.
    :keyword callable or None response_hook: Synchronous callback receiving headers and copied offer records.
    :keyword Mapping[str, Any] kwargs: Call options used to establish the deadline and prepare requests.
    :return: The database's shared throughput settings.
    :rtype: ~azure.cosmos.ThroughputProperties
    """
    started = time.monotonic()
    kwargs = prepare_throughput_kwargs(kwargs, response_hook)
    backend, rust_options, rust_kwargs = gather_rust_call_inputs(
        client_connection, None, kwargs
    )
    routing = _read_routing(backend, rust_options, rust_kwargs)
    timeout = rust_options.get("timeout")
    deadline = None if timeout is None else started + float(timeout)
    offers = _read_database_offers(
        client_connection=client_connection,
        database_link=database_link,
        get_properties=get_properties,
        backend=backend,
        rust_options=rust_options,
        routing=routing,
        legacy_kwargs=lambda: legacy_throughput_kwargs(rust_options, rust_kwargs, kwargs, deadline=deadline),
        deadline=deadline,
    )
    _require_offers(offers, not_found_message)
    return finish_read(offers, client_connection, response_hook)


async def get_database_throughput_async(
    *,
    client_connection: Any,
    database_link: str,
    get_properties: Callable[..., Awaitable[Mapping[str, Any]]],
    not_found_message: str,
    response_hook: Optional[Callable[[Mapping[str, Any], list[dict[str, Any]]], None]],
    kwargs: Mapping[str, Any],
) -> ThroughputProperties:
    """Return a database's provisioned throughput asynchronously.

    :keyword Any client_connection: Connection supplying the backend, options, and response state.
    :keyword str database_link: Name-based database resource link.
    :keyword callable get_properties: Async metadata reader accepting an optional deadline.
    :keyword str not_found_message: Error message when the database has no throughput offer.
    :keyword callable or None response_hook: Synchronous callback receiving headers and copied offer records.
    :keyword Mapping[str, Any] kwargs: Call options used to establish the deadline and prepare requests.
    :return: The database's shared throughput settings.
    :rtype: ~azure.cosmos.ThroughputProperties
    """
    started = time.monotonic()
    kwargs = prepare_throughput_kwargs(kwargs, response_hook)
    backend, rust_options, rust_kwargs = gather_rust_call_inputs(
        client_connection, None, kwargs
    )
    routing = _read_routing(backend, rust_options, rust_kwargs)
    timeout = rust_options.get("timeout")
    deadline = None if timeout is None else started + float(timeout)
    offers = await _read_database_offers_async(
        client_connection=client_connection,
        database_link=database_link,
        get_properties=get_properties,
        backend=backend,
        rust_options=rust_options,
        routing=routing,
        legacy_kwargs=lambda: legacy_throughput_kwargs(rust_options, rust_kwargs, kwargs, deadline=deadline),
        deadline=deadline,
    )
    _require_offers(offers, not_found_message)
    return finish_read(offers, client_connection, response_hook)


def replace_database_throughput(
    *,
    client_connection: Any,
    database_link: str,
    get_properties: Callable[..., Mapping[str, Any]],
    throughput: Union[int, ThroughputProperties],
    not_found_message: str,
    response_hook: Optional[Callable[[Mapping[str, Any], CosmosDict], None]],
    kwargs: Mapping[str, Any],
) -> ThroughputProperties:
    """Set a database's shared throughput and return the updated settings.

    :keyword Any client_connection: Connection supplying the backend, options, and response state.
    :keyword str database_link: Name-based database resource link.
    :keyword callable get_properties: Metadata reader accepting an optional deadline.
    :keyword int or azure.cosmos.ThroughputProperties throughput: Replacement manual or autoscale settings.
    :keyword str not_found_message: Error message when the database has no throughput offer.
    :keyword callable or None response_hook: Synchronous callback receiving copied headers and replaced offer.
    :keyword Mapping[str, Any] kwargs: Call options used to establish the shared workflow deadline.
    :return: The replaced database throughput settings.
    :rtype: ~azure.cosmos.ThroughputProperties
    """
    started = time.monotonic()
    validate_replacement_throughput(throughput)
    kwargs = prepare_throughput_kwargs(kwargs, response_hook)
    backend, rust_options, rust_kwargs = gather_rust_call_inputs(
        client_connection, None, kwargs
    )
    rust_eligible = can_use_rust_replace_throughput(
        backend=backend,
        options=rust_options,
        kwargs=rust_kwargs,
    )
    routing = read_routing(
        backend, rust_options, supported=rust_eligible, capability=REPLACE_THROUGHPUT,
    )
    timeout = rust_options.get("timeout")
    deadline = None if timeout is None else started + float(timeout)
    offers = _read_database_offers(
        client_connection=client_connection,
        database_link=database_link,
        get_properties=get_properties,
        backend=backend,
        rust_options=rust_options,
        routing=routing,
        legacy_kwargs=lambda: legacy_throughput_kwargs(rust_options, rust_kwargs, kwargs, deadline=deadline),
        deadline=deadline,
    )
    _require_offers(offers, not_found_message)
    new_offer = deepcopy(offers[0])
    _replace_throughput(throughput=throughput, new_throughput_properties=new_offer)
    updated_offer = backend.run_operation(
        build_request=lambda: build_replace_throughput_from_connection(
            client_connection=client_connection,
            container_link=database_link,
            offer=new_offer,
            options=rust_options,
        ),
        routing=OperationRouting(
            "replace_throughput", routing.supported, capability=REPLACE_THROUGHPUT
        ),
        legacy_call=lambda: client_connection.ReplaceOffer(
            offer_link=new_offer["_self"],
            offer=new_offer,
            **legacy_throughput_kwargs(rust_options, rust_kwargs, kwargs, deadline=deadline),
        ),
        process_response=lambda response: process_replace_throughput_response(
            response, client_connection=client_connection
        ),
        deadline=deadline,
    )
    remaining_timeout(deadline)
    return finish_replacement(updated_offer, client_connection, response_hook)


async def replace_database_throughput_async(
    *,
    client_connection: Any,
    database_link: str,
    get_properties: Callable[..., Awaitable[Mapping[str, Any]]],
    throughput: Union[int, ThroughputProperties],
    not_found_message: str,
    response_hook: Optional[Callable[[Mapping[str, Any], CosmosDict], None]],
    kwargs: Mapping[str, Any],
) -> ThroughputProperties:
    """Set a database's shared throughput asynchronously.

    :keyword Any client_connection: Connection supplying the backend, options, and response state.
    :keyword str database_link: Name-based database resource link.
    :keyword callable get_properties: Async metadata reader accepting an optional deadline.
    :keyword int or azure.cosmos.ThroughputProperties throughput: Replacement manual or autoscale settings.
    :keyword str not_found_message: Error message when the database has no throughput offer.
    :keyword callable or None response_hook: Synchronous callback receiving copied headers and replaced offer.
    :keyword Mapping[str, Any] kwargs: Call options used to establish the shared workflow deadline.
    :return: The replaced database throughput settings.
    :rtype: ~azure.cosmos.ThroughputProperties
    """
    started = time.monotonic()
    validate_replacement_throughput(throughput)
    kwargs = prepare_throughput_kwargs(kwargs, response_hook)
    backend, rust_options, rust_kwargs = gather_rust_call_inputs(
        client_connection, None, kwargs
    )
    rust_eligible = can_use_rust_replace_throughput(
        backend=backend,
        options=rust_options,
        kwargs=rust_kwargs,
    )
    routing = read_routing(
        backend, rust_options, supported=rust_eligible, capability=REPLACE_THROUGHPUT,
    )
    timeout = rust_options.get("timeout")
    deadline = None if timeout is None else started + float(timeout)
    offers = await _read_database_offers_async(
        client_connection=client_connection,
        database_link=database_link,
        get_properties=get_properties,
        backend=backend,
        rust_options=rust_options,
        routing=routing,
        legacy_kwargs=lambda: legacy_throughput_kwargs(rust_options, rust_kwargs, kwargs, deadline=deadline),
        deadline=deadline,
    )
    _require_offers(offers, not_found_message)
    new_offer = deepcopy(offers[0])
    _replace_throughput(throughput=throughput, new_throughput_properties=new_offer)

    async def run_legacy_replace() -> Any:
        """Replace the offer through the legacy client connection.

        :return: The replaced offer properties.
        :rtype: ~azure.cosmos.CosmosDict
        """
        return await client_connection.ReplaceOffer(
            offer_link=new_offer["_self"],
            offer=new_offer,
            **legacy_throughput_kwargs(rust_options, rust_kwargs, kwargs, deadline=deadline),
        )

    updated_offer = await run_with_deadline(
        lambda: backend.run_operation(
            build_request=lambda: build_replace_throughput_from_connection(
                client_connection=client_connection,
                container_link=database_link,
                offer=new_offer,
                options=rust_options,
            ),
            routing=OperationRouting(
                "replace_throughput", routing.supported, capability=REPLACE_THROUGHPUT
            ),
            legacy_call=run_legacy_replace,
            process_response=lambda response: process_replace_throughput_response(
                response, client_connection=client_connection
            ),
            deadline=deadline,
        ),
        deadline,
    )
    remaining_timeout(deadline)
    return finish_replacement(updated_offer, client_connection, response_hook)
