# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Poll change-feed pages when the customer app advances the async page iterator.

ChangeFeedConfig and ChangeFeedPageState supply the shared settings and
continuation rules. This module awaits the Rust backend. Constructing the pager
does not start a metadata request or fetch a page.
"""

from typing import Any, Optional

from azure.core.async_paging import AsyncPageIterator
from azure.core.utils import CaseInsensitiveDict

from ..._cosmos_responses import CosmosAsyncItemPaged
from ..._helpers._change_feed import ChangeFeedConfig, ChangeFeedPageState
from ..._operation_deadline import run_with_deadline
from ..._telemetry import trace_operation_async


@trace_operation_async(
    binding_operation="query_items_change_feed",
    operation_name="query_items_change_feed",
    name_of_span="ContainerProxy.query_items_change_feed.fetch",
)
async def _fetch_rust_page(
    config: ChangeFeedConfig, state: ChangeFeedPageState, deadline: Optional[float], **_tracing_kwargs: Any
) -> Optional[tuple[Optional[str], list[dict[str, Any]]]]:
    """Drain one authorized fetch before completing its public page.

    Additional ``_tracing_kwargs`` are consumed by the operation's telemetry decorator.

    :param ChangeFeedConfig config: Prepared feed configuration and async execution backend.
    :param ChangeFeedPageState state: Iterator progress updated by parsing and response completion.
    :param float or None deadline: Shared monotonic deadline for the exposed page.
    :return: Continuation and rows, or None when a bootstrap poll requires another fetch.
    :rtype: tuple[str or None, list[dict]] or None
    """

    async def fetch_one() -> list[dict[str, Any]]:
        pages = config.backend.execute_pages(state.prepared_page(deadline), deadline=deadline)
        try:
            page = await pages.__anext__()
        except StopAsyncIteration as error:
            raise RuntimeError("Rust backend returned no change-feed page.") from error
        finally:
            await pages.aclose()
        return state.parse(page)

    rows = await run_with_deadline(fetch_one, deadline)
    return None if state.poll_again else state.finish(rows, deadline)


class AsyncChangeFeedPageIterator(AsyncPageIterator):
    """Keep this iterator's feed cursor, continuation token, and polling progress."""

    def __init__(
        self,
        config: ChangeFeedConfig,
        headers: CaseInsensitiveDict,
        continuation_token: Optional[str] = None,
    ) -> None:
        token = continuation_token if continuation_token is not None else config.options.get("continuation")
        self.state = ChangeFeedPageState(config, headers, token)
        super().__init__(self._fetch, self._unpack, continuation_token=token)

    async def _unpack(self, value: tuple[Optional[str], list[dict[str, Any]]]) -> Any:
        # Pass through the continuation token and rows for the page iterator.
        return value

    async def _fetch(self, _token: Optional[str]) -> tuple[Optional[str], list[dict[str, Any]]]:
        """Await a poll and then complete its result using the shared state.

        A poll starting at a particular time can require another fetch before
        returning. Those fetches share one deadline.

        :param str or None _token: Core pager token; retained state supplies the actual polling position.
        :return: The durable continuation and documents for the completed poll.
        :rtype: tuple[str or None, list[dict]]
        """
        state = self.state
        if state.done:
            raise StopAsyncIteration
        if state.failed:
            raise RuntimeError("change-feed pager failed; resume a new pager from the last delivered bookmark.")
        # A blocking context manager would wait rather than reject overlapping async fetches.
        # The finally block releases this explicitly acquired lock.
        if not state.lock.acquire(blocking=False):  # pylint: disable=consider-using-with
            raise RuntimeError("Concurrent use of a change-feed pager is not supported.")
        try:
            config, deadline = state.config, state.config.deadline()
            state.begin()
            while True:
                result = await _fetch_rust_page(config, state, deadline, **config.recording_options.kwargs)
                if result is not None:
                    return result
        except BaseException as error:
            state.invalidate(error)
            raise
        finally:
            state.lock.release()


def query_items_change_feed(proxy: Any, kwargs: dict[str, Any]) -> CosmosAsyncItemPaged:
    """Return a change-feed pager without starting its first poll.

    :param Any proxy: Container proxy supplying its context and resource link.
    :param dict[str, Any] kwargs: Working change-feed keywords consumed during configuration.
    :return: Lazy async change-feed pager with operation-owned response headers.
    :rtype: ~azure.core.async_paging.AsyncItemPaged
    """
    config = ChangeFeedConfig(proxy, kwargs)
    headers = CaseInsensitiveDict()
    return CosmosAsyncItemPaged(
        config,
        headers,
        page_iterator_class=AsyncChangeFeedPageIterator,
        response_headers=headers,
    )
