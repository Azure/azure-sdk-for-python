# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Shared feed request preparation, response parsing, and per-page state."""

from __future__ import annotations

import threading
import time
from copy import deepcopy
from dataclasses import replace
from typing import TYPE_CHECKING, Any, Mapping, Optional

from azure.core.exceptions import AzureError
from azure.core.utils import CaseInsensitiveDict

from .._backend.contracts import PreparedPageRequest, BackendPage
from .._backend.partition_key_input import BindingPartitionKey
from .._cosmos_responses import CosmosDict
from ..exceptions import CosmosClientTimeoutError
from .._operation_deadline import remaining_timeout
from .._telemetry import RecordingOptions
from ._read_items import ResponseHeaderAccumulator
from ._request_settings import (
    build_request_headers_and_settings,
    compose_options_from_kwargs,
    HEADERS_THE_DRIVER_REGENERATES,
    is_supported_operation_timeout,
)
from ._response_parse import page_to_backend_response, process_backend_response


if TYPE_CHECKING:
    from azure.cosmos._rust import _ItemFeedCursor


class FeedConfig:
    """Copy the options and keep the adapter used to fetch pages."""

    def __init__(
        self, proxy: Any, kwargs: dict[str, Any], *, operation: str, backend: Any, retained: bool = True
    ) -> None:
        self.operation = operation
        if operation != "query_items" and "populate_query_metrics" in kwargs:
            raise TypeError(f"{operation}() does not accept 'populate_query_metrics'.")
        self.hook = kwargs.pop("response_hook", None)
        if self.hook is not None and not callable(self.hook):
            raise TypeError(f"{operation} response_hook must be callable or None.")
        kwargs["request_options"] = deepcopy(kwargs.get("request_options", kwargs.pop("feed_options", {})) or {})
        self.options = deepcopy(compose_options_from_kwargs(kwargs))
        if "timeout" in kwargs:
            self.options["timeout"] = kwargs.pop("timeout")
        self.timeout = self.options.get("timeout")
        if not is_supported_operation_timeout(self.timeout):
            raise ValueError(f"{operation} timeout must be None or finite seconds >= 1 and < 2**64.")
        count = self.options.get("maxItemCount")
        if count is not None and (isinstance(count, bool) or not isinstance(count, int) or count == 0 or count < -1):
            raise ValueError(f"{operation} max_item_count must be a positive integer, -1, or None.")
        cache = self.options.get("maxIntegratedCacheStaleness")
        if cache is not None and (isinstance(cache, bool) or not isinstance(cache, int) or cache < 0):
            raise ValueError(f"{operation} cache staleness must be a nonnegative integer or None.")
        if operation != "query_items" and "populateQueryMetrics" in self.options:
            raise TypeError(f"{operation}() does not accept query metrics.")
        self.proxy = proxy
        context = proxy._item_context
        self._item_context = context
        self.response_state = context.response_state if context is not None else None
        self.backend = backend
        self.rust = retained
        self.recording_options = RecordingOptions.take(kwargs) if self.rust else RecordingOptions.snapshot({})
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
                    "populateQueryMetrics",
                    "populateIndexMetrics",
                    "populateQueryAdvice",
                    "enableScanInQuery",
                    "availabilityStrategy",
                    "correlatedActivityId",
                    "responseContinuationTokenLimitInKb",
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
            if kwargs or set(self.options) - allowed or any(name.lower() in reserved for name in (initial or {})):
                raise NotImplementedError(
                    f"{operation} cannot honor these options on Rust; no legacy fallback will be used."
                )
        if self.rust and context is not None:
            context.defaults.apply_to_options(self.options)
        self.kwargs = kwargs

    def deadline(self) -> Optional[float]:
        return None if self.timeout is None else time.monotonic() + self.timeout

    def prepared(
        self,
        token: Optional[str],
        cursor: Optional[_ItemFeedCursor],
        deadline: Optional[float],
    ) -> PreparedPageRequest:
        """Build a page request with its existing cursor.

        The adapter passes the cursor separately to the binding, not in the request body.
        """
        if cursor is None:
            raise RuntimeError("Retained paging requires a pager-owned cursor.")
        options = dict(self.options)
        options.pop("continuation", None)
        options.pop("maxItemCount", None)
        headers, settings = build_request_headers_and_settings(options)
        # Metadata, planning and page requests share the same timeout.
        remaining = remaining_timeout(deadline)
        if remaining is not None:
            settings = replace(settings, timeout_seconds=remaining)
        return PreparedPageRequest(
            op=self.operation,
            container_link=self.proxy.container_link,
            partition_key=BindingPartitionKey("cross_partition"),
            continuation=token,
            max_item_count=self.options.get("maxItemCount"),
            headers=headers,
            settings=settings,
            cursor=cursor,
        )


