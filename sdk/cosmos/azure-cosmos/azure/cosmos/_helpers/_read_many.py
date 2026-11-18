# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Collect Rust read-many pages into Python's ordered read_items result."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from typing import TYPE_CHECKING, Any, Generic, Optional, TypeVar

from azure.core.utils import CaseInsensitiveDict

from .._backend.contracts import BackendPage, ContainerMetadata, PreparedPageRequest, ReadManyItem
from .._backend.cosmos_backend import CosmosBackend
from .._backend.partition_key_input import BindingPartitionKey
from .._cosmos_responses import CosmosList
from .._operation_deadline import remaining_timeout
from .._telemetry import RecordingOptions, trace_operation
from ._item_context import ItemClientContext
from ._read_items import (
    ResponseHeaderAccumulator,
    complete_read_items_response,
    index_query_results,
    index_requested_items,
    normalize_read_items,
    partition_key_components,
    prepare_read_items,
)
from ._request_settings import (
    HEADERS_THE_DRIVER_REGENERATES,
    build_request_headers_and_settings,
    compose_options_from_kwargs,
)
from ._response_parse import page_to_backend_response, process_backend_response
from ..partition_key import _Undefined

if TYPE_CHECKING:
    from ..aio._backend.cosmos_backend import AsyncCosmosBackend
    from .._rust import _ItemFeedCursor

_BackendT = TypeVar("_BackendT", "CosmosBackend", "AsyncCosmosBackend")


