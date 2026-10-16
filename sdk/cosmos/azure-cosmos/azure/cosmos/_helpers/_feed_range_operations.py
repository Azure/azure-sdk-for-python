# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Prepare feed-range calls in the Python wrapper for both client types.

A customer divides an order scan among workers by passing each worker a
returned feed-range dictionary. Treat it as an unchanged value describing
which part of the container to read, not as order data or a continuation token.

Range discovery waits until iteration. The binding asks the Rust driver to
resolve the container and obtain its ranges. Each returned pager keeps its
own result state and available response headers. Unsupported Rust-path options
and discovery failures do not cause fallback to the legacy path.

The legacy branches remain for migration tests and unmigrated family members,
not as another execution path for release. Partition-key conversion and
range-subset checks share this module but have their own operation rules.
"""

from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
from dataclasses import replace
import threading

from azure.cosmos._backend.capabilities import OperationRouting

from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Iterator,
    Mapping,
    Optional,
)

from azure.core.async_paging import AsyncList
from azure.core.utils import CaseInsensitiveDict

from .._backend.contracts import BackendResponse, PreparedRequest
from .._constants import _Constants as Constants
from .._cosmos_responses import CosmosAsyncItemPaged, CosmosItemPaged
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
    validate_read_feed_ranges_force_refresh,
)
from .._change_feed.feed_range_internal import FeedRangeInternalEpk
from .._helpers._response_parse import build_response_headers, parse_response_body, process_backend_response
from .._routing.routing_range import Range


class _FeedRangesResult:
    """Keep one range discovery's results and headers separate from other calls."""

    def __init__(self, client_connection: Any) -> None:
        self.connection = client_connection
        self.ranges: Optional[list[dict[str, Any]]] = None
        self.headers = CaseInsensitiveDict()
        self._lock = threading.Lock()

    @contextmanager
    def fetch(self, continuation_token: Optional[str]) -> Iterator[None]:
        if continuation_token is not None:
            raise ValueError("read_feed_ranges does not support continuation tokens.")
        if not self._lock.acquire(blocking=False):
            raise RuntimeError("read_feed_ranges does not support concurrent fetches on one result iterator.")
        try:
            yield
        except (StopIteration, StopAsyncIteration) as error:
            raise RuntimeError("read_feed_ranges ended without returning a range result.") from error
        finally:
            self._lock.release()

    def process_response(self, response: BackendResponse) -> list[dict[str, Any]]:
        headers = build_response_headers(response)
        self.connection.last_response_headers = deepcopy(headers)
        ranges = parse_read_feed_ranges_payload(parse_response_body(replace(response, headers=headers)))
        self.headers.clear()
        self.headers.update(deepcopy(headers))
        return ranges


def _container_rid(
    client_connection: Any,
    container_link: str,
    properties: Mapping[str, Any],
) -> str:
    """Return the container resource id from properties or the connection cache."""
    rid = properties.get("_rid")
    if isinstance(rid, str):
        return rid
    # Preserve the existing cache contract for test doubles and legacy connection
    # implementations whose property-population callback returns no value.
    return client_connection._container_properties_cache[container_link]["_rid"]


def read_feed_ranges(
    *,
    client_connection: Any,
    container_link: str,
    get_properties: Callable[[], Mapping[str, Any]],
    force_refresh: bool,
    kwargs: Mapping[str, Any],
) -> CosmosItemPaged:
    """Fetch one complete range set lazily; return copies on subsequent iteration."""
    validate_read_feed_ranges_force_refresh(force_refresh)
    kwargs = dict(kwargs)
    selected_backend = client_connection._backend
    backend = selected_backend
    rust_eligible = can_use_rust_backend_for_read_feed_ranges(
        backend=selected_backend, kwargs=kwargs
    )
    result = _FeedRangesResult(client_connection)

    def get_next(
        continuation_token: Optional[str],
    ) -> list[dict[str, Any]]:
        def run_legacy() -> list[dict[str, Any]]:
            if force_refresh:
                client_connection.refresh_routing_map_provider()
            properties = get_properties()
            feed_options: Dict[str, Any] = {
                Constants.ContainerRID: _container_rid(
                    client_connection, container_link, properties
                )
            }
            partition_key_ranges = (
                client_connection._routing_map_provider.get_overlapping_ranges(
                    container_link,
                    [Range("", "FF", True, False)],
                    feed_options,
                    **kwargs,
                )
            )
            return [
                FeedRangeInternalEpk(
                    Range.PartitionKeyRangeToRange(partition_key_range)
                ).to_dict()
                for partition_key_range in partition_key_ranges
            ]

        with result.fetch(continuation_token):
            if result.ranges is None:
                result.ranges = backend.run_operation(
                    build_request=lambda: build_read_feed_ranges_prepared_request(
                        container_link=container_link,
                        force_refresh=force_refresh,
                    ),
                    routing=OperationRouting("read_feed_ranges", rust_eligible),
                    legacy_call=run_legacy,
                    process_response=result.process_response,
                )
            return deepcopy(result.ranges)

    def extract_data(feed_ranges_response: list[dict[str, Any]]):
        return None, iter(feed_ranges_response)

    return CosmosItemPaged(get_next, extract_data, response_headers=result.headers)


