# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""The feed-range family coordinator: lists and computes a container's feed ranges.

A "feed range" is a slice of a container's key space -- one partition-key range.
Customers use them to split a large read (a query, or the change feed) into pieces
they can process in parallel: ask for the container's feed ranges, then read each
range on its own. The functions here back the public ``ContainerProxy`` methods
(sync and async):

* ``read_feed_ranges`` -- list the container's feed ranges (its partition-key ranges).
* ``feed_range_from_partition_key`` -- the single feed range a partition-key value falls in.
* ``is_feed_range_subset`` -- whether one feed range is fully inside another. This
  is a local calculation; it makes no service call.

Why this module exists (public methods must not know which engine runs): without
it, these calls would read ``client_connection._backend`` and branch -- try the
rust engine, else run the legacy routing-map code -- inside the customer-facing
proxy method. Instead each function uses the concrete backend stored by the
client and drives the work through
:meth:`~azure.cosmos._backend.base.CosmosBackend.run_operation`, so the proxy
method is a thin delegate that names no engine. This mirrors
:class:`~azure.cosmos._helpers.item_helper.ItemHelper` and the throughput
coordinator.
"""
from __future__ import annotations

from typing import Any, AsyncIterable, Awaitable, Callable, Dict, Iterable, Mapping, Optional

from azure.core.async_paging import AsyncItemPaged, AsyncList

from .._backend.contracts import LegacyOperation
from .._constants import _Constants as Constants
from .._cosmos_responses import CosmosItemPaged
from .._feed_ranges_rust_routing import (
    build_feed_range_from_partition_key_prepared_request,
    build_is_feed_range_subset_prepared_request,
    build_read_feed_ranges_prepared_request,
    can_use_rust_backend_for_feed_range_from_partition_key,
    can_use_rust_backend_for_is_feed_range_subset,
    can_use_rust_backend_for_read_feed_ranges,
    parse_feed_range_from_partition_key_payload,
    parse_is_feed_range_subset_payload,
    parse_read_feed_ranges_payload,
)
from .._change_feed.feed_range_internal import FeedRangeInternalEpk
from .._helpers._response_parse import parse_backend_response
from .._routing.routing_range import Range


def _container_rid(
    client_connection: Any,
    container_link: str,
    properties: Mapping[str, Any],
) -> str:
    """Return the container resource id from properties or the connection cache."""
    rid = properties.get("_rid")
    if isinstance(rid, str):
        return rid
    # Preserve the existing cache contract for test doubles and older connection
    # implementations whose property-population callback returns no value.
    return client_connection._container_properties_cache[container_link]["_rid"]


def read_feed_ranges(
    *,
    client_connection: Any,
    container_link: str,
    get_properties: Callable[[], Mapping[str, Any]],
    force_refresh: bool,
    kwargs: Mapping[str, Any],
) -> Iterable[dict[str, Any]]:
    """Return feed ranges while keeping engine selection outside the public proxy."""
    selected_backend = client_connection._backend
    backend = selected_backend
    rust_eligible = can_use_rust_backend_for_read_feed_ranges(
        backend=selected_backend, kwargs=kwargs
    )
    cached: Optional[list[dict[str, Any]]] = None

    def get_next(continuation_token: str) -> list[dict[str, Any]]:  # pylint: disable=unused-argument
        nonlocal cached
        if cached is not None:
            return cached

        def run_legacy() -> list[dict[str, Any]]:
            if force_refresh:
                client_connection.refresh_routing_map_provider()
            properties = get_properties()
            feed_options: Dict[str, Any] = {
                Constants.ContainerRID: _container_rid(client_connection, container_link, properties)
            }
            partition_key_ranges = client_connection._routing_map_provider.get_overlapping_ranges(
                container_link,
                [Range("", "FF", True, False)],
                feed_options,
                **kwargs,
            )
            return [
                FeedRangeInternalEpk(Range.PartitionKeyRangeToRange(partition_key_range)).to_dict()
                for partition_key_range in partition_key_ranges
            ]

        cached = backend.run_operation(
            build_prepared=lambda: build_read_feed_ranges_prepared_request(
                container_link=container_link,
                force_refresh=force_refresh,
            ),
            legacy_operation=LegacyOperation(op="read_feed_ranges", invoke=run_legacy),
            parse_response=lambda response: parse_read_feed_ranges_payload(
                parse_backend_response(
                    response,
                    client_connection=client_connection,
                    response_hook=None,
                )
            ),
            rust_eligible=rust_eligible,
        )
        return cached

    def extract_data(feed_ranges_response: list[dict[str, Any]]):
        return None, iter(feed_ranges_response)

    return CosmosItemPaged(get_next, extract_data)


def feed_range_from_partition_key(
    *,
    client_connection: Any,
    container_link: str,
    partition_key_value: Any,
    get_legacy_epk_range: Callable[[Any], Range],
) -> dict[str, Any]:
    """Calculate one partition key's feed range through the selected engine."""
    selected_backend = client_connection._backend
    backend = selected_backend
    return backend.run_operation(
        build_prepared=lambda: build_feed_range_from_partition_key_prepared_request(
            container_link=container_link,
            partition_key_value=partition_key_value,
        ),
        legacy_operation=LegacyOperation(
            op="feed_range_from_partition_key",
            invoke=lambda: FeedRangeInternalEpk(
                get_legacy_epk_range(partition_key_value)
            ).to_dict(),
        ),
        parse_response=lambda response: parse_feed_range_from_partition_key_payload(
            parse_backend_response(
                response,
                client_connection=client_connection,
                response_hook=None,
            )
        ),
        rust_eligible=can_use_rust_backend_for_feed_range_from_partition_key(
            backend=selected_backend
        ),
    )


