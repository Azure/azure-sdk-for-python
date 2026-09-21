# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Backend-pinned change-feed polling with page-local checkpoints."""

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

from .. import _base, http_constants
from .._availability_strategy_config import _validate_request_hedging_strategy
from .._backend.contracts import PreparedQuery, QueryPage
from .._backend.operations import OP_QUERY_ITEMS_CHANGE_FEED
from .._change_feed.change_feed_fetcher import ChangeFeedFetcherV1, ChangeFeedFetcherV2
from .._change_feed.change_feed_state import ChangeFeedState, ChangeFeedStateVersion
from .._constants import _Constants as Constants
from .._cosmos_responses import CosmosItemPaged
from .._operation_deadline import legacy_deadline_options, remaining_timeout
from .._query_rust_routing import page_to_backend_response
from ..partition_key import (
    NonePartitionKeyValue,
    NullPartitionKeyValue,
    _Empty,
    _Undefined,
    _build_partition_key_from_properties,
    _return_undefined_or_empty_partition_key,
)
from ._legacy_partition_key import legacy_partition_key_header
from ._partition_key import normalize_partition_key, query_partition_key_components, partition_key_bookmark_value
from .._backend.partition_key_input import BindingPartitionKey
from ._read_all_items import ReadAllConfig, ReadAllPageState
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


def _decode(token: str, *, urlsafe: bool = False) -> dict[str, Any]:
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


def _settings(values: dict[str, Any], *, rust: bool) -> dict[str, Any]:
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
        raise ValueError(
            "partition_key, feed_range and partition_key_range_id are exclusive."
        )
    if mode == "AllVersionsAndDeletes" and (
        start != "Now" or "partition_key_range_id" in scopes
    ):
        raise ValueError(
            "A fresh AllVersionsAndDeletes feed requires Now and a logical scope or feed_range."
        )
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
        if rust:
            raise NotImplementedError(
                "Rust change feed requires feed_range, not partition_key_range_id; no fallback."
            )
        result["range_id"] = range_id
    if "partition_key" in scopes:
        key = values["partition_key"]
        if key is NullPartitionKeyValue:
            key = None
        if key is NonePartitionKeyValue:
            key = _Undefined()
        components = key if isinstance(key, (list, tuple)) else [key]
        if not 1 <= len(components) <= 3 or any(
            not (
                value is None
                or isinstance(value, (str, int, float, bool, _Empty, _Undefined))
            )
            or isinstance(value, float)
            and not math.isfinite(value)
            for value in components
        ):
            raise ValueError(
                "partition_key must contain one to three JSON scalar components."
            )
        if rust:
            result["partition_key"] = (
                normalize_partition_key(key) if isinstance(key, _Empty)
                else query_partition_key_components(components)
            )
        elif any(isinstance(value, _Undefined) for value in components):
            result["partition_key"] = json.dumps(
                [
                    {} if isinstance(value, _Undefined) else value
                    for value in components
                ],
                separators=(",", ":"),
            )
        else:
            result["partition_key"] = legacy_partition_key_header(key)
    if "feed_range" in scopes:
        feed = values["feed_range"]
        interval = feed.get("Range") if isinstance(feed, dict) else None
        if not isinstance(interval, dict):
            raise ValueError("feed_range must contain a Range object.")
        minimum, maximum = interval.get("min"), interval.get("max")
        if (
            not isinstance(minimum, str)
            or not isinstance(maximum, str)
            or minimum >= maximum
            or interval.get("isMinInclusive", True) is not True
            or interval.get("isMaxInclusive", False) is not False
        ):
            raise ValueError(
                "feed_range must be a nonempty min-inclusive, max-exclusive range."
            )
        result["feed_range"] = [minimum, maximum]
    return result