def feed_range_from_partition_key(
    *,
    client_connection: Any,
    container_link: str,
    partition_key_value: Any,
    get_legacy_epk_range: Callable[[Any], Range],
) -> dict[str, Any]:
    """Calculate one partition key's feed range through the selected Python backend."""
    selected_backend = client_connection._backend
    backend = selected_backend
    return backend.run_operation(
        build_request=lambda: build_feed_range_from_partition_key_prepared_request(
            container_link=container_link,
            partition_key_value=partition_key_value,
        ),
        routing=OperationRouting(
            "feed_range_from_partition_key",
            can_use_rust_backend_for_feed_range_from_partition_key(
                backend=selected_backend
            ),
        ),
        legacy_call=lambda: FeedRangeInternalEpk(
            get_legacy_epk_range(partition_key_value)
        ).to_dict(),
        process_response=lambda response: parse_feed_range_from_partition_key_payload(
            process_backend_response(
                response,
                client_connection=client_connection,
                response_hook=None,
            )
        ),
    )


def is_feed_range_subset(
    *,
    client_connection: Any,
    parent_feed_range: dict[str, Any],
    child_feed_range: dict[str, Any],
) -> bool:
    """Compare feed ranges through the selected Python backend."""
    selected_backend = client_connection._backend
    backend = selected_backend

    def run_legacy() -> bool:
        parent = FeedRangeInternalEpk.from_json(parent_feed_range)
        child = FeedRangeInternalEpk.from_json(child_feed_range)
        return child.get_normalized_range().is_subset(parent.get_normalized_range())

    return backend.run_operation(
        build_request=lambda: build_is_feed_range_subset_prepared_request(
            parent_feed_range=parent_feed_range,
            child_feed_range=child_feed_range,
        ),
        routing=OperationRouting(
            "is_feed_range_subset",
            can_use_rust_backend_for_is_feed_range_subset(
                backend=selected_backend,
                parent_feed_range=parent_feed_range,
                child_feed_range=child_feed_range,
            ),
        ),
        legacy_call=run_legacy,
        process_response=lambda response: parse_is_feed_range_subset_payload(
            process_backend_response(
                response,
                client_connection=None,
                response_hook=None,
            )
        ),
    )


def read_feed_ranges_async(
    *,
    client_connection: Any,
    container_link: str,
    get_properties: Callable[[], Awaitable[Mapping[str, Any]]],
    force_refresh: bool,
    kwargs: Mapping[str, Any],
) -> CosmosAsyncItemPaged:
    """Async twin of :func:`read_feed_ranges`."""
    validate_read_feed_ranges_force_refresh(force_refresh)
    kwargs = dict(kwargs)
    selected_backend = client_connection._backend
    backend = selected_backend
    rust_eligible = can_use_rust_backend_for_read_feed_ranges(
        backend=selected_backend, kwargs=kwargs
    )
    result = _FeedRangesResult(client_connection)

    async def get_next(
        continuation_token: Optional[str],
    ) -> list[dict[str, Any]]:
        def build_request() -> PreparedRequest:
            return build_read_feed_ranges_prepared_request(
                container_link=container_link,
                force_refresh=force_refresh,
            )

        async def run_legacy() -> list[dict[str, Any]]:
            if force_refresh:
                await client_connection.refresh_routing_map_provider()
            properties = await get_properties()
            feed_options: Dict[str, Any] = {
                Constants.ContainerRID: _container_rid(
                    client_connection, container_link, properties
                )
            }
            partition_key_ranges = (
                await client_connection._routing_map_provider.get_overlapping_ranges(
                    container_link,
                    [Range("", "FF", True, False)],
                    feed_options,
                    **kwargs,
                )
            )
            return [
                FeedRangeInternalEpk(
                    Range.PartitionKeyRangeToRange(partition_key_range)
                ).to_dict()
                for partition_key_range in partition_key_ranges
            ]

        with result.fetch(continuation_token):
            if result.ranges is None:
                result.ranges = await backend.run_operation(
                    build_request=build_request,
                    routing=OperationRouting("read_feed_ranges", rust_eligible),
                    legacy_call=run_legacy,
                    process_response=result.process_response,
                )
            return deepcopy(result.ranges)

    async def extract_data(feed_ranges_response: list[dict[str, Any]]):
        return None, AsyncList(feed_ranges_response)

    return CosmosAsyncItemPaged(get_next, extract_data, response_headers=result.headers)


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

    def build_request() -> PreparedRequest:
        return build_feed_range_from_partition_key_prepared_request(
            container_link=container_link,
            partition_key_value=partition_key_value,
        )

    async def run_legacy() -> dict[str, Any]:
        return FeedRangeInternalEpk(
            await get_legacy_epk_range(partition_key_value)
        ).to_dict()

    return await backend.run_operation(
        build_request=build_request,
        routing=OperationRouting(
            "feed_range_from_partition_key",
            can_use_rust_backend_for_feed_range_from_partition_key(
                backend=selected_backend
            ),
        ),
        legacy_call=run_legacy,
        process_response=lambda response: parse_feed_range_from_partition_key_payload(
            process_backend_response(
                response,
                client_connection=client_connection,
                response_hook=None,
            )
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

    def build_request() -> PreparedRequest:
        return build_is_feed_range_subset_prepared_request(
            parent_feed_range=parent_feed_range,
            child_feed_range=child_feed_range,
        )

    async def run_legacy() -> bool:
        parent = FeedRangeInternalEpk.from_json(parent_feed_range)
        child = FeedRangeInternalEpk.from_json(child_feed_range)
        return child.get_normalized_range().is_subset(parent.get_normalized_range())

    return await backend.run_operation(
        build_request=build_request,
        routing=OperationRouting(
            "is_feed_range_subset",
            can_use_rust_backend_for_is_feed_range_subset(
                backend=selected_backend,
                parent_feed_range=parent_feed_range,
                child_feed_range=child_feed_range,
            ),
        ),
        legacy_call=run_legacy,
        process_response=lambda response: parse_is_feed_range_subset_payload(
            process_backend_response(
                response,
                client_connection=None,
                response_hook=None,
            )
        ),
    )
