# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Poll a change feed through the client's Rust backend.

Each ChangeFeedPageIterator has its own progress. On the Rust path it retains
a feed cursor; the cf1. continuation token also records the feed settings for
a later compatible request. An empty final poll finishes this iteration, not the
container's ability to produce future changes.
"""

from __future__ import annotations

import base64
import binascii
import json
import math
import warnings
from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timezone
from typing import Any, Optional

from azure.core.paging import PageIterator
from azure.core.utils import CaseInsensitiveDict

from .._backend.constants import is_rust_backend
from .._backend.contracts import PreparedPageRequest, BackendPage
from .._backend.operations import OP_QUERY_ITEMS_CHANGE_FEED
from .._cosmos_responses import CosmosItemPaged
from .._query_rust_routing import page_to_backend_response
from .._telemetry import trace_operation
from ..partition_key import (
    NonePartitionKeyValue,
    NullPartitionKeyValue,
    _Empty,
    _Undefined,
)
from ._partition_key import (
    normalize_partition_key,
    query_partition_key_components,
    serialize_partition_key_for_continuation,
)
from .._backend.partition_key_input import BindingPartitionKey
from ._feed_paging import FeedConfig, FeedPageState, normalize_feed_range
from ._response_parse import process_backend_response

_PREFIX = "cf1."
_SETTINGS = (
    "mode",
    "start_time",
    "partition_key",
    "feed_range",
    "partition_key_range_id",
    "is_start_from_beginning",
)


def _decode_continuation_payload(token: str, *, urlsafe: bool = False) -> dict[str, Any]:
    try:
        value = json.loads(
            base64.b64decode(
                token + "=" * (-len(token) % 4),
                altchars=b"-_" if urlsafe else None,
                validate=True,
            )
        )
    except (ValueError, UnicodeError, binascii.Error) as error:
        raise ValueError("Invalid change-feed continuation.") from error
    if not isinstance(value, dict):
        raise ValueError("Invalid change-feed continuation.")
    return value


def _normalize_change_feed_settings(values: dict[str, Any]) -> dict[str, Any]:
    mode = values.get("mode")
    if mode is None:
        mode = "LatestVersion"
    if mode not in ("LatestVersion", "AllVersionsAndDeletes"):
        raise ValueError("mode must be LatestVersion or AllVersionsAndDeletes.")
    beginning = values.get("is_start_from_beginning")
    if beginning is not None and not isinstance(beginning, bool):
        raise TypeError("is_start_from_beginning must be a bool.")
    if beginning and values.get("start_time") is not None:
        raise ValueError("is_start_from_beginning and start_time are exclusive.")
    start = "Beginning" if beginning else values.get("start_time")
    if start is None:
        start = "Now"
    if isinstance(start, datetime):
        start = start.astimezone(timezone.utc).isoformat()
    elif isinstance(start, str) and start.lower() in ("now", "beginning"):
        start = start.title()
    else:
        raise ValueError("start_time must be Now, Beginning, or a datetime.")
    scopes = [
        key
        for key in ("partition_key", "feed_range", "partition_key_range_id")
        if key in values and (key == "partition_key" or values[key] is not None)
    ]
    if len(scopes) > 1:
        raise ValueError("partition_key, feed_range and partition_key_range_id are exclusive.")
    if mode == "AllVersionsAndDeletes" and (start != "Now" or "partition_key_range_id" in scopes):
        raise ValueError("A fresh AllVersionsAndDeletes feed requires Now and a logical scope or feed_range.")
    result: dict[str, Any] = {
        "mode": mode,
        "start": start,
        "partition_key": None,
        "feed_range": None,
    }
    if "partition_key_range_id" in scopes:
        range_id = values["partition_key_range_id"]
        if not isinstance(range_id, str) or not range_id:
            raise ValueError("partition_key_range_id must be a nonempty string.")
        result["range_id"] = range_id
    if "partition_key" in scopes:
        key = values["partition_key"]
        if key is NullPartitionKeyValue:
            key = None
        if key is NonePartitionKeyValue:
            key = _Undefined()
        components = key if isinstance(key, (list, tuple)) else [key]
        if not 1 <= len(components) <= 3 or any(
            not (value is None or isinstance(value, (str, int, float, bool, _Empty, _Undefined)))
            or isinstance(value, float)
            and not math.isfinite(value)
            for value in components
        ):
            raise ValueError("partition_key must contain one to three JSON scalar components.")
        result["partition_key"] = (
            normalize_partition_key(key) if isinstance(key, _Empty) else query_partition_key_components(components)
        )
    if "feed_range" in scopes:
        result["feed_range"] = normalize_feed_range(values["feed_range"])
    return result


class ChangeFeedConfig(FeedConfig):
    def __init__(self, proxy: Any, kwargs: dict[str, Any]) -> None:
        context = proxy._client_context
        if context is None or not is_rust_backend(context.adapter):
            raise NotImplementedError(
                "query_items_change_feed requires a client-owned Rust backend; no legacy fallback."
            )
        self.requested = {key: deepcopy(kwargs.pop(key)) for key in _SETTINGS if key in kwargs}
        for key, replacement in (
            ("partition_key_range_id", "feed_range"),
            ("is_start_from_beginning", "start_time"),
        ):
            if key in self.requested:
                warnings.warn(
                    f"'{key}' is deprecated; use '{replacement}'.",
                    DeprecationWarning,
                    stacklevel=4,
                )
        super().__init__(
            proxy, kwargs, operation=OP_QUERY_ITEMS_CHANGE_FEED,
            backend=context.adapter,
        )
        self.resolve(self.options.get("continuation"))

    def resolve(self, token: Optional[str]) -> tuple[dict[str, Any], Optional[str]]:
        """Return normalized feed settings and the continuation passed to the backend.

        Without a token, normalize the requested settings. A wrapper checkpoint
        restores its saved settings and inner token after backend/container checks.
        Legacy, invalid or incompatible tokens raise ValueError.

        :param str or None token: Wrapper checkpoint to resume, or None for a fresh feed.
        :return: Normalized feed settings and the opaque inner continuation token.
        :rtype: tuple[dict[str, Any], str or None]
        """
        if token is None:
            return _normalize_change_feed_settings(self.requested), None
        if not isinstance(token, str) or not token:
            raise ValueError("change-feed continuation must be a nonempty string or None.")
        if token.startswith(_PREFIX):
            saved = _decode_continuation_payload(token[len(_PREFIX) :], urlsafe=True)
            if (
                saved.get("backend") != "rust"
                or saved.get("container") != self.proxy.container_link
            ):
                raise ValueError("change-feed continuation belongs to an incompatible backend or container.")
            settings, inner = saved.get("settings"), saved.get("token")
            if not isinstance(settings, dict) or not isinstance(inner, str) or not inner:
                raise ValueError("Invalid change-feed continuation.")
            if (
                settings.get("mode") not in ("LatestVersion", "AllVersionsAndDeletes")
                or set(settings) - {"mode", "start", "partition_key", "feed_range", "range_id"}
            ):
                raise ValueError("Invalid change-feed continuation settings.")
            # Validate the Python wrapper's continuation format without decoding
            # the inner continuation token.
            values: dict[str, Any] = {
                "mode": settings.get("mode"),
                "start_time": settings.get("start"),
            }
            if values["start_time"] not in ("Now", "Beginning"):
                try:
                    values["start_time"] = datetime.fromisoformat(values["start_time"])
                except (TypeError, ValueError) as error:
                    raise ValueError("Invalid change-feed continuation start.") from error
            if settings.get("partition_key") is not None:
                try:
                    components = json.loads(settings["partition_key"])
                except (TypeError, ValueError) as error:
                    raise ValueError("Invalid change-feed continuation partition key.") from error
                if not isinstance(components, list):
                    raise ValueError("Invalid change-feed continuation partition key.")
                values["partition_key"] = [_Undefined() if component == {} else component for component in components]
            if settings.get("feed_range") is not None:
                interval = settings["feed_range"]
                if not isinstance(interval, list) or len(interval) != 2:
                    raise ValueError("Invalid change-feed continuation range.")
                values["feed_range"] = {"Range": {"min": interval[0], "max": interval[1]}}
            if "range_id" in settings:
                values["partition_key_range_id"] = settings["range_id"]
            normalized = _normalize_change_feed_settings(values)
            if not inner.startswith(("c1.", "c2.")):
                raise ValueError("change-feed continuation belongs to an incompatible backend.")
            return normalized, inner
        if token.startswith(("c1.", "c2.")):
            raise ValueError("change-feed continuation belongs to an incompatible backend or operation.")
        raise ValueError(
            "This continuation token is not supported. Use a token returned by the Rust-backed change feed."
        )


class ChangeFeedPageState(FeedPageState):
    """Retain the feed settings, inner continuation token, and polling progress."""

    config: ChangeFeedConfig

    def __init__(
        self,
        config: ChangeFeedConfig,
        headers: CaseInsensitiveDict,
        token: Optional[str],
    ) -> None:
        super().__init__(config, headers, token)
        self.settings, self.inner_token = config.resolve(token)
        self.initial_time_poll = self.inner_token is None and self.settings["start"] not in ("Now", "Beginning")
        self.poll_again = False

    def prepared_page(self, deadline: Optional[float]) -> PreparedPageRequest:
        return replace(
            self.config.prepared(self.inner_token, self.cursor, deadline),
            op=OP_QUERY_ITEMS_CHANGE_FEED,
            change_feed={key: value for key, value in self.settings.items() if key != "partition_key"},
            partition_key=self.settings["partition_key"] or BindingPartitionKey("cross_partition"),
        )

    def encode_continuation_token(self, inner: str) -> str:
        """Wrap the inner continuation token with the selected path and feed settings.

        :param str inner: Opaque continuation returned by the Rust change-feed backend.
        :return: A cf1 checkpoint recording the container, backend, and normalized feed settings.
        :rtype: str
        """
        persisted_settings = dict(self.settings)
        key = persisted_settings["partition_key"]
        if isinstance(key, BindingPartitionKey):
            persisted_settings["partition_key"] = serialize_partition_key_for_continuation(key)
        payload = {
            "backend": "rust",
            "container": self.config.proxy.container_link,
            "settings": persisted_settings,
            "token": inner,
        }
        return _PREFIX + base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8")).decode(
            "ascii"
        ).rstrip("=")

    def parse(self, page: BackendPage) -> list[dict[str, Any]]:
        result = process_backend_response(page_to_backend_response(page), response_state=self.config.response_state)
        if not page.continuation:
            raise ValueError("Rust change feed returned no durable continuation.")
        rows = [] if page.status_code == 304 else result.get("Documents")
        if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
            raise ValueError("change feed received an invalid Documents response envelope.")
        if self.settings["mode"] == "LatestVersion":
            if any(not isinstance(row.get("current"), dict) for row in rows):
                raise ValueError("LatestVersion change feed received a record without current.")
            rows = [row["current"] for row in rows]
        self.capture(result.get_response_headers(), result)
        self.inner_token = page.continuation
        self.token = self.encode_continuation_token(self.inner_token)
        self.poll_again = self.initial_time_poll and not rows
        self.initial_time_poll = False
        return rows

    def finish(
        self, rows: list[dict[str, Any]], deadline: Optional[float], *, notify_hook: bool = True
    ) -> tuple[Optional[str], list[dict[str, Any]]]:
        # ETags describe the final response, not an earlier bootstrap poll.
        if self.responses and "etag" not in self.captured:
            self.accumulated.headers.pop("etag", None)
        result = super().finish(rows, deadline, notify_hook=notify_hook)
        self.done = not rows
        if self.done:
            self.cursor = None
        return result


@trace_operation(
    binding_operation="query_items_change_feed",
    operation_name="query_items_change_feed",
    name_of_span="ContainerProxy.query_items_change_feed.fetch",
)
def _fetch_rust_page(
    config: ChangeFeedConfig,
    state: ChangeFeedPageState,
    deadline: Optional[float],
    **_tracing_kwargs: Any,
) -> Optional[tuple[Optional[str], list[dict[str, Any]]]]:
    """Record one poll; finish the public page only after its final fetch.

    Additional ``_tracing_kwargs`` are consumed by the operation's telemetry decorator.

    :param ChangeFeedConfig config: Prepared feed configuration and execution backend.
    :param ChangeFeedPageState state: Iterator progress updated by parsing and response completion.
    :param float or None deadline: Shared monotonic deadline for the exposed page.
    :return: Continuation and rows, or None when a bootstrap poll requires another fetch.
    :rtype: tuple[str or None, list[dict]] or None
    """
    pages = config.backend.execute_pages(state.prepared_page(deadline), deadline=deadline)
    try:
        page = next(pages)
    except StopIteration as error:
        raise RuntimeError("Rust backend returned no change-feed page.") from error
    finally:
        pages.close()
    rows = state.parse(page)
    return None if state.poll_again else state.finish(rows, deadline)


class ChangeFeedPageIterator(PageIterator):
    def __init__(
        self,
        config: ChangeFeedConfig,
        headers: CaseInsensitiveDict,
        continuation_token: Optional[str] = None,
    ) -> None:
        token = continuation_token if continuation_token is not None else config.options.get("continuation")
        self.state = ChangeFeedPageState(config, headers, token)
        super().__init__(self._fetch, self._unpack, continuation_token=token)

    @staticmethod
    def _unpack(value: tuple[Optional[str], list[dict[str, Any]]]) -> Any:
        # azure-core types this callback as never receiving the None it sends
        # to mark the end of iteration, so the annotation here is narrower than
        # what can actually arrive. The value is passed straight through.
        return value

    def _fetch(self, _token: Optional[str]) -> tuple[Optional[str], list[dict[str, Any]]]:
        state = self.state
        if state.done:
            raise StopIteration
        if state.failed:
            raise RuntimeError("change-feed pager failed; resume a new pager from the last delivered bookmark.")
        # A blocking context manager would wait rather than reject concurrent pager use.
        # The finally block releases this explicitly acquired lock.
        if not state.lock.acquire(blocking=False):  # pylint: disable=consider-using-with
            raise RuntimeError("Concurrent use of a change-feed pager is not supported.")
        try:
            config, deadline = state.config, state.config.deadline()
            state.begin()
            while True:
                result = _fetch_rust_page(config, state, deadline, **config.recording_options.kwargs)
                if result is not None:
                    return result
        except BaseException as error:
            state.invalidate(error)
            raise
        finally:
            state.lock.release()


def query_items_change_feed(proxy: Any, kwargs: dict[str, Any]) -> CosmosItemPaged:
    config = ChangeFeedConfig(proxy, kwargs)
    headers = CaseInsensitiveDict()
    return CosmosItemPaged(
        config,
        headers,
        page_iterator_class=ChangeFeedPageIterator,
        response_headers=headers,
    )
