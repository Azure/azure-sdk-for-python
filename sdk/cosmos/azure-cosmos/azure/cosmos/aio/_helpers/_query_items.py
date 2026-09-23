# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Fetch query pages while retaining a feed cursor in the async page iterator.

QueryConfig prepares the query once; QueryPageState owns this iterator's
progress and continuation checks. This module awaits backend pages and returns
their rows for async iteration, using the same completion rules as the
synchronous query helper.
"""

from typing import Any, AsyncIterator, Optional

from azure.core.async_paging import AsyncList
from azure.core.utils import CaseInsensitiveDict

from ..._cosmos_responses import CosmosAsyncItemPaged
from ..._helpers._query_items import QueryConfig, QueryPageState
from ..._operation_deadline import run_with_deadline


class AsyncQueryPageIterator(AsyncIterator[AsyncIterator[Any]]):
    """Keep one query's progress and reject overlapping fetches on this iterator."""

    def __init__(
        self,
        config: QueryConfig,
        headers: CaseInsensitiveDict,
        continuation_token: Optional[str] = None,
    ) -> None:
        token = (
            continuation_token
            if continuation_token is not None
            else config.options.get("continuation")
        )
        self.state = QueryPageState(config, headers, token)

    @property
    def continuation_token(self) -> Optional[str]:
        """Return the last delivered continuation token, not progress from a pending fetch.

        A query can have more rows even when it cannot provide a resumable
        continuation token. In that case this property raises; iteration can
        still continue using the feed cursor.
        """
        if not self.state.resumable:
            raise NotImplementedError(
                "The driver cannot bookmark this query shape; continue using this iterator."
            )
        return self.state.last_delivered_continuation_token

    async def __anext__(self) -> Any:
        """Await enough backend pages to deliver rows or reach the end of the query.

        Empty pages share the same deadline. The shared state checks has_more
        and token progress; this method does not infer completion from a missing
        token alone. state.accept() runs the response hook before publishing
        the last delivered continuation token.
        """
        state = self.state
        if state.done:
            raise StopAsyncIteration
        state.check()
        try:
            deadline = state.config.deadline()
            state.begin()

            async def fetch() -> list[Any]:
                while True:
                    previous = state.token
                    pages = state.config.backend.execute_pages(
                        state.config.prepared(state.token, state.cursor, deadline),
                        deadline=deadline,
                    )
                    try:
                        page = await pages.__anext__()
                    except StopAsyncIteration as error:
                        raise RuntimeError(
                            "Rust backend returned no query page."
                        ) from error
                    finally:
                        await pages.aclose()
                    rows = state.parse(page)
                    if state.should_deliver(rows, previous):
                        return rows

            rows = await run_with_deadline(fetch, deadline)
            state.accept(rows, deadline)
        except BaseException as error:
            state.invalidate(error)
            raise
        finally:
            state.lock.release()
        if not rows and state.done:
            raise StopAsyncIteration
        return AsyncList(rows)


def query_items(proxy: Any, kwargs: dict[str, Any]) -> CosmosAsyncItemPaged:
    """Prepare query inputs and return a pager; fetching waits for async iteration."""
    config = QueryConfig(proxy, kwargs)
    headers = CaseInsensitiveDict()
    return CosmosAsyncItemPaged(
        config,
        headers,
        page_iterator_class=AsyncQueryPageIterator,
        response_headers=headers,
    )
