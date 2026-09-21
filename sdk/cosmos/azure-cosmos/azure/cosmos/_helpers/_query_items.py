# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Backend-pinned SQL queries with retained plans and query-bound bookmarks.

The service query body is serialized once per pager. Scope and page settings
travel separately, so fetching another page does not encode the query again.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
from copy import deepcopy
from dataclasses import replace
from typing import TYPE_CHECKING, Any, Iterator, Optional
from uuid import uuid4

from azure.core.exceptions import AzureError
from azure.core.utils import CaseInsensitiveDict

from .. import _utils, http_constants
from .._availability_strategy_config import _validate_request_hedging_strategy
from .._backend.contracts import QueryScope, PreparedQuery, QueryPage
from .._backend._immutable import freeze_json
from .._backend.operations import OP_QUERY_ITEMS
from .._backend.partition_key_input import BindingPartitionKey
from .._cosmos_responses import CosmosItemPaged
from .._query_advisor import get_query_advice_info
from ._partition_key import query_partition_key_components, partition_key_bookmark_value
from ._read_all_items import ReadAllConfig, ReadAllPageState
from ._read_items import partition_key_components
from ._wire_encoding import serialize_body_to_bytes
from ._request_settings import normalize_query_specification

_PREFIX = "q1."
_QUERY_OPTIONS = {
    "populate_query_metrics": "populateQueryMetrics",
    "populate_index_metrics": "populateIndexMetrics",
    "populate_query_advice": "populateQueryAdvice",
    "enable_scan_in_query": "enableScanInQuery",
}


def uses_rust(proxy: Any) -> bool:
    context = proxy._item_context
    backend = (
        context.backend if context is not None else proxy.client_connection._backend
    )
    return backend.name != "core-python"


def reject_rust_bookmark(kwargs: dict[str, Any]) -> None:
    options = kwargs.get("request_options", kwargs.get("feed_options", {})) or {}
    token = kwargs.get("continuation", options.get("continuation"))
    if isinstance(token, str) and token.startswith(("q1.", "c1.", "cf1.")):
        raise ValueError("query_items continuation belongs to an incompatible backend.")


if TYPE_CHECKING:
    from azure.cosmos._rust import _ItemFeedCursor