class ChangeFeedConfig(ReadAllConfig):
    def __init__(self, proxy: Any, kwargs: dict[str, Any]) -> None:
        self.requested = {
            key: deepcopy(kwargs.pop(key)) for key in _SETTINGS if key in kwargs
        }
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
        super().__init__(proxy, kwargs, operation=OP_QUERY_ITEMS_CHANGE_FEED)
        self.path = _base.GetPathFromLink(
            proxy.container_link, http_constants.ResourceType.Document
        )
        self.collection_id = _base.GetResourceIdOrFullNameFromLink(proxy.container_link)
        if self.rust:
            reserved = {
                "if-none-match",
                "if-modified-since",
                "a-im",
                "x-ms-cosmos-changefeed-wire-format-version",
                "x-ms-start-epk",
                "x-ms-end-epk",
                "x-ms-documentdb-readfeed-key-type",
                "x-ms-max-item-count",
            }
            if "maxIntegratedCacheStaleness" in self.options or any(
                name.lower() in reserved
                for name in (self.options.get("initialHeaders") or {})
            ):
                raise NotImplementedError(
                    "Rust change feed cannot honor these options; no fallback."
                )
        elif self.options.get(Constants.Kwargs.AVAILABILITY_STRATEGY) is not None:
            self.options[Constants.Kwargs.AVAILABILITY_STRATEGY] = (
                _validate_request_hedging_strategy(
                    self.options[Constants.Kwargs.AVAILABILITY_STRATEGY]
                )
            )

    def resolve(self, token: Optional[str]) -> tuple[dict[str, Any], Optional[str]]:
        if token is None:
            return _settings(self.requested, rust=self.rust), None
        if not isinstance(token, str) or not token:
            raise ValueError(
                "change-feed continuation must be a nonempty string or None."
            )
        if token.startswith(_PREFIX):
            saved = _decode(token[len(_PREFIX) :], urlsafe=True)
            expected = "rust" if self.rust else "core-python"
            if (
                saved.get("backend") != expected
                or saved.get("container") != self.proxy.container_link
            ):
                raise ValueError(
                    "change-feed continuation belongs to an incompatible backend or container."
                )
            settings, inner = saved.get("settings"), saved.get("token")
            if (
                not isinstance(settings, dict)
                or not isinstance(inner, str)
                or not inner
            ):
                raise ValueError("Invalid change-feed continuation.")
            if (
                settings.get("mode") not in ("LatestVersion", "AllVersionsAndDeletes")
                or set(settings)
                - {"mode", "start", "partition_key", "feed_range", "range_id"}
                or not self.rust
                and not inner.strip('"').isdigit()
            ):
                raise ValueError("Invalid change-feed continuation settings.")
            # Check our own bookmark format without relying on the layout of the
    # token the driver keeps to itself.
            values: dict[str, Any] = {
                "mode": settings.get("mode"),
                "start_time": settings.get("start"),
            }
            if values["start_time"] not in ("Now", "Beginning"):
                try:
                    values["start_time"] = datetime.fromisoformat(values["start_time"])
                except (TypeError, ValueError) as error:
                    raise ValueError(
                        "Invalid change-feed continuation start."
                    ) from error
            if settings.get("partition_key") is not None:
                try:
                    components = json.loads(settings["partition_key"])
                except (TypeError, ValueError) as error:
                    raise ValueError(
                        "Invalid change-feed continuation partition key."
                    ) from error
                if not isinstance(components, list):
                    raise ValueError("Invalid change-feed continuation partition key.")
                values["partition_key"] = [
                    _Undefined() if component == {} else component
                    for component in components
                ]
            if settings.get("feed_range") is not None:
                interval = settings["feed_range"]
                if not isinstance(interval, list) or len(interval) != 2:
                    raise ValueError("Invalid change-feed continuation range.")
                values["feed_range"] = {
                    "Range": {"min": interval[0], "max": interval[1]}
                }
            if "range_id" in settings:
                values["partition_key_range_id"] = settings["range_id"]
            normalized = _settings(values, rust=self.rust)
            if (
                self.rust
                and not inner.startswith("c1.")
                or not self.rust
                and inner.startswith(("c1.", _PREFIX))
            ):
                raise ValueError(
                    "change-feed continuation belongs to an incompatible backend."
                )
            return normalized, inner
        if self.rust or token.startswith("c1."):
            raise ValueError(
                "change-feed continuation belongs to an incompatible backend or operation."
            )
        if token.strip('"').isdigit():
            values = dict(self.requested)
            values.update(
                mode="LatestVersion", start_time="Now", is_start_from_beginning=False
            )
            return _settings(values, rust=False), token
        saved = _decode(token)
        if saved.get("v") != "v2" or saved.get("mode") not in (
            "LatestVersion",
            "AllVersionsAndDeletes",
        ):
            raise ValueError("Invalid legacy change-feed continuation.")
        # V2 restores and validates its own mode, start, scope and container RID.
        return _settings({"mode": saved["mode"]}, rust=False), token


