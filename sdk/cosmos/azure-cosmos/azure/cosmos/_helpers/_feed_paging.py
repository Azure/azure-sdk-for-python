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

from .._backend.capabilities import reject_removed_options, reject_rust_arguments
from .._backend.constants import is_rust_backend
from .._backend.contracts import PreparedPageRequest, BackendPage
from .._backend.partition_key_input import BindingPartitionKey
from .._cosmos_responses import CosmosDict
from ..exceptions import CosmosClientTimeoutError
from .._operation_deadline import remaining_timeout
from .._routing.routing_range import Range
from .._telemetry import RecordingOptions
from ._read_items import ResponseHeaderAccumulator
from ._request_settings import (
    build_request_headers_and_settings,
    compose_options_from_kwargs,
    HEADERS_THE_DRIVER_REGENERATES,
    is_supported_operation_timeout,
    reject_unknown_feed_kwargs,
)
from ._response_parse import page_to_backend_response, process_backend_response


if TYPE_CHECKING:
    from azure.cosmos._rust import _ItemFeedCursor


def normalize_feed_range(feed: Any) -> list[str]:
    """Validate a feed scope and normalize SDK-produced inclusive point ranges.

    :param Any feed: Feed-range dictionary containing a Range interval.
    :return: Inclusive minimum and exclusive maximum effective partition-key bounds.
    :rtype: list[str]
    """
    interval = feed.get("Range") if isinstance(feed, dict) else None
    if not isinstance(interval, dict) or (
        not isinstance(interval.get("min"), str)
        or not isinstance(interval.get("max"), str)
        or interval.get("isMinInclusive", True) is not True
    ):
        raise ValueError("feed_range requires a nonempty min-inclusive, max-exclusive Range.")
    if interval["min"] == interval["max"] and interval.get("isMaxInclusive", False) is True:
        if any(char not in "0123456789abcdefABCDEF" for char in interval["min"]):
            raise ValueError("feed_range point bounds must be hexadecimal.")
        interval = Range(interval["min"], interval["max"], True, True).to_normalized_range().to_dict()
    if interval["min"] >= interval["max"] or interval.get("isMaxInclusive", False) is not False:
        raise ValueError("feed_range requires a nonempty min-inclusive, max-exclusive Range.")
    return [interval["min"], interval["max"]]


def _validate_change_feed_options(options: Mapping[str, Any], kwargs: Mapping[str, Any]) -> None:
    """Reject unsupported Rust change-feed options in their established order.

    :param options: Normalized request options.
    :type options: Mapping[str, Any]
    :param kwargs: Remaining operation keyword arguments.
    :type kwargs: Mapping[str, Any]
    :return: None.
    :rtype: None
    """
    if "disableRUPerMinuteUsage" in options:
        raise TypeError(
            "query_items_change_feed() does not accept disable_ru_per_minute_usage "
            "(disableRUPerMinuteUsage) on Rust-backed clients; omit this option. "
            "Per-request RU-per-minute usage control is not supported by this Rust-backed API."
        )
    if "offerEnableRUPerMinuteThroughput" in options:
        raise TypeError(
            "query_items_change_feed() does not accept offer_enable_ru_per_minute_throughput "
            "(offerEnableRUPerMinuteThroughput) on Rust-backed clients; omit this option. "
            "Change-feed reads do not configure container throughput."
        )
    if "retry_write" in options:
        raise TypeError(
            "query_items_change_feed() does not accept retry_write on Rust-backed clients; "
            "omit this option. It applies to writes, not change-feed reads; "
            "read retries remain driver-managed."
        )
    if "responsePayloadOnWriteDisabled" in options:
        raise TypeError(
            "query_items_change_feed() does not accept no_response (responsePayloadOnWriteDisabled) "
            "on Rust-backed clients; omit this option. It applies to write responses, not change-feed reads."
        )
    if "queryVersion" in options:
        raise TypeError(
            "query_items_change_feed() does not accept query_version (queryVersion) "
            "on Rust-backed clients; omit this option. Change feed does not use a SQL query version."
        )
    if "supportedQueryFeatures" in options:
        raise TypeError(
            "query_items_change_feed() does not accept supported_query_features (supportedQueryFeatures) "
            "on Rust-backed clients; omit this option. Change feed does not use a SQL query plan."
        )
    if "isQueryPlanRequest" in options:
        raise TypeError(
            "query_items_change_feed() does not accept is_query_plan_request (isQueryPlanRequest) "
            "on Rust-backed clients; omit this option. Change feed does not use a SQL query plan."
        )
    if "contentType" in options:
        raise TypeError(
            "query_items_change_feed() does not accept content_type (contentType) "
            "on Rust-backed clients; omit this option. The Rust driver manages Content-Type."
        )
    if "accessCondition" in options:
        raise TypeError(
            "query_items_change_feed() does not accept access_condition (accessCondition) "
            "on Rust-backed clients; omit this option. To resume, use continuation instead, "
            "with a token returned by this Rust-backed API."
        )
    if "proxy" in kwargs or "proxy" in options:
        raise TypeError(
            "query_items_change_feed() does not accept per-call proxy on Rust-backed clients; "
            "omit this option. Configure the proxy through environment variables and permit its use "
            "with ConnectionPoolOptions.proxy_allowed on the client's CosmosRuntime."
        )
    if "stream" in kwargs or "stream" in options:
        raise TypeError(
            "query_items_change_feed() does not accept stream on Rust-backed clients; "
            "response bodies are always buffered. Omit this option; pagination remains supported."
        )
    for name in (
        "retry_total", "retry_connect", "retry_read", "retry_status",
        "retry_backoff_factor", "retry_backoff_max", "retry_on_methods",
    ):
        if name in kwargs or name in options:
            raise TypeError(
                f"query_items_change_feed() does not accept per-call {name} on Rust-backed clients; "
                "omit this option to use driver-managed retries."
            )
    if "connection_timeout" in kwargs or "connection_timeout" in options:
        raise TypeError(
            "query_items_change_feed() does not accept per-call connection_timeout; "
            "configure ConnectionPoolOptions.connection_timeout on the client's CosmosRuntime instead."
        )


