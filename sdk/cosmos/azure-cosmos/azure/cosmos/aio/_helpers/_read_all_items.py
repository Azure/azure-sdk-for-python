# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Fetch item-feed pages, keeping a feed cursor per iterator on the Rust path.

ReadAllConfig and ReadAllPageState provide the shared request and continuation
rules. This module awaits page fetching through the selected Python backend.
The customer app receives a CosmosAsyncItemPaged pager, not this page iterator.
"""

from typing import Any, Optional

from azure.core.async_paging import AsyncPageIterator
from azure.core.utils import CaseInsensitiveDict

from ..._cosmos_responses import CosmosAsyncItemPaged
from ..._helpers._read_all_items import ReadAllConfig, ReadAllPageState
from ..._telemetry import trace_operation_async
from ..._operation_deadline import (
    legacy_deadline_options,
    remaining_timeout,
    run_with_deadline,
)


@trace_operation_async(
    binding_operation="read_all_items",
    operation_name="read_all_items",
    name_of_span="ContainerProxy.read_all_items.fetch",
)
async def _fetch_rust_page(
    config: ReadAllConfig, state: ReadAllPageState, deadline: Optional[float]
) -> Optional[tuple[Optional[str], list[dict[str, Any]]]]:
    """Record one internal fetch, draining deadline work before completion."""
    previous = state.token

    async def fetch_one() -> list[dict[str, Any]]:
        pages = config.backend.execute_pages(
            config.prepared(state.token, state.cursor, deadline),
            deadline=deadline,
        )
        try:
            page = await pages.__anext__()
        except StopAsyncIteration as exc:
            raise RuntimeError("Rust backend returned no read_all_items page.") from exc
        finally:
            await pages.aclose()
        return state.parse(page)

    rows = await run_with_deadline(fetch_one, deadline)
    if rows or state.token is None:
        return state.finish(rows, deadline)
    if state.token == previous:
        raise RuntimeError("read_all_items returned an empty page without continuation progress.")
    return None


class AsyncReadAllPageIterator(AsyncPageIterator):
    """Keep this iterator's progress separate and reject overlapping fetches."""

    def __init__(
        self,
        config: ReadAllConfig,
        headers: CaseInsensitiveDict,
        continuation_token: Optional[str] = None,
    ) -> None:
        token = (
            continuation_token
            if continuation_token is not None
            else config.options.get("continuation")
        )
        self.state = ReadAllPageState(config, headers, token)
        super().__init__(self._fetch, self._unpack, continuation_token=token)

    async def _unpack(self, value: tuple[Optional[str], list[dict[str, Any]]]) -> Any:
        # Pass through the rows and continuation token; None marks the end.
        return value

    async def _fetch(
        self, _token: Optional[str]
    ) -> tuple[Optional[str], list[dict[str, Any]]]:
        """Fetch rows under one deadline, including any empty pages skipped.

        state.begin() may create a feed cursor but does not acquire a driver
        handle. Failed fetches go through the shared state's failure handling;
        a safe initial setup failure may permit a later explicit retry.
        """
        state = self.state
        if state.done:
            raise StopAsyncIteration
        if state.failed:
            raise RuntimeError(
                "read_all_items pager failed; resume a new pager from the last delivered bookmark."
            )
        if not state.lock.acquire(blocking=False):
            raise RuntimeError(
                "Concurrent use of a read_all_items pager is not supported."
            )
        try:
            config = state.config
            deadline = config.deadline()
            state.begin()

            if config.rust:
                while True:
                    result = await _fetch_rust_page(config, state, deadline)
                    if result is not None:
                        break
                rows = result[1]
                if not rows and state.done:
                    raise StopAsyncIteration
                return result

            async def fetch() -> list[dict[str, Any]]:
                state.legacy_options.update(legacy_deadline_options(config.options, deadline))
                if state.legacy_pages is None:
                    await config.proxy._get_properties_with_options(
                        state.legacy_options
                    )
                    remaining_timeout(deadline)
                    state.legacy_options["_read_all_response_headers"] = state.captured
                    items = config.connection.ReadItems(
                        collection_link=config.proxy.container_link,
                        feed_options=state.legacy_options,
                        response_hook=state.capture,
                        _read_all_backend=config.backend,
                        containerProperties=config.proxy._get_properties_with_options,
                        **config.kwargs,
                    )
                    state.legacy_pages = items.by_page(continuation_token=state.token)
                try:
                    page = await state.legacy_pages.__anext__()
                except StopAsyncIteration:
                    state.token = None
                    return []
                rows = [row async for row in page]
                state.token = state.legacy_pages.continuation_token
                return rows

            rows = await run_with_deadline(fetch, deadline)
            result = state.finish(rows, deadline)
            if not rows and state.done:
                raise StopAsyncIteration
            return result
        except StopAsyncIteration:
            raise
        except BaseException as error:
            state.invalidate(error)
            raise
        finally:
            state.lock.release()


def read_all_items(proxy: Any, kwargs: dict[str, Any]) -> CosmosAsyncItemPaged:
    """Return a pager without fetching a page; async iteration starts the work."""
    config = ReadAllConfig(proxy, kwargs)
    headers = CaseInsensitiveDict()
    return CosmosAsyncItemPaged(
        config,
        headers,
        page_iterator_class=AsyncReadAllPageIterator,
        response_headers=headers,
    )