class ChangeFeedPageState(ReadAllPageState):
    config: ChangeFeedConfig

    def __init__(
        self,
        config: ChangeFeedConfig,
        headers: CaseInsensitiveDict,
        token: Optional[str],
    ) -> None:
        super().__init__(config, headers, token)
        self.settings, self.inner_token = config.resolve(token)
        self.fetcher: Any = None
        self.initial_time_poll = self.inner_token is None and self.settings[
            "start"
        ] not in ("Now", "Beginning")
        self.poll_again = False

    def prepared_page(self, deadline: Optional[float]) -> PreparedQuery:
        return replace(
            self.config.prepared(self.inner_token, self.cursor, deadline),
            op=OP_QUERY_ITEMS_CHANGE_FEED,
            change_feed={key: value for key, value in self.settings.items() if key != "partition_key"},
            partition_key=self.settings["partition_key"] or BindingPartitionKey("cross_partition"),
        )

    def bookmark(self, inner: str) -> str:
        persisted_settings = dict(self.settings)
        key = persisted_settings["partition_key"]
        if isinstance(key, BindingPartitionKey):
            persisted_settings["partition_key"] = partition_key_bookmark_value(key)
        payload = {
            "backend": "rust" if self.config.rust else "core-python",
            "container": self.config.proxy.container_link,
            "settings": persisted_settings,
            "token": inner,
        }
        return _PREFIX + base64.urlsafe_b64encode(
            json.dumps(payload, separators=(",", ":")).encode("utf-8")
        ).decode("ascii").rstrip("=")

    def parse(self, page: QueryPage) -> list[dict[str, Any]]:
        result = process_backend_response(
            page_to_backend_response(page), response_state=self.config.response_state
        )
        if not page.continuation:
            raise ValueError("Rust change feed returned no durable continuation.")
        rows = [] if page.status_code == 304 else result.get("Documents")
        if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
            raise ValueError(
                "change feed received an invalid Documents response envelope."
            )
        if self.settings["mode"] == "LatestVersion":
            if any(not isinstance(row.get("current"), dict) for row in rows):
                raise ValueError(
                    "LatestVersion change feed received a record without current."
                )
            rows = [row["current"] for row in rows]
        self.capture(page.headers or {}, result)
        self.inner_token = page.continuation
        self.token = self.bookmark(self.inner_token)
        self.poll_again = self.initial_time_poll and not rows
        self.initial_time_poll = False
        return rows

    def legacy_state(self, properties: dict[str, Any]) -> ChangeFeedState:
        context: dict[str, Any] = {"mode": self.settings["mode"]}
        if self.inner_token is not None:
            context[
                (
                    "continuationPkRangeId"
                    if self.inner_token.strip('"').isdigit()
                    else "continuationFeedRange"
                )
            ] = self.inner_token
        start = self.settings["start"]
        context["startTime"] = (
            start if start in ("Now", "Beginning") else datetime.fromisoformat(start)
        )
        if self.inner_token is None or self.inner_token.strip('"').isdigit():
            if "range_id" in self.settings:
                context["partitionKeyRangeId"] = self.settings["range_id"]
            if self.settings["feed_range"] is not None:
                minimum, maximum = self.settings["feed_range"]
                context["feedRange"] = {
                    "Range": {
                        "min": minimum,
                        "max": maximum,
                        "isMinInclusive": True,
                        "isMaxInclusive": False,
                    }
                }
            if self.settings["partition_key"] is not None:
                components = json.loads(self.settings["partition_key"])
                key = components[0] if len(components) == 1 else components
                if key == {}:
                    key = _return_undefined_or_empty_partition_key(
                        properties.get("partitionKey", {}).get("systemKey", False)
                    )
                context["partitionKey"] = key
                context["partitionKeyFeedRange"] = _build_partition_key_from_properties(
                    properties
                )._get_epk_range_for_partition_key(key)
        self.legacy_options[Constants.ContainerRID] = properties["_rid"]
        return ChangeFeedState.from_json(
            self.config.proxy.container_link, properties["_rid"], context
        )

    def legacy_result(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        inner = self.fetcher.continuation_token
        if not isinstance(inner, str) or not inner:
            raise ValueError("Legacy change feed returned no durable continuation.")
        self.inner_token = inner
        # Keep V2's bookmark, which describes itself and carries the scope that
        # should be trusted.
        self.token = (
            inner
            if self.fetcher._change_feed_state.version == ChangeFeedStateVersion.V2
            else self.bookmark(inner)
        )
        return rows

    def finish(
        self, rows: list[dict[str, Any]], deadline: Optional[float]
    ) -> tuple[Optional[str], list[dict[str, Any]]]:
        if self.token is not None:
            self.accumulated.headers["etag"] = self.token
        result = super().finish(rows, deadline)
        self.done = not rows
        if self.done:
            self.cursor = None
            self.fetcher = None
        return result

    def invalidate(self, error: BaseException) -> None:
        super().invalidate(error)
        if self.failed:
            self.fetcher = None


class ChangeFeedPageIterator(PageIterator):
    def __init__(
        self,
        config: ChangeFeedConfig,
        headers: CaseInsensitiveDict,
        continuation_token: Optional[str] = None,
    ) -> None:
        token = (
            continuation_token
            if continuation_token is not None
            else config.options.get("continuation")
        )
        self.state = ChangeFeedPageState(config, headers, token)
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
                "change-feed pager failed; resume a new pager from the last delivered bookmark."
            )
        if not state.lock.acquire(blocking=False):
            raise RuntimeError(
                "Concurrent use of a change-feed pager is not supported."
            )
        try:
            config, deadline = state.config, state.config.deadline()
            state.begin()
            if config.rust:
                while True:
                    pages = config.backend.execute_pages(state.prepared_page(deadline), deadline=deadline)
                    try:
                        page = next(pages)
                    except StopIteration as error:
                        raise RuntimeError(
                            "Rust backend returned no change-feed page."
                        ) from error
                    finally:
                        pages.close()
                    rows = state.parse(page)
                    if not state.poll_again:
                        break
            else:
                state.legacy_options.update(
                    legacy_deadline_options(config.options, deadline)
                )
                state.legacy_options.pop("continuation", None)
                if state.fetcher is None:
                    properties = config.proxy._get_properties_with_options(
                        state.legacy_options
                    )
                    remaining_timeout(deadline)
                    change_state = state.legacy_state(properties)
                    state.legacy_options["changeFeedState"] = change_state

                    def fetch(
                        options: dict[str, Any],
                    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
                        remaining_timeout(options.get("_item_operation_deadline"))
                        rows, headers = config.connection.QueryFeed(
                            config.path,
                            config.collection_id,
                            None,
                            options,
                            response_hook=state.capture,
                            **config.kwargs,
                        )
                        return rows, dict(headers)

                    factory = (
                        ChangeFeedFetcherV1
                        if change_state.version == ChangeFeedStateVersion.V1
                        else ChangeFeedFetcherV2
                    )
                    state.fetcher = factory(
                        config.connection,
                        config.proxy.container_link,
                        state.legacy_options,
                        fetch,
                    )
                rows = state.legacy_result(state.fetcher.fetch_next_block())
            return state.finish(rows, deadline)
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
