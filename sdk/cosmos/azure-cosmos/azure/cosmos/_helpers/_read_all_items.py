# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Shared retained-feed configuration, page accounting and read-all paging."""

from __future__ import annotations

from .._backend.partition_key_input import BindingPartitionKey

import threading
import time
from copy import deepcopy
from dataclasses import replace
from ._request_settings import (
    build_request_headers_and_settings,
    compose_options_from_kwargs,
    HEADERS_THE_DRIVER_REGENERATES,
    is_supported_operation_timeout,
)
from typing import TYPE_CHECKING, Any, Mapping, Optional

from azure.core.exceptions import AzureError
from azure.core.paging import PageIterator
from azure.core.utils import CaseInsensitiveDict

from .._backend.contracts import PreparedQuery, QueryPage
from .._backend.operations import OP_READ_ALL_ITEMS
from .._constants import _Constants as Constants
from .._cosmos_responses import CosmosDict, CosmosItemPaged
from ..exceptions import CosmosClientTimeoutError
from .._operation_deadline import legacy_deadline_options, remaining_timeout
from ._read_items import ReadItemsHeaders
from ._response_parse import process_backend_response
from .._query_rust_routing import page_to_backend_response


def validate_bookmark(token: Optional[str], rust: bool) -> None:
    if token is None:
        return
    if not isinstance(token, str) or not token:
        raise ValueError(
            "read_all_items continuation must be a nonempty string or None."
        )
    if token.startswith("c1.") != rust:
        raise ValueError(
            "read_all_items continuation belongs to an incompatible backend."
        )


if TYPE_CHECKING:
    from azure.cosmos._rust import _ItemFeedCursor


class ReadAllConfig:
    def __init__(
        self, proxy: Any, kwargs: dict[str, Any], *, operation: str = "read_all_items"
    ) -> None:
        self.operation = operation
        if operation != "query_items" and "populate_query_metrics" in kwargs:
            raise TypeError(f"{operation}() does not accept 'populate_query_metrics'.")
        self.hook = kwargs.pop("response_hook", None)
        if self.hook is not None and not callable(self.hook):
            raise TypeError(f"{operation} response_hook must be callable or None.")
        kwargs["request_options"] = deepcopy(
            kwargs.get("request_options", kwargs.pop("feed_options", {})) or {}
        )
        self.options = deepcopy(compose_options_from_kwargs(kwargs))
        for key in ("timeout", "read_timeout"):
            if key in kwargs:
                self.options[key] = kwargs.pop(key)
        self.timeout = self.options.get("timeout")
        if not is_supported_operation_timeout(self.timeout):
            raise ValueError(
                f"{operation} timeout must be None or finite seconds >= 1 and < 2**64."
            )
        count = self.options.get("maxItemCount")
        if count is not None and (
            isinstance(count, bool)
            or not isinstance(count, int)
            or count == 0
            or count < -1
        ):
            raise ValueError(
                f"{operation} max_item_count must be a positive integer, -1, or None."
            )
        cache = self.options.get("maxIntegratedCacheStaleness")
        if cache is not None and (
            isinstance(cache, bool) or not isinstance(cache, int) or cache < 0
        ):
            raise ValueError(
                f"{operation} cache staleness must be a nonnegative integer or None."
            )
        if operation != "query_items" and "populateQueryMetrics" in self.options:
            raise TypeError(f"{operation}() does not accept query metrics.")
        self.proxy = proxy
        self.connection = proxy.client_connection
        context = proxy._item_context
        self.response_state = context.response_state if context is not None else None
        self.backend = (
            context.backend if context is not None else self.connection._backend
        )
        self.rust = self.backend.name != "core-python"
        if self.rust:
            allowed = {
                "maxItemCount",
                "sessionToken",
                "initialHeaders",
                "priorityLevel",
                "throughputBucket",
                "excludedLocations",
                "maxIntegratedCacheStaleness",
                "timeout",
                "continuation",
                "consistencyLevel",
            }
            if operation == "query_items":
                allowed |= {
                    "populateQueryMetrics", "populateIndexMetrics", "populateQueryAdvice",
                    "enableScanInQuery", "availabilityStrategy", "correlatedActivityId",
                }
            initial = self.options.get("initialHeaders")
            if initial is not None and not isinstance(initial, dict):
                raise TypeError(f"{operation} initial_headers must be a dict or None.")
            if any(not isinstance(name, str) for name in (initial or {})):
                raise TypeError(f"{operation} initial_headers names must be strings.")
            reserved = HEADERS_THE_DRIVER_REGENERATES | {
                "x-ms-continuation",
                "x-ms-documentdb-partitionkey",
                "x-ms-documentdb-partitionkeyrangeid",
                "x-ms-documentdb-query-enablecrosspartition",
                "x-ms-documentdb-isquery",
                "x-ms-cosmos-is-query-plan-request",
            }
            if (
                kwargs
                or set(self.options) - allowed
                or any(name.lower() in reserved for name in (initial or {}))
            ):
                raise NotImplementedError(
                    f"{operation} cannot honor these options on Rust; no legacy fallback will be used."
                )
        if self.rust and context is not None:
            context.defaults.apply_to_options(self.options)
        self.kwargs = kwargs
        if operation == "read_all_items":
            validate_bookmark(self.options.get("continuation"), self.rust)

    def deadline(self) -> Optional[float]:
        return None if self.timeout is None else time.monotonic() + self.timeout

    def prepared(
        self, token: Optional[str], cursor: Optional[_ItemFeedCursor], deadline: Optional[float]
    ) -> PreparedQuery:
        if cursor is None:
            raise RuntimeError("Retained paging requires a pager-owned cursor.")
        options = dict(self.options)
        options.pop("continuation", None)
        options.pop("maxItemCount", None)
        headers, settings = build_request_headers_and_settings(options)
        # The overall time limit covers metadata lookup and planning as
        # well. Timeouts set on individual driver requests cannot extend
        # past it.
        remaining = remaining_timeout(deadline)
        if remaining is not None:
            settings = replace(settings, timeout_seconds=remaining)
        return PreparedQuery(
            op=OP_READ_ALL_ITEMS,
            container_link=self.proxy.container_link,
            partition_key=BindingPartitionKey("cross_partition"),
            continuation=token,
            max_item_count=self.options.get("maxItemCount"),
            headers=headers,
            settings=settings,
            cursor=cursor,
        )


