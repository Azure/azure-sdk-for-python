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
metadata requests. Reads and replacements share an offer lookup that can
refresh metadata once after an empty result or a container-recreation error,
then repeat the lookup on the same Rust path if the container changed. This
recovery never replays a write. One deadline covers the complete call.
Explicit legacy selection exists only for migration comparisons.
"""

from __future__ import annotations

from copy import deepcopy
from functools import partial
import time
from typing import Any, Awaitable, Callable, Mapping, Optional, Union

from azure.cosmos._backend.capabilities import GET_CONTAINER_THROUGHPUT, OperationRouting, REPLACE_THROUGHPUT
from azure.cosmos._backend.constants import is_rust_backend

from .._base import _replace_throughput
from .. import exceptions
from ..exceptions import _container_recreate_exception
from ..http_constants import HttpHeaders, StatusCodes, SubStatusCodes
from .._constants import _Constants as Constants
from .._cosmos_responses import CosmosDict
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
from ._throughput_setup import gather_rust_call_inputs, offer_query
from ._throughput_read import prepare_read_kwargs, finish_read, legacy_read_kwargs, read_routing
from ._throughput_replace import finish_replacement, validate_replacement_throughput


def _require_container_offers(
    offers: list[dict[str, Any]], properties: Mapping[str, Any],
) -> None:
    if not offers:
        raise exceptions.CosmosResourceNotFoundError(
            status_code=StatusCodes.NOT_FOUND,
            message="Could not find ThroughputProperties for container " + properties["_self"],
            response=exceptions._InternalCosmosException(
                status_code=StatusCodes.NOT_FOUND,
                headers={HttpHeaders.SubStatus: SubStatusCodes.THROUGHPUT_OFFER_NOT_FOUND},
            ),
        )


def _read_container_offers(
    *,
    client_connection: Any,
    container_link: str,
    backend: Any,
    rust_options: dict[str, Any],
    routing: OperationRouting,
    get_properties: Callable[..., Mapping[str, Any]],
    refresh_properties: Callable[..., Mapping[str, Any]],
    legacy_kwargs: Callable[[], dict[str, Any]],
    deadline: Optional[float],
) -> list[dict[str, Any]]:
    """Resolve an offer, refreshing a stale identity once before any write.

    :keyword client_connection: Connection retaining response state.
    :keyword container_link: Name-based container address.
    :keyword backend: Already-selected execution backend.
    :keyword rust_options: Owned request options updated with the current container RID.
    :keyword routing: Validated offer-query routing.
    :keyword get_properties: Read cached or uncached metadata within the deadline.
    :keyword refresh_properties: Reload metadata after a stale-identity signal.
    :keyword legacy_kwargs: Prepare legacy comparison options with remaining time.
    :keyword deadline: Absolute monotonic deadline, or None.
    :returns: Nonempty offers for the current container.
    :rtype: list[dict[str, Any]]
    """
    remaining_timeout(deadline)
    properties = get_properties() if deadline is None else get_properties(deadline=deadline)
    remaining_timeout(deadline)
    offers: list[dict[str, Any]] = []
    for attempt in range(2):
        query_spec = offer_query(properties["_self"])
        rust_options[Constants.ContainerRID] = properties["_rid"]
        recovery_error = None
        try:
            offers = backend.run_operation(
                build_request=lambda query_spec=query_spec: build_get_throughput_from_connection(
                    client_connection=client_connection,
                    container_link=container_link,
                    offer_query=query_spec,
                    options=rust_options,
                ),
                routing=routing,
                legacy_call=lambda query_spec=query_spec: list(client_connection.QueryOffers(
                    query_spec, **legacy_kwargs(),
                )),
                process_response=lambda response: process_get_throughput_response(
                    response, client_connection=client_connection
                ),
                deadline=deadline,
            )
        except exceptions.CosmosHttpResponseError as error:
            if attempt or not is_rust_backend(backend) or not _container_recreate_exception(error):
                raise
            recovery_error = error
        else:
            remaining_timeout(deadline)
            if offers or attempt or not is_rust_backend(backend):
                break
        # An account-level offer query cannot refresh the owning container.
        remaining_timeout(deadline)
        refreshed = refresh_properties() if deadline is None else refresh_properties(deadline=deadline)
        remaining_timeout(deadline)
        if refreshed["_rid"] == properties["_rid"]:
            if recovery_error is not None:
                raise recovery_error
            break
        properties = refreshed

    _require_container_offers(offers, properties)
    return offers


async def _read_container_offers_async(
    *,
    client_connection: Any,
    container_link: str,
    backend: Any,
    rust_options: dict[str, Any],
    routing: OperationRouting,
    get_properties: Callable[..., Awaitable[Mapping[str, Any]]],
    refresh_properties: Callable[..., Awaitable[Mapping[str, Any]]],
    legacy_kwargs: Callable[[], dict[str, Any]],
    deadline: Optional[float],
) -> list[dict[str, Any]]:
    """Resolve the current offer asynchronously, without replaying a write.

    :keyword client_connection: Connection retaining response state.
    :keyword container_link: Name-based container address.
    :keyword backend: Already-selected asynchronous backend.
    :keyword rust_options: Owned request options updated with the current container RID.
    :keyword routing: Validated offer-query routing.
    :keyword get_properties: Await cached or uncached metadata within the deadline.
    :keyword refresh_properties: Await fresh metadata after a stale-identity signal.
    :keyword legacy_kwargs: Prepare legacy comparison options with remaining time.
    :keyword deadline: Absolute monotonic deadline, or None.
    :returns: Nonempty offers for the current container.
    :rtype: list[dict[str, Any]]
    """
    remaining_timeout(deadline)
    properties = await run_with_deadline(
        lambda: get_properties() if deadline is None else get_properties(deadline=deadline), deadline,
    )
    remaining_timeout(deadline)

    async def query_offers(query_spec: dict[str, Any]) -> list[dict[str, Any]]:
        async def run_legacy_read() -> list[dict[str, Any]]:
            return [offer async for offer in client_connection.QueryOffers(query_spec, **legacy_kwargs())]

        return await backend.run_operation(
            build_request=lambda: build_get_throughput_from_connection(
                client_connection=client_connection,
                container_link=container_link,
                offer_query=query_spec,
                options=rust_options,
            ),
            routing=routing,
            legacy_call=run_legacy_read,
            process_response=lambda response: process_get_throughput_response(
                response, client_connection=client_connection
            ),
            deadline=deadline,
        )

    offers: list[dict[str, Any]] = []
    for attempt in range(2):
        query_spec = offer_query(properties["_self"])
        rust_options[Constants.ContainerRID] = properties["_rid"]
        recovery_error = None
        try:
            offers = await run_with_deadline(
                partial(query_offers, query_spec),
                deadline,
            )
        except exceptions.CosmosHttpResponseError as error:
            if attempt or not is_rust_backend(backend) or not _container_recreate_exception(error):
                raise
            recovery_error = error
        else:
            remaining_timeout(deadline)
            if offers or attempt or not is_rust_backend(backend):
                break
        remaining_timeout(deadline)
        refreshed = await run_with_deadline(
            lambda: refresh_properties() if deadline is None else refresh_properties(deadline=deadline), deadline,
        )
        remaining_timeout(deadline)
        if refreshed["_rid"] == properties["_rid"]:
            if recovery_error is not None:
                raise recovery_error
            break
        properties = refreshed

    _require_container_offers(offers, properties)
    return offers


def get_container_throughput(
    *,
    client_connection: Any,
    container_link: str,
    get_properties: Callable[..., Mapping[str, Any]],
    refresh_properties: Callable[..., Mapping[str, Any]],
    response_hook: Optional[Callable[[Mapping[str, Any], list[dict[str, Any]]], None]],
    kwargs: Mapping[str, Any],
) -> ThroughputProperties:
    """Read dedicated throughput within one metadata-and-offer deadline."""
    started = time.monotonic()
    kwargs = prepare_read_kwargs(kwargs, response_hook)
    backend, rust_options, rust_kwargs = gather_rust_call_inputs(client_connection, None, kwargs)
    routing = read_routing(
        backend, rust_options,
        supported=can_use_rust_backend_for_get_throughput(
            backend=backend, options=rust_options, kwargs=rust_kwargs,
        ),
        capability=GET_CONTAINER_THROUGHPUT,
    )
    timeout = rust_options.get("timeout")
    deadline = None if timeout is None else started + float(timeout)
    offers = _read_container_offers(
        client_connection=client_connection, container_link=container_link,
        backend=backend, rust_options=rust_options, routing=routing,
        get_properties=get_properties, refresh_properties=refresh_properties,
        legacy_kwargs=lambda: legacy_read_kwargs(rust_options, rust_kwargs, kwargs, deadline=deadline),
        deadline=deadline,
    )
    remaining_timeout(deadline)
    return finish_read(offers, client_connection, response_hook)


async def get_container_throughput_async(
    *,
    client_connection: Any,
    container_link: str,
    get_properties: Callable[..., Awaitable[Mapping[str, Any]]],
    refresh_properties: Callable[..., Awaitable[Mapping[str, Any]]],
    response_hook: Optional[Callable[[Mapping[str, Any], list[dict[str, Any]]], None]],
    kwargs: Mapping[str, Any],
) -> ThroughputProperties:
    """Read dedicated throughput asynchronously within the same deadline."""
    started = time.monotonic()
    kwargs = prepare_read_kwargs(kwargs, response_hook)
    backend, rust_options, rust_kwargs = gather_rust_call_inputs(client_connection, None, kwargs)
    routing = read_routing(
        backend, rust_options,
        supported=can_use_rust_backend_for_get_throughput(
            backend=backend, options=rust_options, kwargs=rust_kwargs,
        ),
        capability=GET_CONTAINER_THROUGHPUT,
    )
    timeout = rust_options.get("timeout")
    deadline = None if timeout is None else started + float(timeout)
    offers = await _read_container_offers_async(
        client_connection=client_connection, container_link=container_link,
        backend=backend, rust_options=rust_options, routing=routing,
        get_properties=get_properties, refresh_properties=refresh_properties,
        legacy_kwargs=lambda: legacy_read_kwargs(rust_options, rust_kwargs, kwargs, deadline=deadline),
        deadline=deadline,
    )
    remaining_timeout(deadline)
    return finish_read(offers, client_connection, response_hook)


def replace_container_throughput(
    *,
    client_connection: Any,
    container_link: str,
    get_properties: Callable[..., Mapping[str, Any]],
    refresh_properties: Callable[..., Mapping[str, Any]],
    throughput: Union[int, ThroughputProperties],
    response_hook: Optional[Callable[[Mapping[str, Any], CosmosDict], None]],
    kwargs: Mapping[str, Any],
) -> ThroughputProperties:
    """Replace container throughput without backend logic in the public proxy.

    Read-modify-write: run one ``get_throughput`` to get the current offer, apply the
    new RU/s to a copy, then run one ``replace_throughput`` to write it back. Both go
    through the same selected Python backend; the public method does not select it.
    """
    started = time.monotonic()
    validate_replacement_throughput(throughput)
    kwargs = prepare_read_kwargs(kwargs, response_hook)
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
    offers = _read_container_offers(
        client_connection=client_connection, container_link=container_link,
        backend=backend, rust_options=rust_options, routing=routing,
        get_properties=get_properties, refresh_properties=refresh_properties,
        legacy_kwargs=lambda: legacy_read_kwargs(rust_options, rust_kwargs, kwargs, deadline=deadline),
        deadline=deadline,
    )
    remaining_timeout(deadline)
    new_offer = deepcopy(offers[0])
    _replace_throughput(throughput=throughput, new_throughput_properties=new_offer)
    updated_offer = backend.run_operation(
        build_request=lambda: build_replace_throughput_from_connection(
            client_connection=client_connection,
            container_link=container_link,
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


async def replace_container_throughput_async(
    *,
    client_connection: Any,
    container_link: str,
    get_properties: Callable[..., Awaitable[Mapping[str, Any]]],
    refresh_properties: Callable[..., Awaitable[Mapping[str, Any]]],
    throughput: Union[int, ThroughputProperties],
    response_hook: Optional[Callable[[Mapping[str, Any], CosmosDict], None]],
    kwargs: Mapping[str, Any],
) -> ThroughputProperties:
    """Replace throughput, awaiting the offer read and replacement on the same path."""
    started = time.monotonic()
    validate_replacement_throughput(throughput)
    kwargs = prepare_read_kwargs(kwargs, response_hook)
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
    offers = await _read_container_offers_async(
        client_connection=client_connection, container_link=container_link,
        backend=backend, rust_options=rust_options, routing=routing,
        get_properties=get_properties, refresh_properties=refresh_properties,
        legacy_kwargs=lambda: legacy_read_kwargs(rust_options, rust_kwargs, kwargs, deadline=deadline),
        deadline=deadline,
    )
    remaining_timeout(deadline)
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
                container_link=container_link,
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
