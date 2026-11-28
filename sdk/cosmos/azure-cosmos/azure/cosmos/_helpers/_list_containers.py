# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Prepare container metadata pages without a legacy query execution context."""

from __future__ import annotations

import time
from copy import deepcopy
from dataclasses import replace
from typing import Any, Mapping, Optional

from azure.core.paging import ItemPaged
from azure.core.utils import CaseInsensitiveDict

from .. import _base, http_constants
from .._backend.constants import is_rust_backend
from .._backend.contracts import PreparedPageRequest
from .._constants import _Constants, TimeoutScope
from .._operation_deadline import (
    legacy_deadline_kwargs,
    legacy_deadline_options,
    remaining_timeout,
)
from .._query_rust_routing import (
    build_list_containers_page,
    build_query_containers_page,
    can_use_rust_list_containers,
    can_use_rust_query_containers,
)
from ._item_arguments import get_selected_backend
from ._metadata_feed import MetadataFeedPageIterator, RecordingOptions
from ._request_settings import (
    compose_item_options,
    is_supported_operation_timeout,
    normalize_metadata_page_size,
    normalize_query_specification,
    reject_unknown_feed_kwargs,
)
from ._response_parse import validate_response_hook_is_synchronous


class ListContainersConfig:  # pylint: disable=too-many-instance-attributes
    operation = "list_containers"
    response_key = "DocumentCollections"
    owner_name = "DatabaseProxy"

    def __init__(self, proxy: Any, kwargs: dict[str, Any]) -> None:
        self.started = time.monotonic()
        self.hook = kwargs.pop("response_hook", None)
        if self.hook is not None and not callable(self.hook):
            raise TypeError(f"{self.operation} response_hook must be callable or None.")
        validate_response_hook_is_synchronous(self.hook, self.operation)
        for options in (kwargs.get("request_options"), kwargs.get("feed_options")):
            if not isinstance(options, Mapping):
                continue
            for name, key in (
                ("session_token", "sessionToken"),
                ("populate_query_metrics", "populateQueryMetrics"),
                ("availability_strategy", "availabilityStrategy"),
            ):
                if name in options or key in options:
                    raise TypeError(f"{self.operation}() does not support the '{name}' option")
        self.options = deepcopy(compose_item_options(kwargs))
        kwargs.pop("timeout", None)
        self.options.pop(_Constants.OperationStartTime, None)
        self.kwargs = kwargs
        self.recording_options = RecordingOptions.snapshot(kwargs)
        self.timeout = self.options.get("timeout")
        if not is_supported_operation_timeout(self.timeout):
            raise ValueError(f"{self.operation} timeout must be None or finite seconds >= 1 and < 2**64.")
        self.telemetry_owner = proxy
        connection = proxy.client_connection
        context = proxy._client_context
        self.backend = context.adapter if context is not None else get_selected_backend(connection)
        self.response_state = context.response_state if context is not None else connection._response_state
        self.rust = is_rust_backend(self.backend)
        self.connection = None if self.rust else connection
        self.default_headers = dict(connection.default_headers)
        normalize_metadata_page_size(self.options, self.default_headers, operation=self.operation)
        self.path = _base.GetPathFromLink(proxy.database_link, http_constants.ResourceType.Collection)
        self.resource_id = _base.GetResourceIdOrFullNameFromLink(proxy.database_link)

    @property
    def query_payload(self) -> Optional[dict[str, Any]]:
        return None

    @property
    def binding_operation(self) -> str:
        return "list_containers" if self.query_payload is None else "query_containers"

    def _page_query_payload(self) -> Optional[dict[str, Any]]:
        return self.query_payload

    def bind_pager(self, pager: Any) -> None:
        hook = self.hook
        if hook is not None:
            self.hook = lambda headers: hook(headers, pager)

    def deadline(self) -> Optional[float]:
        if self.timeout is None:
            return None
        started = (
            self.started if self.options.get(_Constants.TimeoutScope) == TimeoutScope.OPERATION else time.monotonic()
        )
        return started + self.timeout

    def prepared(self, token: Optional[str], deadline: Optional[float]) -> PreparedPageRequest:
        query = self._page_query_payload()
        eligible = (
            can_use_rust_list_containers(
                path=self.path,
                options=self.options,
                kwargs=self.kwargs,
                is_query_plan=False,
                resource_type=http_constants.ResourceType.Collection,
            )
            if query is None
            else can_use_rust_query_containers(
                path=self.path,
                query_payload=query,
                options=self.options,
                kwargs=self.kwargs,
                is_query_plan=False,
                resource_type=http_constants.ResourceType.Collection,
            )
        )
        if not eligible:
            remaining_kwargs = (
                self.kwargs.keys() - self.recording_options.kwargs.keys() - {_Constants.OperationStartTime}
            )
            reject_unknown_feed_kwargs(self.operation, remaining_kwargs)
            detail = f": {', '.join(repr(name) for name in sorted(remaining_kwargs))}" if remaining_kwargs else ""
            raise TypeError(
                f"{self.operation} cannot honor these options on Rust{detail}; "
                "the request will not be sent through legacy Python."
            )
        options = dict(self.options)
        options["continuation"] = token
        prepared = (
            build_list_containers_page(
                path=self.path,
                options=options,
                req_headers=self.default_headers,
            )
            if query is None
            else build_query_containers_page(
                path=self.path,
                query_payload=query,
                options=options,
                req_headers=self.default_headers,
            )
        )
        return replace(
            prepared,
            settings=replace(prepared.settings, timeout_seconds=remaining_timeout(deadline)),
        )

    def legacy_page(
        self,
        token: Optional[str],
        deadline: Optional[float],
        response_headers: Optional[CaseInsensitiveDict] = None,
    ) -> Any:
        if self.connection is None:
            raise RuntimeError("A legacy container feed requires its selected connection.")
        options = legacy_deadline_options(self.options, deadline)
        options["continuation"] = token
        return self.connection._CosmosClientConnection__QueryFeed(  # pylint: disable=protected-access
            self.path,
            http_constants.ResourceType.Collection,
            self.resource_id,
            lambda body: body[self.response_key],
            lambda _, body: body,
            self._page_query_payload(),
            options,
            _feed_backend=self.backend,
            response_headers=response_headers,
            **legacy_deadline_kwargs(self.kwargs, deadline),
        )