class ReadAllPageState:
    def __init__(
        self, config: ReadAllConfig, headers: CaseInsensitiveDict, token: Optional[str]
    ) -> None:
        if config.operation == "read_all_items":
            validate_bookmark(token, config.rust)
        self.config = config
        self.headers = headers
        self.token = token
        self.cursor: Optional[_ItemFeedCursor] = None
        self.failed = False
        self.done = False
        self.legacy_options: dict[str, Any] = {}
        self.legacy_pages: Any = None
        self.captured = CaseInsensitiveDict()
        self.envelope: dict[str, Any] = {}
        self.accumulated = ReadItemsHeaders()
        self.responses = 0
        self.has_charge = False
        self.lock = threading.Lock()

    def begin(self) -> None:
        if self.config.rust and self.cursor is None:
            cursor = self.config.backend.create_item_feed_cursor()
            if not hasattr(cursor, "can_retry_setup"):
                raise RuntimeError(
                    "The compiled extension lacks _ItemFeedCursor.can_retry_setup; "
                    "rebuild it from the current source."
                )
            self.cursor = cursor
        self.accumulated = ReadItemsHeaders()
        self.responses = 0
        self.has_charge = False

    def invalidate(self, error: BaseException) -> None:
        # Only the binding can establish that no plan has begun execution.
        # Timeouts/cancellation remain terminal, including in-flight shutdown.
        if (
            self.config.rust
            and isinstance(error, AzureError)
            and not isinstance(error, CosmosClientTimeoutError)
            and self.cursor is not None
            and self.cursor.can_retry_setup
        ):
            return
        self.failed = True
        self.cursor = None
        self.legacy_pages = None

    def capture(self, headers: Any, body: Any) -> None:
        self.responses += 1
        self.has_charge = (
            self.has_charge or "x-ms-request-charge" in CaseInsensitiveDict(headers)
        )
        self.accumulated(headers, None)
        self.captured.clear()
        self.captured.update(headers)
        if isinstance(body, Mapping):
            self.envelope = dict(body)

    def parse(self, page: QueryPage) -> list[dict[str, Any]]:
        result = process_backend_response(
            page_to_backend_response(page),
            response_state=(
                self.config.response_state
                if page.headers or page.continuation is not None
                else None
            ),
        )
        if not isinstance(result, dict) or not isinstance(
            result.get("Documents"), list
        ):
            raise ValueError(
                f"{self.config.operation} received an invalid Documents response envelope."
            )
        rows = result["Documents"]
        if self.config.operation != "query_items" and any(not isinstance(row, dict) for row in rows):
            raise ValueError("read_all_items received a non-object document.")
        # A None returned by execute_plan means this pager has finished
        # locally. It is not a service response, so do not invent a
        # response hook call or a request charge for it.
        if rows or page.continuation is not None or page.headers:
            self.capture(result.get_response_headers(), result)
        self.token = page.continuation
        if self.token is None:
            self.captured.pop("x-ms-continuation", None)
        else:
            self.captured["x-ms-continuation"] = self.token
        return rows

    def finish(
        self, rows: list[dict[str, Any]], deadline: Optional[float]
    ) -> tuple[Optional[str], list[dict[str, Any]]]:
        remaining_timeout(deadline)
        hook = self.config.hook
        headers = CaseInsensitiveDict(
            self.accumulated.headers if self.responses else self.headers
        )
        if self.responses and not self.has_charge:
            headers.pop("x-ms-request-charge", None)
        if self.token is None:
            headers.pop("x-ms-continuation", None)
        else:
            headers["x-ms-continuation"] = self.token
        if hook is not None and self.responses:
            body = deepcopy(self.envelope)
            body["Documents"] = deepcopy(rows)
            if "_count" in body:
                body["_count"] = len(rows)
            try:
                hook(
                    CaseInsensitiveDict(headers),
                    CosmosDict(body, response_headers=CaseInsensitiveDict(headers)),
                )
            except (StopIteration, StopAsyncIteration) as error:
                raise RuntimeError(
                    f"{self.config.operation} response_hook raised an iteration-stop exception."
                ) from error
        self.headers.clear()
        self.headers.update(headers)
        self.done = self.is_done()
        if self.done:
            self.cursor = None
            self.legacy_pages = None
        return self.token, rows

    def is_done(self) -> bool:
        return self.token is None


