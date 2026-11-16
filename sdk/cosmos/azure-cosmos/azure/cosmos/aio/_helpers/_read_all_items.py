# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Read Rust read-many pages asynchronously, without saved continuation tokens."""

from typing import Any, AsyncIterator, Optional

from azure.core.async_paging import AsyncList
from azure.core.utils import CaseInsensitiveDict

from ..._cosmos_responses import CosmosAsyncItemPaged
from ..._helpers._read_all_items import ReadAllConfig, ReadAllPageState
from ..._operation_deadline import run_with_deadline
from ..._telemetry import trace_operation_async


@trace_operation_async(
    binding_operation="read_all_items",
    operation_name="read_all_items",
    name_of_span="ContainerProxy.read_all_items.fetch",
)
async def _fetch_rust_page(
    config: ReadAllConfig, state: ReadAllPageState, deadline: Optional[float], **_tracing_kwargs: Any
) -> Optional[list[dict[str, Any]]]:
    async def fetch_one() -> list[dict[str, Any]]:
        pages = config.backend.execute_pages(config.prepared(None, state.cursor, deadline), deadline=deadline)
        try:
            page = await pages.__anext__()
        except StopAsyncIteration as error:
            raise RuntimeError("Rust backend returned no read_all_items page.") from error
        finally:
            close = getattr(pages, "aclose", None)
            if close is not None:
                await close()
        return state.parse(page)

    rows = await run_with_deadline(fetch_one, deadline)
    return state.finish(rows, deadline)[1] if rows or state.is_done() else None


class AsyncReadAllPageIterator(AsyncIterator[AsyncIterator[dict[str, Any]]]):
    """Keep one cursor and reject attempts to fetch two pages at once."""

    def __init__(
        self, config: ReadAllConfig, headers: CaseInsensitiveDict, continuation_token: Optional[str] = None
    ) -> None:
        self.state = ReadAllPageState(config, headers, continuation_token)

    @property
    def continuation_token(self) -> None:
        raise NotImplementedError("read_all_items cannot be bookmarked; continue using this iterator.")

    async def __anext__(self) -> AsyncIterator[dict[str, Any]]:
        state = self.state
        if state.done:
            raise StopAsyncIteration
        if state.failed:
            raise RuntimeError("read_all_items pager failed; a new enumeration starts from the beginning.")
        if not state.lock.acquire(blocking=False):
            raise RuntimeError("Concurrent use of a read_all_items pager is not supported.")
        try:
            config = state.config
            deadline = config.deadline()
            state.begin()
            while True:
                rows = await _fetch_rust_page(config, state, deadline, **config.recording_options.kwargs)
                if rows is not None:
                    break
        except BaseException as error:
            state.invalidate(error)
            raise
        finally:
            state.lock.release()
        if not rows and state.done:
            raise StopAsyncIteration

        return AsyncList(rows)


def read_all_items(proxy: Any, kwargs: dict[str, Any]) -> CosmosAsyncItemPaged:
    config = ReadAllConfig(proxy, kwargs)
    headers = CaseInsensitiveDict()
    return CosmosAsyncItemPaged(config, headers, page_iterator_class=AsyncReadAllPageIterator, response_headers=headers)