class QueryContainersConfig(ListContainersConfig):
    operation = "query_containers"

    def __init__(self, proxy: Any, query: Any, parameters: Any, kwargs: dict[str, Any]) -> None:
        for options in (kwargs.get("request_options"), kwargs.get("feed_options")):
            if isinstance(options, Mapping) and (
                "enable_cross_partition_query" in options or "enableCrossPartitionQuery" in options
            ):
                raise TypeError(f"{self.operation}() does not support the 'enable_cross_partition_query' option")
        self._query: Optional[dict[str, Any]] = None
        modes = proxy.client_connection._QueryCompatibilityMode
        if query is not None or parameters is not None:
            if proxy.client_connection._query_compatibility_mode not in (modes.Default, modes.Query):
                raise SystemError("Unexpected query compatibility mode.")
            if query is not None and not isinstance(query, (str, dict)):
                raise TypeError("query body must be a dict or string.")
            normalize_query_specification(query, parameters, operation=self.operation)
            # Preserve caller edits until each fetch, as the original lazy query did.
            self._query = query if isinstance(query, dict) else {"query": query, "parameters": parameters}
        super().__init__(proxy, kwargs)

    @property
    def query_payload(self) -> Optional[dict[str, Any]]:
        return self._query

    def _page_query_payload(self) -> Optional[dict[str, Any]]:
        if self._query is None:
            return None
        text, values = normalize_query_specification(self._query, None, operation=self.operation)
        return {"query": text, "parameters": list(values)}


def list_containers(proxy: Any, kwargs: dict[str, Any]) -> ItemPaged[dict[str, Any]]:
    config = ListContainersConfig(proxy, kwargs)
    pager: ItemPaged[dict[str, Any]] = ItemPaged(config, page_iterator_class=MetadataFeedPageIterator)
    config.bind_pager(pager)
    return pager


def query_containers(proxy: Any, query: Any, parameters: Any, kwargs: dict[str, Any]) -> ItemPaged[Any]:
    config = QueryContainersConfig(proxy, query, parameters, kwargs)
    pager: ItemPaged[Any] = ItemPaged(config, page_iterator_class=MetadataFeedPageIterator)
    config.bind_pager(pager)
    return pager
