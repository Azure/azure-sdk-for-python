# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Read Rust read-many pages as needed, without saved continuation tokens."""

from __future__ import annotations

import time
from typing import Any, Iterator, Optional

from azure.core.utils import CaseInsensitiveDict

from .._backend.contracts import BackendPage
from .._backend.capabilities import reject_rust_arguments
from .._cosmos_responses import CosmosItemPaged
from .._telemetry import trace_operation
from ._feed_paging import FeedConfig, FeedPageState


def validate_read_all_continuation_token(token: Optional[str]) -> None:
    if token is not None:
        raise ValueError("read_all_items does not support continuation tokens; continue using the same iterator.")


class ReadAllConfig(FeedConfig):
    """Use the client's Rust adapter without accessing a legacy connection."""

    def __init__(self, proxy: Any, kwargs: dict[str, Any], *, operation: str = "read_all_items") -> None:
        context = proxy._item_context
        if context is None or context.adapter.name == "core-python":
            raise NotImplementedError(f"{operation} requires a client-owned Rust backend; no legacy fallback.")
        context.defaults.apply_timeout(kwargs)
        reject_rust_arguments(kwargs)
        super().__init__(proxy, kwargs, operation=operation, backend=context.adapter)
        if operation == "read_all_items":
            validate_read_all_continuation_token(self.options.get("continuation"))

    def deadline(self) -> Optional[float]:
        return None if self.timeout is None else time.monotonic() + self.timeout


class ReadAllPageState(FeedPageState):
    """Use the cursor's has_more flag to tell when all items have been read."""

    config: ReadAllConfig

    def __init__(self, config: ReadAllConfig, headers: CaseInsensitiveDict, token: Optional[str]) -> None:
        validate_read_all_continuation_token(token)
        super().__init__(config, headers, None)
        self.more = True

    def parse(self, page: BackendPage) -> list[dict[str, Any]]:
        rows = super().parse(page)
        if page.continuation is not None or not isinstance(page.has_more, bool):
            raise RuntimeError("read_all_items requires non-resumable Rust cursor progress.")
        self.more = page.has_more
        return rows

    def is_done(self) -> bool:
        return not self.more


@trace_operation(
    binding_operation="read_all_items",
    operation_name="read_all_items",
    name_of_span="ContainerProxy.read_all_items.fetch",
)
def _fetch_rust_page(
    config: ReadAllConfig, state: ReadAllPageState, deadline: Optional[float], **_tracing_kwargs: Any
) -> Optional[list[dict[str, Any]]]:
    pages = config.backend.execute_pages(config.prepared(None, state.cursor, deadline), deadline=deadline)
    try:
        page = next(pages)
    except StopIteration as error:
        raise RuntimeError("Rust backend returned no read_all_items page.") from error
    finally:
        close = getattr(pages, "close", None)
        if close is not None:
            close()
    rows = state.parse(page)
    return state.finish(rows, deadline)[1] if rows or state.is_done() else None


class ReadAllPageIterator(Iterator[Iterator[dict[str, Any]]]):
    """Keep the cursor between pages; time spent processing a page does not count toward its fetch timeout."""

    def __init__(
        self, config: ReadAllConfig, headers: CaseInsensitiveDict, continuation_token: Optional[str] = None
    ) -> None:
        self.state = ReadAllPageState(config, headers, continuation_token)

    @property
    def continuation_token(self) -> None:
        raise NotImplementedError("read_all_items cannot be bookmarked; continue using this iterator.")

    def __next__(self) -> Iterator[dict[str, Any]]:
        state = self.state
        if state.done:
            raise StopIteration
        if state.failed:
            raise RuntimeError("read_all_items pager failed; a new enumeration starts from the beginning.")
        if not state.lock.acquire(blocking=False):
            raise RuntimeError("Concurrent use of a read_all_items pager is not supported.")
        try:
            config = state.config
            deadline = config.deadline()
            state.begin()
            while True:
                rows = _fetch_rust_page(config, state, deadline, **config.recording_options.kwargs)
                if rows is not None:
                    break
        except BaseException as error:
            state.invalidate(error)
            raise
        finally:
            state.lock.release()
        if not rows and state.done:
            raise StopIteration
        return iter(rows)


def read_all_items(proxy: Any, kwargs: dict[str, Any]) -> CosmosItemPaged:
    config = ReadAllConfig(proxy, kwargs)
    headers = CaseInsensitiveDict()
    return CosmosItemPaged(config, headers, page_iterator_class=ReadAllPageIterator, response_headers=headers)
