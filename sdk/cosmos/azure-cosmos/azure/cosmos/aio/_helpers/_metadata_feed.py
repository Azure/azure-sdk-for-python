# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Await metadata pages while retaining each iterator's own bookmark."""
from typing import Any, Awaitable, Callable, Optional

from azure.core.async_paging import AsyncPageIterator
from azure.core.utils import CaseInsensitiveDict

from ..._backend.errors import BindingProtocolError
from ..._helpers._metadata_feed import MetadataFeedConfig, MetadataFeedPageState
from ..._operation_deadline import remaining_timeout, run_with_deadline
from ..._telemetry import trace_operation_async


class AsyncMetadataFeedPageIterator(AsyncPageIterator):
    """Await database or container pages using shared response rules.

    :param MetadataFeedConfig config: Operation-specific request preparation.
    :param str continuation_token: Optional bookmark from an earlier page.
    """

    def __init__(self, config: MetadataFeedConfig, continuation_token: Optional[str] = None) -> None:
        self.state = MetadataFeedPageState(config, continuation_token)
        super().__init__(self._fetch, self._unpack, continuation_token=self.state.token)

    async def _unpack(self, value: Any) -> Any:
        return value

    async def __anext__(self) -> Any:
        """Prevent overlapping fetches and mark failures, including cancellation.

        :return: The next page of rows.
        :rtype: Any
        """
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

        :param str _token: Unused azure-core token; the page state owns its bookmark.
        :return: The next bookmark and rows.
        :rtype: tuple
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

        async def fetch_and_accept(_owner: Any, **_tracing_kwargs: Any) -> list[Any]:
            remaining_timeout(deadline)
            response = await run_with_deadline(fetch, deadline)
            return state.accept(response, deadline)

        fetch_page: Callable[..., Awaitable[list[Any]]] = fetch_and_accept
        if state.config.telemetry_owner is not None:
            fetch_page = trace_operation_async(
                binding_operation=state.config.binding_operation,
                operation_name=state.config.operation,
                name_of_span=f"{state.config.owner_name}.{state.config.operation}.fetch",
            )(fetch_page)
        tracing_kwargs = {
            key: state.config.kwargs[key]
            for key in ("tracing_options", "tracing_attributes")
            if key in state.config.kwargs
        }
        while True:
            rows = await fetch_page(state.config.telemetry_owner, **tracing_kwargs)
            if rows:
                return state.token, rows
            if state.done:
                self.continuation_token = None
                raise StopAsyncIteration
