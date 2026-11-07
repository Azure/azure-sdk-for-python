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
from ..exceptions import CosmosResourceNotFoundError
from ..http_constants import StatusCodes as _StatusCodes
from .._throughput_rust_routing import (
    can_use_rust_backend_for_get_throughput,
    can_use_rust_backend_for_replace_throughput,
    process_get_throughput_response,
    process_replace_throughput_response,
    build_get_throughput_from_connection,
    build_replace_throughput_from_connection,
)
from ..offer import ThroughputProperties
from .._operation_deadline import remaining_timeout, run_with_deadline
from ._throughput_read import prepare_read_kwargs, finish_read, legacy_read_kwargs, read_routing
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
    get_properties: Callable[..., Mapping[str, Any]],
    not_found_message: str,
    response_hook: Optional[Callable[[Mapping[str, Any], list[dict[str, Any]]], None]],
    kwargs: Mapping[str, Any],
) -> ThroughputProperties:
    """Return the provisioned throughput shared by a database's containers."""
    started = time.monotonic()
    kwargs = prepare_read_kwargs(kwargs, response_hook)
    backend, rust_options, rust_kwargs = gather_rust_call_inputs(
        client_connection, None, kwargs
    )
    routing = _read_routing(backend, rust_options, rust_kwargs)
    timeout = rust_options.get("timeout")
    deadline = None if timeout is None else started + float(timeout)
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
                **legacy_read_kwargs(rust_options, rust_kwargs, kwargs, deadline=deadline),
            )
        ),
        process_response=lambda response: process_get_throughput_response(
            response, client_connection=client_connection
        ),
        deadline=deadline,
    )
    remaining_timeout(deadline)
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
    """Return a database's provisioned throughput asynchronously."""
    started = time.monotonic()
    kwargs = prepare_read_kwargs(kwargs, response_hook)
    backend, rust_options, rust_kwargs = gather_rust_call_inputs(
        client_connection, None, kwargs
    )
    routing = _read_routing(backend, rust_options, rust_kwargs)
    timeout = rust_options.get("timeout")
    deadline = None if timeout is None else started + float(timeout)
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
        """
        return [
            offer async for offer in client_connection.QueryOffers(
                query_spec,
                **legacy_read_kwargs(rust_options, rust_kwargs, kwargs, deadline=deadline),
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
    _require_offers(offers, not_found_message)
    return finish_read(offers, client_connection, response_hook)


def replace_database_throughput(
    *,
    client_connection: Any,
    database_link: str,
    get_properties: Callable[..., Mapping[str, Any]],
    throughput: Union[int, ThroughputProperties],
    not_found_message: str,
    kwargs: Mapping[str, Any],
) -> ThroughputProperties:
    """Set a database's shared throughput and return the updated settings."""
    started = time.monotonic()
    validate_replacement_throughput(throughput)
    response_hook = kwargs.get("response_hook")
    kwargs = prepare_read_kwargs(kwargs, response_hook)
    kwargs.pop("response_hook", None)
    backend, rust_options, rust_kwargs = gather_rust_call_inputs(
        client_connection, None, kwargs
    )
    rust_eligible = can_use_rust_backend_for_replace_throughput(
        backend=backend,
        options=rust_options,
        kwargs=rust_kwargs,
    )
    routing = read_routing(
        backend, rust_options, supported=rust_eligible, capability=REPLACE_THROUGHPUT,
    )
    timeout = rust_options.get("timeout")
    deadline = None if timeout is None else started + float(timeout)
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
                **legacy_read_kwargs(rust_options, rust_kwargs, kwargs, deadline=deadline),
            )
        ),
        process_response=lambda response: process_get_throughput_response(
            response, client_connection=client_connection
        ),
        deadline=deadline,
    )
    remaining_timeout(deadline)
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
            **legacy_read_kwargs(rust_options, rust_kwargs, kwargs, deadline=deadline),
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
    kwargs: Mapping[str, Any],
) -> ThroughputProperties:
    """Set a database's shared throughput asynchronously."""
    started = time.monotonic()
    validate_replacement_throughput(throughput)
    response_hook = kwargs.get("response_hook")
    kwargs = prepare_read_kwargs(kwargs, response_hook)
    kwargs.pop("response_hook", None)
    backend, rust_options, rust_kwargs = gather_rust_call_inputs(
        client_connection, None, kwargs
    )
    rust_eligible = can_use_rust_backend_for_replace_throughput(
        backend=backend,
        options=rust_options,
        kwargs=rust_kwargs,
    )
    routing = read_routing(
        backend, rust_options, supported=rust_eligible, capability=REPLACE_THROUGHPUT,
    )
    timeout = rust_options.get("timeout")
    deadline = None if timeout is None else started + float(timeout)
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
        """
        return [
            offer async for offer in client_connection.QueryOffers(
                query_spec,
                **legacy_read_kwargs(rust_options, rust_kwargs, kwargs, deadline=deadline),
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
    _require_offers(offers, not_found_message)
    new_offer = deepcopy(offers[0])
    _replace_throughput(throughput=throughput, new_throughput_properties=new_offer)

    async def run_legacy_replace() -> Any:
        """Replace the offer through the legacy client connection."""
        return await client_connection.ReplaceOffer(
            offer_link=new_offer["_self"],
            offer=new_offer,
            **legacy_read_kwargs(rust_options, rust_kwargs, kwargs, deadline=deadline),
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
