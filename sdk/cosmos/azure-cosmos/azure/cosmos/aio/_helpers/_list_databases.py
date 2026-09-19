# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Async database listing with pager-owned state and a budget per page fetch."""
from typing import Any, Optional

from azure.core.async_paging import AsyncItemPaged, AsyncPageIterator
from azure.core.utils import CaseInsensitiveDict

from ..._backend.errors import BindingProtocolError
from ..._helpers._list_databases import ListDatabasesConfig, ListDatabasesPageState
from ..._operation_deadline import remaining_timeout, run_with_deadline


class AsyncListDatabasesPageIterator(AsyncPageIterator):
    def __init__(self, config: ListDatabasesConfig, continuation_token: Optional[str] = None) -> None:
        self.state = ListDatabasesPageState(config, continuation_token)
        super().__init__(self._fetch, self._unpack, continuation_token=self.state.token)

    async def _unpack(self, value: Any) -> Any:
        return value

    async def __anext__(self) -> Any:
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
                raise BindingProtocolError("Rust backend returned no list_databases page.") from error
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
    return AsyncItemPaged(ListDatabasesConfig(client, kwargs), page_iterator_class=AsyncListDatabasesPageIterator)
