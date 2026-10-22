# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Prepare container metadata pages without a legacy query execution context."""
from __future__ import annotations

import time
from copy import deepcopy
from dataclasses import replace
from typing import Any, Optional

from azure.core.paging import ItemPaged
from azure.core.utils import CaseInsensitiveDict

from .. import _base, http_constants
from .._backend.contracts import PreparedPageRequest
from .._constants import _Constants, TimeoutScope
from .._operation_deadline import legacy_deadline_kwargs, legacy_deadline_options, remaining_timeout
from .._query_rust_routing import (
    build_list_containers_prepared_page_request,
    build_query_containers_prepared_page_request,
    can_use_rust_backend_for_list_containers_page,
    can_use_rust_backend_for_query_containers_page,
)
from ._item_arguments import get_selected_backend
from ._metadata_feed import MetadataFeedPageIterator
from ._request_settings import compose_item_options, is_supported_operation_timeout


class ListContainersConfig:  # pylint: disable=too-many-instance-attributes
    operation = "list_containers"
    response_key = "DocumentCollections"
    owner_name = "DatabaseProxy"

    def __init__(self, proxy: Any, kwargs: dict[str, Any]) -> None:
        self.started = time.monotonic()
        self.hook = kwargs.pop("response_hook", None)
        self.options = deepcopy(compose_item_options(kwargs))
        kwargs.pop("timeout", None)
        self.options.pop(_Constants.OperationStartTime, None)
        self.kwargs = kwargs
        self.timeout = self.options.get("timeout")
        self.telemetry_owner = proxy
        connection = proxy.client_connection
        context = proxy._item_context
        self.backend = context.adapter if context is not None else get_selected_backend(connection)
        self.response_state = context.response_state if context is not None else connection._response_state
        self.rust = self.backend.name != "core-python"
        self.connection = None if self.rust else connection
        self.default_headers = dict(connection.default_headers)
        self.path = _base.GetPathFromLink(proxy.database_link, http_constants.ResourceType.Collection)
        self.resource_id = _base.GetResourceIdOrFullNameFromLink(proxy.database_link)

    @property
    def query_payload(self) -> Optional[dict[str, Any]]:
        return None

    @property
    def binding_operation(self) -> str:
        return "list_containers" if self.query_payload is None else "query_containers"

    def bind_pager(self, pager: Any) -> None:
        hook = self.hook
        if hook is not None:
            self.hook = lambda headers: hook(headers, pager)

    def deadline(self) -> Optional[float]:
        if self.timeout is None:
            return None
        if self.rust and not is_supported_operation_timeout(self.timeout):
            raise NotImplementedError(
                f"{self.operation} cannot honor this timeout on Rust; "
                "the request will not be sent through legacy Python."
            )
        started = (
            self.started if self.options.get(_Constants.TimeoutScope) == TimeoutScope.OPERATION
            else time.monotonic()
        )
        return started + self.timeout

    def prepared(self, token: Optional[str], deadline: Optional[float]) -> PreparedPageRequest:
        query = self.query_payload
        eligible = can_use_rust_backend_for_list_containers_page(
            path=self.path, options=self.options, kwargs=self.kwargs,
            is_query_plan=False, resource_type=http_constants.ResourceType.Collection,
        ) if query is None else can_use_rust_backend_for_query_containers_page(
            path=self.path, query_payload=query, options=self.options, kwargs=self.kwargs,
            is_query_plan=False, resource_type=http_constants.ResourceType.Collection,
        )
        if not eligible:
            raise NotImplementedError(
                f"{self.operation} cannot honor these options on Rust; "
                "the request will not be sent through legacy Python."
            )
        options = dict(self.options)
        options["continuation"] = token
        prepared = (
            build_list_containers_prepared_page_request(
                path=self.path, options=options, req_headers=self.default_headers,
            ) if query is None else build_query_containers_prepared_page_request(
                path=self.path, query_payload=query, options=options, req_headers=self.default_headers,
            )
        )
        return replace(prepared, settings=replace(prepared.settings, timeout_seconds=remaining_timeout(deadline)))

    def legacy_page(
        self, token: Optional[str], deadline: Optional[float],
        response_headers: Optional[CaseInsensitiveDict] = None,
    ) -> Any:
        if self.connection is None:
            raise RuntimeError("A legacy container feed requires its selected connection.")
        options = legacy_deadline_options(self.options, deadline)
        options["continuation"] = token
        return self.connection._CosmosClientConnection__QueryFeed(  # pylint: disable=protected-access
            self.path, http_constants.ResourceType.Collection, self.resource_id,
            lambda body: body[self.response_key], lambda _, body: body, self.query_payload, options,
            _read_all_backend=self.backend, response_headers=response_headers,
            **legacy_deadline_kwargs(self.kwargs, deadline),
        )


class QueryContainersConfig(ListContainersConfig):
    operation = "query_containers"

    def __init__(self, proxy: Any, query: Any, parameters: Any, kwargs: dict[str, Any]) -> None:
        self._query = deepcopy(query if parameters is None else {"query": query, "parameters": parameters})
        modes = proxy.client_connection._QueryCompatibilityMode
        self.query_mode_supported = proxy.client_connection._query_compatibility_mode in (modes.Default, modes.Query)
        super().__init__(proxy, kwargs)

    @property
    def query_payload(self) -> Optional[dict[str, Any]]:
        if self._query is None:
            return None
        if not self.query_mode_supported:
            raise SystemError("Unexpected query compatibility mode.")
        if isinstance(self._query, str):
            return {"query": self._query}
        if not isinstance(self._query, dict):
            raise TypeError("query body must be a dict or string.")
        if not self._query.get("query"):
            raise ValueError('query body must have valid query text with key "query".')
        return self._query


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
