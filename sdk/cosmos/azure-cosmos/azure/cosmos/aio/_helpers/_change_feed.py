# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Poll change-feed pages when the customer app advances the async page iterator.

ChangeFeedConfig and ChangeFeedPageState supply the shared settings and
continuation rules. This module awaits the selected Python backend or legacy
fetcher. Constructing the pager does not start a metadata request or fetch a page.
"""

from typing import Any, Optional

from azure.core.async_paging import AsyncPageIterator
from azure.core.utils import CaseInsensitiveDict

from ..._change_feed.aio.change_feed_fetcher import (
    ChangeFeedFetcherV1,
    ChangeFeedFetcherV2,
)
from ..._change_feed.change_feed_state import ChangeFeedStateVersion
from ..._cosmos_responses import CosmosAsyncItemPaged
from ..._helpers._change_feed import ChangeFeedConfig, ChangeFeedPageState
from ..._operation_deadline import (
    legacy_deadline_options,
    remaining_timeout,
    run_with_deadline,
)


class AsyncChangeFeedPageIterator(AsyncPageIterator):
    """Keep this iterator's feed cursor, continuation token, and polling progress."""

    def __init__(
        self,
        config: ChangeFeedConfig,
        headers: CaseInsensitiveDict,
        continuation_token: Optional[str] = None,
    ) -> None:
        token = (
            continuation_token
            if continuation_token is not None
            else config.options.get("continuation")
        )
        self.state = ChangeFeedPageState(config, headers, token)
        super().__init__(self._fetch, self._unpack, continuation_token=token)

    async def _unpack(self, value: tuple[Optional[str], list[dict[str, Any]]]) -> Any:
        # Pass through the continuation token and rows for the page iterator.
        return value

    async def _fetch(
        self, _token: Optional[str]
    ) -> tuple[Optional[str], list[dict[str, Any]]]:
        """Await a poll and then complete its result using the shared state.

        A poll starting at a particular time can require another fetch before
        returning. Those fetches share one deadline. The legacy fetcher and its
        metadata request are created only when that path is actually used.
        """
        state = self.state
        if state.done:
            raise StopAsyncIteration
        if state.failed:
            raise RuntimeError(
                "change-feed pager failed; resume a new pager from the last delivered bookmark."
            )
        if not state.lock.acquire(blocking=False):
            raise RuntimeError(
                "Concurrent use of a change-feed pager is not supported."
            )
        try:
            config, deadline = state.config, state.config.deadline()
            state.begin()

            async def fetch_page() -> list[dict[str, Any]]:
                if config.rust:
                    while True:
                        pages = config.backend.execute_pages(
                            state.prepared_page(deadline), deadline=deadline
                        )
                        try:
                            page = await pages.__anext__()
                        except StopAsyncIteration as error:
                            raise RuntimeError(
                                "Rust backend returned no change-feed page."
                            ) from error
                        finally:
                            await pages.aclose()
                        rows = state.parse(page)
                        if not state.poll_again:
                            return rows
                state.legacy_options.update(
                    legacy_deadline_options(config.options, deadline)
                )
                state.legacy_options.pop("continuation", None)
                if state.fetcher is None:
                    properties = await config.proxy._get_properties_with_options(
                        state.legacy_options
                    )
                    remaining_timeout(deadline)
                    change_state = state.legacy_state(properties)
                    state.legacy_options["changeFeedState"] = change_state

                    async def fetch(
                        options: dict[str, Any],
                    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
                        remaining_timeout(options.get("_item_operation_deadline"))
                        before = state.responses
                        rows = await config.connection.QueryFeed(
                            config.path,
                            config.collection_id,
                            None,
                            options,
                            response_hook=state.capture,
                            **config.kwargs
                        )
                        if state.responses == before:
                            raise RuntimeError(
                                "Legacy change-feed response headers were not captured."
                            )
                        return rows, dict(state.captured)

                    factory = (
                        ChangeFeedFetcherV1
                        if change_state.version == ChangeFeedStateVersion.V1
                        else ChangeFeedFetcherV2
                    )
                    state.fetcher = factory(
                        config.connection,
                        config.proxy.container_link,
                        state.legacy_options,
                        fetch,
                    )
                return state.legacy_result(await state.fetcher.fetch_next_block())

            rows = await run_with_deadline(fetch_page, deadline)
            return state.finish(rows, deadline)
        except BaseException as error:
            state.invalidate(error)
            raise
        finally:
            state.lock.release()


def query_items_change_feed(proxy: Any, kwargs: dict[str, Any]) -> CosmosAsyncItemPaged:
    """Return a change-feed pager without starting its first poll."""
    config = ChangeFeedConfig(proxy, kwargs)
    headers = CaseInsensitiveDict()
    return CosmosAsyncItemPaged(
        config,
        headers,
        page_iterator_class=AsyncChangeFeedPageIterator,
        response_headers=headers,
    )