class ReadAllPageIterator(PageIterator):
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

    @staticmethod
    def _unpack(value: tuple[Optional[str], list[dict[str, Any]]]) -> Any:
        # azure-core types this callback as never receiving the None it sends
        # to mark the end of iteration, so the annotation here is narrower than
        # what can actually arrive. The value is passed straight through.
        return value

    def _fetch(
        self, _token: Optional[str]
    ) -> tuple[Optional[str], list[dict[str, Any]]]:
        state = self.state
        if state.done:
            raise StopIteration
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
                    previous = state.token
                    pages = config.backend.execute_pages(
                        config.prepared(state.token, state.cursor, deadline),
                        deadline=deadline,
                    )
                    try:
                        page = next(pages)
                    except StopIteration as exc:
                        raise RuntimeError(
                            "Rust backend returned no read_all_items page."
                        ) from exc
                    finally:
                        pages.close()
                    rows = state.parse(page)
                    if rows or state.token is None:
                        break
                    if state.token == previous:
                        raise RuntimeError(
                            "read_all_items returned an empty page without continuation progress."
                        )
            else:
                state.legacy_options.update(
                    legacy_deadline_options(config.options, deadline)
                )
                if state.legacy_pages is None:
                    properties = config.proxy._get_properties_with_options(
                        state.legacy_options
                    )
                    state.legacy_options[Constants.ContainerRID] = properties["_rid"]
                    remaining_timeout(deadline)
                    state.legacy_options["_read_all_response_headers"] = state.captured
                    items = config.connection.ReadItems(
                        collection_link=config.proxy.container_link,
                        feed_options=state.legacy_options,
                        response_hook=state.capture,
                        _read_all_backend=config.backend,
                        **config.kwargs,
                    )
                    state.legacy_pages = items.by_page(continuation_token=state.token)
                try:
                    rows = list(next(state.legacy_pages))
                except StopIteration:
                    rows = []
                    state.token = None
                else:
                    state.token = state.legacy_pages.continuation_token
            result = state.finish(rows, deadline)
            if not rows and state.done:
                raise StopIteration
            return result
        except StopIteration:
            raise
        except BaseException as error:
            state.invalidate(error)
            raise
        finally:
            state.lock.release()


def read_all_items(proxy: Any, kwargs: dict[str, Any]) -> CosmosItemPaged:
    config = ReadAllConfig(proxy, kwargs)
    headers = CaseInsensitiveDict()
    return CosmosItemPaged(
        config,
        headers,
        page_iterator_class=ReadAllPageIterator,
        response_headers=headers,
    )