class _FeedContext:
    """Retain the execution context and telemetry inputs shared by feed configurations.

    :param Any proxy: Container proxy supplying its client context.
    :param dict[str, Any] kwargs: Working keywords from which Rust telemetry options are consumed.
    :param Any backend: Already-selected execution backend.
    :param bool rust: Whether telemetry controls should be consumed for Rust execution.
    """

    def __init__(self, proxy: Any, kwargs: dict[str, Any], backend: Any, rust: bool) -> None:
        self.proxy = proxy
        context = proxy._client_context
        self._client_context = context
        self.response_state = context.response_state if context is not None else None
        self.backend = backend
        self.recording_options = RecordingOptions.take(kwargs) if rust else RecordingOptions.snapshot({})


class FeedConfig(_FeedContext):
    """Copy the options and keep the adapter used to fetch pages."""

    def __init__(
        self, proxy: Any, kwargs: dict[str, Any], *, operation: str, backend: Any
    ) -> None:
        self.operation = operation
        self.rust = is_rust_backend(backend)
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
        supports_cache_staleness = operation in ("query_items", "read_all_items")
        if self.rust and not supports_cache_staleness and "maxIntegratedCacheStaleness" in self.options:
            raise TypeError(
                f"{operation}() does not accept max_integrated_cache_staleness_in_ms "
                "(maxIntegratedCacheStaleness); omit this option."
            )
        cache = self.options.get("maxIntegratedCacheStaleness")
        if cache is not None and (isinstance(cache, bool) or not isinstance(cache, int) or cache < 0):
            raise ValueError(f"{operation} cache staleness must be a nonnegative integer or None.")
        if operation != "query_items" and "populateQueryMetrics" in self.options:
            raise TypeError(f"{operation}() does not accept query metrics.")
        super().__init__(proxy, kwargs, backend, self.rust)
        if self.rust:
            self._validate_rust_options(kwargs, supports_cache_staleness)
        if self.rust and self._client_context is not None:
            self._client_context.defaults.apply_to_options(self.options)
        self.kwargs = kwargs

    def _validate_rust_options(self, kwargs: dict[str, Any], supports_cache_staleness: bool) -> None:
        operation = self.operation
        if operation == "query_items_change_feed":
            _validate_change_feed_options(self.options, kwargs)
        if operation in ("read_all_items", "query_items_change_feed") and "availabilityStrategy" in self.options:
            raise TypeError(
                f"{operation}() does not accept availability_strategy (availabilityStrategy) "
                "on Rust-backed clients; omit this option."
            )
        allowed = {
            "maxItemCount", "sessionToken", "initialHeaders", "priorityLevel", "throughputBucket",
            "excludedLocations", "timeout", "continuation", "consistencyLevel", "utf8DecodingMode",
        }
        if supports_cache_staleness:
            allowed.add("maxIntegratedCacheStaleness")
        if operation == "query_items":
            allowed |= {
                "populateQueryMetrics", "populateIndexMetrics", "populateQueryAdvice", "enableScanInQuery",
                "availabilityStrategy", "correlatedActivityId", "responseContinuationTokenLimitInKb",
            }
        initial = self.options.get("initialHeaders")
        if initial is not None and not isinstance(initial, dict):
            raise TypeError(f"{operation} initial_headers must be a dict or None.")
        if any(not isinstance(name, str) for name in (initial or {})):
            raise TypeError(f"{operation} initial_headers names must be strings.")
        reserved = HEADERS_THE_DRIVER_REGENERATES | {
            "x-ms-continuation", "x-ms-documentdb-partitionkey", "x-ms-documentdb-partitionkeyrangeid",
            "x-ms-documentdb-query-enablecrosspartition", "x-ms-documentdb-isquery",
            "x-ms-cosmos-is-query-plan-request",
        }
        reject_unknown_feed_kwargs(operation, kwargs)
        unsupported = [repr(name) for name in kwargs]
        unsupported.extend(f"request_options[{name!r}]" for name in self.options.keys() - allowed)
        if operation != "query_items_change_feed":
            unsupported.extend(
                f"initial_headers[{name!r}]" for name in (initial or {}) if name.lower() in reserved
            )
        if unsupported:
            raise NotImplementedError(
                f"{operation} cannot honor these options on Rust: {', '.join(sorted(unsupported))}; "
                "no legacy fallback will be used."
            )

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

        :param str or None token: Continuation token for the next page.
        :param _ItemFeedCursor or None cursor: Iterator-owned binding cursor, required for retained paging.
        :param float or None deadline: Monotonic deadline whose remaining time governs the page request.
        :return: Prepared page request with typed settings and the retained cursor.
        :rtype: ~azure.cosmos._backend.contracts.PreparedPageRequest
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


