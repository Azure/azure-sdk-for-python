# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Collect Rust read-many pages asynchronously within one timeout."""

from __future__ import annotations

from typing import Any, Optional

from ..._cosmos_responses import CosmosList
from ..._helpers._item_context import ItemClientContext
from ..._helpers._read_many import ReadManyRequest
from ..._operation_deadline import run_with_deadline
from ..._telemetry import trace_operation_async
from .._backend.cosmos_backend import AsyncCosmosBackend


@trace_operation_async(
    binding_operation="read_items", operation_name="read_items", name_of_span="ContainerProxy.read_items.fetch"
)
async def _fetch_page(request: ReadManyRequest[AsyncCosmosBackend], **_tracing_kwargs: Any) -> bool:
    pages = request.backend.execute_pages(request.prepared(), deadline=request.deadline)
    try:
        page = await run_with_deadline(pages.__anext__, request.deadline)
    except StopAsyncIteration as error:
        raise RuntimeError("Rust backend returned no read_items page.") from error
    finally:
        close = getattr(pages, "aclose", None)
        if close is not None:
            await close()
    return request.consume(page)


async def read_items(
    context: Optional[ItemClientContext[AsyncCosmosBackend]],
    container_link: str,
    items: Any,
    kwargs: dict[str, Any],
) -> CosmosList:
    if context is None:
        raise NotImplementedError("read_items requires a client-owned Rust context.")
    request = ReadManyRequest(context, container_link, items, kwargs)
    try:
        if request.items:
            metadata = await run_with_deadline(
                lambda: request.backend.get_container_metadata(container_link, deadline=request.deadline),
                request.deadline,
            )
            request.initialize(metadata)
            while await _fetch_page(request, **request.recording.kwargs):
                pass
        return request.finish()
    finally:
        request.cursor = None
