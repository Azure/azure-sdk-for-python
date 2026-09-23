# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""List or query databases using an async page iterator and stateless paging.

The shared ListDatabasesConfig or QueryDatabasesConfig prepares page requests.
Each ListDatabasesPageState keeps one page iterator's continuation token,
without a feed cursor. With a timeout, the config supplies an existing operation
deadline when configured, or a new per-page deadline otherwise.
"""
from typing import Any, Optional

from azure.core.async_paging import AsyncItemPaged, AsyncPageIterator
from azure.core.utils import CaseInsensitiveDict

from ..._backend.errors import BindingProtocolError
from ..._helpers._list_databases import ListDatabasesConfig, ListDatabasesPageState, QueryDatabasesConfig
from ..._operation_deadline import remaining_timeout, run_with_deadline


class AsyncListDatabasesPageIterator(AsyncPageIterator):
    """Await database pages using the shared configuration and response rules."""

    def __init__(self, config: ListDatabasesConfig, continuation_token: Optional[str] = None) -> None:
        self.state = ListDatabasesPageState(config, continuation_token)
        super().__init__(self._fetch, self._unpack, continuation_token=self.state.token)

    async def _unpack(self, value: Any) -> Any:
        return value

    async def __anext__(self) -> Any:
        """Prevent overlapping fetches and mark failures, including cancellation."""
        self.state.acquire()
        try:
            return await super().__anext__()
        except StopAsyncIteration:
            raise
        except BaseException:
            self.state.failed = True
            raise
        finally:
            self.state.lock.release()

    async def _fetch(self, _token: Optional[str]) -> Any:
        """Skip empty pages under one deadline and return the next rows and token.

        The backend page is parsed before state.accept() calls the synchronous
        response hook. Errors do not switch to the legacy path.
        """
        state = self.state
        if state.done:
            raise StopAsyncIteration
        deadline = state.config.deadline()

        async def fetch() -> Any:
            if not state.config.rust:
                headers = CaseInsensitiveDict()
                rows = await state.config.legacy_page(state.token, deadline, headers)
                return rows, headers
            pages = state.config.backend.execute_pages(
                state.config.prepared(state.token, deadline), deadline=deadline,
            )
            try:
                page = await pages.__anext__()
            except StopAsyncIteration as error:
                raise BindingProtocolError(f"Rust backend returned no {state.config.operation} page.") from error
            finally:
                await pages.aclose()
            return state.parse(page)

        while True:
            remaining_timeout(deadline)
            response = await run_with_deadline(fetch, deadline)
            rows = state.accept(response, deadline)
            if rows:
                return state.token, rows
            if state.done:
                self.continuation_token = None
                raise StopAsyncIteration


def list_databases(client: Any, kwargs: dict[str, Any]) -> AsyncItemPaged[dict[str, Any]]:
    """Return a database-listing pager; no page is fetched until async iteration."""
    return AsyncItemPaged(ListDatabasesConfig(client, kwargs), page_iterator_class=AsyncListDatabasesPageIterator)


def query_databases(client: Any, query: Any, parameters: Any, kwargs: dict[str, Any]) -> AsyncItemPaged[Any]:
    """Return a database-query pager using the same page iterator as listing."""
    return AsyncItemPaged(
        QueryDatabasesConfig(client, query, parameters, kwargs), page_iterator_class=AsyncListDatabasesPageIterator,
    )