class QueryConfig(ReadAllConfig):
    def __init__(self, proxy: Any, kwargs: dict[str, Any]) -> None:
        self.query, self.parameters = normalize_query_specification(
            kwargs.pop("query", None), kwargs.pop("parameters", None), operation="query_items",
        )
        options = deepcopy(
            kwargs.pop("request_options", kwargs.pop("feed_options", {})) or {}
        )
        if kwargs.get("read_timeout") is None:
            kwargs.pop("read_timeout", None)
        if options.get("read_timeout") is None:
            options.pop("read_timeout", None)
        for public, internal in _QUERY_OPTIONS.items():
            if public in kwargs:
                options[internal] = kwargs.pop(public)
            if (
                internal in options
                and options[internal] is not None
                and not isinstance(options[internal], bool)
            ):
                raise TypeError(f"{public} must be a bool or None.")
        key = kwargs.pop("partition_key", options.pop("partitionKey", None))
        feed = kwargs.pop("feed_range", None)
        if key is not None and feed is not None:
            raise ValueError("partition_key and feed_range are exclusive.")
        partition = None
        if key is not None:
            components = partition_key_components(key)
            if len(components) > 3:
                raise ValueError(
                    "Query partition keys support at most three components."
                )
            partition = query_partition_key_components(components)
        interval = None
        if feed is not None:
            interval = feed.get("Range") if isinstance(feed, dict) else None
            if not isinstance(interval, dict) or (
                not isinstance(interval.get("min"), str)
                or not isinstance(interval.get("max"), str)
                or interval["min"] >= interval["max"]
                or interval.get("isMinInclusive", True) is not True
                or interval.get("isMaxInclusive", False) is not False
            ):
                raise ValueError(
                    "feed_range requires a nonempty min-inclusive, max-exclusive Range."
                )
            interval = [interval["min"], interval["max"]]
        cross = kwargs.pop(
            "enable_cross_partition_query",
            options.pop("enableCrossPartitionQuery", None),
        )
        if cross is not None and not isinstance(cross, bool):
            raise TypeError("enable_cross_partition_query must be a bool or None.")
        self.partition_key = partition or BindingPartitionKey("cross_partition")
        self.scope = QueryScope(
            feed_range=(interval[0], interval[1]) if interval is not None else None,
            allow_cross_partition=cross is not False,
        )
        limit = kwargs.pop(
            "continuation_token_limit",
            options.pop("responseContinuationTokenLimitInKb", None),
        )
        if limit is not None:
            if isinstance(limit, bool) or not isinstance(limit, int) or limit < 0:
                raise ValueError(
                    "continuation_token_limit must be a nonnegative integer."
                )
            if limit:
                raise NotImplementedError(
                    "Rust query bookmarks include client merge state and cannot honor continuation_token_limit; no fallback."
                )
        scope = kwargs.pop(
            "full_text_score_scope", options.pop("fullTextScoreScope", None)
        )
        if scope is not None:
            if scope not in ("Local", "Global"):
                raise ValueError("full_text_score_scope must be Local or Global.")
            raise NotImplementedError(
                "Full-text statistics scope requires driver hybrid processing; no fallback."
            )
        options["correlatedActivityId"] = str(uuid4())
        kwargs["request_options"] = options
        super().__init__(proxy, kwargs, operation=OP_QUERY_ITEMS)
        strategy = self.options.get("availabilityStrategy")
        if strategy is not None:
            if not isinstance(strategy, (bool, dict)):
                raise TypeError("availability_strategy must be a bool, dict, or None.")
            if strategy is True and self.backend._client_config is not None:
                threshold = self.backend._client_config.hedging_threshold_ms
                if threshold is not None:
                    strategy = {"threshold_ms": threshold}
            self.options["availabilityStrategy"] = _validate_request_hedging_strategy(
                strategy
            )
        initial = self.options.get("initialHeaders") or {}
        if any(
            name.lower()
            in {
                "x-ms-start-epk",
                "x-ms-end-epk",
                "x-ms-max-item-count",
                "x-ms-cosmos-supported-query-features",
                "x-ms-cosmos-query-version",
                "x-ms-documentdb-responsecontinuationtokenlimitinkb",
            }
            for name in initial
        ):
            raise NotImplementedError(
                "Query scope, paging and planning headers cannot be overridden; no fallback."
            )
        bookmark_scope = {
            **self.scope.as_dict(),
            "partition_key": partition_key_bookmark_value(partition) if partition is not None else None,
        }
        encoded = json.dumps(
            [
                self.backend._endpoint,
                proxy.container_link,
                self.query,
                self.parameters,
                bookmark_scope,
            ],
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode()
        self.identity = hashlib.sha256(encoded).hexdigest()
        payload: dict[str, Any] = {"query": self.query}
        if self.parameters:
            payload["parameters"] = list(self.parameters)
        self.query_body = serialize_body_to_bytes(payload, allow_nan=False)
        self.parameters = freeze_json(self.parameters)
        self.decode(self.options.get("continuation"))

    def decode(self, token: Optional[str]) -> Optional[str]:
        if token is None:
            return None
        if not isinstance(token, str) or not token.startswith(_PREFIX):
            raise ValueError(
                "query_items requires a query bookmark, not a legacy or other feed token."
            )
        try:
            value = json.loads(
                base64.b64decode(
                    token[len(_PREFIX) :] + "=" * (-len(token[len(_PREFIX) :]) % 4),
                    altchars=b"-_",
                    validate=True,
                )
            )
        except (ValueError, UnicodeError, binascii.Error) as error:
            raise ValueError("Invalid query_items continuation.") from error
        if (
            not isinstance(value, dict)
            or set(value) != {"identity", "token"}
            or value["identity"] != self.identity
            or not isinstance(value["token"], str)
            or not value["token"].startswith("c1.")
        ):
            raise ValueError(
                "Query bookmark does not match the account, container, query, parameters or scope."
            )
        return value["token"]

    def encode(self, token: Optional[str]) -> Optional[str]:
        if token is None:
            return None
        return _PREFIX + base64.urlsafe_b64encode(
            json.dumps(
                {"identity": self.identity, "token": token}, separators=(",", ":")
            ).encode()
        ).decode().rstrip("=")

    def prepared(
        self, token: Optional[str], cursor: Optional[_ItemFeedCursor], deadline: Optional[float]
    ) -> PreparedQuery:
        return replace(
            super().prepared(self.decode(token), cursor, deadline),
            op=OP_QUERY_ITEMS,
            query=self.query,
            parameters=self.parameters,
            query_body=self.query_body,
            query_scope=self.scope,
            partition_key=self.partition_key,
        )


class QueryPageState(ReadAllPageState):
    config: QueryConfig

    def __init__(
        self, config: QueryConfig, headers: CaseInsensitiveDict, token: Optional[str]
    ) -> None:
        config.decode(token)
        super().__init__(config, headers, token)
        self.more = True
        self.resumable = True
        self.bookmark = token

    def capture(self, headers: Any, body: Any) -> None:
        headers = CaseInsensitiveDict(headers)
        for name, decode in (
            (
                http_constants.HttpHeaders.IndexUtilization,
                _utils.get_index_metrics_info,
            ),
            (http_constants.HttpHeaders.QueryAdvice, get_query_advice_info),
        ):
            if headers.get(name) is not None:
                headers[name] = decode(headers[name])
        super().capture(headers, body)

    def parse(self, page: QueryPage) -> list[Any]:
        if page.has_more is None:
            raise RuntimeError("Rust query page omitted retained cursor progress.")
        self.more = page.has_more
        self.resumable = self.resumable and page.continuation_supported
        headers = CaseInsensitiveDict(page.headers or {})
        token = self.config.encode(page.continuation)
        if token is None:
            headers.pop("x-ms-continuation", None)
        else:
            headers["x-ms-continuation"] = token
        return super().parse(replace(page, continuation=token, headers=headers))

    def is_done(self) -> bool:
        return not self.more

    def accept(self, rows: list[Any], deadline: Optional[float]) -> list[Any]:
        self.finish(rows, deadline)
        self.bookmark = self.token
        if self.config.response_state is not None and self.responses:
            self.config.response_state.last_response_headers = deepcopy(self.headers)
        return rows

    def invalidate(self, error: BaseException) -> None:
        if isinstance(error, AzureError) and not error.continuation_token:
            error.continuation_token = self.bookmark
        super().invalidate(error)

    def check(self) -> None:
        if self.failed:
            raise RuntimeError(
                "Query pager failed; create a new pager from the last delivered bookmark."
            )
        if not self.lock.acquire(blocking=False):
            raise RuntimeError("Concurrent use of a query pager is not supported.")

    def should_deliver(self, rows: list[Any], previous: Optional[str]) -> bool:
        if rows or not self.more:
            return True
        if self.resumable and previous == self.token:
            raise RuntimeError(
                "Query returned an empty page without continuation progress."
            )
        return False


class QueryPageIterator(Iterator[Iterator[Any]]):
    def __init__(
        self,
        config: QueryConfig,
        headers: CaseInsensitiveDict,
        continuation_token: Optional[str] = None,
    ) -> None:
        token = (
            continuation_token
            if continuation_token is not None
            else config.options.get("continuation")
        )
        self.state = QueryPageState(config, headers, token)

    @property
    def continuation_token(self) -> Optional[str]:
        if not self.state.resumable:
            raise NotImplementedError(
                "The driver cannot bookmark this query shape; continue using this iterator."
            )
        return self.state.bookmark

    def __next__(self) -> Any:
        state = self.state
        if state.done:
            raise StopIteration
        state.check()
        try:
            deadline = state.config.deadline()
            state.begin()
            while True:
                previous = state.token
                pages = state.config.backend.execute_pages(
                    state.config.prepared(state.token, state.cursor, deadline),
                    deadline=deadline,
                )
                try:
                    page = next(pages)
                except StopIteration as error:
                    raise RuntimeError(
                        "Rust backend returned no query page."
                    ) from error
                finally:
                    pages.close()
                rows = state.parse(page)
                if state.should_deliver(rows, previous):
                    break
            state.accept(rows, deadline)
        except BaseException as error:
            state.invalidate(error)
            raise
        finally:
            state.lock.release()
        if not rows and state.done:
            raise StopIteration
        return iter(rows)

    next = __next__


def query_items(proxy: Any, kwargs: dict[str, Any]) -> CosmosItemPaged:
    config = QueryConfig(proxy, kwargs)
    headers = CaseInsensitiveDict()
    return CosmosItemPaged(
        config, headers, page_iterator_class=QueryPageIterator, response_headers=headers
    )
