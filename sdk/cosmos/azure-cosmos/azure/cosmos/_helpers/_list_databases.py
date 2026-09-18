# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Independent database listing inputs, response state and synchronous paging."""
from __future__ import annotations

import threading
import time
from copy import deepcopy
from dataclasses import replace
from typing import Any, Optional

from azure.core.paging import ItemPaged, PageIterator
from azure.core.utils import CaseInsensitiveDict

from .. import http_constants
from .._backend.errors import BackendProtocolError
from .._backend.contracts import PreparedQuery, QueryPage
from .._constants import _Constants, TimeoutScope
from .._operation_deadline import legacy_deadline_kwargs, legacy_deadline_options, remaining_timeout
from .._query_rust_routing import (
    build_list_databases_prepared_query,
    can_use_rust_backend_for_list_databases_page,
    page_to_backend_response,
)
from ._request_settings import compose_item_options, is_supported_operation_timeout
from ._response_parse import process_backend_response


class ListDatabasesConfig:
    def __init__(self, client: Any, kwargs: dict[str, Any]) -> None:
        started = time.monotonic()
        for option in ("session_token", "populate_query_metrics", "availability_strategy"):
            if option in kwargs:
                raise TypeError(f"list_databases() does not support the '{option}' keyword argument")
        self.hook = kwargs.pop("response_hook", None)
        if self.hook is not None and not callable(self.hook):
            raise TypeError("list_databases response_hook must be callable or None.")
        self.options = deepcopy(compose_item_options(kwargs))
        for source in (self.options, kwargs):
            if source.pop("read_timeout", None) is not None:
                raise TypeError(
                    "list_databases() does not support the 'read_timeout' keyword argument; "
                    "configure it when constructing CosmosClient."
                )
        kwargs.pop("timeout", None)
        self.timeout = self.options.get("timeout")
        if not is_supported_operation_timeout(self.timeout):
            raise ValueError("list_databases timeout must be None or finite seconds >= 1 and < 2**64.")
        self.options.pop(_Constants.OperationStartTime, None)
        self.operation_deadline = (
            started + self.timeout
            if self.timeout is not None and self.options.get(_Constants.TimeoutScope) == TimeoutScope.OPERATION
            else None
        )
        count = self.options.get("maxItemCount")
        if count is not None and (
            isinstance(count, bool) or not isinstance(count, int)
            or count == 0 or count < -1 or count >= 2**63
        ):
            raise ValueError("list_databases max_item_count must be a positive i64 integer, -1, or None.")
        self.kwargs = kwargs
        self.backend = client._backend
        self.rust = self.backend.name != "core-python"
        self.response_state = client._item_context.response_state
        self.default_headers = dict(client.client_connection.default_headers)
        self.connection = None if self.rust else client.client_connection

    def deadline(self) -> Optional[float]:
        if self.operation_deadline is not None:
            return self.operation_deadline
        return None if self.timeout is None else time.monotonic() + self.timeout

    def prepared(self, token: Optional[str], deadline: Optional[float]) -> PreparedQuery:
        if not can_use_rust_backend_for_list_databases_page(
            options=self.options, kwargs=self.kwargs, is_query_plan=False,
            resource_type=http_constants.ResourceType.Database,
        ):
            raise NotImplementedError(
                "list_databases cannot honor these options on Rust; the request will not be sent through legacy Python."
            )
        options = dict(self.options)
        if token is not None:
            options["continuation"] = token
        else:
            options.pop("continuation", None)
        prepared = build_list_databases_prepared_query(options=options, req_headers=self.default_headers)
        return replace(prepared, settings=replace(prepared.settings, timeout_seconds=remaining_timeout(deadline)))

    def legacy_page(
        self, token: Optional[str], deadline: Optional[float],
        response_headers: Optional[CaseInsensitiveDict] = None,
    ) -> Any:
        if self.connection is None:
            raise RuntimeError("A legacy database listing requires its selected connection.")
        options = legacy_deadline_options(self.options, deadline)
        options["continuation"] = token
        # The old transport retries the request, never the customer's success hook.
        return self.connection._CosmosClientConnection__QueryFeed(
            "/dbs", http_constants.ResourceType.Database, "",
            lambda body: body["Databases"], lambda _, body: body, None, options,
            _read_all_backend=self.backend,
            response_headers=response_headers,
            **legacy_deadline_kwargs(self.kwargs, deadline),
        )


class ListDatabasesPageState:
    def __init__(self, config: ListDatabasesConfig, token: Optional[str]) -> None:
        self.config = config
        self.token = token if token is not None else config.options.get("continuation")
        self.failed = False
        self.done = False
        self.lock = threading.Lock()

    def parse(self, page: QueryPage) -> tuple[list[dict[str, Any]], CaseInsensitiveDict]:
        result = process_backend_response(
            page_to_backend_response(page), response_state=self.config.response_state,
        )
        rows = result.get("Databases")
        if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
            raise BackendProtocolError("list_databases received an invalid Databases response.")
        return rows, CaseInsensitiveDict(result.get_response_headers())

    def accept(
        self, response: tuple[list[dict[str, Any]], Any], deadline: Optional[float],
    ) -> list[dict[str, Any]]:
        rows, headers = response
        remaining_timeout(deadline)
        previous = self.token
        self.token = headers.get("x-ms-continuation") or None
        self.done = self.token is None
        if self.config.hook is not None:
            try:
                self.config.hook(dict(headers))
            except (StopIteration, StopAsyncIteration) as error:
                raise RuntimeError("list_databases response_hook raised an iteration-stop exception.") from error
        if not rows and not self.done and self.token == previous:
            raise BackendProtocolError("list_databases returned an empty page without continuation progress.")
        return rows

    def acquire(self) -> None:
        if not self.lock.acquire(blocking=False):
            raise RuntimeError("Concurrent use of a list_databases pager is not supported.")
        if self.failed:
            self.lock.release()
            raise RuntimeError("list_databases pager failed; resume a new pager from the last delivered bookmark.")


class ListDatabasesPageIterator(PageIterator):
    def __init__(self, config: ListDatabasesConfig, continuation_token: Optional[str] = None) -> None:
        self.state = ListDatabasesPageState(config, continuation_token)
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
        while True:
            remaining_timeout(deadline)
            if state.config.rust:
                pages = state.config.backend.execute_pages(
                    state.config.prepared(state.token, deadline), deadline=deadline,
                )
                try:
                    page = next(pages)
                except StopIteration as error:
                    raise BackendProtocolError("Rust backend returned no list_databases page.") from error
                finally:
                    pages.close()
                response = state.parse(page)
            else:
                response = state.config.legacy_page(state.token, deadline)
            rows = state.accept(response, deadline)
            if rows:
                return state.token, rows
            if state.done:
                self.continuation_token = None
                raise StopIteration


def list_databases(client: Any, kwargs: dict[str, Any]) -> ItemPaged[dict[str, Any]]:
    return ItemPaged(ListDatabasesConfig(client, kwargs), page_iterator_class=ListDatabasesPageIterator)
