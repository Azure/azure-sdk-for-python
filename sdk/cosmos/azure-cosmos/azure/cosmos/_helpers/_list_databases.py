# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""List or query databases with stateless paging through the selected Python backend.

Each page iterator keeps its own continuation token. On the Rust path it builds
a prepared page request without a feed cursor, then parses a backend page.
The customer app receives an ItemPaged pager, not the page iterator itself.
"""
from __future__ import annotations

import time
from copy import deepcopy
from dataclasses import replace
from typing import Any, Optional

from azure.core.paging import ItemPaged
from azure.core.utils import CaseInsensitiveDict

from .. import http_constants
from .._backend.contracts import PreparedPageRequest
from .._constants import _Constants, TimeoutScope
from .._operation_deadline import legacy_deadline_kwargs, legacy_deadline_options, remaining_timeout
from .._query_rust_routing import (
    build_list_databases_prepared_page_request,
    build_query_databases_prepared_page_request,
    can_use_rust_backend_for_list_databases_page,
    can_use_rust_backend_for_query_databases_page,
)
from ._request_settings import (
    build_customer_headers, compose_item_options, is_supported_operation_timeout, normalize_query_specification,
)
from ._metadata_feed import MetadataFeedPageIterator


class ListDatabasesConfig:
    operation = "list_databases"
    response_key = "Databases"
    owner_name = "CosmosClient"
    query_payload: Optional[dict[str, Any]] = None
    unsupported_options: tuple[tuple[str, str], ...] = (
        ("session_token", "sessionToken"),
        ("populate_query_metrics", "populateQueryMetrics"),
        ("availability_strategy", "availabilityStrategy"),
        ("no_response", "responsePayloadOnWriteDisabled"),
        ("content_type", "contentType"),
    )

    def __init__(self, client: Any, kwargs: dict[str, Any]) -> None:
        started = time.monotonic()
        self.hook = kwargs.pop("response_hook", None)
        if self.hook is not None and not callable(self.hook):
            raise TypeError(f"{self.operation} response_hook must be callable or None.")
        self.options = deepcopy(compose_item_options(kwargs))
        for name, key in self.unsupported_options:
            if name in kwargs or key in self.options:
                raise TypeError(f"{self.operation}() does not support the '{name}' option")
        kwargs.pop("timeout", None)
        self.timeout = self.options.get("timeout")
        if not is_supported_operation_timeout(self.timeout):
            raise ValueError(f"{self.operation} timeout must be None or finite seconds >= 1 and < 2**64.")
        self.options.pop(_Constants.OperationStartTime, None)
        self.operation_deadline = (
            started + self.timeout
            if self.timeout is not None and self.options.get(_Constants.TimeoutScope) == TimeoutScope.OPERATION
            else None
        )
        self.default_headers = dict(client.client_connection.default_headers)
        initial = build_customer_headers(self.options.get("initialHeaders"))
        page_size_header = http_constants.HttpHeaders.PageSize
        raw_count = initial.get(
            page_size_header, build_customer_headers(self.default_headers).get(page_size_header),
        )
        # Raw option headers override initial headers; a typed count overrides both.
        for key in tuple(self.options):
            if isinstance(key, str) and key.lower() == page_size_header:
                raw_count = str(self.options.pop(key))
        count = self.options.get("maxItemCount")
        if count is None and raw_count is not None:
            try:
                count = int(raw_count)
            except ValueError as error:
                raise ValueError(f"{self.operation} x-ms-max-item-count must be an integer.") from error
        if count is not None and (
            type(count) is not int
            or count == 0 or count < -1 or count >= 2**63
        ):
            raise ValueError(f"{self.operation} max_item_count must be a positive i64 integer, -1, or None.")
        if count is not None:
            self.options["maxItemCount"] = count
        if "initialHeaders" in self.options:
            initial.pop(page_size_header, None)
            self.options["initialHeaders"] = initial
        self.kwargs = kwargs
        self.telemetry_owner = client
        self.backend = client._adapter
        self.rust = self.backend.name != "core-python"
        self.response_state = client._item_context.response_state
        self.connection = None if self.rust else client.client_connection

    def deadline(self) -> Optional[float]:
        if self.operation_deadline is not None:
            return self.operation_deadline
        return None if self.timeout is None else time.monotonic() + self.timeout

    @property
    def binding_operation(self) -> str:
        return "list_databases" if self.query_payload is None else "query_databases"

    def prepared(self, token: Optional[str], deadline: Optional[float]) -> PreparedPageRequest:
        eligible = can_use_rust_backend_for_list_databases_page(
            options=self.options, kwargs=self.kwargs, is_query_plan=False,
            resource_type=http_constants.ResourceType.Database,
        ) if self.query_payload is None else can_use_rust_backend_for_query_databases_page(
            query_payload=self.query_payload, options=self.options, kwargs=self.kwargs,
            is_query_plan=False, resource_type=http_constants.ResourceType.Database,
        )
        if not eligible:
            raise NotImplementedError(
                f"{self.operation} cannot honor these options on Rust; "
                "the request will not be sent through legacy Python."
            )
        options = dict(self.options)
        if token is not None:
            options["continuation"] = token
        else:
            options.pop("continuation", None)
        prepared = (
            build_list_databases_prepared_page_request(options=options, req_headers=self.default_headers)
            if self.query_payload is None else build_query_databases_prepared_page_request(
                query_payload=self.query_payload, options=options, req_headers=self.default_headers,
            )
        )
        return replace(prepared, settings=replace(prepared.settings, timeout_seconds=remaining_timeout(deadline)))

    def legacy_page(
        self, token: Optional[str], deadline: Optional[float],
        response_headers: Optional[CaseInsensitiveDict] = None,
    ) -> Any:
        if self.connection is None:
            raise RuntimeError("A legacy database listing requires its selected connection.")
        options = legacy_deadline_options(self.options, deadline)
        options["continuation"] = token
        # The legacy path retries the request, never the customer app's success hook.
        return self.connection._CosmosClientConnection__QueryFeed(
            "/dbs", http_constants.ResourceType.Database, "",
            lambda body: body["Databases"], lambda _, body: body, self.query_payload, options,
            _read_all_backend=self.backend,
            response_headers=response_headers,
            **legacy_deadline_kwargs(self.kwargs, deadline),
        )


class QueryDatabasesConfig(ListDatabasesConfig):
    operation = "query_databases"
    unsupported_options = ListDatabasesConfig.unsupported_options + (
        ("enable_cross_partition_query", "enableCrossPartitionQuery"),
    )

    def __init__(
        self, client: Any, query: Any, parameters: Any, kwargs: dict[str, Any],
    ) -> None:
        if query is not None:
            text, values = normalize_query_specification(query, parameters, operation=self.operation)
            self.query_payload = {"query": text, "parameters": list(values)}
        modes = client.client_connection._QueryCompatibilityMode
        self.query_mode_supported = client.client_connection._query_compatibility_mode in (
            modes.Default, modes.Query,
        )
        super().__init__(client, kwargs)

    def prepared(self, token: Optional[str], deadline: Optional[float]) -> PreparedPageRequest:
        if self.query_payload is not None and not self.query_mode_supported:
            raise SystemError("Unexpected query compatibility mode.")
        return super().prepared(token, deadline)


def list_databases(client: Any, kwargs: dict[str, Any]) -> ItemPaged[dict[str, Any]]:
    return ItemPaged(ListDatabasesConfig(client, kwargs), page_iterator_class=MetadataFeedPageIterator)


def query_databases(client: Any, query: Any, parameters: Any, kwargs: dict[str, Any]) -> ItemPaged[Any]:
    return ItemPaged(
        QueryDatabasesConfig(client, query, parameters, kwargs), page_iterator_class=MetadataFeedPageIterator,
    )
