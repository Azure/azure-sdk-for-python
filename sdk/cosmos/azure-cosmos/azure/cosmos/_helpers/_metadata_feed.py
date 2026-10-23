# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Page database and container metadata without sharing enumeration state."""
from __future__ import annotations

import threading
from typing import Any, Callable, Optional, Protocol

from azure.core.paging import PageIterator
from azure.core.utils import CaseInsensitiveDict

from .._backend.contracts import BackendPage, PreparedPageRequest
from .._backend.errors import BindingProtocolError
from .._operation_deadline import remaining_timeout
from .._query_rust_routing import page_to_backend_response
from .._telemetry import trace_operation
from ._response_parse import process_backend_response


class MetadataFeedConfig(Protocol):
    """Operation-specific preparation used by both metadata page iterators."""

    operation: str
    response_key: str
    owner_name: str
    options: dict[str, Any]
    kwargs: dict[str, Any]
    hook: Optional[Callable[..., Any]]
    backend: Any
    response_state: Any
    telemetry_owner: Any
    rust: bool

    @property
    def query_payload(self) -> Optional[dict[str, Any]]: ...

    @property
    def binding_operation(self) -> str: ...

    def deadline(self) -> Optional[float]: ...

    def prepared(self, token: Optional[str], deadline: Optional[float]) -> PreparedPageRequest: ...

    def legacy_page(
        self, token: Optional[str], deadline: Optional[float],
        response_headers: Optional[CaseInsensitiveDict] = None,
    ) -> Any: ...


class MetadataFeedPageState:
    def __init__(self, config: MetadataFeedConfig, token: Optional[str]) -> None:
        self.config = config
        self.token = token if token is not None else config.options.get("continuation")
        self.failed = False
        self.done = False
        self.lock = threading.Lock()

    def parse(self, page: BackendPage) -> tuple[list[Any], CaseInsensitiveDict]:
        result = process_backend_response(
            page_to_backend_response(page), response_state=self.config.response_state,
        )
        rows = result.get(self.config.response_key)
        if not isinstance(rows, list) or (
            self.config.query_payload is None and any(not isinstance(row, dict) for row in rows)
        ):
            raise BindingProtocolError(
                f"{self.config.operation} received an invalid {self.config.response_key} response."
            )
        return rows, CaseInsensitiveDict(result.get_response_headers())

    def accept(
        self, response: tuple[list[Any], Any], deadline: Optional[float],
    ) -> list[Any]:
        rows, headers = response
        remaining_timeout(deadline)
        previous = self.token
        self.token = headers.get("x-ms-continuation") or None
        self.done = self.token is None
        if self.config.hook is not None:
            try:
                self.config.hook(dict(headers))
            except (StopIteration, StopAsyncIteration) as error:
                raise RuntimeError(
                    f"{self.config.operation} response_hook raised an iteration-stop exception."
                ) from error
        if not rows and not self.done and self.token == previous:
            raise BindingProtocolError(f"{self.config.operation} returned an empty page without continuation progress.")
        return rows

    def acquire(self) -> None:
        if not self.lock.acquire(blocking=False):  # pylint: disable=consider-using-with
            raise RuntimeError(f"Concurrent use of a {self.config.operation} pager is not supported.")
        if self.failed:
            self.lock.release()
            raise RuntimeError(
                f"{self.config.operation} pager failed; resume a new pager from the last delivered bookmark."
            )


class MetadataFeedPageIterator(PageIterator):
    def __init__(self, config: MetadataFeedConfig, continuation_token: Optional[str] = None) -> None:
        self.state = MetadataFeedPageState(config, continuation_token)
        super().__init__(self._fetch, lambda value: value, continuation_token=self.state.token)

    def __next__(self) -> Any:
        self.state.acquire()
        try:
            return super().__next__()
        except StopIteration:
            raise
        except BaseException:
            self.state.failed = True
            raise
        finally:
            self.state.lock.release()

    next = __next__

    def _fetch(self, _token: Optional[str]) -> Any:
        state = self.state
        if state.done:
            raise StopIteration
        deadline = state.config.deadline()

        def fetch(_owner: Any, **_tracing_kwargs: Any) -> list[Any]:
            remaining_timeout(deadline)
            if state.config.rust:
                pages = state.config.backend.execute_pages(
                    state.config.prepared(state.token, deadline), deadline=deadline,
                )
                try:
                    page = next(pages)
                except StopIteration as error:
                    raise BindingProtocolError(f"Rust backend returned no {state.config.operation} page.") from error
                finally:
                    pages.close()
                response = state.parse(page)
            else:
                response = state.config.legacy_page(state.token, deadline)
            return state.accept(response, deadline)

        if state.config.telemetry_owner is not None:
            fetch = trace_operation(
                binding_operation=state.config.binding_operation,
                operation_name=state.config.operation,
                name_of_span=f"{state.config.owner_name}.{state.config.operation}.fetch",
            )(fetch)
        tracing_kwargs = {
            key: state.config.kwargs[key]
            for key in ("tracing_options", "tracing_attributes")
            if key in state.config.kwargs
        }
        while True:
            rows = fetch(state.config.telemetry_owner, **tracing_kwargs)
            if rows:
                return state.token, rows
            if state.done:
                self.continuation_token = None
                raise StopIteration