def is_feed_range_subset(
    *,
    client_connection: Any,
    parent_feed_range: dict[str, Any],
    child_feed_range: dict[str, Any],
) -> bool:
    """Compare feed ranges through the selected engine."""
    selected_backend = client_connection._backend
    backend = selected_backend

    def run_legacy() -> bool:
        parent = FeedRangeInternalEpk.from_json(parent_feed_range)
        child = FeedRangeInternalEpk.from_json(child_feed_range)
        return child.get_normalized_range().is_subset(parent.get_normalized_range())

    return backend.run_operation(
        build_prepared=lambda: build_is_feed_range_subset_prepared_request(
            parent_feed_range=parent_feed_range,
            child_feed_range=child_feed_range,
        ),
        legacy_operation=LegacyOperation(op="is_feed_range_subset", invoke=run_legacy),
        parse_response=lambda response: parse_is_feed_range_subset_payload(
            parse_backend_response(
                response,
                client_connection=None,
                response_hook=None,
            )
        ),
        rust_eligible=can_use_rust_backend_for_is_feed_range_subset(
            backend=selected_backend
        ),
        fallback_exceptions=(ValueError,),
    )


def read_feed_ranges_async(
    *,
    client_connection: Any,
    container_link: str,
    get_properties: Callable[[], Awaitable[Mapping[str, Any]]],
    force_refresh: bool,
    kwargs: Mapping[str, Any],
) -> AsyncIterable[dict[str, Any]]:
    """Async twin of :func:`read_feed_ranges`."""
    selected_backend = client_connection._backend
    backend = selected_backend
    rust_eligible = can_use_rust_backend_for_read_feed_ranges(
        backend=selected_backend, kwargs=kwargs
    )
    cached: Optional[list[dict[str, Any]]] = None

    async def get_next(continuation_token: str) -> list[dict[str, Any]]:  # pylint: disable=unused-argument
        nonlocal cached
        if cached is not None:
            return cached
        async def build_prepared():
            return build_read_feed_ranges_prepared_request(
                container_link=container_link,
                force_refresh=force_refresh,
            )

        async def run_legacy() -> list[dict[str, Any]]:
            if force_refresh:
                await client_connection.refresh_routing_map_provider()
            properties = await get_properties()
            feed_options: Dict[str, Any] = {
                Constants.ContainerRID: _container_rid(client_connection, container_link, properties)
            }
            partition_key_ranges = await client_connection._routing_map_provider.get_overlapping_ranges(
                container_link,
                [Range("", "FF", True, False)],
                feed_options,
                **kwargs,
            )
            return [
                FeedRangeInternalEpk(Range.PartitionKeyRangeToRange(partition_key_range)).to_dict()
                for partition_key_range in partition_key_ranges
            ]

        cached = await backend.run_operation(
            build_prepared=build_prepared,
            legacy_operation=LegacyOperation(op="read_feed_ranges", invoke=run_legacy),
            parse_response=lambda response: parse_read_feed_ranges_payload(
                parse_backend_response(
                    response,
                    client_connection=client_connection,
                    response_hook=None,
                )
            ),
            rust_eligible=rust_eligible,
        )
        return cached

    async def extract_data(feed_ranges_response: list[dict[str, Any]]):
        return None, AsyncList(feed_ranges_response)

    return AsyncItemPaged(get_next, extract_data)


async def feed_range_from_partition_key_async(
    *,
    client_connection: Any,
    container_link: str,
    partition_key_value: Any,
    get_legacy_epk_range: Callable[[Any], Awaitable[Range]],
) -> dict[str, Any]:
    """Async twin of :func:`feed_range_from_partition_key`."""
    selected_backend = client_connection._backend
    backend = selected_backend

    async def build_prepared():
        return build_feed_range_from_partition_key_prepared_request(
            container_link=container_link,
            partition_key_value=partition_key_value,
        )

    async def run_legacy() -> dict[str, Any]:
        return FeedRangeInternalEpk(
            await get_legacy_epk_range(partition_key_value)
        ).to_dict()

    return await backend.run_operation(
        build_prepared=build_prepared,
        legacy_operation=LegacyOperation(
            op="feed_range_from_partition_key", invoke=run_legacy
        ),
        parse_response=lambda response: parse_feed_range_from_partition_key_payload(
            parse_backend_response(
                response,
                client_connection=client_connection,
                response_hook=None,
            )
        ),
        rust_eligible=can_use_rust_backend_for_feed_range_from_partition_key(
            backend=selected_backend
        ),
    )


async def is_feed_range_subset_async(
    *,
    client_connection: Any,
    parent_feed_range: dict[str, Any],
    child_feed_range: dict[str, Any],
) -> bool:
    """Async twin of :func:`is_feed_range_subset`."""
    selected_backend = client_connection._backend
    backend = selected_backend

    async def build_prepared():
        return build_is_feed_range_subset_prepared_request(
            parent_feed_range=parent_feed_range,
            child_feed_range=child_feed_range,
        )

    async def run_legacy() -> bool:
        parent = FeedRangeInternalEpk.from_json(parent_feed_range)
        child = FeedRangeInternalEpk.from_json(child_feed_range)
        return child.get_normalized_range().is_subset(parent.get_normalized_range())

    return await backend.run_operation(
        build_prepared=build_prepared,
        legacy_operation=LegacyOperation(op="is_feed_range_subset", invoke=run_legacy),
        parse_response=lambda response: parse_is_feed_range_subset_payload(
            parse_backend_response(
                response,
                client_connection=None,
                response_hook=None,
            )
        ),
        rust_eligible=can_use_rust_backend_for_is_feed_range_subset(
            backend=selected_backend
        ),
        fallback_exceptions=(ValueError,),
    )