class ReadManyRequest(Generic[_BackendT]):
    """Keep the requested items, paging state and timeout without a legacy connection."""

    def __init__(
        self, context: ItemClientContext[_BackendT], container_link: str, items: Any, kwargs: dict[str, Any]
    ) -> None:
        if context is None or context.adapter.name == "core-python":
            raise NotImplementedError("read_items requires the Rust backend; no legacy fallback is available.")
        self._item_context: ItemClientContext[_BackendT] = context
        self.backend: _BackendT = context.adapter
        self.container_link = container_link
        context.defaults.apply_timeout(kwargs)
        self.items, self.deadline = prepare_read_items(items, kwargs)
        kwargs.pop("_item_operation_deadline", None)
        self.hook = kwargs.pop("response_hook", None)
        self.recording = RecordingOptions.take(kwargs)
        options = deepcopy(compose_options_from_kwargs(kwargs))
        for name, key in (("timeout", "timeout"), ("consistency_level", "consistencyLevel")):
            if name in kwargs:
                options[key] = kwargs.pop(name)
        allowed = {
            "timeout", "consistencyLevel", "sessionToken", "initialHeaders", "excludedLocations",
            "priorityLevel", "throughputBucket", "availabilityStrategy", "maxItemCount",
            "maxIntegratedCacheStaleness",
        }
        if kwargs or set(options) - allowed:
            names = sorted(set(kwargs) | (set(options) - allowed))
            raise TypeError(f"read_items does not support these options: {', '.join(names)}")
        count = options.get("maxItemCount")
        if count is not None and (type(count) is not int or count == 0 or count < -1):
            raise ValueError("read_items max_item_count must be a positive integer, -1, or None.")
        cache = options.get("maxIntegratedCacheStaleness")
        if cache is not None and (isinstance(cache, bool) or not isinstance(cache, int) or cache < 0):
            raise ValueError("read_items cache staleness must be a nonnegative integer or None.")
        headers = options.get("initialHeaders") or {}
        reserved = HEADERS_THE_DRIVER_REGENERATES | {
            "x-ms-continuation", "x-ms-documentdb-partitionkey", "x-ms-documentdb-partitionkeyrangeid",
            "x-ms-documentdb-query-enablecrosspartition", "x-ms-documentdb-isquery",
            "x-ms-cosmos-is-query-plan-request",
        }
        if any(not isinstance(name, str) or name.lower() in reserved for name in headers):
            raise TypeError("read_items initial_headers cannot override driver-owned routing or continuation.")
        context.defaults.apply_to_options(options)
        self.headers, self.settings = build_request_headers_and_settings(options)
        self.cursor: Optional[_ItemFeedCursor] = None
        self.selection: tuple[ReadManyItem, ...] = ()
        self.definition: dict[str, Any] = {}
        self.indices: dict[tuple, list[int]] = {}
        self.rows: list[dict[str, Any]] = []
        self.accumulated = ResponseHeaderAccumulator()
        self.has_charge = False

    def initialize(self, metadata: ContainerMetadata) -> None:
        self.definition = {
            "paths": metadata.partition_key_paths,
            "kind": metadata.partition_key_kind,
            "systemKey": metadata.system_key,
        }
        items = normalize_read_items(self.items, self.definition)
        self.indices = index_requested_items([(index, item_id, key) for index, (item_id, key) in enumerate(items)])
        self.selection = tuple(
            ReadManyItem(
                item_id,
                BindingPartitionKey("components", tuple(
                    Ellipsis if isinstance(value, _Undefined) else value for value in partition_key_components(key)
                )),
            )
            for item_id, key in items
        )
        remaining_timeout(self.deadline)
        self.cursor = self.backend.create_item_feed_cursor()

    def prepared(self) -> PreparedPageRequest:
        remaining = remaining_timeout(self.deadline)
        settings = self.settings if remaining is None else replace(self.settings, timeout_seconds=remaining)
        return PreparedPageRequest(
            op="read_items",
            container_link=self.container_link,
            read_many_items=self.selection,
            headers=self.headers,
            settings=settings,
            cursor=self.cursor,
        )

    def consume(self, page: BackendPage) -> bool:
        envelope = process_backend_response(
            page_to_backend_response(page), response_state=self._item_context.response_state
        )
        rows = envelope.get("Documents")
        if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
            raise ValueError("read_items received an invalid Documents response.")
        headers = envelope.get_response_headers()
        self.has_charge = self.has_charge or "x-ms-request-charge" in headers
        self.accumulated(headers, None)
        self.rows.extend(rows)
        if not isinstance(page.has_more, bool):
            raise RuntimeError("read_items requires a binding that reports retained-cursor progress.")
        remaining_timeout(self.deadline)
        return page.has_more

    def finish(self) -> CosmosList:
        indexed = index_query_results(self.rows, self.indices, self.definition) if self.items else []
        indexed.sort(key=lambda entry: entry[0])
        headers = CaseInsensitiveDict(self.accumulated.headers)
        headers.pop("x-ms-continuation", None)
        if not self.has_charge:
            headers.pop("x-ms-request-charge", None)
        result = CosmosList([item for _, item in indexed], response_headers=headers)
        self._item_context.response_state.last_response_headers = CaseInsensitiveDict(headers)
        return complete_read_items_response(result, self.hook, self.deadline)


@trace_operation(
    binding_operation="read_items", operation_name="read_items", name_of_span="ContainerProxy.read_items.fetch"
)
def _fetch_page(request: ReadManyRequest[CosmosBackend], **_tracing_kwargs: Any) -> bool:
    pages = request.backend.execute_pages(request.prepared(), deadline=request.deadline)
    try:
        page = next(pages)
    except StopIteration as error:
        raise RuntimeError("Rust backend returned no read_items page.") from error
    finally:
        close = getattr(pages, "close", None)
        if close is not None:
            close()
    return request.consume(page)


def read_items(
    context: Optional[ItemClientContext[CosmosBackend]],
    container_link: str,
    items: Any,
    kwargs: dict[str, Any],
) -> CosmosList:
    if context is None:
        raise NotImplementedError("read_items requires a client-owned Rust context.")
    request = ReadManyRequest(context, container_link, items, kwargs)
    try:
        if request.items:
            request.initialize(request.backend.get_container_metadata(container_link, deadline=request.deadline))
            while _fetch_page(request, **request.recording.kwargs):
                pass
        return request.finish()
    finally:
        request.cursor = None