class FeedPageState:
    """Keep one page iterator's progress and per-fetch response information."""

    def __init__(self, config: FeedConfig, headers: CaseInsensitiveDict, token: Optional[str]) -> None:
        self.config = config
        self.headers = headers
        self.token = token
        self.cursor: Optional[_ItemFeedCursor] = None
        self.failed = False
        self.done = False
        self.captured = CaseInsensitiveDict()
        self.envelope: dict[str, Any] = {}
        self.accumulated = ResponseHeaderAccumulator()
        self.responses = 0
        self.has_charge = False
        self.lock = threading.Lock()

    def begin(self) -> None:
        """Create a feed cursor if needed and reset the next fetch's response totals."""
        if self.config.rust and self.cursor is None:
            cursor = self.config.backend.create_item_feed_cursor()
            if not hasattr(cursor, "can_retry_setup"):
                raise RuntimeError(
                    "The compiled extension lacks _ItemFeedCursor.can_retry_setup; "
                    "rebuild it from the current source."
                )
            self.cursor = cursor
        self.accumulated = ResponseHeaderAccumulator()
        self.responses = 0
        self.has_charge = False

    def invalidate(self, error: BaseException) -> None:
        # Retry setup only when the binding confirms execution has not started.
        # A timeout or cancellation always makes this iterator unusable.
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

    def capture(self, headers: Any, body: Any) -> None:
        self.responses += 1
        self.has_charge = self.has_charge or "x-ms-request-charge" in CaseInsensitiveDict(headers)
        self.accumulated(headers, None)
        self.captured.clear()
        self.captured.update(headers)
        if isinstance(body, Mapping):
            self.envelope = dict(body)

    def parse(self, page: BackendPage) -> list[dict[str, Any]]:
        result = process_backend_response(
            page_to_backend_response(page),
            response_state=(self.config.response_state if page.headers or page.continuation is not None else None),
        )
        if not isinstance(result, dict) or not isinstance(result.get("Documents"), list):
            raise ValueError(f"{self.config.operation} received an invalid Documents response envelope.")
        rows = result["Documents"]
        if self.config.operation != "query_items" and any(not isinstance(row, dict) for row in rows):
            raise ValueError("read_all_items received a non-object document.")
        # The cursor can finish without another service backend response.
        # In that case, do not add a hook call or a request charge.
        if rows or page.continuation is not None or page.headers:
            self.capture(result.get_response_headers(), result)
        self.token = page.continuation
        if self.token is None:
            self.captured.pop("x-ms-continuation", None)
        else:
            self.captured["x-ms-continuation"] = self.token
        return rows

    def notify_response(self, headers: Mapping[str, Any], body: Mapping[str, Any]) -> None:
        hook = self.config.hook
        if hook is not None:
            try:
                hook(
                    CaseInsensitiveDict(deepcopy(headers)),
                    CosmosDict(deepcopy(body), response_headers=CaseInsensitiveDict(deepcopy(headers))),
                )
            except (StopIteration, StopAsyncIteration) as error:
                raise RuntimeError(
                    f"{self.config.operation} response_hook raised an iteration-stop exception."
                ) from error

    def finish(
        self, rows: list[dict[str, Any]], deadline: Optional[float], *, notify_hook: bool = True
    ) -> tuple[Optional[str], list[dict[str, Any]]]:
        remaining_timeout(deadline)
        headers = CaseInsensitiveDict(self.accumulated.headers if self.responses else self.headers)
        if self.responses and not self.has_charge:
            headers.pop("x-ms-request-charge", None)
        if self.token is None:
            headers.pop("x-ms-continuation", None)
        else:
            headers["x-ms-continuation"] = self.token
        if notify_hook and self.responses:
            body = dict(self.envelope)
            body["Documents"] = rows
            if "_count" in body:
                body["_count"] = len(rows)
            self.notify_response(headers, body)
        self.headers.clear()
        self.headers.update(headers)
        self.done = self.is_done()
        if self.done:
            self.cursor = None
        return self.token, rows

    def is_done(self) -> bool:
        return self.token is None