class RustFeedConfig(FeedConfig):
    """Prepare shared query and read-all settings using the client's Rust adapter."""

    def __init__(self, proxy: Any, kwargs: dict[str, Any], *, operation: str) -> None:
        reject_removed_options(kwargs)
        context = proxy._client_context
        if context is None or not is_rust_backend(context.adapter):
            raise NotImplementedError(f"{operation} requires a client-owned Rust backend; no legacy fallback.")
        context.defaults.apply_timeout(kwargs)
        reject_rust_arguments(kwargs)
        super().__init__(proxy, kwargs, operation=operation, backend=context.adapter)


class _FeedResponseState:
    """Accumulate response headers and retain the latest envelope for a feed fetch."""

    def __init__(self) -> None:
        self.captured = CaseInsensitiveDict()
        self.envelope: dict[str, Any] = {}
        self.accumulated = ResponseHeaderAccumulator()
        self.responses = 0
        self.has_charge = False

    def capture(self, headers: Any, body: Any) -> None:
        self.responses += 1
        self.has_charge = self.has_charge or "x-ms-request-charge" in CaseInsensitiveDict(headers)
        self.accumulated(headers, None)
        self.captured.clear()
        self.captured.update(headers)
        if isinstance(body, Mapping):
            self.envelope = dict(body)


class FeedPageState(_FeedResponseState):
    """Keep one page iterator's progress and per-fetch response information."""

    def __init__(self, config: FeedConfig, headers: CaseInsensitiveDict, token: Optional[str]) -> None:
        self.config = config
        self.headers = headers
        self.token = token
        self.cursor: Optional[_ItemFeedCursor] = None
        self.failed = False
        self.done = False
        super().__init__()
        self.lock = threading.Lock()

    def begin(self) -> None:
        """Create a feed cursor if needed and reset the next fetch's response totals.

        :return: None.
        :rtype: None
        """
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
        if notify_hook and self.responses and self.config.hook is not None:
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
