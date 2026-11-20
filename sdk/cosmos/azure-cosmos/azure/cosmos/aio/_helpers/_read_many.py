# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Collect Rust read-many pages asynchronously within one timeout."""

from __future__ import annotations

from typing import Any, Optional

from ..._cosmos_responses import CosmosList
from ..._helpers._client_context import CosmosClientContext
from ..._helpers._read_many import ReadManyRequest
from ..._operation_deadline import run_with_deadline
from .._backend.cosmos_backend import AsyncCosmosBackend


async def _fetch_page(request: ReadManyRequest[AsyncCosmosBackend]) -> bool:
    if request.cursor is None:
        # Resolve the container before the first page, so a lookup failure is logged and traced.
        metadata = await run_with_deadline(
            lambda: request.backend.get_container_metadata(
                request.container_link, deadline=request.deadline, op="read_items"
            ),
            request.deadline,
        )
        request.initialize(metadata)
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
    context: Optional[CosmosClientContext[AsyncCosmosBackend]],
    container_link: str,
    items: Any,
    kwargs: dict[str, Any],
) -> CosmosList:
    if context is None:
        raise NotImplementedError("read_items requires a client-owned Rust context.")
    request = ReadManyRequest(context, container_link, items, kwargs)
    try:
        if request.items:
            while await _fetch_page(request):
                pass
        return request.finish()
    finally:
        request.cursor = None
